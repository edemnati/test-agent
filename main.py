"""Point d'entrée CLI pour tester l'agent directement depuis le terminal."""

import sys

from src.agent.graph import run_analysis
from src.config import get_settings


def main() -> None:
    """
    Lance une analyse de marché depuis la ligne de commande.

    Utilisation
    ───────────
    py main.py "iPhone 16 Pro"
    py main.py "Nike Air Max 270"
    py main.py                       # Utilise "iPhone 16 Pro" par défaut
    """
    sujet = " ".join(sys.argv[1:]).strip() or "iPhone 16 Pro"
    settings = get_settings()

    print(f"🔍 Analyse en cours : {sujet}")
    print(f"   Modèle : {settings.llm_model} ({settings.llm_provider})\n")

    resultat = run_analysis(sujet, settings)
    rapport  = resultat["rapport"]

    print(rapport)

    # Sauvegarde du rapport
    nom_fichier = f"examples/rapport_{sujet.replace(' ', '_').lower()[:30]}.md"
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write(rapport)

    print(f"\n✅ Rapport sauvegardé dans : {nom_fichier}")


if __name__ == "__main__":
    main()
