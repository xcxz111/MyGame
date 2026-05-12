"""Обработчики кнопок главного меню."""

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from keyboards import language_keyboard, main_menu_keyboard
from locales.texts import get_lang, t
from settings import get_settings
from texts import build_welcome_text

router = Router(name="menu")


def _user_lang(user: User, callback: CallbackQuery) -> str:
    """Язык из БД, а если ещё не выбран — по подсказке клиента Telegram."""
    return user.language_code or get_lang(callback.from_user.language_code)


@router.callback_query(F.data == "menu:lang", F.message.chat.type == "private")
async def on_menu_lang(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    """🌐 — показываем выбор языка и кнопку возврата на главную."""
    lang = _user_lang(user, callback)
    await callback.message.edit_text(
        t("choose_language", lang),
        reply_markup=language_keyboard(with_back_to_main=True, nav_lang=lang),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:main", F.message.chat.type == "private")
async def on_menu_main(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    """Возврат в главное меню."""
    settings = get_settings()
    lang = _user_lang(user, callback)
    await callback.message.edit_text(
        build_welcome_text(lang, user.user_id, user.balance),
        reply_markup=main_menu_keyboard(lang, user.user_id, settings.admin_id),
    )
    await callback.answer()
