"""
Servidor Backend FastAPI para el Buscador y Predictor Deportivo RAG.
Sirve la interfaz web estática (static/index.html) y expone el endpoint de inferencia /api/predict.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from llm_agent import generate_prediction
from scraper import fetch_sports_data

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Sports Predictor RAG API",
    description="Buscador y predictor deportivo Open-Source con Playwright, BeautifulSoup4 y LLM RAG (OpenAI / Gemini).",
    version="1.0.0",
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
    status: str
    sport: str
    event: str
    llm_provider: str
    sources_queried: List[str]
    scraped_data: Dict[str, Any]
    prediction: str


@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Archivo static/index.html no encontrado.")
    return FileResponse(index_path)


@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    openai_configured = bool(os.getenv("OPENAI_API_KEY", "").strip())
    gemini_configured = bool(os.getenv("GEMINI_API_KEY", "").strip())
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    if not openai_configured and not gemini_configured:
        active_llm = "demo-mode (configure .env)"
    elif provider == "gemini" and gemini_configured:
        active_llm = "gemini"
    elif openai_configured:
        active_llm = "openai"
    else:
        active_llm = "gemini"

    return {
        "status": "ok",
        "llm_provider": active_llm,
    }


@app.post("/api/predict", response_model=PredictResponse)
async def predict_sport_event(payload: PredictRequest) -> PredictResponse:
    try:
        scraped_data = await fetch_sports_data(payload.sport, payload.event)
        prediction_text, provider_used = generate_prediction(
            sport=payload.sport,
            event=payload.event,
            scraped_data=scraped_data,
        )
        return PredictResponse(
            status="success",
            sport=payload.sport,
            event=payload.event,
            llm_provider=provider_used,
            sources_queried=scraped_data.get("sources_queried", []),
            scraped_data=scraped_data,
            prediction=prediction_text,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la predicción para '{payload.event}': {str(exc)}",
        ) from exc


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
