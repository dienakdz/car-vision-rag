from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.chat_routes import router as chat_router
from app.api.routes import router
from app.core.config import STATIC_DIR, UPLOAD_DIR
from app.services.qdrant_store import close_qdrant_client


@asynccontextmanager
async def app_lifespan(_: FastAPI):
    yield
    close_qdrant_client()


app = FastAPI(
    title="Car Vision RAG",
    version="0.1.0",
    lifespan=app_lifespan,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(router)
app.include_router(chat_router)
