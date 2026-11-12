@echo off
setlocal enabledelayedexpansion

rem Limpiar posibles variables de proxy SOCKS del entorno que bloquean a pip
set ALL_PROXY=
set all_proxy=
set HTTP_PROXY=
set http_proxy=
set HTTPS_PROXY=
set https_proxy=
set NO_PROXY=*
set no_proxy=*

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
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat

echo [2/4] Actualizando pip e instalando dependencias de requirements.txt...
python -m pip install --upgrade pip --proxy ""
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al actualizar pip.
    exit /b 1
)

python -m pip install -r requirements.txt --proxy ""
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al instalar requirements.txt.
    exit /b 1
)

echo [3/4] Instalando navegadores de Playwright (Chromium)...
python -m playwright install chromium

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
echo     .\.venv\Scripts\python.exe main.py
echo ============================================================
pause
