import streamlit as st
import asyncio
import uuid
from app.graph.workflow import app_graph
from app.core.database import Session, engine
from app.db.models import ContractRequest
import json

st.set_page_config(page_title="ContractReviewOrchestrator", layout="wide")

st.title("📑 ContractReviewOrchestrator")
st.subheader("Agentic Real Estate Milestone Extraction")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Input Contract")
    raw_text = st.text_area(
        "Paste Contract Text Here", 
        height=400,
        placeholder="AGREEMENT OF SALE...\nThis agreement is made between..."
    )
    parent_tx = st.text_input("Parent Transaction ID (Optional)", value="TX-999")
    
    if st.button("🚀 Run Orchestrator", use_container_width=True):
        if not raw_text:
            st.error("Please paste a contract first!")
        else:
            with st.status("Running Agentic Pipeline...", expanded=True) as status:
                st.write("Initializing state...")
                request_id = str(uuid.uuid4())
                initial_state = {
                    "raw_text": raw_text,
                    "request_id": request_id,
                    "parent_transaction_id": parent_tx,
                    "extraction": None,
                    "mls_verification": None,
                    "crm_sync_result": None,
                    "guardrail_results": {},
                    "next_node": "",
                    "iteration_count": 0,
                    "errors": [],
                    "status": "pending"
                }
                
                # Run the graph
                st.write("Executing LangGraph nodes...")
                final_state = asyncio.run(app_graph.ainvoke(initial_state))
                
                status.update(label="Workflow Complete!", state="complete", expanded=False)
                
                st.session_state.final_state = final_state
                st.success(f"Status: {final_state['status'].upper()}")

with col2:
    st.header("Orchestrator Results")
    
    if "final_state" in st.session_state:
        state = st.session_state.final_state
        
        # Display Extraction
        if state["extraction"]:
            st.success("✅ Extraction Successful")
            st.json(state["extraction"].model_dump())
            
            st.divider()
            st.subheader("Milestones")
            for m in state["extraction"].milestones:
                st.info(f"📅 **{m.name}**: {m.due_date}")
        
        # Display Guardrails
        st.divider()
        st.subheader("Safety Guardrails")
        gr = state["guardrail_results"]
        if "mid_flight" in gr:
            action = gr["mid_flight"]["action"]
            color = "green" if action == "PROCEED" else "red"
            st.markdown(f"**Financial Circuit Breaker:** :{color}[{action}]")
        
        if "post_flight" in gr:
            safe = gr["post_flight"]["is_safe"]
            color = "green" if safe else "red"
            st.markdown(f"**Legal Advice Scrubber:** :{color}[{'SAFE' if safe else 'VIOLATION'}]")
            
        # Display Tool Outputs
        if state["mls_verification"]:
            st.write("**MLS Verification:** ✅ Verified" if state["mls_verification"]["status"] == "verified" else "**MLS Verification:** ❌ Not Found")
        
        if state["crm_sync_result"]:
            st.write(f"**CRM Sync:** {state['crm_sync_result']['message']}")
            
        if state["errors"]:
            st.error(f"Errors encountered: {', '.join(state['errors'])}")
    else:
        st.info("Paste a contract and click 'Run Orchestrator' to see results.")

st.sidebar.markdown("### System Telemetry")
if "final_state" in st.session_state:
    st.sidebar.write(f"Request ID: `{st.session_state.final_state['request_id']}`")
    st.sidebar.write(f"Final Status: `{st.session_state.final_state['status']}`")
else:
    st.sidebar.write("No active session.")
