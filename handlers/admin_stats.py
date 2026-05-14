"""Админская статистика."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.models.user import UserStatus
from database.repositories import fees as fees_repo
from database.repositories import user_levels as user_levels_repo
from database.repositories import users as users_repo
from locales.texts import get_lang, t
from permissions import is_admin
from settings import get_settings

router = Router(name="admin_stats")


class AdminStatsUserState(StatesGroup):
    waiting_query = State()
    waiting_topup_amount = State()
    waiting_withdraw_percent = State()
    waiting_referral_percent = State()


def _lang(user: User, callback: CallbackQuery) -> str:
    return user.language_code or get_lang(callback.from_user.language_code)


def _lang_msg(user: User, message: Message) -> str:
    return user.language_code or get_lang(message.from_user.language_code)


async def _deny(callback: CallbackQuery, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await callback.answer(t("admin_no_access", lang), show_alert=True)
    return True


async def _deny_msg(message: Message, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await message.answer(t("admin_no_access", lang))
    return True


async def _safe_edit_text(
    callback: CallbackQuery, text: str, *, reply_markup: InlineKeyboardMarkup
) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        raise


def _fmt_money(value: Decimal | int | None) -> str:
    return f"{Decimal(str(value or '0')):.2f}"


def _fmt_percent(value: Decimal | int | None) -> str:
    return f"{Decimal(str(value or '0')):.2f}"


def _parse_percent(raw: str) -> Decimal | None | bool:
    value = raw.strip().replace(",", ".").rstrip("%").strip().lower()
    if value in {"-", "сброс", "общая", "общий", "default"}:
        return None
    try:
        percent = Decimal(value)
    except (InvalidOperation, ValueError):
        return False
    if percent < 0 or percent > 100:
        return False
    return percent.quantize(Decimal("0.01"))


def _user_label(target: User) -> str:
    name = target.name or target.user_name or str(target.user_id)
    username = f"@{target.user_name}" if target.user_name else "—"
    return f"{escape(name)} ({escape(username)})"


def _stats_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_stats_btn_users", lang),
            callback_data="admin:stats:users",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:admin", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def _back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:stats", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def _user_search_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:stats", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def _user_card_keyboard(target: User, lang: str) -> InlineKeyboardMarkup:
    user_id = int(target.user_id)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_user_btn_topup", lang),
            callback_data=f"admin:stats:user:topup:{user_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_user_btn_withdraw_percent", lang),
            callback_data=f"admin:stats:user:withdraw:{user_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_user_btn_referral_percent", lang),
            callback_data=f"admin:stats:user:referral:{user_id}",
        )
    )
    ban_key = (
        "admin_user_btn_unban"
        if int(target.status) == UserStatus.BANNED
        else "admin_user_btn_ban"
    )
    ban_action = "unban" if int(target.status) == UserStatus.BANNED else "ban"
    builder.row(
        InlineKeyboardButton(
            text=t(ban_key, lang),
            callback_data=f"admin:stats:user:{ban_action}:{user_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_user_btn_find_other", lang),
            callback_data="admin:stats:users",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:stats", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


async def _user_card_text(session: AsyncSession, target: User, lang: str) -> str:
    global_withdraw = await fees_repo.get_withdraw_percent(session)
    global_referral = await fees_repo.get_referral_percent(session)
    level_withdraw_discount, level_referral_bonus = await user_levels_repo.get_bonus_totals(
        session, int(target.level or 1)
    )
    effective_withdraw = await users_repo.effective_withdraw_percent(session, target)
    effective_referral = await users_repo.effective_referral_percent(session, target)
    referrals = await users_repo.list_referrals_with_profit(session, target.user_id)
    referral_profit = sum((profit for _, profit in referrals), Decimal("0.00"))
    status = (
        t("admin_user_status_banned", lang)
        if int(target.status) == UserStatus.BANNED
        else t("admin_user_status_active", lang)
    )
    withdraw_source = (
        t("admin_user_withdraw_discount", lang).format(
            global_percent=_fmt_percent(global_withdraw),
            discount=_fmt_percent(target.withdraw_percent),
        )
        if target.withdraw_percent is not None
        else t("admin_user_percent_global", lang).format(
            percent=_fmt_percent(global_withdraw)
        )
    )
    referral_source = (
        t("admin_user_referral_bonus", lang).format(
            global_percent=_fmt_percent(global_referral),
            bonus=_fmt_percent(target.referral_percent),
        )
        if target.referral_percent is not None
        else t("admin_user_percent_global", lang).format(
            percent=_fmt_percent(global_referral)
        )
    )
    referrer = "—"
    if target.referrer_id is not None:
        referrer_user = await users_repo.get_user(session, int(target.referrer_id))
        referrer = (
            f"{_user_label(referrer_user)} / <code>{referrer_user.user_id}</code>"
            if referrer_user is not None
            else str(target.referrer_id)
        )
    return t("admin_user_card", lang).format(
        label=_user_label(target),
        user_id=target.user_id,
        username=escape(f"@{target.user_name}" if target.user_name else "—"),
        status=status,
        balance=_fmt_money(target.balance),
        level=int(target.level or 1),
        level_progress=_fmt_money(target.level_win_bet_sum),
        level_withdraw_discount=_fmt_percent(level_withdraw_discount),
        level_referral_bonus=_fmt_percent(level_referral_bonus),
        language=escape(target.language_code or "—"),
        referrer=referrer,
        withdraw_percent=_fmt_percent(effective_withdraw),
        withdraw_source=withdraw_source,
        referral_percent=_fmt_percent(effective_referral),
        referral_source=referral_source,
        referrals_count=len(referrals),
        referrals_profit=_fmt_money(referral_profit),
    )


async def _send_user_card(
    message: Message, session: AsyncSession, target: User, lang: str
) -> None:
    await message.answer(
        await _user_card_text(session, target, lang),
        reply_markup=_user_card_keyboard(target, lang),
    )


async def _edit_user_card(
    callback: CallbackQuery, session: AsyncSession, target: User, lang: str
) -> None:
    await _safe_edit_text(
        callback,
        await _user_card_text(session, target, lang),
        reply_markup=_user_card_keyboard(target, lang),
    )


@router.callback_query(F.data == "admin:stats", F.message.chat.type == "private")
async def on_admin_stats(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.clear()
    await _safe_edit_text(
        callback,
        t("admin_stats_title", lang),
        reply_markup=_stats_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats:users", F.message.chat.type == "private")
async def on_admin_stats_users(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.set_state(AdminStatsUserState.waiting_query)
    await _safe_edit_text(
        callback,
        t("admin_user_search_prompt", lang),
        reply_markup=_user_search_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats:summary", F.message.chat.type == "private")
async def on_admin_stats_users_summary(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    row = (
        await session.execute(
            select(
                func.count(User.user_id).label("total"),
                func.coalesce(
                    func.sum(case((User.status == UserStatus.ACTIVE, 1), else_=0)), 0
                ).label("active"),
                func.coalesce(
                    func.sum(case((User.status == UserStatus.BANNED, 1), else_=0)), 0
                ).label("banned"),
                func.coalesce(func.sum(case((User.balance > 0, 1), else_=0)), 0).label(
                    "with_balance"
                ),
                func.coalesce(func.sum(User.balance), 0).label("balance_sum"),
            )
        )
    ).one()
    await _safe_edit_text(
        callback,
        t("admin_stats_users_title", lang).format(
            total=int(row.total or 0),
            active=int(row.active or 0),
            banned=int(row.banned or 0),
            with_balance=int(row.with_balance or 0),
            balance_sum=_fmt_money(row.balance_sum),
        ),
        reply_markup=_back_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(AdminStatsUserState.waiting_query), F.chat.type == "private")
async def on_admin_user_query(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang_msg(user, message)
    if await _deny_msg(message, user, lang):
        await state.clear()
        return
    target = await users_repo.find_user_by_id_or_username(session, message.text or "")
    if target is None:
        await message.answer(t("admin_user_not_found", lang))
        return
    await state.clear()
    await _send_user_card(message, session, target, lang)


async def _open_user_action(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    *,
    state_to_set: State,
    prompt_key: str,
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    target_id = int(callback.data.split(":")[-1])
    target = await users_repo.get_user(session, target_id)
    if target is None:
        await callback.answer(t("admin_user_not_found", lang), show_alert=True)
        return
    await state.set_state(state_to_set)
    await state.update_data(target_user_id=target_id)
    await _safe_edit_text(
        callback,
        t(prompt_key, lang).format(user=_user_label(target), user_id=target_id),
        reply_markup=_user_search_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:stats:user:topup:"), F.message.chat.type == "private"
)
async def on_admin_user_topup_open(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _open_user_action(
        callback,
        session,
        user,
        state,
        state_to_set=AdminStatsUserState.waiting_topup_amount,
        prompt_key="admin_user_topup_prompt",
    )


@router.callback_query(
    F.data.startswith("admin:stats:user:withdraw:"), F.message.chat.type == "private"
)
async def on_admin_user_withdraw_open(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _open_user_action(
        callback,
        session,
        user,
        state,
        state_to_set=AdminStatsUserState.waiting_withdraw_percent,
        prompt_key="admin_user_withdraw_prompt",
    )


@router.callback_query(
    F.data.startswith("admin:stats:user:referral:"), F.message.chat.type == "private"
)
async def on_admin_user_referral_open(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _open_user_action(
        callback,
        session,
        user,
        state,
        state_to_set=AdminStatsUserState.waiting_referral_percent,
        prompt_key="admin_user_referral_prompt",
    )


@router.message(
    StateFilter(AdminStatsUserState.waiting_topup_amount), F.chat.type == "private"
)
async def on_admin_user_topup_amount(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang_msg(user, message)
    if await _deny_msg(message, user, lang):
        await state.clear()
        return
    data = await state.get_data()
    target_id = int(data.get("target_user_id") or 0)
    target = await users_repo.get_user(session, target_id)
    if target is None:
        await state.clear()
        await message.answer(t("admin_user_not_found", lang))
        return
    raw = (message.text or "").strip().replace(",", ".")
    try:
        amount = Decimal(raw)
    except (InvalidOperation, ValueError):
        await message.answer(t("admin_user_amount_invalid", lang))
        return
    if amount <= 0:
        await message.answer(t("admin_user_amount_invalid", lang))
        return
    amount = amount.quantize(Decimal("0.01"))
    await users_repo.adjust_balance(
        session,
        target_id,
        amount,
        method="admin:balance:topup",
    )
    await session.commit()
    await state.clear()
    target = await users_repo.get_user(session, target_id)
    await message.answer(t("admin_user_topup_done", lang).format(amount=_fmt_money(amount)))
    if target is not None:
        await _send_user_card(message, session, target, lang)


async def _handle_percent_input(
    message: Message,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    *,
    setter,
    done_key: str,
) -> None:
    lang = _lang_msg(user, message)
    if await _deny_msg(message, user, lang):
        await state.clear()
        return
    data = await state.get_data()
    target_id = int(data.get("target_user_id") or 0)
    target = await users_repo.get_user(session, target_id)
    if target is None:
        await state.clear()
        await message.answer(t("admin_user_not_found", lang))
        return
    parsed = _parse_percent(message.text or "")
    if parsed is False:
        await message.answer(t("admin_user_percent_invalid", lang))
        return
    await setter(session, target_id, parsed)
    await session.commit()
    await state.clear()
    target = await users_repo.get_user(session, target_id)
    percent_text = (
        t("admin_user_percent_reset", lang)
        if parsed is None
        else f"{_fmt_percent(parsed)}%"
    )
    await message.answer(t(done_key, lang).format(percent=percent_text))
    if target is not None:
        await _send_user_card(message, session, target, lang)


@router.message(
    StateFilter(AdminStatsUserState.waiting_withdraw_percent),
    F.chat.type == "private",
)
async def on_admin_user_withdraw_percent(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _handle_percent_input(
        message,
        session,
        user,
        state,
        setter=users_repo.set_withdraw_percent,
        done_key="admin_user_withdraw_done",
    )


@router.message(
    StateFilter(AdminStatsUserState.waiting_referral_percent),
    F.chat.type == "private",
)
async def on_admin_user_referral_percent(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _handle_percent_input(
        message,
        session,
        user,
        state,
        setter=users_repo.set_referral_percent,
        done_key="admin_user_referral_done",
    )


@router.callback_query(
    F.data.startswith("admin:stats:user:ban:"), F.message.chat.type == "private"
)
async def on_admin_user_ban(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    target_id = int(callback.data.split(":")[-1])
    target = await users_repo.get_user(session, target_id)
    if target is None:
        await callback.answer(t("admin_user_not_found", lang), show_alert=True)
        return
    await users_repo.set_status(session, target_id, UserStatus.BANNED)
    await session.commit()
    target = await users_repo.get_user(session, target_id)
    await callback.answer(t("admin_user_banned", lang), show_alert=True)
    if target is not None:
        await _edit_user_card(callback, session, target, lang)


@router.callback_query(
    F.data.startswith("admin:stats:user:unban:"), F.message.chat.type == "private"
)
async def on_admin_user_unban(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    target_id = int(callback.data.split(":")[-1])
    target = await users_repo.get_user(session, target_id)
    if target is None:
        await callback.answer(t("admin_user_not_found", lang), show_alert=True)
        return
    await users_repo.set_status(session, target_id, UserStatus.ACTIVE)
    await session.commit()
    target = await users_repo.get_user(session, target_id)
    await callback.answer(t("admin_user_unbanned", lang), show_alert=True)
    if target is not None:
        await _edit_user_card(callback, session, target, lang)
