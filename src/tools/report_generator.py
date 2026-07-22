"""Outil de génération du rapport d'analyse de marché en Markdown."""

import json
from datetime import datetime

from langchain_core.tools import tool


def _charger_json(raw: str, nom: str) -> dict:
    """Parse le JSON en gérant les erreurs avec un fallback vide."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


@tool
def generate_report(
    product_data: str,
    sentiment_data: str,
    trend_data: str,
) -> str:
    """
    Compile les données des trois outils d'analyse en un rapport Markdown structuré.

    Args:
        product_data  : JSON retourné par scrape_product.
        sentiment_data: JSON retourné par analyze_sentiment.
        trend_data    : JSON retourné par get_market_trends.

    Returns:
        Rapport complet en Markdown avec résumé exécutif et recommandations.
    """
    produit   = _charger_json(product_data,   "scrape_product")
    sentiment = _charger_json(sentiment_data, "analyze_sentiment")
    tendances = _charger_json(trend_data,     "get_market_trends")

    nom_produit  = produit.get("nom") or tendances.get("produit") or "Produit"
    categorie    = produit.get("categorie", "N/A")
    description  = produit.get("description", "Aucune description disponible.")
    plateformes  = produit.get("plateformes", [])
    prix_min     = produit.get("prix_min", "N/A")
    prix_max     = produit.get("prix_max", "N/A")
    prix_moyen   = produit.get("prix_moyen", "N/A")
    now          = datetime.now().strftime("%d/%m/%Y à %H:%M")

    # ── En-tête ───────────────────────────────────────────────────────────────
    rapport = f"""# Rapport d'analyse de marché — {nom_produit}

> **Généré le** : {now}  
> **Catégorie** : {categorie}

---

## Résumé exécutif

| Indicateur | Valeur |
|---|---|
| Prix moyen marché | {prix_moyen} EUR |
| Sentiment client | **{sentiment.get("label_sentiment", "N/A").upper()}** ({sentiment.get("score_sentiment", "N/A")}/1.0) |
| Tendance de prix | {tendances.get("tendance_prix", "N/A")} ({tendances.get("variation_30j", 0):+.1f}% / 30 jours) |
| Popularité | {tendances.get("popularite_recherche", "N/A")} / 100 |
| Part de marché | {tendances.get("part_de_marche", "N/A")} % |

---

## 1. Présentation du produit

{description}

---

## 2. Comparatif des prix

| Plateforme | Prix (EUR) | Disponible | Vendeur |
|---|---|---|---|
"""

    for p in plateformes:
        dispo = "✅" if p.get("disponible") else "❌"
        rapport += (
            f"| {p.get('plateforme', 'N/A')} "
            f"| {p.get('prix', 'N/A'):.2f} "
            f"| {dispo} "
            f"| {p.get('vendeur', 'N/A')} |\n"
        )

    rapport += f"""
**Prix minimum** : {prix_min} EUR  
**Prix maximum** : {prix_max} EUR  
**Prix moyen**   : {prix_moyen} EUR

---

## 3. Analyse du sentiment client

| Métrique | Valeur |
|---|---|
| Score | {sentiment.get("score_sentiment", "N/A")} / 1.0 |
| Sentiment global | **{sentiment.get("label_sentiment", "N/A").upper()}** |
| Avis analysés | {sentiment.get("nombre_avis_analysés", "N/A")} |
| Positifs / Neutres / Négatifs | {sentiment.get("répartition", {}).get("positifs", 0)} / {sentiment.get("répartition", {}).get("neutres", 0)} / {sentiment.get("répartition", {}).get("négatifs", 0)} |

### Points forts
"""
    for point in sentiment.get("points_forts", ["Non disponible"]):
        rapport += f"- {point}\n"

    rapport += "\n### Points faibles\n"
    for point in sentiment.get("points_faibles", ["Non disponible"]):
        rapport += f"- {point}\n"

    if sentiment.get("résumé"):
        rapport += f"\n> {sentiment['résumé']}\n"

    # ── Tendances ─────────────────────────────────────────────────────────────
    rapport += """
---

## 4. Tendances de marché

| Indicateur | Valeur |
|---|---|
"""
    indicateurs = [
        ("Tendance de prix",     tendances.get("tendance_prix", "N/A")),
        ("Variation (30 jours)", f"{tendances.get('variation_30j', 0):+.1f}%"),
        ("Popularité",           f"{tendances.get('popularite_recherche', 'N/A')} / 100"),
        ("Recommandation",       tendances.get("recommandation_achat", "N/A")),
        ("Saisonnalité",         tendances.get("saisonnalite", "N/A")),
    ]
    for label, valeur in indicateurs:
        rapport += f"| {label} | {valeur} |\n"

    rapport += "\n### Concurrents principaux\n"
    for concurrent in tendances.get("concurrents_principaux", []):
        rapport += f"- {concurrent}\n"

    # ── Historique de prix ────────────────────────────────────────────────────
    historique = tendances.get("historique_prix_6_mois", [])
    if historique:
        rapport += "\n### Évolution des prix (6 derniers mois)\n\n"
        rapport += "| Mois | Prix (EUR) |\n|---|---|\n"
        for point in historique:
            rapport += f"| {point.get('mois', 'N/A')} | {point.get('prix', 'N/A'):.2f} |\n"

    # ── Recommandations ───────────────────────────────────────────────────────
    rapport += "\n---\n\n## 5. Recommandations stratégiques\n\n"

    score_sentiment = sentiment.get("score_sentiment", 0.5)
    variation_prix  = tendances.get("variation_30j", 0)

    if score_sentiment >= 0.65:
        rapport += (
            "✅ **Sentiment positif** — Le produit bénéficie d'une excellente perception client. "
            "Capitaliser sur les avis positifs dans la stratégie de contenu et les fiches produit.\n\n"
        )
    elif score_sentiment >= 0.40:
        rapport += (
            "⚠️ **Sentiment neutre** — Des actions d'amélioration du produit ou du service "
            "après-vente permettraient d'augmenter la satisfaction.\n\n"
        )
    else:
        rapport += (
            "🔴 **Sentiment négatif** — Des améliorations significatives sont requises. "
            "Analyser les retours négatifs en priorité.\n\n"
        )

    if variation_prix > 2:
        rapport += (
            f"📈 **Tendance haussière** ({variation_prix:+.1f}%) — Positionner le produit sur "
            "la valeur ajoutée ou proposer une offre groupée compétitive.\n\n"
        )
    elif variation_prix < -2:
        rapport += (
            f"📉 **Tendance baissière** ({variation_prix:+.1f}%) — Opportunité d'achat ou "
            "de repositionnement prix agressif pour gagner des parts de marché.\n\n"
        )
    else:
        rapport += (
            f"➡️ **Marché stable** ({variation_prix:+.1f}%) — Différenciation par "
            "le service, la garantie et la qualité de la relation client.\n\n"
        )

    rapport += "---\n\n*Rapport généré automatiquement par l'Agent d'Analyse de Marché E-commerce.*\n"

    return rapport
