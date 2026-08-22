"""API du POC agent IA ouvertures d'échecs — point d'entrée FastAPI."""

from contextlib import asynccontextmanager
from importlib.metadata import version as pkg_version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from config import get_settings
from services import engine
from services.cache import get_cache

APP_VERSION = "0.4.0"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    engine.shutdown()


app = FastAPI(
    title="Agent IA ouvertures d'échecs — POC FFE",
    version=APP_VERSION,
    description="Coups théoriques (Lichess), contexte RAG (Milvus), vidéos (YouTube), "
    "évaluation moteur (Stockfish), orchestrés par LangGraph.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/api/v1/healthcheck")
def healthcheck() -> dict:
    """Statut du service et de ses dépendances."""
    return {
        "status": "ok",
        "service": "backend",
        "version": APP_VERSION,
        "fastapi": pkg_version("fastapi"),
        "mongo_cache": "ok" if get_cache().ok else "off",
    }
