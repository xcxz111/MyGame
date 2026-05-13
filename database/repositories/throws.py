"""Броски в играх (таблица `throws`)."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.throw import Throw


async def add_throw(
    session: AsyncSession,
    *,
    game_id: int,
    user_id: int,
    round_number: int,
    throw_index: int,
    value: int,
) -> Throw:
    row = Throw(
        game_id=game_id,
        user_id=user_id,
        round_number=round_number,
        throw_index=throw_index,
        value=value,
    )
    session.add(row)
    await session.flush()
    return row


async def get_round_totals(
    session: AsyncSession, game_id: int, round_number: int
) -> list[tuple[int, int]]:
    """Сумма очков за раунд (только основные броски throw_index 0,1,2)."""
    result = await session.execute(
        select(Throw.user_id, func.coalesce(func.sum(Throw.value), 0))
        .where(
            Throw.game_id == game_id,
            Throw.round_number == round_number,
            Throw.throw_index < 3,
        )
        .group_by(Throw.user_id)
    )
    return [(int(uid), int(total or 0)) for uid, total in result.all()]


async def get_round_tiebreak_totals(
    session: AsyncSession, game_id: int, round_number: int
) -> list[tuple[int, int]]:
    """Сумма доп. бросков тай-брейка (throw_index >= 3)."""
    result = await session.execute(
        select(Throw.user_id, func.coalesce(func.sum(Throw.value), 0))
        .where(
            Throw.game_id == game_id,
            Throw.round_number == round_number,
            Throw.throw_index >= 3,
        )
        .group_by(Throw.user_id)
    )
    return [(int(uid), int(total or 0)) for uid, total in result.all()]
