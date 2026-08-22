"""Chargement — vectorisation des fiches et insertion dans Milvus (commit 3 d'É3).

- Embeddings via Ollama (qwen3-embedding:0.6b, 1024 d) — documents NUS : le préfixe
  d'instruction est réservé aux requêtes (règle mesurée, notebook 02).
- Passe near-dup promise au commit 2 : cosinus > 0,95 entre fiches → la seconde est écartée.
- Collection openings_kb : schéma de la diapo 7, index HNSW, métrique cosinus.
- Contrôles post-charge : count == insérées + requêtes de bon sens. Rapport chiffré.
"""

import json
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from pymilvus import DataType, MilvusClient

import argparse

_p = argparse.ArgumentParser(description="Chargement paramétrable (Run A/B)")
_p.add_argument("--dossier", default="chunks")
_p.add_argument("--collection", default="openings_kb")
ARGS, _ = _p.parse_known_args()

CHUNKS = Path(__file__).parent / ARGS.dossier / "chunks.jsonl"
RAPPORT = Path(__file__).parent / ARGS.dossier / "rapport-chargement.json"
OLLAMA = "http://localhost:11434"
MODELE = "qwen3-embedding:0.6b"
MILVUS = "http://localhost:19530"
COLLECTION = ARGS.collection
INSTR = "Instruct: Given a question about chess openings, retrieve relevant passages\nQuery: "
NEAR_DUP_SEUIL = 0.95


def embed(textes: list[str]) -> list[list[float]]:
    corps = json.dumps({"model": MODELE, "input": textes}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/embed", data=corps,
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))["embeddings"]


def lots_adaptatifs(textes: list[str], max_items: int = 16, max_chars: int = 8000):
    """Lots bornés en nombre ET en volume — 32 grosses fiches d'un coup noient le runner."""
    lot: list[str] = []
    for texte in textes:
        if lot and (len(lot) >= max_items or sum(map(len, lot)) + len(texte) > max_chars):
            yield lot
            lot = []
        lot.append(texte)
    if lot:
        yield lot


def vectoriser(fiches: list[dict], rapport: dict) -> np.ndarray:
    debut = time.perf_counter()
    vecteurs: list[list[float]] = []
    # 3000 c ≈ 750 tokens (plafond sûr mesuré du runner) : garde-fou par fiche ; lots adaptatifs : garde-fou par requête ;
    # repli fiche-par-fiche si le runner refuse un lot (crash EOF observé sur les grosses fiches)
    replis = 0
    for lot in lots_adaptatifs([f["text"][:3000] for f in fiches]):
        try:
            vecteurs += embed(lot)
        except urllib.error.HTTPError:
            replis += 1
            for texte in lot:
                for tentative in (1, 2, 3):
                    try:
                        vecteurs += embed([texte])
                        break
                    except urllib.error.HTTPError:
                        if tentative == 3:
                            raise
                        time.sleep(2)
    rapport["lots_en_repli"] = replis
    rapport["vectorisation_s"] = round(time.perf_counter() - debut, 1)
    matrice = np.array(vecteurs, dtype=np.float32)
    return matrice / np.linalg.norm(matrice, axis=1, keepdims=True)


def ecarter_near_dups(fiches: list[dict], matrice: np.ndarray, rapport: dict):
    similarites = matrice @ matrice.T
    np.fill_diagonal(similarites, 0.0)
    a_ecarter: set[int] = set()
    paires = []
    for i, j in zip(*np.where(similarites > NEAR_DUP_SEUIL), strict=True):
        if i < j and j not in a_ecarter:
            a_ecarter.add(int(j))
            paires.append({"gardee": fiches[i]["id"], "ecartee": fiches[j]["id"],
                           "similarite": round(float(similarites[i, j]), 3)})
    rapport["near_dups_cosinus"] = len(a_ecarter)
    rapport["paires_near_dup"] = paires[:10]
    garder = [k for k in range(len(fiches)) if k not in a_ecarter]
    return [fiches[k] for k in garder], matrice[garder]


def creer_collection(client: MilvusClient) -> None:
    if client.has_collection(COLLECTION):
        client.drop_collection(COLLECTION)
    schema = client.create_schema(auto_id=True)
    schema.add_field("pk", DataType.INT64, is_primary=True)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=1024)
    schema.add_field("text", DataType.VARCHAR, max_length=8192)
    for champ, longueur in [("ouverture", 64), ("eco", 32), ("opening_name", 512),
                            ("fen_ref", 128), ("lang", 8), ("source_url", 512),
                            ("licence", 32), ("section", 256), ("content_hash", 64),
                            ("ingested_at", 40)]:
        schema.add_field(champ, DataType.VARCHAR, max_length=longueur)
    index = client.prepare_index_params()
    index.add_index("vector", index_type="HNSW", metric_type="COSINE",
                    params={"M": 16, "efConstruction": 200})
    client.create_collection(COLLECTION, schema=schema, index_params=index)


def controles(client: MilvusClient, attendu: int) -> list[str]:
    """Requêtes de bon sens : la bonne ouverture doit dominer le top-3."""
    verdicts = []
    total = client.query(COLLECTION, output_fields=["count(*)"])[0]["count(*)"]
    verdicts.append(f"count {total} == insérées {attendu} : {'✅' if total == attendu else '❌'}")
    cas = [
        ("Quelles sont les idées principales de la partie italienne ?", None, "italienne"),
        ("Pourquoi jouer le gambit dame ?", None, "gambit_dame"),
        ("What are the main plans in the sicilian defence?", None, "sicilienne"),
        ("idées d'attaque", 'ouverture == "espagnole"', "espagnole"),
    ]
    for question, filtre, attendue in cas:
        vecteur = embed([INSTR + question])
        hits = client.search(COLLECTION, data=vecteur, limit=3, filter=filtre or "",
                             output_fields=["ouverture"])[0]
        trouvees = [h["entity"]["ouverture"] for h in hits]
        ok = trouvees.count(attendue) >= 2
        verdicts.append(f"« {question[:44]}… » → {trouvees} : {'✅' if ok else '❌'}")
    return verdicts


def principal() -> None:
    fiches = [json.loads(ligne) for ligne in open(CHUNKS)]
    rapport: dict = {"fiches_lues": len(fiches)}
    matrice = vectoriser(fiches, rapport)
    fiches, matrice = ecarter_near_dups(fiches, matrice, rapport)
    rapport["fiches_a_inserer"] = len(fiches)

    client = MilvusClient(uri=MILVUS)
    creer_collection(client)
    horodatage = datetime.now(UTC).isoformat(timespec="seconds")
    lignes = []
    for fiche, vecteur in zip(fiches, matrice, strict=True):
        lignes.append({
            "vector": vecteur.tolist(),
            "text": fiche["text"].encode()[:8000].decode(errors="ignore"),  # Milvus compte en octets
            "ouverture": fiche["ouverture"],
            "eco": fiche["eco"],
            "opening_name": fiche["opening_name"][:500],
            "fen_ref": fiche["fen_ref"] or "",
            "lang": fiche["lang"],
            "source_url": fiche["source_url"][:500],
            "licence": fiche["licence"],
            "section": fiche["section"][:250],
            "content_hash": fiche["content_hash"],
            "ingested_at": horodatage,
        })
    debut = time.perf_counter()
    for i in range(0, len(lignes), 128):
        client.insert(COLLECTION, lignes[i : i + 128])
    client.flush(COLLECTION)
    rapport["insertion_s"] = round(time.perf_counter() - debut, 1)

    debut = time.perf_counter()
    verdicts = controles(client, len(lignes))
    rapport["controles_s"] = round(time.perf_counter() - debut, 2)
    rapport["controles"] = verdicts
    RAPPORT.write_text(json.dumps(rapport, ensure_ascii=False, indent=2))
    for k, v in rapport.items():
        if k != "paires_near_dup":
            print(f"{k}: {v}" if k != "controles" else "controles :")
    for v in verdicts:
        print("  " + v)


if __name__ == "__main__":
    principal()
