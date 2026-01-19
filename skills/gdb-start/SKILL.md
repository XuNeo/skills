---
name: gdb-start
description: "Start GDB for Vela/NuttX crash dump analysis or live debugging. Supports coredump (*.core), crashlog (*.log), and memory dump (*.bin) files. Uses tmux for GDB process management and nxgdbmcp for AI-controlled debugging via gdbrpc socket."
license: Apache-2.0
compatibility: "Requires: tmux skill (preferred) or executor skill (fallback), gdbmcp MCP server. GDB variants: gdb-multiarch, xtensa-esp32s3-elf-gdb, tricore-gdb, or gdb."
metadata:
  category: debugging
  platform: vela,nuttx,embedded
---

# gdb

Start GDB session for Vela/NuttX crash dump analysis or live debugging.

## Architecture

```
tmux ──▶ GDB ──▶ gdbrpc ──▶ nxgdbmcp (AI control)
```

- **Step 1-2 use tmux**: Start GDB, load nxgdb, start gdbrpc
- **Step 3+ use nxgdbmcp**: All subsequent commands via nxgdbmcp

## GDB Variant Selection

| Architecture | GDB Command |
|--------------|-------------|
| Xtensa (ESP32-S3) | `xtensa-esp32s3-elf-gdb` |
| Tricore | `tricore-gdb` |
| Host (x86/x64) | `gdb` |
| Other | `gdb-multiarch` |

## Standard Workflow

### Step 1-2: tmux - Start GDB and gdbrpc

```bash
SESSION="gdb-debug"
tmux new -d -s "$SESSION"
tmux send-keys -t "$SESSION" -- 'gdb-multiarch --quiet ./vela_ap.elf' Enter
tmux send-keys -t "$SESSION" -- 'py import gdbrpc' Enter
tmux send-keys -t "$SESSION" -- 'gdbrpc start' Enter
tmux capture-pane -p -J -t "$SESSION" -S -20  # Get port number
```

If `py import gdbrpc` fails, install it:
```bash
/usr/bin/python3 -m pip install -U gdbrpc
```

If tmux unavailable, refer to **executor skill**.

---

**From Step 3 onwards, all commands via nxgdbmcp.**

---

### Step 3: nxgdbmcp Connect

```python
session = mcp_gdbmcp_gdb_connect(port=20819)
sid = session["session_id"]
```

### Step 4: Load nxgdb Extensions

```python
# Load nxgdb (choose one)
mcp_gdbmcp_gdb_command(session_id=sid, command="py import nxgdb")
# or: mcp_gdbmcp_gdb_command(session_id=sid, command="source nuttx/tools/pynuttx/gdbinit.py")

# List available extension commands
mcp_gdbmcp_gdb_command(session_id=sid, command="help user-defined")
```

### Step 5: target nxstub - Load Dump

`target nxstub` loads various dump types with auto-detection.

**Supported dump types (ALL are valid dumps):**
| Type | File Patterns | Description |
|------|---------------|-------------|
| coredump | `*.core`, `core.*` | ELF core dump |
| crashlog | `*.log` | Text crash log with register info |
| memory dump | `*.bin`, `0x*.bin`, directory with .bin files | Raw memory binary dump |

**IMPORTANT**: `.bin` files are memory dumps, not just binary files. When you see `.bin` files in a crash directory, they ARE dump files that can be loaded.

**Special case - SIM platform:**

For NuttX SIM (simulator) platform, crash context is not in memory dump. Use GDB's native coredump loading:

```python
# SIM platform: Load coredump directly with GDB (not nxstub)
mcp_gdbmcp_gdb_command(session_id=sid, command="core-file ./core.dump")

# Standard GDB commands work for crash analysis
mcp_gdbmcp_gdb_command(session_id=sid, command="info threads")
mcp_gdbmcp_gdb_command(session_id=sid, command="bt")

# Only use nxstub when you need NuttX-specific thread state
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./core.dump")
```

**Auto-detection (recommended):**
```python
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./core.dump")
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./crash.log")
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./dump.bin")
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./0x40000000.bin")
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./memorydump/")
```

**Explicit parameters:**
```python
# coredump
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub -c core.dump")
# crashlog
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub -l crash.log")
# memory dump (with base address)
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub -r dump.bin:0x40000000")
# multiple memory dumps
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub -r ram1.bin:0x40000000 ram2.bin:0x80000000")
```

**target nxstub parameters:**
```
-a, --arch      Architecture (arm, arm-a, arm64, riscv, x86-64, esp32s3, xtensa), auto-detected
-e, --elffile   ELF file (not needed if already loaded)
-c, --core      Coredump file
-l, --log       Crashlog file
-r, --rawfile   Memory dump, format: file.bin:address
--remap         Memory remap, format: from,to,length
```

### Step 6: Analyze System State

```python
bt = mcp_gdbmcp_gdb_backtrace(session_id=sid, full=True)
threads = mcp_gdbmcp_gdb_thread_list(session_id=sid)
mcp_gdbmcp_gdb_command(session_id=sid, command="ps")
mcp_gdbmcp_gdb_command(session_id=sid, command="free")
```

After overview, use **crash-analysis skill** for deep analysis.

## Examples

### Crash Dump Analysis

```bash
# === tmux: Start GDB and gdbrpc ===
SESSION="crash-analysis"
tmux new -d -s "$SESSION"
tmux send-keys -t "$SESSION" -- 'gdb-multiarch --quiet ./crash/vela_ap.elf' Enter
tmux send-keys -t "$SESSION" -- 'py import gdbrpc' Enter
tmux send-keys -t "$SESSION" -- 'gdbrpc start' Enter
```

```python
# === nxgdbmcp: All subsequent operations ===
session = mcp_gdbmcp_gdb_connect(port=20819)
sid = session["session_id"]

mcp_gdbmcp_gdb_command(session_id=sid, command="py import nxgdb")
mcp_gdbmcp_gdb_command(session_id=sid, command="help user-defined")
mcp_gdbmcp_gdb_command(session_id=sid, command="target nxstub ./crash/core.dump")

bt = mcp_gdbmcp_gdb_backtrace(session_id=sid, full=True)
threads = mcp_gdbmcp_gdb_thread_list(session_id=sid)
```

### Live Debugging

```bash
# === tmux ===
SESSION="live-debug"
tmux new -d -s "$SESSION"
tmux send-keys -t "$SESSION" -- 'arm-none-eabi-gdb --quiet ./firmware.elf' Enter
tmux send-keys -t "$SESSION" -- 'py import gdbrpc' Enter
tmux send-keys -t "$SESSION" -- 'gdbrpc start' Enter
```

```python
# === nxgdbmcp ===
session = mcp_gdbmcp_gdb_connect(port=20819)
sid = session["session_id"]

mcp_gdbmcp_gdb_command(session_id=sid, command="target remote localhost:3333")
mcp_gdbmcp_gdb_set_breakpoint(session_id=sid, location="main")
mcp_gdbmcp_gdb_continue(session_id=sid)
```

## User Monitoring

```
tmux attach -t gdb-debug
tmux capture-pane -p -J -t gdb-debug -S -200
```

## Cleanup

```python
mcp_gdbmcp_gdb_terminate(session_id=sid)
```
```bash
tmux kill-session -t "$SESSION"
```

## Related Skills

- **tmux / executor**: GDB process startup
- **jira-fetch**: Get crash files
- **crash-analysis**: Deep analysis

## Notes

1. **tmux only for startup**, then use nxgdbmcp for commands
2. **Dump file recognition**: `.core`, `.log`, AND `.bin` are ALL valid dump files
3. **Code-tool match**: dev code should not use trunk tools
4. **GDB version**: 11+ recommended, use prebuilt gdb-multiarch
5. **List extensions**: `help user-defined`
