from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.app_chat import AppChat
from locales.texts import t


def _normalize_invite_url(raw: str | None) -> str | None:
    if not raw:
        return None
    s = str(raw).strip()
    if not s:
        return None
    if s.startswith(("http://", "https://", "tg://")):
        return s
    return f"https://{s.lstrip('/')}"


def main_menu_chat_link_buttons(
    chats: Sequence[AppChat] | None, language_code: str
) -> list[InlineKeyboardButton]:
    """Кнопки со ссылкой в чат (только если в БД есть invite URL)."""
    lang = language_code
    out: list[InlineKeyboardButton] = []
    if not chats:
        return out
    fallback = t("main_menu_chat_fallback", lang)
    if fallback == "main_menu_chat_fallback":
        fallback = "💬 Chat"
    for c in chats:
        url = _normalize_invite_url(c.chat_link)
        if not url:
            continue
        label = (c.button_title_for(lang) or fallback).strip() or fallback
        if len(label) > 64:
            label = label[:61] + "…"
        out.append(InlineKeyboardButton(text=label, url=url))
    return out


def main_menu_keyboard(
    language_code: str,
    user_id: int,
    admin_telegram_id: int | None,
    *,
    menu_chats: Sequence[AppChat] | None = None,
    show_game21: bool = True,
    show_slot: bool = True,
) -> InlineKeyboardMarkup:
    lang = language_code
    builder = InlineKeyboardBuilder()
    casino_text = t("btn_casino", lang)
    if casino_text == "btn_casino":
        casino_text = "🎰 Слот 🎰"

    builder.add(InlineKeyboardButton(text=t("btn_cabinet", lang), callback_data="menu:cabinet"))
    builder.add(InlineKeyboardButton(text=t("btn_topup", lang), callback_data="menu:topup"))
    builder.add(InlineKeyboardButton(text=t("btn_signup", lang), callback_data="menu:signup"))
    for chat_btn in main_menu_chat_link_buttons(menu_chats, lang):
        builder.add(chat_btn)
    if show_game21:
        builder.add(InlineKeyboardButton(text=t("btn_play_21_bot", lang), callback_data="menu:play21bot"))
    if show_slot:
        builder.add(InlineKeyboardButton(text=casino_text, callback_data="menu:casino"))

    if admin_telegram_id is not None and int(user_id) == int(admin_telegram_id):
        builder.add(InlineKeyboardButton(text=t("btn_admin", lang), callback_data="menu:admin"))

    builder.add(InlineKeyboardButton(text=t("btn_lang", lang), callback_data="menu:lang"))
    builder.adjust(1)
    return builder.as_markup()
