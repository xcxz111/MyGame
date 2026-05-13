"""Репозиторий для `withdrawals`."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.withdrawal import Withdrawal, WithdrawalStatus


async def get(session: AsyncSession, withdrawal_id: int) -> Withdrawal | None:
    return await session.get(Withdrawal, withdrawal_id)


async def get_pending_for_user(
    session: AsyncSession, user_id: int
) -> Withdrawal | None:
    result = await session.execute(
        select(Withdrawal)
        .where(
            Withdrawal.user_id == user_id,
            Withdrawal.status == WithdrawalStatus.PENDING,
        )
        .order_by(Withdrawal.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create(
    session: AsyncSession,
    *,
    user_id: int,
    amount: Decimal,
    fee_percent: Decimal,
    payout_amount: Decimal,
    blik_number: str,
) -> Withdrawal:
    withdrawal = Withdrawal(
        user_id=user_id,
        amount=amount,
        fee_percent=fee_percent,
        payout_amount=payout_amount,
        blik_number=blik_number,
        status=WithdrawalStatus.PENDING,
    )
    session.add(withdrawal)
    await session.flush()
    return withdrawal


async def update(
    session: AsyncSession, withdrawal_id: int, **fields: Any
) -> Withdrawal | None:
    withdrawal = await session.get(Withdrawal, withdrawal_id)
    if withdrawal is None:
        return None
    for key, value in fields.items():
        setattr(withdrawal, key, value)
    await session.flush()
    return withdrawal


async def set_admin_message(
    session: AsyncSession,
    withdrawal_id: int,
    chat_id: int,
    message_id: int,
) -> None:
    await update(
        session,
        withdrawal_id,
        admin_chat_id=chat_id,
        admin_message_id=message_id,
    )


async def mark_approved(
    session: AsyncSession, withdrawal_id: int, *, approved_by: int
) -> Withdrawal | None:
    return await update(
        session,
        withdrawal_id,
        status=WithdrawalStatus.APPROVED,
        approved_by=approved_by,
        approved_at=datetime.now(timezone.utc),
    )


async def mark_cancelled(
    session: AsyncSession, withdrawal_id: int
) -> Withdrawal | None:
    return await update(
        session,
        withdrawal_id,
        status=WithdrawalStatus.CANCELLED,
        cancelled_at=datetime.now(timezone.utc),
    )
