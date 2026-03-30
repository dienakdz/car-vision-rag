from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")

APP_DIR = BASE_DIR / "app"
UPLOAD_DIR = BASE_DIR / "uploads"
MODEL_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

MAX_FILE_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

PUBLIC_UPLOAD_URL_PREFIX = "/uploads"

LLM_API_BASE = os.getenv("LLM_API_BASE", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "700"))
LLM_TIMEOUT_SEC = float(os.getenv("LLM_TIMEOUT_SEC", "45"))
LLM_CONTEXT_DOCS = int(os.getenv("LLM_CONTEXT_DOCS", "5"))
LLM_CONTEXT_CHARS = int(os.getenv("LLM_CONTEXT_CHARS", "1200"))
CHAT_RETRIEVAL_LIMIT = int(os.getenv("CHAT_RETRIEVAL_LIMIT", "5"))
PDF_RETRIEVAL_LIMIT = int(os.getenv("PDF_RETRIEVAL_LIMIT", "5"))
