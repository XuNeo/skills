---
description: Commit changes with optimized message and optional project-specific format checks
argument-hint: "[JIRA-number] [optional commit reference]"
allowed-tools: Bash(git:*), Bash(cd:*), Bash(tools/checkpatch.sh:*), Read, Grep
---

# Git Commit with Format Check

Commit changes with automatic code format checking (for supported projects) and optimized commit message generation.

## Parameters

- **$1** (optional): JIRA issue number or commit reference (e.g., `123`, `VELAPLATFO-123`, or a commit message draft)
- **$2** (optional): Additional commit message reference/draft - will be optimized based on code changes

## Workflow

### Step 1: Check Git Status

Verify there are changes to commit:

```bash
git status
```

If no changes are staged or modified, inform the user and stop.

### Step 2: Detect Project Type

Check if the current directory is a NuttX repository:

```bash
if [ -f "tools/checkpatch.sh" ]; then
    echo "Detected NuttX repository"
    IS_NUTTX=true
else
    echo "Standard git repository"
    IS_NUTTX=false
fi
```

### Step 3: Get Code Changes

Retrieve the diff to understand what changes are being committed:

```bash
git diff HEAD
```

### Step 4: Run Code Format Check (NuttX Only)

**If NuttX repository detected**: Run NuttX's checkpatch.sh to verify code formatting compliance:

```bash
git diff HEAD | tools/checkpatch.sh -
```

**Important**:
- If checkpatch.sh reports errors or warnings, display them clearly to the user
- Ask the user if they want to proceed with the commit despite format issues
- Only continue to the next step if the user confirms or if there are no issues

**If not NuttX**: Skip format check and proceed to commit message generation.

### Step 5: Generate Optimized Commit Message

Analyze the code changes and generate an appropriate commit message.

**For NuttX repositories** (when JIRA number is provided):

**Format Template**:
```
<component>: <optimized brief summary>

VELAPLATFO-$1

<detailed description based on code diff and user's input reference>
```

**Guidelines**:
- **Line 1**: Identify the affected component (e.g., `drivers/serial`, `arch/arm`, `fs/vfs`) and write a concise summary (under 72 characters)
- **Line 3**: Empty line
- **Line 4**: Must be `VELAPLATFO-{JIRA_NUMBER}` where JIRA_NUMBER is extracted from $1 (if user provides `VELAPLATFO-123`, use `123`; if user provides `123`, use `123`)
- **Line 5**: Empty line
- **Lines 6+**: Detailed description combining:
  - Analysis of the code changes from the diff
  - User's input from $2 (if provided) as reference
  - Why the change is needed
  - What problem it solves
- Use present tense (e.g., "Fix bug" not "Fixed bug")
- Wrap lines at 72 characters

**For standard repositories**:

**Format Template**:
```
<optimized brief summary>

<detailed description based on code diff and user's input reference>
```

### Step 6: Create Commit

**For NuttX repositories**: Execute the commit with the `-s` flag for automatic sign-off:

```bash
git commit -s -m "<generated commit message>"
```

Use a HEREDOC for proper multi-line message formatting:

```bash
git commit -s -m "$(cat <<'EOF'
<generated commit message with proper line breaks>
EOF
)"
```

**For standard repositories**: Execute the commit without sign-off:

```bash
git commit -m "<generated commit message>"
```

Use a HEREDOC for proper multi-line message formatting:

```bash
git commit -m "$(cat <<'EOF'
<generated commit message with proper line breaks>
EOF
)"
```

## Error Handling

- **No changes**: If git status shows no changes, inform user and exit
- **Format check failures (NuttX only)**: Display all checkpatch.sh errors/warnings and require user confirmation
- **Commit failures**: Display the error and suggest corrections

## Example Usage

### NuttX Repository

```bash
# With JIRA number only (auto-generate commit message)
/git-commit 123

# With JIRA number and reference message
/git-commit VELAPLATFO-456 "fix serial driver bug"

# Full example with reference
/git-commit 789 "update UART configuration to support higher baud rates"
```

### Standard Repository

```bash
# Auto-generate commit message from diff
/git-commit

# With commit message reference
/git-commit "fix memory leak in parser"

# With detailed reference
/git-commit "update API to handle edge cases and improve error handling"
```

## Notes

- The command works in the current directory (no automatic navigation)
- For NuttX repositories, format check uses `tools/checkpatch.sh`
- For NuttX repositories, the `-s` flag automatically adds your `Signed-off-by` line based on git config
- For standard repositories, no sign-off is added
- The command automatically detects the project type and adjusts behavior accordingly
