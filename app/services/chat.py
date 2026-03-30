from app.core.config import CHAT_RETRIEVAL_LIMIT
from app.services.llm import generate_answer_with_rag
from app.services.retriever import retrieve_company_context, retrieve_vehicle_context
from app.services.session_store import get_last_prediction


def classify_chat_intent(message: str) -> str:
    msg = message.lower()

    if any(
        x in msg
        for x in ["trả góp", "mua xe", "đặt cọc", "giao xe", "bảo hành", "showroom", "chính sách"]
    ):
        return "company"

    if any(
        x in msg
        for x in ["xe này", "chiếc xe", "xe vừa upload", "body type", "sedan", "suv", "pickup", "hatchback"]
    ):
        return "vehicle"

    return "general"


def _build_fallback_answer(prediction: dict | None, docs: list[dict], intent: str) -> str:
    parts: list[str] = []

    if prediction and intent == "vehicle":
        label = prediction.get("predicted_label")
        confidence = prediction.get("confidence")
        if label and confidence is not None:
            parts.append(
                f"Dựa trên ảnh gần nhất, hệ thống đang nghiêng về '{label}' với độ tin cậy khoảng {round(confidence * 100, 2)}%."
            )

    if not docs:
        parts.append("Hiện chưa truy hồi được tài liệu phù hợp trong knowledge base để trả lời chi tiết.")
        return " ".join(parts).strip()

    refs = []
    for idx, doc in enumerate(docs[:3], start=1):
        source = doc.get("source_file") or "unknown"
        page = doc.get("page")
        if page is None:
            refs.append(f"[{idx}] {source}")
        else:
            refs.append(f"[{idx}] {source} (trang {page})")

    parts.append("Mình đã tìm thấy tài liệu liên quan nhưng chưa thể tạo câu trả lời ngôn ngữ tự nhiên ở lượt này.")
    if refs:
        parts.append("Nguồn tham chiếu: " + "; ".join(refs) + ".")
    parts.append("Bạn hỏi lại theo hướng cụ thể hơn (ví dụ: so sánh, chi phí, nhu cầu sử dụng) để mình trả lời sát hơn.")
    return " ".join(parts).strip()


def chat_with_context(message: str) -> dict:
    message = " ".join(message.strip().split())
    if not message:
        return {
            "intent": "general",
            "last_prediction": get_last_prediction(),
            "answer": "Vui lòng nhập câu hỏi cụ thể để mình hỗ trợ.",
            "sources": [],
            "generation": {
                "mode": "fallback",
                "reason": "empty_message",
            },
        }

    prediction = get_last_prediction()
    intent = classify_chat_intent(message)

    if intent == "vehicle":
        body_type = prediction.get("predicted_label") if prediction else None
        query_text = f"{message}. related to uploaded car body type {body_type}" if body_type else message
        docs = retrieve_vehicle_context(
            body_type=body_type,
            query_text=query_text,
            limit=CHAT_RETRIEVAL_LIMIT,
        )
    else:
        docs = retrieve_company_context(
            query_text=message,
            limit=CHAT_RETRIEVAL_LIMIT,
        )

    llm_answer, generation = generate_answer_with_rag(
        message=message,
        prediction=prediction,
        docs=docs,
        intent=intent,
    )

    answer = llm_answer or _build_fallback_answer(prediction=prediction, docs=docs, intent=intent)

    return {
        "intent": intent,
        "last_prediction": prediction,
        "answer": answer,
        "sources": docs,
        "generation": generation,
    }
