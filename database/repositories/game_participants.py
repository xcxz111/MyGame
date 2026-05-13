"""Репозиторий участников игры."""

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.game_participant import GameParticipant
from database.models.throw import Throw
from database.models.user import User


async def for_game_with_users(
    session: AsyncSession, game_id: int
) -> list[tuple[GameParticipant, User | None]]:
    """[(participant, user|None), ...] в порядке записи."""
    result = await session.execute(
        select(GameParticipant, User)
        .join(User, User.user_id == GameParticipant.user_id, isouter=True)
        .where(GameParticipant.game_id == game_id)
        .order_by(GameParticipant.registered_at.asc(), GameParticipant.id.asc())
    )
    return [(p, u) for p, u in result.all()]


async def is_registered(
    session: AsyncSession, *, game_id: int, user_id: int
) -> bool:
    result = await session.execute(
        select(func.count(GameParticipant.id)).where(
            GameParticipant.game_id == game_id,
            GameParticipant.user_id == user_id,
        )
    )
    return int(result.scalar() or 0) > 0


async def register(
    session: AsyncSession, *, game_id: int, user_id: int
) -> GameParticipant:
    p = GameParticipant(game_id=game_id, user_id=user_id)
    session.add(p)
    await session.flush()
    return p


async def unregister(
    session: AsyncSession, *, game_id: int, user_id: int
) -> bool:
    result = await session.execute(
        select(GameParticipant).where(
            GameParticipant.game_id == game_id,
            GameParticipant.user_id == user_id,
        )
    )
    p = result.scalar_one_or_none()
    if p is None:
        return False
    await session.delete(p)
    await session.flush()
    return True


async def list_user_ids(session: AsyncSession, game_id: int) -> list[int]:
    result = await session.execute(
        select(GameParticipant.user_id)
        .where(GameParticipant.game_id == game_id)
        .order_by(GameParticipant.registered_at.asc(), GameParticipant.id.asc())
    )
    return [int(r[0]) for r in result.all()]


async def list_user_ids_missed_game(session: AsyncSession, game_id: int) -> list[int]:
    """Участники с суммой основных бросков (throw_index < 3) = 0 (не сыграли)."""
    main_sum = func.coalesce(
        func.sum(case((Throw.throw_index < 3, Throw.value), else_=0)),
        0,
    )
    result = await session.execute(
        select(GameParticipant.user_id)
        .outerjoin(
            Throw,
            (Throw.game_id == GameParticipant.game_id)
            & (Throw.user_id == GameParticipant.user_id),
        )
        .where(GameParticipant.game_id == game_id)
        .group_by(GameParticipant.user_id)
        .having(main_sum == 0)
    )
    return [int(r[0]) for r in result.all()]
