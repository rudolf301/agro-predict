from datetime import date, timedelta
from typing import Optional

import pandas as pd

from .crops import get_crop
from .model import FrostModel
from .weather import add_features, fetch_forecast, fetch_historical


def _traffic_light(risk_score: float) -> str:
    if risk_score < 0.15:
        return "green"
    if risk_score < 0.35:
        return "yellow"
    return "red"


def _risk_label(color: str) -> str:
    return {
        "green": "Low risk \u2014 safe to plant",
        "yellow": "Moderate risk \u2014 monitor weather closely",
        "red": "High risk \u2014 delay planting",
    }[color]


async def _prepare_location_data(
    lat: float, lon: float, elevation: float, model: Optional[FrostModel]
) -> tuple[pd.DataFrame, pd.DataFrame]:
    historical = await fetch_historical(lat, lon)
    historical = add_features(historical)

    forecast = await fetch_forecast(lat, lon)
    forecast = add_features(forecast)
    forecast["elevation"] = elevation
    forecast["latitude"] = lat

    if model is not None:
        forecast["frost_probability"] = model.predict_proba(forecast)
    else:
        forecast["frost_probability"] = (
            forecast["temperature_2m_min"] <= 0.0
        ).astype(float)

    return historical, forecast


def _build_single_crop_prediction(
    crop_id: str,
    historical: pd.DataFrame,
    forecast: pd.DataFrame,
    model: Optional[FrostModel],
    elevation: float,
    latitude: float,
) -> dict:
    crop = get_crop(crop_id)
    frost_threshold = crop["frost_risk_threshold_c"]

    f = forecast.copy()
    f["frost_risk_crop"] = (f["temperature_2m_min"] <= frost_threshold).astype(int)

    next_14 = f.head(14).copy()
    avg_frost_prob = float(next_14["frost_probability"].mean())
    max_frost_prob = float(next_14["frost_probability"].max())
    crop_risk_days = int(next_14["frost_risk_crop"].sum())

    optimal = _recommend_planting_window(
        historical=historical, forecast=next_14, crop=crop
    )

    color = _traffic_light(
        risk_score=0.6 * avg_frost_prob + 0.4 * (crop_risk_days / 14)
    )

    daily = [
        {
            "date": row["time"].date().isoformat(),
            "temp_min_c": round(float(row["temperature_2m_min"]), 1),
            "temp_max_c": round(float(row["temperature_2m_max"]), 1),
            "precipitation_mm": round(float(row["precipitation_sum"]), 1),
            "frost_probability": round(float(row["frost_probability"]), 3),
            "crop_frost_risk": bool(row["frost_risk_crop"]),
        }
        for _, row in next_14.iterrows()
    ]

    confidence = _confidence_score(model, avg_frost_prob, len(historical))

    return {
        "crop": {
            "id": crop_id,
            "name_en": crop["name_en"],
            "name_bs": crop["name_bs"],
            "frost_tolerance": crop["frost_tolerance"],
            "growing_days": crop["growing_days"],
        },
        "recommended_planting": optimal,
        "risk": {
            "traffic_light": color,
            "label": _risk_label(color),
            "avg_frost_probability_14d": round(avg_frost_prob, 3),
            "max_frost_probability_14d": round(max_frost_prob, 3),
            "crop_frost_risk_days_14d": crop_risk_days,
        },
        "forecast_14d": daily,
        "confidence": confidence,
    }


async def build_predictions(
    lat: float,
    lon: float,
    crop_ids: list[str],
    elevation: float,
    model: Optional[FrostModel],
) -> dict:
    historical, forecast = await _prepare_location_data(lat, lon, elevation, model)

    predictions = [
        _build_single_crop_prediction(
            crop_id=cid,
            historical=historical,
            forecast=forecast,
            model=model,
            elevation=elevation,
            latitude=lat,
        )
        for cid in crop_ids
    ]

    return {
        "location": {
            "latitude": lat,
            "longitude": lon,
            "elevation_m": round(elevation, 1),
        },
        "predictions": predictions,
    }


def _recommend_planting_window(
    historical: pd.DataFrame, forecast: pd.DataFrame, crop: dict
) -> dict:
    today = date.today()
    year = today.year

    start_md = crop["planting_window_start"]
    end_md = crop["planting_window_end"]

    start_date = _md_to_date(start_md, year)
    end_date = _md_to_date(end_md, year)
    if end_date < start_date:
        end_date = _md_to_date(end_md, year + 1)

    if today > end_date:
        start_date = _md_to_date(start_md, year + 1)
        end_date = _md_to_date(end_md, year + 1)

    window_start = max(start_date, today)

    daily_frost_rate = _historical_frost_rate_by_doy(
        historical, threshold_c=crop["frost_risk_threshold_c"]
    )

    candidates = []
    cursor = window_start
    while cursor <= end_date:
        doy = cursor.timetuple().tm_yday
        hist_risk = daily_frost_rate.get(doy, 0.0)

        forecast_row = forecast[forecast["time"].dt.date == cursor]
        if len(forecast_row):
            forecast_risk = float(forecast_row["frost_probability"].iloc[0])
        else:
            forecast_risk = hist_risk

        combined = 0.6 * forecast_risk + 0.4 * hist_risk
        candidates.append((cursor, combined, hist_risk, forecast_risk))
        cursor += timedelta(days=1)

    if not candidates:
        return {
            "date": None,
            "confidence": 0.0,
            "historical_frost_rate": 0.0,
            "reason": "Planting window has passed for current year",
        }

    best = min(candidates, key=lambda c: c[1])
    best_date, combined_risk, hist_risk, forecast_risk = best

    return {
        "date": best_date.isoformat(),
        "confidence": round(1.0 - combined_risk, 3),
        "historical_frost_rate": round(hist_risk, 3),
        "forecast_frost_probability": round(forecast_risk, 3),
        "window_start": start_date.isoformat(),
        "window_end": end_date.isoformat(),
    }


def _md_to_date(md: str, year: int) -> date:
    month, day = map(int, md.split("-"))
    return date(year, month, day)


def _historical_frost_rate_by_doy(
    historical: pd.DataFrame, threshold_c: float
) -> dict[int, float]:
    df = historical.copy()
    df["doy"] = df["time"].dt.dayofyear
    df["frost"] = (df["temperature_2m_min"] <= threshold_c).astype(int)
    grouped = df.groupby("doy")["frost"].mean()
    smoothed = grouped.rolling(7, min_periods=1, center=True).mean()
    return smoothed.to_dict()


def _confidence_score(
    model: Optional[FrostModel], avg_frost_prob: float, n_hist_samples: int
) -> dict:
    model_auc = float(model.metrics.get("auc", 0.8)) if model else 0.6
    data_quality = min(n_hist_samples / 7300, 1.0)
    overall = round(0.6 * model_auc + 0.3 * data_quality + 0.1 * (1 - avg_frost_prob), 3)
    return {
        "overall": overall,
        "model_auc": round(model_auc, 3),
        "historical_coverage": round(data_quality, 3),
    }
