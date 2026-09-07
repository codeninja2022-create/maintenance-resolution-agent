"""Manually run the real AnthropicClassifier against fixture cases.

Day 3 check (see DAILY_PLAN.md): eyeball structured output + trace/cost on a
few cases, and confirm the emergency override fires.

Usage (from repo root):
    python scripts/run_classifier.py                # runs a default sample
    python scripts/run_classifier.py case_01 case_10 # runs specific cases
    python scripts/run_classifier.py --all           # runs all 15

Needs ANTHROPIC_API_KEY in the environment or in a .env file at the repo root.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "cases.json"
DEFAULT_SAMPLE = ["case_01", "case_06", "case_10", "case_11", "case_13"]


def main() -> int:
    import os

    from app.config import load_dotenv

    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY is not set.\n"
            "Set it in your shell, or copy .env.example to .env and fill it in."
        )
        return 1

    from app.classifier import AnthropicClassifier
    from app.models import Issue

    cases = {c["id"]: c for c in json.loads(FIXTURES.read_text())}

    args = sys.argv[1:]
    if args == ["--all"]:
        wanted = list(cases)
    elif args:
        wanted = args
    else:
        wanted = DEFAULT_SAMPLE

    classifier = AnthropicClassifier()
    print(f"Model: {classifier._model}\n")

    for case_id in wanted:
        case = cases.get(case_id)
        if case is None:
            print(f"!! unknown case id: {case_id}")
            continue

        issue = Issue(
            description=case["description"],
            property=case["property"],
            unit=case["unit"],
            attachments=case["attachments"],
            reporter=case["reporter"],
        )
        result = classifier.classify(issue)

        print("=" * 72)
        print(f"{case_id}: {case['description']}")
        print(
            f"  expected: category={case['expected_category']} "
            f"urgency={case['expected_urgency']}"
        )
        print(f"  got:      {result.model_dump_json(indent=2)}")
        if result.emergency_override_applied:
            print(
                f"  >> EMERGENCY OVERRIDE: model said '{result.llm_urgency.value}', "
                f"policy rule '{result.matched_emergency_rule}' forced 'emergency'"
            )
        elif result.matched_emergency_rule:
            print(
                f"  >> emergency policy rule '{result.matched_emergency_rule}' matched "
                f"(model already said 'emergency' — no change needed)"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
