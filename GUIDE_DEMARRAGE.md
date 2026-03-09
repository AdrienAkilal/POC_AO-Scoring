# Guide de Démarrage Rapide

## 📋 Prérequis

1. **Python 3.11+**
   ```bash
   python --version
   ```

2. **Tesseract OCR** (optionnel, pour PDF scannés)
   - Windows: https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - macOS: `brew install tesseract`

3. **Clé API OpenAI**
   - Créer un compte sur https://platform.openai.com
   - Générer une clé API

## 🚀 Installation

### Étape 1: Créer un environnement virtuel

```bash
cd POC_AO-Scoring
python -m venv venv
```

**Activer l'environnement:**
- Windows: `venv\Scripts\activate`
- Linux/macOS: `source venv/bin/activate`

### Étape 2: Installer les dépendances

```bash
pip install -r requirements.txt
```

### Étape 3: Configurer les variables d'environnement

1. Copier le fichier d'exemple:
   ```bash
   copy .env.example .env
   ```

2. Éditer `.env` et ajouter votre clé API OpenAI:
   ```
   OPENAI_API_KEY=sk-votre-cle-api-ici
   ```

### Étape 4: Initialiser la base REG

```bash
python scripts/init_reg.py
```

Cette commande va:
- Indexer les documents dans `data/reg_docs/`
- Créer la base vectorielle ChromaDB
- Afficher les statistiques d'indexation

**Note**: Les documents d'exemple (WMS, TMS, Sécurité) sont déjà fournis dans `data/reg_docs/`.

## 🧪 Tester l'installation

```bash
python scripts/test_pipeline.py
```

Ce script teste:
- ✅ Extraction PDF
- ✅ Extraction NLP avec GPT-4o
- ✅ Recherche RAG
- ✅ API Papers (simulée)
- ✅ Moteur de scoring

**Note**: Pour tester avec un vrai PDF, placez un fichier PDF d'AO dans `data/ao_pdf/`.

## 🎨 Lancer l'application

```bash
streamlit run src/ui/app.py
```

L'application sera accessible sur: **http://localhost:8501**

## 📝 Utilisation

### 1. Analyser un AO

1. Dans la barre latérale, cliquer sur **"📤 Uploader un AO"**
2. Sélectionner un fichier PDF (CCTP, RC, etc.)
3. Cliquer sur **"🚀 Analyser"**
4. Attendre la fin de l'analyse (30 secondes à 2 minutes)

### 2. Consulter les résultats

L'application affiche:
- **Score global** sur 100
- **Décision**: Go / Go sous réserve / No-Go
- **Scores détaillés** par critère (5 dimensions)
- **Contexte extrait**: exigences, questions, red flags
- **Preuves REG**: documents internes correspondants

### 3. Générer les livrables

Dans l'onglet **"📦 Livrables"**:

- **Rapport No-Go** (PDF/Word): pour les AO refusés
- **Dossier Go** (Word/PDF): pack complet pour répondre

### 4. Personnaliser la décision

Les managers peuvent surcharger la décision automatique avec un commentaire justificatif.

## 🔧 Configuration Avancée

### Ajuster les seuils de scoring

Éditer `.env`:
```
SCORE_THRESHOLD_GO=70        # Seuil pour décision Go
SCORE_THRESHOLD_RESERVE=50   # Seuil pour Go sous réserve
```

### Modifier les pondérations

Éditer `src/config.py`:
```python
SCORING_WEIGHTS = {
    "matching_produit": 0.30,       # 30%
    "faisabilite": 0.20,             # 20%
    "conformite": 0.20,              # 20%
    "similarite_historique": 0.15,   # 15%
    "rentabilite": 0.15              # 15%
}
```

### Ajouter des documents REG

1. Placer vos PDF ou fichiers Markdown dans `data/reg_docs/`
2. Réindexer:
   ```bash
   python scripts/init_reg.py
   ```

Ou via l'interface:
- Cliquer sur **"🔄 Réindexer REG"** dans la barre latérale

### Enrichir le profil entreprise

Éditer `data/papers_mock/profil_entreprise.json`:
- Ajouter des références clients
- Mettre à jour les certifications
- Compléter les compétences

### Alimenter l'historique

Éditer `data/historique/historique_ao.json`:
- Ajouter des AO passés
- Indiquer le résultat (gagné/perdu/abandonné)
- Le système utilisera ces données pour le scoring "similarité historique"

## 📊 Structure des Données

```
data/
├── ao_pdf/          # PDF des AO à analyser
├── reg_docs/        # Documentation interne (PDF, MD)
├── papers_mock/     # Profil entreprise (JSON)
├── historique/      # AO passés (JSON)
└── chroma_db/       # Base vectorielle (auto-générée)

outputs/
├── reports/         # Rapports No-Go générés
└── decisions/       # Dossiers Go générés
```

## 🐛 Dépannage

### Erreur: "OpenAI API key not found"

➡️ Vérifiez que `.env` contient bien `OPENAI_API_KEY=sk-...`

### Erreur: "ChromaDB collection not found"

➡️ Exécutez `python scripts/init_reg.py`

### Erreur: "No module named 'src'"

➡️ Assurez-vous d'être à la racine du projet et que l'environnement virtuel est activé

### L'extraction PDF ne fonctionne pas

➡️ Pour les PDF scannés, installez Tesseract OCR

### Les résultats NLP sont de mauvaise qualité

➡️ Vérifiez:
- La qualité du PDF source
- Que vous utilisez le modèle `gpt-4o` (pas gpt-3.5-turbo)
- Que vous avez des crédits OpenAI suffisants

## 📞 Support

Pour toute question:
1. Consultez le [README.md](README.md)
2. Vérifiez les logs dans la console
3. Ouvrez une issue sur le dépôt Git

## 🎯 Prochaines Étapes

1. **Tester avec vos propres AO**: Placez des PDF réels dans `data/ao_pdf/`
2. **Enrichir le REG**: Ajoutez votre documentation produit
3. **Calibrer le scoring**: Ajustez les pondérations selon vos priorités
4. **Valider les décisions**: Comparez avec le jugement humain
5. **Alimenter l'historique**: Capitalisez sur les AO traités

Bon scoring ! 🚀
