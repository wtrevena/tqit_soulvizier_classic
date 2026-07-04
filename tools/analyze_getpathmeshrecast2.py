"""
Follow-up analysis: the function at 0x101B3180 is actually TWO functions:
  0x101B3180: tiny getter (mov eax, [ecx+0x6a38]; ret) - 7 bytes
  0x101B3190: the real GetPathMeshRecast function (starts with push ebp)

Search for callers of BOTH entry points.
Also dump more hex from GetPathMeshRecast around key areas.
"""
import struct

DLL_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll"

IMAGE_BASE = 0x10000000
TEXT_RVA = 0x1000
TEXT_RAW = 0x400
TEXT_SIZE = 0x2aa800
RDATA_RVA = 0x2ac000
RDATA_RAW = 0x2aac00

KNOWN = {
    0x103743B8: "PathFinder_singleton",
    0x103743F0: "PathFinder_global",
    0x101EA720: "PathFinder::AddMesh(PathMesh*)",
    0x101EA9B0: "PathFinder::AddMesh(PathMeshRecast*)",
    0x101EA7F0: "PathFinder::SetRecastMode",
    0x101B1D00: "Level::CreatePathMesh",
    0x101F4BA0: "ProcessRLTD",
    0x101F6100: "ProcessRLTD_init",
    0x10195800: "GridPathMeshCalculator::CreateNavigationMesh",
    0x101B3180: "Level::GetRLTDHandler (getter)",
    0x101B3190: "Level::GetPathMeshRecast (real)",
    0x101F6210: "ProcessRLTD_flow",
    0x101AD570: "???_called_from_GetPathMeshRecast",
}

def va_to_raw(va):
    rva = va - IMAGE_BASE
    if TEXT_RVA <= rva < TEXT_RVA + TEXT_SIZE:
        return TEXT_RAW + (rva - TEXT_RVA)
    elif RDATA_RVA <= rva < RDATA_RVA + 0x0c1c00:
        return RDATA_RAW + (rva - RDATA_RVA)
    elif rva >= 0x36e000:
        return 0x36c800 + (rva - 0x36e000)
    return None

def find_callers_of(data, target_va):
    callers = []
    for i in range(TEXT_SIZE - 4):
        if data[TEXT_RAW + i] == 0xE8:
            rel32 = struct.unpack_from('<i', data, TEXT_RAW + i + 1)[0]
            call_va = IMAGE_BASE + TEXT_RVA + i
            dest = call_va + 5 + rel32
            if dest == target_va:
                callers.append(call_va)
    return callers

def read_cstring(data, offset, maxlen=256):
    end = offset
    while end < len(data) and end < offset + maxlen and data[end] != 0:
        end += 1
    return data[offset:end].decode('ascii', errors='replace')

def name_va(va):
    if va in KNOWN:
        return KNOWN[va]
    return ""

def main():
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    # ========================================================================
    # 1. Search for callers of the GETTER at 0x101B3180
    # ========================================================================
    print("=" * 80)
    print("  Callers of Level::GetRLTDHandler getter @ 0x101B3180")
    print("=" * 80)
    callers_getter = find_callers_of(data, 0x101B3180)
    print(f"  Found {len(callers_getter)} caller(s)")
    for c in callers_getter:
        raw = va_to_raw(c)
        pre = data[max(TEXT_RAW, raw-16):raw]
        call = data[raw:raw+5]
        post = data[raw+5:min(raw+21, TEXT_RAW+TEXT_SIZE)]
        print(f"\n  {c:#010x}:")
        print(f"    Before: {' '.join(f'{b:02x}' for b in pre)}")
        print(f"    CALL:   {' '.join(f'{b:02x}' for b in call)}")
        print(f"    After:  {' '.join(f'{b:02x}' for b in post)}")
        # Find function start
        for back in range(0, min(0x4000, raw - TEXT_RAW)):
            cr = raw - back
            if data[cr] == 0x55 and data[cr+1] == 0x8B and data[cr+2] == 0xEC:
                fva = IMAGE_BASE + TEXT_RVA + (cr - TEXT_RAW)
                fn = name_va(fva)
                print(f"    In function: {fva:#010x} {fn}")
                break

    # ========================================================================
    # 2. Search for callers of the REAL function at 0x101B3190
    # ========================================================================
    print("\n" + "=" * 80)
    print("  Callers of Level::GetPathMeshRecast @ 0x101B3190")
    print("=" * 80)
    callers_real = find_callers_of(data, 0x101B3190)
    print(f"  Found {len(callers_real)} caller(s)")
    for c in callers_real:
        raw = va_to_raw(c)
        pre = data[max(TEXT_RAW, raw-16):raw]
        call = data[raw:raw+5]
        post = data[raw+5:min(raw+21, TEXT_RAW+TEXT_SIZE)]
        print(f"\n  {c:#010x}:")
        print(f"    Before: {' '.join(f'{b:02x}' for b in pre)}")
        print(f"    CALL:   {' '.join(f'{b:02x}' for b in call)}")
        print(f"    After:  {' '.join(f'{b:02x}' for b in post)}")
        for back in range(0, min(0x4000, raw - TEXT_RAW)):
            cr = raw - back
            if data[cr] == 0x55 and data[cr+1] == 0x8B and data[cr+2] == 0xEC:
                fva = IMAGE_BASE + TEXT_RVA + (cr - TEXT_RAW)
                fn = name_va(fva)
                print(f"    In function: {fva:#010x} {fn}")
                break

    # ========================================================================
    # 3. Deeper look at GetPathMeshRecast key sections
    # ========================================================================
    print("\n" + "=" * 80)
    print("  GetPathMeshRecast: hex dump around 0x6a38 refs and PathFinder refs")
    print("=" * 80)

    raw_base = va_to_raw(0x101B3190)

    # Around the 0x0b push and 0x6a38 references (offsets 0x8e8-0x920 from 0x101B3180)
    # Which is 0x8d8-0x910 from 0x101B3190
    # Let's dump 0x101B3A50 - 0x101B3B20 (the PathFinder area)
    print("\n--- Hex around PathFinder references (0x101B3A50 - 0x101B3B50) ---")
    start_va = 0x101B3A50
    start_raw = va_to_raw(start_va)
    for i in range(0, 256, 16):
        chunk = data[start_raw+i:start_raw+i+16]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {start_va+i:08X}  {hexpart:<48s}  {ascpart}")

    # ========================================================================
    # 4. Identify the call at 0x101b3a31 -> 0x1019ab90 and 0x101b3a8c -> 0x101f5260
    # ========================================================================
    print("\n" + "=" * 80)
    print("  Key calls from GetPathMeshRecast near the end")
    print("=" * 80)

    # 0x101b3a31 calls 0x1019ab90 - what is this?
    print("\n--- Function at 0x1019ab90 (called from GetPathMeshRecast) ---")
    raw_f = va_to_raw(0x1019ab90)
    prologue = data[raw_f:raw_f+64]
    print(f"  Prologue: {' '.join(f'{b:02x}' for b in prologue)}")
    # Check for string refs in first 256 bytes
    for i in range(252):
        val = struct.unpack_from('<I', data, raw_f + i)[0]
        rva = val - IMAGE_BASE
        if RDATA_RVA <= rva < RDATA_RVA + 0x0c1c00:
            rdata_raw = RDATA_RAW + (rva - RDATA_RVA)
            if rdata_raw < len(data):
                s = read_cstring(data, rdata_raw)
                if len(s) >= 3 and all(c < '\x7f' and c >= ' ' for c in s[:4]):
                    print(f"  +{i:#x}: str ref -> \"{s}\"")

    # 0x101b3a8c calls 0x101f5260 - what is this?
    print("\n--- Function at 0x101f5260 (called from GetPathMeshRecast) ---")
    raw_f2 = va_to_raw(0x101f5260)
    prologue2 = data[raw_f2:raw_f2+64]
    print(f"  Prologue: {' '.join(f'{b:02x}' for b in prologue2)}")
    for i in range(512):
        val = struct.unpack_from('<I', data, raw_f2 + i)[0]
        rva = val - IMAGE_BASE
        if RDATA_RVA <= rva < RDATA_RVA + 0x0c1c00:
            rdata_raw = RDATA_RAW + (rva - RDATA_RVA)
            if rdata_raw < len(data):
                s = read_cstring(data, rdata_raw)
                if len(s) >= 3 and all(c < '\x7f' and c >= ' ' for c in s[:4]):
                    print(f"  +{i:#x}: str ref -> \"{s}\"")

    # 0x101b3ab0 calls 0x10218a20 - what is this?
    print("\n--- Function at 0x10218a20 (called from GetPathMeshRecast) ---")
    raw_f3 = va_to_raw(0x10218a20)
    prologue3 = data[raw_f3:raw_f3+64]
    print(f"  Prologue: {' '.join(f'{b:02x}' for b in prologue3)}")
    for i in range(512):
        val = struct.unpack_from('<I', data, raw_f3 + i)[0]
        rva = val - IMAGE_BASE
        if RDATA_RVA <= rva < RDATA_RVA + 0x0c1c00:
            rdata_raw = RDATA_RAW + (rva - RDATA_RVA)
            if rdata_raw < len(data):
                s = read_cstring(data, rdata_raw)
                if len(s) >= 3 and all(c < '\x7f' and c >= ' ' for c in s[:4]):
                    print(f"  +{i:#x}: str ref -> \"{s}\"")

    # 0x101b3410 calls 0x101ad570 - critical path mesh call
    print("\n--- Function at 0x101ad570 (called from GetPathMeshRecast - likely LoadPathMesh?) ---")
    raw_f4 = va_to_raw(0x101ad570)
    prologue4 = data[raw_f4:raw_f4+64]
    print(f"  Prologue: {' '.join(f'{b:02x}' for b in prologue4)}")
    # Find calls and strings in first 1024 bytes
    for i in range(1020):
        if data[raw_f4 + i] == 0xE8:
            rel32 = struct.unpack_from('<i', data, raw_f4 + i + 1)[0]
            target = 0x101ad570 + i + 5 + rel32
            tgt_rva = target - IMAGE_BASE
            if TEXT_RVA <= tgt_rva < TEXT_RVA + TEXT_SIZE:
                n = name_va(target)
                extra = f" = {n}" if n else ""
                print(f"  +{i:#x}: CALL {target:#010x}{extra}")
        val = struct.unpack_from('<I', data, raw_f4 + i)[0]
        rva = val - IMAGE_BASE
        if RDATA_RVA <= rva < RDATA_RVA + 0x0c1c00:
            rdata_raw = RDATA_RAW + (rva - RDATA_RVA)
            if rdata_raw < len(data):
                s = read_cstring(data, rdata_raw)
                if len(s) >= 3 and all(c < '\x7f' and c >= ' ' for c in s[:4]):
                    print(f"  +{i:#x}: str ref -> \"{s}\"")

    # ========================================================================
    # 5. Look at the "LVL" constant at 0x101B33C0
    # ========================================================================
    print("\n" + "=" * 80)
    print("  GetPathMeshRecast: LVL section reading logic")
    print("=" * 80)
    # The hex shows D$XLVL at 0x101B33C4 which is the LVL section tag
    # Let's dump 0x101B33B0 - 0x101B3440 to see the section reading
    start_va = 0x101B33B0
    start_raw = va_to_raw(start_va)
    print(f"\n--- Hex 0x101B33B0 - 0x101B3450 ---")
    for i in range(0, 160, 16):
        chunk = data[start_raw+i:start_raw+i+16]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {start_va+i:08X}  {hexpart:<48s}  {ascpart}")

    # Check what 0x114C5634 is - the LVL tag value
    print(f"\n  'LVL\\x11' as dword: {struct.unpack('<I', b'LVL\\x11')[0]:#010x}")
    print(f"  Actual dword at that position: {struct.unpack_from('<I', data, va_to_raw(0x101B33C4))[0]:#010x}")

    # ========================================================================
    # 6. ProcessRLTD_flow: look for AddMesh calls (direct and indirect)
    # ========================================================================
    print("\n" + "=" * 80)
    print("  ProcessRLTD_flow: searching for ALL PathFinder-related calls")
    print("=" * 80)

    raw5 = va_to_raw(0x101F6210)
    # Search for calls to SetRecastMode and both AddMesh variants
    targets_of_interest = {
        0x101EA720: "PathFinder::AddMesh(PathMesh*)",
        0x101EA9B0: "PathFinder::AddMesh(PathMeshRecast*)",
        0x101EA7F0: "PathFinder::SetRecastMode",
    }
    for i in range(0x2000 - 4):
        if data[raw5 + i] == 0xE8:
            rel32 = struct.unpack_from('<i', data, raw5 + i + 1)[0]
            target = 0x101F6210 + i + 5 + rel32
            if target in targets_of_interest:
                print(f"  +{i:#06x} ({0x101F6210+i:#010x}): CALL {target:#010x} = {targets_of_interest[target]}")
                ctx = data[raw5+max(0,i-16):raw5+min(i+21, 0x2000)]
                print(f"    context: {' '.join(f'{b:02x}' for b in ctx)}")

    # Also check the functions called from ProcessRLTD_flow that might call AddMesh
    print("\n--- Checking functions called from ProcessRLTD_flow for AddMesh calls ---")
    flow_calls = set()
    for i in range(0x2000 - 4):
        if data[raw5 + i] == 0xE8:
            rel32 = struct.unpack_from('<i', data, raw5 + i + 1)[0]
            target = 0x101F6210 + i + 5 + rel32
            tgt_rva = target - IMAGE_BASE
            if TEXT_RVA <= tgt_rva < TEXT_RVA + TEXT_SIZE:
                flow_calls.add(target)

    for fc in sorted(flow_calls):
        fc_raw = va_to_raw(fc)
        if fc_raw is None or fc_raw + 2048 > len(data):
            continue
        for i in range(min(2048, len(data) - fc_raw - 4)):
            if data[fc_raw + i] == 0xE8:
                rel32 = struct.unpack_from('<i', data, fc_raw + i + 1)[0]
                target = fc + i + 5 + rel32
                if target in targets_of_interest:
                    print(f"  {fc:#010x}+{i:#x} ({fc+i:#010x}): CALL {targets_of_interest[target]}")

    # ========================================================================
    # 7. Check who calls ProcessRLTD_flow
    # ========================================================================
    print("\n" + "=" * 80)
    print("  Callers of ProcessRLTD_flow @ 0x101F6210")
    print("=" * 80)
    callers_flow = find_callers_of(data, 0x101F6210)
    print(f"  Found {len(callers_flow)} caller(s)")
    for c in callers_flow:
        raw = va_to_raw(c)
        pre = data[max(TEXT_RAW, raw-16):raw]
        call = data[raw:raw+5]
        post = data[raw+5:min(raw+21, TEXT_RAW+TEXT_SIZE)]
        print(f"\n  {c:#010x}:")
        print(f"    Before: {' '.join(f'{b:02x}' for b in pre)}")
        print(f"    CALL:   {' '.join(f'{b:02x}' for b in call)}")
        print(f"    After:  {' '.join(f'{b:02x}' for b in post)}")
        for back in range(0, min(0x4000, raw - TEXT_RAW)):
            cr = raw - back
            if data[cr] == 0x55 and data[cr+1] == 0x8B and data[cr+2] == 0xEC:
                fva = IMAGE_BASE + TEXT_RVA + (cr - TEXT_RAW)
                fn = name_va(fva)
                print(f"    In function: {fva:#010x} {fn}")
                break

    # ========================================================================
    # 8. Full hex dump: GetPathMeshRecast bytes 1024-2699
    # ========================================================================
    print("\n" + "=" * 80)
    print("  GetPathMeshRecast: hex dump bytes 1024-2048")
    print("=" * 80)
    raw_base = va_to_raw(0x101B3180)
    for i in range(1024, min(2048, 2699), 16):
        chunk = data[raw_base+i:raw_base+i+16]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {0x101B3180+i:08X}  {hexpart:<48s}  {ascpart}")

    print("\n" + "=" * 80)
    print("  GetPathMeshRecast: hex dump bytes 2048-2699")
    print("=" * 80)
    for i in range(2048, 2699, 16):
        chunk = data[raw_base+i:raw_base+i+min(16, 2699-i)]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {0x101B3180+i:08X}  {hexpart:<48s}  {ascpart}")

    # ========================================================================
    # 9. Check the global at 0x10374441 ("AD7") referenced from ProcessRLTD_flow
    # ========================================================================
    print("\n" + "=" * 80)
    print("  Global byte check: 0x10374441 (AD7 reference in ProcessRLTD_flow)")
    print("=" * 80)
    raw_g = va_to_raw(0x10374441)
    if raw_g and raw_g < len(data):
        ctx = data[raw_g-4:raw_g+16]
        print(f"  Bytes around 0x10374441: {' '.join(f'{b:02x}' for b in ctx)}")
        print(f"  This is cmp byte ptr [0x10374441], 0  -- a Recast mode flag?")

    # Who else references 0x10374441?
    print("\n  Other references to 0x10374441 in .text:")
    val_bytes = struct.pack('<I', 0x10374441)
    count = 0
    for i in range(TEXT_SIZE - 3):
        if data[TEXT_RAW+i:TEXT_RAW+i+4] == val_bytes:
            va = IMAGE_BASE + TEXT_RVA + i
            ctx = data[TEXT_RAW+max(0,i-2):TEXT_RAW+min(i+8, TEXT_SIZE)]
            print(f"    {va:#010x}: ctx={' '.join(f'{b:02x}' for b in ctx)}")
            count += 1
            if count > 20:
                print("    ... (truncated)")
                break

    print("\n  Done.")


if __name__ == '__main__':
    main()
