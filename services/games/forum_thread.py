"""Вспомогательные вызовы API с message_thread_id (часть методов в aiogram без поля в обёртке Bot)."""

from __future__ import annotations

import re
from typing import Any

from aiogram import Bot
from aiogram.methods import EditMessageText, PinChatMessage, UnpinChatMessage
from pydantic import Field

from locales.texts import t

_STUB_TOPIC_DB_NAME = re.compile(r"^#(\d+)$")


def format_forum_topic_display_label(
    lang: str, *, message_thread_id: int, name: str | None
) -> str:
    """Человекочитаемая подпись ветки: плейсхолдер «#id» из БД заменяем на локализованный текст."""
    raw = (name or "").strip()
    m = _STUB_TOPIC_DB_NAME.fullmatch(raw)
    if m and int(m.group(1)) == message_thread_id:
        return t("admin_game_forum_thread_placeholder", lang).format(
            id=message_thread_id
        )
    return raw or str(message_thread_id)


class PinChatMessageInForum(PinChatMessage):
    message_thread_id: int | None = Field(default=None)


class EditMessageTextInForum(EditMessageText):
    message_thread_id: int | None = Field(default=None)


class UnpinChatMessageInForum(UnpinChatMessage):
    message_thread_id: int | None = Field(default=None)


def thread_kw(message_thread_id: int | None) -> dict[str, Any]:
    if message_thread_id is None:
        return {}
    return {"message_thread_id": int(message_thread_id)}


async def pin_chat_message_in_forum(
    bot: Bot,
    *,
    chat_id: int,
    message_id: int,
    message_thread_id: int | None,
    disable_notification: bool | None = None,
) -> bool:
    if message_thread_id is None:
        return await bot.pin_chat_message(
            chat_id, message_id, disable_notification=disable_notification
        )
    return await bot(
        PinChatMessageInForum(
            chat_id=chat_id,
            message_id=message_id,
            message_thread_id=message_thread_id,
            disable_notification=disable_notification,
        )
    )


async def unpin_chat_message_in_forum(
    bot: Bot,
    *,
    chat_id: int,
    message_id: int,
    message_thread_id: int | None,
) -> bool:
    if message_thread_id is None:
        return await bot.unpin_chat_message(chat_id=chat_id, message_id=message_id)
    return await bot(
        UnpinChatMessageInForum(
            chat_id=chat_id,
            message_id=message_id,
            message_thread_id=message_thread_id,
        )
    )


async def edit_message_text_in_forum(
    bot: Bot,
    *,
    chat_id: int,
    message_id: int,
    text: str,
    message_thread_id: int | None,
    parse_mode: str | None = None,
    reply_markup: Any = None,
) -> Any:
    base_kw: dict[str, Any] = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "reply_markup": reply_markup,
    }
    if parse_mode is not None:
        base_kw["parse_mode"] = parse_mode
    if message_thread_id is None:
        return await bot.edit_message_text(**base_kw)
    return await bot(EditMessageTextInForum(message_thread_id=message_thread_id, **base_kw))
