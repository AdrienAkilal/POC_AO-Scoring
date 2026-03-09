# 🪟 Installation Simplifiée pour Windows

## ✅ Solution Rapide (Sans Compilation)

Cette version utilise **FAISS** au lieu de ChromaDB pour éviter les problèmes de compilation sur Windows.

### Étape 1 : Nettoyer l'environnement

```bash
# Si vous avez déjà un venv, le supprimer
rmdir /s venv

# Créer un nouvel environnement virtuel
python -m venv venv

# Activer l'environnement
venv\Scripts\activate
```

### Étape 2 : Mettre à jour pip

```bash
python -m pip install --upgrade pip
```

### Étape 3 : Installer les dépendances

```bash
pip install -r requirements_simple.txt
```

Cette commande va installer :
- ✅ LangChain + OpenAI
- ✅ **FAISS** (base vectorielle, pas de compilation)
- ✅ PyMuPDF (extraction PDF)
- ✅ Streamlit (interface)
- ✅ python-docx + reportlab (génération documents)

**Durée** : 2-3 minutes

### Étape 4 : Configurer la clé OpenAI

1. Copier le fichier d'exemple :
   ```bash
   copy .env.example .env
   ```

2. Ouvrir `.env` avec un éditeur de texte

3. Remplacer `your_openai_api_key_here` par votre vraie clé :
   ```
   OPENAI_API_KEY=sk-votre-clé-ici
   ```

4. Sauvegarder le fichier

### Étape 5 : Initialiser la base REG

```bash
python scripts\init_reg.py
```

Vous devriez voir :
```
==============================================================
INITIALISATION DE LA BASE REG
==============================================================

Documents trouvés dans ...\data\reg_docs:
  - Fichiers PDF: 0
  - Fichiers Markdown: 3

Initialisation du REG Manager...
Indexation des documents...

✅ Indexation terminée avec succès!
```

### Étape 6 : Lancer l'application

```bash
streamlit run src\ui\app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse :
**http://localhost:8501**

## 🧪 Tester l'Installation

```bash
python scripts\test_pipeline.py
```

## ❌ En Cas de Problème

### Erreur : "No module named 'faiss'"

➡️ Réinstaller FAISS :
```bash
pip install faiss-cpu==1.7.4
```

### Erreur : "No module named 'openai'"

➡️ Installer OpenAI :
```bash
pip install openai langchain-openai
```

### Erreur : "OPENAI_API_KEY not found"

➡️ Vérifier que le fichier `.env` contient bien :
```
OPENAI_API_KEY=sk-...
```

### L'application ne se lance pas

➡️ Vérifier que l'environnement virtuel est activé :
```bash
# Vous devriez voir (venv) au début de la ligne de commande
(venv) PS C:\Users\...\POC_AO-Scoring>
```

Si ce n'est pas le cas :
```bash
venv\Scripts\activate
```

## 📊 Différences FAISS vs ChromaDB

| Caractéristique | FAISS | ChromaDB |
|----------------|-------|----------|
| **Installation Windows** | ✅ Simple | ❌ Nécessite compilation |
| **Performance** | ⚡ Très rapide | ⚡ Rapide |
| **Persistance** | ✅ Fichiers locaux | ✅ Base de données |
| **Filtres métadonnées** | ⚠️ Limités | ✅ Avancés |

Pour ce POC, **FAISS est parfait** et même plus rapide !

## 🎯 Prochaines Étapes

Une fois l'application lancée :

1. **Uploader un PDF d'AO** dans la sidebar
2. **Cliquer "Analyser"**
3. **Consulter** le score et les détails
4. **Générer** les livrables (rapport No-Go ou dossier Go)

## 💡 Conseils

- Les **3 documents REG d'exemple** sont déjà fournis (WMS, TMS, Sécurité)
- Vous pouvez **ajouter vos propres documents** dans `data\reg_docs\`
- Après ajout, **réindexer** avec `python scripts\init_reg.py`

Bon scoring ! 🚀
