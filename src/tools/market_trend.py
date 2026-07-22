"""Outil d'analyse des tendances de marché et d'évolution des prix."""

import json
from datetime import datetime, timedelta

from langchain_core.tools import tool

# ─── Données de tendances simulées ────────────────────────────────────────────

_TENDANCES_MOCK: dict[str, dict] = {
    "iphone": {
        "tendance_prix": "stable",
        "variation_30j": -1.2,
        "popularite_recherche": 95,
        "part_de_marche": 27.5,
        "concurrents_principaux": ["Samsung Galaxy S25 Ultra", "Google Pixel 9 Pro", "Xiaomi 15 Pro"],
        "saisonnalite": "Forte demande en septembre (nouveau lancement) et décembre (fêtes de fin d'année).",
        "recommandation_achat": "Prix stables — bon moment pour acheter.",
        "base_prix": 1199.99,
    },
    "nike": {
        "tendance_prix": "hausse",
        "variation_30j": 3.5,
        "popularite_recherche": 78,
        "part_de_marche": 18.2,
        "concurrents_principaux": ["Adidas Ultra Boost 24", "New Balance 1080 v13", "Asics Gel-Nimbus 26"],
        "saisonnalite": "Pics en janvier (résolutions sportives) et septembre (rentrée scolaire).",
        "recommandation_achat": "Tendance haussière — envisager l'achat avant une nouvelle hausse.",
        "base_prix": 149.99,
    },
    "macbook": {
        "tendance_prix": "baisse",
        "variation_30j": -2.8,
        "popularite_recherche": 82,
        "part_de_marche": 21.3,
        "concurrents_principaux": ["Dell XPS 13", "Lenovo ThinkPad X1 Carbon", "Microsoft Surface Laptop 7"],
        "saisonnalite": "Forte demande en août-septembre (rentrée étudiante) et janvier (soldes).",
        "recommandation_achat": "Tendance baissière — attendre encore quelques semaines pour un meilleur prix.",
        "base_prix": 1299.00,
    },
}

_TENDANCES_GENERIQUES = {
    "tendance_prix": "stable",
    "variation_30j": 0.8,
    "popularite_recherche": 60,
    "part_de_marche": 5.0,
    "concurrents_principaux": ["Concurrent A", "Concurrent B", "Concurrent C"],
    "saisonnalite": "Demande régulière tout au long de l'année, légère hausse en décembre.",
    "recommandation_achat": "Marché stable — acheter selon le besoin.",
    "base_prix": 99.99,
}


def _generer_historique_prix(base_prix: float, mois: int = 6) -> list[dict]:
    """Génère un historique de prix simulé sur N mois avec variations réalistes."""
    historique = []
    prix_courant = base_prix

    for i in range(mois, 0, -1):
        date = (datetime.now() - timedelta(days=i * 30)).strftime("%Y-%m")
        # Variation déterministe basée sur le hash pour reproductibilité
        variation_pct = ((hash(f"{base_prix:.2f}-{i}") % 21) - 10) / 100
        prix_courant = round(base_prix * (1 + variation_pct), 2)
        historique.append({"mois": date, "prix": prix_courant})

    return historique


# ─── Outil LangChain ──────────────────────────────────────────────────────────

@tool
def get_market_trends(product_name: str) -> str:
    """
    Analyse les tendances de marché, l'évolution des prix et la popularité d'un produit.

    Args:
        product_name: Nom du produit ou marché à analyser.

    Returns:
        JSON avec tendance de prix, variation sur 30 jours, historique 6 mois,
        popularité, concurrents et recommandation d'achat.
    """
    nom_lower = product_name.lower()

    tendances = next(
        (data for mot_cle, data in _TENDANCES_MOCK.items() if mot_cle in nom_lower),
        _TENDANCES_GENERIQUES,
    )

    base_prix = tendances.pop("base_prix", 99.99)

    resultat = {
        "produit": product_name,
        "date_analyse": datetime.now().isoformat(timespec="seconds"),
        **tendances,
        "historique_prix_6_mois": _generer_historique_prix(base_prix),
    }

    # Remettre base_prix dans le dict source pour les appels ultérieurs
    tendances["base_prix"] = base_prix

    return json.dumps(resultat, ensure_ascii=False, indent=2)
