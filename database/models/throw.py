"""Броски кубиков/боулинга/дартса по раундам игры."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Throw(Base):
    __tablename__ = "throws"
    __table_args__ = (
        Index("ix_throws_game_round_user", "game_id", "round_number", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("games.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
    )
    round_number: Mapped[int] = mapped_column(Integer)
    throw_index: Mapped[int] = mapped_column(SmallInteger)
    value: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return (
            f"<Throw id={self.id} game_id={self.game_id} user_id={self.user_id} "
            f"round={self.round_number} idx={self.throw_index} value={self.value}>"
        )
