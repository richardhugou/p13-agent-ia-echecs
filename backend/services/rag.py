"""Recherche documentaire — la bibliothèque Milvus au service du graphe et de l'API.

Règles mesurées (notebook 02) : le préfixe d'instruction s'applique aux REQUÊTES
uniquement, les documents sont indexés nus. Le filtre scalaire traduit un code ECO
(ex. « C50 ») vers son rayon d'ouverture (« italienne ») — mêmes bornes que le
manifeste signé corpus.yml.
"""

import httpx2
from pymilvus import MilvusClient
from pymilvus.exceptions import MilvusException

from config import get_settings

INSTRUCTION = "Instruct: Given a question about chess openings, retrieve relevant passages\nQuery: "

# Bornes ECO du manifeste signé (etl/corpus.yml)
ECO_VERS_OUVERTURE = {
    "italienne": ("C50", "C54"),
    "espagnole": ("C60", "C99"),
    "sicilienne": ("B20", "B99"),
    "francaise": ("C00", "C19"),
    "caro_kann": ("B10", "B19"),
    "gambit_dame": ("D06", "D69"),
    "est_indienne": ("E60", "E99"),
    "anglaise": ("A10", "A39"),
}


class RagUnavailable(Exception):
    """Bibliothèque injoignable (Milvus ou embeddings) — l'agent dégrade sans planter."""


_client: MilvusClient | None = None


def _milvus() -> MilvusClient:
    global _client
    if _client is None:
        settings = get_settings()
        _client = MilvusClient(uri=f"http://{settings.milvus_host}:{settings.milvus_port}")
    return _client


def eco_vers_ouverture(eco: str | None) -> str | None:
    """« C50 » → « italienne » ; hors des rayons du manifeste → None (pas de filtre)."""
    if not eco or len(eco) < 2:
        return None
    for nom, (debut, fin) in ECO_VERS_OUVERTURE.items():
        if debut <= eco[:3].upper() <= fin:
            return nom
    return None


def _embed_question(question: str) -> list[float]:
    settings = get_settings()
    response = httpx2.post(
        f"{settings.ollama_base_url}/api/embed",
        json={"model": settings.embedding_model, "input": [INSTRUCTION + question]},
        timeout=settings.llm_timeout_s,
    )
    if response.status_code >= 400:
        # le corps d'Ollama dit POURQUOI (ex. « model not found ») — 15 min de debug économisées
        raise RagUnavailable(
            f"embeddings HTTP {response.status_code} ({settings.embedding_model}) : "
            f"{response.text[:160]}"
        )
    return response.json()["embeddings"][0]


def search(
    question: str,
    eco: str | None = None,
    k: int | None = None,
    score_min: float | None = None,
) -> list[dict]:
    """Les k fiches les plus proches de la question, filtrées par rayon si l'ECO est connu.

    Les fiches sous le seuil d'abstention sont écartées AVANT le rédacteur : le code
    ne peut pas citer ce qu'il ne transmet pas (décision du 26/08, notebook 07).
    score_min=0.0 désactive le seuil (usage diagnostic : /vector-search).
    """
    settings = get_settings()
    seuil = settings.rag_score_min if score_min is None else score_min
    rayon = eco_vers_ouverture(eco)
    try:
        vecteur = _embed_question(question)
        hits = _milvus().search(
            "openings_kb",
            data=[vecteur],
            limit=k or settings.rag_top_k,
            filter=f'ouverture == "{rayon}"' if rayon else "",
            output_fields=["text", "source_url", "opening_name", "lang", "section", "ouverture"],
        )[0]
    except (httpx2.HTTPError, MilvusException, KeyError, OSError) as exc:
        raise RagUnavailable(f"{type(exc).__name__}: {exc}") from exc
    return [
        {
            "text": hit["entity"]["text"],
            "score": round(hit["distance"], 3),
            "source_url": hit["entity"]["source_url"],
            "opening_name": hit["entity"]["opening_name"],
            "lang": hit["entity"]["lang"],
            "section": hit["entity"]["section"],
            "ouverture": hit["entity"]["ouverture"],
        }
        for hit in hits
        if hit["distance"] >= seuil
    ]
