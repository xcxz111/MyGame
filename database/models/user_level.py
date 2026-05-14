"""Настройки уровней пользователей."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class UserLevel(Base):
    __tablename__ = "user_levels"

    level: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
    title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    required_win_bet_sum: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
        comment="Сумма выигранных ставок, необходимая для уровня",
    )
    balance_reward: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
        comment="Награда на баланс при получении уровня",
    )
    withdraw_discount_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
        comment="Скидка к комиссии вывода за уровень",
    )
    referral_bonus_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
        comment="Надбавка к реферальному проценту за уровень",
    )
    active: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=1,
        server_default="1",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
