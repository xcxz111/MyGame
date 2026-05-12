"""IMAP-клиент с опциональным SOCKS/HTTP-прокси."""

import asyncio
import logging
import ssl
from typing import Optional

import aioimaplib

logger = logging.getLogger(__name__)


class _ProxyMixin:
    proxy_url: Optional[str]

    async def _proxy_socket(self) -> asyncio.BaseTransport:
        from python_socks.async_.asyncio import Proxy  # lazy import

        proxy = Proxy.from_url(self.proxy_url)
        sock = await proxy.connect(dest_host=self.host, dest_port=self.port)
        return sock


class ProxiedIMAP4(_ProxyMixin, aioimaplib.IMAP4):
    def __init__(
        self, host: str, port: int, proxy_url: Optional[str] = None, timeout: float = 30
    ) -> None:
        self.proxy_url = proxy_url
        super().__init__(host=host, port=port, timeout=timeout)

    async def _connect(self) -> None:
        if not self.proxy_url:
            await super()._connect()
            return
        sock = await self._proxy_socket()
        loop = asyncio.get_running_loop()
        await loop.create_connection(lambda: self.protocol, sock=sock)
        await self.wait_hello_from_server()


class ProxiedIMAP4SSL(_ProxyMixin, aioimaplib.IMAP4_SSL):
    def __init__(
        self,
        host: str,
        port: int,
        proxy_url: Optional[str] = None,
        timeout: float = 30,
        ssl_context: Optional[ssl.SSLContext] = None,
    ) -> None:
        self.proxy_url = proxy_url
        super().__init__(host=host, port=port, timeout=timeout, ssl_context=ssl_context)

    async def _connect(self) -> None:
        if not self.proxy_url:
            await super()._connect()
            return
        sock = await self._proxy_socket()
        ctx = self.ssl_context or ssl.create_default_context()
        loop = asyncio.get_running_loop()
        await loop.create_connection(
            lambda: self.protocol,
            sock=sock,
            ssl=ctx,
            server_hostname=self.host,
        )
        await self.wait_hello_from_server()


def create_imap_client(
    host: str,
    port: int,
    use_ssl: bool,
    proxy_url: Optional[str] = None,
    timeout: float = 30,
) -> aioimaplib.IMAP4:
    if use_ssl:
        return ProxiedIMAP4SSL(host=host, port=port, proxy_url=proxy_url, timeout=timeout)
    return ProxiedIMAP4(host=host, port=port, proxy_url=proxy_url, timeout=timeout)
