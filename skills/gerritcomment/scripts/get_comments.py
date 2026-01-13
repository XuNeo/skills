#!/usr/bin/env python3
"""Fetch Gerrit review comments for a change. Self-contained, no external dependencies except python-gerrit-api."""
from __future__ import annotations

import argparse
import json
import os
import sys
from urllib.parse import urlparse

from gerrit import GerritClient
from requests import HTTPError


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
        raise GerritError(f"Missing environment variables: {', '.join(missing)}")

    return base_url, username, password


def fetch_comments(base_url: str, change_ref: str, revision: str | None = None,
                   unresolved_only: bool = True) -> dict:
    """Fetch comments from Gerrit API.

    Args:
        base_url: Gerrit server base URL.
        change_ref: Change number or Change-Id.
        revision: Optional revision (SHA, patch set number, or 'current').
        unresolved_only: If True, only return unresolved comments (default: True).

    Returns:
        Dict with 'comments' list and 'latest_patchset' number.
    """
    _, username, password = get_config()
    client = GerritClient(base_url=base_url, username=username, password=password)

    try:
        change = client.changes.get(change_ref)
        # Get latest patchset number via direct API call with CURRENT_REVISION option
        change_data = client.get(f"/changes/{change_ref}?o=CURRENT_REVISION")
        current_rev_sha = change_data.get("current_revision")
        revisions = change_data.get("revisions", {})
        latest_patchset = revisions.get(current_rev_sha, {}).get("_number") if current_rev_sha else None
        if revision:
            raw = change.get_revision(revision).comments.list()
        else:
            raw = change.list_comments()
    except HTTPError as e:
        status = e.response.status_code if e.response is not None else 0
        if status == 401:
            raise GerritError("Authentication failed (401)")
        if status == 404:
            raise GerritError("Change not found (404)")
        raise GerritError(f"HTTP error: {e}")
    except Exception as e:
        raise GerritError(str(e))

    # Flatten, filter and format comments with essential fields only
    comments = []
    for path, items in raw.items():
        for c in items:
            is_unresolved = bool(c.get("unresolved"))

            # Skip resolved comments if unresolved_only is True
            if unresolved_only and not is_unresolved:
                continue

            # Extract author name (prefer display_name, fallback to name)
            author_info = c.get("author", {})
            author_name = author_info.get("display_name") or author_info.get("name") or "Unknown"

            # Build simplified comment object
            comment = {
                "file": path or None,
                "range": c.get("range"),
                "patch_set": c.get("patch_set"),
                "author": author_name,
                "message": c.get("message", "").strip(),
            }

            # Only include unresolved field if showing all comments
            if not unresolved_only:
                comment["unresolved"] = is_unresolved

            comments.append(comment)

    comments.sort(key=lambda x: (x.get("patch_set") or 0, x.get("file") or "", x.get("line") or 0))
    return {"comments": comments, "latest_patchset": latest_patchset}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch Gerrit review comments as JSON")
    parser.add_argument("--change", required=True, help="Change URL, number, or Change-Id")
    parser.add_argument("--revision", help="Revision (SHA, patch set number, or 'current')")
    parser.add_argument("--all", action="store_true", dest="show_all",
                        help="Show all comments (default: only unresolved)")
    args = parser.parse_args(argv)

    change = args.change.strip()
    revision = args.revision.strip() if args.revision else None
    unresolved_only = not args.show_all

    try:
        # Determine base_url and change_ref
        if change.startswith(("http://", "https://")):
            base_url, change_ref = parse_change_url(change)
        else:
            base_url, _, _ = get_config()
            change_ref = change

        data = fetch_comments(base_url, change_ref, revision, unresolved_only)
        result = {
            "change": change_ref,
            "latest_patchset": data["latest_patchset"],
            "unresolved_only": unresolved_only,
            "comment_count": len(data["comments"]),
            "comments": data["comments"],
        }
    except GerritError as e:
        result = {
            "change": change,
            "revision": revision,
            "error": {"type": type(e).__name__, "message": str(e)},
        }
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 1

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
