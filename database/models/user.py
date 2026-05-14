from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Numeric, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class UserStatus:
    """Значения для поля `users.status`."""

    ACTIVE = 0
    BANNED = 1


class UserRole:
    """Значения для поля `users.role`."""

    USER = "user"
    OPERATOR = "operator"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=False,
        comment="Telegram user id",
    )
    user_name: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        default=None,
        comment="Telegram @username",
    )
    name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        default=None,
        comment="first + last name",
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=UserStatus.ACTIVE,
        server_default=str(UserStatus.ACTIVE),
        comment="0 = active, 1 = banned",
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=UserRole.USER,
        server_default=UserRole.USER,
        comment="user | operator | moderator | admin",
    )
    language_code: Mapped[str | None] = mapped_column(
        String(8),
        nullable=True,
        default=None,
    )
    referrer_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        default=None,
        comment="Telegram user_id пригласившего пользователя",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<User user_id={self.user_id} role={self.role} status={self.status}>"
