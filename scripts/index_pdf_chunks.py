from pathlib import Path
import json

from qdrant_client import QdrantClient

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_PATH = BASE_DIR / "data" / "kb" / "pdf_chunks.json"
QDRANT_STORAGE = BASE_DIR / "data" / "qdrant_local"
COLLECTION_NAME = "car_pdf_kb"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_chunks() -> list[dict]:
    with CHUNKS_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    chunks = load_chunks()
    if not chunks:
        print("Khong co chunk de index.")
        return

    QDRANT_STORAGE.mkdir(parents=True, exist_ok=True)
    try:
        client = QdrantClient(path=str(QDRANT_STORAGE))
    except RuntimeError as exc:
        msg = str(exc)
        if "already accessed by another instance" in msg:
            print("Qdrant local dang bi lock. Hay tat app/server dang chay roi thu lai.")
            return
        raise

    try:
        client.set_model(EMBED_MODEL)

        if client.collection_exists(COLLECTION_NAME):
            client.delete_collection(COLLECTION_NAME)

        documents = [chunk["text"] for chunk in chunks]
        metadata = []
        ids = []

        for chunk in chunks:
            payload = dict(chunk["payload"])
            payload["text"] = chunk["text"]
            metadata.append(payload)
            ids.append(chunk["id"])

        client.add(
            collection_name=COLLECTION_NAME,
            documents=documents,
            metadata=metadata,
            ids=ids,
        )
        print(f"Da index {len(chunks)} chunks vao collection: {COLLECTION_NAME}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
