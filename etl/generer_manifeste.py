"""Génération assistée du manifeste corpus.yml — décision D-c : Richard relit et signe.

Méthode, par ouverture cible :
- FR (Wikipédia) : candidats explicites vérifiés via l'API (les pages douteuses sont
  signalées « absente ») + membres des catégories dédiées quand elles existent,
  filtrés par motif.
- EN (Wikibooks « Chess Opening Theory ») : sous-arbre du préfixe de la ligne,
  trié du plus général au plus profond, plafonné (en_max) — 3 026 pages existent,
  on ne prend que la tête de chaque arbre.

Sortie : corpus.yml (statut: brouillon) + un rapport chiffré sur stdout.
Rejouable : mêmes entrées ⇒ même manifeste (l'ordre est déterministe).
"""

import json
import re
import time
import urllib.parse
import urllib.request
from datetime import date

import yaml

UA = {"User-Agent": "P13-POC-etl/0.1 (richard.hugou@gmail.com)"}
FR_API = "https://fr.wikipedia.org/w/api.php"
EN_API = "https://en.wikibooks.org/w/api.php"
EN_MAX_PAR_OUVERTURE = 12
EN_MAX_PAUVRES_EN_FR = 18  # française, anglaise, caro_kann
FR_MAX = 12  # rabotage des grosses catégories : priorité candidats explicites puis titres courts

OUVERTURES = {
    "italienne": {
        "eco": "C50-C54",
        "fr_candidats": [
            "Partie italienne", "Giuoco Piano", "Défense des deux cavaliers",
            "Gambit Evans", "Gambit Blackburne Shilling",
        ],
        "fr_categories": [],
        "en_prefixes": ["Chess Opening Theory/1. e4/1...e5/2. Nf3/2...Nc6/3. Bc4"],
    },
    "espagnole": {
        "eco": "C60-C99",
        "fr_candidats": ["Partie espagnole"],
        "fr_categories": ["Catégorie:Partie espagnole", "Catégorie:Espagnole fermée"],
        "en_prefixes": ["Chess Opening Theory/1. e4/1...e5/2. Nf3/2...Nc6/3. Bb5"],
    },
    "sicilienne": {
        "eco": "B20-B99",
        "fr_candidats": ["Défense sicilienne"],
        "fr_categories": ["Catégorie:Défense sicilienne"],
        "en_prefixes": ["Chess Opening Theory/1. e4/1...c5"],
    },
    "francaise": {
        "en_max": 18,
        "eco": "C00-C19",
        "fr_candidats": ["Défense française"],
        "fr_categories": [],
        "fr_filtre": "française",
        "en_prefixes": ["Chess Opening Theory/1. e4/1...e6"],
    },
    "caro_kann": {
        "en_max": 18,
        "eco": "B10-B19",
        "fr_candidats": ["Défense Caro-Kann", "Attaque Panov"],
        "fr_categories": [],
        "en_prefixes": ["Chess Opening Theory/1. e4/1...c6"],
    },
    "gambit_dame": {
        "eco": "D06-D69",
        "fr_candidats": ["Gambit dame", "Gambit dame accepté", "Gambit dame refusé", "Défense slave"],
        "fr_categories": ["Catégorie:Gambit dame", "Catégorie:Gambit dame refusé"],
        "en_prefixes": ["Chess Opening Theory/1. d4/1...d5/2. c4"],
    },
    "est_indienne": {
        "eco": "E60-E99",
        "fr_candidats": ["Défense est-indienne"],
        "fr_categories": ["Catégorie:Défense indienne"],
        "fr_filtre": "est-indienne",
        "en_prefixes": ["Chess Opening Theory/1. d4/1...Nf6/2. c4/2...g6"],
    },
    "anglaise": {
        "en_max": 18,
        "eco": "A10-A39",
        "fr_candidats": ["Partie anglaise"],
        "fr_categories": [],
        "fr_filtre": "anglaise",
        "en_prefixes": ["Chess Opening Theory/1. c4"],
    },
}


def api(base: str, params: dict, retries: int = 4) -> dict:
    url = base + "?" + urllib.parse.urlencode(params)
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            out = json.load(urllib.request.urlopen(req, timeout=30))
            time.sleep(0.3)
            return out
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and i < retries - 1:
                time.sleep(15)
                continue
            raise
    raise RuntimeError("inaccessible")


def pages_existantes(titres: list[str]) -> tuple[list[str], list[str]]:
    """Vérifie l'existence (en suivant les redirections). Retourne (trouvées, absentes)."""
    trouvees, absentes = [], []
    for lot in [titres[i : i + 50] for i in range(0, len(titres), 50)]:
        r = api(FR_API, {"action": "query", "titles": "|".join(lot),
                         "redirects": "1", "format": "json"})
        pages = r["query"]["pages"]
        resolus = {p["title"] for p in pages.values() if "missing" not in p}
        redirections = {x["from"]: x["to"] for x in r["query"].get("redirects", [])}
        for t in lot:
            cible = redirections.get(t, t)
            (trouvees if cible in resolus else absentes).append(cible)
    return sorted(set(trouvees)), sorted(set(absentes))


def membres_categorie(cmtitle: str) -> list[str]:
    membres, cont = [], {}
    while True:
        r = api(FR_API, {"action": "query", "list": "categorymembers", "cmtitle": cmtitle,
                         "cmlimit": "500", "cmtype": "page", "format": "json", **cont})
        membres += [m["title"] for m in r["query"]["categorymembers"]]
        if "continue" in r:
            cont = r["continue"]
        else:
            return membres


def sous_arbre_en(prefixe: str, plafond: int) -> tuple[list[str], int]:
    """Pages du sous-arbre, triées du général au profond, plafonnées. Retourne (retenues, total)."""
    pages, cont = [], {}
    while True:
        r = api(EN_API, {"action": "query", "list": "allpages", "apprefix": prefixe,
                         "aplimit": "500", "format": "json", **cont})
        pages += [p["title"] for p in r["query"]["allpages"]]
        if "continue" in r:
            cont = r["continue"]
        else:
            break
    pages.sort(key=lambda t: (t.count("/"), len(t), t))
    return pages[:plafond], len(pages)


def principal() -> None:
    manifeste: dict = {
        "meta": {
            "statut": "SIGNÉ par Richard le 2026-08-23 — arbitrages : rabotage FR (12 max), EN 18 pour française/anglaise/caro-kann, est-indienne élargie à 2...g6, candidats absents abandonnés (axe d'amélioration)",
            "genere_le": str(date.today()),
            "methode": "candidats FR vérifiés + catégories filtrées ; sous-arbres EN plafonnés "
                       f"à {EN_MAX_PAR_OUVERTURE} pages, du général au profond",
            "regle": "toute modification du périmètre repasse par une signature",
        },
        "ouvertures": {},
    }
    total_fr = total_en = 0
    for nom, cfg in OUVERTURES.items():
        candidats = list(cfg["fr_candidats"])
        for cat in cfg["fr_categories"]:
            candidats += membres_categorie(cat)
        filtre = cfg.get("fr_filtre")
        if filtre:
            candidats = [t for t in candidats
                         if filtre.lower() in t.lower() or t in cfg["fr_candidats"]]
        fr, absentes = pages_existantes(candidats)
        fr = [t for t in fr if not re.match(r"^(Liste|Lexique)", t)]
        explicites = set(cfg["fr_candidats"])
        fr.sort(key=lambda t: (t not in explicites, len(t), t))
        fr_ecartees = max(0, len(fr) - FR_MAX)
        fr = sorted(fr[:FR_MAX])

        en, en_total = [], 0
        for prefixe in cfg["en_prefixes"]:
            retenues, total = sous_arbre_en(prefixe, cfg.get("en_max", EN_MAX_PAR_OUVERTURE))
            en += retenues
            en_total += total

        manifeste["ouvertures"][nom] = {
            "eco": cfg["eco"],
            "wikipedia_fr": fr,
            "wikibooks_en": en,
            "en_disponibles_dans_l_arbre": en_total,
        }
        if fr_ecartees:
            manifeste["ouvertures"][nom]["fr_ecartees_par_rabotage"] = fr_ecartees
        total_fr += len(fr)
        total_en += len(en)
        print(f"{nom:<14} FR {len(fr):>3} pages · EN {len(en):>3}/{en_total} retenues"
              + (f" · absents: {absentes}" if absentes else ""))

    with open("corpus.yml", "w") as f:
        yaml.safe_dump(manifeste, f, allow_unicode=True, sort_keys=False, width=100)
    yaml.safe_load(open("corpus.yml"))  # auto-contrôle : le fichier se relit
    print(f"\nTOTAL : {total_fr} pages FR + {total_en} pages EN = {total_fr + total_en} "
          f"(cible plan : ~100-150) → corpus.yml")


if __name__ == "__main__":
    principal()
