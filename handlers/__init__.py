from aiogram import Router

from handlers.admin import router as admin_router
from handlers.cabinet import router as cabinet_router
from handlers.menu import router as menu_router
from handlers.start import router as start_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(menu_router)
    root.include_router(cabinet_router)
    root.include_router(admin_router)
    return root
