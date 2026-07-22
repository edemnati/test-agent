"""Modèles Pydantic pour l'API REST."""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class StatutAnalyse(str, Enum):
    """Statuts du cycle de vie d'une analyse."""
    EN_ATTENTE = "en_attente"
    EN_COURS   = "en_cours"
    TERMINEE   = "terminee"
    ERREUR     = "erreur"


class RequeteAnalyse(BaseModel):
    """Corps attendu pour POST /api/v1/analyses."""

    sujet: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Produit ou marché à analyser",
        examples=["iPhone 16 Pro", "Nike Air Max 270", "MacBook Air M4"],
    )


class Analyse(BaseModel):
    """Représentation interne d'une analyse (stockage en mémoire)."""

    id:               UUID         = Field(default_factory=uuid4)
    sujet:            str
    statut:           StatutAnalyse = StatutAnalyse.EN_ATTENTE
    rapport_markdown: str           = ""
    erreur:           str | None    = None
    cree_le:          datetime      = Field(default_factory=datetime.now)
    termine_le:       datetime | None = None


class ReponseAnalyse(BaseModel):
    """Réponse sérialisée retournée par l'API."""

    id:               UUID
    sujet:            str
    statut:           StatutAnalyse
    rapport_markdown: str           = ""
    erreur:           str | None    = None
    cree_le:          datetime
    termine_le:       datetime | None = None
