"""Блокирует команды и inline-кнопки в ЛС во время активной партии «21 против бота»."""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import CallbackQuery, Message, TelegramObject

from database.models import User
from locales.texts import get_lang, t
from services.game21 import bot_flow

_ALLOWED_STOP_CALLBACK = "menu:play21bot:stop"


def _private_lang(data: dict[str, Any], event: TelegramObject) -> str:
    user = data.get("user")
    if isinstance(user, User) and user.language_code:
        return user.language_code
    fu = getattr(event, "from_user", None)
    return get_lang(fu.language_code if fu else None)


class ActiveBotGameBlockMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        fu = getattr(event, "from_user", None)
        uid = getattr(fu, "id", None)
        if uid is None or (fu is not None and fu.is_bot):
            return await handler(event, data)

        if not bot_flow.is_in_bot_game(int(uid)):
            return await handler(event, data)

        lang = _private_lang(data, event)

        if isinstance(event, Message):
            if event.chat.type != ChatType.PRIVATE:
                return await handler(event, data)
            dice = event.dice
            if dice and dice.emoji == "🎲":
                return await handler(event, data)
            await event.answer(t("game21_bot_midgame_menu_blocked", lang))
            return None

        if isinstance(event, CallbackQuery):
            msg = event.message
            if msg is None or msg.chat.type != ChatType.PRIVATE:
                return await handler(event, data)
            if event.data == _ALLOWED_STOP_CALLBACK:
                return await handler(event, data)
            await event.answer()
            await msg.answer(t("game21_bot_midgame_menu_blocked", lang))
            return None

        return await handler(event, data)
