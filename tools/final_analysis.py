"""
Final analysis: verify the complete dispatch chain and understand how
Func2 is reached (since it has no direct callers and no vtable entry).
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

    # 1. Check what's at 0x101b4325 (jne target after cmp edx, 0x09)
    print("=" * 80)
    print("AREA AT 0x101b4325 (after cmp edx, 0x09 handler)")
    print("=" * 80)
    hexdump(data, 0x101b4320, 0x40)

    off = va_to_file(0x101b4325)
    print(f"\n  Bytes at 0x101b4325: {data[off]:02x} {data[off+1]:02x} {data[off+2]:02x}")
    if data[off] == 0x83 and data[off+1] == 0xFA:
        imm = data[off+2]
        print(f"  -> cmp edx, {imm:#x}")

    # 2. Trace version sub-dispatch in type 0x06 handler more carefully
    print("\n" + "=" * 80)
    print("TYPE 0x06 VERSION SUB-DISPATCH (0x101b41a9)")
    print("=" * 80)

    # At 0x101b41a9: cmp edx, 0x06; jne 0x101b42fb
    # If type == 6:
    # 0x101b41b1: 8a 5c 24 13 -> mov bl, [esp+0x13] (version byte stored earlier)
    # 0x101b41b5: 80 fb 0b    -> cmp bl, 0x0b
    # 0x101b41b8: 7d 04       -> jge (if version >= 0x0b)
    # 0x101b41ba: 33 c0       -> xor eax, eax (version < 0x0b => eax = 0)
    # 0x101b41bc: eb 09       -> jmp past
    # 0x101b41be: 8b 01       -> mov eax, [ecx] (version >= 0x0b => read dword from data)
    # 0x101b41c0: 83 c1 04    -> add ecx, 4
    # Then: sub eax, 0; je ...; dec eax; je ...; dec eax; jne ...
    # This is a 3-way switch on a sub-type value (0, 1, 2)

    hexdump(data, 0x101b41af, 0xC0)

    print("\nDecoding type 0x06 handler:")
    print("  0x101b41b1: mov bl, [esp+0x13]    ; bl = version byte")
    print("  0x101b41b5: cmp bl, 0x0b")
    print("  0x101b41b8: jge +4                 ; if version >= 0x0b, read sub-type")
    print("  0x101b41ba: xor eax, eax           ; else sub-type = 0")
    print("  0x101b41bc: jmp +9")
    print("  0x101b41be: mov eax, [ecx]         ; read sub-type dword from stream")
    print("  0x101b41c0: add ecx, 4             ; advance cursor")
    print("  0x101b41c5: sub eax, 0             ; test sub-type == 0?")
    print("  0x101b41c8: je ...                 ; handle sub-type 0 (old format)")
    print("  0x101b41cd: dec eax                ; sub-type == 1?")
    print("  0x101b41ce: je ...                 ; handle sub-type 1")
    print("  0x101b41d3: dec eax                ; sub-type == 2?")
    print("  0x101b41d4: jne ...                ; if not 0/1/2, skip")
    print("  Then three different allocation sizes: 0xb8, 0xd4, and another")

    # 3. Now the big question: how is Func2 (0x101b1d00) reached?
    # It's not in any vtable, not called directly.
    # Could it be reached via a register-indirect call? Let's search for
    # patterns that load its address.
    print("\n" + "=" * 80)
    print("SEARCHING FOR HOW FUNC2 (0x101b1d00) IS REACHED")
    print("=" * 80)

    # Check if it's right after Func1's callers
    # Func1 caller: 0x101b5fb5 in function 0x101b5f70
    # Another caller: 0x10209bb9 in function 0x10209b10
    # Func2 starts at 0x101b1d00

    # Maybe Func2 is a different code path in the same class.
    # Let's check: Func1's `this` is at edi (mov edi, ecx at 0x101b3ff0)
    # Func1 accesses this->0x6a38 at 0x101b4149: 8b 87 38 6a 00 00 (mov eax, [edi+0x6a38])
    # Func2's `this` is at ebx (mov ebx, ecx at 0x101b1d33)
    # Func2 accesses this->0x6a38 at 0x101b1d39: 8b b3 38 6a 00 00 (mov esi, [ebx+0x6a38])

    # Same `this` type! Both access this->0x6a38
    # Func2 is probably a virtual method called through a vtable.
    # OR it could be called via a member function pointer.

    # Let's search ALL of .text + .rdata for the bytes 00 1d 1b 10 (little-endian 0x101b1d00)
    target_le = struct.pack('<I', 0x101b1d00)
    print(f"\n  Searching all sections for {target_le.hex(' ')}...")

    for off in range(0, len(data) - 4):
        if data[off:off+4] == target_le:
            # Determine section
            if TEXT_RAW <= off < TEXT_RAW + TEXT_SIZE:
                va = file_to_va(off)
                section = ".text"
            elif RDATA_RAW <= off < RDATA_RAW + RDATA_SIZE:
                va = file_to_va(off)
                section = ".rdata"
            else:
                va = off  # raw offset
                section = "other"
            print(f"  Found at file offset {off:#x} (VA {va:#010x} if applicable) in {section}")
            # Show context
            ctx_start = max(0, off - 8)
            ctx = data[ctx_start:off+12]
            print(f"    Context: {ctx.hex(' ')}")

    # Let's also check other sections (PE header shows more sections)
    # First, let me check the section table
    print("\n  Checking PE sections...")
    pe_sig_off = struct.unpack_from('<I', data, 0x3C)[0]
    num_sections = struct.unpack_from('<H', data, pe_sig_off + 6)[0]
    opt_header_size = struct.unpack_from('<H', data, pe_sig_off + 0x14)[0]
    section_table_off = pe_sig_off + 0x18 + opt_header_size

    for i in range(num_sections):
        sec_off = section_table_off + i * 40
        name = data[sec_off:sec_off+8].rstrip(b'\x00').decode('ascii', errors='replace')
        vsize = struct.unpack_from('<I', data, sec_off + 8)[0]
        vrva = struct.unpack_from('<I', data, sec_off + 12)[0]
        raw_size = struct.unpack_from('<I', data, sec_off + 16)[0]
        raw_off = struct.unpack_from('<I', data, sec_off + 20)[0]
        chars = struct.unpack_from('<I', data, sec_off + 36)[0]
        print(f"    {name:8s} RVA={vrva:#010x} VSize={vsize:#010x} Raw={raw_off:#010x} RSize={raw_size:#010x} Chars={chars:#010x}")

    # 4. Understand the 0x0b handler in Func1 in detail
    print("\n" + "=" * 80)
    print("0x0b HANDLER DETAILED FLOW")
    print("=" * 80)

    # After cmp edx, 0x0b; jne 0x101b41a9 (if not 0x0b, skip to type 0x06 check)
    # If type IS 0x0b:
    # 0x101b412e: 89 4c 24 38 -> mov [esp+0x38], ecx   (save cursor)
    # 0x101b4132: 89 74 24 40 -> mov [esp+0x40], esi   (save section_size)
    # 0x101b4136: c6 44 24 44 00 -> mov byte [esp+0x44], 0   (clear flag)
    # 0x101b413b: 89 4c 24 3c -> mov [esp+0x3c], ecx   (save cursor again)
    # 0x101b413f: c6 84 24 a8 01 00 00 02 -> mov byte [esp+0x1a8], 2  (state=2)
    # 0x101b4147: 8b 87 38 6a 00 00 -> mov eax, [edi+0x6a38]  (this->rltd_handler?)
    # 0x101b414d: 85 c0 -> test eax, eax
    # 0x101b414f: 74 29 -> je +0x29  (if handler is null, skip RLTD processing)
    # 0x101b4151: 8d 4c 24 38 -> lea ecx, [esp+0x38]  (ptr to {cursor, size, flag, cursor2})
    # 0x101b4155: 51 -> push ecx  (push struct ptr)
    # 0x101b4156: 8b c8 -> mov ecx, eax  (this = rltd_handler from edi+0x6a38)
    # 0x101b4158: e8 43 0a 04 00 -> CALL 0x101f4ba0  (call RLTD handler)
    # 0x101b415d: 84 c0 -> test al, al  (check return value)
    # 0x101b415f: 75 15 -> jne +0x15  (if success, skip error log)
    # If failed (al==0):
    # 0x101b4161: log error "RLTD processing failed"
    # After handler:
    # 0x101b4176: 8b 4c 24 18 -> mov ecx, [esp+0x18]  (restore cursor)
    # 0x101b417a: 03 ce -> add ecx, esi  (advance by section_size)
    # ... then loop back

    print("  0x101b412e: save cursor and section_size to local struct")
    print("  0x101b4147: eax = this->rltd_handler (offset 0x6a38)")
    print("  0x101b414d: test eax, eax")
    print("  0x101b414f: je skip_rltd  (if no RLTD handler object, skip)")
    print("  0x101b4151: lea ecx, [local_struct]")
    print("  0x101b4155: push ecx (section data descriptor)")
    print("  0x101b4156: mov ecx, eax (this = rltd_handler)")
    print("  0x101b4158: CALL 0x101f4ba0 (RLTD handler method)")
    print("  0x101b415d: test al, al (check success)")
    print("  0x101b415f: jne ok")
    print("  0x101b4161: LOG_ERROR (RLTD processing failed)")
    print("  ok: advance cursor by section_size, loop back")

    print("\n  KEY INSIGHT: The rltd_handler object at this->0x6a38 is")
    print("  the object whose method processes 0x0b (RLTD) data.")
    print("  If this->0x6a38 is NULL, the 0x0b section is silently skipped.")

    # 5. Verify the complete dispatch chain with fall-through behavior
    print("\n" + "=" * 80)
    print("COMPLETE DISPATCH CHAIN SUMMARY")
    print("=" * 80)

    print("""
Function: 0x101b3fb0 (Level::LoadFromBlob or similar)
  Signature: bool __thiscall func(void* data, int size, ???)

  PROLOGUE:
    0x101b4020: Read first 3 bytes as "LV" + check byte
    0x101b4039: cmp [local], "LV"   ; check magic bytes 'L','V'
    0x101b4048: cmp byte, 'L'       ; check 3rd byte is 'L' (completing "LVL")
    0x101b4052: Read version byte (4th byte) into BL
    0x101b406b: sub al, 0x0a        ; version -= 10
    0x101b4075: cmp al, 7           ; if version > 17, error
    0x101b4077: ja error_path       ; valid versions: 10..17 (0x0a..0x11)

  SECTION LOOP (starts at 0x101b40c0):
    ecx = cursor pointer into blob data
    Read uint32 section_type -> edx
    Read uint32 section_size -> esi

    Check section_size <= remaining data:
    0x101b40e0: jb error (section exceeds blob bounds)

    DISPATCH on edx (section_type):
      0x05 (ENTITIES):
        Store entity data pointer and size. Advance cursor. Loop back.

      0x14 (METADATA):
        Store metadata pointer and size. Advance cursor. Loop back.

      0x0b (RLTD PATHFINDING):
        If this->rltd_handler (offset 0x6a38) is non-null:
          Call rltd_handler->method(section_data_descriptor)
          => Calls 0x101f4ba0 which processes RLTD/REC data
        Advance cursor. Loop back.

      0x06 (SUB-TYPED SECTION):
        If version >= 0x0b (11): read sub-type dword
        Else: sub-type = 0
        Switch on sub-type (0, 1, 2):
          Allocates different sized objects (0xb8, 0xd4, ...)
          Processes section data

      0x09 (GRID):
        Calls grid loading function (0x101b6000)

      0x03 (TERRAIN?):
        Calls 0x1019fa30

      0x17 (UNKNOWN):
        Calls 0x10218800

      DEFAULT (including 0x0a!):
        Advance cursor by section_size (skip). Loop back.
        At 0x101b40f7: add ecx, esi (cursor += section_size)
        This is the skip path - reached by all unrecognized section types.

    0x0a (PTH PATHFINDING) IS SILENTLY SKIPPED!
    There is NO handler for section type 0x0a in this function.

  POST-LOOP (at 0x101b43b4):
    Sets up level grid, pathfinding, entity processing
    Calls various initialization functions
""")

    # 6. Now check: does Func2 share the SAME handler object access pattern?
    # Func2 at 0x101b1d00: accesses this->0x6a38, then calls 0x101f6210 (RLTD handler #2)
    # Func2 call to 0x101f6210 is at 0x101b221a:
    # Let's check what 'this' is used for that call

    print("\n" + "=" * 80)
    print("FUNC2 RLTD CALL CONTEXT")
    print("=" * 80)
    hexdump(data, 0x101b21f0, 0x40)
    print()
    print("  0x101b21fc: 8b 8a 38 6a 00 00 -> mov ecx, [edx+0x6a38]")
    print("  0x101b2202: 85 c9 -> test ecx, ecx")
    print("  0x101b2204: 74 1f -> je skip_rltd2")
    print("  0x101b2206: 8d 44 24 18 -> lea eax, [esp+0x18]")
    print("  0x101b220a: 50 -> push eax")
    print("  0x101b220b: 8d 44 24 50 -> lea eax, [esp+0x50]")
    print("  0x101b220f: 50 -> push eax")
    print("  0x101b2210: 8d 82 8c 6a 00 00 -> lea eax, [edx+0x6a8c]")
    print("  0x101b2216: 50 -> push eax")
    print("  0x101b2217: 56 -> push esi")
    print("  0x101b2218: e8 ... -> CALL 0x101f6210 (RLTD handler #2)")
    print()
    print("  Func2 also uses this->0x6a38 as the RLTD handler!")
    print("  And this->0x6a8c as another related data structure.")
    print("  Func2 passes 4 args to RLTD handler #2 (vs 1 arg for handler #1).")

    # 7. Let's check Func2 more carefully - it does NOT parse the LVL blob format.
    # It seems to be a POST-PROCESSING function, not a blob parser.
    # Let's look at what it does at the start.

    print("\n" + "=" * 80)
    print("FUNC2 PURPOSE ANALYSIS")
    print("=" * 80)
    hexdump(data, 0x101b1d00, 0x80)
    print()
    print("  Func2 at 0x101b1d00 does NOT read LVL magic or section types.")
    print("  It appears to be a post-load processing function that:")
    print("  - Accesses this->0x6a38 (RLTD handler) at the start")
    print("  - If it exists, calls cleanup/initialization")
    print("  - Calls 0x101ad8d0 to get level bounds/grid info")
    print("  - Then iterates over entities (loop at 0x101b1f30)")
    print("  - For each entity, does visibility/pathfinding setup")
    print("  - Calls RLTD handler #2 (0x101f6210) for RLTD data association")
    print()
    print("  Func2 is NOT a blob parser - it's a post-processing step.")
    print("  It processes already-parsed RLTD data to set up runtime structures.")

    # 8. Final: search for 0x0a as a DWORD comparison anywhere near pathfinding
    print("\n" + "=" * 80)
    print("SEARCHING FOR ANY 0x0a SECTION TYPE HANDLER IN ENTIRE .text")
    print("=" * 80)

    # Search for the pattern: cmp edx, 0x0a (83 FA 0A)
    count = 0
    for off in range(TEXT_RAW, TEXT_RAW + TEXT_SIZE - 3):
        if data[off] == 0x83 and data[off+1] == 0xFA and data[off+2] == 0x0A:
            va = file_to_va(off)
            # Show wider context
            ctx_start = max(TEXT_RAW, off - 16)
            ctx = data[ctx_start:off+16]
            print(f"  {va:#010x}: cmp edx, 0x0a")
            print(f"    Context: {' '.join(f'{b:02x}' for b in ctx)}")
            count += 1

    # Also check cmp eax, 0x0a (83 F8 0A)
    for off in range(TEXT_RAW, TEXT_RAW + TEXT_SIZE - 3):
        if data[off] == 0x83 and data[off+1] == 0xF8 and data[off+2] == 0x0A:
            va = file_to_va(off)
            ctx = data[max(TEXT_RAW,off-8):off+16]
            print(f"  {va:#010x}: cmp eax, 0x0a")
            print(f"    Context: {' '.join(f'{b:02x}' for b in ctx)}")
            count += 1

    # Check cmp ecx, 0x0a (83 F9 0A)
    for off in range(TEXT_RAW, TEXT_RAW + TEXT_SIZE - 3):
        if data[off] == 0x83 and data[off+1] == 0xF9 and data[off+2] == 0x0A:
            va = file_to_va(off)
            ctx = data[max(TEXT_RAW,off-8):off+16]
            print(f"  {va:#010x}: cmp ecx, 0x0a")
            print(f"    Context: {' '.join(f'{b:02x}' for b in ctx)}")
            count += 1

    print(f"\n  Total 'cmp reg, 0x0a' instructions found: {count}")
    print("  (Many will be unrelated to level blob parsing)")


if __name__ == '__main__':
    main()
