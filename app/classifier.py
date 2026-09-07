"""Classifier abstraction.

Lets the API depend on an interface, not a specific model provider, so the
underlying model can change later without touching the endpoint.

    Classifier
      ├── MockClassifier      (Day 1 — deterministic, no API calls, for fast tests)
      └── AnthropicClassifier (Day 3 — real LLM-backed implementation)

Only one real implementation is planned for Phase 1 (locked stack: "one
hosted LLM"). This abstraction exists so that swap is cheap later, not to
support multiple providers now — see DECISIONS.md re: LiteLLM being deferred.
"""

from abc import ABC, abstractmethod

from app.models import ClassificationResult, Issue


class Classifier(ABC):
    """Interface every classifier implementation must satisfy."""

    @abstractmethod
    def classify(self, issue: Issue) -> ClassificationResult:
        """Given an Issue, return a structured ClassificationResult."""
        raise NotImplementedError


class MockClassifier(Classifier):
    """Deterministic, no-API-call classifier for fast unit tests.

    Returns a fixed, valid ClassificationResult regardless of input, purely
    so the rest of the system (endpoint, schema validation, tests) can be
    built and tested before a real LLM call is wired in on Day 3.
    """

    def classify(self, issue: Issue) -> ClassificationResult:
        return ClassificationResult(
            category="other",
            urgency="low",
            missing_information=[],
            recommended_action="Mock response — no real classification performed.",
            confidence=0.5,
            trace=None,
        )
