"""Définition de l'état partagé entre les nœuds du graphe LangGraph."""

from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """
    État de l'agent propagé à travers le graphe LangGraph.

    Attributs
    ─────────
    messages        : Historique complet des messages (HumanMessage, AIMessage, ToolMessage).
                      Le reducer `add_messages` ajoute les nouveaux messages à la liste
                      au lieu de la remplacer.
    sujet           : Produit ou marché à analyser (ex: "iPhone 16 Pro").
    rapport_markdown: Rapport final généré en Markdown (vide jusqu'à la fin de l'analyse).
    """

    messages: Annotated[list, add_messages]
    sujet: str
    rapport_markdown: str
