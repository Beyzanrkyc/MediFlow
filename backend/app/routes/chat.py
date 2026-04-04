from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_pipeline import run_rag, run_rag_stream
from fastapi.responses import StreamingResponse

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(req: ChatRequest):
    return run_rag(req.message)


# 🔥 STREAM ENDPOINT
@router.post("/chat-stream")
async def chat_stream(req: ChatRequest):
    def generator():
        for chunk in run_rag_stream(req.message):
            yield chunk

    return StreamingResponse(generator(), media_type="text/plain")