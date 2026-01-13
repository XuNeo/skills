---
name: vela-run
description: Run Vela RTOS targets (QEMU variants, simulator, goldfish) with automatic detection and appropriate launch commands
license: MIT
---

# Vela Run Skill

Run Vela RTOS builds on various targets including QEMU variants, simulator, and goldfish emulator.

## Target Types

Vela supports several runtime targets:

1. **QEMU ARM Cortex-M (MPS-AN547)**: ARM Cortex-M on QEMU MPS3-AN547 machine
2. **QEMU ARMv7-A**: ARM Cortex-A7 on QEMU virt machine
3. **QEMU ARM64 (AArch64)**: ARM Cortex-A53 on QEMU virt machine with SMP support
4. **Simulator**: Native host binary built with vendor/sim/ or nuttx/boards/sim
5. **Goldfish**: Android emulator using emulator.sh script

## Usage

Use this skill by mentioning it:

"Use the vela-run skill to run the qemu-armv8a build on port 1234"

"Use the vela-run skill to run the simulator"

"Use the vela-run skill to run goldfish with gdb on port 1129"

## Run Workflow

### Step 1: Detect Target Type

Analyze the build output to determine which target type to run:

```bash
# Read build output directory from vela-build
OUTDIR=$(cat .vela_build_outdir 2>/dev/null || echo "build")

# Detect target from directory name or user input
# - Check for sim, qemu, goldfish keywords
# - Ask user if unclear
```

### Step 2: Locate Binary

Find the appropriate ELF or binary file:

```bash
# Common binary names
# - nuttx (ELF file)
# - nuttx.bin (raw binary)
# - For goldfish: entire output directory

# Search in output directory
ELF="$OUTDIR/nuttx"
if [[ ! -f "$ELF" ]]; then
    echo "Binary not found in $OUTDIR"
    exit 1
fi
```

### Step 3: Run QEMU ARM Cortex-M (MPS-AN547)

```bash
qemu-system-arm -M mps3-an547 -m 2G -nographic -kernel {elf} -gdb tcp::{gdbport}
```

**Parameters:**
- `{elf}`: Path to ELF file (e.g., `build/nuttx`)
- `{gdbport}`: GDB debugging port (default: 1234)

**Example:**
```bash
qemu-system-arm -M mps3-an547 -m 2G -nographic -kernel build/nuttx -gdb tcp::1234
```

### Step 4: Run QEMU ARMv7-A

```bash
qemu-system-arm -cpu cortex-a7 -nographic -machine virt,virtualization=off,gic-version=2 -net none -chardev stdio,id=con,mux=on -serial chardev:con -mon chardev=con,mode=readline -kernel {elf} -gdb tcp::{gdbport}
```

**Parameters:**
- `{elf}`: Path to ELF file
- `{gdbport}`: GDB debugging port (default: 1234)

**Example:**
```bash
qemu-system-arm -cpu cortex-a7 -nographic -machine virt,virtualization=off,gic-version=2 -net none -chardev stdio,id=con,mux=on -serial chardev:con -mon chardev=con,mode=readline -kernel build/nuttx -gdb tcp::1234
```

### Step 5: Run QEMU ARM64 (AArch64)

```bash
qemu-system-aarch64 -smp {cpus} -cpu cortex-a53 -semihosting -nographic -machine virt,virtualization=on,gic-version=3 -net none -chardev stdio,id=con,mux=on -serial chardev:con -mon chardev=con,mode=readline -kernel {elf} -gdb tcp::{gdbport}
```

**Parameters:**
- `{cpus}`: Number of CPUs for SMP (default: 4, can be 1 if user specifies)
- `{elf}`: Path to ELF file
- `{gdbport}`: GDB debugging port (default: 1234)

**Example:**
```bash
qemu-system-aarch64 -smp 4 -cpu cortex-a53 -semihosting -nographic -machine virt,virtualization=on,gic-version=3 -net none -chardev stdio,id=con,mux=on -serial chardev:con -mon chardev=con,mode=readline -kernel build/nuttx -gdb tcp::1234
```

### Step 6: Run Simulator

The simulator is a native host binary that can be executed directly.

**IMPORTANT**: Use the executor skill to run the simulator to capture stdio:

```bash
# Using executor skill (recommended)
executor_start(command="{path_to_binary}", working_dir="{cwd}")
executor_read_output(tail_lines=50)
# ... interact with simulator ...
executor_stop()
```

**Alternative**: Run directly in background:

```bash
# Direct execution (stdio goes to terminal)
{path_to_binary}
```

**Parameters:**
- `{path_to_binary}`: Path to simulator binary (e.g., `build/nuttx`, `out/nuttx`)

**Example:**
```bash
# With executor
executor_start(command="build/nuttx", working_dir="/path/to/vela")

# Or direct
./build/nuttx
```

### Step 7: Run Goldfish

Goldfish uses the `emulator.sh` script in the project root:

```bash
./emulator.sh {build_output_path} -qemu -gdb tcp::{gdbport} [additional_qemu_args]
```

**Parameters:**
- `{build_output_path}`: Path to goldfish build output (e.g., `out/qemu_vela_goldfish-armeabi-v7a-ap`)
- `{gdbport}`: GDB debugging port (default: 1129)
- `[additional_qemu_args]`: Optional additional arguments passed to QEMU after `-qemu`

**Example:**
```bash
./emulator.sh out/qemu_vela_goldfish-armeabi-v7a-ap -qemu -gdb tcp::1129
```

## Target Detection Logic

### From Build Output Directory

```bash
OUTDIR=$(cat .vela_build_outdir 2>/dev/null || echo "build")

# Check directory name for hints
if [[ "$OUTDIR" == *"sim"* ]] || [[ "$OUTDIR" == *"simulator"* ]]; then
    TARGET_TYPE="sim"
elif [[ "$OUTDIR" == *"goldfish"* ]]; then
    TARGET_TYPE="goldfish"
elif [[ "$OUTDIR" == *"qemu"* ]]; then
    # Further detect QEMU variant from board name
    TARGET_TYPE="qemu"
else
    # Ask user
    TARGET_TYPE="unknown"
fi
```

### QEMU Variant Detection

```bash
# Check board name or config for architecture hints
# - mps3, mps-an547, cortex-m -> MPS-AN547
# - v7a, cortex-a7, armv7 -> ARMv7-A
# - v8a, armv8a, aarch64, arm64, cortex-a53 -> ARM64
```

### From User Input

Ask user to specify:
- Target type: qemu-m, qemu-v7a, qemu-arm64, sim, goldfish
- GDB port (optional, defaults provided)
- SMP count for ARM64 (optional, default 4)

## Default Parameters

- **GDB Port**:
  - QEMU: 1234
  - Goldfish: 1129
- **SMP Count (ARM64)**: 4
- **Output Directory**: Read from `.vela_build_outdir`, fallback to `build/`

## Error Handling

- **Binary not found**: Search for `nuttx` in output directory, suggest running vela-build first
- **Unknown target**: Ask user to specify target type
- **Missing emulator.sh**: Check project root, inform user if not found
- **QEMU not installed**: Check for `qemu-system-arm` and `qemu-system-aarch64`, suggest installation

## Example Usage

### QEMU ARM64 with Custom Port

```
Use the vela-run skill to run qemu-arm64 with gdb on port 5678
```

**Expected behavior:**
1. Read output directory from `.vela_build_outdir`
2. Find `nuttx` ELF in output directory
3. Run: `qemu-system-aarch64 -smp 4 ... -kernel {elf} -gdb tcp::5678`

### Simulator with Executor

```
Use the vela-run skill to run the simulator
```

**Expected behavior:**
1. Read output directory from `.vela_build_outdir`
2. Find simulator binary (e.g., `build/nuttx`)
3. Use executor skill to run binary and capture stdio
4. Display output to user

### Goldfish with Default Port

```
Use the vela-run skill to run goldfish
```

**Expected behavior:**
1. Read output directory from `.vela_build_outdir`
2. Detect goldfish build path (e.g., `out/qemu_vela_goldfish-armeabi-v7a-ap`)
3. Run: `./emulator.sh {path} -qemu -gdb tcp::1129`

### QEMU ARMv7-A with SMP 1

```
Use the vela-run skill to run qemu-v7a on port 1234
```

**Expected behavior:**
1. Read output directory
2. Find ELF file
3. Run: `qemu-system-arm -cpu cortex-a7 ... -kernel {elf} -gdb tcp::1234`

## Integration with Other Skills

### vela-build Integration

This skill reads `.vela_build_outdir` created by vela-build to locate binaries:

```bash
OUTDIR=$(cat .vela_build_outdir)
ELF="$OUTDIR/nuttx"
```

### executor Skill Integration

For simulator targets, use executor skill to manage the process:

```bash
# Start simulator
executor_start(command="$OUTDIR/nuttx")

# Read output
executor_read_output(tail_lines=100)

# Stop simulator
executor_stop()
```

### Debugging Workflow

After starting QEMU with `-gdb tcp::{port}`, user can attach GDB:

```bash
# In another terminal
gdb {elf}
(gdb) target remote :{port}
(gdb) continue
```

## Best Practices

- Always read `.vela_build_outdir` to locate binaries
- Use default GDB ports unless user specifies
- For simulator, prefer executor skill to capture stdio
- Provide clear instructions for GDB attachment
- Check binary exists before launching
- Ask user for target type if detection is ambiguous

## Common Scenarios

### Quick Test Run (No Debug)

For quick testing without debugging, omit GDB port:

```bash
# QEMU without GDB
qemu-system-aarch64 -smp 4 -cpu cortex-a53 -semihosting -nographic -machine virt,virtualization=on,gic-version=3 -net none -chardev stdio,id=con,mux=on -serial chardev:con -mon chardev=con,mode=readline -kernel build/nuttx
```

### Debug Session Setup

1. Start QEMU with GDB port
2. In separate terminal, attach GDB
3. Set breakpoints and debug

### Simulator Interactive Session

Use executor to send commands to simulator:

```bash
executor_start(command="build/nuttx")
executor_send(text="help")
executor_send(text="ps")
executor_stop()
```
