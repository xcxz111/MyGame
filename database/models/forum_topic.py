"""Синхронизированные темы форума (Telegram не отдаёт список тем через Bot API)."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class ForumTopic(Base):
    """Тема супергруппы с включёнными Topics; пополняется из forum_topic_* апдейтов."""

    __tablename__ = "forum_topics"
    __table_args__ = (UniqueConstraint("chat_id", "message_thread_id", name="uq_forum_topic_chat_thread"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    message_thread_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<ForumTopic chat={self.chat_id} thread={self.message_thread_id} {self.name!r}>"
