# Progress

## Phase 1 — Foundation (ACTIVE)
- [x] Repo created (pyproject.toml, not requirements.txt)
- [x] Issue schema written (`app/models.py`: Issue, ClassificationResult, ClassificationTrace)
- [x] 15 test cases created (`tests/fixtures/cases.json`)
- [x] Classifier abstraction + MockClassifier (`app/classifier.py`) — real LLM classifier is Day 3
- [x] Day 1 tests passing (4/4): model validation, fixture parsing, MockClassifier interface, PII-absence check
- [x] Real LLM classifier (`AnthropicClassifier` in `app/classifier.py`) — structured output via `messages.parse` + `_LLMClassification`, bounded retry on malformed output
- [x] Deterministic emergency-override policy (`app/policy.py`) — 5 rules, forces `urgency=emergency`; matches all 15 fixtures exactly (5 fire, 10 untouched, 0 false positives)
- [x] PII redaction (`app/redaction.py`) — email/phone stripped from all returned text; `app/prompt.py` also instructs the model
- [x] Cost/trace fields populated (`ClassificationTrace`: request_id, model_name, latency_ms, input/output tokens, estimated_cost)
- [x] Day 3 offline tests passing (23/23 total): `test_policy.py`, `test_redaction.py`, `test_anthropic_classifier.py` (fake client, no network)
- [x] Day 3 manual real-LLM run — ran cases 01/06/10/11/13 through `AnthropicClassifier` on `claude-opus-5`; all produced valid typed JSON with populated trace/cost (input ~1.3k tok, output 160-465 tok, ~$0.011-0.018/call, latency 3.9-8.4s). Emergency policy rule engaged on case_01 (`gas_leak`); the override forcing behaviour (policy beats a wrong model) is proven by `test_policy.py` + `test_anthropic_classifier.py::test_emergency_override_beats_the_model`.
- [x] Added `llm_urgency` to `ClassificationResult` so model-vs-policy urgency is visible on every response

### Day 3 observation (for Day 5 metrics / prompt tuning, not a blocker)
On the 5-case sample, `claude-opus-5` over-escalated urgency on every ambiguous case: case_10 high vs expected normal, case_11 normal vs low, case_13 emergency vs high. Direction is consistently "too hot". Clean cases (01, 06) were exact. Confirm on all 15 at Day 5 before deciding whether to tune the urgency rubric in the prompt.

- [x] Single FastAPI endpoint (`app/api.py`) — `POST /classify` (Issue → ClassificationResult), `GET /health`. Classifier injected via `Depends` so tests use MockClassifier. Error handling: 422 malformed body (FastAPI), 502 `ClassifierError`, 500 anything else (internals not leaked).
- [x] Day 4 verified live — `uvicorn app.api:app` + curl: `/health` 200, malformed body 422, real gas-leak complaint → 200 with valid `ClassificationResult` JSON incl. trace (`req_...`, latency 4.4s, 1334 in / 200 out tok, $0.0117). `/docs` Swagger UI loads.
- [x] `app/config.py` — dependency-free `.env` loader, used by the API and the run script
- [x] API tests (`tests/test_api.py`, 5): health, structured output, 422, 502, 500-no-leak. Full suite 29/29.
- [x] All 15 cases evaluated with real metrics (`scripts/eval.py` → `evals/SUMMARY.md`). Run 2026-09-07, `claude-opus-5`, $0.21 total:
  - valid-output 1.0 · category accuracy 0.87 · urgency accuracy 0.73 · **emergency recall 1.0** · emergency precision 0.71 · missing-info detection 0.27 · PII leaks 0 · avg 5.5 s / $0.014 per case
- [x] Day 5 pytest coverage — `tests/test_schema.py` (contract), plus existing PII-leakage and per-category emergency-override tests. **37/37 passing.**
- [x] README "how to run" sections (tests, classifier script, API, eval)

**Phase 1 is complete.** One narrow path works end to end: messy issue in → validated structured output out, over HTTP, with a deterministic safety layer, cost/trace on every call, and real numbers not vibes.

### Where the classifier is strong vs. shaky (Day 5 read)
Strong on **category** (0.87) and on **safety**: it caught all 5 true emergencies (recall 1.0), the deterministic policy fired correctly on each, PII never leaked, and no call produced malformed output. Shaky on **urgency** — accuracy 0.73, and all 4 errors are over-escalations (the model consistently rates ambiguous cases hotter than ground truth; emergency precision is only 0.71, with 2 false emergencies both coming from the model, not the policy). Also shaky: **`missing_information` is near-useless as a signal** — the model attaches clarifying questions to 14 of 15 cases including fully actionable ones, so it can't currently gate human review. Cost/latency ($0.014, 5.5 s per case on opus-5) is demo-fine, volume-expensive.

### Next real failure to fix (per DAILY_PLAN "After Day 5")
The urgency over-escalation + the noisy `missing_information` field are the two concrete failures in the working system. Both point at **prompt/rubric tuning and confidence-threshold work — Phase 3 (Classification refinement)** — before touching retrieval or vendors. Logged in DECISIONS.md.

## Phase 2+
Not started — see ROADMAP.md. Phase 3 (classification refinement) is the priority based on Day 5 results, not Phase 2 ordering.
