"""Глобальные настройки комиссий (singleton, id=1).

Сейчас одно поле — комиссия вывода. В будущем сюда добавим комиссии для
переводов между юзерами, игр и т.п.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Fee(Base):
    __tablename__ = "fees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    withdraw_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("0.00"),
        server_default="0.00",
        comment="Комиссия за вывод средств, в процентах от запрошенной суммы",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Fee id={self.id} withdraw_percent={self.withdraw_percent}>"
