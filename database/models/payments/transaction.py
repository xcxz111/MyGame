"""Распознанная банковская транзакция (после AI-парсинга письма)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class MBankTransaction(Base):
    __tablename__ = "mbank_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    email_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("mbank_raw_emails.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        default=None,
    )
    account_email: Mapped[str] = mapped_column(String(255), index=True)
    uid: Mapped[int] = mapped_column(Integer)

    sender: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)

    # Поля, которые AI извлёк из письма
    account_number: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True, default=None)
    currency: Mapped[str | None] = mapped_column(String(16), nullable=True, default=None)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None, comment="назначение платежа; TRN###### ищется здесь")
    transaction_date: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    balance_after: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True, default=None)

    raw_body: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    missing_fields: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<MBankTransaction id={self.id} amount={self.amount} title={self.title!r}>"
