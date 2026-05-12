"""Проверки прав пользователя."""

from database.models import User, UserRole
from settings import Settings


def is_admin(user: User, settings: Settings) -> bool:
    """Админ — либо `ADMIN_ID` из .env, либо `role='admin'` в БД."""
    if settings.admin_id is not None and int(user.user_id) == int(settings.admin_id):
        return True
    return user.role == UserRole.ADMIN
