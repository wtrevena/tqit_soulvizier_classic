#!/bin/bash
# Build 32-bit PathEngine shim
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GCC=/c/msys64/mingw32/bin/g++.exe

echo "Building pathengine_shim.exe (32-bit)..."
PATH="/c/msys64/mingw32/bin:$PATH" "$GCC" \
    -o "$SCRIPT_DIR/pathengine_shim.exe" \
    "$SCRIPT_DIR/pathengine_shim.cpp" \
    -static-libgcc -static-libstdc++ \
    -Wall -Wno-attributes \
    -O2 2>&1
echo "Exit: $?"
ls -la "$SCRIPT_DIR/pathengine_shim.exe" 2>/dev/null
