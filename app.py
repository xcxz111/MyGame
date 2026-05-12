import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database.engine import get_session_maker
from database.init_db import init_db
from handlers import setup_routers
from middlewares import DbSessionMiddleware, UserMiddleware
from settings import get_settings

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)

    settings = get_settings()

    logger.info("Initializing database…")
    await init_db()

    bot = Bot(
        settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    session_maker = get_session_maker()
    for event in (dp.message, dp.callback_query):
        event.middleware(DbSessionMiddleware(session_maker))
        event.middleware(UserMiddleware())

    dp.include_router(setup_routers())

    logger.info("Starting bot polling…")
    await dp.start_polling(bot)


def run() -> None:
    asyncio.run(main())
