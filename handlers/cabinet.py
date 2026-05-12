"""Хендлеры личного кабинета."""

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from keyboards import cabinet_menu_keyboard
from locales.texts import get_lang, t

router = Router(name="cabinet")


@router.callback_query(F.data == "menu:cabinet", F.message.chat.type == "private")
async def on_menu_cabinet(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = user.language_code or get_lang(callback.from_user.language_code)
    await callback.message.edit_text(
        t("cabinet_title", lang),
        reply_markup=cabinet_menu_keyboard(lang),
    )
    await callback.answer()
