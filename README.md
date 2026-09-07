# Maintenance Resolution Intelligence Agent

Accepts an unclear tenant maintenance complaint and returns a structured
classification: category, urgency, missing information, recommended action,
and a confidence score.

See `DESIGN_BRIEF.md` for the full plan, `ROADMAP.md` for phase-by-phase
architecture, `DECISIONS.md` for the reasoning log, and `PROGRESS.md` +
`DAILY_PLAN.md` for current status.

## Phase 1 status: Day 1 in progress

## Setup

```bash
pip install -e ".[dev]"
```

## Run tests

```bash
pytest
```

## Project layout

```
app/
  models.py      — Issue, ClassificationResult, ClassificationTrace
  classifier.py  — Classifier interface, MockClassifier (real LLM classifier: Day 3)
tests/
  fixtures/cases.json — 15 synthetic evaluation cases
```
