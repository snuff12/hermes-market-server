import json
import socket

import httpx
import pytest

from hermes_market.api import admin_app
from hermes_market.contracts import PROTOCOL, Problem
from hermes_market.directory import ServiceDirectory, directory_app
from hermes_market.public_http import PublicSellerClient, public_addresses, public_origin
from hermes_market.settings import TestnetSettings, initialize_testnet

MARKET = "https://market.example.com"
SELLER = "https://seller.example.com"


@pytest.mark.parametrize("origin", ["http://127.0.0.1:8785", "https://127.0.0.1", "https://169.254.169.254", "https://[::1]", "https://seller.local", "https://seller.example.com:8443", "https://seller.example.com.", "https://SELLER.example.com"])
def test_public_directory_rejects_nonpublic_or_ambiguous_origins(origin):
    with pytest.raises(Problem):
        public_origin(origin)


async def test_dns_validation_rejects_mixed_public_and_private_answers(monkeypatch):
    async def lookup(*args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443)) for ip in ["1.1.1.1", "127.0.0.1"]]
    import asyncio
    monkeypatch.setattr(asyncio.get_running_loop(), "getaddrinfo", lookup)
    with pytest.raises(Problem, match="only to public"):
        await public_addresses("seller.example.com")


async def test_public_fetch_pins_ip_host_and_tls_name_without_a_second_lookup():
    calls = []
    async def resolve(host):
        calls.append(("dns", host))
        return ["1.1.1.1"]
    async def fetch(request):
        calls.append((str(request.url), request.headers["host"], request.extensions["sni_hostname"]))
        return httpx.Response(200, json={"ready": True})
    client = PublicSellerClient(resolver=resolve, transport=httpx.MockTransport(fetch))
    try:
        assert (await client.get(SELLER + "/health/ready")).json()["ready"]
        assert calls == [("dns", "seller.example.com"), ("https://1.1.1.1/health/ready", "seller.example.com", "seller.example.com")]
        with pytest.raises(Problem):
            await client.get(SELLER + "/admin/services")
    finally:
        await client.aclose()


async def test_redirects_and_oversized_documents_cannot_expand_public_fetches():
    calls = []
    async def resolve(host): return ["1.1.1.1"]
    async def fetch(request):
        calls.append(request.url.path)
        if request.url.path == "/ui-config":
            return httpx.Response(302, headers={"Location": "http://169.254.169.254/"})
        return httpx.Response(200, content=b"x" * 180_001)
    client = PublicSellerClient(resolver=resolve, transport=httpx.MockTransport(fetch))
    try:
        assert (await client.get(SELLER + "/ui-config")).status_code == 302
        with pytest.raises(Problem, match="too large"):
            await client.get(SELLER + "/health/ready")
        assert calls == ["/ui-config", "/health/ready"]
    finally:
        await client.aclose()


async def test_public_registration_requires_owner_opt_in_and_testnet_contract(tmp_path, revision):
    publication = {"protocol": PROTOCOL, "directory_origin": MARKET, "origin": SELLER,
                   "mode": "testnet", "service": revision["public"]}
    enabled = False
    async def fetch(request):
        assert request.headers["host"] == "seller.example.com"
        if request.url.path == "/health/ready": return httpx.Response(200, json={"ready": True})
        return httpx.Response(200, json=publication) if enabled else httpx.Response(404)
    directory = ServiceDirectory(tmp_path / "directory.sqlite3", MARKET, public=True, open_registration=True,
                                 transport=httpx.MockTransport(fetch))
    async def resolve(host): return ["1.1.1.1"]
    directory.client.resolve = resolve
    try:
        with pytest.raises(Problem): await directory.refresh(SELLER, "diff-review")
        enabled = True
        record = await directory.refresh(SELLER, "diff-review")
        assert record["origin"] == SELLER and record["state"] == "online"
        assert "bundle" not in json.dumps(record)
        publication["mode"] = "simulation"
        assert (await directory.refresh(SELLER, "diff-review"))["state"] == "offline"
        with pytest.raises(Problem): await directory.refresh("https://127.0.0.1", "diff-review")
        app = directory_app(directory)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=MARKET) as browser:
            assert (await browser.get("/ui-config", headers={"CF-Connecting-IP": "8.8.8.8"})).json()["public_directory"]
            assert (await browser.get("/v1/listings", headers={"Host": "evil.example"})).status_code == 403
            assert (await browser.post("/v1/listings", json={"origin": SELLER, "slug": "diff-review"})).status_code == 403
            assert (await browser.get("/v1/listings", headers={"Origin": "https://evil.example"})).status_code == 403
    finally:
        await directory.close()


def test_public_seller_separates_https_identity_from_loopback_listener(tmp_path):
    path = initialize_testnet(tmp_path / "testnet")["config"]
    data = json.loads(open(path).read())
    data.update(origin=SELLER, directory_origin=MARKET, listen_port=8985)
    open(path, "w").write(json.dumps(data))
    settings = TestnetSettings.load(path)
    assert settings.origin == SELLER and settings.port == 8985 and settings.admin_port == 8786
    del data["listen_port"]
    open(path, "w").write(json.dumps(data))
    with pytest.raises(ValueError, match="listen_port"): TestnetSettings.load(path)


async def test_remote_directory_does_not_expose_owner_workspace(seller):
    app = admin_app(seller, "owner-token", directory_origin=MARKET)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1:8766") as client:
        assert (await client.get("/ui-config")).json()["directory_origin"] == MARKET
        assert (await client.get("/ui-config", headers={"CF-Connecting-IP": "8.8.8.8"})).status_code == 403


def test_hostname_change_cannot_rekey_existing_orders(seller):
    from conftest import quote
    order = quote(seller)
    seller.store.bind_origin(order["origin"])
    with pytest.raises(Problem, match="another seller origin"):
        seller.store.bind_origin(SELLER)
    assert seller.store.order(order["id"])["order_digest"] == order["order_digest"]


def test_tunnel_configuration_exposes_only_two_public_applications(tmp_path):
    from hermes_market.tunnel import write_config
    path = tmp_path / "tunnel.json"
    write_config(path, "1525ac19-656f-4d42-bc2b-4e6f7f646d3c", tmp_path / "credential.json", MARKET, SELLER)
    config = json.loads(path.read_text())
    assert [row["service"] for row in config["ingress"]] == ["http://127.0.0.1:8995", "http://127.0.0.1:8985", "http_status:404"]
    assert all("token" not in row for row in config["ingress"])
    assert path.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError):
        write_config(path, config["tunnel"], tmp_path / "credential.json", MARKET, SELLER)
