# Safety Harness Architecture: ContractReviewOrchestrator

This document outlines the architecture of the deterministic safety harness governing the ContractReviewOrchestrator agent.

## The Four Pillars of the Harness

The harness treats the LLM as an **untrusted reasoning engine**. All safety and logic is enforced by the harness, not by system prompts.

### 1. Guardrails (Deterministic Policy)
Guardrails are hard-coded Python checks that validate inputs and outputs against a strict policy.
*   **Pre-flight:** Validates document type and token limits in `app/harness/guardrails/pre_flight.py`.
*   **Post-flight:** A regex-based scrubber in `app/harness/guardrails/post_flight.py` that blocks unauthorized legal advice.
*   **Schema Enforcement:** Guaranteed JSON structures via `Instructor` and Pydantic.

### 2. Checkpoints (State Persistence)
Checkpoints allow the harness to persist the state of the agent at every node execution.
*   **Implementation:** Every state transition is recorded in the SQLModel database (`app/db/models.py`).
*   **Resumption:** Because the state is stored in `AgentState` and backed by SQL, the harness can recover or replay a run from any checkpoint.

### 3. Material Handling (Input/Output Isolation)
Material handling ensures the agent only interacts with approved data structures and tools.
*   **Input Parsing:** `app/core/parser.py` handles PDF-to-Text conversion before the agent sees the data.
*   **Tool Isolation:** The agent does not have raw network access. It must call `mls_client` or `crm_client`, which are governed by the harness.

### 4. Alarms (Structured Failure Reporting)
Alarms are triggered when a guardrail or checkpoint fails. They produce structured outputs instead of generic errors.
*   **Alarm Structure:** Includes `type`, `severity`, `context`, and `recommended_action`.
*   **Implementation:** Located in `app/harness/alarms.py`.

## Swappable Agent Interface
The harness is decoupled from the agent. By modifying `app/graph/nodes.py`, a different LLM (e.g., Claude) or a different extraction logic can be swapped in without changing the core harness logic in the LangGraph workflow.

## Human-in-the-Loop (HITL)
For high-value transactions (>$5M), the harness triggers a `FINANCIAL_THRESHOLD_ALARM` which halts automated syncs and escalates the state to a manual approval status.
