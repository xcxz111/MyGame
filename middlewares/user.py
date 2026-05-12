"""Создаёт/обновляет запись пользователя на каждый апдейт и кладёт её в data['user']."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.repositories import users as users_repo


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        session = data.get("session")
        tg_user = getattr(event, "from_user", None)
        if session is None or tg_user is None or tg_user.is_bot:
            return await handler(event, data)

        full_name = " ".join(
            part for part in (tg_user.first_name, tg_user.last_name) if part
        ).strip() or None

        user = await users_repo.upsert_user(
            session,
            user_id=tg_user.id,
            user_name=tg_user.username,
            name=full_name,
        )
        data["user"] = user
        return await handler(event, data)
