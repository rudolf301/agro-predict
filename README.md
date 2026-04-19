# Agro-Predict API

AI-powered planting-date recommendations for small farmers in the Western Balkans. Uses 20 years of Open-Meteo historical data + a Gradient Boosting frost classifier to recommend optimal sowing windows per crop and location.

Built for **Adria Future Hackathon 2026** (Montenegro).

## Features
- Frost-probability classifier trained on 12 WB locations × 20 years
- 14-day frost forecast per location
- Per-crop planting window recommendation (10 crops: corn, wheat, soybeans, barley, potato, tomato, onion, pepper, rapeseed, sunflower)
- Traffic-light risk scoring (green/yellow/red)
- Bilingual explanations (EN/BS)
- Zero hardware — public APIs only

## Quick start

```bash
cd predictApp
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

# 1) Train the frost model (first run only; ~2-5 min, fetches historical data)
python -m scripts.train

# 2) Start the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for interactive Swagger UI.

## API

### `GET /health`
```json
{ "status": "ok", "model_loaded": true, "model_auc": 0.92 }
```

### `GET /crops`
Returns list of supported crops.
```json
{ "crops": [ { "id": "corn", "name_en": "Corn", "name_bs": "Kukuruz" }, ... ] }
```

### `GET /predict`
Main endpoint. Supports **one or many crops in a single call** — weather data is fetched once and reused, so passing 5 crops costs the same as 1.

**Query params:**
- `lat` (required, -90..90)
- `lon` (required, -180..180)
- `crop` (required) — one id or comma-separated list (e.g. `corn` or `corn,wheat,potato`)
- `elevation` (optional, meters — auto-fetched if omitted)
- `lang` (optional, `en` or `bs`, default `en`)

**Examples:**
```
GET /predict?lat=43.8563&lon=18.4131&crop=corn&lang=bs
GET /predict?lat=43.8563&lon=18.4131&crop=corn,tomato,potato&lang=bs
```

**Response (shape is the same for 1 or N crops — always an array):**
```json
{
  "location": { "latitude": 43.8563, "longitude": 18.4131, "elevation_m": 543.0 },
  "predictions": [
    {
      "crop": { "id": "corn", "name_en": "Corn", "name_bs": "Kukuruz", "frost_tolerance": "none", "growing_days": 120 },
      "recommended_planting": {
        "date": "2026-05-04",
        "confidence": 0.98,
        "historical_frost_rate": 0.0,
        "forecast_frost_probability": 0.0,
        "window_start": "2026-04-15",
        "window_end": "2026-05-31"
      },
      "risk": {
        "traffic_light": "yellow",
        "label": "Moderate risk — monitor weather closely",
        "avg_frost_probability_14d": 0.001,
        "max_frost_probability_14d": 0.002,
        "crop_frost_risk_days_14d": 6
      },
      "forecast_14d": [
        { "date": "2026-04-19", "temp_min_c": 3.8, "temp_max_c": 19.7, "precipitation_mm": 0.0, "frost_probability": 0.0, "crop_frost_risk": false }
      ],
      "confidence": { "overall": 0.88, "model_auc": 0.99, "historical_coverage": 1.0 },
      "explanation": [
        "Optimalni datum sjetve za Corn: 2026-05-04.",
        "Istorijski, mraz na ovoj lokaciji nakon ovog datuma javlja se samo u 0.0% godina.",
        "Uslovi su grani\u010dni — pratite prognoze dnevno."
      ]
    }
  ]
}
```

## Integration notes for frontend team

- **Mobile GPS workflow:** grab coordinates with `navigator.geolocation.getCurrentPosition()` (web) or native FusedLocationProvider / CoreLocation (native) → pass as `lat`/`lon`. No municipality lookup needed — the API handles elevation and historical data per coordinate.
- **Multi-select pills:** if the user picks multiple crops (like the reference UI's "Wheat ✓" chips), send them comma-separated: `?crop=corn,wheat,potato`. Response `predictions[]` order matches input order.
- **Response is always an array** (`predictions[]`), even for 1 crop — keeps frontend logic uniform.
- CORS is open to all origins (development). Lock down to your domain before prod.
- First call to `/predict` for a new location takes 5-15s (cold Open-Meteo archive fetch). Subsequent calls use local cache (`cache/` folder) and return in <500ms.
- All dates are ISO-8601. All temps in °C, precipitation in mm.
- `traffic_light` values: `green` | `yellow` | `red`. Use for colored badge UI.
- `explanation` is a list of short bullets ready to render as a list.
- Error responses: HTTP 400 with `{ "detail": "Unknown crop: X. Available: [...]" }` if crop id invalid.

## Architecture

```
predictApp/
├── app/
│   ├── main.py       # FastAPI app + endpoints
│   ├── weather.py    # Open-Meteo client (archive + forecast) with disk cache
│   ├── model.py      # FrostModel wrapper (load/save/predict)
│   ├── crops.py      # Crop lookup (loads crops.json)
│   ├── predict.py    # Core prediction pipeline
│   ├── explain.py    # Bilingual explanation generator
│   └── config.py     # Paths, constants
├── data/
│   └── crops.json    # 10 crops × optimal conditions
├── models/
│   └── frost_model.pkl
├── scripts/
│   └── train.py      # One-shot training script
├── cache/            # HTTP response cache
└── requirements.txt
```

## Model

- **Algorithm:** Gradient Boosting Classifier (`sklearn.ensemble.GradientBoostingClassifier`, 200 estimators, max_depth=4)
- **Target:** `temperature_2m_min <= 0°C` (binary)
- **Features:** day of year, month, daily mean temp, 7/14-day mean temp, 7-day min temp, 7-day precipitation, elevation, latitude
- **Training data:** ~87,600 daily records (12 cities × 20 years × 365 days)
- **Typical AUC:** 0.90+ on held-out split

## Sustainability — UN SDG alignment
- **SDG 2 (Zero Hunger):** reduces crop losses from frost and weather volatility
- **SDG 13 (Climate Action):** helps farmers adapt to shifting planting calendars

## License
MIT — Adria Future Hackathon 2026
