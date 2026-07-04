"""
Find the level blob section dispatcher in Engine.dll.

Strategy:
1. Find function boundaries for VA 0x101f50f0 and 0x101f7feb
   by scanning backwards for CC CC (int3 padding) or common prologues.
2. Find all CALL (E8) and JMP (E9) instructions targeting those functions.
3. For each caller, find its function boundary and dump context.
"""

import struct
import sys
import subprocess
import os

DLL_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll"
IMAGE_BASE = 0x10000000

# PE section info
TEXT_RVA = 0x001000
TEXT_RAW = 0x000400
TEXT_SIZE = 0x2aa800

RDATA_RVA = 0x2ac000
RDATA_RAW = 0x2aac00
RDATA_SIZE = 0x0c1c00

# Target VAs (the two functions that call the RLTD validator at 0x101002b0)
RLTD_CALLERS = [0x101f50f0, 0x101f7feb]


def va_to_file(va):
    """Convert VA to file offset using .text section mapping."""
    rva = va - IMAGE_BASE
    if TEXT_RVA <= rva < TEXT_RVA + TEXT_SIZE:
        return rva - TEXT_RVA + TEXT_RAW
    elif RDATA_RVA <= rva < RDATA_RVA + RDATA_SIZE:
        return rva - RDATA_RVA + RDATA_RAW
    return None


def file_to_va(offset):
    """Convert file offset to VA."""
    if TEXT_RAW <= offset < TEXT_RAW + TEXT_SIZE:
        rva = offset - TEXT_RAW + TEXT_RVA
        return IMAGE_BASE + rva
    elif RDATA_RAW <= offset < RDATA_RAW + RDATA_SIZE:
        rva = offset - RDATA_RAW + RDATA_RVA
        return IMAGE_BASE + rva
    return None


def find_function_start(data, target_va):
    """
    Scan backwards from target_va to find function start.
    Look for CC CC padding (int3) or certain prologue patterns.
    """
    target_off = va_to_file(target_va)
    if target_off is None:
        return None

    # Scan backwards up to 0x2000 bytes looking for CC CC followed by non-CC
    scan_start = max(TEXT_RAW, target_off - 0x2000)

    for off in range(target_off - 1, scan_start, -1):
        # Look for CC CC (int3 padding) followed by a non-CC byte
        if data[off] == 0xCC and data[off - 1] == 0xCC:
            # The function likely starts at off + 1
            func_start_off = off + 1
            func_start_va = file_to_va(func_start_off)
            return func_start_va

        # Also look for common prologue: 55 8B EC (push ebp; mov ebp, esp)
        # right at a boundary after CC padding
        if off >= 2 and data[off] == 0x55 and data[off + 1] == 0x8B and data[off + 2] == 0xEC:
            if data[off - 1] == 0xCC or data[off - 1] == 0xC3 or data[off - 1] == 0xCB:
                return file_to_va(off)

    return None


def find_callers(data, target_va):
    """
    Find all E8 (CALL rel32) and E9 (JMP rel32) instructions in .text
    that target the given VA.
    """
    callers = []

    for off in range(TEXT_RAW, TEXT_RAW + TEXT_SIZE - 5):
        opcode = data[off]
        if opcode == 0xE8 or opcode == 0xE9:
            rel32 = struct.unpack_from('<i', data, off + 1)[0]
            call_va = file_to_va(off)
            if call_va is None:
                continue
            dest_va = call_va + 5 + rel32
            if dest_va == target_va:
                callers.append({
                    'type': 'CALL' if opcode == 0xE8 else 'JMP',
                    'file_offset': off,
                    'va': call_va,
                    'dest_va': dest_va,
                })

    return callers


def disassemble_range(dll_path, file_offset, length, start_va):
    """Use objdump to disassemble a range of bytes."""
    try:
        # Use objdump with raw binary mode
        result = subprocess.run(
            ['objdump', '-D', '-b', 'binary', '-m', 'i386',
             '--adjust-vma=' + hex(start_va),
             '--start-address=' + hex(start_va),
             '--stop-address=' + hex(start_va + length),
             dll_path],
            capture_output=True, text=True, timeout=30
        )
        # That won't work well for a DLL. Let's use PE mode instead.
    except Exception:
        pass

    # Try PE-aware disassembly
    try:
        result = subprocess.run(
            ['objdump', '-d',
             '--start-address=' + hex(start_va),
             '--stop-address=' + hex(start_va + length),
             dll_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except Exception:
        pass

    return None


def hexdump_context(data, center_off, before=64, after=64):
    """Print a hex dump around a file offset."""
    start = max(0, center_off - before)
    end = min(len(data), center_off + after)
    lines = []
    for off in range(start, end, 16):
        chunk = data[off:off+16]
        va = file_to_va(off)
        va_str = f"{va:08x}" if va else "????????"
        hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
        ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        marker = " <<<<" if center_off >= off and center_off < off + 16 else ""
        lines.append(f"  {va_str} ({off:08x}): {hex_bytes:<48s} {ascii_chars}{marker}")
    return '\n'.join(lines)


def main():
    print(f"Reading {DLL_PATH}...")
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    print(f"File size: {len(data)} bytes ({len(data)/1024/1024:.1f} MB)")
    print(f".text section: file {TEXT_RAW:#x}..{TEXT_RAW+TEXT_SIZE:#x}, VA {IMAGE_BASE+TEXT_RVA:#x}..{IMAGE_BASE+TEXT_RVA+TEXT_SIZE:#x}")
    print()

    # Step 1: Find function boundaries for our two target VAs
    print("=" * 80)
    print("STEP 1: Find function boundaries for RLTD caller functions")
    print("=" * 80)

    func_starts = {}
    for target_va in RLTD_CALLERS:
        func_start = find_function_start(data, target_va)
        func_starts[target_va] = func_start
        target_off = va_to_file(target_va)

        print(f"\n  Target VA: {target_va:#010x} (file offset {target_off:#x})")
        if func_start:
            func_off = va_to_file(func_start)
            print(f"  Function start: {func_start:#010x} (file offset {func_off:#x})")
            print(f"  Function entry bytes:")
            print(hexdump_context(data, func_off, before=16, after=48))

            # Show bytes just before function start (should be CC CC)
            print(f"  Bytes before function:")
            print(hexdump_context(data, func_off - 16, before=0, after=32))
        else:
            print(f"  Could not find function start!")
            # Show context around the target
            print(f"  Context around target:")
            print(hexdump_context(data, target_off, before=128, after=32))

    # Step 2: Find all callers of these two functions
    print("\n" + "=" * 80)
    print("STEP 2: Find callers of RLTD caller functions")
    print("=" * 80)

    all_callers = {}
    for target_va in RLTD_CALLERS:
        func_start = func_starts.get(target_va)
        search_target = func_start if func_start else target_va

        print(f"\n  Searching for calls to {search_target:#010x} (function containing {target_va:#010x})...")
        callers = find_callers(data, search_target)
        all_callers[target_va] = callers

        if callers:
            print(f"  Found {len(callers)} caller(s):")
            for c in callers:
                print(f"    {c['type']} at VA {c['va']:#010x} (file offset {c['file_offset']:#x})")
        else:
            print(f"  No callers found for function start {search_target:#010x}")
            # Also try the raw VA in case function detection was wrong
            if func_start and func_start != target_va:
                print(f"  Trying raw VA {target_va:#010x}...")
                callers2 = find_callers(data, target_va)
                if callers2:
                    print(f"  Found {len(callers2)} caller(s) to raw VA:")
                    for c in callers2:
                        print(f"    {c['type']} at VA {c['va']:#010x} (file offset {c['file_offset']:#x})")
                    all_callers[target_va] = callers2

    # Step 3: For each caller, find its function and dump context
    print("\n" + "=" * 80)
    print("STEP 3: Disassemble context around each caller")
    print("=" * 80)

    seen_callers = set()
    for target_va, callers in all_callers.items():
        for c in callers:
            caller_va = c['va']
            if caller_va in seen_callers:
                continue
            seen_callers.add(caller_va)

            caller_off = va_to_file(caller_va)
            caller_func = find_function_start(data, caller_va)

            print(f"\n  --- Caller at {caller_va:#010x} ({c['type']} -> {target_va:#010x}) ---")
            if caller_func:
                print(f"  Containing function starts at: {caller_func:#010x}")
            else:
                print(f"  Could not determine containing function")

            # Dump 200 bytes before and 100 bytes after the call
            before = 200
            after = 100
            start_off = max(TEXT_RAW, caller_off - before)
            end_off = min(TEXT_RAW + TEXT_SIZE, caller_off + after)
            start_va = file_to_va(start_off)
            end_va = file_to_va(end_off)

            print(f"  Disassembling VA range {start_va:#010x} .. {end_va:#010x}")

            asm = disassemble_range(DLL_PATH, start_off, end_off - start_off, start_va)
            if asm:
                # Filter to just the disassembly lines
                lines = asm.split('\n')
                in_section = False
                for line in lines:
                    if '<.text>' in line or 'Disassembly' in line:
                        in_section = True
                        continue
                    if in_section and line.strip():
                        # Mark the caller line
                        if f'{caller_va:x}' in line.lower() or f'{caller_va:08x}' in line.lower():
                            print(f"  >>> {line}")
                        else:
                            print(f"      {line}")
            else:
                print(f"  objdump failed, showing hex dump instead:")
                print(hexdump_context(data, caller_off, before=before, after=after))

    # Step 4: Also search for "LVL" magic near these callers
    print("\n" + "=" * 80)
    print("STEP 4: Search for LVL magic (4c 56 4c) comparisons in .text")
    print("=" * 80)

    lvl_magic = b'\x4c\x56\x4c'  # "LVL"
    # In x86, comparing against "LVL" could appear as:
    # cmp dword [reg], 0x004c564c  (little-endian, but with version byte)
    # or cmp with partial magic
    # Search for the 3 bytes as immediate in various forms

    # Search for 4C 56 4C as part of a 4-byte immediate (any version byte)
    found_lvl = []
    for off in range(TEXT_RAW, TEXT_RAW + TEXT_SIZE - 4):
        # LVL in little-endian as part of dword: xx 4C 56 4C (where xx is version byte at highest byte)
        # Actually "LVL\x01" as dword in little-endian = 0x014c564c
        # But wait: if stored in memory as bytes "L","V","L",ver -> dword read = ver<<24 | 'L'<<16 | 'V'<<8 | 'L'
        # = 0x014c564c for version 1
        # As immediate in x86 (little-endian): 4c 56 4c 01
        if data[off] == 0x4c and data[off+1] == 0x56 and data[off+2] == 0x4c:
            va = file_to_va(off)
            # Check if this looks like an immediate operand (preceded by cmp-like opcode)
            # Common patterns: 3D xx xx xx xx (cmp eax, imm32)
            #                  81 F? xx xx xx xx (cmp reg, imm32)
            #                  81 3? xx xx xx xx (cmp [reg], imm32)
            prev1 = data[off - 1] if off > TEXT_RAW else 0
            prev2 = data[off - 2] if off > TEXT_RAW + 1 else 0
            context = f"prev bytes: {data[max(0,off-4):off].hex(' ')}"
            found_lvl.append((off, va, context))

    if found_lvl:
        print(f"  Found {len(found_lvl)} occurrences of '4c 56 4c' in .text:")
        for off, va, ctx in found_lvl[:30]:  # limit output
            print(f"    File {off:#08x}, VA {va:#010x} - {ctx}")
            print(f"    Bytes: {data[max(0,off-6):off+10].hex(' ')}")
    else:
        print("  No raw 'LVL' bytes found in .text as immediate")

    # Also try reversed byte order (if the comparison loads individual bytes)
    # And search in .rdata for "LVL" string
    print(f"\n  Searching .rdata for 'LVL' string...")
    for off in range(RDATA_RAW, RDATA_RAW + RDATA_SIZE - 4):
        if data[off:off+3] == b'LVL':
            va = file_to_va(off)
            surrounding = data[off:off+16]
            print(f"    File {off:#08x}, VA {va:#010x}: {surrounding.hex(' ')} = {surrounding}")

    # Step 5: Search for section type comparisons (cmp reg, 0x0a and 0x0b)
    # near the callers we found
    print("\n" + "=" * 80)
    print("STEP 5: Search for section type dispatch (cmp with 0x05, 0x0a, 0x0b) near callers")
    print("=" * 80)

    for target_va, callers in all_callers.items():
        for c in callers:
            caller_va = c['va']
            caller_func = find_function_start(data, caller_va)
            if not caller_func:
                continue

            func_off = va_to_file(caller_func)
            # Scan the function (up to 0x1000 bytes) for cmp instructions with our section types
            scan_end = min(func_off + 0x1000, TEXT_RAW + TEXT_SIZE)

            print(f"\n  Scanning function at {caller_func:#010x} for section type comparisons:")

            for off in range(func_off, scan_end):
                va = file_to_va(off)
                byte = data[off]

                # cmp eax, imm8: 3C xx
                if byte == 0x3C and off + 1 < scan_end:
                    imm = data[off + 1]
                    if imm in (0x05, 0x06, 0x09, 0x0a, 0x0b, 0x14, 0x17):
                        print(f"    {va:#010x}: cmp al, {imm:#04x}  (section type {imm:#x})")

                # cmp reg, imm8: 83 F8..FF xx (83 /7 for cmp)
                if byte == 0x83 and off + 2 < scan_end:
                    modrm = data[off + 1]
                    reg_op = (modrm >> 3) & 7
                    mod = (modrm >> 6) & 3
                    if reg_op == 7 and mod == 3:  # cmp with register
                        imm = data[off + 2]
                        if imm in (0x05, 0x06, 0x09, 0x0a, 0x0b, 0x14, 0x17):
                            reg_names = ['eax', 'ecx', 'edx', 'ebx', 'esp', 'ebp', 'esi', 'edi']
                            reg = modrm & 7
                            print(f"    {va:#010x}: cmp {reg_names[reg]}, {imm:#04x}  (section type {imm:#x})")

                # cmp reg, imm32: 81 F8..FF xx xx xx xx
                if byte == 0x81 and off + 5 < scan_end:
                    modrm = data[off + 1]
                    reg_op = (modrm >> 3) & 7
                    mod = (modrm >> 6) & 3
                    if reg_op == 7 and mod == 3:
                        imm = struct.unpack_from('<I', data, off + 2)[0]
                        if imm in (0x05, 0x06, 0x09, 0x0a, 0x0b, 0x14, 0x17):
                            reg_names = ['eax', 'ecx', 'edx', 'ebx', 'esp', 'ebp', 'esi', 'edi']
                            reg = modrm & 7
                            print(f"    {va:#010x}: cmp {reg_names[reg]}, {imm:#010x}  (section type {imm:#x})")

                # je/jne/ja/jb after comparison - just note them
                # Also check for switch-style jump table: jmp [reg*4 + table]

                # Break if we hit CC CC (next function)
                if off > func_off + 5 and data[off] == 0xCC and data[off+1] == 0xCC:
                    # But only if we're past the caller VA
                    if va > caller_va + 10:
                        break

    # Step 6: dump full disassembly of the caller functions
    print("\n" + "=" * 80)
    print("STEP 6: Full disassembly of caller-containing functions")
    print("=" * 80)

    for target_va, callers in all_callers.items():
        for c in callers:
            caller_va = c['va']
            caller_func = find_function_start(data, caller_va)
            if not caller_func:
                continue

            func_off = va_to_file(caller_func)
            # Find function end (next CC CC or RET followed by CC)
            func_end_off = func_off
            for off in range(func_off + 5, min(func_off + 0x2000, TEXT_RAW + TEXT_SIZE)):
                if data[off] == 0xCC and off + 1 < len(data) and data[off + 1] == 0xCC:
                    func_end_off = off
                    break

            func_size = func_end_off - func_off
            func_end_va = file_to_va(func_end_off)

            print(f"\n  Function at {caller_func:#010x} .. {func_end_va:#010x} ({func_size} bytes)")
            print(f"  (Contains {c['type']} to {target_va:#010x} at {caller_va:#010x})")

            asm = disassemble_range(DLL_PATH, func_off, func_size, caller_func)
            if asm:
                lines = asm.split('\n')
                in_disasm = False
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    # Look for actual disassembly lines (start with hex address)
                    if ':' in stripped and any(c in '0123456789abcdef' for c in stripped[:8]):
                        in_disasm = True
                    if in_disasm:
                        if f'{caller_va:x}' in line.lower():
                            print(f"  >>> {line}")
                        else:
                            print(f"      {line}")
            else:
                print(f"  objdump unavailable, hex dump:")
                for off in range(func_off, func_end_off, 16):
                    va = file_to_va(off)
                    chunk = data[off:off+16]
                    hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
                    ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                    print(f"    {va:08x}: {hex_bytes:<48s} {ascii_chars}")


if __name__ == '__main__':
    main()
