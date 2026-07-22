"""Routes de l'API REST."""

import asyncio
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException

from src.agent.graph import run_analysis
from src.api.models import Analyse, RequeteAnalyse, ReponseAnalyse, StatutAnalyse
from src.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["analyse"])

# Stockage en mémoire — remplaçable par PostgreSQL/Redis en production
_analyses: dict[UUID, Analyse] = {}


# ─── Tâche de fond ────────────────────────────────────────────────────────────

async def _executer_analyse(analyse_id: UUID, sujet: str) -> None:
    """Lance l'analyse dans un thread pour ne pas bloquer la boucle asyncio."""
    analyse = _analyses[analyse_id]
    analyse.statut = StatutAnalyse.EN_COURS

    try:
        settings = get_settings()
        resultat = await asyncio.to_thread(run_analysis, sujet, settings)
        analyse.rapport_markdown = resultat["rapport"]
        analyse.statut = StatutAnalyse.TERMINEE
    except Exception as exc:
        analyse.statut = StatutAnalyse.ERREUR
        analyse.erreur = str(exc)
    finally:
        analyse.termine_le = datetime.now()


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/analyses", response_model=ReponseAnalyse, status_code=202)
async def creer_analyse(
    requete: RequeteAnalyse,
    background_tasks: BackgroundTasks,
) -> ReponseAnalyse:
    """
    Lance une nouvelle analyse de marché en arrière-plan.

    Retourne immédiatement un objet avec l'ID et le statut `en_attente`.
    Interrogez `GET /api/v1/analyses/{id}` pour obtenir le résultat.
    """
    analyse = Analyse(sujet=requete.sujet)
    _analyses[analyse.id] = analyse
    background_tasks.add_task(_executer_analyse, analyse.id, requete.sujet)
    return ReponseAnalyse(**analyse.model_dump())


@router.get("/analyses/{analyse_id}", response_model=ReponseAnalyse)
async def obtenir_analyse(analyse_id: UUID) -> ReponseAnalyse:
    """Récupère le statut et le rapport d'une analyse par son ID."""
    analyse = _analyses.get(analyse_id)
    if not analyse:
        raise HTTPException(status_code=404, detail="Analyse non trouvée.")
    return ReponseAnalyse(**analyse.model_dump())


@router.get("/analyses", response_model=list[ReponseAnalyse])
async def lister_analyses() -> list[ReponseAnalyse]:
    """Retourne toutes les analyses (du plus récent au plus ancien)."""
    return [
        ReponseAnalyse(**a.model_dump())
        for a in sorted(_analyses.values(), key=lambda x: x.cree_le, reverse=True)
    ]


@router.delete("/analyses/{analyse_id}", status_code=204)
async def supprimer_analyse(analyse_id: UUID) -> None:
    """Supprime une analyse de la mémoire."""
    if analyse_id not in _analyses:
        raise HTTPException(status_code=404, detail="Analyse non trouvée.")
    del _analyses[analyse_id]


@router.get("/health")
async def health_check() -> dict:
    """Vérifie l'état de santé de l'API."""
    settings = get_settings()
    return {
        "statut": "ok",
        "version": "1.0.0",
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "analyses_en_memoire": len(_analyses),
    }
