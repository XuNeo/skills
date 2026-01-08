---
name: tmux
description: "Remote control tmux sessions for interactive CLIs (python, gdb, etc.) by sending keystrokes and scraping pane output."
license: Vibecoded
---

# tmux Skill

Use tmux as a programmable terminal multiplexer for interactive work. Works on Linux and macOS with stock tmux; avoid custom config by using a private socket.

## Quickstart (use current tmux server)

```bash
SESSION=python-debug                           # descriptive names; avoid spaces
tmux new -d -s "$SESSION"
tmux send-keys -t "$SESSION".1 -- 'python3 -q' Enter
tmux capture-pane -p -J -t "$SESSION".1 -S -200  # watch output
tmux kill-session -t "$SESSION"                # clean up
```

If not running inside tmux (no `$TMUX` env var), use an isolated socket:

```bash
SOCKET_DIR=${TMPDIR:-/tmp}/claude-tmux-sockets
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/claude.sock"
SESSION=python-debug
tmux -S "$SOCKET" new -d -s "$SESSION"
tmux -S "$SOCKET" send-keys -t "$SESSION".1 -- 'python3 -q' Enter
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION".1 -S -200
tmux -S "$SOCKET" kill-session -t "$SESSION"
```

After starting a session ALWAYS tell the user how to monitor the session by giving them a command to copy paste:

```
To monitor this session yourself:
  tmux attach -t python-debug

Or to capture the output once:
  tmux capture-pane -p -J -t python-debug.1 -S -200
```

If using an isolated socket (not in tmux), include `-S "$SOCKET"`:

```
To monitor this session yourself:
  tmux -S "$SOCKET" attach -t python-debug

Or to capture the output once:
  tmux -S "$SOCKET" capture-pane -p -J -t python-debug.1 -S -200
```

This must ALWAYS be printed right after a session was started and once again at the end of the tool loop.  But the earlier you send it, the happier the user will be.

## Socket convention

- **Preferred**: When running inside tmux (check `$TMUX` env var), use the current tmux server without `-S` flag.
- **Fallback**: If not in tmux, agents MUST place tmux sockets under `CLAUDE_TMUX_SOCKET_DIR` (defaults to `${TMPDIR:-/tmp}/claude-tmux-sockets`) and use `tmux -S "$SOCKET"` so we can enumerate/clean them. Create the dir first: `mkdir -p "$CLAUDE_TMUX_SOCKET_DIR"`.
- Default socket path to use unless you must isolate further: `SOCKET="$CLAUDE_TMUX_SOCKET_DIR/claude.sock"`.

## Targeting panes and naming

- Target format: `{session}.{pane}`, defaults to `{session}.1` if omitted. Use descriptive names (e.g., `python-debug`, `gdb-session`, `build-test`).
- **Session naming convention**: Use descriptive names that indicate the tool and purpose:
  - `python-debug` - Python REPL for debugging/calculations
  - `gdb-session` - GDB debugger for C/C++/embedded debugging
  - `build-test` - Build process or test runner
  - `shell-work` - General shell session for file operations
- **Creating new panes**: `tmux split-window -h -t "$SESSION"` creates a new pane (pane 2). Always target the specific pane when sending commands: `tmux send-keys -t "$SESSION".2 -- 'command' Enter`
- Use `-S "$SOCKET"` consistently to stay on the private socket path. If you need user config, drop `-f /dev/null`; otherwise `-f /dev/null` gives a clean config.
- Inspect: `tmux -S "$SOCKET" list-sessions`, `tmux -S "$SOCKET" list-panes -a`.

## Finding sessions

- List sessions on your active socket with metadata: `./scripts/find-sessions.sh -S "$SOCKET"`; add `-q partial-name` to filter.
- Scan all sockets under the shared directory: `./scripts/find-sessions.sh --all` (uses `CLAUDE_TMUX_SOCKET_DIR` or `${TMPDIR:-/tmp}/claude-tmux-sockets`).

## Sending input safely

- **To send a command with Enter (newline)**: `tmux ... send-keys -t target -- 'your command' Enter`
  - The `--` separates command from keys, and `Enter` sends a newline (not literal text)
  - Always use single quotes around the command to prevent shell expansion and URL truncation
- **To send literal text without interpretation**: `tmux ... send-keys -t target -l -- 'literal text'`
  - Use `-l` flag to send text exactly as-is, useful for special characters
- **To send text with embedded newline**: `tmux ... send-keys -t target -l -- $'text\nwith\nnewlines'`
  - Use ANSI-C quoting with `-l` for embedded newlines
- To send control keys: `tmux ... send-keys -t target C-c`, `C-d`, `C-z`, `Escape`, etc.

## Watching output

- Capture recent history (joined lines to avoid wrapping artifacts): `tmux -L "$SOCKET" capture-pane -p -J -t target -S -200`.
- For continuous monitoring, poll with the helper script (below) instead of `tmux wait-for` (which does not watch pane output).
- You can also temporarily attach to observe: `tmux -L "$SOCKET" attach -t "$SESSION"`; detach with `Ctrl+b d`.
- When giving instructions to a user, **explicitly print a copy/paste monitor command** alongside the action don't assume they remembered the command.

## Spawning Processes

Some special rules for processes:

- when asked to debug, use lldb by default
- when starting a python interactive shell, always set the `PYTHON_BASIC_REPL=1` environment variable. This is very important as the non-basic console interferes with your send-keys.

## Synchronizing / waiting for prompts

- Use timed polling to avoid races with interactive tools. Example: wait for a Python prompt before sending code:
  ```bash
  ./scripts/wait-for-text.sh -t "$SESSION" -p '^>>>' -T 15 -l 4000
  ```
- For long-running commands, poll for completion text (`"Type quit to exit"`, `"Program exited"`, etc.) before proceeding.

## Interactive tool recipes

- **Python REPL**: `tmux ... send-keys -t "$SESSION".1 -- 'python3 -q' Enter`; wait for `^>>>`; send code with `-t "$SESSION".1 -- 'code' Enter`; interrupt with `C-c`. Always with `PYTHON_BASIC_REPL`.
- **gdb**: `tmux ... send-keys -t "$SESSION".1 -- 'gdb --quiet ./a.out' Enter`; disable paging `tmux ... send-keys -t "$SESSION".1 -- 'set pagination off' Enter`; break with `C-c`; issue `bt`, `info locals`, etc.; exit via `quit` then confirm `y`.
- **Other TTY apps** (ipdb, psql, mysql, node, bash): same pattern—start the program, poll for its prompt, then send command with `-t "$SESSION".1 -- 'command' Enter`.

## Cleanup

- Kill a session when done: `tmux -S "$SOCKET" kill-session -t "$SESSION"`.
- Kill all sessions on a socket: `tmux -S "$SOCKET" list-sessions -F '#{session_name}' | xargs -r -n1 tmux -S "$SOCKET" kill-session -t`.
- Remove everything on the private socket: `tmux -S "$SOCKET" kill-server`.

## Helper: wait-for-text.sh

`./scripts/wait-for-text.sh` polls a pane for a regex (or fixed string) with a timeout. Works on Linux/macOS with bash + tmux + grep.

```bash
./scripts/wait-for-text.sh -t session -p 'pattern' [-F] [-T 20] [-i 0.5] [-l 2000]
```

- `-t`/`--target` pane target (required, format: `{session}.{pane}`)
- `-p`/`--pattern` regex to match (required); add `-F` for fixed string
- `-T` timeout seconds (integer, default 15)
- `-i` poll interval seconds (default 0.5)
- `-l` history lines to search from the pane (integer, default 1000)
- Exits 0 on first match, 1 on timeout. On failure prints the last captured text to stderr to aid debugging.
