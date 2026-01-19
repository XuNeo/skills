---
name: crash-analysis
description: "Systematic NuttX/Vela crash analysis using GDB. Locates crash threads, examines call stacks, inspects memory, and identifies root causes. Requires gdb-start skill for GDB session setup. Use after loading coredump to understand why a program crashed."
license: Apache-2.0
compatibility: "Requires: gdb-start skill (for GDB session via nxgdbmcp), nxgdb extension. Read-only analysis - never executes target code."
---

# crash-analysis

Systematic crash analysis using GDB to identify root causes. This skill focuses on analysis methodology - use **gdb-start skill** for all GDB session setup and command execution.

## Prerequisites

- Active GDB session with loaded coredump (setup via **gdb-start skill**)
- nxgdb extension loaded
- ELF file with debug symbols

## Safety Principles

**Read-only analysis only - never execute target code:**

- ❌ Never: `continue`, `step`, `next`, `finish`, `until`
- ❌ Never: `call foo()`, `p get_result()` (function calls)
- ❌ Never: Write to memory or modify variables
- ✅ Allowed: Read-only inspection and static analysis

## Workflow

### Step 1: Setup GDB Session (via gdb-start skill)

Refer to **gdb-start skill** for complete setup:

```python
# 1. Start GDB in tmux and launch gdbrpc
# 2. Connect via nxgdbmcp
session = mcp_gdbmcp_gdb_connect(port=20819)
sid = session["session_id"]

# 3. Load nxgdb extension
mcp_gdbmcp_gdb_command(session_id=sid, command="py import nxgdb")

# 4. IMPORTANT: Get available extension commands
mcp_gdbmcp_gdb_command(session_id=sid, command="help user-defined")

# 5. Load dump file
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./crash/core.dump")
```

**Special case - SIM platform:**

For NuttX SIM (simulator) platform, crash context is not in memory dump. Use GDB's native coredump loading instead:

```python
# SIM platform: Load coredump directly with GDB (not nxstub)
mcp_gdbmcp_gdb_command(session_id=sid, command="core-file ./core.dump")

# Standard GDB commands work for crash analysis
mcp_gdbmcp_gdb_command(session_id=sid, command="info threads")
mcp_gdbmcp_gdb_command(session_id=sid, command="bt")

# Only use nxstub when you need NuttX-specific thread state
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./core.dump")
```

### Step 2: Initial Crash Assessment

**Get thread overview:**
```python
# List all threads - identify crashing thread
mcp_gdbmcp_gdb_command(session_id=sid, command="info threads")
```

**IMPORTANT - Thread ID vs PID:**
```
  Id   Target Id                  Frame
* 1    Thread 1 (Idle_Task)       0x... in up_idle ()
  2    Thread 2 (hpwork)          0x... in nxsem_wait ()
  125  Thread 473 (vappxms)       0x... in __assert ()
```
- **First column (Id)**: GDB thread ID - use this with `thread` command
- **Thread N**: NuttX PID (e.g., Thread 473) - NOT for `thread` command

**Common mistake:** Using PID instead of GDB ID
- ❌ Wrong: `thread 473` (this is the NuttX PID)
- ✅ Correct: `thread 125` (this is the GDB thread ID)

**Examine crash context:**
```python
# Get backtrace of current (likely crashing) thread
bt = mcp_gdbmcp_gdb_backtrace(session_id=sid, full=True)

# Check crash type from top frame:
# - segfault, assertion, panic, etc.
```

**Check register state:**
```python
mcp_gdbmcp_gdb_command(session_id=sid, command="info registers")
# Look for: null pointers, corrupted addresses, invalid PC/SP
```

### Step 3: Root Cause Investigation

**For each suspicious thread:**

```python
# Switch to thread (use ID from first column of info threads)
mcp_gdbmcp_gdb_thread_select(session_id=sid, thread_id=125)

# Get backtrace
bt = mcp_gdbmcp_gdb_backtrace(session_id=sid, full=True)

# For each frame of interest:
mcp_gdbmcp_gdb_command(session_id=sid, command="frame 0")
mcp_gdbmcp_gdb_command(session_id=sid, command="info args")
mcp_gdbmcp_gdb_command(session_id=sid, command="info locals")

# Examine structures and pointers
mcp_gdbmcp_gdb_print(session_id=sid, expression="*ptr")
```

**Source code navigation:**
```python
# Get source file path
mcp_gdbmcp_gdb_command(session_id=sid, command="info source")

# Path mapping: nuttx/apps code may have different root paths
# Look for nuttx/ or apps/ in paths, map to current workspace
```

### Step 4: Memory Issue Analysis

**Memory corruption detection:**
```python
# Check heap corruption
mcp_gdbmcp_gdb_command(session_id=sid, command="mm check")

# Memory validation
mcp_gdbmcp_gdb_command(session_id=sid, command="memrange")
```

**Out of Memory (OOM) analysis:**
```python
# Check memory state
mcp_gdbmcp_gdb_command(session_id=sid, command="free")

# Check fragmentation
mcp_gdbmcp_gdb_command(session_id=sid, command="mm frag")

# Top memory consumers (limit output!)
mcp_gdbmcp_gdb_command(session_id=sid, command="memdump --top 20 --no-backtrace")
```

**Memory leak investigation:**
```python
# Check for obvious leaks
mcp_gdbmcp_gdb_command(session_id=sid, command="memleak")

# Exclude memory pools: --no-pid -1
mcp_gdbmcp_gdb_command(session_id=sid, command="memdump --top 20 --no-backtrace --no-pid -1")
```

### Step 5: Advanced Techniques

**Register context recovery (when backtrace is corrupted):**

Use `setregs` to restore saved register context:

```python
# Common saved context locations:
# 1. CPU crash registers: g_last_regs[<cpu_id>]
# 2. Thread context: tcb->xcp.regs
# 3. Exception frames: regs parameter in IRQ handlers

mcp_gdbmcp_gdb_command(session_id=sid, command="setregs <address>")

# Fallback if standard fails:
mcp_gdbmcp_gdb_command(session_id=sid, command="monitor setregs <address>")
mcp_gdbmcp_gdb_command(session_id=sid, command="maint flush register-cache")
```

**NuttX-specific commands:**
```python
# Process list
mcp_gdbmcp_gdb_command(session_id=sid, command="ps")

# System messages
mcp_gdbmcp_gdb_command(session_id=sid, command="dmesg")
```

**Note:** Prefer standard GDB commands (`info threads`, `thread N`, `bt`) for thread inspection. Only use NuttX-specific commands (`info nxthread`, `nxthread`) when standard commands fail or when specifically requested by user.

## Common Crash Patterns

| Pattern | Symptoms | Investigation Focus |
|---------|----------|---------------------|
| Null pointer | Segfault at low address | Check pointer initialization, error handling |
| Use-after-free | Segfault on valid-looking address | Check object lifecycle, freed memory access |
| Stack overflow | Crash in deep recursion | Check stack size, recursion depth |
| Heap corruption | Random crashes, corrupted metadata | Check buffer writes, memory boundaries |
| Assertion | Clear assertion message | Validate assertion condition, check preconditions |
| Deadlock | Hung threads, waiting locks | Check lock ordering, resource dependencies |
| KASAN error | kasan/hook.c in backtrace | Memory access violation - check allocation history |

## Analysis Best Practices

1. **Be methodical**: Follow the workflow systematically
2. **Dig deeper**: Don't stop at surface symptoms
3. **Read code**: Source context is essential for understanding
4. **Connect dots**: Link observations across threads/frames
5. **Think critically**: Question assumptions, verify hypotheses
6. **Be efficient**: Use targeted commands, avoid excessive output
7. **Limit output**: Always use `--top N` for memdump commands

## Output Format

Present analysis conclusions concisely:
- **What happened**: Crash type
- **Where**: Code location (file:line)
- **Why**: Root cause
- **How to fix**: Recommendations

Do NOT dump raw command outputs unless specifically relevant.

## Example: Complete Analysis

```python
# === Setup (via gdb-start skill) ===
session = mcp_gdbmcp_gdb_connect(port=20819)
sid = session["session_id"]
mcp_gdbmcp_gdb_command(session_id=sid, command="py import nxgdb")
mcp_gdbmcp_gdb_command(session_id=sid, command="help user-defined")
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./crash/core.dump")

# === Phase 1: Initial Assessment ===
mcp_gdbmcp_gdb_command(session_id=sid, command="info threads")
bt = mcp_gdbmcp_gdb_backtrace(session_id=sid, full=True)
mcp_gdbmcp_gdb_command(session_id=sid, command="info registers")

# === Phase 2: Root Cause ===
# Identify crash thread from backtrace (e.g., thread 125)
mcp_gdbmcp_gdb_thread_select(session_id=sid, thread_id=125)
mcp_gdbmcp_gdb_command(session_id=sid, command="frame 0")
mcp_gdbmcp_gdb_command(session_id=sid, command="info args")
mcp_gdbmcp_gdb_command(session_id=sid, command="info locals")

# === Phase 3: Memory Analysis (if needed) ===
mcp_gdbmcp_gdb_command(session_id=sid, command="mm check")
mcp_gdbmcp_gdb_command(session_id=sid, command="memdump --top 20 --no-backtrace")

# === Conclusion ===
# Crash Type: KASAN memory access error
# Location: kasan/hook.c:207
# Root Cause: Use-after-free in LVGL event handler
# Fix: Add null check before object access
```

## Fallback Strategies

If standard analysis yields no clear results:

1. **Expand scope**: Check other threads for related issues
2. **Review logs**: Examine system logs for warnings/errors
3. **Check resources**: Verify file descriptors, sockets, semaphores
4. **Timing issues**: Look for race conditions or deadlock patterns
5. **Register recovery**: Use `setregs` if backtrace is corrupted

## Related Skills

- **gdb-start**: GDB session setup and command execution (REQUIRED)
- **jira-analysis**: Fetch crash files from Jira
- **tmux**: GDB process management
