from fastapi import APIRouter
from app.services.rag_pipeline import run_rag

router = APIRouter()

@router.post("/triage")
def triage(query: str):
    answer = run_rag(query)
    return {"response": answer}