"""Telegram-теги уровня пользователя в подключённых чатах."""

from __future__ import annotations

import logging
import time

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

logger = logging.getLogger(__name__)

_tag_cache: dict[tuple[int, int], tuple[int, float]] = {}
_fail_cache: dict[int, float] = {}
_TAG_TTL_SECONDS = 3600
_FAIL_TTL_SECONDS = 600


def level_tag(level: int) -> str:
    return f"level: {int(level)}"


async def ensure_level_tag(bot: Bot, *, chat_id: int, user_id: int, level: int) -> bool:
    """Ставит пользователю тег уровня в группе, с лёгким in-memory throttle."""
    chat_id = int(chat_id)
    user_id = int(user_id)
    level = int(level or 1)
    now = time.time()

    failed_until = _fail_cache.get(chat_id)
    if failed_until is not None and failed_until > now:
        return False

    key = (chat_id, user_id)
    cached = _tag_cache.get(key)
    if cached is not None:
        cached_level, updated_at = cached
        if cached_level == level and now - updated_at < _TAG_TTL_SECONDS:
            return True

    try:
        await bot.set_chat_member_tag(chat_id=chat_id, user_id=user_id, tag=level_tag(level))
    except (TelegramBadRequest, TelegramForbiddenError) as exc:
        # Обычно это значит, что у бота нет can_manage_tags или чат не поддерживает теги.
        logger.info("Failed to set level tag chat=%s user=%s: %s", chat_id, user_id, exc)
        _fail_cache[chat_id] = now + _FAIL_TTL_SECONDS
        return False
    except Exception as exc:
        logger.warning("Failed to set level tag chat=%s user=%s: %s", chat_id, user_id, exc)
        return False

    _tag_cache[key] = (level, now)
    return True
