"""Репозиторий для `fees` (singleton с id=1)."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.fees import Fee

_SINGLETON_ID = 1


async def get_or_create(session: AsyncSession) -> Fee:
    fee = await session.get(Fee, _SINGLETON_ID)
    if fee is None:
        fee = Fee(id=_SINGLETON_ID, withdraw_percent=Decimal("0.00"))
        session.add(fee)
        await session.flush()
    return fee


async def get_withdraw_percent(session: AsyncSession) -> Decimal:
    fee = await get_or_create(session)
    return fee.withdraw_percent or Decimal("0.00")


async def set_withdraw_percent(
    session: AsyncSession, percent: Decimal
) -> Fee:
    fee = await get_or_create(session)
    fee.withdraw_percent = percent
    await session.flush()
    return fee
