from dataclasses import dataclass
from typing import Optional

import joblib
import numpy as np
import pandas as pd

from .config import FROST_MODEL_FILE

FEATURE_COLUMNS = [
    "day_of_year",
    "month",
    "temperature_2m_mean",
    "temp_mean_7d",
    "temp_mean_14d",
    "temp_min_7d",
    "precip_7d",
    "elevation",
    "latitude",
]


@dataclass
class FrostModel:
    model: object
    metrics: dict

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        X = df[FEATURE_COLUMNS].fillna(method="bfill").fillna(method="ffill").fillna(0)
        return self.model.predict_proba(X)[:, 1]


def build_frost_label(df: pd.DataFrame, threshold_c: float = 0.0) -> pd.Series:
    return (df["temperature_2m_min"] <= threshold_c).astype(int)


def prepare_training_frame(df: pd.DataFrame, elevation: float, latitude: float) -> pd.DataFrame:
    df = df.copy()
    df["elevation"] = elevation
    df["latitude"] = latitude
    df = df.dropna(subset=["temperature_2m_min", "temperature_2m_mean"])
    return df


def save_model(model: FrostModel) -> None:
    joblib.dump({"model": model.model, "metrics": model.metrics}, FROST_MODEL_FILE)


def load_model() -> Optional[FrostModel]:
    if not FROST_MODEL_FILE.exists():
        return None
    payload = joblib.load(FROST_MODEL_FILE)
    return FrostModel(model=payload["model"], metrics=payload["metrics"])
