from typing import TypedDict, List, Dict, Any, Optional
from app.schemas.contract import ContractExtraction
from app.harness.alarms import Alarm

class AgentState(TypedDict):
    # The raw text of the contract (Material Handling)
    raw_text: str
    
    # Metadata for tracking
    request_id: str
    parent_transaction_id: Optional[str]
    
    # The data extracted by the LLM (Material)
    extraction: Optional[ContractExtraction]
    
    # Tool outputs (Material)
    mls_verification: Optional[Dict[str, Any]]
    crm_sync_result: Optional[Dict[str, Any]]
    
    # Safety and Guardrail results
    guardrail_results: Dict[str, Any]
    
    # Structured Alarms
    alarms: List[Alarm]
    
    # Control flow (Checkpoints)
    next_node: str
    iteration_count: int
    errors: List[str]
    status: str # pending, validated, approved, blocked, completed, failed
