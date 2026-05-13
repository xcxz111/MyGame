"""Фильтрация списка тем по whitelist из `app_chat_allowed_topics`."""

from __future__ import annotations


def filter_topic_rows(
    rows: list[tuple[int, str]],
    allowed: frozenset[int | None] | None,
) -> list[tuple[int, str]]:
    if allowed is None:
        return list(rows)
    return [(tid, name) for tid, name in rows if tid in allowed]


def general_play_allowed(allowed: frozenset[int | None] | None) -> bool:
    if allowed is None:
        return True
    return None in allowed


def forum_topic_choice_possible(
    *,
    is_forum: bool,
    filtered_topics: list[tuple[int, str]],
    general_ok: bool,
) -> bool:
    if not is_forum:
        return False
    return bool(filtered_topics) or general_ok
