"""Лог всех движений по балансам пользователей (`payments_bot`)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class PaymentLogMethod:
    """Зарезервированные значения `method`, чтобы не было опечаток.

    В поле можно писать и произвольные значения (например, название игры).
    """

    TOPUP = "topup"               # пополнение баланса через BLIK
    WITHDRAW = "withdraw"         # списание при создании заявки на вывод
    WITHDRAW_REFUND = "withdraw_refund"  # возврат денег при отмене вывода
    TRANSFER_IN = "transfer_in"   # входящий перевод от другого юзера (на будущее)
    TRANSFER_OUT = "transfer_out" # исходящий перевод (на будущее)
    GAME_ENTRY = "game_entry"     # взнос за участие в игре (платная игра)
    GAME_ENTRY_REFUND = "game_entry_refund"  # возврат взноса (отмена игры / выход до старта)
    GAME_PRIZE = "game_prize"     # выигрыш по месту (method + place в отдельном поле не кладём — см. amount)
    # для игр сюда будем класть код/название: 'game:21', 'game:slot', и т.п.


class PaymentLog(Base):
    __tablename__ = "payments_bot"
    __table_args__ = (
        Index("ix_payments_bot_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
    )

    method: Mapped[str] = mapped_column(
        String(64),
        index=True,
        comment="Тип движения: 'topup' / 'withdraw' / 'withdraw_refund' / 'game:21' / ...",
    )

    # Сумма движения: положительная — зачисление, отрицательная — списание.
    amount: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2), nullable=True, default=None
    )

    # Баланс пользователя сразу после операции.
    balance_after: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return (
            f"<PaymentLog id={self.id} user_id={self.user_id} "
            f"method={self.method} amount={self.amount} "
            f"balance_after={self.balance_after}>"
        )
