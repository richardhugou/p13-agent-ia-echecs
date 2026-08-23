import httpx2
import pytest

from services import lichess


class FakeResponse:
    def __init__(self, status_code: int, payload: dict | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload


def test_fetch_masters_401_message_actionnable(monkeypatch) -> None:
    monkeypatch.setattr(httpx2, "get", lambda *a, **k: FakeResponse(401))
    with pytest.raises(lichess.LichessUnavailable, match="LICHESS_API_TOKEN"):
        lichess.fetch_masters("fen")


def test_fetch_masters_429(monkeypatch) -> None:
    monkeypatch.setattr(httpx2, "get", lambda *a, **k: FakeResponse(429))
    with pytest.raises(lichess.LichessRateLimited):
        lichess.fetch_masters("fen")


def test_fetch_masters_5xx(monkeypatch) -> None:
    monkeypatch.setattr(httpx2, "get", lambda *a, **k: FakeResponse(503))
    with pytest.raises(lichess.LichessUnavailable):
        lichess.fetch_masters("fen")


def test_fetch_masters_ok(monkeypatch) -> None:
    monkeypatch.setattr(httpx2, "get", lambda *a, **k: FakeResponse(200, {"moves": []}))
    assert lichess.fetch_masters("fen") == {"moves": []}
