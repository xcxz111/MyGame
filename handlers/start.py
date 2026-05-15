from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import app_chats as app_chats_repo
from database.repositories import checkers as checkers_repo
from database.repositories import game21_settings as g21_repo
from database.repositories import slot as slot_repo
from database.repositories import users as users_repo
from keyboards import language_keyboard, main_menu_keyboard
from locales.texts import LANG_NAMES, get_lang, t
from settings import get_settings
from texts import build_welcome_text

router = Router(name="start")


def _start_referrer_id(message: Message) -> int | None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return None
    payload = parts[1].strip()
    if payload.startswith("ref_"):
        payload = payload[4:]
    try:
        return int(payload)
    except ValueError:
        return None


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(message: Message, session: AsyncSession, user: User) -> None:
    """Создание/обновление юзера уже сделано в UserMiddleware."""
    settings = get_settings()
    referrer_id = _start_referrer_id(message)
    if referrer_id is not None:
        await users_repo.set_referrer_if_empty(session, user.user_id, referrer_id)

    if user.language_code is None:
        hint_lang = get_lang(message.from_user.language_code)
        await message.answer(
            t("choose_language", hint_lang),
            reply_markup=language_keyboard(),
        )
        return

    menu_chats = await app_chats_repo.list_for_main_menu(session)
    show_game21 = await g21_repo.any_game21_enabled(session)
    show_checkers = await checkers_repo.is_enabled(session)
    show_kmb = await app_chats_repo.any_kmb_enabled(session)
    show_slot = await slot_repo.is_enabled(session)
    await message.answer(
        build_welcome_text(
            user.language_code, user.user_id, user.balance, user.level or 0
        ),
        reply_markup=main_menu_keyboard(
            user.language_code,
            user.user_id,
            settings.admin_id,
            menu_chats=menu_chats,
            show_game21=show_game21,
            show_checkers=show_checkers,
            show_kmb=show_kmb,
            show_slot=show_slot,
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
    show_game21 = await g21_repo.any_game21_enabled(session)
    show_checkers = await checkers_repo.is_enabled(session)
    show_kmb = await app_chats_repo.any_kmb_enabled(session)
    show_slot = await slot_repo.is_enabled(session)
    await callback.message.edit_text(
        build_welcome_text(code, user.user_id, user.balance, user.level or 0),
        reply_markup=main_menu_keyboard(
            code,
            user.user_id,
            settings.admin_id,
            menu_chats=menu_chats,
            show_game21=show_game21,
            show_checkers=show_checkers,
            show_kmb=show_kmb,
            show_slot=show_slot,
        ),
    )
    await callback.answer()
