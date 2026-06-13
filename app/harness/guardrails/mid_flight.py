from typing import Dict, Any

FINANCIAL_THRESHOLD = 5000000.0 # $5M

def check_financial_threshold(purchase_price: float) -> Dict[str, Any]:
    """
    Blocks automated tool calls for high-value transactions.
    """
    if purchase_price > FINANCIAL_THRESHOLD:
        return {
            "action": "BLOCK",
            "reason": f"Transaction value ${purchase_price:,.2f} exceeds threshold ${FINANCIAL_THRESHOLD:,.2f}. Manual HITL approval required.",
            "requires_hitl": True
        }
    
    return {
        "action": "PROCEED",
        "requires_hitl": False
    }
