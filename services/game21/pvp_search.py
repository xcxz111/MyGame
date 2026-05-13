"""Таймаут поиска соперника PvP 21, открепление/удаление объявлений."""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal

from aiogram import Bot

from database import get_session_maker
from database.repositories import users as users_repo
from locales.texts import get_lang, t
from services.game21.balance import METHOD_PVP_REFUND, add_balance
from services.game21.formatting import fmt_money
from services.game21.pvp_state import get_search, lock_for_chat, pop_search
from services.games.forum_thread import thread_kw, unpin_chat_message_in_forum

logger = logging.getLogger(__name__)


async def cancel_owner_pvp_search_now(bot: Bot, owner_user_id: int) -> bool:
    """Снимает объявление о поиске и возвращает ставку владельцу. Без уведомления «таймаут»."""
    uid = int(owner_user_id)
    req0 = get_search(uid) or {}
    if not req0:
        return False
    chat_id = int(req0.get("chat_id") or 0)
    thread_id = req0.get("message_thread_id")
    if thread_id is not None:
        thread_id = int(thread_id)
    else:
        thread_id = None
    lock = lock_for_chat(chat_id, thread_id)
    async with lock:
        req = get_search(uid) or {}
        if not req:
            return False
        if req.get("accepted_by"):
            return False
        amount = Decimal(str(req.get("bet_amount") or "0"))
        lang = req.get("lang") or "ru"
        mid_topic = req.get("message_id")
        mid_gen = req.get("message_id_general")
        pop_search(uid)

    sm = get_session_maker()
    async with sm() as session:
        await add_balance(session, uid, amount, method=METHOD_PVP_REFUND)
        await session.commit()

    for mid, tid in ((mid_topic, thread_id), (mid_gen, None)):
        if mid is None:
            continue
        try:
            await unpin_chat_message_in_forum(
                bot,
                chat_id=chat_id,
                message_id=int(mid),
                message_thread_id=tid,
            )
        except Exception as exc:
            logger.debug("pvp search cancel unpin: %s", exc)
        try:
            await bot.delete_message(chat_id=chat_id, message_id=int(mid))
        except Exception as exc:
            logger.debug("pvp search cancel delete: %s", exc)
    return True


async def arm_search_timeout(bot: Bot, owner_user_id: int, token: int) -> None:
    await asyncio.sleep(300)
    req0 = get_search(owner_user_id) or {}
    if not req0:
        return
    chat_id = int(req0.get("chat_id") or 0)
    thread_id = req0.get("message_thread_id")
    if thread_id is not None:
        thread_id = int(thread_id)
    else:
        thread_id = None
    lock = lock_for_chat(chat_id, thread_id)
    async with lock:
        req = get_search(owner_user_id) or {}
        if not req:
            return
        if req.get("accepted_by"):
            return
        if int(req.get("search_timeout_token") or 0) != int(token):
            return
        amount = Decimal(str(req.get("bet_amount") or "0"))
        lang = req.get("lang") or "ru"
        mid_topic = req.get("message_id")
        mid_gen = req.get("message_id_general")
        pop_search(owner_user_id)

    sm = get_session_maker()
    async with sm() as session:
        u = await users_repo.get_user(session, owner_user_id)
        await add_balance(session, owner_user_id, amount, method=METHOD_PVP_REFUND)
        await session.commit()
    lang_dm = get_lang(u.language_code if u else None) or lang

    for mid, tid in ((mid_topic, thread_id), (mid_gen, None)):
        if mid is None:
            continue
        try:
            await unpin_chat_message_in_forum(
                bot,
                chat_id=chat_id,
                message_id=int(mid),
                message_thread_id=tid,
            )
        except Exception as exc:
            logger.debug("pvp search timeout unpin: %s", exc)
        try:
            await bot.delete_message(chat_id=chat_id, message_id=int(mid))
        except Exception as exc:
            logger.debug("pvp search timeout delete: %s", exc)

    try:
        await bot.send_message(
            owner_user_id,
            t("game21_pvp_search_not_accepted", lang_dm).format(amount=fmt_money(amount)),
        )
    except Exception as exc:
        logger.debug("pvp timeout dm: %s", exc)
