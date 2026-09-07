# Resolvly — Maintenance Resolution Intelligence Agent
## Roadmap

This is the target end-state architecture. **Only Phase 1 is active.** Every later phase is deferred until the phase before it is working end-to-end and proven — not just planned.

Rule for adding anything new to this roadmap (tool, library, pattern): it must answer **"what specific failure in the current working system does this solve?"** If there's no current failure it solves, it goes in the roadmap, not in this week's code.

---

### ✅ Phase 1 — Foundation (ACTIVE / CURRENT)
- Repository structure
- Issue schema (description, property, unit, attachments, reporter)
- 15 representative maintenance cases
- One FastAPI endpoint: issue in → `{category, urgency, missing_information, recommended_action, confidence}` out
- Stack: FastAPI, LangGraph, one hosted LLM, PostgreSQL, pgvector, Pytest, Braintrust/Langfuse, Docker, Cloud Run

**No vector DB, no memory framework, no cloud deployment yet.** Prove one input → one controlled workflow → validated structured output first.

---

### Phase 2 — Intake API hardening
- `POST /requests` with real persistence (not just in-memory)
- Request validation, structured error handling
- API-level tests

### Phase 3 — Classification refinement
- Baseline deterministic classifier vs. LLM classifier interface
- Confidence threshold tuning
- Emergency routing logic
- Classification-specific test suite

### Phase 4 — LangGraph workflow expansion
- Explicit typed state (request, classification, property_details, similar_work_orders, vendor_candidates, recommendation, evidence, approval_status, repair_draft, errors, audit_events)
- Conditional routing, checkpointing, explicit error path
- Human-review state as a first-class node
- **Investigation step can run in parallel** (property lookup, vendor lookup, historical work-order search as concurrent LangGraph nodes feeding into one recommendation node) — this is a parallel-execution detail *inside one graph*, not a reason to introduce a multi-agent/supervisor architecture. Revisit multi-agent only if a single graph genuinely can't express the logic (see deferred table below).

### Phase 5 — Tool boundary / MCP
- `search_work_orders`, `get_property_details`, `find_available_vendor`, `get_vendor_history`, `create_repair_draft`
- Read-only tools before write tools
- `create_repair_draft` never runs pre-approval
- Strict input/output schemas, timeout/error behavior, per-call logging

### Phase 6 — RAG / retrieval
- Seeded historical work-order data, ingestion + normalization
- pgvector search (already in stack) → hybrid (BM25 + vector) if pgvector-only proves insufficient
- Metadata filtering (property_id, unit_id, category, urgency, date, vendor_id, cost)
- Property-level filtering correctness (never surface a similar case from the wrong property)
- Citations/evidence attached to recommendations
- **RAG-specific eval metrics enter here**: context precision/recall, groundedness, faithfulness (RAGAS or DeepEval)

### Phase 7 — Vendor intelligence
- Vendor records: specialties, service area, availability, response time, completion rate, cost history, ratings, insurance/license status
- Ranking logic with an explainable "why this vendor" output

### Phase 8 — Guardrails, safety, privacy
- Authorization checks, PII minimization/redaction
- Prompt-injection tests, malicious-input tests
- Treat historical work-order text as **untrusted input**
- Audit trail, rate limits, retry/timeout policies
- Implement directly in code first — don't reach for NeMo Guardrails just to claim "guardrails"

### Phase 9 — Evaluation at scale
- Expand from 15 cases → 50+ case golden dataset
- Metrics: category accuracy, urgency accuracy, emergency recall, confidence calibration, retrieval precision/recall, groundedness, vendor-selection accuracy, tool-selection accuracy, human-review accuracy, latency, token cost, failure rate
- Error taxonomy: wrong category, wrong urgency, missed emergency, irrelevant retrieval, wrong property, unsupported recommendation, unsafe vendor action, PII leakage, unnecessary tool call, failed tool recovery
- Unit tests for deterministic logic; LLM-as-judge only where genuinely needed, never as the sole check
- Add **Promptfoo** here for red-team testing

### Phase 10 — Production readiness
- Docker Compose for local dev, health checks
- Tracing/metrics (Braintrust/Langfuse already in stack; OpenTelemetry only if that proves insufficient)
- Retries, timeouts, idempotency (already required from Phase 1 for work-order creation)
- Cost tracking, CI/CD (GitHub Actions), deployment docs
- Architecture diagram, demo script, interview narrative

---

## Explicitly deferred tools (not rejected — gated behind a trigger)

| Tool | Trigger to add it |
|---|---|
| **Input-boundary PII redaction** | **Required gate — not optional.** Must be built before real NYC 311 descriptions (Phase 6) or any real tenant data (real-property deployment) flow into the system. Current PII test only checks the output doesn't echo PII back; it does nothing to stop raw PII in the input from reaching the LLM, database, or tracing tool. See DECISIONS.md. |
| Mem0 | Only for cross-session user preferences — not needed for single-session classification |
| RAGAS / DeepEval | When retrieval (Phase 6) exists and needs measuring |
| Promptfoo | Phase 9, red-team/regression testing |
| NeMo Guardrails | Only if code-level authorization/approval rules prove insufficient |
| LiteLLM | If/when multi-provider model switching is actually needed |
| Ollama / vLLM / SGLang | If self-hosted model serving becomes a real requirement, not before |
| Qdrant | If pgvector proves insufficient at scale |
| LlamaIndex | If retrieval orchestration outgrows hand-rolled pgvector queries |
| Firecrawl | If a web-scraping data source is actually needed |
| MCP server | Phase 5 — once there's a real tool boundary past LangGraph nodes |
| Redis | If LangGraph checkpointing/short-lived state needs exceed Postgres |
| OpenTelemetry / LangSmith | If Braintrust/Langfuse tracing proves insufficient |
| Multiple agents | Only if a single deterministic LangGraph workflow genuinely can't express the logic |
| Voice interface | Not on the roadmap unless a real use case emerges |