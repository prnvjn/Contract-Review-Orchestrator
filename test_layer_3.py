import asyncio
from app.schemas.contract import ContractExtraction, Milestone
from app.tools.mls_client import mls_client
from app.tools.crm_client import crm_client
from datetime import date

async def test_layer_3():
    print("🚀 Starting Layer 3: Schemas and Tools Test...")

    # 1. Test Schema Validation
    print("📋 Testing Pydantic Schema...")
    try:
        extraction = ContractExtraction(
            property_address="123 Main St, New York, NY",
            purchase_price=500000,
            buyer_names=["John Doe"],
            seller_names=["Jane Smith"],
            closing_date=date(2023, 12, 31),
            earnest_money_deposit=10000,
            milestones=[
                Milestone(name="Inspection", due_date=date(2023, 7, 1))
            ]
        )
        print(f"✅ Schema valid: {extraction.property_address} at ${extraction.purchase_price}")
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return

    # 2. Test MLS Client (Mock)
    print("📋 Testing MLS Client (Mock)...")
    mls_result = await mls_client.verify_parcel_data("123 Main St")
    print(f"✅ MLS Result: {mls_result}")
    assert mls_result["status"] == "verified"

    # 3. Test CRM Client (Mock)
    print("📋 Testing CRM Client (Mock)...")
    crm_result = await crm_client.sync_transaction_milestones(
        "test_req_123", 
        extraction.model_dump()
    )
    print(f"✅ CRM Result: {crm_result}")
    assert crm_result["status"] == "success"

    print("\n🏆 Layer 3 Schemas and Tools Test: PASSED")

if __name__ == "__main__":
    asyncio.run(test_layer_3())
