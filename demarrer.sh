#!/usr/bin/env bash
# Démarrage complet du POC — neutralise les pannes rencontrées (journal du 24/08) :
#   1. Ollama mort avec son shell        → démarré en service, attendu, vérifié
#   2. modèle absent (404 « not found ») → pull automatique des deux modèles
#   3. conteneur gelé sur un vieux .env  → compose up -d recrée si la config a changé
#      (jamais « docker restart », qui ne relit PAS le .env)
set -euo pipefail
cd "$(dirname "$0")"

echo "── Ollama ──"
if ! curl -sf http://localhost:11434/api/version > /dev/null; then
  if command -v brew > /dev/null; then
    brew services start ollama > /dev/null 2>&1 || nohup ollama serve > /tmp/ollama.log 2>&1 &
  else
    nohup ollama serve > /tmp/ollama.log 2>&1 &
  fi
  until curl -sf http://localhost:11434/api/version > /dev/null; do sleep 1; done
fi
echo "ollama OK : $(curl -sf http://localhost:11434/api/version)"

for modele in "qwen3.5:4b" "qwen3-embedding:0.6b"; do
  ollama list | grep -q "$modele" || { echo "pull $modele…"; ollama pull "$modele"; }
done
echo "modèles OK"

echo "── .env ──"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  .env créé depuis l'exemple : remplir LICHESS_API_TOKEN avant la théorie"
fi

echo "── Docker ──"
if ! docker info > /dev/null 2>&1; then
  open -a Docker
  until docker info > /dev/null 2>&1; do sleep 2; done
fi
docker compose up -d --build

echo "── Santé ──"
until [ "$(docker inspect -f '{{.State.Health.Status}}' p13-api 2>/dev/null)" = "healthy" ]; do
  sleep 2
done
curl -sf http://localhost:8000/api/v1/healthcheck; echo
echo "── Bibliothèque (Milvus recharge ses collections après un redémarrage) ──"
until curl -sf "http://localhost:8000/api/v1/vector-search?q=pret&k=1" > /dev/null 2>&1; do
  sleep 3
done
echo "bibliothèque prête"
echo "✅ POC prêt — Swagger : http://localhost:8000/docs · MLflow : http://localhost:5001"
