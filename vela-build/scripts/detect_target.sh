#!/bin/bash
# Detect target type for Vela/NuttX build
# Usage: ./detect_target.sh <target>
# Output: nuttx, vela, or unknown

TARGET="$1"

if [[ -z "$TARGET" ]]; then
    echo "Usage: $0 <target>"
    echo "Example: $0 qemu-armv8a"
    echo "Example: $0 vendor/bes/xxx"
    exit 1
fi

# Check if target is in vendor/ (Vela-specific)
if [[ "$TARGET" == vendor/* ]]; then
    if [[ -d "$TARGET" ]]; then
        echo "vela"
        exit 0
    else
        echo "unknown"
        exit 1
    fi
fi

# Check if target is a NuttX board
# NuttX boards are in nuttx/boards/<arch>/<chip>/<board>/
for arch_dir in nuttx/boards/*/; do
    for chip_dir in "$arch_dir"*/; do
        if [[ -d "${chip_dir}${TARGET}" ]]; then
            echo "nuttx"
            exit 0
        fi
    done
done

# Check if target matches board:config format
if [[ "$TARGET" == *:* ]]; then
    BOARD="${TARGET%%:*}"
    for arch_dir in nuttx/boards/*/; do
        for chip_dir in "$arch_dir"*/; do
            if [[ -d "${chip_dir}${BOARD}" ]]; then
                echo "nuttx"
                exit 0
            fi
        done
    done
fi

echo "unknown"
exit 1
