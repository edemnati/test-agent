"""Graphe LangGraph de l'agent d'analyse de marché."""

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from src.agent.prompts import SYSTEM_PROMPT
from src.agent.state import AgentState
from src.config import Settings
from src.llm_factory import create_llm
from src.tools import ALL_TOOLS


# ─── Nœuds du graphe ──────────────────────────────────────────────────────────

def _build_agent_node(llm_with_tools):
    """Fabrique le nœud agent avec le LLM configuré."""

    def agent_node(state: AgentState) -> dict:
        """
        Nœud de décision : le LLM choisit le prochain outil à appeler
        ou termine l'analyse si tous les outils ont été utilisés.
        """
        system_message = SystemMessage(
            content=SYSTEM_PROMPT.format(sujet=state.get("sujet", "produit inconnu"))
        )
        messages = [system_message] + list(state["messages"])
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    return agent_node


def _extract_report_node(state: AgentState) -> dict:
    """
    Nœud de synthèse : extrait le rapport Markdown depuis les messages d'outils.

    Cherche en priorité le résultat de `generate_report`, sinon tout contenu
    commençant par un titre Markdown (#).
    """
    for msg in reversed(state["messages"]):
        # ToolMessage issu de generate_report
        if getattr(msg, "name", None) == "generate_report":
            return {"rapport_markdown": msg.content}

    # Fallback : premier contenu ressemblant à un rapport Markdown
    for msg in reversed(state["messages"]):
        content = getattr(msg, "content", "")
        if isinstance(content, str) and content.startswith("#"):
            return {"rapport_markdown": content}

    return {"rapport_markdown": "Rapport non disponible — analyse incomplète."}


# ─── Condition de routage ──────────────────────────────────────────────────────

def _should_continue(state: AgentState) -> str:
    """
    Détermine le prochain nœud selon le dernier message de l'agent.

    - Si le LLM demande des appels d'outils → nœud 'tools'
    - Sinon                                  → nœud 'extract_report'
    """
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return "extract_report"


# ─── Construction du graphe ───────────────────────────────────────────────────

def build_agent_graph(settings: Settings):
    """
    Construit et compile le graphe LangGraph de l'agent.

    Architecture
    ────────────
    [START] ──► agent ──► tools ──► agent ──► ... ──► extract_report ──► [END]
                  └──────────────────────────────────────────────────────────►

    Le cycle agent → tools se répète jusqu'à ce que le LLM n'émette plus
    d'appels d'outils, puis le rapport final est extrait.

    Args:
        settings: Configuration de l'application (fournisseur LLM, modèle, etc.)

    Returns:
        Graphe LangGraph compilé, prêt à être invoqué.
    """
    llm = create_llm(settings)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    graph = StateGraph(AgentState)

    # Ajout des nœuds
    graph.add_node("agent", _build_agent_node(llm_with_tools))
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    graph.add_node("extract_report", _extract_report_node)

    # Point d'entrée
    graph.set_entry_point("agent")

    # Routage conditionnel depuis l'agent
    graph.add_conditional_edges("agent", _should_continue, {
        "tools": "tools",
        "extract_report": "extract_report",
    })

    # Retour des outils vers l'agent
    graph.add_edge("tools", "agent")

    # Fin après extraction du rapport
    graph.add_edge("extract_report", END)

    return graph.compile()


# ─── Point d'entrée public ────────────────────────────────────────────────────

def run_analysis(sujet: str, settings: Settings) -> dict:
    """
    Exécute une analyse de marché complète pour le sujet donné.

    Args:
        sujet   : Produit ou marché à analyser (ex: "iPhone 16 Pro")
        settings: Configuration de l'application

    Returns:
        Dictionnaire contenant :
        - 'rapport'  : Rapport d'analyse en Markdown
        - 'messages' : Historique complet des messages de l'agent
    """
    graph = build_agent_graph(settings)

    etat_initial: AgentState = {
        "messages": [HumanMessage(content=f"Analyse le marché pour : {sujet}")],
        "sujet": sujet,
        "rapport_markdown": "",
    }

    resultat = graph.invoke(
        etat_initial,
        config={"recursion_limit": settings.agent_max_iterations * 2},
    )

    return {
        "rapport": resultat.get("rapport_markdown", ""),
        "messages": resultat["messages"],
    }
