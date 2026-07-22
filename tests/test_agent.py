"""Tests d'intégration pour l'orchestration de l'agent LangGraph."""

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage


class TestBuildAgentGraph:
    """Tests pour la construction et compilation du graphe."""

    def test_graph_compile_sans_erreur(self, settings_mock):
        """Le graphe se compile sans erreur avec un LLM simulé."""
        with patch("src.agent.graph.create_llm") as mock_create_llm:
            mock_llm = MagicMock()
            mock_llm.bind_tools.return_value = mock_llm
            mock_create_llm.return_value = mock_llm

            from src.agent.graph import build_agent_graph

            graphe = build_agent_graph(settings_mock)
            assert graphe is not None

    def test_graph_possede_noeuds_attendus(self, settings_mock):
        """Le graphe compilé contient les nœuds agent, tools et extract_report."""
        with patch("src.agent.graph.create_llm") as mock_create_llm:
            mock_llm = MagicMock()
            mock_llm.bind_tools.return_value = mock_llm
            mock_create_llm.return_value = mock_llm

            from src.agent.graph import build_agent_graph

            graphe = build_agent_graph(settings_mock)
            noeuds = set(graphe.nodes)
            assert "agent" in noeuds
            assert "tools" in noeuds
            assert "extract_report" in noeuds


class TestRunAnalysis:
    """Tests pour la fonction run_analysis."""

    def _creer_ai_message_final(self, contenu: str) -> AIMessage:
        """Crée un AIMessage sans appels d'outils (fin de l'analyse)."""
        msg = AIMessage(content=contenu)
        msg.tool_calls = []
        return msg

    def test_run_analysis_retourne_dict_avec_cles_attendues(self, settings_mock):
        """run_analysis retourne un dict avec les clés 'rapport' et 'messages'."""
        with patch("src.agent.graph.create_llm") as mock_create_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = self._creer_ai_message_final("Analyse terminée.")
            mock_llm.bind_tools.return_value = mock_llm
            mock_create_llm.return_value = mock_llm

            from src.agent.graph import run_analysis

            resultat = run_analysis("iPhone 16", settings_mock)

            assert "rapport" in resultat
            assert "messages" in resultat

    def test_etat_initial_premier_message_contient_sujet(self, settings_mock):
        """Le premier message de l'état initial contient le sujet d'analyse."""
        sujet = "Nike Air Max 270"
        with patch("src.agent.graph.create_llm") as mock_create_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = self._creer_ai_message_final("Terminé.")
            mock_llm.bind_tools.return_value = mock_llm
            mock_create_llm.return_value = mock_llm

            from src.agent.graph import run_analysis

            resultat = run_analysis(sujet, settings_mock)
            premier_message = resultat["messages"][0]

            assert sujet in premier_message.content

    def test_messages_est_une_liste(self, settings_mock):
        """L'historique des messages est une liste."""
        with patch("src.agent.graph.create_llm") as mock_create_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = self._creer_ai_message_final("Terminé.")
            mock_llm.bind_tools.return_value = mock_llm
            mock_create_llm.return_value = mock_llm

            from src.agent.graph import run_analysis

            resultat = run_analysis("MacBook Air", settings_mock)
            assert isinstance(resultat["messages"], list)
            assert len(resultat["messages"]) >= 1


class TestShouldContinue:
    """Tests pour la logique de routage conditionnel."""

    def test_message_avec_tool_calls_route_vers_tools(self):
        """Un AIMessage avec tool_calls déclenche le passage vers le nœud tools."""
        from src.agent.graph import _should_continue

        ai_msg = AIMessage(content="")
        ai_msg.tool_calls = [{"name": "scrape_product", "args": {}, "id": "1"}]

        etat = {
            "messages": [HumanMessage(content="test"), ai_msg],
            "sujet": "test",
            "rapport_markdown": "",
        }
        assert _should_continue(etat) == "tools"

    def test_message_sans_tool_calls_route_vers_extract_report(self):
        """Un AIMessage sans tool_calls déclenche extract_report."""
        from src.agent.graph import _should_continue

        ai_msg = AIMessage(content="Analyse terminée.")
        ai_msg.tool_calls = []

        etat = {
            "messages": [HumanMessage(content="test"), ai_msg],
            "sujet": "test",
            "rapport_markdown": "",
        }
        assert _should_continue(etat) == "extract_report"
