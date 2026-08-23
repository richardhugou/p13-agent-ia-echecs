"""Annotation française des coups SAN — la parade mesurée aux confusions de pièces.

Les petits modèles lisent mal la notation brute (« Bc5 » → « tour », « chevalier »).
On leur fournit des faits annotés en toutes lettres : « Fc5 — le Fou va en c5 ».
"""

PIECES = {
    "K": ("R", "le Roi"),
    "Q": ("D", "la Dame"),
    "R": ("T", "la Tour"),
    "B": ("F", "le Fou"),
    "N": ("C", "le Cavalier"),
}

PROMOTIONS = {"Q": "Dame", "R": "Tour", "B": "Fou", "N": "Cavalier"}

NOMS_COURTS = {"K": "roi", "Q": "dame", "R": "tour", "B": "fou", "N": "cavalier"}


def libelle_fr(san: str, uci: str) -> str:
    """« Bc5 » + « f8c5 » → « Fc5 (fou f8) » — notation FR avec la pièce et sa case de départ.

    Née de l'alerte « Bc5 illégal » : sans la case de départ, l'œil attribue le coup
    à la mauvaise pièce (le fou c8 au lieu du fou f8). L'UCI porte toujours l'origine.
    """
    if not san:
        return san
    depart = uci[:2] if uci and len(uci) >= 4 else ""
    if san.startswith("O-O-O"):
        return f"{san} (grand roque)"
    if san.startswith("O-O"):
        return f"{san} (petit roque)"
    if san[0] in PIECES:
        lettre_fr, _ = PIECES[san[0]]
        piece = NOMS_COURTS[san[0]]
        return f"{lettre_fr}{san[1:]} ({piece} {depart})".rstrip()
    return f"{san} (pion {depart})".rstrip() if depart else san


def annoter_san(san: str) -> str:
    """« Bc5 » → « Fc5 — le Fou va en c5 » ; gère roques, pions, promotions."""
    if san.startswith("O-O-O"):
        return f"{san} — le grand roque"
    if san.startswith("O-O"):
        return f"{san} — le petit roque"

    coeur = san.rstrip("+#")
    if san[0] in PIECES:
        lettre_fr, piece = PIECES[san[0]]
        return f"{lettre_fr}{san[1:]} — {piece} va en {coeur[-2:]}"
    if "=" in coeur:
        case, promo = coeur.split("=")
        nom = PROMOTIONS.get(promo, promo)
        return f"{san} — le pion va en {case[-2:]} et devient une {nom}"
    return f"{san} — le pion va en {coeur[-2:]}"
