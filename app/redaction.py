"""PII redaction for classifier output.

Phase 1 rule (see DECISIONS.md, 2026-09-07): sensitive-looking text that a
tenant accidentally types into a free-text complaint — a phone number, an
email address — must never be echoed back unredacted in the structured
output. This is a defence-in-depth layer: the prompt also instructs the model
not to repeat contact details, but we do not rely on the model for a safety
property. Every string field returned to the caller passes through here.

Deliberately narrow: only high-precision patterns (email, phone) so we don't
mangle legitimate content (unit numbers, dates, measurements). Name detection
is explicitly out of scope for Phase 1 — it needs NER and has a high false-positive
rate on ordinary words; deferred with the rest of the privacy work to Phase 8.
"""

import re
from typing import List

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# North-American style phone numbers: optional +1, then 10 digits with common
# separators ( ) - . or space. Requires at least one separator or grouping so
# we don't match a bare 10-digit ID.
PHONE_RE = re.compile(
    r"""(?x)
    (?<!\d)
    (?:\+?1[\s.-]?)?
    (?:
        \(\d{3}\)[\s.-]?\d{3}[\s.-]?\d{4}
      | \d{3}[\s.-]\d{3}[\s.-]\d{4}
    )
    (?!\d)
    """
)

EMAIL_PLACEHOLDER = "[redacted-email]"
PHONE_PLACEHOLDER = "[redacted-phone]"


def redact_text(text: str) -> str:
    """Return `text` with email addresses and phone numbers replaced by placeholders."""
    text = EMAIL_RE.sub(EMAIL_PLACEHOLDER, text)
    text = PHONE_RE.sub(PHONE_PLACEHOLDER, text)
    return text


def redact_all(items: List[str]) -> List[str]:
    """Redact every string in a list."""
    return [redact_text(item) for item in items]


def contains_pii(text: str) -> bool:
    """True if `text` still contains an email or phone number. Used by tests."""
    return bool(EMAIL_RE.search(text) or PHONE_RE.search(text))
