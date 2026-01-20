# NuttX GDB Extension Commands Reference

Custom GDB commands implemented in `nuttx/tools/pynuttx`.

## Loading

```gdb
(gdb) py import nxgdb
# or
(gdb) source nuttx/tools/pynuttx/gdbinit.py
```

## List Commands

```gdb
(gdb) help user-defined  # All commands
(gdb) xxx --help         # Specific command help
```

## Command Categories

### Sched

| Command | Function |
|---------|----------|
| `info nxthread` | NuttX thread info |
| `setregs` | Set registers, switch thread context |
| `deadlock` | Deadlock detection |
| `ps` | Process status |
| `crash thread` | Find crash thread |
| `crash busyloop` | Detect busy loop |

### Memory

| Command | Function |
|---------|----------|
| `memdump` | Dump memory nodes |
| `memleak` | Memory leak detection |
| `memcheck` | Memory integrity check |
| `memfind` | Find memory pattern |
| `mm range` | Memory regions |
| `crash stackoverflow` | Stack overflow detection |

### System

| Command | Function |
|---------|----------|
| `free` | Memory info |
| `uname` | Firmware version |
| `dmesg` | Ramlog |
| `diagnose` | Diagnostic report |
| `target nxstub` | Load dump files |
| `gdbrpc` | Socket remote control |

## Notes

1. GDB version 11+
2. Recommend `prebuilts/gcc/linux/gdb-multiarch/bin/gdb-multiarch`
3. Code and tools must match
