"""Админка настройки уровней пользователей."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.models.user_level import UserLevel
from database.repositories import user_levels as levels_repo
from locales.texts import get_lang, t
from permissions import is_admin
from settings import get_settings
from states.admin_levels import AdminLevelState

router = Router(name="admin_levels")


def _lang(user: User, event) -> str:
    return user.language_code or get_lang(getattr(event.from_user, "language_code", None))


async def _deny_cb(callback: CallbackQuery, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await callback.answer(t("admin_no_access", lang), show_alert=True)
    return True


async def _deny_msg(message: Message, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await message.answer(t("admin_no_access", lang))
    return True


async def _safe_edit(
    callback: CallbackQuery, text: str, *, reply_markup: InlineKeyboardMarkup
) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        raise


def _fmt(value: Decimal | int | None) -> str:
    value = Decimal(str(value or "0"))
    if value == value.to_integral_value():
        return str(int(value))
    return f"{value:f}".rstrip("0").rstrip(".")


def _parse_decimal(raw: str, *, percent: bool = False) -> Decimal | None:
    value = raw.strip().replace(",", ".").rstrip("%").strip()
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError):
        return None
    if amount < 0:
        return None
    if percent and amount > 100:
        return None
    return amount.quantize(Decimal("0.01"))


def _levels_keyboard(levels: list[UserLevel], lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for level in levels:
        status = "🟢" if int(level.active or 0) == 1 else "⚪"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {level.level}. {level.title or 'Уровень'}",
                callback_data=f"admin:levels:open:{level.level}",
            )
        )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:settings", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def _level_keyboard(level: UserLevel, lang: str) -> InlineKeyboardMarkup:
    level_no = int(level.level)
    active_key = "admin_levels_btn_disable" if int(level.active or 0) else "admin_levels_btn_enable"
    active_action = "disable" if int(level.active or 0) else "enable"
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_levels_btn_title", lang),
            callback_data=f"admin:levels:edit:title:{level_no}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_levels_btn_required", lang),
            callback_data=f"admin:levels:edit:required:{level_no}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_levels_btn_reward", lang),
            callback_data=f"admin:levels:edit:reward:{level_no}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_levels_btn_withdraw", lang),
            callback_data=f"admin:levels:edit:withdraw:{level_no}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_levels_btn_referral", lang),
            callback_data=f"admin:levels:edit:referral:{level_no}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t(active_key, lang),
            callback_data=f"admin:levels:{active_action}:{level_no}",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:settings:levels", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def _level_text(level: UserLevel, lang: str) -> str:
    status = t("admin_levels_status_on", lang) if int(level.active or 0) else t("admin_levels_status_off", lang)
    return t("admin_levels_detail", lang).format(
        level=level.level,
        title=level.title or "—",
        status=status,
        required=_fmt(level.required_win_bet_sum),
        reward=_fmt(level.balance_reward),
        withdraw=_fmt(level.withdraw_discount_percent),
        referral=_fmt(level.referral_bonus_percent),
    )


async def _render_list(
    callback: CallbackQuery, session: AsyncSession, lang: str
) -> None:
    levels = await levels_repo.list_levels(session)
    await _safe_edit(
        callback,
        t("admin_levels_title", lang),
        reply_markup=_levels_keyboard(levels, lang),
    )


async def _render_level(
    callback: CallbackQuery, session: AsyncSession, level_no: int, lang: str
) -> None:
    level = await levels_repo.get_level(session, level_no)
    if level is None:
        await callback.answer(t("admin_levels_not_found", lang), show_alert=True)
        await _render_list(callback, session, lang)
        return
    await _safe_edit(callback, _level_text(level, lang), reply_markup=_level_keyboard(level, lang))


@router.callback_query(F.data == "admin:settings:levels", F.message.chat.type == "private")
async def on_levels_open(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny_cb(callback, user, lang):
        return
    await state.clear()
    await _render_list(callback, session, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:levels:open:"), F.message.chat.type == "private")
async def on_level_open(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny_cb(callback, user, lang):
        return
    await state.clear()
    level_no = int(callback.data.split(":")[-1])
    await _render_level(callback, session, level_no, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:levels:edit:"), F.message.chat.type == "private")
async def on_level_edit(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny_cb(callback, user, lang):
        return
    parts = (callback.data or "").split(":")
    field = parts[-2]
    level_no = int(parts[-1])
    level = await levels_repo.get_level(session, level_no)
    if level is None:
        await callback.answer(t("admin_levels_not_found", lang), show_alert=True)
        return
    state_map = {
        "title": AdminLevelState.waiting_title,
        "required": AdminLevelState.waiting_required,
        "reward": AdminLevelState.waiting_reward,
        "withdraw": AdminLevelState.waiting_withdraw_discount,
        "referral": AdminLevelState.waiting_referral_bonus,
    }
    prompt_map = {
        "title": "admin_levels_prompt_title",
        "required": "admin_levels_prompt_required",
        "reward": "admin_levels_prompt_reward",
        "withdraw": "admin_levels_prompt_withdraw",
        "referral": "admin_levels_prompt_referral",
    }
    if field not in state_map:
        await callback.answer()
        return
    await state.set_state(state_map[field])
    await state.update_data(level_no=level_no)
    await _safe_edit(
        callback,
        t(prompt_map[field], lang).format(level=level_no),
        reply_markup=_level_keyboard(level, lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:levels:enable:"), F.message.chat.type == "private")
@router.callback_query(F.data.startswith("admin:levels:disable:"), F.message.chat.type == "private")
async def on_level_toggle(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny_cb(callback, user, lang):
        return
    await state.clear()
    parts = (callback.data or "").split(":")
    active = parts[-2] == "enable"
    level_no = int(parts[-1])
    await levels_repo.set_active(session, level_no, active=active)
    await session.commit()
    await _render_level(callback, session, level_no, lang)
    await callback.answer(t("admin_levels_saved", lang))


async def _level_from_state(
    message: Message, session: AsyncSession, state: FSMContext, lang: str
) -> UserLevel | None:
    data = await state.get_data()
    level_no = int(data.get("level_no") or 0)
    level = await levels_repo.get_level(session, level_no)
    if level is None:
        await state.clear()
        await message.answer(t("admin_levels_not_found", lang))
        return None
    return level


async def _send_updated_level(
    message: Message, level: UserLevel, lang: str
) -> None:
    await message.answer(
        _level_text(level, lang),
        reply_markup=_level_keyboard(level, lang),
    )


@router.message(StateFilter(AdminLevelState.waiting_title), F.chat.type == "private")
async def on_level_title_input(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, message)
    if await _deny_msg(message, user, lang):
        await state.clear()
        return
    level = await _level_from_state(message, session, state, lang)
    if level is None:
        return
    title = (message.text or "").strip()
    if not title:
        await message.answer(t("admin_levels_invalid_text", lang))
        return
    level = await levels_repo.set_title(session, int(level.level), title[:100])
    await session.commit()
    await state.clear()
    await message.answer(t("admin_levels_saved", lang))
    await _send_updated_level(message, level, lang)


async def _handle_decimal_input(
    message: Message,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    *,
    setter,
    percent: bool = False,
) -> None:
    lang = _lang(user, message)
    if await _deny_msg(message, user, lang):
        await state.clear()
        return
    level = await _level_from_state(message, session, state, lang)
    if level is None:
        return
    value = _parse_decimal(message.text or "", percent=percent)
    if value is None:
        await message.answer(
            t("admin_levels_invalid_percent" if percent else "admin_levels_invalid_amount", lang)
        )
        return
    level = await setter(session, int(level.level), value)
    await session.commit()
    await state.clear()
    await message.answer(t("admin_levels_saved", lang))
    await _send_updated_level(message, level, lang)


@router.message(StateFilter(AdminLevelState.waiting_required), F.chat.type == "private")
async def on_level_required_input(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _handle_decimal_input(
        message, session, user, state, setter=levels_repo.set_required_win_bet_sum
    )


@router.message(StateFilter(AdminLevelState.waiting_reward), F.chat.type == "private")
async def on_level_reward_input(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _handle_decimal_input(
        message, session, user, state, setter=levels_repo.set_balance_reward
    )


@router.message(StateFilter(AdminLevelState.waiting_withdraw_discount), F.chat.type == "private")
async def on_level_withdraw_input(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _handle_decimal_input(
        message, session, user, state, setter=levels_repo.set_withdraw_discount_percent, percent=True
    )


@router.message(StateFilter(AdminLevelState.waiting_referral_bonus), F.chat.type == "private")
async def on_level_referral_input(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    await _handle_decimal_input(
        message, session, user, state, setter=levels_repo.set_referral_bonus_percent, percent=True
    )
