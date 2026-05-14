"""Игра «Слот» (аналог casino из Game_bot, но с названием Слот)."""

from __future__ import annotations

import asyncio
from decimal import Decimal, InvalidOperation

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import fees as fees_repo
from database.repositories import slot as slot_repo
from database.repositories import user_levels as user_levels_repo
from database.repositories import users as users_repo
from locales.texts import get_lang, t
from permissions import is_admin
from services.game21.balance import add_balance, get_balance, take_balance
from services.games.busy import user_in_any_interactive_game
from services.slot import decode_line, fmt_money, fmt_multiplier, multiplier_for, payout_for
from settings import get_settings
from states.slot import SlotAdminRulesState, SlotState

router = Router(name="slot")

METHOD_SLOT_STAKE = "game:slot:stake"
METHOD_SLOT_WIN = "game:slot:win"

_locks: dict[int, asyncio.Lock] = {}


def _lock(uid: int) -> asyncio.Lock:
    lo = _locks.get(uid)
    if lo is None:
        lo = asyncio.Lock()
        _locks[uid] = lo
    return lo


def _lang(user: User, event) -> str:
    return user.language_code or get_lang(getattr(event.from_user, "language_code", None))


def _main_keyboard(lang: str) -> InlineKeyboardMarkup:
    label = t("btn_main", lang)
    if lang == "ru":
        label = "Главная"
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data="menu:main")]]
    )


async def _slot_prompt_text(session: AsyncSession, lang: str, user_id: int) -> str:
    balance = await get_balance(session, user_id)
    settings = await slot_repo.get_settings(session)
    rules = (settings.rules_text or "").strip() or t("slot_rules_block", lang)
    return (
        rules
        + "\n\n"
        + t("slot_enter_bet_with_balance", lang).format(balance=fmt_money(balance))
    )


def _admin_slot_keyboard(lang: str, *, enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_slot_btn_disable" if enabled else "admin_slot_btn_enable", lang),
            callback_data="admin:casino:toggle",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_slot_btn_rules", lang),
            callback_data="admin:casino:rules",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:admin", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


async def _render_admin_slot(callback: CallbackQuery, session: AsyncSession, lang: str) -> None:
    settings = await slot_repo.get_settings(session)
    st = await slot_repo.get_stats(session)
    enabled = bool(settings.enabled)
    await callback.message.edit_text(
        t("admin_slot_mode_text", lang).format(
            status=t("admin_21_on" if enabled else "admin_21_off", lang),
            total_games=st["total_games"],
            unique_users=st["unique_users"],
            users_won_sum=fmt_money(st["users_won_sum"]),
            users_lost_sum=fmt_money(st["users_lost_sum"]),
            bot_profit_sum=fmt_money(st["bot_profit_sum"]),
        ),
        reply_markup=_admin_slot_keyboard(lang, enabled=enabled),
    )


def _combo_label(lang: str, slot_value: int) -> str:
    uniq = len(set(decode_line(slot_value)))
    if uniq == 1:
        return t("slot_combo_three", lang)
    if uniq == 2:
        return t("slot_combo_two", lang)
    return t("slot_combo_none", lang)


@router.callback_query(F.data == "menu:casino", F.message.chat.type == ChatType.PRIVATE)
async def on_slot_menu(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if user_in_any_interactive_game(user.user_id):
        await callback.answer(t("checkers_active_notice", lang), show_alert=True)
        return
    if not await slot_repo.is_enabled(session):
        await callback.answer(t("slot_disabled", lang), show_alert=True)
        return
    await state.set_state(SlotState.waiting_bet)
    await callback.message.edit_text(
        await _slot_prompt_text(session, lang, user.user_id),
        reply_markup=_main_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(SlotState.waiting_bet), F.chat.type == ChatType.PRIVATE)
async def on_slot_bet(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, message)
    raw = (message.text or "").strip().replace(",", ".").replace(" ", "")
    try:
        bet = Decimal(raw).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        await message.answer(t("slot_bet_invalid", lang))
        await message.answer(
            await _slot_prompt_text(session, lang, user.user_id),
            reply_markup=_main_keyboard(lang),
        )
        return
    if bet <= 0:
        await message.answer(t("slot_bet_invalid", lang))
        await message.answer(
            await _slot_prompt_text(session, lang, user.user_id),
            reply_markup=_main_keyboard(lang),
        )
        return
    balance = await get_balance(session, user.user_id)
    if balance < bet:
        await message.answer(t("slot_not_enough_balance", lang))
        await message.answer(
            await _slot_prompt_text(session, lang, user.user_id),
            reply_markup=_main_keyboard(lang),
        )
        return
    await state.set_state(SlotState.waiting_spin)
    await state.update_data(bet=str(bet))
    await message.answer(
        t("slot_spin_prompt", lang).format(
            balance=fmt_money(balance),
            amount=fmt_money(bet),
        ),
        reply_markup=_main_keyboard(lang),
    )


@router.message(StateFilter(SlotState.waiting_spin), F.chat.type == ChatType.PRIVATE, F.dice.emoji == "🎰")
async def on_slot_spin(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, message)
    data = await state.get_data()
    bet = Decimal(str(data.get("bet") or "0")).quantize(Decimal("0.01"))
    uid = int(user.user_id)
    async with _lock(uid):
        if bet <= 0:
            await state.set_state(SlotState.waiting_bet)
            await message.answer(t("slot_bet_invalid", lang), reply_markup=_main_keyboard(lang))
            return
        ok = await take_balance(session, uid, bet, method=METHOD_SLOT_STAKE)
        if not ok:
            await state.set_state(SlotState.waiting_bet)
            await session.rollback()
            await message.answer(t("slot_not_enough_balance", lang), reply_markup=_main_keyboard(lang))
            return

        slot_value = int(message.dice.value or 0)
        multiplier = multiplier_for(slot_value)
        commission = await fees_repo.get_slot_percent(session)
        payout = payout_for(bet, multiplier, commission)
        if payout > 0:
            await add_balance(session, uid, payout, method=METHOD_SLOT_WIN)
            await user_levels_repo.add_winning_bet_progress(
                session,
                user_id=uid,
                bet_amount=bet,
                source="game:slot",
            )
        await slot_repo.add_spin(
            session,
            user_id=uid,
            bet_amount=bet,
            slot_value=slot_value,
            multiplier=multiplier,
            commission_percent=commission,
            payout=payout,
        )
        bot_profit = (bet - payout).quantize(Decimal("0.01"))
        await users_repo.award_referral_percent(
            session,
            referral_id=uid,
            base_amount=bot_profit,
            source="game:slot",
        )
        await session.commit()
        await state.set_state(SlotState.waiting_spin)
        await state.update_data(bet=str(bet))

    balance_after = await get_balance(session, uid)
    combo = _combo_label(lang, slot_value)
    if payout > 0:
        text = t("slot_result_win", lang).format(
            balance=fmt_money(balance_after),
            combo=combo,
            bet=fmt_money(bet),
            mult=fmt_multiplier(multiplier),
            payout=fmt_money(payout),
        )
    else:
        text = t("slot_result_lose", lang).format(
            balance=fmt_money(balance_after),
            combo=combo,
            bet=fmt_money(bet),
        )
    await message.answer(text, reply_markup=_main_keyboard(lang))


@router.callback_query(F.data == "admin:casino", F.message.chat.type == ChatType.PRIVATE)
async def on_admin_slot_stats(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if not is_admin(user, get_settings()):
        await callback.answer(t("admin_no_access", lang), show_alert=True)
        return
    await state.clear()
    await _render_admin_slot(callback, session, lang)
    await callback.answer()


@router.callback_query(F.data == "admin:casino:toggle", F.message.chat.type == ChatType.PRIVATE)
async def on_admin_slot_toggle(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _lang(user, callback)
    if not is_admin(user, get_settings()):
        await callback.answer(t("admin_no_access", lang), show_alert=True)
        return
    settings = await slot_repo.get_settings(session)
    await slot_repo.set_enabled(session, not bool(settings.enabled))
    await session.commit()
    await _render_admin_slot(callback, session, lang)
    await callback.answer()


@router.callback_query(F.data == "admin:casino:rules", F.message.chat.type == ChatType.PRIVATE)
async def on_admin_slot_rules(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if not is_admin(user, get_settings()):
        await callback.answer(t("admin_no_access", lang), show_alert=True)
        return
    settings = await slot_repo.get_settings(session)
    await state.set_state(SlotAdminRulesState.waiting_text)
    current = (settings.rules_text or "").strip()
    text = t("admin_slot_rules_prompt", lang)
    if current:
        text += "\n\n" + t("admin_slot_rules_current", lang).format(rules=current)
    await callback.message.edit_text(
        text,
        reply_markup=None,
    )
    await callback.answer()


@router.message(StateFilter(SlotAdminRulesState.waiting_text), F.chat.type == ChatType.PRIVATE)
async def on_admin_slot_rules_text(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = user.language_code or get_lang(message.from_user.language_code)
    if not is_admin(user, get_settings()):
        await message.answer(t("admin_no_access", lang))
        await state.clear()
        return
    text = (message.text or "").strip()
    if not text:
        await message.answer(t("admin_slot_rules_empty", lang))
        return
    await slot_repo.set_rules(session, text)
    await session.commit()
    await state.clear()
    settings = await slot_repo.get_settings(session)
    await message.answer(
        t("admin_slot_rules_saved", lang),
        reply_markup=_admin_slot_keyboard(lang, enabled=bool(settings.enabled)),
    )
