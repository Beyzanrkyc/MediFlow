import requests
import pdfplumber
import io

PDF_URLS = {
    "ng136": "https://www.nice.org.uk/guidance/ng136/resources/hypertension-in-adults-diagnosis-and-management-pdf",
    "ng28":  "https://www.nice.org.uk/guidance/ng28/resources/type-2-diabetes-in-adults-management-pdf",
}

def extract_pdf_text(url, source_name):
    """Download and extract text from a NICE PDF guideline."""
    print(f"📄 Downloading {source_name}...")
    response = requests.get(url)
    
    with pdfplumber.open(io.BytesIO(response.content)) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)

    return "\n\n".join(pages)

# pip install pdfplumber