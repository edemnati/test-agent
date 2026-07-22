"""Fixtures partagées entre tous les modules de test."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from src.api.main import app
from src.config import Settings


@pytest.fixture
def client() -> TestClient:
    """Client HTTP de test pour l'API FastAPI (synchrone, pas de serveur requis)."""
    return TestClient(app)


@pytest.fixture
def settings_mock() -> Settings:
    """Paramètres de test avec données mock activées et LLM fictif."""
    return Settings(
        use_mock_data=True,
        llm_provider="ollama",
        llm_model="test-model",
        llm_base_url="http://localhost:11434",
    )


@pytest.fixture
def mock_llm() -> MagicMock:
    """LLM simulé — ne fait aucun appel réseau."""
    llm = MagicMock()
    llm.bind_tools.return_value = llm
    return llm
