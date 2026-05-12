"""Репозиторий для таблицы `users`.

Подключим к хендлерам на следующем шаге.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User, UserRole, UserStatus


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def upsert_user(
    session: AsyncSession,
    *,
    user_id: int,
    user_name: str | None = None,
    name: str | None = None,
    language_code: str | None = None,
) -> User:
    """Создаёт пользователя, если его нет; иначе обновляет переданные поля."""
    user = await session.get(User, user_id)
    if user is None:
        user = User(
            user_id=user_id,
            user_name=user_name,
            name=name,
            language_code=language_code,
            status=UserStatus.ACTIVE,
            role=UserRole.USER,
        )
        session.add(user)
    else:
        if user_name is not None:
            user.user_name = user_name
        if name is not None:
            user.name = name
        if language_code is not None:
            user.language_code = language_code
    await session.flush()
    return user


async def set_language(session: AsyncSession, user_id: int, language_code: str) -> None:
    user = await session.get(User, user_id)
    if user is not None:
        user.language_code = language_code
        await session.flush()


async def set_status(session: AsyncSession, user_id: int, status: int) -> None:
    user = await session.get(User, user_id)
    if user is not None:
        user.status = status
        await session.flush()


async def set_role(session: AsyncSession, user_id: int, role: str) -> None:
    user = await session.get(User, user_id)
    if user is not None:
        user.role = role
        await session.flush()
