"""Призовые места игры (только суммы в PLN, бот сам припишет валюту)."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Prize(Base):
    __tablename__ = "prizes"
    __table_args__ = (
        UniqueConstraint("game_id", "place_number", name="uq_prizes_game_place"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("games.id", ondelete="CASCADE"),
        index=True,
    )
    place_number: Mapped[int] = mapped_column(Integer)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    def __repr__(self) -> str:
        return (
            f"<Prize id={self.id} game_id={self.game_id} "
            f"place={self.place_number} amount={self.amount}>"
        )
