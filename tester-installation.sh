#!/usr/bin/env bash
# Test d'installation fraîche — mesure le critère « docker compose up → utilisable < 5 min ».
# Protocole : conteneurs + images construites + cache de build supprimés ; les VOLUMES sont
# conservés (le corpus et les runs MLflow sont des données, pas de l'installation) ; les
# images de base (node, nginx, python, milvus…) restent en cache local — sur une machine
# réellement vierge, ajouter leur téléchargement (dépend du réseau).
# Mesuré le 23/08/2026 (Apple M5) : app utilisable à 2 min 09 · bibliothèque prête à 2 min 28.
set -euo pipefail
cd "$(dirname "$0")"

docker compose down --rmi local
docker builder prune -f

debut=$(date +%s)
docker compose up -d --build
until [ "$(docker inspect -f '{{.State.Health.Status}}' p13-api 2>/dev/null)" = "healthy" ]; do sleep 2; done
curl -sf -o /dev/null http://localhost:4200/
echo "✅ app utilisable à $(( $(date +%s) - debut )) s"
until curl -sf "http://localhost:8000/api/v1/vector-search?q=pret&k=1" > /dev/null 2>&1; do sleep 3; done
echo "✅ bibliothèque vectorielle prête à $(( $(date +%s) - debut )) s"
