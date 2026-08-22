"""Banc de mesure des embeddings (décision D-a) — version test, rejouable à volonté.

Sauté quand Ollama est absent (CI) : c'est une mesure locale, pas un test CI.
Version narrative avec chiffres : notebooks/02-mesures-embeddings.ipynb.
"""

import json
import math
import urllib.request

import pytest

OLLAMA = "http://localhost:11434"
MODELE = "qwen3-embedding:0.6b"
INSTR = "Instruct: Given a question about chess openings, retrieve relevant passages\nQuery: "

QUESTION = "Quelles sont les idées principales de la partie italienne ?"
CIBLE = (
    "La partie italienne commence par 1.e4 e5 2.Cf3 Cc6 3.Fc4. "
    "Le fou en c4 vise le point faible f7 ; les Blancs développent vite."
)
HORS_SUJET = "La tarte tatin se prépare avec des pommes caramélisées."


def _ollama_disponible() -> bool:
    try:
        urllib.request.urlopen(f"{OLLAMA}/api/version", timeout=2)
        return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(
    not _ollama_disponible(), reason="Ollama absent — banc de mesure local uniquement"
)


def _embed(textes: list[str]) -> list[list[float]]:
    corps = json.dumps({"model": MODELE, "input": textes}).encode()
    req = urllib.request.Request(
        f"{OLLAMA}/api/embed", data=corps, headers={"Content-Type": "application/json"}
    )
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))["embeddings"]
    except urllib.error.HTTPError as exc:
        pytest.skip(f"modèle {MODELE} absent ({exc}) — `ollama pull {MODELE}`")


def _cosinus(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(x * x for x in b)))


def test_dimension_conforme_au_plan_milvus() -> None:
    assert len(_embed(["test"])[0]) == 1024


def test_separation_cible_hors_sujet_avec_prefixe() -> None:
    q, cible, hs = _embed([INSTR + QUESTION, CIBLE, HORS_SUJET])
    ecart = _cosinus(q, cible) - _cosinus(q, hs)
    assert ecart > 0.35, f"séparation dégradée : {ecart:.3f} (mesure d'adoption : 0,50)"


def test_le_prefixe_ameliore_la_recherche() -> None:
    sans, avec, cible = _embed([QUESTION, INSTR + QUESTION, CIBLE])
    assert _cosinus(avec, cible) > _cosinus(sans, cible)
