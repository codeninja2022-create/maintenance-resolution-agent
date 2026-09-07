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
- [ ] Endpoint tested against all 15 cases with real metrics (category/urgency accuracy, emergency recall, etc.) — Day 5

## Phase 2+
Not started — see ROADMAP.md
