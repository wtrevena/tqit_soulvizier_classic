"""
Final summary: locate RTTI for both classes and produce a clean picture.
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
DATA_RVA = 0x36e000
DATA_RAW = 0x36c800
DATA_VSIZE = 0xae574


def va_to_file(va):
    rva = va - IMAGE_BASE
    if TEXT_RVA <= rva < TEXT_RVA + TEXT_SIZE:
        return rva - TEXT_RVA + TEXT_RAW
    elif RDATA_RVA <= rva < RDATA_RVA + RDATA_SIZE:
        return rva - RDATA_RVA + RDATA_RAW
    elif DATA_RVA <= rva < DATA_RVA + DATA_VSIZE:
        return rva - DATA_RVA + DATA_RAW
    return None


def file_to_va(off):
    if TEXT_RAW <= off < TEXT_RAW + TEXT_SIZE:
        return IMAGE_BASE + (off - TEXT_RAW + TEXT_RVA)
    elif RDATA_RAW <= off < RDATA_RAW + RDATA_SIZE:
        return IMAGE_BASE + (off - RDATA_RAW + RDATA_RVA)
    elif DATA_RAW <= off < DATA_RAW + DATA_VSIZE:
        return IMAGE_BASE + (off - DATA_RAW + DATA_RVA)
    return None


def read_rtti_name(data, col_va):
    """Follow RTTI Complete Object Locator to get class name."""
    col_off = va_to_file(col_va)
    if col_off is None or col_off + 16 > len(data):
        return None

    # COL structure: signature(4), offset(4), cdOffset(4), typeDescriptorPtr(4), ...
    td_ptr = struct.unpack_from('<I', data, col_off + 12)[0]
    td_off = va_to_file(td_ptr)
    if td_off is None or td_off + 12 > len(data):
        return f"(td_ptr={td_ptr:#010x}, can't resolve)"

    # TypeDescriptor: vtable(4), spare(4), name(...)
    name_off = td_off + 8
    name_bytes = data[name_off:name_off + 300]
    null_idx = name_bytes.find(b'\x00')
    if null_idx >= 0:
        name_bytes = name_bytes[:null_idx]
    return name_bytes.decode('ascii', errors='replace')


def find_vtable_with_function(data, func_va):
    """Find all vtable entries in .rdata that point to func_va."""
    results = []
    target = struct.pack('<I', func_va)
    for off in range(RDATA_RAW, RDATA_RAW + RDATA_SIZE - 4):
        if data[off:off+4] == target:
            results.append(file_to_va(off))
    return results


def main():
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    # The vtable at 0x102f7484 had RTTI=0x00007525 which is bogus.
    # Let's re-examine - MSVC vtables have the RTTI COL pointer at vtable[-1]
    # But the vtable start detection may be off. Let me look more carefully.

    print("=" * 80)
    print("VTABLE AT 0x102f7488 - RTTI INVESTIGATION")
    print("=" * 80)

    # Show raw data around the vtable
    for o in range(va_to_file(0x102f7470), va_to_file(0x102f74f0), 4):
        va = file_to_va(o)
        dword = struct.unpack_from('<I', data, o)[0]
        dword_rva = dword - IMAGE_BASE
        is_text = TEXT_RVA <= dword_rva < TEXT_RVA + TEXT_SIZE
        is_rdata = RDATA_RVA <= dword_rva < RDATA_RVA + RDATA_SIZE
        is_data = DATA_RVA <= dword_rva < DATA_RVA + DATA_VSIZE

        label = ""
        if is_text:
            label = " -> .text"
        elif is_rdata:
            label = " -> .rdata (maybe RTTI COL?)"
            rtti_name = read_rtti_name(data, dword)
            if rtti_name:
                label += f"  [{rtti_name}]"
        elif is_data:
            label = " -> .data"
        elif dword == 0:
            label = " (NULL)"

        if va == 0x102f74c4:
            label += "  <<< blob parser 0x1016e580"

        print(f"  {va:#010x}: {dword:#010x}{label}")

    # Try another approach: search for the real vtable that contains 0x101b3fb0
    # Actually, 0x101b3fb0 isn't virtual, so it won't be in a vtable.
    # But the Level class might have a vtable. Let's find it via the callers.

    # The callers of 0x101b3fb0:
    #   0x101b5fb5 in function 0x101b5f70
    #   0x10209bb9 in function 0x10209b10

    # Let's look at function 0x101b5f70 - is it a virtual method?
    print("\n" + "=" * 80)
    print("CALLER 0x101b5f70 (calls blob dispatcher)")
    print("=" * 80)

    vtable_refs = find_vtable_with_function(data, 0x101b5f70)
    if vtable_refs:
        for vt_va in vtable_refs:
            print(f"  Found 0x101b5f70 in vtable at {vt_va:#010x}")
            # Show vtable context
            vt_off = va_to_file(vt_va)
            for o in range(max(RDATA_RAW, vt_off - 20), min(RDATA_RAW + RDATA_SIZE, vt_off + 40), 4):
                va = file_to_va(o)
                dword = struct.unpack_from('<I', data, o)[0]
                dword_rva = dword - IMAGE_BASE
                label = ""
                if TEXT_RVA <= dword_rva < TEXT_RVA + TEXT_SIZE:
                    label = " -> .text"
                elif RDATA_RVA <= dword_rva < RDATA_RVA + RDATA_SIZE:
                    rtti_name = read_rtti_name(data, dword)
                    if rtti_name:
                        label = f" -> RTTI: {rtti_name}"
                    else:
                        label = " -> .rdata"
                if o == vt_off:
                    label += " <<<"
                print(f"    {va:#010x}: {dword:#010x}{label}")
    else:
        print("  0x101b5f70 NOT found in any vtable (not virtual)")

    # Let's check 0x10209b10 too
    vtable_refs2 = find_vtable_with_function(data, 0x10209b10)
    if vtable_refs2:
        for vt_va in vtable_refs2:
            print(f"\n  Found 0x10209b10 in vtable at {vt_va:#010x}")
    else:
        print("  0x10209b10 NOT found in any vtable")

    # Now produce the definitive summary
    print("\n" + "=" * 100)
    print("DEFINITIVE FINDINGS: LEVEL BLOB SECTION PARSER")
    print("=" * 100)
    print(f"""
1. THE LEVEL BLOB PARSER
   Function: VA 0x101b3fb0
   File offset: 0x1b33b0
   Size: ~1765 bytes (ends at 0x101b4695)

   This is the function that iterates over level blob sections and dispatches
   based on section type. It is NOT a virtual method - it's called directly.

   Format: "LVL" + version_byte (0x0a..0x11) + sections
   Each section: uint32 type + uint32 size + [size] bytes

   SECTION DISPATCH (at 0x101b40c0):
   The section_type is read into EDX, then a chain of cmp/jne checks:

     0x101b40e6: cmp edx, 0x05 -> ENTITIES
                 (stores entity data pointer and size)

     0x101b4114: cmp edx, 0x14 -> METADATA
                 (stores metadata pointer and size)

     0x101b4129: cmp edx, 0x0b -> RLTD PATHFINDING
                 (calls this->rltd_handler->ProcessRLTD() at 0x101f4ba0)
                 (the handler object is at this+0x6a38; if NULL, section is skipped)

     0x101b41a9: cmp edx, 0x06 -> SUB-TYPED SECTION
                 (version-dependent sub-dispatch with 3 variants: sub-type 0,1,2)

     0x101b42fb: cmp edx, 0x09 -> GRID
                 (calls grid loading at 0x101b6000)

     0x101b4325: cmp edx, 0x03 -> TERRAIN
                 (calls 0x1019fa30)

     0x101b4344: cmp edx, 0x17 -> UNKNOWN_17
                 (calls 0x10218800 with this+0x6a4c)

     DEFAULT (0x101b40f7):
       add ecx, esi (cursor += section_size) -> skip section, loop back

   SECTION TYPE 0x0a (PTH PATHFINDING) IS NOT HANDLED.
   It falls through to the default skip path.

2. CALLERS
   0x101b5fb5 (function 0x101b5f70) - non-virtual, direct call
   0x10209bb9 (function 0x10209b10) - non-virtual, direct call

3. THE 0x0b HANDLER IN DETAIL
   When section_type == 0x0b:
     - Saves cursor position and section size to a local struct
     - Reads this->rltd_handler (offset 0x6a38 from this)
     - If handler is NULL, skips the section
     - Otherwise, calls handler->method(struct_ptr)
       which is 0x101f4ba0 (RLTD handler function)
     - This function processes the "REC\\x02" format data

4. THE MSH PARSER (SEPARATE FORMAT)
   A completely different parser at VA 0x1016e580 handles "MSH" format
   (mesh/sector files). It has its own dispatch including 0x0a (PTH)
   and 0x0b (RLTD), but this operates on MESH data, not LEVEL data.

5. VERSION HANDLING
   At 0x101b406b: version_byte - 0x0a is checked against 0..7
   Valid versions: 0x0a (10) through 0x11 (17)
   Version affects the 0x06 sub-type dispatch:
     version < 0x0b: sub-type forced to 0
     version >= 0x0b: sub-type read from stream

6. THE RLTD HANDLER OBJECT (this+0x6a38)
   This is a pointer to an object that processes RLTD pathfinding data.
   Method at 0x101f4ba0 processes blob section data (1 arg: section descriptor)
   Method at 0x101f6210 does post-load entity association (4 args)
   Validator at 0x101002b0 validates RLTD data integrity
""")


if __name__ == '__main__':
    main()
