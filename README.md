## Car Vision RAG

FastAPI app for:
- Detecting and cropping car from uploaded image (YOLO).
- Classifying body type (ResNet18 classifier).
- Retrieving knowledge from local Qdrant (RAG).
- Answering chat with Gemini API + retrieved context.

## Quick Start

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Configure environment:
   - Copy `.env.example` to `.env`
   - Set `LLM_API_KEY` with your Gemini API key
3. Run app:
   - `python run.py`
4. Open:
   - `http://127.0.0.1:8888`

## Required Env

- `LLM_API_KEY`

## Useful Env

- `LLM_MODEL` (default: `gemini-2.5-flash`)
- `LLM_TIMEOUT_SEC`
- `LLM_CONTEXT_DOCS`
- `LLM_CONTEXT_CHARS`
- `CHAT_RETRIEVAL_LIMIT`
