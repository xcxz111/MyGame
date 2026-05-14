"""Общие проверки занятости игроков и игровых слотов."""

from __future__ import annotations


def user_in_any_interactive_game(user_id: int) -> bool:
    from services.checkers.state import user_in_checkers
    from services.game21.active import user_in_any_game21
    from services.kmb.state import user_in_kmb

    return user_in_checkers(user_id) or user_in_any_game21(user_id) or user_in_kmb(user_id)


def active_interactive_chat_id_for_user(user_id: int) -> int | None:
    from services.checkers.state import active_chat_id_for_user as checkers_chat_id
    from services.game21.active import pvp_busy_chat_id_for_user
    from services.kmb.state import active_chat_id_for_user as kmb_chat_id

    return pvp_busy_chat_id_for_user(user_id) or checkers_chat_id(user_id) or kmb_chat_id(user_id)


def slot_busy_for_new_game(chat_id: int, message_thread_id: int | None) -> bool:
    from services.checkers.state import is_slot_busy as checkers_slot_busy
    from services.game21.pvp_state import is_slot_busy as game21_slot_busy
    from services.kmb.state import is_slot_busy as kmb_slot_busy

    return game21_slot_busy(chat_id, message_thread_id) or checkers_slot_busy(
        chat_id, message_thread_id
    ) or kmb_slot_busy(chat_id, message_thread_id)


def slot_busy_outside_game21(chat_id: int, message_thread_id: int | None) -> bool:
    from services.checkers.state import is_slot_busy as checkers_slot_busy
    from services.kmb.state import is_slot_busy as kmb_slot_busy

    return checkers_slot_busy(chat_id, message_thread_id) or kmb_slot_busy(
        chat_id, message_thread_id
    )


def slot_busy_outside_checkers(chat_id: int, message_thread_id: int | None) -> bool:
    from services.game21.pvp_state import is_slot_busy as game21_slot_busy
    from services.kmb.state import is_slot_busy as kmb_slot_busy

    return game21_slot_busy(chat_id, message_thread_id) or kmb_slot_busy(
        chat_id, message_thread_id
    )


def slot_busy_outside_kmb(chat_id: int, message_thread_id: int | None) -> bool:
    from services.checkers.state import is_slot_busy as checkers_slot_busy
    from services.game21.pvp_state import is_slot_busy as game21_slot_busy

    return game21_slot_busy(chat_id, message_thread_id) or checkers_slot_busy(
        chat_id, message_thread_id
    )
