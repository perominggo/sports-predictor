# 🏟️ Sports Predictor RAG (Open-Source Sports Analytics & Betting Intelligence)

Sistema de predicción deportiva impulsado por **Web Scraping (Playwright + BeautifulSoup4)** y **Modelos de Lenguaje (OpenAI / Google Gemini)** bajo arquitectura RAG (Retrieval-Augmented Generation). Diseñado con interfaz web minimalista estilo terminal en modo oscuro y preparado para desplegarse con un solo comando mediante **Docker** o scripts nativos.

---

## 🏗️ Arquitectura y Flujo de Ejecución

1. **Frontend (`static/index.html`)**: Interfaz oscura estilo terminal en HTML5, CSS3 y Vanilla JS. El usuario selecciona el deporte (`Fútbol`, `Baloncesto`, `Tenis`, `MMA / UFC`) e introduce el evento (ej. `"Ilia Topuria vs Max Holloway"` o `"Real Madrid vs Barcelona"`).
2. **Backend API (`main.py`)**: Servidor asíncrono con **FastAPI** que sirve la interfaz estática y expone el endpoint `POST /api/predict`.
3. **Módulo de Extracción (`scraper.py`)**: Motor híbrido con **Playwright** (headless Chromium con configuración stealth para evasión de Cloudflare) y **BeautifulSoup4** para extraer métricas avanzadas y cuotas de mercado:
   - **Fútbol**: FBref, Understat, SofaScore, FotMob, Flashscore, OddsPortal.
   - **Baloncesto**: Basketball-Reference, NBA.com/Stats, Flashscore, OddsPortal.
   - **Tenis**: Tennis Abstract, ATP / WTA Tour, TennisExplorer, Flashscore.
   - **MMA / UFC**: UFCStats, Tapology, Sherdog, BestFightOdds.
4. **Cerebro Predictivo RAG (`llm_agent.py`)**: Inyecta el JSON estadístico y las cuotas extraídas en un prompt estructurado hacia **OpenAI (`gpt-4o-mini` / `gpt-4o`)** o **Google Gemini (`gemini-2.5-flash`)** para calcular probabilidades implícitas, detectar valor esperado (*Expected Value - EV+*) y emitir el pronóstico detallado.

---

## 📁 Estructura del Proyecto

```text
sports-predictor/
├── static/
│   └── index.html         # UI completa (HTML5 + CSS Terminal Dark + Vanilla JS)
├── main.py                # Servidor FastAPI y endpoints REST
├── scraper.py             # Extracción de datos con Playwright y BeautifulSoup4
├── llm_agent.py           # Agente RAG compatible con OpenAI y Google Gemini
├── requirements.txt       # Dependencias de Python
├── .env.example           # Plantilla de variables de entorno (sin claves reales)
├── Dockerfile             # Imagen oficial de Playwright + Python + FastAPI
├── docker-compose.yml     # Orquestación lista para levantar con un comando
├── setup.sh               # Instalador automatizado para Linux / macOS
├── setup.bat              # Instalador automatizado para Windows
└── README.md              # Documentación del proyecto
```

---

## 🚀 Instalación y Uso Rápido

### Paso 1: Configurar Variables de Entorno

Clona el repositorio y crea tu archivo `.env` a partir de la plantilla `.env.example`:

```bash
git clone https://github.com/perominggo/sports-predictor.git
cd sports-predictor
cp .env.example .env
```

Edita el archivo `.env` y añade tu clave de API de **OpenAI** o de **Google Gemini** (el sistema detectará automáticamente cuál has configurado o usará el proveedor indicado en `LLM_PROVIDER`):

```ini
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-tu-clave-aqui
GEMINI_API_KEY=
```

---

### Opción A: Despliegue con Docker Compose (Recomendado)

No necesitas instalar Python ni navegadores en tu máquina anfitriona:

```bash
docker compose up --build
```

Abre tu navegador en: **`http://localhost:8000`**

---

### Opción B: Instalación Local en Linux / macOS

Ejecuta el script de instalación automatizada (crea el entorno virtual `.venv`, instala paquetes de `requirements.txt` y descarga los binarios de Chromium para Playwright):

```bash
chmod +x setup.sh
./setup.sh
```

Para iniciar el servidor:

```bash
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Opción C: Instalación Local en Windows

Haz doble clic en `setup.bat` o ejecútalo desde CMD / PowerShell:

```bat
.\setup.bat
```

Para iniciar el servidor:

```bat
call .venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔌 API Reference

### `POST /api/predict`

**Request Body:**
```json
{
  "sport": "mma",
  "event": "Ilia Topuria vs Max Holloway"
}
```

**Response Body:**
```json
{
  "status": "success",
  "sport": "mma",
  "event": "Ilia Topuria vs Max Holloway",
  "sources_queried": ["UFCStats", "BestFightOdds", "Tapology", "Sherdog"],
  "scraped_data": { ... },
  "prediction": "..."
}
```

---

## 🛡️ Seguridad y Buenas Prácticas

- **Nunca subas tu archivo `.env` a GitHub.** Asegúrate de incluir `.env` y `.venv/` en tu `.gitignore`.
- Todas las credenciales son leídas dinámicamente en tiempo de ejecución mediante `python-dotenv`.

## 📄 Licencia

Distribuido bajo la licencia **MIT**. Libre para uso personal, educativo y comercial.
