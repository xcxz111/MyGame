"""Сборка приветственного сообщения над главным меню."""

from decimal import Decimal

from locales.texts import t


def _format_balance(balance: Decimal | float | int) -> str:
    """`0.00 → '0'`, `12.50 → '12.50'`, `12.00 → '12'`."""
    value = Decimal(balance)
    if value == value.to_integral_value():
        return str(int(value))
    return f"{value:.2f}"


def build_welcome_text(
    language_code: str,
    user_id: int,
    balance: Decimal | float | int = 0,
) -> str:
    """
    Текст вида:
        Добро пожаловать в бота для игр

        Ваш ID: 123
        Ваш баланс: 0 PLN
    """
    lang = language_code
    lines = [
        t("welcome_menu", lang),
        "",
        t("welcome_user_id", lang).format(user_id=user_id),
        t("welcome_balance", lang).format(balance=_format_balance(balance)),
    ]
    return "\n".join(lines)
