"""Состояние PvP «21» в памяти (слот = чат + ветка форума)."""

from __future__ import annotations

import asyncio
from typing import Any

from services.games.state import resolve_active_game_id

# owner_user_id -> meta поиска соперника
_pvp_search: dict[int, dict[str, Any]] = {}
# (chat_id, thread_key) -> live state ; thread_key 0 = без темы
_pvp_live: dict[tuple[int, int], dict[str, Any]] = {}
_locks: dict[tuple[int, int], asyncio.Lock] = {}
# Сериализация денежных операций и «одна активность 21 на пользователя» между разными чатами
_user_game21_locks: dict[int, asyncio.Lock] = {}


def slot_key(chat_id: int, message_thread_id: int | None) -> tuple[int, int]:
    tid = int(message_thread_id) if message_thread_id is not None else 0
    return (int(chat_id), tid)


def _lock(sk: tuple[int, int]) -> asyncio.Lock:
    lo = _locks.get(sk)
    if lo is None:
        lo = asyncio.Lock()
        _locks[sk] = lo
    return lo


def is_slot_busy(chat_id: int, message_thread_id: int | None) -> bool:
    sk = slot_key(chat_id, message_thread_id)
    st = _pvp_live.get(sk)
    if st and not st.get("finished"):
        return True
    for s in _pvp_search.values():
        if int(s.get("chat_id") or 0) == sk[0] and int(s.get("message_thread_id") or 0) == sk[1]:
            return True
    if resolve_active_game_id(sk[0], message_thread_id if sk[1] else None):
        return True
    return False


def store_search(owner_id: int, meta: dict[str, Any]) -> None:
    _pvp_search[owner_id] = meta


def pop_search(owner_id: int) -> dict[str, Any] | None:
    return _pvp_search.pop(owner_id, None)


def get_search(owner_id: int) -> dict[str, Any] | None:
    return _pvp_search.get(owner_id)


def session_token(st: dict[str, Any] | None) -> int:
    return int((st or {}).get("pvp_session_token") or 0)


def store_live(sk: tuple[int, int], st: dict[str, Any]) -> bool:
    """Как `_pvp_store_live_state` в Game_bot: не перезаписываем завершённую партию и не подменяем чужой токен."""
    cur_raw = _pvp_live.get(sk)
    if cur_raw is not None and bool(cur_raw.get("finished")):
        return False
    cur = cur_raw or {}
    t_new = session_token(st)
    t_old = session_token(cur)
    if cur and t_new and t_old and t_new != t_old:
        return False
    _pvp_live[sk] = st
    return True


def get_live(sk: tuple[int, int]) -> dict[str, Any] | None:
    return _pvp_live.get(sk)


def live_slot_for_participant(user_id: int) -> tuple[tuple[int, int], dict[str, Any]] | None:
    """Слот живой партии, где участвует пользователь (p1 или p2)."""
    uid = int(user_id)
    for sk, st in list(_pvp_live.items()):
        if st.get("finished"):
            continue
        p1 = int(st.get("player1_id") or 0)
        p2 = int(st.get("player2_id") or 0)
        if uid in (p1, p2):
            return sk, st
    return None


def pop_live(sk: tuple[int, int]) -> None:
    _pvp_live.pop(sk, None)


def lock_for_chat(chat_id: int, message_thread_id: int | None) -> asyncio.Lock:
    return _lock(slot_key(chat_id, message_thread_id))


def user_game21_lock(user_id: int) -> asyncio.Lock:
    """Глобально на user_id: не параллелить списание ставки в двух чатах и гонки accept/поиск."""
    uid = int(user_id)
    lo = _user_game21_locks.get(uid)
    if lo is None:
        lo = asyncio.Lock()
        _user_game21_locks[uid] = lo
    return lo
