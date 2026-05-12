"""IMAP-монитор одного аккаунта: backfill + IDLE цикл с автопереподключением."""

import asyncio
import email
import logging
import re
from email.header import decode_header
from typing import Any, Awaitable, Callable, Optional

import aioimaplib

from services.payments.imap_client import create_imap_client

logger = logging.getLogger(__name__)

OnNewMessage = Callable[[str, int, dict[str, Any]], Awaitable[None]]
OnUidUpdate = Callable[[int, int], Awaitable[None]]
OnDeactivate = Callable[[int], Awaitable[None]]


class AccountMonitor:
    def __init__(
        self,
        account_id: int,
        email_addr: str,
        password: str,
        imap_host: str,
        imap_port: int,
        use_ssl: bool,
        mailbox: str,
        proxy_url: Optional[str],
        last_uid: int,
        on_new_message: OnNewMessage,
        on_uid_update: OnUidUpdate,
        on_deactivate: Optional[OnDeactivate] = None,
        reconnect_initial_delay: int = 5,
        reconnect_max_delay: int = 300,
        reconnect_max_failures: int = 10,
        idle_timeout: int = 1740,
        imap_timeout: int = 120,
        initial_backfill_count: int = 0,
    ) -> None:
        self.account_id = account_id
        self.email_addr = email_addr
        self.password = password
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.use_ssl = use_ssl
        self.mailbox = mailbox
        self.proxy_url = proxy_url
        self.last_uid = last_uid
        self.on_new_message = on_new_message
        self.on_uid_update = on_uid_update
        self.on_deactivate = on_deactivate
        self._reconnect_initial_delay = reconnect_initial_delay
        self._reconnect_max_delay = reconnect_max_delay
        self._reconnect_max_failures = reconnect_max_failures
        self._idle_timeout = idle_timeout
        self._imap_timeout = imap_timeout
        self._initial_backfill_count = max(0, initial_backfill_count)

        self._running = False
        self._task: Optional[asyncio.Task] = None

    # ── Public control ────────────────────────────────────────────────────────

    def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(
            self._run_loop(), name=f"imap-monitor-{self.email_addr}"
        )

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    @property
    def is_running(self) -> bool:
        return self._running

    # ── Main loop ─────────────────────────────────────────────────────────────

    async def _run_loop(self) -> None:
        delay = self._reconnect_initial_delay
        consecutive_failures = 0

        while self._running:
            try:
                await self._session()
                delay = self._reconnect_initial_delay
                consecutive_failures = 0
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                consecutive_failures += 1
                logger.error(
                    "[%s] Session error (%d/%d): %s",
                    self.email_addr,
                    consecutive_failures,
                    self._reconnect_max_failures,
                    exc,
                    exc_info=True,
                )
                if not self._running:
                    break
                if consecutive_failures >= self._reconnect_max_failures:
                    logger.warning(
                        "[%s] Reached %d consecutive failures — deactivating account",
                        self.email_addr,
                        self._reconnect_max_failures,
                    )
                    self._running = False
                    if self.on_deactivate:
                        await self.on_deactivate(self.account_id)
                    break
                logger.info("[%s] Reconnecting in %ds …", self.email_addr, delay)
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._reconnect_max_delay)

    # ── Single IMAP session ───────────────────────────────────────────────────

    async def _session(self) -> None:
        client = create_imap_client(
            host=self.imap_host,
            port=self.imap_port,
            use_ssl=self.use_ssl,
            proxy_url=self.proxy_url,
            timeout=self._imap_timeout,
        )
        try:
            await client.wait_hello_from_server()

            resp = await client.login(self.email_addr, self.password)
            if resp.result != "OK":
                raise ConnectionError(f"LOGIN failed: {resp.lines}")
            logger.info("[%s] Logged in to %s", self.email_addr, self.imap_host)

            resp = await client.select(self.mailbox)
            if resp.result != "OK":
                raise ConnectionError(f"SELECT {self.mailbox!r} failed: {resp.lines}")

            await self._backfill(client)
            await self._idle_loop(client)
        finally:
            try:
                await asyncio.wait_for(client.logout(), timeout=5)
            except Exception:
                pass

    # ── Backfill ──────────────────────────────────────────────────────────────

    async def _backfill(self, client: aioimaplib.IMAP4) -> None:
        if self.last_uid == 0:
            await self._set_initial_anchor(client)
            # Если после якоря last_uid всё ещё 0 — ящик пуст, выходим
            if self.last_uid == 0 and self._initial_backfill_count == 0:
                return

        seqs = await self._search_seqs_since_uid(client, self.last_uid)
        if not seqs:
            logger.debug("[%s] No messages to backfill", self.email_addr)
            return

        logger.info(
            "[%s] Backfilling %d message(s) (UID > %d)",
            self.email_addr,
            len(seqs),
            self.last_uid,
        )
        for seq in seqs:
            await self._fetch_and_dispatch(client, seq)

    async def _set_initial_anchor(self, client: aioimaplib.IMAP4) -> None:
        """
        Якорь для нового аккаунта (last_uid==0).

        Если задан `initial_backfill_count > 0`, отматываем last_uid так,
        чтобы перечитать последние N писем (по UID — последние N независимо
        от наличия «дыр» в нумерации).
        Иначе ставим якорь на UID последнего письма и пропускаем историю.
        """
        resp = await client.uid_search("ALL")
        if resp.result != "OK":
            logger.warning(
                "[%s] UID SEARCH ALL failed: %s", self.email_addr, resp.lines
            )
            return

        raw = resp.lines[0] if resp.lines else b""
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("ascii", errors="ignore")
        uids = sorted(int(s) for s in raw.split() if s.isdigit())

        if not uids:
            logger.info(
                "[%s] Mailbox is empty — will deliver from first incoming message",
                self.email_addr,
            )
            return

        latest_uid = uids[-1]

        if self._initial_backfill_count > 0:
            tail = uids[-self._initial_backfill_count:]
            # last_uid должен быть строго меньше UID первого письма из «хвоста»,
            # чтобы SEARCH UID (tail[0]):* подхватил ровно их.
            self.last_uid = max(0, tail[0] - 1)
            await self.on_uid_update(self.account_id, self.last_uid)
            logger.info(
                "[%s] Initial backfill: re-reading last %d/%d message(s) "
                "(UID %d..%d, last_uid set to %d)",
                self.email_addr,
                len(tail),
                len(uids),
                tail[0],
                tail[-1],
                self.last_uid,
            )
        else:
            self.last_uid = latest_uid
            await self.on_uid_update(self.account_id, latest_uid)
            logger.info(
                "[%s] Initial anchor set to UID=%d — history skipped",
                self.email_addr,
                latest_uid,
            )

    # ── IDLE loop ─────────────────────────────────────────────────────────────

    async def _idle_loop(self, client: aioimaplib.IMAP4) -> None:
        logger.info("[%s] Entering IDLE loop (last_uid=%d)", self.email_addr, self.last_uid)
        _IDLE_POLL_INTERVAL = 30

        while self._running:
            idle_future = await client.idle_start(timeout=self._idle_timeout)
            logger.debug(
                "[%s] IDLE started (poll interval %ds)",
                self.email_addr,
                _IDLE_POLL_INTERVAL,
            )
            try:
                push = await client.wait_server_push(timeout=_IDLE_POLL_INTERVAL)
                logger.info("[%s] IDLE push: %s", self.email_addr, push)
            except asyncio.TimeoutError:
                logger.debug(
                    "[%s] No push in %ds — checking for new messages",
                    self.email_addr,
                    _IDLE_POLL_INTERVAL,
                )
            except Exception as exc:
                logger.warning("[%s] wait_server_push error: %s", self.email_addr, exc)
            finally:
                client.idle_done()
                try:
                    await asyncio.wait_for(idle_future, timeout=10)
                except (asyncio.TimeoutError, asyncio.CancelledError, Exception) as e:
                    logger.debug("[%s] idle_future wait ended: %s", self.email_addr, e)

            seqs = await self._search_seqs_since_uid(client, self.last_uid)
            if seqs:
                logger.debug("[%s] SEARCH returned seqs: %s", self.email_addr, seqs)
            for seq in seqs:
                await self._fetch_and_dispatch(client, seq)

    # ── Helpers ───────────────────────────────────────────────────────────────

    async def _search_seqs_since_uid(
        self, client: aioimaplib.IMAP4, since_uid: int
    ) -> list[int]:
        start = since_uid + 1
        resp = await client.search(f"UID {start}:*")
        if resp.result != "OK":
            logger.warning("[%s] SEARCH failed: %s", self.email_addr, resp.lines)
            return []

        raw = resp.lines[0]
        if isinstance(raw, bytes):
            raw = raw.decode()
        return sorted(int(s) for s in raw.split() if s.isdigit())

    async def _fetch_and_dispatch(self, client: aioimaplib.IMAP4, seq: int) -> None:
        uid_resp = await client.fetch(str(seq), "(UID)")
        if uid_resp.result != "OK":
            logger.warning(
                "[%s] FETCH(UID) seq=%d failed: %s",
                self.email_addr,
                seq,
                uid_resp.lines,
            )
            return

        uid = self._extract_uid(uid_resp.lines)
        if uid is None:
            logger.warning("[%s] FETCH seq=%d: could not parse UID", self.email_addr, seq)
            return

        if uid <= self.last_uid:
            logger.debug(
                "[%s] Skipping seq=%d UID=%d (already processed)",
                self.email_addr,
                seq,
                uid,
            )
            return

        resp = await client.fetch(str(seq), "(UID RFC822)")
        if resp.result != "OK":
            logger.warning("[%s] FETCH seq=%d failed: %s", self.email_addr, seq, resp.lines)
            return

        raw_bytes = self._extract_literal(resp.lines)
        if not raw_bytes:
            logger.warning(
                "[%s] FETCH seq=%d (UID=%d): no message data", self.email_addr, seq, uid
            )
            return

        msg = email.message_from_bytes(raw_bytes)
        parsed = _parse_message(msg)
        try:
            await self.on_new_message(self.email_addr, uid, parsed)
        except Exception as exc:
            logger.error(
                "[%s] on_new_message raised for UID=%d: %s",
                self.email_addr,
                uid,
                exc,
                exc_info=True,
            )

        self.last_uid = uid
        await self.on_uid_update(self.account_id, uid)

    @staticmethod
    def _extract_uid(lines: list) -> Optional[int]:
        for item in lines:
            if isinstance(item, (bytes, bytearray)):
                item = item.decode("ascii", errors="ignore")
            if isinstance(item, str):
                m = re.search(r"\bUID\s+(\d+)", item, re.IGNORECASE)
                if m:
                    return int(m.group(1))
        return None

    @staticmethod
    def _extract_literal(lines: list) -> Optional[bytes]:
        candidates = [
            bytes(item)
            for item in lines
            if isinstance(item, (bytes, bytearray)) and len(item) > 30
        ]
        return max(candidates, key=len) if candidates else None


# ── Email parsing ─────────────────────────────────────────────────────────────


def _decode_header_value(raw: str) -> str:
    parts = decode_header(raw or "")
    decoded: list[str] = []
    for value, charset in parts:
        if isinstance(value, bytes):
            try:
                decoded.append(value.decode(charset or "utf-8", errors="replace"))
            except (LookupError, TypeError):
                decoded.append(value.decode("latin-1", errors="replace"))
        else:
            decoded.append(value)
    return "".join(decoded)


def _parse_message(msg: email.message.Message) -> dict[str, Any]:
    subject = _decode_header_value(msg.get("Subject", ""))
    from_addr = _decode_header_value(msg.get("From", ""))
    to_addr = _decode_header_value(msg.get("To", ""))
    date = msg.get("Date", "")

    body_plain = ""
    body_html = ""

    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain" and not body_plain:
                payload = part.get_payload(decode=True)
                if payload:
                    body_plain = payload.decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
            elif ct == "text/html" and not body_html:
                payload = part.get_payload(decode=True)
                if payload:
                    body_html = payload.decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                body_html = text
            else:
                body_plain = text

    return {
        "subject": subject,
        "from": from_addr,
        "to": to_addr,
        "date": date,
        "body": body_plain or body_html,
        "body_plain": body_plain,
        "body_html": body_html,
        "raw": msg,
    }
