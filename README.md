# Agent d'Analyse de Marché E-commerce

Un agent intelligent qui analyse des produits e-commerce en quelques secondes. Donnez-lui un produit (ex: "iPhone 16 Pro"), et il compile automatiquement un rapport complet avec prix, sentiments clients, tendances du marché et recommandations.

**Supports Ollama (local gratuit), Groq, OpenAI, OpenRouter.**

---

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Démarrer rapidement](#démarrer-rapidement)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [Utilisation](#utilisation)
6. [Stockage des données](#stockage-des-données)
7. [Monitoring](#monitoring)
8. [Scaling](#scaling)

---

## Vue d'ensemble

### Ce que fait l'agent

Il automatise le travail d'un analyste marché :

1. **Scrape** les prix et caractéristiques produit depuis plusieurs plateformes
2. **Analyse** les avis clients pour extraire sentiments et tendances
3. **Suit** l'évolution des prix et identifie les concurrents clés
4. **Génère** un rapport Markdown avec insights et recommandations

Le tout en orchestrant ces appels via un agent LLM qui décide quand appeler quel outil — exactement comme un analyste qui référence ses sources au fur et à mesure.

### Pourquoi LangGraph

- **Flux explicite** : facile à modifier et debugger
- **Gestion native ReAct** : agent ↔ outils sans boucle manuelle
- **Observabilité** : traçage gratuit avec LangSmith
- **Production-ready** : gestion d'erreurs, timeouts, parallélisme

---

## Démarrer rapidement

### Option 1 : Groq (API rapide, gratuit)

Easiest pour démarrer — il suffit d'une clé d'API gratuite.

```powershell
# 1. Créer une clé sur https://console.groq.com

# 2. Setup du projet
git clone https://github.com/...
cd test-agent
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Configurer
copy .env.example .env

# Modifier .env :
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=gsk_xxxxxx

# 4. Tester
py main.py "iPhone 16 Pro"
```

### Option 2 : Ollama local (100% gratuit, zero API)

Si vous préférez ne rien envoyer sur Internet.

```powershell
# 1. Installer Ollama
winget install Ollama.Ollama

# 2. Télécharger un modèle
ollama pull llama3.2:3b

# 3. Setup du projet
git clone https://github.com/...
cd test-agent
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# 4. Tester (le .env est déjà configuré pour Ollama)
py main.py "Nike Air Max 270"
```

### Option 3 : API REST avec Docker

```powershell
docker-compose up --build
# API sur http://localhost:8000/docs
```

---

## Architecture

### Comment ça marche

L'agent suit le pattern **ReAct** (Reason → Act → Observe → Loop) :

```
1. Agent reçoit "analyse iPhone 16 Pro"
   ↓
2. Agent demande au LLM: "quel outil appeler ?"
   LLM dit: "d'abord scraper les prix"
   ↓
3. Exécute scrape_product, reçoit les données
   ↓
4. Agent demande: "quel outil maintenant ?"
   LLM dit: "analyser les sentiments"
   ↓
5. Exécute analyze_sentiment, reçoit scores
   ... (boucle continue)
   ↓
6. Quand suffisamment d'infos: "génère le rapport final"
   ↓
7. Rapport complet en Markdown
```

### Structure du code

```
src/
├── config.py              # Configuration (via .env)
├── llm_factory.py         # Crée le LLM selon le provider
├── agent/
│   ├── graph.py          # Graphe LangGraph (orchestration)
│   ├── state.py          # État partagé entre les étapes
│   └── prompts.py        # Templates de system prompts
├── tools/
│   ├── web_scraper.py    # Scrape prix/specs
│   ├── sentiment_analyzer.py
│   ├── market_trend.py
│   └── report_generator.py
└── api/
    ├── main.py           # FastAPI app
    ├── routes.py
    └── models.py
```

### Les 4 outils de l'agent

| Outil | Rôle | Exemple |
|-------|------|---------|
| **scrape_product** | Récupère prix et caractéristiques | "Trouver le prix de l'iPhone 16 Pro sur Amazon" |
| **analyze_sentiment** | Score et tendances avis clients | "Quel est l'avis des clients sur la caméra ?" |
| **get_market_trends** | Évolution prix, concurrents | "Y a-t-il une tendance à la baisse ?" |
| **generate_report** | Compile le rapport final | "Mets tout ça en rapport Markdown" |

---

## Configuration

Tout se configure via un seul fichier `.env`. Zéro modification de code.

### Fichier `.env`

```dotenv
# Quel fournisseur LLM ?
LLM_PROVIDER=groq              # groq | ollama | openai | openrouter
LLM_MODEL=llama-3.3-70b-versatile
LLM_BASE_URL=http://localhost:11434  # Ignoré pour Groq/OpenAI
LLM_API_KEY=gsk_xxxxxx         # Vide pour Ollama

# Paramètres
LLM_TEMPERATURE=0.1            # 0=strict, 1=créatif
LLM_TIMEOUT=120                # Secondes max par appel

# Agent
AGENT_MAX_ITERATIONS=10        # Max appels outils par analyse

# Données
USE_MOCK_DATA=true             # true=données simulées (dev)

# API (FastAPI)
API_HOST=0.0.0.0
API_PORT=8000
```

### Exemples pour chaque provider

**Groq (recommandé, ultra-rapide) :**
```dotenv
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=gsk_xxxxx
```

**Ollama (local, gratuit) :**
```dotenv
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2:3b
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=
```

**OpenAI :**
```dotenv
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-xxxxx
```

**OpenRouter :**
```dotenv
LLM_PROVIDER=openrouter
LLM_MODEL=meta-llama/llama-3.2-3b-instruct
LLM_API_KEY=sk-or-xxxxx
```

---

## Utilisation

### CLI (Plus rapide pour tester)

```powershell
py main.py "iPhone 16 Pro"
py main.py "Nike Air Max 270"

# Le rapport s'affiche dans le terminal
# ET se sauvegarde en rapport_iphone_16_pro.md
```

### API REST

Pour intégrer dans une app ou faire des requêtes programmatiques.

```powershell
uvicorn src.api.main:app --reload
# Documentation interactive: http://localhost:8000/docs
```

**Exemples de requêtes :**

```bash
# Lancer une analyse
curl -X POST http://localhost:8000/api/v1/analyses \
  -H "Content-Type: application/json" \
  -d '{"sujet": "iPhone 16 Pro"}'

# Récupérer un rapport
curl http://localhost:8000/api/v1/analyses/uuid...

# Lister analyses
curl http://localhost:8000/api/v1/analyses

# Santé
curl http://localhost:8000/api/v1/health
```

### Tests

```powershell
pytest                    # Tous les tests
pytest -v --tb=short     # Verbose
pytest tests/test_tools.py -v  # Un seul fichier
```

---

## Stockage des données

### Schéma PostgreSQL (production)

**Analyses :**
```sql
CREATE TABLE analyses (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sujet            VARCHAR(200) NOT NULL,
    statut           VARCHAR(20) NOT NULL,
    rapport_markdown TEXT,
    llm_provider     VARCHAR(50),
    llm_model        VARCHAR(100),
    duree_ms         INTEGER,
    cree_le          TIMESTAMPTZ DEFAULT NOW(),
    termine_le       TIMESTAMPTZ
);
```

**Historique (pour debugger) :**
```sql
CREATE TABLE historique_requetes (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analyse_id   UUID REFERENCES analyses(id),
    etape        VARCHAR(50),  -- 'scrape', 'sentiment', 'trend', 'report'
    input_data   JSONB,
    output_data  JSONB,
    duree_ms     INTEGER,
    cree_le      TIMESTAMPTZ DEFAULT NOW()
);
```

### Recommendations par cas

| Cas | Base | Raison |
|-----|------|--------|
| Résultats d'analyse | PostgreSQL | Requêtes complexes, ACID |
| Cache court terme | Redis | TTL 1h, très rapide |
| Rapports volumineux | S3 / Azure Blob | Économique, scalable |
| Dev local | SQLite | Zéro setup |
| Queue d'analyses | Redis Streams | Celery broker |

**Cache intelligent :**
- Même produit analysé dans l'heure → réutiliser le rapport
- Sinon → relancer l'agent

---

## Monitoring

### Tracer les exécutions (LangSmith)

Pour tracker chaque appel agent (optionnel).

```dotenv
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_xxxxx
LANGCHAIN_PROJECT=market-analysis-agent
```

Vous voyez :
- Séquence d'appels outils
- Tokens consommés
- Latence par nœud
- Erreurs et timeouts

### Métriques clés

| Métrique | Alerte | Tool |
|----------|--------|------|
| Latence totale | > 120s | Prometheus |
| Taux erreur | > 5% | AlertManager |
| Tokens/heure | > 80% quota | Webhooks |
| Temps réponse p95 | > 500ms | Prometheus |

---

## Scaling

### Pour 100+ analyses simultanées

Utiliser **Celery** + **Redis** pour découpler les requêtes HTTP de l'exécution :

```
HTTP Request
    ↓
FastAPI (N replicas)
    ↓
Redis Queue
    ↓
Celery Worker Pool (auto-scaling)
    ↓
Agent LangGraph
```

Chaque worker exécute une analyse à la fois. L'auto-scaling Kubernetes ajuste selon la file.

### Optimiser les coûts LLM

| Technique | Économie | Implémentation |
|-----------|----------|---|
| Cache sémantique | 30-60% | RedisSemanticCache |
| Modèle local | 100% | `LLM_PROVIDER=ollama` |
| Compression prompt | 20-40% | Résumer après 5 tours |
| Modèle smaller | 50% | Router logique |

### Paralléliser

Les trois outils de collecte (scrape, sentiment, trends) sont indépendants → les exécuter en parallèle réduit la latence de **60%**.

---

## Support & Contribution

Pour des questions ou contributions, consultez la doc ou ouvrez une issue sur GitHub.
