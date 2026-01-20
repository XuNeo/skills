---
name: git-commit
description: "Commit changes with optimized message generation and optional project-specific format checks. Supports NuttX repositories with checkpatch.sh validation and automatic sign-off. Use when committing code changes, generating commit messages from diffs, or ensuring code format compliance before commits."
license: Apache-2.0
compatibility: "Requires git. Optional: NuttX tools/checkpatch.sh for format validation."
---

# git-commit

Commit changes with automatic code format checking (for supported projects) and optimized commit message generation.

## Parameters

- **JIRA number** (optional): Issue number (e.g., `123` or `PROJECT-123`)
- **Reference message** (optional): Draft commit message to optimize based on code changes

## Workflow

### Step 1: Check Git Status and Git Log

```bash
git status
```

If no changes are staged or modified, inform user and stop.
Check previous commit format and learn if a pattern exists.

### Step 2: Detect Project Type

```bash
if [ -f "tools/checkpatch.sh" ]; then
    echo "NuttX repository detected"
else
    echo "Standard git repository"
fi
```

### Step 3: Get Code Changes

```bash
git diff HEAD
```

### Step 4: Run Format Check (NuttX Only)

**NuttX repositories only:**

```bash
git diff HEAD | tools/checkpatch.sh -
```

- If errors/warnings reported, display them clearly
- Ask user confirmation before proceeding
- Skip this step for non-NuttX repositories

### Step 5: Generate Commit Message

**NuttX format (with JIRA):**

```
<component>: <brief summary under 72 chars>

PROJECT-{JIRA_NUMBER}

<detailed description>
- Analysis of code changes
- Why the change is needed
- What problem it solves
```

**Standard format:**

```
<brief summary>

<detailed description based on diff>
```

**Guidelines:**

- Use present tense ("Fix bug" not "Fixed bug")
- Wrap lines at 72 characters
- Identify affected component from file paths

### Step 6: Create Commit

**NuttX (with sign-off):**

```bash
git commit -s -m "$(cat <<'EOF'
<generated commit message>
EOF
)"
```

**Standard:**

```bash
git commit -m "$(cat <<'EOF'
<generated commit message>
EOF
)"
```

## Error Handling

| Error | Action |
|-------|--------|
| No changes | Inform user and exit |
| Format check failures | Display errors, require user confirmation |
| Commit failures | Display error and suggest corrections |

## Examples

### NuttX Repository

```bash
# With JIRA number only
/git-commit 123

# With JIRA and reference message
/git-commit PROJECT-456 "fix serial driver bug"

# Full example
/git-commit 789 "update UART configuration for higher baud rates"
```

### Standard Repository

```bash
# Auto-generate from diff
/git-commit

# With reference message
/git-commit "fix memory leak in parser"
```

## Notes

- Works in current directory only
- NuttX: Uses `tools/checkpatch.sh` for format validation
- NuttX: `-s` flag adds `Signed-off-by` line from git config
- Standard repos: No sign-off added
