# Progress

## Phase 1 — Foundation (COMPLETE ✅, merged to main)
- [x] Repo created (pyproject.toml)
- [x] Issue schema written
- [x] 15 test cases created
- [x] Classifier abstraction + MockClassifier
- [x] Real AnthropicClassifier implemented
- [x] Deterministic emergency-override policy implemented (coverage gap noted — never proven load-bearing on real fixture data, see DECISIONS.md)
- [x] Cost/trace fields populated from real calls
- [x] Single FastAPI endpoint
- [x] Endpoint tested against all 15 cases with real metrics — see `evals/latest_run.json`
  - Category accuracy: strong
  - Emergency recall: strong (5/5)
  - Urgency accuracy: 11/15 — 100% of misses are one-directional (+1 level), all on deliberately-ambiguous cases. See DECISIONS.md for full analysis.

## Post-Phase-1 follow-on — out-of-domain handling (DONE 2026-09-08)
- [x] Added `NOT_MAINTENANCE = "not_maintenance"` to `IssueCategory` + a "Scope rule" block in `app/prompt.py`
- [x] Added 4 fixtures (case_16/17/19 out-of-domain, case_18 borderline access equipment) → 19 total; `test_all_fixture_cases_parse_as_valid_issues` updated
- [x] Re-ran the eval (now 19-case). Out-of-domain **3/3**, borderline 1/1, **no regression**. Category 0.95, urgency 0.79, emergency recall 1.0. Noted: eval has ~±1 case run-to-run variance on opus-5. Full results in DECISIONS.md + `evals/SUMMARY.md`.

## Phase 3 — Classification refinement (ACTIVE, evidence-driven)
- [ ] Identify the 0.90-confidence wrong case (it's **case_13** — ceiling stain "could give way" → emergency @ 0.90, expected high), diagnose why confidence stayed high
- [ ] Add adversarial override test to prove the emergency override is load-bearing (on all 5 true emergencies the LLM independently said `emergency`, so the policy has never actually corrected it on fixture data)
- [ ] Decide (and log) whether the +1 urgency-toward-caution bias should be corrected, left as-is, or bounded
- [ ] Fix the noisy `missing_information` field — model attaches questions to most cases including fully-actionable and `not_maintenance` ones; detection accuracy ~0.32, currently unusable as a human-review gate
- [ ] Address eval-run variance — average ≥3 runs (opus-5 has no temperature control; single runs move ~±1 case)
- [ ] Model A/B — Sonnet/Haiku vs `claude-opus-5` ($0.015 + 5.7 s per case)
- [ ] If correcting urgency: adjust prompt/calibration, re-run the 19-case eval, confirm no new under-prediction on true emergencies

## Phase 2, 4+
Not started — see ROADMAP.md. Phase 3 was prioritized ahead of Phase 2 (intake API hardening) because it's addressing an observed failure from real eval data, per the project's governing scope rule.