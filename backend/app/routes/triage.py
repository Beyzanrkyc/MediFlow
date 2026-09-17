from fastapi import APIRouter
from pydantic import BaseModel

from app.services.rag_pipeline import run_rag

router = APIRouter()


class TriageRequest(BaseModel):
    query: str


@router.post("/triage")
def triage(req: TriageRequest):
    result = run_rag(req.query)
    return {
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "chunks": result.get("chunks", []),
    }