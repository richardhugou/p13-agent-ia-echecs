"""Transformation — du wikitext brut aux fiches prêtes à vectoriser (commit 2 d'É3).

Règles (docs 04/06 du projet) :
- nettoyage wikitext (modèles, refs, tables, liens) en conservant titres de sections ;
- chunking par section, cible 300-500 tokens estimés, recouvrement ~15 %,
  jamais une suite de coups coupée (découpe aux frontières de paragraphes/phrases,
  les points de coups « 1.e4 » ne sont pas des fins de phrase) ;
- fil d'Ariane préfixé sur chaque fiche (« Ouverture > Page > Section ») ;
- FEN de référence calculé en rejouant les coups du titre Wikibooks (python-chess) ;
- déduplication : hash exact + quasi-doublons (Jaccard shingles 8 mots > 0,9) —
  la passe cosinus > 0,95 se rejoue au chargement (commit 3) ;
- pages vides/stubs écartées ; rapport chiffré à chaque exécution.

Entrée : brut/<ouverture>/*.json · Sortie : chunks/chunks.jsonl + rapport JSON.
"""

import hashlib
import json
import re
import statistics
import time
from pathlib import Path

import chess

import argparse

ARGS = argparse.Namespace(cible=400, maxi=550, recouvrement=0.15, sortie="chunks", naif=False)
if __name__ == "__main__":
    _p = argparse.ArgumentParser(description="Transformation paramétrable (Run A/B)")
    _p.add_argument("--cible", type=int, default=400)
    _p.add_argument("--maxi", type=int, default=550)
    _p.add_argument("--recouvrement", type=float, default=0.15)
    _p.add_argument("--sortie", default="chunks")
    _p.add_argument("--naif", action="store_true",
                    help="Run A : page entière, fenêtres fixes, sans sections ni ariane")
    ARGS = _p.parse_args()

BRUT = Path(__file__).parent / "brut"
SORTIE = Path(__file__).parent / ARGS.sortie
CIBLE_TOKENS = ARGS.cible
MAX_TOKENS = ARGS.maxi
MIN_TOKENS_PAGE = 50
MIN_TOKENS_CHUNK = 60
RECOUVREMENT = ARGS.recouvrement
JACCARD_SEUIL = 0.9

NOMS = {
    "italienne": "Partie italienne", "espagnole": "Partie espagnole",
    "sicilienne": "Défense sicilienne", "francaise": "Défense française",
    "caro_kann": "Défense Caro-Kann", "gambit_dame": "Gambit dame",
    "est_indienne": "Défense est-indienne", "anglaise": "Partie anglaise",
}


def est_tokens(texte: str) -> int:
    return round(len(texte.split()) * 1.33)


def nettoyer_wikitext(brut: str) -> str:
    t = re.sub(r"<!--.*?-->", "", brut, flags=re.S)
    t = re.sub(r"<ref[^>/]*/>", "", t)
    t = re.sub(r"<ref[^>]*>.*?</ref>", "", t, flags=re.S)
    for _ in range(20):  # modèles {{...}}, du plus imbriqué vers l'extérieur
        t2 = re.sub(r"\{\{[^{}]*\}\}", "", t, flags=re.S)
        if t2 == t:
            break
        t = t2
    t = re.sub(r"\{\|.*?\|\}", "", t, flags=re.S)  # tables
    t = re.sub(r"\[\[(?:Fichier|File|Image):[^\[\]]*(?:\[\[[^\]]*\]\][^\[\]]*)*\]\]", "", t)
    t = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", t)  # liens internes
    t = re.sub(r"\[https?://[^\s\]]+ ([^\]]*)\]", r"\1", t)  # liens externes libellés
    t = re.sub(r"\[https?://[^\s\]]+\]", "", t)
    t = t.replace("'''", "").replace("''", "")
    t = re.sub(r"<[^>]+>", "", t)  # balises restantes
    t = re.sub(r"^[ \t]*[|!].*$", "", t, flags=re.M)  # résidus de tables
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def decouper_sections(texte: str) -> list[tuple[str, str]]:
    """[(titre_de_section, contenu)] — l'introduction s'appelle « Introduction »."""
    morceaux = re.split(r"^=+\s*(.*?)\s*=+\s*$", texte, flags=re.M)
    sections = [("Introduction", morceaux[0])]
    for i in range(1, len(morceaux) - 1, 2):
        sections.append((morceaux[i], morceaux[i + 1]))
    return [(t, c.strip()) for t, c in sections if c.strip()]


def phrases(paragraphe: str) -> list[str]:
    # fin de phrase = point après une lettre minuscule — « 1.e4 » n'en est pas une
    return re.split(r"(?<=[a-zàâäéèêëîïôöûüç][.!?])\s+(?=[A-ZÀ-Ü0-9])", paragraphe)


def morceaux_de_section(contenu: str) -> list[str]:
    """Paragraphes, les trop longs redécoupés en phrases (jamais au milieu d'un coup)."""
    morceaux = []
    for para in [p.strip() for p in contenu.split("\n\n") if p.strip()]:
        if est_tokens(para) <= MAX_TOKENS:
            morceaux.append(para)
            continue
        lot: list[str] = []
        for ph in phrases(para):
            if est_tokens(" ".join([*lot, ph])) > MAX_TOKENS and lot:
                morceaux.append(" ".join(lot))
                lot = []
            lot.append(ph)
        if lot:
            morceaux.append(" ".join(lot))
    return morceaux


def assembler_chunks(morceaux: list[str]) -> list[str]:
    chunks, lot = [], []
    for m in morceaux:
        lot.append(m)
        if est_tokens("\n".join(lot)) >= CIBLE_TOKENS:
            chunks.append("\n".join(lot))
            queue = chunks[-1].split()
            lot = ([" ".join(queue[-max(1, int(len(queue) * RECOUVREMENT)):])]
                   if RECOUVREMENT > 0 else [])
    reste = "\n".join(lot).strip()
    if reste and est_tokens(reste) >= MIN_TOKENS_CHUNK:
        chunks.append(reste)
    elif reste and chunks:
        chunks[-1] += "\n" + reste
    return chunks


def fen_depuis_titre_wikibooks(titre: str, rapport: dict) -> str | None:
    segments = titre.split("/")[1:]  # après « Chess Opening Theory »
    board = chess.Board()
    try:
        for seg in segments:
            san = re.sub(r"^\d+\.(\.\.)?\s*", "", seg.strip())
            board.push_san(san)
        return board.fen()
    except ValueError:
        rapport["fen_echoues"] += 1
        return None


def shingles(texte: str) -> frozenset:
    mots = re.sub(r"\W+", " ", texte.lower()).split()
    return frozenset(" ".join(mots[i : i + 8]) for i in range(max(1, len(mots) - 7)))


def principal() -> None:
    SORTIE.mkdir(exist_ok=True)
    rapport = {"pages_lues": 0, "pages_stubs_ecartees": 0, "sections": 0,
               "chunks_bruts": 0, "doublons_exacts": 0, "quasi_doublons": 0,
               "fen_calcules": 0, "fen_echoues": 0}
    debut = time.perf_counter()
    fiches, hashes, empreintes = [], set(), []

    for fichier in sorted(BRUT.glob("*/*.json")):
        if fichier.name.startswith("rapport") or fichier.name == "redirections.json":
            continue
        page = json.loads(fichier.read_text())
        rapport["pages_lues"] += 1
        texte = nettoyer_wikitext(page["wikitext"])
        if est_tokens(texte) < MIN_TOKENS_PAGE:
            rapport["pages_stubs_ecartees"] += 1
            continue
        fen_ref = (fen_depuis_titre_wikibooks(page["titre"], rapport)
                   if page["lang"] == "en" else None)
        if fen_ref:
            rapport["fen_calcules"] += 1
        sections = [("Page", texte)] if ARGS.naif else decouper_sections(texte)
        for section, contenu in sections:
            rapport["sections"] += 1
            ariane = f"{NOMS[page['ouverture']]} > {page['titre']} > {section}"
            if ARGS.naif:  # fenêtres fixes en mots, aveugles aux frontières
                mots = contenu.split()
                pas = int(CIBLE_TOKENS / 1.33)
                morceaux = [" ".join(mots[i : i + pas]) for i in range(0, len(mots), pas)]
            else:
                morceaux = morceaux_de_section(contenu)
            for corps in assembler_chunks(morceaux):
                rapport["chunks_bruts"] += 1
                texte_fiche = corps if ARGS.naif else f"{ariane} —\n{corps}"
                h = hashlib.sha256(
                    re.sub(r"\s+", " ", corps.lower()).encode()).hexdigest()
                if h in hashes:
                    rapport["doublons_exacts"] += 1
                    continue
                empreinte = shingles(corps)
                if any(len(empreinte & e) / max(1, len(empreinte | e)) > JACCARD_SEUIL
                       for e in empreintes):
                    rapport["quasi_doublons"] += 1
                    continue
                hashes.add(h)
                empreintes.append(empreinte)
                fiches.append({
                    "id": f"{page['ouverture']}-{len(fiches):04d}",
                    "text": texte_fiche,
                    "ouverture": page["ouverture"],
                    "eco": page["eco"],
                    "opening_name": page["titre"],
                    "fen_ref": fen_ref,
                    "lang": page["lang"],
                    "source_url": page["source_url"],
                    "licence": page["licence"],
                    "section": section,
                    "rev_timestamp": page["rev_timestamp"],
                    "content_hash": h,
                    "n_tokens_est": est_tokens(texte_fiche),
                })

    with open(SORTIE / "chunks.jsonl", "w") as f:
        for fiche in fiches:
            f.write(json.dumps(fiche, ensure_ascii=False) + "\n")

    longueurs = [f["n_tokens_est"] for f in fiches]
    rapport.update({
        "chunks_retenus": len(fiches),
        "tokens_moyenne": round(statistics.mean(longueurs)),
        "tokens_mediane": round(statistics.median(longueurs)),
        "par_ouverture": {n: sum(1 for f in fiches if f["ouverture"] == n) for n in NOMS},
        "par_langue": {"fr": sum(1 for f in fiches if f["lang"] == "fr"),
                       "en": sum(1 for f in fiches if f["lang"] == "en")},
        "duree_s": round(time.perf_counter() - debut, 1),
    })
    (SORTIE / "rapport-transformation.json").write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2))
    for k, v in rapport.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    principal()
