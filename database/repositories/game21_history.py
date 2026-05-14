"""Запись истории «21» в таблицы как в Game_bot (`game21_bot_sessions`, `game21_users_sessions`)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import case, delete, func, select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.models.game21_gamebot import (
    Game21BotRound,
    Game21BotSession,
    Game21UsersRound,
    Game21UsersSession,
)

logger = logging.getLogger(__name__)

SessionMaker = async_sessionmaker[AsyncSession]


async def create_bot_session_gb(
    session: AsyncSession,
    *,
    user_id: int,
    bet_amount: Decimal,
    commission_percent: Decimal,
) -> int:
    """Как `create_21_bot_session` в Game_bot: строка со status=active."""
    row = Game21BotSession(
        user_id=int(user_id),
        status="active",
        bet_amount=bet_amount,
        commission_percent=commission_percent,
        total_rounds=0,
        total_wins=0,
        total_losses=0,
        total_draws=0,
        net_result=Decimal("0"),
    )
    session.add(row)
    await session.flush()
    return int(row.id)


async def close_bot_session_gb(
    session: AsyncSession,
    *,
    session_id: int,
    result: str,
    winner: str,
    net_result: Decimal,
    round_number: int = 1,
    player_cards: str = "",
    bot_cards: str = "",
    player_points: int = 0,
    bot_points: int = 0,
) -> None:
    """Как `close_21_bot_session` в Game_bot."""
    row = await session.get(Game21BotSession, int(session_id))
    if row is None:
        logger.warning("game21_history: close_bot_session_gb missing id=%s", session_id)
        return
    wins = 1 if result == "win" else 0
    losses = 1 if result == "lose" else 0
    draws = 1 if result == "draw" else 0
    row.status = "finish"
    row.round_number = int(round_number)
    row.player_cards = player_cards or ""
    row.bot_cards = bot_cards or ""
    row.player_points = int(player_points)
    row.bot_points = int(bot_points)
    row.result = result
    row.winner = winner
    row.net_result = net_result
    row.total_rounds = 1
    row.total_wins = wins
    row.total_losses = losses
    row.total_draws = draws
    row.updated_at = datetime.now(timezone.utc)
    await _replace_bot_round_gb(
        session,
        session_id=int(session_id),
        round_number=int(round_number),
        player_cards=player_cards,
        bot_cards=bot_cards,
        player_points=int(player_points),
        bot_points=int(bot_points),
        result=result,
        winner=winner,
        bet_amount=row.bet_amount,
        commission_percent=row.commission_percent,
        net_result=net_result,
    )


async def cancel_bot_session_gb(session: AsyncSession, *, session_id: int) -> None:
    row = await session.get(Game21BotSession, int(session_id))
    if row is None:
        return
    row.status = "cancelled"
    row.updated_at = datetime.now(timezone.utc)


async def _replace_bot_round_gb(
    session: AsyncSession,
    *,
    session_id: int,
    round_number: int,
    player_cards: str,
    bot_cards: str,
    player_points: int,
    bot_points: int,
    result: str,
    winner: str,
    bet_amount: Decimal,
    commission_percent: Decimal,
    net_result: Decimal,
) -> None:
    """Записать итог раунда против бота в `game21_bot_rounds` без дублей."""
    await session.execute(
        delete(Game21BotRound).where(
            Game21BotRound.session_id == int(session_id),
            Game21BotRound.round_number == int(round_number),
        )
    )
    session.add(
        Game21BotRound(
            session_id=int(session_id),
            round_number=int(round_number),
            player_cards=player_cards or "",
            bot_cards=bot_cards or "",
            player_points=int(player_points),
            bot_points=int(bot_points),
            result=result,
            winner=winner,
            bet_amount=bet_amount,
            commission_percent=commission_percent,
            net_result=net_result,
        )
    )
    await session.flush()


async def _replace_users_round_events_gb(
    session: AsyncSession,
    *,
    session_id: int,
    events: list | None,
) -> None:
    """Разложить `round_events_json` в legacy-таблицу `game21_users_rounds`."""
    await session.execute(
        delete(Game21UsersRound).where(Game21UsersRound.session_id == int(session_id))
    )
    for ev in events or []:
        try:
            total_raw = ev.get("total_after")
            session.add(
                Game21UsersRound(
                    session_id=int(session_id),
                    phase=str(ev.get("phase") or "turn"),
                    user_id=int(ev.get("user_id") or 0),
                    throw_order=int(ev.get("throw_order") or 0),
                    value=int(ev.get("value") or 0),
                    total_after=int(total_raw) if total_raw is not None else None,
                )
            )
        except Exception:
            logger.exception("game21_history: bad round event session_id=%s event=%r", session_id, ev)
    await session.flush()


async def upsert_users_session_gb(
    session: AsyncSession,
    *,
    chat_id: int | None,
    pvp_session_token: int | None,
    player1_id: int,
    player2_id: int,
    bet_amount: Decimal,
    commission_percent: Decimal,
    commission_amount: Decimal,
    result: str,
    winner_id: int | None,
    round_events: list | None,
) -> None:
    """Как `add_21_users_game` в Game_bot (идемпотентность по pvp_session_token)."""
    events_json: str | None
    try:
        events_json = json.dumps(round_events or [], ensure_ascii=False)
    except Exception:
        events_json = None
    vals = dict(
        chat_id=int(chat_id) if chat_id is not None else None,
        pvp_session_token=int(pvp_session_token) if pvp_session_token is not None else None,
        player1_id=int(player1_id),
        player2_id=int(player2_id),
        bet_amount=bet_amount,
        commission_percent=commission_percent,
        commission_amount=commission_amount,
        result=str(result or "draw"),
        winner_id=int(winner_id) if winner_id is not None else None,
        round_events_json=events_json,
    )
    try:
        session_id: int | None = None
        if vals["pvp_session_token"] is not None:
            stmt = mysql_insert(Game21UsersSession).values(**vals)
            stmt = stmt.on_duplicate_key_update(
                chat_id=stmt.inserted.chat_id,
                player1_id=stmt.inserted.player1_id,
                player2_id=stmt.inserted.player2_id,
                bet_amount=stmt.inserted.bet_amount,
                commission_percent=stmt.inserted.commission_percent,
                commission_amount=stmt.inserted.commission_amount,
                result=stmt.inserted.result,
                winner_id=stmt.inserted.winner_id,
                round_events_json=stmt.inserted.round_events_json,
            )
            await session.execute(stmt)
            session_id = await session.scalar(
                select(Game21UsersSession.id).where(
                    Game21UsersSession.pvp_session_token == vals["pvp_session_token"]
                )
            )
        else:
            row = Game21UsersSession(**vals)
            session.add(row)
            await session.flush()
            session_id = int(row.id)
        if session_id:
            await _replace_users_round_events_gb(
                session,
                session_id=int(session_id),
                events=round_events,
            )
    except Exception:
        logger.exception("game21_history: upsert_users_session_gb failed token=%s", pvp_session_token)


async def get_admin_stats(session: AsyncSession) -> dict[str, Decimal | int]:
    bot_row = (
        await session.execute(
            select(
                func.count(Game21BotSession.id).label("bot_total"),
                func.coalesce(
                    func.sum(case((Game21BotSession.result == "lose", 1), else_=0)),
                    0,
                ).label("bot_won_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (Game21BotSession.result == "lose", -Game21BotSession.net_result),
                            else_=0,
                        )
                    ),
                    0,
                ).label("bot_won_sum"),
                func.coalesce(
                    func.sum(case((Game21BotSession.result == "win", 1), else_=0)),
                    0,
                ).label("bot_lost_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (Game21BotSession.result == "win", Game21BotSession.net_result),
                            else_=0,
                        )
                    ),
                    0,
                ).label("bot_lost_sum"),
                func.coalesce(
                    func.sum(case((Game21BotSession.result == "draw", 1), else_=0)),
                    0,
                ).label("bot_draw_count"),
                func.coalesce(func.sum(-Game21BotSession.net_result), 0).label("bot_profit_sum"),
            ).where(Game21BotSession.status == "finish")
        )
    ).one()
    pvp_row = (
        await session.execute(
            select(
                func.count(Game21UsersSession.id).label("pvp_total"),
                func.coalesce(func.sum(Game21UsersSession.commission_amount), 0).label(
                    "pvp_commission_sum"
                ),
            )
        )
    ).one()
    return {
        "bot_total": int(bot_row.bot_total or 0),
        "bot_won_count": int(bot_row.bot_won_count or 0),
        "bot_won_sum": Decimal(str(bot_row.bot_won_sum or "0")).quantize(Decimal("0.01")),
        "bot_lost_count": int(bot_row.bot_lost_count or 0),
        "bot_lost_sum": Decimal(str(bot_row.bot_lost_sum or "0")).quantize(Decimal("0.01")),
        "bot_draw_count": int(bot_row.bot_draw_count or 0),
        "bot_profit_sum": Decimal(str(bot_row.bot_profit_sum or "0")).quantize(Decimal("0.01")),
        "pvp_total": int(pvp_row.pvp_total or 0),
        "pvp_commission_sum": Decimal(str(pvp_row.pvp_commission_sum or "0")).quantize(
            Decimal("0.01")
        ),
    }
