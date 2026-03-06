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
    "my25-camry-ebrochure.pdf": {
        "make": "Toyota",
        "model": "Camry",
        "year": 2025,
        "body_type": "sedan"
    },
    "rav4_ebrochure.pdf": {
        "make": "Toyota",
        "model": "RAV4",
        "year": 2023,
        "body_type": "suv"
    },
    "tacoma_ebrochure.pdf": {
        "make": "Toyota",
        "model": "Tacoma",
        "year": 2024,
        "body_type": "pickup"
    },
    "MY17 Civic HB Brochure Online PDF_B14.pdf": {
        "make": "Honda",
        "model": "Civic Hatchback",
        "year": 2017,
        "body_type": "hatchback"
    }
}


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    chunks = []
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


def extract_pdf_text(pdf_path: Path):
    doc = fitz.open(pdf_path)
    pages = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        text = clean_text(text)
        if text:
            pages.append({
                "page": page_num,
                "text": text
            })

    doc.close()
    return pages


def main():
    all_chunks = []
    chunk_id = 1

    pdf_files = list(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print("Không tìm thấy file PDF nào trong data/kb/pdfs/")
        return

    for pdf_file in pdf_files:
        metadata = FILE_METADATA.get(pdf_file.name, {
            "make": None,
            "model": pdf_file.stem,
            "year": None,
            "body_type": None
        })

        print(f"Đang xử lý: {pdf_file.name}")

        pages = extract_pdf_text(pdf_file)

        for page_data in pages:
            page_num = page_data["page"]
            page_text = page_data["text"]

            chunks = chunk_text(page_text)

            for i, chunk in enumerate(chunks, start=1):
                all_chunks.append({
                    "id": chunk_id,
                    "text": chunk,
                    "payload": {
                        "source_file": pdf_file.name,
                        "page": page_num,
                        "chunk_index": i,
                        "make": metadata["make"],
                        "model": metadata["model"],
                        "year": metadata["year"],
                        "body_type": metadata["body_type"],
                        "doc_type": "pdf_brochure"
                    }
                })
                chunk_id += 1

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nĐã lưu {len(all_chunks)} chunks vào: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()