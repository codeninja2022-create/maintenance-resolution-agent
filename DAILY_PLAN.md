# Phase 1 — Day-by-Day Plan

Goal for the whole phase: one messy issue in → one validated structured output out. Nothing else. Adjust pacing (compress or stretch) to your actual available time — the point is each day ends with something concrete and checkable, not a fixed calendar.

---

### Day 1 — Repo + Schema
**Goal:** project skeleton exists, and the shape of an "issue" is nailed down in code.
- Create `maintenance-resolution-agent` repo
- Use `pyproject.toml` (not just `requirements.txt`) for dependency management
- Folder structure: `/app`, `/tests`, `pyproject.toml`, `.gitignore`, `README.md`, `ROADMAP.md`, `DECISIONS.md`, `PROGRESS.md`, `DESIGN_BRIEF.md`, `DAILY_PLAN.md`
- Write the `Issue` Pydantic model: description, property, unit, attachments, reporter
- Write the output-shape Pydantic model: category, urgency, missing_information, recommended_action, confidence
- Define a `Classifier` abstraction (interface) with `MockClassifier` (returns canned output, no API calls — for fast tests) as the first implementation; real LLM-backed implementation comes Day 3
**Done when:** `python -c "from app.models import Issue"` runs with no errors, both models are defined with types, and `MockClassifier` satisfies the interface.

### Day 2 — Test Data
**Goal:** 15 real, representative maintenance cases to build and test against.
- Hand-write 15 synthetic maintenance complaint cases (do NOT pull real NYC 311 data yet — adds PII/location complexity for no benefit at this stage; real data is deferred to Phase 6 retrieval)
- Cover a spread: at least one emergency (gas leak / no heat in winter / active flooding / fire-sparks / structural collapse — the same categories as the Day 3 deterministic override list), a few ambiguous/multi-issue ones, a few easy/clean ones, at least one that's genuinely missing info
- Store as a JSON/YAML fixture file in `/tests/fixtures`
- No real names, phone numbers, emails, or identifying details anywhere in the fixture data — synthetic only
**Done when:** 15 cases exist as structured fixture data, each with an expected category + urgency you'd assign by hand (this becomes your first tiny eval set).

### Day 3 — Classification Logic (offline, no API yet)
**Goal:** the actual reasoning step — prompt design and structured output parsing — works against one hardcoded case before it's wired to an endpoint.
- Write the LLM prompt/call that takes an `Issue` and returns the structured output (as a real `Classifier` implementation, e.g. `AnthropicClassifier`, satisfying the Day 1 interface)
- Enforce structured output (Pydantic validation on the LLM response, retry on malformed output)
- Add a deterministic emergency-override policy layer in Python, checked *before or alongside* the LLM result: gas leak, fire/sparks, active flooding, no heat during freezing weather, collapsed ceiling. If matched, urgency is forced to `emergency` regardless of what the LLM returned — the LLM classifies, but Python policy can override it on safety-critical cases
- Add trace/cost fields to every response: `request_id`, `model_name`, `latency_ms`, `input_tokens`, `output_tokens`, `estimated_cost`
- Add a test proving sensitive-looking text (e.g. a fake phone number or name accidentally in a description) is never echoed back unredacted in the output
- Run it manually against 2-3 of your 15 cases from a script, eyeball the output
**Done when:** one script run produces valid, correctly-typed JSON for a real case, including trace/cost fields, and the emergency override demonstrably fires on at least one test case.

### Day 4 — FastAPI Endpoint
**Goal:** the logic from Day 3 is reachable over HTTP.
- Wire a single `POST /classify` (or similar) endpoint using FastAPI
- Request body = `Issue`, response body = the structured output model (including trace/cost fields)
- Basic error handling (malformed input, LLM call failure)
**Done when:** `curl` or Swagger UI (`/docs`) hits the endpoint with a real issue and gets back valid structured JSON.

### Day 5 — Run All 15, Write Tests, Check the Loop
**Goal:** prove the narrow end-to-end path actually holds up, not just on the 2-3 cases you eyeballed — with real metrics, not vibes.
- Run all 15 fixture cases through the endpoint
- Pytest suite: schema validation tests, PII-leakage test (from Day 3), emergency-override tests (each of the 5 hardcoded categories forces `emergency` regardless of LLM output)
- Compute and record actual metrics, not just "looks correct":
  - category accuracy
  - urgency accuracy
  - valid structured-output rate
  - emergency recall
  - missing-information accuracy
  - average latency
  - average cost
- Update `PROGRESS.md` — check off all Phase 1 boxes
- Write a short `README.md` section: what it does, how to run it
**Done when:** all 15 cases produce valid structured output, tests pass (including PII and emergency-override tests), metrics are recorded in the repo (not just eyeballed), and you can explain in one paragraph where the classifier is strong vs. shaky.

---

## After Day 5
Phase 1 is done. Do not start Phase 2 (retrieval, vendors, LangGraph expansion) until you've actually looked at Day 5's results and decided, based on real output — not vibes — what the next real failure to fix is. That decision goes in `DECISIONS.md`.
