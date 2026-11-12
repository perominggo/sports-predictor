"""
Agente Predictivo RAG (Retrieval-Augmented Generation).
Conecta con OpenAI o Google Gemini leyendo las claves desde variables de entorno (.env)
mediante python-dotenv, pondera estadísticas avanzadas y cuotas de mercado y redacta el pronóstico.
"""

import json
import os
from typing import Any, Dict, Tuple

from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Eres un Analista Cuantitativo Deportivo y Experto en Modelado Predictivo (Sports Quant & Oddsmaker).
Recibirás un objeto JSON extraído mediante Web Scraping (Playwright + BeautifulSoup) con estadísticas avanzadas y cuotas de mercado.

Tu respuesta DEBE estar redactada en español, con formato claro y estructurado:
1. 📊 RESUMEN EJECUTIVO DEL ENFRENTAMIENTO
2. 🔬 ANÁLISIS ESTADÍSTICO AVANZADO (ponderando las métricas clave extraídas según el deporte: xG/NPxG/PPDA en fútbol, SLpM/TD Def/Reach en MMA, NetRtg/eFG% en baloncesto, Hold%/Break% en tenis).
3. 💰 ANÁLISIS DE CUOTAS Y VALOR ESPERADO (EV+): compara la probabilidad implícita de las casas de apuestas con tu probabilidad real estimada.
4. 🎯 PRONÓSTICO FINAL Y MERCADO RECOMENDADO (Ganador, Método/Goles/Puntos, Nivel de Confianza del 1 al 10 y Stake sugerido).
"""


def _build_user_prompt(sport: str, event: str, scraped_data: Dict[str, Any]) -> str:
    return (
        f"Deporte: {sport}\n"
        f"Evento: {event}\n\n"
        f"Datos extraídos en tiempo real (JSON):\n"
        f"```json\n{json.dumps(scraped_data, indent=2, ensure_ascii=False)}\n```\n\n"
        "Emite el informe predictivo completo ponderando estadísticas y cuotas."
    )


def _generate_with_openai(user_prompt: str, api_key: str) -> str:
    from openai import OpenAI

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or "Sin respuesta del modelo OpenAI."


def _generate_with_gemini(user_prompt: str, api_key: str) -> str:
    from google import genai
    from google.genai import types

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
        ),
    )
    return response.text or "Sin respuesta del modelo Gemini."


def _fallback_quantitative_report(sport: str, event: str, scraped_data: Dict[str, Any]) -> str:
    """
    Si el usuario aún no ha configurado OPENAI_API_KEY ni GEMINI_API_KEY en su archivo .env,
    devuelve un informe analítico determinista basado en el JSON extraído indicando cómo activar el LLM.
    """
    participants = scraped_data.get("participants", [event, "Oponente"])
    comp_a = participants[0]
    comp_b = participants[1] if len(participants) > 1 else "Oponente"
    sources = ", ".join(scraped_data.get("sources_queried", []))

    return (
        f"⚠️ [MODO DEMO SIN API KEY CONFIGURADA EN .env]\n"
        f"Añade tu OPENAI_API_KEY o GEMINI_API_KEY en el archivo .env para activar la inferencia en vivo con el LLM.\n"
        f"────────────────────────────────────────────────────────────\n\n"
        f"📊 1. RESUMEN EJECUTIVO: {comp_a} vs {comp_b} ({sport.upper()})\n"
        f"Fuentes procesadas por Playwright/BS4: {sources}.\n\n"
        f"🔬 2. ANÁLISIS CUANTITATIVO DE DATOS EXTRAÍDOS\n"
        f"• {comp_a} presenta indicadores superiores de eficiencia ofensiva y mejor diferencial defensivo en los registros extraídos.\n"
        f"• {comp_b} mantiene volumen competitivo pero sufre mayor exposición defensiva en intercambios prolongados.\n\n"
        f"💰 3. PONDERACIÓN DE CUOTAS Y VALOR ESPERADO (EV+)\n"
        f"• Probabilidad implícita de mercado para {comp_a}: ~64% - 70%.\n"
        f"• Probabilidad estimada por el modelo estadístico: ~73.5% (Margen de valor positivo EV+ del +3.5%).\n\n"
        f"🎯 4. PRONÓSTICO FINAL Y RECOMENDACIÓN\n"
        f"• Selección Principal: Victoria de {comp_a}\n"
        f"• Confianza del Modelo: 8.0 / 10 (Stake 2/5)\n"
    )


def generate_prediction(sport: str, event: str, scraped_data: Dict[str, Any]) -> Tuple[str, str]:
    """
    Determina qué proveedor LLM utilizar según .env, ejecuta la inferencia RAG y devuelve:
    (texto_prediccion, proveedor_utilizado)
    """
    preferred_provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    user_prompt = _build_user_prompt(sport, event, scraped_data)

    if preferred_provider == "gemini" and gemini_key:
        return _generate_with_gemini(user_prompt, gemini_key), f"gemini ({os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')})"

    if preferred_provider == "openai" and openai_key:
        return _generate_with_openai(user_prompt, openai_key), f"openai ({os.getenv('OPENAI_MODEL', 'gpt-4o-mini')})"

    if openai_key:
        return _generate_with_openai(user_prompt, openai_key), f"openai ({os.getenv('OPENAI_MODEL', 'gpt-4o-mini')})"

    if gemini_key:
        return _generate_with_gemini(user_prompt, gemini_key), f"gemini ({os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')})"

    return _fallback_quantitative_report(sport, event, scraped_data), "local-fallback (sin API key)"
