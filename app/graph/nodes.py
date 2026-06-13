import instructor
from openai import OpenAI
from anthropic import Anthropic
from app.core.config import settings
from app.graph.state import AgentState
from app.schemas.contract import ContractExtraction
from app.harness.guardrails.pre_flight import validate_document
from app.harness.guardrails.mid_flight import check_financial_threshold
from app.harness.guardrails.post_flight import scrub_legal_advice
from app.harness.alarms import trigger_alarm
from app.tools.mls_client import mls_client
from app.tools.crm_client import crm_client
from datetime import date
import json

# Initialize Clients
openai_client = instructor.patch(OpenAI(api_key=settings.OPENAI_API_KEY or "mock_key"))
anthropic_client = instructor.from_anthropic(Anthropic(api_key=settings.ANTHROPIC_API_KEY or "mock_key"))

async def validate_preflight_node(state: AgentState):
    """
    GUARDRAIL: Checks if the document is valid before starting extraction.
    ALARM: Triggers INVALID_DOCUMENT alarm on failure.
    """
    result = validate_document(state["raw_text"])
    
    if not result["is_valid"]:
        alarm = trigger_alarm(
            "INVALID_DOCUMENT", 
            {"raw_text_length": len(state["raw_text"])},
            result["error"]
        )
        return {
            "status": "failed",
            "alarms": state.get("alarms", []) + [alarm],
            "errors": [result["error"]],
            "next_node": "end"
        }
    
    return {"status": "validated", "next_node": "extract"}

async def extract_contract_node(state: AgentState):
    """
    MATERIAL HANDLING: Calls the LLM to extract contract details.
    SWAPPABLE AGENT: Supports switching between OpenAI and Anthropic.
    """
    provider = settings.LLM_PROVIDER
    
    # Check for keys before attempting live call
    if provider == "openai" and not settings.OPENAI_API_KEY:
        # Mock for demo if no key
        return {
            "extraction": ContractExtraction(
                property_address="123 OpenAI St, GPT City",
                purchase_price=450000,
                buyer_names=["GPT User"],
                seller_names=["OpenAI Judge"],
                closing_date=date(2024, 12, 31),
                earnest_money_deposit=5000,
                milestones=[]
            ),
            "status": "extracted",
            "next_node": "verify_mls"
        }
    
    if provider == "anthropic" and not settings.ANTHROPIC_API_KEY:
        # Mock for demo if no key
        return {
            "extraction": ContractExtraction(
                property_address="456 Swappable Lane, Claude City",
                purchase_price=1200000,
                buyer_names=["Claude User"],
                seller_names=["Hackathon Judge"],
                closing_date=date(2025, 1, 1),
                earnest_money_deposit=20000,
                milestones=[]
            ),
            "status": "extracted",
            "next_node": "verify_mls"
        }

    try:
        if provider == "openai":
            extraction = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                response_model=ContractExtraction,
                messages=[
                    {"role": "system", "content": "Extract real estate contract details accurately."},
                    {"role": "user", "content": state["raw_text"]}
                ]
            )
        elif provider == "anthropic":
            extraction = anthropic_client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4096,
                response_model=ContractExtraction,
                messages=[
                    {"role": "user", "content": f"Extract real estate contract details accurately from this text: {state['raw_text']}"}
                ]
            )
            
        return {"extraction": extraction, "status": "extracted", "next_node": "verify_mls"}
    except Exception as e:
        alarm = trigger_alarm("EXTRACTION_FAILURE", {"error": str(e)}, f"LLM ({provider}) failed to produce valid schema.")
        return {
            "errors": [str(e)], 
            "status": "failed", 
            "alarms": state.get("alarms", []) + [alarm],
            "next_node": "end"
        }

async def verify_mls_node(state: AgentState):
    """
    MATERIAL HANDLING: Verifies property data using the MLS tool.
    """
    address = state["extraction"].property_address
    result = await mls_client.verify_parcel_data(address)
    
    return {
        "mls_verification": result,
        "next_node": "check_safety"
    }

async def check_safety_node(state: AgentState):
    """
    GUARDRAIL (Mid-flight): Check financial thresholds.
    GUARDRAIL (Post-flight): Scrub legal advice.
    ALARM: Triggers alarms for violations.
    """
    price = state["extraction"].purchase_price
    mid_flight = check_financial_threshold(price)
    alarms = state.get("alarms", [])
    
    if mid_flight["action"] == "BLOCK":
        alarm = trigger_alarm(
            "FINANCIAL_THRESHOLD_EXCEEDED", 
            {"price": price},
            mid_flight["reason"]
        )
        return {
            "status": "blocked",
            "alarms": alarms + [alarm],
            "guardrail_results": {"mid_flight": mid_flight},
            "next_node": "end"
        }
    
    # Post-flight: Check for legal advice
    post_flight = scrub_legal_advice(str(state["extraction"].model_dump()))
    
    if not post_flight["is_safe"]:
        alarm = trigger_alarm(
            "LEGAL_ADVICE_DETECTED", 
            {"violations": post_flight["violations"]},
            post_flight["error"]
        )
        return {
            "status": "failed",
            "alarms": alarms + [alarm],
            "errors": [post_flight["error"]],
            "guardrail_results": {"post_flight": post_flight},
            "next_node": "end"
        }
    
    return {
        "status": "approved",
        "guardrail_results": {"mid_flight": mid_flight, "post_flight": post_flight},
        "next_node": "sync_crm"
    }

async def sync_crm_node(state: AgentState):
    """
    MATERIAL HANDLING: Final sync to external CRM.
    """
    result = await crm_client.sync_transaction_milestones(
        state["request_id"],
        state["extraction"].model_dump()
    )
    
    return {
        "crm_sync_result": result,
        "status": "completed",
        "next_node": "end"
    }
