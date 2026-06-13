# ContractReviewOrchestrator Implementation Plan

## Project Structure Implementation

I'll create the directory structure as specified in the architecture:

1. **Main Application Files:**
   - `app/main.py` - FastAPI application entry point
   - `app/app_ui.py` - Streamlit Dashboard for live demo

2. **Core Components:**
   - `app/core/config.py` - Environment variables and settings
   - `app/core/database.py` - SQLModel engine and session maker

3. **Database Models:**
   - `app/db/models.py` - SQL tables for Requests, Observability Logs, ToolCalls

4. **Schemas:**
   - `app/schemas/contract.py` - Pydantic models for Instructor validation

5. **Tools:**
   - `app/tools/mls_client.py` - READ Tool for SimplyRETS API calls
   - `app/tools/crm_client.py` - WRITE Tool for FollowUpBoss webhook

6. **Guardrails (Safety Layer):**
   - `app/guardrails/pre_flight.py` - Document type validation and token limits
   - `app/guardrails/mid_flight.py` - Financial thresholds (Circuit Breakers)
   - `app/guardrails/post_flight.py` - Legal advice regex scrubbers

7. **LangGraph State Machine:**
   - `app/graph/state.py` - TypedDict defining the current state of the loop
   - `app/graph/nodes.py` - Execution steps (Call_Model, Run_Tool, Evaluate_Guardrails)
   - `app/graph/workflow.py` - Compiled graph compiling nodes and max_turn limits

8. **API Routes:**
   - `app/api/routes/extract.py` - Trigger contract extraction pipeline
   - `app/api/routes/webhooks.py` - Endpoints for HITL Slack approvals

## Key Implementation Details

**FastAPI Setup:**
- Create main application with proper routing
- Configure middleware for security and logging
- Implement proper dependency injection

**LangGraph Integration:**
- Set up the state machine with typed dictionaries
- Implement nodes for model calling, tool execution, and guardrail evaluation
- Configure recursion limits to prevent infinite loops (5 turns max)

**Guardrails Implementation:**
- Schema enforcement using Instructor + Pydantic
- Legal advice blocking middleware
- Financial circuit breaker logic

**Database Integration:**
- SQLModel setup with SQLite/PostgreSQL support
- Models for tracking requests, tool calls, and observability logs
- Proper session management

**Tool Integration:**
- MLS client with mocked SimplyRETS API
- CRM client with mocked FollowUpBoss webhook
- Proper error handling for external service calls

## Deployment Strategy

Following the recommended approach:
- For hackathon deployment, implement Option A (Unified Monolith)
- Integrate all components into Streamlit layout for single-file deployment
- Ensure it runs on Streamlit Community Cloud without CORS issues

This plan will create a robust, production-ready system that handles real estate contract processing with strong safety measures and observability.