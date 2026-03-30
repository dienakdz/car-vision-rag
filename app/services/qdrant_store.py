import atexit
from pathlib import Path
from threading import Lock

from qdrant_client import QdrantClient

BASE_DIR = Path(__file__).resolve().parent.parent.parent
QDRANT_STORAGE = BASE_DIR / "data" / "qdrant_local"
COLLECTION_NAME = "car_pdf_kb"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_client: QdrantClient | None = None
_client_lock = Lock()


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is not None:
        return _client

    with _client_lock:
        if _client is None:
            QDRANT_STORAGE.mkdir(parents=True, exist_ok=True)
            client = QdrantClient(path=str(QDRANT_STORAGE))
            client.set_model(EMBED_MODEL)
            _client = client

    return _client


def close_qdrant_client() -> None:
    global _client
    if _client is None:
        return
    try:
        _client.close()
    except Exception:
        pass
    finally:
        _client = None


atexit.register(close_qdrant_client)
