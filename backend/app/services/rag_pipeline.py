from app.services.embeddings import get_embedding
from app.services.vector_db import query
from app.services.llm_service import generate_answer, stream_answer


def run_rag(query_text: str) -> dict:
    if not query_text.strip():
        return {"answer": "Please provide a valid question.", "sources": []}

    query_embedding = get_embedding(query_text)
    relevant_chunks = query(query_embedding)

    context_texts = [c["text"] for c in relevant_chunks]
    sources = list(set(c["source"] for c in relevant_chunks))

    answer = generate_answer(query_text, context_texts)

    return {"answer": answer, "sources": sources}


# 🔥 STREAMING VERSION
def run_rag_stream(query_text: str):
    query_embedding = get_embedding(query_text)
    relevant_chunks = query(query_embedding)

    context_texts = [c["text"] for c in relevant_chunks]

    return stream_answer(query_text, context_texts)