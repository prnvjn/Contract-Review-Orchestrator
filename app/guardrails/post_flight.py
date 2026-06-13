import re
from typing import Dict, Any, List

# Blocklisted phrases that look like legal advice
LEGAL_ADVICE_PATTERNS = [
    r"you should",
    r"i recommend",
    r"we recommend",
    r"strike this",
    r"legally binding",
    r"consult an attorney",
    r"this is not legal advice" # ironically, sometimes used when giving advice
]

def scrub_legal_advice(text: str) -> Dict[str, Any]:
    """
    Sweeps output strings for blocklisted patterns to prevent unauthorized legal advice.
    """
    found_violations = []
    for pattern in LEGAL_ADVICE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            found_violations.append(pattern)
    
    if found_violations:
        return {
            "is_safe": False,
            "violations": found_violations,
            "error": "Output contains patterns indicative of unauthorized legal advice."
        }
    
    return {"is_safe": True, "violations": []}
