from typing import TypedDict, List, Dict, Any, Optional
from app.schemas.contract import ContractExtraction

class AgentState(TypedDict):
    # The raw text of the contract
    raw_text: str
    
    # Metadata for tracking
    request_id: str
    parent_transaction_id: Optional[str]
    
    # The data extracted by the LLM
    extraction: Optional[ContractExtraction]
    
    # Tool outputs
    mls_verification: Optional[Dict[str, Any]]
    crm_sync_result: Optional[Dict[str, Any]]
    
    # Safety and Guardrail results
    guardrail_results: Dict[str, Any]
    
    # Control flow
    next_node: str
    iteration_count: int
    errors: List[str]
    status: str # pending, approved, blocked, completed, failed
