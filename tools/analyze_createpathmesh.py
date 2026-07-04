"""Disassemble Level::CreatePathMesh and related functions from Engine.dll.
   Enhanced: larger scan, .rdata string resolution, IAT resolution, SSE-aware RET detection."""
import struct
import sys

DLL_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll"

IMAGE_BASE  = 0x10000000
TEXT_RVA    = 0x1000
TEXT_RAW    = 0x400
TEXT_SIZE   = 0x2aa800
RDATA_RVA   = 0x2ac000
RDATA_RAW   = 0x2aac00
RDATA_SIZE  = 0x0c1c00
DATA_RVA    = 0x36e000
DATA_RAW    = 0x36c800

KNOWN_SYMBOLS = {
    0x103743B8: "PathFinder_singleton",
    0x103743F0: "PathFinder_related_global",
    0x101EA720: "PathFinder::AddMesh(PathMesh*)",
    0x101EA9B0: "PathFinder::AddMesh(PathMeshRecast*)",
    0x101EA7F0: "PathFinder::SetRecastMode",
    0x101EA960: "PathFinder::GetPathEngine",
    0x101F4BA0: "ProcessRLTD",
    0x101F6100: "ProcessRLTD_init",
    0x101B1D00: "Level::CreatePathMesh",
    0x101EB3F0: "PathFinder::AddMesh_inner",
    0x101F0260: "PathMesh_compilation_orphan",
    0x101EE560: "PathFinder_func_1EE560",
    0x101FAFA0: "PathFinder_func_1FAFA0",
    0x1020BEC0: "PathFinder_func_20BEC0",
    0x10234DB0: "PathFinder_func_234DB0",
    0x10195800: "PathFinder_func_195800",
    0x101F8D00: "PathFinder_func_1F8D00",
    0x101F8C70: "PathFinder_func_1F8C70",
}

def va_to_file(va):
    """Convert VA to file offset, auto-detecting section."""
    rva = va - IMAGE_BASE
    if TEXT_RVA <= rva < TEXT_RVA + TEXT_SIZE:
        return rva - TEXT_RVA + TEXT_RAW
    elif RDATA_RVA <= rva < RDATA_RVA + RDATA_SIZE:
        return rva - RDATA_RVA + RDATA_RAW
    elif rva >= DATA_RVA:
        return rva - DATA_RVA + DATA_RAW
    else:
        return None

def is_rdata_va(va):
    rva = va - IMAGE_BASE
    return RDATA_RVA <= rva < RDATA_RVA + RDATA_SIZE

def is_data_va(va):
    rva = va - IMAGE_BASE
    return rva >= DATA_RVA

def is_text_va(va):
    rva = va - IMAGE_BASE
    return TEXT_RVA <= rva < TEXT_RVA + TEXT_SIZE

def read_string_at_va(data, va, max_len=200):
    off = va_to_file(va)
    if off is None or off < 0 or off >= len(data):
        return None
    end = min(off + max_len, len(data))
    s = []
    for i in range(off, end):
        b = data[i]
        if b == 0:
            break
        if 0x20 <= b < 0x7f:
            s.append(chr(b))
        else:
            return None  # not a printable string
    if len(s) < 2:
        return None
    return ''.join(s)

def read_dword_at_va(data, va):
    off = va_to_file(va)
    if off is None or off < 0 or off + 4 > len(data):
        return None
    return struct.unpack_from('<I', data, off)[0]

def hexdump(raw, base_va, count):
    lines = []
    for i in range(0, min(count, len(raw)), 16):
        hex_part = ' '.join(f'{raw[i+j]:02X}' if i+j < len(raw) else '  ' for j in range(16))
        ascii_part = ''.join(chr(raw[i+j]) if 0x20 <= raw[i+j] < 0x7f else '.' for j in range(16) if i+j < len(raw))
        lines.append(f'  {base_va+i:08X}  {hex_part}  {ascii_part}')
    return '\n'.join(lines)

def section_name(va):
    if is_rdata_va(va): return ".rdata"
    if is_data_va(va): return ".data"
    if is_text_va(va): return ".text"
    return "???"


def analyze_function(data, va_start, size, label="Function"):
    off_start = va_to_file(va_start)
    if off_start is None:
        print(f"\n  ERROR: Cannot map VA 0x{va_start:08X} to file offset")
        return
    raw = data[off_start:off_start+size]

    print(f"\n{'='*90}")
    print(f"  {label} @ 0x{va_start:08X}  (file offset 0x{off_start:X}, scanning {size} bytes)")
    print(f"{'='*90}")

    # Hex dump
    print(f"\nRaw hex ({min(size, len(raw))} bytes):")
    print(hexdump(raw, va_start, min(size, len(raw))))

    # Prologue check
    if len(raw) >= 3 and raw[0] == 0x55 and raw[1] == 0x8B and raw[2] == 0xEC:
        print(f"\n  Prologue: push ebp / mov ebp, esp (standard frame)")
    elif len(raw) >= 1 and raw[0] == 0x55:
        print(f"\n  Prologue: push ebp (followed by 0x{raw[1]:02X} 0x{raw[2]:02X})")
    elif len(raw) >= 1 and raw[0] in (0x53, 0x56, 0x57):
        regs = {0x53:'ebx',0x56:'esi',0x57:'edi'}
        print(f"\n  Prologue: push {regs.get(raw[0],'?')} (non-standard)")
    elif len(raw) >= 2 and raw[0] == 0x6A:
        print(f"\n  Prologue: push 0x{raw[1]:02X} (SEH setup, no frame pointer)")
    elif len(raw) >= 2 and raw[0] == 0x8B:
        regs32 = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
        modrm = raw[1]
        src_reg = modrm & 7
        dst_reg = (modrm >> 3) & 7
        print(f"\n  Prologue: mov {regs32[dst_reg]}, {regs32[src_reg]} (thunk/forwarder)")
    else:
        print(f"\n  Prologue: 0x{raw[0]:02X} 0x{raw[1]:02X} (unrecognized)")

    # Find function end by looking for CC CC padding (INT3 padding between functions)
    func_end = None
    for i in range(16, len(raw) - 3):
        if raw[i] == 0xCC and raw[i+1] == 0xCC and raw[i+2] == 0xCC:
            # Walk backward to find the last real instruction
            func_end = i
            break
    if func_end:
        print(f"  Function ends at ~0x{va_start+func_end:08X} (size ~0x{func_end:X} = {func_end} bytes)")

    # Collect all findings
    calls = []
    refs = []
    rets = []
    jmps = []
    cond_jmps = []
    strings_found = []
    indirect_calls = []

    i = 0
    while i < len(raw) - 4:
        b = raw[i]

        # ---- Skip known multi-byte prefixes to avoid false positives ----
        # F3 0F = SSE prefix -- skip the whole SSE instruction
        if b == 0xF3 and i+1 < len(raw) and raw[i+1] == 0x0F:
            # SSE instruction: F3 0F xx [modrm] ...
            # Most are 3-4 bytes minimum, but with modrm can be longer
            # Skip at least 3 bytes, then skip modrm displacement
            if i+3 < len(raw):
                modrm = raw[i+2]  # This is actually the opcode byte for SSE
                # The real modrm is at i+3
                if i+4 < len(raw):
                    real_modrm = raw[i+3]
                    mod = (real_modrm >> 6) & 3
                    rm = real_modrm & 7
                    instr_len = 4  # F3 0F op modrm
                    if mod == 0 and rm == 5:
                        instr_len += 4  # disp32
                    elif mod == 0 and rm == 4:
                        instr_len += 1  # SIB
                    elif mod == 1:
                        instr_len += 1  # disp8
                        if rm == 4: instr_len += 1  # SIB
                    elif mod == 2:
                        instr_len += 4  # disp32
                        if rm == 4: instr_len += 1  # SIB
                    i += instr_len
                    continue
            i += 3
            continue

        # 66 0F = operand size prefix + two-byte opcode
        if b == 0x66 and i+1 < len(raw) and raw[i+1] == 0x0F:
            if i+4 < len(raw):
                real_modrm = raw[i+3]
                mod = (real_modrm >> 6) & 3
                rm = real_modrm & 7
                instr_len = 4  # 66 0F op modrm
                if mod == 0 and rm == 5:
                    instr_len += 4
                elif mod == 0 and rm == 4:
                    instr_len += 1
                elif mod == 1:
                    instr_len += 1
                    if rm == 4: instr_len += 1
                elif mod == 2:
                    instr_len += 4
                    if rm == 4: instr_len += 1
                i += instr_len
                continue
            i += 3
            continue

        # 0F 5B, 0F 2F, 0F 57, 0F 5A, 0F 2C etc = SSE without prefix
        if b == 0x0F and i+1 < len(raw):
            op2 = raw[i+1]
            # Two-byte opcode: 0F xx modrm
            if i+3 < len(raw):
                # Conditional jumps: 0F 80-8F rel32
                if 0x80 <= op2 <= 0x8F and i+6 <= len(raw):
                    rel = struct.unpack_from('<i', raw, i+2)[0]
                    target = va_start + i + 6 + rel
                    jcc_names = ['jo','jno','jb','jnb','jz','jnz','jbe','ja',
                                 'js','jns','jp','jnp','jl','jge','jle','jg']
                    cond_jmps.append((va_start+i, target, jcc_names[op2-0x80]))
                    i += 6
                    continue
                # Other 0F instructions with modrm
                if 0x10 <= op2 <= 0x7F or 0xA0 <= op2 <= 0xFE:
                    real_modrm = raw[i+2]
                    mod = (real_modrm >> 6) & 3
                    rm = real_modrm & 7
                    instr_len = 3
                    if mod == 0 and rm == 5:
                        instr_len += 4
                    elif mod == 0 and rm == 4:
                        instr_len += 1
                    elif mod == 1:
                        instr_len += 1
                        if rm == 4: instr_len += 1
                    elif mod == 2:
                        instr_len += 4
                        if rm == 4: instr_len += 1
                    # Check for movss/movsd with disp32 referencing .rdata
                    if mod == 0 and rm == 5 and instr_len >= 7:
                        addr = struct.unpack_from('<I', raw, i+3)[0]
                        if addr >= IMAGE_BASE and addr < IMAGE_BASE + 0x400000:
                            refs.append((va_start+i, f"SSE op with [0x{addr:08X}]", addr, KNOWN_SYMBOLS.get(addr,"")))
                    i += instr_len
                    continue
            i += 2
            continue

        # F2 0F = SSE2 prefix
        if b == 0xF2 and i+1 < len(raw) and raw[i+1] == 0x0F:
            if i+4 < len(raw):
                real_modrm = raw[i+3]
                mod = (real_modrm >> 6) & 3
                rm = real_modrm & 7
                instr_len = 4
                if mod == 0 and rm == 5:
                    instr_len += 4
                elif mod == 0 and rm == 4:
                    instr_len += 1
                elif mod == 1:
                    instr_len += 1
                    if rm == 4: instr_len += 1
                elif mod == 2:
                    instr_len += 4
                    if rm == 4: instr_len += 1
                i += instr_len
                continue
            i += 3
            continue

        # E8 rel32 = CALL
        if b == 0xE8 and i + 5 <= len(raw):
            rel = struct.unpack_from('<i', raw, i+1)[0]
            target = va_start + i + 5 + rel
            # Sanity: target should be in .text
            if IMAGE_BASE < target < IMAGE_BASE + 0x400000:
                sym = KNOWN_SYMBOLS.get(target, "")
                calls.append((va_start + i, target, sym))
            i += 5
            continue

        # E9 rel32 = JMP
        if b == 0xE9 and i + 5 <= len(raw):
            rel = struct.unpack_from('<i', raw, i+1)[0]
            target = va_start + i + 5 + rel
            if IMAGE_BASE < target < IMAGE_BASE + 0x400000:
                sym = KNOWN_SYMBOLS.get(target, "")
                jmps.append((va_start + i, target, sym))
            i += 5
            continue

        # Short conditional jumps: 70-7F rel8
        if 0x70 <= b <= 0x7F and i+2 <= len(raw):
            rel = struct.unpack_from('<b', raw, i+1)[0]
            target = va_start + i + 2 + rel
            jcc_names = ['jo','jno','jb','jnb','jz','jnz','jbe','ja',
                         'js','jns','jp','jnp','jl','jge','jle','jg']
            cond_jmps.append((va_start+i, target, jcc_names[b-0x70]))
            i += 2
            continue

        # EB rel8 = JMP short
        if b == 0xEB and i+2 <= len(raw):
            rel = struct.unpack_from('<b', raw, i+1)[0]
            target = va_start + i + 2 + rel
            jmps.append((va_start+i, target, "short"))
            i += 2
            continue

        # FF /2 = CALL [mem], FF /4 = JMP [mem]
        if b == 0xFF and i+1 < len(raw):
            modrm = raw[i+1]
            reg_field = (modrm >> 3) & 7
            mod = (modrm >> 6) & 3
            rm = modrm & 7
            if reg_field in (2, 4):  # CALL or JMP indirect
                if mod == 0 and rm == 5 and i+6 <= len(raw):
                    addr = struct.unpack_from('<I', raw, i+2)[0]
                    sym = KNOWN_SYMBOLS.get(addr, "")
                    # Try to resolve the IAT entry
                    iat_target = read_dword_at_va(data, addr)
                    iat_info = ""
                    if iat_target:
                        iat_info = f" -> IAT target 0x{iat_target:08X}"
                    op = "CALL" if reg_field == 2 else "JMP"
                    indirect_calls.append((va_start+i, addr, f"{op} [{addr:#010x}]{sym}{iat_info}"))
                    i += 6
                    continue
                # Other mod/rm combinations
                instr_len = 2
                if mod == 1: instr_len += 1
                elif mod == 2: instr_len += 4
                if rm == 4: instr_len += 1  # SIB
                i += instr_len
                continue

        # C3 = RET
        if b == 0xC3:
            rets.append(va_start + i)
            i += 1
            continue
        # C2 xx xx = RETN imm16
        if b == 0xC2 and i+3 <= len(raw):
            imm16 = struct.unpack_from('<H', raw, i+1)[0]
            rets.append((va_start + i, imm16))
            i += 3
            continue

        # MOV reg, imm32 (B8-BF)
        if 0xB8 <= b <= 0xBF and i+5 <= len(raw):
            imm = struct.unpack_from('<I', raw, i+1)[0]
            regs32 = {0xB8:'eax',0xB9:'ecx',0xBA:'edx',0xBB:'ebx',0xBC:'esp',0xBD:'ebp',0xBE:'esi',0xBF:'edi'}
            if imm >= IMAGE_BASE and imm < IMAGE_BASE + 0x400000:
                sym = KNOWN_SYMBOLS.get(imm, "")
                refs.append((va_start+i, f"mov {regs32[b]}, 0x{imm:08X}", imm, sym))
                s = read_string_at_va(data, imm)
                if s:
                    strings_found.append((va_start+i, imm, s))
            i += 5
            continue

        # PUSH imm32 (68)
        if b == 0x68 and i+5 <= len(raw):
            imm = struct.unpack_from('<I', raw, i+1)[0]
            if imm >= IMAGE_BASE and imm < IMAGE_BASE + 0x400000:
                sym = KNOWN_SYMBOLS.get(imm, "")
                refs.append((va_start+i, f"push 0x{imm:08X}", imm, sym))
                s = read_string_at_va(data, imm)
                if s:
                    strings_found.append((va_start+i, imm, s))
            i += 5
            continue

        # A1 = MOV EAX, [addr]
        if b == 0xA1 and i+5 <= len(raw):
            addr = struct.unpack_from('<I', raw, i+1)[0]
            if addr >= IMAGE_BASE and addr < IMAGE_BASE + 0x400000:
                sym = KNOWN_SYMBOLS.get(addr, "")
                refs.append((va_start+i, f"mov eax, [0x{addr:08X}]", addr, sym))
                s = read_string_at_va(data, addr)
                if s:
                    strings_found.append((va_start+i, addr, s))
            i += 5
            continue

        # A3 = MOV [addr], EAX
        if b == 0xA3 and i+5 <= len(raw):
            addr = struct.unpack_from('<I', raw, i+1)[0]
            if addr >= IMAGE_BASE and addr < IMAGE_BASE + 0x400000:
                sym = KNOWN_SYMBOLS.get(addr, "")
                refs.append((va_start+i, f"mov [0x{addr:08X}], eax", addr, sym))
            i += 5
            continue

        # 8B/89/3B/39 with mod=00 rm=5 (disp32)
        if b in (0x8B, 0x89, 0x3B, 0x39) and i+6 <= len(raw):
            modrm = raw[i+1]
            mod = (modrm >> 6) & 3
            rm = modrm & 7
            reg_field = (modrm >> 3) & 7
            regs32 = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            if mod == 0 and rm == 5:
                addr = struct.unpack_from('<I', raw, i+2)[0]
                if addr >= IMAGE_BASE and addr < IMAGE_BASE + 0x400000:
                    sym = KNOWN_SYMBOLS.get(addr, "")
                    ops = {0x8B: f"mov {regs32[reg_field]}, [0x{addr:08X}]",
                           0x89: f"mov [0x{addr:08X}], {regs32[reg_field]}",
                           0x3B: f"cmp {regs32[reg_field]}, [0x{addr:08X}]",
                           0x39: f"cmp [0x{addr:08X}], {regs32[reg_field]}"}
                    refs.append((va_start+i, ops[b], addr, sym))
                    s = read_string_at_va(data, addr)
                    if s:
                        strings_found.append((va_start+i, addr, s))
                i += 6
                continue

        # 83 3D [addr] imm8 = CMP dword [addr], imm8
        if b == 0x83 and i+7 <= len(raw):
            modrm = raw[i+1]
            mod = (modrm >> 6) & 3
            rm = modrm & 7
            reg_field = (modrm >> 3) & 7
            if mod == 0 and rm == 5:
                addr = struct.unpack_from('<I', raw, i+2)[0]
                if addr >= IMAGE_BASE and addr < IMAGE_BASE + 0x400000:
                    imm8 = raw[i+6]
                    ops8 = ['add','or','adc','sbb','and','sub','xor','cmp']
                    sym = KNOWN_SYMBOLS.get(addr, "")
                    refs.append((va_start+i, f"{ops8[reg_field]} dword [0x{addr:08X}], 0x{imm8:02X}", addr, sym))
                i += 7
                continue

        # C7 05 [addr] [imm32] = MOV dword [addr], imm32
        if b == 0xC7 and i+10 <= len(raw):
            modrm = raw[i+1]
            mod = (modrm >> 6) & 3
            rm = modrm & 7
            reg_field = (modrm >> 3) & 7
            if mod == 0 and rm == 5 and reg_field == 0:
                addr = struct.unpack_from('<I', raw, i+2)[0]
                imm32 = struct.unpack_from('<I', raw, i+6)[0]
                if addr >= IMAGE_BASE and addr < IMAGE_BASE + 0x400000:
                    sym = KNOWN_SYMBOLS.get(addr, "")
                    refs.append((va_start+i, f"mov dword [0x{addr:08X}], 0x{imm32:08X}", addr, sym))
                    if imm32 >= IMAGE_BASE and imm32 < IMAGE_BASE + 0x400000:
                        sym2 = KNOWN_SYMBOLS.get(imm32, "")
                        refs.append((va_start+i, f"  (imm value -> 0x{imm32:08X})", imm32, sym2))
                i += 10
                continue

        i += 1

    # Print results
    print(f"\n  CALL instructions ({len(calls)}):")
    for loc, target, sym in calls:
        sym_str = f"  <- {sym}" if sym else ""
        print(f"    {loc:#010x}: CALL {target:#010x}{sym_str}")

    print(f"\n  Indirect CALL/JMP instructions ({len(indirect_calls)}):")
    for loc, addr, desc in indirect_calls:
        print(f"    {loc:#010x}: {desc}")

    print(f"\n  JMP instructions ({len(jmps)}):")
    for loc, target, sym in jmps:
        sym_str = f"  <- {sym}" if sym else ""
        print(f"    {loc:#010x}: JMP {target:#010x}{sym_str}")

    if cond_jmps:
        print(f"\n  Conditional jumps ({len(cond_jmps)}):")
        for loc, target, name in cond_jmps:
            print(f"    {loc:#010x}: {name} {target:#010x}")

    print(f"\n  Address references ({len(refs)}):")
    for loc, desc, addr, sym in refs:
        sym_str = f"  <- {sym}" if sym else ""
        sec = section_name(addr)
        print(f"    {loc:#010x}: {desc}  [{sec}]{sym_str}")

    print(f"\n  String references ({len(strings_found)}):")
    for loc, addr, s in strings_found:
        print(f"    {loc:#010x}: {addr:#010x} -> \"{s}\"")

    print(f"\n  RET/RETN instructions ({len(rets)}):")
    for r in rets:
        if isinstance(r, tuple):
            print(f"    {r[0]:#010x}: retn {r[1]:#06x}")
        else:
            print(f"    {r:#010x}: ret")

    return calls, refs, strings_found, rets


def main():
    print("Reading Engine.dll...")
    with open(DLL_PATH, 'rb') as f:
        data = f.read()
    print(f"  File size: {len(data)} bytes (0x{len(data):X})")

    # ---- 1. Level::CreatePathMesh ----
    # This is a big function; scan 2048 bytes
    analyze_function(data, 0x101B1D00, 2048, "Level::CreatePathMesh")

    # Also scan the continuation (in case it's > 2048 bytes)
    # Check if there's CC padding at 2048
    off = va_to_file(0x101B1D00 + 2048)
    if data[off] != 0xCC:
        print("\n  [NOTE: Function extends beyond 2048 bytes, scanning more...]")
        analyze_function(data, 0x101B1D00 + 2048, 2048, "Level::CreatePathMesh (continued)")

    # ---- 2. PathFinder::AddMesh(PathMesh*) forwarder ----
    analyze_function(data, 0x101EA720, 16, "PathFinder::AddMesh(PathMesh*) [forwarder]")

    # ---- 3. The inner AddMesh at 0x101EB3F0 ----
    analyze_function(data, 0x101EB3F0, 512, "PathFinder::AddMesh_inner @ 0x101EB3F0")

    # ---- 4. PathFinder::AddMesh(PathMeshRecast*) ----
    analyze_function(data, 0x101EA9B0, 16, "PathFinder::AddMesh(PathMeshRecast*) [forwarder]")

    # ---- 5. PathFinder::SetRecastMode ----
    analyze_function(data, 0x101EA7F0, 128, "PathFinder::SetRecastMode")

    # ---- 6. PathFinder::GetPathEngine ----
    analyze_function(data, 0x101EA960, 16, "PathFinder::GetPathEngine")

    # ---- 7. Orphaned PathMesh compilation function ----
    analyze_function(data, 0x101F0260, 1024, "PathMesh compilation (orphaned) @ 0x101F0260")

    # ---- 8. ProcessRLTD ----
    analyze_function(data, 0x101F4BA0, 1536, "ProcessRLTD @ 0x101F4BA0")

    # ---- 9. ProcessRLTD init ----
    analyze_function(data, 0x101F6100, 512, "ProcessRLTD_init @ 0x101F6100")

    # ---- Bonus: resolve the SEH handler / .rdata push targets ----
    print(f"\n{'='*90}")
    print("  Resolving .rdata push targets (SEH unwind info)")
    print(f"{'='*90}")
    for addr in [0x1029BD3A, 0x102A1212, 0x102A1235, 0x102A189B, 0x102A1BA2,
                 0x102A1118, 0x102A1135]:
        s = read_string_at_va(data, addr)
        if s:
            print(f"  {addr:#010x} -> \"{s}\"")
        else:
            # Read raw bytes
            off = va_to_file(addr)
            if off and off+16 <= len(data):
                raw = data[off:off+16]
                print(f"  {addr:#010x} -> raw: {' '.join(f'{b:02X}' for b in raw)} (SEH scope table entry)")

    # ---- Bonus: resolve IAT entries at 0x102AC17C and 0x102AC178 ----
    print(f"\n{'='*90}")
    print("  Resolving IAT entries")
    print(f"{'='*90}")
    for iat_addr in [0x102AC178, 0x102AC17C, 0x102AC2FC]:
        target = read_dword_at_va(data, iat_addr)
        if target:
            # These are typically in the import section; try to find import name
            # Read a few nearby bytes in .rdata to find the import name
            print(f"  IAT {iat_addr:#010x} -> {target:#010x}")
            # Try to find the import hint/name entry
            # For loaded DLL these would be resolved; in file they point to IMAGE_IMPORT_BY_NAME
            if target >= IMAGE_BASE and target < IMAGE_BASE + 0x400000:
                off = va_to_file(target)
                if off and off+2+64 <= len(data):
                    hint = struct.unpack_from('<H', data, off)[0]
                    name = read_string_at_va(data, target + 2)
                    if name:
                        print(f"    -> Import: hint={hint}, name=\"{name}\"")

    print("\n\nDone.")

if __name__ == '__main__':
    main()
