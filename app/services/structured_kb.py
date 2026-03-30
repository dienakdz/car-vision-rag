import json
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
KB_PATH = BASE_DIR / "data" / "kb" / "cars.json"


@lru_cache(maxsize=1)
def _load_structured_kb() -> list[dict]:
    if not KB_PATH.exists():
        return []

    try:
        with KB_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []
    return data


def get_structured_body_type_knowledge(label: str | None):
    if not label:
        return None

    normalized = label.strip().lower()
    if not normalized:
        return None

    for item in _load_structured_kb():
        if (
            item.get("type") == "body_type"
            and str(item.get("label", "")).strip().lower() == normalized
        ):
            return item

    return None
