"""Репозиторий для таблицы `users`.

Подключим к хендлерам на следующем шаге.
"""

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.payment_log import PaymentLogMethod
from database.models.referral import ReferralReward
from database.models.user import User, UserRole, UserStatus
from database.repositories import fees as fees_repo
from database.repositories import payment_logs as payment_logs_repo
from database.repositories import user_levels as user_levels_repo


async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def find_user_by_id_or_username(session: AsyncSession, query: str) -> User | None:
    value = query.strip()
    if not value:
        return None
    if value.startswith("@"):
        value = value[1:]
    if value.isdigit():
        user = await session.get(User, int(value))
        if user is not None:
            return user
    result = await session.execute(
        select(User).where(func.lower(User.user_name) == value.lower()).limit(1)
    )
    return result.scalar_one_or_none()


async def upsert_user(
    session: AsyncSession,
    *,
    user_id: int,
    user_name: str | None = None,
    name: str | None = None,
    language_code: str | None = None,
) -> User:
    """Создаёт пользователя, если его нет; иначе обновляет переданные поля."""
    user = await session.get(User, user_id)
    if user is None:
        user = User(
            user_id=user_id,
            user_name=user_name,
            name=name,
            language_code=language_code,
            status=UserStatus.ACTIVE,
            role=UserRole.USER,
        )
        session.add(user)
    else:
        if user_name is not None:
            user.user_name = user_name
        if name is not None:
            user.name = name
        if language_code is not None:
            user.language_code = language_code
    await session.flush()
    return user


async def set_language(session: AsyncSession, user_id: int, language_code: str) -> None:
    user = await session.get(User, user_id)
    if user is not None:
        user.language_code = language_code
        await session.flush()


async def set_status(session: AsyncSession, user_id: int, status: int) -> None:
    user = await session.get(User, user_id)
    if user is not None:
        user.status = status
        await session.flush()


async def adjust_balance(
    session: AsyncSession, user_id: int, amount: Decimal, *, method: str
) -> Decimal | None:
    user = await session.get(User, int(user_id))
    if user is None:
        return None
    user.balance = (user.balance or Decimal("0")) + amount
    await session.flush()
    await payment_logs_repo.log(
        session,
        user_id=int(user.user_id),
        method=method,
        amount=amount,
        balance_after=user.balance,
    )
    return user.balance


async def set_withdraw_percent(
    session: AsyncSession, user_id: int, percent: Decimal | None
) -> None:
    user = await session.get(User, int(user_id))
    if user is not None:
        user.withdraw_percent = percent
        await session.flush()


async def set_referral_percent(
    session: AsyncSession, user_id: int, percent: Decimal | None
) -> None:
    user = await session.get(User, int(user_id))
    if user is not None:
        user.referral_percent = percent
        await session.flush()


async def effective_withdraw_percent(session: AsyncSession, user: User) -> Decimal:
    global_percent = await fees_repo.get_withdraw_percent(session)
    level_discount, _ = await user_levels_repo.get_bonus_totals(
        session, int(user.level or 1)
    )
    discount = (user.withdraw_percent or Decimal("0.00")) + level_discount
    effective = global_percent - discount
    return max(effective, Decimal("0.00")).quantize(Decimal("0.01"))


async def effective_referral_percent(session: AsyncSession, user: User) -> Decimal:
    global_percent = await fees_repo.get_referral_percent(session)
    _, level_bonus = await user_levels_repo.get_bonus_totals(session, int(user.level or 1))
    bonus = (user.referral_percent or Decimal("0.00")) + level_bonus
    return (global_percent + bonus).quantize(Decimal("0.01"))


async def set_role(session: AsyncSession, user_id: int, role: str) -> None:
    user = await session.get(User, user_id)
    if user is not None:
        user.role = role
        await session.flush()


async def set_referrer_if_empty(
    session: AsyncSession, user_id: int, referrer_id: int
) -> bool:
    if int(user_id) == int(referrer_id):
        return False
    user = await session.get(User, user_id)
    referrer = await session.get(User, referrer_id)
    if user is None or referrer is None or user.referrer_id is not None:
        return False
    user.referrer_id = int(referrer_id)
    await session.flush()
    return True


async def list_referrals_with_profit(
    session: AsyncSession, referrer_id: int
) -> list[tuple[User, Decimal]]:
    profit_sq = (
        select(
            ReferralReward.referral_id,
            func.coalesce(func.sum(ReferralReward.amount), 0).label("profit"),
        )
        .where(ReferralReward.referrer_id == int(referrer_id))
        .group_by(ReferralReward.referral_id)
        .subquery()
    )
    result = await session.execute(
        select(
            User,
            func.coalesce(profit_sq.c.profit, 0).label("profit"),
        )
        .outerjoin(
            profit_sq,
            profit_sq.c.referral_id == User.user_id,
        )
        .where(User.referrer_id == int(referrer_id))
        .order_by(User.created_at.desc())
    )
    return [(row[0], Decimal(str(row.profit or "0"))) for row in result.all()]


async def add_referral_reward(
    session: AsyncSession,
    *,
    referral_id: int,
    amount: Decimal,
    source: str | None = None,
) -> bool:
    referral = await session.get(User, int(referral_id))
    if referral is None or referral.referrer_id is None or amount <= 0:
        return False
    referrer = await session.get(User, int(referral.referrer_id))
    if referrer is None:
        return False
    referrer.balance = (referrer.balance or Decimal("0")) + amount
    session.add(
        ReferralReward(
            referrer_id=int(referrer.user_id),
            referral_id=int(referral.user_id),
            amount=amount,
            source=source,
        )
    )
    await session.flush()
    await payment_logs_repo.log(
        session,
        user_id=int(referrer.user_id),
        method=PaymentLogMethod.REFERRAL,
        amount=amount,
        balance_after=referrer.balance,
    )
    return True


async def award_referral_percent(
    session: AsyncSession,
    *,
    referral_id: int,
    base_amount: Decimal,
    source: str | None = None,
) -> Decimal:
    if base_amount <= 0:
        return Decimal("0.00")
    referral = await session.get(User, int(referral_id))
    if referral is None or referral.referrer_id is None:
        return Decimal("0.00")
    referrer = await session.get(User, int(referral.referrer_id))
    if referrer is None:
        return Decimal("0.00")
    percent = await effective_referral_percent(session, referrer)
    if percent <= 0:
        return Decimal("0.00")
    amount = (base_amount * percent / Decimal("100")).quantize(Decimal("0.01"))
    if amount <= 0:
        return Decimal("0.00")
    ok = await add_referral_reward(
        session,
        referral_id=referral_id,
        amount=amount,
        source=source,
    )
    return amount if ok else Decimal("0.00")
