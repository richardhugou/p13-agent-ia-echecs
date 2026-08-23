"""Évaluation Run A (naïf) vs Run B (soigné) sur le gold set — les [MESURE] du deck.

Configs :
  A « naïf »    : collection openings_kb_naive (fenêtres 1000, sans sections/ariane/
                  recouvrement), top-3, requêtes SANS préfixe d'instruction, sans filtre.
  B « soigné »  : collection openings_kb (sections 300-500, recouvrement 15 %, ariane),
                  top-5, préfixe d'instruction, filtre ECO→rayon sur les questions par position.

Métriques : recall@k et MRR (20 questions légitimes) ; abstention sur les 5 pièges via
seuil de score choisi SUR LES DONNÉES (point médian entre pièges et légitimes) ;
latences de recherche p50/p95. Sorties : resultats.json + runs MLflow.
"""

import json
import statistics
import time
import urllib.request
from pathlib import Path

import yaml
from pymilvus import MilvusClient

ICI = Path(__file__).parent
OLLAMA = "http://localhost:11434"
MODELE = "qwen3-embedding:0.6b"
INSTR = "Instruct: Given a question about chess openings, retrieve relevant passages\nQuery: "

CONFIGS = {
    "A_naif": {"collection": "openings_kb_naive", "k": 3, "prefixe": False, "filtre": False,
               "chunking": "fenêtres 1000, sans recouvrement, sans sections ni ariane"},
    "B_soigne": {"collection": "openings_kb", "k": 5, "prefixe": True, "filtre": True,
                 "chunking": "sections 300-500, recouvrement 15 %, fil d'Ariane"},
}


def embed(texte: str) -> list[float]:
    corps = json.dumps({"model": MODELE, "input": [texte]}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/embed", data=corps,
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=120))["embeddings"][0]


def rayon_depuis_eco(eco: str) -> str | None:
    bornes = {"italienne": ("C50", "C54"), "espagnole": ("C60", "C99"),
              "sicilienne": ("B20", "B99"), "francaise": ("C00", "C19"),
              "caro_kann": ("B10", "B19"), "gambit_dame": ("D06", "D69"),
              "est_indienne": ("E60", "E99"), "anglaise": ("A10", "A39")}
    for nom, (a, b) in bornes.items():
        if a <= eco[:3] <= b:
            return nom
    return None


def evaluer_config(nom: str, cfg: dict, gold: dict, client: MilvusClient) -> dict:
    ranks, latences, details = [], [], []
    scores_legitimes, scores_pieges = [], []

    legitimes = ([{"q": d["q"], "attendu": d["attendu"], "filtre": None} for d in gold["directes"]]
                 + [{"q": f"Idées principales et plans de l'ouverture {p['opening_name']}",
                     "attendu": p["attendu"],
                     "filtre": rayon_depuis_eco(p["eco"]) if cfg["filtre"] else None}
                    for p in gold["par_position"]])

    for cas in legitimes:
        vecteur = embed((INSTR if cfg["prefixe"] else "") + cas["q"])
        debut = time.perf_counter()
        hits = client.search(cfg["collection"], data=[vecteur], limit=cfg["k"],
                             filter=f'ouverture == "{cas["filtre"]}"' if cas["filtre"] else "",
                             output_fields=["ouverture"])[0]
        latences.append((time.perf_counter() - debut) * 1000)
        trouvees = [h["entity"]["ouverture"] for h in hits]
        rank = next((i + 1 for i, o in enumerate(trouvees) if o in cas["attendu"]), None)
        ranks.append(rank)
        scores_legitimes.append(hits[0]["distance"] if hits else 0.0)
        details.append({"q": cas["q"][:60], "attendu": cas["attendu"],
                        "trouvees": trouvees, "rank": rank})

    for piege in gold["pieges"]:
        vecteur = embed((INSTR if cfg["prefixe"] else "") + piege["q"])
        hits = client.search(cfg["collection"], data=[vecteur], limit=1,
                             output_fields=["ouverture"])[0]
        scores_pieges.append(hits[0]["distance"] if hits else 0.0)

    # seuil d'abstention choisi sur les données : point médian entre les deux nuages
    seuil = round((max(scores_pieges) + min(scores_legitimes)) / 2, 3)
    abstentions_ok = sum(1 for s in scores_pieges if s < seuil)
    legitimes_rejetees = sum(1 for s in scores_legitimes if s < seuil)

    latences.sort()
    return {
        "config": {k: v for k, v in cfg.items()},
        "recall_at_k": round(sum(1 for r in ranks if r) / len(ranks), 3),
        "mrr": round(sum(1 / r for r in ranks if r) / len(ranks), 3),
        "abstention_seuil": seuil,
        "abstention_correcte": f"{abstentions_ok}/{len(scores_pieges)}",
        "legitimes_rejetees": legitimes_rejetees,
        "scores_pieges": [round(s, 3) for s in scores_pieges],
        "score_legitime_min": round(min(scores_legitimes), 3),
        "latence_ms_p50": round(latences[len(latences) // 2], 1),
        "latence_ms_p95": round(latences[int(len(latences) * 0.95)], 1),
        "details": details,
    }


def principal() -> None:
    gold = yaml.safe_load(open(ICI / "gold_set.yml"))
    client = MilvusClient(uri="http://localhost:19530")
    resultats = {"gold_set_version": gold["meta"]["version"], "runs": {}}
    for nom, cfg in CONFIGS.items():
        resultats["runs"][nom] = evaluer_config(nom, cfg, gold, client)
        r = resultats["runs"][nom]
        print(f"{nom:<10} recall@{cfg['k']} {r['recall_at_k']} · MRR {r['mrr']}"
              f" · abstention {r['abstention_correcte']} (seuil {r['abstention_seuil']},"
              f" légitimes rejetées {r['legitimes_rejetees']})"
              f" · p95 {r['latence_ms_p95']} ms")

    (ICI / "resultats.json").write_text(json.dumps(resultats, ensure_ascii=False, indent=2))

    try:  # MLflow : le cahier d'expériences (service compose) — repli silencieux si absent
        import mlflow
        mlflow.set_tracking_uri("http://localhost:5001")
        mlflow.set_experiment("gold-set-rag")
        for nom, r in resultats["runs"].items():
            with mlflow.start_run(run_name=nom):
                mlflow.log_params({**r["config"], "gold_set_version": gold["meta"]["version"]})
                mlflow.log_metrics({"recall_at_k": r["recall_at_k"], "mrr": r["mrr"],
                                    "abstention_correcte": int(r["abstention_correcte"][0]),
                                    "legitimes_rejetees": r["legitimes_rejetees"],
                                    "latence_ms_p95": r["latence_ms_p95"]})
                mlflow.log_artifact(str(ICI / "resultats.json"))
                mlflow.log_artifact(str(ICI / "gold_set.yml"))
        print("→ runs loggés dans MLflow (http://localhost:5001)")
    except Exception as exc:  # noqa: BLE001 — l'éval reste valable sans le cahier
        print(f"MLflow indisponible ({type(exc).__name__}) — resultats.json fait foi")


if __name__ == "__main__":
    principal()
