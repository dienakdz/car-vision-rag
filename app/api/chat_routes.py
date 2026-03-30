from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from app.services.chat import chat_with_context

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)


@router.post("")
async def chat(req: ChatRequest):
    return await run_in_threadpool(chat_with_context, req.message.strip())
