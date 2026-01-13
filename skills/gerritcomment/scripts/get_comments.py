#!/usr/bin/env python3
"""Fetch Gerrit review comments for a change.

Self-contained, no external dependencies except python-gerrit-api.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
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
        missing_str = ", ".join(missing)
        raise GerritError(f"Missing environment variables: {missing_str}")

    return base_url, username, password


def fetch_comments(base_url: str, change_ref: str, revision: str | None = None,
                   unresolved_only: bool = True) -> dict:
    """Fetch comments from Gerrit API.

    Args:
        base_url: Gerrit server base URL.
        change_ref: Change number or Change-Id.
        revision: Optional revision (SHA, patch set number, or 'current').
        unresolved_only: If True, only return unresolved threads.

    Returns:
        Dict with 'threads' list and 'latest_patchset' number.
    """
    _, username, password = get_config()
    client = GerritClient(
        base_url=base_url,
        username=username,
        password=password,
    )

    try:
        change = client.changes.get(change_ref)
        # Get latest patchset number via direct API call with CURRENT_REVISION
        change_data = client.get(f"/changes/{change_ref}?o=CURRENT_REVISION")
        current_rev_sha = change_data.get("current_revision")
        revisions = change_data.get("revisions", {})
        if current_rev_sha:
            latest_patchset = revisions.get(current_rev_sha, {}).get("_number")
        else:
            latest_patchset = None
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

    def _parse_updated(value: str | None) -> datetime:
        # Gerrit typically returns: "2013-02-26 15:40:43.986000000"
        if not value:
            return datetime.min
        v = value.strip()
        # Drop nanoseconds to microseconds for Python
        if "." in v:
            head, frac = v.split(".", 1)
            frac = "".join(ch for ch in frac if ch.isdigit())
            frac = (frac + "000000")[:6]
            v = f"{head}.{frac}"
            try:
                return datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                return datetime.min
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.min

    def _location_key(path: str, c: dict) -> tuple:
        # Thread location is defined by file + (range|line|file-level)
        rng = c.get("range")
        if rng:
            return (
                path or "",
                "range",
                rng.get("start_line"),
                rng.get("start_character"),
                rng.get("end_line"),
                rng.get("end_character"),
            )
        line = c.get("line")
        if line is not None:
            return (path or "", "line", int(line))
        return (path or "", "file")

    # Build index of all comments by id and group by location
    by_id: dict[str, dict] = {}
    by_location: dict[tuple, list[dict]] = defaultdict(list)
    for path, items in raw.items():
        for c in items:
            cid = c.get("id")
            if cid:
                by_id[cid] = c
            by_location[_location_key(path, c)].append(c)

    threads: list[dict] = []
    for loc_key, items in by_location.items():
        # Group into threads by root comment id (walk in_reply_to chain)
        threads_by_root: dict[str, list[dict]] = defaultdict(list)
        for c in items:
            cid = c.get("id")
            if not cid:
                continue
            root = cid
            seen: set[str] = set()
            cur = c
            while True:
                in_reply_to = cur.get("in_reply_to")
                if not in_reply_to:
                    break
                if in_reply_to in seen:
                    break
                seen.add(in_reply_to)
                parent = by_id.get(in_reply_to)
                if not parent:
                    # Orphan reply; treat itself as root
                    break
                root = in_reply_to
                cur = parent
            threads_by_root[root].append(c)

        for root_id, t_items in threads_by_root.items():
            # Sort comments in thread by updated time (chronological)
            t_items_sorted = sorted(
                t_items,
                key=lambda x: _parse_updated(x.get("updated")),
            )
            last = t_items_sorted[-1] if t_items_sorted else None
            thread_unresolved = bool(last.get("unresolved")) if last else False

            if unresolved_only and not thread_unresolved:
                continue

            # Use root comment for location metadata
            root_comment = by_id.get(root_id) or (
                t_items_sorted[0] if t_items_sorted else {}
            )
            file_path = loc_key[0] or None
            thread_range = root_comment.get("range")
            thread_line = root_comment.get("line")

            comments_out = []
            for c in t_items_sorted:
                author_info = c.get("author", {})
                author_name = (
                    author_info.get("display_name")
                    or author_info.get("name")
                    or "Unknown"
                )
                comments_out.append(
                    {
                        "id": c.get("id"),
                        "in_reply_to": c.get("in_reply_to"),
                        "patch_set": c.get("patch_set"),
                        "author": author_name,
                        "message": (c.get("message") or "").strip(),
                        "updated": c.get("updated"),
                        "unresolved": bool(c.get("unresolved")),
                    }
                )

            threads.append(
                {
                    "file": file_path,
                    "range": thread_range,
                    "line": thread_line,
                    "unresolved": thread_unresolved,
                    "updated": last.get("updated") if last else None,
                    "comments": comments_out,
                }
            )

    # Sort threads by latest comment time (newest first)
    threads.sort(key=lambda t: _parse_updated(t.get("updated")), reverse=True)
    return {"threads": threads, "latest_patchset": latest_patchset}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch Gerrit review comment threads as JSON"
    )
    parser.add_argument(
        "--change",
        required=True,
        help="Change URL, number, or Change-Id",
    )
    parser.add_argument(
        "--revision",
        help="Revision (SHA, patch set number, or 'current')",
    )
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
            "thread_count": len(data["threads"]),
            "threads": data["threads"],
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
