"""Репозиторий тем форума (синхронизация из апдейтов)."""

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.forum_topic import ForumTopic


async def list_for_chat(session: AsyncSession, chat_id: int) -> list[ForumTopic]:
    result = await session.execute(
        select(ForumTopic)
        .where(ForumTopic.chat_id == chat_id)
        .order_by(ForumTopic.name.asc())
    )
    return list(result.scalars().all())


async def ensure_thread_stub(
    session: AsyncSession,
    *,
    chat_id: int,
    message_thread_id: int,
) -> ForumTopic:
    """Создать строку о ветке, если её ещё нет (темы, созданные до бота, не дают forum_topic_created)."""
    r = await session.execute(
        select(ForumTopic)
        .where(
            ForumTopic.chat_id == chat_id,
            ForumTopic.message_thread_id == message_thread_id,
        )
        .limit(1)
    )
    row = r.scalar_one_or_none()
    if row is not None:
        return row
    label = f"#{message_thread_id}"
    ins = mysql_insert(ForumTopic).values(
        chat_id=chat_id,
        message_thread_id=message_thread_id,
        name=label,
    )
    stmt = ins.on_duplicate_key_update(chat_id=ins.inserted.chat_id)
    await session.execute(stmt)
    await session.flush()
    r2 = await session.execute(
        select(ForumTopic)
        .where(
            ForumTopic.chat_id == chat_id,
            ForumTopic.message_thread_id == message_thread_id,
        )
        .limit(1)
    )
    return r2.scalar_one()


async def upsert(
    session: AsyncSession,
    *,
    chat_id: int,
    message_thread_id: int,
    name: str | None,
) -> ForumTopic:
    label = (name or "").strip() or f"#{message_thread_id}"
    r = await session.execute(
        select(ForumTopic)
        .where(
            ForumTopic.chat_id == chat_id,
            ForumTopic.message_thread_id == message_thread_id,
        )
        .limit(1)
    )
    row = r.scalar_one_or_none()
    if row is not None:
        row.name = label
    else:
        row = ForumTopic(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            name=label,
        )
        session.add(row)
    await session.flush()
    return row
