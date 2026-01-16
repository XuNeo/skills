---
name: kconfig-tweak
description: "Modify Linux kernel or NuttX .config files from command line without interactive menuconfig. Use when needing to enable/disable config options, set values, query option states, or batch-modify kernel configurations in scripts or CI/CD pipelines."
---

# kconfig-tweak

Command-line tool for modifying `.config` files without launching interactive menuconfig.

## Quick Reference

```bash
# Enable/disable options
kconfig-tweak --enable DEBUG_INFO
kconfig-tweak --disable MODULES
kconfig-tweak -e SMP -d PREEMPT    # Multiple in one command

# Set values
kconfig-tweak --set-val LOG_BUF_SHIFT 17
kconfig-tweak --set-str LOCALVERSION "-custom"

# Query state
kconfig-tweak --state DEBUG_INFO   # Returns: y, n, m, or undef

# Specify config file
kconfig-tweak --file boards/myboard/.config --enable USB

# Module support
kconfig-tweak --module DRM         # Set to m (module)
```

## Commands

| Command | Short | Description |
|---------|-------|-------------|
| `--enable OPTION` | `-e` | Set option to y |
| `--disable OPTION` | `-d` | Set option to n |
| `--module OPTION` | `-m` | Set option to m (module) |
| `--set-val OPTION VALUE` | - | Set integer/hex value |
| `--set-str OPTION STRING` | - | Set string value (quoted) |
| `--undefine OPTION` | `-u` | Remove option definition |
| `--state OPTION` | `-s` | Query current state |

## Position Control

Insert options after a specific option (useful for maintaining config order):

```bash
kconfig-tweak --enable-after USB USB_STORAGE    # -E
kconfig-tweak --disable-after NET BRIDGE        # -D
kconfig-tweak --module-after DRM DRM_I915       # -M
```

## Options

| Option | Description |
|--------|-------------|
| `--file FILE` | Target config file (default: .config) |
| `--keep-case` / `-k` | Preserve symbol case (default: auto-uppercase) |

## Environment Variables

- `CONFIG_` - Symbol prefix (default: "CONFIG_")

## Common Patterns

### Batch Configuration
```bash
# Enable multiple debug options
kconfig-tweak -e DEBUG_INFO -e DEBUG_FS -e KALLSYMS

# Configure network stack
kconfig-tweak --file .config \
  -e NET -e INET -e IPV6 \
  --set-val TCP_CONG_CUBIC y
```

### CI/CD Integration
```bash
# Start from defconfig, then customize
make defconfig
kconfig-tweak -e DEBUG_INFO -d MODULES
make olddefconfig  # Resolve dependencies
```

### Query Before Modify
```bash
# Check current state
STATE=$(kconfig-tweak -s PREEMPT)
if [ "$STATE" = "y" ]; then
  kconfig-tweak -d PREEMPT
fi
```

## Notes

- kconfig-tweak does NOT validate dependencies; run `make olddefconfig` after modifications
- Symbol names auto-uppercase unless `--keep-case` is used
- Changes are immediate; no confirmation prompt
