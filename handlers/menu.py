"""Обработчики кнопок главного меню."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import app_chats as app_chats_repo
from database.repositories import checkers as checkers_repo
from database.repositories import game21_settings as g21_repo
from database.repositories import slot as slot_repo
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
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    """Возврат в главное меню: как в Game_bot, удаляем источник и шлём меню заново."""
    await state.clear()
    settings = get_settings()
    lang = _user_lang(user, callback)
    menu_chats = await app_chats_repo.list_for_main_menu(session)
    show_game21 = await g21_repo.any_game21_enabled(session)
    show_checkers = await checkers_repo.is_enabled(session)
    show_slot = await slot_repo.is_enabled(session)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=build_welcome_text(lang, user.user_id, user.balance),
        reply_markup=main_menu_keyboard(
            lang,
            user.user_id,
            settings.admin_id,
            menu_chats=menu_chats,
            show_game21=show_game21,
            show_checkers=show_checkers,
            show_slot=show_slot,
        ),
    )
    await callback.answer()
