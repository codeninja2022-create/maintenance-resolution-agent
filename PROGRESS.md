# Progress

## Phase 1 — Foundation (COMPLETE ✅, merged to main)
- [x] Repo created (pyproject.toml)
- [x] Issue schema written
- [x] 15 test cases created
- [x] Classifier abstraction + MockClassifier
- [x] Real AnthropicClassifier implemented
- [x] Deterministic emergency-override policy implemented — proven load-bearing by unit test across all 5 categories through the full classify() path (real opus-5 has never disagreed with it, but correctness no longer depends on that)
- [x] Cost/trace fields populated from real calls
- [x] Single FastAPI endpoint
- [x] Endpoint tested against all 15 cases with real metrics — see `evals/latest_run.json`
  - Category accuracy: strong
  - Emergency recall: strong (5/5)
  - Urgency accuracy: 11/15 — 100% of misses are one-directional (+1 level), all on deliberately-ambiguous cases. See DECISIONS.md for full analysis.

## Post-Phase-1 follow-on — out-of-domain handling (DONE 2026-09-08)
- [x] Added `NOT_MAINTENANCE = "not_maintenance"` to `IssueCategory` + a "Scope rule" block in `app/prompt.py`
- [x] Added 5 fixtures (case_16/17/19 out-of-domain, case_18 borderline access equipment, case_20 adversarial override) → 20 total; `test_all_fixture_cases_parse_as_valid_issues` updated
- [x] Re-ran the eval (now 20-case). Out-of-domain **3/3**, borderline 1/1, emergency recall **6/6**, **no regression**. Category 0.95, urgency 0.80. Noted: eval has ~±1 case run-to-run variance on opus-5. Full results in DECISIONS.md + `evals/SUMMARY.md`.

## Phase 3 — Classification refinement (ACTIVE, evidence-driven)
- [x] 0.90-confidence wrong case identified & fixed — it was **case_13** ("could give way" → emergency @ 0.90). Rubric rewrite (emergency = active now, not anticipated) → now `high` @ 0.85. See below.
- [x] Emergency override proven load-bearing — unit test across all 5 categories through the full `classify()` path (`test_override_forces_emergency_for_every_hardcoded_category_when_llm_says_low`). **And now demonstrated on real data:** post-rubric-fix, case_20's model output is `high` and the `gas_leak` policy forces `emergency` — first real override.
- [x] Added `urgency_rationale` (one line, always populated, PII-redacted) to `_LLMClassification` / `ClassificationResult` / `MockClassifier`; surfaced in `evals/SUMMARY.md`
- [x] Rubric fix + 20-case re-eval (`claude-opus-5`, $0.38):
  - case_13 resolved (emergency→high), case_15 resolved (both category + urgency), case_10 correct this run
  - only remaining urgency miss: case_11 (low→normal) @ conf **0.30** — a confidence gate catches it
  - **confidence calibration fixed**: wrong-urgency confidences [0.60,0.25,0.90,0.45] → **[0.30]**; no confidently-wrong case remains, so a ~0.90 human-review threshold now works
  - aggregate 15→20: category 0.87→1.0, urgency 0.73→0.95, emergency precision 0.71→1.0, recall stays 1.0
- [x] **Decision logged:** rubric fix alone is sufficient — do NOT build the coherence-override rule. +1 caution bias essentially gone from the eval.
- [ ] Fix the noisy `missing_information` field — still ~0.20 detection, untouched, unusable as a review gate
- [ ] Address eval-run variance — average ≥3 runs (single runs move ~±1 case; confirm the rubric-fix gains hold)
- [ ] Model A/B — Sonnet/Haiku vs `claude-opus-5` (now $0.019 + 6.1 s per case after the rationale field)

## Phase 2, 4+
Not started — see ROADMAP.md. Phase 3 was prioritized ahead of Phase 2 (intake API hardening) because it's addressing an observed failure from real eval data, per the project's governing scope rule.