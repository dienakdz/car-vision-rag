from pathlib import Path
from qdrant_client import QdrantClient, models

BASE_DIR = Path(__file__).resolve().parent.parent.parent
QDRANT_STORAGE = BASE_DIR / "data" / "qdrant_local"

COLLECTION_NAME = "car_pdf_kb"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_client = None


def get_qdrant_client():
    global _client
    if _client is None:
        _client = QdrantClient(path=str(QDRANT_STORAGE))
        _client.set_model(EMBED_MODEL)
    return _client


def build_query_from_classification(label: str, top_k: list | None = None) -> str:
    if not top_k:
        return f"{label} car brochure features specifications description"

    labels = [item["label"] for item in top_k[:3]]
    joined = ", ".join(labels)
    return f"car brochure for body type likely one of {joined}. retrieve vehicle description, features, and specifications"


def retrieve_pdf_knowledge(label: str, top_k: list | None = None, limit: int = 5) -> dict:
    client = get_qdrant_client()
    query_text = build_query_from_classification(label, top_k)

    query_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="body_type",
                match=models.MatchValue(value=label)
            )
        ]
    )

    hits = client.query(
        collection_name=COLLECTION_NAME,
        query_text=query_text,
        query_filter=query_filter,
        limit=limit
    )

    retrieved_docs = []
    for hit in hits:
        payload = hit.metadata if hasattr(hit, "metadata") else hit.payload
        score = getattr(hit, "score", None)

        retrieved_docs.append({
            "score": round(score, 4) if score is not None else None,
            "text": payload.get("text"),
            "source_file": payload.get("source_file"),
            "page": payload.get("page"),
            "make": payload.get("make"),
            "model": payload.get("model"),
            "year": payload.get("year"),
            "body_type": payload.get("body_type")
        })

    summary = retrieved_docs[0]["text"] if retrieved_docs else None

    return {
        "query": query_text,
        "label": label,
        "summary": summary,
        "retrieved_docs": retrieved_docs
    }