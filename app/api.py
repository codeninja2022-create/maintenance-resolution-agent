"""FastAPI surface — Phase 1, Day 4.

One endpoint: POST /classify takes an Issue, returns a ClassificationResult
(category, urgency, missing_information, recommended_action, confidence, plus
the emergency-override outcome and a cost/latency trace).

The classifier is a FastAPI dependency so tests can swap in MockClassifier
without touching the network. `GET /health` is included for uptime checks and
to make the app trivially testable without an API key.
"""

import logging
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException

from app.classifier import AnthropicClassifier, Classifier, ClassifierError
from app.config import load_dotenv
from app.models import ClassificationResult, Issue

logger = logging.getLogger("resolvly.api")

# Pick up ANTHROPIC_API_KEY from a .env file for local dev (`uvicorn app.api:app`).
load_dotenv()

app = FastAPI(
    title="Maintenance Resolution Intelligence Agent",
    description="Classify an unclear tenant maintenance complaint into structured output.",
    version="0.1.0",
)


@lru_cache
def get_classifier() -> Classifier:
    """Real classifier, built once. Overridden in tests via dependency_overrides."""
    return AnthropicClassifier()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/classify", response_model=ClassificationResult)
def classify(
    issue: Issue,
    classifier: Classifier = Depends(get_classifier),
) -> ClassificationResult:
    """Classify a single maintenance complaint.

    - 422: request body is not a valid Issue (handled by FastAPI)
    - 502: the model could not produce a valid classification
    - 500: anything else went wrong server-side
    """
    try:
        return classifier.classify(issue)
    except ClassifierError as e:
        logger.warning("classification failed: %s", e)
        raise HTTPException(status_code=502, detail=f"Classification failed: {e}")
    except Exception:  # noqa: BLE001 — deliberately broad; don't leak internals to the caller
        logger.exception("unexpected error during classification")
        raise HTTPException(status_code=500, detail="Internal error during classification")
