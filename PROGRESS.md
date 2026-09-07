# Progress

## Phase 1 — Foundation (ACTIVE)
- [x] Repo created (pyproject.toml, not requirements.txt)
- [x] Issue schema written (`app/models.py`: Issue, ClassificationResult, ClassificationTrace)
- [x] 15 test cases created (`tests/fixtures/cases.json`)
- [x] Classifier abstraction + MockClassifier (`app/classifier.py`) — real LLM classifier is Day 3
- [x] Day 1 tests passing (4/4): model validation, fixture parsing, MockClassifier interface, PII-absence check
- [ ] Real LLM classifier (AnthropicClassifier) — Day 3
- [ ] Deterministic emergency-override policy — Day 3
- [ ] Cost/trace fields populated from real calls — Day 3
- [ ] Single FastAPI endpoint — Day 4
- [ ] Endpoint tested against all 15 cases with real metrics (category/urgency accuracy, emergency recall, etc.) — Day 5

## Phase 2+
Not started — see ROADMAP.md
