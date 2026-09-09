"""Re-score a saved eval run against the CURRENT fixture expectations.

Use when the fixtures' expected_* values change but the model output did not —
recomputes metrics and rewrites evals/SUMMARY.md from a saved run file, with no
new API calls.

    python scripts/rescore.py path/to/run.json
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.eval import compute_metrics, write_summary, FIXTURES, EVALS_DIR  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    run = json.loads(Path(sys.argv[1]).read_text())
    rows = run["cases"]
    fixtures = {c["id"]: c for c in json.loads(FIXTURES.read_text())}

    # Refresh the expected_* fields on each row from the current fixtures;
    # leave the model's got_* output untouched.
    for r in rows:
        f = fixtures[r["id"]]
        r["expected_category"] = f["expected_category"]
        r["expected_urgency"] = f["expected_urgency"]
        r["expected_missing_info"] = bool(f["expected_missing_information"])

    metrics = compute_metrics(rows)
    model = run.get("model", "unknown")

    EVALS_DIR.mkdir(exist_ok=True)
    (EVALS_DIR / "latest_run.json").write_text(
        json.dumps({"model": model, "metrics": metrics, "cases": rows, "rescored": True}, indent=2),
        encoding="utf-8",
    )
    write_summary(metrics, rows, model)

    print(json.dumps(metrics, indent=2))
    print("\nRe-scored — wrote evals/SUMMARY.md and evals/latest_run.json (rescored: true)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
