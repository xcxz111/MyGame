"""История партий шашек."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.app_chat import AppChat
from database.models.checkers import CheckersSession, CheckersSettings

_SETTINGS_ID = 1


async def get_settings(session: AsyncSession) -> CheckersSettings:
    row = await session.get(CheckersSettings, _SETTINGS_ID)
    if row is None:
        row = CheckersSettings(id=_SETTINGS_ID)
        session.add(row)
        await session.flush()
    return row


async def is_enabled(session: AsyncSession) -> bool:
    result = await session.execute(
        select(AppChat.id).where(AppChat.checkers_enabled == 1).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def set_enabled(session: AsyncSession, enabled: bool) -> None:
    s = await get_settings(session)
    s.enabled = 1 if enabled else 0
    await session.flush()


async def get_commission_percent(session: AsyncSession) -> Decimal:
    s = await get_settings(session)
    return s.commission_percent or Decimal("0.00")


async def set_commission_percent(session: AsyncSession, percent: Decimal) -> None:
    s = await get_settings(session)
    s.commission_percent = percent
    await session.flush()


async def set_rules(
    session: AsyncSession,
    text: str | None,
    *,
    translations: dict[str, str] | None = None,
) -> None:
    s = await get_settings(session)
    s.rules_text = text
    translations = translations or {}
    s.rules_text_en = translations.get("en")
    s.rules_text_uk = translations.get("uk")
    s.rules_text_pl = translations.get("pl")
    await session.flush()


def rules_for_lang(s: CheckersSettings, lang: str) -> str | None:
    if lang == "en":
        return s.rules_text_en or s.rules_text
    if lang == "uk":
        return s.rules_text_uk or s.rules_text
    if lang == "pl":
        return s.rules_text_pl or s.rules_text
    return s.rules_text


async def create_session(
    session: AsyncSession,
    *,
    chat_id: int,
    message_thread_id: int | None,
    player1_id: int,
    player2_id: int,
    bet_amount: Decimal,
    board: dict[str, str],
    commission_percent: Decimal = Decimal("0.00"),
    commission_amount: Decimal = Decimal("0.00"),
) -> int:
    row = CheckersSession(
        chat_id=int(chat_id),
        message_thread_id=int(message_thread_id) if message_thread_id is not None else None,
        player1_id=int(player1_id),
        player2_id=int(player2_id),
        bet_amount=bet_amount,
        commission_percent=commission_percent,
        commission_amount=commission_amount,
        status="active",
        board_json=json.dumps(board, ensure_ascii=False),
        moves_json="[]",
    )
    session.add(row)
    await session.flush()
    return int(row.id)


async def get_stats(session: AsyncSession) -> dict[str, Decimal | int]:
    row = (
        await session.execute(
            select(
                func.count(CheckersSession.id).label("total_games"),
                func.coalesce(func.sum(CheckersSession.commission_amount), 0).label(
                    "commission_sum"
                ),
            ).where(CheckersSession.status == "finish")
        )
    ).one()
    return {
        "total_games": int(row.total_games or 0),
        "commission_sum": Decimal(str(row.commission_sum or "0")),
    }


async def finish_session(
    session: AsyncSession,
    *,
    session_id: int,
    result: str,
    winner_id: int | None,
    board: dict[str, str],
    moves: list[dict[str, Any]],
) -> None:
    row = await session.get(CheckersSession, int(session_id))
    if row is None:
        return
    row.status = "finish"
    row.result = result
    row.winner_id = int(winner_id) if winner_id is not None else None
    if result == "draw":
        row.commission_amount = Decimal("0.00")
    row.board_json = json.dumps(board, ensure_ascii=False)
    row.moves_json = json.dumps(moves, ensure_ascii=False)
    row.finished_at = datetime.now(timezone.utc)
    await session.flush()
