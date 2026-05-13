"""Репозиторий призов игры."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.prize import Prize


async def for_game(session: AsyncSession, game_id: int) -> list[Prize]:
    result = await session.execute(
        select(Prize)
        .where(Prize.game_id == game_id)
        .order_by(Prize.place_number.asc())
    )
    return list(result.scalars().all())


async def add(
    session: AsyncSession, *, game_id: int, place_number: int, amount: Decimal
) -> Prize:
    prize = Prize(game_id=game_id, place_number=place_number, amount=amount)
    session.add(prize)
    await session.flush()
    return prize


async def bulk_add(
    session: AsyncSession, *, game_id: int, amounts: list[Decimal]
) -> list[Prize]:
    prizes: list[Prize] = []
    for idx, amount in enumerate(amounts, 1):
        prizes.append(await add(session, game_id=game_id, place_number=idx, amount=amount))
    return prizes
