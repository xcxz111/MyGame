"""Репозиторий для `mbank_raw_emails`."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from database.models.payments.raw_email import MBankRawEmail


async def create(session: AsyncSession, **fields: Any) -> MBankRawEmail:
    email = MBankRawEmail(**fields)
    session.add(email)
    await session.flush()
    return email
