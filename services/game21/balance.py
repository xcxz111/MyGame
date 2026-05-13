"""Списания и начисления по балансу для игры 21."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import payment_logs as payment_logs_repo
from database.repositories import users as users_repo

METHOD_PVP_STAKE = "game:21:pvp:stake"
METHOD_PVP_WIN = "game:21:pvp:win"
METHOD_PVP_REFUND = "game:21:pvp:refund"
METHOD_BOT_STAKE = "game:21:bot:stake"
METHOD_BOT_WIN = "game:21:bot:win"
METHOD_BOT_REFUND = "game:21:bot:refund"


async def get_balance(session: AsyncSession, user_id: int) -> Decimal:
    u = await users_repo.get_user(session, user_id)
    if u is None:
        return Decimal("0")
    return u.balance or Decimal("0")


async def add_balance(
    session: AsyncSession,
    user_id: int,
    amount: Decimal,
    *,
    method: str,
) -> Decimal | None:
    u = await users_repo.get_user(session, user_id)
    if u is None:
        return None
    u.balance = (u.balance or Decimal("0")) + amount
    await session.flush()
    await payment_logs_repo.log(
        session,
        user_id=user_id,
        method=method,
        amount=amount,
        balance_after=u.balance,
    )
    return u.balance


async def take_balance(
    session: AsyncSession,
    user_id: int,
    amount: Decimal,
    *,
    method: str,
) -> bool:
    u = await users_repo.get_user(session, user_id)
    if u is None:
        return False
    bal = u.balance or Decimal("0")
    if bal < amount:
        return False
    u.balance = bal - amount
    await session.flush()
    await payment_logs_repo.log(
        session,
        user_id=user_id,
        method=method,
        amount=-amount,
        balance_after=u.balance,
    )
    return True
