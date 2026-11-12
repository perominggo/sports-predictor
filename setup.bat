@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Sports Predictor RAG - Setup para Windows
echo ============================================================

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    echo Instala Python 3.10+ desde https://www.python.org/
    exit /b 1
)

echo [1/4] Creando entorno virtual en .venv...
python -m venv .venv
call .venv\Scripts\activate.bat

echo [2/4] Actualizando pip e instalando dependencias de requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [3/4] Instalando navegadores de Playwright (Chromium)...
playwright install chromium

if not exist .env (
    echo [4/4] Creando archivo .env a partir de .env.example...
    copy .env.example .env >nul
    echo [AVISO] Recuerda editar el archivo .env y anadir tu OPENAI_API_KEY o GEMINI_API_KEY.
) else (
    echo [4/4] El archivo .env ya existe. Omitiendo copia.
)

echo ============================================================
echo   Instalacion completada con exito.
echo   Para iniciar el servidor ejecuta:
echo     call .venv\Scripts\activate
echo     uvicorn main:app --host 0.0.0.0 --port 8000 --reload
echo ============================================================
pause
