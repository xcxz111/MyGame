"""Создаёт таблицы по моделям SQLAlchemy.

Использование:
    python -m database.init_db

База данных (`mysql_database` из .env) должна существовать.
Если её нет — создайте вручную:
    CREATE DATABASE mygame CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"""

import asyncio
import logging

from database.base import Base
from database.engine import get_engine
from database.models import (  # noqa: F401  — регистрирует модели в metadata
    MBankAccount,
    MBankOrder,
    MBankRawEmail,
    MBankTransaction,
    User,
)

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Создаёт таблицы по моделям. Движок не закрывает — он переиспользуется ботом."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _standalone() -> None:
    """Точка входа для запуска отдельно (`python -m database.init_db`)."""
    try:
        await init_db()
    finally:
        await get_engine().dispose()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.info("Initializing database…")
    asyncio.run(_standalone())
    logger.info("Done.")


if __name__ == "__main__":
    main()
