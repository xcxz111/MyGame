"""Клавиатуры для подключённых чатов в админ-панели."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.app_chat import AppChat
from locales.texts import t


def admin_chats_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Экран «Подключённые чаты»: добавить, удалить, назад в настройки бота, главная."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_chats_btn_add", lang),
            callback_data="admin:chats:add",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_chats_btn_delete", lang),
            callback_data="admin:chats:delete",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_chats_btn_game_topics", lang),
            callback_data="admin:chats:topics",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:settings", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def admin_chats_delete_list_keyboard(
    language_code: str, chats: list[tuple[AppChat, str | None]]
) -> InlineKeyboardMarkup:
    """Список чатов для удаления. chats: [(chat, resolved_title|None), ...]."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    for chat, title in chats:
        label = title or str(chat.chat_id)
        builder.row(
            InlineKeyboardButton(
                text=label, callback_data=f"admin:chats:delete:ask:{chat.chat_id}"
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data="admin:settings:chats",
            style="primary",
        ),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def admin_chats_delete_confirm_keyboard(
    language_code: str, chat_id: int
) -> InlineKeyboardMarkup:
    """Подтверждение удаления чата."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("withdraw_btn_yes", lang),
            callback_data=f"admin:chats:delete:yes:{chat_id}",
            style="success",
        ),
        InlineKeyboardButton(
            text=t("withdraw_btn_no", lang),
            callback_data="admin:settings:chats",
            style="danger",
        ),
    )
    return builder.as_markup()


def admin_chats_topics_chat_list_keyboard(
    language_code: str, chats: list[tuple[AppChat, str | None]]
) -> InlineKeyboardMarkup:
    """Выбор чата для настройки whitelist тем."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    for chat, title in chats:
        label = title or str(chat.chat_id)
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f"admin:chats:topics:open:{chat.chat_id}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data="admin:settings:chats",
            style="primary",
        ),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def admin_chats_topic_whitelist_keyboard(
    language_code: str,
    telegram_chat_id: int,
    *,
    whitelist_active: bool,
    items: list[tuple[int | None, str, bool]],
    back_callback_data: str = "admin:chats:topics",
) -> InlineKeyboardMarkup:
    """При активном whitelist — переключатели тем; иначе — только кнопка «включить ограничения»."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    if whitelist_active:
        for pub_tid, label, is_on in items:
            prefix = "✅ " if is_on else "⬜ "
            text = f"{prefix}{label}"
            text = text if len(text) <= 60 else text[:57] + "…"
            cb_tid = 0 if pub_tid is None else int(pub_tid)
            builder.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"admin:chats:topics:toggle:{telegram_chat_id}:{cb_tid}",
                )
            )
        builder.row(
            InlineKeyboardButton(
                text=t("admin_chats_topics_btn_disable", lang),
                callback_data=f"admin:chats:topics:clear:{telegram_chat_id}",
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=t("admin_chats_topics_btn_enable", lang),
                callback_data=f"admin:chats:topics:restrict:{telegram_chat_id}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_back", lang),
            callback_data=back_callback_data,
            style="primary",
        ),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def admin_chats_fsm_nav_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Назад к списку чатов и главная (сброс FSM обрабатывает `on_admin_chats`)."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:settings:chats", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()
