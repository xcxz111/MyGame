"""Whitelist тем форума для подключённого чата."""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.app_chat_allowed_topic import (
    GENERAL_THREAD_DB,
    AppChatAllowedTopic,
)
from database.repositories import app_chats as app_chats_repo


def public_thread_to_db(message_thread_id: int | None) -> int:
    return GENERAL_THREAD_DB if message_thread_id is None else int(message_thread_id)


def db_thread_to_public(db_value: int) -> int | None:
    return None if int(db_value) == GENERAL_THREAD_DB else int(db_value)


async def count_for_app_chat(session: AsyncSession, app_chat_id: int) -> int:
    r = await session.execute(
        select(func.count())
        .select_from(AppChatAllowedTopic)
        .where(AppChatAllowedTopic.app_chat_id == app_chat_id)
    )
    return int(r.scalar_one() or 0)


async def whitelist_active(session: AsyncSession, app_chat_id: int) -> bool:
    return await count_for_app_chat(session, app_chat_id) > 0


async def list_allowed_db_threads(session: AsyncSession, app_chat_id: int) -> set[int]:
    r = await session.execute(
        select(AppChatAllowedTopic.message_thread_id).where(
            AppChatAllowedTopic.app_chat_id == app_chat_id
        )
    )
    return {int(row[0]) for row in r.all()}


async def effective_allowed_public_threads(
    session: AsyncSession, telegram_chat_id: int
) -> frozenset[int | None] | None:
    """None — ограничений нет (все темы и общий чат). Иначе множество разрешённых (None = общий)."""
    ac = await app_chats_repo.get_by_chat_id(session, telegram_chat_id)
    if ac is None:
        return frozenset()
    if not await whitelist_active(session, ac.id):
        return None
    raw = await list_allowed_db_threads(session, ac.id)
    return frozenset(db_thread_to_public(x) for x in raw)


async def is_allowed_public(
    session: AsyncSession,
    telegram_chat_id: int,
    message_thread_id: int | None,
) -> bool:
    eff = await effective_allowed_public_threads(session, telegram_chat_id)
    if eff is None:
        return True
    return message_thread_id in eff


async def toggle(
    session: AsyncSession, app_chat_id: int, *, message_thread_id: int | None
) -> bool:
    """Переключает разрешение. Возвращает True, если тема теперь в whitelist."""
    db_tid = public_thread_to_db(message_thread_id)
    existing = await session.execute(
        select(AppChatAllowedTopic.id).where(
            AppChatAllowedTopic.app_chat_id == app_chat_id,
            AppChatAllowedTopic.message_thread_id == db_tid,
        )
    )
    row_id = existing.scalar_one_or_none()
    if row_id is not None:
        await session.execute(
            delete(AppChatAllowedTopic).where(AppChatAllowedTopic.id == row_id)
        )
        await session.flush()
        return False
    session.add(
        AppChatAllowedTopic(
            app_chat_id=app_chat_id,
            message_thread_id=db_tid,
        )
    )
    await session.flush()
    return True


async def clear_whitelist(session: AsyncSession, app_chat_id: int) -> None:
    await session.execute(
        delete(AppChatAllowedTopic).where(
            AppChatAllowedTopic.app_chat_id == app_chat_id
        )
    )
    await session.flush()


async def replace_with_full_seed(
    session: AsyncSession, app_chat_id: int, telegram_chat_id: int
) -> None:
    """Включает whitelist: все известные темы этого чата + общий чат (дальше админ снимает лишнее)."""
    from database.repositories import forum_topics as forum_topics_repo

    await clear_whitelist(session, app_chat_id)
    session.add(
        AppChatAllowedTopic(
            app_chat_id=app_chat_id,
            message_thread_id=GENERAL_THREAD_DB,
        )
    )
    topics = await forum_topics_repo.list_for_chat(session, telegram_chat_id)
    for top in topics:
        session.add(
            AppChatAllowedTopic(
                app_chat_id=app_chat_id,
                message_thread_id=int(top.message_thread_id),
            )
        )
    await session.flush()
