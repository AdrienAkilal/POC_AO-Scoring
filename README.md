# Application de Scoring et Préparation de Réponses aux Appels d'Offres

POC - Phase de prototypage | Soutenance du 13 mars 2025

## 📋 Description

Application automatisée pour analyser les appels d'offres (AO), calculer un score de pertinence et générer automatiquement les livrables de réponse (Go Pack ou No-Go Report).

### Fonctionnalités principales

- **Ingestion automatique** de PDF d'appels d'offres (CCTP, RC, annexes)
- **Extraction NLP structurée** avec GPT-4o (exigences, questions, critères, dates)
- **RAG (Retrieval-Augmented Generation)** avec base vectorielle ChromaDB
- **Scoring multi-critères** sur 5 dimensions pondérées
- **Détection de red flags** bloquants
- **Génération de livrables** (rapport No-Go PDF ou dossier Go complet)
- **Interface utilisateur** Streamlit intuitive

## 🏗️ Architecture

```
┌─────────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐
│  Ingestion  │ -> │  Parser  │ -> │   RAG   │ -> │  Papers  │ -> │ Scoring │ -> │    UI    │
│   (PDF)     │    │  (NLP)   │    │  (REG)  │    │  (API)   │    │ (Rules) │    │(Streamlit)│
└─────────────┘    └──────────┘    └─────────┘    └──────────┘    └─────────┘    └──────────┘
```

## 🚀 Installation

### Prérequis

- Python 3.11+
- Tesseract OCR (pour les PDF scannés)
- Clé API OpenAI

### Étapes

1. **Cloner le projet**
```bash
cd POC_AO-Scoring
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env et ajouter votre clé API OpenAI
```

5. **Initialiser la base REG**
```bash
python scripts/init_reg.py
```

## 📊 Utilisation

### Lancer l'application

```bash
streamlit run src/ui/app.py
```

L'application sera accessible sur `http://localhost:8501`

### Workflow typique

1. **Charger un AO** : Uploader un PDF d'appel d'offres
2. **Analyser** : L'extraction NLP et le scoring se lancent automatiquement
3. **Consulter** : Voir le score détaillé et les preuves REG
4. **Générer** : Créer le rapport No-Go ou le dossier Go
5. **Valider** : Le manager peut surcharger la décision si nécessaire

## 📈 Grille de Scoring

| Critère | Poids | Description |
|---------|-------|-------------|
| **Matching produit/service** | 30% | Alignement entre exigences AO et catalogue éditeur |
| **Faisabilité** | 20% | Complexité d'implémentation, contraintes calendrier |
| **Conformité** | 20% | Certifications requises, RGPD, sécurité |
| **Similarité historique** | 15% | AO similaires passés (gagnés/perdus) |
| **Rentabilité estimée** | 15% | Budget vs coût projet estimé |

### Seuils décisionnels

- **Score ≥ 70** : Go ✅
- **Score 50-69** : Go sous réserve ⚠️
- **Score < 50** : No-Go ❌

### Red flags bloquants (No-Go automatique)

- Deadline AO dépassée ou < 5 jours ouvrés
- Certification obligatoire non détenue
- Techno imposée incompatible

## 📁 Structure du projet

```
POC_AO-Scoring/
├── src/
│   ├── ingestion/       # Chargement et extraction PDF
│   ├── parser/          # Extraction NLP structurée
│   ├── rag/             # RAG avec ChromaDB
│   ├── scoring/         # Moteur de scoring
│   ├── livrables/       # Génération Word/PDF
│   └── ui/              # Interface Streamlit
├── data/
│   ├── ao_pdf/          # AO à analyser
│   ├── reg_docs/        # Documentation interne REG
│   ├── papers_mock/     # Données entreprise simulées
│   └── historique/      # AO passés
├── outputs/
│   ├── reports/         # Rapports No-Go générés
│   └── decisions/       # Dossiers Go générés
└── requirements.txt
```

## 🧪 Tests

Le POC inclut 3 AO réels de test dans `data/ao_pdf/`.

## 🔧 Technologies utilisées

- **Python 3.11** - Langage principal
- **LangChain** - Orchestration RAG et LLM
- **OpenAI GPT-4o** - Extraction NLP
- **OpenAI Embeddings** - text-embedding-3-small
- **ChromaDB** - Base vectorielle
- **PyMuPDF + Tesseract** - Extraction PDF
- **Streamlit** - Interface web
- **python-docx / ReportLab** - Génération livrables

## 📝 Limites connues

- Qualité d'extraction variable selon mise en page PDF
- REG limité (20 docs pour le POC)
- Pondérations scoring fixées manuellement
- Données Papers simulées
- Pas de gestion des versions d'AO

## 🚀 Pistes d'amélioration

- Scraping automatique plateformes AO (PLACE, AWS)
- Intégration API Papers en production
- Module ML pour ajuster pondérations scoring
- OCR GPU (EasyOCR) pour meilleure extraction
- Authentification utilisateurs et gestion rôles

## 📄 Licence

Projet POC interne - Tous droits réservés
