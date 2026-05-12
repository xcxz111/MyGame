"""Асинхронный движок и фабрика сессий SQLAlchemy.

Ленивая инициализация: движок создаётся только при первом обращении,
чтобы импорт пакета не падал без переменных окружения для БД.
"""

from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from settings import get_settings


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(
        settings.mysql_url,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )


@lru_cache
def get_session_maker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        get_engine(),
        expire_on_commit=False,
        class_=AsyncSession,
    )
