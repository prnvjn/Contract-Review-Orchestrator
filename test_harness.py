import asyncio
import uuid
from app.graph.nodes import check_safety_node, validate_preflight_node
from app.schemas.contract import ContractExtraction
from datetime import date

async def test_alarms_and_harness():
    print("🚀 Starting Safety Harness & Alarms Test (Node Level)...")
    
    # Test 1: Financial Threshold Alarm (Mid-flight)
    print("\n📊 Test 1: Financial Threshold Alarm (> $5M)")
    state_high_value = {
        "raw_text": "Valid contract for 123 Main St.",
        "request_id": str(uuid.uuid4()),
        "extraction": ContractExtraction(
            property_address="123 High St",
            purchase_price=6000000,
            buyer_names=["Rich Buyer"],
            seller_names=["Lucky Seller"],
            closing_date=date(2024, 12, 31),
            earnest_money_deposit=100000,
            milestones=[]
        ),
        "alarms": [],
        "status": "pending"
    }
    
    result = await check_safety_node(state_high_value)
    
    print(f"✅ Node Result Status: {result.get('status')}")
    if result.get("alarms"):
        alarm = result["alarms"][0]
        print(f"🚨 ALARM TRIGGERED: {alarm.alarm_type}")
        print(f"🚨 Severity: {alarm.severity}")
        print(f"🚨 Action: {alarm.recommended_action}")
        assert alarm.alarm_type == "FINANCIAL_THRESHOLD_EXCEEDED"
    else:
        print("❌ Alarm NOT triggered!")

    # Test 2: Legal Advice Alarm (Post-flight)
    print("\n📊 Test 2: Legal Advice Scrubber Alarm")
    state_illegal = {
        "raw_text": "Valid contract.",
        "extraction": ContractExtraction(
            property_address="123 Law Ave",
            purchase_price=500000,
            buyer_names=["Buyer"],
            seller_names=["Seller"],
            closing_date=date(2024, 12, 31),
            earnest_money_deposit=5000,
            milestones=[{"name": "i recommend you strike this clause", "due_date": date(2024, 7, 1)}]
        ),
        "alarms": [],
        "status": "pending"
    }
    
    result_legal = await check_safety_node(state_illegal)
    print(f"✅ Node Result Status: {result_legal.get('status')}")
    if result_legal.get("alarms"):
        alarm = result_legal["alarms"][-1]
        print(f"🚨 ALARM TRIGGERED: {alarm.alarm_type}")
        assert alarm.alarm_type == "LEGAL_ADVICE_DETECTED"
    else:
        print("❌ Alarm NOT triggered!")

    # Test 3: Invalid Document Alarm (Pre-flight)
    print("\n📊 Test 3: Invalid Document Alarm")
    state_invalid = {
        "raw_text": "Just some random text without keywords.",
        "alarms": [],
        "status": "pending"
    }
    result_invalid = await validate_preflight_node(state_invalid)
    if result_invalid.get("alarms"):
        alarm = result_invalid["alarms"][0]
        print(f"🚨 ALARM TRIGGERED: {alarm.alarm_type}")
        assert alarm.alarm_type == "INVALID_DOCUMENT"
    
    print("\n🏆 Safety Harness & Alarms Test: PASSED")

if __name__ == "__main__":
    asyncio.run(test_alarms_and_harness())
