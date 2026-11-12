#!/usr/bin/env bash
set -euo pipefail

# Limpiar posibles variables de proxy SOCKS del entorno que bloquean a pip
unset ALL_PROXY all_proxy HTTP_PROXY http_proxy HTTPS_PROXY https_proxy

echo "============================================================"
echo "  Sports Predictor RAG - Setup para Linux / macOS"
echo "============================================================"

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no está instalado. Instala Python 3.10 o superior."
    exit 1
fi

echo "[1/4] Creando entorno virtual en .venv..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/4] Actualizando pip e instalando dependencias de requirements.txt..."
python -m pip install --upgrade pip --proxy ""
python -m pip install -r requirements.txt --proxy ""

echo "[3/4] Instalando navegadores de Playwright (Chromium)..."
python -m playwright install chromium

if [ ! -f .env ]; then
    echo "[4/4] Creando archivo .env a partir de .env.example..."
    cp .env.example .env
    echo "[AVISO] Recuerda editar el archivo .env y añadir tu OPENAI_API_KEY o GEMINI_API_KEY."
else
    echo "[4/4] El archivo .env ya existe. Omitiendo copia."
fi

echo "============================================================"
echo "  Instalación completada con éxito."
echo "  Para iniciar el servidor ejecuta:"
echo "    source .venv/bin/activate"
echo "    python main.py"
echo "============================================================"
