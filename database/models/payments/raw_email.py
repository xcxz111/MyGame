"""Сырое письмо из IMAP (до парсинга)."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class MBankRawEmail(Base):
    __tablename__ = "mbank_raw_emails"
    __table_args__ = (
        UniqueConstraint("account_email", "uid", name="uq_mbank_raw_emails_account_uid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    account_email: Mapped[str] = mapped_column(String(255), index=True)
    uid: Mapped[int] = mapped_column(Integer)

    sender: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    subject: Mapped[str | None] = mapped_column(String(512), nullable=True, default=None)
    date: Mapped[str | None] = mapped_column(String(64), nullable=True, default=None)

    body_plain: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<MBankRawEmail id={self.id} email={self.account_email} uid={self.uid}>"
