"""Клавиатуры для управления играми в админ-панели."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.app_chat import AppChat
from database.models.game import Game, GameType
from locales.texts import t
from services.games.constants import MAIN_GAME_EMOJI_HINT
from services.games.forum_thread import format_forum_topic_display_label


def admin_game_chat_pick_keyboard(
    language_code: str, chats: list[tuple[AppChat, str | None]]
) -> InlineKeyboardMarkup:
    """Выбор целевого чата для новой игры (если их несколько)."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    for chat, title in chats:
        label = title or str(chat.chat_id)
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f"admin:games:create:chat:{chat.chat_id}",
            )
        )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:games"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


def admin_game_forum_topic_keyboard(
    language_code: str,
    topic_rows: list[tuple[int, str]],
    *,
    show_general_option: bool = True,
) -> InlineKeyboardMarkup:
    """Выбор темы форума (message_thread_id, подпись)."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    for thread_id, title in topic_rows:
        label = format_forum_topic_display_label(lang, message_thread_id=thread_id, name=title)
        label = label if len(label) <= 60 else label[:57] + "…"
        builder.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f"admin:games:create:forum:{thread_id}",
            )
        )
    if show_general_option:
        builder.row(
            InlineKeyboardButton(
                text=t("admin_game_forum_skip", lang),
                callback_data="admin:games:create:forum:skip",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_game_forum_reload", lang),
            callback_data="admin:games:create:forum:reload",
        ),
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:games"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


def admin_game_cancel_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """На промежуточных шагах ввода — только Отмена и Главная."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_btn_cancel_create", lang),
            callback_data="admin:games:create:cancel",
        ),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


def admin_game_confirm_keyboard(language_code: str) -> InlineKeyboardMarkup:
    """Превью с кнопками Создать / Отменить."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_btn_confirm_create", lang),
            callback_data="admin:games:create:confirm",
        ),
        InlineKeyboardButton(
            text=t("admin_btn_cancel_create", lang),
            callback_data="admin:games:create:cancel",
        ),
    )
    return builder.as_markup()


def admin_games_list_keyboard(
    language_code: str, games: list[Game], *, back_to: str
) -> InlineKeyboardMarkup:
    """Список игр (по одной кнопке на игру). back_to — callback назад."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    for game in games:
        date_label = game.start_time.strftime("%d.%m %H:%M")
        type_label = {
            GameType.DICE: "🎲",
            GameType.BOWLING: "🎳",
            GameType.DARTS: "🎯",
            GameType.ANY: MAIN_GAME_EMOJI_HINT,
        }.get(game.game_type, "🎲")
        builder.row(
            InlineKeyboardButton(
                text=f"{type_label} #{game.id} · {date_label}",
                callback_data=f"admin:games:view:{game.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data=back_to),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


def admin_game_detail_keyboard(
    language_code: str, game: Game, *, back_to: str
) -> InlineKeyboardMarkup:
    """Экран детали игры (пока только Назад/Главная — кнопки управления добавим позже)."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data=back_to),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()
