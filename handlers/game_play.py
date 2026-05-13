"""Броски в игровом чате (dice + текстовые эмодзи)."""

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.engine import get_session_maker
from services.game21.pvp_runtime import handle_pvp_group_dice
from services.games.runtime import handle_game_dice_message, handle_game_emoji_text_message
from services.games.state import resolve_active_game_id

router = Router(name="game_play")


def _session_maker() -> async_sessionmaker[AsyncSession]:
    return get_session_maker()


@router.message(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    F.dice,
)
async def on_group_dice(
    message: Message, bot: Bot, session: AsyncSession
) -> None:
    if message.dice and message.dice.emoji == "🎲":
        if await handle_pvp_group_dice(bot, message, _session_maker()):
            return
    if resolve_active_game_id(message.chat.id, message.message_thread_id) is None:
        return
    await handle_game_dice_message(bot, message, session, _session_maker())


@router.message(
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
    F.text,
)
async def on_group_game_emoji_text(
    message: Message, bot: Bot, session: AsyncSession
) -> None:
    if resolve_active_game_id(message.chat.id, message.message_thread_id) is None:
        return
    await handle_game_emoji_text_message(bot, message, session, _session_maker())
