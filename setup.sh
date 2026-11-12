#!/usr/bin/env bash
set -euo pipefail

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
pip install --upgrade pip
pip install -r requirements.txt

echo "[3/4] Instalando navegadores de Playwright (Chromium)..."
playwright install chromium

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
echo "    uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo "============================================================"
