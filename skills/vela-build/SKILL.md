---
name: vela-build
description: Build Vela RTOS (NuttX-based) with automatic detection of NuttX and Vela-specific targets
license: MIT
---

# Vela Build Skill

Build Vela RTOS with automatic detection of target type and appropriate build method.

## Target Types

Vela supports two categories of targets:

1. **NuttX/Board Targets**: Standard NuttX boards in `nuttx/boards/`
   - Example: `qemu-armv8a`, `stm32f4discovery`
   - Build method: CMake + Ninja (preferred) or Makefile

2. **Vela-Specific Targets**: Custom boards in `vendor/xxx/`
   - Examples: `vendor/sim/`, `vendor/qemu/`, `vendor/bes/`, `vendor/allwinnertech/`
   - Build method: Vela build system (envsetup.sh + lunch + m)

## Usage

Use this skill by mentioning it:

"Use the vela-build skill to build qemu-armv8a with nsh_smp config"

"Use the vela-build skill to build vendor/bes/xxx board"

## Build Workflow

### Step 1: Detect Target Type

Analyze the target to determine which build method to use:

```bash
# Check if target is in vendor/ (Vela-specific)
if [[ "$TARGET" == vendor/* ]]; then
    BUILD_TYPE="vela"
elif [[ -d "nuttx/boards/$TARGET" ]]; then
    BUILD_TYPE="nuttx"
else
    # Ask user for clarification
    BUILD_TYPE="unknown"
fi
```

### Step 2: Determine Build Method

**For NuttX targets:**
- Default: CMake + Ninja
- Fallback: Makefile if CMake not available or target doesn't support it
- Ask user if uncertain

**For Vela targets:**
- Always use Vela build system (envsetup.sh + lunch + m)

### Step 3: Build NuttX Target

**Using CMake + Ninja (preferred):**

```bash
# Configure
cmake -B{OUTDIR} -GNinja -DBOARD_CONFIG={BOARD}:{CONFIG} nuttx

# Build
ninja -C {OUTDIR}
```

**Parameters:**
- `OUTDIR`: Output directory (e.g., `build`, `out-nuttx`)
- `BOARD`: Board name (e.g., `qemu-armv8a`)
- `CONFIG`: Configuration name (e.g., `nsh_smp`)

**Using Makefile (fallback):**

```bash
# Configure
make -C nuttx tools
make -C nuttx {BOARD}_{CONFIG}_defconfig

# Build
make -C nuttx -j$(nproc)
```

### Step 4: Build Vela Target

```bash
# Source environment
source build/envsetup.sh

# Lunch configuration
lunch {CONFIG_PATH}

# Build
m -j32
```

**Parameters:**
- `CONFIG_PATH`: Path to configuration (e.g., `vendor/bes/xxx/configs/defconfig`)
- Output directory: Always `out/` (hardcoded)

### Step 5: Track Output Directory

**CRITICAL**: Save the output directory for use by other skills:

```bash
# For NuttX builds
echo "{OUTDIR}" > .vela_build_outdir

# For Vela builds
echo "out" > .vela_build_outdir
```

This file will be used by skills like `kconfig-tweak` to locate the build output.

## Detection Logic

### NuttX Target Detection

Check if target exists in `nuttx/boards/`:

```bash
if [[ -d "nuttx/boards/$BOARD" ]]; then
    echo "Detected NuttX board target"
fi
```

### Vela Target Detection

Check if target is in `vendor/`:

```bash
if [[ "$TARGET" == vendor/* ]]; then
    echo "Detected Vela-specific target"
fi
```

### Build Method Detection

Check available build tools:

```bash
# Check for CMake
if command -v cmake &> /dev/null; then
    echo "CMake available"
fi

# Check for Ninja
if command -v ninja &> /dev/null; then
    echo "Ninja available"
fi

# Check for Make
if command -v make &> /dev/null; then
    echo "Make available"
fi
```

## Error Handling

- **Target not found**: Inform user and suggest available targets
- **Build method not supported**: Ask user to specify alternative method
- **Build failures**: Display error log and suggest fixes
- **Missing dependencies**: Inform user of required tools (cmake, ninja, make)

## Example Usage

### NuttX Target with CMake

```
Use the vela-build skill to build qemu-armv8a with nsh_smp config
```

**Expected behavior:**
1. Detect `qemu-armv8a` as NuttX target
2. Use CMake + Ninja to build
3. Output to `build/` directory
4. Save `.vela_build_outdir` with `build/`

### Vela Target

```
Use the vela-build skill to build vendor/bes/xxx board
```

**Expected behavior:**
1. Detect `vendor/bes/xxx` as Vela target
2. Source `build/envsetup.sh`
3. Lunch appropriate configuration
4. Build with `m -j32`
5. Output to `out/` directory
6. Save `.vela_build_outdir` with `out/`

### Ambiguous Target

```
Use the vela-build skill to build my-custom-board
```

**Expected behavior:**
1. Cannot determine target type
2. Ask user: "Is this a NuttX board or Vela-specific target?"
3. Ask: "Which build method to use? (cmake/makefile)"
4. Proceed with user's choice

## Integration with Other Skills

This skill creates `.vela_build_outdir` file containing the output directory path. Other skills can read this file to locate build artifacts:

```bash
# Read output directory
OUTDIR=$(cat .vela_build_outdir)

# Use in other operations
ls $OUTDIR
```

Skills that should integrate:
- `kconfig-tweak`: Modify kernel configuration
- `flash`: Flash firmware to device
- `debug`: Start debugging session
- `test`: Run tests on build output

## Best Practices

- Always verify target exists before building
- Use parallel builds (`-j32` for Vela, `-j$(nproc)` for NuttX)
- Clean build directory if configuration changes
- Save output directory for other skills
- Provide clear error messages with suggestions
