"""Tests pour les endpoints de l'API REST."""

import pytest
from fastapi.testclient import TestClient


# ═════════════════════════════════════════════════════════════════════════════
# Health check
# ═════════════════════════════════════════════════════════════════════════════

class TestHealthCheck:
    """Tests pour l'endpoint GET /api/v1/health."""

    def test_health_retourne_200(self, client: TestClient):
        """L'endpoint health est disponible et retourne 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_statut_ok(self, client: TestClient):
        """Le champ statut vaut 'ok'."""
        response = client.get("/api/v1/health")
        assert response.json()["statut"] == "ok"

    def test_health_expose_version(self, client: TestClient):
        """La version de l'API est exposée."""
        response = client.get("/api/v1/health")
        assert "version" in response.json()

    def test_health_expose_provider_llm(self, client: TestClient):
        """Le fournisseur LLM configuré est exposé."""
        response = client.get("/api/v1/health")
        assert "llm_provider" in response.json()


# ═════════════════════════════════════════════════════════════════════════════
# POST /api/v1/analyses
# ═════════════════════════════════════════════════════════════════════════════

class TestCreerAnalyse:
    """Tests pour POST /api/v1/analyses."""

    def test_cree_analyse_retourne_202(self, client: TestClient):
        """La création retourne le code HTTP 202 Accepted."""
        response = client.post("/api/v1/analyses", json={"sujet": "iPhone 16"})
        assert response.status_code == 202

    def test_cree_analyse_retourne_id_uuid(self, client: TestClient):
        """La réponse contient un ID au format UUID."""
        response = client.post("/api/v1/analyses", json={"sujet": "Nike Air Max"})
        data = response.json()
        assert "id" in data
        assert len(data["id"]) == 36  # Format UUID standard

    def test_cree_analyse_statut_initial_en_attente(self, client: TestClient):
        """Le statut initial est 'en_attente'."""
        response = client.post("/api/v1/analyses", json={"sujet": "MacBook Air"})
        assert response.json()["statut"] == "en_attente"

    def test_cree_analyse_sujet_retourne_dans_reponse(self, client: TestClient):
        """Le sujet fourni est retourné dans la réponse."""
        sujet = "Produit de test unique"
        response = client.post("/api/v1/analyses", json={"sujet": sujet})
        assert response.json()["sujet"] == sujet

    def test_cree_analyse_sujet_vide_retourne_422(self, client: TestClient):
        """Un sujet vide déclenche une erreur de validation 422."""
        response = client.post("/api/v1/analyses", json={"sujet": ""})
        assert response.status_code == 422

    def test_cree_analyse_sans_body_retourne_422(self, client: TestClient):
        """Une requête sans corps retourne 422."""
        response = client.post("/api/v1/analyses", json={})
        assert response.status_code == 422

    def test_cree_analyse_sujet_trop_long_retourne_422(self, client: TestClient):
        """Un sujet dépassant 200 caractères retourne 422."""
        sujet_long = "x" * 201
        response = client.post("/api/v1/analyses", json={"sujet": sujet_long})
        assert response.status_code == 422


# ═════════════════════════════════════════════════════════════════════════════
# GET /api/v1/analyses/{id}
# ═════════════════════════════════════════════════════════════════════════════

class TestObtenirAnalyse:
    """Tests pour GET /api/v1/analyses/{analyse_id}."""

    def test_obtenir_analyse_existante_retourne_200(self, client: TestClient):
        """Récupérer une analyse existante retourne 200."""
        create_resp = client.post("/api/v1/analyses", json={"sujet": "Test"})
        analyse_id  = create_resp.json()["id"]

        get_resp = client.get(f"/api/v1/analyses/{analyse_id}")
        assert get_resp.status_code == 200

    def test_obtenir_analyse_id_correspond(self, client: TestClient):
        """L'ID retourné correspond à celui de la création."""
        create_resp = client.post("/api/v1/analyses", json={"sujet": "Test ID"})
        analyse_id  = create_resp.json()["id"]

        get_resp = client.get(f"/api/v1/analyses/{analyse_id}")
        assert get_resp.json()["id"] == analyse_id

    def test_obtenir_analyse_inexistante_retourne_404(self, client: TestClient):
        """Un ID inexistant retourne 404 Not Found."""
        response = client.get("/api/v1/analyses/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


# ═════════════════════════════════════════════════════════════════════════════
# GET /api/v1/analyses
# ═════════════════════════════════════════════════════════════════════════════

class TestListerAnalyses:
    """Tests pour GET /api/v1/analyses."""

    def test_lister_retourne_liste(self, client: TestClient):
        """L'endpoint retourne une liste JSON."""
        response = client.get("/api/v1/analyses")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_analyse_cree_apparait_dans_liste(self, client: TestClient):
        """Une analyse créée est visible dans la liste."""
        sujet = "Produit listable unique"
        client.post("/api/v1/analyses", json={"sujet": sujet})

        response = client.get("/api/v1/analyses")
        sujets = [a["sujet"] for a in response.json()]
        assert sujet in sujets


# ═════════════════════════════════════════════════════════════════════════════
# DELETE /api/v1/analyses/{id}
# ═════════════════════════════════════════════════════════════════════════════

class TestSupprimerAnalyse:
    """Tests pour DELETE /api/v1/analyses/{analyse_id}."""

    def test_supprimer_analyse_retourne_204(self, client: TestClient):
        """La suppression d'une analyse existante retourne 204 No Content."""
        create_resp = client.post("/api/v1/analyses", json={"sujet": "À supprimer"})
        analyse_id  = create_resp.json()["id"]

        delete_resp = client.delete(f"/api/v1/analyses/{analyse_id}")
        assert delete_resp.status_code == 204

    def test_apres_suppression_get_retourne_404(self, client: TestClient):
        """Après suppression, l'analyse n'est plus accessible."""
        create_resp = client.post("/api/v1/analyses", json={"sujet": "Supprimé après"})
        analyse_id  = create_resp.json()["id"]
        client.delete(f"/api/v1/analyses/{analyse_id}")

        get_resp = client.get(f"/api/v1/analyses/{analyse_id}")
        assert get_resp.status_code == 404

    def test_supprimer_inexistant_retourne_404(self, client: TestClient):
        """Supprimer un ID inexistant retourne 404."""
        response = client.delete("/api/v1/analyses/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
