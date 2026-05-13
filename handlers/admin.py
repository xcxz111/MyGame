"""Хендлеры админки."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from keyboards import (
    admin_bot_settings_keyboard,
    admin_fees_keyboard,
    admin_menu_keyboard,
)
from locales.texts import get_lang, t
from permissions import is_admin
from settings import get_settings

router = Router(name="admin")


def _resolve_lang(user: User, callback: CallbackQuery) -> str:
    return user.language_code or get_lang(callback.from_user.language_code)


async def _deny_if_not_admin(callback: CallbackQuery, user: User, lang: str) -> bool:
    """Возвращает True, если доступ запрещён (и уже показано всплывающее)."""
    if is_admin(user, get_settings()):
        return False
    await callback.answer(t("admin_no_access", lang), show_alert=True)
    return True


@router.callback_query(F.data == "menu:admin", F.message.chat.type == "private")
async def on_menu_admin(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return

    await state.clear()
    await callback.message.edit_text(
        t("admin_title", lang),
        reply_markup=admin_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:settings", F.message.chat.type == "private")
async def on_admin_settings(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return

    await state.clear()
    await callback.message.edit_text(
        t("admin_settings_title", lang),
        reply_markup=admin_bot_settings_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(
    F.data == "admin:settings:fees", F.message.chat.type == "private"
)
async def on_admin_fees(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return

    await callback.message.edit_text(
        t("admin_fees_title", lang),
        reply_markup=admin_fees_keyboard(lang),
    )
    await callback.answer()
