from fastapi.testclient import TestClient

import api
from main import app

client = TestClient(app)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

EXPLORER_FIXTURE = {
    "white": 100,
    "draws": 80,
    "black": 60,
    "opening": {"eco": "C50", "name": "Italian Game"},
    "moves": [
        {"uci": "e2e4", "san": "e4", "white": 60, "draws": 40, "black": 30},
        {"uci": "d2d4", "san": "d4", "white": 40, "draws": 40, "black": 30},
        {"uci": "e7e5", "san": "e5", "white": 5, "draws": 5, "black": 5},
    ],
    "topGames": [
        {
            "white": {"name": "Kasparov"},
            "black": {"name": "Karpov"},
            "year": 1985,
            "winner": "white",
        }
    ],
}


def test_moves_fen_invalide() -> None:
    response = client.get("/api/v1/moves", params={"fen": "n'importe quoi"})
    assert response.status_code == 400
    assert "FEN invalide" in response.json()["detail"]


def test_moves_position_illegale() -> None:
    # deux rois blancs
    response = client.get("/api/v1/moves", params={"fen": "kK5K/8/8/8/8/8/8/8 w - - 0 1"})
    assert response.status_code == 400


def test_moves_nominal_et_garde_fou_coups_illegaux(monkeypatch) -> None:
    monkeypatch.setattr(api.lichess, "fetch_masters", lambda fen: EXPLORER_FIXTURE)
    response = client.get("/api/v1/moves", params={"fen": START_FEN})
    assert response.status_code == 200
    body = response.json()
    assert body["opening"] == {"eco": "C50", "name": "Italian Game"}
    assert body["in_theory"] is True  # 240 parties >= seuil 5
    ucis = [m["uci"] for m in body["moves"]]
    assert "e2e4" in ucis and "d2d4" in ucis
    assert "e7e5" not in ucis  # coup noir illégal au trait blanc → filtré (objectif O1)
    assert body["moves"][0]["games"] == 130
    assert body["top_games"][0]["white"] == "Kasparov"


def test_moves_hors_theorie(monkeypatch) -> None:
    fixture = {**EXPLORER_FIXTURE, "white": 1, "draws": 0, "black": 1, "moves": []}
    monkeypatch.setattr(api.lichess, "fetch_masters", lambda fen: fixture)
    response = client.get("/api/v1/moves", params={"fen": START_FEN})
    assert response.json()["in_theory"] is False  # 2 parties < seuil 5


def test_moves_lichess_indisponible(monkeypatch) -> None:
    def boom(fen):
        raise api.lichess.LichessUnavailable("Timeout explorer")

    monkeypatch.setattr(api.lichess, "fetch_masters", boom)
    response = client.get("/api/v1/moves", params={"fen": START_FEN})
    assert response.status_code == 503


def test_moves_rate_limited(monkeypatch) -> None:
    def boom(fen):
        raise api.lichess.LichessRateLimited("429")

    monkeypatch.setattr(api.lichess, "fetch_masters", boom)
    response = client.get("/api/v1/moves", params={"fen": START_FEN})
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "60"
