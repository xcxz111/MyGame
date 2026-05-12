from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    admin_id: int | None = None

    # ---- MySQL ----
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "mygame"

    @property
    def mysql_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset=utf8mb4"
        )

    # ---- MBanks (IMAP-мониторинг входящих платежей) ----
    # Включать ли запуск IMAP-мониторов при старте бота
    mbanks_enabled: bool = False
    # Минимальная и максимальная сумма пополнения через BLIK (PLN)
    mbanks_min_topup: int = 1
    mbanks_max_topup: int = 1000

    # IMAP-параметры (общие на все аккаунты)
    imap_reconnect_initial_delay: int = 5
    imap_reconnect_max_delay: int = 300
    imap_reconnect_max_failures: int = 10
    imap_idle_timeout: int = 1740  # ~29 мин (по RFC)
    imap_timeout: int = 120
    # При первом подключении (last_uid=0): сколько последних писем перечитать.
    # 0 — ничего, ставим якорь на последний UID. >0 — backfill последних N писем.
    imap_initial_backfill_count: int = 20

    # Дефолты для новых mbank-аккаунтов
    default_bank_daily_limit: float | None = None
    default_bank_limit_type: Literal["all", "matched"] = "all"

    # ---- AI ----
    ai_provider: Literal["groq", "openai", "claude"] = "groq"
    ai_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
