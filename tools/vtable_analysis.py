"""
Analyze the vtable containing the second blob parser (0x1016e580)
and understand the class hierarchy.
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


def main():
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    # Vtable entry for 0x1016e580 found at 0x102f74c4
    vtable_entry_va = 0x102f74c4
    vtable_entry_off = va_to_file(vtable_entry_va)

    print("=" * 80)
    print("VTABLE CONTAINING 0x1016e580")
    print("=" * 80)

    # Scan backwards to find vtable start (first entry that's NOT a .text pointer)
    # Vtables in MSVC usually start right after a RTTI pointer or at a boundary
    scan_start = max(RDATA_RAW, vtable_entry_off - 256)
    vtable_start_off = vtable_entry_off

    for off in range(vtable_entry_off - 4, scan_start, -4):
        dword = struct.unpack_from('<I', data, off)[0]
        dword_rva = dword - IMAGE_BASE
        if TEXT_RVA <= dword_rva < TEXT_RVA + TEXT_SIZE:
            vtable_start_off = off
        else:
            # This could be the RTTI pointer or end of previous vtable
            # Check if it looks like an RTTI pointer (.rdata address)
            if RDATA_RVA <= dword_rva < RDATA_RVA + RDATA_SIZE:
                # Could be RTTI - vtable starts at next dword
                vtable_start_off = off + 4
            break

    vtable_start_va = file_to_va(vtable_start_off)
    print(f"  Vtable start: {vtable_start_va:#010x}")

    # RTTI pointer is at vtable_start - 4
    rtti_off = vtable_start_off - 4
    rtti_ptr = struct.unpack_from('<I', data, rtti_off)[0]
    print(f"  RTTI pointer at {file_to_va(rtti_off):#010x}: {rtti_ptr:#010x}")

    # Try to follow RTTI to get class name
    rtti_rva = rtti_ptr - IMAGE_BASE
    if RDATA_RVA <= rtti_rva < RDATA_RVA + RDATA_SIZE:
        rtti_file_off = rtti_rva - RDATA_RVA + RDATA_RAW
        # RTTI Complete Object Locator points to TypeDescriptor
        # At offset +12 in COL is the TypeDescriptor pointer
        type_desc_ptr = struct.unpack_from('<I', data, rtti_file_off + 12)[0]
        print(f"  Type descriptor ptr: {type_desc_ptr:#010x}")

        type_desc_rva = type_desc_ptr - IMAGE_BASE
        # Check .data section too
        data_rva = 0x36e000
        data_raw = 0x36c800
        data_vsize = 0xae574

        if RDATA_RVA <= type_desc_rva < RDATA_RVA + RDATA_SIZE:
            td_off = type_desc_rva - RDATA_RVA + RDATA_RAW
        elif data_rva <= type_desc_rva < data_rva + data_vsize:
            td_off = type_desc_rva - data_rva + data_raw
        else:
            td_off = None

        if td_off and td_off + 20 < len(data):
            # TypeDescriptor: vtable_ptr(4) + spare(4) + name (mangled)
            name_start = td_off + 8
            name_bytes = data[name_start:name_start + 200]
            null_idx = name_bytes.find(b'\x00')
            if null_idx >= 0:
                name_bytes = name_bytes[:null_idx]
            class_name = name_bytes.decode('ascii', errors='replace')
            print(f"  Class name (mangled): {class_name}")

    # Show all vtable entries
    print(f"\n  Vtable entries:")
    idx = 0
    for off in range(vtable_start_off, vtable_start_off + 256, 4):
        dword = struct.unpack_from('<I', data, off)[0]
        dword_rva = dword - IMAGE_BASE
        va = file_to_va(off)
        if TEXT_RVA <= dword_rva < TEXT_RVA + TEXT_SIZE:
            marker = " <<<" if dword == 0x1016e580 else ""
            known = ""
            if dword == 0x1016e580:
                known = " (BLOB PARSER WITH 0x0a SUPPORT)"
            print(f"    [{idx:2d}] {va:#010x}: {dword:#010x} -> .text{marker}{known}")
            idx += 1
        else:
            # End of vtable
            print(f"    --- End of vtable (non-.text entry: {dword:#010x})")
            break

    # Now let's look at what the "MSH" magic is
    # At 0x1016e600: cmp [local], "MS" then check for 'H'
    print("\n" + "=" * 80)
    print("MAGIC CHECK IN SECOND PARSER")
    print("=" * 80)
    print("  At 0x1016e600-0x1016e61e:")
    print("    66 81 3a 4d 53  -> cmp word [edx], 'MS' (0x534d)")
    print("    then:")
    print("    80 7a 02 48     -> cmp byte [edx+2], 'H' (0x48)")
    print()
    print("  Magic bytes: 'MSH' (not 'LVL'!)")
    print("  This is a MESH/SECTOR parser, not a Level parser!")
    print("  Section types in .MSH files overlap with .LVL section types.")

    # Show bytes around the magic check
    off = va_to_file(0x1016e5f8)
    ctx = data[off:off+32]
    print(f"\n  Bytes: {ctx.hex(' ')}")

    # Decode: the first 2 bytes are checked against "MS", then byte 2 against "H"
    # MSH = MeSH format

    # Now let's understand the relationship between the two parsers
    print("\n" + "=" * 80)
    print("RELATIONSHIP BETWEEN THE TWO PARSERS")
    print("=" * 80)
    print("""
PARSER 1: VA 0x101b3fb0 ("LVL" format)
  - Direct function call (not virtual)
  - Called from 0x101b5f70 and 0x10209b10
  - Checks "LVL" magic
  - Handles section types: 0x03, 0x05, 0x06, 0x09, 0x0b, 0x14, 0x17
  - Skips 0x0a (PTH pathfinding)
  - this->0x6a38 = RLTD handler object
  - Level::LoadFromBlob()

PARSER 2: VA 0x1016e580 ("MSH" format)
  - Virtual function (vtable at 0x102f74c4)
  - Checks "MSH" magic
  - Handles ALL section types: 0x00-0x0d + more
    - 0x09 -> Grid
    - 0x0a -> PTH pathfinding (calls 0x1016e3f0)
    - 0x0b -> RLTD pathfinding (calls 0x1016cd90)
    - 0x02, 0x04, 0x05, 0x06, 0x07, 0x08, 0x0c, 0x0d
  - this->0x68 = some object
  - this->0xf8, 0x158, etc. different layout
  - Sector/Mesh::LoadFromBlob()

These are DIFFERENT file formats with overlapping section type IDs:
  - LVL files use section types 0x03-0x17 for level-wide data
  - MSH files use section types 0x00-0x0d for mesh/sector data

The PTH (0x0a) section type exists in MSH files and IS handled.
In LVL files, type 0x0a is skipped - PTH data is NOT in level blobs,
or if it is, it's legacy data that TQAE doesn't use.

CONCLUSION: The LVL-format blob parser at 0x101b3fb0 is the one
that decides between 0x0a (skip) and 0x0b (process) pathfinding.
The engine ONLY processes RLTD (0x0b) pathfinding from level blobs.
PTH pathfinding (0x0a) may be handled in mesh/sector files instead.
""")

    # Double-check: what calls the 0x0a handler (0x1016e3f0) in the MSH parser?
    print("=" * 80)
    print("0x0a PTH HANDLER IN MSH PARSER")
    print("=" * 80)
    print("  The 0x0a handler calls 0x1016e3f0. Let's check what that function does.")

    func_off = va_to_file(0x1016e3f0)
    print(f"\n  Function at 0x1016e3f0:")
    for o in range(func_off, func_off + 0x80, 16):
        va = file_to_va(o)
        chunk = data[o:o+16]
        hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
        ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"    {va:#010x}: {hex_bytes}  {ascii_chars}")

    # Check if it calls any PathEngine-related functions
    for off in range(func_off, func_off + 0x200):
        if data[off] == 0xE8:
            rel32 = struct.unpack_from('<i', data, off + 1)[0]
            call_va = file_to_va(off)
            dest_va = call_va + 5 + rel32
            print(f"    CALL at {call_va:#010x} -> {dest_va:#010x}")

    # Also check 0x1016cd90 (0x0b handler in MSH parser)
    print(f"\n  0x0b handler function at 0x1016cd90:")
    func_off2 = va_to_file(0x1016cd90)
    for o in range(func_off2, func_off2 + 0x40, 16):
        va = file_to_va(o)
        chunk = data[o:o+16]
        hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
        ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"    {va:#010x}: {hex_bytes}  {ascii_chars}")


if __name__ == '__main__':
    main()
