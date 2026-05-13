"""Репозиторий для `payments_bot`."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.payment_log import PaymentLog


async def log(
    session: AsyncSession,
    *,
    user_id: int,
    method: str,
    balance_after: Decimal,
    amount: Decimal | None = None,
) -> PaymentLog:
    """Записывает движение по балансу. session.commit() — на стороне вызывающего."""
    entry = PaymentLog(
        user_id=user_id,
        method=method,
        amount=amount,
        balance_after=balance_after,
    )
    session.add(entry)
    await session.flush()
    return entry
