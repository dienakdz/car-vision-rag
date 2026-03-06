from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import STATIC_DIR

app = FastAPI(title="Car Vision RAG", version="0.1.0")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(router)