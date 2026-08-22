"""Extraction des pages du manifeste signé — archive brute datée, rejouable sans re-télécharger.

Refuse de tourner si le manifeste n'est pas signé (règle D-c).
Chaque page → un JSON dans brut/<ouverture>/ : wikitext + métadonnées complètes
(titre, url, révision, date, licence). Une page déjà archivée n'est pas re-téléchargée
(relancer avec --force pour tout rafraîchir). Rapport chiffré en fin d'exécution.
"""

import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import yaml

UA = {"User-Agent": "P13-POC-etl/0.1 (richard.hugou@gmail.com)"}
APIS = {
    "fr": ("https://fr.wikipedia.org/w/api.php", "https://fr.wikipedia.org/wiki/"),
    "en": ("https://en.wikibooks.org/w/api.php", "https://en.wikibooks.org/wiki/"),
}
BRUT = Path(__file__).parent / "brut"
REDIRECTIONS = BRUT / "redirections.json"


def api(base: str, params: dict, retries: int = 4) -> dict:
    url = base + "?" + urllib.parse.urlencode(params)
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            out = json.load(urllib.request.urlopen(req, timeout=60))
            time.sleep(0.3)
            return out
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and i < retries - 1:
                time.sleep(15)
                continue
            raise
    raise RuntimeError("inaccessible")


def slug(titre: str) -> str:
    s = unicodedata.normalize("NFKD", titre).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()[:80]


def extraire(lang: str, titres: list[str], ouverture: str, eco: str,
             force: bool, rapport: dict, redirections: dict) -> None:
    base, wiki = APIS[lang]
    dossier = BRUT / ouverture
    dossier.mkdir(parents=True, exist_ok=True)
    a_faire = []
    for t in titres:
        canonique = redirections.get(t, t)
        if not force and (dossier / f"{slug(canonique)}.json").exists():
            rapport["sautees_deja_archivees"] += 1
        else:
            a_faire.append(t)
    for lot in [a_faire[i : i + 50] for i in range(0, len(a_faire), 50)]:
        r = api(base, {"action": "query", "prop": "revisions",
                       "rvprop": "content|timestamp|ids", "rvslots": "main",
                       "titles": "|".join(lot), "redirects": "1",
                       "format": "json", "formatversion": "2"})
        for x in r["query"].get("redirects", []):
            redirections[x["from"]] = x["to"]
        for page in r["query"]["pages"]:
            if page.get("missing"):
                rapport["absentes"].append(page["title"])
                continue
            rev = page["revisions"][0]
            doc = {
                "titre": page["title"],
                "lang": lang,
                "ouverture": ouverture,
                "eco": eco,
                "source_url": wiki + urllib.parse.quote(page["title"].replace(" ", "_")),
                "revid": rev["revid"],
                "rev_timestamp": rev["timestamp"],
                "retrieved_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "licence": "CC BY-SA 4.0",
                "wikitext": rev["slots"]["main"]["content"],
            }
            chemin = dossier / f"{slug(page['title'])}.json"
            chemin.write_text(json.dumps(doc, ensure_ascii=False))
            rapport["extraites"] += 1
            rapport["octets"] += chemin.stat().st_size


def principal() -> None:
    manifeste = yaml.safe_load(open(Path(__file__).parent / "corpus.yml"))
    if "SIGNÉ" not in manifeste["meta"]["statut"]:
        sys.exit("REFUS : le manifeste n'est pas signé (règle D-c). Statut : "
                 + manifeste["meta"]["statut"])
    force = "--force" in sys.argv
    rapport = {"demandees": 0, "extraites": 0, "sautees_deja_archivees": 0,
               "absentes": [], "octets": 0}
    redirections = json.load(open(REDIRECTIONS)) if REDIRECTIONS.exists() else {}
    debut = time.perf_counter()
    for nom, o in manifeste["ouvertures"].items():
        rapport["demandees"] += len(o["wikipedia_fr"]) + len(o["wikibooks_en"])
        extraire("fr", o["wikipedia_fr"], nom, o["eco"], force, rapport, redirections)
        extraire("en", o["wikibooks_en"], nom, o["eco"], force, rapport, redirections)
        print(f"{nom:<14} archivé")
    REDIRECTIONS.write_text(json.dumps(redirections, ensure_ascii=False, indent=2))
    rapport["duree_s"] = round(time.perf_counter() - debut, 1)
    (BRUT / "rapport-extraction.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2))
    print(f"\nRAPPORT : {rapport['demandees']} demandées · {rapport['extraites']} extraites"
          f" · {rapport['sautees_deja_archivees']} déjà archivées"
          f" · absentes : {rapport['absentes'] or 'aucune'}"
          f" · {rapport['octets'] / 1e6:.1f} Mo · {rapport['duree_s']} s")


if __name__ == "__main__":
    principal()
