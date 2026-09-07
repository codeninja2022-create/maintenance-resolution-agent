# Maintenance Resolution Intelligence Agent

Accepts an unclear tenant maintenance complaint and returns a structured
classification: category, urgency, missing information, recommended action,
and a confidence score.

See `DESIGN_BRIEF.md` for the full plan, `ROADMAP.md` for phase-by-phase
architecture, `DECISIONS.md` for the reasoning log, and `PROGRESS.md` +
`DAILY_PLAN.md` for current status.

## Phase 1 status: complete — messy issue in → validated structured output out, over HTTP

Evaluated on 15 cases (`evals/SUMMARY.md`): category accuracy 0.87, emergency
recall 1.0, 0 PII leaks. Weak spot: urgency runs hot (over-escalates ambiguous
cases). Phase 3 (classification refinement) is next.

## Setup

```bash
pip install -e ".[dev]"
```

## Run tests

```bash
pytest          # 37 offline tests, no API key needed
```

## Run the real classifier against fixture cases

Needs an Anthropic API key. Copy `.env.example` to `.env` and fill in
`ANTHROPIC_API_KEY` (or export it in your shell).

```bash
python scripts/run_classifier.py            # default sample of 5 cases
python scripts/run_classifier.py case_01     # a specific case
python scripts/run_classifier.py --all       # all 15
```

Model defaults to `claude-opus-5`; override with `RESOLVLY_CLASSIFIER_MODEL`.

## Run the API

```bash
uvicorn app.api:app --reload        # reads ANTHROPIC_API_KEY from .env
```

- Swagger UI: http://127.0.0.1:8000/docs
- `GET /health` → `{"status": "ok"}`
- `POST /classify` — body is an `Issue`, response is a `ClassificationResult`

```bash
curl -X POST http://127.0.0.1:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"description":"I smell gas near the stove, getting stronger.",
       "property":"12 Maple St","unit":"3B","attachments":[],"reporter":"tenant"}'
```

Status codes: `422` malformed body, `502` model could not classify, `500` other.

## Run the evaluation

```bash
python scripts/eval.py       # 15 real API calls (~$0.20), writes evals/SUMMARY.md
```

## Project layout

```
app/
  models.py      — Issue, ClassificationResult, ClassificationTrace
  classifier.py  — Classifier interface, MockClassifier, AnthropicClassifier
  policy.py      — deterministic emergency-override (gas, fire, flood, no-heat, collapse)
  redaction.py   — strips email / phone from returned text
  prompt.py      — the classification prompt
  api.py         — FastAPI app: POST /classify, GET /health
  config.py      — minimal .env loader
scripts/
  run_classifier.py  — manual runner against fixture cases
  eval.py            — run all 15 cases, compute metrics
evals/
  SUMMARY.md         — committed metrics record + strong/shaky read
tests/
  fixtures/cases.json — 15 synthetic evaluation cases
```
