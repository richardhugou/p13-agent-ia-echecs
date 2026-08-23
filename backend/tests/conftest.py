"""Hermétisme des tests : aucun fournisseur externe ambiant ne doit fuir dans la suite.

Leçon du 2026-08-23 : un LLM_PROVIDER=ollama fantôme dans l'environnement a fait
parler le vrai Qwen dans les tests e2e (réponses non déterministes, suite 14× plus
lente). Ici on fige l'environnement AVANT tout import applicatif, puis on purge le
cache de configuration.
"""

import os

os.environ["LLM_PROVIDER"] = "none"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:1"  # port muet : un appel fuité échoue vite
os.environ["MILVUS_HOST"] = "localhost"

from config import get_settings  # noqa: E402

get_settings.cache_clear()
