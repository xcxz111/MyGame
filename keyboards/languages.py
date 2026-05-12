from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import DEFAULT_LANG, LANG_NAMES, t


def language_keyboard(
    with_back_to_main: bool = False,
    nav_lang: str = DEFAULT_LANG,
) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора языка. Если `with_back_to_main=True`, добавляется
    кнопка возврата в главное меню (callback_data='menu:main').
    Подпись этой кнопки локализуется по `nav_lang`.
    """
    builder = InlineKeyboardBuilder()
    for code, label in LANG_NAMES.items():
        builder.add(InlineKeyboardButton(text=label, callback_data=f"lang:{code}"))
    if with_back_to_main:
        builder.add(
            InlineKeyboardButton(text=t("btn_main", nav_lang), callback_data="menu:main")
        )
    builder.adjust(1)
    return builder.as_markup()
