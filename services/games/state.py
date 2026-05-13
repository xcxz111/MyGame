"""In-memory состояние активной игры в чате (раунды / тай-брейк)."""

from typing import Any

# game_id -> state dict
_round_state: dict[int, dict[str, Any]] = {}

# (chat_id, message_thread_key) -> game_id ; message_thread_key: 0 = без ветки (не форум)
_chat_to_game: dict[tuple[int, int], int] = {}


def play_slot_key(chat_id: int, message_thread_id: int | None) -> tuple[int, int]:
    tid = int(message_thread_id) if message_thread_id is not None else 0
    return (int(chat_id), tid)


def resolve_active_game_id(chat_id: int, message_thread_id: int | None) -> int | None:
    """Активная игра в чате/теме (строгое совпадение message_thread_id)."""
    return _chat_to_game.get(play_slot_key(chat_id, message_thread_id))
