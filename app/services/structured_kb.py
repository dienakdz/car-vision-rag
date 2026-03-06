import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
KB_PATH = BASE_DIR / "data" / "kb" / "cars.json"


def get_structured_body_type_knowledge(label: str):
    if not KB_PATH.exists():
        return None

    with open(KB_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        if item.get("type") == "body_type" and item.get("label") == label:
            return item

    return None