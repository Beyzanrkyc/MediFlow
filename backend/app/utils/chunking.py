def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks so context isn't
    lost at chunk boundaries.
    """
    words = text.split()
    chunks = []

    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap  # step back by overlap amount

    return chunks
