from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models.payments.account import MBankAccount
from locales.texts import t

NO_PROXY_BTN_TEXT = "🚫 Без прокси"
REMOVE_LIMIT_BTN_TEXT = "♾ Снять лимит"

BANK_LABELS = {
    "ipko": "🏦 iPKO",
    "santander": "🏦 Santander",
    "other": "🏦 Другой банк",
}


def _status_emoji(account: MBankAccount) -> str:
    if not account.is_active:
        return "⚪"
    if account.limit_sleeping:
        return "😴"
    return "🟢"


def payments_list_keyboard(
    accounts: list[MBankAccount], language_code: str
) -> InlineKeyboardMarkup:
    """Список аккаунтов + «Добавить» + «Комиссия вывода» + Назад/Главная."""
    lang = language_code
    builder = InlineKeyboardBuilder()
    for acc in accounts:
        emoji = _status_emoji(acc)
        blik = acc.blik_number or "—"
        builder.row(
            InlineKeyboardButton(
                text=f"{emoji} #{acc.id} {blik} - {acc.email}",
                callback_data=f"admin:pay:acc:{acc.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_add", lang),
            callback_data="admin:pay:add",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:settings", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def account_detail_keyboard(
    account: MBankAccount, language_code: str
) -> InlineKeyboardMarkup:
    """Карточка аккаунта с управлением."""
    lang = language_code
    builder = InlineKeyboardBuilder()

    if account.is_active:
        builder.row(
            InlineKeyboardButton(
                text=t("admin_pay_btn_deactivate", lang),
                callback_data=f"admin:pay:deactivate:{account.id}",
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=t("admin_pay_btn_activate", lang),
                callback_data=f"admin:pay:activate:{account.id}",
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_edit_proxy", lang),
            callback_data=f"admin:pay:edit_proxy:{account.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_edit_blik", lang),
            callback_data=f"admin:pay:edit_blik:{account.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_edit_limit", lang),
            callback_data=f"admin:pay:edit_limit:{account.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_rescan", lang),
            callback_data=f"admin:pay:rescan:{account.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_delete", lang),
            callback_data=f"admin:pay:delete:{account.id}",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:settings:payments", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def delete_confirm_keyboard(account_id: int, language_code: str) -> InlineKeyboardMarkup:
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_delete_confirm", lang),
            callback_data=f"admin:pay:delete_confirm:{account_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_cancel", lang),
            callback_data=f"admin:pay:acc:{account_id}",
        )
    )
    return builder.as_markup()


def bank_select_keyboard(language_code: str) -> InlineKeyboardMarkup:
    lang = language_code
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=BANK_LABELS["ipko"], callback_data="admin:pay:bank:ipko")
    )
    builder.row(
        InlineKeyboardButton(
            text=BANK_LABELS["santander"], callback_data="admin:pay:bank:santander"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_bank_custom", lang),
            callback_data="admin:pay:bank_custom",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_pay_btn_cancel", lang),
            callback_data="admin:settings:payments",
        )
    )
    return builder.as_markup()


def no_proxy_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=NO_PROXY_BTN_TEXT)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_limit_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=REMOVE_LIMIT_BTN_TEXT)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
