"""Проверка «пользователь уже в игре 21» (PvP или против бота)."""

from __future__ import annotations

from services.game21 import bot_flow
from services.game21.pvp_state import get_live, get_search, live_slot_for_participant, slot_key


def _all_search_items():
    from services.game21 import pvp_state

    return list(pvp_state._pvp_search.items())  # noqa: SLF001


def _all_live_items():
    from services.game21 import pvp_state

    return list(pvp_state._pvp_live.items())  # noqa: SLF001


def user_busy_in_pvp(user_id: int) -> bool:
    uid = int(user_id)
    if get_search(uid):
        return True
    for _, st in _all_live_items():
        if st.get("finished"):
            continue
        if uid in (int(st.get("player1_id") or 0), int(st.get("player2_id") or 0)):
            return True
    return False


def pvp_busy_chat_id_for_user(user_id: int) -> int | None:
    """Чат группы, где у пользователя поиск или живая партия PvP (если есть)."""
    uid = int(user_id)
    meta = get_search(uid)
    if meta:
        cid = int(meta.get("chat_id") or 0)
        return cid if cid else None
    live = live_slot_for_participant(uid)
    if live:
        sk, _st = live
        cid = int(sk[0] or 0)
        return cid if cid else None
    return None


def user_in_any_game21(user_id: int) -> bool:
    if bot_flow.is_in_bot_game(user_id):
        return True
    return user_busy_in_pvp(user_id)


async def cancel_all_in_memory_21_for_user(bot, session_maker, user_id: int) -> None:
    """Завершает все активные сессии 21 пользователя: PvP-партия (ничья), поиск, игра с ботом."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from services.game21 import bot_flow
    from services.game21.pvp_runtime import finish_pvp_game
    from services.game21.pvp_search import cancel_owner_pvp_search_now
    from services.game21.pvp_state import live_slot_for_participant

    sm: async_sessionmaker[AsyncSession] = session_maker
    uid = int(user_id)
    live = live_slot_for_participant(uid)
    if live:
        sk, _st = live
        await finish_pvp_game(bot, sm, sk, draw=True)
    await cancel_owner_pvp_search_now(bot, uid)
    await bot_flow.abort_bot_game_session(bot, sm, uid)


def slot_has_live_or_search(chat_id: int, message_thread_id: int | None) -> bool:
    sk = slot_key(chat_id, message_thread_id)
    st = get_live(sk)
    if st and not st.get("finished"):
        return True
    for _, meta in _all_search_items():
        if int(meta.get("chat_id") or 0) != sk[0]:
            continue
        mtid = meta.get("message_thread_id")
        tid = int(mtid) if mtid is not None else 0
        if tid == sk[1]:
            return True
    return False
