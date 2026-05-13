"""Синхронизация названий тем форума из сервисных сообщений (Bot API не отдаёт список тем)."""

import logging

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import app_chats as app_chats_repo
from database.repositories import forum_topics as forum_topics_repo

logger = logging.getLogger(__name__)
router = Router(name="forum_topic_sync")


@router.message(F.chat.type == ChatType.SUPERGROUP, F.forum_topic_created)
async def on_forum_topic_created(message: Message, session: AsyncSession) -> None:
    if message.chat is None:
        return
    chat_id = int(message.chat.id)
    if message.message_thread_id is None:
        if message.forum_topic_created:
            logger.warning(
                "forum_topic_created without message_thread_id chat_id=%s",
                chat_id,
            )
        return
    if await app_chats_repo.get_by_chat_id(session, chat_id) is None:
        return
    name = message.forum_topic_created.name if message.forum_topic_created else None
    try:
        await forum_topics_repo.upsert(
            session,
            chat_id=chat_id,
            message_thread_id=int(message.message_thread_id),
            name=name,
        )
        await session.commit()
    except Exception as exc:
        logger.warning("forum_topic_created sync chat=%s: %s", chat_id, exc)


@router.message(F.chat.type == ChatType.SUPERGROUP, F.forum_topic_edited)
async def on_forum_topic_edited(message: Message, session: AsyncSession) -> None:
    if message.chat is None:
        return
    chat_id = int(message.chat.id)
    if message.message_thread_id is None:
        if message.forum_topic_edited:
            logger.warning(
                "forum_topic_edited without message_thread_id chat_id=%s",
                chat_id,
            )
        return
    if await app_chats_repo.get_by_chat_id(session, chat_id) is None:
        return
    edited = message.forum_topic_edited
    name = edited.name if edited else None
    try:
        await forum_topics_repo.upsert(
            session,
            chat_id=chat_id,
            message_thread_id=int(message.message_thread_id),
            name=name,
        )
        await session.commit()
    except Exception as exc:
        logger.warning("forum_topic_edited sync chat=%s: %s", chat_id, exc)


@router.message(
    F.chat.type == ChatType.SUPERGROUP,
    F.message_thread_id,
    ~F.forum_topic_created,
    ~F.forum_topic_edited,
    ~F.dice,
)
async def on_forum_topic_learn_from_message(
    message: Message, session: AsyncSession
) -> None:
    """Запоминаем message_thread_id из любых сообщений в ветке (бэкап без forum_topic_created)."""
    if message.chat is None or message.message_thread_id is None:
        return
    chat_id = int(message.chat.id)
    if await app_chats_repo.get_by_chat_id(session, chat_id) is None:
        return
    try:
        await forum_topics_repo.ensure_thread_stub(
            session,
            chat_id=chat_id,
            message_thread_id=int(message.message_thread_id),
        )
    except Exception as exc:
        logger.warning("forum_topic learn-from-message chat=%s: %s", chat_id, exc)
