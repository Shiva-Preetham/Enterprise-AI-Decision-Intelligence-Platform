# Sprint 6 — Enterprise AI Customer Intelligence Copilot

## Overview

Sprint 6 introduces the Agent Layer to our platform, transforming it into an Enterprise AI Copilot powered by LangGraph. This layer enables business stakeholders to ask natural language questions (e.g., "Why is this customer likely to churn?") and receive data-backed, structured insights.

Crucially, we maintain Clean Architecture: the AI **never** accesses the database directly. Instead, the AI operates as a client to the existing backend Service Layer, calling our Python services as "Tools."

---

## Technical Accomplishments

### 1. LangGraph Agent Architecture (`agent/graph.py`)
We implemented a directed acyclic graph (DAG) representing the cognitive flow of the agent:
1. **Guardrails**: Intercepts requests.
2. **Planner (`agent/planner.py`)**: Analyzes the question and selects appropriate enterprise tools using GPT-4o-mini.
3. **Executor (`agent/executor.py`)**: Invokes the selected backend services.
4. **Rule Engine (`agent/recommendation.py`)**: Generates a deterministic Next Best Action based on the tool outputs.
5. **Output Parser (`agent/output_parser.py`)**: Synthesizes the data and rules into a strict Pydantic JSON structure using OpenAI's Structured Outputs.

### 2. Enterprise Tool Calling (`agent/tools.py`)
We wrapped our existing backend services in LangChain `@tool` decorators:
- `get_customer_profile`: Fetches complete Customer 360 data + live ML prediction.
- `get_customer_timeline`: Fetches recent orders and reviews.
- `get_dashboard_metrics`: Fetches high-level KPIs.
- `get_model_metadata`: Fetches ROC AUC, algorithm, and training dates.
- `trigger_background_task`: Allows the AI to spawn Celery tasks natively.

### 3. Guardrails & Security (`agent/guardrails.py`)
AI in the enterprise requires strict safety checks. Before the LLM is invoked, input is validated against:
- **SQL Injection Attempts**: Blocks requests like "DROP TABLE".
- **Prompt Extraction**: Blocks "ignore previous instructions".
- **Code Execution**: Blocks requests to run Python/bash.
- **Domain Enforcement**: Gently nudges users back to business intelligence if they go off-topic.

### 4. Conversational Memory (`agent/memory.py`)
Implemented `langgraph-checkpoint-redis` to allow multi-turn conversations. The Redis memory saver binds to the existing Redis instance, tracking conversations via a unique `conversation_id`.

### 5. FastAPI Integration (`agent/router.py`)
Exposed the agent via `POST /api/v1/agent/chat`. The router performs dependency injection of the existing Services into the LangChain tools, spins up the Redis checkpointer, and streams the structured `AgentResponse` back to the client.

---

## Self Review (Senior AI Engineer Assessment)

### Scores
- **Architecture**: 9.5/10 — Perfect isolation of LLM logic from core business logic by utilizing existing services.
- **Agent Design**: 9.0/10 — The separation of Planner and Output Parser ensures we don't have a massive single "god prompt".
- **Security**: 9.5/10 — Pre-execution guardrails and zero direct DB access ensures high safety.
- **Maintainability**: 9.0/10 — Tools map 1:1 to services.
- **Enterprise Readiness**: 9.5/10 — Structured JSON outputs guarantee the frontend UI won't break due to LLM formatting hallucinations.
- **Interview Readiness**: 10/10 — Demonstrates advanced GenAI patterns (LangGraph, Tool Calling, Structured Outputs).

### Strengths
- **Determinism**: The rule engine forces the LLM to output approved recommendations, preventing it from hallucinating impossible retention actions.
- **Structured Output**: Pydantic models guarantee consistent API responses.
- **Security**: Zero SQL access.

### Weaknesses
- **Latency**: Passing through LangGraph + OpenAI adds ~1-3 seconds to request times.
- **Memory Scaling**: Storing all conversation histories indefinitely in Redis could cause memory bloat.

### Future Improvements (Sprint 7)
- **Agentic Reasoning for Recommendations**: Upgrade the hardcoded Next Best Action rule engine into a dedicated LangGraph reasoning node for dynamic, personalized suggestions.
- **Streaming**: Stream tokens back to the frontend UI via Server-Sent Events (SSE) to reduce perceived latency.
