# Troubleshooting

## Common Issues

### Configuration Not Found

**Error:** `ERROR: No configuration found for <board>:<config>`

**Solution:**
```bash
# List available configurations
cd nuttx
./tools/configure.sh -L | grep <board>
```

### Missing Toolchain

**Error:** `arm-none-eabi-gcc: command not found`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install gcc-arm-none-eabi

# macOS
brew install arm-none-eabi-gcc
```

### CMake Version Too Old

**Error:** `CMake 3.16 or higher is required`

**Solution:**
```bash
# Ubuntu
sudo apt install cmake

# Or install from source
wget https://cmake.org/files/v3.28/cmake-3.28.0-linux-x86_64.sh
chmod +x cmake-3.28.0-linux-x86_64.sh
sudo ./cmake-3.28.0-linux-x86_64.sh --prefix=/usr/local
```

### Ninja Not Found

**Error:** `ninja: command not found`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install ninja-build

# macOS
brew install ninja
```

### Build Fails After Config Change

**Warning:** Configuration changes may require clean build.

**Solution:**
```bash
# CMake
ninja -C build clean
ninja -C build

# Makefile
make clean
make -j$(nproc)

# Vela
m clobber
m -j32
```

### Out of Memory During Build

**Error:** `g++: fatal error: Killed signal terminated program`

**Solution:**
```bash
# Reduce parallel jobs
make -j4  # Instead of -j$(nproc)

# Or add swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Permission Denied

**Error:** `Permission denied` when running scripts

**Solution:**
```bash
chmod +x nuttx/tools/configure.sh
chmod +x build/envsetup.sh
```

## Debug Build Issues

### Enable Verbose Output

```bash
# CMake
cmake -Bbuild -GNinja -DBOARD_CONFIG=<board>:<config> nuttx
ninja -C build -v

# Makefile
make V=1

# Vela
V=1 m -j32
```

### Check Configuration

```bash
# View current config
cat nuttx/.config | grep CONFIG_

# Compare with defconfig
diff nuttx/.config nuttx/boards/<arch>/<chip>/<board>/configs/<config>/defconfig
```

### Clean Build

```bash
# Full clean (CMake)
rm -rf build

# Full clean (Makefile)
make distclean

# Full clean (Vela)
m clobber
```

## Getting Help

- NuttX Mailing List: dev@nuttx.apache.org
- NuttX GitHub: https://github.com/apache/nuttx
- NuttX Documentation: https://nuttx.apache.org/docs/latest/
