"""Configuration centralisée — chargée depuis les variables d'environnement ou le fichier .env."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Paramètres de configuration de l'application.

    Toutes les valeurs peuvent être surchargées via des variables d'environnement
    ou un fichier .env à la racine du projet.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── Fournisseur LLM ──────────────────────────────────────────────────────
    llm_provider: str = Field(
        default="ollama",
        description="Fournisseur LLM : 'ollama' | 'openai' | 'groq' | 'openrouter'",
    )
    llm_model: str = Field(
        default="llama3.2:3b",
        description="Nom du modèle à utiliser (ex: llama3.2:3b, gpt-4o-mini)",
    )
    llm_base_url: str = Field(
        default="http://localhost:11434",
        description="URL de base pour Ollama ou endpoint compatible OpenAI",
    )
    llm_api_key: str = Field(
        default="",
        description="Clé API (laisser vide pour Ollama local)",
    )
    llm_temperature: float = Field(
        default=0.1,
        ge=0.0,
        le=2.0,
        description="Température du LLM (0.0 = déterministe)",
    )
    llm_timeout: int = Field(
        default=120,
        gt=0,
        description="Timeout en secondes pour les appels LLM",
    )

    # ─── Agent ────────────────────────────────────────────────────────────────
    agent_max_iterations: int = Field(
        default=10,
        gt=0,
        description="Nombre maximum d'itérations (appels outils) de l'agent",
    )

    # ─── Données ──────────────────────────────────────────────────────────────
    use_mock_data: bool = Field(
        default=True,
        description="Utiliser des données simulées (True) ou des APIs réelles (False)",
    )

    # ─── API REST ─────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, gt=0, le=65535)
    api_debug: bool = Field(default=False)

    def safe_repr(self) -> str:
        """Représentation sans les données sensibles (clé API masquée)."""
        key_status = "définie" if self.llm_api_key else "non définie"
        return (
            f"Settings(provider={self.llm_provider!r}, model={self.llm_model!r}, "
            f"base_url={self.llm_base_url!r}, api_key={key_status})"
        )


def get_settings() -> Settings:
    """Retourne une instance des paramètres chargés depuis l'environnement."""
    return Settings()
