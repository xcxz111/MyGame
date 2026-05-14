"""Режим «21 против бота» в ЛС (состояние в памяти). Запись в БД — только `game21_bot_sessions` как в Game_bot."""

from __future__ import annotations

import asyncio
import logging
import random
import time
from decimal import Decimal
from typing import Any

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.engine import get_session_maker
from database.repositories import app_chats as app_chats_repo
from database.repositories import game21_history as g21_hist
from database.repositories import game21_settings as g21_repo
from database.repositories import user_levels as user_levels_repo
from database.repositories import users as users_repo
from locales.texts import get_lang, t
from services.game21.balance import (
    METHOD_BOT_REFUND,
    METHOD_BOT_STAKE,
    METHOD_BOT_WIN,
    add_balance,
    take_balance,
)
from services.game21.formatting import fmt_money

logger = logging.getLogger(__name__)

_user_locks: dict[int, asyncio.Lock] = {}
_bot_state: dict[int, dict[str, Any]] = {}


def _lock(uid: int) -> asyncio.Lock:
    lo = _user_locks.get(uid)
    if lo is None:
        lo = asyncio.Lock()
        _user_locks[uid] = lo
    return lo


def is_in_bot_game(user_id: int) -> bool:
    st = _bot_state.get(int(user_id)) or {}
    if not st:
        return False
    if st.get("finished"):
        return False
    return str(st.get("phase") or "") in {"player", "bot"}


def clear_bot_game(user_id: int) -> None:
    _bot_state.pop(int(user_id), None)


async def _close_game21_bot_session_gb(
    session: AsyncSession, st: dict[str, Any], uid: int, result: str
) -> None:
    """Закрыть строку `game21_bot_sessions` как в Game_bot (`close_21_bot_session`)."""
    sid_raw = st.get("session_id")
    if not sid_raw:
        return
    gb_id = int(sid_raw)
    bet = Decimal(str(st.get("bet") or "0"))
    c = Decimal(str(st.get("commission_percent") or "0"))
    player_total = int(st.get("player_total") or 0)
    bot_total = int(st.get("bot_total") or 0)
    player_throws = st.get("player_throws") or []
    bot_throws = st.get("bot_throws") or []
    gross = bet * 2
    payout = (gross * (Decimal("1") - c / Decimal("100"))).quantize(Decimal("0.01"))
    if result == "win":
        winner = str(uid)
        net_result = (payout - bet).quantize(Decimal("0.01"))
    elif result == "draw":
        winner = "DRAW"
        net_result = Decimal("0")
    else:
        winner = "BOT"
        net_result = -bet
    await g21_hist.close_bot_session_gb(
        session,
        session_id=gb_id,
        result=result,
        winner=winner,
        net_result=net_result,
        round_number=1,
        player_cards=",".join(str(v) for v in player_throws),
        bot_cards=",".join(str(v) for v in bot_throws),
        player_points=player_total,
        bot_points=bot_total,
    )


async def abort_bot_game_session(
    bot: Bot,
    session_maker: async_sessionmaker[AsyncSession],
    user_id: int,
) -> bool:
    """Снимает сессию против бота и возвращает ставку. True, если сессия была активна."""
    uid = int(user_id)
    stop_mid: int | None = None
    gb_sid: int | None = None
    async with _lock(uid):
        st = _bot_state.get(uid)
        if not st or st.get("finished"):
            return False
        if str(st.get("phase") or "") not in {"player", "bot"}:
            return False
        bet = Decimal(str(st.get("bet") or "0"))
        gb_raw = st.get("session_id")
        gb_sid = int(gb_raw) if gb_raw is not None else None
        smid = st.get("stop_mid")
        if smid is not None:
            stop_mid = int(smid)
        clear_bot_game(uid)
    if stop_mid is not None:
        try:
            await bot.edit_message_reply_markup(
                chat_id=uid, message_id=stop_mid, reply_markup=None
            )
        except Exception:
            pass
    async with session_maker() as session:
        if bet > 0:
            await add_balance(session, uid, bet, method=METHOD_BOT_REFUND)
        if gb_sid:
            await g21_hist.cancel_bot_session_gb(session, session_id=gb_sid)
        await session.commit()
    return True


def start_bot_session(
    user_id: int,
    *,
    bet: Decimal,
    commission_percent: Decimal,
    lang: str,
    session_token: int,
    session_id: int | None,
) -> None:
    """`session_id` — id строки `game21_bot_sessions` (как в Game_bot)."""
    _bot_state[int(user_id)] = {
        "phase": "player",
        "bet": bet,
        "commission_percent": commission_percent,
        "lang": lang,
        "player_total": 0,
        "bot_total": 0,
        "player_throws": [],
        "bot_throws": [],
        "finished": False,
        "session_token": session_token,
        "stop_mid": None,
        "throw_seq": 0,
        "session_id": session_id,
    }


def _stop_kb(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("game21_btn_stop", lang), callback_data="menu:play21bot:stop"
                )
            ]
        ]
    )


async def _play21_menu_for(bot: Bot, session: AsyncSession, uid: int, lang: str):
    from keyboards.game21 import play21_menu_keyboard

    u = await users_repo.get_user(session, uid)
    ulang = get_lang(u.language_code if u else None) or lang
    s = await g21_repo.get_settings(session)
    rows = await app_chats_repo.get_all(session)
    any_pvp = any(int(c.game21_users_enabled or 0) for c in rows)
    pvp_btn = bool(any_pvp)
    return play21_menu_keyboard(
        ulang, bot_on=bool(s.enabled_bot), pvp_on=bool(pvp_btn)
    )


async def handle_private_dice(bot: Bot, session: AsyncSession, message) -> bool:
    """Обрабатывает бросок 🎲 в ЛС. Возвращает True, если сообщение обработано."""
    if message.from_user is None or message.from_user.is_bot:
        return False
    uid = int(message.from_user.id)
    async with _lock(uid):
        st = _bot_state.get(uid)
        if not st or st.get("finished") or st.get("phase") != "player":
            return False
        if message.forward_date is not None or getattr(message, "forward_origin", None):
            return True
        dice = message.dice
        if not dice or dice.emoji != "🎲":
            return True
        val = int(dice.value or 0)
        if val < 1 or val > 6:
            return True
        lang = st.get("lang") or "ru"
        st["player_total"] = int(st.get("player_total") or 0) + val
        st["player_throws"] = list(st.get("player_throws") or []) + [val]
        total = int(st["player_total"])
        st["throw_seq"] = int(st.get("throw_seq") or 0) + 1
        if total > 21:
            await message.answer(
                t("game21_player_busted", lang).format(total=total),
                parse_mode=ParseMode.HTML,
            )
            st["finished"] = True
            _bot_state[uid] = st
            bet = Decimal(str(st.get("bet") or "0"))
            kb = await _play21_menu_for(bot, session, uid, lang)
            lose_txt = t("game21_end_bot_lose_bust", lang).format(
                player_total=total,
                bet=fmt_money(bet),
            )
            await message.answer(lose_txt, parse_mode=ParseMode.HTML, reply_markup=kb)
            if st.get("session_id"):
                async with get_session_maker() as s2:
                    await _close_game21_bot_session_gb(s2, st, uid, "lose")
                    await s2.commit()
            clear_bot_game(uid)
            return True
        elif total == 21:
            await message.answer(
                t("game21_player_blackjack", lang),
                parse_mode=ParseMode.HTML,
            )
            st["phase"] = "bot"
            _bot_state[uid] = st
        elif total >= 16:
            prev_mid = st.get("stop_mid")
            if prev_mid:
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=uid, message_id=int(prev_mid), reply_markup=None
                    )
                except Exception:
                    pass
                st["stop_mid"] = None
            reply = await message.answer(
                t("game21_player_can_stop", lang).format(total=total),
                parse_mode=ParseMode.HTML,
                reply_markup=_stop_kb(lang),
            )
            st["stop_mid"] = reply.message_id
            _bot_state[uid] = st
            return True
        else:
            await message.answer(
                t("game21_player_result", lang).format(total=total),
                parse_mode=ParseMode.HTML,
            )
            _bot_state[uid] = st
            return True

    await bot.send_message(uid, t("game21_bot_turn_start", lang))
    await _run_bot_turn(bot, session, uid)
    return True


async def on_stop_callback(bot: Bot, session: AsyncSession, user_id: int, lang: str) -> None:
    uid = int(user_id)
    async with _lock(uid):
        st = _bot_state.get(uid)
        if not st or st.get("finished") or st.get("phase") != "player":
            return
        total = int(st.get("player_total") or 0)
        if total < 16:
            return
        st["phase"] = "bot"
        mid = st.get("stop_mid")
        if mid:
            try:
                await bot.edit_message_reply_markup(chat_id=uid, message_id=int(mid), reply_markup=None)
            except Exception:
                pass
            st["stop_mid"] = None
        _bot_state[uid] = st
    await bot.send_message(uid, t("game21_bot_turn_start", lang))
    await _run_bot_turn(bot, session, uid)


def _dice_value_from_msg(msg: Message) -> int | None:
    dice = msg.dice
    if not dice or dice.emoji != "🎲":
        return None
    raw = dice.value
    if raw is None:
        return None
    v = int(raw)
    if 1 <= v <= 6:
        return v
    return None


async def _roll_bot_dice_value(bot: Bot, uid: int) -> int:
    try:
        msg = await bot.send_dice(uid, emoji="🎲")
    except Exception:
        logger.exception("game21: send_dice failed uid=%s", uid)
        return random.randint(1, 6)
    v = _dice_value_from_msg(msg)
    if v is not None:
        return v
    await asyncio.sleep(4.0)
    v = _dice_value_from_msg(msg)
    if v is not None:
        return v
    return random.randint(1, 6)


async def _run_bot_turn(bot: Bot, session: AsyncSession, uid: int) -> None:
    async with _lock(uid):
        st = _bot_state.get(uid)
        if not st or st.get("finished") or str(st.get("phase") or "") != "bot":
            return
        player_total = int(st.get("player_total") or 0)
        session_token = int(st.get("session_token") or 0)
        lang = str(st.get("lang") or "ru")

    throws: list[int] = []
    bot_total = 0
    while True:
        roll = await _roll_bot_dice_value(bot, uid)
        throws.append(roll)
        bot_total += roll
        await asyncio.sleep(3.5)
        try:
            await bot.send_message(
                uid,
                t("game21_bot_result", lang).format(total=bot_total),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            logger.exception("game21: intermediate bot_result uid=%s", uid)
        if bot_total > 21:
            break
        if bot_total >= player_total:
            break

    async with _lock(uid):
        st = _bot_state.get(uid)
        if not st:
            logger.warning("game21: bot turn end — state missing uid=%s", uid)
            return
        if st.get("finished"):
            logger.warning("game21: bot turn end — already finished uid=%s", uid)
            return
        if int(st.get("session_token") or 0) != session_token:
            logger.warning(
                "game21: bot turn end — session_token mismatch uid=%s expected=%s got=%s",
                uid,
                session_token,
                st.get("session_token"),
            )
            return
        if str(st.get("phase") or "") != "bot":
            logger.warning(
                "game21: bot turn end — wrong phase uid=%s phase=%s",
                uid,
                st.get("phase"),
            )
            return
        st["bot_total"] = bot_total
        st["bot_throws"] = throws
        st["throw_seq"] = int(st.get("throw_seq") or 0) + len(throws)
        _bot_state[uid] = st

    lang = str(st.get("lang") or "ru")
    try:
        if bot_total > 21 or (player_total <= 21 and player_total > bot_total):
            await _finish_bot_win(bot, session, uid, lang, st)
        elif player_total == bot_total:
            await _finish_bot_draw(bot, session, uid, lang, st)
        else:
            await _finish_bot_lose(bot, session, uid, lang, st)
    except Exception:
        logger.exception("game21: finish after bot turn uid=%s", uid)


async def _finish_bot_win(
    bot: Bot, session: AsyncSession, uid: int, lang: str, st: dict[str, Any]
) -> None:
    bet: Decimal = st["bet"]
    c = Decimal(str(st.get("commission_percent") or "0"))
    gross = bet * 2
    payout = (gross * (Decimal("1") - c / Decimal("100"))).quantize(Decimal("0.01"))
    player_total = int(st.get("player_total") or 0)
    bot_total = int(st.get("bot_total") or 0)
    await add_balance(session, uid, payout, method=METHOD_BOT_WIN)
    await user_levels_repo.add_winning_bet_progress(
        session,
        user_id=uid,
        bet_amount=bet,
        source="game:21:bot",
    )
    await _close_game21_bot_session_gb(session, st, uid, "win")
    await session.commit()
    st["finished"] = True
    kb = await _play21_menu_for(bot, session, uid, lang)
    text = t("game21_end_bot_win", lang).format(
        payout=fmt_money(payout),
        bet=fmt_money(bet),
        player_total=player_total,
        bot_total=bot_total,
    )
    await bot.send_message(uid, text, parse_mode=ParseMode.HTML, reply_markup=kb)
    clear_bot_game(uid)


async def _finish_bot_draw(
    bot: Bot, session: AsyncSession, uid: int, lang: str, st: dict[str, Any]
) -> None:
    bet: Decimal = st["bet"]
    player_total = int(st.get("player_total") or 0)
    bot_total = int(st.get("bot_total") or 0)
    await add_balance(session, uid, bet, method=METHOD_BOT_REFUND)
    await _close_game21_bot_session_gb(session, st, uid, "draw")
    await session.commit()
    st["finished"] = True
    kb = await _play21_menu_for(bot, session, uid, lang)
    text = t("game21_end_bot_draw", lang).format(
        bet=fmt_money(bet),
        player_total=player_total,
        bot_total=bot_total,
    )
    await bot.send_message(uid, text, parse_mode=ParseMode.HTML, reply_markup=kb)
    clear_bot_game(uid)


async def _finish_bot_lose(
    bot: Bot, session: AsyncSession, uid: int, lang: str, st: dict[str, Any]
) -> None:
    st["finished"] = True
    bet = Decimal(str(st.get("bet") or "0"))
    player_total = int(st.get("player_total") or 0)
    bot_total = int(st.get("bot_total") or 0)
    if st.get("session_id"):
        async with get_session_maker() as s2:
            await users_repo.award_referral_percent(
                s2,
                referral_id=uid,
                base_amount=bet,
                source="game:21:bot",
            )
            await _close_game21_bot_session_gb(s2, st, uid, "lose")
            await s2.commit()
    kb = await _play21_menu_for(bot, session, uid, lang)
    text = t("game21_end_bot_lose", lang).format(
        bet=fmt_money(bet),
        player_total=player_total,
        bot_total=bot_total,
    )
    await bot.send_message(uid, text, parse_mode=ParseMode.HTML, reply_markup=kb)
    clear_bot_game(uid)


async def charge_and_start(
    bot: Bot,
    session_maker: async_sessionmaker[AsyncSession],
    user_id: int,
    bet: Decimal,
    commission_percent: Decimal,
    lang: str,
) -> tuple[bool, str | None]:
    uid = int(user_id)
    async with _lock(uid):
        ex = _bot_state.get(uid)
        if ex and not ex.get("finished"):
            ph = str(ex.get("phase") or "")
            if ph in {"player", "bot"}:
                return False, "game21_active_notice"
        async with session_maker() as session:
            ok = await take_balance(session, uid, bet, method=METHOD_BOT_STAKE)
            if not ok:
                return False, "game21_not_enough_balance"
            tok = time.time_ns()
            gb_id = await g21_hist.create_bot_session_gb(
                session,
                user_id=uid,
                bet_amount=bet,
                commission_percent=commission_percent,
            )
            await session.commit()
        start_bot_session(
            uid,
            bet=bet,
            commission_percent=commission_percent,
            lang=lang,
            session_token=tok,
            session_id=gb_id,
        )
    await bot.send_message(uid, t("game21_throw_now", lang))
    return True, None
