"""Таблицы «21» как в Game_bot (`Documents/Game_bot/db/init_db.py`)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, Numeric, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Game21BotSession(Base):
    __tablename__ = "game21_bot_sessions"
    __table_args__ = (
        Index("idx_21_user", "user_id"),
        Index("idx_21_status", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", server_default="active")
    bet_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    round_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    player_cards: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bot_cards: Mapped[str | None] = mapped_column(String(255), nullable=True)
    player_points: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    bot_points: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    winner: Mapped[str | None] = mapped_column(String(32), nullable=True)
    net_result: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    total_rounds: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    total_wins: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    total_losses: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    total_draws: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Game21BotRound(Base):
    """Раунды против бота (как `game21_bot_rounds` в Game_bot; в рантайме может не заполняться)."""

    __tablename__ = "game21_bot_rounds"
    __table_args__ = (Index("idx_21_round_session", "session_id", "round_number"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("game21_bot_sessions.id", ondelete="CASCADE"), nullable=False
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    player_cards: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bot_cards: Mapped[str | None] = mapped_column(String(255), nullable=True)
    player_points: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    bot_points: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    winner: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bet_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    net_result: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Game21UsersSession(Base):
    __tablename__ = "game21_users_sessions"
    __table_args__ = (
        UniqueConstraint("pvp_session_token", name="uq_21_users_session_token"),
        Index("idx_21_users_created", "created_at"),
        Index("idx_21_users_winner", "winner_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    pvp_session_token: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    player1_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    player2_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    bet_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("0"))
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    result: Mapped[str] = mapped_column(String(20), nullable=False, default="draw", server_default="draw")
    winner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    round_events_json: Mapped[str | None] = mapped_column(MEDIUMTEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Game21UsersRound(Base):
    """Построчные броски PvP (legacy `game21_users_rounds` в Game_bot)."""

    __tablename__ = "game21_users_rounds"
    __table_args__ = (
        Index("idx_21_users_rounds_session", "session_id", "throw_order"),
        Index("idx_21_users_rounds_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    phase: Mapped[str] = mapped_column(String(20), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    throw_order: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    total_after: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
