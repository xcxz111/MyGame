"""Репозиторий для `mbank_accounts`."""

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.payments.account import MBankAccount


async def list_all(session: AsyncSession) -> list[MBankAccount]:
    result = await session.execute(select(MBankAccount).order_by(MBankAccount.id))
    return list(result.scalars().all())


async def list_active(session: AsyncSession) -> list[MBankAccount]:
    result = await session.execute(
        select(MBankAccount).where(MBankAccount.is_active.is_(True)).order_by(MBankAccount.id)
    )
    return list(result.scalars().all())


async def get(session: AsyncSession, account_id: int) -> MBankAccount | None:
    return await session.get(MBankAccount, account_id)


async def get_by_email(session: AsyncSession, email: str) -> MBankAccount | None:
    result = await session.execute(select(MBankAccount).where(MBankAccount.email == email))
    return result.scalar_one_or_none()


async def create(session: AsyncSession, **kwargs: Any) -> MBankAccount:
    account = MBankAccount(**kwargs)
    session.add(account)
    await session.flush()
    return account


async def update(session: AsyncSession, account_id: int, **fields: Any) -> MBankAccount | None:
    account = await session.get(MBankAccount, account_id)
    if account is None:
        return None
    for key, value in fields.items():
        setattr(account, key, value)
    await session.flush()
    return account


async def delete(session: AsyncSession, account_id: int) -> bool:
    account = await session.get(MBankAccount, account_id)
    if account is None:
        return False
    await session.delete(account)
    await session.flush()
    return True


async def set_active(session: AsyncSession, account_id: int, is_active: bool) -> None:
    await update(session, account_id, is_active=is_active)


async def update_last_uid(session: AsyncSession, account_id: int, last_uid: int) -> None:
    await update(session, account_id, last_uid=last_uid)


async def update_balance(
    session: AsyncSession,
    account_id: int,
    balance: Decimal,
    updated_at,
) -> None:
    await update(session, account_id, balance=balance, balance_updated_at=updated_at)
