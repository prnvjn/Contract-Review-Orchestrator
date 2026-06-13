import asyncio
import uuid
from app.graph.workflow import app_graph

async def test_workflow():
    print("🚀 Starting LangGraph Workflow Test...")
    
    initial_state = {
        "raw_text": "This is a Purchase Agreement for 123 Main St. The price is $450,000.",
        "request_id": str(uuid.uuid4()),
        "parent_transaction_id": "tx_test_123",
        "extraction": None,
        "mls_verification": None,
        "crm_sync_result": None,
        "guardrail_results": {},
        "next_node": "",
        "iteration_count": 0,
        "errors": [],
        "status": "pending"
    }

    print("📊 Running graph...")
    final_state = await app_graph.ainvoke(initial_state)
    
    print(f"✅ Workflow Status: {final_state['status']}")
    print(f"🏠 Property Address: {final_state['extraction'].property_address}")
    print(f"💰 Purchase Price: ${final_state['extraction'].purchase_price}")
    
    if final_state["status"] == "completed":
        print("🏆 End-to-End Workflow Test: PASSED")
    else:
        print(f"❌ Workflow ended with status: {final_state['status']}")
        print(f"❌ Errors: {final_state['errors']}")

if __name__ == "__main__":
    asyncio.run(test_workflow())
