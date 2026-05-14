"""Подключённые чаты для анонсов игр."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class AppChat(Base):
    __tablename__ = "app_chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, comment="Telegram chat_id (-100...)"
    )
    chat_link: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        default=None,
        comment="invite-ссылка (бот создаёт через API или экспорт)",
    )
    # Подпись кнопки «в чат» по языку интерфейса (при добавлении можно заполнить одной строкой во все).
    button_title_ru: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )
    button_title_en: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )
    button_title_uk: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )
    button_title_pl: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None
    )
    game21_users_enabled: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
        comment="PvP 21 между пользователями в этом чате",
    )
    checkers_enabled: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        default=0,
        server_default="0",
        comment="PvP шашки в этом чате",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def button_title_for(self, language_code: str | None) -> str | None:
        """Текст кнопки для языка `language_code` (fallback по ru→en→uk→pl)."""
        from locales.texts import get_lang

        code = get_lang(language_code)
        for key in (code, "ru", "en", "uk", "pl"):
            raw = getattr(self, f"button_title_{key}", None)
            if raw and str(raw).strip():
                return str(raw).strip()
        return None

    def __repr__(self) -> str:
        return f"<AppChat id={self.id} chat_id={self.chat_id}>"
