"""Configuration centralisée de l'application"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins de base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

# Dossiers de données
AO_PDF_DIR = DATA_DIR / "ao_pdf"
REG_DOCS_DIR = DATA_DIR / "reg_docs"
PAPERS_MOCK_DIR = DATA_DIR / "papers_mock"
HISTORIQUE_DIR = DATA_DIR / "historique"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"

# Dossiers de sortie
REPORTS_DIR = OUTPUT_DIR / "reports"
DECISIONS_DIR = OUTPUT_DIR / "decisions"

# Créer les dossiers s'ils n'existent pas
for directory in [AO_PDF_DIR, REG_DOCS_DIR, PAPERS_MOCK_DIR, HISTORIQUE_DIR,
                  CHROMA_DB_DIR, REPORTS_DIR, DECISIONS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Configuration ChromaDB
CHROMA_PERSIST_DIRECTORY = str(CHROMA_DB_DIR)
CHROMA_COLLECTION_NAME = "reg_documents"

# Configuration Scoring
SCORE_THRESHOLD_GO = int(os.getenv("SCORE_THRESHOLD_GO", "70"))
SCORE_THRESHOLD_RESERVE = int(os.getenv("SCORE_THRESHOLD_RESERVE", "50"))

# Pondérations des critères de scoring (total = 100%)
SCORING_WEIGHTS = {
    "matching_produit": 0.30,      # 30%
    "faisabilite": 0.20,            # 20%
    "conformite": 0.20,             # 20%
    "similarite_historique": 0.15,  # 15%
    "rentabilite": 0.15             # 15%
}

# Configuration extraction PDF
PDF_CHUNK_SIZE = 500  # tokens par chunk pour le REG
PDF_CHUNK_OVERLAP = 50  # overlap entre chunks

# Red flags bloquants
RED_FLAGS = {
    "deadline_days_min": 5,  # Minimum 5 jours ouvrés
    "certifications_required": ["ISO 27001"],  # Exemple
    "technologies_incompatibles": ["SAP", "Oracle EBS"]  # Exemple
}
