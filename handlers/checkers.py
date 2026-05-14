"""PvP шашки в группах/темах."""

from __future__ import annotations

import asyncio
import html
import time
from decimal import Decimal, InvalidOperation

from aiogram import Bot, F, Router
from aiogram.enums import ChatType, ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session_maker
from database.models import User
from database.repositories import app_chat_allowed_topics as allowed_topics_repo
from database.repositories import app_chats as app_chats_repo
from database.repositories import checkers as checkers_repo
from database.repositories import forum_topics as forum_topics_repo
from database.repositories import user_levels as user_levels_repo
from database.repositories import users as users_repo
from keyboards.checkers import (
    board_keyboard,
    checkers_accept_keyboard,
    checkers_busy_keyboard,
    checkers_chat_pick_keyboard,
    checkers_confirm_keyboard,
    checkers_main_keyboard,
    checkers_topic_pick_keyboard,
)
from locales.texts import get_lang, t
from services.checkers import engine
from services.checkers.state import (
    get_live,
    get_search,
    lock_for_chat,
    pop_live,
    pop_search,
    slot_key,
    store_live,
    store_search,
    user_lock,
)
from services.game21.balance import add_balance, get_balance, take_balance
from services.game21.formatting import fmt_money, name_link, possible_win_pvp
from services.games.busy import (
    slot_busy_for_new_game,
    slot_busy_outside_checkers,
    user_in_any_interactive_game,
)
from services.games.forum_thread import (
    edit_message_text_in_forum,
    format_forum_topic_display_label,
    pin_chat_message_in_forum,
    thread_kw,
    unpin_chat_message_in_forum,
)
from services.user_levels import ensure_level_tag
from states.checkers import CheckersState

router = Router(name="checkers")

METHOD_CHECKERS_STAKE = "game:checkers:stake"
METHOD_CHECKERS_WIN = "game:checkers:win"
METHOD_CHECKERS_REFUND = "game:checkers:refund"
MIN_BOARD_EDIT_INTERVAL = 1.2
TURN_WARNING_AFTER = 60
TURN_TIMEOUT_AFTER = 120
_turn_timeout_tasks: dict[tuple[int, int], asyncio.Task] = {}


def _lang(user: User, event) -> str:
    return user.language_code or get_lang(getattr(event.from_user, "language_code", None))


def _turn_user_id(st: dict) -> int:
    side = st.get("turn_side") or "w"
    key = "white_user_id" if side == "w" else "black_user_id"
    uid = int(st.get(key) or 0)
    return uid or int(st.get("turn_user_id") or 0)


def _opponent_user_id(st: dict, user_id: int) -> int:
    white = int(st.get("white_user_id") or 0)
    black = int(st.get("black_user_id") or 0)
    return black if int(user_id) == white else white


async def _safe_edit_message(bot: Bot, st: dict, text: str, *, reply_markup=None) -> bool:
    now = time.time()
    blocked_until = max(
        float(st.get("edit_blocked_until") or 0),
        float(st.get("next_edit_allowed_at") or 0),
    )
    if blocked_until and now < blocked_until:
        return False
    try:
        await bot.edit_message_text(
            chat_id=int(st["chat_id"]),
            message_id=int(st["board_message_id"]),
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
        )
        st["next_edit_allowed_at"] = time.time() + MIN_BOARD_EDIT_INTERVAL
        return True
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return False
        raise
    except TelegramRetryAfter as exc:
        st["edit_blocked_until"] = time.time() + float(getattr(exc, "retry_after", 30) or 30)
        return False


def _edit_wait_seconds(st: dict) -> int:
    blocked_until = max(
        float(st.get("edit_blocked_until") or 0),
        float(st.get("next_edit_allowed_at") or 0),
    )
    remaining = blocked_until - time.time()
    if remaining <= 0:
        return 0
    return max(1, int(remaining + 0.999))


async def _answer_if_edit_blocked(callback: CallbackQuery, st: dict) -> bool:
    seconds = _edit_wait_seconds(st)
    if seconds <= 0:
        return False
    await callback.answer(
        t("checkers_flood_wait", st.get("lang") or "ru").format(seconds=seconds),
        show_alert=True,
    )
    return True


def _checkers_player_lines(st: dict) -> tuple[str, str]:
    names = st.get("names") or {}
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    return (
        name_link(p1, str(names.get(p1, p1))),
        name_link(p2, str(names.get(p2, p2))),
    )


def _checkers_match_card_html(lang: str, st: dict) -> str:
    p1_h, p2_h = _checkers_player_lines(st)
    bet = Decimal(str(st.get("bet_amount") or "0"))
    commission = Decimal(str(st.get("commission_percent") or "0"))
    win_str = fmt_money(possible_win_pvp(bet, commission))
    rules = html.escape((st.get("rules_text") or "").strip() or t("checkers_rules_body", lang))
    return (
        f"<b>{html.escape(t('checkers_match_title', lang))}</b>\n"
        f"{p1_h}\n"
        f"{p2_h}\n\n"
        f"{t('checkers_match_prize', lang).format(win=html.escape(win_str))}\n\n"
        f"<b>{html.escape(t('checkers_match_rules_heading', lang))}</b>\n"
        f"<blockquote>{rules}</blockquote>"
    )


def _checkers_match_general_html(lang: str, st: dict, *, room_label: str) -> str:
    p1_h, p2_h = _checkers_player_lines(st)
    bet = Decimal(str(st.get("bet_amount") or "0"))
    commission = Decimal(str(st.get("commission_percent") or "0"))
    win_str = fmt_money(possible_win_pvp(bet, commission))
    head = t("checkers_match_started_in_topic", lang).format(room=html.escape(room_label))
    return (
        f"<b>{head}</b>\n"
        f"{p1_h}\n"
        f"{p2_h}\n\n"
        f"{t('checkers_match_prize', lang).format(win=html.escape(win_str))}"
    )


async def _edit_search_messages_accepted(
    bot: Bot, st: dict, *, callback_message: Message | None = None
) -> None:
    chat_id = int(st["chat_id"])
    thread_id = st.get("message_thread_id")
    lang = st.get("lang") or "ru"
    text_topic = _checkers_match_card_html(lang, st)
    text_general = _checkers_match_general_html(
        lang,
        st,
        room_label=str(st.get("room_label") or t("game21_pvp_topic_general", lang)),
    )
    edited_mids: set[int] = set()
    mid_general = st.get("search_message_id_general")
    if mid_general:
        try:
            await edit_message_text_in_forum(
                bot,
                chat_id=chat_id,
                message_id=int(mid_general),
                text=text_general,
                message_thread_id=None,
                parse_mode=ParseMode.HTML,
                reply_markup=None,
            )
            edited_mids.add(int(mid_general))
        except Exception:
            pass
    mid_topic = st.get("search_message_id_topic")
    if mid_topic:
        try:
            await edit_message_text_in_forum(
                bot,
                chat_id=chat_id,
                message_id=int(mid_topic),
                text=text_topic,
                message_thread_id=thread_id,
                parse_mode=ParseMode.HTML,
                reply_markup=None,
            )
            edited_mids.add(int(mid_topic))
        except Exception:
            pass
    if callback_message and int(callback_message.message_id) not in edited_mids:
        try:
            await callback_message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest as exc:
            if "message is not modified" not in str(exc).lower():
                raise
        except Exception:
            pass
    if mid_general:
        try:
            await unpin_chat_message_in_forum(
                bot,
                chat_id=chat_id,
                message_id=int(mid_general),
                message_thread_id=None,
            )
        except Exception:
            pass


def _cancel_turn_timer(sk: tuple[int, int]) -> None:
    task = _turn_timeout_tasks.pop(sk, None)
    if task and not task.done() and task is not asyncio.current_task():
        task.cancel()


async def _delete_turn_warning(bot: Bot, st: dict) -> None:
    mid = st.get("turn_warning_message_id")
    if not mid:
        return
    try:
        await bot.delete_message(int(st["chat_id"]), int(mid))
    except Exception:
        pass
    st["turn_warning_message_id"] = None


async def _clear_turn_timer(bot: Bot, sk: tuple[int, int], st: dict) -> None:
    _cancel_turn_timer(sk)
    await _delete_turn_warning(bot, st)


def _schedule_turn_timer(bot: Bot, sk: tuple[int, int], st: dict) -> None:
    _cancel_turn_timer(sk)
    token = int(st.get("turn_timer_token") or 0) + 1
    st["turn_timer_token"] = token
    store_live(sk, st)
    _turn_timeout_tasks[sk] = asyncio.create_task(_run_turn_timer(bot, sk, token))


async def _run_turn_timer(bot: Bot, sk: tuple[int, int], token: int) -> None:
    try:
        await asyncio.sleep(TURN_WARNING_AFTER)
        async with lock_for_chat(sk[0], sk[1] or None):
            st = get_live(sk) or {}
            if (
                not st
                or st.get("finished")
                or st.get("phase") != "playing"
                or int(st.get("turn_timer_token") or 0) != token
            ):
                return
            names = st.get("names") or {}
            uid = _turn_user_id(st)
            try:
                msg = await bot.send_message(
                    int(st["chat_id"]),
                    t("checkers_turn_timeout_warning", st.get("lang") or "ru").format(
                        name=name_link(uid, str(names.get(uid, uid)))
                    ),
                    parse_mode=ParseMode.HTML,
                    **thread_kw(st.get("message_thread_id")),
                )
                st["turn_warning_message_id"] = msg.message_id
                store_live(sk, st)
            except Exception:
                pass
        await asyncio.sleep(TURN_TIMEOUT_AFTER - TURN_WARNING_AFTER)
        async with lock_for_chat(sk[0], sk[1] or None):
            st = get_live(sk) or {}
            if (
                not st
                or st.get("finished")
                or st.get("phase") != "playing"
                or int(st.get("turn_timer_token") or 0) != token
            ):
                return
            loser_id = _turn_user_id(st)
            winner_id = _opponent_user_id(st, loser_id)
            await _finish_checkers(bot, sk, winner_id=winner_id, timeout_loser_id=loser_id)
    except asyncio.CancelledError:
        return


def _status_text(st: dict) -> str:
    names = st.get("names") or {}
    turn_uid = _turn_user_id(st)
    st["turn_user_id"] = turn_uid
    white_uid = int(st.get("white_user_id") or 0)
    black_uid = int(st.get("black_user_id") or 0)
    return t("checkers_board_text", st.get("lang") or "ru").format(
        white=name_link(white_uid, str(names.get(white_uid, white_uid))),
        black=name_link(black_uid, str(names.get(black_uid, black_uid))),
        turn=name_link(turn_uid, str(names.get(turn_uid, turn_uid))),
        amount=fmt_money(Decimal(str(st.get("bet_amount") or "0")) * 2),
    )


async def _start_board(bot: Bot, st: dict) -> None:
    sent = await bot.send_message(
        int(st["chat_id"]),
        _status_text(st),
        parse_mode=ParseMode.HTML,
        reply_markup=board_keyboard(st),
        **thread_kw(st.get("message_thread_id")),
    )
    st["board_message_id"] = sent.message_id
    sk = slot_key(int(st["chat_id"]), st.get("message_thread_id"))
    store_live(sk, st)
    _schedule_turn_timer(bot, sk, st)


async def _room_place_label(
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


async def _available_chats(bot: Bot, session: AsyncSession) -> list[tuple[int, str]]:
    rows = await app_chats_repo.get_all(session)
    out: list[tuple[int, str]] = []
    for c in rows:
        if not int(c.checkers_enabled or 0):
            continue
        try:
            chat = await bot.get_chat(c.chat_id)
            title = chat.title or str(c.chat_id)
        except Exception:
            title = str(c.chat_id)
        out.append((int(c.chat_id), title))
    return out


async def _present_checkers_topics(
    message: Message,
    *,
    session: AsyncSession,
    lang: str,
    cid: int,
    back_callback_data: str = "menu:checkers",
) -> str:
    allowed = await allowed_topics_repo.effective_allowed_public_threads(session, cid)
    if allowed == frozenset():
        return "no_chat"
    topics_all = await forum_topics_repo.list_for_chat(session, cid)
    topics = [
        (int(x.message_thread_id), x.name)
        for x in topics_all
        if allowed is None or int(x.message_thread_id) in allowed
    ]
    include_general = allowed is None or None in allowed
    if topics or include_general:
        busy = {None for _ in [0] if slot_busy_for_new_game(cid, None)}
        for tid, _ in topics:
            if slot_busy_for_new_game(cid, tid):
                busy.add(tid)
        try:
            await message.edit_text(
                t("checkers_choose_topic", lang),
                reply_markup=checkers_topic_pick_keyboard(
                    lang,
                    chat_id=cid,
                    topics=topics,
                    busy=busy,
                    include_general=include_general,
                    back_callback_data=back_callback_data,
                ),
            )
        except TelegramBadRequest as exc:
            if "message is not modified" not in str(exc):
                raise
        return "topic"
    return "no_chat"


async def _busy_checkers_screen_html(bot: Bot, session: AsyncSession, lang: str, user_id: int) -> str:
    from services.checkers.state import active_chat_id_for_user

    cid = active_chat_id_for_user(user_id)
    if cid:
        row = await app_chats_repo.get_by_chat_id(session, cid)
        stored = str(row.chat_link).strip() if row and row.chat_link else None
        url = None
        if stored:
            url = stored if stored.startswith(("http://", "https://", "tg://")) else f"https://{stored.lstrip('/')}"
        try:
            chat = await bot.get_chat(cid)
            title = (chat.title or str(cid))[:100]
        except Exception:
            title = str(cid)
        esc_title = html.escape(title)
        chat_html = f'<a href="{html.escape(url)}">{esc_title}</a>' if url else esc_title
        return t("game21_busy_screen_text", lang).format(chat=chat_html)
    return html.escape(t("game21_active_notice", lang))


async def _show_checkers_busy(
    callback: CallbackQuery,
    session: AsyncSession,
    bot: Bot,
    lang: str,
    user_id: int,
    *,
    answer_callback: bool = True,
) -> None:
    show_cancel = get_search(user_id) is not None
    await callback.message.edit_text(
        await _busy_checkers_screen_html(bot, session, lang, user_id),
        parse_mode=ParseMode.HTML,
        reply_markup=checkers_busy_keyboard(lang, show_cancel_search=show_cancel),
    )
    if answer_callback:
        await callback.answer()


async def _cancel_owner_checkers_search_now(bot: Bot, owner_id: int) -> bool:
    uid = int(owner_id)
    req0 = get_search(uid) or {}
    if not req0:
        return False
    chat_id = int(req0.get("chat_id") or 0)
    thread_id = req0.get("message_thread_id")
    thread_id = int(thread_id) if thread_id is not None else None
    async with lock_for_chat(chat_id, thread_id):
        req = get_search(uid) or {}
        if not req:
            return False
        amount = Decimal(str(req.get("bet_amount") or "0"))
        mid_topic = req.get("message_id")
        mid_gen = req.get("message_id_general")
        pop_search(uid)
    sm = get_session_maker()
    async with sm() as session:
        await add_balance(session, uid, amount, method=METHOD_CHECKERS_REFUND)
        await session.commit()
    for mid, tid in ((mid_topic, thread_id), (mid_gen, None)):
        if mid is None:
            continue
        try:
            await unpin_chat_message_in_forum(
                bot, chat_id=chat_id, message_id=int(mid), message_thread_id=tid
            )
        except Exception:
            pass
        try:
            await bot.delete_message(chat_id, int(mid))
        except Exception:
            pass
    return True


@router.callback_query(F.data == "menu:checkers:cancel:active", F.message.chat.type == ChatType.PRIVATE)
async def on_checkers_cancel_active(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    if get_search(user.user_id) is None:
        await callback.answer(t("game21_no_active_search_to_cancel", lang), show_alert=True)
        return
    ok = await _cancel_owner_checkers_search_now(bot, user.user_id)
    if not ok:
        await callback.answer(t("game21_no_active_search_to_cancel", lang), show_alert=True)
        if user_in_any_interactive_game(user.user_id):
            await _show_checkers_busy(callback, session, bot, lang, user.user_id, answer_callback=False)
        return
    await state.clear()
    await callback.message.edit_text(
        t("checkers_search_cancelled_refund", lang),
        reply_markup=checkers_main_keyboard(lang),
    )
    await callback.answer(t("game21_active_cancelled_toast", lang))


@router.callback_query(F.data == "menu:checkers", F.message.chat.type == ChatType.PRIVATE)
async def on_checkers_menu(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if not await checkers_repo.is_enabled(session):
        await callback.answer(t("checkers_disabled", lang), show_alert=True)
        return
    if user_in_any_interactive_game(user.user_id):
        await _show_checkers_busy(callback, session, bot, lang, user.user_id)
        return
    await state.clear()
    chats = await _available_chats(bot, session)
    if not chats:
        await callback.answer(t("game21_pvp_no_available_chat", lang), show_alert=True)
        return
    if len(chats) == 1:
        res = await _present_checkers_topics(
            callback.message,
            session=session,
            lang=lang,
            cid=chats[0][0],
            back_callback_data="menu:main",
        )
        if res == "no_chat":
            await callback.answer(t("game21_pvp_no_available_chat", lang), show_alert=True)
            return
        await callback.answer()
        return
    await callback.message.edit_text(
        t("checkers_choose_chat", lang),
        reply_markup=checkers_chat_pick_keyboard(lang, chats),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("menu:checkers:chat:"), F.message.chat.type == ChatType.PRIVATE)
async def on_checkers_chat(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if not await checkers_repo.is_enabled(session):
        await callback.answer(t("checkers_disabled", lang), show_alert=True)
        return
    if user_in_any_interactive_game(user.user_id):
        await callback.answer(t("checkers_active_notice", lang), show_alert=True)
        return
    try:
        cid = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer()
        return
    res = await _present_checkers_topics(
        callback.message,
        session=session,
        lang=lang,
        cid=cid,
    )
    if res == "no_chat":
        await callback.answer(t("game21_pvp_no_available_chat", lang), show_alert=True)
        return
    await callback.answer()


@router.callback_query(F.data.startswith("menu:checkers:th:"), F.message.chat.type == ChatType.PRIVATE)
async def on_checkers_topic(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    parts = callback.data.split(":")
    try:
        cid = int(parts[3])
        tid_raw = int(parts[4])
    except (ValueError, IndexError):
        await callback.answer()
        return
    thread_id = None if tid_raw == 0 else tid_raw
    if not await checkers_repo.is_enabled(session):
        await callback.answer(t("checkers_disabled", lang), show_alert=True)
        return
    row = await app_chats_repo.get_by_chat_id(session, cid)
    if row is None or not bool(row.checkers_enabled):
        await callback.answer(t("checkers_disabled", lang), show_alert=True)
        return
    if not await allowed_topics_repo.is_allowed_public(session, cid, thread_id):
        await callback.answer(t("game21_pvp_topic_forbidden", lang), show_alert=True)
        return
    if slot_busy_for_new_game(cid, thread_id):
        await callback.answer(t("game21_pvp_main_active_exists", lang), show_alert=True)
        return
    try:
        chat = await bot.get_chat(cid)
        title = chat.title or str(cid)
    except Exception:
        title = str(cid)
    await state.update_data(checkers_chat_id=cid, checkers_thread_id=thread_id, checkers_chat_title=title)
    await state.set_state(CheckersState.waiting_bet)
    balance = await get_balance(session, user.user_id)
    await callback.message.edit_text(
        t("checkers_enter_bet", lang).format(chat=html.escape(title), balance=fmt_money(balance)),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@router.message(StateFilter(CheckersState.waiting_bet), F.chat.type == ChatType.PRIVATE)
async def on_checkers_bet(message: Message, session: AsyncSession, user: User, state: FSMContext) -> None:
    lang = _lang(user, message)
    raw = (message.text or "").strip().replace(",", ".").replace(" ", "")
    try:
        bet = Decimal(raw).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        await message.answer(t("game21_bet_invalid", lang))
        return
    if bet <= 0:
        await message.answer(t("game21_bet_invalid", lang))
        return
    if (await get_balance(session, user.user_id)) < bet:
        await message.answer(t("game21_not_enough_balance", lang))
        return
    commission = await checkers_repo.get_commission_percent(session)
    win = possible_win_pvp(bet, commission)
    await state.update_data(checkers_bet=str(bet), checkers_commission=str(commission))
    await state.set_state(CheckersState.waiting_confirm)
    await message.answer(
        t("checkers_confirm", lang).format(amount=fmt_money(bet), win=fmt_money(win)),
        reply_markup=checkers_confirm_keyboard(lang),
    )


@router.callback_query(
    F.data == "menu:checkers:confirm:no",
    F.message.chat.type == ChatType.PRIVATE,
    StateFilter(CheckersState.waiting_confirm),
)
async def on_checkers_confirm_no(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = _lang(user, callback)
    await state.clear()
    await callback.message.edit_text(
        t("game21_cancelled", lang),
        reply_markup=checkers_main_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(
    F.data == "menu:checkers:confirm:yes",
    F.message.chat.type == ChatType.PRIVATE,
    StateFilter(CheckersState.waiting_confirm),
)
async def on_checkers_confirm_yes(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    data = await state.get_data()
    chat_id = int(data.get("checkers_chat_id") or 0)
    thread_id = data.get("checkers_thread_id")
    thread_id = int(thread_id) if thread_id is not None else None
    bet = Decimal(str(data.get("checkers_bet") or "0"))
    commission = Decimal(str(data.get("checkers_commission") or "0"))
    win = possible_win_pvp(bet, commission)
    lock = lock_for_chat(chat_id, thread_id)
    async with user_lock(user.user_id):
        async with lock:
            if not await checkers_repo.is_enabled(session):
                await callback.answer(t("checkers_disabled", lang), show_alert=True)
                return
            row = await app_chats_repo.get_by_chat_id(session, chat_id)
            if row is None or not bool(row.checkers_enabled):
                await callback.answer(t("checkers_disabled", lang), show_alert=True)
                return
            if user_in_any_interactive_game(user.user_id):
                await callback.answer(t("checkers_active_notice", lang), show_alert=True)
                return
            if slot_busy_for_new_game(chat_id, thread_id):
                await callback.answer(t("game21_pvp_main_active_exists", lang), show_alert=True)
                return
            if not await take_balance(session, user.user_id, bet, method=METHOD_CHECKERS_STAKE):
                await callback.answer(t("game21_not_enough_balance", lang), show_alert=True)
                return
            owner_name = callback.from_user.full_name or callback.from_user.username or str(user.user_id)
            store_search(
                user.user_id,
                {
                    "owner_user_id": user.user_id,
                    "owner_name": owner_name,
                    "chat_id": chat_id,
                    "message_thread_id": thread_id,
                    "bet_amount": bet,
                    "commission_percent": commission,
                    "lang": lang,
                    "message_id": None,
                    "message_id_general": None,
                    "search_timeout_token": 0,
                },
            )
            await session.commit()
    text = t("checkers_search_post", lang).format(
        user=name_link(user.user_id, owner_name),
        amount=fmt_money(bet),
        win=fmt_money(win),
    )
    markup = checkers_accept_keyboard(lang, user.user_id)
    gen = None
    try:
        sent = await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML, reply_markup=markup, **thread_kw(thread_id))
        try:
            await pin_chat_message_in_forum(bot, chat_id=chat_id, message_id=sent.message_id, message_thread_id=thread_id)
        except Exception:
            pass
        if thread_id is not None:
            gen = await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML, reply_markup=markup)
            try:
                await pin_chat_message_in_forum(bot, chat_id=chat_id, message_id=gen.message_id, message_thread_id=None)
            except Exception:
                pass
    except Exception:
        pop_search(user.user_id)
        await add_balance(session, user.user_id, bet, method=METHOD_CHECKERS_REFUND)
        await session.commit()
        for msg in (locals().get("sent"), gen):
            if msg is not None:
                try:
                    await bot.delete_message(chat_id, msg.message_id)
                except Exception:
                    pass
        await callback.answer(t("game21_pvp_search_post_failed", lang), show_alert=True)
        return
    token = int(time.time() * 1000)
    meta = get_search(user.user_id)
    if meta:
        meta["message_id"] = sent.message_id
        meta["message_id_general"] = gen.message_id if gen else None
        meta["search_timeout_token"] = token
        store_search(user.user_id, meta)
    await state.clear()
    asyncio.create_task(_arm_search_timeout(bot, user.user_id, token))
    await callback.message.edit_text(
        t("checkers_search_started", lang).format(amount=fmt_money(bet)),
        reply_markup=checkers_main_keyboard(lang),
    )
    await callback.answer()


async def _arm_search_timeout(bot: Bot, owner_id: int, token: int) -> None:
    await asyncio.sleep(300)
    req = get_search(owner_id)
    if not req or int(req.get("search_timeout_token") or 0) != int(token):
        return
    chat_id = int(req.get("chat_id") or 0)
    thread_id = req.get("message_thread_id")
    amount = Decimal(str(req.get("bet_amount") or "0"))
    lang = req.get("lang") or "ru"
    pop_search(owner_id)
    sm = get_session_maker()
    async with sm() as session:
        await add_balance(session, owner_id, amount, method=METHOD_CHECKERS_REFUND)
        await session.commit()
    for mid, tid in ((req.get("message_id"), thread_id), (req.get("message_id_general"), None)):
        if not mid:
            continue
        try:
            await unpin_chat_message_in_forum(bot, chat_id=chat_id, message_id=int(mid), message_thread_id=tid)
        except Exception:
            pass
        try:
            await bot.delete_message(chat_id, int(mid))
        except Exception:
            pass
    try:
        await bot.send_message(
            owner_id,
            t("checkers_search_timeout", lang).format(amount=fmt_money(amount)),
            reply_markup=checkers_main_keyboard(lang),
        )
    except Exception:
        pass


@router.callback_query(
    F.data.startswith("menu:checkers:accept:"),
    F.message.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def on_checkers_accept(callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot) -> None:
    lang = _lang(user, callback)
    try:
        owner_id = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer()
        return
    if callback.from_user.id == owner_id:
        await callback.answer(t("game21_pvp_self_accept_forbidden", lang), show_alert=True)
        return
    req = get_search(owner_id)
    if not req:
        await callback.answer(t("game21_cancelled", lang), show_alert=True)
        return
    chat_id = int(req.get("chat_id") or 0)
    thread_id = req.get("message_thread_id")
    bet = Decimal(str(req.get("bet_amount") or "0"))
    sk = slot_key(chat_id, thread_id)
    async with user_lock(callback.from_user.id):
        async with lock_for_chat(chat_id, thread_id):
            if not await checkers_repo.is_enabled(session):
                await callback.answer(t("checkers_disabled", lang), show_alert=True)
                return
            row = await app_chats_repo.get_by_chat_id(session, chat_id)
            if row is None or not bool(row.checkers_enabled):
                await callback.answer(t("checkers_disabled", lang), show_alert=True)
                return
            if (
                get_live(sk)
                or slot_busy_outside_checkers(chat_id, thread_id)
                or user_in_any_interactive_game(callback.from_user.id)
            ):
                await callback.answer(t("checkers_active_notice", lang), show_alert=True)
                return
            if not await take_balance(session, callback.from_user.id, bet, method=METHOD_CHECKERS_STAKE):
                await callback.answer(t("game21_not_enough_balance", lang), show_alert=True)
                return
            req = pop_search(owner_id) or req
            owner_name = str(req.get("owner_name") or owner_id)
            second_name = callback.from_user.full_name or callback.from_user.username or str(callback.from_user.id)
            game_lang = req.get("lang") or lang
            settings = await checkers_repo.get_settings(session)
            commission = Decimal(
                str(req.get("commission_percent") or settings.commission_percent or "0")
            )
            payout = possible_win_pvp(bet, commission)
            commission_amount = (bet * 2 - payout).quantize(Decimal("0.01"))
            rules_text = (checkers_repo.rules_for_lang(settings, game_lang) or "").strip()
            room_label = await _room_place_label(session, game_lang, chat_id, thread_id)
            sid = await checkers_repo.create_session(
                session,
                chat_id=chat_id,
                message_thread_id=thread_id,
                player1_id=owner_id,
                player2_id=callback.from_user.id,
                bet_amount=bet,
                board={},
                commission_percent=commission,
                commission_amount=commission_amount,
            )
            token = time.time_ns()
            st = {
                "token": token,
                "session_id": sid,
                "chat_id": chat_id,
                "message_thread_id": thread_id,
                "player1_id": owner_id,
                "player2_id": callback.from_user.id,
                "phase": "decide_white",
                "decide_rolls": {},
                "white_user_id": None,
                "black_user_id": None,
                "turn_side": None,
                "turn_user_id": None,
                "bet_amount": bet,
                "commission_percent": commission,
                "commission_amount": commission_amount,
                "board": {},
                "selected": None,
                "moves": [],
                "no_capture_moves": 0,
                "draw_warning_message_id": None,
                "turn_warning_message_id": None,
                "turn_timer_token": 0,
                "names": {owner_id: owner_name, callback.from_user.id: second_name},
                "lang": game_lang,
                "rules_text": rules_text,
                "room_label": room_label,
                "search_message_id_topic": req.get("message_id"),
                "search_message_id_general": req.get("message_id_general"),
                "finished": False,
            }
            await session.commit()
            store_live(sk, st)
    await _edit_search_messages_accepted(bot, st, callback_message=callback.message)
    await bot.send_message(
        chat_id,
        t("checkers_decide_white", st.get("lang") or lang).format(
            players=(
                f"{name_link(owner_id, str(st['names'][owner_id]))}, "
                f"{name_link(callback.from_user.id, str(st['names'][callback.from_user.id]))}"
            )
        ),
        parse_mode=ParseMode.HTML,
        **thread_kw(thread_id),
    )
    await callback.answer()


@router.message(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    F.dice.emoji == "🎲",
    ~F.from_user.is_bot,
)
async def on_checkers_decide_dice(message: Message, bot: Bot) -> None:
    if not message.from_user:
        return
    sk = slot_key(message.chat.id, message.message_thread_id)
    st = get_live(sk)
    if not st or st.get("finished") or st.get("phase") != "decide_white":
        return
    uid = message.from_user.id
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    if uid not in (p1, p2):
        return
    lang = st.get("lang") or "ru"
    names = st.get("names") or {}
    val = int(message.dice.value or 0)
    async with lock_for_chat(message.chat.id, message.message_thread_id):
        st = get_live(sk) or {}
        if not st or st.get("phase") != "decide_white":
            return
        rolls = dict(st.get("decide_rolls") or {})
        if uid in rolls:
            return
        rolls[uid] = val
        st["decide_rolls"] = rolls
        store_live(sk, st)
    await bot.send_message(
        message.chat.id,
        t("game21_pvp_decide_roll_result", lang).format(
            name=name_link(uid, str(names.get(uid, uid))),
            value=val,
        ),
        parse_mode=ParseMode.HTML,
        **thread_kw(st.get("message_thread_id")),
    )
    async with lock_for_chat(message.chat.id, message.message_thread_id):
        st = get_live(sk) or {}
        rolls = dict(st.get("decide_rolls") or {})
        if p1 not in rolls or p2 not in rolls:
            return
        v1, v2 = int(rolls[p1]), int(rolls[p2])
        if v1 == v2:
            st["decide_rolls"] = {}
            store_live(sk, st)
            await bot.send_message(message.chat.id, t("game21_pvp_decide_tie", lang), **thread_kw(st.get("message_thread_id")))
            return
        white = p1 if v1 > v2 else p2
        black = p2 if white == p1 else p1
        st["white_user_id"] = white
        st["black_user_id"] = black
        st["turn_side"] = "w"
        st["turn_user_id"] = white
        st["phase"] = "playing"
        st["decide_rolls"] = {}
        st["board"] = engine.initial_board()
        store_live(sk, st)
    await bot.send_message(
        message.chat.id,
        t("checkers_white_chosen", lang).format(name=name_link(white, str(names.get(white, white)))),
        parse_mode=ParseMode.HTML,
        **thread_kw(st.get("message_thread_id")),
    )
    await _start_board(bot, st)


@router.callback_query(F.data.startswith("chk:m:"))
async def on_checkers_board(callback: CallbackQuery, bot: Bot) -> None:
    if not callback.message or not callback.from_user:
        await callback.answer()
        return
    parts = callback.data.split(":")
    try:
        token = int(parts[2])
        pos = engine.key(int(parts[3]), int(parts[4]))
    except (ValueError, IndexError):
        await callback.answer()
        return
    chat_id = callback.message.chat.id
    thread_id = callback.message.message_thread_id
    sk = slot_key(chat_id, thread_id)
    async with lock_for_chat(chat_id, thread_id):
        st = get_live(sk)
        if not st or int(st.get("token") or 0) != token or st.get("finished") or st.get("phase") != "playing":
            await callback.answer()
            return
        uid = callback.from_user.id
        turn_uid = _turn_user_id(st)
        if int(st.get("turn_user_id") or 0) != turn_uid:
            st["turn_user_id"] = turn_uid
            store_live(sk, st)
        if uid != turn_uid:
            await callback.answer(t("checkers_not_your_turn", st.get("lang") or "ru"), show_alert=True)
            return
        if await _answer_if_edit_blocked(callback, st):
            return
        board = st.get("board") or {}
        side = st.get("turn_side") or "w"
        piece = board.get(pos)
        selected = st.get("selected")
        if piece and engine.color(piece) == side:
            if selected == pos:
                await callback.answer()
                return
            st["selected"] = pos
            store_live(sk, st)
            edited = await _safe_edit_message(bot, st, _status_text(st), reply_markup=board_keyboard(st, selected=pos))
            if not edited and await _answer_if_edit_blocked(callback, st):
                return
            await callback.answer()
            return
        if not selected:
            await callback.answer()
            return
        move = next((m for m in engine.legal_moves(board, side) if m["from"] == selected and m["to"] == pos), None)
        if not move:
            await callback.answer(t("checkers_bad_move", st.get("lang") or "ru"), show_alert=True)
            return
        await _clear_turn_timer(bot, sk, st)
        moved_piece = board.get(selected)
        new_board, dst, more_capture = engine.apply_move(board, move)
        captured = bool(move.get("capture"))
        previous_chain = list(st.get("current_move_chain") or [])
        if not previous_chain or previous_chain[-1].get("to") != selected:
            previous_chain = []
        move_segment = {
            "from": selected,
            "to": pos,
            "capture": move.get("capture"),
            "piece": new_board.get(pos) or moved_piece,
        }
        move_chain = previous_chain + [move_segment]
        st["board"] = new_board
        st["last_move"] = move_segment
        st["last_move_chain"] = move_chain
        st["moves"] = list(st.get("moves") or []) + [{"u": uid, "from": selected, "to": pos, "capture": move.get("capture")}]
        if captured:
            st["no_capture_moves"] = 0
        else:
            st["no_capture_moves"] = int(st.get("no_capture_moves") or 0) + 1
        if more_capture:
            st["selected"] = dst
            st["current_move_chain"] = move_chain
            store_live(sk, st)
            _schedule_turn_timer(bot, sk, st)
            edited = await _safe_edit_message(bot, st, _status_text(st), reply_markup=board_keyboard(st, selected=dst))
            if not edited and await _answer_if_edit_blocked(callback, st):
                return
            await callback.answer()
            return
        next_side = engine.opponent(side)
        winner_side = engine.winner_side(new_board, next_side)
        if winner_side:
            await _finish_checkers(bot, sk, winner_id=int(st["white_user_id"] if winner_side == "w" else st["black_user_id"]))
            await callback.answer()
            return
        if await _maybe_finish_or_update_draw_countdown(bot, sk, st, captured=captured):
            await callback.answer()
            return
        st["turn_side"] = next_side
        st["turn_user_id"] = int(st["white_user_id"] if next_side == "w" else st["black_user_id"])
        st["selected"] = None
        st["current_move_chain"] = []
        store_live(sk, st)
        _schedule_turn_timer(bot, sk, st)
        edited = await _safe_edit_message(bot, st, _status_text(st), reply_markup=board_keyboard(st))
        if not edited and await _answer_if_edit_blocked(callback, st):
            return
    await callback.answer()


async def _maybe_finish_or_update_draw_countdown(
    bot: Bot, sk: tuple[int, int], st: dict, *, captured: bool
) -> bool:
    lang = st.get("lang") or "ru"
    chat_id = int(st["chat_id"])
    thread_id = st.get("message_thread_id")
    warning_mid = st.get("draw_warning_message_id")
    if captured:
        if warning_mid:
            try:
                await bot.delete_message(
                    chat_id=chat_id,
                    message_id=int(warning_mid),
                )
            except Exception:
                pass
            st["draw_warning_message_id"] = None
        store_live(sk, st)
        return False

    no_capture = int(st.get("no_capture_moves") or 0)
    if no_capture < 10:
        return False
    remaining = 20 - no_capture
    if remaining <= 0:
        await _finish_checkers_draw(bot, sk)
        return True
    text = t("checkers_draw_countdown", lang).format(
        no_capture=no_capture,
        remaining=remaining,
    )
    if warning_mid:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=int(warning_mid),
                text=text,
                **thread_kw(thread_id),
            )
        except Exception:
            pass
    else:
        try:
            msg = await bot.send_message(chat_id, text, **thread_kw(thread_id))
            st["draw_warning_message_id"] = msg.message_id
            store_live(sk, st)
        except Exception:
            pass
    return False


async def _finish_checkers(
    bot: Bot,
    sk: tuple[int, int],
    *,
    winner_id: int,
    timeout_loser_id: int | None = None,
) -> None:
    st = get_live(sk) or {}
    if not st or st.get("finished"):
        return
    await _clear_turn_timer(bot, sk, st)
    st["finished"] = True
    bet = Decimal(str(st.get("bet_amount") or "0"))
    commission = Decimal(str(st.get("commission_percent") or "0"))
    payout = possible_win_pvp(bet, commission)
    commission_amount = ((bet * 2) - payout).quantize(Decimal("0.01"))
    player_commission_base = (commission_amount / Decimal("2")).quantize(Decimal("0.01"))
    sm = get_session_maker()
    async with sm() as session:
        await add_balance(session, winner_id, payout, method=METHOD_CHECKERS_WIN)
        new_level = await user_levels_repo.add_winning_bet_progress(
            session,
            user_id=winner_id,
            bet_amount=bet,
            source="game:checkers",
        )
        if new_level is not None:
            await ensure_level_tag(
                bot,
                chat_id=int(st["chat_id"]),
                user_id=winner_id,
                level=new_level,
            )
        for uid in (int(st.get("player1_id") or 0), int(st.get("player2_id") or 0)):
            await users_repo.award_referral_percent(
                session,
                referral_id=uid,
                base_amount=player_commission_base,
                source="game:checkers",
            )
        await checkers_repo.finish_session(
            session,
            session_id=int(st["session_id"]),
            result="win",
            winner_id=winner_id,
            board=st.get("board") or {},
            moves=list(st.get("moves") or []),
        )
        await session.commit()
    lang = st.get("lang") or "ru"
    names = st.get("names") or {}
    await _safe_edit_message(bot, st, _status_text(st), reply_markup=board_keyboard(st))
    result_text = (
        t("checkers_turn_timeout_result", lang).format(
            loser=name_link(
                int(timeout_loser_id),
                str(names.get(int(timeout_loser_id), timeout_loser_id)),
            ),
            winner=name_link(winner_id, str(names.get(winner_id, winner_id))),
            payout=fmt_money(payout),
        )
        if timeout_loser_id is not None
        else t("checkers_winner", lang).format(
            name=name_link(winner_id, str(names.get(winner_id, winner_id))),
            payout=fmt_money(payout),
        )
    )
    await bot.send_message(
        int(st["chat_id"]),
        result_text,
        parse_mode=ParseMode.HTML,
        **thread_kw(st.get("message_thread_id")),
    )
    pop_live(sk)


async def _finish_checkers_draw(bot: Bot, sk: tuple[int, int]) -> None:
    st = get_live(sk) or {}
    if not st or st.get("finished"):
        return
    await _clear_turn_timer(bot, sk, st)
    st["finished"] = True
    bet = Decimal(str(st.get("bet_amount") or "0"))
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    sm = get_session_maker()
    async with sm() as session:
        await add_balance(session, p1, bet, method=METHOD_CHECKERS_REFUND)
        await add_balance(session, p2, bet, method=METHOD_CHECKERS_REFUND)
        await checkers_repo.finish_session(
            session,
            session_id=int(st["session_id"]),
            result="draw",
            winner_id=None,
            board=st.get("board") or {},
            moves=list(st.get("moves") or []),
        )
        await session.commit()
    lang = st.get("lang") or "ru"
    await _safe_edit_message(bot, st, _status_text(st), reply_markup=board_keyboard(st))
    await bot.send_message(
        int(st["chat_id"]),
        t("checkers_draw_result", lang).format(amount=fmt_money(bet)),
        parse_mode=ParseMode.HTML,
        **thread_kw(st.get("message_thread_id")),
    )
    pop_live(sk)
