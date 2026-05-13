"""Глобальные настройки 21 — таблица `game21_settings` (singleton id=1)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, SmallInteger, func
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Game21Settings(Base):
    __tablename__ = "game21_settings"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False, default=1)
    enabled: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0")
    enabled_users: Mapped[int] = mapped_column(SmallInteger, default=1, server_default="1")
    commission_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), server_default="0.00"
    )
    commission_users_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), server_default="0.00"
    )
    rules_bot_text: Mapped[str | None] = mapped_column(MEDIUMTEXT, nullable=True)
    rules_users_text: Mapped[str | None] = mapped_column(MEDIUMTEXT, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    @property
    def enabled_bot(self) -> int:
        return int(self.enabled)

    @enabled_bot.setter
    def enabled_bot(self, v: int) -> None:
        self.enabled = int(v)

    @property
    def commission_bot_percent(self) -> Decimal:
        return self.commission_percent

    @commission_bot_percent.setter
    def commission_bot_percent(self, v: Decimal) -> None:
        self.commission_percent = v
