from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import t


def cabinet_menu_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Клавиатура личного кабинета."""
    lang = language_code
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=t("btn_topup", lang), callback_data="menu:topup"))
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()
