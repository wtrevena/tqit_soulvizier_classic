"""
Check the interesting location at 0x1016e64b which has both:
  cmp eax, 0x0a  (at 0x1016e64b)
  cmp eax, 0x0b  (right after at 0x1016e656)

This could be a section-type dispatch for 0x0a/0x0b!
Also check 0x1016e90d which has cmp eax, 0x0a in the same function area.
"""

import struct

DLL_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll"
IMAGE_BASE = 0x10000000
TEXT_RVA = 0x001000
TEXT_RAW = 0x000400
TEXT_SIZE = 0x2aa800

def va_to_file(va):
    rva = va - IMAGE_BASE
    return rva - TEXT_RVA + TEXT_RAW

def file_to_va(off):
    rva = off - TEXT_RAW + TEXT_RVA
    return IMAGE_BASE + rva

def find_function_start(data, target_va):
    target_off = va_to_file(target_va)
    for off in range(target_off - 1, max(TEXT_RAW, target_off - 0x2000), -1):
        if data[off] == 0xCC and data[off - 1] == 0xCC:
            return file_to_va(off + 1)
    return None

def hexdump(data, start_va, length):
    start_off = va_to_file(start_va)
    for o in range(start_off, start_off + length, 16):
        va = file_to_va(o)
        chunk = data[o:o+16]
        hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
        ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {va:#010x}: {hex_bytes}  {ascii_chars}")


def main():
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    # The pattern at 0x1016e64b: cmp eax, 0x0a; je ...; cmp eax, 0x0b; je ...
    print("=" * 80)
    print("POTENTIAL 0x0a/0x0b DISPATCH AT 0x1016e64b")
    print("=" * 80)

    func_start = find_function_start(data, 0x1016e64b)
    print(f"  Containing function starts at: {func_start:#010x}")

    # Show extensive context around both comparisons
    print("\nContext around 0x1016e64b (cmp eax, 0x0a; cmp eax, 0x0b):")
    hexdump(data, 0x1016e620, 0x100)

    # Also check at 0x1016e90d
    print("\n\nContext around 0x1016e90d (cmp eax, 0x0a):")
    hexdump(data, 0x1016e8f0, 0x60)

    # Check the function prologue
    if func_start:
        print(f"\nFunction prologue at {func_start:#010x}:")
        hexdump(data, func_start, 0x60)

    # ====================================================================
    # Also, let's look at the error string referenced by the 0x0b handler
    # At 0x101b4161: push 0x102d8d94 then logger call
    # This is a string pointer - let's read it
    print("\n" + "=" * 80)
    print("RLTD ERROR STRING")
    print("=" * 80)
    off = va_to_file(0x102d8d94)
    s = data[off:off+100]
    null_idx = s.find(b'\x00')
    if null_idx >= 0:
        s = s[:null_idx]
    print(f"  String at 0x102d8d94: {s.decode('ascii', errors='replace')}")

    # ====================================================================
    # Now, let's trace 0x1027b1f0 which has cmp edx, 0x0a with jump table
    print("\n" + "=" * 80)
    print("DISPATCH AT 0x1027b1f0 (cmp edx, 0x0a with jump table)")
    print("=" * 80)
    func_start2 = find_function_start(data, 0x1027b1f0)
    print(f"  Containing function starts at: {func_start2:#010x}")
    hexdump(data, 0x1027b1d0, 0x60)

    # ====================================================================
    # Let's also look at what calls 0x101b6000 (the grid handler called for type 0x09)
    # since it's in the same function
    print("\n" + "=" * 80)
    print("GRID HANDLER AT 0x101b6000")
    print("=" * 80)

    grid_func_start = find_function_start(data, 0x101b6000)
    print(f"  0x101b6000 is at function start: {grid_func_start:#010x}")
    hexdump(data, 0x101b6000, 0x40)

    # Does the grid handler (0x101b6000) internally handle 0x0a?
    # Search for 0x0a comparison within that function
    grid_off = va_to_file(0x101b6000)
    grid_end = grid_off + 0x1000  # search up to 4KB
    for off in range(grid_off, min(grid_end, TEXT_RAW + TEXT_SIZE - 3)):
        if data[off] == 0xCC and off + 1 < len(data) and data[off+1] == 0xCC:
            break
        if data[off] == 0x83 and data[off+1] in (0xF8, 0xFA, 0xF9) and data[off+2] == 0x0A:
            va = file_to_va(off)
            reg = {0xF8: 'eax', 0xFA: 'edx', 0xF9: 'ecx'}[data[off+1]]
            print(f"  Found: {va:#010x}: cmp {reg}, 0x0a")

    # ====================================================================
    # Search specifically for "PTH" string references in code
    print("\n" + "=" * 80)
    print("PTH STRING REFERENCES (pathfinding format)")
    print("=" * 80)

    # "PTH" at 0x102df160 area (from user info)
    # Search .rdata for "PTH"
    pth_bytes = b'PTH'
    for off in range(va_to_file(0x102ac000), va_to_file(0x102ac000) + RDATA_SIZE - 4):
        if data[off:off+3] == pth_bytes:
            va = file_to_va(off)
            ctx = data[off:off+20]
            print(f"  {va:#010x}: {ctx.hex(' ')} = {ctx.rstrip(b'\\x00')}")

    # Also search for "tok" string (PathEngine token mesh)
    print("\n  'tok' strings:")
    tok_bytes = b'tok'
    for off in range(va_to_file(0x102ac000), va_to_file(0x102ac000) + RDATA_SIZE - 4):
        if data[off:off+3] == tok_bytes and (off == 0 or data[off-1] == 0):
            va = file_to_va(off)
            ctx = data[off:off+20]
            print(f"  {va:#010x}: {ctx.hex(' ')} = {ctx}")

    # ====================================================================
    # FINAL: Summarize the complete picture
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print("""
THE LEVEL BLOB SECTION PARSER IS AT VA 0x101b3fb0.

Function signature (thiscall):
  bool Level::LoadFromBlob(void* blob_data, int blob_size, ???)

Arguments:
  this = Level object (ECX -> saved to EDI)
  arg1 (ebp+8) = pointer to blob data
  arg2 (ebp+0xc) = blob data size

Key object fields:
  this+0x6a38 = RLTD pathfinding handler object (can be NULL)
  this+0x6a8c = related pathfinding data
  this+0x04   = some pointer used in various handlers
  this+0x08   = grid? data pointer
  this+0x0c   = entity data
  this+0x10   = entity data ptr
  this+0x6a4c = another structure (used with type 0x17)

LVL Format:
  Bytes 0-2: "LVL" magic
  Byte 3:   version (valid range: 0x0a = 10 through 0x11 = 17)
  Then sections, each:
    uint32 type
    uint32 size
    [size] bytes of data

Section type dispatch (0x101b40c0):
  0x03 -> Terrain handler (calls 0x1019fa30)
  0x05 -> Entity data (stores pointer + size for later processing)
  0x06 -> Sub-typed section (version-dependent, 3 variants)
  0x09 -> Grid handler (calls 0x101b6000)
  0x0b -> RLTD/REC pathfinding (calls handler at this+0x6a38 -> 0x101f4ba0)
  0x14 -> Metadata (stores pointer + size)
  0x17 -> Unknown handler (calls 0x10218800 with this+0x6a4c)
  0x0a -> *** SILENTLY SKIPPED *** (no handler, default path advances cursor)
  other -> Silently skipped

Callers:
  0x101b5f70::0x101b5fb5 -> calls LoadFromBlob
  0x10209b10::0x10209bb9 -> calls LoadFromBlob

THE 0x0a (PTH) SECTION TYPE HAS NO HANDLER IN TQAE.
Section type 0x0a data (PTH pathfinding) is present in level files
but the engine silently skips it during blob parsing.
Only 0x0b (RLTD/REC) pathfinding data is actually processed.
""")


if __name__ == '__main__':
    main()
