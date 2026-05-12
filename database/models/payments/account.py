"""Почтовый аккаунт банка, который мониторится через IMAP."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class MBankAccount(Base):
    __tablename__ = "mbank_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # --- IMAP подключение ---
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    imap_host: Mapped[str] = mapped_column(String(255), default="imap.gmail.com", server_default="imap.gmail.com")
    imap_port: Mapped[int] = mapped_column(Integer, default=993, server_default="993")
    use_ssl: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    mailbox: Mapped[str] = mapped_column(String(64), default="INBOX", server_default="INBOX")
    proxy: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)

    # --- Мониторинг ---
    last_uid: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    # --- Бизнес-атрибуты ---
    bank: Mapped[str] = mapped_column(
        String(20),
        default="other",
        server_default="other",
        comment="ipko | santander | other",
    )
    blik_number: Mapped[str | None] = mapped_column(String(32), nullable=True, default=None)
    account_number: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)

    # --- Лимиты ---
    daily_limit: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        default=None,
        comment="NULL = без лимита",
    )
    limit_type: Mapped[str] = mapped_column(
        String(20),
        default="all",
        server_default="all",
        comment="all | matched",
    )
    limit_sleeping: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    daily_used: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        server_default="0.00",
    )

    # --- Баланс из писем ---
    balance: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True, default=None)
    balance_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)

    # --- timestamps ---
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<MBankAccount id={self.id} email={self.email} bank={self.bank}>"
