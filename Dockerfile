FROM python:3.13-slim

WORKDIR /app

# Copie des dépendances en premier (optimise le cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src/ src/
COPY main.py .

EXPOSE 8000

# Démarrage du serveur FastAPI
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
