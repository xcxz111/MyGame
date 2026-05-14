"""Старт игр по расписанию, напоминания, раунды и тай-брейк (как в Game_bot)."""

from __future__ import annotations

import asyncio
import html
import logging
import random
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from aiogram import Bot
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from aiogram.types import Message

from database.models.game import Game, GameStatus, GameType
from database.models.payment_log import PaymentLogMethod
from database.models.user import User
from database.repositories import app_chats as app_chats_repo
from database.repositories import checkers as checkers_repo
from database.repositories import game21_settings as g21_repo
from database.repositories import game_participants as gp_repo
from database.repositories import games as games_repo
from database.repositories import payment_logs as payment_logs_repo
from database.repositories import prizes as prizes_repo
from database.repositories import slot as slot_repo
from database.repositories import throws as throws_repo
from database.repositories import users as users_repo
from keyboards.main_menu import main_menu_keyboard
from locales.texts import get_lang, t
from services.games.constants import (
    ELIMINATED_MARKER,
    GAME_TYPE_DICE_EMOJI,
    MAIN_GAME_ALLOWED_EMOJIS,
    MAIN_GAME_EMOJI_HINT,
)
from services.games.forum_thread import (
    edit_message_text_in_forum,
    pin_chat_message_in_forum,
    thread_kw,
    unpin_chat_message_in_forum,
)
from services.games.state import (
    _chat_to_game,
    _round_state,
    play_slot_key,
    resolve_active_game_id,
)
from settings import get_settings

logger = logging.getLogger(__name__)

SessionMaker = async_sessionmaker[AsyncSession]


def _fmt_pln(value: Decimal) -> str:
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    s = f"{d:.2f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def _tw(st: dict[str, Any] | None) -> dict[str, Any]:
    if not st:
        return {}
    return thread_kw(st.get("message_thread_id"))


def _switch_round_writer(state: dict[str, Any], next_user_id: int | None) -> None:
    if next_user_id is not None:
        state["current_writer_uid"] = int(next_user_id)
    else:
        state.pop("current_writer_uid", None)


def _release_round_state(game_id: int) -> None:
    st = _round_state.pop(game_id, None)
    if st is not None:
        _release_round_chat_restrictions(st)
        cid = int(st["chat_id"])
        slot = play_slot_key(cid, st.get("message_thread_id"))
        _chat_to_game.pop(slot, None)


def _release_round_chat_restrictions(state: dict[str, Any]) -> None:
    state.pop("current_writer_uid", None)


def _display_name(user: User | None, uid: int) -> str:
    if user is None:
        return str(uid)
    return (user.name or user.user_name or str(uid)).strip() or str(uid)


async def _pick_ui_lang(session: AsyncSession, user_ids: list[int]) -> str:
    if not user_ids:
        return "ru"
    u = await users_repo.get_user(session, user_ids[0])
    return get_lang(u.language_code if u else None)


async def _participants_display(
    session: AsyncSession, game_id: int
) -> list[tuple[int, str]]:
    rows = await gp_repo.for_game_with_users(session, game_id)
    return [(int(p.user_id), _display_name(u, int(p.user_id))) for p, u in rows]


def _place_range_label(lang: str, start_idx: int, end_exclusive: int) -> str:
    a = start_idx + 1
    b = end_exclusive
    if a == b:
        return t("round_tiebreak_place_one", lang).format(n=a)
    return t("round_tiebreak_place_span", lang).format(a=a, b=b)


def _format_participants_list(
    participants: list[tuple[int, str]],
    totals_by_uid: dict[int, Any],
    lang: str,
    *,
    with_header: bool = True,
) -> str:
    pending = t("round_score_pending", lang)
    lines: list[str] = []
    if with_header:
        lines.extend([t("round_list_participants", lang), ""])
    for i, (uid, name) in enumerate(participants, 1):
        safe_name = html.escape(name)
        scores = totals_by_uid.get(uid)
        if scores is None:
            score_str = pending
        elif isinstance(scores, list):
            parts: list[str] = []
            for s in scores:
                if s == ELIMINATED_MARKER:
                    parts.append(t("round_score_eliminated", lang))
                elif s is not None:
                    parts.append(str(s))
                else:
                    parts.append(pending)
            score_str = "/".join(parts)
        else:
            score_str = str(scores) if scores is not None else pending
        lines.append(f'{i}. <a href="tg://user?id={uid}">{safe_name}</a>   {score_str}')
    return "\n".join(lines)


async def _build_totals_multiround(
    session: AsyncSession,
    game_id: int,
    participants: list[tuple[int, str]],
    current_index: int,
    round_number: int,
    playing_participants: list[tuple[int, str]] | None = None,
) -> dict[int, Any]:
    result: dict[int, list[Any]] = {uid: [] for uid, _ in participants}
    playing_uids = {p[0] for p in (playing_participants or [])}
    for r in range(1, round_number + 1):
        totals = await throws_repo.get_round_totals(session, game_id, r)
        by_uid = dict(totals)
        for i, (uid, _) in enumerate(participants):
            if uid in by_uid:
                result[uid].append(by_uid[uid])
            elif r < round_number:
                result[uid].append(0)
            elif playing_participants is not None and r == round_number:
                if uid not in playing_uids:
                    result[uid].append(ELIMINATED_MARKER)
                else:
                    playing_idx = next(
                        j for j, (u, _) in enumerate(playing_participants) if u == uid
                    )
                    if playing_idx < current_index:
                        result[uid].append(0)
                    else:
                        result[uid].append(None)
            elif i < current_index:
                result[uid].append(0)
            else:
                result[uid].append(None)
    return result


async def send_5min_reminders(bot: Bot, session_maker: SessionMaker) -> None:
    now = datetime.now()
    async with session_maker() as session:
        games = await games_repo.list_for_5min_reminder(session, now)
        menu_chats = await app_chats_repo.list_for_main_menu(session)
        show_game21 = await g21_repo.any_game21_enabled(session)
        show_checkers = await checkers_repo.is_enabled(session)
        show_slot = await slot_repo.is_enabled(session)
        for game in games:
            try:
                uids = await gp_repo.list_user_ids(session, game.id)
            except Exception as exc:
                logger.warning("5min reminder participants game=%s: %s", game.id, exc)
                continue
            try:
                chat = await bot.get_chat(game.chat_id)
                chat_title = chat.title or str(game.chat_id)
            except Exception:
                chat_title = str(game.chat_id)
            texts: dict[str, str] = {}
            settings = get_settings()
            for uid in uids:
                u = await users_repo.get_user(session, uid)
                lang = get_lang(u.language_code if u else None)
                if lang not in texts:
                    texts[lang] = t("game_reminder_5min", lang).format(
                        chat_title=html.escape(chat_title)
                    )
                try:
                    await bot.send_message(
                        uid,
                        texts[lang],
                        parse_mode=ParseMode.HTML,
                        reply_markup=main_menu_keyboard(
                            lang,
                            uid,
                            settings.admin_id,
                            menu_chats=menu_chats,
                            show_game21=show_game21,
                            show_checkers=show_checkers,
                            show_slot=show_slot,
                        ),
                    )
                except Exception as exc:
                    logger.warning("5min reminder user=%s: %s", uid, exc)
            await games_repo.update(session, game.id, reminder_5min_sent=1)
        await session.commit()


async def _cancel_game_not_enough(
    bot: Bot, session_maker: SessionMaker, game_id: int
) -> None:
    settings = get_settings()
    async with session_maker() as session:
        g = await games_repo.get(session, game_id)
        if g is None or g.status != GameStatus.DRAFT:
            return
        registered = await games_repo.count_participants(session, game_id)
        min_r = int(g.min_participants or 0)
        if min_r <= 0 or registered >= min_r:
            return
        user_ids = await gp_repo.list_user_ids(session, game_id)
        await games_repo.update(session, game_id, status=GameStatus.CANCELLED)
        fee = g.entry_fee or Decimal("0")
        paid = bool(int(g.is_paid or 0)) and fee > Decimal("0")
        langs: dict[int, str] = {}
        for uid in user_ids:
            u = await users_repo.get_user(session, uid)
            langs[uid] = get_lang(u.language_code if u else None)
            if paid and u is not None:
                u.balance = (u.balance or Decimal("0")) + fee
                await session.flush()
                await payment_logs_repo.log(
                    session,
                    user_id=uid,
                    method=PaymentLogMethod.GAME_ENTRY_REFUND,
                    amount=fee,
                    balance_after=u.balance,
                )
        ann_id = g.announcement_message_id
        ann_gen_id = g.announcement_message_id_general
        chat_id = g.chat_id
        ann_thread = g.message_thread_id
        menu_chats = await app_chats_repo.list_for_main_menu(session)
        show_game21 = await g21_repo.any_game21_enabled(session)
        show_checkers = await checkers_repo.is_enabled(session)
        show_slot = await slot_repo.is_enabled(session)
        await session.commit()

    if ann_id:
        try:
            await unpin_chat_message_in_forum(
                bot,
                chat_id=int(chat_id),
                message_id=int(ann_id),
                message_thread_id=ann_thread,
            )
        except Exception as exc:
            logger.debug("unpin announce: %s", exc)
    if ann_gen_id:
        try:
            await unpin_chat_message_in_forum(
                bot,
                chat_id=int(chat_id),
                message_id=int(ann_gen_id),
                message_thread_id=None,
            )
        except Exception as exc:
            logger.debug("unpin general announce: %s", exc)

    for uid in user_ids:
        lang = langs.get(uid, "ru")
        text = t("game_cancelled_not_enough_players_dm", lang).format(
            current=registered, required=min_r
        )
        if paid and fee > Decimal("0"):
            text += "\n\n" + t("game_cancelled_refund_full_fee", lang).format(
                fee=_fmt_pln(fee)
            )
        try:
            await bot.send_message(
                uid,
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=main_menu_keyboard(
                    lang,
                    uid,
                    settings.admin_id,
                    menu_chats=menu_chats,
                    show_game21=show_game21,
                    show_checkers=show_checkers,
                    show_slot=show_slot,
                ),
            )
        except Exception as exc:
            logger.warning("cancel dm user=%s: %s", uid, exc)


async def process_due_games(bot: Bot, session_maker: SessionMaker) -> None:
    now = datetime.now()
    async with session_maker() as session:
        due = await games_repo.list_draft_past_start_buffer(session, now)
    for game in due:
        g: Game | None = None
        async with session_maker() as session:
            g = await games_repo.get(session, game.id)
            if g is None or g.status != GameStatus.DRAFT:
                continue
            n = await games_repo.count_participants(session, g.id)
            min_r = int(g.min_participants or 0)
        if g is None:
            continue
        if min_r > 0 and n < min_r:
            await _cancel_game_not_enough(bot, session_maker, g.id)
            continue
        try:
            await announce_game_start(bot, session_maker, g.id)
        except Exception:
            logger.exception("announce_game_start game_id=%s", g.id)


async def announce_game_start(bot: Bot, session_maker: SessionMaker, game_id: int) -> None:
    gen_ann_id: int | None = None
    async with session_maker() as session:
        game = await games_repo.get(session, game_id)
        if game is None or game.status != GameStatus.DRAFT:
            return
        participants = await _participants_display(session, game_id)
        prize_rows = await prizes_repo.for_game(session, game_id)
        lang = await _pick_ui_lang(session, [p[0] for p in participants])
        chat_id = int(game.chat_id)
        msg_thread = game.message_thread_id
        gen_ann_id = game.announcement_message_id_general
        start_label = game.start_time.strftime("%d.%m.%Y %H:%M")
        min_top = game.min_topup or Decimal("0")
        since = game.min_topup_since
        is_paid = bool(int(game.is_paid or 0))
        fee = game.entry_fee or Decimal("0")
        cond_lines: list[str] = []
        if min_top > Decimal("0"):
            if since is not None:
                since_lbl = since.strftime("%d.%m.%Y") if isinstance(since, date) else str(since)
                cond_lines.append(
                    t("game_start_cond_min_topup_period", lang).format(
                        n=_fmt_pln(min_top), since=since_lbl, until=start_label
                    )
                )
            else:
                cond_lines.append(
                    t("game_start_cond_min_topup_alltime", lang).format(n=_fmt_pln(min_top))
                )
        if is_paid and fee > Decimal("0"):
            cond_lines.append(
                t("game_start_cond_paid", lang).format(fee=_fmt_pln(fee))
            )
        else:
            cond_lines.append(t("game_start_cond_free", lang))
        if not cond_lines:
            cond_lines.append(t("game_start_cond_none", lang))
        prize_lines = [
            f"{i}. {_fmt_pln(p.amount)} PLN"
            for i, p in enumerate(prize_rows, 1)
        ]
        prizes_block = "\n".join(prize_lines) if prize_lines else "—"
        conditions_block = "\n".join(cond_lines)
        msg1 = t("game_start_header", lang).format(
            conditions=html.escape(conditions_block),
            prizes=html.escape(prizes_block),
        )

    try:
        await bot.send_message(
            chat_id, msg1, parse_mode=ParseMode.HTML, **thread_kw(msg_thread)
        )
        await asyncio.sleep(3)
    except Exception as exc:
        logger.warning("announce msg1 chat=%s: %s", chat_id, exc)
        return

    rules = t("game_rules_block", lang)
    try:
        await bot.send_message(chat_id, rules, **thread_kw(msg_thread))
        await asyncio.sleep(3)
    except Exception as exc:
        logger.warning("announce rules chat=%s: %s", chat_id, exc)

    list_text = t("game_round1_list_intro", lang) + "\n\n" + _format_participants_list(
        participants, {}, lang, with_header=False
    )
    list_message_id: int | None = None
    try:
        sent = await bot.send_message(
            chat_id, list_text, parse_mode=ParseMode.HTML, **thread_kw(msg_thread)
        )
        await pin_chat_message_in_forum(
            bot,
            chat_id=chat_id,
            message_id=sent.message_id,
            message_thread_id=msg_thread,
        )
        list_message_id = sent.message_id
    except Exception as exc:
        logger.warning("announce list/pin chat=%s: %s", chat_id, exc)

    emoji = (
        random.choice(["🎲", "🎳", "🎯"])
        if game.game_type == GameType.ANY
        else GAME_TYPE_DICE_EMOJI.get(game.game_type, "🎲")
    )
    try:
        await asyncio.sleep(3)
        await bot.send_dice(chat_id=chat_id, emoji=emoji, **thread_kw(msg_thread))
    except Exception as exc:
        logger.warning("announce dice demo chat=%s: %s", chat_id, exc)

    if gen_ann_id:
        try:
            await unpin_chat_message_in_forum(
                bot,
                chat_id=chat_id,
                message_id=int(gen_ann_id),
                message_thread_id=None,
            )
        except Exception as exc:
            logger.debug("unpin general duplicate announce: %s", exc)
        async with session_maker() as session:
            await games_repo.update(
                session, game_id, announcement_message_id_general=None
            )
            await session.commit()

    async with session_maker() as session:
        await games_repo.update(session, game_id, status=GameStatus.ACTIVE)
        await session.commit()

    asyncio.create_task(delayed_start_round_1(bot, session_maker, game_id, list_message_id))


async def delayed_start_round_1(
    bot: Bot,
    session_maker: SessionMaker,
    game_id: int,
    list_message_id: int | None,
) -> None:
    await asyncio.sleep(5)
    msg_thread: int | None = None
    async with session_maker() as session:
        participants = await _participants_display(session, game_id)
        game = await games_repo.get(session, game_id)
        if not participants or game is None:
            return
        lang = await _pick_ui_lang(session, [p[0] for p in participants])
        prize_places = int(game.prize_places or 1)
        chat_id = int(game.chat_id)
        game_type = game.game_type or GameType.ANY
        msg_thread = game.message_thread_id
    is_final_round = len(participants) < 8 or len(participants) < (prize_places * 3)
    _round_state[game_id] = {
        "ui_lang": lang,
        "participant_ids": list(participants),
        "round_participants": list(participants),
        "all_participants": list(participants),
        "current_index": 0,
        "throw_count": 0,
        "chat_id": chat_id,
        "message_thread_id": msg_thread,
        "game_type": game_type,
        "round_number": 1,
        "list_message_id": list_message_id,
        "is_final_round": is_final_round,
        "turn_id": 0,
    }
    slot = play_slot_key(chat_id, msg_thread)
    _chat_to_game[slot] = game_id
    uid0, name0 = participants[0]
    name_link = f'<a href="tg://user?id={uid0}">{html.escape(name0)}</a>'
    text = t("round_throw_prompt", lang).format(name=name_link, emoji=MAIN_GAME_EMOJI_HINT)
    try:
        await bot.send_message(
            chat_id, text, parse_mode=ParseMode.HTML, **thread_kw(msg_thread)
        )
        _switch_round_writer(_round_state[game_id], uid0)
        _round_state[game_id]["turn_id"] = 1
        asyncio.create_task(
            _timeout_for_turn(
                bot, session_maker, game_id, 0, 1, 1
            )
        )
    except Exception as exc:
        logger.warning("delayed_start_round_1: %s", exc)
        st = _round_state.pop(game_id, None)
        if st:
            _release_round_chat_restrictions(st)
        _chat_to_game.pop(slot, None)


async def _timeout_for_turn(
    bot: Bot,
    session_maker: SessionMaker,
    game_id: int,
    participant_index: int,
    turn_id: int,
    expected_round: int,
) -> None:
    state = _round_state.get(game_id)
    timeout_sec = int(state.get("timeout_seconds", 120)) if state else 120
    if timeout_sec > 60:
        await asyncio.sleep(timeout_sec - 60)
        state = _round_state.get(game_id)
        if not state:
            return
        if state.get("turn_id") != turn_id or state.get("round_number") != expected_round:
            return
        participants = state["participant_ids"]
        lang = state.get("ui_lang", "ru")
        if participant_index < len(participants) and state.get("current_index") == participant_index:
            uid_rem, name_rem = participants[participant_index]
            name_link = f'<a href="tg://user?id={uid_rem}">{html.escape(name_rem)}</a>'
            try:
                await bot.send_message(
                    state["chat_id"],
                    t("round_turn_60sec_left", lang).format(name=name_link),
                    parse_mode=ParseMode.HTML,
                    **_tw(state),
                )
            except Exception:
                pass
        await asyncio.sleep(60)
    else:
        await asyncio.sleep(timeout_sec)

    state = _round_state.get(game_id)
    if not state:
        return
    if state.get("turn_id") != turn_id or state.get("round_number") != expected_round:
        return
    participants = state["participant_ids"]
    if state["current_index"] != participant_index or participant_index >= len(participants):
        return
    lang = state.get("ui_lang", "ru")
    chat_id = state["chat_id"]
    list_msg_id = state.get("list_message_id")
    current_index = state["current_index"]
    list_participants = state.get("all_participants") or participants
    list_index = (current_index + 1) if not state.get("is_missed_pass") else len(list_participants)
    playing = participants if len(list_participants) > len(participants) else None
    async with session_maker() as session:
        totals_by_uid = await _build_totals_multiround(
            session, game_id, list_participants, list_index, state["round_number"], playing
        )
    if list_msg_id is not None:
        try:
            await edit_message_text_in_forum(
                bot,
                chat_id=chat_id,
                message_id=list_msg_id,
                text=_format_participants_list(list_participants, totals_by_uid, lang),
                message_thread_id=state.get("message_thread_id"),
                parse_mode=ParseMode.HTML,
            )
        except Exception as exc:
            logger.debug("timeout edit list: %s", exc)
    skipped_uid, skipped_name = participants[participant_index]
    skipped_link = f'<a href="tg://user?id={skipped_uid}">{html.escape(skipped_name)}</a>'
    try:
        await bot.send_message(
            chat_id,
            t("round_participant_skipped", lang).format(name=skipped_link),
            parse_mode=ParseMode.HTML,
            **_tw(state),
        )
    except Exception:
        pass
    state["current_index"] = current_index + 1
    state["throw_count"] = 0
    if state["current_index"] >= len(participants):
        _switch_round_writer(state, None)
        if state.get("is_missed_pass"):
            await _finish_round_and_maybe_next(bot, session_maker, game_id, state, None)
        else:
            await _check_catchup_or_finish(bot, session_maker, game_id, state, None)
        return
    next_uid, next_name = participants[state["current_index"]]
    name_link = f'<a href="tg://user?id={next_uid}">{html.escape(next_name)}</a>'
    text = t("round_throw_prompt", lang).format(name=name_link, emoji=MAIN_GAME_EMOJI_HINT)
    try:
        await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML, **_tw(state))
        _switch_round_writer(state, next_uid)
        state["turn_id"] = int(state.get("turn_id") or 0) + 1
        asyncio.create_task(
            _timeout_for_turn(
                bot, session_maker, game_id, state["current_index"], state["turn_id"], state["round_number"]
            )
        )
    except Exception as exc:
        logger.warning("timeout_for_turn next: %s", exc)


async def process_one_throw(
    bot: Bot,
    session: AsyncSession | None,
    session_maker: SessionMaker | None,
    *,
    chat_id: int,
    game_id: int,
    state: dict[str, Any],
    user_id: int,
    value: int,
) -> None:
    lang = state.get("ui_lang", "ru")
    participants = state["participant_ids"]
    current_index = state["current_index"]
    current_name = participants[current_index][1]

    async def _db(coro):
        if session is not None:
            return await coro(session)
        assert session_maker is not None
        async with session_maker() as s:
            r = await coro(s)
            await s.commit()
            return r

    async def add_throw(s: AsyncSession):
        await throws_repo.add_throw(
            s,
            game_id=game_id,
            user_id=user_id,
            round_number=state["round_number"],
            throw_index=int(state["throw_count"]),
            value=value,
        )

    await _db(lambda s: add_throw(s))

    state["throw_count"] += 1
    throw_count = state["throw_count"]
    result_line = t("round_your_result", lang).format(value=value)
    if throw_count == 1:
        await bot.send_message(
            chat_id,
            f"{result_line}\n{t('round_throw_2_more', lang).format(emoji=MAIN_GAME_EMOJI_HINT)}",
            **_tw(state),
        )
        return
    if throw_count == 2:
        await bot.send_message(
            chat_id,
            f"{result_line}\n{t('round_throw_1_more', lang).format(emoji=MAIN_GAME_EMOJI_HINT)}",
            **_tw(state),
        )
        return

    async def round_totals(s: AsyncSession):
        return await throws_repo.get_round_totals(s, game_id, state["round_number"])

    totals_rows = await _db(lambda s: round_totals(s))
    current_total = next((tot for uid, tot in totals_rows if uid == user_id), 0)
    name_link = f'<a href="tg://user?id={user_id}">{html.escape(current_name)}</a>'
    third = t("round_third_throw_done", lang).format(
        result_line=result_line, name=name_link, total=current_total
    )
    try:
        await bot.send_message(chat_id, third, parse_mode=ParseMode.HTML, **_tw(state))
    except Exception:
        pass

    list_participants = state.get("all_participants") or state["participant_ids"]
    list_index = (state["current_index"] + 1) if not state.get("is_missed_pass") else len(list_participants)
    playing = state["participant_ids"] if len(list_participants) > len(state["participant_ids"]) else None

    async def build_tot(s: AsyncSession):
        return await _build_totals_multiround(
            s, game_id, list_participants, list_index, state["round_number"], playing
        )

    totals_by_uid = await _db(lambda s: build_tot(s))
    list_msg_id = state.get("list_message_id")
    if list_msg_id is not None:
        try:
            await edit_message_text_in_forum(
                bot,
                chat_id=chat_id,
                message_id=list_msg_id,
                text=_format_participants_list(list_participants, totals_by_uid, lang),
                message_thread_id=state.get("message_thread_id"),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
    state["current_index"] += 1
    state["throw_count"] = 0
    if state["current_index"] >= len(participants):
        _switch_round_writer(state, None)
        if state.get("is_missed_pass"):
            await _finish_round_and_maybe_next(bot, session_maker, game_id, state, session)
        else:
            await _check_catchup_or_finish(bot, session_maker, game_id, state, session)
        return
    next_uid, next_name = participants[state["current_index"]]
    name_link2 = f'<a href="tg://user?id={next_uid}">{html.escape(next_name)}</a>'
    text2 = t("round_throw_prompt", lang).format(name=name_link2, emoji=MAIN_GAME_EMOJI_HINT)
    try:
        await asyncio.sleep(3)
        await bot.send_message(chat_id, text2, parse_mode=ParseMode.HTML, **_tw(state))
        _switch_round_writer(state, next_uid)
        state["turn_id"] = int(state.get("turn_id") or 0) + 1
        assert session_maker is not None
        asyncio.create_task(
            _timeout_for_turn(
                bot, session_maker, game_id, state["current_index"], state["turn_id"], state["round_number"]
            )
        )
    except Exception as exc:
        logger.warning("process_one_throw next: %s", exc)


async def _check_catchup_or_finish(
    bot: Bot,
    session_maker: SessionMaker,
    game_id: int,
    state: dict[str, Any],
    handler_session: AsyncSession | None,
) -> None:
    lang = state.get("ui_lang", "ru")
    chat_id = state["chat_id"]
    round_number = state["round_number"]
    participants_this_round = state["participant_ids"]

    async def totals(s: AsyncSession):
        return dict(await throws_repo.get_round_totals(s, game_id, round_number))

    if handler_session is not None:
        totals_by_uid = await totals(handler_session)
    else:
        async with session_maker() as s:
            totals_by_uid = await totals(s)
    for uid, _ in participants_this_round:
        totals_by_uid.setdefault(uid, 0)
    missed = [uid for uid, _ in participants_this_round if totals_by_uid[uid] == 0]
    if not missed:
        await _finish_round_and_maybe_next(bot, session_maker, game_id, state, handler_session)
        return

    lines = [t("round_participants_missed", lang), ""]
    missed_with_names: list[tuple[int, str]] = []
    async with session_maker() as session:
        for uid in missed:
            u = await users_repo.get_user(session, uid)
            name = _display_name(u, uid)
            safe_name = html.escape(name)
            lines.append(f'• <a href="tg://user?id={uid}">{safe_name}</a>')
            missed_with_names.append((uid, name))
    lines.append("")
    lines.append(t("round_catchup_5min", lang))
    try:
        await bot.send_message(chat_id, "\n".join(lines), parse_mode=ParseMode.HTML, **_tw(state))
    except Exception:
        pass
    state["participant_ids"] = missed_with_names
    state["current_index"] = 0
    state["throw_count"] = 0
    state["timeout_seconds"] = 60
    state["is_missed_pass"] = True
    uid0, name0 = missed_with_names[0]
    name_link = f'<a href="tg://user?id={uid0}">{html.escape(name0)}</a>'
    text = t("round_throw_prompt", lang).format(name=name_link, emoji=MAIN_GAME_EMOJI_HINT)
    try:
        await asyncio.sleep(3)
        await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML, **_tw(state))
        _switch_round_writer(state, uid0)
        state["turn_id"] = int(state.get("turn_id") or 0) + 1
        asyncio.create_task(
            _timeout_for_turn(bot, session_maker, game_id, 0, state["turn_id"], round_number)
        )
    except Exception as exc:
        logger.warning("catchup start: %s", exc)


async def _finish_round_and_maybe_next(
    bot: Bot,
    session_maker: SessionMaker,
    game_id: int,
    state: dict[str, Any],
    handler_session: AsyncSession | None,
) -> None:
    lang = state.get("ui_lang", "ru")
    chat_id = state["chat_id"]
    _switch_round_writer(state, None)
    participants_this_round = state.get("round_participants") or state["participant_ids"]
    participants = state.get("all_participants") or participants_this_round
    round_number = state["round_number"]

    async def get_tot(s: AsyncSession):
        return dict(await throws_repo.get_round_totals(s, game_id, round_number))

    if handler_session is not None:
        totals_by_uid = await get_tot(handler_session)
    else:
        async with session_maker() as s:
            totals_by_uid = await get_tot(s)

    values = [total for _, total in totals_by_uid.items()]
    avg = sum(values) / len(values) if values else 0
    passing_score = int(avg)

    async with session_maker() as session:
        game = await games_repo.get(session, game_id)
        prize_places = int(game.prize_places or 1) if game else 1

    if not state.get("is_final_round"):
        round_label = (
            t("round_1_finished", lang)
            if round_number == 1
            else t("round_N_finished", lang).format(round=round_number)
        )
        try:
            await bot.send_message(
                chat_id,
                "\n".join(
                    [
                        round_label,
                        t("round_passing_score", lang).format(score=passing_score),
                    ]
                ),
                **_tw(state),
            )
        except Exception:
            pass

    if state.get("is_final_round"):
        state["participant_ids"] = participants_this_round
        started = await _do_tiebreak_and_winners(
            bot, session_maker, game_id, state, [], prize_places, handler_session
        )
        if not started:
            _release_round_state(game_id)
        return

    passed = [(uid, total) for uid, total in totals_by_uid.items() if total >= passing_score]
    passed.sort(key=lambda x: -x[1])
    if not passed:
        _release_round_state(game_id)
        return

    async with session_maker() as session:
        passed_with_names: list[tuple[int, str]] = []
        for uid, _ in passed:
            u = await users_repo.get_user(session, uid)
            passed_with_names.append((uid, _display_name(u, uid)))

    num_next = len(passed_with_names)
    is_final_next = num_next < 8 or num_next < (prize_places * 3)
    header_key = "round_list_passed_final" if is_final_next else "round_list_passed"
    lines_passed = [t(header_key, lang), ""]
    for i, (uid, _) in enumerate(passed, 1):
        async with session_maker() as session:
            u = await users_repo.get_user(session, uid)
            name = _display_name(u, uid)
        safe_name = html.escape(name)
        lines_passed.append(f'{i}. <a href="tg://user?id={uid}">{safe_name}</a>')
    try:
        await bot.send_message(
            chat_id, "\n".join(lines_passed), parse_mode=ParseMode.HTML, **_tw(state)
        )
    except Exception:
        pass

    all_display = state.get("all_participants") or state["participant_ids"]
    await _start_round_n(
        bot,
        session_maker,
        game_id,
        chat_id,
        state["game_type"],
        state.get("message_thread_id"),
        state.get("list_message_id"),
        passed_with_names,
        round_number + 1,
        is_final_round=is_final_next,
        all_display_participants=all_display,
    )


async def _start_round_n(
    bot: Bot,
    session_maker: SessionMaker,
    game_id: int,
    chat_id: int,
    game_type: str,
    message_thread_id: int | None,
    list_message_id: int | None,
    participants: list[tuple[int, str]],
    round_number: int,
    *,
    is_final_round: bool,
    all_display_participants: list[tuple[int, str]] | None,
) -> None:
    async with session_maker() as session:
        lang = await _pick_ui_lang(session, [p[0] for p in participants])
        await games_repo.update(session, game_id, current_round=round_number)
        await session.commit()

    display_list = list(all_display_participants or participants)
    if round_number > 1:
        async with session_maker() as session:
            prev_totals = dict(
                await throws_repo.get_round_totals(session, game_id, round_number - 1)
            )
        display_list = sorted(display_list, key=lambda p: -prev_totals.get(p[0], 0))

    _round_state[game_id] = {
        "ui_lang": lang,
        "participant_ids": list(participants),
        "round_participants": list(participants),
        "all_participants": display_list,
        "current_index": 0,
        "throw_count": 0,
        "chat_id": chat_id,
        "message_thread_id": message_thread_id,
        "game_type": game_type,
        "round_number": round_number,
        "list_message_id": list_message_id,
        "is_final_round": is_final_round,
        "turn_id": 0,
    }
    slot = play_slot_key(chat_id, message_thread_id)
    _chat_to_game[slot] = game_id

    async with session_maker() as session:
        if all_display_participants is not None:
            totals_by_uid = await _build_totals_multiround(
                session, game_id, display_list, 0, round_number, playing_participants=participants
            )
        else:
            totals_by_uid = await _build_totals_multiround(
                session, game_id, participants, 0, round_number
            )

    if list_message_id is not None:
        try:
            await edit_message_text_in_forum(
                bot,
                chat_id=chat_id,
                message_id=list_message_id,
                text=_format_participants_list(display_list, totals_by_uid, lang),
                message_thread_id=message_thread_id,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
    uid0, name0 = participants[0]
    name_link = f'<a href="tg://user?id={uid0}">{html.escape(name0)}</a>'
    text = t("round_throw_prompt", lang).format(name=name_link, emoji=MAIN_GAME_EMOJI_HINT)
    try:
        await bot.send_message(
            chat_id, text, parse_mode=ParseMode.HTML, **thread_kw(message_thread_id)
        )
        _switch_round_writer(_round_state[game_id], uid0)
        _round_state[game_id]["turn_id"] = 1
        asyncio.create_task(
            _timeout_for_turn(bot, session_maker, game_id, 0, 1, round_number)
        )
    except Exception as exc:
        logger.warning("start_round_n: %s", exc)
        _release_round_state(game_id)


async def _start_tiebreak_turn(
    bot: Bot, session_maker: SessionMaker, game_id: int, state: dict[str, Any], index: int
) -> None:
    tied = state.get("tiebreak_tied_group") or []
    if index >= len(tied):
        return
    uid, name = tied[index]
    state["tiebreak_wait_uid"] = uid
    state["tiebreak_index"] = index
    state["phase"] = "tiebreak"
    lang = state.get("ui_lang", "ru")
    chat_id = state["chat_id"]
    emoji = (
        MAIN_GAME_EMOJI_HINT
        if state.get("game_type") == GameType.ANY
        else GAME_TYPE_DICE_EMOJI.get(state["game_type"], "🎲")
    )
    name_link = f'<a href="tg://user?id={uid}">{html.escape(name)}</a>'
    text = t("round_tiebreak_throw", lang).format(name=name_link, emoji=emoji)
    try:
        await bot.send_message(chat_id, text, parse_mode=ParseMode.HTML, **_tw(state))
        _switch_round_writer(state, uid)
        asyncio.create_task(_timeout_tiebreak_turn(bot, session_maker, game_id, index))
    except Exception as exc:
        logger.warning("start_tiebreak_turn: %s", exc)


async def _timeout_tiebreak_turn(
    bot: Bot, session_maker: SessionMaker, game_id: int, waiting_index: int
) -> None:
    await asyncio.sleep(120)
    state = _round_state.get(game_id)
    if not state or state.get("phase") != "tiebreak":
        return
    tied = state.get("tiebreak_tied_group") or []
    if waiting_index >= len(tied) or state.get("tiebreak_index") != waiting_index:
        return
    lang = state.get("ui_lang", "ru")
    chat_id = state["chat_id"]
    skipped_uid, skipped_name = tied[waiting_index]
    async with session_maker() as session:
        await throws_repo.add_throw(
            session,
            game_id=game_id,
            user_id=skipped_uid,
            round_number=state["round_number"],
            throw_index=int(state.get("tiebreak_next_throw_index", 3)),
            value=0,
        )
        await session.commit()
    state["tiebreak_next_throw_index"] = int(state.get("tiebreak_next_throw_index", 3)) + 1
    state["tiebreak_index"] = waiting_index + 1
    skipped_link = f'<a href="tg://user?id={skipped_uid}">{html.escape(skipped_name)}</a>'
    try:
        await bot.send_message(
            chat_id,
            t("round_participant_skipped", lang).format(name=skipped_link),
            parse_mode=ParseMode.HTML,
            **_tw(state),
        )
    except Exception:
        pass
    prize_places = state.get("prize_places_cache", 1)
    if state["tiebreak_index"] >= len(tied):
        state["phase"] = None
        state["tiebreak_cycle_completed"] = True
        await _do_tiebreak_and_winners(
            bot, session_maker, game_id, state, [], prize_places, None
        )
        return
    await _start_tiebreak_turn(bot, session_maker, game_id, state, state["tiebreak_index"])


async def _do_tiebreak_and_winners(
    bot: Bot,
    session_maker: SessionMaker,
    game_id: int,
    state: dict[str, Any],
    passed: list,
    prize_places: int,
    handler_session: AsyncSession | None,
) -> bool:
    lang = state.get("ui_lang", "ru")
    chat_id = state["chat_id"]
    round_number = state["round_number"]

    async def load_totals(s: AsyncSession):
        base = dict(await throws_repo.get_round_totals(s, game_id, round_number))
        extra = dict(await throws_repo.get_round_tiebreak_totals(s, game_id, round_number))
        return base, extra

    if handler_session is not None:
        by_uid_base, by_uid_extra = await load_totals(handler_session)
    else:
        async with session_maker() as s:
            by_uid_base, by_uid_extra = await load_totals(s)

    for uid, _ in state["participant_ids"]:
        by_uid_base.setdefault(uid, 0)
        by_uid_extra.setdefault(uid, 0)

    ordered = sorted(
        state["participant_ids"],
        key=lambda p: (-by_uid_base.get(p[0], 0), -by_uid_extra.get(p[0], 0)),
    )

    async def announce_places(start_idx: int, end_exclusive: int) -> None:
        lines = [t("round_results_header", lang), ""]
        for pos in range(start_idx, end_exclusive):
            uid, name = ordered[pos]
            safe = html.escape(name)
            lines.append(f'{pos + 1}. <a href="tg://user?id={uid}">{safe}</a>')
        try:
            await bot.send_message(
                chat_id, "\n".join(lines), parse_mode=ParseMode.HTML, **_tw(state)
            )
        except Exception:
            pass

    if state.get("tiebreak_cycle_completed") and state.get("tiebreak_target_from") is not None:
        target_from = int(state["tiebreak_target_from"])
        target_to = int(state["tiebreak_target_to"])
        tied_group = state.get("tiebreak_tied_group") or []
        slots_count = max(1, target_to - target_from)
        ranked = sorted(tied_group, key=lambda p: (-by_uid_extra.get(p[0], 0), p[1].lower()))
        if len(ranked) <= slots_count:
            await announce_places(target_from, target_to)
            for k in (
                "tiebreak_cycle_completed",
                "tiebreak_target_from",
                "tiebreak_target_to",
                "tiebreak_tied_group",
                "tiebreak_wait_uid",
                "tiebreak_ordered",
                "phase",
            ):
                state.pop(k, None)
        else:
            boundary_score = by_uid_extra.get(ranked[slots_count - 1][0], 0)
            higher = [p for p in ranked if by_uid_extra.get(p[0], 0) > boundary_score]
            equal = [p for p in ranked if by_uid_extra.get(p[0], 0) == boundary_score]
            remaining_slots = slots_count - len(higher)
            if remaining_slots > 0 and len(equal) > remaining_slots:
                next_target_from = target_from + len(higher)
                next_target_to = next_target_from + remaining_slots
                try:
                    pr = _place_range_label(lang, next_target_from, next_target_to)
                    lines = [t("round_tiebreak", lang), t("round_tiebreak_for", lang).format(places=pr), ""]
                    for uid, name in equal:
                        lines.append(
                            f'• <a href="tg://user?id={uid}">{html.escape(name)}</a>'
                        )
                    await bot.send_message(
                        chat_id, "\n".join(lines), parse_mode=ParseMode.HTML, **_tw(state)
                    )
                except Exception:
                    pass
                state["tiebreak_tied_group"] = equal
                state["tiebreak_target_from"] = next_target_from
                state["tiebreak_target_to"] = next_target_to
                state["tiebreak_index"] = 0
                state["phase"] = "tiebreak"
                state["tiebreak_cycle_completed"] = False
                state.setdefault("tiebreak_next_throw_index", 3)
                await _start_tiebreak_turn(bot, session_maker, game_id, state, 0)
                return True
            await announce_places(target_from, target_to)
            for k in (
                "tiebreak_cycle_completed",
                "tiebreak_target_from",
                "tiebreak_target_to",
                "tiebreak_tied_group",
                "tiebreak_wait_uid",
                "tiebreak_ordered",
                "phase",
            ):
                state.pop(k, None)

    while True:
        async with session_maker() as s:
            by_uid_base, by_uid_extra = await load_totals(s)
        for uid, _ in state["participant_ids"]:
            by_uid_base.setdefault(uid, 0)
            by_uid_extra.setdefault(uid, 0)
        ordered = sorted(
            state["participant_ids"],
            key=lambda p: (-by_uid_base.get(p[0], 0), -by_uid_extra.get(p[0], 0)),
        )
        groups: list[tuple[int, int, list[tuple[int, str]]]] = []
        i = 0
        while i < len(ordered):
            j = i + 1
            key_i = (by_uid_base.get(ordered[i][0], 0), by_uid_extra.get(ordered[i][0], 0))
            while j < len(ordered):
                key_j = (by_uid_base.get(ordered[j][0], 0), by_uid_extra.get(ordered[j][0], 0))
                if key_j != key_i:
                    break
                j += 1
            if j - i > 1:
                groups.append((i, j, ordered[i:j]))
            i = j
        candidates = [(s, e, g) for (s, e, g) in groups if s < prize_places]
        if not candidates:
            break
        tied_from, tied_to, tied = max(candidates, key=lambda x: x[0])
        target_to = min(tied_to, prize_places)
        try:
            pr = _place_range_label(lang, tied_from, target_to)
            lines = [t("round_tiebreak", lang), t("round_tiebreak_for", lang).format(places=pr), ""]
            for uid, name in tied:
                lines.append(f'• <a href="tg://user?id={uid}">{html.escape(name)}</a>')
            await bot.send_message(
                chat_id, "\n".join(lines), parse_mode=ParseMode.HTML, **_tw(state)
            )
        except Exception:
            pass
        state["tiebreak_ordered"] = ordered
        state["tiebreak_tied_group"] = tied
        state["tiebreak_index"] = 0
        state["tiebreak_target_from"] = tied_from
        state["tiebreak_target_to"] = target_to
        state["tiebreak_cycle_completed"] = False
        state.setdefault("tiebreak_next_throw_index", 3)
        state["prize_places_cache"] = prize_places
        await _start_tiebreak_turn(bot, session_maker, game_id, state, 0)
        return True

    header_lines: list[str] = []
    if state.get("is_final_round"):
        header_lines.append(t("round_final_finished", lang))
        header_lines.append("")
    me = await bot.get_me()
    bot_un = me.username or "bot"
    sponsor = t("game_sponsor_line", lang).format(bot_link=f"https://t.me/{bot_un}")
    lines = header_lines + [t("round_winners", lang), ""]
    async with session_maker() as session:
        prize_rows = await prizes_repo.for_game(session, game_id)
        by_place = {p.place_number: p.amount for p in prize_rows}

    for i, (uid, name) in enumerate(ordered[:prize_places], 1):
        safe_name = html.escape(name)
        amt = by_place.get(i)
        if amt is not None:
            lines.append(
                f'{i}. <a href="tg://user?id={uid}">{safe_name}</a> — {_fmt_pln(amt)} PLN'
            )
        else:
            lines.append(f'{i}. <a href="tg://user?id={uid}">{safe_name}</a>')
    lines.append("")
    lines.append(sponsor)
    try:
        await bot.send_message(
            chat_id, "\n".join(lines), parse_mode=ParseMode.HTML, **_tw(state)
        )
    except Exception as exc:
        logger.warning("winners chat msg: %s", exc)

    settings = get_settings()
    async with session_maker() as session:
        menu_chats = await app_chats_repo.list_for_main_menu(session)
        show_game21 = await g21_repo.any_game21_enabled(session)
        show_checkers = await checkers_repo.is_enabled(session)
        show_slot = await slot_repo.is_enabled(session)
        prize_rows = await prizes_repo.for_game(session, game_id)
        by_place = {p.place_number: p.amount for p in prize_rows}
        for i in range(min(prize_places, len(ordered))):
            uid = ordered[i][0]
            amount = by_place.get(i + 1)
            if amount is None or amount <= 0:
                continue
            u = await users_repo.get_user(session, uid)
            if u is None:
                continue
            u.balance = (u.balance or Decimal("0")) + amount
            await session.flush()
            await payment_logs_repo.log(
                session,
                user_id=uid,
                method=PaymentLogMethod.GAME_PRIZE,
                amount=amount,
                balance_after=u.balance,
            )
            ulang = get_lang(u.language_code)
            try:
                await bot.send_message(
                    uid,
                    t("game_dm_prize_won", ulang).format(
                        place=i + 1, amount=_fmt_pln(amount)
                    ),
                    parse_mode=ParseMode.HTML,
                    reply_markup=main_menu_keyboard(
                        ulang,
                        uid,
                        settings.admin_id,
                        menu_chats=menu_chats,
                        show_game21=show_game21,
                        show_checkers=show_checkers,
                        show_slot=show_slot,
                    ),
                )
            except Exception as exc:
                logger.warning("prize dm user=%s: %s", uid, exc)
        g = await games_repo.get(session, game_id)
        ann_id = g.announcement_message_id if g else None
        ann_gen_id = g.announcement_message_id_general if g else None
        list_mid = state.get("list_message_id")
        await games_repo.update(session, game_id, status=GameStatus.FINISHED)
        await session.commit()

    if ann_id:
        try:
            await unpin_chat_message_in_forum(
                bot,
                chat_id=chat_id,
                message_id=int(ann_id),
                message_thread_id=state.get("message_thread_id"),
            )
        except Exception:
            pass
    if ann_gen_id:
        try:
            await unpin_chat_message_in_forum(
                bot,
                chat_id=chat_id,
                message_id=int(ann_gen_id),
                message_thread_id=None,
            )
        except Exception:
            pass
    if state.get("list_message_id") is not None:
        try:
            await unpin_chat_message_in_forum(
                bot,
                chat_id=chat_id,
                message_id=int(state["list_message_id"]),
                message_thread_id=state.get("message_thread_id"),
            )
        except Exception:
            pass
    _release_round_state(game_id)
    return False


async def handle_game_dice_message(
    bot: Bot,
    message: Message,
    session: AsyncSession,
    session_maker: SessionMaker,
) -> None:
    if message.forward_date is not None or getattr(message, "forward_origin", None) is not None:
        return
    chat_id = message.chat.id
    game_id = resolve_active_game_id(chat_id, message.message_thread_id)
    if game_id is None:
        return
    state = _round_state.get(game_id)
    if not state:
        return
    user_id = message.from_user.id if message.from_user else None
    if user_id is None or not message.dice:
        return
    lang = state.get("ui_lang", "ru")
    if state.get("phase") == "tiebreak":
        if user_id != state.get("tiebreak_wait_uid"):
            return
        if message.dice.emoji not in MAIN_GAME_ALLOWED_EMOJIS:
            return
        throw_idx = int(state.get("tiebreak_next_throw_index", 3))
        await throws_repo.add_throw(
            session,
            game_id=game_id,
            user_id=user_id,
            round_number=state["round_number"],
            throw_index=throw_idx,
            value=int(message.dice.value),
        )
        await session.flush()
        name = next(
            (n for u, n in (state.get("tiebreak_tied_group") or []) if u == user_id),
            str(user_id),
        )
        name_link = f'<a href="tg://user?id={user_id}">{html.escape(name)}</a>'
        try:
            await bot.send_message(
                chat_id,
                t("round_tiebreak_result", lang).format(
                    name=name_link, value=int(message.dice.value)
                ),
                parse_mode=ParseMode.HTML,
                **_tw(state),
            )
        except Exception:
            pass
        state["tiebreak_next_throw_index"] = throw_idx + 1
        tied = state.get("tiebreak_tied_group") or []
        state["tiebreak_index"] = int(state.get("tiebreak_index", 0)) + 1
        if state["tiebreak_index"] < len(tied):
            await _start_tiebreak_turn(bot, session_maker, game_id, state, state["tiebreak_index"])
        else:
            state["phase"] = None
            state["tiebreak_cycle_completed"] = True
            g = await games_repo.get(session, game_id)
            prize_places = int(g.prize_places or 1) if g else 1
            await _do_tiebreak_and_winners(
                bot, session_maker, game_id, state, [], prize_places, session
            )
        return
    participants = state["participant_ids"]
    current_index = state["current_index"]
    if current_index >= len(participants):
        return
    current_uid = participants[current_index][0]
    if user_id != current_uid:
        return
    if message.dice.emoji not in MAIN_GAME_ALLOWED_EMOJIS:
        return
    await process_one_throw(
        bot,
        session,
        session_maker,
        chat_id=chat_id,
        game_id=game_id,
        state=state,
        user_id=user_id,
        value=int(message.dice.value),
    )


async def handle_game_emoji_text_message(
    bot: Bot,
    message: Message,
    session: AsyncSession,
    session_maker: SessionMaker,
) -> None:
    if not message.text:
        return
    chat_id = message.chat.id
    game_id = resolve_active_game_id(chat_id, message.message_thread_id)
    if game_id is None:
        return
    state = _round_state.get(game_id)
    if not state:
        return
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        return
    text = message.text.strip()
    if not any(text.startswith(e) for e in MAIN_GAME_ALLOWED_EMOJIS):
        return
    lang = state.get("ui_lang", "ru")
    if state.get("phase") == "tiebreak":
        if user_id != state.get("tiebreak_wait_uid"):
            return
        value = random.randint(1, 6)
        throw_idx = int(state.get("tiebreak_next_throw_index", 3))
        await throws_repo.add_throw(
            session,
            game_id=game_id,
            user_id=user_id,
            round_number=state["round_number"],
            throw_index=throw_idx,
            value=value,
        )
        await session.flush()
        name = next(
            (n for u, n in (state.get("tiebreak_tied_group") or []) if u == user_id),
            str(user_id),
        )
        name_link = f'<a href="tg://user?id={user_id}">{html.escape(name)}</a>'
        try:
            await bot.send_message(
                chat_id,
                t("round_tiebreak_result", lang).format(name=name_link, value=value),
                parse_mode=ParseMode.HTML,
                **_tw(state),
            )
        except Exception:
            pass
        state["tiebreak_next_throw_index"] = throw_idx + 1
        tied = state.get("tiebreak_tied_group") or []
        state["tiebreak_index"] = int(state.get("tiebreak_index", 0)) + 1
        if state["tiebreak_index"] < len(tied):
            await _start_tiebreak_turn(bot, session_maker, game_id, state, state["tiebreak_index"])
        else:
            state["phase"] = None
            state["tiebreak_cycle_completed"] = True
            g = await games_repo.get(session, game_id)
            prize_places = int(g.prize_places or 1) if g else 1
            await _do_tiebreak_and_winners(
                bot, session_maker, game_id, state, [], prize_places, session
            )
        return
    participants = state["participant_ids"]
    current_index = state["current_index"]
    if current_index >= len(participants):
        return
    if user_id != participants[current_index][0]:
        return
    value = random.randint(1, 6)
    await process_one_throw(
        bot,
        session,
        session_maker,
        chat_id=chat_id,
        game_id=game_id,
        state=state,
        user_id=user_id,
        value=value,
    )
