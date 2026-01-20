---
name: x4b-device
description: Operate X4B real hardware device including firmware download, flashing via fastboot, adb control, serial monitoring via minicom, and JLink debugging. Integrates with vela-jira for firmware retrieval and gdb-start for debugging.
license: MIT
compatibility: Requires fastboot, adb, minicom, JLinkGDBServer. Linux environment with USB access.
---

# X4B Device Skill

Operate X4B real hardware device for firmware flashing, debugging, and monitoring.

## Workflow Overview

1. **Get Firmware** - Download from CI (URL in JIRA) or local build
2. **Flash Firmware** - Use fastboot to flash images
3. **Monitor Serial** - Use minicom for UART console
4. **Debug** - Use JLink GDB server + gdb-start skill
5. **Control** - Use adb for shell access

## Skill Integration

| Task | Skill | When to Use |
|------|-------|-------------|
| Interactive sessions | **tmux skill** | User needs to interact with device/console |
| Automated operations | **executor skill** | Fully automated tasks without interaction |
| GDB debugging | **gdb-start skill** | Connect to JLink GDB server |
| Get firmware URL | **vela-jira skill** | Retrieve firmware from JIRA issue |

## Firmware Acquisition

### From JIRA (Recommended)

**Use the vela-jira skill** to get firmware URL from JIRA issue description.

Firmware URL pattern:
```
https://cnbj1-fds.api.xiaomi.net/vela-ci/Vela-x4b-dev-system-CI/{build_number}/{timestamp}.tar.gz
```

Example:
```
https://cnbj1-fds.api.xiaomi.net/vela-ci/Vela-x4b-dev-system-CI/16807/2026011909541.tar.gz
```

### Download and Extract

```bash
# Download
wget -O x4b-firmware.tar.gz "{firmware_url}"

# Extract
mkdir -p ~/tmp/{timestamp}/images
tar -xzf x4b-firmware.tar.gz -C ~/tmp/{timestamp}/images/
```

## Firmware Directory Structure

After extraction, the x4b image directory contains:

```
x4b/
├── image_nokasan/         # Combined flash image (default) - FLASHABLE
│   ├── vela_res.bin       # Resource partition image (fastboot flashable)
│   ├── vela_tee.bin       # TEE partition image (fastboot flashable)
│   └── usrdata.fex        # User data partition (fastboot flashable)
├── image_debug/           # Combined flash image (debug) - FLASHABLE
├── image_test/            # Combined flash image (test) - FLASHABLE
├── image_bootloader_test/ # Combined flash image (bootloader test) - FLASHABLE
├── ap/                    # AP core firmware - DEBUG ONLY
│   ├── vela_ap.elf        # ELF with debug symbols (for GDB)
│   ├── vela_ap.bin        # Binary image
│   └── .config            # Build configuration
├── ap_debug/              # AP core firmware (debug) - DEBUG ONLY
├── ap_test/               # AP core firmware (test) - DEBUG ONLY
├── bootloader/            # Bootloader firmware - DEBUG ONLY
│   ├── vela_bl.elf        # ELF with debug symbols (for GDB)
│   └── vela_bl.bin        # Binary image
├── tee/                   # TEE firmware - DEBUG ONLY
│   ├── vela_tee.elf       # ELF with debug symbols (for GDB)
│   └── vela_tee.bin       # Binary image
├── ota/                   # OTA firmware - DEBUG ONLY
└── x4b.build_cmd          # Build commands reference
```

### Important Notes

- **Only `image_xxx/` directories contain flashable images** (vela_res.bin, vela_tee.bin, usrdata.fex)
- Other directories (ap/, tee/, bootloader/) provide **ELF files for debugging only**
- **Default: Use `image_nokasan/` unless user specifies otherwise**

### Image Selection

| Use Case | Directory | Description |
|----------|-----------|-------------|
| **Normal use** | `image_nokasan/` | Default, no KASAN |
| Debug build | `image_debug/` | With debug symbols |
| Test build | `image_test/` | With test features |
| Bootloader test | `image_bootloader_test/` | Bootloader testing |

## Fastboot Flashing

### Prerequisites

Before using fastboot:
```bash
# Enable debug mode on device first
echo "" > /data/debugmode
```

### Troubleshooting fwupd Conflict

If fastboot hangs or device stuck in bootloader:
```bash
# Check if fwupd is running
ps -ef | grep fwupd | grep -v grep

# Disable fwupd service
sudo systemctl stop fwupd.service
sudo systemctl disable fwupd.service
sudo chmod -x /usr/libexec/fwupd/fwupd
```

### Enter Fastboot Mode

```bash
# Method 1 - From device shell (if device is responsive)
reboot bootloader

# Method 2 - Via ADB (if ADB is available)
adb reboot bootloader

# Method 3 - Auto-download mode (if device is bricked)
# 1. Run fastboot command on host (enters "< waiting for any device >" state)
# 2. Reboot/power cycle device
# 3. Device will stop in bootloader when it receives PC packet
```

Verify device detected:
```bash
fastboot devices
```

### Flash Partitions

**Flash res partition (contains AP firmware):**
```bash
fastboot flash res {image_dir}/image_nokasan/vela_res.bin
```

**Flash tee partition:**
```bash
fastboot flash tee {image_dir}/image_nokasan/vela_tee.bin
# Or from tee directory:
fastboot flash tee {image_dir}/tee/vela_tee.bin
```

**Flash bootloader partition:**
```bash
fastboot flash bootloader {image_dir}/bootloader/vela_bl.bin
```

**Flash usrdata partition (must erase first):**
```bash
fastboot erase usrdata
fastboot flash usrdata {image_dir}/image_nokasan/usrdata.fex
```

### Reboot After Flashing

```bash
fastboot reboot
```

### Fastboot Commands Reference

| Command | Description |
|---------|-------------|
| `fastboot devices` | List connected devices |
| `fastboot flash {partition} {file}` | Flash partition |
| `fastboot erase {partition}` | Erase partition |
| `fastboot reboot` | Reboot device |
| `fastboot getvar product` | Get product name |
| `fastboot getvar version` | Get version |
| `fastboot getvar max-download-size` | Get max download size |

### Partition Names

| Partition | Content |
|-----------|---------|
| `res` | Resource partition (contains vela_ap.bin) |
| `tee` | TEE firmware |
| `bootloader` | Bootloader |
| `usrdata` | User data (yaffs filesystem) |

## ADB Control

After device boots:

### Verify Connection

```bash
adb devices
```

### Shell Access

```bash
adb shell
```

### Common ADB Commands

| Command | Description |
|---------|-------------|
| `adb devices` | List connected devices |
| `adb shell` | Interactive shell |
| `adb shell {cmd}` | Run single command |
| `adb push {local} {remote}` | Push file to device |
| `adb pull {remote} {local}` | Pull file from device |
| `adb logcat` | View system logs |
| `adb reboot` | Reboot device |
| `adb reboot bootloader` | Reboot to fastboot |

## Serial Monitoring (minicom)

### Start minicom

```bash
minicom -D /dev/ttyUSB0 -b 921600
```

**Baud rate: 921600** (fixed for X4B)

Common serial ports:
- `/dev/ttyUSB0` - USB-UART adapter
- `/dev/ttyACM0` - CDC ACM device

### minicom Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl-A Z` | Help menu |
| `Ctrl-A X` | Exit minicom |
| `Ctrl-A Q` | Quit without reset |
| `Ctrl-A L` | Capture to file |

**Use the tmux skill** to run minicom in a managed session for interactive monitoring.

## JLink Debugging

### Start JLink GDB Server

X4B uses R528S3 dual-core ARM processor.

Connect to Core 0 (AP):
```bash
JLinkGDBServer -if JTAG -speed 1000KHZ -device R528S3-CORE0 -port 23331
```

Connect to Core 1 (TEE):
```bash
JLinkGDBServer -if JTAG -speed 1000KHZ -device R528S3-CORE1 -port 23332
```

### JLink Parameters

| Parameter | Description |
|-----------|-------------|
| `-if JTAG` | Interface type (JTAG) |
| `-speed 1000KHZ` | JTAG clock speed |
| `-device R528S3-CORE0` | AP core |
| `-device R528S3-CORE1` | TEE core |
| `-port {port}` | GDB server port |

### Connect GDB

**Use the gdb-start skill** to connect GDB to JLink GDB server.

ELF files for debugging:
- AP: `{image_dir}/ap/vela_ap.elf`
- TEE: `{image_dir}/tee/vela_tee.elf`
- Bootloader: `{image_dir}/bootloader/vela_bl.elf`

GDB target:
- Core 0 (AP): `localhost:23331`
- Core 1 (TEE): `localhost:23332`

**Use the tmux skill** to run JLinkGDBServer in interactive session.

## Quick Reference

### Flash and Boot

```bash
# 1. Download firmware (get URL from JIRA via vela-jira skill)
wget -O fw.tar.gz "{url}"
tar -xzf fw.tar.gz

# 2. Enter fastboot mode
adb reboot bootloader
# Or from device shell: reboot bootloader

# 3. Flash (use image_nokasan by default)
fastboot flash res x4b/image_nokasan/vela_res.bin
fastboot flash tee x4b/image_nokasan/vela_tee.bin
fastboot reboot

# 4. Verify
adb devices
adb shell
```

### Debug Session

```bash
# 1. Start JLink GDB Server (use tmux skill for interactive session)
JLinkGDBServer -if JTAG -speed 1000KHZ -device R528S3-CORE0 -port 2331

# 2. Connect GDB (use gdb-start skill)
# Target: localhost:2331
# ELF: x4b/ap/vela_ap.elf
```

### Serial Monitor

```bash
# Use tmux skill to run minicom
minicom -D /dev/ttyUSB0 -b 1500000
```

## Memory Dump (Crash Analysis)

Dump device memory via fastboot for crash analysis.

### Enable Dump Mode

Before crash occurs, enable dump mode on device:
```bash
echo "" > /data/dumpmode
```

When device crashes, it will automatically stop in bootloader mode, allowing memory dump.

### Dump Memory

```bash
# Device is in bootloader after crash

# Dump memory region (address, size)
fastboot oem memdump 0x40000000 0x8000000

# Retrieve the dump file
fastboot get_staged 0x40000000.bin
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `0x40000000` | Start address (DRAM base) |
| `0x8000000` | Size (128MB) |

### Common Memory Regions

| Region | Address | Size | Description |
|--------|---------|------|-------------|
| DRAM | `0x40000000` | `0x8000000` | Main memory (128MB) |

**Use with crash-analysis skill** to analyze the memory dump with ELF symbols.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `fastboot devices` empty | Check USB, ensure device in fastboot mode |
| Fastboot hangs | Disable fwupd service (see above) |
| `adb devices` unauthorized | Accept authorization on device |
| `/dev/ttyUSB0` permission denied | `sudo usermod -aG dialout $USER` |
| JLink connection failed | Check JTAG cable, verify device power |
| AVB signature error | Update bootloader to 0825+ version |
| Image rollback error | Update bootloader to 0825+ version |
