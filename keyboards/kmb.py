from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import t


def _return_main_button(lang: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=t("btn_return_main", lang),
        callback_data="menu:main",
        style="primary",
    )


def kmb_chat_pick_keyboard(lang: str, chats: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cid, title in chats:
        builder.row(InlineKeyboardButton(text=title[:64], callback_data=f"menu:kmb:chat:{cid}"))
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def kmb_topic_pick_keyboard(
    lang: str,
    *,
    chat_id: int,
    topics: list[tuple[int, str]],
    busy: set[int | None],
    include_general: bool = True,
    back_callback_data: str = "menu:kmb",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if include_general:
        em = "🔴" if None in busy else "🟢"
        builder.row(
            InlineKeyboardButton(text=f"{em} Chat", callback_data=f"menu:kmb:th:{chat_id}:0")
        )
    for tid, name in topics:
        em = "🔴" if tid in busy else "🟢"
        builder.row(
            InlineKeyboardButton(text=f"{em} {name}"[:64], callback_data=f"menu:kmb:th:{chat_id}:{tid}")
        )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def kmb_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("game21_btn_yes", lang), callback_data="menu:kmb:confirm:yes", style="success"),
        InlineKeyboardButton(text=t("game21_btn_no", lang), callback_data="menu:kmb:confirm:no", style="danger"),
    )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def kmb_accept_keyboard(lang: str, owner_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("kmb_btn_accept", lang),
                    callback_data=f"menu:kmb:accept:{owner_id}",
                )
            ]
        ]
    )


def kmb_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[_return_main_button(lang)]]
    )


def kmb_busy_keyboard(lang: str, *, show_cancel_search: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if show_cancel_search:
        builder.row(
            InlineKeyboardButton(
                text=t("game21_btn_abort_session", lang),
                callback_data="menu:kmb:cancel:active",
            )
        )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def kmb_choice_keyboard(token: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👊", callback_data=f"kmb:pick:{token}:rock"),
                InlineKeyboardButton(text="✌️", callback_data=f"kmb:pick:{token}:scissors"),
                InlineKeyboardButton(text="🤚", callback_data=f"kmb:pick:{token}:paper"),
            ]
        ]
    )
