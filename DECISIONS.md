# Decision Log — Resolvly / Maintenance Resolution Intelligence Agent

One line per decision. Newest at top. When a new idea/tool/suggestion shows up (from anywhere — ChatGPT, blog posts, Claude, your own brainstorming), it gets logged here as deferred-with-a-trigger, not silently added to or dropped from current work.

---

**2026-09-07 — Project locked as "Maintenance Resolution Intelligence Agent" (Resolvly, unblocked by public data)**
Resolvly had the right problem shape (real ambiguity, real stakes) but was never started — no tenant data existed. Unblocked by using NYC 311/HPD data as a stand-in for messy real complaints, plus synthetic data for vendors/repair costs/outcomes. This is Resolvly's problem, just made buildable now instead of waiting indefinitely on real tenants.

**2026-09-07 — Chose this over Chunking Strategy Selector (parked, not abandoned)**
Selector is a strong technical-credibility piece (touches unsolved 2025-2026 research, clean eval story) but has no real tool integration and a thinner "judgment under ambiguity" story. Good candidate for a second portfolio project once this one ships. Not deleted from the tracker — moved to Parked.

**2026-09-07 — Locked initial tech stack, rejected larger stack from a ChatGPT-provided spec**
A more elaborate spec (MCP server, Redis, OpenTelemetry, LangSmith, hybrid retrieval, 50-case golden dataset, prompt-injection suite) is good architecture but wrong for week one — it's the "bigger toolbox before a working loop" trap. Spec preserved in full in ROADMAP.md as Phases 2-10. Phase 1 stays locked to: FastAPI, LangGraph, one hosted LLM, PostgreSQL, pgvector, Pytest, Braintrust/Langfuse, Docker, Cloud Run.

**2026-09-07 — Deferred tools list locked**
Mem0, NeMo Guardrails, Promptfoo, RAGAS, DeepEval, LiteLLM, Ollama, vLLM/SGLang, Qdrant, LlamaIndex, Firecrawl, voice, multiple agents. None rejected outright — each has a stated trigger condition in ROADMAP.md. Rule: every addition must answer "what specific failure in the current system does this solve?"

**2026-09-07 — Eval metric family clarified: classification metrics now, RAG metrics later**
Current scope (issue → category/urgency/confidence) is a classification problem: precision/recall per category, F1, confusion matrix, confidence calibration, fallback/escalation rate. RAG-specific metrics (groundedness, faithfulness, context precision/recall) don't apply until Phase 6 (retrieval) exists — logged here so this doesn't get re-debated.

**2026-09-07 — Multi-agent supervisor diagram (Supervisor → Classification Agent → Investigation Subgraph → Work-Order/Property/Vendor agents → Resolution Agent → Guardrails) proposed, not adopted**
Good diagram, but Phase 4+ territory, not now. "Multiple agents" is already on the deferred list with the trigger "only if a single deterministic LangGraph workflow genuinely can't express the logic" — no evidence yet that it can't. Kept the one genuinely useful piece: investigation (property/vendor/work-order lookups) can run as **parallel nodes inside one LangGraph workflow**, not as separate agents with a supervisor. Logged in ROADMAP.md Phase 4.

**2026-09-07 — PII protection gap identified: output-check is not enough**
Current test only guards that PII isn't echoed back in the *output* — it does nothing about the *input* description flowing through the system (LLM calls, storage, logs, tracing) with PII intact. Fine for now since synthetic data has no real PII. **Before any real tenant data or unfiltered real 311 descriptions are used, input-boundary PII redaction/masking must be built** — detecting and stripping names/phones/emails before the description ever reaches the LLM, database, or tracing tool, not just checking it's absent from the response. This is a nontrivial task (PII detection on free text) and should be scoped as its own piece of work when that trigger is hit, not built now against fake data. Added to ROADMAP.md as a gate before Phase 6 real-data use and before any real-property deployment.

**2026-09-07 — Six production-minded additions locked for Phase 1 (pyproject.toml, PII rule + test, deterministic emergency override, model-provider abstraction, cost/trace fields, real Day 5 metrics)**
All six are thin/structural, not scope creep — they don't require new infra or deferred tools, just better design of the code already being written. Emergency override (gas leak, fire/sparks, active flooding, no-heat-freezing, structural collapse) is a hardcoded Python policy layer above the LLM — the LLM classifies, Python can override on safety-critical categories. This directly strengthens the "judgment under ambiguity" story with a defensible, explicit design choice.

**2026-09-07 — Correction: use synthetic hand-written cases for Day 2, not real NYC 311 data yet**
Real 311 data adds PII/location-handling complexity for no benefit at this stage. Synthetic cases give tighter control over deliberate edge cases (ambiguous, multi-issue, missing-info). Real 311 data is deferred to Phase 6 (retrieval), where volume and realistic noise actually matter.

**2026-09-07 — Today's four tasks locked**
1. Create repo
2. Write issue schema (description, property, unit, attachments, reporter)
3. Create 15 representative maintenance cases
4. One endpoint: issue in → `{category, urgency, missing_information, recommended_action, confidence}` out
No vector DB, no memory, no cloud deployment yet.
