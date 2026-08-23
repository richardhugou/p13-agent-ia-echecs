#!/usr/bin/env bash
set -e

# Définition du répertoire de stockage des modèles Ollama
export OLLAMA_MODELS="${OLLAMA_MODELS:-/app/ollama_models}"
export OLLAMA_HOST="0.0.0.0:11434"

echo "=== Démarrage de la stack complète GPU Coach IA ==="

# Démarrage du serveur Ollama en arrière-plan
ollama serve &
OLLAMA_PID=$!

# Attente active de la disponibilité de l'API Ollama
echo "Initialisation du serveur Ollama (GPU/CPU)..."
MAX_RETRIES=30
COUNT=0
until curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; do
    sleep 1
    COUNT=$((COUNT + 1))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "Avertissement : Ollama a mis trop de temps à répondre."
        break
    fi
done

if [ $COUNT -lt $MAX_RETRIES ]; then
    echo "Serveur Ollama opérationnel."
    # Si le modèle cible n'est pas encore présent, on s'assure qu'il est disponible
    MODEL_NAME="${LLM_MODEL:-qwen3.5:4b}"
    if ! ollama list | grep -q "${MODEL_NAME%%:*}"; then
        echo "Téléchargement du modèle ${MODEL_NAME}..."
        ollama pull "${MODEL_NAME}" || ollama pull "qwen2.5:3b" || echo "Impossible de télécharger ${MODEL_NAME}, bascule sur gabarit si nécessaire."
    fi
fi

# Lancement de l'application FastAPI / Angular
echo "Lancement de FastAPI sur le port 7860..."
exec uv run --no-sync uvicorn main:app --host 0.0.0.0 --port 7860
