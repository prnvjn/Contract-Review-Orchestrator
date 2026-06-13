from pypdf import PdfReader
import io
from typing import Optional

def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
    """
    Extracts raw text from a PDF file provided as bytes.
    """
    try:
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None
