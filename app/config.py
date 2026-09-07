"""Minimal environment loading — no dependency.

Reads a `.env` file at the repo root (KEY=VALUE lines, `#` comments) into
os.environ without overriding anything already set. Kept dependency-free on
purpose; python-dotenv can come in later if config grows.
"""

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or (REPO_ROOT / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
