from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session
from app.core.database import init_db, get_session
from app.db.models import ContractRequest
from app.graph.workflow import app_graph
import uuid
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="ContractReviewOrchestrator API")

@app.on_event("startup")
def on_startup():
    init_db()

class ExtractionRequest(BaseModel):
    raw_text: str
    parent_transaction_id: Optional[str] = None

@app.post("/extract")
async def trigger_extraction(request: ExtractionRequest, db: Session = Depends(get_session)):
    request_id = str(uuid.uuid4())
    
    # 1. Save initial request to DB
    new_request = ContractRequest(
        id=uuid.UUID(request_id),
        document_id=f"doc_{request_id[:8]}",
        parent_transaction_id=request.parent_transaction_id,
        raw_text=request.raw_text,
        status="pending"
    )
    db.add(new_request)
    db.commit()

    # 2. Run the LangGraph Workflow
    initial_state = {
        "raw_text": request.raw_text,
        "request_id": request_id,
        "parent_transaction_id": request.parent_transaction_id,
        "extraction": None,
        "mls_verification": None,
        "crm_sync_result": None,
        "guardrail_results": {},
        "next_node": "",
        "iteration_count": 0,
        "errors": [],
        "status": "pending"
    }

    try:
        final_state = await app_graph.ainvoke(initial_state)
        
        # 3. Update DB with results
        db_request = db.get(ContractRequest, uuid.UUID(request_id))
        db_request.status = final_state["status"]
        if final_state["extraction"]:
            db_request.extracted_data = final_state["extraction"].model_dump()
        db_request.updated_at = db_request.updated_at # Trigger update
        db.add(db_request)
        db.commit()
        db.refresh(db_request)

        return {
            "request_id": request_id,
            "status": final_state["status"],
            "extraction": final_state["extraction"],
            "errors": final_state["errors"]
        }
    except Exception as e:
        db_request = db.get(ContractRequest, uuid.UUID(request_id))
        db_request.status = "failed"
        db.add(db_request)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}
