"""Client LLM multi-fournisseur — ollama (local, défaut POC) | anthropic (option qualité).

Décision D1 révisée (mesures du 2026-08-22) : qwen3.5:4b via Ollama, garde-fous
mesurés : faits annotés + température 0,2 + mode non-pensant. Changer de
fournisseur = changer LLM_PROVIDER.
"""

import json

import httpx2

from config import get_settings

TEMPERATURE = 0.2
MAX_TOKENS = 260


class LLMUnavailable(Exception):
    """Fournisseur injoignable ou en erreur — la synthèse repliera sur le gabarit."""


def generate(system: str, user: str) -> str:
    settings = get_settings()
    if settings.llm_provider == "ollama":
        return _ollama(system, user)
    if settings.llm_provider == "anthropic":
        return _anthropic(system, user)
    raise LLMUnavailable(f"Fournisseur LLM inconnu : {settings.llm_provider!r}")


def _ollama(system: str, user: str) -> str:
    settings = get_settings()
    try:
        response = httpx2.post(
            f"{settings.ollama_base_url}/api/chat",
            json={
                "model": settings.llm_model,
                "stream": False,
                "think": False,
                "options": {"temperature": TEMPERATURE, "num_predict": MAX_TOKENS},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
            timeout=settings.llm_timeout_s,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except (httpx2.HTTPError, KeyError, json.JSONDecodeError) as exc:
        raise LLMUnavailable(f"Ollama : {exc}") from exc


def _anthropic(system: str, user: str) -> str:
    settings = get_settings()
    if not settings.llm_api_key:
        raise LLMUnavailable("LLM_API_KEY manquante pour le fournisseur anthropic")
    try:
        response = httpx2.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.llm_api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": settings.llm_model,
                "max_tokens": MAX_TOKENS,
                "temperature": TEMPERATURE,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=settings.llm_timeout_s,
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]
    except (httpx2.HTTPError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise LLMUnavailable(f"Anthropic : {exc}") from exc
