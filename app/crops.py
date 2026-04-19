import json
from functools import lru_cache

from .config import CROPS_FILE


@lru_cache(maxsize=1)
def load_crops() -> dict:
    with open(CROPS_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_crop(crop_id: str) -> dict:
    crops = load_crops()
    crop_id = crop_id.lower().strip()
    if crop_id not in crops:
        raise KeyError(f"Unknown crop: {crop_id}. Available: {list(crops.keys())}")
    return crops[crop_id]


def list_crops() -> list[dict]:
    return [
        {"id": k, "name_en": v["name_en"], "name_bs": v["name_bs"]}
        for k, v in load_crops().items()
    ]
