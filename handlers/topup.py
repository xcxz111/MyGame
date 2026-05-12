"""Пользовательский flow «💳 Пополнить баланс»."""

import logging
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.models.payments.account import MBankAccount
from database.models.payments.order import MBankOrderStatus
from database.repositories.payments import accounts as accounts_repo
from database.repositories.payments import orders as orders_repo
from keyboards.topup import topup_amount_keyboard, topup_order_keyboard
from locales.texts import get_lang, t
from settings import get_settings
from states import TopupState

logger = logging.getLogger(__name__)

router = Router(name="topup")


def _resolve_lang(user: User, event) -> str:
    return user.language_code or get_lang(
        getattr(event.from_user, "language_code", None)
    )


async def _pick_account(session: AsyncSession) -> MBankAccount | None:
    """Возвращает первый активный (и не спящий) mbank-аккаунт; иначе None."""
    accounts = await accounts_repo.list_active(session)
    for acc in accounts:
        if not acc.limit_sleeping and acc.blik_number:
            return acc
    return None


# ── Открыть форму пополнения ──────────────────────────────────────────────────


@router.callback_query(F.data == "menu:topup", F.message.chat.type == "private")
async def on_menu_topup(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    settings = get_settings()
    await state.set_state(TopupState.waiting_amount)
    await callback.message.edit_text(
        t("topup_enter_amount", lang).format(
            min=settings.mbanks_min_topup,
            max=settings.mbanks_max_topup,
        ),
        reply_markup=topup_amount_keyboard(lang),
    )
    await callback.answer()


# ── Ввод суммы ────────────────────────────────────────────────────────────────


@router.message(StateFilter(TopupState.waiting_amount), F.chat.type == "private")
async def on_topup_amount(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)
    settings = get_settings()

    text = (message.text or "").strip().replace(",", ".")
    try:
        amount = Decimal(text)
    except (InvalidOperation, ValueError):
        await message.answer(t("topup_invalid_amount", lang))
        return

    min_amount = Decimal(settings.mbanks_min_topup)
    max_amount = Decimal(settings.mbanks_max_topup)
    if amount < min_amount or amount > max_amount:
        await message.answer(
            t("topup_out_of_range", lang).format(
                min=settings.mbanks_min_topup,
                max=settings.mbanks_max_topup,
            )
        )
        return

    amount = amount.quantize(Decimal("0.01"))

    account = await _pick_account(session)
    if account is None:
        await state.clear()
        await message.answer(t("topup_no_accounts", lang))
        return

    order = await orders_repo.create(
        session,
        user_id=user.user_id,
        amount=amount,
        account_email=account.email,
        currency="PLN",
        blik_number=account.blik_number,
        description=f"Top-up via {account.bank}",
    )
    await session.commit()
    await state.clear()

    logger.info(
        "Topup order %s created: user_id=%s amount=%s account=%s",
        order.id,
        user.user_id,
        amount,
        account.email,
    )

    amount_str = (
        str(int(amount)) if amount == amount.to_integral_value() else f"{amount:f}"
    )
    await message.answer(
        t("topup_order_created", lang).format(
            amount=amount_str,
            order_id=order.id,
            blik=account.blik_number or "—",
        ),
        reply_markup=topup_order_keyboard(order.id, lang),
    )


# ── Отмена ордера ─────────────────────────────────────────────────────────────


@router.callback_query(
    F.data.startswith("topup:cancel:"), F.message.chat.type == "private"
)
async def on_topup_cancel(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _resolve_lang(user, callback)
    order_id = callback.data.split(":", 2)[-1]
    order = await orders_repo.get(session, order_id)

    if (
        order is None
        or order.user_id != user.user_id
        or order.status != MBankOrderStatus.PENDING
    ):
        await callback.answer(t("topup_order_not_found", lang), show_alert=True)
        return

    await orders_repo.update(session, order_id, status=MBankOrderStatus.FAILED)
    await session.commit()
    await callback.message.edit_text(
        t("topup_order_cancelled", lang).format(order_id=order_id)
    )
    await callback.answer()
