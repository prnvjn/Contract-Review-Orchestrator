from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date

class Milestone(BaseModel):
    name: str = Field(..., description="The name of the milestone (e.g., 'Inspection Contingency')")
    due_date: date = Field(..., description="The date the milestone is due")
    value: Optional[float] = Field(None, description="The financial value associated with this milestone, if any")

class ContractExtraction(BaseModel):
    """
    Schema for extracting key information from a real estate contract.
    """
    property_address: str = Field(..., description="The full address of the property")
    purchase_price: float = Field(..., description="The total purchase price of the property")
    buyer_names: List[str] = Field(..., description="List of names of the buyers")
    seller_names: List[str] = Field(..., description="List of names of the sellers")
    closing_date: date = Field(..., description="The agreed-upon closing date")
    earnest_money_deposit: float = Field(..., description="The amount of the earnest money deposit")
    
    milestones: List[Milestone] = Field(
        default_factory=list, 
        description="Key dates and contingencies extracted from the contract"
    )

    @validator("purchase_price", "earnest_money_deposit")
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price and deposit must be positive values")
        return v
