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
        "topup_enter_amount": "💳 <b>Пополнение баланса</b>\n\nВведите сумму пополнения в PLN (от {min} до {max} PLN):",
        "topup_invalid_amount": "❌ Неверная сумма. Введите число (например 50).",
        "topup_out_of_range": "❌ Сумма должна быть от {min} до {max} PLN.",
        "topup_no_accounts": "⚠️ Пополнения временно недоступны — нет активных платежных аккаунтов. Попробуйте позже.",
        "topup_order_created": (
            "💳 <b>Заявка на пополнение создана</b>\n\n"
            "Сумма: <b>{amount} PLN</b>\n"
            "Номер заявки: <code>{order_id}</code>\n\n"
            "📱 Сделайте BLIK-перевод на номер:\n<code>{blik}</code>\n\n"
            "⚠️ <b>В назначении платежа обязательно укажите код:</b>\n<code>{order_id}</code>\n\n"
            "После получения платежа баланс зачислится автоматически."
        ),
        "topup_btn_cancel_order": "❌ Отменить заявку",
        "topup_order_cancelled": "❌ Заявка <code>{order_id}</code> отменена.",
        "topup_order_not_found": "❌ Заявка не найдена или уже закрыта.",
        "btn_withdraw": "💸 Запросить вывод средств",
        "btn_cancel_withdraw": "❌ Отменить вывод средств",
        "withdraw_enter_amount": (
            "💸 <b>Вывод средств</b>\n\n"
            "Введите сумму вывода в PLN (минимум {min} PLN).\n"
            "Комиссия: <b>{fee}%</b>\n"
            "⏱ Вывод осуществляется в течение 24 часов."
        ),
        "withdraw_invalid_amount": "❌ Неверная сумма. Введите число (например 150).",
        "withdraw_below_min": "❌ Вывод доступен от {min} PLN.",
        "withdraw_not_enough": "❌ Недостаточно средств. Ваш баланс: {balance} PLN.",
        "withdraw_enter_blik": "📱 Введите номер BLIK (минимум 9 цифр):",
        "withdraw_invalid_blik": "❌ Неверный формат BLIK. Минимум 9 цифр.",
        "withdraw_confirm": (
            "💸 <b>Подтверждение вывода</b>\n\n"
            "Сумма с баланса: <b>{amount} PLN</b>\n"
            "Комиссия: <b>{fee}%</b> ({fee_amount} PLN)\n"
            "К выплате: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "Подтвердить вывод?"
        ),
        "withdraw_btn_yes": "✅ Да",
        "withdraw_btn_no": "❌ Нет",
        "withdraw_created": (
            "✅ <b>Заявка на вывод создана</b>\n\n"
            "Номер: <code>#{id}</code>\n"
            "К выплате: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "⏱ Вывод будет произведён в течение 24 часов."
        ),
        "withdraw_cancel_ask": "❓ Вы уверены, что хотите отменить вывод <code>#{id}</code>?",
        "withdraw_cancelled": "✅ Вывод <code>#{id}</code> отменён. Деньги возвращены на баланс.",
        "withdraw_not_pending": "❌ Заявка не найдена или уже обработана.",
        "withdraw_already_pending": "⚠️ У вас уже есть активная заявка на вывод. Отмените её, чтобы создать новую.",
        "withdraw_admin_message": (
            "🏦 <b>Новый запрос на вывод</b>\n\n"
            "👤 {mention}{username}\n"
            "🆔 <code>{user_id}</code>\n"
            "💸 Запрошено: <b>{amount} PLN</b>\n"
            "🧾 Комиссия: {fee}% ({fee_amount} PLN)\n"
            "💵 К выплате: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>"
        ),
        "withdraw_admin_btn_approve": "✅ Принять",
        "withdraw_admin_approved": "✅ <b>ОПЛАЧЕНО</b>",
        "withdraw_admin_cancelled": "❌ <b>ОТМЕНЕНО</b>",
        "withdraw_approved_user": (
            "✅ Ваш вывод <code>#{id}</code> на сумму <b>{payout} PLN</b> отправлен."
        ),
        "cabinet_title": "💼 Личный кабинет",
        "cabinet_balance": "💰 Баланс: <b>{balance} PLN</b>",
        "cabinet_level": "⭐ Уровень: <b>{level}</b>",
        "cabinet_next_level": "📈 До уровня {level}: <b>{amount} PLN</b>",
        "cabinet_next_level_max": "📈 Следующий уровень: <b>максимальный уровень достигнут</b>",
        "cabinet_referral_link": "🔗 Ваша реферальная ссылка:\n<code>{link}</code>",
        "btn_referral_program": "🤝 Реферальная программа",
        "referral_program_text": (
            "🤝 <b>Реферальная программа</b>\n\n"
            "Ваша ссылка:\n<code>{link}</code>\n\n"
            "Условия: приглашайте игроков по своей ссылке и получайте "
            "<b>{percent}%</b> от каждой выйгранной ставки вашего реферала\n\n"
            "<b>Ваши рефералы:</b>\n{referrals}"
        ),
        "referral_empty": "Пока нет рефералов.",
        "referral_line": "• {name} — {profit} PLN",
        "btn_signup": "🎮 Записаться на игру 🎯🎳🎲",
        "main_menu_chat_fallback": "💬 Чат",
        "btn_play_21_bot": "♠️♥️Играть в 21♣️♦️",
        "btn_checkers": "⚪️ Шашки ⚫️",
        "btn_kmb": "👊✌️🤚 КМБ 👊✌️🤚",
        "btn_casino": "🎰 Слот 🎰",
        "slot_enter_bet_with_balance": "Ваш баланс: {balance} PLN\nВведите сумму ставки (например 1):",
        "slot_rules_block": "Правила и выплаты:\n• 3 одинаковых — x4\n• 2 одинаковых — x1.1\n• Все разные — проигрыш",
        "slot_bet_invalid": "Неверная сумма ставки. Введите положительное число.",
        "slot_not_enough_balance": "Недостаточно средств для ставки.",
        "slot_spin_prompt": "Ваш баланс: {balance} PLN\nСтавка {amount} PLN принята.\nТеперь крутите 🎰",
        "slot_balance_update_failed": "Не удалось обновить баланс. Попробуйте еще раз.",
        "slot_combo_three": "3 одинаковых",
        "slot_combo_two": "2 одинаковых",
        "slot_combo_none": "все разные",
        "slot_result_win": "Ваш баланс: {balance} PLN\nРезультат 🎰: {combo}\nСтавка {bet} PLN умножается на x{mult}\nВыплата: {payout} PLN",
        "slot_result_lose": "Ваш баланс: {balance} PLN\nРезультат 🎰: {combo}\nСтавка {bet} PLN сгорела.",
        "slot_disabled": "Слот сейчас выключен.",
        "admin_slot_stats_text": "Слот:\nБОТ выиграл: {bot_won_sum} PLN\nБОТ проиграл: {bot_lost_sum} PLN\nОбщая прибыль БОТа: {bot_profit_sum} PLN",
        "admin_slot_mode_text": (
            "🎰 <b>Режим слот</b>\n\n"
            "{status}\n\n"
            "-------------------------------------------\n"
            "Всего игр: {total_games}\n"
            "уникальных пользователей: {unique_users}\n"
            "выйграно пользователями: {users_won_sum} PLN\n"
            "проиграно пользователями: {users_lost_sum} PLN\n"
            "общая прибыль бота: {bot_profit_sum} PLN\n"
            "-------------------------------------------"
        ),
        "admin_slot_btn_enable": "Включить",
        "admin_slot_btn_disable": "Выключить",
        "admin_slot_btn_rules": "Правило",
        "admin_slot_rules_prompt": "Введите правило для Слота:",
        "admin_slot_rules_current": "Текущее правило:\n{rules}",
        "admin_slot_rules_empty": "❌ Правило не может быть пустым. Введите текст правила.",
        "admin_slot_rules_saved": "✅ Правило Слота сохранено.",
        "btn_admin": "Админка",
        "btn_lang": "🌐",
        "btn_main": "🏠 Главная",
        "btn_back": "← Назад",
        "btn_return_main": "вернуться на главную",
        "input_cancel_hint": "нажмите /back для отмены",
        "admin_title": "Админка",
        "admin_no_access": "⛔ Нет доступа",
        "admin_btn_games": "🎯 Игры",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Слот",
        "admin_btn_checkers": "⚪️ Шашки ⚫️",
        "admin_checkers_title": (
            "⚪️ Шашки ⚫️\n\n"
            "комиссия: {commission}%\n\n"
            "Всего игр в шашки: {total_games}\n"
            "Прибыль с комиссии: {commission_sum} PLN"
        ),
        "admin_checkers_btn_enable": "Включить/Выключить",
        "admin_checkers_enable_title": "⚪️ Шашки ⚫️\n\nВыберите чат для включения/выключения игры:",
        "admin_checkers_chat_on": "Шашки в «{title}»: выкл",
        "admin_checkers_chat_off": "Шашки в «{title}»: вкл",
        "admin_checkers_btn_disable": "Выключить",
        "admin_checkers_btn_rules": "Правила",
        "admin_checkers_rules_title": "⚪️ Правила шашек ⚫️\n\n{rules}",
        "admin_checkers_rules_prompt": "Введите правила шашек на русском языке. Бот сохранит их и переведёт для других языков.",
        "admin_checkers_rules_empty": "Правила ещё не заданы.",
        "admin_btn_kmb": "🪖 КМБ",
        "admin_kmb_title": (
            "кнб\n\n"
            "Комиссия: {commission}%\n\n"
            "Уникальных пользователей: {unique_users}\n"
            "Всего игр в КНБ: {total_games}\n"
            "Прибыль с комиссии: {commission_sum} PLN"
        ),
        "admin_kmb_btn_enable": "Включить/Выключить",
        "admin_kmb_enable_title": "👊✌️🤚 КМБ 👊✌️🤚\n\nВыберите чат для включения/выключения игры:",
        "admin_kmb_chat_on": "КМБ в «{title}»: выкл",
        "admin_kmb_chat_off": "КМБ в «{title}»: вкл",
        "admin_kmb_btn_rules": "Правила",
        "admin_kmb_rules_title": "Правила КНБ\n\n{rules}",
        "admin_kmb_rules_prompt": "Введите правила КНБ:",
        "admin_kmb_rules_empty": "Правила ещё не заданы.",
        "admin_kmb_rules_saved": "✅ Правила КНБ сохранены.",
        "admin_btn_stats": "📊 Статистика",
        "admin_stats_title": "📊 <b>Статистика</b>",
        "admin_stats_btn_users": "👥 Пользователи",
        "admin_stats_users_title": (
            "👥 <b>Пользователи</b>\n\n"
            "Всего пользователей: {total}\n"
            "Активных: {active}\n"
            "Заблокированных: {banned}\n"
            "С балансом: {with_balance}\n"
            "Общий баланс: {balance_sum} PLN"
        ),
        "admin_user_search_prompt": "👥 Введите ID пользователя или username:",
        "admin_user_not_found": "❌ Пользователь не найден. Введите ID или username ещё раз.",
        "admin_user_card": (
            "👤 <b>{label}</b>\n\n"
            "ID: <code>{user_id}</code>\n"
            "Username: {username}\n"
            "Статус: {status}\n"
            "Баланс: <b>{balance} PLN</b>\n"
            "Уровень: <b>{level}</b>\n"
            "Выигранных ставок для уровня: {level_progress} PLN\n"
            "Бонус уровня: вывод −{level_withdraw_discount}%, рефералы +{level_referral_bonus}%\n"
            "Язык: {language}\n"
            "Пригласил: {referrer}\n\n"
            "Комиссия вывода: <b>{withdraw_percent}%</b> ({withdraw_source})\n"
            "Реферальный %: <b>{referral_percent}%</b> ({referral_source})\n\n"
            "Рефералов: {referrals_count}\n"
            "Прибыль от рефералов: {referrals_profit} PLN"
        ),
        "admin_user_status_active": "🟢 активен",
        "admin_user_status_banned": "🔴 забанен",
        "admin_user_percent_global": "общая {percent}%",
        "admin_user_percent_personal": "персональная {percent}%",
        "admin_user_withdraw_discount": "общая {global_percent}% − скидка {discount}%",
        "admin_user_referral_bonus": "общая {global_percent}% + надбавка {bonus}%",
        "admin_user_percent_reset": "без персональной настройки",
        "admin_user_btn_topup": "💳 Пополнить баланс",
        "admin_user_btn_withdraw_percent": "💸 Изменить комиссию на вывод",
        "admin_user_btn_referral_percent": "🤝 Изменить реферальный %",
        "admin_user_btn_ban": "🚫 Забанить",
        "admin_user_btn_unban": "✅ Разбанить",
        "admin_user_btn_find_other": "🔎 Найти другого пользователя",
        "admin_user_topup_prompt": "Введите сумму пополнения для {user} / <code>{user_id}</code>:",
        "admin_user_withdraw_prompt": (
            "Введите скидку к комиссии вывода для {user} / <code>{user_id}</code>.\n\n"
            "Например: если общая комиссия 10%, а вы введёте <code>1</code>, "
            "итоговая комиссия будет 9%.\n\n"
            "Отправьте процент от 0 до 100 или <code>-</code>, чтобы убрать персональную скидку."
        ),
        "admin_user_referral_prompt": (
            "Введите надбавку к реферальному проценту для {user} / <code>{user_id}</code>.\n\n"
            "Например: если общий реферальный процент 1%, а вы введёте <code>1</code>, "
            "итоговый процент будет 2%.\n\n"
            "Отправьте процент от 0 до 100 или <code>-</code>, чтобы убрать персональную надбавку."
        ),
        "admin_user_amount_invalid": "❌ Введите положительную сумму.",
        "admin_user_percent_invalid": "❌ Введите процент от 0 до 100 или <code>-</code> для сброса.",
        "admin_user_topup_done": "✅ Баланс пополнен на <b>{amount} PLN</b>.",
        "admin_user_withdraw_done": "✅ Скидка к комиссии вывода обновлена: <b>{percent}</b>.",
        "admin_user_referral_done": "✅ Надбавка к реферальному проценту обновлена: <b>{percent}</b>.",
        "admin_user_banned": "Пользователь забанен.",
        "admin_user_unbanned": "Пользователь разбанен.",
        "admin_btn_bot_settings": "⚙️ Настройки бота",
        "admin_games_title": "🎯 <b>Игры</b>",
        "admin_btn_create_game": "➕ Создать игру",
        "admin_btn_active_games": "🟢 Текущие игры",
        "admin_btn_past_games": "📚 Прошедшие игры",
        "admin_wip": "🚧 В разработке",
        "admin_settings_title": "⚙️ Настройки бота",
        "admin_btn_payments": "💳 Настройка платежей",
        "admin_btn_fees": "💸 Настройка комиссий",
        "admin_btn_levels": "⭐ Настройка уровней",
        "admin_levels_title": "⭐ <b>Настройка уровней</b>\n\nВыберите уровень для редактирования:",
        "admin_levels_detail": (
            "⭐ <b>Уровень {level}</b>\n\n"
            "Название: <b>{title}</b>\n"
            "Статус: {status}\n\n"
            "Нужно выигранных ставок: <b>{required} PLN</b>\n"
            "Награда на баланс: <b>{reward} PLN</b>\n"
            "Скидка к комиссии вывода: <b>{withdraw}%</b>\n"
            "Надбавка к реферальному %: <b>{referral}%</b>"
        ),
        "admin_levels_status_on": "🟢 включён",
        "admin_levels_status_off": "⚪ выключен",
        "admin_levels_not_found": "❌ Уровень не найден.",
        "admin_levels_saved": "✅ Сохранено.",
        "admin_levels_btn_title": "Название",
        "admin_levels_btn_required": "Условие получения",
        "admin_levels_btn_reward": "Награда на баланс",
        "admin_levels_btn_withdraw": "Скидка вывода",
        "admin_levels_btn_referral": "Бонус рефералов",
        "admin_levels_btn_enable": "Включить",
        "admin_levels_btn_disable": "Выключить",
        "admin_levels_prompt_title": "Введите название для уровня {level}:",
        "admin_levels_prompt_required": "Введите сумму выигранных ставок для получения уровня {level}:",
        "admin_levels_prompt_reward": "Введите награду на баланс за уровень {level}:",
        "admin_levels_prompt_withdraw": "Введите скидку к комиссии вывода за уровень {level} (0-100):",
        "admin_levels_prompt_referral": "Введите надбавку к реферальному проценту за уровень {level} (0-100):",
        "admin_levels_invalid_text": "❌ Текст не может быть пустым.",
        "admin_levels_invalid_amount": "❌ Введите положительное число или 0.",
        "admin_levels_invalid_percent": "❌ Введите процент от 0 до 100.",
        "admin_btn_withdraw_fee": "💸 Комиссия вывода",
        "admin_btn_slot_fee": "🎰 Комиссия Слота",
        "admin_btn_checkers_fee": "⚪️ Комиссия Шашек ⚫️",
        "admin_btn_kmb_fee": "👊✌️🤚 Комиссия КНБ",
        "admin_btn_referral_fee": "🤝 Комиссия рефералов",
        "admin_fees_title": "💸 <b>Настройка комиссий</b>",
        "admin_pay_title": "<b>MBanks</b> — аккаунты:",
        "admin_pay_empty": "<b>MBanks</b>\nАккаунтов нет.",
        "admin_pay_btn_add": "➕ Добавить аккаунт",
        "admin_pay_btn_withdraw_fee": "💸 Комиссия вывода",
        "admin_withdraw_fee_title": "💸 <b>Комиссия вывода</b>\n\nТекущее значение: <b>{percent}%</b>\n\nВведите новый процент (например <code>5</code> или <code>2.5</code>):",
        "admin_withdraw_fee_invalid": "❌ Неверный формат. Введите число от 0 до 100 (например <code>5</code> или <code>2.5</code>).",
        "admin_withdraw_fee_updated": "✅ Комиссия вывода обновлена: <b>{percent}%</b>",
        "admin_slot_fee_title": "🎰 <b>Комиссия Слота</b>\n\nТекущее значение: <b>{percent}%</b>\n\nВведите новый процент:",
        "admin_slot_fee_updated": "✅ Комиссия Слота обновлена: <b>{percent}%</b>",
        "admin_checkers_fee_title": "⚪️ <b>Комиссия Шашек</b> ⚫️\n\nТекущее значение: <b>{percent}%</b>\n\nВведите новый процент:",
        "admin_checkers_fee_updated": "✅ Комиссия Шашек обновлена: <b>{percent}%</b>",
        "admin_kmb_fee_title": "👊✌️🤚 <b>Комиссия КНБ</b>\n\nТекущее значение: <b>{percent}%</b>\n\nВведите новый процент:",
        "admin_kmb_fee_updated": "✅ Комиссия КНБ обновлена: <b>{percent}%</b>",
        "admin_referral_fee_title": "🤝 <b>Комиссия рефералов</b>\n\nТекущее значение: <b>{percent}%</b>\n\nВведите новый процент:",
        "admin_referral_fee_updated": "✅ Комиссия рефералов обновлена: <b>{percent}%</b>",
        "admin_btn_game21_fees": "♠️ 21 — комиссии",
        "admin_fees_21_title": (
            "♠️ <b>Комиссии игры 21</b>\n\n"
            "Против бота: <b>{bot}%</b>\n"
            "Между пользователями: <b>{users}%</b>"
        ),
        "admin_game21_fee_btn_bot": "Против бота",
        "admin_game21_fee_btn_users": "Между пользователями",
        "admin_game21_fee_bot_title": "💸 Комиссия 21 (против бота)\n\nТекущее: <b>{percent}%</b>\n\nВведите новый процент:",
        "admin_game21_fee_users_title": "💸 Комиссия 21 (PvP)\n\nТекущее: <b>{percent}%</b>\n\nВведите новый процент:",
        "admin_game21_fee_updated": "✅ Комиссия 21 обновлена: <b>{percent}%</b>",
        "admin_21_title": (
            "♠️ <b>Режим 21</b>\n\n"
            "Против бота: {bot}\n\n"
            "Комиссии: бот {bot_fee}% · PvP {users_fee}%\n\n"
            "Выберите раздел настроек."
        ),
        "admin_21_summary": (
            "♠️ <b>Режим 21</b>\n\n"
            "-------------------------------------------\n"
            "Против БОТа:  {bot_fee}%\n\n"
            "Комиссия: {bot_fee}%\n\n"
            "Всего игр с БОТОМ: {bot_total}\n"
            "БОТ выиграл: {bot_won_count} игр, {bot_won_sum} PLN\n"
            "БОТ проиграл: {bot_lost_count} игр, {bot_lost_sum} PLN\n"
            "Ничьи: {bot_draw_count}\n\n"
            "Прибыль БОТа: {bot_profit_sum} PLN\n\n"
            "-------------------------------------------\n"
            "Между пользователями:\n\n"
            "Комиссия: {users_fee}%\n\n"
            "Всего PvP игр: {pvp_total}\n"
            "Прибыль с комиссии: {pvp_commission_sum} PLN\n\n"
            "-------------------------------------------\n"
            "Общая прибыль: {total_profit_sum} PLN"
        ),
        "admin_21_on": "🟢 вкл",
        "admin_21_off": "⚪ выкл",
        "admin_21_btn_enable": "Включить",
        "admin_21_btn_rules": "Правила",
        "admin_21_enable_title": "♠️ <b>21 — включение режимов</b>\n\nВключите игру против бота или PvP для подключённых чатов.",
        "admin_21_rules_title": "♠️ <b>21 — правила</b>\n\nДля игры с ботом: {bot}\nМежду пользователями: {users}",
        "admin_21_rules_btn_bot": "Для игры с ботом",
        "admin_21_rules_btn_users": "Между пользователями",
        "admin_21_rules_prompt_bot": "Введите правила для игры 21 с ботом:",
        "admin_21_rules_prompt_users": "Введите правила для игры 21 между пользователями:",
        "admin_21_rules_empty": "❌ Правила не могут быть пустыми. Введите текст правил.",
        "admin_21_rules_saved": "✅ Правила сохранены. Переводы для других языков обновлены автоматически.",
        "admin_21_rules_saved_no_translate": "✅ Правила сохранены на русском. Автоперевод не выполнен: проверьте AI-ключ в настройках.",
        "admin_21_btn_bot_on": "Против бота: выключить",
        "admin_21_btn_bot_off": "Против бота: включить",
        "admin_21_btn_users_on": "PvP глобально: выключить",
        "admin_21_btn_users_off": "PvP глобально: включить",
        "admin_21_chat_pvp_on": "PvP в «{title}»: выкл",
        "admin_21_chat_pvp_off": "PvP в «{title}»: вкл",
        "game21_active_notice": "У вас уже есть активная игра. Сначала завершите её.",
        "game21_bot_midgame_menu_blocked": (
            "Вы сейчас находитесь в активной игре. Сначала завершите текущую игру."
        ),
        "game21_busy_screen_text": "У вас уже есть активная игра в чате {chat}",
        "game21_busy_screen_text_bot": (
            "У вас уже есть активная игра с ботом. Доиграйте партию в этом чате."
        ),
        "game21_btn_abort_session": "Отменить игру",
        "game21_active_cancelled_toast": "Текущая сессия 21 отменена.",
        "game21_no_active_search_to_cancel": (
            "Нет активного поиска соперника (поиск уже завершён или игра началась)."
        ),
        "game21_pvp_choose_topic": "Выберите игровую комнату (🟢 свободна, 🔴 занята):",
        "game21_pvp_topic_free": "🟢",
        "game21_pvp_topic_busy": "🔴",
        "game21_pvp_topic_general": "Общий чат",
        "game21_pvp_search_post_failed": "Не удалось опубликовать поиск в чате. Ставка возвращена.",
        "game21_pvp_decide_prompt_other": "{name}, бросьте кубик 🎲 один раз.",
        "game21_menu_title": "Режим 21",
        "game21_btn_rules": "Правила",
        "game21_btn_vs_bot": "Играть против бота",
        "game21_btn_vs_user_chat": "Играть против пользователя в чате",
        "game21_coming_soon_all_off": "Игра 21 пока недоступна.",
        "game21_coming_soon_play": "Игра 21 против бота недоступна.",
        "game21_enter_bet": "Введите сумму ставки (PLN):",
        "game21_bet_invalid": "Неверная сумма. Введите положительное число.",
        "game21_not_enough_balance": "Недостаточно средств на балансе.",
        "game21_confirm_bet_with_win": "Ставка: {amount} PLN\nВозможный выигрыш: {win} PLN\n\nСогласны?",
        "game21_btn_yes": "Да",
        "game21_btn_no": "Нет",
        "game21_cancelled": "Отменено.",
        "game21_rules_title": "<b>Правила игры 21</b>",
        "game21_rules": "См. разделы ниже.",
        "game21_rules_bot": (
            "<b>Против бота</b>\n"
            "Бросайте 🎲 в ЛС. Минимум 16, затем «Хватит». Бот бросает после вас."
        ),
        "game21_rules_users": (
            "<b>PvP в чате {chat_title}</b>\n"
            "Поиск соперника, затем кубик для очередности и раунд до 21."
        ),
        "game21_throw_now": "Бросайте кубик 🎲",
        "game21_player_result": "Ваш результат: {total}",
        "game21_player_busted": "Ваш результат: {total}\nПеребор!",
        "game21_player_blackjack": "У вас 21!",
        "game21_player_can_stop": "Ваш результат: {total}\nМожно продолжать или нажать «Хватит».",
        "game21_btn_stop": "Хватит",
        "game21_bot_turn_start": "Ход бота.",
        "game21_bot_result": "Результат бота: {total}",
        "game21_result_win": "Вы выиграли!",
        "game21_result_lose": "Вы проиграли.",
        "game21_result_draw": "Ничья.",
        "game21_end_bot_win": (
            "<b>Вы выиграли!</b>\n"
            "На баланс зачислено <b>{payout} PLN</b>.\n"
            "Счёт: вы {player_total} — бот {bot_total}."
        ),
        "game21_end_bot_lose": "Вы проиграли {bet} PLN\nСчёт: вы {player_total} — бот {bot_total}.",
        "game21_end_bot_lose_bust": "Вы проиграли {bet} PLN\nПеребор: {player_total}.",
        "game21_end_bot_draw": (
            "<b>Ничья.</b>\n"
            "Ставка <b>{bet} PLN</b> возвращена на баланс.\n"
            "Счёт: {player_total} — {bot_total}."
        ),
        "game21_pvp_enter_bet": "Введите сумму ставки (PLN):\n\nДля игры в 21 в {room}",
        "game21_pvp_confirm": "Согласны начать поиск соперника?\nСтавка: {amount} PLN\nВозможный выигрыш: {win} PLN",
        "game21_pvp_search_started": (
            "Поиск соперника запущен\n\n"
            "С вашего баланса списана ставка {amount} PLN"
        ),
        "game21_pvp_choose_chat": "Выберите чат:",
        "game21_pvp_no_available_chat": "Нет доступных чатов для PvP.",
        "game21_pvp_must_join_chat": "Нужно состоять в чате: {chat_title}",
        "game21_pvp_not_member_title": "Вы не в игровом чате",
        "game21_pvp_not_member_intro": "Чтобы играть в 21 с пользователем, вступите в чат по ссылке ниже. После этого снова нажмите «Играть против пользователя в чате».",
        "game21_pvp_main_active_exists": "Нельзя создать запрос на игру так как там в данный момент проходит игра.",
        "game21_chat_command_active_exists": "В данный момент в {topic} есть активная игра.",
        "game21_chat_command_usage": "Используйте формат: <code>/21 10</code>",
        "checkers_chat_command_usage": "Используйте формат: <code>/checkers 10</code>",
        "kmb_chat_command_usage": "Используйте формат: <code>/kmb 10 3</code>, где 3 — до скольких побед играть.",
        "info_command_text": (
            "<b>Команды бота</b>\n\n"
            "<code>/info</code> — показать это сообщение.\n"
            "<code>/21 10</code> — создать игру в 21 PvP со ставкой 10 PLN.\n"
            "<code>/checkers 10</code> — создать игру в шашки со ставкой 10 PLN.\n"
            "<code>/kmb 10 3</code> — создать КМБ со ставкой 10 PLN, игра до 3 побед.\n"
            "<code>/back</code> — отменить текущий ввод в личном чате.\n\n"
            "Также работают старые форматы: <code>/play21:10</code>, "
            "<code>/checkers:10</code>, <code>/kmb:10:3</code>, <code>/rps 10 3</code>."
        ),
        "game21_pvp_active_exists": "В этом слоте уже идёт игра или поиск.",
        "game21_pvp_self_accept_forbidden": "Вы не можете играть сам с собой.",
        "game21_pvp_search_post": (
            "{user} ищет соперника в 21\n\n"
            "Ставка: {amount} PLN\nВозможный выигрыш: {win} PLN\n\n"
            "Игра на баланс бота {bot_link}"
        ),
        "game21_pvp_btn_accept": "Принять",
        "game21_pvp_match_title": "Игра в 21",
        "game21_pvp_match_started_in_topic": "Игра в 21 началась в {room}",
        "game21_pvp_match_prize": "<b>Сумма выигрыша: {win} PLN</b>",
        "game21_pvp_match_rules_heading": "Правила игры:",
        "game21_pvp_rules_body": (
            "В начале каждый один раз бросает кубик 🎲 — у кого меньше, тот ходит первым. "
            "Дальше по очереди набираете очки, цель — как можно ближе к 21, но не больше. "
            "Когда счёт совпал у обоих и наступила нужная фаза, можно «Хватит». "
            "После остановок или перебора сравниваются суммы; возможна ничья."
        ),
        "game21_pvp_started": (
            "Игра 21\n{p1}\n{p2}\n\nСтавка: {amount} PLN · выигрыш до {win} PLN\n{bot_link}"
        ),
        "game21_pvp_general_started_notice": (
            "Игра между {p1} и {p2} в 21 началась в <b>{room}</b>."
        ),
        "game21_pvp_topic_started_notice": (
            "Игра между {p1} и {p2} в 21 началась.\n\nПриз: {prize} PLN."
        ),
        "game21_pvp_decide_first": "{players} — бросьте кубик 🎲 по одному разу (кто меньше, ходит первым).",
        "game21_pvp_decide_roll_result": "{name}:, результат: {value}",
        "game21_pvp_decide_tie": "Результаты равны. Бросьте еще по одному разу.",
        "game21_pvp_turn_prompt": "{name}, ваш ход. Бросайте 🎲",
        "game21_pvp_player_result": "{name}, результат: {total}",
        "game21_pvp_player_busted": "{name}, результат: {total} — перебор!",
        "game21_pvp_player_blackjack": "{name} — 21!",
        "game21_pvp_player_can_stop": "{name}, результат: {total}. Можно «Хватит» или ещё бросок.",
        "game21_pvp_stop_announce": "Игрок {name} сказал «Хватит».\nЕго результат: {total}",
        "game21_pvp_not_your_turn_stop": "Сейчас ход игрока {name}",
        "checkers_choose_chat": "Выберите чат для игры в шашки:",
        "checkers_choose_topic": "Выберите игровую комнату (🟢 свободна, 🔴 занята):",
        "checkers_enter_bet": "<b>{chat}</b>\nВаш баланс: {balance} PLN\nВведите сумму ставки:",
        "checkers_confirm": "Ставка: {amount} PLN\nСумма выигрыша: {win} PLN\nНачать поиск соперника?",
        "checkers_search_post": "{user} ищет соперника в шашки.\nСтавка: {amount} PLN\nСумма выигрыша: {win} PLN",
        "checkers_match_title": "Игра в шашки",
        "checkers_match_started_in_topic": "Игра в шашки началась в {room}",
        "checkers_match_prize": "Сумма выигрыша: {win} PLN",
        "checkers_match_rules_heading": "Правила игры:",
        "checkers_rules_body": (
            "Белые ходят первыми. Шашки ходят по диагонали, обязательное взятие нужно выполнять. "
            "Дамка ходит по диагонали на любое расстояние. Если игрок не делает ход 2 минуты, он проигрывает."
        ),
        "checkers_btn_accept": "Принять игру",
        "checkers_search_started": "Поиск игры в шашки начат. Ставка {amount} PLN списана.",
        "checkers_search_cancelled_refund": "Отменено.\nСумма ставки возвращена на баланс.",
        "checkers_search_timeout": "Игру в шашки никто не принял. Ставка {amount} PLN возвращена на баланс.",
        "checkers_active_notice": "У вас уже есть активная игра или поиск игры.",
        "checkers_disabled": "Игра в шашки временно выключена.",
        "checkers_board_text": (
            "⚪️ <b>Шашки</b> ⚫️\n"
            "⚪ {white}\n"
            "⚫ {black}\n\n"
            "Банк: {amount} PLN\n"
            "Ходит: {turn}"
        ),
        "checkers_not_your_turn": "Сейчас не ваш ход.",
        "checkers_bad_move": "Так ходить нельзя.",
        "checkers_flood_wait": "Слишком быстро. Подождите {seconds} сек.",
        "checkers_decide_white": "{players} — бросьте кубик 🎲 по одному разу. Кто выбросит больше, играет белыми.",
        "checkers_white_chosen": "{name} играет белыми. Игра начинается.",
        "checkers_turn_timeout_warning": "{name}, у вас осталась 1 минута, чтобы сделать ход, иначе вы проиграете.",
        "checkers_turn_timeout_result": (
            "Время на ход вышло.\n"
            "{loser} проиграл.\n\n"
            "Победитель: {winner}\n"
            "Выигрыш {payout} PLN добавлен на баланс."
        ),
        "checkers_draw_countdown": (
            "В игре уже {no_capture} ходов не была сбита ни одна шашка.\n"
            "Если в течение 10 ходов (по 5 на каждого) не будет сбита ни одна шашка, будет объявлена ничья.\n\n"
            "До ничьей осталось ходов: {remaining}"
        ),
        "checkers_draw_countdown_reset": "Шашка была сбита. Отсчёт до ничьей сброшен.",
        "checkers_draw_result": "Игра окончена.\nНичья.\n\nСтавка {amount} PLN возвращена обоим игрокам.",
        "checkers_winner": "Игра окончена.\nПобедитель: {name}\n\nВыигрыш {payout} PLN добавлен на баланс.",
        "kmb_choose_chat": "Выберите чат для игры в КМБ:",
        "kmb_no_chats": "КМБ сейчас недоступен: нет включённых чатов или тем.",
        "kmb_choose_topic": "Выберите игровую комнату (🟢 свободна, 🔴 занята):",
        "kmb_enter_wins": "<b>{chat}</b>\nДо скольких побед играем?\nВведите число от 1 до 10:",
        "kmb_wins_invalid": "Неверное количество побед. Введите число от 1 до 10.",
        "kmb_enter_bet": "<b>{chat}</b>\nВаш баланс: {balance} PLN\nВведите сумму ставки:",
        "kmb_confirm": "Игра до {wins} побед\nСтавка: {amount} PLN\nСумма выигрыша: {win} PLN\nНачать поиск соперника?",
        "kmb_search_post": "{user} ищет соперника в КМБ.\nИгра до {wins} побед\nСтавка: {amount} PLN\nСумма выигрыша: {win} PLN",
        "kmb_btn_accept": "Принять игру",
        "kmb_search_started": "Поиск игры в КМБ начат. Игра до {wins} побед. Ставка {amount} PLN списана.",
        "kmb_search_cancelled_refund": "Отменено.\nСумма ставки возвращена на баланс.",
        "kmb_search_timeout": "Игру в КМБ никто не принял. Ставка {amount} PLN возвращена на баланс.",
        "kmb_match_started_in_topic": "Игра в Камень/Ножницы/Бумага началась в {room}",
        "kmb_match_title": "Игра в Камень/Ножницы/Бумага",
        "kmb_match_prize": "Сумма выигрыша: {win} PLN",
        "kmb_match_rules_heading": "Правила игры:",
        "kmb_rules_body": (
            "Камень бьёт ножницы, ножницы режут бумагу, бумага накрывает камень. "
            "При одинаковом выборе раунд считается ничьей и переигрывается."
        ),
        "kmb_pick_prompt": (
            "👊✌️🤚 <b>КМБ</b>\n\n"
            "Игра до {wins} побед\n"
            "Счёт: {p1_score} - {p2_score}\n\n"
            "{p1}: {p1_status}\n"
            "{p2}: {p2_status}\n\n"
            "Выберите: камень, ножницы или бумага."
        ),
        "kmb_pick_wait": "ожидает выбор",
        "kmb_pick_done": "выбор сделан",
        "kmb_not_your_game": "Это не ваша игра.",
        "kmb_choice_saved": "Выбор принят.",
        "kmb_round_win": (
            "Раунд окончен.\n"
            "{p1}: {p1_choice}\n"
            "{p2}: {p2_choice}\n\n"
            "Раунд выиграл: {winner}\n"
            "Счёт: {p1_score} - {p2_score}\n\n"
            "Игра до {wins} побед. Выберите ещё раз."
        ),
        "kmb_result_win": (
            "Игра окончена.\n"
            "Финальный счёт: {p1_score} - {p2_score}\n\n"
            "{p1}: {p1_choice}\n"
            "{p2}: {p2_choice}\n\n"
            "Победитель: {winner}\n"
            "Выигрыш {payout} PLN добавлен на баланс."
        ),
        "kmb_result_draw": (
            "Ничья.\n"
            "{p1}: {p1_choice}\n"
            "{p2}: {p2_choice}\n\n"
            "Счёт: {p1_score} - {p2_score}\n"
            "Игра до {wins} побед.\n\n"
            "Выберите ещё раз."
        ),
        "game21_pvp_stop_only_on_equal": "«Хватит» доступно только при равном счёте.",
        "game21_pvp_winner": (
            "Игра окончена.\n"
            "Победитель: {name}\n\n"
            "Ваш выйгрыш {payout} PLN добавлен на баланс в боте {bot_link}"
        ),
        "game21_pvp_draw": "Ничья. Возврат {amount} PLN · {bot_link}",
        "game21_pvp_pm_bet_deducted": "Списана ставка {amount} PLN.",
        "game21_pvp_search_not_accepted": "Никто не принял заявку. Возврат {amount} PLN.",
        "game21_pvp_topic_forbidden": "Эта тема недоступна для игры.",
        "game21_pvp_topics_restricted_empty": "В этом чате нет тем, разрешённых администратором для игр.",
        # ---- Chats settings ----
        "admin_chats_title": "💬 <b>Подключённые чаты</b>",
        "admin_chats_empty": "Чатов пока нет.",
        "admin_chats_list_line": "• <code>{chat_id}</code> · {title}",
        "admin_chats_btn_add": "➕ Добавить чат",
        "admin_chats_btn_delete": "🗑 Удалить чат",
        "admin_chats_btn_game_topics": "📋 Темы для игр",
        "admin_chats_topics_choose_chat": "Выберите чат, в котором настроить, в каких темах форума можно играть (21 и игры с кубиком):",
        "admin_chats_topics_not_forum": "Этот чат не форум-супергруппа с темами — настройка не нужна.",
        "admin_chats_topics_chat_unavailable": "Не удалось открыть чат.",
        "admin_chats_topics_body_open": (
            "📋 <b>Темы для игр</b>: {title}\n\n"
            "Сейчас ограничений нет — PvP 21 и создание игр доступны во всех известных темах и в общем чате.\n\n"
            "Нажмите «Включить ограничения», чтобы явно выбрать, где разрешены игры (список заполнится текущими темами; снимите лишние галочки)."
        ),
        "admin_chats_topics_body_restricted": (
            "📋 <b>Темы для игр</b>: {title}\n\n"
            "Включён список разрешённых тем. Игры только там, где отмечено ✅.\n\n"
            "«Снять ограничения» — снова разрешить везде."
        ),
        "admin_chats_topics_btn_enable": "Включить ограничения по темам",
        "admin_chats_topics_btn_disable": "Снять ограничения (все темы)",
        "admin_chats_enter_button_title": (
            "Введите <b>название кнопки</b> — так она будет отображаться пользователям при выборе чата "
            "(для каждого языка интерфейса можно задать свой текст позже; сейчас одно и то же название "
            "запишется для ru / en / uk / pl).\n\n"
            "Длина до 200 символов."
        ),
        "admin_chats_invalid_button_title": "❌ Введите непустое название (до 200 символов).",
        "admin_chats_enter_chat_id": (
            "Введите <b>ID чата</b> (например <code>-1001234567890</code>).\n\n"
            "Чтобы узнать ID: добавьте бота в группу и перешлите оттуда любое сообщение боту "
            "<a href=\"https://t.me/userinfobot\">@userinfobot</a>, либо используйте сервис вроде getidsbot."
        ),
        "admin_chats_invalid_id": "❌ Неверный формат. Введите целое число, начинающееся с <code>-100</code>.",
        "admin_chats_already_added": "⚠️ Этот чат уже подключён.",
        "admin_chats_added": "✅ Чат <code>{chat_id}</code> подключён.",
        "admin_chats_invite_ok": "✅ Ссылка-приглашение создана автоматически.",
        "admin_chats_invite_link_failed": (
            "⚠️ Не удалось получить invite-ссылку: проверьте, что бот добавлен в чат как <b>администратор</b> "
            "с правом приглашать участников (или что у группы включены приглашения по ссылке)."
        ),
        "admin_chats_session_lost": "⚠️ Сессия добавления сброшена. Начните снова с «Добавить чат».",
        "admin_chats_delete_choose": "Выберите чат для удаления:",
        "admin_chats_delete_confirm": "Удалить чат <code>{chat_id}</code>?",
        "admin_chats_deleted": "✅ Чат удалён.",
        "admin_chats_delete_none": "Нет подключённых чатов для удаления.",
        # ---- Games create FSM ----
        "admin_game_no_chats": "⚠️ Сначала подключите хотя бы один чат в «Настройки бота → Настройка чатов».",
        "admin_game_pick_chat": "В каком чате анонсировать игру?",
        "admin_game_pick_forum_topic": "📂 <b>Тема форума</b>\n\nВыберите тему, где будет проходить игра (анонс, раунды, броски).\n\nПодпись «Ветка · id …» значит, что бот запомнил только внутренний номер ветки (Telegram не присылает название в обычных сообщениях). Чтобы было как в чате, один раз переименуйте тему в группе — бот обновит название.",
        "admin_game_pick_forum_topic_empty": "📂 <b>Тема форума</b>\n\nВ списке пусто: Telegram не отдаёт список тем через API, бот запоминает ветки из сообщений и сервисных событий.\n\nЕсли темы уже есть: отправьте в каждую нужную тему любое сообщение (или один раз переименуйте тему), затем нажмите «🔄 Обновить список тем».\n\nМожно пропустить и вести игру в общем чате без ветки.",
        "admin_game_forum_skip": "Без темы (общий чат)",
        "admin_game_forum_reload": "🔄 Обновить список тем",
        "admin_game_forum_thread_placeholder": "Ветка · id {id}",
        "admin_game_forum_reload_toast": "Список обновлён",
        "admin_game_forum_reload_lost": "⚠️ Сессия сброшена. Начните создание игры заново.",
        "admin_game_topic_forbidden": "Нельзя выбрать эту тему: её нет в списке разрешённых для этого чата.",
        "admin_game_pick_type": "🎯 <b>Тип игры</b>\n\nВыберите вид броска:",
        "admin_game_type_dice": "🎲 Кубики",
        "admin_game_type_bowling": "🎳 Боулинг",
        "admin_game_type_darts": "🎯 Дартс",
        "admin_game_type_any": "🎲 🎳 🎯 (любой бросок)",
        "admin_game_name_prefix": "Игра",
        "admin_game_enter_participants": "👥 <b>Кол-во участников</b>\n\nВведите минимум и максимум через «/» или «-».\nПример: <code>10/100</code>",
        "admin_game_invalid_participants": "❌ Формат: <code>min/max</code>, оба — положительные числа, min ≤ max.",
        "admin_game_enter_prizes": "🏆 <b>Призы</b>\n\nВведите суммы в PLN, каждая с новой строки. Сколько строк — столько призовых мест.\nПример:\n<code>20\n10\n5</code>\n\nПобедителям эти суммы будут начислены на баланс автоматически.",
        "admin_game_invalid_prizes": "❌ Призы должны быть положительными числами (например <code>20</code> или <code>10.5</code>), каждый с новой строки.",
        "admin_game_prizes_more_than_max": "❌ Призовых мест ({n}) больше, чем максимум участников ({max}). Уменьшите количество призов или измените участников.",
        "admin_game_enter_min_topup": "💰 <b>Условие записи: минимальная сумма пополнений</b>\n\nФорматы:\n• <code>0</code> — без условия\n• <code>100</code> — пополнил хотя бы на 100 PLN за всё время\n• <code>100 : 01.01.2026</code> — пополнил хотя бы на 100 PLN с указанной даты до старта игры",
        "admin_game_invalid_min_topup": "❌ Формат: число PLN (<code>100</code>) или число и дата через «:» (<code>100 : 01.01.2026</code>).",
        "admin_game_enter_entry_fee": "💵 <b>Стоимость взноса</b>\n\nВведите сумму в PLN (0 — бесплатно).",
        "admin_game_invalid_entry_fee": "❌ Введите число ≥ 0 (например <code>0</code> или <code>5</code>).",
        "admin_game_enter_datetime": "🗓 <b>Дата и время старта</b>\n\nФорматы:\n• <code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n• <code>ЧЧ:ММ</code> (сегодня)",
        "admin_game_invalid_datetime": "❌ Не удалось распознать дату/время. Пример: <code>25.12.2026 19:30</code>.",
        "admin_game_datetime_in_past": "❌ Время старта должно быть в будущем.",
        "admin_game_topup_since_after_start": "❌ Дата начала периода пополнений позже даты старта игры. Поменяйте условие или дату.",
        "admin_game_preview_title": "📋 <b>Превью игры</b>",
        "admin_game_preview_chat": "Чат: <b>{chat}</b>",
        "admin_game_preview_forum_topic": "Тема: <b>{topic}</b>",
        "admin_game_preview_type": "Тип: <b>{type}</b>",
        "admin_game_preview_participants": "Участники: <b>{min}–{max}</b>",
        "admin_game_preview_prizes": "Призы:",
        "admin_game_preview_min_topup_none": "Условие: <b>без условий</b>",
        "admin_game_preview_min_topup_alltime": "Условие: пополнения от <b>{n} PLN</b> (за всё время)",
        "admin_game_preview_min_topup_period": "Условие: пополнения от <b>{n} PLN</b> с <b>{since}</b>",
        "admin_game_preview_pay_free": "Тип: <b>бесплатная</b>",
        "admin_game_preview_pay_paid": "Тип: <b>платная</b>, взнос <b>{fee} PLN</b>",
        "admin_game_preview_datetime": "Старт: <b>{datetime}</b>",
        "admin_btn_confirm_create": "✅ Создать",
        "admin_btn_cancel_create": "❌ Отменить",
        "admin_game_created": "✅ Игра #{id} создана.",
        "admin_game_create_cancelled": "❌ Создание отменено.",
        # ---- Game lists ----
        "admin_games_active_title": "🟢 <b>Текущие игры</b>",
        "admin_games_past_title": "📚 <b>Прошедшие игры</b>",
        "admin_games_empty_active": "Сейчас активных игр нет.",
        "admin_games_empty_past": "Прошедших игр пока нет.",
        "admin_game_detail_title": "🎯 <b>Игра #{id}</b>",
        "admin_game_detail_status": "Статус: <b>{status}</b>",
        "admin_game_detail_participants_count": "Записалось: <b>{count}/{max}</b> (минимум {min})",
        "admin_game_status_draft": "ожидает старта",
        "admin_game_status_active": "идёт сейчас",
        "admin_game_status_finished": "завершена",
        "admin_game_status_cancelled": "отменена",
        # ---- Announcement (in chat + DM) ----
        "game_announce_title": "🎯 Игра для <b>{chat}</b> создана",
        "game_announce_date": "Дата: <b>{date}</b>",
        "game_announce_participants_range": "Участников: <b>{min}–{max}</b>",
        "game_announce_conditions": "<b>Условия участия:</b>",
        "game_announce_cond_min_topup_alltime": "• минимум пополнений: <b>{n} PLN</b> (за всё время)",
        "game_announce_cond_min_topup_period": "• минимум пополнений: <b>{n} PLN</b> (с {since} до старта игры)",
        "game_announce_cond_pay_free": "• бесплатно",
        "game_announce_cond_pay_paid": "• платная, взнос <b>{fee} PLN</b>",
        "game_announce_cond_none": "• без дополнительных условий",
        "game_announce_prizes": "<b>Призы:</b>",
        "game_announce_signup_link": "Запись на игру через бота {bot_link}",
        "game_announce_signup_no_link": "Запись на игру — напишите боту в личные сообщения.",
        "game_btn_signup": "🎮 Записаться на игру",
        "game_reminder_5min": "⏳ До игры в чате «{chat_title}» осталось около 5 минут.",
        "game_cancelled_not_enough_players_dm": "Игра отменена: набралось только {current} из {required} участников.",
        "game_cancelled_refund_full_fee": "Взнос {fee} PLN возвращён на ваш баланс.",
        "game_start_header": "<b>Условия игры:</b>\n{conditions}\n\n<b>Призы:</b>\n{prizes}",
        "game_start_cond_min_topup_period": "• минимум пополнений: {n} PLN (с {since} до {until})",
        "game_start_cond_min_topup_alltime": "• минимум пополнений: {n} PLN (за всё время)",
        "game_start_cond_paid": "• платная игра, взнос {fee} PLN",
        "game_start_cond_free": "• бесплатная игра",
        "game_start_cond_none": "• без дополнительных условий",
        "game_rules_block": (
            "Правила:\n"
            "1) Раунды по очереди, по 3 броска на игрока.\n"
            "2) Можно бросать 🎲 🎳 🎯 (или тем же текстом).\n"
            "3) После раунда — проходной балл по среднему среди сделавших броски.\n"
            "4) Пропустившие ход получают догоняющую попытку.\n"
            "5) Финал и тай-брейк — по правилам бота."
        ),
        "game_round1_list_intro": "Первый раунд!",
        "round_list_participants": "Список участников",
        "round_score_pending": "…",
        "round_score_eliminated": "выл",
        "round_your_result": "Ваш бросок: {value}",
        "round_throw_2_more": "Сделайте ещё 2 броска {emoji}",
        "round_throw_1_more": "Сделайте ещё 1 бросок {emoji}",
        "round_third_throw_done": "{result_line}\n{name}, итог в этом раунде: <b>{total}</b>",
        "round_throw_prompt": "{name}, сделайте 3 броска любым эмодзи: {emoji}",
        "round_turn_60sec_left": "{name}, осталась 1 минута на ход.",
        "round_participant_skipped": "{name} — ход пропущен.",
        "round_participants_missed": "Участники без очков в этом раунде:",
        "round_catchup_5min": "У вас есть время на 3 броска (ускоренный режим).",
        "round_1_finished": "Первый раунд завершён.",
        "round_N_finished": "Раунд {round} завершён.",
        "round_passing_score": "Проходной балл: {score}",
        "round_list_passed": "В следующий раунд проходят:",
        "round_list_passed_final": "В финальный раунд проходят:",
        "round_results_header": "Результаты:",
        "round_tiebreak": "Тай-брейк!",
        "round_tiebreak_for": "Для определения: {places}",
        "round_tiebreak_place_one": "{n}-е место",
        "round_tiebreak_place_span": "мест с {a} по {b}",
        "round_tiebreak_throw": "{name}, сделайте 1 бросок {emoji}",
        "round_tiebreak_result": "{name} — бросок тай-брейка: {value}",
        "round_final_finished": "Финальный раунд завершён.",
        "round_winners": "Победители:",
        "game_sponsor_line": "Спонсор: {bot_link}",
        "game_dm_prize_won": "🎉 Вы заняли {place} место! На баланс зачислено <b>{amount} PLN</b>.",
        "game_signup_no_games": "Сейчас нет игр с открытой записью.",
        "game_signup_list_title": "Открытая запись на игры (нажмите игру):",
        "game_signup_list_item": "#{id} {when} — {chat}",
        "game_signup_btn_join": "✅ Записаться",
        "game_signup_btn_leave": "🚫 Выйти",
        "game_signup_not_found": "Игра не найдена.",
        "game_signup_not_draft": "Запись недоступна (игра уже не в статусе ожидания).",
        "game_signup_started": "Игра уже стартовала или запись закрыта.",
        "game_signup_full": "Мест больше нет.",
        "game_signup_min_topup": "Недостаточно пополнений: нужно {need} PLN, у вас {have} PLN (по правилам игры).",
        "game_signup_low_balance": "Недостаточно средств: взнос {fee} PLN, баланс {balance} PLN.",
        "game_signup_already_in": "Вы уже в списке участников.",
        "game_signup_ok": "Вы записаны.",
        "game_signup_left": "Вы вышли из списка участников.",
        "game_signup_not_in": "Вы не были записаны.",
        "game_signup_card": (
            "🎯 <b>Игра #{id}</b>\n"
            "Чат: {chat}\n"
            "Старт: <b>{start}</b>\n"
            "Игроки: <b>{count}</b> / {max_p} (мин. {min_p})\n\n"
            "<b>Условия:</b>\n{conditions}\n\n"
            "<b>Призы (PLN):</b>\n{prizes}"
        ),
        "game_signup_cond_topup_period": "• пополнения от {n} PLN с {since}",
        "game_signup_cond_topup_alltime": "• пополнения от {n} PLN за всё время",
        "game_signup_cond_paid": "• взнос {fee} PLN",
        "game_signup_cond_free": "• бесплатно",
        "game_signup_cond_none": "—",
        "admin_pay_btn_activate": "▶️ Запустить",
        "admin_pay_btn_deactivate": "⏹ Остановить",
        "admin_pay_btn_edit_proxy": "🌐 Изменить прокси",
        "admin_pay_btn_edit_blik": "📱 Изменить BLIK",
        "admin_pay_btn_edit_limit": "📊 Изменить лимит",
        "admin_pay_btn_rescan": "🔁 Перечитать последние письма",
        "admin_pay_btn_delete": "🗑 Удалить",
        "admin_pay_btn_delete_confirm": "✅ Подтвердить удаление",
        "admin_pay_btn_cancel": "❌ Отмена",
        "admin_pay_btn_bank_custom": "✏️ Другой",
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
        "topup_enter_amount": "💳 <b>Top up balance</b>\n\nEnter the top-up amount in PLN (from {min} to {max} PLN):",
        "topup_invalid_amount": "❌ Invalid amount. Enter a number (e.g. 50).",
        "topup_out_of_range": "❌ Amount must be between {min} and {max} PLN.",
        "topup_no_accounts": "⚠️ Top-ups are temporarily unavailable — no active payment accounts. Please try later.",
        "topup_order_created": (
            "💳 <b>Top-up order created</b>\n\n"
            "Amount: <b>{amount} PLN</b>\n"
            "Order ID: <code>{order_id}</code>\n\n"
            "📱 Make a BLIK transfer to:\n<code>{blik}</code>\n\n"
            "⚠️ <b>Include this code in the payment title:</b>\n<code>{order_id}</code>\n\n"
            "Your balance will be credited automatically after the payment arrives."
        ),
        "topup_btn_cancel_order": "❌ Cancel order",
        "topup_order_cancelled": "❌ Order <code>{order_id}</code> cancelled.",
        "topup_order_not_found": "❌ Order not found or already closed.",
        "btn_withdraw": "💸 Request withdrawal",
        "btn_cancel_withdraw": "❌ Cancel withdrawal",
        "withdraw_enter_amount": (
            "💸 <b>Withdrawal</b>\n\n"
            "Enter the amount in PLN (minimum {min} PLN).\n"
            "Fee: <b>{fee}%</b>\n"
            "⏱ Withdrawals are processed within 24 hours."
        ),
        "withdraw_invalid_amount": "❌ Invalid amount. Enter a number (e.g. 150).",
        "withdraw_below_min": "❌ Withdrawal is available from {min} PLN.",
        "withdraw_not_enough": "❌ Not enough funds. Your balance: {balance} PLN.",
        "withdraw_enter_blik": "📱 Enter your BLIK number (at least 9 digits):",
        "withdraw_invalid_blik": "❌ Invalid BLIK format. At least 9 digits.",
        "withdraw_confirm": (
            "💸 <b>Confirm withdrawal</b>\n\n"
            "Debited from balance: <b>{amount} PLN</b>\n"
            "Fee: <b>{fee}%</b> ({fee_amount} PLN)\n"
            "Payout: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "Confirm withdrawal?"
        ),
        "withdraw_btn_yes": "✅ Yes",
        "withdraw_btn_no": "❌ No",
        "withdraw_created": (
            "✅ <b>Withdrawal request created</b>\n\n"
            "ID: <code>#{id}</code>\n"
            "Payout: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "⏱ It will be processed within 24 hours."
        ),
        "withdraw_cancel_ask": "❓ Are you sure you want to cancel withdrawal <code>#{id}</code>?",
        "withdraw_cancelled": "✅ Withdrawal <code>#{id}</code> cancelled. Funds returned to your balance.",
        "withdraw_not_pending": "❌ Request not found or already processed.",
        "withdraw_already_pending": "⚠️ You already have an active withdrawal. Cancel it before creating a new one.",
        "withdraw_admin_message": (
            "🏦 <b>New withdrawal request</b>\n\n"
            "👤 {mention}{username}\n"
            "🆔 <code>{user_id}</code>\n"
            "💸 Requested: <b>{amount} PLN</b>\n"
            "🧾 Fee: {fee}% ({fee_amount} PLN)\n"
            "💵 Payout: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>"
        ),
        "withdraw_admin_btn_approve": "✅ Approve",
        "withdraw_admin_approved": "✅ <b>PAID</b>",
        "withdraw_admin_cancelled": "❌ <b>CANCELLED</b>",
        "withdraw_approved_user": (
            "✅ Your withdrawal <code>#{id}</code> for <b>{payout} PLN</b> has been sent."
        ),
        "cabinet_title": "💼 Personal account",
        "cabinet_balance": "💰 Balance: <b>{balance} PLN</b>",
        "cabinet_level": "⭐ Level: <b>{level}</b>",
        "cabinet_next_level": "📈 Until level {level}: <b>{amount} PLN</b>",
        "cabinet_next_level_max": "📈 Next level: <b>maximum level reached</b>",
        "cabinet_referral_link": "🔗 Your referral link:\n<code>{link}</code>",
        "btn_referral_program": "🤝 Referral program",
        "btn_return_main": "back to main menu",
        "btn_checkers": "⚪️ Checkers ⚫️",
        "btn_kmb": "👊✌️🤚 RPS 👊✌️🤚",
        "input_cancel_hint": "type /back to cancel",
        "referral_empty": "No referrals yet.",
        "referral_line": "• {name} — {profit} PLN",
        "referral_program_text": (
            "🤝 <b>Referral program</b>\n\n"
            "Your link:\n<code>{link}</code>\n\n"
            "Terms: invite players with your link and earn <b>{percent}%</b> "
            "of each winning bet your referral makes\n\n"
            "<b>Your referrals:</b>\n{referrals}"
        ),
        "admin_21_summary": (
            "♠️ <b>21 mode</b>\n\n"
            "-------------------------------------------\n"
            "Vs BOT:\n\n"
            "Fee: {bot_fee}%\n\n"
            "Total BOT games: {bot_total}\n"
            "BOT won: {bot_won_count} games, {bot_won_sum} PLN\n"
            "BOT lost: {bot_lost_count} games, {bot_lost_sum} PLN\n"
            "Draws: {bot_draw_count}\n\n"
            "BOT profit: {bot_profit_sum} PLN\n\n"
            "-------------------------------------------\n"
            "PvP:\n\n"
            "Fee: {users_fee}%\n\n"
            "Total PvP games: {pvp_total}\n"
            "Commission profit: {pvp_commission_sum} PLN\n\n"
            "-------------------------------------------\n"
            "Total profit: {total_profit_sum} PLN"
        ),
        "admin_btn_checkers_fee": "⚪️ Checkers fee ⚫️",
        "admin_btn_kmb_fee": "👊✌️🤚 RPS fee",
        "admin_btn_levels": "⭐ Level settings",
        "admin_btn_referral_fee": "🤝 Referral fee",
        "admin_checkers_btn_disable": "Disable",
        "admin_checkers_btn_enable": "Enable / Disable",
        "admin_checkers_btn_rules": "Rules",
        "admin_checkers_chat_off": "Checkers in «{title}»: ON",
        "admin_checkers_chat_on": "Checkers in «{title}»: OFF",
        "admin_checkers_enable_title": "⚪️ Checkers ⚫️\n\nPick a chat to enable or disable the game:",
        "admin_checkers_fee_title": "⚪️ <b>Checkers fee</b> ⚫️\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_checkers_fee_updated": "✅ Checkers fee updated: <b>{percent}%</b>",
        "admin_checkers_rules_empty": "Rules are not set yet.",
        "admin_checkers_rules_prompt": "Enter checkers rules in Russian. The bot will save them and translate for other languages.",
        "admin_checkers_rules_title": "⚪️ Checkers rules ⚫️\n\n{rules}",
        "admin_checkers_title": "⚪️ Checkers ⚫️\n\nFee: {commission}%\n\nTotal games: {total_games}\nCommission profit: {commission_sum} PLN",
        "admin_kmb_btn_enable": "Enable / Disable",
        "admin_kmb_btn_rules": "Rules",
        "admin_kmb_chat_off": "RPS in «{title}»: ON",
        "admin_kmb_chat_on": "RPS in «{title}»: OFF",
        "admin_kmb_enable_title": "👊✌️🤚 RPS 👊✌️🤚\n\nPick a chat to enable or disable the game:",
        "admin_kmb_fee_title": "👊✌️🤚 <b>RPS fee</b>\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_kmb_fee_updated": "✅ RPS fee updated: <b>{percent}%</b>",
        "admin_kmb_rules_empty": "Rules are not set yet.",
        "admin_kmb_rules_prompt": "Enter RPS rules:",
        "admin_kmb_rules_saved": "✅ RPS rules saved.",
        "admin_kmb_rules_title": "RPS rules\n\n{rules}",
        "admin_kmb_title": "RPS\n\nFee: {commission}%\n\nUnique users: {unique_users}\nTotal RPS games: {total_games}\nCommission profit: {commission_sum} PLN",
        "admin_levels_btn_disable": "Disable",
        "admin_levels_btn_enable": "Enable",
        "admin_levels_btn_referral": "Referral bonus",
        "admin_levels_btn_required": "Requirement",
        "admin_levels_btn_reward": "Balance reward",
        "admin_levels_btn_title": "Title",
        "admin_levels_btn_withdraw": "Withdraw discount",
        "admin_levels_detail": (
            "⭐ <b>Level {level}</b>\n\n"
            "Title: <b>{title}</b>\n"
            "Status: {status}\n\n"
            "Winning bets required: <b>{required} PLN</b>\n"
            "Balance reward: <b>{reward} PLN</b>\n"
            "Withdraw fee discount: <b>{withdraw}%</b>\n"
            "Referral % bonus: <b>{referral}%</b>"
        ),
        "admin_levels_invalid_amount": "❌ Enter a positive number or 0.",
        "admin_levels_invalid_percent": "❌ Enter a percent from 0 to 100.",
        "admin_levels_invalid_text": "❌ Text cannot be empty.",
        "admin_levels_not_found": "❌ Level not found.",
        "admin_levels_prompt_referral": "Enter referral % bonus for level {level} (0-100):",
        "admin_levels_prompt_required": "Enter winning bet sum required for level {level}:",
        "admin_levels_prompt_reward": "Enter balance reward for level {level}:",
        "admin_levels_prompt_title": "Enter title for level {level}:",
        "admin_levels_prompt_withdraw": "Enter withdraw fee discount for level {level} (0-100):",
        "admin_levels_saved": "✅ Saved.",
        "admin_levels_status_off": "⚪ disabled",
        "admin_levels_status_on": "🟢 enabled",
        "admin_levels_title": "⭐ <b>Level settings</b>\n\nPick a level to edit:",
        "admin_referral_fee_title": "🤝 <b>Referral fee</b>\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_referral_fee_updated": "✅ Referral fee updated: <b>{percent}%</b>",
        "admin_user_amount_invalid": "❌ Enter a positive amount.",
        "admin_user_banned": "User banned.",
        "admin_user_btn_ban": "🚫 Ban",
        "admin_user_btn_find_other": "🔎 Find another user",
        "admin_user_btn_referral_percent": "🤝 Change referral %",
        "admin_user_btn_topup": "💳 Top up balance",
        "admin_user_btn_unban": "✅ Unban",
        "admin_user_btn_withdraw_percent": "💸 Change withdrawal fee",
        "admin_user_card": (
            "👤 <b>{label}</b>\n\n"
            "ID: <code>{user_id}</code>\n"
            "Username: {username}\n"
            "Status: {status}\n"
            "Balance: <b>{balance} PLN</b>\n"
            "Level: <b>{level}</b>\n"
            "Winning bets toward level: {level_progress} PLN\n"
            "Level bonus: withdraw −{level_withdraw_discount}%, referral +{level_referral_bonus}%\n"
            "Language: {language}\n"
            "Invited by: {referrer}\n\n"
            "Withdrawal fee: <b>{withdraw_percent}%</b> ({withdraw_source})\n"
            "Referral %: <b>{referral_percent}%</b> ({referral_source})\n\n"
            "Referrals: {referrals_count}\n"
            "Profit from referrals: {referrals_profit} PLN"
        ),
        "admin_user_not_found": "❌ User not found. Enter ID or username again.",
        "admin_user_percent_global": "global {percent}%",
        "admin_user_percent_invalid": "❌ Enter percent 0–100 or <code>-</code> to reset.",
        "admin_user_percent_personal": "personal {percent}%",
        "admin_user_percent_reset": "no personal override",
        "admin_user_referral_bonus": "global {global_percent}% + bonus {bonus}%",
        "admin_user_referral_done": "✅ Referral bonus updated: <b>{percent}</b>.",
        "admin_user_referral_prompt": (
            "Enter referral bonus for {user} / <code>{user_id}</code>.\n\n"
            "Example: if global referral is 1% and you send <code>1</code>, effective is 2%.\n\n"
            "Send percent 0–100 or <code>-</code> to remove personal bonus."
        ),
        "admin_user_search_prompt": "👥 Enter user ID or username:",
        "admin_user_status_active": "🟢 active",
        "admin_user_status_banned": "🔴 banned",
        "admin_user_topup_done": "✅ Balance topped up by <b>{amount} PLN</b>.",
        "admin_user_topup_prompt": "Enter top-up amount for {user} / <code>{user_id}</code>:",
        "admin_user_unbanned": "User unbanned.",
        "admin_user_withdraw_discount": "global {global_percent}% − discount {discount}%",
        "admin_user_withdraw_done": "✅ Withdrawal discount updated: <b>{percent}</b>.",
        "admin_user_withdraw_prompt": (
            "Enter withdrawal fee discount for {user} / <code>{user_id}</code>.\n\n"
            "Example: if global fee is 10% and you send <code>1</code>, effective is 9%.\n\n"
            "Send percent 0–100 or <code>-</code> to remove personal discount."
        ),
        "checkers_active_notice": "You already have an active game or search.",
        "checkers_bad_move": "This move is not allowed.",
        "checkers_board_text": "⚪️ <b>Checkers</b> ⚫️\n⚪ {white}\n⚫ {black}\n\nPot: {amount} PLN\nTurn: {turn}",
        "checkers_btn_accept": "Accept game",
        "checkers_choose_chat": "Pick a chat for checkers:",
        "checkers_choose_topic": "Pick a game room (🟢 free, 🔴 busy):",
        "checkers_confirm": "Bet: {amount} PLN\nWin amount: {win} PLN\nStart opponent search?",
        "checkers_decide_white": "{players} — roll 🎲 once each. Higher roll plays white.",
        "checkers_disabled": "Checkers is temporarily disabled.",
        "checkers_draw_countdown": (
            "No capture for {no_capture} moves.\n"
            "If no capture in the next 10 moves (5 per side), it will be a draw.\n\n"
            "Moves until draw: {remaining}"
        ),
        "checkers_draw_countdown_reset": "A piece was captured. Draw countdown reset.",
        "checkers_draw_result": "Game over.\nDraw.\n\nBet {amount} PLN refunded to both players.",
        "checkers_enter_bet": "<b>{chat}</b>\nYour balance: {balance} PLN\nEnter bet amount:",
        "checkers_flood_wait": "Too fast. Wait {seconds} s.",
        "checkers_match_prize": "Win amount: {win} PLN",
        "checkers_match_rules_heading": "Rules:",
        "checkers_match_started_in_topic": "Checkers started in {room}",
        "checkers_match_title": "Checkers",
        "checkers_not_your_turn": "Not your turn.",
        "checkers_rules_body": (
            "White moves first. Pieces move diagonally; captures are mandatory. "
            "Kings move any distance diagonally. If you do not move within 2 minutes, you lose."
        ),
        "checkers_search_cancelled_refund": "Cancelled.\nBet returned to balance.",
        "checkers_search_post": "{user} is looking for a checkers opponent.\nBet: {amount} PLN\nWin amount: {win} PLN",
        "checkers_search_started": "Checkers search started. Bet {amount} PLN deducted.",
        "checkers_search_timeout": "No one accepted. Bet {amount} PLN returned to balance.",
        "checkers_turn_timeout_result": "Time is up.\n{loser} lost.\n\nWinner: {winner}\n{payout} PLN credited to balance.",
        "checkers_turn_timeout_warning": "{name}, you have 1 minute to move or you lose.",
        "checkers_white_chosen": "{name} plays white. Game begins.",
        "checkers_winner": "Game over.\nWinner: {name}\n\n{payout} PLN credited to balance.",
        "kmb_btn_accept": "Accept game",
        "kmb_choice_saved": "Choice saved.",
        "kmb_choose_chat": "Pick a chat for RPS:",
        "kmb_choose_topic": "Pick a game room (🟢 free, 🔴 busy):",
        "kmb_confirm": "First to {wins} wins\nBet: {amount} PLN\nWin amount: {win} PLN\nStart search?",
        "kmb_enter_bet": "<b>{chat}</b>\nYour balance: {balance} PLN\nEnter bet amount:",
        "kmb_enter_wins": "<b>{chat}</b>\nPlay first to how many wins?\nEnter 1–10:",
        "kmb_match_prize": "Win amount: {win} PLN",
        "kmb_match_rules_heading": "Rules:",
        "kmb_match_started_in_topic": "Rock/Paper/Scissors started in {room}",
        "kmb_match_title": "Rock / Paper / Scissors",
        "kmb_no_chats": "RPS unavailable: no enabled chats or topics.",
        "kmb_not_your_game": "This is not your game.",
        "kmb_pick_done": "choice made",
        "kmb_pick_prompt": (
            "👊✌️🤚 <b>RPS</b>\n\n"
            "First to {wins} wins\n"
            "Score: {p1_score} - {p2_score}\n\n"
            "{p1}: {p1_status}\n"
            "{p2}: {p2_status}\n\n"
            "Pick rock, scissors or paper."
        ),
        "kmb_pick_wait": "waiting for choice",
        "kmb_result_draw": (
            "Draw.\n"
            "{p1}: {p1_choice}\n"
            "{p2}: {p2_choice}\n\n"
            "Score: {p1_score} - {p2_score}\n"
            "First to {wins} wins.\n\n"
            "Pick again."
        ),
        "kmb_result_win": (
            "Game over.\n"
            "Final score: {p1_score} - {p2_score}\n\n"
            "{p1}: {p1_choice}\n"
            "{p2}: {p2_choice}\n\n"
            "Winner: {winner}\n"
            "{payout} PLN credited to balance."
        ),
        "kmb_round_win": (
            "Round over.\n"
            "{p1}: {p1_choice}\n"
            "{p2}: {p2_choice}\n\n"
            "Round winner: {winner}\n"
            "Score: {p1_score} - {p2_score}\n\n"
            "First to {wins} wins. Pick again."
        ),
        "kmb_rules_body": (
            "Rock beats scissors, scissors cut paper, paper covers rock. "
            "Same choice is a tie and the round is replayed."
        ),
        "kmb_search_cancelled_refund": "Cancelled.\nBet returned to balance.",
        "kmb_search_post": "{user} is looking for an RPS opponent.\nFirst to {wins} wins\nBet: {amount} PLN\nWin amount: {win} PLN",
        "kmb_search_started": "RPS search started. First to {wins} wins. Bet {amount} PLN deducted.",
        "kmb_search_timeout": "No one accepted. Bet {amount} PLN returned to balance.",
        "kmb_wins_invalid": "Invalid wins count. Enter 1–10.",
        "btn_signup": "Sign up for a game",
        "main_menu_chat_fallback": "💬 Chat",
        "btn_play_21_bot": "Play 21",
        "btn_casino": "🎰 Slot 🎰",
        "slot_enter_bet_with_balance": "Your balance: {balance} PLN\nEnter bet amount (e.g. 1):",
        "slot_rules_block": "Rules and payouts:\n• 3 of a kind — x4\n• 2 of a kind — x1.1\n• All different — lose",
        "slot_bet_invalid": "Invalid bet amount. Enter a positive number.",
        "slot_not_enough_balance": "Insufficient balance for this bet.",
        "slot_spin_prompt": "Your balance: {balance} PLN\nBet {amount} PLN accepted.\nNow spin 🎰",
        "slot_balance_update_failed": "Failed to update balance. Please try again.",
        "slot_combo_three": "3 of a kind",
        "slot_combo_two": "2 of a kind",
        "slot_combo_none": "all different",
        "slot_result_win": "Your balance: {balance} PLN\n🎰 Result: {combo}\nBet {bet} PLN is multiplied by x{mult}\nPayout: {payout} PLN",
        "slot_result_lose": "Your balance: {balance} PLN\n🎰 Result: {combo}\nBet {bet} PLN is lost.",
        "slot_disabled": "Slot is currently disabled.",
        "admin_slot_stats_text": "Slot:\nBOT won: {bot_won_sum} PLN\nBOT lost: {bot_lost_sum} PLN\nTotal BOT profit: {bot_profit_sum} PLN",
        "admin_slot_mode_text": (
            "🎰 <b>Slot mode</b>\n\n"
            "{status}\n\n"
            "-------------------------------------------\n"
            "Total games: {total_games}\n"
            "unique users: {unique_users}\n"
            "won by users: {users_won_sum} PLN\n"
            "lost by users: {users_lost_sum} PLN\n"
            "total bot profit: {bot_profit_sum} PLN\n"
            "-------------------------------------------"
        ),
        "admin_slot_btn_enable": "Enable",
        "admin_slot_btn_disable": "Disable",
        "admin_slot_btn_rules": "Rule",
        "admin_slot_rules_prompt": "Enter Slot rule:",
        "admin_slot_rules_current": "Current rule:\n{rules}",
        "admin_slot_rules_empty": "❌ Rule cannot be empty. Enter rule text.",
        "admin_slot_rules_saved": "✅ Slot rule saved.",
        "btn_admin": "Admin",
        "btn_lang": "🌐",
        "btn_main": "🏠 Main",
        "btn_back": "← Back",
        "admin_title": "Admin panel",
        "admin_no_access": "⛔ Access denied",
        "admin_btn_games": "🎯 Games",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Slot",
        "admin_btn_checkers": "⚪️ Checkers ⚫️",
        "admin_btn_kmb": "🪖 KMB",
        "admin_btn_stats": "📊 Statistics",
        "admin_stats_title": "📊 <b>Statistics</b>",
        "admin_stats_btn_users": "👥 Users",
        "admin_stats_users_title": (
            "👥 <b>Users</b>\n\n"
            "Total users: {total}\n"
            "Active: {active}\n"
            "Banned: {banned}\n"
            "With balance: {with_balance}\n"
            "Total balance: {balance_sum} PLN"
        ),
        "admin_btn_bot_settings": "⚙️ Bot settings",
        "admin_games_title": "🎯 <b>Games</b>",
        "admin_btn_create_game": "➕ Create game",
        "admin_btn_active_games": "🟢 Active games",
        "admin_btn_past_games": "📚 Past games",
        "admin_wip": "🚧 Work in progress",
        "admin_settings_title": "⚙️ Bot settings",
        "admin_btn_payments": "💳 Payments settings",
        "admin_btn_fees": "💸 Fees settings",
        "admin_btn_withdraw_fee": "💸 Withdrawal fee",
        "admin_btn_slot_fee": "🎰 Slot fee",
        "admin_fees_title": "💸 <b>Fees settings</b>",
        "admin_pay_title": "<b>MBanks</b> — accounts:",
        "admin_pay_empty": "<b>MBanks</b>\nNo accounts yet.",
        "admin_pay_btn_add": "➕ Add account",
        "admin_pay_btn_withdraw_fee": "💸 Withdrawal fee",
        "admin_withdraw_fee_title": "💸 <b>Withdrawal fee</b>\n\nCurrent: <b>{percent}%</b>\n\nEnter a new percent (e.g. <code>5</code> or <code>2.5</code>):",
        "admin_withdraw_fee_invalid": "❌ Invalid format. Enter a number between 0 and 100 (e.g. <code>5</code> or <code>2.5</code>).",
        "admin_withdraw_fee_updated": "✅ Withdrawal fee updated: <b>{percent}%</b>",
        "admin_slot_fee_title": "🎰 <b>Slot fee</b>\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_slot_fee_updated": "✅ Slot fee updated: <b>{percent}%</b>",
        "admin_btn_game21_fees": "♠️ 21 — fees",
        "admin_fees_21_title": "♠️ <b>Game 21 fees</b>\n\nVs bot: <b>{bot}%</b>\nPvP: <b>{users}%</b>",
        "admin_game21_fee_btn_bot": "Vs bot",
        "admin_game21_fee_btn_users": "Between users",
        "admin_game21_fee_bot_title": "💸 21 fee (vs bot)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_users_title": "💸 21 fee (PvP)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_updated": "✅ 21 fee updated: <b>{percent}%</b>",
        "admin_21_title": "♠️ <b>Game 21</b>\n\nVs bot: {bot}\n\nFees: bot {bot_fee}% · PvP {users_fee}%\n\nChoose settings section.",
        "admin_21_on": "🟢 on",
        "admin_21_off": "⚪ off",
        "admin_21_btn_enable": "Enable",
        "admin_21_btn_rules": "Rules",
        "admin_21_enable_title": "♠️ <b>21 — modes</b>\n\nEnable vs bot or PvP for connected chats.",
        "admin_21_rules_title": "♠️ <b>21 — rules</b>\n\nVs bot: {bot}\nBetween users: {users}",
        "admin_21_rules_btn_bot": "Vs bot",
        "admin_21_rules_btn_users": "Between users",
        "admin_21_rules_prompt_bot": "Enter rules for 21 vs bot:",
        "admin_21_rules_prompt_users": "Enter rules for 21 between users:",
        "admin_21_rules_empty": "❌ Rules cannot be empty. Enter rules text.",
        "admin_21_rules_saved": "✅ Rules saved. Translations for other languages were updated automatically.",
        "admin_21_rules_saved_no_translate": "✅ Rules saved in Russian. Auto-translation was not completed: check the AI key in settings.",
        "admin_21_btn_bot_on": "Vs bot: turn off",
        "admin_21_btn_bot_off": "Vs bot: turn on",
        "admin_21_btn_users_on": "PvP global: turn off",
        "admin_21_btn_users_off": "PvP global: turn on",
        "admin_21_chat_pvp_on": "PvP in «{title}»: off",
        "admin_21_chat_pvp_off": "PvP in «{title}»: on",
        "game21_active_notice": "You already have an active game. Finish it first.",
        "game21_bot_midgame_menu_blocked": (
            "You are currently in an active game. First finish the current game."
        ),
        "game21_busy_screen_text": "You already have an active game in {chat}.",
        "game21_busy_screen_text_bot": (
            "You already have an active game vs the bot. Finish the round in this chat."
        ),
        "game21_btn_abort_session": "Cancel game",
        "game21_active_cancelled_toast": "Your 21 session was cancelled.",
        "game21_no_active_search_to_cancel": (
            "There is no active opponent search (it was already cancelled or the match has started)."
        ),
        "game21_pvp_choose_topic": "Choose a game room (🟢 free, 🔴 busy):",
        "game21_pvp_topic_free": "🟢",
        "game21_pvp_topic_busy": "🔴",
        "game21_pvp_topic_general": "General",
        "game21_pvp_search_post_failed": "Could not post search. Bet refunded.",
        "game21_pvp_decide_prompt_other": "{name}, roll the dice 🎲 once.",
        "game21_menu_title": "Game 21",
        "game21_btn_rules": "Rules",
        "game21_btn_vs_bot": "Play vs bot",
        "game21_btn_vs_user_chat": "Play vs user in chat",
        "game21_coming_soon_all_off": "Game 21 is unavailable.",
        "game21_coming_soon_play": "Vs bot is unavailable.",
        "game21_enter_bet": "Enter bet (PLN):",
        "game21_bet_invalid": "Invalid amount.",
        "game21_not_enough_balance": "Insufficient balance.",
        "game21_confirm_bet_with_win": "Bet: {amount} PLN\nPossible win: {win} PLN\n\nConfirm?",
        "game21_btn_yes": "Yes",
        "game21_btn_no": "No",
        "game21_cancelled": "Cancelled.",
        "game21_rules_title": "<b>Rules 21</b>",
        "game21_rules": "See sections below.",
        "game21_rules_bot": "<b>Vs bot</b>\nRoll 🎲 in DM. Min 16, then Stop. Bot rolls after you.",
        "game21_rules_users": "<b>PvP in {chat_title}</b>\nFind opponent, roll for order, play to 21.",
        "game21_throw_now": "Roll the dice 🎲",
        "game21_player_result": "Your total: {total}",
        "game21_player_busted": "Your total: {total}\nBust!",
        "game21_player_blackjack": "You have 21!",
        "game21_player_can_stop": "Your total: {total}\nRoll or press Stop.",
        "game21_btn_stop": "Stop",
        "game21_bot_turn_start": "Bot's turn.",
        "game21_bot_result": "Bot total: {total}",
        "game21_result_win": "You won!",
        "game21_result_lose": "You lost.",
        "game21_result_draw": "Draw.",
        "game21_end_bot_win": (
            "<b>You won!</b>\n"
            "Credited to balance: <b>{payout} PLN</b>.\n"
            "Score: you {player_total} — bot {bot_total}."
        ),
        "game21_end_bot_lose": "You lost {bet} PLN\nScore: you {player_total} — bot {bot_total}.",
        "game21_end_bot_lose_bust": "You lost {bet} PLN\nBust at {player_total}.",
        "game21_end_bot_draw": (
            "<b>Draw.</b>\n"
            "Stake <b>{bet} PLN</b> refunded to your balance.\n"
            "Score: {player_total} — {bot_total}."
        ),
        "game21_pvp_enter_bet": "Enter bet (PLN):\n\nPlaying 21 in {room}",
        "game21_pvp_confirm": "Start opponent search?\nBet: {amount} PLN\nPossible win: {win} PLN",
        "game21_pvp_search_started": (
            "Opponent search started.\n\n"
            "{amount} PLN has been deducted from your balance."
        ),
        "game21_pvp_choose_chat": "Choose a chat:",
        "game21_pvp_no_available_chat": "No chats available for PvP.",
        "game21_pvp_must_join_chat": "You must be in the chat: {chat_title}",
        "game21_pvp_not_member_title": "You're not in the game chat",
        "game21_pvp_not_member_intro": "To play 21 vs another user, join the chat using the link below, then tap «Play vs user in chat» again.",
        "game21_pvp_main_active_exists": "You can't create a game request there — a game is in progress.",
        "game21_chat_command_active_exists": "There is an active game in {topic} right now.",
        "game21_chat_command_usage": "Use this format: <code>/21 10</code>",
        "checkers_chat_command_usage": "Use this format: <code>/checkers 10</code>",
        "kmb_chat_command_usage": "Use this format: <code>/kmb 10 3</code>, where 3 is target wins.",
        "info_command_text": (
            "<b>Bot commands</b>\n\n"
            "<code>/info</code> — show this message.\n"
            "<code>/21 10</code> — create a PvP 21 game with a 10 PLN bet.\n"
            "<code>/checkers 10</code> — create a checkers game with a 10 PLN bet.\n"
            "<code>/kmb 10 3</code> — create an RPS game with a 10 PLN bet, first to 3 wins.\n"
            "<code>/back</code> — cancel current input in private chat.\n\n"
            "Old formats also work: <code>/play21:10</code>, "
            "<code>/checkers:10</code>, <code>/kmb:10:3</code>, <code>/rps 10 3</code>."
        ),
        "game21_pvp_active_exists": "This slot already has a game or search.",
        "game21_pvp_self_accept_forbidden": "You cannot accept your own request.",
        "game21_pvp_search_post": "{user} looks for a 21 opponent\n\nBet: {amount} PLN\nWin up to: {win} PLN\n\nBalance in bot {bot_link}",
        "game21_pvp_btn_accept": "Accept",
        "game21_pvp_match_title": "Game 21",
        "game21_pvp_match_started_in_topic": "Game 21 started in {room}",
        "game21_pvp_match_prize": "<b>Payout: {win} PLN</b>",
        "game21_pvp_match_rules_heading": "Rules:",
        "game21_pvp_rules_body": (
            "Each rolls 🎲 once — lower roll goes first. "
            "Then take turns; get as close to 21 as you can without going over. "
            "When allowed, you can tap Stop. "
            "After both finish or bust, totals are compared; a draw is possible."
        ),
        "game21_pvp_started": "Game 21\n{p1}\n{p2}\n\nBet: {amount} PLN · win up to {win} PLN\n{bot_link}",
        "game21_pvp_general_started_notice": "A game of 21 between {p1} and {p2} has started in <b>{room}</b>.",
        "game21_pvp_topic_started_notice": "A game of 21 between {p1} and {p2} has started.\n\nPrize: {prize} PLN.",
        "game21_pvp_decide_first": "{players} — roll 🎲 once each (lower starts).",
        "game21_pvp_decide_roll_result": "{name} rolled {value}",
        "game21_pvp_decide_tie": "Tie on rolls. Roll again.",
        "game21_pvp_turn_prompt": "{name}, your turn. Roll 🎲",
        "game21_pvp_player_result": "{name}: {total}",
        "game21_pvp_player_busted": "{name}: {total} — bust!",
        "game21_pvp_player_blackjack": "{name} — 21!",
        "game21_pvp_player_can_stop": "{name}: {total}. Stop or roll again.",
        "game21_pvp_stop_announce": "{name} stopped at {total}",
        "game21_pvp_not_your_turn_stop": "It is {name}'s turn now.",
        "game21_pvp_stop_only_on_equal": "Stop is only when totals are equal.",
        "game21_pvp_winner": "Winner: {name}\nPayout {payout} PLN · {bot_link}",
        "game21_pvp_draw": "Draw. Refund {amount} PLN · {bot_link}",
        "game21_pvp_pm_bet_deducted": "Bet deducted: {amount} PLN.",
        "game21_pvp_search_not_accepted": "No one accepted. Refund {amount} PLN.",
        "game21_pvp_topic_forbidden": "This topic is not available for play.",
        "game21_pvp_topics_restricted_empty": "There are no topics allowed by the admin for games in this chat.",
        # ---- Chats settings ----
        "admin_chats_title": "💬 <b>Connected chats</b>",
        "admin_chats_empty": "No chats yet.",
        "admin_chats_list_line": "• <code>{chat_id}</code> · {title}",
        "admin_chats_btn_add": "➕ Add chat",
        "admin_chats_btn_delete": "🗑 Delete chat",
        "admin_chats_btn_game_topics": "📋 Game topics",
        "admin_chats_topics_choose_chat": "Pick a chat to configure which forum topics allow games (21 PvP and dice games):",
        "admin_chats_topics_not_forum": "This chat is not a forum supergroup with topics — nothing to configure.",
        "admin_chats_topics_chat_unavailable": "Could not open the chat.",
        "admin_chats_topics_body_open": (
            "📋 <b>Game topics</b>: {title}\n\n"
            "No restrictions now — 21 PvP and game creation are allowed in all known topics and the main chat.\n\n"
            "Tap «Enable topic limits» to choose where play is allowed (the list will be filled with current topics; uncheck what you do not need)."
        ),
        "admin_chats_topics_body_restricted": (
            "📋 <b>Game topics</b>: {title}\n\n"
            "An allowlist is on. Games are only where ✅ is set.\n\n"
            "«Remove limits» allows all topics again."
        ),
        "admin_chats_topics_btn_enable": "Enable topic limits",
        "admin_chats_topics_btn_disable": "Remove limits (all topics)",
        "admin_chats_enter_button_title": (
            "Send the <b>button label</b> — users will see it when picking a chat for a game. "
            "The same text will be stored for <b>ru / en / uk / pl</b> for now; you can set per-language "
            "labels later.\n\n"
            "Up to 200 characters."
        ),
        "admin_chats_invalid_button_title": "❌ Send a non-empty label (max 200 characters).",
        "admin_chats_enter_chat_id": (
            "Send the <b>chat ID</b> (e.g. <code>-1001234567890</code>).\n\n"
            "To find the ID: add the bot to the group and forward any message from there to "
            "<a href=\"https://t.me/userinfobot\">@userinfobot</a>, or use a bot like getidsbot."
        ),
        "admin_chats_invalid_id": "❌ Invalid format. Send an integer starting with <code>-100</code>.",
        "admin_chats_already_added": "⚠️ This chat is already connected.",
        "admin_chats_added": "✅ Chat <code>{chat_id}</code> connected.",
        "admin_chats_invite_ok": "✅ Invite link was created automatically.",
        "admin_chats_invite_link_failed": (
            "⚠️ Could not create an invite link: make sure the bot is an <b>admin</b> in the chat "
            "with permission to invite users (or that the group allows invite links)."
        ),
        "admin_chats_session_lost": "⚠️ Add-chat session was reset. Tap «Add chat» again.",
        "admin_chats_delete_choose": "Choose a chat to delete:",
        "admin_chats_delete_confirm": "Delete chat <code>{chat_id}</code>?",
        "admin_chats_deleted": "✅ Chat deleted.",
        "admin_chats_delete_none": "There are no connected chats to delete.",
        # ---- Games create FSM ----
        "admin_game_no_chats": "⚠️ Connect at least one chat first: Bot settings → Chats.",
        "admin_game_pick_chat": "Which chat to announce the game in?",
        "admin_game_pick_forum_topic": "📂 <b>Forum topic</b>\n\nPick the topic where the game will run (announcement, rounds, throws).\n\nIf a button shows «Topic · id …», the bot only knows Telegram’s internal thread id (plain messages don’t include the visible title). Rename the topic once in the group — the bot will pick up the new name.",
        "admin_game_pick_forum_topic_empty": "📂 <b>Forum topic</b>\n\nThe list is empty: Telegram does not expose forum topics via the Bot API; the bot learns threads from messages and service events.\n\nIf topics already exist: send any message in each topic you need (or rename a topic once), then tap «🔄 …».\n\nYou can skip and run the game in the main chat without a topic.",
        "admin_game_forum_skip": "No topic (main chat)",
        "admin_game_forum_reload": "🔄 Refresh topic list",
        "admin_game_forum_thread_placeholder": "Topic · id {id}",
        "admin_game_forum_reload_toast": "List updated",
        "admin_game_forum_reload_lost": "⚠️ Session lost. Start creating the game again.",
        "admin_game_topic_forbidden": "This topic is not on the allowlist for this chat.",
        "admin_game_pick_type": "🎯 <b>Game type</b>\n\nPick the throw kind:",
        "admin_game_type_dice": "🎲 Dice",
        "admin_game_type_bowling": "🎳 Bowling",
        "admin_game_type_darts": "🎯 Darts",
        "admin_game_type_any": "🎲 🎳 🎯 (any throw)",
        "admin_game_name_prefix": "Game",
        "admin_game_enter_participants": "👥 <b>Participants</b>\n\nSend min and max separated by «/» or «-».\nExample: <code>10/100</code>",
        "admin_game_invalid_participants": "❌ Format: <code>min/max</code>, both positive integers, min ≤ max.",
        "admin_game_enter_prizes": "🏆 <b>Prizes</b>\n\nSend prize amounts in PLN, one per line. Number of lines = number of prize places.\nExample:\n<code>20\n10\n5</code>\n\nWinners will be credited automatically.",
        "admin_game_invalid_prizes": "❌ Prizes must be positive numbers (e.g. <code>20</code> or <code>10.5</code>), one per line.",
        "admin_game_prizes_more_than_max": "❌ Prize places ({n}) exceed max participants ({max}).",
        "admin_game_enter_min_topup": "💰 <b>Signup requirement: minimum top-ups</b>\n\nFormats:\n• <code>0</code> — no requirement\n• <code>100</code> — topped up at least 100 PLN all time\n• <code>100 : 01.01.2026</code> — topped up at least 100 PLN since that date",
        "admin_game_invalid_min_topup": "❌ Format: a number (<code>100</code>) or number + date with «:» (<code>100 : 01.01.2026</code>).",
        "admin_game_enter_entry_fee": "💵 <b>Entry fee</b>\n\nSend amount in PLN (0 = free).",
        "admin_game_invalid_entry_fee": "❌ Send a number ≥ 0 (e.g. <code>0</code> or <code>5</code>).",
        "admin_game_enter_datetime": "🗓 <b>Start date & time</b>\n\nFormats:\n• <code>DD.MM.YYYY HH:MM</code>\n• <code>HH:MM</code> (today)",
        "admin_game_invalid_datetime": "❌ Could not parse date/time. Example: <code>25.12.2026 19:30</code>.",
        "admin_game_datetime_in_past": "❌ Start time must be in the future.",
        "admin_game_topup_since_after_start": "❌ Top-up period start is after the game start. Adjust condition or date.",
        "admin_game_preview_title": "📋 <b>Game preview</b>",
        "admin_game_preview_chat": "Chat: <b>{chat}</b>",
        "admin_game_preview_forum_topic": "Topic: <b>{topic}</b>",
        "admin_game_preview_type": "Type: <b>{type}</b>",
        "admin_game_preview_participants": "Participants: <b>{min}–{max}</b>",
        "admin_game_preview_prizes": "Prizes:",
        "admin_game_preview_min_topup_none": "Requirement: <b>none</b>",
        "admin_game_preview_min_topup_alltime": "Requirement: top-ups from <b>{n} PLN</b> (all time)",
        "admin_game_preview_min_topup_period": "Requirement: top-ups from <b>{n} PLN</b> since <b>{since}</b>",
        "admin_game_preview_pay_free": "Type: <b>free</b>",
        "admin_game_preview_pay_paid": "Type: <b>paid</b>, fee <b>{fee} PLN</b>",
        "admin_game_preview_datetime": "Start: <b>{datetime}</b>",
        "admin_btn_confirm_create": "✅ Create",
        "admin_btn_cancel_create": "❌ Cancel",
        "admin_game_created": "✅ Game #{id} created.",
        "admin_game_create_cancelled": "❌ Cancelled.",
        # ---- Game lists ----
        "admin_games_active_title": "🟢 <b>Active games</b>",
        "admin_games_past_title": "📚 <b>Past games</b>",
        "admin_games_empty_active": "No active games right now.",
        "admin_games_empty_past": "No past games yet.",
        "admin_game_detail_title": "🎯 <b>Game #{id}</b>",
        "admin_game_detail_status": "Status: <b>{status}</b>",
        "admin_game_detail_participants_count": "Registered: <b>{count}/{max}</b> (min {min})",
        "admin_game_status_draft": "awaiting start",
        "admin_game_status_active": "in progress",
        "admin_game_status_finished": "finished",
        "admin_game_status_cancelled": "cancelled",
        # ---- Announcement ----
        "game_announce_title": "🎯 Game for <b>{chat}</b> is set",
        "game_announce_date": "Date: <b>{date}</b>",
        "game_announce_participants_range": "Participants: <b>{min}–{max}</b>",
        "game_announce_conditions": "<b>Conditions:</b>",
        "game_announce_cond_min_topup_alltime": "• min top-ups: <b>{n} PLN</b> (all time)",
        "game_announce_cond_min_topup_period": "• min top-ups: <b>{n} PLN</b> (since {since} until start)",
        "game_announce_cond_pay_free": "• free",
        "game_announce_cond_pay_paid": "• paid, entry fee <b>{fee} PLN</b>",
        "game_announce_cond_none": "• no extra conditions",
        "game_announce_prizes": "<b>Prizes:</b>",
        "game_announce_signup_link": "Sign up via {bot_link}",
        "game_announce_signup_no_link": "Sign up — message the bot in DM.",
        "game_btn_signup": "🎮 Sign up",
        "game_reminder_5min": "⏳ About 5 minutes until the game in «{chat_title}».",
        "game_cancelled_not_enough_players_dm": "Game cancelled: only {current} of {required} players signed up.",
        "game_cancelled_refund_full_fee": "Entry fee {fee} PLN was refunded to your balance.",
        "game_start_header": "<b>Conditions:</b>\n{conditions}\n\n<b>Prizes:</b>\n{prizes}",
        "game_start_cond_min_topup_period": "• min top-ups: {n} PLN (from {since} until {until})",
        "game_start_cond_min_topup_alltime": "• min top-ups: {n} PLN (all time)",
        "game_start_cond_paid": "• paid game, entry fee {fee} PLN",
        "game_start_cond_free": "• free game",
        "game_start_cond_none": "• no extra conditions",
        "game_rules_block": (
            "Rules:\n"
            "1) Rounds in turn order, 3 throws each.\n"
            "2) You may throw 🎲 🎳 🎯 (dice message or the same emojis as text).\n"
            "3) After a round, passing score is the integer average among players who threw.\n"
            "4) Missed turns get a catch-up pass.\n"
            "5) Final round and tie-break follow bot logic."
        ),
        "game_round1_list_intro": "Round 1!",
        "round_list_participants": "Players",
        "round_score_pending": "…",
        "round_score_eliminated": "out",
        "round_your_result": "Your throw: {value}",
        "round_throw_2_more": "Throw 2 more times {emoji}",
        "round_throw_1_more": "Throw 1 more time {emoji}",
        "round_third_throw_done": "{result_line}\n{name}, your round total: <b>{total}</b>",
        "round_throw_prompt": "{name}, make 3 throws with any emoji: {emoji}",
        "round_turn_60sec_left": "{name}, 1 minute left for your throw.",
        "round_participant_skipped": "{name} — turn skipped.",
        "round_participants_missed": "Players with 0 in this round:",
        "round_catchup_5min": "You have time for 3 throws (faster mode).",
        "round_1_finished": "Round 1 finished.",
        "round_N_finished": "Round {round} finished.",
        "round_passing_score": "Passing score: {score}",
        "round_list_passed": "Advancing to the next round:",
        "round_list_passed_final": "Advancing to the final round:",
        "round_results_header": "Results:",
        "round_tiebreak": "Tie-break!",
        "round_tiebreak_for": "To decide: {places}",
        "round_tiebreak_place_one": "{n} place",
        "round_tiebreak_place_span": "places {a}–{b}",
        "round_tiebreak_throw": "{name}, make 1 throw {emoji}",
        "round_tiebreak_result": "{name} — tie-break throw: {value}",
        "round_final_finished": "Final round finished.",
        "round_winners": "Winners:",
        "game_sponsor_line": "Sponsor: {bot_link}",
        "game_dm_prize_won": "🎉 You placed {place}! <b>{amount} PLN</b> credited to your balance.",
        "game_signup_no_games": "No games open for signup right now.",
        "game_signup_list_title": "Open signups (tap a game):",
        "game_signup_list_item": "#{id} {when} — {chat}",
        "game_signup_btn_join": "✅ Join",
        "game_signup_btn_leave": "🚫 Leave",
        "game_signup_not_found": "Game not found.",
        "game_signup_not_draft": "Signup is closed (game is not in draft).",
        "game_signup_started": "The game already started or signup closed.",
        "game_signup_full": "No free slots.",
        "game_signup_min_topup": "Not enough top-ups: need {need} PLN, you have {have} PLN (per game rules).",
        "game_signup_low_balance": "Not enough balance: fee {fee} PLN, your balance {balance} PLN.",
        "game_signup_already_in": "You are already registered.",
        "game_signup_ok": "You are registered.",
        "game_signup_left": "You left the game.",
        "game_signup_not_in": "You were not registered.",
        "game_signup_card": (
            "🎯 <b>Game #{id}</b>\n"
            "Chat: {chat}\n"
            "Start: <b>{start}</b>\n"
            "Players: <b>{count}</b> / {max_p} (min {min_p})\n\n"
            "<b>Conditions:</b>\n{conditions}\n\n"
            "<b>Prizes (PLN):</b>\n{prizes}"
        ),
        "game_signup_cond_topup_period": "• top-ups from {n} PLN since {since}",
        "game_signup_cond_topup_alltime": "• top-ups from {n} PLN (all time)",
        "game_signup_cond_paid": "• entry fee {fee} PLN",
        "game_signup_cond_free": "• free",
        "game_signup_cond_none": "—",
        "admin_pay_btn_activate": "▶️ Start",
        "admin_pay_btn_deactivate": "⏹ Stop",
        "admin_pay_btn_edit_proxy": "🌐 Edit proxy",
        "admin_pay_btn_edit_blik": "📱 Edit BLIK",
        "admin_pay_btn_edit_limit": "📊 Edit limit",
        "admin_pay_btn_rescan": "🔁 Re-scan recent emails",
        "admin_pay_btn_delete": "🗑 Delete",
        "admin_pay_btn_delete_confirm": "✅ Confirm delete",
        "admin_pay_btn_cancel": "❌ Cancel",
        "admin_pay_btn_bank_custom": "✏️ Other",
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
        "topup_enter_amount": "💳 <b>Поповнення балансу</b>\n\nВведіть суму поповнення в PLN (від {min} до {max} PLN):",
        "topup_invalid_amount": "❌ Невірна сума. Введіть число (наприклад 50).",
        "topup_out_of_range": "❌ Сума повинна бути від {min} до {max} PLN.",
        "topup_no_accounts": "⚠️ Поповнення тимчасово недоступне — немає активних платіжних акаунтів. Спробуйте пізніше.",
        "topup_order_created": (
            "💳 <b>Заявку на поповнення створено</b>\n\n"
            "Сума: <b>{amount} PLN</b>\n"
            "Номер заявки: <code>{order_id}</code>\n\n"
            "📱 Зробіть BLIK-переказ на номер:\n<code>{blik}</code>\n\n"
            "⚠️ <b>У призначенні платежу обов'язково вкажіть код:</b>\n<code>{order_id}</code>\n\n"
            "Після отримання платежу баланс зарахується автоматично."
        ),
        "topup_btn_cancel_order": "❌ Скасувати заявку",
        "topup_order_cancelled": "❌ Заявку <code>{order_id}</code> скасовано.",
        "topup_order_not_found": "❌ Заявку не знайдено або вже закрито.",
        "btn_withdraw": "💸 Запросити виведення",
        "btn_cancel_withdraw": "❌ Скасувати виведення",
        "withdraw_enter_amount": (
            "💸 <b>Виведення коштів</b>\n\n"
            "Введіть суму у PLN (мінімум {min} PLN).\n"
            "Комісія: <b>{fee}%</b>\n"
            "⏱ Виведення протягом 24 годин."
        ),
        "withdraw_invalid_amount": "❌ Невірна сума. Введіть число (наприклад 150).",
        "withdraw_below_min": "❌ Виведення доступне від {min} PLN.",
        "withdraw_not_enough": "❌ Недостатньо коштів. Ваш баланс: {balance} PLN.",
        "withdraw_enter_blik": "📱 Введіть номер BLIK (мінімум 9 цифр):",
        "withdraw_invalid_blik": "❌ Невірний формат BLIK. Мінімум 9 цифр.",
        "withdraw_confirm": (
            "💸 <b>Підтвердження виведення</b>\n\n"
            "З балансу: <b>{amount} PLN</b>\n"
            "Комісія: <b>{fee}%</b> ({fee_amount} PLN)\n"
            "До виплати: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "Підтвердити виведення?"
        ),
        "withdraw_btn_yes": "✅ Так",
        "withdraw_btn_no": "❌ Ні",
        "withdraw_created": (
            "✅ <b>Заявку на виведення створено</b>\n\n"
            "Номер: <code>#{id}</code>\n"
            "До виплати: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "⏱ Виведення протягом 24 годин."
        ),
        "withdraw_cancel_ask": "❓ Ви впевнені, що хочете скасувати виведення <code>#{id}</code>?",
        "withdraw_cancelled": "✅ Виведення <code>#{id}</code> скасовано. Кошти повернено на баланс.",
        "withdraw_not_pending": "❌ Заявку не знайдено або вже опрацьовано.",
        "withdraw_already_pending": "⚠️ У вас вже є активна заявка на виведення. Скасуйте її, щоб створити нову.",
        "withdraw_admin_message": (
            "🏦 <b>Новий запит на виведення</b>\n\n"
            "👤 {mention}{username}\n"
            "🆔 <code>{user_id}</code>\n"
            "💸 Запит: <b>{amount} PLN</b>\n"
            "🧾 Комісія: {fee}% ({fee_amount} PLN)\n"
            "💵 До виплати: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>"
        ),
        "withdraw_admin_btn_approve": "✅ Прийняти",
        "withdraw_admin_approved": "✅ <b>ОПЛАЧЕНО</b>",
        "withdraw_admin_cancelled": "❌ <b>СКАСОВАНО</b>",
        "withdraw_approved_user": (
            "✅ Ваше виведення <code>#{id}</code> на суму <b>{payout} PLN</b> надіслано."
        ),
        "cabinet_title": "💼 Особистий кабінет",
        "cabinet_balance": "💰 Баланс: <b>{balance} PLN</b>",
        "cabinet_level": "⭐ Рівень: <b>{level}</b>",
        "cabinet_next_level": "📈 До рівня {level}: <b>{amount} PLN</b>",
        "cabinet_next_level_max": "📈 Наступний рівень: <b>максимальний рівень досягнуто</b>",
        "cabinet_referral_link": "🔗 Ваше реферальне посилання:\n<code>{link}</code>",
        "btn_referral_program": "🤝 Реферальна програма",
        "btn_return_main": "повернутися на головну",
        "btn_checkers": "⚪️ Шашки ⚫️",
        "btn_kmb": "👊✌️🤚 КНБ 👊✌️🤚",
        "input_cancel_hint": "натисніть /back для скасування",
        "referral_empty": "Поки немає рефералів.",
        "referral_line": "• {name} — {profit} PLN",
        "referral_program_text": (
            "🤝 <b>Реферальна програма</b>\n\n"
            "Ваше посилання:\n<code>{link}</code>\n\n"
            "Умови: запрошуйте гравців за посиланням і отримуйте <b>{percent}%</b> "
            "з кожної виграної ставки вашого реферала\n\n"
            "<b>Ваші реферали:</b>\n{referrals}"
        ),
        "admin_21_summary": (
            "♠️ <b>Режим 21</b>\n\n"
            "-------------------------------------------\n"
            "Проти БОТА:\n\n"
            "Комісія: {bot_fee}%\n\n"
            "Усього ігор з БОТОМ: {bot_total}\n"
            "БОТ виграв: {bot_won_count} ігор, {bot_won_sum} PLN\n"
            "БОТ програв: {bot_lost_count} ігор, {bot_lost_sum} PLN\n"
            "Нічиї: {bot_draw_count}\n\n"
            "Прибуток БОТА: {bot_profit_sum} PLN\n\n"
            "-------------------------------------------\n"
            "Між користувачами:\n\n"
            "Комісія: {users_fee}%\n\n"
            "Усього PvP ігор: {pvp_total}\n"
            "Прибуток з комісії: {pvp_commission_sum} PLN\n\n"
            "-------------------------------------------\n"
            "Загальний прибуток: {total_profit_sum} PLN"
        ),
        "admin_btn_checkers_fee": "⚪️ Комісія шашок ⚫️",
        "admin_btn_kmb_fee": "👊✌️🤚 Комісія КНБ",
        "admin_btn_levels": "⭐ Налаштування рівнів",
        "admin_btn_referral_fee": "🤝 Комісія рефералів",
        "admin_checkers_btn_disable": "Вимкнути",
        "admin_checkers_btn_enable": "Увімкнути / Вимкнути",
        "admin_checkers_btn_rules": "Правила",
        "admin_checkers_chat_off": "Шашки в «{title}»: увімкнути",
        "admin_checkers_chat_on": "Шашки в «{title}»: вимкнути",
        "admin_checkers_enable_title": "⚪️ Шашки ⚫️\n\nОберіть чат, щоб увімкнути або вимкнути гру:",
        "admin_checkers_fee_title": "⚪️ <b>Комісія шашок</b> ⚫️\n\nПоточне значення: <b>{percent}%</b>\n\nВведіть новий відсоток:",
        "admin_checkers_fee_updated": "✅ Комісію шашок оновлено: <b>{percent}%</b>",
        "admin_checkers_rules_empty": "Правила ще не задані.",
        "admin_checkers_rules_prompt": "Введіть правила шашок російською. Бот збереже їх і перекладе для інших мов.",
        "admin_checkers_rules_title": "⚪️ Правила шашок ⚫️\n\n{rules}",
        "admin_checkers_title": "⚪️ Шашки ⚫️\n\nкомісія: {commission}%\n\nУсього ігор у шашки: {total_games}\nПрибуток з комісії: {commission_sum} PLN",
        "admin_kmb_btn_enable": "Увімкнути / Вимкнути",
        "admin_kmb_btn_rules": "Правила",
        "admin_kmb_chat_off": "КНБ в «{title}»: увімкнути",
        "admin_kmb_chat_on": "КНБ в «{title}»: вимкнути",
        "admin_kmb_enable_title": "👊✌️🤚 КНБ 👊✌️🤚\n\nОберіть чат, щоб увімкнути або вимкнути гру:",
        "admin_kmb_fee_title": "👊✌️🤚 <b>Комісія КНБ</b>\n\nПоточне значення: <b>{percent}%</b>\n\nВведіть новий відсоток:",
        "admin_kmb_fee_updated": "✅ Комісію КНБ оновлено: <b>{percent}%</b>",
        "admin_kmb_rules_empty": "Правила ще не задані.",
        "admin_kmb_rules_prompt": "Введіть правила КНБ:",
        "admin_kmb_rules_saved": "✅ Правила КНБ збережено.",
        "admin_kmb_rules_title": "Правила КНБ\n\n{rules}",
        "admin_kmb_title": "КНБ\n\nКомісія: {commission}%\n\nУнікальних користувачів: {unique_users}\nУсього ігор у КНБ: {total_games}\nПрибуток з комісії: {commission_sum} PLN",
        "admin_levels_btn_disable": "Вимкнути",
        "admin_levels_btn_enable": "Увімкнути",
        "admin_levels_btn_referral": "Бонус рефералів",
        "admin_levels_btn_required": "Умова отримання",
        "admin_levels_btn_reward": "Нагорода на баланс",
        "admin_levels_btn_title": "Назва",
        "admin_levels_btn_withdraw": "Знижка на вивід",
        "admin_levels_detail": (
            "⭐ <b>Рівень {level}</b>\n\n"
            "Назва: <b>{title}</b>\n"
            "Статус: {status}\n\n"
            "Потрібно виграних ставок: <b>{required} PLN</b>\n"
            "Нагорода на баланс: <b>{reward} PLN</b>\n"
            "Знижка до комісії виводу: <b>{withdraw}%</b>\n"
            "Надбавка до реферального %: <b>{referral}%</b>"
        ),
        "admin_levels_invalid_amount": "❌ Введіть додатне число або 0.",
        "admin_levels_invalid_percent": "❌ Введіть відсоток від 0 до 100.",
        "admin_levels_invalid_text": "❌ Текст не може бути порожнім.",
        "admin_levels_not_found": "❌ Рівень не знайдено.",
        "admin_levels_prompt_referral": "Введіть надбавку до реферального відсотка за рівень {level} (0-100):",
        "admin_levels_prompt_required": "Введіть суму виграних ставок для отримання рівня {level}:",
        "admin_levels_prompt_reward": "Введіть нагороду на баланс за рівень {level}:",
        "admin_levels_prompt_title": "Введіть назву для рівня {level}:",
        "admin_levels_prompt_withdraw": "Введіть знижку до комісії виводу за рівень {level} (0-100):",
        "admin_levels_saved": "✅ Збережено.",
        "admin_levels_status_off": "⚪ вимкнено",
        "admin_levels_status_on": "🟢 увімкнено",
        "admin_levels_title": "⭐ <b>Налаштування рівнів</b>\n\nОберіть рівень для редагування:",
        "admin_referral_fee_title": "🤝 <b>Комісія рефералів</b>\n\nПоточне значення: <b>{percent}%</b>\n\nВведіть новий відсоток:",
        "admin_referral_fee_updated": "✅ Комісію рефералів оновлено: <b>{percent}%</b>",
        "admin_user_amount_invalid": "❌ Введіть додатну суму.",
        "admin_user_banned": "Користувача заблоковано.",
        "admin_user_btn_ban": "🚫 Заблокувати",
        "admin_user_btn_find_other": "🔎 Знайти іншого користувача",
        "admin_user_btn_referral_percent": "🤝 Змінити реферальний %",
        "admin_user_btn_topup": "💳 Поповнити баланс",
        "admin_user_btn_unban": "✅ Розблокувати",
        "admin_user_btn_withdraw_percent": "💸 Змінити комісію на вивід",
        "admin_user_card": (
            "👤 <b>{label}</b>\n\n"
            "ID: <code>{user_id}</code>\n"
            "Username: {username}\n"
            "Статус: {status}\n"
            "Баланс: <b>{balance} PLN</b>\n"
            "Рівень: <b>{level}</b>\n"
            "Виграних ставок для рівня: {level_progress} PLN\n"
            "Бонус рівня: вивід −{level_withdraw_discount}%, реферали +{level_referral_bonus}%\n"
            "Мова: {language}\n"
            "Запросив: {referrer}\n\n"
            "Комісія виводу: <b>{withdraw_percent}%</b> ({withdraw_source})\n"
            "Реферальний %: <b>{referral_percent}%</b> ({referral_source})\n\n"
            "Рефералів: {referrals_count}\n"
            "Прибуток від рефералів: {referrals_profit} PLN"
        ),
        "admin_user_not_found": "❌ Користувача не знайдено. Введіть ID або username ще раз.",
        "admin_user_percent_global": "загальна {percent}%",
        "admin_user_percent_invalid": "❌ Введіть відсоток від 0 до 100 або <code>-</code> для скидання.",
        "admin_user_percent_personal": "персональна {percent}%",
        "admin_user_percent_reset": "без персональних налаштувань",
        "admin_user_referral_bonus": "загальна {global_percent}% + надбавка {bonus}%",
        "admin_user_referral_done": "✅ Надбавку до реферального відсотка оновлено: <b>{percent}</b>.",
        "admin_user_referral_prompt": (
            "Введіть надбавку до реферального відсотка для {user} / <code>{user_id}</code>.\n\n"
            "Приклад: якщо загальний реферальний відсоток 1%, а ви введете <code>1</code>, підсумок буде 2%.\n\n"
            "Надішліть відсоток від 0 до 100 або <code>-</code>, щоб прибрати персональну надбавку."
        ),
        "admin_user_search_prompt": "👥 Введіть ID користувача або username:",
        "admin_user_status_active": "🟢 активний",
        "admin_user_status_banned": "🔴 заблокований",
        "admin_user_topup_done": "✅ Баланс поповнено на <b>{amount} PLN</b>.",
        "admin_user_topup_prompt": "Введіть суму поповнення для {user} / <code>{user_id}</code>:",
        "admin_user_unbanned": "Користувача розблоковано.",
        "admin_user_withdraw_discount": "загальна {global_percent}% − знижка {discount}%",
        "admin_user_withdraw_done": "✅ Знижку до комісії виводу оновлено: <b>{percent}</b>.",
        "admin_user_withdraw_prompt": (
            "Введіть знижку до комісії виводу для {user} / <code>{user_id}</code>.\n\n"
            "Приклад: якщо загальна комісія 10%, а ви введете <code>1</code>, підсумок буде 9%.\n\n"
            "Надішліть відсоток від 0 до 100 або <code>-</code>, щоб прибрати персональну знижку."
        ),
        "checkers_active_notice": "У вас уже є активна гра або пошук гри.",
        "checkers_bad_move": "Так ходити не можна.",
        "checkers_board_text": "⚪️ <b>Шашки</b> ⚫️\n⚪ {white}\n⚫ {black}\n\nБанк: {amount} PLN\nХід: {turn}",
        "checkers_btn_accept": "Прийняти гру",
        "checkers_choose_chat": "Оберіть чат для гри в шашки:",
        "checkers_choose_topic": "Оберіть ігрову кімнату (🟢 вільна, 🔴 зайнята):",
        "checkers_confirm": "Ставка: {amount} PLN\nСума виграшу: {win} PLN\nПочати пошук суперника?",
        "checkers_decide_white": "{players} — киньте кубик 🎲 по одному разу. У кого більше, грає білими.",
        "checkers_disabled": "Гру в шашки тимчасово вимкнено.",
        "checkers_draw_countdown": (
            "У грі вже {no_capture} ходів не було жодного взяття.\n"
            "Якщо протягом 10 ходів (по 5 на кожного) не буде взяття, буде нічия.\n\n"
            "До нічиї залишилось ходів: {remaining}"
        ),
        "checkers_draw_countdown_reset": "Шашку взяли. Відлік до нічиї скинуто.",
        "checkers_draw_result": "Гру завершено.\nНічия.\n\nСтавку {amount} PLN повернуто обом гравцям.",
        "checkers_enter_bet": "<b>{chat}</b>\nВаш баланс: {balance} PLN\nВведіть суму ставки:",
        "checkers_flood_wait": "Занадто швидко. Зачекайте {seconds} с.",
        "checkers_match_prize": "Сума виграшу: {win} PLN",
        "checkers_match_rules_heading": "Правила гри:",
        "checkers_match_started_in_topic": "Гру в шашки розпочато в {room}",
        "checkers_match_title": "Гра в шашки",
        "checkers_not_your_turn": "Зараз не ваш хід.",
        "checkers_rules_body": (
            "Білі ходять першими. Шашки ходять по діагоналі, обов'язкове взяття потрібно виконувати. "
            "Дамка ходить по діагоналі на будь-яку відстань. Якщо гравець не зробить хід за 2 хвилини, він програє."
        ),
        "checkers_search_cancelled_refund": "Скасовано.\nСуму ставки повернуто на баланс.",
        "checkers_search_post": "{user} шукає суперника в шашки.\nСтавка: {amount} PLN\nСума виграшу: {win} PLN",
        "checkers_search_started": "Пошук гри в шашки розпочато. Ставку {amount} PLN списано.",
        "checkers_search_timeout": "Ніхто не прийняв гру в шашки. Ставку {amount} PLN повернуто на баланс.",
        "checkers_turn_timeout_result": "Час на хід вичерпано.\n{loser} програв.\n\nПереможець: {winner}\nВиграш {payout} PLN зараховано на баланс.",
        "checkers_turn_timeout_warning": "{name}, у вас залишилась 1 хвилина на хід, інакше ви програєте.",
        "checkers_white_chosen": "{name} грає білими. Гра починається.",
        "checkers_winner": "Гру завершено.\nПереможець: {name}\n\nВиграш {payout} PLN зараховано на баланс.",
        "kmb_btn_accept": "Прийняти гру",
        "kmb_choice_saved": "Вибір прийнято.",
        "kmb_choose_chat": "Оберіть чат для гри в КНБ:",
        "kmb_choose_topic": "Оберіть ігрову кімнату (🟢 вільна, 🔴 зайнята):",
        "kmb_confirm": "Гра до {wins} перемог\nСтавка: {amount} PLN\nСума виграшу: {win} PLN\nПочати пошук суперника?",
        "kmb_enter_bet": "<b>{chat}</b>\nВаш баланс: {balance} PLN\nВведіть суму ставки:",
        "kmb_enter_wins": "<b>{chat}</b>\nДо скількох перемог граємо?\nВведіть число від 1 до 10:",
        "kmb_match_prize": "Сума виграшу: {win} PLN",
        "kmb_match_rules_heading": "Правила гри:",
        "kmb_match_started_in_topic": "Гру в Камінь/Ножиці/Папір розпочато в {room}",
        "kmb_match_title": "Гра в Камінь / Ножиці / Папір",
        "kmb_no_chats": "КНБ зараз недоступний: немає увімкнених чатів або тем.",
        "kmb_not_your_game": "Це не ваша гра.",
        "kmb_pick_done": "вибір зроблено",
        "kmb_pick_prompt": (
            "👊✌️🤚 <b>КНБ</b>\n\n"
            "Гра до {wins} перемог\n"
            "Рахунок: {p1_score} - {p2_score}\n\n"
            "{p1}: {p1_status}\n"
            "{p2}: {p2_status}\n\n"
            "Оберіть: камінь, ножиці чи папір."
        ),
        "kmb_pick_wait": "очікує вибору",
        "kmb_result_draw": (
            "Нічия.\n"
            "{p1}: {p1_choice}\n"
            "{p2}: {p2_choice}\n\n"
            "Рахунок: {p1_score} - {p2_score}\n"
            "Гра до {wins} перемог.\n\n"
            "Оберіть ще раз."
        ),
        "kmb_result_win": (
            "Гру завершено.\n"
            "Фінальний рахунок: {p1_score} - {p2_score}\n\n"
            "{p1}: {p1_choice}\n"
            "{p2}: {p2_choice}\n\n"
            "Переможець: {winner}\n"
            "Виграш {payout} PLN зараховано на баланс."
        ),
        "kmb_round_win": (
            "Раунд завершено.\n"
            "{p1}: {p1_choice}\n"
            "{p2}: {p2_choice}\n\n"
            "Раунд виграв: {winner}\n"
            "Рахунок: {p1_score} - {p2_score}\n\n"
            "Гра до {wins} перемог. Оберіть ще раз."
        ),
        "kmb_rules_body": (
            "Камінь б'є ножиці, ножиці ріжуть папір, папір накриває камінь. "
            "При однаковому виборі раунд — нічия і переграється."
        ),
        "kmb_search_cancelled_refund": "Скасовано.\nСуму ставки повернуто на баланс.",
        "kmb_search_post": "{user} шукає суперника в КНБ.\nГра до {wins} перемог\nСтавка: {amount} PLN\nСума виграшу: {win} PLN",
        "kmb_search_started": "Пошук гри в КНБ розпочато. Гра до {wins} перемог. Ставку {amount} PLN списано.",
        "kmb_search_timeout": "Ніхто не прийняв гру в КНБ. Ставку {amount} PLN повернуто на баланс.",
        "kmb_wins_invalid": "Невірна кількість перемог. Введіть число від 1 до 10.",
        "btn_signup": "Записатися на гру",
        "main_menu_chat_fallback": "💬 Чат",
        "btn_play_21_bot": "Грати в 21",
        "btn_casino": "🎰 Слот 🎰",
        "slot_enter_bet_with_balance": "Ваш баланс: {balance} PLN\nВведіть суму ставки (наприклад 1):",
        "slot_rules_block": "Правила та виплати:\n• 3 однакових — x4\n• 2 однакових — x1.1\n• Усі різні — програш",
        "slot_bet_invalid": "Невірна сума ставки. Введіть додатне число.",
        "slot_not_enough_balance": "Недостатньо коштів для ставки.",
        "slot_spin_prompt": "Ваш баланс: {balance} PLN\nСтавку {amount} PLN прийнято.\nТепер крутіть 🎰",
        "slot_balance_update_failed": "Не вдалося оновити баланс. Спробуйте ще раз.",
        "slot_combo_three": "3 однакових",
        "slot_combo_two": "2 однакових",
        "slot_combo_none": "усі різні",
        "slot_result_win": "Ваш баланс: {balance} PLN\nРезультат 🎰: {combo}\nСтавка {bet} PLN множиться на x{mult}\nВиплата: {payout} PLN",
        "slot_result_lose": "Ваш баланс: {balance} PLN\nРезультат 🎰: {combo}\nСтавка {bet} PLN згоріла.",
        "slot_disabled": "Слот зараз вимкнено.",
        "admin_slot_stats_text": "Слот:\nБОТ виграв: {bot_won_sum} PLN\nБОТ програв: {bot_lost_sum} PLN\nЗагальний прибуток БОТа: {bot_profit_sum} PLN",
        "admin_slot_mode_text": (
            "🎰 <b>Режим слот</b>\n\n"
            "{status}\n\n"
            "-------------------------------------------\n"
            "Усього ігор: {total_games}\n"
            "унікальних користувачів: {unique_users}\n"
            "виграно користувачами: {users_won_sum} PLN\n"
            "програно користувачами: {users_lost_sum} PLN\n"
            "загальний прибуток бота: {bot_profit_sum} PLN\n"
            "-------------------------------------------"
        ),
        "admin_slot_btn_enable": "Увімкнути",
        "admin_slot_btn_disable": "Вимкнути",
        "admin_slot_btn_rules": "Правила",
        "admin_slot_rules_prompt": "Введіть правило для Слота:",
        "admin_slot_rules_current": "Поточне правило:\n{rules}",
        "admin_slot_rules_empty": "❌ Правило не може бути порожнім. Введіть текст правила.",
        "admin_slot_rules_saved": "✅ Правило Слота збережено.",
        "btn_admin": "Адмінка",
        "btn_lang": "🌐",
        "btn_main": "🏠 Головна",
        "btn_back": "← Назад",
        "admin_title": "Адмінка",
        "admin_no_access": "⛔ Немає доступу",
        "admin_btn_games": "🎯 Ігри",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Слот",
        "admin_btn_checkers": "⚪️ Шашки ⚫️",
        "admin_btn_kmb": "🪖 КМБ",
        "admin_btn_stats": "📊 Статистика",
        "admin_stats_title": "📊 <b>Статистика</b>",
        "admin_stats_btn_users": "👥 Користувачі",
        "admin_stats_users_title": (
            "👥 <b>Користувачі</b>\n\n"
            "Усього користувачів: {total}\n"
            "Активних: {active}\n"
            "Заблокованих: {banned}\n"
            "З балансом: {with_balance}\n"
            "Загальний баланс: {balance_sum} PLN"
        ),
        "admin_btn_bot_settings": "⚙️ Налаштування бота",
        "admin_games_title": "🎯 <b>Ігри</b>",
        "admin_btn_create_game": "➕ Створити гру",
        "admin_btn_active_games": "🟢 Поточні ігри",
        "admin_btn_past_games": "📚 Минулі ігри",
        "admin_wip": "🚧 У розробці",
        "admin_settings_title": "⚙️ Налаштування бота",
        "admin_btn_payments": "💳 Налаштування платежів",
        "admin_btn_fees": "💸 Налаштування комісій",
        "admin_btn_withdraw_fee": "💸 Комісія виводу",
        "admin_btn_slot_fee": "🎰 Комісія Слота",
        "admin_fees_title": "💸 <b>Налаштування комісій</b>",
        "admin_pay_title": "<b>MBanks</b> — акаунти:",
        "admin_pay_empty": "<b>MBanks</b>\nАкаунтів немає.",
        "admin_pay_btn_add": "➕ Додати акаунт",
        "admin_pay_btn_withdraw_fee": "💸 Комісія виводу",
        "admin_withdraw_fee_title": "💸 <b>Комісія виводу</b>\n\nПоточне значення: <b>{percent}%</b>\n\nВведіть новий відсоток (наприклад <code>5</code> або <code>2.5</code>):",
        "admin_withdraw_fee_invalid": "❌ Невірний формат. Введіть число від 0 до 100 (наприклад <code>5</code> або <code>2.5</code>).",
        "admin_withdraw_fee_updated": "✅ Комісію виводу оновлено: <b>{percent}%</b>",
        "admin_slot_fee_title": "🎰 <b>Комісія Слота</b>\n\nПоточне значення: <b>{percent}%</b>\n\nВведіть новий процент:",
        "admin_slot_fee_updated": "✅ Комісію Слота оновлено: <b>{percent}%</b>",
        "admin_btn_game21_fees": "♠️ 21 — fees",
        "admin_fees_21_title": "♠️ <b>Game 21 fees</b>\n\nVs bot: <b>{bot}%</b>\nPvP: <b>{users}%</b>",
        "admin_game21_fee_btn_bot": "Vs bot",
        "admin_game21_fee_btn_users": "Between users",
        "admin_game21_fee_bot_title": "💸 21 fee (vs bot)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_users_title": "💸 21 fee (PvP)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_updated": "✅ 21 fee updated: <b>{percent}%</b>",
        "admin_21_title": "♠️ <b>Гра 21</b>\n\nБот: {bot}\n\nКомісії: бот {bot_fee}% · PvP {users_fee}%\n\nВиберіть розділ налаштувань.",
        "admin_21_on": "🟢 on",
        "admin_21_off": "⚪ off",
        "admin_21_btn_enable": "Увімкнути",
        "admin_21_btn_rules": "Правила",
        "admin_21_enable_title": "♠️ <b>21 — режими</b>\n\nУвімкніть гру з ботом або PvP для підключених чатів.",
        "admin_21_rules_title": "♠️ <b>21 — правила</b>\n\nЗ ботом: {bot}\nМіж користувачами: {users}",
        "admin_21_rules_btn_bot": "Для гри з ботом",
        "admin_21_rules_btn_users": "Між користувачами",
        "admin_21_rules_prompt_bot": "Введіть правила для гри 21 з ботом:",
        "admin_21_rules_prompt_users": "Введіть правила для гри 21 між користувачами:",
        "admin_21_rules_empty": "❌ Правила не можуть бути порожніми. Введіть текст правил.",
        "admin_21_rules_saved": "✅ Правила збережено. Переклади для інших мов оновлено автоматично.",
        "admin_21_rules_saved_no_translate": "✅ Правила збережено російською. Автопереклад не виконано: перевірте AI-ключ у налаштуваннях.",
        "admin_21_btn_bot_on": "Vs bot: turn off",
        "admin_21_btn_bot_off": "Vs bot: turn on",
        "admin_21_btn_users_on": "PvP global: turn off",
        "admin_21_btn_users_off": "PvP global: turn on",
        "admin_21_chat_pvp_on": "PvP in «{title}»: off",
        "admin_21_chat_pvp_off": "PvP in «{title}»: on",
        "game21_active_notice": "У вас вже є активна гра. Спочатку завершіть її.",
        "game21_bot_midgame_menu_blocked": (
            "Ви зараз у активній грі. Спочатку завершіть поточну гру."
        ),
        "game21_busy_screen_text": "У вас вже є активна гра в чаті {chat}",
        "game21_busy_screen_text_bot": (
            "У вас вже є активна гра з ботом. Доіграйте партію в цьому чаті."
        ),
        "game21_btn_abort_session": "Скасувати гру",
        "game21_active_cancelled_toast": "Поточну сесію 21 скасовано.",
        "game21_no_active_search_to_cancel": (
            "Немає активного пошуку суперника (його вже скасовано або гра почалася)."
        ),
        "game21_pvp_choose_topic": "Оберіть ігрову кімнату (🟢 вільна, 🔴 зайнята):",
        "game21_pvp_topic_free": "🟢",
        "game21_pvp_topic_busy": "🔴",
        "game21_pvp_topic_general": "General",
        "game21_pvp_search_post_failed": "Could not post search. Bet refunded.",
        "game21_pvp_decide_prompt_other": "{name}, roll the dice 🎲 once.",
        "game21_menu_title": "Game 21",
        "game21_btn_rules": "Rules",
        "game21_btn_vs_bot": "Play vs bot",
        "game21_btn_vs_user_chat": "Play vs user in chat",
        "game21_coming_soon_all_off": "Game 21 is unavailable.",
        "game21_coming_soon_play": "Vs bot is unavailable.",
        "game21_enter_bet": "Enter bet (PLN):",
        "game21_bet_invalid": "Invalid amount.",
        "game21_not_enough_balance": "Insufficient balance.",
        "game21_confirm_bet_with_win": "Bet: {amount} PLN\nPossible win: {win} PLN\n\nConfirm?",
        "game21_btn_yes": "Yes",
        "game21_btn_no": "No",
        "game21_cancelled": "Cancelled.",
        "game21_rules_title": "<b>Rules 21</b>",
        "game21_rules": "See sections below.",
        "game21_rules_bot": "<b>Vs bot</b>\nRoll 🎲 in DM. Min 16, then Stop. Bot rolls after you.",
        "game21_rules_users": "<b>PvP in {chat_title}</b>\nFind opponent, roll for order, play to 21.",
        "game21_throw_now": "Roll the dice 🎲",
        "game21_player_result": "Your total: {total}",
        "game21_player_busted": "Your total: {total}\nBust!",
        "game21_player_blackjack": "You have 21!",
        "game21_player_can_stop": "Your total: {total}\nRoll or press Stop.",
        "game21_btn_stop": "Stop",
        "game21_bot_turn_start": "Bot's turn.",
        "game21_bot_result": "Bot total: {total}",
        "game21_result_win": "You won!",
        "game21_result_lose": "You lost.",
        "game21_result_draw": "Draw.",
        "game21_end_bot_win": (
            "<b>Ви виграли!</b>\n"
            "На баланс зараховано <b>{payout} PLN</b>.\n"
            "Рахунок: ви {player_total} — бот {bot_total}."
        ),
        "game21_end_bot_lose": "Ви програли {bet} PLN\nРахунок: ви {player_total} — бот {bot_total}.",
        "game21_end_bot_lose_bust": "Ви програли {bet} PLN\nПеребір: {player_total}.",
        "game21_end_bot_draw": (
            "<b>Нічия.</b>\n"
            "Ставку <b>{bet} PLN</b> повернуто на баланс.\n"
            "Рахунок: {player_total} — {bot_total}."
        ),
        "game21_pvp_enter_bet": "Введіть суму ставки (PLN):\n\nГра в 21 у {room}",
        "game21_pvp_confirm": "Start opponent search?\nBet: {amount} PLN\nPossible win: {win} PLN",
        "game21_pvp_search_started": (
            "Пошук суперника розпочато\n\n"
            "З вашого балансу списано ставку {amount} PLN"
        ),
        "game21_pvp_choose_chat": "Choose a chat:",
        "game21_pvp_no_available_chat": "No chats available for PvP.",
        "game21_pvp_must_join_chat": "You must be in the chat: {chat_title}",
        "game21_pvp_not_member_title": "Ви не в ігровому чаті",
        "game21_pvp_not_member_intro": "Щоб грати в 21 з іншим користувачем, увійдіть у чат за посиланням нижче. Потім знову оберіть у боті пункт гри з користувачем у чаті.",
        "game21_pvp_main_active_exists": "Неможливо створити запит на гру, бо там зараз триває гра.",
        "game21_chat_command_active_exists": "Зараз у {topic} є активна гра.",
        "game21_chat_command_usage": "Використовуйте формат: <code>/21 10</code>",
        "checkers_chat_command_usage": "Використовуйте формат: <code>/checkers 10</code>",
        "kmb_chat_command_usage": "Використовуйте формат: <code>/kmb 10 3</code>, де 3 — до скількох перемог грати.",
        "info_command_text": (
            "<b>Команди бота</b>\n\n"
            "<code>/info</code> — показати це повідомлення.\n"
            "<code>/21 10</code> — створити гру 21 PvP зі ставкою 10 PLN.\n"
            "<code>/checkers 10</code> — створити гру в шашки зі ставкою 10 PLN.\n"
            "<code>/kmb 10 3</code> — створити КМБ зі ставкою 10 PLN, гра до 3 перемог.\n"
            "<code>/back</code> — скасувати поточне введення в особистому чаті.\n\n"
            "Також працюють старі формати: <code>/play21:10</code>, "
            "<code>/checkers:10</code>, <code>/kmb:10:3</code>, <code>/rps 10 3</code>."
        ),
        "game21_pvp_active_exists": "This slot already has a game or search.",
        "game21_pvp_self_accept_forbidden": "You cannot accept your own request.",
        "game21_pvp_search_post": "{user} looks for a 21 opponent\n\nBet: {amount} PLN\nWin up to: {win} PLN\n\nBalance in bot {bot_link}",
        "game21_pvp_btn_accept": "Accept",
        "game21_pvp_match_title": "Гра в 21",
        "game21_pvp_match_started_in_topic": "Гра в 21 розпочалась у {room}",
        "game21_pvp_match_prize": "<b>Сума виграшу: {win} PLN</b>",
        "game21_pvp_match_rules_heading": "Правила гри:",
        "game21_pvp_rules_body": (
            "Спочатку кожен один раз кидає кубик 🎲 — менший результат ходить першим. "
            "Далі по черзі набираєте очки, ціль — якомога ближче до 21, не більше. "
            "Коли дозволено правилами, можна «Стоп». "
            "Після зупинок або перебору порівнюють суми; можлива нічия."
        ),
        "game21_pvp_started": "Game 21\n{p1}\n{p2}\n\nBet: {amount} PLN · win up to {win} PLN\n{bot_link}",
        "game21_pvp_general_started_notice": "Гра в 21 між {p1} та {p2} розпочалась у <b>{room}</b>.",
        "game21_pvp_topic_started_notice": "Гра в 21 між {p1} та {p2} розпочалась.\n\nНагорода: {prize} PLN.",
        "game21_pvp_decide_first": "{players} — roll 🎲 once each (lower starts).",
        "game21_pvp_decide_roll_result": "{name} rolled {value}",
        "game21_pvp_decide_tie": "Tie on rolls. Roll again.",
        "game21_pvp_turn_prompt": "{name}, your turn. Roll 🎲",
        "game21_pvp_player_result": "{name}: {total}",
        "game21_pvp_player_busted": "{name}: {total} — bust!",
        "game21_pvp_player_blackjack": "{name} — 21!",
        "game21_pvp_player_can_stop": "{name}: {total}. Stop or roll again.",
        "game21_pvp_stop_announce": "{name} stopped at {total}",
        "game21_pvp_not_your_turn_stop": "It is {name}'s turn now.",
        "game21_pvp_stop_only_on_equal": "Stop is only when totals are equal.",
        "game21_pvp_winner": "Winner: {name}\nPayout {payout} PLN · {bot_link}",
        "game21_pvp_draw": "Draw. Refund {amount} PLN · {bot_link}",
        "game21_pvp_pm_bet_deducted": "Bet deducted: {amount} PLN.",
        "game21_pvp_search_not_accepted": "No one accepted. Refund {amount} PLN.",
        "game21_pvp_topic_forbidden": "Ця тема недоступна для гри.",
        "game21_pvp_topics_restricted_empty": "У цьому чаті немає тем, дозволених адміністратором для ігор.",
        # ---- Chats settings ----
        "admin_chats_title": "💬 <b>Підключені чати</b>",
        "admin_chats_empty": "Чатів поки немає.",
        "admin_chats_list_line": "• <code>{chat_id}</code> · {title}",
        "admin_chats_btn_add": "➕ Додати чат",
        "admin_chats_btn_delete": "🗑 Видалити чат",
        "admin_chats_btn_game_topics": "📋 Теми для ігор",
        "admin_chats_topics_choose_chat": "Оберіть чат, у якому налаштувати, у яких темах форуму можна грати (21 PvP та ігри з кубиком):",
        "admin_chats_topics_not_forum": "Цей чат не форум-супергрупа з темами — налаштування не потрібне.",
        "admin_chats_topics_chat_unavailable": "Не вдалося відкрити чат.",
        "admin_chats_topics_body_open": (
            "📋 <b>Теми для ігор</b>: {title}\n\n"
            "Зараз без обмежень — 21 PvP і створення ігор доступні в усіх відомих темах і в загальному чаті.\n\n"
            "Натисніть «Увімкнути обмеження за темами», щоб явно обрати, де дозволені ігри (список заповниться поточними темами; зніміть зайві галочки)."
        ),
        "admin_chats_topics_body_restricted": (
            "📋 <b>Теми для ігор</b>: {title}\n\n"
            "Увімкнено список дозволених тем. Ігри лише там, де стоїть ✅.\n\n"
            "«Зняти обмеження» — знову дозволити всюди."
        ),
        "admin_chats_topics_btn_enable": "Увімкнути обмеження за темами",
        "admin_chats_topics_btn_disable": "Зняти обмеження (усі теми)",
        "admin_chats_enter_button_title": (
            "Введіть <b>назву кнопки</b> — так вона відображатиметься користувачам при виборі чату. "
            "Зараз один і той самий текст буде збережено для <b>ru / en / uk / pl</b>; пізніше можна "
            "задати окремі підписи для кожної мови.\n\n"
            "До 200 символів."
        ),
        "admin_chats_invalid_button_title": "❌ Введіть непорожню назву (до 200 символів).",
        "admin_chats_enter_chat_id": (
            "Введіть <b>ID чату</b> (наприклад <code>-1001234567890</code>).\n\n"
            "Щоб дізнатися ID: додайте бота в групу і перешліть звідти будь-яке повідомлення боту "
            "<a href=\"https://t.me/userinfobot\">@userinfobot</a>, або скористайтеся сервісом на кшталт getidsbot."
        ),
        "admin_chats_invalid_id": "❌ Невірний формат. Введіть число, що починається з <code>-100</code>.",
        "admin_chats_already_added": "⚠️ Цей чат уже підключений.",
        "admin_chats_added": "✅ Чат <code>{chat_id}</code> підключено.",
        "admin_chats_invite_ok": "✅ Посилання-запрошення створено автоматично.",
        "admin_chats_invite_link_failed": (
            "⚠️ Не вдалося отримати invite-посилання: переконайтеся, що бот у чаті як <b>адміністратор</b> "
            "з правом запрошувати учасників (або що в групі дозволені запрошення за посиланням)."
        ),
        "admin_chats_session_lost": "⚠️ Сесію додавання скинуто. Почніть знову з «Додати чат».",
        "admin_chats_delete_choose": "Оберіть чат для видалення:",
        "admin_chats_delete_confirm": "Видалити чат <code>{chat_id}</code>?",
        "admin_chats_deleted": "✅ Чат видалений.",
        "admin_chats_delete_none": "Немає підключених чатів для видалення.",
        # ---- Games create FSM ----
        "admin_game_no_chats": "⚠️ Спершу підключіть хоч один чат: Налаштування бота → Чати.",
        "admin_game_pick_chat": "В якому чаті анонсувати гру?",
        "admin_game_pick_forum_topic": "📂 <b>Тема форуму</b>\n\nОберіть тему, де відбуватиметься гра (анонс, раунди, кидки).\n\nЯкщо на кнопці «Гілка · id …»: бот бачить лише внутрішній id вітки (у звичайних повідомленнях немає видимої назви). Один раз перейменуйте тему в групі — бот оновить підпис.",
        "admin_game_pick_forum_topic_empty": "📂 <b>Тема форуму</b>\n\nСписок порожній: Telegram не віддає список тем через API, бот запам’ятовує вітки з повідомлень і службових подій.\n\nЯкщо теми вже є: надішліть у кожну потрібну тему будь-яке повідомлення (або один раз перейменуйте тему), потім натисніть «🔄 …».\n\nМожна пропустити й вести гру в загальному чаті без гілки.",
        "admin_game_forum_skip": "Без теми (загальний чат)",
        "admin_game_forum_reload": "🔄 Оновити список тем",
        "admin_game_forum_thread_placeholder": "Гілка · id {id}",
        "admin_game_forum_reload_toast": "Список оновлено",
        "admin_game_forum_reload_lost": "⚠️ Сесію скинуто. Почніть створення гри знову.",
        "admin_game_topic_forbidden": "Неможливо обрати цю тему: її немає в списку дозволених для цього чату.",
        "admin_game_pick_type": "🎯 <b>Тип гри</b>\n\nОберіть вид кидка:",
        "admin_game_type_dice": "🎲 Кості",
        "admin_game_type_bowling": "🎳 Боулінг",
        "admin_game_type_darts": "🎯 Дартс",
        "admin_game_type_any": "🎲 🎳 🎯 (будь-який кидок)",
        "admin_game_name_prefix": "Гра",
        "admin_game_enter_participants": "👥 <b>Кількість учасників</b>\n\nВведіть мін./макс. через «/» або «-».\nПриклад: <code>10/100</code>",
        "admin_game_invalid_participants": "❌ Формат: <code>min/max</code>, обидва — додатні числа, min ≤ max.",
        "admin_game_enter_prizes": "🏆 <b>Призи</b>\n\nВведіть суми у PLN, кожна з нового рядка. Кількість рядків = кількість місць.\nПриклад:\n<code>20\n10\n5</code>\n\nПереможцям ці суми будуть нараховані на баланс автоматично.",
        "admin_game_invalid_prizes": "❌ Призи мають бути додатними числами (наприклад <code>20</code> або <code>10.5</code>), кожне з нового рядка.",
        "admin_game_prizes_more_than_max": "❌ Призових місць ({n}) більше за максимум учасників ({max}).",
        "admin_game_enter_min_topup": "💰 <b>Умова: мінімальна сума поповнень</b>\n\nФормати:\n• <code>0</code> — без умов\n• <code>100</code> — поповнив на 100 PLN за весь час\n• <code>100 : 01.01.2026</code> — поповнив на 100 PLN з вказаної дати",
        "admin_game_invalid_min_topup": "❌ Формат: число (<code>100</code>) або число + дата через «:» (<code>100 : 01.01.2026</code>).",
        "admin_game_enter_entry_fee": "💵 <b>Вартість внеску</b>\n\nВведіть суму у PLN (0 — безкоштовно).",
        "admin_game_invalid_entry_fee": "❌ Введіть число ≥ 0 (наприклад <code>0</code> або <code>5</code>).",
        "admin_game_enter_datetime": "🗓 <b>Дата і час старту</b>\n\nФормати:\n• <code>ДД.ММ.РРРР ГГ:ХХ</code>\n• <code>ГГ:ХХ</code> (сьогодні)",
        "admin_game_invalid_datetime": "❌ Не вдалося розпізнати дату/час. Приклад: <code>25.12.2026 19:30</code>.",
        "admin_game_datetime_in_past": "❌ Час старту має бути в майбутньому.",
        "admin_game_topup_since_after_start": "❌ Дата початку періоду пізніша за дату старту гри.",
        "admin_game_preview_title": "📋 <b>Превʼю гри</b>",
        "admin_game_preview_chat": "Чат: <b>{chat}</b>",
        "admin_game_preview_forum_topic": "Тема: <b>{topic}</b>",
        "admin_game_preview_type": "Тип: <b>{type}</b>",
        "admin_game_preview_participants": "Учасники: <b>{min}–{max}</b>",
        "admin_game_preview_prizes": "Призи:",
        "admin_game_preview_min_topup_none": "Умова: <b>без умов</b>",
        "admin_game_preview_min_topup_alltime": "Умова: поповнення від <b>{n} PLN</b> (за весь час)",
        "admin_game_preview_min_topup_period": "Умова: поповнення від <b>{n} PLN</b> з <b>{since}</b>",
        "admin_game_preview_pay_free": "Тип: <b>безкоштовна</b>",
        "admin_game_preview_pay_paid": "Тип: <b>платна</b>, внесок <b>{fee} PLN</b>",
        "admin_game_preview_datetime": "Старт: <b>{datetime}</b>",
        "admin_btn_confirm_create": "✅ Створити",
        "admin_btn_cancel_create": "❌ Скасувати",
        "admin_game_created": "✅ Гра #{id} створена.",
        "admin_game_create_cancelled": "❌ Скасовано.",
        # ---- Game lists ----
        "admin_games_active_title": "🟢 <b>Поточні ігри</b>",
        "admin_games_past_title": "📚 <b>Минулі ігри</b>",
        "admin_games_empty_active": "Зараз активних ігор немає.",
        "admin_games_empty_past": "Минулих ігор поки немає.",
        "admin_game_detail_title": "🎯 <b>Гра #{id}</b>",
        "admin_game_detail_status": "Статус: <b>{status}</b>",
        "admin_game_detail_participants_count": "Записалось: <b>{count}/{max}</b> (мін. {min})",
        "admin_game_status_draft": "очікує старту",
        "admin_game_status_active": "йде зараз",
        "admin_game_status_finished": "завершено",
        "admin_game_status_cancelled": "скасована",
        # ---- Announcement ----
        "game_announce_title": "🎯 Гра для <b>{chat}</b> створена",
        "game_announce_date": "Дата: <b>{date}</b>",
        "game_announce_participants_range": "Учасники: <b>{min}–{max}</b>",
        "game_announce_conditions": "<b>Умови участі:</b>",
        "game_announce_cond_min_topup_alltime": "• мінімум поповнень: <b>{n} PLN</b> (за весь час)",
        "game_announce_cond_min_topup_period": "• мінімум поповнень: <b>{n} PLN</b> (з {since} до старту)",
        "game_announce_cond_pay_free": "• безкоштовно",
        "game_announce_cond_pay_paid": "• платна, внесок <b>{fee} PLN</b>",
        "game_announce_cond_none": "• без додаткових умов",
        "game_announce_prizes": "<b>Призи:</b>",
        "game_announce_signup_link": "Запис на гру через бота {bot_link}",
        "game_announce_signup_no_link": "Запис на гру — напишіть боту в особисті.",
        "game_btn_signup": "🎮 Записатись на гру",
        "game_reminder_5min": "⏳ До гри в «{chat_title}» залишилось близько 5 хвилин.",
        "game_cancelled_not_enough_players_dm": "Гру скасовано: записалося лише {current} з {required} учасників.",
        "game_cancelled_refund_full_fee": "Внесок {fee} PLN повернуто на баланс.",
        "game_start_header": "<b>Умови:</b>\n{conditions}\n\n<b>Призи:</b>\n{prizes}",
        "game_start_cond_min_topup_period": "• мінімум поповнень: {n} PLN (з {since} до {until})",
        "game_start_cond_min_topup_alltime": "• мінімум поповнень: {n} PLN (за весь час)",
        "game_start_cond_paid": "• платна гра, внесок {fee} PLN",
        "game_start_cond_free": "• безкоштовна гра",
        "game_start_cond_none": "• без додаткових умов",
        "game_rules_block": (
            "Правила:\n"
            "1) Раунди по черзі, по 3 кидки на гравця.\n"
            "2) Можна кидати 🎲 🎳 🎯 (або тим самим текстом).\n"
            "3) Після раунду — прохідний бал за середнім серед тих, хто кинув.\n"
            "4) Пропуски — доганяюча спроба.\n"
            "5) Фінал і тай-брейк — за логікою бота."
        ),
        "game_round1_list_intro": "Перший раунд!",
        "round_list_participants": "Список учасників",
        "round_score_pending": "…",
        "round_score_eliminated": "вибув",
        "round_your_result": "Ваш кидок: {value}",
        "round_throw_2_more": "Зробіть ще 2 кидки {emoji}",
        "round_throw_1_more": "Зробіть ще 1 кидок {emoji}",
        "round_third_throw_done": "{result_line}\n{name}, підсумок у раунді: <b>{total}</b>",
        "round_throw_prompt": "{name}, зробіть 3 кидки будь-яким емодзі: {emoji}",
        "round_turn_60sec_left": "{name}, залишилась 1 хвилина на хід.",
        "round_participant_skipped": "{name} — хід пропущено.",
        "round_participants_missed": "Учасники без очок у цьому раунді:",
        "round_catchup_5min": "Є час на 3 кидки (прискорений режим).",
        "round_1_finished": "Перший раунд завершено.",
        "round_N_finished": "Раунд {round} завершено.",
        "round_passing_score": "Прохідний бал: {score}",
        "round_list_passed": "До наступного раунду проходять:",
        "round_list_passed_final": "До фінального раунду проходять:",
        "round_results_header": "Результати:",
        "round_tiebreak": "Тай-брейк!",
        "round_tiebreak_for": "Щоб визначити: {places}",
        "round_tiebreak_place_one": "{n}-е місце",
        "round_tiebreak_place_span": "місця з {a} по {b}",
        "round_tiebreak_throw": "{name}, зробіть 1 кидок {emoji}",
        "round_tiebreak_result": "{name} — кидок тай-брейку: {value}",
        "round_final_finished": "Фінальний раунд завершено.",
        "round_winners": "Переможці:",
        "game_sponsor_line": "Спонсор: {bot_link}",
        "game_dm_prize_won": "🎉 Ви зайняли {place} місце! На баланс зараховано <b>{amount} PLN</b>.",
        "game_signup_no_games": "Зараз немає ігор з відкритим записом.",
        "game_signup_list_title": "Відкритий запис (оберіть гру):",
        "game_signup_list_item": "#{id} {when} — {chat}",
        "game_signup_btn_join": "✅ Записатись",
        "game_signup_btn_leave": "🚫 Вийти",
        "game_signup_not_found": "Гру не знайдено.",
        "game_signup_not_draft": "Запис недоступний (гра не в чернетці).",
        "game_signup_started": "Гра вже стартувала або запис закрито.",
        "game_signup_full": "Місць немає.",
        "game_signup_min_topup": "Недостатньо поповнень: потрібно {need} PLN, у вас {have} PLN.",
        "game_signup_low_balance": "Недостатньо коштів: внесок {fee} PLN, баланс {balance} PLN.",
        "game_signup_already_in": "Ви вже в списку.",
        "game_signup_ok": "Вас записано.",
        "game_signup_left": "Ви вийшли зі списку.",
        "game_signup_not_in": "Вас не було в списку.",
        "game_signup_card": (
            "🎯 <b>Гра #{id}</b>\n"
            "Чат: {chat}\n"
            "Старт: <b>{start}</b>\n"
            "Гравці: <b>{count}</b> / {max_p} (мін. {min_p})\n\n"
            "<b>Умови:</b>\n{conditions}\n\n"
            "<b>Призи (PLN):</b>\n{prizes}"
        ),
        "game_signup_cond_topup_period": "• поповнення від {n} PLN з {since}",
        "game_signup_cond_topup_alltime": "• поповнення від {n} PLN за весь час",
        "game_signup_cond_paid": "• внесок {fee} PLN",
        "game_signup_cond_free": "• безкоштовно",
        "game_signup_cond_none": "—",
        "admin_pay_btn_activate": "▶️ Запустити",
        "admin_pay_btn_deactivate": "⏹ Зупинити",
        "admin_pay_btn_edit_proxy": "🌐 Змінити проксі",
        "admin_pay_btn_edit_blik": "📱 Змінити BLIK",
        "admin_pay_btn_edit_limit": "📊 Змінити ліміт",
        "admin_pay_btn_rescan": "🔁 Перечитати останні листи",
        "admin_pay_btn_delete": "🗑 Видалити",
        "admin_pay_btn_delete_confirm": "✅ Підтвердити видалення",
        "admin_pay_btn_cancel": "❌ Скасувати",
        "admin_pay_btn_bank_custom": "✏️ Інший",
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
        "topup_enter_amount": "💳 <b>Doładowanie salda</b>\n\nWprowadź kwotę doładowania w PLN (od {min} do {max} PLN):",
        "topup_invalid_amount": "❌ Nieprawidłowa kwota. Wprowadź liczbę (np. 50).",
        "topup_out_of_range": "❌ Kwota musi być od {min} do {max} PLN.",
        "topup_no_accounts": "⚠️ Doładowania chwilowo niedostępne — brak aktywnych kont płatniczych. Spróbuj później.",
        "topup_order_created": (
            "💳 <b>Zamówienie doładowania utworzone</b>\n\n"
            "Kwota: <b>{amount} PLN</b>\n"
            "Numer zamówienia: <code>{order_id}</code>\n\n"
            "📱 Wykonaj przelew BLIK na numer:\n<code>{blik}</code>\n\n"
            "⚠️ <b>W tytule przelewu musisz wpisać kod:</b>\n<code>{order_id}</code>\n\n"
            "Saldo zostanie doładowane automatycznie po otrzymaniu wpłaty."
        ),
        "topup_btn_cancel_order": "❌ Anuluj zamówienie",
        "topup_order_cancelled": "❌ Zamówienie <code>{order_id}</code> anulowane.",
        "topup_order_not_found": "❌ Zamówienie nie znalezione lub już zamknięte.",
        "btn_withdraw": "💸 Wypłata środków",
        "btn_cancel_withdraw": "❌ Anuluj wypłatę",
        "withdraw_enter_amount": (
            "💸 <b>Wypłata środków</b>\n\n"
            "Wpisz kwotę w PLN (minimum {min} PLN).\n"
            "Prowizja: <b>{fee}%</b>\n"
            "⏱ Wypłata realizowana w ciągu 24 godzin."
        ),
        "withdraw_invalid_amount": "❌ Nieprawidłowa kwota. Wpisz liczbę (np. 150).",
        "withdraw_below_min": "❌ Wypłata dostępna od {min} PLN.",
        "withdraw_not_enough": "❌ Niewystarczające środki. Twoje saldo: {balance} PLN.",
        "withdraw_enter_blik": "📱 Wpisz numer BLIK (minimum 9 cyfr):",
        "withdraw_invalid_blik": "❌ Nieprawidłowy format BLIK. Minimum 9 cyfr.",
        "withdraw_confirm": (
            "💸 <b>Potwierdzenie wypłaty</b>\n\n"
            "Z salda: <b>{amount} PLN</b>\n"
            "Prowizja: <b>{fee}%</b> ({fee_amount} PLN)\n"
            "Do wypłaty: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "Potwierdzić wypłatę?"
        ),
        "withdraw_btn_yes": "✅ Tak",
        "withdraw_btn_no": "❌ Nie",
        "withdraw_created": (
            "✅ <b>Zlecenie wypłaty utworzone</b>\n\n"
            "Numer: <code>#{id}</code>\n"
            "Do wypłaty: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "⏱ Wypłata w ciągu 24 godzin."
        ),
        "withdraw_cancel_ask": "❓ Czy na pewno chcesz anulować wypłatę <code>#{id}</code>?",
        "withdraw_cancelled": "✅ Wypłata <code>#{id}</code> anulowana. Środki zwrócone na saldo.",
        "withdraw_not_pending": "❌ Zlecenie nie znalezione lub już przetworzone.",
        "withdraw_already_pending": "⚠️ Masz już aktywne zlecenie wypłaty. Anuluj je, aby utworzyć nowe.",
        "withdraw_admin_message": (
            "🏦 <b>Nowe zlecenie wypłaty</b>\n\n"
            "👤 {mention}{username}\n"
            "🆔 <code>{user_id}</code>\n"
            "💸 Żądane: <b>{amount} PLN</b>\n"
            "🧾 Prowizja: {fee}% ({fee_amount} PLN)\n"
            "💵 Do wypłaty: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>"
        ),
        "withdraw_admin_btn_approve": "✅ Zatwierdź",
        "withdraw_admin_approved": "✅ <b>OPŁACONE</b>",
        "withdraw_admin_cancelled": "❌ <b>ANULOWANE</b>",
        "withdraw_approved_user": (
            "✅ Twoja wypłata <code>#{id}</code> na kwotę <b>{payout} PLN</b> została wysłana."
        ),
        "cabinet_title": "💼 Konto osobiste",
        "cabinet_balance": "💰 Saldo: <b>{balance} PLN</b>",
        "cabinet_level": "⭐ Poziom: <b>{level}</b>",
        "cabinet_next_level": "📈 Do poziomu {level}: <b>{amount} PLN</b>",
        "cabinet_next_level_max": "📈 Następny poziom: <b>osiągnięto maksymalny poziom</b>",
        "cabinet_referral_link": "🔗 Twój link polecający:\n<code>{link}</code>",
        "btn_referral_program": "🤝 Program poleceń",
        "btn_return_main": "powrót do menu głównego",
        "btn_checkers": "⚪️ Warcaby ⚫️",
        "btn_kmb": "👊✌️🤚 RPS 👊✌️🤚",
        "input_cancel_hint": "wpisz /back, aby anulować",
        "referral_empty": "Nie masz jeszcze poleconych.",
        "referral_line": "• {name} — {profit} PLN",
        "referral_program_text": "🤝 <b>Program polecający</b>\n\nTwój link:\n<code>{link}</code>\n\nWarunki: zaproś graczy za pomocą swojego linku i zdobądź <b>{percent}%</b> każdego zwycięskiego zakładu postawionego przez Twojego poleconego\n\n<b>Twoje polecenia:</b>\n{referrals}",
        "admin_21_summary": "♠️ <b>Tryb 21</b>\n\n-------------------------------------------\nVs BOT:\n\nOpłata: {bot_fee}%\n\nŁączna liczba gier BOT: {bot_total}\nBOT wygrał: {bot_won_count} gier, {bot_won_sum} PLN\nBOT przegrał: {bot_lost_count} gier, {bot_lost_sum} PLN\nRemisy: {bot_draw_count}\n\nZysk BOT: {bot_profit_sum} PLN\n\n-------------------------------------------\nPvP:\n\nOpłata: {users_fee}%\n\nCałkowita liczba gier PvP: {pvp_total}\nZysk z prowizji: {pvp_commission_sum} PLN\n\n-------------------------------------------\nŁączny zysk: {total_profit_sum} PLN",
        "admin_btn_checkers_fee": "⚪️ Opłata — warcaby ⚫️",
        "admin_btn_kmb_fee": "👊✌️🤚 Opłata RPS",
        "admin_btn_levels": "⭐ Ustawienia poziomu",
        "admin_btn_referral_fee": "🤝 Opłata za polecenie",
        "admin_checkers_btn_disable": "Wyłączyć",
        "admin_checkers_btn_enable": "Włącz / wyłącz",
        "admin_checkers_btn_rules": "Zasady",
        "admin_checkers_chat_off": "Warcaby w «{title}»: WŁ",
        "admin_checkers_chat_on": "Warcaby w «{title}»: WYŁ",
        "admin_checkers_enable_title": "⚪️ Warcaby ⚫️\n\nWybierz czat, aby włączyć lub wyłączyć grę:",
        "admin_checkers_fee_title": "⚪️ <b>Opłata za warcaby</b> ⚫️\n\nObecnie: <b>{percent}%</b>\n\nWprowadź nowy procent:",
        "admin_checkers_fee_updated": "✅ Zaktualizowano opłatę za warcaby: <b>{percent}%</b>",
        "admin_checkers_rules_empty": "Zasady nie są jeszcze ustalone.",
        "admin_checkers_rules_prompt": "Wprowadź zasady gry w warcaby w języku rosyjskim. Bot je zapisze i przetłumaczy na inne języki.",
        "admin_checkers_rules_title": "⚪️ Zasady warcabów ⚫️\n\n{rules}",
        "admin_checkers_title": "⚪️ Warcaby ⚫️\n\nProwizja: {commission}%\n\nŁącznie gier: {total_games}\nZysk z prowizji: {commission_sum} PLN",
        "admin_kmb_btn_enable": "Włącz / wyłącz",
        "admin_kmb_btn_rules": "Zasady",
        "admin_kmb_chat_off": "RPS w «{title}»: WŁ",
        "admin_kmb_chat_on": "RPS w «{title}»: WYŁ",
        "admin_kmb_enable_title": "👊✌️🤚 RPS 👊✌️🤚\n\nWybierz czat, aby włączyć lub wyłączyć grę:",
        "admin_kmb_fee_title": "👊✌️🤚 <b>Opłata RPS</b>\n\nObecnie: <b>{percent}%</b>\n\nWprowadź nowy procent:",
        "admin_kmb_fee_updated": "✅ Zaktualizowano opłatę RPS: <b>{percent}%</b>",
        "admin_kmb_rules_empty": "Zasady nie są jeszcze ustalone.",
        "admin_kmb_rules_prompt": "Wprowadź reguły RPS:",
        "admin_kmb_rules_saved": "✅ Reguły RPS zapisane.",
        "admin_kmb_rules_title": "Zasady RPS\n\n{rules}",
        "admin_kmb_title": "RPS\n\nOpłata: {commission}%\n\nUnikalni użytkownicy: {unique_users}\nŁączna liczba gier RPS: {total_games}\nZysk z prowizji: {commission_sum} PLN",
        "admin_levels_btn_disable": "Wyłączyć",
        "admin_levels_btn_enable": "Włączać",
        "admin_levels_btn_referral": "Bonus za polecenie",
        "admin_levels_btn_required": "Wymóg",
        "admin_levels_btn_reward": "Bilans nagrody",
        "admin_levels_btn_title": "Tytuł",
        "admin_levels_btn_withdraw": "Wycofaj rabat",
        "admin_levels_detail": "⭐ <b>Poziom {level}</b>\n\nTytuł: <b>{title}</b>\nStan: {status}\n\nWymagane zwycięskie zakłady: <b>{required} PLN</b>\nNagroda za saldo: <b>{reward} PLN</b>\nZniżka za wypłatę: <b>{withdraw}%</b>\nBonus za polecenie %: <b>{referral}%</b>",
        "admin_levels_invalid_amount": "❌ Wpisz liczbę dodatnią lub 0.",
        "admin_levels_invalid_percent": "❌ Wprowadź procent od 0 do 100.",
        "admin_levels_invalid_text": "❌ Tekst nie może być pusty.",
        "admin_levels_not_found": "❌ Nie znaleziono poziomu.",
        "admin_levels_prompt_referral": "Podaj % premii za polecenie dla poziomu {level} (0-100):",
        "admin_levels_prompt_required": "Wpisz zwycięską sumę zakładu wymaganą dla poziomu {level}:",
        "admin_levels_prompt_reward": "Podaj nagrodę salda dla poziomu {level}:",
        "admin_levels_prompt_title": "Wpisz tytuł poziomu {level}:",
        "admin_levels_prompt_withdraw": "Wprowadź zniżkę za wypłatę dla poziomu {level} (0-100):",
        "admin_levels_saved": "✅ Zapisano.",
        "admin_levels_status_off": "⚪ wyłączony",
        "admin_levels_status_on": "🟢 włączony",
        "admin_levels_title": "⭐ <b>Ustawienia poziomu</b>\n\nWybierz poziom do edycji:",
        "admin_referral_fee_title": "🤝 <b>Opłata za polecenie</b>\n\nObecnie: <b>{percent}%</b>\n\nWprowadź nowy procent:",
        "admin_referral_fee_updated": "✅ Zaktualizowano opłatę za polecenie: <b>{percent}%</b>",
        "admin_user_amount_invalid": "❌ Wpisz kwotę dodatnią.",
        "admin_user_banned": "Użytkownik zbanowany.",
        "admin_user_btn_ban": "🚫 Zablokuj",
        "admin_user_btn_find_other": "🔎 Znajdź innego użytkownika",
        "admin_user_btn_referral_percent": "🤝 Zmień % poleceń",
        "admin_user_btn_topup": "💳 Uzupełnij saldo",
        "admin_user_btn_unban": "✅ Odblokuj",
        "admin_user_btn_withdraw_percent": "💸 Zmień opłatę za wypłatę",
        "admin_user_card": "👤 <b>{label}</b>\n\nIdentyfikator: <code>{user_id}</code>\nNazwa użytkownika: {username}\nStan: {status}\nSaldo: <b>{balance} PLN</b>\nPoziom: <b>{level}</b>\nWygrane zakłady w kierunku poziomu: {level_progress} PLN\nBonus za poziom: wypłata −{level_withdraw_discount}%, polecenie +{level_referral_bonus}%\nJęzyk: {language}\nZaproszony przez: {referrer}\n\nOpłata za wypłatę: <b>{withdraw_percent}%</b> ({withdraw_source})\n% poleceń: <b>{referral_percent}%</b> ({referral_source})\n\nPolecenia: {referrals_count}\nZysk z poleconych: {referrals_profit} PLN",
        "admin_user_not_found": "❌ Nie znaleziono użytkownika. Wprowadź ponownie identyfikator lub nazwę użytkownika.",
        "admin_user_percent_global": "globalny {percent}%",
        "admin_user_percent_invalid": "❌ Wprowadź procent 0–100 lub <code>-</code>, aby zresetować.",
        "admin_user_percent_personal": "osobiste {percent}%",
        "admin_user_percent_reset": "żadnych osobistych zmian",
        "admin_user_referral_bonus": "globalne {global_percent}% + premia {bonus}%",
        "admin_user_referral_done": "✅ Zaktualizowano bonus za polecenie: <b>{percent}</b>.",
        "admin_user_referral_prompt": "Wprowadź premię za polecenie dla {user} / <code>{user_id}</code>.\n\nPrzykład: jeśli globalne polecenie wynosi 1% i wyślesz <code>1</code>, skuteczność wynosi 2%.\n\nWyślij procent 0–100 lub <code>-</code>, aby usunąć bonus osobisty.",
        "admin_user_search_prompt": "👥 Wpisz identyfikator użytkownika lub nazwę użytkownika:",
        "admin_user_status_active": "🟢 aktywny",
        "admin_user_status_banned": "🔴 zablokowany",
        "admin_user_topup_done": "✅ Saldo doładowane o <b>{amount} PLN</b>.",
        "admin_user_topup_prompt": "Podaj kwotę doładowania dla {user} / <code>{user_id}</code>:",
        "admin_user_unbanned": "Użytkownik odblokowany.",
        "admin_user_withdraw_discount": "globalne {global_percent}% − rabat {discount}%",
        "admin_user_withdraw_done": "✅ Zaktualizowano rabat za wypłatę: <b>{percent}</b>.",
        "admin_user_withdraw_prompt": "Wpisz zniżkę do prowizji za wypłatę dla {user} / <code>{user_id}</code>.\n\nPrzykład: jeśli globalna prowizja to 10%, a wyślesz <code>1</code>, w praktyce jest 9%.\n\nWyślij procent 0–100 lub <code>-</code>, aby usunąć osobistą zniżkę.",
        "checkers_active_notice": "Masz już aktywną grę lub wyszukiwanie.",
        "checkers_bad_move": "Ten ruch jest niedozwolony.",
        "checkers_board_text": "⚪️ <b>Warcaby</b> ⚫️\n⚪ {white}\n⚫ {black}\n\nPula: {amount} PLN\nTura: {turn}",
        "checkers_btn_accept": "Zaakceptuj grę",
        "checkers_choose_chat": "Wybierz czat dla warcabów:",
        "checkers_choose_topic": "Wybierz pokój gier (🟢 wolny, 🔴 zajęty):",
        "checkers_confirm": "Zakład: {amount} PLN\nKwota wygranej: {win} PLN\nRozpocząć wyszukiwanie przeciwnika?",
        "checkers_decide_white": "{players} — rzućcie kością 🎲 po jednym razie. Wyższy wynik gra białymi.",
        "checkers_disabled": "Warcaby są tymczasowo wyłączone.",
        "checkers_draw_countdown": "Brak przejęcia dla {no_capture} ruchów.\nJeśli w ciągu następnych 10 ruchów (po 5 na stronę) nie zostanie zbity, będzie remis.\n\nRuchy do remisu: {remaining}",
        "checkers_draw_countdown_reset": "Zbicie pionka. Licznik remisu został zresetowany.",
        "checkers_draw_result": "Koniec gry.\nRemis.\n\nStawka {amount} PLN zwrócona obu graczom.",
        "checkers_enter_bet": "<b>{chat}</b>\nTwoje saldo: {balance} PLN\nWpisz kwotę zakładu:",
        "checkers_flood_wait": "Za szybko. Poczekaj {seconds} s.",
        "checkers_match_prize": "Kwota wygranej: {win} PLN",
        "checkers_match_rules_heading": "Zasady:",
        "checkers_match_started_in_topic": "Warcaby rozpoczęły się w {room}",
        "checkers_match_title": "Warcaby",
        "checkers_not_your_turn": "Nie twoja kolej.",
        "checkers_rules_body": "Białe poruszają się pierwsze. Kawałki poruszają się po przekątnej; przechwytywanie jest obowiązkowe. Królowie poruszają się na dowolną odległość po przekątnej. Jeśli nie wykonasz ruchu w ciągu 2 minut, przegrywasz.",
        "checkers_search_cancelled_refund": "Anulowano.\nStawka wróciła na saldo.",
        "checkers_search_post": "{user} szuka warcabowego przeciwnika.\nZakład: {amount} PLN\nKwota wygranej: {win} PLN",
        "checkers_search_started": "Rozpoczęło się wyszukiwanie warcabów. Zakład {amount} PLN odliczony.",
        "checkers_search_timeout": "Nikt nie przyjął. Zakład {amount} PLN wrócił do salda.",
        "checkers_turn_timeout_result": "Czas minął.\n{loser} przegrał(a).\n\nZwycięzca: {winner}\n{payout} PLN zaksięgowano na saldo.",
        "checkers_turn_timeout_warning": "{name}, masz 1 minutę na ruch, inaczej przegrywasz.",
        "checkers_white_chosen": "{name} gra białymi. Rozpoczyna się gra.",
        "checkers_winner": "Koniec gry.\nZwycięzca: {name}\n\n{payout} PLN zaksięgowano na saldo.",
        "kmb_btn_accept": "Zaakceptuj grę",
        "kmb_choice_saved": "Wybór zapisany.",
        "kmb_choose_chat": "Wybierz czat dla RPS:",
        "kmb_choose_topic": "Wybierz pokój gier (🟢 wolny, 🔴 zajęty):",
        "kmb_confirm": "Pierwszy do {wins} wygrywa\nZakład: {amount} PLN\nKwota wygranej: {win} PLN\nRozpocząć wyszukiwanie?",
        "kmb_enter_bet": "<b>{chat}</b>\nTwoje saldo: {balance} PLN\nWpisz kwotę zakładu:",
        "kmb_enter_wins": "<b>{chat}</b>\nZagraj jako pierwszy do ilu wygranych?\nWpisz 1–10:",
        "kmb_match_prize": "Kwota wygranej: {win} PLN",
        "kmb_match_rules_heading": "Zasady:",
        "kmb_match_started_in_topic": "Kamień/Papier/Nożyce rozpoczęły się w {room}",
        "kmb_match_title": "Kamień / Papier / Nożyce",
        "kmb_no_chats": "RPS niedostępny: brak włączonych czatów i tematów.",
        "kmb_not_your_game": "To nie jest twoja gra.",
        "kmb_pick_done": "dokonany wybór",
        "kmb_pick_prompt": "👊✌️🤚 <b>RPS</b>\n\nPierwszy do {wins} wygrywa\nWynik: {p1_score} - {p2_score}\n\n{p1}: {p1_status}\n{p2}: {p2_status}\n\nWybierz kamień, nożyczki lub papier.",
        "kmb_pick_wait": "czeka na wybór",
        "kmb_result_draw": "Remis.\n{p1}: {p1_choice}\n{p2}: {p2_choice}\n\nWynik: {p1_score} - {p2_score}\nGra do {wins} zwycięstw.\n\nWybierz ponownie.",
        "kmb_result_win": "Koniec gry.\nWynik końcowy: {p1_score} - {p2_score}\n\n{p1}: {p1_choice}\n{p2}: {p2_choice}\n\nZwycięzca: {winner}\n{payout} PLN zaksięgowano na saldo.",
        "kmb_round_win": "Runda zakończona.\n{p1}: {p1_choice}\n{p2}: {p2_choice}\n\nZwycięzca rundy: {winner}\nWynik: {p1_score} - {p2_score}\n\nGra do {wins} zwycięstw. Wybierz ponownie.",
        "kmb_rules_body": "Kamień bije nożyce, nożyce tną papier, papier przykrywa kamień. Ten sam wybór to remis i runda jest powtarzana.",
        "kmb_search_cancelled_refund": "Anulowano.\nStawka wróciła na saldo.",
        "kmb_search_post": "{user} szuka przeciwnika RPS.\nPierwszy do {wins} wygrywa\nZakład: {amount} PLN\nKwota wygranej: {win} PLN",
        "kmb_search_started": "Rozpoczęło się wyszukiwanie RPS. Pierwszy do {wins} wygrywa. Zakład {amount} PLN odliczony.",
        "kmb_search_timeout": "Nikt nie przyjął. Zakład {amount} PLN wrócił do salda.",
        "kmb_wins_invalid": "Nieprawidłowa liczba wygranych. Wpisz 1–10.",
        "btn_signup": "Zapisz się na grę",
        "main_menu_chat_fallback": "💬 Czat",
        "btn_play_21_bot": "Graj w 21",
        "btn_casino": "🎰 Slot 🎰",
        "slot_enter_bet_with_balance": "Twoje saldo: {balance} PLN\nPodaj kwotę stawki (np. 1):",
        "slot_rules_block": "Zasady i wypłaty:\n• 3 takie same — x4\n• 2 takie same — x1.1\n• Wszystkie różne — przegrana",
        "slot_bet_invalid": "Nieprawidłowa kwota stawki. Podaj dodatnią liczbę.",
        "slot_not_enough_balance": "Niewystarczające środki na tę stawkę.",
        "slot_spin_prompt": "Twoje saldo: {balance} PLN\nStawka {amount} PLN przyjęta.\nTeraz zakręć 🎰",
        "slot_balance_update_failed": "Nie udało się zaktualizować salda. Spróbuj ponownie.",
        "slot_combo_three": "3 takie same",
        "slot_combo_two": "2 takie same",
        "slot_combo_none": "wszystkie różne",
        "slot_result_win": "Twoje saldo: {balance} PLN\nWynik 🎰: {combo}\nStawka {bet} PLN jest mnożona przez x{mult}\nWypłata: {payout} PLN",
        "slot_result_lose": "Twoje saldo: {balance} PLN\nWynik 🎰: {combo}\nStawka {bet} PLN przepada.",
        "slot_disabled": "Slot jest obecnie wyłączony.",
        "admin_slot_stats_text": "Slot:\nBOT wygrał: {bot_won_sum} PLN\nBOT przegrał: {bot_lost_sum} PLN\nŁączny zysk BOTA: {bot_profit_sum} PLN",
        "admin_slot_mode_text": (
            "🎰 <b>Tryb slot</b>\n\n"
            "{status}\n\n"
            "-------------------------------------------\n"
            "Łącznie gier: {total_games}\n"
            "unikalnych użytkowników: {unique_users}\n"
            "wygrane użytkowników: {users_won_sum} PLN\n"
            "przegrane użytkowników: {users_lost_sum} PLN\n"
            "łączny zysk bota: {bot_profit_sum} PLN\n"
            "-------------------------------------------"
        ),
        "admin_slot_btn_enable": "Włącz",
        "admin_slot_btn_disable": "Wyłącz",
        "admin_slot_btn_rules": "Zasady",
        "admin_slot_rules_prompt": "Wpisz zasady dla Slotu:",
        "admin_slot_rules_current": "Aktualna zasada:\n{rules}",
        "admin_slot_rules_empty": "❌ Zasada nie może być pusta. Wpisz tekst zasady.",
        "admin_slot_rules_saved": "✅ Zasada Slotu zapisana.",
        "btn_admin": "Panel admina",
        "btn_lang": "🌐",
        "btn_main": "🏠 Główna",
        "btn_back": "← Wstecz",
        "admin_title": "Panel admina",
        "admin_no_access": "⛔ Brak dostępu",
        "admin_btn_games": "🎯 Gry",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Slot",
        "admin_btn_checkers": "⚪️ Warcaby ⚫️",
        "admin_btn_kmb": "🪖 KMB",
        "admin_btn_stats": "📊 Statystyka",
        "admin_stats_title": "📊 <b>Statystyka</b>",
        "admin_stats_btn_users": "👥 Użytkownicy",
        "admin_stats_users_title": (
            "👥 <b>Użytkownicy</b>\n\n"
            "Łącznie użytkowników: {total}\n"
            "Aktywnych: {active}\n"
            "Zablokowanych: {banned}\n"
            "Z saldem: {with_balance}\n"
            "Łączne saldo: {balance_sum} PLN"
        ),
        "admin_btn_bot_settings": "⚙️ Ustawienia bota",
        "admin_games_title": "🎯 <b>Gry</b>",
        "admin_btn_create_game": "➕ Utwórz grę",
        "admin_btn_active_games": "🟢 Bieżące gry",
        "admin_btn_past_games": "📚 Minione gry",
        "admin_wip": "🚧 W trakcie tworzenia",
        "admin_settings_title": "⚙️ Ustawienia bota",
        "admin_btn_payments": "💳 Ustawienia płatności",
        "admin_btn_fees": "💸 Ustawienia prowizji",
        "admin_btn_withdraw_fee": "💸 Prowizja wypłaty",
        "admin_btn_slot_fee": "🎰 Prowizja Slotu",
        "admin_fees_title": "💸 <b>Ustawienia prowizji</b>",
        "admin_pay_title": "<b>MBanks</b> — konta:",
        "admin_pay_empty": "<b>MBanks</b>\nBrak kont.",
        "admin_pay_btn_add": "➕ Dodaj konto",
        "admin_pay_btn_withdraw_fee": "💸 Prowizja wypłaty",
        "admin_withdraw_fee_title": "💸 <b>Prowizja wypłaty</b>\n\nObecnie: <b>{percent}%</b>\n\nWpisz nowy procent (np. <code>5</code> lub <code>2.5</code>):",
        "admin_withdraw_fee_invalid": "❌ Nieprawidłowy format. Wpisz liczbę od 0 do 100 (np. <code>5</code> lub <code>2.5</code>).",
        "admin_withdraw_fee_updated": "✅ Prowizja wypłaty zaktualizowana: <b>{percent}%</b>",
        "admin_slot_fee_title": "🎰 <b>Prowizja Slotu</b>\n\nObecnie: <b>{percent}%</b>\n\nPodaj nowy procent:",
        "admin_slot_fee_updated": "✅ Prowizja Slotu zaktualizowana: <b>{percent}%</b>",
        "admin_btn_game21_fees": "♠️ 21 — fees",
        "admin_fees_21_title": "♠️ <b>Game 21 fees</b>\n\nVs bot: <b>{bot}%</b>\nPvP: <b>{users}%</b>",
        "admin_game21_fee_btn_bot": "Vs bot",
        "admin_game21_fee_btn_users": "Between users",
        "admin_game21_fee_bot_title": "💸 21 fee (vs bot)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_users_title": "💸 21 fee (PvP)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_updated": "✅ 21 fee updated: <b>{percent}%</b>",
        "admin_21_title": "♠️ <b>Gra 21</b>\n\nVs bot: {bot}\n\nProwizje: bot {bot_fee}% · PvP {users_fee}%\n\nWybierz sekcję ustawień.",
        "admin_21_on": "🟢 on",
        "admin_21_off": "⚪ off",
        "admin_21_btn_enable": "Włącz",
        "admin_21_btn_rules": "Zasady",
        "admin_21_enable_title": "♠️ <b>21 — tryby</b>\n\nWłącz grę z botem lub PvP dla podłączonych czatów.",
        "admin_21_rules_title": "♠️ <b>21 — zasady</b>\n\nZ botem: {bot}\nMiędzy użytkownikami: {users}",
        "admin_21_rules_btn_bot": "Dla gry z botem",
        "admin_21_rules_btn_users": "Między użytkownikami",
        "admin_21_rules_prompt_bot": "Wpisz zasady gry 21 z botem:",
        "admin_21_rules_prompt_users": "Wpisz zasady gry 21 między użytkownikami:",
        "admin_21_rules_empty": "❌ Zasady nie mogą być puste. Wpisz tekst zasad.",
        "admin_21_rules_saved": "✅ Zasady zapisane. Tłumaczenia dla innych języków zostały zaktualizowane automatycznie.",
        "admin_21_rules_saved_no_translate": "✅ Zasady zapisane po rosyjsku. Automatyczne tłumaczenie nie zostało wykonane: sprawdź klucz AI w ustawieniach.",
        "admin_21_btn_bot_on": "Vs bot: turn off",
        "admin_21_btn_bot_off": "Vs bot: turn on",
        "admin_21_btn_users_on": "PvP global: turn off",
        "admin_21_btn_users_off": "PvP global: turn on",
        "admin_21_chat_pvp_on": "PvP in «{title}»: off",
        "admin_21_chat_pvp_off": "PvP in «{title}»: on",
        "game21_active_notice": "Masz już aktywną grę. Najpierw ją zakończ.",
        "game21_bot_midgame_menu_blocked": (
            "Jesteś w trakcie aktywnej gry. Najpierw dokończ bieżącą grę."
        ),
        "game21_busy_screen_text": "Masz już aktywną grę na czacie {chat}.",
        "game21_busy_screen_text_bot": (
            "Masz już aktywną grę z botem. Dokończ rundę na tym czacie."
        ),
        "game21_btn_abort_session": "Anuluj grę",
        "game21_active_cancelled_toast": "Sesja 21 została anulowana.",
        "game21_no_active_search_to_cancel": (
            "Brak aktywnego szukania przeciwnika (już anulowane lub mecz się rozpoczął)."
        ),
        "game21_pvp_choose_topic": "Wybierz pokój gry (🟢 wolny, 🔴 zajęty):",
        "game21_pvp_topic_free": "🟢",
        "game21_pvp_topic_busy": "🔴",
        "game21_pvp_topic_general": "General",
        "game21_pvp_search_post_failed": "Could not post search. Bet refunded.",
        "game21_pvp_decide_prompt_other": "{name}, roll the dice 🎲 once.",
        "game21_menu_title": "Game 21",
        "game21_btn_rules": "Rules",
        "game21_btn_vs_bot": "Play vs bot",
        "game21_btn_vs_user_chat": "Play vs user in chat",
        "game21_coming_soon_all_off": "Game 21 is unavailable.",
        "game21_coming_soon_play": "Vs bot is unavailable.",
        "game21_enter_bet": "Enter bet (PLN):",
        "game21_bet_invalid": "Invalid amount.",
        "game21_not_enough_balance": "Insufficient balance.",
        "game21_confirm_bet_with_win": "Bet: {amount} PLN\nPossible win: {win} PLN\n\nConfirm?",
        "game21_btn_yes": "Yes",
        "game21_btn_no": "No",
        "game21_cancelled": "Cancelled.",
        "game21_rules_title": "<b>Rules 21</b>",
        "game21_rules": "See sections below.",
        "game21_rules_bot": "<b>Vs bot</b>\nRoll 🎲 in DM. Min 16, then Stop. Bot rolls after you.",
        "game21_rules_users": "<b>PvP in {chat_title}</b>\nFind opponent, roll for order, play to 21.",
        "game21_throw_now": "Roll the dice 🎲",
        "game21_player_result": "Your total: {total}",
        "game21_player_busted": "Your total: {total}\nBust!",
        "game21_player_blackjack": "You have 21!",
        "game21_player_can_stop": "Your total: {total}\nRoll or press Stop.",
        "game21_btn_stop": "Stop",
        "game21_bot_turn_start": "Bot's turn.",
        "game21_bot_result": "Bot total: {total}",
        "game21_result_win": "You won!",
        "game21_result_lose": "You lost.",
        "game21_result_draw": "Draw.",
        "game21_end_bot_win": (
            "<b>Wygrałeś!</b>\n"
            "Na balans wpłacono <b>{payout} PLN</b>.\n"
            "Wynik: ty {player_total} — bot {bot_total}."
        ),
        "game21_end_bot_lose": "Przegrałeś {bet} PLN\nWynik: ty {player_total} — bot {bot_total}.",
        "game21_end_bot_lose_bust": "Przegrałeś {bet} PLN\nPrzebicie: {player_total}.",
        "game21_end_bot_draw": (
            "<b>Remis.</b>\n"
            "Stawka <b>{bet} PLN</b> zwrócona na balans.\n"
            "Wynik: {player_total} — {bot_total}."
        ),
        "game21_pvp_enter_bet": "Wpisz stawkę (PLN):\n\nGra w 21 w {room}",
        "game21_pvp_confirm": "Start opponent search?\nBet: {amount} PLN\nPossible win: {win} PLN",
        "game21_pvp_search_started": (
            "Szukanie przeciwnika rozpoczęte.\n\n"
            "Z Twojego salda potrącono stawkę {amount} PLN"
        ),
        "game21_pvp_choose_chat": "Choose a chat:",
        "game21_pvp_no_available_chat": "No chats available for PvP.",
        "game21_pvp_must_join_chat": "You must be in the chat: {chat_title}",
        "game21_pvp_not_member_title": "Nie jesteś na czacie gry",
        "game21_pvp_not_member_intro": "Aby grać w 21 z innym użytkownikiem, dołącz do czatu przez poniższy link, a potem ponownie wybierz w bocie grę z użytkownikiem na czacie.",
        "game21_pvp_main_active_exists": "Nie można utworzyć zaproszenia do gry, ponieważ tam właśnie trwa gra.",
        "game21_chat_command_active_exists": "W {topic} jest teraz aktywna gra.",
        "game21_chat_command_usage": "Użyj formatu: <code>/21 10</code>",
        "checkers_chat_command_usage": "Użyj formatu: <code>/checkers 10</code>",
        "kmb_chat_command_usage": "Użyj formatu: <code>/kmb 10 3</code>, gdzie 3 to liczba zwycięstw.",
        "info_command_text": (
            "<b>Komendy bota</b>\n\n"
            "<code>/info</code> — pokaż tę wiadomość.\n"
            "<code>/21 10</code> — utwórz grę 21 PvP ze stawką 10 PLN.\n"
            "<code>/checkers 10</code> — utwórz grę w warcaby ze stawką 10 PLN.\n"
            "<code>/kmb 10 3</code> — utwórz grę KMB ze stawką 10 PLN, gra do 3 zwycięstw.\n"
            "<code>/back</code> — anuluj bieżące wprowadzanie w czacie prywatnym.\n\n"
            "Działają też stare formaty: <code>/play21:10</code>, "
            "<code>/checkers:10</code>, <code>/kmb:10:3</code>, <code>/rps 10 3</code>."
        ),
        "game21_pvp_active_exists": "This slot already has a game or search.",
        "game21_pvp_self_accept_forbidden": "You cannot accept your own request.",
        "game21_pvp_search_post": "{user} looks for a 21 opponent\n\nBet: {amount} PLN\nWin up to: {win} PLN\n\nBalance in bot {bot_link}",
        "game21_pvp_btn_accept": "Accept",
        "game21_pvp_match_title": "Gra w 21",
        "game21_pvp_match_started_in_topic": "Gra w 21 rozpoczęta w {room}",
        "game21_pvp_match_prize": "<b>Kwota wygranej: {win} PLN</b>",
        "game21_pvp_match_rules_heading": "Zasady:",
        "game21_pvp_rules_body": (
            "Na początku każdy raz rzuca kością 🎲 — mniejszy wynik zaczyna. "
            "Potem na zmianę zbieracie punkty, celem jest jak najbliżej 21, nie więcej. "
            "Gdy zasady na to pozwalają, można «Stop». "
            "Po zakończeniu lub przebiciu porównuje się sumy; możliwy jest remis."
        ),
        "game21_pvp_started": "Game 21\n{p1}\n{p2}\n\nBet: {amount} PLN · win up to {win} PLN\n{bot_link}",
        "game21_pvp_general_started_notice": "Gra w 21 między {p1} a {p2} rozpoczęła się w <b>{room}</b>.",
        "game21_pvp_topic_started_notice": "Gra w 21 między {p1} a {p2} rozpoczęła się.\n\nNagroda: {prize} PLN.",
        "game21_pvp_decide_first": "{players} — roll 🎲 once each (lower starts).",
        "game21_pvp_decide_roll_result": "{name} rolled {value}",
        "game21_pvp_decide_tie": "Tie on rolls. Roll again.",
        "game21_pvp_turn_prompt": "{name}, your turn. Roll 🎲",
        "game21_pvp_player_result": "{name}: {total}",
        "game21_pvp_player_busted": "{name}: {total} — bust!",
        "game21_pvp_player_blackjack": "{name} — 21!",
        "game21_pvp_player_can_stop": "{name}: {total}. Stop or roll again.",
        "game21_pvp_stop_announce": "{name} stopped at {total}",
        "game21_pvp_not_your_turn_stop": "Teraz ruch gracza {name}.",
        "game21_pvp_stop_only_on_equal": "Stop is only when totals are equal.",
        "game21_pvp_winner": "Winner: {name}\nPayout {payout} PLN · {bot_link}",
        "game21_pvp_draw": "Draw. Refund {amount} PLN · {bot_link}",
        "game21_pvp_pm_bet_deducted": "Bet deducted: {amount} PLN.",
        "game21_pvp_search_not_accepted": "No one accepted. Refund {amount} PLN.",
        "game21_pvp_topic_forbidden": "Ten wątek nie jest dostępny do gry.",
        "game21_pvp_topics_restricted_empty": "W tym czacie nie ma tematów dozwolonych przez administratora do gier.",
        # ---- Chats settings ----
        "admin_chats_title": "💬 <b>Podłączone czaty</b>",
        "admin_chats_empty": "Brak czatów.",
        "admin_chats_list_line": "• <code>{chat_id}</code> · {title}",
        "admin_chats_btn_add": "➕ Dodaj czat",
        "admin_chats_btn_delete": "🗑 Usuń czat",
        "admin_chats_btn_game_topics": "📋 Tematy do gier",
        "admin_chats_topics_choose_chat": "Wybierz czat, w którym ustawisz, w jakich wątkach forum można grać (21 PvP i gry z kośćmi):",
        "admin_chats_topics_not_forum": "Ten czat nie jest supergrupą forum z wątkami — nic do ustawiania.",
        "admin_chats_topics_chat_unavailable": "Nie udało się otworzyć czatu.",
        "admin_chats_topics_body_open": (
            "📋 <b>Tematy do gier</b>: {title}\n\n"
            "Teraz bez ograniczeń — 21 PvP i tworzenie gier są dozwolone we wszystkich znanych wątkach i w głównym czacie.\n\n"
            "Dotknij «Włącz limity wątków», aby wybrać, gdzie gra jest dozwolona (lista wypełni się bieżącymi wątkami; odznacz niepotrzebne)."
        ),
        "admin_chats_topics_body_restricted": (
            "📋 <b>Tematy do gier</b>: {title}\n\n"
            "Włączona jest lista dozwolonych wątków. Gra tylko tam, gdzie jest ✅.\n\n"
            "«Usuń limity» — znów wszędzie."
        ),
        "admin_chats_topics_btn_enable": "Włącz limity wątków",
        "admin_chats_topics_btn_disable": "Usuń limity (wszystkie wątki)",
        "admin_chats_enter_button_title": (
            "Wyślij <b>tekst przycisku</b> — taki zobaczą użytkownicy przy wyborze czatu. "
            "Ten sam tekst zapiszemy na razie dla <b>ru / en / uk / pl</b>; później można dodać "
            "osobne napisy dla każdego języka.\n\n"
            "Maks. 200 znaków."
        ),
        "admin_chats_invalid_button_title": "❌ Podaj niepusty tekst (maks. 200 znaków).",
        "admin_chats_enter_chat_id": (
            "Wyślij <b>ID czatu</b> (np. <code>-1001234567890</code>).\n\n"
            "Jak sprawdzić ID: dodaj bota do grupy i przekaż mu stamtąd dowolną wiadomość przez "
            "<a href=\"https://t.me/userinfobot\">@userinfobot</a> albo użyj bota typu getidsbot."
        ),
        "admin_chats_invalid_id": "❌ Nieprawidłowy format. Liczba całkowita zaczynająca się od <code>-100</code>.",
        "admin_chats_already_added": "⚠️ Ten czat jest już podłączony.",
        "admin_chats_added": "✅ Czat <code>{chat_id}</code> podłączony.",
        "admin_chats_invite_ok": "✅ Link zaproszenia utworzony automatycznie.",
        "admin_chats_invite_link_failed": (
            "⚠️ Nie udało się utworzyć linku zaproszenia: upewnij się, że bot jest <b>adminem</b> w czacie "
            "z prawem zapraszania użytkowników (albo że grupa zezwala na linki zaproszeń)."
        ),
        "admin_chats_session_lost": "⚠️ Sesja dodawania została zresetowana. Zacznij od «Dodaj czat».",
        "admin_chats_delete_choose": "Wybierz czat do usunięcia:",
        "admin_chats_delete_confirm": "Usunąć czat <code>{chat_id}</code>?",
        "admin_chats_deleted": "✅ Czat usunięty.",
        "admin_chats_delete_none": "Brak podłączonych czatów do usunięcia.",
        # ---- Games create FSM ----
        "admin_game_no_chats": "⚠️ Najpierw podłącz co najmniej jeden czat: Ustawienia bota → Czaty.",
        "admin_game_pick_chat": "W którym czacie ogłosić grę?",
        "admin_game_pick_forum_topic": "📂 <b>Wątek forum</b>\n\nWybierz wątek, w którym odbędzie się gra (ogłoszenie, rundy, rzuty).\n\nJeśli na przycisku jest «Wątek · id …», bot zna tylko wewnętrzny identyfikator (zwykłe wiadomości nie zawierają widocznej nazwy). Zmień raz nazwę wątku w grupie — bot zaktualizuje podpis.",
        "admin_game_pick_forum_topic_empty": "📂 <b>Wątek forum</b>\n\nLista jest pusta: Telegram nie udostępnia listy wątków w Bot API; bot uczy się wątków z wiadomości i zdarzeń serwisowych.\n\nJeśli wątki już są: wyślij dowolną wiadomość w każdym potrzebnym wątku (albo raz zmień nazwę), potem dotknij «🔄 …».\n\nMożesz pominąć i prowadzić grę w głównym czacie bez wątku.",
        "admin_game_forum_skip": "Bez wątku (główny czat)",
        "admin_game_forum_reload": "🔄 Odśwież listę wątków",
        "admin_game_forum_thread_placeholder": "Wątek · id {id}",
        "admin_game_forum_reload_toast": "Lista zaktualizowana",
        "admin_game_forum_reload_lost": "⚠️ Sesja wygasła. Zacznij tworzenie gry od nowa.",
        "admin_game_topic_forbidden": "Nie można wybrać tego wątku: nie ma go na liście dozwolonych dla tego czatu.",
        "admin_game_pick_type": "🎯 <b>Typ gry</b>\n\nWybierz rodzaj rzutu:",
        "admin_game_type_dice": "🎲 Kości",
        "admin_game_type_bowling": "🎳 Kręgle",
        "admin_game_type_darts": "🎯 Lotki",
        "admin_game_type_any": "🎲 🎳 🎯 (dowolny rzut)",
        "admin_game_name_prefix": "Gra",
        "admin_game_enter_participants": "👥 <b>Liczba uczestników</b>\n\nWpisz min/max przez «/» lub «-».\nPrzykład: <code>10/100</code>",
        "admin_game_invalid_participants": "❌ Format: <code>min/max</code>, dodatnie liczby, min ≤ max.",
        "admin_game_enter_prizes": "🏆 <b>Nagrody</b>\n\nWpisz kwoty w PLN, każda w nowej linii. Liczba linii = liczba miejsc.\nPrzykład:\n<code>20\n10\n5</code>\n\nZwycięzcy dostaną kwoty automatycznie na saldo.",
        "admin_game_invalid_prizes": "❌ Nagrody muszą być dodatnimi liczbami (np. <code>20</code> lub <code>10.5</code>), każda w nowej linii.",
        "admin_game_prizes_more_than_max": "❌ Miejsc nagrodowych ({n}) jest więcej niż maks. uczestników ({max}).",
        "admin_game_enter_min_topup": "💰 <b>Warunek: minimalna kwota doładowań</b>\n\nFormaty:\n• <code>0</code> — bez warunku\n• <code>100</code> — co najmniej 100 PLN w sumie\n• <code>100 : 01.01.2026</code> — co najmniej 100 PLN od podanej daty",
        "admin_game_invalid_min_topup": "❌ Format: liczba (<code>100</code>) lub liczba i data przez «:» (<code>100 : 01.01.2026</code>).",
        "admin_game_enter_entry_fee": "💵 <b>Opłata wejściowa</b>\n\nWpisz kwotę w PLN (0 = za darmo).",
        "admin_game_invalid_entry_fee": "❌ Wpisz liczbę ≥ 0 (np. <code>0</code> lub <code>5</code>).",
        "admin_game_enter_datetime": "🗓 <b>Data i czas startu</b>\n\nFormaty:\n• <code>DD.MM.RRRR HH:MM</code>\n• <code>HH:MM</code> (dziś)",
        "admin_game_invalid_datetime": "❌ Nie udało się rozpoznać daty/czasu. Przykład: <code>25.12.2026 19:30</code>.",
        "admin_game_datetime_in_past": "❌ Czas startu musi być w przyszłości.",
        "admin_game_topup_since_after_start": "❌ Data początku okresu doładowań jest po dacie startu.",
        "admin_game_preview_title": "📋 <b>Podgląd gry</b>",
        "admin_game_preview_chat": "Czat: <b>{chat}</b>",
        "admin_game_preview_forum_topic": "Wątek: <b>{topic}</b>",
        "admin_game_preview_type": "Typ: <b>{type}</b>",
        "admin_game_preview_participants": "Uczestnicy: <b>{min}–{max}</b>",
        "admin_game_preview_prizes": "Nagrody:",
        "admin_game_preview_min_topup_none": "Warunek: <b>brak</b>",
        "admin_game_preview_min_topup_alltime": "Warunek: doładowania od <b>{n} PLN</b> (cały czas)",
        "admin_game_preview_min_topup_period": "Warunek: doładowania od <b>{n} PLN</b> od <b>{since}</b>",
        "admin_game_preview_pay_free": "Typ: <b>za darmo</b>",
        "admin_game_preview_pay_paid": "Typ: <b>płatna</b>, wejście <b>{fee} PLN</b>",
        "admin_game_preview_datetime": "Start: <b>{datetime}</b>",
        "admin_btn_confirm_create": "✅ Utwórz",
        "admin_btn_cancel_create": "❌ Anuluj",
        "admin_game_created": "✅ Gra #{id} utworzona.",
        "admin_game_create_cancelled": "❌ Anulowano.",
        # ---- Game lists ----
        "admin_games_active_title": "🟢 <b>Bieżące gry</b>",
        "admin_games_past_title": "📚 <b>Minione gry</b>",
        "admin_games_empty_active": "Brak bieżących gier.",
        "admin_games_empty_past": "Brak minionych gier.",
        "admin_game_detail_title": "🎯 <b>Gra #{id}</b>",
        "admin_game_detail_status": "Status: <b>{status}</b>",
        "admin_game_detail_participants_count": "Zapisanych: <b>{count}/{max}</b> (min. {min})",
        "admin_game_status_draft": "oczekuje startu",
        "admin_game_status_active": "trwa",
        "admin_game_status_finished": "zakończona",
        "admin_game_status_cancelled": "anulowana",
        # ---- Announcement ----
        "game_announce_title": "🎯 Gra dla <b>{chat}</b> została utworzona",
        "game_announce_date": "Data: <b>{date}</b>",
        "game_announce_participants_range": "Uczestnicy: <b>{min}–{max}</b>",
        "game_announce_conditions": "<b>Warunki uczestnictwa:</b>",
        "game_announce_cond_min_topup_alltime": "• min. doładowania: <b>{n} PLN</b> (cały czas)",
        "game_announce_cond_min_topup_period": "• min. doładowania: <b>{n} PLN</b> (od {since} do startu)",
        "game_announce_cond_pay_free": "• za darmo",
        "game_announce_cond_pay_paid": "• płatna, wejście <b>{fee} PLN</b>",
        "game_announce_cond_none": "• bez dodatkowych warunków",
        "game_announce_prizes": "<b>Nagrody:</b>",
        "game_announce_signup_link": "Zapis przez bota {bot_link}",
        "game_announce_signup_no_link": "Zapisz się przez prywatną wiadomość do bota.",
        "game_btn_signup": "🎮 Zapisz się",
        "game_reminder_5min": "⏳ Do gry w «{chat_title}» zostało ok. 5 minut.",
        "game_cancelled_not_enough_players_dm": "Gra anulowana: zapisano tylko {current} z {required} graczy.",
        "game_cancelled_refund_full_fee": "Wpłata {fee} PLN została zwrócona na saldo.",
        "game_start_header": "<b>Warunki:</b>\n{conditions}\n\n<b>Nagrody:</b>\n{prizes}",
        "game_start_cond_min_topup_period": "• min. doładowań: {n} PLN (od {since} do {until})",
        "game_start_cond_min_topup_alltime": "• min. doładowań: {n} PLN (cały czas)",
        "game_start_cond_paid": "• gra płatna, wpisowe {fee} PLN",
        "game_start_cond_free": "• gra darmowa",
        "game_start_cond_none": "• bez dodatkowych warunków",
        "game_rules_block": (
            "Zasady:\n"
            "1) Rundy po kolei, 3 rzuty na gracza.\n"
            "2) Można rzucać 🎲 🎳 🎯 (wiadomość dice lub te same emoji w tekście).\n"
            "3) Po rundzie próg to średnia (całkowita część) wśród graczy, którzy rzucali.\n"
            "4) Pominięcia — dogrywka.\n"
            "5) Finał i dogrywka według logiki bota."
        ),
        "game_round1_list_intro": "Runda 1!",
        "round_list_participants": "Lista graczy",
        "round_score_pending": "…",
        "round_score_eliminated": "out",
        "round_your_result": "Twój rzut: {value}",
        "round_throw_2_more": "Rzuć jeszcze 2 razy {emoji}",
        "round_throw_1_more": "Rzuć jeszcze raz {emoji}",
        "round_third_throw_done": "{result_line}\n{name}, wynik rundy: <b>{total}</b>",
        "round_throw_prompt": "{name}, zrób 3 rzuty dowolnym emoji: {emoji}",
        "round_turn_60sec_left": "{name}, została 1 minuta na ruch.",
        "round_participant_skipped": "{name} — pominięty ruch.",
        "round_participants_missed": "Gracze z 0 w tej rundzie:",
        "round_catchup_5min": "Masz czas na 3 rzuty (tryb przyspieszony).",
        "round_1_finished": "Runda 1 zakończona.",
        "round_N_finished": "Runda {round} zakończona.",
        "round_passing_score": "Próg przejścia: {score}",
        "round_list_passed": "Awans do następnej rundy:",
        "round_list_passed_final": "Awans do rundy finałowej:",
        "round_results_header": "Wyniki:",
        "round_tiebreak": "Dogrywka!",
        "round_tiebreak_for": "Aby ustalić: {places}",
        "round_tiebreak_place_one": "{n}. miejsce",
        "round_tiebreak_place_span": "miejsca {a}–{b}",
        "round_tiebreak_throw": "{name}, zrób 1 rzut {emoji}",
        "round_tiebreak_result": "{name} — rzut dogrywki: {value}",
        "round_final_finished": "Finał zakończony.",
        "round_winners": "Zwycięzcy:",
        "game_sponsor_line": "Sponsor: {bot_link}",
        "game_dm_prize_won": "🎉 Zająłeś(-aś) {place}. miejsce! Na saldo dodano <b>{amount} PLN</b>.",
        "game_signup_no_games": "Brak gier z otwartym zapisem.",
        "game_signup_list_title": "Otwarty zapis (wybierz grę):",
        "game_signup_list_item": "#{id} {when} — {chat}",
        "game_signup_btn_join": "✅ Zapisz się",
        "game_signup_btn_leave": "🚫 Wypisz się",
        "game_signup_not_found": "Nie znaleziono gry.",
        "game_signup_not_draft": "Zapis niedostępny (gra nie jest w szkicu).",
        "game_signup_started": "Gra już wystartowała lub zapis zamknięty.",
        "game_signup_full": "Brak wolnych miejsc.",
        "game_signup_min_topup": "Za mało doładowań: wymagane {need} PLN, masz {have} PLN.",
        "game_signup_low_balance": "Za mało środków: wpisowe {fee} PLN, saldo {balance} PLN.",
        "game_signup_already_in": "Jesteś już zapisany(-a).",
        "game_signup_ok": "Zapisano.",
        "game_signup_left": "Wypisano z gry.",
        "game_signup_not_in": "Nie byłeś(-aś) zapisany(-a).",
        "game_signup_card": (
            "🎯 <b>Gra #{id}</b>\n"
            "Czat: {chat}\n"
            "Start: <b>{start}</b>\n"
            "Gracze: <b>{count}</b> / {max_p} (min {min_p})\n\n"
            "<b>Warunki:</b>\n{conditions}\n\n"
            "<b>Nagrody (PLN):</b>\n{prizes}"
        ),
        "game_signup_cond_topup_period": "• doładowania od {n} PLN od {since}",
        "game_signup_cond_topup_alltime": "• doładowania od {n} PLN (cały czas)",
        "game_signup_cond_paid": "• wpisowe {fee} PLN",
        "game_signup_cond_free": "• za darmo",
        "game_signup_cond_none": "—",
        "admin_pay_btn_activate": "▶️ Uruchom",
        "admin_pay_btn_deactivate": "⏹ Zatrzymaj",
        "admin_pay_btn_edit_proxy": "🌐 Zmień proxy",
        "admin_pay_btn_edit_blik": "📱 Zmień BLIK",
        "admin_pay_btn_edit_limit": "📊 Zmień limit",
        "admin_pay_btn_rescan": "🔁 Sprawdź ostatnie maile",
        "admin_pay_btn_delete": "🗑 Usuń",
        "admin_pay_btn_delete_confirm": "✅ Potwierdź usunięcie",
        "admin_pay_btn_cancel": "❌ Anuluj",
        "admin_pay_btn_bank_custom": "✏️ Inny",
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


INPUT_HINT_KEYS = {
    "topup_enter_amount",
    "withdraw_enter_amount",
    "withdraw_enter_blik",
    "slot_enter_bet_with_balance",
    "admin_slot_rules_prompt",
    "admin_checkers_rules_prompt",
    "admin_kmb_rules_prompt",
    "admin_user_search_prompt",
    "admin_user_topup_prompt",
    "admin_user_withdraw_prompt",
    "admin_user_referral_prompt",
    "admin_levels_prompt_title",
    "admin_levels_prompt_required",
    "admin_levels_prompt_reward",
    "admin_levels_prompt_withdraw",
    "admin_levels_prompt_referral",
    "admin_withdraw_fee_title",
    "admin_slot_fee_title",
    "admin_checkers_fee_title",
    "admin_kmb_fee_title",
    "admin_referral_fee_title",
    "admin_game21_fee_bot_title",
    "admin_game21_fee_users_title",
    "admin_21_rules_prompt_bot",
    "admin_21_rules_prompt_users",
    "game21_enter_bet",
    "game21_pvp_enter_bet",
    "checkers_enter_bet",
    "kmb_enter_wins",
    "kmb_enter_bet",
    "admin_chats_enter_button_title",
    "admin_chats_enter_chat_id",
    "admin_game_enter_participants",
    "admin_game_enter_prizes",
    "admin_game_enter_min_topup",
    "admin_game_enter_entry_fee",
    "admin_game_enter_datetime",
}


def t(key: str, language_code: Optional[str] = None) -> str:
    lang = get_lang(language_code)
    value = TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(
        key, TEXTS[DEFAULT_LANG].get(key, key)
    )
    if key in INPUT_HINT_KEYS and "/back" not in value:
        hint = TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(
            "input_cancel_hint", TEXTS[DEFAULT_LANG]["input_cancel_hint"]
        )
        value = f"{value}\n\n{hint}"
    return value
