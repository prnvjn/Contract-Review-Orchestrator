from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes import (
    validate_preflight_node,
    extract_contract_node,
    verify_mls_node,
    check_safety_node,
    sync_crm_node
)

def create_workflow():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("validate_preflight", validate_preflight_node)
    workflow.add_node("extract_contract", extract_contract_node)
    workflow.add_node("verify_mls", verify_mls_node)
    workflow.add_node("check_safety", check_safety_node)
    workflow.add_node("sync_crm", sync_crm_node)

    # Set Entry Point
    workflow.set_entry_point("validate_preflight")

    # Add Edges
    def route_preflight(state: AgentState):
        if state["status"] == "failed":
            return END
        return "extract_contract"

    workflow.add_conditional_edges(
        "validate_preflight",
        route_preflight,
        {
            "extract_contract": "extract_contract",
            END: END
        }
    )

    def route_extraction(state: AgentState):
        if state["status"] == "failed":
            return END
        return "verify_mls"

    workflow.add_conditional_edges(
        "extract_contract",
        route_extraction,
        {
            "verify_mls": "verify_mls",
            END: END
        }
    )

    workflow.add_edge("verify_mls", "check_safety")

    # Conditional Logic for Safety Check
    def route_after_safety(state: AgentState):
        if state["status"] == "approved":
            return "sync_crm"
        return END

    workflow.add_conditional_edges(
        "check_safety",
        route_after_safety,
        {
            "sync_crm": "sync_crm",
            END: END
        }
    )

    # Edge from Sync to End
    workflow.add_edge("sync_crm", END)

    return workflow.compile()

# Export the compiled graph
app_graph = create_workflow()
