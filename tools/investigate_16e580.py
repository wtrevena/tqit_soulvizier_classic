"""
Investigate the function at 0x1016e580 which has dispatch on section types 0x09, 0x0a, 0x0b.
This could be a DIFFERENT level blob parser (perhaps for a different version or usage).

Also: find the caller chain for this function to understand when it's used.
"""

import struct

DLL_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll"
IMAGE_BASE = 0x10000000
TEXT_RVA = 0x001000
TEXT_RAW = 0x000400
TEXT_SIZE = 0x2aa800
RDATA_RVA = 0x2ac000
RDATA_RAW = 0x2aac00
RDATA_SIZE = 0x0c1c00


def va_to_file(va):
    rva = va - IMAGE_BASE
    if TEXT_RVA <= rva < TEXT_RVA + TEXT_SIZE:
        return rva - TEXT_RVA + TEXT_RAW
    elif RDATA_RVA <= rva < RDATA_RVA + RDATA_SIZE:
        return rva - RDATA_RVA + RDATA_RAW
    return None

def file_to_va(off):
    if TEXT_RAW <= off < TEXT_RAW + TEXT_SIZE:
        rva = off - TEXT_RAW + TEXT_RVA
        return IMAGE_BASE + rva
    elif RDATA_RAW <= off < RDATA_RAW + RDATA_SIZE:
        rva = off - RDATA_RAW + RDATA_RVA
        return IMAGE_BASE + rva
    return None


def find_function_start(data, target_va):
    target_off = va_to_file(target_va)
    for off in range(target_off - 1, max(TEXT_RAW, target_off - 0x2000), -1):
        if data[off] == 0xCC and data[off - 1] == 0xCC:
            return file_to_va(off + 1)
    return None


def find_function_end(data, start_va):
    start_off = va_to_file(start_va)
    for off in range(start_off + 5, min(start_off + 0x3000, TEXT_RAW + TEXT_SIZE)):
        if data[off] == 0xCC and data[off + 1] == 0xCC:
            return file_to_va(off)
    return file_to_va(start_off + 0x1000)


def find_callers(data, target_va):
    callers = []
    for off in range(TEXT_RAW, TEXT_RAW + TEXT_SIZE - 5):
        b = data[off]
        if b == 0xE8 or b == 0xE9:
            rel32 = struct.unpack_from('<i', data, off + 1)[0]
            call_va = file_to_va(off)
            dest_va = call_va + 5 + rel32
            if dest_va == target_va:
                callers.append(('CALL' if b == 0xE8 else 'JMP', call_va))
    return callers


def hexdump(data, start_va, length):
    start_off = va_to_file(start_va)
    for o in range(start_off, start_off + length, 16):
        va = file_to_va(o)
        chunk = data[o:o + 16]
        hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
        ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {va:#010x}: {hex_bytes}  {ascii_chars}")


def main():
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    func_va = 0x1016e580
    func_end = find_function_end(data, func_va)
    func_size = (va_to_file(func_end) - va_to_file(func_va))

    print("=" * 80)
    print(f"FUNCTION AT {func_va:#010x} (size: {func_size} bytes, ends at {func_end:#010x})")
    print("=" * 80)

    # Show the full function hex dump
    print("\nFull hex dump:")
    hexdump(data, func_va, min(func_size, 0x600))

    # Find all section type comparisons in this function
    print("\n" + "=" * 80)
    print("SECTION TYPE COMPARISONS IN THIS FUNCTION")
    print("=" * 80)

    func_off = va_to_file(func_va)
    func_end_off = va_to_file(func_end)

    section_types = {0x03: "TERRAIN?", 0x05: "ENTITIES", 0x06: "SUB-TYPED",
                     0x09: "GRID", 0x0a: "PTH_PATHFINDING", 0x0b: "RLTD_PATHFINDING",
                     0x14: "METADATA", 0x17: "UNKNOWN_17"}

    for off in range(func_off, func_end_off - 3):
        b = data[off]
        # cmp eax, imm8 (83 F8 xx)
        if b == 0x83 and data[off + 1] == 0xF8:
            imm = data[off + 2]
            va = file_to_va(off)
            name = section_types.get(imm, "")
            if name or imm <= 0x20:
                print(f"  {va:#010x}: cmp eax, {imm:#04x}  {name}")
        # cmp edx, imm8 (83 FA xx)
        if b == 0x83 and data[off + 1] == 0xFA:
            imm = data[off + 2]
            va = file_to_va(off)
            name = section_types.get(imm, "")
            if name or imm <= 0x20:
                print(f"  {va:#010x}: cmp edx, {imm:#04x}  {name}")
        # cmp ecx, imm8 (83 F9 xx)
        if b == 0x83 and data[off + 1] == 0xF9:
            imm = data[off + 2]
            va = file_to_va(off)
            name = section_types.get(imm, "")
            if name or imm <= 0x20:
                print(f"  {va:#010x}: cmp ecx, {imm:#04x}  {name}")

    # Find all CALL instructions in this function
    print("\n" + "=" * 80)
    print("ALL CALLS FROM THIS FUNCTION")
    print("=" * 80)

    known_funcs = {
        0x101f4ba0: "RLTD_HANDLER_1",
        0x101f6210: "RLTD_HANDLER_2",
        0x101002b0: "RLTD_VALIDATOR",
        0x101b3fb0: "MAIN_BLOB_DISPATCHER",
        0x101b1d00: "POST_LOAD_PROCESSOR",
        0x101b6000: "GRID_HANDLER",
    }

    for off in range(func_off, func_end_off - 5):
        if data[off] == 0xE8:
            rel32 = struct.unpack_from('<i', data, off + 1)[0]
            call_va = file_to_va(off)
            dest_va = call_va + 5 + rel32
            ann = known_funcs.get(dest_va, "")
            if ann:
                print(f"  {call_va:#010x}: CALL {dest_va:#010x}  ; {ann}")
            else:
                print(f"  {call_va:#010x}: CALL {dest_va:#010x}")

    # Find callers of this function
    print("\n" + "=" * 80)
    print(f"CALLERS OF {func_va:#010x}")
    print("=" * 80)

    callers = find_callers(data, func_va)
    if callers:
        for typ, va in callers:
            containing = find_function_start(data, va)
            print(f"  {typ} at {va:#010x} (in function {containing:#010x})" if containing else f"  {typ} at {va:#010x}")
    else:
        print("  No direct callers found!")

        # Search for address in vtable
        target_bytes = struct.pack('<I', func_va)
        for off in range(RDATA_RAW, RDATA_RAW + RDATA_SIZE - 4):
            if data[off:off + 4] == target_bytes:
                va = file_to_va(off)
                print(f"  Found as vtable entry at {va:#010x}")

    # Now let's look at the 0x0a handler code path in detail
    # At 0x1016e64b: cmp eax, 0x0a; je 0x1016e7bb (0x16c offset)
    print("\n" + "=" * 80)
    print("0x0a HANDLER PATH")
    print("=" * 80)

    off_je = va_to_file(0x1016e64f)
    if data[off_je] == 0x0F and data[off_je + 1] == 0x84:
        rel32 = struct.unpack_from('<i', data, off_je + 2)[0]
        target = 0x1016e655 + rel32
        print(f"  je target for 0x0a handler: {target:#010x}")

        # Show the 0x0a handler code
        print(f"\n  Code at 0x0a handler ({target:#010x}):")
        hexdump(data, target, 0x80)

    # And the 0x0b handler
    print("\n" + "=" * 80)
    print("0x0b HANDLER PATH")
    print("=" * 80)

    off_je2 = va_to_file(0x1016e656)
    if data[off_je2] == 0x0F and data[off_je2 + 1] == 0x84:
        rel32 = struct.unpack_from('<i', data, off_je2 + 2)[0]
        target = 0x1016e65c + rel32
        print(f"  je target for 0x0b handler: {target:#010x}")

        print(f"\n  Code at 0x0b handler ({target:#010x}):")
        hexdump(data, target, 0x80)

    # Also check the second dispatch point at 0x1016e90d
    print("\n" + "=" * 80)
    print("SECOND 0x0a DISPATCH AT 0x1016e90d")
    print("=" * 80)
    hexdump(data, 0x1016e900, 0x60)
    off_jne = va_to_file(0x1016e90d)
    print(f"\n  Bytes at 0x1016e90d: {data[off_jne]:02x} {data[off_jne+1]:02x}")
    if data[off_jne] == 0x75:
        rel8 = struct.unpack_from('<b', data, off_jne + 1)[0]
        target = 0x1016e90f + rel8
        print(f"  jne {target:#010x} (if eax != 0x0a, skip to {target:#010x})")
        print(f"  If eax == 0x0a: fall through to handler at 0x1016e90f")
        print(f"\n  0x0a handler code at 0x1016e90f:")
        hexdump(data, 0x1016e90f, 0x30)

    # Understand this function's structure
    print("\n" + "=" * 80)
    print("FUNCTION STRUCTURE ANALYSIS")
    print("=" * 80)
    print("""
Function at 0x1016e580:
  - Prologue: standard MSVC SEH frame
  - At 0x1016e5b9: accesses this->0x68 (mov eax, [edi+0x68])
    - Then accesses [eax+0x34] -> vtable call via [eax+0x1e8]
    - This is different from the Level object (which uses offset 0x6a38)
  - At 0x1016e5da: gets arg from [ebp+0x0c] (2nd arg = blob size?)

  This function accesses 'this' at offset 0x68, 0x158, 0xf8 - different
  from the main blob parser which uses 0x6a38, 0x6a4c, etc.

  It dispatches on section types 0x09, 0x0a, 0x0b which suggests it's
  a SECTION-SPECIFIC parser that handles only grid/pathfinding sections.
  Possibly called from a different context (level editor? server?).

  The dispatch chain at 0x1016e64b:
    cmp eax, 0x0a -> je (handle PTH pathfinding)
    cmp eax, 0x0b -> je (handle RLTD pathfinding)
    cmp eax, 0x09 -> jne (handle grid if == 0x09)

  There's also a SECOND pass at 0x1016e8f0:
    cmp eax, 0x0a -> if equal, handle
    cmp eax, 0x02 -> if equal, handle
""")

    # Check what this function stores for 0x0a
    # Let's look at the je target for 0x0a more carefully
    off_je = va_to_file(0x1016e64f)
    if data[off_je] == 0x0F and data[off_je + 1] == 0x84:
        rel32 = struct.unpack_from('<i', data, off_je + 2)[0]
        target_va = 0x1016e655 + rel32
        print(f"\n0x0a handler at {target_va:#010x}:")
        hexdump(data, target_va, 0x60)

        # Look for calls in the 0x0a handler
        target_off = va_to_file(target_va)
        for off in range(target_off, target_off + 0x60):
            if data[off] == 0xE8:
                rel32 = struct.unpack_from('<i', data, off + 1)[0]
                call_va = file_to_va(off)
                dest_va = call_va + 5 + rel32
                ann = known_funcs.get(dest_va, "")
                print(f"  CALL at {call_va:#010x} -> {dest_va:#010x} {ann}")


if __name__ == '__main__':
    main()
