"""Форматирование для сообщений игры 21."""

from __future__ import annotations

import html
from decimal import Decimal


def name_link(user_id: int, name: str) -> str:
    n = (name or "").strip() or str(user_id)
    return f'<a href="tg://user?id={user_id}">{html.escape(n)}</a>'


def fmt_money(value: Decimal | float | int) -> str:
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    s = f"{d:.2f}"
    return s.rstrip("0").rstrip(".")


def possible_win_pvp(bet: Decimal, commission_percent: Decimal) -> Decimal:
    gross = bet * 2
    return (gross * (Decimal("1") - commission_percent / Decimal("100"))).quantize(
        Decimal("0.01")
    )


def pvp_status_line(name_link: str, total: int | None) -> str:
    if total is None:
        return name_link
    if int(total) == 21:
        return f"{name_link} результат: 21 ОЧКО!!!"
    return f"{name_link} результат: {int(total)}"
