"""
Deep analysis of Level::GetPathMeshRecast and GridPathMeshCalculator::CreateNavigationMesh
in Engine.dll for TQAE PathEngine tok data investigation.
"""
import struct
import sys

DLL_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll"

IMAGE_BASE = 0x10000000
TEXT_RVA = 0x1000
TEXT_RAW = 0x400
TEXT_SIZE = 0x2aa800
RDATA_RVA = 0x2ac000
RDATA_RAW = 0x2aac00
RDATA_SIZE = 0x0c1c00
DATA_RVA = 0x36e000
DATA_RAW = 0x36c800

# Known addresses
KNOWN = {
    0x103743B8: "PathFinder_singleton",
    0x103743F0: "PathFinder_global",
    0x101EA720: "PathFinder::AddMesh(PathMesh*)",
    0x101EA9B0: "PathFinder::AddMesh(PathMeshRecast*)",
    0x101EA7F0: "PathFinder::SetRecastMode",
    0x101B1D00: "Level::CreatePathMesh",
    0x101F4BA0: "ProcessRLTD",
    0x101F6100: "ProcessRLTD_init",
    0x101b3fb0: "Level_LVL_parser",
    0x10195800: "GridPathMeshCalculator::CreateNavigationMesh",
    0x101B3180: "Level::GetPathMeshRecast",
    0x101F6210: "ProcessRLTD_flow",
}

def va_to_raw(va):
    rva = va - IMAGE_BASE
    if TEXT_RVA <= rva < TEXT_RVA + TEXT_SIZE:
        return TEXT_RAW + (rva - TEXT_RVA)
    elif RDATA_RVA <= rva < RDATA_RVA + RDATA_SIZE:
        return RDATA_RAW + (rva - RDATA_RVA)
    elif rva >= DATA_RVA:
        return DATA_RAW + (rva - DATA_RVA)
    return None

def raw_to_va(raw):
    if TEXT_RAW <= raw < TEXT_RAW + TEXT_SIZE:
        return IMAGE_BASE + TEXT_RVA + (raw - TEXT_RAW)
    elif RDATA_RAW <= raw < RDATA_RAW + RDATA_SIZE:
        return IMAGE_BASE + RDATA_RVA + (raw - RDATA_RAW)
    elif raw >= DATA_RAW:
        return IMAGE_BASE + DATA_RVA + (raw - DATA_RAW)
    return None

def read_cstring(data, offset, maxlen=256):
    end = offset
    while end < len(data) and end < offset + maxlen and data[end] != 0:
        end += 1
    try:
        return data[offset:end].decode('ascii', errors='replace')
    except:
        return "<decode error>"

def is_rdata_va(va):
    return (IMAGE_BASE + RDATA_RVA) <= va < (IMAGE_BASE + RDATA_RVA + RDATA_SIZE)

def is_data_va(va):
    return va >= (IMAGE_BASE + DATA_RVA)

def is_text_va(va):
    return (IMAGE_BASE + TEXT_RVA) <= va < (IMAGE_BASE + TEXT_RVA + TEXT_SIZE)

def name_va(va):
    if va in KNOWN:
        return KNOWN[va]
    if is_rdata_va(va):
        return f".rdata+{va - IMAGE_BASE - RDATA_RVA:#x}"
    if is_data_va(va):
        return f".data+{va - IMAGE_BASE - DATA_RVA:#x}"
    if is_text_va(va):
        return f".text+{va - IMAGE_BASE - TEXT_RVA:#x}"
    return ""

def find_calls(data, func_raw, func_va, size):
    """Find all E8 rel32 CALL instructions in a function."""
    calls = []
    for i in range(size - 4):
        if data[func_raw + i] == 0xE8:
            rel32 = struct.unpack_from('<i', data, func_raw + i + 1)[0]
            target_va = func_va + i + 5 + rel32
            if is_text_va(target_va):
                calls.append((func_va + i, target_va))
    return calls

def find_dword_refs(data, func_raw, size, check_fn):
    """Find all dword immediates matching check_fn in the function bytes."""
    refs = []
    for i in range(size - 3):
        val = struct.unpack_from('<I', data, func_raw + i)[0]
        if check_fn(val):
            refs.append((i, val))
    return refs

def find_callers_of(data, target_va):
    """Search entire .text for E8 calls to target_va."""
    callers = []
    text_start = TEXT_RAW
    for i in range(TEXT_SIZE - 4):
        if data[text_start + i] == 0xE8:
            rel32 = struct.unpack_from('<i', data, text_start + i + 1)[0]
            call_va = IMAGE_BASE + TEXT_RVA + i
            dest = call_va + 5 + rel32
            if dest == target_va:
                callers.append(call_va)
    return callers

def hexdump(data, offset, size, base_va):
    lines = []
    for i in range(0, size, 16):
        if offset + i + 16 > len(data):
            break
        chunk = data[offset + i: offset + i + 16]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"  {base_va + i:08X}  {hexpart:<48s}  {ascpart}")
    return '\n'.join(lines)

def analyze_function(data, name, va, size):
    raw = va_to_raw(va)
    print(f"\n{'='*80}")
    print(f"  {name} @ {va:#010x}  (raw {raw:#x}, {size} bytes)")
    print(f"{'='*80}")

    # Hex dump first 1024 bytes
    dump_size = min(1024, size)
    print(f"\n--- First {dump_size} bytes hex dump ---")
    print(hexdump(data, raw, dump_size, va))

    # Find all CALL targets
    calls = find_calls(data, raw, va, size)
    print(f"\n--- CALL targets ({len(calls)} found) ---")
    for call_site, target in calls:
        label = name_va(target)
        extra = f"  <-- {label}" if label else ""
        print(f"  {call_site:#010x}: CALL {target:#010x}{extra}")

    # Find references to known addresses
    print(f"\n--- References to known addresses ---")
    for i in range(size - 3):
        val = struct.unpack_from('<I', data, raw + i)[0]
        if val in KNOWN:
            ctx_start = max(0, i - 2)
            ctx_bytes = data[raw + ctx_start: raw + min(i + 6, size)]
            ctx_hex = ' '.join(f'{b:02x}' for b in ctx_bytes)
            print(f"  offset +{i:#x} (VA {va+i:#010x}): dword {val:#010x} = {KNOWN[val]}")
            print(f"    context: {ctx_hex}")

    # Find .rdata string references
    print(f"\n--- .rdata string references ---")
    rdata_refs = []
    for i in range(size - 3):
        val = struct.unpack_from('<I', data, raw + i)[0]
        if is_rdata_va(val):
            rdata_raw = va_to_raw(val)
            if rdata_raw and rdata_raw < len(data):
                s = read_cstring(data, rdata_raw)
                if len(s) >= 2 and all(c < '\x7f' and c >= ' ' for c in s[:min(len(s),4)]):
                    rdata_refs.append((i, val, s))
    # Deduplicate by (offset, val)
    seen = set()
    for off, val, s in rdata_refs:
        key = (off, val)
        if key not in seen:
            seen.add(key)
            print(f"  +{off:#06x} (VA {va+off:#010x}): -> {val:#010x}: \"{s}\"")

    return calls, rdata_refs


def main():
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    print(f"Engine.dll loaded: {len(data)} bytes")

    # ========================================================================
    # 1. Level::GetPathMeshRecast @ 0x101B3180
    # ========================================================================
    calls1, rdata1 = analyze_function(data, "Level::GetPathMeshRecast", 0x101B3180, 2699)

    # Additional analysis for GetPathMeshRecast
    raw1 = va_to_raw(0x101B3180)
    print(f"\n--- GetPathMeshRecast: Looking for operator new (common patterns) ---")
    # operator new typically pushes a size then calls; look for push imm32 + call patterns
    for call_site, target in calls1:
        off_in_func = call_site - 0x101B3180
        # Check bytes before the call for push instructions
        if off_in_func >= 5:
            pre = data[raw1 + off_in_func - 5: raw1 + off_in_func]
            # push imm32 = 68 xx xx xx xx
            if pre[0] == 0x68:
                size_val = struct.unpack_from('<I', pre, 1)[0]
                if size_val < 0x10000:  # reasonable object size
                    print(f"  {call_site:#010x}: push {size_val:#x} then CALL {target:#010x} -- possible operator new(size={size_val})")
        if off_in_func >= 2:
            pre2 = data[raw1 + off_in_func - 2: raw1 + off_in_func]
            # push imm8 = 6a xx
            if pre2[0] == 0x6a:
                size_val = pre2[1]
                if size_val > 0:
                    print(f"  {call_site:#010x}: push {size_val:#x} then CALL {target:#010x} -- possible operator new(size={size_val})")

    # Look for conditional jumps (branching logic)
    print(f"\n--- GetPathMeshRecast: Conditional jumps (control flow) ---")
    jcc_opcodes = {
        0x74: 'JE/JZ', 0x75: 'JNE/JNZ', 0x76: 'JBE', 0x77: 'JA',
        0x7C: 'JL', 0x7D: 'JGE', 0x7E: 'JLE', 0x7F: 'JG',
        0x72: 'JB', 0x73: 'JAE', 0x78: 'JS', 0x79: 'JNS',
    }
    for i in range(2699 - 1):
        b = data[raw1 + i]
        if b in jcc_opcodes:
            rel8 = struct.unpack_from('<b', data, raw1 + i + 1)[0]
            target = 0x101B3180 + i + 2 + rel8
            print(f"  {0x101B3180+i:#010x}: {jcc_opcodes[b]} -> {target:#010x} (rel={rel8:+d})")
        # Near conditional jumps: 0F 8x rel32
        if b == 0x0F and i + 5 < 2699:
            b2 = data[raw1 + i + 1]
            near_jcc = {
                0x84: 'JE/JZ', 0x85: 'JNE/JNZ', 0x86: 'JBE', 0x87: 'JA',
                0x8C: 'JL', 0x8D: 'JGE', 0x8E: 'JLE', 0x8F: 'JG',
                0x82: 'JB', 0x83: 'JAE',
            }
            if b2 in near_jcc:
                rel32 = struct.unpack_from('<i', data, raw1 + i + 2)[0]
                target = 0x101B3180 + i + 6 + rel32
                print(f"  {0x101B3180+i:#010x}: {near_jcc[b2]} (near) -> {target:#010x} (rel={rel32:+d})")

    # Look for Level+0x6a38 reference
    print(f"\n--- GetPathMeshRecast: Looking for offset 0x6a38 (RLTD handler) ---")
    for i in range(2699 - 3):
        val = struct.unpack_from('<I', data, raw1 + i)[0]
        if val == 0x6a38:
            ctx = data[raw1 + max(0,i-4): raw1 + min(i+8, 2699)]
            print(f"  +{i:#06x} (VA {0x101B3180+i:#010x}): found 0x6a38, context: {' '.join(f'{b:02x}' for b in ctx)}")
        # Also check as 16-bit immediate
        if i < 2699 - 1:
            val16 = struct.unpack_from('<H', data, raw1 + i)[0]
            if val16 == 0x6a38 and data[raw1 + i - 1:raw1 + i] in [b'\x81', b'\x8b', b'\x89', b'\x8d']:
                pass  # already caught above likely

    # Look for 0x0b section marker references
    print(f"\n--- GetPathMeshRecast: Looking for 0x0b constant (section marker) ---")
    for i in range(2699 - 3):
        # cmp reg, 0x0b patterns: 83 f8 0b (cmp eax, 0b), 83 f9 0b (cmp ecx, 0b), etc.
        if data[raw1 + i] == 0x83 and i + 2 < 2699:
            if data[raw1 + i + 2] == 0x0b:
                modrm = data[raw1 + i + 1]
                reg_field = (modrm >> 3) & 7
                if reg_field == 7:  # cmp
                    regs = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
                    r = modrm & 7
                    print(f"  +{i:#06x} (VA {0x101B3180+i:#010x}): cmp {regs[r]}, 0x0b")
        # push 0x0b = 6a 0b
        if data[raw1 + i] == 0x6a and data[raw1 + i + 1] == 0x0b:
            print(f"  +{i:#06x} (VA {0x101B3180+i:#010x}): push 0x0b")

    # ========================================================================
    # 2. GridPathMeshCalculator::CreateNavigationMesh @ 0x10195800
    # ========================================================================
    calls2, rdata2 = analyze_function(data, "GridPathMeshCalculator::CreateNavigationMesh", 0x10195800, 2356)

    # Signature analysis
    raw2 = va_to_raw(0x10195800)
    print(f"\n--- CreateNavigationMesh: Function prologue analysis ---")
    prologue = data[raw2:raw2+32]
    print(f"  First 32 bytes: {' '.join(f'{b:02x}' for b in prologue)}")
    # Check for typical thiscall/stdcall patterns
    # sub esp, N for local variable space
    for i in range(min(32, 2356) - 2):
        if data[raw2+i] == 0x81 and data[raw2+i+1] == 0xEC:
            locals_size = struct.unpack_from('<I', data, raw2+i+2)[0]
            print(f"  sub esp, {locals_size:#x} -- {locals_size} bytes of locals")
        if data[raw2+i] == 0x83 and data[raw2+i+1] == 0xEC:
            locals_size = data[raw2+i+2]
            print(f"  sub esp, {locals_size:#x} -- {locals_size} bytes of locals")

    # operator new calls
    print(f"\n--- CreateNavigationMesh: operator new candidates ---")
    for call_site, target in calls2:
        off_in_func = call_site - 0x10195800
        if off_in_func >= 5:
            pre = data[raw2 + off_in_func - 5: raw2 + off_in_func]
            if pre[0] == 0x68:
                size_val = struct.unpack_from('<I', pre, 1)[0]
                if size_val < 0x100000:
                    print(f"  {call_site:#010x}: push {size_val:#x} then CALL {target:#010x}")
        if off_in_func >= 2:
            pre2 = data[raw2 + off_in_func - 2: raw2 + off_in_func]
            if pre2[0] == 0x6a and pre2[1] > 0:
                print(f"  {call_site:#010x}: push {pre2[1]:#x} then CALL {target:#010x}")

    # ========================================================================
    # 3. Cross-reference: who calls GetPathMeshRecast?
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"  Cross-reference: callers of Level::GetPathMeshRecast (0x101B3180)")
    print(f"{'='*80}")
    callers1 = find_callers_of(data, 0x101B3180)
    print(f"  Found {len(callers1)} caller(s)")
    for caller_va in callers1:
        caller_raw = va_to_raw(caller_va)
        # Show 16 bytes before, 5 bytes of call, 16 bytes after
        pre_raw = max(TEXT_RAW, caller_raw - 16)
        post_end = min(TEXT_RAW + TEXT_SIZE, caller_raw + 5 + 16)
        pre_bytes = data[pre_raw:caller_raw]
        call_bytes = data[caller_raw:caller_raw+5]
        post_bytes = data[caller_raw+5:post_end]
        label = name_va(caller_va)
        extra = f"  (in {label})" if label else ""
        print(f"\n  Caller at {caller_va:#010x}{extra}:")
        print(f"    Before: {' '.join(f'{b:02x}' for b in pre_bytes)}")
        print(f"    CALL:   {' '.join(f'{b:02x}' for b in call_bytes)}")
        print(f"    After:  {' '.join(f'{b:02x}' for b in post_bytes)}")

        # Try to identify which function this caller is in
        # Search backward for common prologue patterns (push ebp; mov ebp, esp = 55 8b ec)
        for back in range(0, min(0x2000, caller_raw - TEXT_RAW), 1):
            check_raw = caller_raw - back
            if data[check_raw] == 0x55 and data[check_raw+1] == 0x8B and data[check_raw+2] == 0xEC:
                func_start_va = raw_to_va(check_raw)
                fname = name_va(func_start_va)
                if fname:
                    print(f"    Likely in function: {func_start_va:#010x} = {fname}")
                else:
                    print(f"    Likely function start: {func_start_va:#010x}")
                break

    # ========================================================================
    # 4. Cross-reference: who calls CreateNavigationMesh?
    # ========================================================================
    print(f"\n{'='*80}")
    print(f"  Cross-reference: callers of GridPathMeshCalculator::CreateNavigationMesh (0x10195800)")
    print(f"{'='*80}")
    callers2 = find_callers_of(data, 0x10195800)
    print(f"  Found {len(callers2)} caller(s)")
    for caller_va in callers2:
        caller_raw = va_to_raw(caller_va)
        pre_raw = max(TEXT_RAW, caller_raw - 16)
        post_end = min(TEXT_RAW + TEXT_SIZE, caller_raw + 5 + 16)
        pre_bytes = data[pre_raw:caller_raw]
        call_bytes = data[caller_raw:caller_raw+5]
        post_bytes = data[caller_raw+5:post_end]
        label = name_va(caller_va)
        extra = f"  (in {label})" if label else ""
        print(f"\n  Caller at {caller_va:#010x}{extra}:")
        print(f"    Before: {' '.join(f'{b:02x}' for b in pre_bytes)}")
        print(f"    CALL:   {' '.join(f'{b:02x}' for b in call_bytes)}")
        print(f"    After:  {' '.join(f'{b:02x}' for b in post_bytes)}")

        for back in range(0, min(0x2000, caller_raw - TEXT_RAW), 1):
            check_raw = caller_raw - back
            if data[check_raw] == 0x55 and data[check_raw+1] == 0x8B and data[check_raw+2] == 0xEC:
                func_start_va = raw_to_va(check_raw)
                fname = name_va(func_start_va)
                if fname:
                    print(f"    Likely in function: {func_start_va:#010x} = {fname}")
                else:
                    print(f"    Likely function start: {func_start_va:#010x}")
                break

    # ========================================================================
    # 5. ProcessRLTD flow @ 0x101F6210
    # ========================================================================
    analyze_function(data, "ProcessRLTD_flow", 0x101F6210, 0x2000)

    # Extra: first 512 bytes detailed
    raw5 = va_to_raw(0x101F6210)
    print(f"\n--- ProcessRLTD_flow: First 512 bytes hex dump ---")
    print(hexdump(data, raw5, 512, 0x101F6210))

    # Specifically look for AddMesh(PathMeshRecast*) references
    print(f"\n--- ProcessRLTD_flow: References to PathFinder::AddMesh(PathMeshRecast*) = 0x101EA9B0 ---")
    calls5 = find_calls(data, raw5, 0x101F6210, 0x2000)
    for call_site, target in calls5:
        if target == 0x101EA9B0:
            off = call_site - 0x101F6210
            ctx_raw = raw5 + max(0, off - 16)
            ctx_end = raw5 + min(off + 21, 0x2000)
            ctx = data[ctx_raw:ctx_end]
            print(f"  {call_site:#010x}: CALL AddMesh(PathMeshRecast*)")
            print(f"    context: {' '.join(f'{b:02x}' for b in ctx)}")

    # Also check for indirect calls to AddMesh via vtable
    print(f"\n--- ProcessRLTD_flow: Looking for PathFinder singleton/global refs ---")
    for i in range(0x2000 - 3):
        val = struct.unpack_from('<I', data, raw5 + i)[0]
        if val in (0x103743B8, 0x103743F0):
            ctx = data[raw5 + max(0,i-4): raw5 + min(i+8, 0x2000)]
            print(f"  +{i:#06x} (VA {0x101F6210+i:#010x}): {val:#010x} = {KNOWN[val]}")
            print(f"    context: {' '.join(f'{b:02x}' for b in ctx)}")

    print(f"\n{'='*80}")
    print(f"  Analysis complete.")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
