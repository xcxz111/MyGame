"""Игра 21: меню, против бота (ЛС), PvP в подключённых чатах."""

from __future__ import annotations

import asyncio
import html
import logging
import time
from decimal import Decimal, InvalidOperation

from aiogram import Bot, F, Router
from aiogram.enums import ChatType, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session_maker
from database.models import User
from database.repositories import app_chats as app_chats_repo
from database.repositories import app_chat_allowed_topics as allowed_topics_repo
from database.repositories import forum_topics as forum_topics_repo
from database.repositories import game21_settings as g21_repo
from database.repositories import slot as slot_repo
from keyboards.game21 import (
    play21_busy_keyboard,
    play21_confirm_keyboard,
    play21_menu_keyboard,
    play21_pvp_accept_keyboard,
    play21_pvp_chat_pick_keyboard,
    play21_pvp_confirm_keyboard,
    play21_rules_back_keyboard,
    play21_pvp_topic_pick_keyboard,
)
from keyboards.main_menu import main_menu_keyboard
from locales.texts import get_lang, t
from services.forum_topic_allowlist import (
    filter_topic_rows,
    forum_topic_choice_possible,
    general_play_allowed,
)
from services.games.forum_thread import (
    format_forum_topic_display_label,
    edit_message_text_in_forum,
    thread_kw,
)
from services.game21 import bot_flow
from services.game21.active import pvp_busy_chat_id_for_user, user_in_any_game21
from services.game21.balance import METHOD_PVP_REFUND, METHOD_PVP_STAKE, add_balance, take_balance
from services.game21.formatting import fmt_money, name_link, possible_win_pvp
from services.game21.pvp_post import post_dual_search, unpin_general_message
from services.game21.pvp_runtime import (
    apply_pvp_stop,
    pvp_decide_first_prompt_html,
    pvp_match_card_html,
    pvp_match_general_channel_html,
)
from services.game21.pvp_state import (
    get_live,
    get_search,
    is_slot_busy,
    lock_for_chat,
    pop_search,
    slot_key,
    store_live,
    store_search,
    user_game21_lock,
)
from services.game21.pvp_search import arm_search_timeout, cancel_owner_pvp_search_now
from services.games.state import resolve_active_game_id
from settings import get_settings
from states.game21 import Play21BotState, Play21PvpState

logger = logging.getLogger(__name__)

router = Router(name="game21")


def _lang(user: User, ev) -> str:
    return user.language_code or get_lang(getattr(ev.from_user, "language_code", None))


async def _edit_text_skip_not_modified(message: Message, *args, **kwargs) -> None:
    try:
        await message.edit_text(*args, **kwargs)
    except TelegramBadRequest as exc:
        desc = (getattr(exc, "message", None) or str(exc)).lower()
        if "message is not modified" in desc:
            return
        raise


async def _edit_reply_markup_skip_not_modified(message: Message, **kwargs) -> None:
    try:
        await message.edit_reply_markup(**kwargs)
    except TelegramBadRequest as exc:
        desc = (getattr(exc, "message", None) or str(exc)).lower()
        if "message is not modified" in desc:
            return
        raise


async def _collect_pvp_chats(
    bot: Bot, session: AsyncSession, user_id: int
) -> list[tuple[int, str]]:
    rows = await app_chats_repo.get_all(session)
    out: list[tuple[int, str]] = []
    for c in rows:
        if not int(c.game21_users_enabled or 0):
            continue
        try:
            m = await bot.get_chat_member(c.chat_id, user_id)
            st = str(getattr(m, "status", "")).lower()
            if st in {"left", "kicked", "banned"}:
                continue
        except Exception:
            continue
        try:
            chat = await bot.get_chat(c.chat_id)
            title = (chat.title or str(c.chat_id))[:50]
        except Exception:
            title = str(c.chat_id)
        out.append((c.chat_id, title))
    return out


async def _pvp_enabled_rows(session: AsyncSession):
    rows = await app_chats_repo.get_all(session)
    return [c for c in rows if int(c.game21_users_enabled or 0)]


async def _try_resolve_invite_url(bot: Bot, chat_id: int, stored: str | None) -> str | None:
    if stored and str(stored).strip():
        return str(stored).strip()
    try:
        inv = await bot.create_chat_invite_link(chat_id=chat_id)
        return inv.invite_link
    except TelegramBadRequest:
        try:
            return await bot.export_chat_invite_link(chat_id=chat_id)
        except TelegramBadRequest:
            return None


async def _edit_message_not_in_pvp_chats(
    message: Message,
    *,
    bot: Bot,
    session: AsyncSession,
    lang: str,
    chat_ids: list[int] | None = None,
) -> None:
    rows_all = await _pvp_enabled_rows(session)
    if chat_ids is not None:
        want = {int(x) for x in chat_ids}
        rows = [r for r in rows_all if int(r.chat_id) in want]
        if not rows:
            rows = []
            for cid in want:
                r = await app_chats_repo.get_by_chat_id(session, cid)
                if r is not None:
                    rows.append(r)
    else:
        rows = rows_all
    title = html.escape(t("game21_pvp_not_member_title", lang))
    intro = html.escape(t("game21_pvp_not_member_intro", lang))
    body_lines = [f"<b>{title}</b>", "", intro, ""]
    for row in rows:
        cid = int(row.chat_id)
        try:
            cht = await bot.get_chat(cid)
            chat_title = html.escape((cht.title or str(cid))[:100])
        except Exception:
            chat_title = html.escape(str(cid))
        url = await _try_resolve_invite_url(bot, cid, row.chat_link)
        if url:
            body_lines.append(f'• <a href="{html.escape(url)}">{chat_title}</a>')
        else:
            body_lines.append(f"• {chat_title}")
    if not rows:
        body_lines.append(html.escape(t("game21_pvp_no_available_chat", lang)))
    await _edit_text_skip_not_modified(
        message,
        "\n".join(body_lines),
        parse_mode=ParseMode.HTML,
        reply_markup=play21_rules_back_keyboard(lang),
    )


async def _pvp_room_place_label(
    session: AsyncSession, lang: str, chat_id: int, thread_id: int | None
) -> str:
    if thread_id is None:
        return t("game21_pvp_topic_general", lang)
    topics = await forum_topics_repo.list_for_chat(session, chat_id)
    tid = int(thread_id)
    for top in topics:
        if int(top.message_thread_id) == tid:
            return format_forum_topic_display_label(
                lang, message_thread_id=tid, name=top.name or ""
            )
    return format_forum_topic_display_label(lang, message_thread_id=tid, name="")


async def _html_pvp_enter_bet_screen(
    bot: Bot,
    session: AsyncSession,
    lang: str,
    *,
    chat_id: int,
    thread_id: int | None,
    balance: Decimal,
) -> str:
    place = await _pvp_room_place_label(session, lang, chat_id, thread_id)
    esc_place = html.escape(place)
    url: str | None = None
    try:
        chat = await bot.get_chat(chat_id)
        uname = (getattr(chat, "username", None) or "").strip()
        if uname:
            if thread_id is not None:
                url = f"https://t.me/{uname}/{int(thread_id)}"
            else:
                url = f"https://t.me/{uname}"
    except Exception:
        pass
    if not url:
        row = await app_chats_repo.get_by_chat_id(session, chat_id)
        stored = str(row.chat_link).strip() if row and row.chat_link else None
        url = await _try_resolve_invite_url(bot, chat_id, stored)
    room_html = f'<a href="{html.escape(url)}">{esc_place}</a>' if url else esc_place
    balance_line = html.escape(
        t("welcome_balance", lang).format(balance=fmt_money(balance))
    )
    sub = t("game21_pvp_enter_bet", lang).format(room=room_html)
    return f"<b>{balance_line}</b>\n\n{sub}"


async def _present_pvp_after_chat_selected(
    message: Message,
    *,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    bot: Bot,
    lang: str,
    cid: int,
) -> str:
    """`topic` — показан выбор темы; `bet` — сразу ввод ставки; `restricted_empty` — нет разрешённых тем;
    `bad_chat` — чат недоступен."""
    try:
        chat = await bot.get_chat(cid)
        title = (chat.title or str(cid))[:80]
        is_forum = bool(getattr(chat, "is_forum", False))
    except Exception:
        return "bad_chat"
    topics = await forum_topics_repo.list_for_chat(session, cid)
    topic_rows = [(top.message_thread_id, top.name or "") for top in topics]
    allowed = await allowed_topics_repo.effective_allowed_public_threads(session, cid)
    filtered = filter_topic_rows(topic_rows, allowed)
    gen_ok = general_play_allowed(allowed)
    if forum_topic_choice_possible(
        is_forum=is_forum,
        filtered_topics=filtered,
        general_ok=gen_ok,
    ):
        await _edit_text_skip_not_modified(
            message,
            t("game21_pvp_choose_topic", lang),
            reply_markup=play21_pvp_topic_pick_keyboard(
                lang, chat_id=cid, topics=filtered, include_general=gen_ok
            ),
        )
        return "topic"
    if is_forum and allowed is not None and not filtered and not gen_ok:
        s = await g21_repo.get_settings(session)
        opts = await _collect_pvp_chats(bot, session, user.user_id)
        if len(opts) > 1:
            await _edit_text_skip_not_modified(
                message,
                t("game21_pvp_topics_restricted_empty", lang),
                reply_markup=play21_pvp_chat_pick_keyboard(lang, opts),
            )
        else:
            await _edit_text_skip_not_modified(
                message,
                t("game21_pvp_topics_restricted_empty", lang),
                reply_markup=play21_rules_back_keyboard(lang),
            )
        return "restricted_empty"
    await state.update_data(pvp_chat_id=cid, pvp_chat_title=title, pvp_thread_id=None)
    await state.set_state(Play21PvpState.waiting_bet)
    bal = user.balance if user.balance is not None else Decimal("0")
    body = await _html_pvp_enter_bet_screen(
        bot, session, lang, chat_id=cid, thread_id=None, balance=bal
    )
    await _edit_text_skip_not_modified(
        message,
        body,
        parse_mode=ParseMode.HTML,
        reply_markup=play21_rules_back_keyboard(lang),
    )
    return "bet"


def _game_notice(lang: str) -> str:
    return t("game21_active_notice", lang)


async def _busy_play21_screen_html(
    bot: Bot, session: AsyncSession, lang: str, user_id: int
) -> str:
    cid = pvp_busy_chat_id_for_user(user_id)
    if cid:
        row = await app_chats_repo.get_by_chat_id(session, cid)
        stored = str(row.chat_link).strip() if row and row.chat_link else None
        url = await _try_resolve_invite_url(bot, cid, stored)
        try:
            chat = await bot.get_chat(cid)
            title = (chat.title or str(cid))[:100]
        except Exception:
            title = str(cid)
        esc_title = html.escape(title)
        chat_html = f'<a href="{html.escape(url)}">{esc_title}</a>' if url else esc_title
        return t("game21_busy_screen_text", lang).format(chat=chat_html)
    if bot_flow.is_in_bot_game(user_id):
        return t("game21_busy_screen_text_bot", lang)
    return html.escape(t("game21_active_notice", lang))


async def _redraw_play21_main_menu(
    message: Message,
    *,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
    ev: CallbackQuery | Message,
) -> None:
    lang = _lang(user, ev)
    await state.clear()
    s = await g21_repo.get_settings(session)
    rows = await app_chats_repo.get_all(session)
    any_pvp = any(int(c.game21_users_enabled or 0) for c in rows)
    pvp_btn = bool(any_pvp)
    await _edit_text_skip_not_modified(
        message,
        t("game21_menu_title", lang),
        reply_markup=play21_menu_keyboard(
            lang, bot_on=bool(s.enabled_bot), pvp_on=bool(pvp_btn)
        ),
    )


async def _show_play21_busy(
    callback: CallbackQuery,
    session: AsyncSession,
    bot: Bot,
    lang: str,
    user_id: int,
    *,
    answer_callback: bool = True,
) -> None:
    show_cancel = get_search(user_id) is not None
    body = await _busy_play21_screen_html(bot, session, lang, user_id)
    await _edit_text_skip_not_modified(
        callback.message,
        body,
        parse_mode=ParseMode.HTML,
        reply_markup=play21_busy_keyboard(lang, show_cancel_search=show_cancel),
    )
    if answer_callback:
        await callback.answer()


@router.callback_query(F.data == "menu:play21bot:cancel:active", F.message.chat.type == "private")
async def on_play21_cancel_active(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    bot: Bot,
) -> None:
    lang = _lang(user, callback)
    if get_search(user.user_id) is None:
        await callback.answer(t("game21_no_active_search_to_cancel", lang), show_alert=True)
        return
    ok = await cancel_owner_pvp_search_now(bot, user.user_id)
    if not ok:
        await callback.answer(t("game21_no_active_search_to_cancel", lang), show_alert=True)
        if user_in_any_game21(user.user_id):
            await _show_play21_busy(
                callback, session, bot, lang, user.user_id, answer_callback=False
            )
        return
    await _redraw_play21_main_menu(
        callback.message,
        session=session,
        user=user,
        bot=bot,
        state=state,
        ev=callback,
    )
    await callback.answer(t("game21_active_cancelled_toast", lang))


@router.callback_query(F.data == "menu:play21bot", F.message.chat.type == "private")
async def on_play21_menu(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    state: FSMContext,
) -> None:
    lang = _lang(user, callback)
    if user_in_any_game21(user.user_id):
        await _show_play21_busy(callback, session, callback.bot, lang, user.user_id)
        return
    s = await g21_repo.get_settings(session)
    rows = await app_chats_repo.get_all(session)
    any_pvp = any(int(c.game21_users_enabled or 0) for c in rows)
    pvp_btn = bool(any_pvp)
    if not bool(s.enabled_bot) and not pvp_btn:
        await callback.answer(t("game21_coming_soon_all_off", lang), show_alert=True)
        return
    await _redraw_play21_main_menu(
        callback.message,
        session=session,
        user=user,
        bot=callback.bot,
        state=state,
        ev=callback,
    )
    await callback.answer()


@router.callback_query(F.data == "menu:play21bot:rules", F.message.chat.type == "private")
async def on_play21_rules(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _lang(user, callback)
    s = await g21_repo.get_settings(session)
    parts = []
    if s.enabled_bot:
        parts.append((g21_repo.rules_bot_for_lang(s, lang) or "").strip() or t("game21_rules_bot", lang))
    pvp_chats = await _collect_pvp_chats(bot, session, user.user_id)
    pvp_on = bool(pvp_chats)
    if pvp_on and pvp_chats:
        try:
            cid = pvp_chats[0][0]
            chat = await bot.get_chat(cid)
            ctitle = html.escape((chat.title or str(cid))[:80])
        except Exception:
            ctitle = "—"
        users_rules = (g21_repo.rules_users_for_lang(s, lang) or "").strip() or t("game21_rules_users", lang)
        try:
            users_rules = users_rules.format(chat_title=ctitle)
        except (KeyError, IndexError, ValueError):
            pass
        parts.append(users_rules)
    text = t("game21_rules_title", lang) + "\n\n" + ("\n\n".join(parts) if parts else t("game21_rules", lang))
    await _edit_text_skip_not_modified(callback.message, text, reply_markup=play21_rules_back_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "menu:play21bot:bot", F.message.chat.type == "private")
async def on_play21_bot(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    s = await g21_repo.get_settings(session)
    if not s.enabled_bot:
        await callback.answer(t("game21_coming_soon_play", lang), show_alert=True)
        return
    if user_in_any_game21(user.user_id):
        await _show_play21_busy(callback, session, callback.bot, lang, user.user_id)
        return
    await state.set_state(Play21BotState.waiting_bet)
    await state.update_data(bot_bet_prompt_mid=callback.message.message_id)
    await _edit_text_skip_not_modified(
        callback.message,
        t("game21_enter_bet", lang), reply_markup=play21_rules_back_keyboard(lang)
    )
    await callback.answer()


@router.message(StateFilter(Play21BotState.waiting_bet), F.chat.type == "private")
async def on_play21_bot_bet(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, message)
    raw = (message.text or "").strip().replace(",", ".").replace(" ", "")
    try:
        bet = Decimal(raw)
    except (InvalidOperation, ValueError):
        await message.answer(t("game21_bet_invalid", lang))
        return
    if bet <= 0:
        await message.answer(t("game21_bet_invalid", lang))
        return
    bet = bet.quantize(Decimal("0.01"))
    s = await g21_repo.get_settings(session)
    bal = user.balance or Decimal("0")
    if bal < bet:
        await message.answer(t("game21_not_enough_balance", lang))
        return
    c = s.commission_bot_percent or Decimal("0")
    win = possible_win_pvp(bet, c)
    await state.update_data(bet=str(bet), commission=str(c))
    await state.set_state(Play21BotState.waiting_confirm)
    await message.answer(
        t("game21_confirm_bet_with_win", lang).format(amount=fmt_money(bet), win=fmt_money(win)),
        reply_markup=play21_confirm_keyboard(lang),
    )
    data = await state.get_data()
    pmid = data.get("bot_bet_prompt_mid")
    if pmid is not None:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=int(pmid))
        except Exception:
            pass
        await state.update_data(bot_bet_prompt_mid=None)


@router.callback_query(
    F.data == "menu:play21bot:confirm:yes",
    F.message.chat.type == "private",
    StateFilter(Play21BotState.waiting_confirm),
)
async def on_play21_bot_confirm_yes(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    data = await state.get_data()
    bet = Decimal(str(data.get("bet") or "0"))
    c = Decimal(str(data.get("commission") or "0"))
    sm = get_session_maker()
    ok, err = await bot_flow.charge_and_start(bot, sm, user.user_id, bet, c, lang)
    if not ok:
        await callback.answer(t(err or "game21_not_enough_balance", lang), show_alert=True)
        await state.clear()
        return
    await state.clear()
    s = await g21_repo.get_settings(session)
    rules_bot_text = (g21_repo.rules_bot_for_lang(s, lang) or "").strip()
    await _edit_text_skip_not_modified(
        callback.message,
        t("game21_rules_title", lang) + "\n\n" + (rules_bot_text or t("game21_rules_bot", lang)),
        reply_markup=None,
    )
    await callback.answer()


@router.callback_query(F.data == "menu:play21bot:confirm:no", F.message.chat.type == "private")
async def on_play21_bot_confirm_no(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    await state.clear()
    menu_chats = await app_chats_repo.list_for_main_menu(session)
    show_game21 = await g21_repo.any_game21_enabled(session)
    show_slot = await slot_repo.is_enabled(session)
    await _edit_text_skip_not_modified(
        callback.message,
        t("game21_cancelled", lang),
        reply_markup=main_menu_keyboard(
            lang,
            user.user_id,
            get_settings().admin_id,
            menu_chats=menu_chats,
            show_game21=show_game21,
            show_slot=show_slot,
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:play21bot:stop", F.message.chat.type == "private")
async def on_play21_bot_stop(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _lang(user, callback)
    await bot_flow.on_stop_callback(bot, session, user.user_id, lang)
    await callback.answer()


@router.callback_query(F.data == "menu:play21bot:pvp", F.message.chat.type == "private")
async def on_play21_pvp_entry(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    if user_in_any_game21(user.user_id):
        await _show_play21_busy(callback, session, callback.bot, lang, user.user_id)
        return
    opts = await _collect_pvp_chats(bot, session, user.user_id)
    if not opts:
        await _edit_message_not_in_pvp_chats(
            callback.message, bot=bot, session=session, lang=lang, chat_ids=None
        )
        await callback.answer()
        return
    if len(opts) > 1:
        await _edit_text_skip_not_modified(
            callback.message,
            t("game21_pvp_choose_chat", lang),
            reply_markup=play21_pvp_chat_pick_keyboard(lang, opts),
        )
        await callback.answer()
        return
    cid, _title = opts[0]
    res = await _present_pvp_after_chat_selected(
        callback.message,
        session=session,
        user=user,
        state=state,
        bot=bot,
        lang=lang,
        cid=cid,
    )
    if res == "bad_chat":
        await callback.answer(t("game21_pvp_no_available_chat", lang), show_alert=True)
        return
    await callback.answer()


@router.callback_query(
    F.data.startswith("menu:play21bot:pvp:chat:"), F.message.chat.type == "private"
)
async def on_play21_pvp_chat(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    if user_in_any_game21(user.user_id):
        await _show_play21_busy(callback, session, callback.bot, lang, user.user_id)
        return
    try:
        cid = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer()
        return
    res = await _present_pvp_after_chat_selected(
        callback.message,
        session=session,
        user=user,
        state=state,
        bot=bot,
        lang=lang,
        cid=cid,
    )
    if res == "bad_chat":
        await callback.answer(t("game21_pvp_no_available_chat", lang), show_alert=True)
        return
    await callback.answer()


@router.callback_query(
    F.data.startswith("menu:play21bot:pvp:th:"), F.message.chat.type == "private"
)
async def on_play21_pvp_topic(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    parts = callback.data.split(":")
    if len(parts) < 6:
        await callback.answer()
        return
    try:
        cid = int(parts[4])
        tid = int(parts[5])
    except ValueError:
        await callback.answer()
        return
    thread_id = None if tid == 0 else tid
    if not await allowed_topics_repo.is_allowed_public(session, cid, thread_id):
        await callback.answer(t("game21_pvp_topic_forbidden", lang), show_alert=True)
        return
    if is_slot_busy(cid, thread_id):
        await callback.answer(t("game21_pvp_main_active_exists", lang), show_alert=True)
        return
    try:
        chat = await bot.get_chat(cid)
        title = (chat.title or str(cid))[:80]
    except Exception:
        await callback.answer()
        return
    await state.update_data(pvp_chat_id=cid, pvp_chat_title=title, pvp_thread_id=thread_id)
    await state.set_state(Play21PvpState.waiting_bet)
    bal = user.balance if user.balance is not None else Decimal("0")
    body = await _html_pvp_enter_bet_screen(
        bot, session, lang, chat_id=cid, thread_id=thread_id, balance=bal
    )
    await _edit_text_skip_not_modified(
        callback.message,
        body,
        parse_mode=ParseMode.HTML,
        reply_markup=play21_rules_back_keyboard(lang),
    )
    await callback.answer()


@router.message(StateFilter(Play21PvpState.waiting_bet), F.chat.type == "private")
async def on_play21_pvp_bet(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, message)
    data = await state.get_data()
    cid = int(data.get("pvp_chat_id") or 0)
    if not cid:
        await state.clear()
        return
    raw = (message.text or "").strip().replace(",", ".").replace(" ", "")
    try:
        bet = Decimal(raw)
    except (InvalidOperation, ValueError):
        await message.answer(t("game21_bet_invalid", lang))
        return
    if bet <= 0:
        await message.answer(t("game21_bet_invalid", lang))
        return
    bet = bet.quantize(Decimal("0.01"))
    bal = user.balance or Decimal("0")
    if bal < bet:
        await message.answer(t("game21_not_enough_balance", lang))
        return
    s = await g21_repo.get_settings(session)
    c = s.commission_users_percent or Decimal("0")
    win = possible_win_pvp(bet, c)
    await state.update_data(bet=str(bet), commission=str(c))
    await state.set_state(Play21PvpState.waiting_confirm)
    await message.answer(
        t("game21_pvp_confirm", lang).format(amount=fmt_money(bet), win=fmt_money(win)),
        reply_markup=play21_pvp_confirm_keyboard(lang),
    )


@router.callback_query(F.data == "menu:play21bot:pvp:confirm:no", F.message.chat.type == "private")
async def on_pvp_confirm_no(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    await state.clear()
    s = await g21_repo.get_settings(session)
    rows = await app_chats_repo.get_all(session)
    any_pvp = any(int(c.game21_users_enabled or 0) for c in rows)
    pvp_btn = bool(any_pvp)
    await _edit_text_skip_not_modified(
        callback.message,
        t("game21_cancelled", lang),
        reply_markup=play21_menu_keyboard(
            lang, bot_on=bool(s.enabled_bot), pvp_on=bool(pvp_btn)
        ),
    )
    await callback.answer()


@router.callback_query(
    F.data == "menu:play21bot:pvp:confirm:yes",
    F.message.chat.type == "private",
    StateFilter(Play21PvpState.waiting_confirm),
)
async def on_pvp_confirm_yes(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    data = await state.get_data()
    game_chat_id = int(data.get("pvp_chat_id") or 0)
    thread_id = data.get("pvp_thread_id")
    if thread_id is not None:
        thread_id = int(thread_id)
    bet = Decimal(str(data.get("bet") or "0"))
    c = Decimal(str(data.get("commission") or "0"))
    if not game_chat_id or bet <= 0:
        await state.clear()
        await callback.answer()
        return
    try:
        m = await bot.get_chat_member(game_chat_id, user.user_id)
        st = str(getattr(m, "status", "")).lower()
        if st in {"left", "kicked", "banned"}:
            await state.clear()
            await _edit_message_not_in_pvp_chats(
                callback.message,
                bot=bot,
                session=session,
                lang=lang,
                chat_ids=[game_chat_id],
            )
            await callback.answer()
            return
    except Exception:
        await state.clear()
        await _edit_message_not_in_pvp_chats(
            callback.message,
            bot=bot,
            session=session,
            lang=lang,
            chat_ids=[game_chat_id],
        )
        await callback.answer()
        return
    if resolve_active_game_id(game_chat_id, thread_id):
        await callback.answer(t("game21_pvp_main_active_exists", lang), show_alert=True)
        return
    sk = slot_key(game_chat_id, thread_id)
    lock = lock_for_chat(game_chat_id, thread_id)
    async with user_game21_lock(user.user_id):
        async with lock:
            if get_live(sk):
                await callback.answer(t("game21_pvp_active_exists", lang), show_alert=True)
                return
            if user_in_any_game21(user.user_id):
                await callback.answer(t("game21_active_notice", lang), show_alert=True)
                return
            ok = await take_balance(session, user.user_id, bet, method=METHOD_PVP_STAKE)
            if not ok:
                await callback.answer(t("game21_not_enough_balance", lang), show_alert=True)
                return
            owner_name = (
                (callback.from_user.full_name or callback.from_user.username or str(user.user_id)).strip()
            )
            store_search(
                user.user_id,
                {
                    "owner_user_id": user.user_id,
                    "bet_amount": bet,
                    "commission_percent": c,
                    "chat_id": game_chat_id,
                    "message_thread_id": thread_id,
                    "message_id": None,
                    "message_id_general": None,
                    "search_timeout_token": 0,
                    "lang": lang,
                    "owner_name": owner_name,
                },
            )
            await session.commit()

    kb = play21_pvp_accept_keyboard(lang, user.user_id)
    mid_t, mid_g = await post_dual_search(
        bot,
        chat_id=game_chat_id,
        message_thread_id=thread_id,
        lang=lang,
        owner_id=user.user_id,
        owner_name=owner_name,
        bet=bet,
        commission_percent=c,
        accept_markup=kb,
    )
    if mid_t is None:
        async with user_game21_lock(user.user_id):
            async with lock:
                pop_search(user.user_id)
        await add_balance(session, user.user_id, bet, method=METHOD_PVP_REFUND)
        await session.commit()
        await state.clear()
        await callback.answer(t("game21_pvp_search_post_failed", lang), show_alert=True)
        return

    token = int(time.time() * 1000)
    async with user_game21_lock(user.user_id):
        async with lock:
            meta = get_search(user.user_id)
            if meta:
                meta["message_id"] = mid_t
                meta["message_id_general"] = mid_g
                meta["search_timeout_token"] = token
                store_search(user.user_id, meta)

    await state.clear()
    asyncio.create_task(arm_search_timeout(bot, user.user_id, token))
    s = await g21_repo.get_settings(session)
    rows = await app_chats_repo.get_all(session)
    any_pvp = any(int(x.game21_users_enabled or 0) for x in rows)
    pvp_btn = bool(any_pvp)
    await _edit_text_skip_not_modified(
        callback.message,
        t("game21_pvp_search_started", lang).format(amount=fmt_money(bet)),
        reply_markup=play21_menu_keyboard(
            lang, bot_on=bool(s.enabled_bot), pvp_on=bool(pvp_btn)
        ),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("menu:play21bot:pvp:accept:"),
    F.message.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def on_pvp_accept(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _lang(user, callback)
    parts = callback.data.split(":")
    if len(parts) < 5:
        await callback.answer()
        return
    try:
        owner_id = int(parts[4])
    except ValueError:
        await callback.answer()
        return
    if callback.from_user.id == owner_id:
        await callback.answer(t("game21_pvp_self_accept_forbidden", lang), show_alert=True)
        return
    if user_in_any_game21(callback.from_user.id):
        await callback.answer(_game_notice(lang), show_alert=True)
        return
    req = get_search(owner_id)
    if not req:
        await callback.answer(t("game21_cancelled", lang), show_alert=True)
        return
    snap = dict(req)
    game_chat_id = int(snap.get("chat_id") or 0)
    thread_id = snap.get("message_thread_id")
    if thread_id is not None:
        thread_id = int(thread_id)
    sk = slot_key(game_chat_id, thread_id)
    bet = Decimal(str(snap.get("bet_amount") or "0"))
    lock = lock_for_chat(game_chat_id, thread_id)
    async with user_game21_lock(callback.from_user.id):
        async with lock:
            req = get_search(owner_id)
            if not req:
                await callback.answer(t("game21_cancelled", lang), show_alert=True)
                return
            if get_live(sk):
                await callback.answer(t("game21_pvp_active_exists", lang), show_alert=True)
                return
            if user_in_any_game21(callback.from_user.id):
                await callback.answer(_game_notice(lang), show_alert=True)
                return
            ok = await take_balance(session, callback.from_user.id, bet, method=METHOD_PVP_STAKE)
            if not ok:
                await callback.answer(t("game21_not_enough_balance", lang), show_alert=True)
                return
            commission = Decimal(str(snap.get("commission_percent") or "0"))
            owner_name = str(snap.get("owner_name") or str(owner_id))
            second_name = (
                (callback.from_user.full_name or callback.from_user.username or str(callback.from_user.id)).strip()
            )
            game_lang = snap.get("lang") or lang
            tok = time.time_ns()
            st_live = {
                "owner_id": owner_id,
                "player1_id": owner_id,
                "player2_id": callback.from_user.id,
                "chat_id": game_chat_id,
                "message_thread_id": thread_id,
                "bet_amount": bet,
                "commission_percent": commission,
                "phase": "decide_first",
                "decide_rolls": {},
                "lang": game_lang,
                "names": {owner_id: owner_name, callback.from_user.id: second_name},
                "search_message_id_topic": snap.get("message_id"),
                "search_message_id_general": snap.get("message_id_general"),
                "status_message_id": None,
                "first_turn_uid": None,
                "throw_order_seq": 0,
                "round_events": [],
                "pvp_session_token": tok,
                "finished": False,
            }
            pop_search(owner_id)
            store_live(sk, st_live)
    await session.commit()

    mid_topic = int(snap.get("message_id") or 0)
    mid_gen_raw = snap.get("message_id_general")
    mid_gen = int(mid_gen_raw) if mid_gen_raw is not None else None

    st_board = get_live(sk) or {}
    room_lbl = await _pvp_room_place_label(session, game_lang, game_chat_id, thread_id)
    card = pvp_match_card_html(game_lang, st_board)
    card_general = pvp_match_general_channel_html(game_lang, st_board, room_label=room_lbl)

    edited_mids: set[int] = set()
    if mid_gen:
        try:
            await edit_message_text_in_forum(
                bot,
                chat_id=game_chat_id,
                message_id=mid_gen,
                text=card_general,
                message_thread_id=None,
                parse_mode=ParseMode.HTML,
                reply_markup=None,
            )
            edited_mids.add(mid_gen)
        except Exception as exc:
            logger.warning("pvp edit search general: %s", exc)
    if mid_topic:
        try:
            await edit_message_text_in_forum(
                bot,
                chat_id=game_chat_id,
                message_id=mid_topic,
                text=card,
                message_thread_id=thread_id,
                parse_mode=ParseMode.HTML,
                reply_markup=None,
            )
            edited_mids.add(mid_topic)
        except Exception as exc:
            logger.warning("pvp edit search topic: %s", exc)

    cb_msg = callback.message
    if cb_msg and int(cb_msg.message_id) not in edited_mids:
        await _edit_reply_markup_skip_not_modified(cb_msg, reply_markup=None)

    await unpin_general_message(bot, chat_id=game_chat_id, message_id=snap.get("message_id_general"))

    status_mid = int(mid_topic or mid_gen or 0)
    if status_mid:
        st_upd = get_live(sk) or {}
        st_upd["status_message_id"] = status_mid
        store_live(sk, st_upd)
    if st_board:
        await bot.send_message(
            game_chat_id,
            pvp_decide_first_prompt_html(game_lang, st_board),
            message_thread_id=thread_id,
            parse_mode=ParseMode.HTML,
        )
    await callback.answer()


@router.callback_query(
    F.data.startswith("menu:play21bot:pvp:stop:"),
    F.message.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def on_pvp_stop_cb(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _lang(user, callback)
    sm = get_session_maker()
    await apply_pvp_stop(bot, sm, callback, lang)


@router.message(F.chat.type == "private", F.dice.emoji == "🎲", ~F.from_user.is_bot)
async def on_private_dice_21(
    message: Message, session: AsyncSession, user: User, bot: Bot
) -> None:
    if await bot_flow.handle_private_dice(bot, session, message):
        return


# game21_fee in admin_payments
