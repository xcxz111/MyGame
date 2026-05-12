"""Тексты кнопок по языку (по образцу старого бота — только нужные строки)."""

from typing import Optional

DEFAULT_LANG = "ru"

LANG_NAMES = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "pl": "🇵🇱 Polski",
    "uk": "🇺🇦 Українська",
}

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "choose_language": "Выберите язык / Choose language:",
        "welcome_menu": "Добро пожаловать в бота для игр",
        "welcome_user_id": "Ваш ID: {user_id}",
        "welcome_balance": "Ваш баланс: {balance} PLN",
        "btn_cabinet": "💼Личный кабинет💼",
        "btn_topup": "💳 Пополнить баланс",
        "cabinet_title": "💼 Личный кабинет",
        "btn_signup": "🎮 Записаться на игру 🎯🎳🎲",
        "btn_play_21_bot": "♠️♥️Играть в 21♣️♦️",
        "btn_casino": "🎰 Казино 🎰",
        "btn_admin": "Админка",
        "btn_lang": "🌐",
        "btn_main": "🏠 Главная",
        "btn_back": "← Назад",
        "admin_title": "Админка",
        "admin_no_access": "⛔ Нет доступа",
        "admin_btn_games": "🎯 Игры",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Казино",
        "admin_btn_checkers": "🔴 Шашки",
        "admin_btn_kmb": "🪖 КМБ",
        "admin_btn_stats": "📊 Статистика",
        "admin_btn_bot_settings": "⚙️ Настройки бота",
        "admin_settings_title": "⚙️ Настройки бота",
        "admin_btn_payments": "💳 Настройка платежей",
        "admin_btn_chats": "💬 Настройка чатов",
        "admin_btn_forbidden_words": "🚫 Запрещённые слова",
        "admin_btn_admins": "👥 Настройка админов",
    },
    "en": {
        "choose_language": "Choose language / Выберите язык:",
        "welcome_menu": "Welcome to the game bot",
        "welcome_user_id": "Your ID: {user_id}",
        "welcome_balance": "Your balance: {balance} PLN",
        "btn_cabinet": "Personal account",
        "btn_topup": "💳 Top up balance",
        "cabinet_title": "💼 Personal account",
        "btn_signup": "Sign up for a game",
        "btn_play_21_bot": "Play 21",
        "btn_casino": "🎰 Casino 🎰",
        "btn_admin": "Admin",
        "btn_lang": "🌐",
        "btn_main": "🏠 Main",
        "btn_back": "← Back",
        "admin_title": "Admin panel",
        "admin_no_access": "⛔ Access denied",
        "admin_btn_games": "🎯 Games",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Casino",
        "admin_btn_checkers": "🔴 Checkers",
        "admin_btn_kmb": "🪖 KMB",
        "admin_btn_stats": "📊 Statistics",
        "admin_btn_bot_settings": "⚙️ Bot settings",
        "admin_settings_title": "⚙️ Bot settings",
        "admin_btn_payments": "💳 Payments settings",
        "admin_btn_chats": "💬 Chats settings",
        "admin_btn_forbidden_words": "🚫 Forbidden words",
        "admin_btn_admins": "👥 Admins settings",
    },
    "uk": {
        "choose_language": "Оберіть мову / Choose language:",
        "welcome_menu": "Ласкаво просимо в бота для ігор",
        "welcome_user_id": "Ваш ID: {user_id}",
        "welcome_balance": "Ваш баланс: {balance} PLN",
        "btn_cabinet": "Особистий кабінет",
        "btn_topup": "💳 Поповнити баланс",
        "cabinet_title": "💼 Особистий кабінет",
        "btn_signup": "Записатися на гру",
        "btn_play_21_bot": "Грати в 21",
        "btn_casino": "🎰 Казино 🎰",
        "btn_admin": "Адмінка",
        "btn_lang": "🌐",
        "btn_main": "🏠 Головна",
        "btn_back": "← Назад",
        "admin_title": "Адмінка",
        "admin_no_access": "⛔ Немає доступу",
        "admin_btn_games": "🎯 Ігри",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Казино",
        "admin_btn_checkers": "🔴 Шашки",
        "admin_btn_kmb": "🪖 КМБ",
        "admin_btn_stats": "📊 Статистика",
        "admin_btn_bot_settings": "⚙️ Налаштування бота",
        "admin_settings_title": "⚙️ Налаштування бота",
        "admin_btn_payments": "💳 Налаштування платежів",
        "admin_btn_chats": "💬 Налаштування чатів",
        "admin_btn_forbidden_words": "🚫 Заборонені слова",
        "admin_btn_admins": "👥 Налаштування адмінів",
    },
    "pl": {
        "choose_language": "Wybierz język / Choose language:",
        "welcome_menu": "Witamy w bocie do gier",
        "welcome_user_id": "Twój ID: {user_id}",
        "welcome_balance": "Twoje saldo: {balance} PLN",
        "btn_cabinet": "Konto osobiste",
        "btn_topup": "💳 Doładuj saldo",
        "cabinet_title": "💼 Konto osobiste",
        "btn_signup": "Zapisz się na grę",
        "btn_play_21_bot": "Graj w 21",
        "btn_casino": "🎰 Kasyno 🎰",
        "btn_admin": "Panel admina",
        "btn_lang": "🌐",
        "btn_main": "🏠 Główna",
        "btn_back": "← Wstecz",
        "admin_title": "Panel admina",
        "admin_no_access": "⛔ Brak dostępu",
        "admin_btn_games": "🎯 Gry",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Kasyno",
        "admin_btn_checkers": "🔴 Warcaby",
        "admin_btn_kmb": "🪖 KMB",
        "admin_btn_stats": "📊 Statystyka",
        "admin_btn_bot_settings": "⚙️ Ustawienia bota",
        "admin_settings_title": "⚙️ Ustawienia bota",
        "admin_btn_payments": "💳 Ustawienia płatności",
        "admin_btn_chats": "💬 Ustawienia czatów",
        "admin_btn_forbidden_words": "🚫 Zabronione słowa",
        "admin_btn_admins": "👥 Ustawienia adminów",
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
