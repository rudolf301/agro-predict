"""Optional GPT-4o enrichment of predictions. Activates only when an OpenAI key is supplied per-request.

This keeps the ML pipeline the source of truth (frost probabilities, traffic light, dates) and uses GPT
only for a natural-language layer on top — so predictions stay reproducible without a key.
"""
import json
from typing import Optional

import httpx

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"


SYSTEM_PROMPT = """You are an agricultural advisor for Western Balkans / Central European farmers.
You receive a JSON prediction from an ML model (frost probability, historical frost rate, optimal sowing date,
14-day forecast). You generate 3-5 concise bullets in the requested language that:
- Explain WHY the recommended sowing date is optimal (reference historical frost rate + forecast)
- Flag the single most important risk in the next 14 days, if any
- Give one concrete action the farmer can take

Rules:
- Bullets must be 1 sentence each, no headers, no markdown, no emojis
- Ground every claim in the numbers provided — do not invent facts
- Stay under 25 words per bullet
- Output pure JSON: {"bullets": ["...", "..."]}
"""


async def enrich_with_gpt(
    prediction: dict,
    api_key: str,
    lang: str = "en",
    model: str = DEFAULT_MODEL,
) -> Optional[list[str]]:
    """Call GPT-4o (or similar). Returns a list of bullets, or None on any failure."""
    if not api_key or not api_key.startswith("sk-"):
        return None

    lang_name = "Bosnian/Croatian/Serbian" if lang == "bs" else "English"
    user_payload = {
        "crop": prediction.get("crop"),
        "location": prediction.get("location", {}),
        "recommended_planting": prediction.get("recommended_planting"),
        "risk": prediction.get("risk"),
        "forecast_14d_summary": _summarize_forecast(prediction.get("forecast_14d", [])),
        "confidence": prediction.get("confidence"),
        "response_language": lang_name,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                OPENAI_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": (
                                f"Generate bullets in {lang_name}. "
                                f"Prediction data: {json.dumps(user_payload, ensure_ascii=False)}"
                            ),
                        },
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.3,
                    "max_tokens": 400,
                },
            )
            if r.status_code != 200:
                return None
            data = r.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            bullets = parsed.get("bullets")
            if isinstance(bullets, list) and all(isinstance(b, str) for b in bullets):
                return bullets
            return None
    except Exception:
        return None


def _summarize_forecast(daily: list[dict]) -> dict:
    if not daily:
        return {}
    mins = [d["temp_min_c"] for d in daily]
    maxes = [d["temp_max_c"] for d in daily]
    precips = [d["precipitation_mm"] for d in daily]
    frost_days = sum(1 for d in daily if d.get("crop_frost_risk"))
    return {
        "days": len(daily),
        "temp_min_range": [min(mins), max(mins)],
        "temp_max_range": [min(maxes), max(maxes)],
        "total_precipitation_mm": round(sum(precips), 1),
        "crop_frost_days": frost_days,
    }
