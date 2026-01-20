---
name: jira-crash
description: "Fetch crash information from Jira issues, extract crash platform links from comments, download ELF/coredump/log files using playwright browser automation, and organize files for GDB debugging. Supports multiple cores (ap, cp, sensor, audio) and auto-detects latest crash from tool comments."
license: Apache-2.0
compatibility: "Requires Jira MCP server, playwright MCP server with proxy for internal network access. Optional: executor MCP for GDB sessions."
---

# jira-crash

Fetch crash information from Jira issues and download debug files from crash analysis platform using playwright browser automation.

## When to Use

- Analyze crash issues from Jira
- Download ELF, coredump, and log files from crash analysis platform
- Fetch crash files for multiple cores (ap, cp, sensor, audio)

## Prerequisites

**Required:**

- Jira MCP server - Fetch Jira issue information
- Playwright MCP server - Browser automation for crash platform access

**Playwright configuration (with proxy if needed):**

```json
"playwright": {
  "command": "npx",
  "args": ["@playwright/mcp@latest", "--proxy-server", "http://127.0.0.1:7890"]
}
```

## Workflow

### Step 1: Fetch Jira Issue Basic Information

Use `mcp_mi_jira_jira_get_issue` to get issue details:

```
issue_key: "PROJECT-XXXXX"
fields: "summary,description,status,assignee,reporter,issuetype,created,priority,labels"
comment_limit: 20
```

**Extract key information:**

- summary: Issue title
- description: Issue description containing crash report link
- status: Current status
- labels: Label information

### Step 2: Extract Crash Platform Link

**From description:**

```
Crash report link format: http://crash.example.internal/crash_report?id=XXXXXX
```

**From comments (important):**

Tools automatically comment new identical crash information to Jira. Check recent comments:

- If multiple crashes are auto-commented by tools, get the crash link from the **latest comment**
- If no tool comments exist, use crash information from the main issue description

**Identifying tool auto-comment characteristics:**

- Comment content contains `crash_report?id=` link
- Comment format is typically structured crash information

### Step 3: Access Crash Platform Using Playwright

```
mcp_playwright_browser_navigate: http://crash.example.internal/crash_report?id={crash_id}
```

**Authentication handling:**

- First access may redirect to SSO login page
- If intermediate page appears, click "Continue to access"
- Use `mcp_playwright_browser_take_screenshot` to capture QR code for user scanning with authenticator app

### Step 4: Extract Download Links

Identify available core types from page (via tab labels):

- **ap** - Application Processor (most common)
- **cp** - Communication Processor
- **sensor** - Sensor Hub
- **audio** - Audio DSP
- **tee** - Trusted Execution Environment

**URL patterns:**

```
ELF:  https://storage.example.internal/crash-logs/{crash_id}/{core}/firmware_{core}.elf
Dump: https://storage.example.internal/crash-logs/{crash_id}/{core}/*.bin
Log:  https://storage.example.internal/crash-logs/{crash_id}/{core}/full_run.log
```

### Step 5: Download Files to Local Directory

**Directory structure:**

```
./crash-{crash_id}/
├── ap/
│   ├── firmware_ap.elf
│   ├── 0-0x40000000.bin
│   └── full_run.log
├── cp/
│   ├── firmware_cp.elf
│   ├── *.bin
│   └── full_run.log
├── sensor/
│   └── ...
└── audio/
    └── ...
```

**Download commands:**

```bash
mkdir -p ./crash-{crash_id}/{core}
curl -L -o ./crash-{crash_id}/{core}/firmware_{core}.elf "{elf_url}"
curl -L -o ./crash-{crash_id}/{core}/{dump_filename} "{dump_url}"
curl -L -o ./crash-{crash_id}/{core}/full_run.log "{log_url}"
```

## Output

After successful execution:

- Downloaded file paths
- Crash basic information (product, branch, crash type)
- Command hints for GDB analysis

If any download fails: **STOP and ask user** - do not proceed
Never use existing local files or files from other directories

## Examples

### Example 1: Standard Jira Crash Analysis

**User request:**

```
Analyze crash issue PROJECT-12345
```

**Execution flow:**

1. Get Jira issue:

```
mcp_mi_jira_jira_get_issue(issue_key="PROJECT-12345", fields="summary,description,status", comment_limit=20)
```

1. Extract crash_id from description or latest comment: `303533`

2. Access crash platform:

```
mcp_playwright_browser_navigate(url="http://crash.example.internal/crash_report?id=303533")
```

1. Get page snapshot to extract download links:

```
mcp_playwright_browser_snapshot()
```

1. Download AP core files:

```bash
mkdir -p ./crash-303533/ap
curl -L -o ./crash-303533/ap/firmware_ap.elf "https://storage.example.internal/crash-logs/303533/ap/firmware_ap.elf"
curl -L -o ./crash-303533/ap/0-0x40000000.bin "https://storage.example.internal/crash-logs/303533/ap/0-0x40000000.bin"
curl -L -o ./crash-303533/ap/full_run.log "https://storage.example.internal/crash-logs/303533/ap/full_run.log"
```

### Example 2: Multi-Core Crash

**Scenario:** Jira comments contain multiple crashes, need to download files for multiple cores

**Execution:**

```bash
# Download all available cores
for core in ap cp sensor audio; do
  mkdir -p ./crash-{crash_id}/$core
  curl -L -f -o ./crash-{crash_id}/$core/firmware_$core.elf \
    "https://storage.example.internal/crash-logs/{crash_id}/$core/firmware_$core.elf" || true
done
```

### Example 3: Get Latest Crash from Tool Auto-Comments

**Scenario:** Jira has multiple tool auto-commented crashes

**Processing logic:**

1. Get recent 20 comments
2. Filter comments containing `crash_report?id=`
3. Take crash_id from the latest matching comment
4. Download files for that crash

## Error Handling

### Login Issues

If redirected to SSO login page:

1. Screenshot to display QR code
2. User scans with authenticator app
3. Continue after successful login

### File Not Found

Some cores may not have crash files, use `curl -f` to ignore 404 errors:

```bash
curl -L -f -o file.elf "url" || echo "File not found, skipping"
```

### Incomplete Coredump

Page may show "coredump incomplete, requires manual analysis":

- Still download available dump files
- Analyze with `full_run.log`

## Integration

After download, use `crash-analysis` skill or `gdb-start` skill for debugging:

```bash
# Start GDB
gdb-multiarch ./crash-{crash_id}/ap/firmware_ap.elf

# Import nxgdb
(gdb) py import nxgdb

# Load dump
(gdb) target nxstub --rawfile ./crash-{crash_id}/ap/0-0x40000000.bin:0x40000000
```

## URL Patterns

| Resource Type | URL Pattern |
|---------------|-------------|
| Crash Report Page | `http://crash.example.internal/crash_report?id={crash_id}` |
| ELF File | `https://storage.example.internal/crash-logs/{crash_id}/{core}/firmware_{core}.elf` |
| Coredump | `https://storage.example.internal/crash-logs/{crash_id}/{core}/*.bin` |
| Run Log | `https://storage.example.internal/crash-logs/{crash_id}/{core}/full_run.log` |

## Notes

- Generally prioritize analyzing **ap** core crash data
- Dump filename format `{offset}-{base_address}.bin`, e.g., `0-0x40000000.bin` means base address `0x40000000`
- If multiple crashes are auto-commented to Jira by tools, default to getting the latest one
