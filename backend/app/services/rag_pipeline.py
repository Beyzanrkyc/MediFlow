from app.services.embeddings import get_embedding
from app.services.vector_db import query
from app.services.llm_service import generate_answer, stream_answer


def _distance_to_confidence(distance: float) -> float:
    """
    Heuristic-only conversion from ChromaDB's L2 distance to a 0-1 'confidence'.
    This is NOT a calibrated probability — just a monotonic, boundable proxy
    for retrieval similarity, useful for ranking/display purposes.
    """
    return round(1 / (1 + distance), 3)


def run_rag(query_text: str) -> dict:
    if not query_text.strip():
        return {"answer": "Please provide a valid question.", "sources": []}

    query_embedding = get_embedding(query_text)
    relevant_chunks = query(query_embedding)

    context_texts = [c["text"] for c in relevant_chunks]
    sources = list(set(c["source"] for c in relevant_chunks))
    source_confidences = {
        c["source"]: _distance_to_confidence(c["distance"]) for c in relevant_chunks
    }

    answer = generate_answer(query_text, context_texts)

    return {
        "answer": answer,
        "sources": sources,
        "chunks": relevant_chunks,
        "source_confidences": source_confidences,
    }


# 🔥 STREAMING VERSION (UPDATED)
def run_rag_stream(query_text: str):
    query_embedding = get_embedding(query_text)
    relevant_chunks = query(query_embedding)

    context_texts = [c["text"] for c in relevant_chunks]
    sources = list(set(c["source"] for c in relevant_chunks))
    source_confidences = {
        c["source"]: _distance_to_confidence(c["distance"]) for c in relevant_chunks
    }

    stream = stream_answer(query_text, context_texts)

    return stream, sources, relevant_chunks, source_confidences
