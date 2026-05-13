"""Репозиторий для `payments_bot`."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.payment_log import PaymentLog, PaymentLogMethod


async def sum_topup_amount(
    session: AsyncSession,
    *,
    user_id: int,
    since: date | None = None,
    until: datetime | None = None,
) -> Decimal:
    """Сумма пополнений (method=topup) за период. `since` — с начала этого дня (включительно)."""
    q = select(func.coalesce(func.sum(PaymentLog.amount), 0)).where(
        PaymentLog.user_id == user_id,
        PaymentLog.method == PaymentLogMethod.TOPUP,
        PaymentLog.amount.isnot(None),
        PaymentLog.amount > 0,
    )
    if since is not None:
        start_dt = datetime.combine(since, datetime.min.time())
        q = q.where(PaymentLog.created_at >= start_dt)
    if until is not None:
        q = q.where(PaymentLog.created_at <= until)
    result = await session.execute(q)
    val = result.scalar()
    return Decimal(str(val or 0)).quantize(Decimal("0.01"))


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
