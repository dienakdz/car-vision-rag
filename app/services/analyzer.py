from pathlib import Path

from app.core.config import UPLOAD_DIR, PUBLIC_UPLOAD_URL_PREFIX
from app.services.detector import detect_car
from app.services.classifier import classify_body_type
from app.services.rag import retrieve_pdf_knowledge
from app.services.structured_kb import get_structured_body_type_knowledge
from app.utils.image import crop_image


def build_analysis_summary(classification_result: dict) -> str:
    if not classification_result:
        return "Chưa có kết quả phân loại."

    predicted_label = classification_result.get("predicted_label")
    confidence = classification_result.get("confidence")
    is_uncertain = classification_result.get("is_uncertain", True)

    if predicted_label is None or confidence is None:
        return "Chưa có model phân loại body type."

    percent = round(confidence * 100, 2)

    if is_uncertain:
        return f"Hệ thống nghiêng về body type '{predicted_label}', nhưng độ tin cậy còn thấp ({percent}%)."
    return f"Hệ thống dự đoán body type là '{predicted_label}' với độ tin cậy {percent}%."


def analyze_car_image(image_path: str) -> dict:
    detection_result = detect_car(image_path)

    image_file = Path(image_path)
    original_url = f"{PUBLIC_UPLOAD_URL_PREFIX}/{image_file.name}"

    if not detection_result["detected"] or not detection_result["main_car"]:
        return {
            "detected": False,
            "message": "Không phát hiện được ô tô trong ảnh.",
            "summary": "Hệ thống chưa phát hiện được xe nên chưa thể phân loại.",
            "original_image_url": original_url,
            "detection": detection_result,
            "crop": None,
            "classification": None,
            "knowledge": {
                "structured": None,
                "pdf": None
            }
        }

    main_car = detection_result["main_car"]
    bbox = main_car["bbox"]

    crop_filename = f"{image_file.stem}_car_crop.jpg"
    crop_path = UPLOAD_DIR / crop_filename

    crop_result = crop_image(
        image_path=image_path,
        bbox=bbox,
        output_path=str(crop_path)
    )
    crop_result["crop_url"] = f"{PUBLIC_UPLOAD_URL_PREFIX}/{crop_filename}"

    classification_result = classify_body_type(str(crop_path))
    summary = build_analysis_summary(classification_result)

    predicted_label = classification_result.get("predicted_label")
    top_k = classification_result.get("top_k", [])

    structured_knowledge = get_structured_body_type_knowledge(predicted_label) if predicted_label else None
    pdf_knowledge = retrieve_pdf_knowledge(predicted_label, top_k=top_k) if predicted_label else None

    return {
        "detected": True,
        "message": "Đã phát hiện và crop xe chính.",
        "summary": summary,
        "original_image_url": original_url,
        "detection": detection_result,
        "crop": crop_result,
        "classification": classification_result,
        "knowledge": {
            "structured": structured_knowledge,
            "pdf": pdf_knowledge
        }
    }