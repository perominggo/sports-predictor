"""
Servidor Backend FastAPI para el Buscador y Predictor Deportivo RAG (Edición Winamax UI).
Sirve la interfaz web estática (static/index.html), expone el endpoint de inferencia /api/predict
y gestiona el historial persistente de enfrentamientos y pronósticos (/api/history).
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

# En Windows, asegurar ProactorEventLoop para subprocesos de Playwright
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Limpiar variables de proxy SOCKS residuales del sistema que puedan bloquear httpx/OpenAI/Gemini
for _proxy_var in ("ALL_PROXY", "all_proxy", "HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
    if os.environ.get(_proxy_var, "").startswith("socks"):
        os.environ.pop(_proxy_var, None)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from llm_agent import generate_prediction
from scraper import fetch_sports_data

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
HISTORY_FILE = BASE_DIR / "history_store.json"

load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

app = FastAPI(
    title="Sports Predictor RAG API — Winamax Edition",
    description="Buscador y predictor deportivo Open-Source con Playwright, BeautifulSoup4, LLM RAG e historial persistente.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


class PredictRequest(BaseModel):
    sport: str = Field(..., examples=["mma"], description="Deporte: mma, football, basketball o tennis")
    event: str = Field(..., min_length=3, examples=["Ilia Topuria vs Max Holloway"])


class PredictResponse(BaseModel):
    id: str
    timestamp: str
    status: str
    sport: str
    event: str
    llm_provider: str
    sources_queried: List[str]
    scraped_data: Dict[str, Any]
    prediction: str


def _load_history() -> List[Dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_history(items: List[Dict[str, Any]]) -> None:
    try:
        HISTORY_FILE.write_text(
            json.dumps(items[:100], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception as err:
        print(f"[WARN] No se pudo guardar history_store.json: {err}")


@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Archivo static/index.html no encontrado.")
    return FileResponse(index_path)


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
    openai_configured = bool(os.getenv("OPENAI_API_KEY", "").strip())
    gemini_configured = bool(os.getenv("GEMINI_API_KEY", "").strip())
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    if not openai_configured and not gemini_configured:
        active_llm = "quant-rag-local"
    elif provider == "gemini" and gemini_configured:
        active_llm = f"gemini ({os.getenv('GEMINI_MODEL', 'gemini-3.8-flash')})"
    elif openai_configured:
        active_llm = f"openai ({os.getenv('OPENAI_MODEL', 'gpt-4o-mini')})"
    else:
        active_llm = "gemini"

    return {
        "status": "ok",
        "llm_provider": active_llm,
    }


@app.get("/api/history")
async def get_history() -> Dict[str, Any]:
    return {"items": _load_history()}


@app.delete("/api/history")
async def clear_history() -> Dict[str, str]:
    _save_history([])
    return {"status": "cleared"}


@app.delete("/api/history/{item_id}")
async def delete_history_item(item_id: str) -> Dict[str, Any]:
    history = _load_history()
    filtered = [item for item in history if item.get("id") != item_id]
    _save_history(filtered)
    return {"status": "deleted", "remaining": len(filtered)}


@app.post("/api/predict", response_model=PredictResponse)
async def predict_sport_event(payload: PredictRequest) -> PredictResponse:
    try:
        scraped_data = await fetch_sports_data(payload.sport, payload.event)
        prediction_text, provider_used = await asyncio.to_thread(
            generate_prediction,
            payload.sport,
            payload.event,
            scraped_data,
        )
        item_id = str(uuid.uuid4())[:8]
        now_iso = datetime.now(timezone.utc).isoformat()

        response_obj = PredictResponse(
            id=item_id,
            timestamp=now_iso,
            status="success",
            sport=payload.sport,
            event=payload.event,
            llm_provider=provider_used,
            sources_queried=scraped_data.get("sources_queried", []),
            scraped_data=scraped_data,
            prediction=prediction_text,
        )

        # Guardar automáticamente en el historial persistente
        history = _load_history()
        history.insert(0, response_obj.model_dump())
        _save_history(history)

        return response_obj
    except Exception as exc:
        err_msg = str(exc).strip() or repr(exc)
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la predicción para '{payload.event}': {err_msg}",
        ) from exc


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
