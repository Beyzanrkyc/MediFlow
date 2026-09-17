from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.rag_pipeline import run_rag, run_rag_stream
from app.utils.triage_logging import log_triage_session

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


# ─────────────────────────────────────────────
# ✅ NORMAL (NON-STREAM) ENDPOINT
# ─────────────────────────────────────────────
@router.post("/chat")
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        result = run_rag(req.message)
        sources = result.get("sources", [])
        confidences = result.get("source_confidences", {})

        log_triage_session(db, req.message, result["answer"], sources, confidences)

        return JSONResponse({
            "answer": result["answer"],
            "sources": sources,
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
async def chat_stream(req: ChatRequest, db: Session = Depends(get_db)):

    try:
        stream, sources, chunks, confidences = run_rag_stream(req.message)

    except Exception as e:
        print("STREAM INIT ERROR:", e)

        def error_generator():
            yield "⚠️ Failed to start AI stream."

        return StreamingResponse(error_generator(), media_type="text/plain")

    def generator():
        full_answer = []
        try:
            for chunk in stream:
                full_answer.append(chunk)
                yield chunk

        except Exception as e:
            print("STREAM ERROR:", e)
            yield "\n\n⚠️ AI service interrupted."
        finally:
            # Log after the stream completes so we capture the full answer.
            if full_answer:
                log_triage_session(db, req.message, "".join(full_answer), sources, confidences)

    return StreamingResponse(generator(), media_type="text/plain")