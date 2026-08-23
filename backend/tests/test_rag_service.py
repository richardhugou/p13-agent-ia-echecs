import httpx2
import pytest

from services import rag


def test_eco_vers_ouverture() -> None:
    assert rag.eco_vers_ouverture("C50") == "italienne"
    assert rag.eco_vers_ouverture("B22") == "sicilienne"
    assert rag.eco_vers_ouverture("E75") == "est_indienne"
    assert rag.eco_vers_ouverture("D35") == "gambit_dame"
    assert rag.eco_vers_ouverture("A40") is None  # hors des rayons du manifeste
    assert rag.eco_vers_ouverture("C57") is None  # deux cavaliers : hors bornes signées
    assert rag.eco_vers_ouverture(None) is None


def _fiche(distance: float, ouverture: str = "italienne") -> dict:
    return {
        "distance": distance,
        "entity": {
            "text": "Partie italienne > Page > Section —\nLe fou vise f7.",
            "source_url": "https://fr.wikipedia.org/wiki/Partie_italienne",
            "opening_name": "Partie italienne",
            "lang": "fr",
            "section": "Introduction",
            "ouverture": ouverture,
        },
    }


class FakeMilvus:
    def __init__(self, distances: list[float] | None = None) -> None:
        self.dernier_filtre = None
        self.distances = distances if distances is not None else [0.712]

    def search(self, collection, data, limit, filter, output_fields):
        self.dernier_filtre = filter
        return [[_fiche(d) for d in self.distances]]


def test_search_filtre_par_rayon(monkeypatch) -> None:
    fake = FakeMilvus()
    monkeypatch.setattr(rag, "_milvus", lambda: fake)
    monkeypatch.setattr(rag, "_embed_question", lambda q: [0.0])
    resultats = rag.search("pourquoi le fou en c4 ?", eco="C50")
    assert fake.dernier_filtre == 'ouverture == "italienne"'
    assert resultats[0]["score"] == 0.712
    assert "wikipedia" in resultats[0]["source_url"]


def test_search_sans_eco_sans_filtre(monkeypatch) -> None:
    fake = FakeMilvus()
    monkeypatch.setattr(rag, "_milvus", lambda: fake)
    monkeypatch.setattr(rag, "_embed_question", lambda q: [0.0])
    rag.search("question libre")
    assert fake.dernier_filtre == ""


def test_seuil_filet_ecarte_les_fiches_hors_sujet(monkeypatch) -> None:
    # Décision du 26/08 (notebook 07) : le filet 0,58 coupe les hors-sujet grossiers
    # (pièges mesurés ≤ 0,548) sans toucher les questions réelles (démo 0,629).
    fake = FakeMilvus(distances=[0.712, 0.629, 0.548, 0.486])
    monkeypatch.setattr(rag, "_milvus", lambda: fake)
    monkeypatch.setattr(rag, "_embed_question", lambda q: [0.0])
    scores = [fiche["score"] for fiche in rag.search("pourquoi joue-t-on 3.Fc4 ?")]
    assert scores == [0.712, 0.629]  # 0,548 et 0,486 écartées par le filet
    brut = rag.search("la même, vue diagnostic", score_min=0.0)
    assert len(brut) == 4  # score_min=0.0 : /vector-search garde les scores bruts visibles


def test_rayon_depuis_question() -> None:
    # La règle des rayons signés : le nom d'ouverture dans la question établit le rayon.
    depuis = rag.rayon_depuis_question
    assert depuis("Pourquoi le fou vise-t-il f7 dans la partie italienne ?") == "italienne"
    assert depuis("What are the main lines of the Sicilian Defence?") == "sicilienne"
    assert depuis("Qu'est-ce que la défense slave ?") == "gambit_dame"
    assert depuis("Faut-il accepter le Queen's Gambit ?") == "gambit_dame"
    assert depuis("Quelles sont les idées de la défense scandinave ?") is None
    assert depuis("Comment jouer le gambit du roi ?") is None
    assert depuis("Quelle est la meilleure recette de crêpes bretonnes ?") is None
    assert depuis(None) is None


def test_search_indisponible(monkeypatch) -> None:
    def boom(question):
        raise httpx2.HTTPError("ollama éteint")

    monkeypatch.setattr(rag, "_embed_question", boom)
    with pytest.raises(rag.RagUnavailable):
        rag.search("q")
