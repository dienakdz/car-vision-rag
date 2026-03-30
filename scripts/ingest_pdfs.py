from pathlib import Path
import json
import re

import fitz  # PyMuPDF

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "kb" / "pdfs"
OUTPUT_PATH = BASE_DIR / "data" / "kb" / "pdf_chunks.json"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

FILE_METADATA = {
    "01_Ho_so_cong_ty_Minh_Dien_Showroom_KB.pdf": {
        "make": None,
        "model": "Company Profile",
        "year": None,
        "body_type": None,
        "kb_type": "company_profile",
    },
    "02_Ho_so_mau_xe_Template_Minh_Dien_Showroom.pdf": {
        "make": None,
        "model": "Vehicle Template",
        "year": None,
        "body_type": None,
        "kb_type": "vehicle_template",
    },
    "03_Chinh_sach_ban_hang_va_dich_vu_Minh_Dien_Showroom.pdf": {
        "make": None,
        "model": "Sales Policy",
        "year": None,
        "body_type": None,
        "kb_type": "sales_policy",
    },
    "04_FAQ_va_KB_Chatbot_Minh_Dien_Showroom.pdf": {
        "make": None,
        "model": "Chatbot FAQ",
        "year": None,
        "body_type": None,
        "kb_type": "chatbot_faq",
    },
    "05_Guide_Sedan_Minh_Dien_Showroom.pdf": {
        "make": None,
        "model": "Sedan Guide",
        "year": None,
        "body_type": "sedan",
        "kb_type": "vehicle_template",
    },
    "06_Guide_SUV_Minh_Dien_Showroom.pdf": {
        "make": None,
        "model": "SUV Guide",
        "year": None,
        "body_type": "suv",
        "kb_type": "vehicle_template",
    },
    "07_Guide_Pickup_Minh_Dien_Showroom.pdf": {
        "make": None,
        "model": "Pickup Guide",
        "year": None,
        "body_type": "pickup",
        "kb_type": "vehicle_template",
    },
    "08_Guide_Hatchback_Minh_Dien_Showroom.pdf": {
        "make": None,
        "model": "Hatchback Guide",
        "year": None,
        "body_type": "hatchback",
        "kb_type": "vehicle_template",
    },
    "09_Bo_cau_hoi_tu_van_theo_nhu_cau_Minh_Dien_Showroom.pdf": {
        "make": None,
        "model": "Consultation Question Bank",
        "year": None,
        "body_type": None,
        "kb_type": "chatbot_faq",
    },
    "10_Quy_trinh_Test_Drive_va_Dinh_gia_Thu_xe_cu_Minh_Dien_Showroom.pdf": {
        "make": None,
        "model": "Test Drive and Trade-in Workflow",
        "year": None,
        "body_type": None,
        "kb_type": "sales_policy",
    },
}

BODY_TYPE_KEYWORDS = {
    "sedan": ("sedan",),
    "suv": ("suv",),
    "hatchback": ("hatchback",),
    "pickup": ("pickup", "truck"),
}


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks: list[str] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end == text_length:
            break
        start = end - overlap

    return chunks


def extract_pdf_text(pdf_path: Path) -> list[dict]:
    doc = fitz.open(pdf_path)
    pages: list[dict] = []

    for page_num, page in enumerate(doc, start=1):
        text = clean_text(page.get_text("text"))
        if text:
            pages.append({"page": page_num, "text": text})

    doc.close()
    return pages


def infer_body_type_from_text(text: str) -> str | None:
    lower = text.lower()
    best_label = None
    best_score = 0

    for label, keywords in BODY_TYPE_KEYWORDS.items():
        score = sum(lower.count(keyword) for keyword in keywords)
        if score > best_score:
            best_label = label
            best_score = score

    return best_label if best_score > 0 else None


def detect_section_type(text: str) -> str:
    lower = text.lower()

    for word in ("design", "exterior", "interior", "performance", "capability", "technology", "safety"):
        if word in lower:
            return word

    if "feature" in lower or "features" in lower:
        return "features"

    if "specification" in lower or "dimensions" in lower or "capacity" in lower:
        return "specs"

    return "general"


def main() -> None:
    all_chunks: list[dict] = []
    chunk_id = 1
    pdf_files = list(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print("Khong tim thay file PDF nao trong data/kb/pdfs/")
        return

    for pdf_file in pdf_files:
        metadata = FILE_METADATA.get(
            pdf_file.name,
            {
                "make": None,
                "model": pdf_file.stem,
                "year": None,
                "body_type": None,
                "kb_type": "unknown",
            },
        )

        print(f"Dang xu ly: {pdf_file.name}")
        pages = extract_pdf_text(pdf_file)

        for page_data in pages:
            page_num = page_data["page"]
            page_text = page_data["text"]
            chunks = chunk_text(page_text)

            for idx, chunk in enumerate(chunks, start=1):
                section_type = detect_section_type(chunk)
                chunk_body_type = metadata.get("body_type")
                if not chunk_body_type and metadata.get("kb_type") == "vehicle_template":
                    chunk_body_type = infer_body_type_from_text(chunk)

                all_chunks.append(
                    {
                        "id": chunk_id,
                        "text": chunk,
                        "payload": {
                            "source_file": pdf_file.name,
                            "page": page_num,
                            "chunk_index": idx,
                            "make": metadata.get("make"),
                            "model": metadata.get("model"),
                            "year": metadata.get("year"),
                            "body_type": chunk_body_type,
                            "kb_type": metadata.get("kb_type", "unknown"),
                            "doc_type": f"{metadata.get('kb_type', 'unknown')}_pdf",
                            "section_type": section_type,
                        },
                    }
                )
                chunk_id += 1

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nDa luu {len(all_chunks)} chunks vao: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
