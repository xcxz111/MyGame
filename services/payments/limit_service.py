"""Дневные лимиты по mbank-аккаунтам."""

import logging
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from database.models.payments.account import MBankAccount

logger = logging.getLogger(__name__)


async def add_usage_and_check(
    session_maker: async_sessionmaker[AsyncSession],
    account_email: str,
    amount: Decimal,
) -> None:
    """Прибавляет `amount` к daily_used. Если перешагнули лимит — кладём аккаунт спать."""
    async with session_maker() as session:
        account = await session.scalar(
            select(MBankAccount).where(MBankAccount.email == account_email)
        )
        if account is None or account.daily_limit is None:
            return

        already_sleeping = account.limit_sleeping
        account.daily_used = (account.daily_used or Decimal("0.00")) + amount

        if account.daily_used >= account.daily_limit and not already_sleeping:
            account.limit_sleeping = True
            logger.warning(
                "[%s] Daily limit %.2f reached (used=%.2f) — going to sleep",
                account_email,
                float(account.daily_limit),
                float(account.daily_used),
            )

        await session.commit()


async def reset_all_limits(
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    """Сброс daily_used и пробуждение всех спящих аккаунтов (вызывается раз в сутки)."""
    async with session_maker() as session:
        await session.execute(
            update(MBankAccount).values(daily_used=Decimal("0.00"), limit_sleeping=False)
        )
        await session.commit()
    logger.info("Daily limits reset for all mbank accounts")
