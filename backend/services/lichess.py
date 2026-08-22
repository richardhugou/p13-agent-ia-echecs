"""Client Lichess Opening Explorer (base masters) — source de vérité des coups théoriques."""

import httpx2

from config import get_settings

USER_AGENT = "P13-POC-chess-agent/0.2 (contact: richard.hugou@gmail.com)"


class LichessUnavailable(Exception):
    """Explorer injoignable ou en refus (timeout, réseau, 401, 5xx)."""


class LichessRateLimited(Exception):
    """HTTP 429 — la règle Lichess impose d'attendre 60 s."""


def fetch_masters(fen: str) -> dict:
    """Interroge /masters pour un FEN. Lève LichessUnavailable ou LichessRateLimited."""
    settings = get_settings()
    headers = {"User-Agent": USER_AGENT}
    if settings.lichess_api_token:
        headers["Authorization"] = f"Bearer {settings.lichess_api_token}"
    try:
        response = httpx2.get(
            f"{settings.lichess_explorer_url}/masters",
            params={"fen": fen, "topGames": 4},
            headers=headers,
            timeout=settings.lichess_timeout_s,
        )
    except httpx2.TimeoutException as exc:
        raise LichessUnavailable(f"Timeout explorer ({settings.lichess_timeout_s}s)") from exc
    except httpx2.HTTPError as exc:
        raise LichessUnavailable(f"Explorer injoignable : {exc}") from exc

    if response.status_code == 429:
        raise LichessRateLimited("Rate limit Lichess atteint — réessayer dans 60 s")
    if response.status_code == 401:
        raise LichessUnavailable(
            "Explorer : 401 Unauthorized — définir LICHESS_API_TOKEN "
            "(jeton personnel gratuit, requis depuis 2026)"
        )
    if response.status_code >= 400:
        raise LichessUnavailable(f"Explorer en erreur HTTP {response.status_code}")
    return response.json()
