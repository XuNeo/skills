---
name: vela-run
description: Run NuttX and Vela RTOS targets on QEMU, FVP, goldfish emulator, and simulator. Supports ARM Cortex-M (MPS3-AN547), ARMv7-A, ARMv8-A, ARMv8-R FVP, goldfish (Android emulator), and native simulator with automatic detection and GDB debugging.
license: MIT
compatibility: Requires qemu-system-arm, qemu-system-aarch64, or Android emulator. FVP requires ARM FVP_BaseR_AEMv8R tool.
---

# Vela Run Skill

Run NuttX and Vela RTOS builds on various emulation targets.

## Target Types

| Target | Binary | Machine | Use Case |
|--------|--------|---------|----------|
| **mps3-an547** | qemu-system-arm | MPS3-AN547 | ARM Cortex-M55 (ARMv8.1-M) |
| **qemu-armv7a** | qemu-system-arm | virt | ARM Cortex-A7 (ARMv7-A) |
| **qemu-armv8a** | qemu-system-aarch64 | virt | ARM Cortex-A53 (ARMv8-A), SMP |
| **fvp-armv8r** | FVP_BaseR_AEMv8R | FVP | ARM Cortex-R82 (ARMv8-R), SMP |
| **goldfish** | emulator.sh | Android Emulator | Vela goldfish (ARM32/ARM64) |
| **simulator** | native binary | Host | Native simulation |

## Usage Examples

```
Use the vela-run skill to run qemu-armv8a with gdb on port 1234
Use the vela-run skill to run mps3-an547
Use the vela-run skill to run goldfish arm32
Use the vela-run skill to run fvp-armv8r with smp
Use the vela-run skill to run the simulator
```

## QEMU Common Parameters

All QEMU targets share these parameters:

### Debug Parameters

| Parameter | Description |
|-----------|-------------|
| `-S` | Freeze CPU at startup, wait for GDB `continue` |
| `-s` | Shorthand for `-gdb tcp::1234` |
| `-gdb tcp::{port}` | Start GDB server on specified port |

### Display & I/O Parameters

| Parameter | Description |
|-----------|-------------|
| `-nographic` | Disable graphical output, use serial console |
| `-chardev stdio,id=con,mux=on` | Create multiplexed stdio character device |
| `-serial chardev:con` | Connect serial port to chardev |
| `-mon chardev=con,mode=readline` | QEMU monitor on same console (Ctrl-a c to switch) |

### Machine Parameters

| Parameter | Description |
|-----------|-------------|
| `-M {machine}` | Machine type (mps3-an547, virt, etc.) |
| `-machine virt,...` | Virtual machine with options |
| `-cpu {model}` | CPU model (cortex-a7, cortex-a53, etc.) |
| `-smp {n}` | Number of CPU cores for SMP |
| `-m {size}` | Memory size (e.g., 2G) |

### Machine Options (for `-machine virt`)

| Option | Description |
|--------|-------------|
| `virtualization=on/off` | Enable/disable EL2 virtualization |
| `gic-version=2/3` | GIC version (2 for GICv2, 3 for GICv3) |
| `highmem=off` | Disable high memory (required for ivshmem) |

### Network Parameters

| Parameter | Description |
|-----------|-------------|
| `-net none` | Disable networking |
| `-netdev user,id=u1,...` | User-mode networking with port forwarding |
| `-device virtio-net-device,...` | Virtio network device |

### Filesystem Parameters

| Parameter | Description |
|-----------|-------------|
| `-fsdev local,...` | 9pfs filesystem device |
| `-device virtio-9p-device,...` | Virtio 9p device for host sharing |
| `-semihosting` | Enable ARM semihosting (hostfs access) |

### Device Loading

| Parameter | Description |
|-----------|-------------|
| `-kernel {file}` | Kernel/firmware ELF or binary |
| `-device loader,file={img},addr={addr}` | Load file at specific address |

## Run Commands

### MPS3-AN547 (ARM Cortex-M)

Basic run:
```bash
qemu-system-arm -M mps3-an547 -nographic -kernel nuttx.bin
```

With GDB:
```bash
qemu-system-arm -M mps3-an547 -m 2G -nographic -kernel nuttx.bin -S -s
# Or custom port:
qemu-system-arm -M mps3-an547 -m 2G -nographic -kernel nuttx.bin -gdb tcp::1128
```

With ROMFS (for PIC apps):
```bash
qemu-system-arm -M mps3-an547 -m 2G -nographic \
  -kernel nuttx.bin \
  -device loader,file=romfs.img,addr=0x60000000
```

**Note (QEMU 9.20+):** UART interrupts swapped, configure:
```
CONFIG_CMSDK_UART0_TX_IRQ=50
CONFIG_CMSDK_UART0_RX_IRQ=49
```

### QEMU ARMv7-A

Basic run:
```bash
qemu-system-arm -cpu cortex-a7 -nographic \
  -machine virt,virtualization=off,gic-version=2 \
  -net none \
  -chardev stdio,id=con,mux=on \
  -serial chardev:con \
  -mon chardev=con,mode=readline \
  -kernel nuttx
```

With GDB (paused):
```bash
qemu-system-arm -cpu cortex-a7 -nographic \
  -machine virt,virtualization=off,gic-version=2 \
  -net none \
  -chardev stdio,id=con,mux=on \
  -serial chardev:con \
  -mon chardev=con,mode=readline \
  -kernel nuttx \
  -S -s
```

With ivshmem (OpenAMP):
```bash
qemu-system-arm -cpu cortex-a7 -nographic \
  -machine virt,highmem=off \
  -object memory-backend-file,id=shmmem-shmem0,mem-path=/dev/shm/ivshmem0,size=4194304,share=yes \
  -device ivshmem-plain,id=shmem0,memdev=shmmem-shmem0,addr=0xb \
  -kernel nuttx
```

### QEMU ARMv8-A (AArch64)

Single core (GICv3):
```bash
qemu-system-aarch64 -cpu cortex-a53 -nographic \
  -machine virt,virtualization=on,gic-version=3 \
  -net none \
  -chardev stdio,id=con,mux=on \
  -serial chardev:con \
  -mon chardev=con,mode=readline \
  -kernel nuttx
```

SMP (4 cores):
```bash
qemu-system-aarch64 -cpu cortex-a53 -smp 4 -nographic \
  -machine virt,virtualization=on,gic-version=3 \
  -net none \
  -chardev stdio,id=con,mux=on \
  -serial chardev:con \
  -mon chardev=con,mode=readline \
  -kernel nuttx
```

With GDB (paused):
```bash
qemu-system-aarch64 -cpu cortex-a53 -smp 4 -nographic \
  -machine virt,virtualization=on,gic-version=3 \
  -net none \
  -chardev stdio,id=con,mux=on \
  -serial chardev:con \
  -mon chardev=con,mode=readline \
  -kernel nuttx \
  -S -s
```

With semihosting:
```bash
qemu-system-aarch64 -cpu cortex-a53 -smp 4 -semihosting -nographic \
  -machine virt,virtualization=on,gic-version=3 \
  -net none \
  -chardev stdio,id=con,mux=on \
  -serial chardev:con \
  -mon chardev=con,mode=readline \
  -kernel nuttx
```

GICv2 variant:
```bash
qemu-system-aarch64 -cpu cortex-a53 -nographic \
  -machine virt,virtualization=off,gic-version=2 \
  -net none \
  -chardev stdio,id=con,mux=on \
  -serial chardev:con \
  -mon chardev=con,mode=readline \
  -kernel nuttx
```

With virtio networking:
```bash
qemu-system-aarch64 -cpu cortex-a53 -smp 4 -nographic \
  -machine virt,virtualization=on,gic-version=3 \
  -chardev stdio,id=con,mux=on -serial chardev:con \
  -global virtio-mmio.force-legacy=false \
  -netdev user,id=u1,hostfwd=tcp:127.0.0.1:10023-10.0.2.15:23 \
  -device virtio-net-device,netdev=u1,bus=virtio-mmio-bus.0 \
  -mon chardev=con,mode=readline \
  -kernel nuttx
```

With 9pfs (host filesystem sharing):
```bash
qemu-system-aarch64 -cpu cortex-a53 -nographic \
  -machine virt,virtualization=on,gic-version=3 \
  -fsdev local,security_model=none,id=fsdev0,path=/path/to/share \
  -device virtio-9p-device,id=fs0,fsdev=fsdev0,mount_tag=host \
  -chardev stdio,id=con,mux=on -serial chardev:con \
  -mon chardev=con,mode=readline \
  -kernel nuttx
```

### FVP ARMv8-R (Cortex-R82)

**Prerequisites:** Download FVP from [ARM Ecosystem Models](https://developer.arm.com/downloads/-/arm-ecosystem-models)

Single core:
```bash
FVP_BaseR_AEMv8R \
  -f boards/arm64/fvp-v8r/fvp-armv8r/scripts/fvp_cfg.txt \
  -a ./nuttx
```

SMP:
```bash
FVP_BaseR_AEMv8R \
  -f boards/arm64/fvp-v8r/fvp-armv8r/scripts/fvp_cfg_smp.txt \
  -a ./nuttx
```

**Serial ports:** FVP exposes 4 UART ports on localhost:
- terminal_0: port 5000
- terminal_1: port 5001 (default console)
- terminal_2: port 5002
- terminal_3: port 5003

Connect to console:
```bash
telnet localhost 5001
```

### Goldfish (Vela Android Emulator)

ARM32:
```bash
./emulator.sh out/qemu_vela_goldfish-armeabi-v7a-ap/
```

ARM64:
```bash
./emulator.sh out/qemu_vela_goldfish-arm64-v8a-ap/
```

No window (terminal only):
```bash
./emulator.sh out/qemu_vela_goldfish-armeabi-v7a-ap/ -no-window
```

With GDB (paused):
```bash
./emulator.sh out/qemu_vela_goldfish-armeabi-v7a-ap/ -qemu -S -s
```

With semihosting (for hostfs):
```bash
./emulator.sh out/qemu_vela_goldfish-armeabi-v7a-ap/ -qemu -semihosting
```

With 9pfs:
```bash
./emulator.sh out/qemu_vela_goldfish-armeabi-v7a-ap/ \
  -qemu \
  -fsdev local,security_model=passthrough,id=fsdev0,path=/path/to/share \
  -device virtio-9p-pci,id=fs0,fsdev=fsdev0,mount_tag=hostshare
```

Persistent instance (-keep):
```bash
./emulator.sh vela -keep -no-window
```

### Simulator (Native)

Direct execution:
```bash
./build/nuttx
```

## Skill Integration

### Interactive Sessions

For interactive work with QEMU, simulator, or GDB where user needs to interact with the console:

**Use the tmux skill** to start and manage interactive sessions. This allows:
- Running QEMU/simulator in background
- Sending commands and capturing output
- User can attach to monitor the session

### GDB Debugging

For debugging NuttX with GDB:

**Use the gdb-start skill** to connect GDB to QEMU's GDB server. Start QEMU with `-S -s` flags first.

GDB toolchains:
- arm: `gdb-multiarch`
- xtensa: `xtensa-esp32s3-elf-gdb`
- Vela prebuilt: `./prebuilts/gcc/linux/arm[64]/bin/`

Enable debug symbols in defconfig:
```
CONFIG_DEBUG_SYMBOLS=y
```

### Automated Tasks

For fully automated tasks without user interaction:

**Use the executor skill** to run and control processes programmatically.

## Target Detection

### From Build Output

```bash
OUTDIR=$(cat .vela_build_outdir 2>/dev/null || echo "build")

# Detect from directory name
case "$OUTDIR" in
  *sim*|*simulator*) TARGET="simulator" ;;
  *goldfish*) TARGET="goldfish" ;;
  *mps3*|*an547*) TARGET="mps3-an547" ;;
  *armv7a*|*v7a*) TARGET="qemu-armv7a" ;;
  *armv8a*|*v8a*|*arm64*|*aarch64*) TARGET="qemu-armv8a" ;;
  *fvp*|*armv8r*) TARGET="fvp-armv8r" ;;
  *) TARGET="unknown" ;;
esac
```

### Binary Location

| Build Type | Binary Path |
|------------|-------------|
| CMake | `build/nuttx` or `build/nuttx.bin` |
| Makefile | `nuttx/nuttx` |
| Vela | `out/<config>/nuttx` |
| Goldfish | `out/qemu_vela_goldfish-*/` (directory) |

## Default Parameters

| Parameter | Default |
|-----------|---------|
| GDB Port (QEMU `-s`) | 1234 |
| GDB Port (Goldfish) | 1234 |
| SMP Cores (ARM64) | 4 |
| FVP Console Port | 5001 |

## Error Handling

| Error | Solution |
|-------|----------|
| Binary not found | Run vela-build first, check `.vela_build_outdir` |
| QEMU not installed | `apt install qemu-system-arm qemu-system-aarch64` |
| FVP not found | Download from ARM Ecosystem Models |
| emulator.sh missing | Check Vela project root |
| GDB connection refused | Verify QEMU started with `-s` or `-gdb tcp::port` |

## References

- [NuttX MPS3-AN547](https://nuttx.apache.org/docs/latest/platforms/arm/mps/boards/mps3-an547/index.html)
- [NuttX QEMU ARMv7-A](https://nuttx.apache.org/docs/latest/platforms/arm/qemu/boards/qemu-armv7a/index.html)
- [NuttX QEMU ARMv8-A](https://nuttx.apache.org/docs/latest/platforms/arm64/qemu/boards/qemu-armv8a/index.html)
- [NuttX FVP ARMv8-R](https://nuttx.apache.org/docs/12.8.0/platforms/arm64/fvp-v8r/boards/fvp-armv8r/index.html)
