@echo off
echo ========================================
echo Installation POC AO-Scoring (Windows)
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR : Python n'est pas installé ou pas dans le PATH
    echo Installez Python 3.11+ depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Python détecté
python --version

echo.
echo [2/5] Mise à jour de pip...
python -m pip install --upgrade pip

echo.
echo [3/5] Installation des dépendances (2-3 minutes)...
pip install -r requirements_simple.txt

if errorlevel 1 (
    echo.
    echo ERREUR lors de l'installation des dépendances
    echo Vérifiez les messages d'erreur ci-dessus
    pause
    exit /b 1
)

echo.
echo [4/5] Configuration de l'environnement...
if not exist .env (
    copy .env.example .env
    echo Fichier .env créé
    echo.
    echo IMPORTANT : Editez le fichier .env et ajoutez votre clé API OpenAI !
    echo OPENAI_API_KEY=sk-votre-cle-ici
) else (
    echo Fichier .env déjà existant
)

echo.
echo [5/5] Création des dossiers...
if not exist data\ao_pdf mkdir data\ao_pdf
if not exist data\reg_docs mkdir data\reg_docs
if not exist data\papers_mock mkdir data\papers_mock
if not exist data\historique mkdir data\historique
if not exist data\chroma_db mkdir data\chroma_db
if not exist outputs\reports mkdir outputs\reports
if not exist outputs\decisions mkdir outputs\decisions

echo.
echo ========================================
echo Installation terminée avec succès !
echo ========================================
echo.
echo Prochaines étapes :
echo.
echo 1. Editez le fichier .env et ajoutez votre clé OpenAI
echo    OPENAI_API_KEY=sk-votre-cle-ici
echo.
echo 2. Initialisez la base REG :
echo    python scripts\init_reg.py
echo.
echo 3. Lancez l'application :
echo    streamlit run src\ui\app.py
echo.
pause
