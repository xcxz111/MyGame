"""Заявка пользователя на вывод средств."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class WithdrawalStatus:
    PENDING = "pending"
    APPROVED = "approved"
    CANCELLED = "cancelled"


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
    )

    # Запрошенная сумма (списывается с баланса) и итоговая выплата (минус комиссия)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    fee_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        server_default="0.00",
    )
    payout_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    blik_number: Mapped[str] = mapped_column(String(32))

    status: Mapped[str] = mapped_column(
        String(16),
        default=WithdrawalStatus.PENDING,
        server_default=WithdrawalStatus.PENDING,
        index=True,
    )

    # Куда отправили админ-сообщение (для последующего edit)
    admin_chat_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, default=None
    )
    admin_message_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None
    )

    approved_by: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, default=None
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<Withdrawal id={self.id} user_id={self.user_id} "
            f"amount={self.amount} status={self.status}>"
        )
