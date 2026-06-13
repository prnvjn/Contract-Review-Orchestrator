import asyncio
import uuid
from datetime import date
from app.graph.nodes import check_safety_node
from app.schemas.contract import ContractExtraction

async def verify_harness_logic():
    print("🧪 Verifying Harness Guardrail Logic Directly...")
    
    # --- Scenario 1: Financial Threshold (BLOCK) ---
    print("\n💵 Scenario 1: $10M Transaction (Should BLOCK)")
    state_1 = {
        "raw_text": "High value contract for 10 million dollars.",
        "request_id": str(uuid.uuid4()),
        "extraction": ContractExtraction(
            property_address="999 Whale Ave",
            purchase_price=10000000, # 10 Million
            buyer_names=["Rich Buyer"],
            seller_names=["Lucky Seller"],
            closing_date=date(2026, 1, 1),
            earnest_money_deposit=100000,
            milestones=[]
        ),
        "alarms": [],
        "guardrail_results": {},
        "status": "extracted"
    }
    
    result_1 = await check_safety_node(state_1)
    print(f"Result Status: {result_1['status']}")
    # Handle both object and dict for resilience in test
    alarm_types_1 = [a.alarm_type if hasattr(a, 'alarm_type') else a['alarm_type'] for a in result_1['alarms']]
    print(f"Alarms Triggered: {alarm_types_1}")
    
    if result_1['status'] == 'blocked' and "FINANCIAL_THRESHOLD_EXCEEDED" in alarm_types_1:
        print("✅ Scenario 1: PASSED")
    else:
        print("❌ Scenario 1: FAILED")

    # --- Scenario 2: Legal Advice (FAIL) ---
    print("\n⚖️ Scenario 2: Unauthorized Legal Advice (Should FAIL)")
    state_2 = {
        "raw_text": "Illegal contract text.",
        "request_id": str(uuid.uuid4()),
        "extraction": ContractExtraction(
            property_address="123 Law St",
            purchase_price=100000,
            buyer_names=["Buyer"],
            seller_names=["Seller"],
            closing_date=date(2026, 1, 1),
            earnest_money_deposit=1000,
            # Malicious extraction containing legal advice
            milestones=[{"name": "I recommend you strike this clause", "due_date": date(2026, 1, 1), "value": None}]
        ),
        "alarms": [],
        "guardrail_results": {},
        "status": "extracted"
    }
    
    result_2 = await check_safety_node(state_2)
    print(f"Result Status: {result_2['status']}")
    alarm_types_2 = [a.alarm_type if hasattr(a, 'alarm_type') else a['alarm_type'] for a in result_2['alarms']]
    print(f"Alarms Triggered: {alarm_types_2}")

    if result_2['status'] == 'failed' and "LEGAL_ADVICE_DETECTED" in alarm_types_2:
        print("✅ Scenario 2: PASSED")
    else:
        print("❌ Scenario 2: FAILED")

if __name__ == "__main__":
    asyncio.run(verify_harness_logic())
