@echo off
echo ========================================
echo Lancement POC AO-Scoring
echo ========================================
echo.

REM Vérifier que venv existe
if exist venv\Scripts\activate.bat (
    echo Activation de l'environnement virtuel...
    call venv\Scripts\activate.bat
)

REM Vérifier que .env existe
if not exist .env (
    echo.
    echo ATTENTION : Le fichier .env n'existe pas !
    echo Créez-le en copiant .env.example et ajoutez votre clé OpenAI
    pause
    exit /b 1
)

echo.
echo Lancement de Streamlit...
echo L'application va s'ouvrir dans votre navigateur
echo Appuyez sur Ctrl+C pour arrêter l'application
echo.

streamlit run src\ui\app.py

pause
