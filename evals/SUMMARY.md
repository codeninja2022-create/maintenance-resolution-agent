# Evaluation — 20 fixture cases

Model: `claude-opus-5` · Run: 2026-09-09 02:21 UTC

## Metrics

| Metric | Value |
|---|---|
| Valid structured-output rate | 1.0 |
| Category accuracy | 1.0 |
| Urgency accuracy | 0.95 |
| Emergency recall (of 5 emergencies) | 1.0 |
| Emergency precision | 1.0 |
| Missing-info detection accuracy | 0.25 |
| Out-of-domain handled correctly | 3/3 |
| PII leaks | 0 |
| Avg latency | 5692.9 ms |
| Avg cost / case | $0.01852 |
| Total run cost | $0.3704 |

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
| case_10 | electrical / electrical ✓ | normal / normal / normal ✓ | True / True ✓ | — |
| case_11 | other / other ✓ | low / normal / normal ✗ | True / True ✓ | — |
| case_12 | hvac / hvac ✓ | normal / normal / normal ✓ | False / True ✗ | — |
| case_13 | water_leak / water_leak ✓ | high / high / high ✓ | True / True ✓ | — |
| case_14 | plumbing / plumbing ✓ | high / high / high ✓ | False / True ✗ | — |
| case_15 | other / other ✓ | high / high / high ✓ | True / True ✓ | — |
| case_16 | not_maintenance / not_maintenance ✓ | low / low / low ✓ | False / False ✓ | — |
| case_17 | not_maintenance / not_maintenance ✓ | low / low / low ✓ | False / True ✗ | — |
| case_18 | access_lock / access_lock ✓ | normal / normal / normal ✓ | False / True ✗ | — |
| case_19 | not_maintenance / not_maintenance ✓ | low / low / low ✓ | False / True ✗ | — |
| case_20 | gas / gas ✓ | emergency / high / emergency ✓ | False / True ✗ | gas_leak (forced) |

## Urgency rationale

- **case_01** (conf 0.95, emergency→emergency): The tenant reports an actively worsening gas odor near the stove over the past hour, which is a present and immediate danger requiring immediate dispatch.
- **case_02** (conf 0.95, emergency→emergency): Water is actively pouring from the ceiling and spreading fast right now, which is causing ongoing property damage and possible electrical hazard, so it requires immediate dispatch.
- **case_03** (conf 0.93, emergency→emergency): Heat has been completely out since last night with outdoor temperatures below freezing and children in the unit, which is an actively dangerous habitability failure requiring immediate dispatch.
- **case_04** (conf 0.95, emergency→emergency): The tenant observed actual sparking from a bedroom outlet, which is an active fire and shock hazard requiring immediate dispatch.
- **case_05** (conf 0.95, emergency→emergency): A section of the bedroom ceiling has already collapsed leaving debris and an open hole directly above the bed, which is an active structural failure with ongoing risk of further collapse onto an occupant.
- **case_06** (conf 0.92, low→low): A slow drip that has persisted for weeks with no reported water damage or overflow is a minor, slow-developing repair rather than a time-sensitive one.
- **case_07** (conf 0.92, normal→normal): Standing water in a dishwasher after a cycle is a genuine repair need but is contained within the appliance with no active leak or property damage, so it can be scheduled over days rather than hours.
- **case_08** (conf 0.93, normal→normal): Rodent droppings in kitchen cabinets indicate an active pest issue needing treatment over the next few days, but there is no immediate health or safety danger described that would make it higher.
- **case_09** (conf 0.92, high→high): The tenant is currently locked out of their unit due to a jammed front door lock, which is time-sensitive and needs same-day attention, but it is not an active danger or destructive event warranting emergency dispatch.
- **case_10** (conf 0.62, normal→normal): A flickering light and a loose outlet warrant a prompt electrical check, but the tenant reports no sparking, burning smell, exposed wiring, or water damage, so this is a repair over days rather than an emergency; the continuously running toilet is a separate non-urgent plumbing item.
- **case_11** (conf 0.3, low→normal  ⚠ wrong): The tenant reports an ongoing problem of several days but gives no detail indicating active danger, water damage, or loss of an essential system, so it is treated as a routine repair need rather than high or emergency.
- **case_12** (conf 0.88, normal→normal): The AC is still running but rattling and cooling poorly, which is a genuine repair need over days rather than an active danger or total loss of a critical system, so it does not rise to high.
- **case_13** (conf 0.85, high→high): A spreading wet ceiling stain from the upstairs unit's overflow is a credible risk of ceiling failure, but the tenant only says it "looks like it could give way" and describes no active water pouring in or actual collapse, so it is time-sensitive rather than an emergency.
- **case_14** (conf 0.9, high→high): This is a third report of the same unresolved under-sink leak with water pooling again, making it a time-sensitive recurring failure, but it isn't an emergency because the water is contained under the sink rather than actively flooding the unit.
- **case_15** (conf 0.5, high→high): An unidentified odor in a shared hallway combined with a chirping smoke detector warrants a prompt same-day check, but it stays below emergency because the tenant does not describe gas, smoke, or any actively dangerous condition and is unsure the two are even related.
- **case_16** (conf 0.95, low→low): This is a neighbor noise and behavior complaint with no physical repair or building-system issue, so it carries no maintenance urgency.
- **case_17** (conf 0.97, low→low): This is a rent billing and account question with no physical repair or building-system issue involved, so it carries no maintenance urgency.
- **case_18** (conf 0.88, normal→normal): The parking gate code has failed for several days and repeatedly blocks the tenant's access, but they can still get in by waiting for another resident, so it is a genuine repair need rather than an urgent lockout.
- **case_19** (conf 0.95, low→low): This is a general question about the weather with no mention of any repair or building-system problem, so there is nothing time-sensitive to act on.
- **case_20** (conf 0.78, emergency→emergency): The tenant reports a faint, intermittent gas-like odor near the stove but hedges that it is "probably nothing" and describes no active strong leak, so this is a credible risk requiring same-day investigation rather than a confirmed active emergency.

## Read (updated by hand after each run)

**2026-09-09 — rubric fix confirmed stable over 3 runs.**

| | run 1 | run 2 | run 3 |
|---|---|---|---|
| category accuracy | 1.0 | 1.0 | 1.0 |
| urgency accuracy | 0.95 | 0.95 | 0.95 |
| emergency recall / precision | 1.0 / 1.0 | 1.0 / 1.0 | 1.0 / 1.0 |
| missing-info detection | 0.20 | 0.25 | 0.25 |

- **Zero urgency flips, zero category flips across all 3 runs.** The sole urgency
  miss is case_11 every time, at confidence exactly 0.30 every time.
- case_13 stable at `high` @ 0.85–0.86; case_15 stable at `high` @ 0.5–0.6.
- Pooled confidence calibration (60 classifications): correct n=57 mean 0.88;
  wrong n=3, all `[0.30]`. **No confidently-wrong case in any run.**
- The old ±1-case run variance (case_10, case_14 flipping) is gone too — both
  now stable. The rubric + the always-write-a-rationale requirement seem to have
  tightened the decision procedure.

**`missing_information` is measuring the wrong construct — see PROGRESS.md.**
The field is doing double duty (classification-relevant unknowns vs. an
operational checklist for the responder); the model answers the second, the
fixtures grade the first.
