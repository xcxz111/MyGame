"""Открывает async-сессию SQLAlchemy на каждый апдейт и пробрасывает её в хендлер.

После успешного выполнения хендлера транзакция коммитится.
Если хендлер кинул исключение — сессия закроется без коммита (rollback).
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker: async_sessionmaker[AsyncSession]) -> None:
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_maker() as session:
            data["session"] = session
            result = await handler(event, data)
            await session.commit()
            return result
