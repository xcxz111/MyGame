"""MonitorManager — владеет всеми IMAP-мониторами, синхронизирует их с БД."""

import asyncio
import logging
from datetime import datetime, time, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from aiogram import Bot
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from database.models.payments.account import MBankAccount
from services.payments.ai_clients.base import AIClient
from services.payments.imap_monitor import AccountMonitor
from services.payments.limit_service import reset_all_limits
from services.payments.transaction_handler import BankTransactionHandler
from settings import Settings

logger = logging.getLogger(__name__)

WARSAW_TZ = ZoneInfo("Europe/Warsaw")


class MonitorManager:
    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
        ai_client: AIClient,
        settings: Settings,
        bot: Optional[Bot] = None,
    ) -> None:
        self._session_maker = session_maker
        self._settings = settings
        self._bot = bot
        self._handler = BankTransactionHandler(
            session_maker=session_maker,
            ai_client=ai_client,
            bot=bot,
            settings=settings,
        )
        self._monitors: dict[int, AccountMonitor] = {}
        self._daily_reset_task: Optional[asyncio.Task] = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def start_all(self) -> None:
        async with self._session_maker() as session:
            result = await session.execute(
                select(MBankAccount).where(MBankAccount.is_active.is_(True))
            )
            accounts = list(result.scalars().all())

        for account in accounts:
            self._start(account)

        # фоновая задача сброса дневных лимитов в полночь по Варшаве
        if self._daily_reset_task is None:
            self._daily_reset_task = asyncio.create_task(
                self._daily_reset_loop(), name="mbanks-daily-reset"
            )

        logger.info("MonitorManager: started %d account monitor(s)", len(accounts))

    async def stop_all(self) -> None:
        if self._daily_reset_task and not self._daily_reset_task.done():
            self._daily_reset_task.cancel()
            try:
                await self._daily_reset_task
            except asyncio.CancelledError:
                pass
        self._daily_reset_task = None

        for monitor in list(self._monitors.values()):
            await monitor.stop()
        self._monitors.clear()
        logger.info("MonitorManager: all monitors stopped")

    # ── Per-account control (вызывается из админки) ───────────────────────────

    async def add_account(self, account_id: int) -> None:
        account = await self._load(account_id)
        if account and account.is_active:
            self._start(account)

    async def remove_account(self, account_id: int) -> None:
        await self._stop(account_id)

    async def restart_account(self, account_id: int) -> None:
        await self._stop(account_id)
        account = await self._load(account_id)
        if account and account.is_active:
            self._start(account)

    def status(self) -> dict[int, dict]:
        return {
            account_id: {
                "email": m.email_addr,
                "running": m.is_running,
                "last_uid": m.last_uid,
            }
            for account_id, m in self._monitors.items()
        }

    # ── Internals ─────────────────────────────────────────────────────────────

    def _start(self, account: MBankAccount) -> None:
        if account.id in self._monitors:
            logger.debug("Monitor for account_id=%d already running", account.id)
            return

        monitor = AccountMonitor(
            account_id=account.id,
            email_addr=account.email,
            password=account.password,
            imap_host=account.imap_host,
            imap_port=account.imap_port,
            use_ssl=account.use_ssl,
            mailbox=account.mailbox,
            proxy_url=account.proxy,
            last_uid=account.last_uid,
            on_new_message=self._handler.on_new_message,
            on_uid_update=self._persist_uid,
            on_deactivate=self._deactivate_account,
            reconnect_initial_delay=self._settings.imap_reconnect_initial_delay,
            reconnect_max_delay=self._settings.imap_reconnect_max_delay,
            reconnect_max_failures=self._settings.imap_reconnect_max_failures,
            idle_timeout=self._settings.imap_idle_timeout,
            imap_timeout=self._settings.imap_timeout,
            initial_backfill_count=self._settings.imap_initial_backfill_count,
        )
        monitor.start()
        self._monitors[account.id] = monitor
        logger.info(
            "MonitorManager: started monitor for %s (id=%d)", account.email, account.id
        )

    async def _stop(self, account_id: int) -> None:
        monitor = self._monitors.pop(account_id, None)
        if monitor:
            await monitor.stop()
            logger.info(
                "MonitorManager: stopped monitor for account_id=%d", account_id
            )

    async def _load(self, account_id: int) -> MBankAccount | None:
        async with self._session_maker() as session:
            return await session.get(MBankAccount, account_id)

    async def _persist_uid(self, account_id: int, uid: int) -> None:
        async with self._session_maker() as session:
            await session.execute(
                update(MBankAccount)
                .where(MBankAccount.id == account_id)
                .values(last_uid=uid)
            )
            await session.commit()

    async def _deactivate_account(self, account_id: int) -> None:
        self._monitors.pop(account_id, None)
        async with self._session_maker() as session:
            await session.execute(
                update(MBankAccount)
                .where(MBankAccount.id == account_id)
                .values(is_active=False)
            )
            await session.commit()
        logger.warning(
            "MonitorManager: account_id=%d deactivated after too many reconnect failures",
            account_id,
        )

    # ── Daily reset ───────────────────────────────────────────────────────────

    async def _daily_reset_loop(self) -> None:
        """Раз в сутки в 00:00 по Варшаве сбрасывает daily_used и будит «спящих»."""
        while True:
            try:
                now = datetime.now(tz=WARSAW_TZ)
                tomorrow = (now + timedelta(days=1)).date()
                next_midnight = datetime.combine(tomorrow, time.min, tzinfo=WARSAW_TZ)
                sleep_seconds = (next_midnight - now).total_seconds()
                await asyncio.sleep(max(sleep_seconds, 1))
                await reset_all_limits(self._session_maker)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error("daily_reset_loop error: %s", exc, exc_info=True)
                await asyncio.sleep(60)
