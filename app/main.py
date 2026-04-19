import os
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .crops import get_crop, list_crops
from .explain import build_explanation
from .gpt import enrich_with_gpt
from .model import load_model
from .predict import build_predictions
from .weather import fetch_elevation

load_dotenv()

SERVER_OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip() or None
SERVER_OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"

app = FastAPI(
    title="Agro-Predict API",
    description="AI-powered planting-date recommendations for Western Balkans farmers. Adria Future Hackathon.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_MODEL = None


@app.on_event("startup")
async def _startup() -> None:
    global _MODEL
    _MODEL = load_model()


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "model_loaded": _MODEL is not None,
        "model_auc": _MODEL.metrics.get("auc") if _MODEL else None,
        "gpt_configured": SERVER_OPENAI_KEY is not None,
        "gpt_model": SERVER_OPENAI_MODEL if SERVER_OPENAI_KEY else None,
    }


@app.get("/crops")
async def crops_endpoint() -> dict:
    return {"crops": list_crops()}


def _parse_crops(crop: str) -> list[str]:
    ids = [c.strip().lower() for c in crop.split(",") if c.strip()]
    if not ids:
        raise HTTPException(status_code=400, detail="At least one crop id required")
    for cid in ids:
        try:
            get_crop(cid)
        except KeyError as e:
            raise HTTPException(status_code=400, detail=str(e))
    return ids


@app.get("/predict")
async def predict_endpoint(
    lat: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop: str = Query(
        ...,
        description="One or more crop ids, comma-separated (e.g. 'corn' or 'corn,wheat,potato'). See /crops.",
    ),
    elevation: float | None = Query(
        None, description="Optional elevation in meters; auto-fetched if omitted"
    ),
    lang: Literal["en", "bs"] = Query("en"),
    use_gpt: bool = Query(
        True,
        description="Use GPT enrichment when backend has OPENAI_API_KEY set. Default on.",
    ),
    gpt_model: Optional[str] = Query(
        None,
        description="Override server-side OPENAI_MODEL for this request",
    ),
    x_openai_key: Optional[str] = Header(
        None,
        alias="X-OpenAI-Key",
        description="Optional per-request OpenAI API key override (dev/testing only)",
    ),
) -> dict:
    crop_ids = _parse_crops(crop)

    if elevation is None:
        try:
            elevation = await fetch_elevation(lat, lon)
        except Exception:
            elevation = 0.0

    try:
        result = await build_predictions(
            lat=lat, lon=lon, crop_ids=crop_ids, elevation=elevation, model=_MODEL
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream data error: {e}")

    active_key = x_openai_key or (SERVER_OPENAI_KEY if use_gpt else None)
    active_model = gpt_model or SERVER_OPENAI_MODEL

    for pred in result["predictions"]:
        pred["explanation"] = build_explanation(
            {**pred, "location": result["location"]}, lang=lang
        )
        if active_key:
            gpt_bullets = await enrich_with_gpt(
                {**pred, "location": result["location"]},
                api_key=active_key,
                lang=lang,
                model=active_model,
            )
            if gpt_bullets:
                pred["gpt_explanation"] = gpt_bullets
                pred["gpt_model"] = active_model

    result["gpt_enabled"] = bool(active_key)
    return result
