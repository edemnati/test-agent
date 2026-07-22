"""Point d'entrée de l'application FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router

app = FastAPI(
    title="Agent d'Analyse de Marché E-commerce",
    description=(
        "API REST orchestrant un agent LangGraph pour produire des rapports "
        "d'analyse de marché e-commerce complets et structurés."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
