from aiogram import Router

from handlers.admin import router as admin_router
from handlers.admin_payments import router as admin_payments_router
from handlers.cabinet import router as cabinet_router
from handlers.menu import router as menu_router
from handlers.start import router as start_router
from handlers.topup import router as topup_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(menu_router)
    root.include_router(cabinet_router)
    root.include_router(topup_router)
    root.include_router(admin_payments_router)
    root.include_router(admin_router)
    return root
