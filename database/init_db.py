"""Создаёт таблицы по моделям SQLAlchemy.

Использование:
    python -m database.init_db

База данных (`mysql_database` из .env) должна существовать.
Если её нет — создайте вручную:
    CREATE DATABASE mygame CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"""

import asyncio
import logging

from sqlalchemy import inspect, text

from database.base import Base
from database.engine import get_engine
from database.models import (  # noqa: F401  — регистрирует модели в metadata
    AppChat,
    AppChatAllowedTopic,
    CheckersSession,
    CheckersSettings,
    Fee,
    ForumTopic,
    Game,
    Game21BotRound,
    Game21BotSession,
    Game21Settings,
    Game21UsersRound,
    Game21UsersSession,
    GameParticipant,
    KmbSession,
    KmbSettings,
    MBankAccount,
    MBankOrder,
    MBankRawEmail,
    MBankTransaction,
    PaymentLog,
    Prize,
    ReferralReward,
    SlotSettings,
    SlotSpin,
    Throw,
    User,
    UserLevel,
    Withdrawal,
)

logger = logging.getLogger(__name__)


def _migrate_game21_to_game_bot_schema(connection) -> None:
    """Убирает legacy-таблицы матчей; настройки всегда в `game21_settings` (переименование из `game21_bot_settings` при необходимости)."""
    insp = inspect(connection)
    tables = set(insp.get_table_names())
    if "game21_match_moves" in tables:
        connection.execute(text("DROP TABLE IF EXISTS `game21_match_moves`"))
        tables.discard("game21_match_moves")
    if "game21_matches" in tables:
        connection.execute(text("DROP TABLE IF EXISTS `game21_matches`"))
        tables.discard("game21_matches")

    if "game21_bot_settings" in tables and "game21_settings" not in tables:
        connection.execute(text("RENAME TABLE `game21_bot_settings` TO `game21_settings`"))

    insp = inspect(connection)
    if "game21_settings" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("game21_settings")}
    if "enabled_bot" in cols:
        connection.execute(
            text(
                "ALTER TABLE `game21_settings` CHANGE COLUMN `enabled_bot` `enabled` "
                "SMALLINT NOT NULL DEFAULT 0"
            )
        )
    if "commission_bot_percent" in cols:
        connection.execute(
            text(
                "ALTER TABLE `game21_settings` CHANGE COLUMN `commission_bot_percent` "
                "`commission_percent` DECIMAL(5,2) NOT NULL DEFAULT 0.00"
            )
        )
    insp = inspect(connection)
    cols = {c["name"] for c in insp.get_columns("game21_settings")}
    for col, ddl in (
        ("rules_bot_text", "MEDIUMTEXT NULL"),
        ("rules_bot_text_en", "MEDIUMTEXT NULL"),
        ("rules_bot_text_uk", "MEDIUMTEXT NULL"),
        ("rules_bot_text_pl", "MEDIUMTEXT NULL"),
        ("rules_users_text", "MEDIUMTEXT NULL"),
        ("rules_users_text_en", "MEDIUMTEXT NULL"),
        ("rules_users_text_uk", "MEDIUMTEXT NULL"),
        ("rules_users_text_pl", "MEDIUMTEXT NULL"),
    ):
        if col not in cols:
            connection.execute(text(f"ALTER TABLE `game21_settings` ADD COLUMN `{col}` {ddl}"))


def _ensure_app_chats_button_titles(connection) -> None:
    """Добавляет колонки подписей кнопки по языкам в уже существующую таблицу `app_chats`."""
    insp = inspect(connection)
    if "app_chats" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("app_chats")}
    for col, ddl in (
        ("button_title_ru", "VARCHAR(200) NULL"),
        ("button_title_en", "VARCHAR(200) NULL"),
        ("button_title_uk", "VARCHAR(200) NULL"),
        ("button_title_pl", "VARCHAR(200) NULL"),
    ):
        if col not in cols:
            connection.execute(text(f"ALTER TABLE `app_chats` ADD COLUMN `{col}` {ddl}"))
            cols.add(col)


def _ensure_fees_columns(connection) -> None:
    insp = inspect(connection)
    if "fees" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("fees")}
    if "slot_percent" not in cols:
        connection.execute(
            text(
                "ALTER TABLE `fees` ADD COLUMN `slot_percent` DECIMAL(5,2) NOT NULL "
                "DEFAULT 0.00 COMMENT 'Комиссия игры Слот, в процентах от выплаты'"
            )
        )
    if "kmb_percent" not in cols:
        connection.execute(
            text(
                "ALTER TABLE `fees` ADD COLUMN `kmb_percent` DECIMAL(5,2) NOT NULL "
                "DEFAULT 0.00 COMMENT 'Комиссия игры КМБ, в процентах от выплаты'"
            )
        )
    if "referral_percent" not in cols:
        connection.execute(
            text(
                "ALTER TABLE `fees` ADD COLUMN `referral_percent` DECIMAL(5,2) NOT NULL "
                "DEFAULT 0.00 COMMENT 'Процент реферального начисления'"
            )
        )


def _ensure_users_referrer_id(connection) -> None:
    insp = inspect(connection)
    if "users" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("users")}
    for col, ddl in (
        (
            "level",
            "SMALLINT NOT NULL DEFAULT 0 COMMENT 'Текущий уровень пользователя'",
        ),
        (
            "level_win_bet_sum",
            "DECIMAL(14,2) NOT NULL DEFAULT 0.00 COMMENT 'Сумма выигранных ставок для прогресса уровня'",
        ),
        (
            "referrer_id",
            "BIGINT NULL COMMENT 'Telegram user_id пригласившего пользователя'",
        ),
        (
            "withdraw_percent",
            "DECIMAL(5,2) NULL COMMENT 'Персональная скидка к комиссии вывода, NULL = без скидки'",
        ),
        (
            "referral_percent",
            "DECIMAL(5,2) NULL COMMENT 'Персональная надбавка к реферальному проценту, NULL = без надбавки'",
        ),
    ):
        if col not in cols:
            connection.execute(text(f"ALTER TABLE `users` ADD COLUMN `{col}` {ddl}"))
    if "level" in cols:
        connection.execute(
            text(
                "ALTER TABLE `users` MODIFY COLUMN `level` SMALLINT NOT NULL "
                "DEFAULT 0 COMMENT 'Текущий уровень пользователя'"
            )
        )


def _seed_user_levels(connection) -> None:
    insp = inspect(connection)
    if "user_levels" not in insp.get_table_names():
        return
    has_level_zero = connection.execute(
        text("SELECT 1 FROM `user_levels` WHERE `level` = 0 LIMIT 1")
    ).first()
    if has_level_zero is None:
        connection.execute(text("UPDATE `user_levels` SET `level` = `level` - 1000"))
        connection.execute(text("UPDATE `user_levels` SET `level` = `level` + 999"))
        for level in range(1, 10):
            connection.execute(
                text(
                    "UPDATE `user_levels` SET `title` = :new_title "
                    "WHERE `level` = :level AND `title` = :old_title"
                ),
                {
                    "level": level,
                    "new_title": f"Уровень {level}",
                    "old_title": f"Уровень {level + 1}",
                },
            )
        if "users" in insp.get_table_names():
            connection.execute(
                text(
                    "UPDATE `users` SET `level` = CASE "
                    "WHEN `level` > 0 THEN `level` - 1 ELSE 0 END"
                )
            )

    rows = [
        (0, "Начальный уровень", "0.00", "0.00", "0.00", "0.00"),
        (1, "Уровень 1", "100.00", "10.00", "0.00", "0.00"),
        (2, "Уровень 2", "1000.00", "30.00", "1.00", "0.00"),
        (3, "Уровень 3", "5000.00", "50.00", "0.00", "0.00"),
        (4, "Уровень 4", "10000.00", "100.00", "1.00", "1.00"),
        (5, "Уровень 5", "25000.00", "0.00", "0.00", "0.00"),
        (6, "Уровень 6", "50000.00", "0.00", "0.00", "0.00"),
        (7, "Уровень 7", "100000.00", "0.00", "0.00", "0.00"),
        (8, "Уровень 8", "250000.00", "0.00", "0.00", "0.00"),
        (9, "Уровень 9", "500000.00", "0.00", "0.00", "0.00"),
        (10, "Уровень 10", "1000000.00", "0.00", "0.00", "0.00"),
    ]
    for level, title, required, reward, withdraw_discount, referral_bonus in rows:
        connection.execute(
            text(
                "INSERT IGNORE INTO `user_levels` "
                "(`level`, `title`, `required_win_bet_sum`, `balance_reward`, "
                "`withdraw_discount_percent`, `referral_bonus_percent`, `active`) "
                "VALUES (:level, :title, :required, :reward, :withdraw_discount, :referral_bonus, 1)"
            ),
            {
                "level": level,
                "title": title,
                "required": required,
                "reward": reward,
                "withdraw_discount": withdraw_discount,
                "referral_bonus": referral_bonus,
            },
        )


def _ensure_checkers_columns(connection) -> None:
    insp = inspect(connection)
    tables = set(insp.get_table_names())
    if "checkers_sessions" in tables:
        cols = {c["name"] for c in insp.get_columns("checkers_sessions")}
        for col, ddl in (
            ("commission_percent", "DECIMAL(5,2) NOT NULL DEFAULT 0.00"),
            ("commission_amount", "DECIMAL(10,2) NOT NULL DEFAULT 0.00"),
        ):
            if col not in cols:
                connection.execute(text(f"ALTER TABLE `checkers_sessions` ADD COLUMN `{col}` {ddl}"))
    if "checkers_settings" in tables:
        cols = {c["name"] for c in insp.get_columns("checkers_settings")}
        for col, ddl in (
            ("enabled", "SMALLINT NOT NULL DEFAULT 1"),
            ("commission_percent", "DECIMAL(5,2) NOT NULL DEFAULT 0.00"),
            ("rules_text_en", "MEDIUMTEXT NULL"),
            ("rules_text_uk", "MEDIUMTEXT NULL"),
            ("rules_text_pl", "MEDIUMTEXT NULL"),
        ):
            if col not in cols:
                connection.execute(text(f"ALTER TABLE `checkers_settings` ADD COLUMN `{col}` {ddl}"))


def _ensure_kmb_columns(connection) -> None:
    insp = inspect(connection)
    if "kmb_sessions" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("kmb_sessions")}
    if "target_wins" not in cols:
        connection.execute(
            text(
                "ALTER TABLE `kmb_sessions` ADD COLUMN `target_wins` INT NOT NULL "
                "DEFAULT 1 COMMENT 'Игра до N побед'"
            )
        )


def _ensure_games_message_thread_id(connection) -> None:
    insp = inspect(connection)
    if "games" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("games")}
    if "message_thread_id" not in cols:
        connection.execute(
            text(
                "ALTER TABLE `games` ADD COLUMN `message_thread_id` INT NULL "
                "COMMENT 'Тема форума (message_thread_id)'"
            )
        )


def _ensure_games_announcement_general(connection) -> None:
    insp = inspect(connection)
    if "games" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("games")}
    if "announcement_message_id_general" not in cols:
        connection.execute(
            text(
                "ALTER TABLE `games` ADD COLUMN `announcement_message_id_general` BIGINT NULL "
                "COMMENT 'Дубль анонса в общем чате форума'"
            )
        )


def _ensure_app_chats_game21_users(connection) -> None:
    insp = inspect(connection)
    if "app_chats" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("app_chats")}
    if "game21_users_enabled" not in cols:
        connection.execute(
            text(
                "ALTER TABLE `app_chats` ADD COLUMN `game21_users_enabled` SMALLINT NOT NULL "
                "DEFAULT 0 COMMENT 'PvP 21 в чате'"
            )
        )


def _ensure_app_chats_checkers_enabled(connection) -> None:
    insp = inspect(connection)
    if "app_chats" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("app_chats")}
    if "checkers_enabled" not in cols:
        connection.execute(
            text(
                "ALTER TABLE `app_chats` ADD COLUMN `checkers_enabled` SMALLINT NOT NULL "
                "DEFAULT 0 COMMENT 'PvP шашки в чате'"
            )
        )


async def init_db() -> None:
    """Создаёт таблицы по моделям. Движок не закрывает — он переиспользуется ботом."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(_migrate_game21_to_game_bot_schema)
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_fees_columns)
        await conn.run_sync(_ensure_users_referrer_id)
        await conn.run_sync(_seed_user_levels)
        await conn.run_sync(_ensure_checkers_columns)
        await conn.run_sync(_ensure_kmb_columns)
        await conn.run_sync(_ensure_app_chats_button_titles)
        await conn.run_sync(_ensure_app_chats_game21_users)
        await conn.run_sync(_ensure_app_chats_checkers_enabled)
        await conn.run_sync(_ensure_games_message_thread_id)
        await conn.run_sync(_ensure_games_announcement_general)


async def _standalone() -> None:
    """Точка входа для запуска отдельно (`python -m database.init_db`)."""
    try:
        await init_db()
    finally:
        await get_engine().dispose()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.info("Initializing database…")
    asyncio.run(_standalone())
    logger.info("Done.")


if __name__ == "__main__":
    main()
