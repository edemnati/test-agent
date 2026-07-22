"""Outil d'analyse du sentiment des avis clients."""

import json

from langchain_core.tools import tool

# ─── Avis simulés ─────────────────────────────────────────────────────────────

_AVIS_MOCK: dict[str, list[str]] = {
    "iphone": [
        "Excellent smartphone, la caméra est incroyable pour la photo de nuit.",
        "Très bon produit mais le prix est élevé. L'écran est magnifique.",
        "Batterie décevante par rapport au prix. Sinon très fluide.",
        "Meilleur iPhone que j'ai jamais eu ! Vraiment impressionnant.",
        "La qualité photo est exceptionnelle, je recommande vivement.",
        "Déçu par la durée de vie de la batterie, le reste est parfait.",
        "Interface fluide, superbe appareil photo, design premium.",
    ],
    "nike": [
        "Très confortables dès le premier jour, je les recommande !",
        "Bon amorti mais les lacets se détachent facilement.",
        "Superbes chaussures, qualité au rendez-vous.",
        "Qualité top, j'en achète une deuxième paire.",
        "Un peu serrées sur les côtés au début mais très bien après.",
        "Parfaites pour mes séances de running quotidiennes.",
    ],
    "macbook": [
        "Incroyable rapport performance/autonomie. Le M4 est une révolution.",
        "Très léger et puissant, parfait pour le travail en déplacement.",
        "Prix élevé mais justifié par la qualité de fabrication exceptionnelle.",
        "Écran magnifique, clavier agréable, autonomie impressionnante.",
        "Un peu cher mais c'est le meilleur laptop que j'ai utilisé.",
    ],
}

_AVIS_GENERIQUES = [
    "Très bon produit, livraison rapide et conforme à la description.",
    "Qualité correcte pour le prix, je suis satisfait de mon achat.",
    "Service client réactif, produit reçu en bon état et bien emballé.",
    "Bon rapport qualité-prix, je recommande à mon entourage.",
    "Quelques défauts mineurs mais globalement très satisfait.",
]

# Mots-clés pour classification basique du sentiment
_MOTS_POSITIFS = frozenset([
    "excellent", "top", "super", "parfait", "recommande", "incroyable",
    "impressionnant", "magnifique", "incroyable", "puissant", "révolution",
    "agréable", "qualité", "léger", "fluide", "satisfait",
])
_MOTS_NEGATIFS = frozenset([
    "décevant", "déçu", "mauvais", "problème", "défaut", "cher",
    "serrée", "difficile", "médiocre",
])


# ─── Outil LangChain ──────────────────────────────────────────────────────────

@tool
def analyze_sentiment(product_name: str, reviews: list[str] | None = None) -> str:
    """
    Analyse le sentiment des avis clients pour un produit et extrait des insights.

    Args:
        product_name: Nom du produit à analyser.
        reviews     : Liste d'avis à analyser (utilise des données simulées si absent).

    Returns:
        JSON avec score de sentiment (0–1), label, répartition et points forts/faibles.
    """
    if not reviews:
        nom_lower = product_name.lower()
        reviews = next(
            (avis for mot_cle, avis in _AVIS_MOCK.items() if mot_cle in nom_lower),
            _AVIS_GENERIQUES,
        )

    positifs, negatifs = [], []
    for avis in reviews:
        mots = set(avis.lower().split())
        if mots & _MOTS_POSITIFS:
            positifs.append(avis)
        elif mots & _MOTS_NEGATIFS:
            negatifs.append(avis)

    nb_neutres = len(reviews) - len(positifs) - len(negatifs)
    score = round((len(positifs) + nb_neutres * 0.5) / len(reviews), 2)

    if score >= 0.65:
        label = "positif"
    elif score >= 0.40:
        label = "neutre"
    else:
        label = "négatif"

    resultat = {
        "produit": product_name,
        "nombre_avis_analysés": len(reviews),
        "score_sentiment": score,
        "label_sentiment": label,
        "répartition": {
            "positifs": len(positifs),
            "neutres": nb_neutres,
            "négatifs": len(negatifs),
        },
        "points_forts": (positifs[:3] if positifs else ["Bonne qualité générale"]),
        "points_faibles": (negatifs[:2] if negatifs else ["Aucun point négatif majeur relevé"]),
        "résumé": (
            f"Sur {len(reviews)} avis analysés, le sentiment est {label} "
            f"(score : {score}/1.0). "
            + (f"{len(positifs)} avis positifs contre {len(negatifs)} négatifs." if negatifs else
               "Les clients expriment globalement une satisfaction élevée.")
        ),
    }

    return json.dumps(resultat, ensure_ascii=False, indent=2)
