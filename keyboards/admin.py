from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import t


def admin_menu_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Главное меню админки."""
    lang = language_code
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=t("admin_btn_games", lang), callback_data="admin:games"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_21", lang), callback_data="admin:21"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_casino", lang), callback_data="admin:casino"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_checkers", lang), callback_data="admin:checkers"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_kmb", lang), callback_data="admin:kmb"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_stats", lang), callback_data="admin:stats"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_bot_settings", lang), callback_data="admin:settings"))
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


def admin_bot_settings_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Подменю 'Настройки бота'."""
    lang = language_code
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=t("admin_btn_payments", lang), callback_data="admin:settings:payments"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_fees", lang), callback_data="admin:settings:fees"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_chats", lang), callback_data="admin:settings:chats"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_forbidden_words", lang), callback_data="admin:settings:words"))
    builder.row(InlineKeyboardButton(text=t("admin_btn_admins", lang), callback_data="admin:settings:admins"))
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:admin"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


def admin_fees_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Подменю 'Настройка комиссий'."""
    lang = language_code
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=t("admin_btn_withdraw_fee", lang),
            callback_data="admin:fees:withdraw",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:settings"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()
