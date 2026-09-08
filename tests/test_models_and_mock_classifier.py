import json
from pathlib import Path

import pytest

from app.classifier import MockClassifier
from app.models import ClassificationResult, Issue


FIXTURES_PATH = Path(__file__).parent / "fixtures" / "cases.json"


def load_fixture_cases():
    with open(FIXTURES_PATH) as f:
        return json.load(f)


def test_issue_model_accepts_valid_data():
    issue = Issue(
        description="Kitchen sink is leaking.",
        property="12 Maple St",
        unit="3B",
        attachments=[],
        reporter="tenant",
    )
    assert issue.description == "Kitchen sink is leaking."


def test_all_fixture_cases_parse_as_valid_issues():
    cases = load_fixture_cases()
    assert len(cases) == 19
    for case in cases:
        issue = Issue(
            description=case["description"],
            property=case["property"],
            unit=case["unit"],
            attachments=case["attachments"],
            reporter=case["reporter"],
        )
        assert issue.description


def test_mock_classifier_returns_valid_classification_result():
    classifier = MockClassifier()
    issue = Issue(
        description="Something is broken.",
        property="1 Test St",
        unit="1A",
        attachments=[],
        reporter="tenant",
    )
    result = classifier.classify(issue)
    assert isinstance(result, ClassificationResult)
    assert 0.0 <= result.confidence <= 1.0


def test_no_pii_fields_present_in_fixture_cases():
    """Guard against accidentally introducing names/phones/emails into synthetic data."""
    cases = load_fixture_cases()
    forbidden_field_names = {"name", "phone", "email", "tenant_name"}
    for case in cases:
        assert forbidden_field_names.isdisjoint(case.keys())
        assert "@" not in case["description"]
