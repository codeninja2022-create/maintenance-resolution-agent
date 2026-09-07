"""PII redaction unit tests (offline)."""

from app.redaction import contains_pii, redact_all, redact_text


def test_email_is_redacted():
    out = redact_text("Reach me at jane.doe+test@example.co.uk about the leak.")
    assert "jane.doe+test@example.co.uk" not in out
    assert "[redacted-email]" in out
    assert not contains_pii(out)


def test_phone_numbers_are_redacted():
    for raw in [
        "call 555-123-4567",
        "call (555) 123-4567",
        "call +1 555.123.4567",
        "call 1-555-123-4567",
    ]:
        out = redact_text(raw)
        assert "[redacted-phone]" in out, raw
        assert not contains_pii(out), raw


def test_non_pii_content_is_preserved():
    text = "Unit 3B, reported 2026-09-07, pipe is 2 inches, been 14 days."
    assert redact_text(text) == text


def test_redact_all_handles_a_list():
    items = ["email foo@bar.com", "nothing sensitive here"]
    out = redact_all(items)
    assert out[0] == "email [redacted-email]"
    assert out[1] == "nothing sensitive here"
