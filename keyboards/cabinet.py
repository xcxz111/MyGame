from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import t


def cabinet_menu_keyboard(
    language_code: str,
    *,
    has_pending_withdrawal: bool = False,
) -> InlineKeyboardMarkup:
    """Клавиатура личного кабинета.

    Если у юзера есть pending заявка на вывод — показываем кнопку
    «Отменить вывод средств» вместо «Запросить вывод».
    """
    lang = language_code
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=t("btn_topup", lang), callback_data="menu:topup"))
    if has_pending_withdrawal:
        builder.row(
            InlineKeyboardButton(
                text=t("btn_cancel_withdraw", lang),
                callback_data="withdraw:cancel_ask",
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text=t("btn_withdraw", lang),
                callback_data="menu:withdraw",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_referral_program", lang),
            callback_data="cabinet:referral",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("btn_cabinet_levels_info", lang),
            callback_data="cabinet:levels_info",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:main", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()
