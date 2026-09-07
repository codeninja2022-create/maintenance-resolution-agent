# Resolvly — Maintenance Resolution Intelligence Agent
## Design Brief

---

## 1. Problem

A tenant submits a maintenance complaint that is often unclear, incomplete, or mixes multiple issues. Someone (currently a human) has to:
- Figure out what's actually wrong and how urgent it is
- Recall whether this property/unit has had similar issues before, and whether past fixes failed
- Decide what to do next and who should do it (which vendor)
- Get it approved
- Log it without creating duplicate work orders on retries

Doing this well under ambiguity, with real consequences for getting it wrong (safety, cost, tenant trust), is the actual problem — not just "classify some text."

## 2. Why this project (not the alternatives considered)

Two other ideas were seriously evaluated and set aside, not discarded:

- **Chunking Strategy Selector** — a RAG-ingestion tool that tests chunking strategies and recommends one based on retrieval quality. Strong technical/research credibility (touches unsolved 2025-2026 work), strongest possible eval story, but weak on real-world ambiguity and real tool integration. **Parked as a second portfolio project**, not abandoned.
- **Vanilla Resolvly (wait for real tenants)** — right problem shape, but blocked indefinitely on data that didn't exist yet.

This project resolves the blocker: use **NYC 311/HPD data** as a stand-in for real messy tenant complaints (real text, real categories, real ground truth for eval), plus **synthetic private data** for the parts that are genuinely yours to define — vendors, repair attempts, costs, outcomes. Same problem as Resolvly, unblocked.

## 3. What "done" looks like (end state, not week one)

The system will:
1. Accept an unclear complaint
2. Ask for missing information
3. Classify issue + urgency
4. Retrieve similar historical complaints/resolutions
5. Identify recurring issues and previously failed fixes
6. Recommend a next action and an eligible vendor
7. Require manager approval before acting
8. Create a work-order draft — idempotently, no duplicates on retry
9. Be fully evaluated and traced, decision by decision

## 4. Governing rule for scope

**Every new tool, pattern, or idea must answer: "what specific failure in the current working system does this solve?"**
If there's no current failure it solves, it's roadmap material, not this week's work. This rule exists because the project stalled once already (as "vanilla Resolvly") and the single biggest risk to finishing it now isn't lack of ideas — it's too many of them arriving before the core loop works. See `DECISIONS.md` for every time this rule has already been applied.

## 5. Phase 1 scope (active now)

**Stack:** FastAPI, LangGraph, one hosted LLM, PostgreSQL, pgvector, Pytest, Braintrust or Langfuse, Docker, Cloud Run.

**Explicitly not used yet:** Mem0, NeMo Guardrails, Promptfoo, RAGAS, DeepEval, LiteLLM, Ollama, vLLM/SGLang, Qdrant, LlamaIndex, Firecrawl, voice, multiple agents/supervisor architectures, MCP server, Redis, OpenTelemetry/LangSmith. Each has a stated trigger condition for later — see `ROADMAP.md`.

**This week's four tasks:**
1. Create the repository
2. Write the issue schema (description, property, unit, attachments, reporter)
3. Create 15 representative maintenance cases
4. Implement one endpoint: issue in → structured output out:
```json
{
  "category": "plumbing",
  "urgency": "high",
  "missing_information": ["Is the water still flowing?"],
  "recommended_action": "Shut off the unit supply and request manager review.",
  "confidence": 0.82
}
```
No vector DB, no memory, no cloud deployment yet. Prove one input travels through one controlled workflow to validated structured output — first.

## 6. Full architecture (target end-state — see `ROADMAP.md` for phase-by-phase sequencing)

- **Intake layer** — REST API, structured fields (request_id, property_id, unit_id, submitted_by, description, created_at, attachments)
- **Classification** — issue_category, urgency, confidence, safety_flags, missing_information, requires_human_review; low-confidence or dangerous requests route to human review
- **LangGraph workflow** — typed state, explicit nodes (intake → classify → investigate → retrieve history → find vendors → recommend → human approval → create draft → persist outcome). Investigation (property lookup, vendor lookup, work-order history) runs as **parallel nodes inside this one graph** — not as separate agents with a supervisor, unless a single graph proves genuinely insufficient
- **Tool boundary** (Phase 5) — read-only tools before write tools; `create_repair_draft` never runs pre-approval; every call logged and timeout/error-handled
- **RAG / retrieval** (Phase 6) — pgvector first, hybrid (BM25 + vector) only if needed; metadata filtering (property_id, unit_id, category, date, vendor_id, cost); must never surface a similar case from the wrong property; citations attached to recommendations
- **Vendor intelligence** (Phase 7) — specialties, service area, availability, response time, completion rate, cost history, ratings; explainable "why this vendor"
- **Guardrails & safety** (Phase 8) — authorization, PII redaction, prompt-injection tests, audit trail — implemented in code first, not via a guardrails framework by default
- **Evaluation** (Phase 9) — golden dataset grows 15 → 50+; error taxonomy (wrong category, missed emergency, wrong property, unsafe vendor action, PII leakage, etc.)
- **Production readiness** (Phase 10) — Docker Compose, health checks, tracing, retries, idempotency, CI/CD, deployment docs, demo script

## 7. Evaluation approach

**Current phase (classification, no retrieval yet):** classification-family metrics — precision/recall per category, F1, confusion matrix, confidence-accuracy calibration, fallback/escalation rate.

**RAG-family metrics (groundedness, faithfulness, context precision/recall)** do not apply until Phase 6, when a real retrieval step exists. Applying them earlier would be measuring the wrong thing.

**Ground truth source:** NYC 311/HPD's own labels — avoids the bias of hand-writing your own easy-to-classify test complaints.

## 8. Tracking mechanism

Three files, repo root, git-tracked:
- **`ROADMAP.md`** — target architecture, phase by phase, with every deferred tool's trigger condition
- **`DECISIONS.md`** — running log of what was decided/deferred and why, so reasoning isn't relitigated
- **`PROGRESS.md`** — simple checklist per phase, updated each session; git commit history doubles as a timestamped progress log

## 9. FDE narrative (why this project, stated for an interview)

"I found a real, messy, high-stakes problem — tenant maintenance triage — and unblocked it using public NYC data instead of waiting on private data that didn't exist. I built it as a disciplined, sequenced system: proved one narrow end-to-end loop first, then added retrieval, vendor logic, guardrails, and evaluation only as each was justified by a concrete failure in the working system — not because a tool sounded impressive. Every classification decision is measured against real ground truth, every action requires approval, and every work-order creation is idempotent by design."
