"""Day 5 evaluation — run all 15 fixture cases through the real classifier and
compute metrics, not vibes.

Writes two files:
  evals/latest_run.json  — full per-case results (git-ignored, regenerated)
  evals/SUMMARY.md        — the metrics table (committed, this is the record)

Usage (from repo root, needs ANTHROPIC_API_KEY):
    python scripts/eval.py

Makes 15 real API calls (~$0.20 at current prices).
"""

import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "cases.json"
EVALS_DIR = REPO_ROOT / "evals"


def run_all(cases: list) -> list:
    from app.classifier import AnthropicClassifier, ClassifierError
    from app.models import Issue
    from app.redaction import contains_pii

    classifier = AnthropicClassifier()
    rows = []
    for case in cases:
        issue = Issue(
            description=case["description"],
            property=case["property"],
            unit=case["unit"],
            attachments=case["attachments"],
            reporter=case["reporter"],
        )
        row = {
            "id": case["id"],
            "expected_category": case["expected_category"],
            "expected_urgency": case["expected_urgency"],
            "expected_missing_info": bool(case["expected_missing_information"]),
        }
        try:
            r = classifier.classify(issue)
        except ClassifierError as e:
            row["error"] = str(e)
            rows.append(row)
            continue

        pii_leaked = (
            contains_pii(r.recommended_action)
            or contains_pii(r.urgency_rationale)
            or any(contains_pii(m) for m in r.missing_information)
        )
        row.update(
            {
                "got_category": r.category.value,
                "got_urgency": r.urgency.value,
                "got_llm_urgency": r.llm_urgency.value,
                "urgency_rationale": r.urgency_rationale,
                "got_missing_info": bool(r.missing_information),
                "emergency_override_applied": r.emergency_override_applied,
                "matched_emergency_rule": r.matched_emergency_rule,
                "confidence": r.confidence,
                "pii_leaked": pii_leaked,
                "latency_ms": r.trace.latency_ms if r.trace else None,
                "estimated_cost": r.trace.estimated_cost if r.trace else None,
            }
        )
        rows.append(row)
    return rows


def compute_metrics(rows: list) -> dict:
    ok = [r for r in rows if "error" not in r]
    n = len(rows)
    n_ok = len(ok)

    def rate(predicate, sample):
        sample = list(sample)
        return round(sum(1 for r in sample if predicate(r)) / len(sample), 3) if sample else None

    expected_emergencies = [r for r in ok if r["expected_urgency"] == "emergency"]
    predicted_emergencies = [r for r in ok if r["got_urgency"] == "emergency"]

    latencies = [r["latency_ms"] for r in ok if r.get("latency_ms") is not None]
    costs = [r["estimated_cost"] for r in ok if r.get("estimated_cost") is not None]

    ood = [r for r in ok if r["expected_category"] == "not_maintenance"]
    ood_correct = sum(
        1
        for r in ood
        if r["got_category"] == "not_maintenance" and r["got_urgency"] in ("low", "normal")
    )

    return {
        "n_cases": n,
        "valid_output_rate": round(n_ok / n, 3),
        "category_accuracy": rate(lambda r: r["got_category"] == r["expected_category"], ok),
        "urgency_accuracy": rate(lambda r: r["got_urgency"] == r["expected_urgency"], ok),
        "emergency_recall": rate(
            lambda r: r["got_urgency"] == "emergency", expected_emergencies
        ),
        "emergency_precision": rate(
            lambda r: r["expected_urgency"] == "emergency", predicted_emergencies
        ),
        "missing_info_detection_accuracy": rate(
            lambda r: r["got_missing_info"] == r["expected_missing_info"], ok
        ),
        "out_of_domain_cases": len(ood),
        "out_of_domain_correct": ood_correct,
        "pii_leak_count": sum(1 for r in ok if r.get("pii_leaked")),
        "avg_latency_ms": round(statistics.mean(latencies), 1) if latencies else None,
        "avg_cost_usd": round(statistics.mean(costs), 5) if costs else None,
        "total_cost_usd": round(sum(costs), 4) if costs else None,
    }


def write_summary(metrics: dict, rows: list, model: str) -> None:
    EVALS_DIR.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Evaluation — {len(rows)} fixture cases",
        "",
        f"Model: `{model}` · Run: {ts}",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Valid structured-output rate | {metrics['valid_output_rate']} |",
        f"| Category accuracy | {metrics['category_accuracy']} |",
        f"| Urgency accuracy | {metrics['urgency_accuracy']} |",
        f"| Emergency recall (of 5 emergencies) | {metrics['emergency_recall']} |",
        f"| Emergency precision | {metrics['emergency_precision']} |",
        f"| Missing-info detection accuracy | {metrics['missing_info_detection_accuracy']} |",
        f"| Out-of-domain handled correctly | {metrics['out_of_domain_correct']}/{metrics['out_of_domain_cases']} |",
        f"| PII leaks | {metrics['pii_leak_count']} |",
        f"| Avg latency | {metrics['avg_latency_ms']} ms |",
        f"| Avg cost / case | ${metrics['avg_cost_usd']} |",
        f"| Total run cost | ${metrics['total_cost_usd']} |",
        "",
        "## Per-case",
        "",
        "| Case | Category (exp / got) | Urgency (exp / llm / final) | Missing-info (exp / got) | Override |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        if "error" in r:
            lines.append(f"| {r['id']} | ERROR: {r['error']} | | | |")
            continue
        cat = f"{r['expected_category']} / {r['got_category']}"
        cat += " ✓" if r["got_category"] == r["expected_category"] else " ✗"
        urg = f"{r['expected_urgency']} / {r['got_llm_urgency']} / {r['got_urgency']}"
        urg += " ✓" if r["got_urgency"] == r["expected_urgency"] else " ✗"
        mi = f"{r['expected_missing_info']} / {r['got_missing_info']}"
        mi += " ✓" if r["got_missing_info"] == r["expected_missing_info"] else " ✗"
        ov = r["matched_emergency_rule"] or "—"
        if r["emergency_override_applied"]:
            ov += " (forced)"
        lines.append(f"| {r['id']} | {cat} | {urg} | {mi} | {ov} |")

    lines += ["", "## Urgency rationale", ""]
    for r in rows:
        if "error" in r:
            continue
        mark = "" if r["got_urgency"] == r["expected_urgency"] else "  ⚠ wrong"
        lines.append(
            f"- **{r['id']}** (conf {r['confidence']}, "
            f"{r['expected_urgency']}→{r['got_urgency']}{mark}): {r['urgency_rationale']}"
        )

    lines += [
        "",
        "## Read (updated by hand after each run)",
        "",
        "_See the paragraph in PROGRESS.md for the current interpretation._",
    ]
    (EVALS_DIR / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    from app.classifier import DEFAULT_MODEL
    from app.config import load_dotenv

    load_dotenv()
    import os

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set (shell or .env).")
        return 1

    cases = json.loads(FIXTURES.read_text())
    print(f"Running {len(cases)} cases through {DEFAULT_MODEL} ...")
    rows = run_all(cases)
    metrics = compute_metrics(rows)

    EVALS_DIR.mkdir(exist_ok=True)
    (EVALS_DIR / "latest_run.json").write_text(
        json.dumps({"model": DEFAULT_MODEL, "metrics": metrics, "cases": rows}, indent=2),
        encoding="utf-8",
    )
    write_summary(metrics, rows, DEFAULT_MODEL)

    print("\n" + json.dumps(metrics, indent=2))
    print(f"\nWrote evals/SUMMARY.md and evals/latest_run.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
