"""Пользовательский flow «💸 Запросить вывод средств» + админский approve."""

import asyncio
import logging
from decimal import Decimal, InvalidOperation

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.models.payment_log import PaymentLogMethod
from database.models.withdrawal import WithdrawalStatus
from database.repositories import payment_logs as payment_logs_repo
from database.repositories import users as users_repo
from database.repositories import withdrawals as withdrawals_repo
from handlers.cabinet import render_cabinet, send_cabinet
from keyboards.withdraw import (
    admin_withdraw_keyboard,
    withdraw_amount_keyboard,
    withdraw_cancel_confirm_keyboard,
    withdraw_confirm_keyboard,
)
from locales.texts import get_lang, t
from permissions import is_admin
from settings import get_settings
from states import WithdrawState

logger = logging.getLogger(__name__)

router = Router(name="withdraw")

MIN_WITHDRAW = Decimal("100")


def _resolve_lang(user: User, event) -> str:
    return user.language_code or get_lang(
        getattr(event.from_user, "language_code", None)
    )


def _fmt(amount: Decimal | None) -> str:
    if amount is None:
        return "0"
    try:
        if amount == amount.to_integral_value():
            return str(int(amount))
        return f"{amount:f}".rstrip("0").rstrip(".")
    except Exception:
        return str(amount)


def _calc_payout(amount: Decimal, fee_percent: Decimal) -> tuple[Decimal, Decimal]:
    fee_amount = (amount * fee_percent / Decimal("100")).quantize(Decimal("0.01"))
    payout = (amount - fee_amount).quantize(Decimal("0.01"))
    return fee_amount, payout


def _user_mention(user: User) -> tuple[str, str]:
    display = user.user_name or user.name or str(user.user_id)
    mention = f'<a href="tg://user?id={user.user_id}">{display}</a>'
    username = f" (@{user.user_name})" if user.user_name else ""
    return mention, username


async def _flash_error(message: Message, text: str, seconds: float = 3.0) -> None:
    """Имитация popup: удаляем ввод юзера и шлём короткое сообщение, исчезающее через N сек.

    В Telegram нельзя показать alert в ответ на текстовое сообщение —
    это работает только в callback_query. Делаем максимально близко по UX.
    """
    try:
        await message.delete()
    except Exception:
        pass
    try:
        flash = await message.answer(text)
    except Exception:
        return

    async def _auto_delete() -> None:
        await asyncio.sleep(seconds)
        try:
            await flash.delete()
        except Exception:
            pass

    asyncio.create_task(_auto_delete())


# ── Открыть форму вывода ──────────────────────────────────────────────────────


@router.callback_query(F.data == "menu:withdraw", F.message.chat.type == "private")
async def on_menu_withdraw(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    bot: Bot,
) -> None:
    lang = _resolve_lang(user, callback)

    existing = await withdrawals_repo.get_pending_for_user(session, user.user_id)
    if existing is not None:
        await callback.answer(t("withdraw_already_pending", lang), show_alert=True)
        await render_cabinet(callback, session, user, bot)
        return

    fee_percent = await users_repo.effective_withdraw_percent(session, user)
    await state.set_state(WithdrawState.waiting_amount)
    await callback.message.edit_text(
        t("withdraw_enter_amount", lang).format(
            min=_fmt(MIN_WITHDRAW),
            fee=_fmt(fee_percent),
        ),
        reply_markup=withdraw_amount_keyboard(lang),
    )
    await callback.answer()


# ── Ввод суммы ────────────────────────────────────────────────────────────────


@router.message(StateFilter(WithdrawState.waiting_amount), F.chat.type == "private")
async def on_withdraw_amount(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)

    text = (message.text or "").strip().replace(",", ".")
    try:
        amount = Decimal(text)
    except (InvalidOperation, ValueError):
        await _flash_error(message, t("withdraw_invalid_amount", lang))
        return

    if amount < MIN_WITHDRAW:
        await _flash_error(
            message,
            t("withdraw_below_min", lang).format(min=_fmt(MIN_WITHDRAW)),
        )
        return

    balance = user.balance or Decimal("0")
    if amount > balance:
        await _flash_error(
            message,
            t("withdraw_not_enough", lang).format(balance=_fmt(balance)),
        )
        return

    amount = amount.quantize(Decimal("0.01"))
    await state.update_data(amount=str(amount))
    await state.set_state(WithdrawState.waiting_blik)
    await message.answer(t("withdraw_enter_blik", lang))


# ── Ввод BLIK ─────────────────────────────────────────────────────────────────


@router.message(StateFilter(WithdrawState.waiting_blik), F.chat.type == "private")
async def on_withdraw_blik(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)

    blik = (message.text or "").strip()
    digits = "".join(ch for ch in blik if ch.isdigit())
    if len(digits) < 9:
        await message.answer(t("withdraw_invalid_blik", lang))
        return

    data = await state.get_data()
    amount = Decimal(data["amount"])
    fee_percent = await users_repo.effective_withdraw_percent(session, user)
    fee_amount, payout = _calc_payout(amount, fee_percent)

    await state.update_data(
        amount=str(amount),
        blik=blik,
        fee_percent=str(fee_percent),
    )
    await state.set_state(WithdrawState.waiting_confirm)

    await message.answer(
        t("withdraw_confirm", lang).format(
            amount=_fmt(amount),
            fee=_fmt(fee_percent),
            fee_amount=_fmt(fee_amount),
            payout=_fmt(payout),
            blik=blik,
        ),
        reply_markup=withdraw_confirm_keyboard(lang),
    )


# ── Да / Нет в подтверждении ──────────────────────────────────────────────────


@router.callback_query(
    F.data == "withdraw:confirm_no", F.message.chat.type == "private"
)
async def on_withdraw_confirm_no(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    bot: Bot,
) -> None:
    await state.clear()
    await render_cabinet(callback, session, user, bot)
    await callback.answer()


@router.callback_query(
    F.data == "withdraw:confirm_yes", F.message.chat.type == "private"
)
async def on_withdraw_confirm_yes(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    bot: Bot,
) -> None:
    lang = _resolve_lang(user, callback)

    if await state.get_state() != WithdrawState.waiting_confirm.state:
        await callback.answer()
        return

    data = await state.get_data()
    try:
        amount = Decimal(data["amount"])
        blik = data["blik"]
        fee_percent = Decimal(data.get("fee_percent", "0"))
    except (KeyError, InvalidOperation):
        await state.clear()
        await callback.answer("⛔ Сессия истекла, начните заново", show_alert=True)
        return

    balance = user.balance or Decimal("0")
    if amount > balance:
        await state.clear()
        await callback.answer(
            t("withdraw_not_enough", lang).format(balance=_fmt(balance)),
            show_alert=True,
        )
        await render_cabinet(callback, session, user, bot)
        return

    # повторная защита от дублирующего pending
    existing = await withdrawals_repo.get_pending_for_user(session, user.user_id)
    if existing is not None:
        await state.clear()
        await callback.answer(t("withdraw_already_pending", lang), show_alert=True)
        await render_cabinet(callback, session, user, bot)
        return

    fee_amount, payout = _calc_payout(amount, fee_percent)

    # списываем сумму с баланса
    user.balance = (user.balance or Decimal("0.00")) - amount
    await session.flush()
    await payment_logs_repo.log(
        session,
        user_id=user.user_id,
        method=PaymentLogMethod.WITHDRAW,
        amount=-amount,
        balance_after=user.balance,
    )
    withdrawal = await withdrawals_repo.create(
        session,
        user_id=user.user_id,
        amount=amount,
        fee_percent=fee_percent,
        payout_amount=payout,
        blik_number=blik,
    )
    await session.commit()
    await state.clear()

    # сообщение в админ-чат
    settings = get_settings()
    if settings.admin_chat is not None:
        mention, username = _user_mention(user)
        admin_text = t("withdraw_admin_message", "ru").format(
            mention=mention,
            username=username,
            user_id=user.user_id,
            amount=_fmt(amount),
            fee=_fmt(fee_percent),
            fee_amount=_fmt(fee_amount),
            payout=_fmt(payout),
            blik=blik,
        )
        try:
            sent = await bot.send_message(
                settings.admin_chat,
                admin_text,
                reply_markup=admin_withdraw_keyboard(withdrawal.id, "ru"),
            )
            await withdrawals_repo.set_admin_message(
                session, withdrawal.id, sent.chat.id, sent.message_id
            )
            await session.commit()
        except Exception as exc:
            logger.warning(
                "Failed to send withdrawal #%d to admin_chat=%s: %s",
                withdrawal.id,
                settings.admin_chat,
                exc,
            )

    await callback.message.edit_text(
        t("withdraw_created", lang).format(
            id=withdrawal.id,
            payout=_fmt(payout),
            blik=blik,
        ),
    )
    await send_cabinet(callback.message, session, user, bot)
    await callback.answer()


# ── Отмена пользователем ──────────────────────────────────────────────────────


@router.callback_query(
    F.data == "withdraw:cancel_ask", F.message.chat.type == "private"
)
async def on_withdraw_cancel_ask(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _resolve_lang(user, callback)
    pending = await withdrawals_repo.get_pending_for_user(session, user.user_id)
    if pending is None:
        await callback.answer(t("withdraw_not_pending", lang), show_alert=True)
        await render_cabinet(callback, session, user, bot)
        return
    await callback.message.edit_text(
        t("withdraw_cancel_ask", lang).format(id=pending.id),
        reply_markup=withdraw_cancel_confirm_keyboard(pending.id, lang),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("withdraw:cancel_yes:"), F.message.chat.type == "private"
)
async def on_withdraw_cancel_yes(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
) -> None:
    lang = _resolve_lang(user, callback)
    withdrawal_id = int(callback.data.split(":")[-1])
    withdrawal = await withdrawals_repo.get(session, withdrawal_id)
    if (
        withdrawal is None
        or withdrawal.user_id != user.user_id
        or withdrawal.status != WithdrawalStatus.PENDING
    ):
        await callback.answer(t("withdraw_not_pending", lang), show_alert=True)
        await render_cabinet(callback, session, user, bot)
        return

    # возвращаем деньги
    user.balance = (user.balance or Decimal("0.00")) + withdrawal.amount
    await session.flush()
    await payment_logs_repo.log(
        session,
        user_id=user.user_id,
        method=PaymentLogMethod.WITHDRAW_REFUND,
        amount=withdrawal.amount,
        balance_after=user.balance,
    )
    await withdrawals_repo.mark_cancelled(session, withdrawal.id)
    await session.commit()

    # правим сообщение в админ-чате (если оно было)
    if withdrawal.admin_chat_id and withdrawal.admin_message_id:
        try:
            await bot.edit_message_text(
                await _build_admin_text(
                    session, withdrawal, status_key="withdraw_admin_cancelled"
                ),
                chat_id=withdrawal.admin_chat_id,
                message_id=withdrawal.admin_message_id,
                reply_markup=None,
            )
        except Exception as exc:
            logger.warning(
                "Failed to edit admin message for withdrawal #%d: %s",
                withdrawal.id,
                exc,
            )

    await callback.answer(
        t("withdraw_cancelled", lang)
        .format(id=withdrawal.id)
        .replace("<code>", "")
        .replace("</code>", ""),
        show_alert=True,
    )
    await render_cabinet(callback, session, user, bot)


async def _build_admin_text(
    session: AsyncSession, withdrawal, status_key: str | None = None
) -> str:
    """Полный текст админ-сообщения по объекту Withdrawal (+ опциональный header)."""
    target = await session.get(User, withdrawal.user_id)
    if target is not None:
        mention, username = _user_mention(target)
    else:
        mention = f'<a href="tg://user?id={withdrawal.user_id}">{withdrawal.user_id}</a>'
        username = ""

    fee_amount = (
        withdrawal.amount * withdrawal.fee_percent / Decimal("100")
    ).quantize(Decimal("0.01"))
    payout = (withdrawal.amount - fee_amount).quantize(Decimal("0.01"))

    body = t("withdraw_admin_message", "ru").format(
        mention=mention,
        username=username,
        user_id=withdrawal.user_id,
        amount=_fmt(withdrawal.amount),
        fee=_fmt(withdrawal.fee_percent),
        fee_amount=_fmt(fee_amount),
        payout=_fmt(payout),
        blik=withdrawal.blik_number,
    )
    if status_key:
        return f"{t(status_key, 'ru')}\n\n{body}"
    return body


# ── Админ принимает заявку ────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("admin:withdraw:approve:"))
async def on_admin_withdraw_approve(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
) -> None:
    if not is_admin(user, get_settings()):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    withdrawal_id = int(callback.data.split(":")[-1])
    withdrawal = await withdrawals_repo.get(session, withdrawal_id)
    if withdrawal is None or withdrawal.status != WithdrawalStatus.PENDING:
        await callback.answer("Заявка уже обработана", show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        return

    await withdrawals_repo.mark_approved(
        session, withdrawal.id, approved_by=user.user_id
    )
    await session.commit()

    # редактируем админ-сообщение — добавляем «ОПЛАЧЕНО», убираем кнопку
    try:
        new_text = await _build_admin_text(
            session, withdrawal, status_key="withdraw_admin_approved"
        )
        await callback.message.edit_text(new_text, reply_markup=None)
    except Exception as exc:
        logger.warning("Failed to edit approved withdrawal #%d: %s", withdrawal.id, exc)

    # уведомление юзеру
    try:
        target_user = await session.get(User, withdrawal.user_id)
        target_lang = (
            target_user.language_code if target_user and target_user.language_code else "ru"
        )
        await bot.send_message(
            withdrawal.user_id,
            t("withdraw_approved_user", target_lang).format(
                id=withdrawal.id,
                payout=_fmt(withdrawal.payout_amount),
            ),
        )
    except Exception as exc:
        logger.warning(
            "Failed to notify user_id=%s about approved withdrawal #%d: %s",
            withdrawal.user_id,
            withdrawal.id,
            exc,
        )

    await callback.answer("✅ Принято")
