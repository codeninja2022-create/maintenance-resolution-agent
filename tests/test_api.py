"""API tests — TestClient, no network. The classifier dependency is overridden."""

import pytest
from fastapi.testclient import TestClient

from app.api import app, get_classifier
from app.classifier import Classifier, ClassifierError, MockClassifier
from app.models import ClassificationResult, Issue

VALID_BODY = {
    "description": "Kitchen sink is leaking under the cabinet.",
    "property": "12 Maple St",
    "unit": "3B",
    "attachments": [],
    "reporter": "tenant",
}


@pytest.fixture
def client():
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


def use_classifier(instance: Classifier):
    app.dependency_overrides[get_classifier] = lambda: instance


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_classify_returns_structured_output(client):
    use_classifier(MockClassifier())
    r = client.post("/classify", json=VALID_BODY)
    assert r.status_code == 200
    body = r.json()
    # Round-trips through the response model.
    result = ClassificationResult.model_validate(body)
    assert result.category.value == "other"
    assert 0.0 <= result.confidence <= 1.0


def test_malformed_body_is_422(client):
    use_classifier(MockClassifier())
    r = client.post("/classify", json={"property": "12 Maple St", "unit": "3B"})
    assert r.status_code == 422


def test_classifier_error_is_502(client):
    class Failing(Classifier):
        def classify(self, issue: Issue) -> ClassificationResult:
            raise ClassifierError("model gave up after 3 attempts")

    use_classifier(Failing())
    r = client.post("/classify", json=VALID_BODY)
    assert r.status_code == 502
    assert "Classification failed" in r.json()["detail"]


def test_unexpected_error_is_500(client):
    class Exploding(Classifier):
        def classify(self, issue: Issue) -> ClassificationResult:
            raise RuntimeError("kaboom")

    use_classifier(Exploding())
    r = client.post("/classify", json=VALID_BODY)
    assert r.status_code == 500
    # Internal detail is not leaked.
    assert "kaboom" not in r.text
