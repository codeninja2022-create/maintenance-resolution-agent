# Evaluation — 19 fixture cases

Model: `claude-opus-5` · Run: 2026-09-08 11:52 UTC

## Metrics

| Metric | Value |
|---|---|
| Valid structured-output rate | 1.0 |
| Category accuracy | 0.947 |
| Urgency accuracy | 0.789 |
| Emergency recall (of 5 emergencies) | 1.0 |
| Emergency precision | 0.714 |
| Missing-info detection accuracy | 0.316 |
| Out-of-domain handled correctly | 3/3 |
| PII leaks | 0 |
| Avg latency | 5189.8 ms |
| Avg cost / case | $0.01474 |
| Total run cost | $0.28 |

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
| case_14 | plumbing / plumbing ✓ | high / high / high ✓ | False / True ✗ | — |
| case_15 | other / gas ✗ | high / emergency / emergency ✗ | True / True ✓ | — |
| case_16 | not_maintenance / not_maintenance ✓ | low / low / low ✓ | False / False ✓ | — |
| case_17 | not_maintenance / not_maintenance ✓ | low / low / low ✓ | False / True ✗ | — |
| case_18 | access_lock / access_lock ✓ | normal / normal / normal ✓ | False / True ✗ | — |
| case_19 | not_maintenance / not_maintenance ✓ | low / low / low ✓ | False / False ✓ | — |

## Read (updated by hand after each run)

**2026-09-08, 19 cases (added `not_maintenance` category + case_16/17/19 out-of-domain, case_18 borderline).**

- **Out-of-domain detection: 3/3.** case_16 (noise), case_17 (billing), case_19
  ("what's the weather") all → `not_maintenance` / `low` / conf 0.95, no
  missing-info questions on 16 and 19. The scope-rule prompt block works.
- **Borderline 1/1.** case_18 (parking-gate code) → `access_lock` / `normal` /
  0.88 — correctly kept as maintenance, not over-escalated.
- **No regression** from the enum/prompt change: same single category miss
  (case_15 other→gas) and same 4 urgency over-escalations (case_10/11/13/15).
- **Run-to-run variance is real.** opus-5 with no temperature control: between
  the 18- and 19-case runs, case_14 category flipped (water_leak↔plumbing) and
  case_01's `missing_information` flipped (empty↔populated). Single-run numbers
  carry roughly ±1 case of noise — for Phase 3, average 3 runs or treat
  sub-0.05 metric moves as noise.
- Urgency bias unchanged: 15/19 correct, every miss a +1 over-escalation on a
  deliberately-ambiguous case. case_13 still the confidently-wrong one
  (emergency @ 0.90, expected high).
- `missing_information` still noisy (detection 0.32).
- Cost/latency: $0.015 / 5.2 s per case.
