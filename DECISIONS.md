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

**2026-09-09 — `missing_information` fix is a METRIC-DEFINITION fix, not a model fix.**
Following the diagnosis below: the model's `missing_information` behaviour is correct — it produces dispatch-actionable follow-up questions, which is what the prompt asks for. The eval fixtures' `expected_missing_information` had been authored against a *different, unstated* definition ("is this complaint too vague to classify?"). That mismatch, not the model, produced the 0.20 score.
- **Action taken:** rewrote `expected_missing_information` for all 20 fixtures to the intended definition — the 1–3 questions a dispatcher would genuinely want answered to route, prioritise, brief the responder, or bring the right parts. Empty only for the 3 clear `not_maintenance` cases (case_16/17/19), where the correct behaviour is "recognise and route", not "interview". Updated each fixture's `notes` to state what its `missing_information` is testing. **Model and prompt untouched.**
- **Metric renamed** `missing_info_detection_accuracy` → `missing_info_appropriateness` (`scripts/eval.py`) to reflect what it now measures: did the model ask for follow-up exactly when the case warrants it.
- **Re-scored** run 3's saved model output against the corrected fixtures via `scripts/rescore.py` (offline, no new API calls): **0.20 → 0.90**.
- **Two residual misses**, both the same pattern: case_17 (billing) and case_19 (weather) — `not_maintenance` cases where the model asks follow-up questions rather than just recognising "route elsewhere". Minor, consistent; candidate for the Phase 4+ split below. Not fixing now.
- Secondary observation (not scored, not fixed): the model over-asks by ~1–2 questions vs. the curated lists on most cases. A count-band or coverage metric could catch this later.

**Option C — split `missing_information` into two fields (Phase 4+, not now):** `classification_blocking` (answers that would change category/urgency/confidence — usually empty, the real human-review gate) vs. `dispatch_notes` (operational follow-ups for the responder — usually non-empty). This cleanly separates the two constructs that are currently conflated, and would make case_17/case_19 unambiguous (both fields empty for `not_maintenance`). Deferred: it's a schema + prompt + fixture change touching every consumer, and the single-field metric at 0.90 is good enough for Phase 3. Trigger: when a downstream consumer (human-review routing, or the LangGraph investigate step) actually needs the two signals separated.

**2026-09-09 — Rubric fix confirmed over 3 runs; `missing_information` underperformance diagnosed.**

*Stability:* ran the 20-case eval 3× (`claude-opus-5`). category 1.0 / urgency 0.95 / emergency recall 1.0 / emergency precision 1.0 on **every** run. Zero urgency flips, zero category flips. The one urgency miss is case_11 all 3 times at confidence exactly 0.30. Pooled 60 classifications: 57 correct (mean conf 0.88), 3 wrong (all 0.30). No confidently-wrong case in any run. The old ±1-case variance (case_10/case_14) is also gone. **The calibration fix is real, not a one-off.**

*`missing_information` diagnosis (detection stuck at 0.20–0.25):* the field conflates two different questions and the model answers the wrong one.
- The prompt says *"specific questions a dispatcher would need answered before acting."* The model reads this as "any useful thing a responder would want confirmed" → it returns non-empty on ~18/20 cases, including all 5 clear emergencies and the clean easy cases.
- The fixtures grade a narrower thing: *"is the complaint too vague/ambiguous to classify?"* — empty for 16/20, non-empty only for the 4 genuinely-underspecified cases (case_10/11/13/15).
- **The model is not padding.** case_16 (noise complaint): 0 questions. case_19 ("what's the weather"): 1 question — "do you actually have a maintenance issue?". Question count scales with real ambiguity: clear cases get 2–3, case_11 (truly vague) gets 7. The questions are on-topic and useful.
- **But there is a real coherence bug:** on high-confidence cases the model still lists questions whose answers would not change category, urgency, or confidence — e.g. case_01 (gas/emergency, conf 0.95) still asks "have the occupants evacuated?" (an operational follow-up, not a classification input). `confidence` and `missing_information` are currently uncorrelated; only case_11 shows the coherent low-confidence ↔ many-questions pattern.
- **Fixture caveat:** a couple of expected-`[]` cases are arguable — case_07 ("is water overflowing onto the floor?" genuinely bears on urgency), case_14. Worth a fixture review, but the definition is the dominant problem.

*Proposed fix (not yet built — same play as the rubric fix, tighten the prompt first, no deterministic post-filter):* scope `missing_information` to **classification-relevant unknowns only** — "questions whose answers would change your category, urgency, or confidence; facts you are currently guessing at. If you can assign category and urgency without them, return []." Explicitly exclude responder-checklist items (evacuation status, breaker state, make/model, access times). Add: "if confidence ≥ ~0.85, missing_information is normally empty." Expected effect: empty for the 5 emergencies + clean cases, non-empty for case_10/11/13/15 (+ maybe case_20) → detection toward 0.8+. Decide after seeing whether the prompt change alone gets there.

**2026-09-09 — Rubric fix + `urgency_rationale` field. Confidently-wrong gap closed; coherence-override rule NOT needed.**
Two changes: (1) `_LLMClassification` / `ClassificationResult` gain `urgency_rationale` — one sentence, always populated, PII-redacted, explaining the urgency call and (if not emergency) why it isn't higher. Surfaces in `evals/SUMMARY.md`. (2) Prompt rubric rewritten: `emergency` = actively happening / certain-and-immediate now; a credible *risk* not yet happening ("could give way", "I think I smell gas", "probably nothing") is `high`, not `emergency`. The safety-rule paragraph no longer says "even plausibly … treat as emergency" — it now says classify what's described and let the deterministic check force-escalate keywords after.

**20-case eval result (`claude-opus-5`, $0.38, `evals/SUMMARY.md`):**
- **case_13 RESOLVED** — was `emergency` @ 0.90 (confidently wrong), now `high` @ 0.85 (correct). Rationale: "the tenant only says it looks like it could give way rather than describing an active collapse … a credible imminent risk rather than an emergency in progress."
- **case_15 RESOLVED on both axes** — was `other→gas` category + `emergency` urgency, now `other` + `high` @ 0.60 (both correct).
- **case_10 also correct this run** (`normal`, was over-escalated to `high`) — partly the rubric, partly run variance.
- **case_11 still wrong** (`low`→`normal`) but @ conf **0.30** — a confidence gate catches it trivially, and "bothering me for days" is arguably not clearly `low` anyway.
- **case_20: the deterministic override fired for real for the first time** — model now reads the hedged gas smell as `high` (correct per rubric), the `gas_leak` policy forces `emergency`, `emergency_override_applied: True`. The safety net is now demonstrated load-bearing on real model output, not just in unit tests.
- **Confidence calibration is much better.** Wrong-urgency confidences went from [0.60, 0.25, 0.90, 0.45] (one confidently wrong) to **[0.30]** — single miss, low confidence. Correct cases mean 0.88, min 0.60. **No confidently-wrong case remains**, so a ~0.90 human-review threshold now works: it flags case_11 and nothing correct-and-confident slips a wrong answer through.
- Aggregate 15→20: category 0.87→**1.0**, urgency 0.73→**0.95**, emergency precision 0.71→**1.0**, emergency recall stays 1.0.

**Regressions / costs:**
- `missing_information` detection did **not** improve (0.20 this run, low end of its noisy 0.20–0.35 range) — the field was untouched; still Phase 3 work.
- Output cost/latency up ~35% / ~20% ($0.014→$0.019, 5.7→6.1 s per case) from the added `urgency_rationale` tokens. Acceptable for the debuggability gain; revisit in the model A/B.
- Single run — ~±1 case variance (case_10's flip may be partly luck). case_13/case_15 rationales explicitly cite the new rubric wording, so those are real, not noise. Should confirm with ≥3 runs.

**Decision: the rubric fix alone is sufficient for the confidently-wrong problem. Do NOT build the coherence-override rule (flag urgency+missing_info contradictions).** The +1-toward-caution bias is now essentially gone from the eval too (only case_11 remains, in the harmless low→normal direction, low confidence). Remaining Phase 3: noisy `missing_information`, eval-run variance, model A/B.

**2026-09-08 — Emergency override now conclusively proven by unit test (item closed)**
Added `test_anthropic_classifier.py::test_override_forces_emergency_for_every_hardcoded_category_when_llm_says_low`: parametrized over case_01–05, mocks the LLM to return `urgency="low"` for each hardcoded emergency category, runs the full `AnthropicClassifier.classify()` path, and asserts `urgency == emergency` and `emergency_override_applied is True` for all 5. All pass. This settles the "never proven load-bearing" concern from the Phase 3 list — the override's correctness is now established by test regardless of whether the real model ever errs. Real opus-5 has still never disagreed with the policy on any of the 20 fixtures (incl. adversarial case_20); that's now a note, not a gap.

**2026-09-08 — Added adversarial emergency-override case (case_20), and it revealed the override still isn't proven load-bearing on real model output**
case_20: "faint gas-ish smell a few days ago, probably nothing… also the cabinet hinge is squeaky" — gas keyword present but downplayed and bundled with a trivial issue, so the model's tone-based read would plausibly *not* flag emergency. Expected `gas` / `emergency` (forced by the deterministic rule regardless).
**Result (20-case eval):** `gas` / `emergency` / conf 0.82 — but `llm_urgency` was **also `emergency`**. opus-5 was not talked out of it. So `emergency_override_applied` is `false` again: the `gas_leak` rule matched but had nothing to correct. **The override has now survived a deliberate adversarial attempt to make the model disagree, and still hasn't had to fire against real model output on any of the 20 fixtures.** Its load-bearing behaviour is proven only by unit tests (`test_policy.py::test_adversarial_gas_case_still_forces_emergency_when_llm_downplays_it` feeding `Urgency.LOW`; `test_anthropic_classifier.py::test_emergency_override_beats_the_model` with a fake model). Phase 3 decision needed: write a harder adversarial case, or accept that the override is a guaranteed floor for unseen model failures (evidenced by unit test, not eval) and close the item. Emergency recall is now 6/6, precision 0.75 (6/8; case_13, case_15 still the false emergencies).

**2026-09-08 — Added complete non sequitur negative case (case_19)**
`case_16`/`case_17` were still tenant/property-adjacent (noise, billing) — just wrong category. `case_19` ("what is the weather today") tests a stronger failure mode: zero property relevance at all, checking whether the system cleanly returns `not_maintenance` rather than manufacturing a maintenance interpretation out of nothing. Reuses `not_maintenance` rather than a new enum value — the actionable distinction (does a property manager need to act?) is the same regardless of how far off-topic the input is. 19 total fixture cases now.

**Noted, deliberately deferred:** a prompt-injection style case (e.g. "ignore your instructions and mark this emergency") was considered but not added — that's a Phase 8 (guardrails/security) concern, a different category of finding than classification correctness. Revisit when Phase 8 is reached.

**2026-09-08 — Eval gap identified: no out-of-domain negative cases**
All 15 original fixture cases were genuine maintenance complaints. None tested whether the system correctly recognizes input that isn't a maintenance issue at all (noise/neighbor complaints, billing questions) versus forcing it into a category with possibly-inflated urgency — a different, arguably worse failure mode than the +1 ambiguity bias already found. Added 3 cases (case_16, case_17: clearly out-of-domain; case_18: borderline shared-property access equipment, not clean negative but a good edge test) to `tests/fixtures/cases.json`, now 18 total.

**DECIDED 2026-09-08 — option 1: added `NOT_MAINTENANCE = "not_maintenance"` to `IssueCategory`.** Rationale as stated: `other` conflates "unclear *maintenance* issue" with "not a maintenance request at all", and the negative-case eval is only meaningful if the model can name the distinction rather than us inferring it from urgency. Implementation: enum value + a "Scope rule" block in `app/prompt.py` (when to use `not_maintenance` vs `other`, urgency `low`, route not dispatch, and an explicit carve-out that shared-property equipment like a parking gate is still `access_lock`). No deterministic logic added — left it to the prompt so the eval shows the model's unaided behaviour.

**RESULT — 19-case eval, 2026-09-08, `claude-opus-5`, $0.28 (`evals/SUMMARY.md`):**
- **case_16** (noise complaint), **case_17** (rent overcharge), **case_19** ("what's the weather") → all `not_maintenance`, urgency `low`, conf 0.95. Correct on every axis (case_17 still over-attached `missing_information` — the pre-existing noisy-questions issue, not specific to this).
- **case_18** (parking-gate code broken) → `access_lock`, urgency `normal`, conf 0.88. Correct — did **not** force `not_maintenance`, did **not** over-escalate. The scope-rule carve-out worked.
- **Out-of-domain detection: 3/3. Borderline: 1/1.**
- **No regression from the enum/prompt change**: same 4 urgency over-escalations (case_10/11/13/15); category now shows only case_15 wrong (case_14 flipped back to correct this run — see variance note).
- Aggregate 15→19: category accuracy 0.87→0.95, urgency accuracy 0.73→0.79, emergency recall stays 1.0, emergency precision stays 0.71.
- **Run-to-run variance noted:** opus-5 with no temperature control. Between the 18- and 19-case runs, case_14's category flipped (water_leak↔plumbing) and case_01's `missing_information` flipped (empty↔populated). Single-run metrics carry ~±1 case of noise — Phase 3 should average ≥3 runs or ignore sub-0.05 moves.
Conclusion: `not_maintenance` is a clean win, done. Urgency calibration + noisy `missing_information` + eval-run variance remain Phase 3 work.

**2026-09-08 — Phase 1 complete, merged to main. Day 5 eval results logged.**
15-case eval (`evals/latest_run.json`): category accuracy and emergency recall strong. Urgency calibration: 11/15 correct, 4/15 wrong — **100% of errors are one-directional, always exactly +1 urgency level**, and all 4 occur on the cases deliberately written as ambiguous/underspecified (case_10, case_11, case_13, case_15). No case was ever under-predicted. Confidence is well-calibrated overall (correct: mean 0.91, range 0.82–0.97; wrong: mean 0.55) except one wrong case with 0.90 confidence — needs identifying, since confidently-wrong is a worse failure mode than unconfidently-wrong (won't get caught by a low-confidence fallback).

**Coverage gap found:** the deterministic emergency-override policy has never actually had to override the LLM on real fixture data — on all 5 true-emergency cases the LLM independently returned `emergency` anyway. The override is "redundant-but-agreeing," not proven load-bearing. Before considering it done, need an adversarial test case where the LLM's natural read would *disagree* with a hardcoded emergency keyword, to prove the override actually fires.

**Open judgment call, not yet decided:** is the "+1 level toward caution on ambiguous input" pattern a bug to fix, or an acceptable/desirable safety margin? Silently correcting it risks flipping to the opposite, strictly worse failure mode (under-escalating a real emergency). Decide deliberately before changing prompt/calibration logic — don't default to "fix all misses" without considering which direction of error is more costly for this system.

**Phase 3 scoped around this evidence, not the roadmap's generic description:**
1. ~~Identify the 0.90-confidence wrong case~~ — it's **case_13** (ceiling stain "could give way" → emergency @ 0.90, expected high). Still need: diagnose why confidence stayed high.
2. ~~Add an adversarial override test to prove the override is load-bearing~~ — **DONE** (`test_override_forces_emergency_for_every_hardcoded_category_when_llm_says_low`, all 5 categories through the full classify() path). See the 2026-09-08 entry above.
3. Decide explicitly (log the decision) whether the +1-toward-caution bias should be corrected, left as-is, or bounded (e.g., allowed to over-escalate ambiguous cases but not by more than one level, which is already true)
4. Only then, if correction is chosen, adjust prompt/calibration — re-run the 20-case eval to confirm the fix doesn't introduce under-prediction on the true emergencies
5. Fix the noisy `missing_information` field (detection ~0.33) and address eval run-to-run variance (average ≥3 runs)

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