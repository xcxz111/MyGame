from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import t
from services.games.forum_thread import format_forum_topic_display_label
from services.games.busy import slot_busy_for_new_game


def _return_main_button(lang: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=t("btn_return_main", lang),
        callback_data="menu:main",
        style="primary",
    )


def play21_menu_keyboard(lang: str, *, bot_on: bool, pvp_on: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if bot_on:
        builder.row(
            InlineKeyboardButton(
                text=t("game21_btn_vs_bot", lang), callback_data="menu:play21bot:bot"
            )
        )
    if pvp_on:
        builder.row(
            InlineKeyboardButton(
                text=t("game21_btn_vs_user_chat", lang), callback_data="menu:play21bot:pvp"
            )
        )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def play21_busy_keyboard(lang: str, *, show_cancel_search: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if show_cancel_search:
        builder.row(
            InlineKeyboardButton(
                text=t("game21_btn_abort_session", lang),
                callback_data="menu:play21bot:cancel:active",
            )
        )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def play21_rules_back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def play21_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("game21_btn_yes", lang), callback_data="menu:play21bot:confirm:yes", style="success"),
        InlineKeyboardButton(text=t("game21_btn_no", lang), callback_data="menu:play21bot:confirm:no", style="danger"),
    )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def play21_pvp_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("game21_btn_yes", lang), callback_data="menu:play21bot:pvp:confirm:yes", style="success"),
        InlineKeyboardButton(text=t("game21_btn_no", lang), callback_data="menu:play21bot:pvp:confirm:no", style="danger"),
    )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def play21_pvp_chat_pick_keyboard(lang: str, chats: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cid, title in chats:
        builder.row(
            InlineKeyboardButton(
                text=title[:64],
                callback_data=f"menu:play21bot:pvp:chat:{cid}",
            )
        )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def play21_pvp_topic_pick_keyboard(
    lang: str,
    *,
    chat_id: int,
    topics: list[tuple[int, str]],
    include_general: bool = True,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    emoji_free = t("game21_pvp_topic_free", lang)
    emoji_busy = t("game21_pvp_topic_busy", lang)
    general_label = t("game21_pvp_topic_general", lang)
    if include_general:
        busy_g = slot_busy_for_new_game(chat_id, None)
        em = emoji_busy if busy_g else emoji_free
        builder.row(
            InlineKeyboardButton(
                text=f"{em} {general_label}",
                callback_data=f"menu:play21bot:pvp:th:{chat_id}:0",
            )
        )
    for tid, name in topics:
        busy = slot_busy_for_new_game(chat_id, tid)
        em = emoji_busy if busy else emoji_free
        label = format_forum_topic_display_label(lang, message_thread_id=tid, name=name)
        builder.row(
            InlineKeyboardButton(
                text=f"{em} {label}"[:64],
                callback_data=f"menu:play21bot:pvp:th:{chat_id}:{tid}",
            )
        )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def play21_pvp_accept_keyboard(lang: str, owner_user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("game21_pvp_btn_accept", lang),
                    callback_data=f"menu:play21bot:pvp:accept:{owner_user_id}",
                )
            ]
        ]
    )
