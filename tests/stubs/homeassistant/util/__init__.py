"""Minimaler Ersatz fuer homeassistant.util."""
from __future__ import annotations

import re
import unicodedata


def slugify(text: str | None, *, separator: str = "_") -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", separator, text.lower()).strip(separator)
    return slug or "unknown"
