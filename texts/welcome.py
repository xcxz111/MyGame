"""Сборка приветственного сообщения над главным меню."""

from decimal import Decimal

from locales.texts import t


def _format_balance(balance: Decimal | float | int | None) -> str:
    """Как в личном кабинете: `0.00 → '0'`, `173.10 → '173.1'`."""
    if balance is None:
        return "0"
    value = Decimal(balance)
    try:
        if value == value.to_integral_value():
            return str(int(value))
        return f"{value:f}".rstrip("0").rstrip(".")
    except Exception:
        return str(value)


def build_welcome_text(
    language_code: str,
    user_id: int,
    balance: Decimal | float | int = 0,
    level: int = 0,
) -> str:
    """
    Текст вида:
        Добро пожаловать в бота для игр

        Ваш ID: 123
        ⭐ Уровень: 0
        💰 Баланс: 173.1 PLN
    """
    lang = language_code
    lvl = int(level or 0)
    bal = _format_balance(balance)
    lines = [
        t("welcome_menu", lang),
        "",
        t("welcome_user_id", lang).format(user_id=user_id),
        t("cabinet_level", lang).format(level=lvl),
        t("cabinet_balance", lang).format(balance=bal),
    ]
    return "\n".join(lines)
