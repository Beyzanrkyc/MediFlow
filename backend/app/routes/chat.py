from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse

from app.services.rag_pipeline import run_rag, run_rag_stream

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


# ─────────────────────────────────────────────
# ✅ NORMAL (NON-STREAM) ENDPOINT
# ─────────────────────────────────────────────
@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        result = run_rag(req.message)

        return JSONResponse({
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "chunks": result.get("chunks", []),  # 🔥 NEW
        })

    except Exception as e:
        print("CHAT ERROR:", e)
        return JSONResponse({
            "answer": "⚠️ AI service temporarily unavailable.",
            "sources": [],
            "chunks": []
        })


# ─────────────────────────────────────────────
# 🔥 STREAMING ENDPOINT (FIXED)
# ─────────────────────────────────────────────
@router.post("/chat-stream")
async def chat_stream(req: ChatRequest):

    try:
        stream, sources, chunks = run_rag_stream(req.message)

    except Exception as e:
        print("STREAM INIT ERROR:", e)

        def error_generator():
            yield "⚠️ Failed to start AI stream."

        return StreamingResponse(error_generator(), media_type="text/plain")

    def generator():
        try:
            for chunk in stream:
                yield chunk

        except Exception as e:
            print("STREAM ERROR:", e)
            yield "\n\n⚠️ AI service interrupted."

    return StreamingResponse(generator(), media_type="text/plain")