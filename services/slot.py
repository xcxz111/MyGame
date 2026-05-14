"""Логика игры «Слот» (Telegram dice 🎰)."""

from decimal import Decimal, ROUND_HALF_UP


def decode_line(slot_value: int) -> tuple[int, int, int]:
    """Декодирование значения 🎰 (1..64) в три барабана по 4 символа."""
    n = max(1, min(64, int(slot_value or 1))) - 1
    return (n // 16) % 4, (n // 4) % 4, n % 4


def multiplier_for(slot_value: int) -> Decimal:
    reels = decode_line(slot_value)
    uniq = len(set(reels))
    if uniq == 1:
        return Decimal("4.0")
    if uniq == 2:
        return Decimal("1.1")
    return Decimal("0")


def payout_for(bet: Decimal, multiplier: Decimal, commission_percent: Decimal) -> Decimal:
    if multiplier <= 0:
        return Decimal("0.00")
    gross = bet * multiplier
    payout = gross * (Decimal("1") - commission_percent / Decimal("100"))
    return payout.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fmt_money(v: Decimal) -> str:
    q = Decimal(str(v)).quantize(Decimal("0.01"))
    if q == q.to_integral_value():
        return str(int(q))
    return f"{q:f}".rstrip("0").rstrip(".")


def fmt_multiplier(v: Decimal) -> str:
    if v == v.to_integral_value():
        return str(int(v))
    return f"{v:f}".rstrip("0").rstrip(".")
