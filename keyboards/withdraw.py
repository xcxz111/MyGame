from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import t


def withdraw_amount_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Кнопки на этапе ввода суммы — Назад / Главная."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:cabinet", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def withdraw_confirm_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Кнопки Да/Нет в превью вывода."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("withdraw_btn_yes", lang),
            callback_data="withdraw:confirm_yes",
        ),
        InlineKeyboardButton(
            text=t("withdraw_btn_no", lang),
            callback_data="withdraw:confirm_no",
        ),
    )
    return builder.as_markup()


def withdraw_cancel_confirm_keyboard(
    withdrawal_id: int, language_code: str
) -> InlineKeyboardMarkup:
    """Подтверждение отмены пользователем своей заявки на вывод."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("withdraw_btn_yes", lang),
            callback_data=f"withdraw:cancel_yes:{withdrawal_id}",
        ),
        InlineKeyboardButton(
            text=t("withdraw_btn_no", lang),
            callback_data="menu:cabinet",
        ),
    )
    return builder.as_markup()


def admin_withdraw_keyboard(
    withdrawal_id: int, language_code: str
) -> InlineKeyboardMarkup:
    """Кнопка 'Принять' под сообщением в админ-чате."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("withdraw_admin_btn_approve", lang),
            callback_data=f"admin:withdraw:approve:{withdrawal_id}",
        )
    )
    return builder.as_markup()
