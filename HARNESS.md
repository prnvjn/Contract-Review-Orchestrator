# The Four Pillars of the ContractReviewOrchestrator Harness

This document defines the deterministic safety harness using the four execution pillars specified in the Architecture.

## Pillar A: The Loop (LangGraph)
*   **Role:** State Machine & Turn Management.
*   **Implementation:** `app/graph/workflow.py`.
*   **Safety Detail:** Natively enforces a `recursion_limit`. This serves as the system's **Checkpoints**; the state is persisted at every node transition, allowing for full recovery and auditing of the agent's reasoning path.

## Pillar B: The Tools (Read & Write)
*   **Role:** Input/Output Isolation (Material Handling).
*   **Implementation:** `app/tools/` & `app/core/parser.py`.
*   **Safety Detail:** The agent is restricted to approved "airlocks." It cannot interact with external services except through these deterministic clients, ensuring that raw material (PDFs) and side effects (CRM syncs) are strictly governed.

## Pillar C: The Guardrails (Deterministic Gates)
*   **Role:** Safety Policy Enforcement.
*   **Implementation:** `app/harness/guardrails/`.
*   **Safety Detail:** Hard-coded Python checks for document validity, financial thresholds ($5M circuit breaker), and legal advice scrubbing. These are **declared gates** with explicit pass/fail criteria that the agent cannot circumvent.

## Pillar D: The Observability (SQLModel)
*   **Role:** Telemetry, Auditing, and Alarms.
*   **Implementation:** `app/db/models.py` & `app/harness/alarms.py`.
*   **Safety Detail:** Every state change and tool call is recorded. When a guardrail fails, it triggers a **Structured Alarm** with named types, context, severity, and recommended actions, providing the transparency required for mission-critical real estate tasks.
