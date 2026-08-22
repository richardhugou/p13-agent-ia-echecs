"""Configuration centralisée — tout vient des variables d'environnement (.env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:4200"

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "chessagent"

    milvus_host: str = "localhost"
    milvus_port: int = 19530
    embedding_model: str = "qwen3-embedding:0.6b"
    rag_top_k: int = 5

    lichess_explorer_url: str = "https://explorer.lichess.ovh"
    lichess_api_token: str = ""  # requis depuis 2026 : l'explorer répond 401 sans autorisation
    lichess_timeout_s: float = 8.0
    theory_min_games: int = 5

    stockfish_path: str = ""  # vide = auto-détection (PATH puis /usr/games/stockfish)
    stockfish_depth: int = 16
    stockfish_time_ms: int = 1000

    # Synthèse LLM — D1 révisée le 2026-08-22 : ollama/qwen3.5:4b titulaire, mesuré.
    # "none" = gabarit déterministe seul (défaut sûr : tests, CI, démo hors-ligne).
    youtube_api_key: str = ""

    llm_provider: str = "none"  # none | ollama | anthropic
    llm_model: str = "qwen3.5:4b"
    llm_api_key: str = ""  # requis seulement pour anthropic
    llm_timeout_s: float = 30.0
    ollama_base_url: str = "http://localhost:11434"


@lru_cache
def get_settings() -> Settings:
    return Settings()
