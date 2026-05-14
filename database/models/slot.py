"""История спинов игры «Слот»."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Index, Integer, Numeric, SmallInteger, func
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class SlotSpin(Base):
    __tablename__ = "slot_spins"
    __table_args__ = (
        Index("idx_slot_spins_created", "created_at"),
        Index("idx_slot_spins_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    bet_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    slot_value: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    multiplier: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=Decimal("0"))
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    payout: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    bot_profit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SlotSettings(Base):
    __tablename__ = "slot_settings"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False, default=1)
    enabled: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    rules_text: Mapped[str | None] = mapped_column(MEDIUMTEXT, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
