"""Фоновый цикл: напоминание за 5 минут и старт игр по расписанию."""

import asyncio
import logging

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from services.games.runtime import process_due_games, send_5min_reminders

logger = logging.getLogger(__name__)


async def run_games_background_loop(
    bot: Bot, session_maker: async_sessionmaker[AsyncSession]
) -> None:
    first = True
    while True:
        try:
            await send_5min_reminders(bot, session_maker)
            if not first:
                await process_due_games(bot, session_maker)
            first = False
        except Exception:
            logger.exception("games_background_loop tick failed")
        await asyncio.sleep(60)
