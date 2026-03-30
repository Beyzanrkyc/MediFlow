import chromadb
import hashlib

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("nhs_guidelines")


def add_documents(docs):
    """Add documents to ChromaDB, skipping duplicates."""
    for doc in docs:
        doc_id = hashlib.md5(doc["text"].encode()).hexdigest()

        # Skip if already exists
        existing = collection.get(ids=[doc_id])
        if existing["ids"]:
            continue

        collection.add(
            documents=[doc["text"]],
            embeddings=[doc["embedding"]],
            metadatas=[{"source": doc.get("source", "unknown")}],
            ids=[doc_id]
        )


def query(query_embedding, n_results=5):
    """Query ChromaDB and return chunks with their sources."""
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        chunks = results["documents"][0]
        sources = [m["source"] for m in results["metadatas"][0]]

        return [{"text": chunk, "source": source}
                for chunk, source in zip(chunks, sources)]

    except Exception as e:
        print(f"[vector_db] Query failed: {e}")
        return []


def get_collection_size():
    """Useful for debugging — how many docs are stored?"""
    return collection.count()