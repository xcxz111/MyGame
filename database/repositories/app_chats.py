"""Репозиторий подключённых чатов."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.app_chat import AppChat


async def get_all(session: AsyncSession) -> list[AppChat]:
    result = await session.execute(select(AppChat).order_by(AppChat.id.desc()))
    return list(result.scalars().all())


async def list_for_main_menu(session: AsyncSession) -> list[AppChat]:
    """Подключённые чаты в порядке добавления (для кнопок главного меню)."""
    result = await session.execute(select(AppChat).order_by(AppChat.id.asc()))
    return list(result.scalars().all())


async def get_by_chat_id(session: AsyncSession, chat_id: int) -> AppChat | None:
    result = await session.execute(
        select(AppChat).where(AppChat.chat_id == chat_id).limit(1)
    )
    return result.scalar_one_or_none()


async def add_or_update(
    session: AsyncSession,
    *,
    chat_id: int,
    chat_link: str | None = None,
    button_title_ru: str | None = None,
    button_title_en: str | None = None,
    button_title_uk: str | None = None,
    button_title_pl: str | None = None,
) -> AppChat:
    existing = await get_by_chat_id(session, chat_id)
    if existing is not None:
        if chat_link is not None:
            existing.chat_link = chat_link
        for attr, val in (
            ("button_title_ru", button_title_ru),
            ("button_title_en", button_title_en),
            ("button_title_uk", button_title_uk),
            ("button_title_pl", button_title_pl),
        ):
            if val is not None:
                setattr(existing, attr, val)
        await session.flush()
        return existing
    chat = AppChat(
        chat_id=chat_id,
        chat_link=chat_link,
        button_title_ru=button_title_ru,
        button_title_en=button_title_en,
        button_title_uk=button_title_uk,
        button_title_pl=button_title_pl,
    )
    session.add(chat)
    await session.flush()
    return chat


async def delete(session: AsyncSession, chat_id: int) -> bool:
    chat = await get_by_chat_id(session, chat_id)
    if chat is None:
        return False
    await session.delete(chat)
    await session.flush()
    return True


async def set_game21_users_enabled(
    session: AsyncSession, chat_id: int, *, enabled: bool
) -> bool:
    chat = await get_by_chat_id(session, chat_id)
    if chat is None:
        return False
    chat.game21_users_enabled = 1 if enabled else 0
    await session.flush()
    return True


async def set_checkers_enabled(
    session: AsyncSession, chat_id: int, *, enabled: bool
) -> bool:
    chat = await get_by_chat_id(session, chat_id)
    if chat is None:
        return False
    chat.checkers_enabled = 1 if enabled else 0
    await session.flush()
    return True


async def any_checkers_enabled(session: AsyncSession) -> bool:
    result = await session.execute(
        select(AppChat.id).where(AppChat.checkers_enabled == 1).limit(1)
    )
    return result.scalar_one_or_none() is not None
