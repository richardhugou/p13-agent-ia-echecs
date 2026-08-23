"""Recherche documentaire — la bibliothèque Milvus au service du graphe et de l'API.

Règles mesurées (notebook 02) : le préfixe d'instruction s'applique aux REQUÊTES
uniquement, les documents sont indexés nus. Le filtre scalaire traduit un code ECO
(ex. « C50 ») vers son rayon d'ouverture (« italienne ») — mêmes bornes que le
manifeste signé corpus.yml.
"""

import unicodedata

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

# Noms et alias FR/EN des 8 rayons — la règle des rayons signés (décision du 26/08) :
# le corpus n'est consulté que dans un rayon établi par la position OU nommé dans la
# question. Une ouverture hors manifeste ne peut ainsi JAMAIS citer de fiches voisines.
ALIAS_VERS_OUVERTURE = {
    "italienne": "italienne",
    "italian": "italienne",
    "giuoco piano": "italienne",
    "espagnole": "espagnole",
    "ruy lopez": "espagnole",
    "spanish game": "espagnole",
    "sicilienne": "sicilienne",
    "sicilian": "sicilienne",
    "francaise": "francaise",
    "french": "francaise",
    "caro-kann": "caro_kann",
    "caro kann": "caro_kann",
    "gambit dame": "gambit_dame",
    "gambit de la dame": "gambit_dame",
    "queens gambit": "gambit_dame",
    "slave": "gambit_dame",
    "slav": "gambit_dame",
    "est-indienne": "est_indienne",
    "est indienne": "est_indienne",
    "kings indian": "est_indienne",
    "anglaise": "anglaise",
    "english": "anglaise",
}


class RagUnavailable(Exception):
    """Bibliothèque injoignable (Milvus ou embeddings) — l'agent dégrade sans planter."""


_client: MilvusClient | None = None


def _milvus() -> MilvusClient:
    global _client
    if _client is None:
        settings = get_settings()
        # MILVUS_LITE_PATH non vide (ex. /tmp/openings.db) = Milvus Lite embarqué (vitrine)
        uri = settings.milvus_lite_path or f"http://{settings.milvus_host}:{settings.milvus_port}"
        _client = MilvusClient(uri=uri)
    return _client


def _normaliser(texte: str) -> str:
    """Minuscules, sans accents ni apostrophes — pour comparer des noms d'ouvertures."""
    sans_accents = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return sans_accents.casefold().replace("'", "")


def rayon_depuis_question(question: str | None) -> str | None:
    """« pourquoi le fou vise f7 dans la partie italienne ? » → « italienne » ; inconnu → None."""
    if not question:
        return None
    q = _normaliser(question)
    for alias, rayon in ALIAS_VERS_OUVERTURE.items():
        if alias in q:
            return rayon
    return None


def eco_vers_ouverture(eco: str | None) -> str | None:
    """« C50 » → « italienne » ; hors des rayons du manifeste → None (pas de filtre)."""
    if not eco or len(eco) < 2:
        return None
    for nom, (debut, fin) in ECO_VERS_OUVERTURE.items():
        if debut <= eco[:3].upper() <= fin:
            return nom
    return None


_modele_local = None


def _embed_local(texte: str) -> list[float]:
    """Embeddings sans Ollama (mode vitrine) : le MÊME modèle Qwen3-Embedding-0.6B,
    servi par sentence-transformers sur CPU — même espace vectoriel que le corpus."""
    global _modele_local
    if _modele_local is None:
        from sentence_transformers import SentenceTransformer

        _modele_local = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", device="cpu")
    return _modele_local.encode([texte], normalize_embeddings=True)[0].tolist()


def _embed_question(question: str) -> list[float]:
    settings = get_settings()
    if settings.embed_provider == "local":
        try:
            return _embed_local(INSTRUCTION + question)
        except Exception as exc:  # noqa: BLE001 — toute panne d'embedding = bibliothèque KO
            raise RagUnavailable(f"embeddings locaux : {type(exc).__name__}: {exc}") from exc
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
    rayon: str | None = None,
) -> list[dict]:
    """Les k fiches les plus proches de la question, filtrées par rayon si connu.

    Le rayon vient de l'appelant (règle des rayons signés, nœud contexte_rag) ou de
    l'ECO. Les fiches sous le seuil filet sont écartées AVANT le rédacteur : le code
    ne peut pas citer ce qu'il ne transmet pas. score_min=0.0 désactive le filet
    (usage diagnostic : /vector-search).
    """
    settings = get_settings()
    seuil = settings.rag_score_min if score_min is None else score_min
    rayon = rayon or eco_vers_ouverture(eco)
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
