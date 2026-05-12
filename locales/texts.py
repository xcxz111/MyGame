"""Тексты кнопок по языку (по образцу старого бота — только нужные строки)."""

from typing import Optional

DEFAULT_LANG = "ru"

LANG_NAMES = {
    "en": "English",
    "ru": "Русский",
    "pl": "Polski",
    "uk": "Українська",
}

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "choose_language": "Выберите язык / Choose language:",
        "welcome_menu": "Добро пожаловать в бота для игр",
        "welcome_user_id": "Ваш ID: {user_id}",
        "welcome_balance": "Ваш баланс: {balance} PLN",
        "btn_cabinet": "💼Личный кабинет💼",
        "btn_signup": "🎮 Записаться на игру 🎯🎳🎲",
        "btn_play_21_bot": "♠️♥️Играть в 21♣️♦️",
        "btn_casino": "🎰 Казино 🎰",
        "btn_admin": "Админка",
        "btn_lang": "🌐",
    },
    "en": {
        "choose_language": "Choose language / Выберите язык:",
        "welcome_menu": "Welcome to the game bot",
        "welcome_user_id": "Your ID: {user_id}",
        "welcome_balance": "Your balance: {balance} PLN",
        "btn_cabinet": "Personal account",
        "btn_signup": "Sign up for a game",
        "btn_play_21_bot": "Play 21",
        "btn_casino": "🎰 Casino 🎰",
        "btn_admin": "Admin",
        "btn_lang": "🌐",
    },
    "uk": {
        "choose_language": "Оберіть мову / Choose language:",
        "welcome_menu": "Ласкаво просимо в бота для ігор",
        "welcome_user_id": "Ваш ID: {user_id}",
        "welcome_balance": "Ваш баланс: {balance} PLN",
        "btn_cabinet": "Особистий кабінет",
        "btn_signup": "Записатися на гру",
        "btn_play_21_bot": "Грати в 21",
        "btn_casino": "🎰 Казино 🎰",
        "btn_admin": "Адмінка",
        "btn_lang": "🌐",
    },
    "pl": {
        "choose_language": "Wybierz język / Choose language:",
        "welcome_menu": "Witamy w bocie do gier",
        "welcome_user_id": "Twój ID: {user_id}",
        "welcome_balance": "Twoje saldo: {balance} PLN",
        "btn_cabinet": "Konto osobiste",
        "btn_signup": "Zapisz się na grę",
        "btn_play_21_bot": "Graj w 21",
        "btn_casino": "🎰 Kasyno 🎰",
        "btn_admin": "Panel admina",
        "btn_lang": "🌐",
    },
}


def get_lang(language_code: Optional[str]) -> str:
    if not language_code or not str(language_code).strip():
        return DEFAULT_LANG
    lang = str(language_code).strip().split("-")[0].split("_")[0].lower()
    return lang if lang in TEXTS else DEFAULT_LANG


def t(key: str, language_code: Optional[str] = None) -> str:
    lang = get_lang(language_code)
    return TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(
        key, TEXTS[DEFAULT_LANG].get(key, key)
    )
