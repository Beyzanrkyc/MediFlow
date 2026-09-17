"""
Ingest NHS/NICE clinical guideline PDFs into the ChromaDB vector store.

Two ways to feed it documents:
  1. (Primary, recommended) Drop PDF files into backend/data/nhs_guidelines/
     and this script will pick up every .pdf in there.
  2. (Optional) Add real, direct-download PDF URLs to PDF_URLS below — the
     ones a scraper can find on a guideline's public "resources" page.
     NOTE: NICE resource URLs embed a numeric ID that changes per file and
     isn't guessable from the guideline name, so there are no defaults here.
     Grab a real link from e.g. https://www.nice.org.uk/guidance/<NG-code>/resources
     if you want this path.

Run from the `backend/` directory (so the `app` package resolves):
    python -m scripts.ingest_data
"""
import glob
import io
import os
import sys

import requests
import pdfplumber

# Make `app.*` importable when this script is run directly.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.chunking import chunk_text
from app.services.embeddings import get_embedding
from app.services.vector_db import add_documents, get_collection_size

# Optional: source_name -> direct PDF URL. Leave empty and just drop PDFs
# into DATA_DIR if you don't have stable URLs to hand.
PDF_URLS = {
    # "ng136": "https://www.nice.org.uk/guidance/ng136/resources/<real-file-slug>.pdf",
}

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nhs_guidelines")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MediFlowAI-Ingest/1.0)"
}


def extract_pdf_text_from_bytes(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages = [page.extract_text() for page in pdf.pages]
    return "\n\n".join(p for p in pages if p)


def download_pdf(url: str, source_name: str) -> bytes:
    """Download a PDF and cache it locally so re-runs don't hit the network."""
    os.makedirs(DATA_DIR, exist_ok=True)
    cache_path = os.path.join(DATA_DIR, f"{source_name}.pdf")

    if os.path.exists(cache_path):
        print(f"📄 Using cached {source_name}.pdf")
        with open(cache_path, "rb") as f:
            return f.read()

    print(f"📄 Downloading {source_name}...")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    with open(cache_path, "wb") as f:
        f.write(response.content)
    return response.content


def ingest_pdf(source_name: str, pdf_bytes: bytes) -> int:
    """Extract, chunk, embed, and store one PDF. Returns number of chunks added."""
    try:
        text = extract_pdf_text_from_bytes(pdf_bytes)
    except Exception as e:
        print(f"⚠️  Skipping {source_name}: failed to parse PDF ({e})")
        return 0

    if not text.strip():
        print(f"⚠️  Skipping {source_name}: no extractable text (likely a scanned/image PDF — try OCR first)")
        return 0

    chunks = chunk_text(text)
    docs = [
        {"text": chunk, "embedding": get_embedding(chunk), "source": source_name}
        for chunk in chunks
    ]
    add_documents(docs)
    print(f"✅ {source_name}: added {len(docs)} chunks")
    return len(docs)


def main():
    print(f"Collection size before ingest: {get_collection_size()}")
    total = 0

    # 1. Local PDFs already sitting in backend/data/nhs_guidelines/
    os.makedirs(DATA_DIR, exist_ok=True)
    local_pdfs = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    url_backed_names = set(PDF_URLS.keys())

    for path in local_pdfs:
        source_name = os.path.splitext(os.path.basename(path))[0]
        if source_name in url_backed_names:
            continue  # will be handled (and re-used from cache) below
        with open(path, "rb") as f:
            total += ingest_pdf(source_name, f.read())

    # 2. Anything configured with a URL (downloads/caches into DATA_DIR too)
    for source_name, url in PDF_URLS.items():
        try:
            pdf_bytes = download_pdf(url, source_name)
        except Exception as e:
            print(f"⚠️  Skipping {source_name}: download failed ({e})")
            continue
        total += ingest_pdf(source_name, pdf_bytes)

    if not local_pdfs and not PDF_URLS:
        print(f"\nNo PDFs found. Drop some guideline PDFs into {DATA_DIR} and re-run.")

    print(f"\nIngested {total} chunks total.")
    print(f"Collection size after ingest: {get_collection_size()}")


if __name__ == "__main__":
    main()
