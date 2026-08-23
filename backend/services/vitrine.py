"""Mode vitrine (Hugging Face Space) — le corpus pré-vectorisé entre dans Milvus Lite.

Le fichier d'export (space/corpus_export.json.gz) contient les 477 fiches AVEC leurs
vecteurs, produits par le même modèle d'embedding que le POC local : au premier
démarrage du Space, on les insère telles quelles — aucun embedding de document à
recalculer, seule la requête est vectorisée à la volée (sentence-transformers).
"""

import gzip
import json
import logging

from pymilvus import DataType, MilvusClient

logger = logging.getLogger(__name__)

COLLECTION = "openings_kb"


def charger_corpus_si_vide(client: MilvusClient, chemin_export: str) -> None:
    if client.has_collection(COLLECTION):
        if client.get_collection_stats(COLLECTION).get("row_count", 0) > 0:
            logger.info("vitrine : collection déjà chargée")
            return
        client.drop_collection(COLLECTION)

    with gzip.open(chemin_export, "rt", encoding="utf-8") as f:
        fiches = json.load(f)
    logger.info("vitrine : chargement de %d fiches pré-vectorisées", len(fiches))

    schema = client.create_schema(auto_id=True, enable_dynamic_field=False)
    schema.add_field("pk", DataType.INT64, is_primary=True)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=len(fiches[0]["vector"]))
    schema.add_field("text", DataType.VARCHAR, max_length=8192)
    schema.add_field("source_url", DataType.VARCHAR, max_length=512)
    schema.add_field("opening_name", DataType.VARCHAR, max_length=256)
    schema.add_field("lang", DataType.VARCHAR, max_length=8)
    schema.add_field("section", DataType.VARCHAR, max_length=512)
    schema.add_field("ouverture", DataType.VARCHAR, max_length=64)

    index = client.prepare_index_params()
    index.add_index("vector", metric_type="COSINE", index_type="AUTOINDEX")
    client.create_collection(COLLECTION, schema=schema, index_params=index)

    for debut in range(0, len(fiches), 100):
        client.insert(COLLECTION, fiches[debut : debut + 100])
    logger.info("vitrine : bibliothèque prête")
