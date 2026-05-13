"""Singleton-настройки «21»."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.game21_settings import Game21Settings

_ROW_ID = 1


async def _row(session: AsyncSession) -> Game21Settings:
    r = await session.get(Game21Settings, _ROW_ID)
    if r is None:
        r = Game21Settings(id=_ROW_ID)
        session.add(r)
        await session.flush()
    return r


async def get_settings(session: AsyncSession) -> Game21Settings:
    return await _row(session)


async def set_enabled_bot(session: AsyncSession, enabled: bool) -> None:
    s = await _row(session)
    s.enabled = 1 if enabled else 0
    await session.flush()


async def set_enabled_users(session: AsyncSession, enabled: bool) -> None:
    s = await _row(session)
    s.enabled_users = 1 if enabled else 0
    await session.flush()


async def set_commission_bot(session: AsyncSession, percent: Decimal) -> None:
    s = await _row(session)
    s.commission_percent = percent
    await session.flush()


async def set_commission_users(session: AsyncSession, percent: Decimal) -> None:
    s = await _row(session)
    s.commission_users_percent = percent
    await session.flush()
