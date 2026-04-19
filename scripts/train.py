"""Train the frost classifier on historical Open-Meteo data for multiple Western Balkans locations.

Usage:
    python -m scripts.train
"""
import asyncio
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.model import (
    FEATURE_COLUMNS,
    FrostModel,
    build_frost_label,
    prepare_training_frame,
    save_model,
)
from app.weather import add_features, fetch_elevation, fetch_historical

TRAINING_LOCATIONS = [
    ("Sarajevo", 43.8563, 18.4131),
    ("Banja Luka", 44.7722, 17.1910),
    ("Mostar", 43.3438, 17.8078),
    ("Podgorica", 42.4411, 19.2636),
    ("Niksic", 42.7731, 18.9483),
    ("Beograd", 44.7866, 20.4489),
    ("Novi Sad", 45.2671, 19.8335),
    ("Zagreb", 45.8150, 15.9819),
    ("Osijek", 45.5550, 18.6955),
    ("Skopje", 41.9973, 21.4280),
    ("Tirana", 41.3275, 19.8187),
    ("Ljubljana", 46.0569, 14.5058),
]


async def gather_data() -> pd.DataFrame:
    import asyncio as _asyncio
    frames = []
    for name, lat, lon in TRAINING_LOCATIONS:
        print(f"Fetching {name} ({lat}, {lon})...")
        try:
            hist = await fetch_historical(lat, lon)
            elev = await fetch_elevation(lat, lon)
            hist = add_features(hist)
            hist = prepare_training_frame(hist, elevation=elev, latitude=lat)
            hist["location"] = name
            frames.append(hist)
            await _asyncio.sleep(2.0)
        except Exception as e:
            print(f"  ! {name} failed: {e}")
            await _asyncio.sleep(5.0)
    if not frames:
        raise RuntimeError("No training data collected")
    return pd.concat(frames, ignore_index=True)


def train(df: pd.DataFrame) -> FrostModel:
    df = df.dropna(subset=FEATURE_COLUMNS + ["temperature_2m_min"])
    y = build_frost_label(df, threshold_c=0.0)
    X = df[FEATURE_COLUMNS]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.08,
        random_state=42,
    )
    clf.fit(X_train, y_train)

    proba = clf.predict_proba(X_test)[:, 1]
    preds = (proba >= 0.5).astype(int)

    metrics = {
        "auc": float(roc_auc_score(y_test, proba)),
        "report": classification_report(y_test, preds, output_dict=True),
        "n_samples": int(len(df)),
        "n_frost_days": int(y.sum()),
        "feature_columns": FEATURE_COLUMNS,
    }

    print(f"\n=== Training done ===")
    print(f"  Samples: {metrics['n_samples']}")
    print(f"  Frost days: {metrics['n_frost_days']} ({metrics['n_frost_days']/metrics['n_samples']:.1%})")
    print(f"  AUC: {metrics['auc']:.3f}")

    return FrostModel(model=clf, metrics=metrics)


async def main() -> None:
    df = await gather_data()
    model = train(df)
    save_model(model)
    print(f"\nModel saved to {__import__('app.config', fromlist=['FROST_MODEL_FILE']).FROST_MODEL_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
