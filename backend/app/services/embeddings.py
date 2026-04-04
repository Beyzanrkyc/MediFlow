from sentence_transformers import SentenceTransformer

# Load model once (downloads on first run)
model = SentenceTransformer("all-MiniLM-L6-v2")


def get_embedding(text: str):
    """
    Generate embedding for a given text using a local model.
    Returns a list (compatible with ChromaDB).
    """
    return model.encode(text).tolist()