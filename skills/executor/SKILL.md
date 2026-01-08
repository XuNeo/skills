---
name: executor
description: Manage persistent interactive CLI processes (REPLs, database CLIs, debuggers, shells). Use for tools with prompts that maintain state across multiple commands (python -i, psql, gdb, node). Provides executor_start, executor_send, executor_read_output, executor_stop. NOT for one-off commands - use Bash for those.
---

# Executor

Manage persistent interactive CLI processes with stateful stdin/stdout communication.

**Use executor when:** Process has a prompt and maintains state (REPL, database CLI, debugger)
**Use Bash when:** One-off command that completes immediately

## Workflow

**Pattern:** Start → Send* → Stop

### 1. executor_start
```json
{"command": "python3", "args": ["-i"], "working_dir": "/path"}
```
Returns `process_id` for subsequent calls.

### 2. executor_send
```json
{"process_id": "abc123", "text": "x = 42"}
```
**By default, waits 0.1s and returns output directly** (last 20 lines, both stdout and stderr).

Optional parameters:
- `wait_time: 0` - Don't wait, return "Success" immediately
- `wait_time: 0.5` - Custom wait time in seconds
- `tail_lines: 50` - Return more lines (default: 20)
- `add_newline: true` - Append newline (default: true)

Returns plain text output or "Success" (if wait_time=0).

### 3. executor_read_output (optional)
```json
{"process_id": "abc123", "tail_lines": 10}
```
Only needed if you set `wait_time=0` in executor_send.
- Returns both stdout and stderr
- Buffers last 1000 lines per stream

### 4. executor_stop
```json
{"process_id": "abc123", "force": false}
```
- `force: false` = SIGTERM (graceful), `force: true` = SIGKILL

## Examples

### Python REPL (Streamlined)
```python
executor_start(command="python3", args=["-i"])
# Wait 0.3s for Python startup banner
output = executor_send(text="x = 42", wait_time=0.3)  # Returns output directly
output = executor_send(text="print(x * 2)")  # Returns "84\n>>>"
executor_stop()
```

### Database CLI
```python
executor_start(command="psql", args=["dbname"])
# Check connection (wait 0.5s for connection message)
output = executor_send(text="SELECT * FROM users LIMIT 5;", wait_time=0.5)
# Output contains query results
executor_send(text="\\q", wait_time=0)  # Exit without waiting
```

### Debugger (gdb)
```python
executor_start(command="gdb", args=["./binary"])
output = executor_send(text="break main", wait_time=0.2)  # Returns breakpoint confirmation
output = executor_send(text="run")  # Returns execution output
```

### Fast Commands (No Wait)
```python
# When you don't need immediate output
executor_start(command="python3", args=["-i"])
executor_send(text="import sys", wait_time=0)  # Returns "Success"
executor_send(text="import os", wait_time=0)   # Returns "Success"
# Read all output at once
output = executor_read_output(tail_lines=50)
```

## Best Practices

- **Use default wait_time** - `executor_send` now returns output automatically (0.1s default)
- **Set wait_time=0 for fast batches** - When queuing commands without needing immediate output
- **Adjust wait_time as needed** - Slower processes may need 0.3-0.5s
- **Check output for errors** - Response contains both stdout and stderr, look for error patterns
- **Always stop processes** - Use `executor_list` to audit running processes

## Additional Tools

- `executor_list` - List all active processes
- `executor_get_info` - Get detailed process state (buffered lines, PID, log file)

## Logging

All I/O logged to `.executorlog/{process_id}_{timestamp}_{command}.log` for debugging.
