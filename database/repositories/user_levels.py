"""Репозиторий уровней пользователей."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.payment_log import PaymentLogMethod
from database.models.user import User
from database.models.user_level import UserLevel
from database.repositories import payment_logs as payment_logs_repo


async def list_levels(session: AsyncSession) -> list[UserLevel]:
    result = await session.execute(select(UserLevel).order_by(UserLevel.level.asc()))
    return list(result.scalars().all())


async def get_level(session: AsyncSession, level: int) -> UserLevel | None:
    return await session.get(UserLevel, int(level))


async def set_title(session: AsyncSession, level: int, title: str | None) -> UserLevel | None:
    row = await get_level(session, level)
    if row is None:
        return None
    row.title = title
    await session.flush()
    return row


async def set_required_win_bet_sum(
    session: AsyncSession, level: int, amount: Decimal
) -> UserLevel | None:
    row = await get_level(session, level)
    if row is None:
        return None
    row.required_win_bet_sum = amount
    await session.flush()
    return row


async def set_balance_reward(
    session: AsyncSession, level: int, amount: Decimal
) -> UserLevel | None:
    row = await get_level(session, level)
    if row is None:
        return None
    row.balance_reward = amount
    await session.flush()
    return row


async def set_withdraw_discount_percent(
    session: AsyncSession, level: int, percent: Decimal
) -> UserLevel | None:
    row = await get_level(session, level)
    if row is None:
        return None
    row.withdraw_discount_percent = percent
    await session.flush()
    return row


async def set_referral_bonus_percent(
    session: AsyncSession, level: int, percent: Decimal
) -> UserLevel | None:
    row = await get_level(session, level)
    if row is None:
        return None
    row.referral_bonus_percent = percent
    await session.flush()
    return row


async def set_active(
    session: AsyncSession, level: int, *, active: bool
) -> UserLevel | None:
    row = await get_level(session, level)
    if row is None:
        return None
    row.active = 1 if active else 0
    await session.flush()
    return row


async def get_bonus_totals(
    session: AsyncSession, level: int
) -> tuple[Decimal, Decimal]:
    row = (
        await session.execute(
            select(
                func.coalesce(func.sum(UserLevel.withdraw_discount_percent), 0).label(
                    "withdraw_discount"
                ),
                func.coalesce(func.sum(UserLevel.referral_bonus_percent), 0).label(
                    "referral_bonus"
                ),
            ).where(
                UserLevel.active == 1,
                UserLevel.level <= int(level),
            )
        )
    ).one()
    return (
        Decimal(str(row.withdraw_discount or "0")).quantize(Decimal("0.01")),
        Decimal(str(row.referral_bonus or "0")).quantize(Decimal("0.01")),
    )


async def add_winning_bet_progress(
    session: AsyncSession,
    *,
    user_id: int,
    bet_amount: Decimal,
    source: str | None = None,
) -> int | None:
    if bet_amount <= 0:
        return None
    user = await session.get(User, int(user_id))
    if user is None:
        return None

    user.level_win_bet_sum = (user.level_win_bet_sum or Decimal("0")) + bet_amount
    current_level = int(user.level or 1)
    target = (
        await session.execute(
            select(UserLevel)
            .where(
                UserLevel.active == 1,
                UserLevel.required_win_bet_sum <= user.level_win_bet_sum,
            )
            .order_by(UserLevel.level.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if target is None or int(target.level) <= current_level:
        await session.flush()
        return current_level

    levels = (
        await session.execute(
            select(UserLevel)
            .where(
                UserLevel.active == 1,
                UserLevel.level > current_level,
                UserLevel.level <= int(target.level),
            )
            .order_by(UserLevel.level.asc())
        )
    ).scalars().all()
    for level in levels:
        reward = level.balance_reward or Decimal("0")
        if reward > 0:
            user.balance = (user.balance or Decimal("0")) + reward
            await session.flush()
            await payment_logs_repo.log(
                session,
                user_id=int(user.user_id),
                method=PaymentLogMethod.LEVEL_REWARD,
                amount=reward,
                balance_after=user.balance,
            )
    user.level = int(target.level)
    await session.flush()
    return int(target.level)
