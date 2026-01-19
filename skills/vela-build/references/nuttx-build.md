# NuttX Build Reference

## Configuration

### Find Build Target (Important!)

Always use `configure.sh -L` to find the correct `BOARD:CONFIG` format:

```bash
cd nuttx
./tools/configure.sh -L | less

# Filter by keyword
./tools/configure.sh -L | grep qemu
./tools/configure.sh -L | grep stm32
```

Output format: `<board>:<config>` (e.g., `qemu-armv8a:nsh_smp`, `stm32f4discovery:nsh`)

### Initialize Configuration

```bash
cd nuttx
./tools/configure.sh -l <board>:<config>
```

Options:
- `-l`: Linux host
- `-m`: macOS host
- `-c`: Windows/Cygwin host
- `-h`: Show help

### Customize Configuration

```bash
cd nuttx
make menuconfig
```

## Build Methods

### CMake + Ninja (Recommended)

```bash
# Configure
cmake -B<outdir> -GNinja -DBOARD_CONFIG=<board>:<config> nuttx

# Build
ninja -C <outdir>

# Incremental clean (keeps config)
ninja -C <outdir> clean

# Full rebuild from scratch (required when config changes)
rm -rf <outdir>
cmake -B<outdir> -GNinja -DBOARD_CONFIG=<board>:<config> nuttx
ninja -C <outdir>
```

### Makefile

```bash
cd nuttx

# Configure
./tools/configure.sh -l <board>:<config>

# Build
make -j$(nproc)

# Clean
make clean

# Distclean (remove config)
make distclean
```

## Common Boards

| Board | Config | Description |
|-------|--------|-------------|
| `qemu-armv8a` | `nsh_smp` | QEMU ARM64 SMP |
| `qemu-armv8a` | `nsh` | QEMU ARM64 single core |
| `sim` | `nsh` | Host simulation |
| `stm32f4discovery` | `nsh` | STM32F4 Discovery |

## Output Files

| File | Description |
|------|-------------|
| `nuttx` | ELF binary (for GDB debugging) |
| `nuttx.bin` | Raw binary (for flashing) |
| `nuttx.hex` | Intel HEX format |
| `System.map` | Symbol map |

## Environment Variables

```bash
# Toolchain prefix
export CROSSDEV=arm-none-eabi-

# Parallel jobs
export MAKE_JOBS=$(nproc)
```
