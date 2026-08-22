"""Cache MongoDB — explorer (TTL 24 h) et évaluations Stockfish (sans TTL).

Règle de conception : si MongoDB est indisponible, l'agent dégrade (pas de cache)
mais ne plante jamais.
"""

import logging
from datetime import UTC, datetime
from functools import lru_cache

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import get_settings

logger = logging.getLogger(__name__)

EXPLORER_TTL_S = 24 * 3600
VIDEOS_TTL_S = 7 * 24 * 3600


class MongoCache:
    def __init__(self, uri: str, db_name: str) -> None:
        self.ok = False
        self._explorer = None
        self._evals = None
        self._videos = None
        try:
            self._client: MongoClient = MongoClient(uri, serverSelectionTimeoutMS=1500)
            self._client.admin.command("ping")
            db = self._client[db_name]
            self._explorer = db["explorer_cache"]
            self._evals = db["eval_cache"]
            self._videos = db["videos_cache"]
            self._explorer.create_index("cached_at", expireAfterSeconds=EXPLORER_TTL_S)
            self._explorer.create_index("key", unique=True)
            self._evals.create_index("key", unique=True)
            self._videos.create_index("cached_at", expireAfterSeconds=VIDEOS_TTL_S)
            self._videos.create_index("key", unique=True)
            self.ok = True
        except PyMongoError as exc:
            logger.warning("MongoDB indisponible (%s) — cache désactivé", exc)

    def _get(self, collection, key: str) -> dict | None:
        if not self.ok:
            return None
        try:
            doc = collection.find_one({"key": key})
            return doc["payload"] if doc else None
        except PyMongoError as exc:
            logger.warning("Lecture cache échouée (%s)", exc)
            return None

    def _set(self, collection, key: str, payload: dict) -> None:
        if not self.ok:
            return
        try:
            collection.update_one(
                {"key": key},
                {"$set": {"payload": payload, "cached_at": datetime.now(UTC)}},
                upsert=True,
            )
        except PyMongoError as exc:
            logger.warning("Écriture cache échouée (%s)", exc)

    def get_explorer(self, key: str) -> dict | None:
        return self._get(self._explorer, key)

    def set_explorer(self, key: str, payload: dict) -> None:
        self._set(self._explorer, key, payload)

    def get_videos(self, key: str):
        return self._get(self._videos, key)

    def set_videos(self, key: str, payload: list) -> None:
        self._set(self._videos, key, payload)

    def get_eval(self, key: str) -> dict | None:
        return self._get(self._evals, key)

    def set_eval(self, key: str, payload: dict) -> None:
        self._set(self._evals, key, payload)


@lru_cache
def get_cache() -> MongoCache:
    settings = get_settings()
    return MongoCache(settings.mongo_uri, settings.mongo_db)
