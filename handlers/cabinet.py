"""Хендлеры личного кабинета."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import withdrawals as withdrawals_repo
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


async def build_cabinet_view(
    session: AsyncSession, user: User, lang: str
) -> tuple[str, InlineKeyboardMarkup]:
    """Возвращает (текст, клавиатуру) для экрана личного кабинета."""
    pending = await withdrawals_repo.get_pending_for_user(session, user.user_id)
    text = (
        f"{t('cabinet_title', lang)}\n\n"
        + t("cabinet_balance", lang).format(balance=_fmt_balance(user.balance))
    )
    kb = cabinet_menu_keyboard(lang, has_pending_withdrawal=pending is not None)
    return text, kb


async def render_cabinet(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    """Редактирует текущее сообщение колбэка в экран кабинета."""
    lang = user.language_code or get_lang(callback.from_user.language_code)
    text, kb = await build_cabinet_view(session, user, lang)
    await callback.message.edit_text(text, reply_markup=kb)


async def send_cabinet(
    message: Message, session: AsyncSession, user: User
) -> None:
    """Шлёт НОВОЕ сообщение с экраном кабинета (для случаев когда edit неуместен)."""
    lang = user.language_code or get_lang(
        getattr(message.from_user, "language_code", None)
    )
    text, kb = await build_cabinet_view(session, user, lang)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "menu:cabinet", F.message.chat.type == "private")
async def on_menu_cabinet(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    await render_cabinet(callback, session, user)
    await callback.answer()
