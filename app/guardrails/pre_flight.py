from typing import Dict, Any

def validate_document(raw_text: str) -> Dict[str, Any]:
    """
    Ensures the document is likely a real estate contract and within token limits.
    """
    # Simple keyword check for "Contract" or "Agreement"
    keywords = ["agreement", "contract", "purchase", "sale", "buyer", "seller"]
    text_lower = raw_text.lower()
    
    found_keywords = [kw for kw in keywords if kw in text_lower]
    
    if len(found_keywords) < 2:
        return {
            "is_valid": False,
            "error": "Document does not appear to be a real estate contract (missing key terms)."
        }
    
    # Simple token limit check (estimate: 1 word ~ 1.3 tokens)
    word_count = len(raw_text.split())
    if word_count > 10000:
        return {
            "is_valid": False,
            "error": f"Document is too large ({word_count} words). Please provide a shorter excerpt."
        }
    
    return {"is_valid": True, "error": None}
