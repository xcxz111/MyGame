"""Временное хранение языка пользователя (позже — MySQL)."""

from __future__ import annotations

from typing import Optional

_user_id_to_lang: dict[int, str] = {}


def get_stored_language(user_id: int) -> Optional[str]:
    return _user_id_to_lang.get(user_id)


def set_stored_language(user_id: int, lang: str) -> None:
    _user_id_to_lang[user_id] = lang
