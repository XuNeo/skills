# Vela Build Reference

## Build System

Vela uses envsetup build system (inspired by Android envsetup and Python venv).

## Workflow

### 1. Source Environment

```bash
source build/envsetup.sh
```

**Note:** If `build/envsetup.sh` does not exist, the `build/` directory may be a stale CMake output. Remove it and sync:

```bash
rm -rf build
repo sync build
```

This sets up:
- Build functions (`lunch`, `m`, `mm`, `mmm`, etc.)
- Environment variables
- PATH injection for prebuilt tools
- Vendor configurations from `vendorsetup.sh`

### 2. Select Configuration (lunch)

```bash
# Method 1: Interactive menu
lunch
# Then enter menu number

# Method 2: Config path (recommended)
lunch vendor/xx-board/configs/ap

# Method 3: NuttX style (colon or slash separator)
lunch mps3-an547:nsh

# Method 4: Menu number directly
lunch 42

# View current lunch config
clunch

# Custom output directory
lunch vendor/xx-board/configs/ap cmake_out/build
```

### 3. Build (m)

```bash
# Full build (default parallelism = ncpu)
m

# With options
m -j12 V=1

# menuconfig
m menuconfig

# Save menuconfig changes to defconfig
m savedefconfig

# Clean build artifacts
m distclean
```

### 4. Deactivate Environment

```bash
deactivate
```

## Build Commands

| Command | Description |
|---------|-------------|
| `m` | Build from top of tree |
| `mm` | Build all + install targets + prebuilt (for library export) |
| `mmm` | Build only current directory's targets (partial build) |
| `m menuconfig` | Configure with menuconfig |
| `m savedefconfig` | Save config changes to defconfig |
| `m distclean` | Clean all build artifacts |

## Output Structure

Output directory follows: `out/[vendor]_[board]_[config]`

Example: `out/qemu_vela_qemu-armeabi-v7a-bl`

```
out/<vendor>_<board>_<config>/
├── vela_xx.elf     # ELF binary
├── vela_xx.bin     # Raw binary
├── System.map      # Symbol map
└── .config         # Build configuration
```

## Helper Tools

| Command | Description |
|---------|-------------|
| `hmm` | Show all available commands |
| `croot` | Jump to project root directory |
| `godir <regex>` | Jump to directory containing file |
| `cgrep <regex>` | Grep in C/C++ source files |
| `mgrep <regex>` | Grep in build files (*.cmake, *.mk) |
| `kgrep <regex>` | Grep in Kconfig files |

## Vendor Targets

Vela-specific boards are in `vendor/` directory:

```
vendor/
├── sim/            # Simulation target
├── qemu/           # QEMU targets
├── bes/            # BES chips
├── allwinnertech/  # Allwinner chips
└── ...
```

## Configuration Files

Vendor board structure (may have multiple levels under boards/):
```
vendor/<vendor>/boards/<chip>/[.../<subdir>]/<board>/
├── configs/
│   ├── <target1>/        # e.g., ap, tee, audio
│   │   └── defconfig
│   ├── <target2>/
│   │   └── defconfig
│   └── ...
├── Kconfig
├── include/
├── src/
└── ...
```

Examples:
```
vendor/allwinnertech/boards/r528/r528s3-x4b/configs/ap/defconfig
vendor/bes/boards/best2003_ep/evb/configs/ap/defconfig
vendor/bes/boards/best2003_ep/evb/configs/audio/defconfig
```

The `<target>` directory (e.g., `ap`, `tee`, `audio`, `zblue`) represents the build configuration target, and `defconfig` is the fixed config filename.

## Environment Variables

```bash
# CMake generator (default: -GNinja)
export VELA_CMAKE_GENERATOR="-GNinja"

# Extra build flags
export VELA_EXTRA_FLAGS="-Wno-cpp"

# Verbose build
export V=1
```

## Tips

- Always `source build/envsetup.sh` in new terminal
- Use `lunch` without args to see available configs interactively
- Use `hmm` to see all available commands
- Use `clunch` to check current lunch configuration
- Use `deactivate` to restore original environment
- Non-CMake configs (e.g., x4b, smartspeaker) will fallback to Makefile build automatically
