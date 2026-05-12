from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import LANG_NAMES


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, label in LANG_NAMES.items():
        builder.add(InlineKeyboardButton(text=label, callback_data=f"lang:{code}"))
    builder.adjust(1)
    return builder.as_markup()
