"""
Final follow-up: remaining analysis after fixing the escape issue.
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
    0x101F6210: "ProcessRLTD_flow",
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

def name_va(va):
    return KNOWN.get(va, "")

def main():
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    raw_base = va_to_raw(0x101B3180)

    # LVL tag analysis
    print("=" * 80)
    print("  LVL tag analysis")
    print("=" * 80)
    lvl_tag = struct.unpack_from('<I', data, va_to_raw(0x101B33C8))[0]
    print(f"  Dword at 0x101B33C8 (the LVL tag): {lvl_tag:#010x}")
    tag_bytes = struct.pack('<I', lvl_tag)
    print(f"  As bytes: {' '.join(f'{b:02x}' for b in tag_bytes)}")
    print(f"  As ASCII: {''.join(chr(b) if 32 <= b < 127 else '.' for b in tag_bytes)}")
    # This is 0x114C564C = 'LVL\x11'
    # Section tag 0x11 = 17 decimal

    # ========================================================================
    # Full hex dump: GetPathMeshRecast bytes 1024-2699
    # ========================================================================
    print("\n" + "=" * 80)
    print("  GetPathMeshRecast: hex dump bytes 1024-2048")
    print("=" * 80)
    for i in range(1024, min(2048, 2699), 16):
        chunk = data[raw_base+i:raw_base+i+16]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {0x101B3180+i:08X}  {hexpart:<48s}  {ascpart}")

    print("\n" + "=" * 80)
    print("  GetPathMeshRecast: hex dump bytes 2048-2699")
    print("=" * 80)
    for i in range(2048, 2699, 16):
        remaining = min(16, 2699 - i)
        chunk = data[raw_base+i:raw_base+i+remaining]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {0x101B3180+i:08X}  {hexpart:<48s}  {ascpart}")

    # ========================================================================
    # Global at 0x10374441
    # ========================================================================
    print("\n" + "=" * 80)
    print("  Global byte at 0x10374441 (referenced from ProcessRLTD_flow)")
    print("=" * 80)
    raw_g = va_to_raw(0x10374441)
    if raw_g and raw_g < len(data):
        ctx = data[raw_g-8:raw_g+16]
        print(f"  Bytes around 0x10374441: {' '.join(f'{b:02x}' for b in ctx)}")
        print(f"  The instruction 'cmp byte ptr [0x10374441], 0' is a Recast mode flag check")

    # Who else references this global?
    print("\n  Other .text references to 0x10374441:")
    val_bytes = struct.pack('<I', 0x10374441)
    count = 0
    for i in range(TEXT_SIZE - 3):
        if data[TEXT_RAW+i:TEXT_RAW+i+4] == val_bytes:
            va = IMAGE_BASE + TEXT_RVA + i
            ctx = data[TEXT_RAW+max(0,i-3):TEXT_RAW+min(i+8, TEXT_SIZE)]
            print(f"    {va:#010x}: ctx={' '.join(f'{b:02x}' for b in ctx)}")
            count += 1
            if count > 30:
                print("    ... (truncated)")
                break
    print(f"  Total: {count}")

    # ========================================================================
    # Who calls ProcessRLTD_flow?
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
    # Detailed analysis of the PathFinder interaction at end of GetPathMeshRecast
    # ========================================================================
    print("\n" + "=" * 80)
    print("  GetPathMeshRecast: PathFinder interaction detail (0x101B3AB0-0x101B3C10)")
    print("=" * 80)

    # The key sequence around 0x101B3ABF:
    # mov eax, [PathFinder_global]       ; a1 f0 43 37 10
    # push 1                             ; 6a 01
    # mov ecx, [eax+0x260]               ; 8b 88 60 02 00 00
    # push [esp+0x60]                    ; ff 74 24 60
    # mov eax, [ecx]                     ; 8b 01
    # call [eax+8]                       ; ff 50 08  -- vtable call

    # Let's annotate the bytes from 0x101B3AB0 onward
    start = 0x101B3AB0
    raw_s = va_to_raw(start)
    print(f"\n  Annotated disassembly around PathFinder calls:")
    # Print raw hex for reference
    for i in range(0, 160, 16):
        chunk = data[raw_s+i:raw_s+i+16]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {start+i:08X}  {hexpart:<48s}  {ascpart}")

    # ========================================================================
    # ProcessRLTD_flow: check the Recast navigation strings area
    # ========================================================================
    print("\n" + "=" * 80)
    print("  ProcessRLTD_flow: Recast/navigation strings in .rdata")
    print("=" * 80)
    # The strings found:
    strings_to_check = [
        (0x102e088c, "wt"),
        (0x102e08a0, "F:/temp/tq.obj"),
        (0x102e0894, "v %f %f %f\\n"),
        (0x102e08e4, "f %d %d %d\\n"),
        (0x102e09f8, "buildNavigation: Could not build heighfield layers."),
        (0x102e0a2c, "buildNavigation: Out of memory 'layerSet'."),
        (0x102e09a4, "buildNavigation: Could not erode."),
        (0x102e09c8, "buildNavigation: Could not build compact data."),
        (0x102e0944, "buildNavigation: Could not create solid heightfield."),
        (0x102e097c, "buildNavigation: Out of memory 'solid'."),
    ]
    # Read more strings around that area
    rdata_area_raw = va_to_raw(0x102e0880)
    print(f"\n  Strings in .rdata around 0x102e0880-0x102e0a80:")
    offset = 0
    while offset < 0x200:
        raw_pos = rdata_area_raw + offset
        if raw_pos >= len(data):
            break
        if data[raw_pos] == 0:
            offset += 1
            continue
        # Read string
        end = raw_pos
        while end < len(data) and data[end] != 0:
            end += 1
        s = data[raw_pos:end].decode('ascii', errors='replace')
        va = 0x102e0880 + offset
        print(f"    {va:#010x}: \"{s}\"")
        offset += (end - raw_pos) + 1

    # ========================================================================
    # Detailed look at 0x101f5260 - the "REC" function called from GetPathMeshRecast
    # ========================================================================
    print("\n" + "=" * 80)
    print("  Function 0x101f5260: REC section handler (called from GetPathMeshRecast)")
    print("=" * 80)
    raw_rec = va_to_raw(0x101f5260)
    # First 256 bytes hex
    for i in range(0, 256, 16):
        chunk = data[raw_rec+i:raw_rec+i+16]
        hexpart = ' '.join(f'{b:02x}' for b in chunk)
        ascpart = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {0x101f5260+i:08X}  {hexpart:<48s}  {ascpart}")

    # Find all calls in this function (assume ~0x1000 bytes)
    print(f"\n  Calls from 0x101f5260 (first 4096 bytes):")
    targets_of_interest = {
        0x101EA720: "PathFinder::AddMesh(PathMesh*)",
        0x101EA9B0: "PathFinder::AddMesh(PathMeshRecast*)",
        0x101EA7F0: "PathFinder::SetRecastMode",
        0x10195800: "GridPathMeshCalculator::CreateNavigationMesh",
    }
    for i in range(min(4096, len(data) - raw_rec - 4)):
        if data[raw_rec + i] == 0xE8:
            rel32 = struct.unpack_from('<i', data, raw_rec + i + 1)[0]
            target = 0x101f5260 + i + 5 + rel32
            tgt_rva = target - IMAGE_BASE
            if TEXT_RVA <= tgt_rva < TEXT_RVA + TEXT_SIZE:
                n = name_va(target)
                if n or target in targets_of_interest:
                    extra = f" = {n or targets_of_interest.get(target, '')}"
                else:
                    extra = ""
                print(f"    +{i:#06x} ({0x101f5260+i:#010x}): CALL {target:#010x}{extra}")

    # Also search for PathFinder global refs
    print(f"\n  PathFinder global refs in 0x101f5260:")
    pf_bytes = struct.pack('<I', 0x103743F0)
    for i in range(min(4096, len(data) - raw_rec - 3)):
        if data[raw_rec+i:raw_rec+i+4] == pf_bytes:
            ctx = data[raw_rec+max(0,i-2):raw_rec+min(i+8,4096)]
            print(f"    +{i:#06x} ({0x101f5260+i:#010x}): PathFinder_global ref, ctx={' '.join(f'{b:02x}' for b in ctx)}")

    # ========================================================================
    # Check 0x10264920 - another function called from GetPathMeshRecast
    # ========================================================================
    print("\n" + "=" * 80)
    print("  Function 0x10264920 (called from GetPathMeshRecast)")
    print("=" * 80)
    raw_f = va_to_raw(0x10264920)
    prologue = data[raw_f:raw_f+64]
    print(f"  Prologue: {' '.join(f'{b:02x}' for b in prologue)}")
    # Check for string refs
    for i in range(min(512, len(data) - raw_f - 3)):
        val = struct.unpack_from('<I', data, raw_f + i)[0]
        rva = val - IMAGE_BASE
        if RDATA_RVA <= rva < RDATA_RVA + 0x0c1c00:
            rdata_raw = RDATA_RAW + (rva - RDATA_RVA)
            if rdata_raw < len(data):
                end = rdata_raw
                while end < len(data) and data[end] != 0 and end < rdata_raw + 128:
                    end += 1
                s = data[rdata_raw:end].decode('ascii', errors='replace')
                if len(s) >= 3 and all(c < '\x7f' and c >= ' ' for c in s[:4]):
                    print(f"    +{i:#x}: str ref -> \"{s}\"")

    print("\n  Done.")

if __name__ == '__main__':
    main()
