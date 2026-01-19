# gdbrpc - GDB Remote Control

gdbrpc is a socket server started inside GDB, allowing remote control via socket.

## Overview

gdbrpc runs inside the GDB process, exposing Python API for automation. Combined with nxgdbmcp MCP server, AI can directly control GDB for debugging.

## Architecture

```
┌─────────────────────────────────────────────┐
│                  GDB Process                 │
│  ┌─────────────┐    ┌─────────────────────┐ │
│  │   nxgdb     │    │      gdbrpc         │ │
│  │ (extensions)│    │  (socket server)    │ │
│  └─────────────┘    └──────────┬──────────┘ │
└────────────────────────────────┼────────────┘
                                 │ socket
                                 ▼
                    ┌─────────────────────────┐
                    │       nxgdbmcp          │
                    │     (MCP server)        │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      AI Assistant       │
                    └─────────────────────────┘
```

## Usage

### Start gdbrpc in GDB

```gdb
(gdb) gdbrpc start              # Default port 20819
(gdb) gdbrpc start --port 12345 # Custom port
(gdb) gdbrpc stop
(gdb) gdbrpc status
```

### Connect via nxgdbmcp

```python
session = mcp_gdbmcp_gdb_connect(host="localhost", port=20819)
session_id = session["session_id"]

result = mcp_gdbmcp_gdb_command(session_id=session_id, command="info threads")
```

## Notes

1. gdbrpc must be started inside GDB before connecting
2. Get port number from `gdbrpc start` output
3. One GDB process = one gdbrpc server
4. Load nxgdb before starting gdbrpc
5. Load dump files via `target nxstub` command
