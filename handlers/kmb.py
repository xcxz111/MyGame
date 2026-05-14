"""PvP камень/ножницы/бумага в группах/темах."""

from __future__ import annotations

import asyncio
import html
import re
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
from database.repositories import app_chat_allowed_topics as allowed_topics_repo
from database.repositories import app_chats as app_chats_repo
from database.repositories import fees as fees_repo
from database.repositories import forum_topics as forum_topics_repo
from database.repositories import kmb as kmb_repo
from database.repositories import user_levels as user_levels_repo
from database.repositories import users as users_repo
from keyboards.kmb import (
    kmb_accept_keyboard,
    kmb_busy_keyboard,
    kmb_chat_pick_keyboard,
    kmb_choice_keyboard,
    kmb_confirm_keyboard,
    kmb_main_keyboard,
    kmb_topic_pick_keyboard,
)
from locales.texts import get_lang, t
from services.game21.balance import add_balance, get_balance, take_balance
from services.game21.formatting import fmt_money, name_link, possible_win_pvp
from services.games.busy import (
    active_interactive_chat_id_for_user,
    slot_busy_for_new_game,
    slot_busy_outside_kmb,
    user_in_any_interactive_game,
)
from services.games.forum_thread import (
    format_forum_topic_display_label,
    pin_chat_message_in_forum,
    thread_kw,
    unpin_chat_message_in_forum,
)
from services.user_levels import ensure_level_tag
from services.kmb.state import (
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
from states.kmb import KmbState

router = Router(name="kmb")

_KMB_CHAT_COMMAND_RE = re.compile(
    r"^/(?:kmb|rps)(?:@[A-Za-z0-9_]+)?(?:\s*:\s*|\s+)(?P<amount>\d+(?:[,.]\d{1,2})?)(?:(?:\s*:\s*|\s+)(?P<wins>\d{1,2}))?\s*$",
    re.IGNORECASE,
)

METHOD_KMB_STAKE = "game:kmb:stake"
METHOD_KMB_WIN = "game:kmb:win"
METHOD_KMB_REFUND = "game:kmb:refund"

_CHOICE_LABELS = {
    "rock": "👊 камень",
    "scissors": "✌️ ножницы",
    "paper": "🤚 бумага",
}
_WIN_PAIRS = {("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")}


def _lang(user: User, event) -> str:
    return user.language_code or get_lang(getattr(event.from_user, "language_code", None))


def _parse_kmb_chat_command(text: str | None) -> tuple[Decimal, int] | None:
    match = _KMB_CHAT_COMMAND_RE.match((text or "").strip())
    if not match:
        return None
    try:
        amount = Decimal(match.group("amount").replace(",", "."))
        wins = int(match.group("wins") or 1)
    except (InvalidOperation, AttributeError, ValueError):
        return None
    if wins < 1 or wins > 10:
        return None
    return amount, wins


async def _available_chats(bot: Bot, session: AsyncSession) -> list[tuple[int, str]]:
    rows = await app_chats_repo.get_all(session)
    out: list[tuple[int, str]] = []
    for c in rows:
        try:
            chat = await bot.get_chat(c.chat_id)
            title = chat.title or str(c.chat_id)
        except Exception:
            title = str(c.chat_id)
        out.append((int(c.chat_id), title))
    return out


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


async def _present_kmb_topics(
    message: Message,
    *,
    session: AsyncSession,
    lang: str,
    cid: int,
    back_callback_data: str = "menu:kmb",
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
                t("kmb_choose_topic", lang),
                reply_markup=kmb_topic_pick_keyboard(
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


async def _busy_kmb_screen_html(bot: Bot, session: AsyncSession, lang: str, user_id: int) -> str:
    cid = active_interactive_chat_id_for_user(user_id)
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


async def _show_kmb_busy(
    callback: CallbackQuery,
    session: AsyncSession,
    bot: Bot,
    lang: str,
    user_id: int,
    *,
    answer_callback: bool = True,
) -> None:
    await callback.message.edit_text(
        await _busy_kmb_screen_html(bot, session, lang, user_id),
        parse_mode=ParseMode.HTML,
        reply_markup=kmb_busy_keyboard(lang, show_cancel_search=get_search(user_id) is not None),
    )
    if answer_callback:
        await callback.answer()


async def _cancel_owner_kmb_search_now(bot: Bot, owner_id: int) -> bool:
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
        await add_balance(session, uid, amount, method=METHOD_KMB_REFUND)
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


def _player_lines(st: dict) -> tuple[str, str]:
    names = st.get("names") or {}
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    return name_link(p1, str(names.get(p1, p1))), name_link(p2, str(names.get(p2, p2)))


def _match_card_html(lang: str, st: dict) -> str:
    p1_h, p2_h = _player_lines(st)
    bet = Decimal(str(st.get("bet_amount") or "0"))
    win_str = fmt_money(possible_win_pvp(bet, Decimal(str(st.get("commission_percent") or "0"))))
    rules = html.escape((st.get("rules_text") or "").strip() or t("kmb_rules_body", lang))
    return (
        f"<b>{html.escape(t('kmb_match_title', lang))}</b>\n"
        f"{p1_h}\n"
        f"{p2_h}\n\n"
        f"{html.escape(t('kmb_match_prize', lang).format(win=win_str))}\n\n"
        f"<b>{html.escape(t('kmb_match_rules_heading', lang))}</b>\n"
        f"<blockquote>{rules}</blockquote>"
    )


def _match_general_html(lang: str, st: dict, *, room_label: str) -> str:
    p1_h, p2_h = _player_lines(st)
    bet = Decimal(str(st.get("bet_amount") or "0"))
    win_str = fmt_money(possible_win_pvp(bet, Decimal(str(st.get("commission_percent") or "0"))))
    head = t("kmb_match_started_in_topic", lang).format(room=html.escape(room_label))
    prize = html.escape(t("kmb_match_prize", lang).format(win=win_str))
    return f"<b>{head}</b>\n{p1_h}\n{p2_h}\n\n{prize}"


async def _edit_search_messages_accepted(bot: Bot, st: dict, *, callback_message: Message | None) -> None:
    chat_id = int(st["chat_id"])
    thread_id = st.get("message_thread_id")
    lang = st.get("lang") or "ru"
    topic_mid = st.get("search_message_id_topic")
    general_mid = st.get("search_message_id_general")
    texts = [
        (topic_mid, thread_id, _match_card_html(lang, st)),
        (general_mid, None, _match_general_html(lang, st, room_label=str(st.get("room_label") or ""))),
    ]
    for mid, tid, text in texts:
        if not mid:
            continue
        try:
            await unpin_chat_message_in_forum(
                bot, chat_id=chat_id, message_id=int(mid), message_thread_id=tid
            )
        except Exception:
            pass
        try:
            if callback_message and callback_message.message_id == int(mid):
                await callback_message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=None)
            else:
                await bot.edit_message_text(
                    text=text,
                    chat_id=chat_id,
                    message_id=int(mid),
                    parse_mode=ParseMode.HTML,
                    reply_markup=None,
                )
        except TelegramBadRequest as exc:
            if "message is not modified" not in str(exc):
                pass
        except Exception:
            pass


def _choice_text(choice: str | None) -> str:
    if not choice:
        return "—"
    return _CHOICE_LABELS.get(choice, choice)


def _pick_prompt_html(lang: str, st: dict) -> str:
    names = st.get("names") or {}
    choices = st.get("choices") or {}
    scores = st.get("scores") or {}
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    p1_status = t("kmb_pick_done", lang) if p1 in choices else t("kmb_pick_wait", lang)
    p2_status = t("kmb_pick_done", lang) if p2 in choices else t("kmb_pick_wait", lang)
    return t("kmb_pick_prompt", lang).format(
        p1=name_link(p1, str(names.get(p1, p1))),
        p2=name_link(p2, str(names.get(p2, p2))),
        p1_score=int(scores.get(p1, 0)),
        p2_score=int(scores.get(p2, 0)),
        wins=int(st.get("target_wins") or 1),
        p1_status=html.escape(p1_status),
        p2_status=html.escape(p2_status),
    )


def _round_winner(p1_choice: str, p2_choice: str, p1: int, p2: int) -> int | None:
    if p1_choice == p2_choice:
        return None
    return p1 if (p1_choice, p2_choice) in _WIN_PAIRS else p2


@router.callback_query(F.data == "menu:kmb:cancel:active", F.message.chat.type == ChatType.PRIVATE)
async def on_kmb_cancel_active(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    if get_search(user.user_id) is None:
        await callback.answer(t("game21_no_active_search_to_cancel", lang), show_alert=True)
        return
    ok = await _cancel_owner_kmb_search_now(bot, user.user_id)
    if not ok:
        await callback.answer(t("game21_no_active_search_to_cancel", lang), show_alert=True)
        if user_in_any_interactive_game(user.user_id):
            await _show_kmb_busy(callback, session, bot, lang, user.user_id, answer_callback=False)
        return
    await state.clear()
    await callback.message.edit_text(
        t("kmb_search_cancelled_refund", lang),
        reply_markup=kmb_main_keyboard(lang),
    )
    await callback.answer(t("game21_active_cancelled_toast", lang))


@router.callback_query(F.data == "menu:kmb", F.message.chat.type == ChatType.PRIVATE)
async def on_kmb_menu(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if user_in_any_interactive_game(user.user_id):
        await _show_kmb_busy(callback, session, bot, lang, user.user_id)
        return
    await state.clear()
    chats = await _available_chats(bot, session)
    if not chats:
        await callback.answer(t("game21_pvp_no_available_chat", lang), show_alert=True)
        return
    if len(chats) == 1:
        res = await _present_kmb_topics(
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
    await callback.message.edit_text(t("kmb_choose_chat", lang), reply_markup=kmb_chat_pick_keyboard(lang, chats))
    await callback.answer()


@router.callback_query(F.data.startswith("menu:kmb:chat:"), F.message.chat.type == ChatType.PRIVATE)
async def on_kmb_chat(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if user_in_any_interactive_game(user.user_id):
        await callback.answer(t("game21_active_notice", lang), show_alert=True)
        return
    try:
        cid = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer()
        return
    res = await _present_kmb_topics(callback.message, session=session, lang=lang, cid=cid)
    if res == "no_chat":
        await callback.answer(t("game21_pvp_no_available_chat", lang), show_alert=True)
        return
    await callback.answer()


@router.callback_query(F.data.startswith("menu:kmb:th:"), F.message.chat.type == ChatType.PRIVATE)
async def on_kmb_topic(
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
    await state.update_data(kmb_chat_id=cid, kmb_thread_id=thread_id, kmb_chat_title=title)
    await state.set_state(KmbState.waiting_wins)
    await callback.message.edit_text(
        t("kmb_enter_wins", lang).format(chat=html.escape(title)),
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@router.message(StateFilter(KmbState.waiting_wins), F.chat.type == ChatType.PRIVATE)
async def on_kmb_target_wins(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, message)
    raw = (message.text or "").strip()
    try:
        target_wins = int(raw)
    except (TypeError, ValueError):
        await message.answer(t("kmb_wins_invalid", lang))
        return
    if target_wins < 1 or target_wins > 10:
        await message.answer(t("kmb_wins_invalid", lang))
        return
    data = await state.get_data()
    title = str(data.get("kmb_chat_title") or "")
    await state.update_data(kmb_target_wins=target_wins)
    await state.set_state(KmbState.waiting_bet)
    balance = await get_balance(session, user.user_id)
    await message.answer(
        t("kmb_enter_bet", lang).format(chat=html.escape(title), balance=fmt_money(balance)),
        parse_mode=ParseMode.HTML,
    )


@router.message(StateFilter(KmbState.waiting_bet), F.chat.type == ChatType.PRIVATE)
async def on_kmb_bet(message: Message, session: AsyncSession, user: User, state: FSMContext) -> None:
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
    data = await state.get_data()
    target_wins = int(data.get("kmb_target_wins") or 1)
    commission = await fees_repo.get_kmb_percent(session)
    win = possible_win_pvp(bet, commission)
    await state.update_data(kmb_bet=str(bet), kmb_commission=str(commission))
    await state.set_state(KmbState.waiting_confirm)
    await message.answer(
        t("kmb_confirm", lang).format(
            amount=fmt_money(bet), win=fmt_money(win), wins=target_wins
        ),
        reply_markup=kmb_confirm_keyboard(lang),
    )


@router.callback_query(
    F.data == "menu:kmb:confirm:no",
    F.message.chat.type == ChatType.PRIVATE,
    StateFilter(KmbState.waiting_confirm),
)
async def on_kmb_confirm_no(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = _lang(user, callback)
    await state.clear()
    await callback.message.edit_text(t("game21_cancelled", lang), reply_markup=kmb_main_keyboard(lang))
    await callback.answer()


@router.callback_query(
    F.data == "menu:kmb:confirm:yes",
    F.message.chat.type == ChatType.PRIVATE,
    StateFilter(KmbState.waiting_confirm),
)
async def on_kmb_confirm_yes(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    data = await state.get_data()
    chat_id = int(data.get("kmb_chat_id") or 0)
    thread_id = data.get("kmb_thread_id")
    thread_id = int(thread_id) if thread_id is not None else None
    bet = Decimal(str(data.get("kmb_bet") or "0"))
    commission = Decimal(str(data.get("kmb_commission") or "0"))
    target_wins = int(data.get("kmb_target_wins") or 1)
    win = possible_win_pvp(bet, commission)
    async with user_lock(user.user_id):
        async with lock_for_chat(chat_id, thread_id):
            if user_in_any_interactive_game(user.user_id):
                await callback.answer(t("game21_active_notice", lang), show_alert=True)
                return
            if slot_busy_for_new_game(chat_id, thread_id):
                await callback.answer(t("game21_pvp_main_active_exists", lang), show_alert=True)
                return
            if not await take_balance(session, user.user_id, bet, method=METHOD_KMB_STAKE):
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
                    "target_wins": target_wins,
                    "commission_percent": commission,
                    "lang": lang,
                    "message_id": None,
                    "message_id_general": None,
                    "search_timeout_token": 0,
                },
            )
            await session.commit()
    text = t("kmb_search_post", lang).format(
        user=name_link(user.user_id, owner_name),
        amount=fmt_money(bet),
        win=fmt_money(win),
        wins=target_wins,
    )
    markup = kmb_accept_keyboard(lang, user.user_id)
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
        await add_balance(session, user.user_id, bet, method=METHOD_KMB_REFUND)
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
        t("kmb_search_started", lang).format(amount=fmt_money(bet), wins=target_wins),
        reply_markup=kmb_main_keyboard(lang),
    )
    await callback.answer()


@router.message(
    F.text.regexp(_KMB_CHAT_COMMAND_RE),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    ~F.from_user.is_bot,
)
async def on_kmb_chat_command(message: Message, session: AsyncSession, user: User, bot: Bot) -> None:
    lang = _lang(user, message)
    parsed = _parse_kmb_chat_command(message.text)
    if parsed is None:
        await message.reply(t("kmb_chat_command_usage", lang), parse_mode=ParseMode.HTML)
        return
    bet, target_wins = parsed
    if bet <= 0:
        await message.reply(t("kmb_chat_command_usage", lang), parse_mode=ParseMode.HTML)
        return
    chat_id = message.chat.id
    thread_id = message.message_thread_id
    if message.chat.type != ChatType.SUPERGROUP:
        thread_id = None
    async with user_lock(user.user_id):
        async with lock_for_chat(chat_id, thread_id):
            row = await app_chats_repo.get_by_chat_id(session, chat_id)
            if row is None:
                await message.reply(t("kmb_no_chats", lang))
                return
            if thread_id is not None:
                allowed = await allowed_topics_repo.is_allowed_public(session, chat_id, thread_id)
                if not allowed:
                    await message.reply(t("kmb_no_chats", lang))
                    return
            if user_in_any_interactive_game(user.user_id):
                await message.reply(t("game21_active_notice", lang))
                return
            if slot_busy_for_new_game(chat_id, thread_id):
                topic = await _room_place_label(session, lang, chat_id, thread_id)
                await message.reply(t("game21_chat_command_active_exists", lang).format(topic=topic), parse_mode=ParseMode.HTML)
                return
            if await get_balance(session, user.user_id) < bet:
                await message.reply(t("game21_not_enough_balance", lang))
                return
            commission = await fees_repo.get_kmb_percent(session)
            if not await take_balance(session, user.user_id, bet, method=METHOD_KMB_STAKE):
                await message.reply(t("game21_not_enough_balance", lang))
                return
            owner_name = message.from_user.full_name or message.from_user.username or str(user.user_id)
            store_search(
                user.user_id,
                {
                    "owner_user_id": user.user_id,
                    "owner_name": owner_name,
                    "chat_id": chat_id,
                    "message_thread_id": thread_id,
                    "bet_amount": bet,
                    "target_wins": target_wins,
                    "commission_percent": commission,
                    "lang": lang,
                    "message_id": None,
                    "message_id_general": None,
                    "search_timeout_token": 0,
                },
            )
            await session.commit()
    win = possible_win_pvp(bet, commission)
    text = t("kmb_search_post", lang).format(
        user=name_link(user.user_id, owner_name),
        amount=fmt_money(bet),
        win=fmt_money(win),
        wins=target_wins,
    )
    markup = kmb_accept_keyboard(lang, user.user_id)
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
        await add_balance(session, user.user_id, bet, method=METHOD_KMB_REFUND)
        await session.commit()
        for msg in (locals().get("sent"), gen):
            if msg is not None:
                try:
                    await bot.delete_message(chat_id, msg.message_id)
                except Exception:
                    pass
        await message.reply(t("game21_pvp_search_post_failed", lang))
        return
    token = int(time.time() * 1000)
    meta = get_search(user.user_id)
    if meta:
        meta["message_id"] = sent.message_id
        meta["message_id_general"] = gen.message_id if gen else None
        meta["search_timeout_token"] = token
        store_search(user.user_id, meta)
    asyncio.create_task(_arm_search_timeout(bot, user.user_id, token))


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
        await add_balance(session, owner_id, amount, method=METHOD_KMB_REFUND)
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
            t("kmb_search_timeout", lang).format(amount=fmt_money(amount)),
            reply_markup=kmb_main_keyboard(lang),
        )
    except Exception:
        pass


@router.callback_query(
    F.data.startswith("menu:kmb:accept:"),
    F.message.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def on_kmb_accept(callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot) -> None:
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
    thread_id = int(thread_id) if thread_id is not None else None
    sk = slot_key(chat_id, thread_id)
    bet = Decimal(str(req.get("bet_amount") or "0"))
    async with user_lock(callback.from_user.id):
        async with lock_for_chat(chat_id, thread_id):
            if get_live(sk) or slot_busy_outside_kmb(chat_id, thread_id) or user_in_any_interactive_game(callback.from_user.id):
                await callback.answer(t("game21_active_notice", lang), show_alert=True)
                return
            if not await take_balance(session, callback.from_user.id, bet, method=METHOD_KMB_STAKE):
                await callback.answer(t("game21_not_enough_balance", lang), show_alert=True)
                return
            req = pop_search(owner_id) or req
            owner_name = str(req.get("owner_name") or owner_id)
            second_name = callback.from_user.full_name or callback.from_user.username or str(callback.from_user.id)
            game_lang = req.get("lang") or lang
            commission = Decimal(str(req.get("commission_percent") or "0"))
            target_wins = max(1, min(10, int(req.get("target_wins") or 1)))
            payout = possible_win_pvp(bet, commission)
            commission_amount = (bet * 2 - payout).quantize(Decimal("0.01"))
            settings = await kmb_repo.get_settings(session)
            rules_text = (settings.rules_text or "").strip()
            room_label = await _room_place_label(session, game_lang, chat_id, thread_id)
            sid = await kmb_repo.create_session(
                session,
                chat_id=chat_id,
                message_thread_id=thread_id,
                player1_id=owner_id,
                player2_id=callback.from_user.id,
                bet_amount=bet,
                target_wins=target_wins,
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
                "bet_amount": bet,
                "target_wins": target_wins,
                "commission_percent": commission,
                "commission_amount": commission_amount,
                "payout": payout,
                "choices": {},
                "rounds": [],
                "scores": {owner_id: 0, callback.from_user.id: 0},
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
    pick = await bot.send_message(
        chat_id,
        _pick_prompt_html(st.get("lang") or lang, st),
        parse_mode=ParseMode.HTML,
        reply_markup=kmb_choice_keyboard(int(st["token"])),
        **thread_kw(thread_id),
    )
    st["pick_message_id"] = pick.message_id
    store_live(sk, st)
    await callback.answer()


@router.callback_query(
    F.data.startswith("kmb:pick:"),
    F.message.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def on_kmb_pick(callback: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    if not callback.from_user:
        return
    parts = (callback.data or "").split(":")
    try:
        token = int(parts[2])
        choice = parts[3]
    except (ValueError, IndexError):
        await callback.answer()
        return
    if choice not in _CHOICE_LABELS:
        await callback.answer()
        return
    sk = slot_key(callback.message.chat.id, callback.message.message_thread_id)
    async with lock_for_chat(callback.message.chat.id, callback.message.message_thread_id):
        st = get_live(sk)
        if not st or st.get("finished") or int(st.get("token") or 0) != token:
            await callback.answer()
            return
        lang = st.get("lang") or "ru"
        p1 = int(st.get("player1_id") or 0)
        p2 = int(st.get("player2_id") or 0)
        uid = int(callback.from_user.id)
        if uid not in (p1, p2):
            await callback.answer(t("kmb_not_your_game", lang), show_alert=True)
            return
        choices = dict(st.get("choices") or {})
        if uid in choices:
            await callback.answer(t("kmb_choice_saved", lang), show_alert=True)
            return
        choices[uid] = choice
        st["choices"] = choices
        if p1 not in choices or p2 not in choices:
            store_live(sk, st)
            try:
                await callback.message.edit_text(
                    _pick_prompt_html(lang, st),
                    parse_mode=ParseMode.HTML,
                    reply_markup=kmb_choice_keyboard(token),
                )
            except TelegramBadRequest as exc:
                if "message is not modified" not in str(exc):
                    raise
            await callback.answer(t("kmb_choice_saved", lang))
            return

        p1_choice = str(choices[p1])
        p2_choice = str(choices[p2])
        rounds = list(st.get("rounds") or [])
        winner_id = _round_winner(p1_choice, p2_choice, p1, p2)
        names = st.get("names") or {}
        scores = dict(st.get("scores") or {p1: 0, p2: 0})
        if winner_id is None:
            rounds.append({str(p1): p1_choice, str(p2): p2_choice, "winner_id": None})
            st["rounds"] = rounds
            st["choices"] = {}
            store_live(sk, st)
            text = t("kmb_result_draw", lang).format(
                p1=name_link(p1, str(names.get(p1, p1))),
                p2=name_link(p2, str(names.get(p2, p2))),
                p1_choice=html.escape(_choice_text(p1_choice)),
                p2_choice=html.escape(_choice_text(p2_choice)),
                p1_score=int(scores.get(p1, 0)),
                p2_score=int(scores.get(p2, 0)),
                wins=int(st.get("target_wins") or 1),
            )
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=kmb_choice_keyboard(token),
            )
            await callback.answer(t("kmb_choice_saved", lang))
            return

        scores[winner_id] = int(scores.get(winner_id, 0)) + 1
        st["scores"] = scores
        rounds.append(
            {
                str(p1): p1_choice,
                str(p2): p2_choice,
                "winner_id": winner_id,
                "score": {str(p1): int(scores.get(p1, 0)), str(p2): int(scores.get(p2, 0))},
            }
        )
        st["rounds"] = rounds
        target_wins = int(st.get("target_wins") or 1)
        if int(scores.get(winner_id, 0)) < target_wins:
            st["choices"] = {}
            store_live(sk, st)
            text = t("kmb_round_win", lang).format(
                p1=name_link(p1, str(names.get(p1, p1))),
                p2=name_link(p2, str(names.get(p2, p2))),
                p1_choice=html.escape(_choice_text(p1_choice)),
                p2_choice=html.escape(_choice_text(p2_choice)),
                winner=name_link(winner_id, str(names.get(winner_id, winner_id))),
                p1_score=int(scores.get(p1, 0)),
                p2_score=int(scores.get(p2, 0)),
                wins=target_wins,
            )
            await callback.message.edit_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=kmb_choice_keyboard(token),
            )
            await callback.answer(t("kmb_choice_saved", lang))
            return

        bet = Decimal(str(st.get("bet_amount") or "0"))
        payout = Decimal(str(st.get("payout") or "0"))
        commission_amount = ((bet * 2) - payout).quantize(Decimal("0.01"))
        player_commission_base = (commission_amount / Decimal("2")).quantize(Decimal("0.01"))
        await add_balance(session, winner_id, payout, method=METHOD_KMB_WIN)
        new_level = await user_levels_repo.add_winning_bet_progress(
            session,
            user_id=winner_id,
            bet_amount=bet,
            source="game:kmb",
        )
        if new_level is not None:
            await ensure_level_tag(
                bot,
                chat_id=int(st["chat_id"]),
                user_id=winner_id,
                level=new_level,
            )
        for uid in (p1, p2):
            await users_repo.award_referral_percent(
                session,
                referral_id=uid,
                base_amount=player_commission_base,
                source="game:kmb",
            )
        await kmb_repo.finish_session(
            session,
            session_id=int(st.get("session_id") or 0),
            result="win",
            winner_id=winner_id,
            moves=rounds,
        )
        await session.commit()
        st["finished"] = True
        store_live(sk, st)
        pop_live(sk)
        text = t("kmb_result_win", lang).format(
            p1=name_link(p1, str(names.get(p1, p1))),
            p2=name_link(p2, str(names.get(p2, p2))),
            p1_score=int(scores.get(p1, 0)),
            p2_score=int(scores.get(p2, 0)),
            p1_choice=html.escape(_choice_text(p1_choice)),
            p2_choice=html.escape(_choice_text(p2_choice)),
            winner=name_link(winner_id, str(names.get(winner_id, winner_id))),
            payout=fmt_money(payout),
        )
        await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=None)
        await callback.answer(t("kmb_choice_saved", lang))
