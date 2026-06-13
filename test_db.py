from app.core.database import Session, engine, init_db
from app.db.models import ContractRequest, ToolCall, ObservabilityLog
import uuid

def test_database_integrity():
    print("🚀 Starting Database Integrity Test...")
    
    # 1. Initialize (already done, but safe to call)
    init_db()
    
    with Session(engine) as session:
        # 2. Create a dummy ContractRequest
        request_id = uuid.uuid4()
        new_request = ContractRequest(
            id=request_id,
            document_id="doc_123",
            parent_transaction_id="tx_987",
            raw_text="This is a test contract for 123 Main St.",
            extracted_data={"property_address": "123 Main St", "price": 450000}
        )
        session.add(new_request)
        
        # 3. Create a linked ToolCall
        new_tool_call = ToolCall(
            request_id=request_id,
            tool_name="mls_verify",
            input_payload={"address": "123 Main St"},
            output_payload={"verified": True, "apn": "001-002-003"}
        )
        session.add(new_tool_call)
        
        # 4. Create an ObservabilityLog
        new_log = ObservabilityLog(
            request_id=request_id,
            node_name="extraction_node",
            message="Successfully extracted address and price."
        )
        session.add(new_log)
        
        session.commit()
        print("✅ Data successfully committed.")

        # 5. Query and Verify
        retrieved_request = session.get(ContractRequest, request_id)
        print(f"📊 Retrieved Request Status: {retrieved_request.status}")
        print(f"📊 Extracted Data JSON Check: {retrieved_request.extracted_data['property_address']}")
        
        assert retrieved_request.document_id == "doc_123"
        assert retrieved_request.extracted_data["price"] == 450000
        
    print("\n🏆 Layer 2 Database Test: PASSED")

if __name__ == "__main__":
    test_database_integrity()
