"""Configuration centralisée — tout vient des variables d'environnement (.env)."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:4200"

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "chessagent"

    lichess_explorer_url: str = "https://explorer.lichess.ovh"
    lichess_api_token: str = ""  # requis depuis 2026 : l'explorer répond 401 sans autorisation
    lichess_timeout_s: float = 8.0
    theory_min_games: int = 5

    stockfish_path: str = ""  # vide = auto-détection (PATH puis /usr/games/stockfish)
    stockfish_depth: int = 16
    stockfish_time_ms: int = 1000


@lru_cache
def get_settings() -> Settings:
    return Settings()
