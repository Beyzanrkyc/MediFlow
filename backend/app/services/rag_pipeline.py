from app.services.embeddings import get_embedding
from app.services.vector_db import query
from app.services.llm_service import generate_answer


def run_rag(query_text: str) -> dict:
    """
    Run the full RAG pipeline.
    Returns answer + sources so the user knows where info came from.
    """
    if not query_text or not query_text.strip():
        return {"answer": "Please provide a valid question.", "sources": []}

    try:
        query_embedding = get_embedding(query_text)
        relevant_chunks = query(query_embedding)

        if not relevant_chunks:
            return {
                "answer": "I couldn't find relevant NHS guidelines for your question.",
                "sources": []
            }

        # Split text and sources for the LLM
        context_texts = [c["text"] for c in relevant_chunks]
        sources = list(set(c["source"] for c in relevant_chunks))

        answer = generate_answer(query_text, context_texts)

        return {
            "answer": answer,
            "sources": sources  # e.g. ["nhs_diabetes.pdf", "nhs_hypertension.pdf"]
        }

    except Exception as e:
        print(f"[rag_pipeline] Error: {e}")
        return {
            "answer": "Something went wrong. Please try again.",
            "sources": []
        }