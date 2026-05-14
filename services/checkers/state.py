"""In-memory состояние поиска и живых партий шашек."""

from __future__ import annotations

import asyncio
from typing import Any

from services.games.state import resolve_active_game_id

_search: dict[int, dict[str, Any]] = {}
_live: dict[tuple[int, int], dict[str, Any]] = {}
_locks: dict[tuple[int, int], asyncio.Lock] = {}
_user_locks: dict[int, asyncio.Lock] = {}


def slot_key(chat_id: int, message_thread_id: int | None) -> tuple[int, int]:
    return int(chat_id), int(message_thread_id) if message_thread_id is not None else 0


def lock_for_chat(chat_id: int, message_thread_id: int | None) -> asyncio.Lock:
    sk = slot_key(chat_id, message_thread_id)
    lock = _locks.get(sk)
    if lock is None:
        lock = asyncio.Lock()
        _locks[sk] = lock
    return lock


def user_lock(user_id: int) -> asyncio.Lock:
    uid = int(user_id)
    lock = _user_locks.get(uid)
    if lock is None:
        lock = asyncio.Lock()
        _user_locks[uid] = lock
    return lock


def is_slot_busy(chat_id: int, message_thread_id: int | None) -> bool:
    sk = slot_key(chat_id, message_thread_id)
    live = _live.get(sk)
    if live and not live.get("finished"):
        return True
    for meta in _search.values():
        if slot_key(int(meta.get("chat_id") or 0), meta.get("message_thread_id")) == sk:
            return True
    return bool(resolve_active_game_id(sk[0], message_thread_id))


def user_in_checkers(user_id: int) -> bool:
    uid = int(user_id)
    if uid in _search:
        return True
    for st in _live.values():
        if st.get("finished"):
            continue
        if uid in (int(st.get("player1_id") or 0), int(st.get("player2_id") or 0)):
            return True
    return False


def active_chat_id_for_user(user_id: int) -> int | None:
    uid = int(user_id)
    meta = _search.get(uid)
    if meta:
        cid = int(meta.get("chat_id") or 0)
        return cid if cid else None
    for sk, st in _live.items():
        if st.get("finished"):
            continue
        if uid in (int(st.get("player1_id") or 0), int(st.get("player2_id") or 0)):
            return int(sk[0])
    return None


def store_search(owner_id: int, meta: dict[str, Any]) -> None:
    _search[int(owner_id)] = meta


def get_search(owner_id: int) -> dict[str, Any] | None:
    return _search.get(int(owner_id))


def pop_search(owner_id: int) -> dict[str, Any] | None:
    return _search.pop(int(owner_id), None)


def store_live(sk: tuple[int, int], state: dict[str, Any]) -> None:
    _live[sk] = state


def get_live(sk: tuple[int, int]) -> dict[str, Any] | None:
    return _live.get(sk)


def pop_live(sk: tuple[int, int]) -> None:
    _live.pop(sk, None)
