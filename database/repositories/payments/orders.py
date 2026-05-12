"""Репозиторий для `mbank_orders`."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.payments.order import MBankOrder, MBankOrderStatus

ORDER_ID_PREFIX = "TRN"


def _format_order_id(serial: int) -> str:
    return f"{ORDER_ID_PREFIX}{serial:06d}"


async def _next_order_id(session: AsyncSession) -> str:
    count = await session.scalar(select(func.count()).select_from(MBankOrder)) or 0
    return _format_order_id(int(count) + 1)


async def get(session: AsyncSession, order_id: str) -> MBankOrder | None:
    return await session.get(MBankOrder, order_id)


async def create(
    session: AsyncSession,
    *,
    user_id: int | None,
    amount: Decimal,
    account_email: str,
    currency: str = "PLN",
    description: str | None = None,
    blik_number: str | None = None,
) -> MBankOrder:
    order = MBankOrder(
        id=await _next_order_id(session),
        user_id=user_id,
        amount=amount,
        currency=currency,
        description=description,
        account_email=account_email,
        blik_number=blik_number,
        status=MBankOrderStatus.PENDING,
    )
    session.add(order)
    await session.flush()
    return order


async def find_pending_for_user(
    session: AsyncSession,
    *,
    user_id: int,
    amount: Decimal,
    window: timedelta = timedelta(hours=1),
) -> MBankOrder | None:
    """Ищет «свежую» pending-заявку юзера с той же суммой (чтобы переиспользовать)."""
    since = datetime.utcnow() - window
    result = await session.execute(
        select(MBankOrder)
        .where(
            MBankOrder.user_id == user_id,
            MBankOrder.amount == amount,
            MBankOrder.status == MBankOrderStatus.PENDING,
            MBankOrder.created_at >= since,
        )
        .order_by(MBankOrder.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def update(session: AsyncSession, order_id: str, **fields: Any) -> MBankOrder | None:
    order = await session.get(MBankOrder, order_id)
    if order is None:
        return None
    for key, value in fields.items():
        setattr(order, key, value)
    await session.flush()
    return order


async def mark_matched(
    session: AsyncSession,
    order_id: str,
    *,
    bank_transaction_id: int,
    actual_amount: Decimal | None,
) -> MBankOrder | None:
    return await update(
        session,
        order_id,
        status=MBankOrderStatus.MATCHED,
        bank_transaction_id=bank_transaction_id,
        actual_amount=actual_amount,
    )


async def mark_completed(session: AsyncSession, order_id: str) -> None:
    await update(session, order_id, status=MBankOrderStatus.COMPLETED)


async def list_pending(session: AsyncSession) -> list[MBankOrder]:
    """Все pending-ордера (для recovery при старте)."""
    result = await session.execute(
        select(MBankOrder)
        .where(MBankOrder.status == MBankOrderStatus.PENDING)
        .order_by(MBankOrder.created_at)
    )
    return list(result.scalars().all())
