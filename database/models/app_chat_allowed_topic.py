"""Разрешённые темы форума для игр в подключённом чате (whitelist).

`message_thread_id == 0` означает общий чат без темы. Реальные темы Telegram — положительные id.
"""

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base

GENERAL_THREAD_DB = 0


class AppChatAllowedTopic(Base):
    __tablename__ = "app_chat_allowed_topics"
    __table_args__ = (
        UniqueConstraint(
            "app_chat_id",
            "message_thread_id",
            name="uq_app_chat_allowed_thread",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    app_chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("app_chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message_thread_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="0 = общий чат; иначе message_thread_id темы",
    )

    def __repr__(self) -> str:
        return f"<AppChatAllowedTopic app_chat_id={self.app_chat_id} thread={self.message_thread_id}>"
