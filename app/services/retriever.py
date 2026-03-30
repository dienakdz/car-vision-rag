from qdrant_client import models

from app.services.qdrant_store import COLLECTION_NAME, get_qdrant_client

COMPANY_KB_TYPES = ("company_profile", "sales_policy", "chatbot_faq")
VEHICLE_KB_TYPE = "vehicle_template"
MAX_RETRIEVAL_LIMIT = 20


def _format_hits(hits):
    docs = []
    for hit in hits:
        payload = hit.metadata if hasattr(hit, "metadata") else hit.payload
        if not payload:
            continue
        score = getattr(hit, "score", None)
        docs.append({
            "score": round(score, 4) if score is not None else None,
            "text": payload.get("text"),
            "source_file": payload.get("source_file"),
            "page": payload.get("page"),
            "kb_type": payload.get("kb_type"),
            "make": payload.get("make"),
            "model": payload.get("model"),
            "year": payload.get("year"),
            "body_type": payload.get("body_type"),
        })
    return docs


def _safe_limit(limit: int) -> int:
    return max(1, min(int(limit), MAX_RETRIEVAL_LIMIT))


def _query_context(query_text: str, query_filter: models.Filter, limit: int):
    client = get_qdrant_client()
    hits = client.query(
        collection_name=COLLECTION_NAME,
        query_text=query_text,
        query_filter=query_filter,
        limit=_safe_limit(limit),
    )
    return _format_hits(hits)


def build_query_from_classification(label: str, top_k: list | None = None) -> str:
    if not top_k:
        return f"{label} car brochure features specifications description"

    labels = [item["label"] for item in top_k[:3]]
    joined = ", ".join(labels)
    return (
        f"car brochure for body type likely one of {joined}. "
        "retrieve vehicle description, features, and specifications"
    )


def _build_vehicle_filter(body_type: str | None, strict_body_type: bool) -> models.Filter:
    must_conditions = [
        models.FieldCondition(
            key="kb_type",
            match=models.MatchValue(value=VEHICLE_KB_TYPE),
        )
    ]
    if strict_body_type and body_type:
        must_conditions.append(
            models.FieldCondition(
                key="body_type",
                match=models.MatchValue(value=body_type),
            )
        )

    return models.Filter(must=must_conditions)


def retrieve_vehicle_context(body_type: str | None, query_text: str, limit: int = 5):
    primary_filter = _build_vehicle_filter(
        body_type=body_type,
        strict_body_type=bool(body_type),
    )
    docs = _query_context(
        query_text=query_text,
        query_filter=primary_filter,
        limit=limit,
    )
    if docs or not body_type:
        return docs

    fallback_filter = _build_vehicle_filter(
        body_type=None,
        strict_body_type=False,
    )
    return _query_context(
        query_text=query_text,
        query_filter=fallback_filter,
        limit=limit,
    )


def retrieve_company_context(query_text: str, limit: int = 5):
    query_filter = models.Filter(
        should=[
            models.FieldCondition(
                key="kb_type",
                match=models.MatchValue(value=kb_type),
            )
            for kb_type in COMPANY_KB_TYPES
        ]
    )

    return _query_context(
        query_text=query_text,
        query_filter=query_filter,
        limit=limit,
    )


def retrieve_pdf_knowledge(label: str, top_k: list | None = None, limit: int = 5) -> dict:
    query_text = build_query_from_classification(label, top_k)

    primary_filter = _build_vehicle_filter(
        body_type=label,
        strict_body_type=True,
    )
    retrieved_docs = _query_context(
        query_text=query_text,
        query_filter=primary_filter,
        limit=limit,
    )

    if not retrieved_docs:
        fallback_filter = _build_vehicle_filter(
            body_type=None,
            strict_body_type=False,
        )
        retrieved_docs = _query_context(
            query_text=query_text,
            query_filter=fallback_filter,
            limit=limit,
        )

    summary = retrieved_docs[0]["text"] if retrieved_docs else None
    return {
        "query": query_text,
        "label": label,
        "summary": summary,
        "retrieved_docs": retrieved_docs,
    }
