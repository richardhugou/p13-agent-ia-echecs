import shutil

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

stockfish_present = pytest.mark.skipif(
    shutil.which("stockfish") is None, reason="binaire stockfish absent"
)

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
MAT_EN_1 = "6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1"  # Ta1-a8#


def test_evaluate_fen_invalide() -> None:
    response = client.get("/api/v1/evaluate", params={"fen": "xyz"})
    assert response.status_code == 400


@stockfish_present
def test_evaluate_position_initiale() -> None:
    response = client.get("/api/v1/evaluate", params={"fen": START_FEN, "depth": 8})
    assert response.status_code == 200
    body = response.json()
    assert body["mate"] is None
    assert isinstance(body["cp"], int)
    assert abs(body["cp"]) < 150  # la position initiale est ~équilibrée
    assert len(body["best_line"]) > 0
    assert body["engine"] == "stockfish"


@stockfish_present
def test_evaluate_mat_en_un() -> None:
    response = client.get("/api/v1/evaluate", params={"fen": MAT_EN_1, "depth": 8})
    body = response.json()
    assert body["mate"] == 1
    assert body["best_line"][0] == "Ra8#"
