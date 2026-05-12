from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from keyboards import language_keyboard, main_menu_keyboard
from locales.texts import LANG_NAMES, get_lang, t
from settings import get_settings
from storage.user_language import get_stored_language, set_stored_language
from texts import build_welcome_text

router = Router(name="start")


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(message: Message) -> None:
    settings = get_settings()
    user_id = message.from_user.id
    hint_lang = get_lang(message.from_user.language_code)

    stored = get_stored_language(user_id)
    if stored is not None:
        await message.answer(
            build_welcome_text(stored, user_id),
            reply_markup=main_menu_keyboard(stored, user_id, settings.admin_id),
        )
        return

    await message.answer(
        t("choose_language", hint_lang),
        reply_markup=language_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"), F.chat.type == "private")
async def on_language_chosen(callback: CallbackQuery) -> None:
    settings = get_settings()
    user_id = callback.from_user.id
    code = callback.data.split(":", 1)[1] if callback.data else ""
    if code not in LANG_NAMES:
        await callback.answer()
        return

    set_stored_language(user_id, code)
    await callback.message.edit_text(
        build_welcome_text(code, user_id),
        reply_markup=main_menu_keyboard(code, user_id, settings.admin_id),
    )
    await callback.answer()
