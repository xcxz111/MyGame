from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import t


def topup_amount_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Клавиатура на этапе ввода суммы — отмена / главная."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


def topup_order_keyboard(order_id: str, language_code: str) -> InlineKeyboardMarkup:
    """Клавиатура для созданного ордера — отменить ордер / на главную."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("topup_btn_cancel_order", lang),
            callback_data=f"topup:cancel:{order_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()
