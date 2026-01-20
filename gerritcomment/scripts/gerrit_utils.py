#!/usr/bin/env python3
"""Shared utilities for Gerrit scripts."""
from __future__ import annotations

import os
from urllib.parse import urlparse


class GerritError(Exception):
    """Base error for Gerrit operations."""


def parse_change_url(url: str) -> tuple[str, str]:
    """Parse Gerrit change URL, return (base_url, change_ref)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise GerritError(f"Invalid Gerrit URL: {url}")

    base_url = f"{parsed.scheme}://{parsed.netloc}"
    parts = [p for p in parsed.path.split("/") if p]

    if "+" in parts:
        idx = parts.index("+")
        if idx + 1 < len(parts):
            return base_url, parts[idx + 1]

    raise GerritError("URL must contain '+/<change_ref>'")


def get_config() -> tuple[str, str, str]:
    """Load config from environment, return (base_url, username, password)."""
    base_url = os.environ.get("GERRIT_BASE_URL", "").strip()
    username = os.environ.get("GERRIT_USER", "").strip()
    password = os.environ.get("GERRIT_HTTP_PASSWORD", "").strip()

    missing = []
    if not base_url:
        missing.append("GERRIT_BASE_URL")
    if not username:
        missing.append("GERRIT_USER")
    if not password:
        missing.append("GERRIT_HTTP_PASSWORD")

    if missing:
        missing_str = ", ".join(missing)
        raise GerritError(f"Missing environment variables: {missing_str}")

    return base_url, username, password
