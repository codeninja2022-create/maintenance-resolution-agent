# Phase 1 evaluation — 15 fixture cases

Model: `claude-opus-5` · Run: 2026-09-07 22:49 UTC

## Metrics

| Metric | Value |
|---|---|
| Valid structured-output rate | 1.0 |
| Category accuracy | 0.867 |
| Urgency accuracy | 0.733 |
| Emergency recall (of 5 emergencies) | 1.0 |
| Emergency precision | 0.714 |
| Missing-info detection accuracy | 0.267 |
| PII leaks | 0 |
| Avg latency | 5485.4 ms |
| Avg cost / case | $0.01406 |
| Total run cost | $0.2109 |

## Per-case

| Case | Category (exp / got) | Urgency (exp / llm / final) | Missing-info (exp / got) | Override |
|---|---|---|---|---|
| case_01 | gas / gas ✓ | emergency / emergency / emergency ✓ | False / True ✗ | gas_leak |
| case_02 | water_leak / water_leak ✓ | emergency / emergency / emergency ✓ | False / True ✗ | active_flooding |
| case_03 | hvac / hvac ✓ | emergency / emergency / emergency ✓ | False / True ✗ | no_heat_freezing |
| case_04 | electrical / electrical ✓ | emergency / emergency / emergency ✓ | False / True ✗ | fire_or_sparks |
| case_05 | structural / structural ✓ | emergency / emergency / emergency ✓ | False / True ✗ | structural_collapse |
| case_06 | plumbing / plumbing ✓ | low / low / low ✓ | False / True ✗ | — |
| case_07 | appliance / appliance ✓ | normal / normal / normal ✓ | False / True ✗ | — |
| case_08 | pest / pest ✓ | normal / normal / normal ✓ | False / True ✗ | — |
| case_09 | access_lock / access_lock ✓ | high / high / high ✓ | False / True ✗ | — |
| case_10 | electrical / electrical ✓ | normal / high / high ✗ | True / True ✓ | — |
| case_11 | other / other ✓ | low / normal / normal ✗ | True / True ✓ | — |
| case_12 | hvac / hvac ✓ | normal / normal / normal ✓ | False / True ✗ | — |
| case_13 | water_leak / water_leak ✓ | high / emergency / emergency ✗ | True / True ✓ | — |
| case_14 | plumbing / water_leak ✗ | high / high / high ✓ | False / True ✗ | — |
| case_15 | other / gas ✗ | high / emergency / emergency ✗ | True / True ✓ | — |

## Read (updated by hand after each run)

**Strong.** Category (0.87) and the safety layer. Emergency recall is 1.0 — every one of the 5 true emergencies was flagged, and the deterministic policy fired correctly on all 5 (not relied on: the model independently agreed each time). Zero PII leaks. Zero malformed outputs across 15 calls.

**Shaky — the model runs hot on urgency.** Urgency accuracy is 0.73 and *every one of the 4 misses is an over-escalation* (case_10 normal→high, case_11 low→normal, case_13 high→emergency, case_15 high→emergency). Emergency precision is 0.71 — the model called 7 emergencies, 2 of them (case_13, case_15) wrong, both LLM-driven not policy-driven. For a triage tool this bias is arguably the safe direction, but it inflates the emergency queue.

**Shaky — `missing_information` is low-signal.** Detection accuracy 0.27: the model attaches clarifying questions to 14 of 15 cases, including ones the fixtures consider fully actionable. It never says "I have enough to act." As-is the field can't be used to gate human review.

**Cost/latency.** $0.014 and 5.5 s per case on `claude-opus-5` — fine for a demo, expensive for volume. Worth A/B-ing Sonnet/Haiku before Phase 3.
