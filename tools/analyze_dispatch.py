"""
Focused analysis of the blob section dispatcher at VA 0x101b3fb0.

We already know:
- Function 1 at 0x101b3fb0 handles section types: 0x05, 0x06, 0x09, 0x0b, 0x14, 0x17
- Function 2 at 0x101b1d00 calls RLTD handler #2 (0x101f6210)
- The version byte dispatch: sub al, 0x0a; cmp al, 7; ja (versions 0x0a..0x11)
- 0x0a is NOT in the section type comparisons of function 1!

Goal: Understand the relationship between the two functions.
Is function 2 called FROM function 1? Or are they alternatives called based on version?

Also: Find who calls function 1 and function 2.
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


def find_callers(data, target_va):
    """Find all CALL/JMP rel32 targeting given VA."""
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


def find_function_start(data, target_va):
    target_off = va_to_file(target_va)
    for off in range(target_off - 1, max(TEXT_RAW, target_off - 0x2000), -1):
        if data[off] == 0xCC and data[off - 1] == 0xCC:
            return file_to_va(off + 1)
    return None


def main():
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    print("=" * 80)
    print("CALLERS OF BOTH DISPATCHER FUNCTIONS")
    print("=" * 80)

    for func_va, name in [
        (0x101b3fb0, "Func1: blob section dispatcher (0x05,0x06,0x09,0x0b,0x14,0x17)"),
        (0x101b1d00, "Func2: second processor (calls RLTD handler #2)"),
    ]:
        callers = find_callers(data, func_va)
        print(f"\n{name}")
        print(f"  VA: {func_va:#010x}")
        if callers:
            for typ, va in callers:
                func_start = find_function_start(data, va)
                print(f"  {typ} from {va:#010x} (in function {func_start:#010x})" if func_start else f"  {typ} from {va:#010x}")
        else:
            print("  No CALL/JMP callers found (may be called via vtable/indirect)")

    # Check if function 1 calls function 2 or vice versa
    print("\n" + "=" * 80)
    print("CROSS-REFERENCES BETWEEN THE TWO FUNCTIONS")
    print("=" * 80)

    func1_off = va_to_file(0x101b3fb0)
    func1_end = va_to_file(0x101b4695)
    func2_off = va_to_file(0x101b1d00)
    func2_end = va_to_file(0x101b23fc)

    # Check if func1 calls func2
    print("\nDoes Func1 (0x101b3fb0) call Func2 (0x101b1d00)?")
    for off in range(func1_off, func1_end - 5):
        b = data[off]
        if b == 0xE8 or b == 0xE9:
            rel32 = struct.unpack_from('<i', data, off + 1)[0]
            call_va = file_to_va(off)
            dest_va = call_va + 5 + rel32
            if dest_va == 0x101b1d00:
                print(f"  YES! {('CALL' if b==0xE8 else 'JMP')} at {call_va:#010x}")

    # Check if func2 calls func1
    print("\nDoes Func2 (0x101b1d00) call Func1 (0x101b3fb0)?")
    for off in range(func2_off, func2_end - 5):
        b = data[off]
        if b == 0xE8 or b == 0xE9:
            rel32 = struct.unpack_from('<i', data, off + 1)[0]
            call_va = file_to_va(off)
            dest_va = call_va + 5 + rel32
            if dest_va == 0x101b3fb0:
                print(f"  YES! {('CALL' if b==0xE8 else 'JMP')} at {call_va:#010x}")

    # List ALL calls made by func1
    print("\n" + "=" * 80)
    print("ALL CALLS FROM FUNC1 (0x101b3fb0 - blob section dispatcher)")
    print("=" * 80)

    for off in range(func1_off, func1_end - 5):
        b = data[off]
        if b == 0xE8:
            rel32 = struct.unpack_from('<i', data, off + 1)[0]
            call_va = file_to_va(off)
            dest_va = call_va + 5 + rel32

            # Annotate known targets
            annotations = {
                0x101f4ba0: "RLTD_HANDLER_1 (processes 0x0b section)",
                0x101f6210: "RLTD_HANDLER_2 (processes 0x0b section)",
                0x101002b0: "RLTD_VALIDATOR",
                0x101b1d00: "FUNC2 (second processor!)",
            }
            ann = annotations.get(dest_va, "")
            if ann:
                print(f"  {call_va:#010x}: CALL {dest_va:#010x}  ; {ann}")
            else:
                # Show all calls for context
                print(f"  {call_va:#010x}: CALL {dest_va:#010x}")

    # List ALL calls made by func2
    print("\n" + "=" * 80)
    print("ALL CALLS FROM FUNC2 (0x101b1d00 - second processor)")
    print("=" * 80)

    for off in range(func2_off, func2_end - 5):
        b = data[off]
        if b == 0xE8:
            rel32 = struct.unpack_from('<i', data, off + 1)[0]
            call_va = file_to_va(off)
            dest_va = call_va + 5 + rel32

            annotations = {
                0x101f4ba0: "RLTD_HANDLER_1",
                0x101f6210: "RLTD_HANDLER_2 (processes 0x0b section)",
                0x101002b0: "RLTD_VALIDATOR",
                0x101b3fb0: "FUNC1 (blob section dispatcher!)",
            }
            ann = annotations.get(dest_va, "")
            if ann:
                print(f"  {call_va:#010x}: CALL {dest_va:#010x}  ; {ann}")
            else:
                print(f"  {call_va:#010x}: CALL {dest_va:#010x}")

    # Now, the key question: is there a section type 0x0a handler?
    # The dispatch in func1 checks: 0x05, 0x14, 0x0b, 0x06, 0x09, 0x17
    # What about 0x0a?
    # Let's search the ENTIRE .text section for cmp instructions with 0x0a
    # near pathfinding-related code

    print("\n" + "=" * 80)
    print("SEARCHING FOR 0x0a SECTION TYPE HANDLING")
    print("=" * 80)

    # In func1, after the 0x0b handler and 0x06 handler,
    # what handles the remaining section types?
    # Let's look at the flow more carefully.

    # The version dispatch at 0x101b406b: sub al, 0x0a; cmp al, 7
    # This checks if version byte is 0x0a..0x11 (10..17)
    # After that, the section loop starts at 0x101b40c0

    # The section type comparisons we found:
    # 0x101b40e6: cmp edx, 0x05  -> if type==5 (entities), jump
    # 0x101b4114: cmp edx, 0x14  -> if type==0x14 (metadata), jump
    # 0x101b4129: cmp edx, 0x0b  -> if type==0x0b (RLTD pathfinding), jump
    # 0x101b41a9: cmp edx, 0x06  -> if type==0x06, jump
    # 0x101b42fb: cmp edx, 0x09  -> if type==0x09 (grid), jump
    # 0x101b4344: cmp edx, 0x17  -> if type==0x17, jump

    # No cmp edx, 0x0a! Section type 0x0a (PTH pathfinding) is NOT handled!
    # Unknown types are probably just skipped (cursor advances by section size)

    # BUT func2 at 0x101b1d00 calls RLTD handler #2. Let's check if 0x0a
    # is handled there or in a caller.

    # Let's find the callers of func1 and func2 and see if there's a
    # higher-level function that chooses between them.

    print("\nFunc1 callers (deeper search):")
    callers1 = find_callers(data, 0x101b3fb0)
    for typ, va in callers1:
        func = find_function_start(data, va)
        print(f"  {typ} at {va:#010x}, containing function: {func:#010x}" if func else f"  {typ} at {va:#010x}")

        # Show context: what's this function doing?
        if func:
            func_off = va_to_file(func)
            caller_off = va_to_file(va)
            # Show 40 bytes before and 20 after the call for context
            context_start = max(func_off, caller_off - 40)
            for o in range(context_start, min(caller_off + 20, TEXT_RAW + TEXT_SIZE), 16):
                v = file_to_va(o)
                chunk = data[o:o+16]
                hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
                ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                marker = " <<<" if va_to_file(va) >= o and va_to_file(va) < o + 16 else ""
                print(f"    {v:#010x}: {hex_bytes}  {ascii_chars}{marker}")

    print("\nFunc2 callers (deeper search):")
    callers2 = find_callers(data, 0x101b1d00)
    for typ, va in callers2:
        func = find_function_start(data, va)
        print(f"  {typ} at {va:#010x}, containing function: {func:#010x}" if func else f"  {typ} at {va:#010x}")

        if func:
            func_off = va_to_file(func)
            caller_off = va_to_file(va)
            context_start = max(func_off, caller_off - 40)
            for o in range(context_start, min(caller_off + 20, TEXT_RAW + TEXT_SIZE), 16):
                v = file_to_va(o)
                chunk = data[o:o+16]
                hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
                ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                marker = " <<<" if va_to_file(va) >= o and va_to_file(va) < o + 16 else ""
                print(f"    {v:#010x}: {hex_bytes}  {ascii_chars}{marker}")

    # Now let's check if the callers of func1 and func2 are in the SAME parent function
    print("\n" + "=" * 80)
    print("PARENT FUNCTION ANALYSIS")
    print("=" * 80)

    caller1_funcs = set()
    for typ, va in callers1:
        func = find_function_start(data, va)
        if func:
            caller1_funcs.add(func)

    caller2_funcs = set()
    for typ, va in callers2:
        func = find_function_start(data, va)
        if func:
            caller2_funcs.add(func)

    shared = caller1_funcs & caller2_funcs
    if shared:
        print(f"\nBOTH func1 and func2 are called from the SAME function(s): {[f'{x:#010x}' for x in shared]}")
        for parent_va in shared:
            print(f"\n  Analyzing parent function at {parent_va:#010x}:")
            parent_off = va_to_file(parent_va)
            # Find its end
            parent_end = parent_off
            for off in range(parent_off + 5, min(parent_off + 0x3000, TEXT_RAW + TEXT_SIZE)):
                if data[off] == 0xCC and data[off+1] == 0xCC:
                    parent_end = off
                    break
            parent_size = parent_end - parent_off
            print(f"  Size: {parent_size} bytes, VA range: {parent_va:#010x} .. {file_to_va(parent_end):#010x}")

            # Find all CALL instructions in the parent
            print(f"  All CALLs in parent:")
            for off in range(parent_off, parent_end - 5):
                b = data[off]
                if b == 0xE8:
                    rel32 = struct.unpack_from('<i', data, off + 1)[0]
                    call_va = file_to_va(off)
                    dest_va = call_va + 5 + rel32
                    notable = {
                        0x101b3fb0: "<<< FUNC1 (section dispatcher)",
                        0x101b1d00: "<<< FUNC2 (RLTD handler #2 caller)",
                    }
                    ann = notable.get(dest_va, "")
                    if ann:
                        print(f"    {call_va:#010x}: CALL {dest_va:#010x}  {ann}")

            # Search for version-related checks or conditional dispatch
            print(f"\n  CMP instructions in parent (looking for version/flag dispatch):")
            for off in range(parent_off, parent_end - 2):
                b = data[off]

                # cmp reg, imm8
                if b == 0x83:
                    modrm = data[off+1]
                    reg_op = (modrm >> 3) & 7
                    mod = (modrm >> 6) & 3
                    if reg_op == 7 and mod == 3:  # cmp reg, imm8
                        rm = modrm & 7
                        imm = data[off+2]
                        va = file_to_va(off)
                        reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
                        print(f"    {va:#010x}: cmp {reg_names[rm]}, {imm:#x}")

                # cmp al, imm8
                if b == 0x3C:
                    imm = data[off+1]
                    va = file_to_va(off)
                    print(f"    {va:#010x}: cmp al, {imm:#x}")

                # test reg, reg
                if b == 0x85:
                    modrm = data[off+1]
                    mod = (modrm >> 6) & 3
                    reg = (modrm >> 3) & 7
                    rm = modrm & 7
                    if mod == 3 and reg == rm:
                        va = file_to_va(off)
                        reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
                        print(f"    {va:#010x}: test {reg_names[rm]}, {reg_names[rm]}")

    else:
        print(f"\nFunc1 called from: {[f'{x:#010x}' for x in caller1_funcs]}")
        print(f"Func2 called from: {[f'{x:#010x}' for x in caller2_funcs]}")
        print("They are called from DIFFERENT functions.")

    # Finally, let's look at the version-to-section-type mapping
    print("\n" + "=" * 80)
    print("VERSION BYTE ANALYSIS IN FUNC1")
    print("=" * 80)
    print("""
At 0x101b406b: sub al, 0x0a   ; version_byte -= 10
At 0x101b4075: cmp al, 0x7    ; if (version_byte - 10) > 7, jump to error
                               ; Valid versions: 0x0a (10) through 0x11 (17)

The section loop starts at 0x101b40c0:
  - Reads uint32 section_type into EDX
  - Reads uint32 section_size into ESI
  - Then dispatches on EDX:
    0x05 -> entities handler
    0x14 -> metadata handler
    0x0b -> RLTD pathfinding handler (calls 0x101f4ba0)
    0x06 -> unknown handler (sub-dispatches on version byte for 3 variants)
    0x09 -> grid handler
    0x17 -> unknown handler
    0x03 -> terrain? handler (at 0x101b4329)
    default -> skip (advance by section_size)

NOTABLY ABSENT: 0x0a (PTH pathfinding)!
0x0a sections are simply skipped by the default path.
""")

    # Let's verify: what happens for unknown section types?
    # After all the cmp/jne chains, does execution fall through to skip?
    print("Verifying: at the 0x17 check (last in chain):")
    area_off = va_to_file(0x101b4344)
    for o in range(area_off, area_off + 32):
        v = file_to_va(o)
        print(f"  {v:#010x}: {data[o]:02x}", end="")
        if o == area_off:
            print("  ; cmp edx, 0x17", end="")
        print()

    # The jne after cmp edx, 0x17 should jump back to the loop top
    # 0x101b4344: 83 fa 17
    # 0x101b4347: 0f 85 xx xx xx xx  -> jne to loop continuation
    off = va_to_file(0x101b4347)
    if data[off] == 0x0F and data[off+1] == 0x85:
        rel32 = struct.unpack_from('<i', data, off + 2)[0]
        target = file_to_va(off + 6) + rel32
        print(f"\n  After cmp edx, 0x17: jne -> {target:#010x}")
        print(f"  Loop top is at: 0x101b40c0")
        if target < 0x101b40c0:
            # It jumps before the loop - this is the loop continuation/advance
            print(f"  Target is BEFORE loop top -> this jumps to loop advance (skip section)")
        elif target == 0x101b40c0:
            print(f"  Target IS the loop top -> unknown sections restart the loop")
        else:
            print(f"  Target is {target:#010x}")


if __name__ == '__main__':
    main()
