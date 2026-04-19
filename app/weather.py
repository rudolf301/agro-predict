import asyncio
import hashlib
import json
from datetime import date, timedelta
from typing import Optional

import httpx
import pandas as pd

from .config import (
    CACHE_DIR,
    FORECAST_DAYS,
    HISTORICAL_YEARS,
    OPEN_METEO_ARCHIVE_URL,
    OPEN_METEO_ELEVATION_URL,
    OPEN_METEO_FORECAST_URL,
)


def _cache_key(prefix: str, **params) -> str:
    payload = json.dumps(params, sort_keys=True)
    digest = hashlib.md5(payload.encode()).hexdigest()[:12]
    return f"{prefix}_{digest}.json"


def _read_cache(name: str) -> Optional[dict]:
    path = CACHE_DIR / name
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _write_cache(name: str, data: dict) -> None:
    path = CACHE_DIR / name
    path.write_text(json.dumps(data), encoding="utf-8")


async def _get_with_retry(
    client: httpx.AsyncClient, url: str, params: dict, max_attempts: int = 5
) -> httpx.Response:
    for attempt in range(max_attempts):
        r = await client.get(url, params=params)
        if r.status_code == 429:
            wait = 2 ** attempt + 1
            await asyncio.sleep(wait)
            continue
        r.raise_for_status()
        return r
    r.raise_for_status()
    return r


async def fetch_elevation(lat: float, lon: float) -> float:
    name = _cache_key("elev", lat=round(lat, 3), lon=round(lon, 3))
    cached = _read_cache(name)
    if cached:
        return float(cached["elevation"])

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await _get_with_retry(
            client,
            OPEN_METEO_ELEVATION_URL,
            {"latitude": lat, "longitude": lon},
        )
        data = r.json()

    elevation = float(data["elevation"][0]) if data.get("elevation") else 0.0
    _write_cache(name, {"elevation": elevation})
    return elevation


async def fetch_historical(
    lat: float, lon: float, years: int = HISTORICAL_YEARS
) -> pd.DataFrame:
    end = date.today() - timedelta(days=1)
    start = end.replace(year=end.year - years)

    name = _cache_key(
        "hist",
        lat=round(lat, 2),
        lon=round(lon, 2),
        start=start.isoformat(),
        end=end.isoformat(),
    )
    cached = _read_cache(name)
    if cached:
        df = pd.DataFrame(cached)
        df["time"] = pd.to_datetime(df["time"])
        return df

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "precipitation_sum",
                "snowfall_sum",
            ]
        ),
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await _get_with_retry(client, OPEN_METEO_ARCHIVE_URL, params)
        data = r.json()

    daily = data["daily"]
    df = pd.DataFrame(daily)
    df["time"] = pd.to_datetime(df["time"])
    _write_cache(name, df.assign(time=df["time"].astype(str)).to_dict(orient="list"))
    return df


async def fetch_forecast(lat: float, lon: float, days: int = FORECAST_DAYS) -> pd.DataFrame:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "precipitation_sum",
            ]
        ),
        "forecast_days": days,
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await _get_with_retry(client, OPEN_METEO_FORECAST_URL, params)
        data = r.json()

    df = pd.DataFrame(data["daily"])
    df["time"] = pd.to_datetime(df["time"])
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("time").reset_index(drop=True)
    df["day_of_year"] = df["time"].dt.dayofyear
    df["month"] = df["time"].dt.month
    df["temp_mean_7d"] = df["temperature_2m_mean"].rolling(7, min_periods=1).mean()
    df["temp_mean_14d"] = df["temperature_2m_mean"].rolling(14, min_periods=1).mean()
    df["temp_min_7d"] = df["temperature_2m_min"].rolling(7, min_periods=1).min()
    df["precip_7d"] = df["precipitation_sum"].rolling(7, min_periods=1).sum()
    return df
