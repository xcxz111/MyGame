"""Хендлеры личного кабинета."""

from html import escape

from aiogram import F, Router
from aiogram import Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import withdrawals as withdrawals_repo
from database.repositories import users as users_repo
from keyboards import cabinet_menu_keyboard
from locales.texts import get_lang, t

router = Router(name="cabinet")


def _fmt_balance(balance) -> str:
    if balance is None:
        return "0"
    try:
        if balance == balance.to_integral_value():
            return str(int(balance))
        return f"{balance:f}".rstrip("0").rstrip(".")
    except Exception:
        return str(balance)


async def _referral_link(bot: Bot, user_id: int) -> str:
    me = await bot.get_me()
    return f"https://t.me/{me.username}?start=ref_{user_id}"


def _back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:cabinet", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


async def build_cabinet_view(
    session: AsyncSession, user: User, lang: str, bot: Bot
) -> tuple[str, InlineKeyboardMarkup]:
    """Возвращает (текст, клавиатуру) для экрана личного кабинета."""
    pending = await withdrawals_repo.get_pending_for_user(session, user.user_id)
    link = await _referral_link(bot, user.user_id)
    text = (
        f"{t('cabinet_title', lang)}\n\n"
        + t("cabinet_balance", lang).format(balance=_fmt_balance(user.balance))
        + "\n\n"
        + t("cabinet_referral_link", lang).format(link=link)
    )
    kb = cabinet_menu_keyboard(lang, has_pending_withdrawal=pending is not None)
    return text, kb


async def render_cabinet(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    """Редактирует текущее сообщение колбэка в экран кабинета."""
    lang = user.language_code or get_lang(callback.from_user.language_code)
    text, kb = await build_cabinet_view(session, user, lang, bot)
    await callback.message.edit_text(text, reply_markup=kb)


async def send_cabinet(
    message: Message, session: AsyncSession, user: User, bot: Bot
) -> None:
    """Шлёт НОВОЕ сообщение с экраном кабинета (для случаев когда edit неуместен)."""
    lang = user.language_code or get_lang(
        getattr(message.from_user, "language_code", None)
    )
    text, kb = await build_cabinet_view(session, user, lang, bot)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "menu:cabinet", F.message.chat.type == "private")
async def on_menu_cabinet(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    await render_cabinet(callback, session, user, bot)
    await callback.answer()


@router.callback_query(F.data == "cabinet:referral", F.message.chat.type == "private")
async def on_referral_program(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = user.language_code or get_lang(callback.from_user.language_code)
    link = await _referral_link(bot, user.user_id)
    percent = await users_repo.effective_referral_percent(session, user)
    referrals = await users_repo.list_referrals_with_profit(session, user.user_id)
    if referrals:
        lines = []
        for referral, profit in referrals:
            name = referral.name or referral.user_name or str(referral.user_id)
            lines.append(
                t("referral_line", lang).format(
                    name=escape(name),
                    profit=_fmt_balance(profit),
                )
            )
        referrals_text = "\n".join(lines)
    else:
        referrals_text = t("referral_empty", lang)

    await callback.message.edit_text(
        t("referral_program_text", lang).format(
            link=link,
            percent=_fmt_balance(percent),
            referrals=referrals_text,
        ),
        reply_markup=_back_keyboard(lang),
    )
    await callback.answer()
