from aiogram import Router

from handlers.admin import router as admin_router
from handlers.admin_chats import router as admin_chats_router
from handlers.admin_game21 import router as admin_game21_router
from handlers.admin_games import router as admin_games_router
from handlers.admin_payments import router as admin_payments_router
from handlers.game21 import router as game21_router
from handlers.cabinet import router as cabinet_router
from handlers.forum_topic_sync import router as forum_topic_sync_router
from handlers.game_play import router as game_play_router
from handlers.game_signup import router as game_signup_router
from handlers.menu import router as menu_router
from handlers.slot import router as slot_router
from handlers.start import router as start_router
from handlers.topup import router as topup_router
from handlers.withdraw import router as withdraw_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(menu_router)
    root.include_router(game21_router)
    root.include_router(slot_router)
    root.include_router(game_signup_router)
    root.include_router(cabinet_router)
    root.include_router(topup_router)
    root.include_router(withdraw_router)
    root.include_router(forum_topic_sync_router)
    root.include_router(game_play_router)
    root.include_router(admin_games_router)
    root.include_router(admin_chats_router)
    root.include_router(admin_payments_router)
    root.include_router(admin_game21_router)
    root.include_router(admin_router)
    return root
