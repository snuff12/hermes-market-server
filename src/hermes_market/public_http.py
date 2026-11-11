"""Bounded public seller reads with DNS validation and a pinned TLS connection."""

import asyncio
import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from .contracts import Problem
from .discovery import exact_origin


def public_origin(value):
    exact_origin(value)
    parsed = urlparse(value)
    host = parsed.hostname
    if (parsed.scheme != "https" or parsed.port not in {None, 443}
            or parsed.netloc != host or host.endswith(".") or "." not in host
            or host.endswith((".localhost", ".local", ".internal", ".test", ".invalid"))):
        raise Problem("public_origin_required", "Use an exact public HTTPS hostname on port 443.", 422)
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return value
    raise Problem("public_origin_required", "Use a public DNS hostname, not an IP address.", 422)


async def public_addresses(host):
    records = await asyncio.get_running_loop().getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    addresses = list(dict.fromkeys(row[4][0] for row in records))
    if not addresses or any(not ipaddress.ip_address(value).is_global for value in addresses):
        raise Problem("seller_address_denied", "The seller must resolve only to public Internet addresses.", 422)
    return addresses


class PublicSellerClient:
    """Never resolve a seller hostname again between validation and connection."""

    def __init__(self, *, resolver=public_addresses, transport=None):
        self.resolve = resolver
        self.slots = asyncio.Semaphore(8)
        self.http = httpx.AsyncClient(timeout=5, follow_redirects=False, trust_env=False,
                                      transport=transport, limits=httpx.Limits(max_connections=8))

    async def get(self, url):
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        public_origin(origin)
        if parsed.query or parsed.fragment or not (
                parsed.path in {"/ui-config", "/health/ready", "/.well-known/hermes-market/review-key"}
                or parsed.path.startswith("/.well-known/hermes-market/listings/")):
            raise Problem("seller_path_denied", "Only public seller discovery endpoints may be read.", 422)
        async with asyncio.timeout(8), self.slots:
            addresses = await self.resolve(parsed.hostname)
            # Defend against an injected or future resolver that omits validation.
            if not addresses or any(not ipaddress.ip_address(ip).is_global for ip in addresses):
                raise Problem("seller_address_denied", "The seller must resolve only to public Internet addresses.", 422)
            ip = addresses[0]
            host = f"[{ip}]" if ":" in ip else ip
            target = f"https://{host}{parsed.path}"
            async with self.http.stream("GET", target, headers={"Host": parsed.netloc, "Accept": "application/json"},
                                        extensions={"sni_hostname": parsed.hostname}) as response:
                content = bytearray()
                async for chunk in response.aiter_bytes():
                    content.extend(chunk)
                    if len(content) > 180_000:
                        raise Problem("seller_response_too_large", "The public seller response is too large.", 502)
                return httpx.Response(response.status_code, headers={"Content-Type": response.headers.get("Content-Type", "application/json")}, content=bytes(content),
                                      request=httpx.Request("GET", url))

    async def aclose(self):
        await self.http.aclose()
