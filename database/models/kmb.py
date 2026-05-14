"""PvP-игра «Камень/ножницы/бумага»."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Index, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class KmbSession(Base):
    __tablename__ = "kmb_sessions"
    __table_args__ = (
        Index("idx_kmb_created", "created_at"),
        Index("idx_kmb_winner", "winner_id"),
        Index("idx_kmb_chat", "chat_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_thread_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    player1_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    player2_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    bet_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0")
    )
    target_wins: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    commission_percent: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    commission_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0.00"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", server_default="active"
    )
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    winner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    moves_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class KmbSettings(Base):
    __tablename__ = "kmb_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    enabled: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    rules_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
