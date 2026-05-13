from keyboards.admin import (
    admin_bot_settings_keyboard,
    admin_fees_keyboard,
    admin_game21_fees_keyboard,
    admin_games_keyboard,
    admin_menu_keyboard,
)
from keyboards.admin_chats import (
    admin_chats_delete_confirm_keyboard,
    admin_chats_delete_list_keyboard,
    admin_chats_fsm_nav_keyboard,
    admin_chats_keyboard,
    admin_chats_topic_whitelist_keyboard,
    admin_chats_topics_chat_list_keyboard,
)
from keyboards.admin_games import (
    admin_game_cancel_keyboard,
    admin_game_chat_pick_keyboard,
    admin_game_confirm_keyboard,
    admin_game_detail_keyboard,
    admin_game_forum_topic_keyboard,
    admin_games_list_keyboard,
)
from keyboards.cabinet import cabinet_menu_keyboard
from keyboards.languages import language_keyboard
from keyboards.main_menu import main_menu_keyboard

__all__ = [
    "admin_bot_settings_keyboard",
    "admin_fees_keyboard",
    "admin_game21_fees_keyboard",
    "admin_games_keyboard",
    "admin_menu_keyboard",
    "admin_chats_keyboard",
    "admin_chats_fsm_nav_keyboard",
    "admin_chats_delete_list_keyboard",
    "admin_chats_delete_confirm_keyboard",
    "admin_chats_topics_chat_list_keyboard",
    "admin_chats_topic_whitelist_keyboard",
    "admin_game_chat_pick_keyboard",
    "admin_game_cancel_keyboard",
    "admin_game_confirm_keyboard",
    "admin_game_forum_topic_keyboard",
    "admin_games_list_keyboard",
    "admin_game_detail_keyboard",
    "cabinet_menu_keyboard",
    "language_keyboard",
    "main_menu_keyboard",
]
