"""Export centralisé de tous les outils disponibles pour l'agent."""

from src.tools.market_trend import get_market_trends
from src.tools.report_generator import generate_report
from src.tools.sentiment_analyzer import analyze_sentiment
from src.tools.web_scraper import scrape_product

ALL_TOOLS = [scrape_product, analyze_sentiment, get_market_trends, generate_report]

__all__ = [
    "scrape_product",
    "analyze_sentiment",
    "get_market_trends",
    "generate_report",
    "ALL_TOOLS",
]
