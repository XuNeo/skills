---
name: vela-build
description: Build Vela RTOS (NuttX-based) with automatic detection of NuttX and Vela-specific targets. Supports CMake+Ninja, Makefile, and Vela envsetup build system (lunch + m).
compatibility: Requires cmake, ninja, or make. Linux/macOS environment.
---

# Vela Build Skill

Build Vela RTOS with automatic detection of target type and appropriate build method.

## Target Types

| Type | Location | Build Method |
|------|----------|--------------|
| NuttX/Board | `nuttx/boards/` | CMake+Ninja (preferred) or Makefile |
| Vela-Specific | `vendor/xxx/` | envsetup (lunch + m) |

## Quick Start

```bash
# NuttX target (CMake)
cmake -Bbuild -GNinja -DBOARD_CONFIG=qemu-armv8a:nsh_smp nuttx
ninja -C build

# NuttX target (Makefile)
cd nuttx && ./tools/configure.sh -l <board>:<config> && make -j$(nproc)

# Vela target
source build/envsetup.sh
lunch vendor/xx-board/configs/ap
m
```

## Build Workflow

### 1. Detect Target Type

```bash
# Vela target: starts with vendor/
if [[ "$TARGET" == vendor/* ]]; then
    BUILD_TYPE="vela"
# NuttX target: exists in nuttx/boards/
elif [[ -d "nuttx/boards/*/$TARGET" ]]; then
    BUILD_TYPE="nuttx"
fi
```

### 2. Build

**NuttX (CMake - preferred):**
```bash
cmake -B{OUTDIR} -GNinja -DBOARD_CONFIG={BOARD}:{CONFIG} nuttx
ninja -C {OUTDIR}
```

**NuttX (Makefile):**
```bash
cd nuttx
./tools/configure.sh -l {BOARD}:{CONFIG}
make -j$(nproc)
```

**Vela:**
```bash
source build/envsetup.sh
lunch vendor/xx-board/configs/ap
m
```

### 3. Common Vela Commands

```bash
m menuconfig      # Configure
m savedefconfig   # Save config changes
m distclean       # Clean all
```

## Output Locations

| Build Type | Output Directory | Binary Location |
|------------|------------------|-----------------|
| CMake | `build/` (configurable) | `build/nuttx` |
| Makefile | `nuttx/` | `nuttx/nuttx` |
| Vela | `out/<vendor>_<board>_<config>/` | `out/<vendor>_<board>_<config>/vela_xx.elf` |

## Finding Build Targets

**NuttX targets**: Use `./tools/configure.sh -L` to find valid `BOARD:CONFIG`:
```bash
cd nuttx
./tools/configure.sh -L | grep <keyword>
```

**Vela targets**: Use `lunch` menu interactively or browse `vendor/` directory.

## Error Handling

- **Target not found**: Use `./tools/configure.sh -L` for NuttX or `lunch` menu for Vela
- **Build failure**: Check `m menuconfig` for config issues
- **Missing tools**: Install cmake, ninja, or make
- **Missing build/envsetup.sh**: Remove stale `build/` dir and run `repo sync build`

## References

- [NuttX Build Commands](references/nuttx-build.md)
- [Vela Build Commands](references/vela-build.md)
- [Troubleshooting](references/troubleshooting.md)
