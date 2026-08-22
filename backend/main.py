"""API du POC agent IA ouvertures d'échecs — point d'entrée FastAPI."""

import os
from importlib.metadata import version as pkg_version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

APP_VERSION = "0.1.0"

app = FastAPI(
    title="Agent IA ouvertures d'échecs — POC FFE",
    version=APP_VERSION,
    description="Coups théoriques (Lichess), contexte RAG (Milvus), vidéos (YouTube), "
    "évaluation moteur (Stockfish), orchestrés par LangGraph.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:4200").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/healthcheck")
def healthcheck() -> dict:
    """Statut du service et versions — sera enrichi de l'état Milvus/MongoDB plus tard."""
    return {
        "status": "ok",
        "service": "backend",
        "version": APP_VERSION,
        "fastapi": pkg_version("fastapi"),
    }
