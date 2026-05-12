"""Сборка приветственного сообщения над главным меню."""

from locales.texts import t


def build_welcome_text(language_code: str, user_id: int, balance: float | int = 0) -> str:
    """
    Текст вида:
        Добро пожаловать в бота для игр

        Ваш ID: 123
        Ваш баланс: 0 PLN
    Баланс пока всегда 0 — подключим из БД позже.
    """
    lang = language_code
    lines = [
        t("welcome_menu", lang),
        "",
        t("welcome_user_id", lang).format(user_id=user_id),
        t("welcome_balance", lang).format(balance=balance),
    ]
    return "\n".join(lines)
