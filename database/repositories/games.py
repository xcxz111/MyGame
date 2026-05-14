"""Репозиторий игр."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.game import Game, GameStatus


async def get(session: AsyncSession, game_id: int) -> Game | None:
    return await session.get(Game, game_id)


async def get_active_for_update(session: AsyncSession, game_id: int) -> Game | None:
    """Строка игры с блокировкой; только ACTIVE — для единоразовой выплаты призов."""
    result = await session.execute(
        select(Game)
        .where(Game.id == int(game_id), Game.status == GameStatus.ACTIVE)
        .with_for_update()
    )
    return result.scalar_one_or_none()


async def get_draft_for_update(session: AsyncSession, game_id: int) -> Game | None:
    """Строка игры с блокировкой; только DRAFT — запись/выход без гонок по местам и взносу."""
    result = await session.execute(
        select(Game)
        .where(Game.id == int(game_id), Game.status == GameStatus.DRAFT)
        .with_for_update()
    )
    return result.scalar_one_or_none()


async def get_current(session: AsyncSession) -> list[Game]:
    """Текущие игры: draft (ждут старта) + active (уже идут)."""
    result = await session.execute(
        select(Game)
        .where(Game.status.in_([GameStatus.DRAFT, GameStatus.ACTIVE]))
        .order_by(Game.start_time.asc())
    )
    return list(result.scalars().all())


async def get_finished(session: AsyncSession) -> list[Game]:
    """Завершённые и отменённые игры (от свежих к старым)."""
    result = await session.execute(
        select(Game)
        .where(Game.status.in_([GameStatus.FINISHED, GameStatus.CANCELLED]))
        .order_by(Game.start_time.desc())
    )
    return list(result.scalars().all())


async def create(
    session: AsyncSession,
    *,
    name: str,
    game_type: str,
    chat_id: int,
    start_time: datetime,
    min_participants: int,
    max_participants: int,
    prize_places: int,
    is_paid: bool = False,
    entry_fee: Decimal = Decimal("0.00"),
    min_topup: Decimal = Decimal("0.00"),
    min_topup_since: Any = None,
    message_thread_id: int | None = None,
) -> Game:
    game = Game(
        name=name,
        game_type=game_type,
        chat_id=chat_id,
        message_thread_id=message_thread_id,
        start_time=start_time,
        is_paid=1 if is_paid else 0,
        entry_fee=entry_fee,
        min_topup=min_topup,
        min_topup_since=min_topup_since,
        min_participants=min_participants,
        max_participants=max_participants,
        prize_places=prize_places,
        status=GameStatus.DRAFT,
    )
    session.add(game)
    await session.flush()
    return game


async def update(session: AsyncSession, game_id: int, **fields: Any) -> Game | None:
    game = await session.get(Game, game_id)
    if game is None:
        return None
    for key, value in fields.items():
        setattr(game, key, value)
    await session.flush()
    return game


async def set_announcement_message(
    session: AsyncSession, game_id: int, message_id: int
) -> None:
    await update(session, game_id, announcement_message_id=message_id)


async def set_announcement_messages(
    session: AsyncSession,
    game_id: int,
    *,
    topic_message_id: int | None,
    general_message_id: int | None = None,
) -> None:
    await update(
        session,
        game_id,
        announcement_message_id=topic_message_id,
        announcement_message_id_general=general_message_id,
    )


async def count_participants(session: AsyncSession, game_id: int) -> int:
    from database.models.game_participant import GameParticipant

    result = await session.execute(
        select(func.count(GameParticipant.id)).where(
            GameParticipant.game_id == game_id
        )
    )
    return int(result.scalar() or 0)


async def list_for_5min_reminder(session: AsyncSession, now: datetime) -> list[Game]:
    """Игры, до старта которых 5–6 минут (как в Game_bot)."""
    w0 = now + timedelta(minutes=5)
    w1 = now + timedelta(minutes=6)
    result = await session.execute(
        select(Game)
        .where(
            Game.status == GameStatus.DRAFT,
            Game.reminder_5min_sent == 0,
            Game.start_time > w0,
            Game.start_time <= w1,
        )
        .order_by(Game.start_time.asc())
    )
    return list(result.scalars().all())


async def list_draft_past_start_buffer(session: AsyncSession, now: datetime) -> list[Game]:
    """Черновики, время старта которых наступило ≥ 1 мин назад (буфер рассинхрона)."""
    cutoff = now - timedelta(minutes=1)
    result = await session.execute(
        select(Game)
        .where(Game.status == GameStatus.DRAFT, Game.start_time <= cutoff)
        .order_by(Game.start_time.asc())
    )
    return list(result.scalars().all())


async def list_draft_future_for_signup(session: AsyncSession, now: datetime) -> list[Game]:
    """Черновики со стартом в будущем — доступны для записи."""
    result = await session.execute(
        select(Game)
        .where(Game.status == GameStatus.DRAFT, Game.start_time > now)
        .order_by(Game.start_time.asc())
        .limit(30)
    )
    return list(result.scalars().all())
