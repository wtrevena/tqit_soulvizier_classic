"""
Trace the detailed control flow of the section dispatch loop in Func1 (0x101b3fb0).

Key addresses from previous analysis:
  Loop top: 0x101b40c0 (reads section_type into EDX, section_size into ESI)
  Section checks:
    0x101b40e6: cmp edx, 0x05  (ENTITIES)
    0x101b4114: cmp edx, 0x14  (METADATA)
    0x101b4129: cmp edx, 0x0b  (RLTD)
    0x101b41a9: cmp edx, 0x06  (sub-dispatch on version)
    0x101b42fb: cmp edx, 0x09  (GRID)
    0x101b4329: cmp edx, 0x03? (check nearby)
    0x101b4344: cmp edx, 0x17

  Default path (unknown types): jne -> 0x101b40f7

Also: Find the vtable/indirect caller of Func2 (0x101b1d00).
Func2 has this->offset 0x6a38 access pattern, suggesting it's a method.
Let's search for its address as a dword in .rdata (vtable entry).
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


def hexdump_range(data, start_va, length):
    """Hex dump from VA."""
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

    # ===== 1. Trace the default/skip path at 0x101b40f7 =====
    print("=" * 80)
    print("DEFAULT PATH: What happens at 0x101b40f7 (jne target for unknown section types)")
    print("=" * 80)

    # The jne after cmp edx, 0x17 goes to 0x101b40f7
    # Let's see what's there
    hexdump_range(data, 0x101b40e0, 0x40)

    print("\nDetailed analysis of the dispatch chain:")
    print()

    # Let's trace each comparison and its branch target
    dispatch_checks = [
        (0x101b40e6, "83 fa 05", "cmp edx, 0x05 (ENTITIES)"),
        (0x101b40e9, None, "branch if edx==5"),
        (0x101b4114, "83 fa 14", "cmp edx, 0x14 (METADATA)"),
        (0x101b4129, "83 fa 0b", "cmp edx, 0x0b (RLTD PATHFINDING)"),
        (0x101b41a9, "83 fa 06", "cmp edx, 0x06"),
        (0x101b42fb, "83 fa 09", "cmp edx, 0x09 (GRID)"),
        (0x101b4344, "83 fa 17", "cmp edx, 0x17"),
    ]

    for check_va, expected_bytes, desc in dispatch_checks:
        off = va_to_file(check_va)
        # Show the instruction and the branch after it
        # After cmp edx, imm8 (3 bytes), there should be a jne or je
        raw = data[off:off+12]
        print(f"  {check_va:#010x}: {' '.join(f'{b:02x}' for b in raw[:3])}  {desc}")

        # Check what follows
        branch_off = off + 3
        b1 = data[branch_off]
        if b1 == 0x75:  # jne rel8
            rel8 = struct.unpack_from('<b', data, branch_off + 1)[0]
            target = file_to_va(branch_off + 2) + rel8
            print(f"  {file_to_va(branch_off):#010x}: 75 {data[branch_off+1]:02x}       jne {target:#010x} (skip to next check)")
        elif b1 == 0x0F and data[branch_off+1] == 0x85:  # jne rel32
            rel32 = struct.unpack_from('<i', data, branch_off + 2)[0]
            target = file_to_va(branch_off + 6) + rel32
            print(f"  {file_to_va(branch_off):#010x}: 0f 85 ...  jne {target:#010x} (skip to next check)")
        elif b1 == 0x0F and data[branch_off+1] == 0x84:  # je rel32
            rel32 = struct.unpack_from('<i', data, branch_off + 2)[0]
            target = file_to_va(branch_off + 6) + rel32
            print(f"  {file_to_va(branch_off):#010x}: 0f 84 ...  je {target:#010x} (handle this type)")
        print()

    # ===== 2. What's at 0x101b40f7? The loop advance. =====
    print("\n" + "=" * 80)
    print("LOOP ADVANCE at 0x101b40f7")
    print("=" * 80)
    hexdump_range(data, 0x101b40f0, 0x30)

    # At 0x101b40f7: this is inside the entities handler (after cmp edx, 5; je)
    # Let me re-examine. The jne after cmp 0x17 goes to 0x101b40f7.
    # But 0x101b40f7 is between the entities block and the metadata check.
    # Let's look more carefully at the flow:

    print("\n" + "=" * 80)
    print("DETAILED BYTE-BY-BYTE AROUND SECTION LOOP (0x101b40c0 - 0x101b4130)")
    print("=" * 80)

    # Full raw dump
    hexdump_range(data, 0x101b40c0, 0x180)

    # ===== 3. Search for Func2 VA (0x101b1d00) as a dword in .rdata (vtable) =====
    print("\n" + "=" * 80)
    print("SEARCHING FOR FUNC2 (0x101b1d00) AS VTABLE ENTRY")
    print("=" * 80)

    target_bytes = struct.pack('<I', 0x101b1d00)
    found = []
    for off in range(RDATA_RAW, RDATA_RAW + RDATA_SIZE - 4):
        if data[off:off+4] == target_bytes:
            va = file_to_va(off)
            found.append((off, va))

    if found:
        for off, va in found:
            print(f"\n  Found at file offset {off:#x}, VA {va:#010x}")
            # Show surrounding vtable entries
            start = max(RDATA_RAW, off - 32)
            end = min(RDATA_RAW + RDATA_SIZE, off + 64)
            for o in range(start, end, 4):
                v = file_to_va(o)
                dword = struct.unpack_from('<I', data, o)[0]
                marker = " <<<" if o == off else ""
                # Check if the dword points into .text
                dword_rva = dword - IMAGE_BASE
                if TEXT_RVA <= dword_rva < TEXT_RVA + TEXT_SIZE:
                    print(f"    {v:#010x}: {dword:#010x} -> .text (function ptr){marker}")
                else:
                    print(f"    {v:#010x}: {dword:#010x}{marker}")
    else:
        print("  NOT found in .rdata! Checking .text for indirect references...")

        # Search in .text for LEA/MOV with the VA
        for off in range(TEXT_RAW, TEXT_RAW + TEXT_SIZE - 4):
            if data[off:off+4] == target_bytes:
                va = file_to_va(off)
                # Check preceding byte for context
                prev = data[off-1] if off > 0 else 0
                print(f"  Found bytes at VA {va:#010x}, preceding byte: {prev:02x}")

    # Also search for Func1 VA in vtable
    print("\n  Also searching for Func1 (0x101b3fb0) as vtable entry:")
    target_bytes1 = struct.pack('<I', 0x101b3fb0)
    for off in range(RDATA_RAW, RDATA_RAW + RDATA_SIZE - 4):
        if data[off:off+4] == target_bytes1:
            va = file_to_va(off)
            print(f"    Found at VA {va:#010x}")
            # Show context
            for o in range(max(RDATA_RAW, off - 16), min(RDATA_RAW + RDATA_SIZE, off + 32), 4):
                v = file_to_va(o)
                dword = struct.unpack_from('<I', data, o)[0]
                marker = " <<<" if o == off else ""
                dword_rva = dword - IMAGE_BASE
                if TEXT_RVA <= dword_rva < TEXT_RVA + TEXT_SIZE:
                    print(f"      {v:#010x}: {dword:#010x} -> .text{marker}")
                else:
                    print(f"      {v:#010x}: {dword:#010x}{marker}")

    # ===== 4. Deeper look at the 0x0b handler path =====
    print("\n" + "=" * 80)
    print("0x0b HANDLER PATH (RLTD PATHFINDING)")
    print("=" * 80)
    print("At 0x101b4129: cmp edx, 0x0b -> if equal, handle 0x0b section")
    hexdump_range(data, 0x101b4129, 0x80)

    # ===== 5. Check 0x101b41a9 area for sub-dispatch on version for type 0x06 =====
    print("\n" + "=" * 80)
    print("TYPE 0x06 HANDLER with version sub-dispatch")
    print("=" * 80)
    hexdump_range(data, 0x101b41a0, 0xC0)

    # ===== 6. What does the loop continuation look like? =====
    # After handling a section, execution should jump back to 0x101b40c0
    # Let's find all jumps back to 0x101b40c0 (the loop top)
    print("\n" + "=" * 80)
    print("ALL JUMPS TO LOOP TOP (0x101b40c0)")
    print("=" * 80)

    loop_top = 0x101b40c0
    func1_off = va_to_file(0x101b3fb0)
    func1_end = va_to_file(0x101b4695)

    for off in range(func1_off, func1_end - 5):
        b = data[off]
        va = file_to_va(off)

        # E9 rel32 (JMP)
        if b == 0xE9:
            rel32 = struct.unpack_from('<i', data, off + 1)[0]
            target = va + 5 + rel32
            if target == loop_top:
                print(f"  {va:#010x}: jmp {target:#010x} (loop back)")

        # EB rel8 (JMP short)
        if b == 0xEB:
            rel8 = struct.unpack_from('<b', data, off + 1)[0]
            target = va + 2 + rel8
            if target == loop_top:
                print(f"  {va:#010x}: jmp short {target:#010x} (loop back)")

        # 0F 8x rel32 (Jcc)
        if b == 0x0F and off + 5 < func1_end:
            b2 = data[off+1]
            if 0x80 <= b2 <= 0x8F:
                rel32 = struct.unpack_from('<i', data, off + 2)[0]
                target = va + 6 + rel32
                if target == loop_top:
                    cc_names = {
                        0x82: 'jb', 0x83: 'jae', 0x84: 'je', 0x85: 'jne',
                        0x86: 'jbe', 0x87: 'ja', 0x8C: 'jl', 0x8D: 'jge',
                    }
                    name = cc_names.get(b2, f'j{b2:02x}')
                    print(f"  {va:#010x}: {name} {target:#010x} (conditional loop back)")

        # 7x rel8 (Jcc short)
        if 0x70 <= b <= 0x7F:
            rel8 = struct.unpack_from('<b', data, off + 1)[0]
            target = va + 2 + rel8
            if target == loop_top:
                cc_names = {
                    0x72: 'jb', 0x73: 'jae', 0x74: 'je', 0x75: 'jne',
                    0x76: 'jbe', 0x77: 'ja', 0x7C: 'jl', 0x7D: 'jge',
                }
                name = cc_names.get(b, f'j{b:02x}')
                print(f"  {va:#010x}: {name} short {target:#010x} (conditional loop back)")

    # And the main loop condition check
    # At 0x101b40b1: jae 0x101b43b4 (exit loop)
    # At 0x101b40b7: jmp short 0x101b40c0 (enter loop body)
    # The loop condition is: compare cursor position against data end

    print("\n  Loop condition at 0x101b40ad:")
    hexdump_range(data, 0x101b40a8, 0x20)
    print("  0x101b40ad: cmp eax, [esp+0x1c]  ; compare position against data end")
    print("  0x101b40b1: jae 0x101b43b4        ; exit loop if past end")
    print("  0x101b40b7: jmp short 0x101b40c0  ; enter loop body")

    # ===== 7. What's the loop continuation path? =====
    # After a section handler runs, it should advance the cursor and jump to check
    # Let's trace where each handler ends up
    print("\n" + "=" * 80)
    print("SECTION HANDLER RETURN PATHS")
    print("=" * 80)

    # The entities handler (type 0x05):
    # at 0x101b40e6: cmp edx, 5; jne <next>
    # if edx==5: stores section data, then loops back
    off_0x101b40e9 = va_to_file(0x101b40e9)
    b = data[off_0x101b40e9]
    if b == 0x75:
        rel8 = struct.unpack_from('<b', data, off_0x101b40e9 + 1)[0]
        target = 0x101b40eb + rel8
        print(f"  Type 0x05 check: cmp edx, 5; jne {target:#010x} (skip entities handler)")
    elif b == 0x0F:
        # jne rel32 is 6 bytes
        pass

    # After entities handler body, there should be a loop-back jump
    # The entities handler starts at 0x101b40eb and seems to store data and jump
    # Let's look:
    print("\n  Entities handler (type 0x05) body at 0x101b40eb:")
    hexdump_range(data, 0x101b40eb, 0x30)

    # 0x101b40f7 area: this seems to be part of the entities path
    # 03 ce = add ecx, esi (advance cursor by section_size)
    # Then mov esi, [...] and check loop condition
    # Then jmp or fall through back to loop top

    # Let's find all the "03 ce" (add ecx, esi) instructions in the function
    # These advance the cursor by section_size
    print("\n" + "=" * 80)
    print("CURSOR ADVANCE (add ecx, esi) INSTRUCTIONS")
    print("=" * 80)
    for off in range(func1_off, func1_end - 2):
        if data[off] == 0x03 and data[off+1] == 0xCE:
            va = file_to_va(off)
            # Show context
            context = data[off-4:off+8]
            print(f"  {va:#010x}: 03 ce (add ecx, esi)  context: {context.hex(' ')}")


if __name__ == '__main__':
    main()
