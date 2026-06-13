from pypdf import PdfReader
import io
import os
import tempfile
from typing import Optional
from app.core.config import settings

def extract_text_from_pdf_pypdf(file_content: bytes) -> Optional[str]:
    """
    Standard extraction using pypdf.
    """
    try:
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error parsing with pypdf: {e}")
        return None

async def extract_text_from_pdf_llamaparse(file_content: bytes) -> Optional[str]:
    """
    Advanced extraction using LlamaParse for complex documents.
    """
    if not settings.LLAMA_CLOUD_API_KEY:
        print("Llama Cloud API Key missing. Falling back to pypdf.")
        return extract_text_from_pdf_pypdf(file_content)

    try:
        from llama_parse import LlamaParse
        
        # LlamaParse often works best with a physical file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        parser = LlamaParse(
            api_key=settings.LLAMA_CLOUD_API_KEY,
            result_type="text",  # can also use "markdown" for table support
            verbose=True
        )
        
        documents = await parser.aload_data(tmp_path)
        os.remove(tmp_path)
        
        if documents:
            return "\n".join([doc.text for doc in documents])
        return None
    except Exception as e:
        print(f"Error parsing with LlamaParse: {e}")
        return extract_text_from_pdf_pypdf(file_content)

async def extract_text_from_pdf(file_content: bytes) -> Optional[str]:
    """
    Orchestrates extraction based on the configured PARSER_TYPE.
    """
    if settings.PARSER_TYPE == "llamaparse":
        return await extract_text_from_pdf_llamaparse(file_content)
    return extract_text_from_pdf_pypdf(file_content)
