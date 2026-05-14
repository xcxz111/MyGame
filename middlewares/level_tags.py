"""Ставит Telegram-тег уровня на любом сообщении в подключённом чате."""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatType
from aiogram.types import Message, TelegramObject

from database.models import User
from database.repositories import app_chats as app_chats_repo
from services.user_levels import ensure_level_tag


class LevelTagMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.chat.type in {
            ChatType.GROUP,
            ChatType.SUPERGROUP,
        }:
            session = data.get("session")
            user = data.get("user")
            bot = data.get("bot")
            if (
                session is not None
                and isinstance(user, User)
                and isinstance(bot, Bot)
                and event.chat is not None
                and event.from_user is not None
                and not event.from_user.is_bot
                and await app_chats_repo.get_by_chat_id(session, int(event.chat.id))
                is not None
            ):
                await ensure_level_tag(
                    bot,
                    chat_id=int(event.chat.id),
                    user_id=int(user.user_id),
                    level=int(user.level or 0),
                )
        return await handler(event, data)
