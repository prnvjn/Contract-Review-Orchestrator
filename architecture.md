Here is the final, fully consolidated **Architecture Specification Sheet** with the deployment strategy and options integrated as standard production configurations.

This gives you a complete, professional, one-page backend blueprint that you can hand to judges or paste directly into your hackathon submission.

---

# Architecture Specification: ContractReviewOrchestrator

## 1. System Overview

**Domain:** Real Estate Transaction Coordination
**Objective:** A FastAPI-based backend that safely extracts variables from unstructured real estate contracts, validates them against strict schemas, and pushes milestones to a CRM.
**Core Philosophy:** LLMs are treated as untrusted reasoning engines. Safety, compliance, and schema formatting are enforced via hard-coded Python middleware, not system prompts.

---

## 2. The Technology Stack

* **API Framework:** FastAPI


* **Database / ORM:** SQLModel (SQLite/PostgreSQL)


* **AI Provider:** OpenAI (`gpt-4o` or `gpt-4o-mini`)


* **State Machine (The Loop):** LangGraph (Manages the agent's iterative reasoning and enforces turn limits).


* **Schema Enforcement:** Instructor + Pydantic (Patches the OpenAI SDK to guarantee valid JSON matching our database models).


* **Tool Integrations:** `requests` / `httpx`

* **Demo Frontend:** Streamlit (`pip install streamlit`) for rapid UI prototyping.

---

## 3. Refactored Directory Structure

```text
app/
├── main.py                 # FastAPI application entry point
├── app_ui.py               # Streamlit Dashboard (Two-column view for live demo)
├── core/
│   ├── config.py           # Env vars and settings
│   └── database.py         # SQLModel engine and session maker
├── db/
│   └── models.py           # SQL tables: Requests, Observability Logs, ToolCalls
├── schemas/
│   └── contract.py         # Pydantic models for Instructor (e.g., ContractSummary)
├── tools/
│   ├── mls_client.py       # READ Tool: SimplyRETS mocked API calls
│   └── crm_client.py       # WRITE Tool: Mocked FollowUpBoss webhook
├── guardrails/             # DETERMINISTIC SAFETY GATES
│   ├── pre_flight.py       # Document type validation, Token limits
│   ├── mid_flight.py       # Financial thresholds (Circuit Breakers)
│   └── post_flight.py      # Legal advice regex scrubbers, source-fidelity checks
├── graph/                  # LANGGRAPH STATE MACHINE
│   ├── state.py            # TypedDict defining the current state of the loop
│   ├── nodes.py            # Execution steps (Call_Model, Run_Tool, Evaluate_Guardrails)
│   └── workflow.py         # Compiled graph compiling nodes and max_turn limits
└── api/
    └── routes/
        ├── extract.py      # Trigger contract extraction pipeline
        └── webhooks.py     # Endpoints for HITL (Human-in-the-loop) Slack approvals

```

---

## 4. The Four Execution Pillars (Implementation)

### Pillar A: Chat / Loop (LangGraph)

* **State Tracking:** A `State` object tracks the document chunk, the extracted variables, and iteration history.


* **Max Turns Limit:** LangGraph natively enforces recursion limits. If the LLM enters an unstable tool-calling loop, it halts at `recursion_limit=5` and exits defensively.



### Pillar B: Tools (Read & Write)

* **Read Tool (`verify_parcel_data`):** Connects to the SimplyRETS API to cross-reference extracted APNs with tax maps.


* **Write Tool (`sync_transaction_milestones`):** A mocked FollowUpBoss webhook that triggers a milestone sync once data passes all checks.



### Pillar C: Deterministic Guardrails (The Shield Layer)

* **Schema Enforcement:** Handled by `Instructor`. If the LLM outputs a date format dynamically (like `"TBD"` instead of `YYYY-MM-DD`), Pydantic throws a `ValidationError` and triggers a deterministic loop retry.


* **Legal Advice Blocker (`post_flight.py`):** A custom Python middleware that sweeps output strings for blocklisted patterns (e.g., `"you should"`, `"strike this"`), throwing a safety error if found.


* **Financial Circuit Breaker (`mid_flight.py`):** Intercepts tool execution. If `offer_price > 5000000`, the harness blocks the external CRM write and escalates the token state to human-in-the-loop (HITL) approval.



### Pillar D: Observability (SQLModel)

* Permanent telemetry records tracking `token_usage`, `tool_calls` payloads (inputs/outputs), and chronological `compliance_checks` execution logs.



---

## 5. Deployment Options & Strategy

### Option A: Unified Monolith (Recommended Hackathon Configuration)

* **Strategy:** Fold core extraction, guardrails, and LangGraph workflow nodes directly into the Streamlit layout (`app_ui.py`) as Python components, skipping a separate network hop.
* **Target Environment:** **Streamlit Community Cloud** (100% Free).
* **Benefits:** Complete elimination of cross-origin resource sharing (CORS) errors, unified repository deployment, and an instant public URL.

### Option B: Decoupled Multi-Tier Architecture

* **Backend Tier:** **Render.com** (Free Web Service tier running the FastAPI instance).
* **Frontend Tier:** **Streamlit Community Cloud** (Hosting the dashboard UI and targeting the active Render API URL via `httpx`).
* **Operational Note:** Render’s free tier goes to sleep after 15 minutes of idling. The initial api handshake requires a 45-second delay to wake up the underlying server container.