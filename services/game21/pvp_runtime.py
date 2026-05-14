"""Игровой цикл PvP «21» в группе (кубик 🎲), завершение и приём вызова."""

from __future__ import annotations

import html
import logging
import time
from decimal import Decimal
from typing import Any

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.repositories import game21_history as g21_hist
from database.repositories import users as users_repo
from locales.texts import t
from services.game21.balance import (
    METHOD_PVP_REFUND,
    METHOD_PVP_WIN,
    add_balance,
)
from services.game21.formatting import fmt_money, name_link, possible_win_pvp, pvp_status_line
from services.game21.pvp_state import (
    get_live,
    lock_for_chat,
    pop_live,
    session_token,
    slot_key,
    store_live,
)
from services.games.forum_thread import edit_message_text_in_forum, thread_kw, unpin_chat_message_in_forum

logger = logging.getLogger(__name__)

SessionMaker = async_sessionmaker[AsyncSession]


async def _bot_link_html(bot: Bot, lang: str) -> str:
    try:
        me = await bot.get_me()
        un = (me.username or "").strip()
        if not un:
            return "—"
        return f'<a href="https://t.me/{html.escape(un)}">@{html.escape(un)}</a>'
    except Exception:
        return "—"


def _tw(st: dict[str, Any]) -> dict[str, Any]:
    return thread_kw(st.get("message_thread_id"))


def pvp_match_card_html(lang: str, st: dict[str, Any]) -> str:
    """Карточка матча PvP: заголовок, игроки, приз, правила в blockquote."""
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    names = st.get("names") or {}
    totals = st.get("totals") or {}
    t1 = totals.get(p1) if p1 in totals else None
    t2 = totals.get(p2) if p2 in totals else None
    bet = Decimal(str(st.get("bet_amount") or "0"))
    c = Decimal(str(st.get("commission_percent") or "0"))
    win_str = fmt_money(possible_win_pvp(bet, c))
    p1_h = pvp_status_line(name_link(p1, str(names.get(p1, p1))), t1)
    p2_h = pvp_status_line(name_link(p2, str(names.get(p2, p2))), t2)
    title = html.escape(t("game21_pvp_match_title", lang))
    prize = t("game21_pvp_match_prize", lang).format(win=html.escape(win_str))
    rules_heading = html.escape(t("game21_pvp_match_rules_heading", lang))
    rules_body = html.escape(t("game21_pvp_rules_body", lang))
    body = (
        f"<b>{title}</b>\n"
        f"{p1_h}\n"
        f"{p2_h}\n\n"
        f"{prize}\n\n"
        f"<b>{rules_heading}</b>\n"
        f"<blockquote>{rules_body}</blockquote>"
    )
    return body


def pvp_decide_first_prompt_html(lang: str, st: dict[str, Any]) -> str:
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    names = st.get("names") or {}
    players = f"{name_link(p1, str(names.get(p1, p1)))}, {name_link(p2, str(names.get(p2, p2)))}"
    return t("game21_pvp_decide_first", lang).format(players=players)


def pvp_match_general_channel_html(lang: str, st: dict[str, Any], *, room_label: str) -> str:
    """Короткое сообщение в основной ветке группы: игра началась в теме {room}, игроки, приз (без правил)."""
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    names = st.get("names") or {}
    bet = Decimal(str(st.get("bet_amount") or "0"))
    c = Decimal(str(st.get("commission_percent") or "0"))
    win_str = fmt_money(possible_win_pvp(bet, c))
    p1_h = pvp_status_line(name_link(p1, str(names.get(p1, p1))), None)
    p2_h = pvp_status_line(name_link(p2, str(names.get(p2, p2))), None)
    room_e = html.escape(room_label)
    head = t("game21_pvp_match_started_in_topic", lang).format(room=room_e)
    prize = t("game21_pvp_match_prize", lang).format(win=html.escape(win_str))
    return f"<b>{head}</b>\n{p1_h}\n{p2_h}\n\n{prize}"


async def pvp_status_message_html(bot: Bot, lang: str, st: dict[str, Any]) -> str:
    return pvp_match_card_html(lang, st)


async def _pvp_update_status_message(bot: Bot, st: dict[str, Any]) -> None:
    lang = st.get("lang") or "ru"
    chat_id = int(st.get("chat_id") or 0)
    text = await pvp_status_message_html(bot, lang, st)
    mid = int(st.get("status_message_id") or 0)
    if mid:
        try:
            await edit_message_text_in_forum(
                bot,
                chat_id=chat_id,
                message_id=mid,
                text=text,
                message_thread_id=st.get("message_thread_id"),
                parse_mode=ParseMode.HTML,
                reply_markup=None,
            )
        except Exception as exc:
            logger.warning("pvp status edit: %s", exc)


async def _pvp_prompt_turn(bot: Bot, st: dict[str, Any]) -> None:
    lang = st.get("lang") or "ru"
    uid = int(st.get("current_turn_uid") or 0)
    names = st.get("names") or {}
    nm = str(names.get(uid, str(uid)))
    await bot.send_message(
        int(st["chat_id"]),
        t("game21_pvp_turn_prompt", lang).format(name=name_link(uid, nm)),
        parse_mode=ParseMode.HTML,
        **_tw(st),
    )


async def _pvp_after_turn_end(bot: Bot, session_maker: SessionMaker, st: dict[str, Any], finished_uid: int) -> None:
    chat_id = int(st["chat_id"])
    sk = slot_key(chat_id, st.get("message_thread_id"))
    st = get_live(sk) or st
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    other_uid = p2 if int(finished_uid) == p1 else p1
    turns_done = dict(st.get("turns_done") or {})
    if not turns_done:
        turns_done = {
            p1: bool(int(finished_uid) == p1),
            p2: bool(int(finished_uid) == p2),
        }
    if not turns_done.get(other_uid):
        st["current_turn_uid"] = other_uid
        if not store_live(sk, st):
            return
        await _pvp_prompt_turn(bot, st)
        return
    t1 = int((st.get("totals") or {}).get(p1, 0))
    t2 = int((st.get("totals") or {}).get(p2, 0))
    if t1 > 21 and t2 > 21:
        await finish_pvp_game(bot, session_maker, sk, draw=True)
        return
    if t1 > 21:
        await finish_pvp_game(bot, session_maker, sk, winner_id=p2)
        return
    if t2 > 21:
        await finish_pvp_game(bot, session_maker, sk, winner_id=p1)
        return
    if t1 == t2:
        await finish_pvp_game(bot, session_maker, sk, draw=True)
        return
    winner = p1 if t1 > t2 else p2
    await finish_pvp_game(bot, session_maker, sk, winner_id=winner)


async def finish_pvp_game(
    bot: Bot,
    session_maker: SessionMaker,
    sk: tuple[int, int],
    *,
    winner_id: int | None = None,
    draw: bool = False,
) -> None:
    chat_id = sk[0]
    thread_id = sk[1] if sk[1] else None
    lock = lock_for_chat(chat_id, thread_id)
    async with lock:
        if not get_live(sk):
            return
        await _finish_pvp_game_locked(
            bot, session_maker, sk, winner_id=winner_id, draw=draw
        )


async def _finish_pvp_game_locked(
    bot: Bot,
    session_maker: SessionMaker,
    sk: tuple[int, int],
    *,
    winner_id: int | None = None,
    draw: bool = False,
) -> None:
    current = get_live(sk) or {}
    if not current:
        return
    if bool(current.get("finished")):
        return
    # Мутируем dict из `_pvp_live` (под lock в `finish_pvp_game`), без `store_live`:
    # иначе guard «finished» в `store_live` заблокировал бы запись.
    current["finished"] = True
    current["finished_at"] = time.time()
    st = current
    tok = session_token(st)
    lang = st.get("lang") or "ru"
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    bet = Decimal(str(st.get("bet_amount") or "0"))
    commission = Decimal(str(st.get("commission_percent") or "0"))
    gross = bet * 2
    payout = (gross * (Decimal("1") - commission / Decimal("100"))).quantize(Decimal("0.01"))
    commission_amount = (gross - payout) if not draw else Decimal("0")
    chat_id = int(st["chat_id"])
    bl = await _bot_link_html(bot, lang)

    try:
        async with session_maker() as session:
            if draw:
                await add_balance(session, p1, bet, method=METHOD_PVP_REFUND)
                await add_balance(session, p2, bet, method=METHOD_PVP_REFUND)
            elif winner_id in (p1, p2):
                await add_balance(session, int(winner_id), payout, method=METHOD_PVP_WIN)
            player_commission_base = (commission_amount / Decimal("2")).quantize(
                Decimal("0.01")
            )
            if player_commission_base > 0:
                for uid in (p1, p2):
                    await users_repo.award_referral_percent(
                        session,
                        referral_id=uid,
                        base_amount=player_commission_base,
                        source="game:21:pvp",
                    )
            pvp_tok_raw = st.get("pvp_session_token")
            pvp_tok = int(pvp_tok_raw) if pvp_tok_raw is not None else None
            await g21_hist.upsert_users_session_gb(
                session,
                chat_id=chat_id,
                pvp_session_token=pvp_tok,
                player1_id=p1,
                player2_id=p2,
                bet_amount=bet,
                commission_percent=commission,
                commission_amount=commission_amount,
                result="draw" if draw else "win",
                winner_id=None if draw else winner_id,
                round_events=list(st.get("round_events") or []),
            )
            await session.commit()

        if draw:
            await bot.send_message(
                chat_id,
                t("game21_pvp_draw", lang).format(amount=fmt_money(bet), bot_link=bl),
                parse_mode=ParseMode.HTML,
                **_tw(st),
            )
        elif winner_id in (p1, p2):
            w_name = (st.get("names") or {}).get(int(winner_id), str(winner_id))
            await bot.send_message(
                chat_id,
                t("game21_pvp_winner", lang).format(
                    name=name_link(int(winner_id), str(w_name)),
                    payout=fmt_money(payout),
                    bot_link=bl,
                ),
                parse_mode=ParseMode.HTML,
                **_tw(st),
            )

        smid = st.get("search_message_id_topic")
        if smid:
            try:
                await unpin_chat_message_in_forum(
                    bot,
                    chat_id=chat_id,
                    message_id=int(smid),
                    message_thread_id=st.get("message_thread_id"),
                )
            except Exception as exc:
                logger.debug("unpin search topic: %s", exc)
        status_mid = int(st.get("status_message_id") or 0)
        if status_mid:
            try:
                await unpin_chat_message_in_forum(
                    bot,
                    chat_id=chat_id,
                    message_id=status_mid,
                    message_thread_id=st.get("message_thread_id"),
                )
            except Exception as exc:
                logger.debug("unpin status: %s", exc)
    finally:
        live = get_live(sk) or {}
        if session_token(live) == tok:
            pop_live(sk)


def pvp_stop_keyboard(lang: str, owner_user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("game21_btn_stop", lang),
                    callback_data=f"menu:play21bot:pvp:stop:{owner_user_id}",
                )
            ]
        ]
    )


async def apply_pvp_stop(bot: Bot, session_maker: SessionMaker, cb: CallbackQuery, lang: str) -> None:
    parts = (cb.data or "").split(":")
    if len(parts) < 5:
        await cb.answer()
        return
    try:
        owner_id = int(parts[4])
    except ValueError:
        await cb.answer()
        return
    if not cb.message or not cb.from_user:
        await cb.answer()
        return
    chat_id = cb.message.chat.id
    thread_id = cb.message.message_thread_id
    sk = slot_key(chat_id, thread_id)
    lock = lock_for_chat(chat_id, thread_id)
    async with lock:
        st = get_live(sk) or {}
        if bool(st.get("finished")):
            await cb.answer()
            return
        if int(st.get("owner_id") or 0) != owner_id:
            await cb.answer()
            return
        if st.get("phase") != "turn":
            await cb.answer()
            return
        uid = cb.from_user.id
        current_uid = int(st.get("current_turn_uid") or 0)
        if uid != current_uid:
            names = st.get("names") or {}
            current_name = str(names.get(current_uid, current_uid))
            await cb.answer(
                t("game21_pvp_not_your_turn_stop", lang).format(name=current_name),
                show_alert=True,
            )
            return
        try:
            await cb.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        totals = dict(st.get("totals") or {})
        turns_done = dict(st.get("turns_done") or {})
        p1 = int(st.get("player1_id") or 0)
        p2 = int(st.get("player2_id") or 0)
        other_uid = p2 if uid == p1 else p1
        if int(totals.get(uid) or 0) < 16:
            await cb.answer()
            return
        if turns_done.get(other_uid):
            if int(totals.get(uid) or 0) != int(totals.get(other_uid) or 0):
                await cb.answer(
                    t("game21_pvp_stop_only_on_equal", lang),
                    show_alert=True,
                )
                return
        turns_done[uid] = True
        st["turns_done"] = turns_done
        if not store_live(sk, st):
            await cb.answer()
            return
    await cb.answer()
    total = int(totals.get(uid) or 0)
    name_link_s = name_link(uid, (st.get("names") or {}).get(uid, str(uid)))
    total_str = "21 ОЧКО!!!" if int(total) == 21 else str(total)
    await bot.send_message(
        chat_id,
        t("game21_pvp_stop_announce", lang).format(name=name_link_s, total=total_str),
        parse_mode=ParseMode.HTML,
        **_tw(st),
    )
    await _pvp_update_status_message(bot, st)
    await _pvp_after_turn_end(bot, session_maker, st, uid)


async def handle_pvp_group_dice(
    bot: Bot, message, session_maker: SessionMaker
) -> bool:
    if not message.chat or not message.from_user:
        return False
    if message.forward_date is not None or getattr(message, "forward_origin", None):
        return False
    sk = slot_key(message.chat.id, message.message_thread_id)
    st = get_live(sk)
    if not st:
        return False
    if bool(st.get("finished")):
        return True
    dice = message.dice
    if not dice or dice.emoji != "🎲":
        return True
    lang = st.get("lang") or "ru"
    uid = message.from_user.id
    p1 = int(st.get("player1_id") or 0)
    p2 = int(st.get("player2_id") or 0)
    if uid not in (p1, p2):
        return True
    names = st.get("names") or {}
    val = int(getattr(dice, "value", 0) or 0)
    chat_id = int(st["chat_id"])
    lock = lock_for_chat(chat_id, st.get("message_thread_id"))

    if st.get("phase") == "decide_first":
        async with lock:
            st = get_live(sk) or {}
            if not st or st.get("finished"):
                return True
            if st.get("phase") != "decide_first":
                return True
            decide_rolls = dict(st.get("decide_rolls") or {})
            if uid in decide_rolls:
                return True
            st["throw_order_seq"] = int(st.get("throw_order_seq") or 0) + 1
            events = list(st.get("round_events") or [])
            events.append(
                {
                    "phase": "decide_first",
                    "user_id": uid,
                    "throw_order": st["throw_order_seq"],
                    "value": val,
                    "total_after": None,
                }
            )
            st["round_events"] = events
            decide_rolls[uid] = val
            st["decide_rolls"] = decide_rolls
            if not store_live(sk, st):
                return True
        await message.bot.send_message(
            chat_id,
            t("game21_pvp_decide_roll_result", lang).format(
                name=name_link(uid, str(names.get(uid, str(uid)))),
                value=val,
            ),
            parse_mode=ParseMode.HTML,
            **_tw(st),
        )
        other_uid = p2 if uid == p1 else p1
        if other_uid and other_uid not in decide_rolls:
            await message.bot.send_message(
                chat_id,
                t("game21_pvp_decide_prompt_other", lang).format(
                    name=name_link(other_uid, str(names.get(other_uid, str(other_uid))))
                ),
                parse_mode=ParseMode.HTML,
                **_tw(st),
            )
        async with lock:
            st = get_live(sk) or {}
            decide_rolls = dict(st.get("decide_rolls") or {})
            if p1 in decide_rolls and p2 in decide_rolls:
                v1, v2 = int(decide_rolls[p1]), int(decide_rolls[p2])
                if v1 == v2:
                    st["decide_rolls"] = {}
                    if store_live(sk, st):
                        await message.bot.send_message(
                            chat_id, t("game21_pvp_decide_tie", lang), **_tw(st)
                        )
                    return True
                starter = p1 if v1 < v2 else p2
                st["first_turn_uid"] = starter
                st["phase"] = "turn"
                st["current_turn_uid"] = starter
                st["totals"] = {p1: 0, p2: 0}
                st["throws"] = {p1: [], p2: []}
                st["turns_done"] = {p1: False, p2: False}
                st["decide_rolls"] = {}
                if store_live(sk, st):
                    st = get_live(sk) or st
                    await _pvp_update_status_message(message.bot, st)
                    await _pvp_prompt_turn(message.bot, st)
        return True

    if st.get("phase") != "turn":
        return True
    if uid != int(st.get("current_turn_uid") or 0):
        return True

    async with lock:
        st = get_live(sk) or {}
        if not st or st.get("finished") or st.get("phase") != "turn":
            return True
        if uid != int(st.get("current_turn_uid") or 0):
            return True
        st["turn_roll_made"] = True
        stop_mid = st.get("stop_button_message_id")
        stop_uid = st.get("stop_button_uid")
        if stop_mid is not None and stop_uid == uid:
            try:
                await message.bot.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=int(stop_mid),
                    reply_markup=None,
                )
            except Exception:
                pass
            st["stop_button_message_id"] = None
            st["stop_button_uid"] = None
        totals = dict(st.get("totals") or {})
        throws = dict(st.get("throws") or {})
        turns_done = dict(st.get("turns_done") or {})
        totals[uid] = int(totals.get(uid) or 0) + val
        u_throws = list(throws.get(uid) or [])
        u_throws.append(val)
        throws[uid] = u_throws
        st["totals"] = totals
        st["throws"] = throws
        st["throw_order_seq"] = int(st.get("throw_order_seq") or 0) + 1
        events = list(st.get("round_events") or [])
        events.append(
            {
                "phase": "turn",
                "user_id": uid,
                "throw_order": st["throw_order_seq"],
                "value": val,
                "total_after": int(totals[uid]),
            }
        )
        st["round_events"] = events
        if not store_live(sk, st):
            return True
        total = int(totals[uid])
        name_link_s = name_link(uid, str(names.get(uid, str(uid))))
        other_uid = p2 if uid == p1 else p1
        other_total = int(totals.get(other_uid) or 0)
        is_second = bool(turns_done.get(other_uid)) and not bool(turns_done.get(uid))

    if total > 21:
        await message.bot.send_message(
            chat_id,
            t("game21_pvp_player_busted", lang).format(name=name_link_s, total=total),
            parse_mode=ParseMode.HTML,
            **_tw(st),
        )
        loser_id = uid
        wid = p2 if loser_id == p1 else p1
        await finish_pvp_game(bot, session_maker, sk, winner_id=wid)
        return True
    if total == 21:
        await message.bot.send_message(
            chat_id,
            t("game21_pvp_player_blackjack", lang).format(name=name_link_s),
            parse_mode=ParseMode.HTML,
            **_tw(st),
        )
        async with lock:
            st = get_live(sk) or {}
            td = dict(st.get("turns_done") or {})
            td[uid] = True
            st["turns_done"] = td
            store_live(sk, st)
        st = get_live(sk) or st
        await _pvp_update_status_message(message.bot, st)
        if is_second:
            if other_total == 21:
                await finish_pvp_game(bot, session_maker, sk, draw=True)
            else:
                await finish_pvp_game(bot, session_maker, sk, winner_id=uid)
            return True
        await _pvp_after_turn_end(bot, session_maker, st, uid)
        return True
    if total < 16:
        await message.bot.send_message(
            chat_id,
            t("game21_pvp_player_result", lang).format(name=name_link_s, total=total),
            parse_mode=ParseMode.HTML,
            **_tw(st),
        )
        return True
    if is_second:
        if total > other_total:
            await message.bot.send_message(
                chat_id,
                t("game21_pvp_player_result", lang).format(name=name_link_s, total=total),
                parse_mode=ParseMode.HTML,
                **_tw(st),
            )
            async with lock:
                st = get_live(sk) or {}
                td = dict(st.get("turns_done") or {})
                td[uid] = True
                st["turns_done"] = td
                store_live(sk, st)
            await _pvp_after_turn_end(bot, session_maker, st, uid)
            return True
        if total == other_total:
            own = int(st.get("owner_id") or p1)
            stop_msg = await message.bot.send_message(
                chat_id,
                t("game21_pvp_player_can_stop", lang).format(name=name_link_s, total=total),
                parse_mode=ParseMode.HTML,
                reply_markup=pvp_stop_keyboard(lang, own),
                **_tw(st),
            )
            async with lock:
                st = get_live(sk) or {}
                st["stop_button_message_id"] = stop_msg.message_id
                st["stop_button_uid"] = uid
                store_live(sk, st)
            return True
        await message.bot.send_message(
            chat_id,
            t("game21_pvp_player_result", lang).format(name=name_link_s, total=total),
            parse_mode=ParseMode.HTML,
            **_tw(st),
        )
        return True
    own = int(st.get("owner_id") or p1)
    stop_msg = await message.bot.send_message(
        chat_id,
        t("game21_pvp_player_can_stop", lang).format(name=name_link_s, total=total),
        parse_mode=ParseMode.HTML,
        reply_markup=pvp_stop_keyboard(lang, own),
        **_tw(st),
    )
    async with lock:
        st = get_live(sk) or {}
        st["stop_button_message_id"] = stop_msg.message_id
        st["stop_button_uid"] = uid
        store_live(sk, st)
    return True
