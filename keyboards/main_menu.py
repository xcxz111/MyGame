from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import t


def main_menu_keyboard(language_code: str, user_id: int, admin_telegram_id: int | None) -> InlineKeyboardMarkup:
    lang = language_code
    builder = InlineKeyboardBuilder()
    casino_text = t("btn_casino", lang)
    if casino_text == "btn_casino":
        casino_text = "🎰 Казино 🎰"

    builder.add(InlineKeyboardButton(text=t("btn_cabinet", lang), callback_data="menu:cabinet"))
    builder.add(InlineKeyboardButton(text=t("btn_signup", lang), callback_data="menu:signup"))
    builder.add(InlineKeyboardButton(text=t("btn_play_21_bot", lang), callback_data="menu:play21bot"))
    builder.add(InlineKeyboardButton(text=casino_text, callback_data="menu:casino"))

    if admin_telegram_id is not None and int(user_id) == int(admin_telegram_id):
        builder.add(InlineKeyboardButton(text=t("btn_admin", lang), callback_data="menu:admin"))

    builder.add(InlineKeyboardButton(text=t("btn_lang", lang), callback_data="menu:lang"))
    builder.adjust(1)
    return builder.as_markup()
