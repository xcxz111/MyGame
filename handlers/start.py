from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import app_chats as app_chats_repo
from keyboards import language_keyboard, main_menu_keyboard
from locales.texts import LANG_NAMES, get_lang, t
from settings import get_settings
from texts import build_welcome_text

router = Router(name="start")


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(message: Message, session: AsyncSession, user: User) -> None:
    """Создание/обновление юзера уже сделано в UserMiddleware."""
    settings = get_settings()

    if user.language_code is None:
        hint_lang = get_lang(message.from_user.language_code)
        await message.answer(
            t("choose_language", hint_lang),
            reply_markup=language_keyboard(),
        )
        return

    menu_chats = await app_chats_repo.list_for_main_menu(session)
    await message.answer(
        build_welcome_text(user.language_code, user.user_id, user.balance),
        reply_markup=main_menu_keyboard(
            user.language_code,
            user.user_id,
            settings.admin_id,
            menu_chats=menu_chats,
        ),
    )


@router.callback_query(F.data.startswith("lang:"), F.message.chat.type == "private")
async def on_language_chosen(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    settings = get_settings()
    code = callback.data.split(":", 1)[1] if callback.data else ""
    if code not in LANG_NAMES:
        await callback.answer()
        return

    user.language_code = code

    menu_chats = await app_chats_repo.list_for_main_menu(session)
    await callback.message.edit_text(
        build_welcome_text(code, user.user_id, user.balance),
        reply_markup=main_menu_keyboard(
            code, user.user_id, settings.admin_id, menu_chats=menu_chats
        ),
    )
    await callback.answer()
