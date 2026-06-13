from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON
import uuid

# Clear metadata to prevent Streamlit reload collisions
if hasattr(SQLModel, "metadata"):
    SQLModel.metadata.clear()

class RequestBase(SQLModel):
    document_id: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContractRequest(RequestBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    parent_transaction_id: Optional[str] = Field(default=None, index=True)
    raw_text: str
    extracted_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    alarms: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    token_usage_total: int = 0

class ToolCall(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    request_id: uuid.UUID = Field(foreign_key="contractrequest.id")
    tool_name: str
    input_payload: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    output_payload: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    status: str = "success"
    executed_at: datetime = Field(default_factory=datetime.utcnow)

class ObservabilityLog(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    request_id: uuid.UUID = Field(foreign_key="contractrequest.id")
    node_name: str
    log_level: str = "INFO"
    message: str
    details: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
