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

rem Seleccionar Python 3.13/3.12 si esta disponible para usar ruedas precompiladas (.whl) sin requerir Visual C++
set PY_CMD=python
py -3.13 --version >nul 2>nul
if %errorlevel% equ 0 (
    set PY_CMD=py -3.13
) else (
    py -3.12 --version >nul 2>nul
    if !errorlevel! equ 0 (
        set PY_CMD=py -3.12
    )
)

echo Usando interprete: %PY_CMD%

rem Si existe un .venv incompleto sin uvicorn/playwright, recrearlo con la version compatible
if exist .venv (
    if not exist .venv\Scripts\uvicorn.exe (
        echo Eliminando entorno virtual previo incompleto...
        rmdir /s /q .venv
    )
)

echo [1/4] Creando entorno virtual en .venv...
if not exist .venv (
    %PY_CMD% -m venv .venv
)
call .venv\Scripts\activate.bat

echo [2/4] Actualizando pip e instalando dependencias precompiladas de requirements.txt...
python -m pip install --upgrade pip --proxy ""
python -m pip install --prefer-binary -r requirements.txt --proxy ""
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
