---
name: gerrit-comment
description: Fetch published Gerrit review comments (as JSON) for a given change URL, change number, or Change-Id. Use when you need real review feedback for code fixes.
---

## Usage

```bash
python3 scripts/get_comments.py --change "<change>" [--revision "<revision>"]
```

- `--change`: Full URL (e.g., `https://gerrit.example.com/c/repo/+/12345`), change number, or Change-Id
- `--revision`: Optional. SHA, patch set number, or `current`

If user want to fetch the code, use `git fetch {REMOTE} refs/changes/{XX}/{CHANGE_NUMBER}/{PATCH_SET_NUMBER}` to fetch the desired patch set.

- XX is the last two digits of the change number. For example, for change number 12345, XX would be 45.
- CHANGE_NUMBER is the full change number (e.g., 12345).
- PATCH_SET_NUMBER is the specific patch set number you want to fetch, normally use the latest patch set number.

## Environment

| Variable | Required |
|----------|----------|
| `GERRIT_USER` | Yes |
| `GERRIT_HTTP_PASSWORD` | Yes |
| `GERRIT_BASE_URL` | Only when using change number/ID |

## Output

Success:

```json
{"base_url": "...", "change": "12345", "revision": null, "comments": [...]}
```

Error:

```json
{"change": "12345", "revision": null, "error": {"type": "...", "message": "..."}}
```

## Dependency

`pip3 install python-gerrit-api`
