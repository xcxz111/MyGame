"""Запись и статистика игры «Слот»."""

from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.slot import SlotSettings, SlotSpin

_SETTINGS_ID = 1


async def get_settings(session: AsyncSession) -> SlotSettings:
    row = await session.get(SlotSettings, _SETTINGS_ID)
    if row is None:
        row = SlotSettings(id=_SETTINGS_ID, enabled=1)
        session.add(row)
        await session.flush()
    return row


async def is_enabled(session: AsyncSession) -> bool:
    s = await get_settings(session)
    return bool(s.enabled)


async def set_enabled(session: AsyncSession, enabled: bool) -> None:
    s = await get_settings(session)
    s.enabled = 1 if enabled else 0
    await session.flush()


async def set_rules(session: AsyncSession, text: str | None) -> None:
    s = await get_settings(session)
    s.rules_text = text
    await session.flush()


async def add_spin(
    session: AsyncSession,
    *,
    user_id: int,
    bet_amount: Decimal,
    slot_value: int,
    multiplier: Decimal,
    commission_percent: Decimal,
    payout: Decimal,
) -> None:
    bot_profit = (bet_amount - payout).quantize(Decimal("0.01"))
    session.add(
        SlotSpin(
            user_id=int(user_id),
            bet_amount=bet_amount,
            slot_value=int(slot_value),
            multiplier=multiplier,
            commission_percent=commission_percent,
            payout=payout,
            bot_profit=bot_profit,
        )
    )
    await session.flush()


async def get_stats(session: AsyncSession) -> dict[str, Decimal | int]:
    row = (
        await session.execute(
            select(
                func.count(SlotSpin.id).label("total_games"),
                func.count(func.distinct(SlotSpin.user_id)).label("unique_users"),
                func.coalesce(func.sum(SlotSpin.payout), 0).label("users_won_sum"),
                func.coalesce(func.sum(SlotSpin.bet_amount - SlotSpin.payout), 0).label(
                    "users_lost_sum"
                ),
                func.coalesce(
                    func.sum(
                        case((SlotSpin.bot_profit > 0, SlotSpin.bot_profit), else_=0)
                    ),
                    0,
                ).label("bot_won_sum"),
                func.coalesce(
                    func.sum(
                        case((SlotSpin.bot_profit < 0, -SlotSpin.bot_profit), else_=0)
                    ),
                    0,
                ).label("bot_lost_sum"),
                func.coalesce(func.sum(SlotSpin.bot_profit), 0).label("bot_profit_sum"),
            )
        )
    ).one()
    return {
        "total_games": int(row.total_games or 0),
        "unique_users": int(row.unique_users or 0),
        "users_won_sum": Decimal(str(row.users_won_sum or "0")).quantize(Decimal("0.01")),
        "users_lost_sum": Decimal(str(row.users_lost_sum or "0")).quantize(Decimal("0.01")),
        "bot_won_sum": Decimal(str(row.bot_won_sum or "0")).quantize(Decimal("0.01")),
        "bot_lost_sum": Decimal(str(row.bot_lost_sum or "0")).quantize(Decimal("0.01")),
        "bot_profit_sum": Decimal(str(row.bot_profit_sum or "0")).quantize(Decimal("0.01")),
    }
