"""Outil de collecte de données produit sur les plateformes e-commerce."""

import json
from datetime import datetime

from langchain_core.tools import tool

# ─── Données simulées ─────────────────────────────────────────────────────────

_CATALOGUE_MOCK: dict[str, dict] = {
    "iphone": {
        "nom": "Apple iPhone 16 Pro",
        "categorie": "Smartphone",
        "description": (
            "Smartphone haut de gamme avec puce A18 Pro, écran Super Retina XDR 6.3\", "
            "système de caméras ProRes 48 MP et autonomie améliorée."
        ),
        "note_moyenne": 4.6,
        "nombre_avis": 12847,
        "plateformes": [
            {"plateforme": "Amazon.fr",   "prix": 1199.99, "devise": "EUR", "disponible": True,  "vendeur": "Amazon"},
            {"plateforme": "Fnac",        "prix": 1229.00, "devise": "EUR", "disponible": True,  "vendeur": "Fnac"},
            {"plateforme": "Darty",       "prix": 1199.00, "devise": "EUR", "disponible": False, "vendeur": "Darty"},
            {"plateforme": "Apple Store", "prix": 1229.00, "devise": "EUR", "disponible": True,  "vendeur": "Apple"},
        ],
    },
    "nike": {
        "nom": "Nike Air Max 270",
        "categorie": "Chaussures de sport",
        "description": (
            "Chaussure running lifestyle avec la plus grande unité Air Max visible, "
            "tige en mesh breathable et semelle intercalaire en mousse."
        ),
        "note_moyenne": 4.4,
        "nombre_avis": 8923,
        "plateformes": [
            {"plateforme": "Nike.com",   "prix": 150.00, "devise": "EUR", "disponible": True,  "vendeur": "Nike"},
            {"plateforme": "Amazon.fr",  "prix": 139.99, "devise": "EUR", "disponible": True,  "vendeur": "SportsWorld"},
            {"plateforme": "Zalando",    "prix": 149.95, "devise": "EUR", "disponible": True,  "vendeur": "Zalando"},
            {"plateforme": "Foot Locker","prix": 160.00, "devise": "EUR", "disponible": False, "vendeur": "Foot Locker"},
        ],
    },
    "macbook": {
        "nom": "Apple MacBook Air M4",
        "categorie": "Ordinateur portable",
        "description": (
            "Ordinateur ultra-portable avec puce Apple M4, écran Liquid Retina 13.6\", "
            "autonomie jusqu'à 18h et design sans ventilateur."
        ),
        "note_moyenne": 4.8,
        "nombre_avis": 5432,
        "plateformes": [
            {"plateforme": "Apple Store", "prix": 1299.00, "devise": "EUR", "disponible": True,  "vendeur": "Apple"},
            {"plateforme": "Amazon.fr",   "prix": 1279.99, "devise": "EUR", "disponible": True,  "vendeur": "Amazon"},
            {"plateforme": "Fnac",        "prix": 1299.00, "devise": "EUR", "disponible": True,  "vendeur": "Fnac"},
        ],
    },
}

_PRODUIT_GENERIQUE = {
    "categorie": "Produit e-commerce",
    "description": "Produit populaire dans sa catégorie e-commerce.",
    "note_moyenne": 4.2,
    "nombre_avis": 1240,
    "plateformes": [
        {"plateforme": "Amazon.fr", "prix": 89.99, "devise": "EUR", "disponible": True,  "vendeur": "Vendeur Marketplace"},
        {"plateforme": "Cdiscount", "prix": 84.99, "devise": "EUR", "disponible": True,  "vendeur": "Cdiscount"},
    ],
}


# ─── Outil LangChain ──────────────────────────────────────────────────────────

@tool
def scrape_product(query: str) -> str:
    """
    Collecte les prix et informations produit sur plusieurs plateformes e-commerce.

    Args:
        query: Nom ou description du produit (ex: "iPhone 16 Pro", "Nike Air Max 270")

    Returns:
        JSON avec nom, catégorie, prix par plateforme, prix min/max/moyen et métadonnées.
    """
    query_lower = query.lower()

    donnees = None
    for mot_cle, data in _CATALOGUE_MOCK.items():
        if mot_cle in query_lower:
            donnees = {k: v for k, v in data.items()}  # copie superficielle
            break

    if donnees is None:
        donnees = {**_PRODUIT_GENERIQUE, "nom": query}

    prix_liste = [p["prix"] for p in donnees["plateformes"]]
    donnees["prix_min"]    = min(prix_liste)
    donnees["prix_max"]    = max(prix_liste)
    donnees["prix_moyen"]  = round(sum(prix_liste) / len(prix_liste), 2)
    donnees["collecte_le"] = datetime.now().isoformat(timespec="seconds")

    return json.dumps(donnees, ensure_ascii=False, indent=2)
