"""Ордер на пополнение баланса (создаётся при нажатии «Пополнить»)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class MBankOrderStatus:
    """Значения для `mbank_orders.status`."""

    PENDING = "pending"
    MATCHED = "matched"
    COMPLETED = "completed"
    FAILED = "failed"


class MBankOrder(Base):
    __tablename__ = "mbank_orders"

    # TRN000001…TRN999999 — генерируется при создании ордера
    id: Mapped[str] = mapped_column(String(20), primary_key=True)

    # Какой юзер заказал пополнение (для зачисления баланса)
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        default=None,
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(16), default="PLN", server_default="PLN")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)

    status: Mapped[str] = mapped_column(
        String(16),
        default=MBankOrderStatus.PENDING,
        server_default=MBankOrderStatus.PENDING,
        index=True,
    )

    account_email: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("mbank_accounts.email", ondelete="RESTRICT"),
        index=True,
    )
    blik_number: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)

    bank_transaction_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("mbank_transactions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        default=None,
    )
    actual_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<MBankOrder id={self.id} user_id={self.user_id} amount={self.amount} status={self.status}>"
