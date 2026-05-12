"""Репозиторий для `mbank_transactions`."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.payments.transaction import MBankTransaction


async def create(session: AsyncSession, **fields: Any) -> MBankTransaction:
    tx = MBankTransaction(**fields)
    session.add(tx)
    await session.flush()
    return tx


async def get(session: AsyncSession, tx_id: int) -> MBankTransaction | None:
    return await session.get(MBankTransaction, tx_id)
