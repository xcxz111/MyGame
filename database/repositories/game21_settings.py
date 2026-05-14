"""Singleton-настройки «21»."""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.app_chat import AppChat
from database.models.game21_settings import Game21Settings

_ROW_ID = 1


async def _row(session: AsyncSession) -> Game21Settings:
    r = await session.get(Game21Settings, _ROW_ID)
    if r is None:
        r = Game21Settings(id=_ROW_ID)
        session.add(r)
        await session.flush()
    return r


async def get_settings(session: AsyncSession) -> Game21Settings:
    return await _row(session)


async def any_game21_enabled(session: AsyncSession) -> bool:
    s = await _row(session)
    if bool(s.enabled_bot):
        return True
    count = await session.scalar(
        select(func.count())
        .select_from(AppChat)
        .where(AppChat.game21_users_enabled == 1)
    )
    return int(count or 0) > 0


async def set_enabled_bot(session: AsyncSession, enabled: bool) -> None:
    s = await _row(session)
    s.enabled = 1 if enabled else 0
    await session.flush()


async def set_enabled_users(session: AsyncSession, enabled: bool) -> None:
    s = await _row(session)
    s.enabled_users = 1 if enabled else 0
    await session.flush()


async def set_commission_bot(session: AsyncSession, percent: Decimal) -> None:
    s = await _row(session)
    s.commission_percent = percent
    await session.flush()


async def set_commission_users(session: AsyncSession, percent: Decimal) -> None:
    s = await _row(session)
    s.commission_users_percent = percent
    await session.flush()


async def set_rules_bot(
    session: AsyncSession,
    text: str | None,
    *,
    translations: dict[str, str] | None = None,
) -> None:
    s = await _row(session)
    s.rules_bot_text = text
    translations = translations or {}
    s.rules_bot_text_en = translations.get("en")
    s.rules_bot_text_uk = translations.get("uk")
    s.rules_bot_text_pl = translations.get("pl")
    await session.flush()


async def set_rules_users(
    session: AsyncSession,
    text: str | None,
    *,
    translations: dict[str, str] | None = None,
) -> None:
    s = await _row(session)
    s.rules_users_text = text
    translations = translations or {}
    s.rules_users_text_en = translations.get("en")
    s.rules_users_text_uk = translations.get("uk")
    s.rules_users_text_pl = translations.get("pl")
    await session.flush()


def rules_bot_for_lang(s: Game21Settings, lang: str) -> str | None:
    if lang == "en":
        return s.rules_bot_text_en or s.rules_bot_text
    if lang == "uk":
        return s.rules_bot_text_uk or s.rules_bot_text
    if lang == "pl":
        return s.rules_bot_text_pl or s.rules_bot_text
    return s.rules_bot_text


def rules_users_for_lang(s: Game21Settings, lang: str) -> str | None:
    if lang == "en":
        return s.rules_users_text_en or s.rules_users_text
    if lang == "uk":
        return s.rules_users_text_uk or s.rules_users_text
    if lang == "pl":
        return s.rules_users_text_pl or s.rules_users_text
    return s.rules_users_text
