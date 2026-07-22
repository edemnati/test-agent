"""Fabrique de modèles LLM — change de fournisseur via la configuration sans modifier le code."""

from langchain_core.language_models import BaseChatModel

from src.config import Settings


def create_llm(settings: Settings) -> BaseChatModel:
    """
    Instancie et retourne un modèle LLM selon la configuration.

    Fournisseurs supportés
    ─────────────────────
    - ollama     : Modèle local via Ollama (défaut — gratuit, aucune clé requise)
    - openai     : API OpenAI officielle
    - groq       : API Groq (très rapide, tier gratuit disponible)
    - openrouter : Agrégateur de modèles (accès unifié à de nombreux LLM)

    Pour changer de fournisseur, modifier LLM_PROVIDER dans le fichier .env.
    """
    provider = settings.llm_provider.lower().strip()

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            temperature=settings.llm_temperature,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            temperature=settings.llm_temperature,
            timeout=settings.llm_timeout,
        )

    if provider == "groq":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url="https://api.groq.com/openai/v1",
            temperature=settings.llm_temperature,
            timeout=settings.llm_timeout,
        )

    if provider == "openrouter":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm_model,
            api_key=settings.llm_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=settings.llm_temperature,
            timeout=settings.llm_timeout,
        )

    raise ValueError(
        f"Fournisseur LLM non supporté : {provider!r}. "
        "Valeurs valides : ollama | openai | groq | openrouter"
    )
