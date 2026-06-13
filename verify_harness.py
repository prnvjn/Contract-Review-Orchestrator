import asyncio
import uuid
from datetime import date
from app.graph.workflow import app_graph
from app.schemas.contract import ContractExtraction
from app.core.database import init_db, get_session
from app.db.models import ContractRequest

async def test_harness_scenarios():
    print("🧪 Starting Safety Harness Verification...")
    init_db()
    
    # --- Scenario 1: Financial Threshold (BLOCK) ---
    print("\n💵 Scenario 1: $10M Transaction (Should BLOCK)")
    state_1 = {
        "raw_text": "High value contract for 10 million dollars.",
        "request_id": str(uuid.uuid4()),
        "parent_transaction_id": "TEST-HIGH-VALUE",
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
        "status": "extracted",
        "next_node": "check_safety"
    }
    
    # We skip to check_safety to isolate the harness logic
    final_1 = await app_graph.ainvoke(state_1)
    print(f"Result Status: {final_1['status']}")
    print(f"Alarms Triggered: {[a.alarm_type for a in final_1['alarms']]}")
    
    if final_1['status'] == 'blocked' and any(a.alarm_type == "FINANCIAL_THRESHOLD_EXCEEDED" for a in final_1['alarms']):
        print("✅ Scenario 1: PASSED")
    else:
        print("❌ Scenario 1: FAILED")

    # --- Scenario 2: Legal Advice (FAIL) ---
    print("\n⚖️ Scenario 2: Unauthorized Legal Advice (Should FAIL)")
    state_2 = {
        "raw_text": "Illegal contract text.",
        "request_id": str(uuid.uuid4()),
        "parent_transaction_id": "TEST-LEGAL-ADVICE",
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
        "status": "extracted",
        "next_node": "check_safety"
    }
    
    final_2 = await app_graph.ainvoke(state_2)
    print(f"Result Status: {final_2['status']}")
    print(f"Alarms Triggered: {[a.alarm_type for a in final_2['alarms']]}")

    if final_2['status'] == 'failed' and any(a.alarm_type == "LEGAL_ADVICE_DETECTED" for a in final_2['alarms']):
        print("✅ Scenario 2: PASSED")
    else:
        print("❌ Scenario 2: FAILED")

if __name__ == "__main__":
    asyncio.run(test_harness_scenarios())
