"""Vidéos pédagogiques — YouTube Data API v3, métadonnées uniquement, cache 7 jours.

Conformité : jamais les fichiers vidéo — identifiants, titres, durées ; l'affichage
se fait en lien/lecteur intégré côté front. Quota protégé par le cache MongoDB
(une recherche = 100 unités ; les ~8 rayons se stabilisent en ~16 requêtes).
"""

import re
import unicodedata

import httpx2

from config import get_settings
from services.cache import get_cache

DUREE_MIN_S = 4 * 60
DUREE_MAX_S = 30 * 60
MOTS_GENERIQUES = {"partie", "defense", "gambit", "ouverture", "the", "game", "chess"}

NOMS_FR = {
    "italienne": "partie italienne",
    "espagnole": "partie espagnole",
    "sicilienne": "défense sicilienne",
    "francaise": "défense française",
    "caro_kann": "défense caro-kann",
    "gambit_dame": "gambit dame",
    "est_indienne": "défense est-indienne",
    "anglaise": "partie anglaise",
}


class VideosUnavailable(Exception):
    """API YouTube injoignable, clé absente ou quota — l'agent continue sans vidéos."""


def _normaliser(texte: str) -> str:
    sans_accents = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return sans_accents.lower()


def _duree_secondes(iso8601: str) -> int:
    """« PT12M4S » → 724."""
    heures = re.search(r"(\d+)H", iso8601)
    minutes = re.search(r"(\d+)M", iso8601)
    secondes = re.search(r"(\d+)S", iso8601)
    return (
        (int(heures[1]) * 3600 if heures else 0)
        + (int(minutes[1]) * 60 if minutes else 0)
        + (int(secondes[1]) if secondes else 0)
    )


def _titre_pertinent(titre: str, terme: str) -> bool:
    """Le titre doit contenir un mot distinctif du nom d'ouverture (« italienne »…)."""
    titre_n = _normaliser(titre)
    distinctifs = [
        m
        for m in _normaliser(terme).replace("-", " ").split()
        if len(m) >= 4 and m not in MOTS_GENERIQUES
    ]
    return any(m in titre_n for m in distinctifs) if distinctifs else True


def rechercher(terme: str, maxi: int = 3) -> list[dict]:
    """Vidéos pertinentes pour une ouverture (nom FR). Cache 7 j, filtres durée + titre."""
    settings = get_settings()
    if not settings.youtube_api_key:
        raise VideosUnavailable("YOUTUBE_API_KEY manquante dans le .env")

    cache = get_cache()
    cle = _normaliser(terme)
    en_cache = cache.get_videos(cle)
    if en_cache is not None:
        return en_cache[:maxi]

    try:
        recherche = httpx2.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "q": f"{terme} échecs",
                "type": "video",
                "maxResults": 10,
                "relevanceLanguage": "fr",
                "safeSearch": "strict",
                "key": settings.youtube_api_key,
            },
            timeout=settings.lichess_timeout_s,
        )
        if recherche.status_code == 403:
            raise VideosUnavailable(f"clé ou quota YouTube : {recherche.text[:140]}")
        recherche.raise_for_status()
        identifiants = [i["id"]["videoId"] for i in recherche.json().get("items", [])]
        if not identifiants:
            cache.set_videos(cle, [])
            return []

        details = httpx2.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet,contentDetails,status",
                "id": ",".join(identifiants),
                "key": settings.youtube_api_key,
            },
            timeout=settings.lichess_timeout_s,
        )
        details.raise_for_status()
    except httpx2.HTTPError as exc:
        raise VideosUnavailable(f"YouTube injoignable : {exc}") from exc

    videos = []
    for item in details.json().get("items", []):
        duree = _duree_secondes(item["contentDetails"]["duration"])
        if not DUREE_MIN_S <= duree <= DUREE_MAX_S:
            continue
        if not _titre_pertinent(item["snippet"]["title"], terme):
            continue
        videos.append(
            {
                "video_id": item["id"],
                "titre": item["snippet"]["title"],
                "chaine": item["snippet"]["channelTitle"],
                "duree_s": duree,
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "embeddable": bool(item.get("status", {}).get("embeddable")),
            }
        )
    cache.set_videos(cle, videos)
    return videos[:maxi]
