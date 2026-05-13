"""Игра-турнир (кубики / боулинг / дартс)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class GameType:
    """Тип игры (Telegram-эмодзи бросков)."""

    DICE = "dice"        # 🎲
    BOWLING = "bowling"  # 🎳
    DARTS = "darts"      # 🎯
    ANY = "any"          # 🎲🎳🎯 — игрок сам выбирает эмодзи броска

    LEGACY = (DICE, BOWLING, DARTS)


class GameStatus:
    """Статусы жизненного цикла игры."""

    DRAFT = "draft"          # создана, ждёт времени старта (запись игроков идёт)
    ACTIVE = "active"        # сейчас играем
    FINISHED = "finished"    # завершена (есть победители)
    CANCELLED = "cancelled"  # отменена (нет минимума участников и т.п.)


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (
        Index("ix_games_status_start", "status", "start_time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    game_type: Mapped[str] = mapped_column(
        String(16), default=GameType.ANY, server_default=GameType.ANY
    )

    # Куда публикуется анонс и проходят раунды (для форума — конкретная тема)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_thread_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None,
        comment="ID темы форума (message_thread_id); NULL — обычный чат или основная ветка без явного id",
    )

    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)

    # Платная игра / стоимость взноса
    is_paid: Mapped[bool] = mapped_column(SmallInteger, default=0, server_default="0")
    entry_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), server_default="0.00"
    )

    # Условие для записи: минимальная сумма пополнений баланса (PLN)
    # 0 — без условия. min_topup_since=NULL — за всё время; иначе за период с указанной даты.
    min_topup: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00"), server_default="0.00"
    )
    min_topup_since: Mapped[datetime | None] = mapped_column(
        Date, nullable=True, default=None
    )

    min_participants: Mapped[int] = mapped_column(Integer, default=2, server_default="2")
    max_participants: Mapped[int] = mapped_column(
        Integer, default=50, server_default="50"
    )
    prize_places: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    status: Mapped[str] = mapped_column(
        String(16),
        default=GameStatus.DRAFT,
        server_default=GameStatus.DRAFT,
        index=True,
    )
    current_round: Mapped[int] = mapped_column(Integer, default=1, server_default="1")

    # ID сообщения с анонсом в чате (для форума — в выбранной теме; открепление при завершении)
    announcement_message_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, default=None
    )
    # Дубль анонса в «общем» чате супергруппы (без message_thread_id); открепляется при старте игры
    announcement_message_id_general: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, default=None
    )
    reminder_5min_sent: Mapped[bool] = mapped_column(
        SmallInteger, default=0, server_default="0"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<Game id={self.id} type={self.game_type} status={self.status} "
            f"start={self.start_time} chat={self.chat_id}>"
        )
