"""История партий КМБ."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.kmb import KmbSession, KmbSettings

_SETTINGS_ID = 1


async def get_settings(session: AsyncSession) -> KmbSettings:
    row = await session.get(KmbSettings, _SETTINGS_ID)
    if row is None:
        row = KmbSettings(id=_SETTINGS_ID)
        session.add(row)
        await session.flush()
    return row


async def set_rules(session: AsyncSession, text: str | None) -> None:
    settings = await get_settings(session)
    settings.rules_text = text
    await session.flush()


async def create_session(
    session: AsyncSession,
    *,
    chat_id: int,
    message_thread_id: int | None,
    player1_id: int,
    player2_id: int,
    bet_amount: Decimal,
    target_wins: int = 1,
    commission_percent: Decimal = Decimal("0.00"),
    commission_amount: Decimal = Decimal("0.00"),
) -> int:
    row = KmbSession(
        chat_id=int(chat_id),
        message_thread_id=int(message_thread_id) if message_thread_id is not None else None,
        player1_id=int(player1_id),
        player2_id=int(player2_id),
        bet_amount=bet_amount,
        target_wins=max(1, min(10, int(target_wins))),
        commission_percent=commission_percent,
        commission_amount=commission_amount,
        status="active",
        moves_json="[]",
    )
    session.add(row)
    await session.flush()
    return int(row.id)


async def finish_session(
    session: AsyncSession,
    *,
    session_id: int,
    result: str,
    winner_id: int | None,
    moves: list[dict[str, Any]],
) -> None:
    row = await session.get(KmbSession, int(session_id))
    if row is None:
        return
    row.status = "finish"
    row.result = result
    row.winner_id = int(winner_id) if winner_id is not None else None
    if result == "draw":
        row.commission_amount = Decimal("0.00")
    row.moves_json = json.dumps(moves, ensure_ascii=False)
    row.finished_at = datetime.now(timezone.utc)
    await session.flush()


async def get_stats(session: AsyncSession) -> dict[str, Decimal | int]:
    totals = (
        await session.execute(
            select(
                func.count(KmbSession.id).label("total_games"),
                func.coalesce(func.sum(KmbSession.commission_amount), 0).label(
                    "commission_sum"
                ),
            ).where(KmbSession.status == "finish")
        )
    ).one()
    users_subq = union_all(
        select(KmbSession.player1_id.label("user_id")).where(KmbSession.status == "finish"),
        select(KmbSession.player2_id.label("user_id")).where(KmbSession.status == "finish"),
    ).subquery()
    unique_users = (
        await session.execute(select(func.count(func.distinct(users_subq.c.user_id))))
    ).scalar_one()
    return {
        "unique_users": int(unique_users or 0),
        "total_games": int(totals.total_games or 0),
        "commission_sum": Decimal(str(totals.commission_sum or "0")),
    }
