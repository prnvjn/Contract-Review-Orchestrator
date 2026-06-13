import streamlit as st
import asyncio
import uuid
from app.graph.workflow import app_graph
from app.core.database import Session, engine, get_session, init_db
from app.db.models import ContractRequest
import json
import pandas as pd
from app.core.parser import extract_text_from_pdf
from app.core.config import settings

# Initialize Database
init_db()

st.set_page_config(page_title="ContractReviewOrchestrator", layout="wide")

st.title("📑 ContractReviewOrchestrator")

# Use tabs for Navigation
tab_orchestrator, tab_dashboard, tab_harness = st.tabs(["🚀 Orchestrator", "📊 Transaction Dashboard", "🛡️ Harness Audit Log"])

with tab_orchestrator:
    st.subheader("Agentic Real Estate Milestone Extraction")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Input Contract")
        
        input_method = st.radio("Choose Input Method:", ["Upload PDF", "Paste Text"])
        
        raw_text = ""
        if input_method == "Upload PDF":
            uploaded_file = st.file_uploader("Upload a Contract PDF", type=["pdf"])
            if uploaded_file:
                with st.spinner("Extracting text from PDF..."):
                    file_bytes = uploaded_file.read()
                    raw_text = asyncio.run(extract_text_from_pdf(file_bytes))
                    if raw_text:
                        st.success("Text extracted successfully!")
                        with st.expander("Show Extracted Text"):
                            st.text(raw_text[:1000] + "...")
                    else:
                        st.error("Failed to extract text from PDF.")
        else:
            raw_text = st.text_area(
                "Paste Contract Text Here", 
                height=400,
                placeholder="AGREEMENT OF SALE...\nThis agreement is made between..."
            )
        
        parent_tx = st.text_input("Parent Transaction ID (Optional)", value="TX-999")
        
        if st.button("🚀 Run Orchestrator", width="stretch"):
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
                    final_state = asyncio.run(app_graph.ainvoke(
                        initial_state, 
                        config={"recursion_limit": settings.RECURSION_LIMIT}
                    ))
                    
                    # Persist to DB
                    try:
                        db = next(get_session())
                        new_request = ContractRequest(
                            id=uuid.UUID(request_id),
                            document_id=f"doc_{request_id[:8]}",
                            parent_transaction_id=parent_tx,
                            raw_text=raw_text,
                            status=final_state["status"],
                            extracted_data=final_state["extraction"].model_dump() if final_state["extraction"] else None,
                            alarms=[a.model_dump() for a in final_state["alarms"]] if final_state["alarms"] else None
                        )
                        db.add(new_request)
                        db.commit()
                    except Exception as e:
                        st.warning(f"Failed to persist to database: {e}")

                    status.update(label="Workflow Complete!", state="complete", expanded=False)
                    
                    st.session_state.final_state = final_state
                    st.success(f"Status: {final_state['status'].upper()}")

    with col2:
        st.header("Orchestrator Results")
        
        if "final_state" in st.session_state:
            state = st.session_state.final_state
            
            # Display Extraction
            if state["extraction"]:
                ext = state["extraction"]
                st.success("✅ Extraction Successful")
                
                col_c, col_d = st.columns(2)
                with col_c:
                    st.write(f"📍 **Address:** {ext.property_address}")
                    st.write(f"💰 **Price:** ${ext.purchase_price:,.2f}")
                with col_d:
                    st.write(f"👥 **Buyers:** {', '.join(ext.buyer_names)}")
                    st.write(f"📅 **Closing:** {ext.closing_date}")
                
                st.divider()
                st.subheader("Milestones")
                if ext.milestones:
                    m_list = [
                        {
                            "Milestone": m.name, 
                            "Due Date": str(m.due_date),
                            "Value": f"${m.value:,.2f}" if m.value is not None else "—"
                        } 
                        for m in ext.milestones
                    ]
                    st.table(m_list)
                else:
                    st.info("No milestones detected.")
                
                with st.expander("View Raw Extraction"):
                    st.json(ext.model_dump())
            
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

with tab_dashboard:
    st.subheader("Historical Extractions & Milestones")
    
    # Session management for DB
    try:
        db = next(get_session())
        from sqlmodel import select
        requests = db.exec(select(ContractRequest).order_by(ContractRequest.created_at.desc())).all()
        
        if requests:
            # Prepare data for display
            data = []
            for r in requests:
                data.append({
                    "Transaction ID": r.parent_transaction_id,
                    "Status": r.status,
                    "Address": r.extracted_data.get("property_address") if r.extracted_data else "N/A",
                    "Price": f"${r.extracted_data.get('purchase_price'):,.2f}" if r.extracted_data and r.extracted_data.get('purchase_price') else "N/A",
                    "Created At": r.created_at.strftime("%Y-%m-%d %H:%M")
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            
            # Detail selection
            selected_tx = st.selectbox("Select Transaction to View Details", df["Transaction ID"].unique())
            if selected_tx:
                req = next(r for r in requests if r.parent_transaction_id == selected_tx)
                st.write(f"### Details for {selected_tx}")
                
                # Human-in-the-Loop Action Center
                if req.status not in ["completed", "rejected"]:
                    st.markdown("### 🛠️ Final Review Actions")
                    col_approve, col_reject = st.columns(2)
                    
                    with col_approve:
                        if st.button(f"✅ Approve {selected_tx}", use_container_width=True):
                            try:
                                req.status = "completed"
                                db.add(req)
                                db.commit()
                                st.success("Transaction approved.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Approval failed: {e}")
                    
                    with col_reject:
                        if st.button(f"❌ Reject {selected_tx}", use_container_width=True):
                            try:
                                req.status = "rejected"
                                db.add(req)
                                db.commit()
                                st.error("Transaction rejected.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Rejection failed: {e}")
                    
                    if req.status == "blocked":
                        st.warning("⚠️ Note: This is currently BLOCKED by the Financial Circuit Breaker.")
                else:
                    status_color = "green" if req.status == "completed" else "red"
                    st.markdown(f"**Final Decision:** :{status_color}[{req.status.upper()}]")
                
                if req.extracted_data:
                    ext = req.extracted_data
                    st.markdown("---")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(f"📍 **Address:** {ext.get('property_address', 'N/A')}")
                        st.markdown(f"💰 **Price:** ${ext.get('purchase_price', 0):,.2f}")
                        st.markdown(f"🏦 **Earnest Money:** ${ext.get('earnest_money_deposit', 0):,.2f}")
                    
                    with col_b:
                        st.markdown(f"👥 **Buyers:** {', '.join(ext.get('buyer_names', []))}")
                        st.markdown(f"👤 **Sellers:** {', '.join(ext.get('seller_names', []))}")
                        st.markdown(f"📅 **Closing Date:** {ext.get('closing_date', 'N/A')}")

                    if ext.get("milestones"):
                        st.markdown("#### 📅 Transaction Milestones")
                        m_data = [
                            {
                                "Milestone": m["name"], 
                                "Due Date": str(m["due_date"]),
                                "Value": f"${m['value']:,.2f}" if m.get("value") is not None else "—"
                            } 
                            for m in ext["milestones"]
                        ]
                        st.table(m_data)
                    
                    with st.expander("View Raw Extraction JSON"):
                        st.json(ext)
        else:
            st.info("No historical data found.")
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

with tab_harness:
    st.subheader("🛡️ Safety Harness Audit Log")
    st.info("This log shows deterministic alarms triggered by the harness during agent execution.")
    
    # Query all requests and filter in Python for robustness
    db = next(get_session())
    from sqlmodel import select
    all_requests = db.exec(select(ContractRequest).order_by(ContractRequest.created_at.desc())).all()
    requests_with_alarms = [r for r in all_requests if r.alarms]
    
    if requests_with_alarms:
        for r in requests_with_alarms:
            with st.expander(f"🚨 {r.parent_transaction_id} - {r.created_at.strftime('%H:%M:%S')}"):
                for alarm in r.alarms:
                    sev_color = {"CRITICAL": "red", "HIGH": "orange", "MEDIUM": "blue", "LOW": "grey"}.get(alarm['severity'], "grey")
                    st.markdown(f"### Type: `{alarm['alarm_type']}`")
                    st.markdown(f"**Severity:** :{sev_color}[{alarm['severity']}]")
                    st.warning(f"**Message:** {alarm['message']}")
                    st.info(f"👉 **Recommended Action:** {alarm['recommended_action']}")
                    st.json(alarm['context'])
    else:
        st.success("No safety alarms triggered in recent history. Harness is quiet.")

st.sidebar.markdown("### 🤖 Agent Configuration")
provider = st.sidebar.selectbox("LLM Provider", ["anthropic", "openai"], index=0)
parser_type = st.sidebar.selectbox("PDF Parser", ["pypdf", "llamaparse"], index=0)

settings.LLM_PROVIDER = provider
settings.PARSER_TYPE = parser_type

st.sidebar.markdown("### System Telemetry")
if "final_state" in st.session_state:
    st.sidebar.write(f"Request ID: `{st.session_state.final_state['request_id']}`")
    st.sidebar.write(f"Final Status: `{st.session_state.final_state['status']}`")
else:
    st.sidebar.write("No active session.")
