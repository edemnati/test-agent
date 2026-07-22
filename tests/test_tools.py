"""Tests unitaires pour les quatre outils de l'agent."""

import json

import pytest

from src.tools.market_trend import get_market_trends
from src.tools.report_generator import generate_report
from src.tools.sentiment_analyzer import analyze_sentiment
from src.tools.web_scraper import scrape_product


# ═════════════════════════════════════════════════════════════════════════════
# Web Scraper
# ═════════════════════════════════════════════════════════════════════════════

class TestWebScraper:
    """Tests pour l'outil scrape_product."""

    def test_produit_connu_retourne_donnees_completes(self):
        """Un produit du catalogue mock retourne toutes les clés attendues."""
        result = scrape_product.invoke({"query": "iPhone 16"})
        data = json.loads(result)

        assert data["nom"] == "Apple iPhone 16 Pro"
        assert len(data["plateformes"]) == 4
        assert "prix_min" in data
        assert "prix_max" in data
        assert "prix_moyen" in data

    def test_prix_min_inferieur_ou_egal_prix_max(self):
        """La cohérence des prix calculés est garantie."""
        result = scrape_product.invoke({"query": "Nike Air Max"})
        data = json.loads(result)

        assert data["prix_min"] <= data["prix_moyen"] <= data["prix_max"]

    def test_produit_inconnu_retourne_donnees_generiques(self):
        """Un produit hors catalogue retourne des données génériques avec le nom fourni."""
        query = "Lampe de bureau XYZ-9000"
        result = scrape_product.invoke({"query": query})
        data = json.loads(result)

        assert data["nom"] == query
        assert len(data["plateformes"]) >= 1

    def test_retourne_toujours_json_valide(self):
        """Le retour est toujours un JSON parsable, quelle que soit l'entrée."""
        for query in ["", "???", "iPhone", "produit inconnu 12345"]:
            result = scrape_product.invoke({"query": query})
            data = json.loads(result)  # ne doit pas lever d'exception
            assert isinstance(data, dict)

    def test_champ_collecte_le_est_present(self):
        """Le timestamp de collecte est inclus dans le résultat."""
        result = scrape_product.invoke({"query": "MacBook"})
        data = json.loads(result)

        assert "collecte_le" in data
        assert len(data["collecte_le"]) > 0


# ═════════════════════════════════════════════════════════════════════════════
# Sentiment Analyzer
# ═════════════════════════════════════════════════════════════════════════════

class TestSentimentAnalyzer:
    """Tests pour l'outil analyze_sentiment."""

    def test_score_dans_intervalle_valide(self):
        """Le score de sentiment est compris entre 0.0 et 1.0."""
        result = analyze_sentiment.invoke({"product_name": "iPhone"})
        data = json.loads(result)

        assert 0.0 <= data["score_sentiment"] <= 1.0

    def test_label_est_une_valeur_valide(self):
        """Le label de sentiment appartient à l'ensemble des valeurs attendues."""
        result = analyze_sentiment.invoke({"product_name": "Nike Air Max"})
        data = json.loads(result)

        assert data["label_sentiment"] in ("positif", "neutre", "négatif")

    def test_avis_fournis_manuellement(self):
        """L'outil fonctionne avec des avis passés en paramètre."""
        avis = ["Excellent produit !", "Très satisfait.", "Qualité top."]
        result = analyze_sentiment.invoke({"product_name": "Test", "reviews": avis})
        data = json.loads(result)

        assert data["nombre_avis_analysés"] == 3

    def test_points_forts_et_faibles_sont_des_listes(self):
        """Les points forts et faibles sont des listes non nulles."""
        result = analyze_sentiment.invoke({"product_name": "MacBook"})
        data = json.loads(result)

        assert isinstance(data["points_forts"], list)
        assert isinstance(data["points_faibles"], list)
        assert len(data["points_forts"]) >= 1

    def test_resume_contient_le_label(self):
        """Le résumé textuel mentionne le label de sentiment."""
        result = analyze_sentiment.invoke({"product_name": "iPhone"})
        data = json.loads(result)

        assert data["label_sentiment"] in data["résumé"]

    def test_repartition_somme_egale_nombre_avis(self):
        """La somme positifs + neutres + négatifs égale le nombre total d'avis."""
        result = analyze_sentiment.invoke({"product_name": "Nike"})
        data = json.loads(result)

        rep = data["répartition"]
        total = rep["positifs"] + rep["neutres"] + rep["négatifs"]
        assert total == data["nombre_avis_analysés"]


# ═════════════════════════════════════════════════════════════════════════════
# Market Trend
# ═════════════════════════════════════════════════════════════════════════════

class TestMarketTrend:
    """Tests pour l'outil get_market_trends."""

    def test_historique_contient_six_mois(self):
        """L'historique des prix couvre exactement 6 mois."""
        result = get_market_trends.invoke({"product_name": "iPhone"})
        data = json.loads(result)

        assert len(data["historique_prix_6_mois"]) == 6

    def test_chaque_point_historique_a_mois_et_prix(self):
        """Chaque entrée de l'historique contient les clés 'mois' et 'prix'."""
        result = get_market_trends.invoke({"product_name": "Nike"})
        data = json.loads(result)

        for point in data["historique_prix_6_mois"]:
            assert "mois" in point
            assert "prix" in point
            assert isinstance(point["prix"], float)

    def test_variation_30j_est_numerique(self):
        """La variation de prix sur 30 jours est un nombre."""
        result = get_market_trends.invoke({"product_name": "MacBook"})
        data = json.loads(result)

        assert isinstance(data["variation_30j"], (int, float))

    def test_concurrents_principaux_non_vide(self):
        """La liste de concurrents contient au moins un élément."""
        result = get_market_trends.invoke({"product_name": "iPhone"})
        data = json.loads(result)

        assert len(data["concurrents_principaux"]) >= 1

    def test_produit_inconnu_retourne_tendances_par_defaut(self):
        """Un produit hors catalogue retourne des tendances génériques valides."""
        result = get_market_trends.invoke({"product_name": "Widget inédit 99"})
        data = json.loads(result)

        assert "tendance_prix" in data
        assert "popularite_recherche" in data
        assert "recommandation_achat" in data

    def test_tendance_prix_est_valeur_connue(self):
        """La tendance de prix est l'une des valeurs attendues."""
        result = get_market_trends.invoke({"product_name": "Nike"})
        data = json.loads(result)

        assert data["tendance_prix"] in ("hausse", "baisse", "stable")


# ═════════════════════════════════════════════════════════════════════════════
# Report Generator
# ═════════════════════════════════════════════════════════════════════════════

class TestReportGenerator:
    """Tests pour l'outil generate_report."""

    @pytest.fixture
    def jeu_de_donnees(self):
        """Jeu de données JSON valide pour les tests du générateur de rapport."""
        product_data = json.dumps({
            "nom": "Produit Test",
            "categorie": "Électronique",
            "description": "Description de test.",
            "plateformes": [
                {"plateforme": "Amazon", "prix": 99.99, "devise": "EUR", "disponible": True, "vendeur": "Test"},
                {"plateforme": "Fnac",   "prix": 104.99,"devise": "EUR", "disponible": False,"vendeur": "Fnac"},
            ],
            "prix_min": 99.99,
            "prix_max": 104.99,
            "prix_moyen": 102.49,
        })
        sentiment_data = json.dumps({
            "score_sentiment": 0.8,
            "label_sentiment": "positif",
            "nombre_avis_analysés": 10,
            "répartition": {"positifs": 8, "neutres": 1, "négatifs": 1},
            "points_forts": ["Très bonne qualité"],
            "points_faibles": ["Prix un peu élevé"],
            "résumé": "Sentiment positif global.",
        })
        trend_data = json.dumps({
            "produit": "Produit Test",
            "tendance_prix": "stable",
            "variation_30j": 1.5,
            "popularite_recherche": 70,
            "part_de_marche": 8.0,
            "concurrents_principaux": ["Concurrent A", "Concurrent B"],
            "saisonnalite": "Stable toute l'année.",
            "recommandation_achat": "Acheter maintenant.",
            "historique_prix_6_mois": [
                {"mois": "2026-01", "prix": 98.50},
                {"mois": "2026-02", "prix": 99.00},
            ],
        })
        return product_data, sentiment_data, trend_data

    def test_rapport_commence_par_titre_markdown(self, jeu_de_donnees):
        """Le rapport commence par un titre de niveau 1 (#)."""
        product_data, sentiment_data, trend_data = jeu_de_donnees
        result = generate_report.invoke({
            "product_data": product_data,
            "sentiment_data": sentiment_data,
            "trend_data": trend_data,
        })
        assert result.startswith("#")

    def test_rapport_contient_cinq_sections(self, jeu_de_donnees):
        """Le rapport contient les 5 sections numérotées principales."""
        product_data, sentiment_data, trend_data = jeu_de_donnees
        result = generate_report.invoke({
            "product_data": product_data,
            "sentiment_data": sentiment_data,
            "trend_data": trend_data,
        })
        for i in range(1, 6):
            assert f"## {i}." in result

    def test_rapport_contient_le_nom_produit(self, jeu_de_donnees):
        """Le rapport mentionne le nom du produit dans le titre."""
        product_data, sentiment_data, trend_data = jeu_de_donnees
        result = generate_report.invoke({
            "product_data": product_data,
            "sentiment_data": sentiment_data,
            "trend_data": trend_data,
        })
        assert "Produit Test" in result

    def test_rapport_avec_json_invalide_ne_leve_pas_exception(self):
        """Le générateur résiste aux entrées JSON malformées."""
        result = generate_report.invoke({
            "product_data": "INVALIDE",
            "sentiment_data": "{}",
            "trend_data": "{}",
        })
        assert isinstance(result, str)
        assert len(result) > 0

    def test_rapport_contient_tableau_prix(self, jeu_de_donnees):
        """Le rapport contient un tableau Markdown avec les plateformes."""
        product_data, sentiment_data, trend_data = jeu_de_donnees
        result = generate_report.invoke({
            "product_data": product_data,
            "sentiment_data": sentiment_data,
            "trend_data": trend_data,
        })
        assert "Amazon" in result
        assert "99.99" in result

    def test_rapport_sentiment_positif_recommandation_positive(self, jeu_de_donnees):
        """Un sentiment positif génère une recommandation affirmative."""
        product_data, sentiment_data, trend_data = jeu_de_donnees
        result = generate_report.invoke({
            "product_data": product_data,
            "sentiment_data": sentiment_data,
            "trend_data": trend_data,
        })
        assert "✅" in result  # Icône du sentiment positif
