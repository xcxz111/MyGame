import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database.engine import get_session_maker
from database.init_db import init_db
from handlers import setup_routers
from middlewares import ActiveBotGameBlockMiddleware, DbSessionMiddleware, UserMiddleware
from services.games import run_games_background_loop
from services.payments.ai_clients.factory import create_ai_client
from services.payments.monitor_manager import MonitorManager
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
        event.middleware(ActiveBotGameBlockMiddleware())

    # ── MBanks (IMAP + AI) ────────────────────────────────────────────────────
    mbanks_manager: MonitorManager | None = None
    if settings.mbanks_enabled:
        try:
            ai_client = create_ai_client(settings)
            mbanks_manager = MonitorManager(
                session_maker=session_maker,
                ai_client=ai_client,
                settings=settings,
                bot=bot,
            )
            logger.info("MBanks: enabled (AI provider=%s)", settings.ai_provider)
        except Exception as exc:
            logger.error("MBanks init failed: %s", exc, exc_info=True)
            mbanks_manager = None
    else:
        logger.info("MBanks: disabled (set MBANKS_ENABLED=true in .env to enable)")

    # пробрасываем в хендлеры через workflow_data (даже None — чтобы aiogram мог инжектить)
    dp["mbanks_manager"] = mbanks_manager

    dp.include_router(setup_routers())

    async def _on_startup() -> None:
        if mbanks_manager is not None:
            await mbanks_manager.start_all()
        asyncio.create_task(run_games_background_loop(bot, session_maker))

    async def _on_shutdown() -> None:
        if mbanks_manager is not None:
            await mbanks_manager.stop_all()

    dp.startup.register(_on_startup)
    dp.shutdown.register(_on_shutdown)

    logger.info("Starting bot polling…")
    await dp.start_polling(bot)


def run() -> None:
    asyncio.run(main())
