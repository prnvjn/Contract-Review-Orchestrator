from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class Alarm(BaseModel):
    alarm_type: str
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    context: Dict[str, Any]
    message: str
    recommended_action: str

def trigger_alarm(alarm_type: str, context: Dict[str, Any], message: str) -> Alarm:
    """
    Produces a structured Alarm output.
    """
    severity_map = {
        "INVALID_DOCUMENT": "MEDIUM",
        "FINANCIAL_THRESHOLD_EXCEEDED": "HIGH",
        "LEGAL_ADVICE_DETECTED": "CRITICAL",
        "EXTRACTION_FAILURE": "MEDIUM"
    }
    
    action_map = {
        "INVALID_DOCUMENT": "Reject input and notify user to upload a valid real estate contract.",
        "FINANCIAL_THRESHOLD_EXCEEDED": "Halt automated sync. Escalating to Human-in-the-Loop (HITL) for manual review.",
        "LEGAL_ADVICE_DETECTED": "Block output. Scrub sensitive phrases and re-run extraction with stricter penalty.",
        "EXTRACTION_FAILURE": "Retry extraction once; if it fails again, flag for manual entry."
    }
    
    return Alarm(
        alarm_type=alarm_type,
        severity=severity_map.get(alarm_type, "LOW"),
        context=context,
        message=message,
        recommended_action=action_map.get(alarm_type, "Log error and await developer review.")
    )
