# Evaluation — 20 fixture cases

Model: `claude-opus-5` · Run: 2026-09-09 02:02 UTC

## Metrics

| Metric | Value |
|---|---|
| Valid structured-output rate | 1.0 |
| Category accuracy | 1.0 |
| Urgency accuracy | 0.95 |
| Emergency recall (of 5 emergencies) | 1.0 |
| Emergency precision | 1.0 |
| Missing-info detection accuracy | 0.2 |
| Out-of-domain handled correctly | 3/3 |
| PII leaks | 0 |
| Avg latency | 6131.8 ms |
| Avg cost / case | $0.01914 |
| Total run cost | $0.3829 |

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
| case_16 | not_maintenance / not_maintenance ✓ | low / low / low ✓ | False / True ✗ | — |
| case_17 | not_maintenance / not_maintenance ✓ | low / low / low ✓ | False / True ✗ | — |
| case_18 | access_lock / access_lock ✓ | normal / normal / normal ✓ | False / True ✗ | — |
| case_19 | not_maintenance / not_maintenance ✓ | low / low / low ✓ | False / True ✗ | — |
| case_20 | gas / gas ✓ | emergency / high / emergency ✓ | False / True ✗ | gas_leak (forced) |

## Urgency rationale

- **case_01** (conf 0.95, emergency→emergency): The tenant reports an actively worsening gas odor near the stove over the past hour, which is an ongoing hazard requiring immediate dispatch rather than a hedged or speculative risk.
- **case_02** (conf 0.95, emergency→emergency): Water is actively pouring from the living room ceiling and spreading fast, which is causing immediate property damage and a possible ceiling collapse or electrical hazard.
- **case_03** (conf 0.93, emergency→emergency): Heat has been completely out overnight with outside temperatures below freezing and children in the unit, so this is an actively dangerous loss of an essential system requiring immediate dispatch.
- **case_04** (conf 0.95, emergency→emergency): Visible sparking from an outlet is active arcing that presents an immediate fire and shock hazard, so it warrants same-day emergency dispatch rather than a scheduled repair.
- **case_05** (conf 0.95, emergency→emergency): A section of the bedroom ceiling has already collapsed over the bed, leaving debris and an open hole, which is an active structural failure with ongoing risk of further collapse and injury.
- **case_06** (conf 0.93, low→low): A slow drip that has persisted for a couple of weeks with no reported pooling, spraying, or water damage is a minor, non-time-sensitive repair rather than an active or worsening leak.
- **case_07** (conf 0.92, normal→normal): Standing water pooling in a dishwasher after a cycle is a genuine repair need but it is contained within the appliance with no active overflow or property damage, so it does not rise above normal.
- **case_08** (conf 0.92, normal→normal): Rodent droppings in kitchen cabinets indicate an active pest issue that needs pest-control treatment within days, but there is no immediate safety hazard or property damage occurring, so it does not rise above normal.
- **case_09** (conf 0.93, high→high): The tenant is locked out of their unit right now due to a jammed front door lock, which is time-sensitive and needs attention within hours, but it is not an emergency because no active danger or property damage is occurring.
- **case_10** (conf 0.6, normal→normal): Flickering light plus a loose outlet suggests a possible wiring fault worth prompt attention, but it is not higher because the tenant reports no sparking, burning smell, or shock, and the running toilet is a non-urgent water-waste issue.
- **case_11** (conf 0.3, low→normal  ⚠ wrong): The tenant reports an ongoing problem of several days but gives no detail indicating active danger, damage, or loss of an essential service, so it is treated as a routine repair need rather than high or emergency.
- **case_12** (conf 0.88, normal→normal): The AC is still running but rattling and cooling poorly, which is a genuine repair need over days rather than an active danger or total loss of a critical system, so it does not rise to high or emergency.
- **case_13** (conf 0.85, high→high): Water from the upstairs unit has already saturated the ceiling and the stain is spreading, but the tenant only says it looks like it could give way rather than describing an active collapse or water pouring in, so this is a credible imminent risk rather than an emergency in progress.
- **case_14** (conf 0.89, high→high): This is a recurring failed repair with water pooling again under the sink, which is time-sensitive, but it is a contained under-sink leak rather than water actively pouring in, so it is not an emergency.
- **case_15** (conf 0.6, high→high): An unidentified hallway odor combined with a chirping smoke detector warrants a same-day check because the smell could indicate gas, burning, or sewer gas, but it stays below emergency since the tenant cannot identify the odor and describes no smoke, flame, or active alarm.
- **case_16** (conf 0.95, low→low): This is a neighbor noise and behavior complaint rather than a physical repair or building-system issue, so it carries no maintenance urgency and is routed as low priority.
- **case_17** (conf 0.97, low→low): This is a billing and account question about an unexplained fee rather than any physical repair or building-system problem, so it carries no safety or property-damage time pressure.
- **case_18** (conf 0.86, normal→normal): The parking gate code has failed for several days and the tenant can still get in with help from others, so it is a genuine access repair need over days rather than a lockout or safety issue requiring same-day dispatch.
- **case_19** (conf 0.95, low→low): This is a general question about the weather with no mention of any repair or building-system problem, so there is nothing time-sensitive to act on.
- **case_20** (conf 0.78, emergency→emergency): The tenant reports a faint, hedged gas-like odor near the stove rather than a confirmed active leak, which makes it a credible risk requiring same-day investigation but not a confirmed emergency; the squeaky cabinet hinge is trivial by comparison.

## Read (updated by hand after each run)

_See the paragraph in PROGRESS.md for the current interpretation._
