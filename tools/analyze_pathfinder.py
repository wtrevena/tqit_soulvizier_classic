"""Analyze PathFinder, PathMesh, PathMeshRecast class layouts in Engine.dll."""
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

def va_to_raw(va):
    """Convert virtual address to raw file offset."""
    rva = va - IMAGE_BASE
    if TEXT_RVA <= rva < TEXT_RVA + TEXT_SIZE:
        return rva - TEXT_RVA + TEXT_RAW
    elif RDATA_RVA <= rva < RDATA_RVA + RDATA_SIZE:
        return rva - RDATA_RVA + RDATA_RAW
    elif rva >= DATA_RVA:
        return rva - DATA_RVA + DATA_RAW
    else:
        return None

def raw_to_va(raw):
    """Convert raw file offset to VA (approximate, for .text)."""
    if TEXT_RAW <= raw < TEXT_RAW + TEXT_SIZE:
        return raw - TEXT_RAW + TEXT_RVA + IMAGE_BASE
    elif RDATA_RAW <= raw < RDATA_RAW + RDATA_SIZE:
        return raw - RDATA_RAW + RDATA_RVA + IMAGE_BASE
    elif raw >= DATA_RAW:
        return raw - DATA_RAW + DATA_RVA + IMAGE_BASE
    return None

def hexdump(data, base_va, width=16):
    """Pretty hex dump."""
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"  {base_va+i:08X}: {hex_part:<{width*3}}  {ascii_part}")
    return '\n'.join(lines)

def disasm_simple(data, base_va):
    """Very basic x86 disassembly hints for common patterns."""
    notes = []
    i = 0
    while i < len(data):
        va = base_va + i
        b = data[i]

        # mov ecx, [ecx+N] or similar
        if i + 2 < len(data) and data[i] == 0x8B:
            modrm = data[i+1]
            mod = (modrm >> 6) & 3
            reg = (modrm >> 3) & 7
            rm = modrm & 7
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            if mod == 1 and i + 3 <= len(data):  # [reg+disp8]
                disp = data[i+2]
                notes.append(f"  {va:08X}: mov {reg_names[reg]}, [{reg_names[rm]}+0x{disp:02X}]")
                i += 3
                continue
            elif mod == 2 and i + 6 <= len(data):  # [reg+disp32]
                disp = struct.unpack_from('<I', data, i+2)[0]
                notes.append(f"  {va:08X}: mov {reg_names[reg]}, [{reg_names[rm]}+0x{disp:X}]")
                i += 6
                continue
            elif mod == 0 and rm == 5 and i + 6 <= len(data):  # [disp32]
                disp = struct.unpack_from('<I', data, i+2)[0]
                notes.append(f"  {va:08X}: mov {reg_names[reg]}, [0x{disp:08X}]")
                i += 6
                continue

        # jmp [ecx+N] or call [ecx+N]
        if i + 2 < len(data) and data[i] == 0xFF:
            modrm = data[i+1]
            mod = (modrm >> 6) & 3
            op = (modrm >> 3) & 7  # 2=call, 4=jmp
            rm = modrm & 7
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            op_name = {2: 'call', 4: 'jmp'}.get(op, f'ff/{op}')
            if mod == 1 and i + 3 <= len(data):
                disp = data[i+2]
                notes.append(f"  {va:08X}: {op_name} [{reg_names[rm]}+0x{disp:02X}]")
                i += 3
                continue
            elif mod == 2 and i + 6 <= len(data):
                disp = struct.unpack_from('<I', data, i+2)[0]
                notes.append(f"  {va:08X}: {op_name} [{reg_names[rm]}+0x{disp:X}]")
                i += 6
                continue

        # call rel32
        if b == 0xE8 and i + 5 <= len(data):
            rel = struct.unpack_from('<i', data, i+1)[0]
            target = va + 5 + rel
            notes.append(f"  {va:08X}: call 0x{target:08X}")
            i += 5
            continue

        # jmp rel32
        if b == 0xE9 and i + 5 <= len(data):
            rel = struct.unpack_from('<i', data, i+1)[0]
            target = va + 5 + rel
            notes.append(f"  {va:08X}: jmp 0x{target:08X}")
            i += 5
            continue

        # jmp rel8
        if b == 0xEB and i + 2 <= len(data):
            rel = struct.unpack_from('<b', data, i+1)[0]
            target = va + 2 + rel
            notes.append(f"  {va:08X}: jmp short 0x{target:08X}")
            i += 2
            continue

        # jcc rel8
        if 0x70 <= b <= 0x7F and i + 2 <= len(data):
            cc_names = ['jo','jno','jb','jnb','jz','jnz','jbe','ja',
                       'js','jns','jp','jnp','jl','jnl','jle','jnle']
            rel = struct.unpack_from('<b', data, i+1)[0]
            target = va + 2 + rel
            notes.append(f"  {va:08X}: {cc_names[b-0x70]} short 0x{target:08X}")
            i += 2
            continue

        # jcc rel32 (0F 8x)
        if b == 0x0F and i + 6 <= len(data) and 0x80 <= data[i+1] <= 0x8F:
            cc_names = ['jo','jno','jb','jnb','jz','jnz','jbe','ja',
                       'js','jns','jp','jnp','jl','jnl','jle','jnle']
            rel = struct.unpack_from('<i', data, i+2)[0]
            target = va + 6 + rel
            notes.append(f"  {va:08X}: {cc_names[data[i+1]-0x80]} 0x{target:08X}")
            i += 6
            continue

        # ret
        if b == 0xC3:
            notes.append(f"  {va:08X}: ret")
            i += 1
            continue
        if b == 0xC2 and i + 3 <= len(data):
            imm = struct.unpack_from('<H', data, i+1)[0]
            notes.append(f"  {va:08X}: ret 0x{imm:X}")
            i += 3
            continue

        # push reg
        if 0x50 <= b <= 0x57:
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            notes.append(f"  {va:08X}: push {reg_names[b-0x50]}")
            i += 1
            continue

        # pop reg
        if 0x58 <= b <= 0x5F:
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            notes.append(f"  {va:08X}: pop {reg_names[b-0x58]}")
            i += 1
            continue

        # push imm32
        if b == 0x68 and i + 5 <= len(data):
            imm = struct.unpack_from('<I', data, i+1)[0]
            notes.append(f"  {va:08X}: push 0x{imm:08X}")
            i += 5
            continue

        # push imm8
        if b == 0x6A and i + 2 <= len(data):
            imm = data[i+1]
            notes.append(f"  {va:08X}: push 0x{imm:02X}")
            i += 2
            continue

        # test/cmp with modrm
        if b == 0x85 and i + 2 <= len(data):
            modrm = data[i+1]
            mod = (modrm >> 6) & 3
            reg = (modrm >> 3) & 7
            rm = modrm & 7
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            if mod == 3:
                notes.append(f"  {va:08X}: test {reg_names[rm]}, {reg_names[reg]}")
                i += 2
                continue

        # cmp [reg+disp8], imm8 (83 /7)
        if b == 0x83 and i + 3 <= len(data):
            modrm = data[i+1]
            mod = (modrm >> 6) & 3
            op = (modrm >> 3) & 7
            rm = modrm & 7
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            op_names = ['add','or','adc','sbb','and','sub','xor','cmp']
            if mod == 1:
                disp = data[i+2]
                imm = struct.unpack_from('<b', data, i+3)[0]
                notes.append(f"  {va:08X}: {op_names[op]} dword [{reg_names[rm]}+0x{disp:02X}], 0x{imm & 0xFF:02X}")
                i += 4
                continue
            elif mod == 3:
                imm = struct.unpack_from('<b', data, i+2)[0]
                notes.append(f"  {va:08X}: {op_names[op]} {reg_names[rm]}, 0x{imm & 0xFF:02X}")
                i += 3
                continue

        # xor reg,reg
        if b == 0x33 and i + 2 <= len(data):
            modrm = data[i+1]
            if (modrm >> 6) == 3:
                reg = (modrm >> 3) & 7
                rm = modrm & 7
                reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
                notes.append(f"  {va:08X}: xor {reg_names[reg]}, {reg_names[rm]}")
                i += 2
                continue

        # lea
        if b == 0x8D and i + 2 <= len(data):
            modrm = data[i+1]
            mod = (modrm >> 6) & 3
            reg = (modrm >> 3) & 7
            rm = modrm & 7
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            if mod == 1:
                disp = data[i+2]
                notes.append(f"  {va:08X}: lea {reg_names[reg]}, [{reg_names[rm]}+0x{disp:02X}]")
                i += 3
                continue
            elif mod == 2 and i + 6 <= len(data):
                disp = struct.unpack_from('<I', data, i+2)[0]
                notes.append(f"  {va:08X}: lea {reg_names[reg]}, [{reg_names[rm]}+0x{disp:X}]")
                i += 6
                continue

        # mov reg, imm32
        if 0xB8 <= b <= 0xBF and i + 5 <= len(data):
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            imm = struct.unpack_from('<I', data, i+1)[0]
            notes.append(f"  {va:08X}: mov {reg_names[b-0xB8]}, 0x{imm:08X}")
            i += 5
            continue

        # sub esp, N
        if b == 0x81 and i + 6 <= len(data):
            modrm = data[i+1]
            op = (modrm >> 3) & 7
            rm = modrm & 7
            mod = (modrm >> 6) & 3
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            op_names = ['add','or','adc','sbb','and','sub','xor','cmp']
            if mod == 3:
                imm = struct.unpack_from('<I', data, i+2)[0]
                notes.append(f"  {va:08X}: {op_names[op]} {reg_names[rm]}, 0x{imm:X}")
                i += 6
                continue

        # mov [reg+disp8], reg  (89 /r)
        if b == 0x89 and i + 2 <= len(data):
            modrm = data[i+1]
            mod = (modrm >> 6) & 3
            reg = (modrm >> 3) & 7
            rm = modrm & 7
            reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
            if mod == 1 and i + 3 <= len(data):
                disp = data[i+2]
                notes.append(f"  {va:08X}: mov [{reg_names[rm]}+0x{disp:02X}], {reg_names[reg]}")
                i += 3
                continue
            elif mod == 3:
                notes.append(f"  {va:08X}: mov {reg_names[rm]}, {reg_names[reg]}")
                i += 2
                continue

        i += 1

    return '\n'.join(notes)


def main():
    with open(DLL_PATH, 'rb') as f:
        dll = f.read()

    print("=" * 80)
    print("ENGINE.DLL PathFinder / PathMesh / PathMeshRecast Analysis")
    print("=" * 80)

    # =========================================================================
    # 1. PathFinder::FindPath at VA 0x101EA6C0
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. PathFinder::FindPath @ 0x101EA6C0")
    print("=" * 80)

    va = 0x101EA6C0
    raw = va_to_raw(va)
    data = dll[raw:raw+64]
    print(f"\nFirst 64 bytes (raw offset 0x{raw:X}):")
    print(hexdump(data, va))
    print(f"\nDisassembly hints:")
    print(disasm_simple(data, va))

    # Try to trace the forwarding - look for mov ecx,[ecx+4] then jmp [eax+N]
    # or call to another function
    print(f"\n--- Tracing forwarding ---")
    # Look for call/jmp targets in the first 64 bytes
    for i in range(len(data)):
        if data[i] == 0xE9 and i + 5 <= len(data):  # jmp rel32
            rel = struct.unpack_from('<i', data, i+1)[0]
            target = va + i + 5 + rel
            print(f"  Found jmp to 0x{target:08X} at offset +{i}")
            # Read target
            traw = va_to_raw(target)
            if traw:
                tdata = dll[traw:traw+512]
                print(f"\n  Target function at 0x{target:08X} (first 512 bytes):")
                print(hexdump(tdata, target))
                print(f"\n  Disassembly hints:")
                print(disasm_simple(tdata, target))
        if data[i] == 0xE8 and i + 5 <= len(data):  # call rel32
            rel = struct.unpack_from('<i', data, i+1)[0]
            target = va + i + 5 + rel
            print(f"  Found call to 0x{target:08X} at offset +{i}")

    # Also check if it's a vtable dispatch (mov eax,[ecx]; jmp [eax+N])
    # Check for pattern: mov ecx,[ecx+4]; mov eax,[ecx]; jmp [eax+N]
    print(f"\n--- Looking for vtable dispatch pattern ---")
    for i in range(min(len(data)-5, 30)):
        # FF 20 = jmp [eax], FF 60 XX = jmp [eax+XX]
        if data[i] == 0xFF:
            modrm = data[i+1]
            op = (modrm >> 3) & 7
            if op == 4:  # jmp indirect
                mod = (modrm >> 6) & 3
                rm = modrm & 7
                reg_names = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
                if mod == 0:
                    print(f"  jmp [{reg_names[rm]}] at +{i} (VA 0x{va+i:08X})")
                elif mod == 1:
                    disp = data[i+2]
                    print(f"  jmp [{reg_names[rm]}+0x{disp:02X}] at +{i} (VA 0x{va+i:08X})")
                    print(f"  => vtable slot {disp//4}")

    # Now dump a larger block starting from FindPath to understand the full flow
    print(f"\n--- Extended dump (512 bytes from FindPath) ---")
    data512 = dll[raw:raw+512]
    print(hexdump(data512, va))
    print(f"\nDisassembly:")
    print(disasm_simple(data512, va))

    # =========================================================================
    # 2. Exported functions containing "PathMesh"
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. Exported functions containing 'PathMesh'")
    print("=" * 80)

    # Parse PE export table
    pe_sig_off = struct.unpack_from('<I', dll, 0x3C)[0]
    # Optional header starts at pe_sig_off + 4 (sig) + 20 (file header)
    opt_hdr_off = pe_sig_off + 4 + 20
    # Export table RVA is first data directory entry
    # Data directories start at opt_hdr_off + 96 (for PE32)
    num_rva_sizes = struct.unpack_from('<I', dll, opt_hdr_off + 92)[0]
    export_rva = struct.unpack_from('<I', dll, opt_hdr_off + 96)[0]
    export_size = struct.unpack_from('<I', dll, opt_hdr_off + 100)[0]

    export_raw = va_to_raw(export_rva + IMAGE_BASE)

    # Parse export directory
    num_functions = struct.unpack_from('<I', dll, export_raw + 20)[0]
    num_names = struct.unpack_from('<I', dll, export_raw + 24)[0]
    addr_table_rva = struct.unpack_from('<I', dll, export_raw + 28)[0]
    name_ptr_rva = struct.unpack_from('<I', dll, export_raw + 32)[0]
    ordinal_table_rva = struct.unpack_from('<I', dll, export_raw + 36)[0]

    addr_table_raw = va_to_raw(addr_table_rva + IMAGE_BASE)
    name_ptr_raw = va_to_raw(name_ptr_rva + IMAGE_BASE)
    ordinal_table_raw = va_to_raw(ordinal_table_rva + IMAGE_BASE)

    pathmesh_exports = []
    for i in range(num_names):
        name_rva = struct.unpack_from('<I', dll, name_ptr_raw + i*4)[0]
        name_raw = va_to_raw(name_rva + IMAGE_BASE)
        # Read null-terminated string
        end = dll.index(b'\x00', name_raw)
        name = dll[name_raw:end].decode('ascii', errors='replace')

        if 'PathMesh' in name:
            ordinal = struct.unpack_from('<H', dll, ordinal_table_raw + i*2)[0]
            func_rva = struct.unpack_from('<I', dll, addr_table_raw + ordinal*4)[0]
            func_va = func_rva + IMAGE_BASE
            pathmesh_exports.append((name, func_va))

    print(f"\nFound {len(pathmesh_exports)} exports with 'PathMesh':\n")
    for name, func_va in sorted(pathmesh_exports, key=lambda x: x[1]):
        func_raw = va_to_raw(func_va)
        if func_raw is None:
            print(f"  {func_va:08X}: {name} (raw offset not in known section)")
            continue
        first16 = dll[func_raw:func_raw+16]
        hex_str = ' '.join(f'{b:02X}' for b in first16)

        # Classify as REAL or STUB
        is_stub = False
        stub_info = ""
        if first16[0] == 0xC3:
            is_stub = True
            stub_info = "ret"
        elif first16[0] == 0xC2:
            imm = struct.unpack_from('<H', first16, 1)[0]
            is_stub = True
            stub_info = f"ret 0x{imm:X}"
        elif first16[0] == 0x33 and first16[1] == 0xC0 and first16[2] == 0xC3:
            is_stub = True
            stub_info = "xor eax,eax; ret"
        elif first16[0] == 0x33 and first16[1] == 0xC0 and first16[2] == 0xC2:
            imm = struct.unpack_from('<H', first16, 3)[0]
            is_stub = True
            stub_info = f"xor eax,eax; ret 0x{imm:X}"
        elif first16[0] == 0xB8 and first16[5] == 0xC3:
            imm = struct.unpack_from('<I', first16, 1)[0]
            is_stub = True
            stub_info = f"mov eax,0x{imm:X}; ret"

        # Estimate size for real functions (scan for next function prologue or INT3 padding)
        size_est = "?"
        if not is_stub:
            # Look for CC CC or next push ebp; mov ebp,esp
            for j in range(16, 4096):
                if func_raw + j + 2 >= len(dll):
                    break
                # CC padding followed by push ebp
                if dll[func_raw+j] == 0xCC and dll[func_raw+j+1] == 0xCC:
                    size_est = f"~{j} bytes"
                    break
                # Another common end: ret followed by push ebp or sub_xxx
                if j > 32 and dll[func_raw+j-1] in (0xC3,) and dll[func_raw+j] == 0x55 and dll[func_raw+j+1] == 0x8B:
                    size_est = f"~{j} bytes"
                    break

        classification = f"STUB ({stub_info})" if is_stub else f"REAL ({size_est})"
        print(f"  {func_va:08X}: [{hex_str}]")
        print(f"    {classification}")
        print(f"    {name}")
        print()

    # =========================================================================
    # 3. References to PathFinder singleton at 0x103743B8
    # =========================================================================
    print("\n" + "=" * 80)
    print("3. References to PathFinder singleton @ 0x103743B8 in .text")
    print("=" * 80)

    singleton_bytes = struct.pack('<I', 0x103743B8)
    text_data = dll[TEXT_RAW:TEXT_RAW+TEXT_SIZE]
    text_base_va = IMAGE_BASE + TEXT_RVA

    refs = []
    pos = 0
    while True:
        idx = text_data.find(singleton_bytes, pos)
        if idx == -1:
            break
        ref_va = text_base_va + idx
        refs.append((idx, ref_va))
        pos = idx + 1

    print(f"\nFound {len(refs)} references:\n")
    for idx, ref_va in refs:
        # Show context: 8 bytes before, the 4-byte ref, 8 bytes after = 20 bytes
        ctx_start = max(0, idx - 8)
        ctx_end = min(len(text_data), idx + 4 + 8)
        ctx_data = text_data[ctx_start:ctx_end]
        ctx_va = text_base_va + ctx_start

        print(f"  Reference at VA 0x{ref_va:08X}:")
        print(hexdump(ctx_data, ctx_va))
        # Also show disasm of a small window around it
        window_start = max(0, idx - 16)
        window_end = min(len(text_data), idx + 20)
        window_data = text_data[window_start:window_end]
        window_va = text_base_va + window_start
        disasm = disasm_simple(window_data, window_va)
        if disasm.strip():
            print(f"  Disasm context:")
            print(disasm)
        print()

    # =========================================================================
    # 4. PathFinder::AddMesh(PathMeshRecast*) at VA 0x101EA9B0
    # =========================================================================
    print("\n" + "=" * 80)
    print("4. PathFinder::AddMesh(PathMeshRecast*) @ 0x101EA9B0")
    print("=" * 80)

    va = 0x101EA9B0
    raw = va_to_raw(va)
    data = dll[raw:raw+128]
    print(f"\nFirst 128 bytes:")
    print(hexdump(data, va))
    print(f"\nDisassembly hints:")
    print(disasm_simple(data, va))

    # Check if this also forwards
    for i in range(min(len(data)-4, 20)):
        if data[i] == 0xE9:
            rel = struct.unpack_from('<i', data, i+1)[0]
            target = va + i + 5 + rel
            print(f"\n  Forwards via jmp to 0x{target:08X}")
            traw = va_to_raw(target)
            if traw:
                tdata = dll[traw:traw+256]
                print(f"  Target (256 bytes):")
                print(hexdump(tdata, target))
                print(f"\n  Disassembly:")
                print(disasm_simple(tdata, target))

    # =========================================================================
    # 5. RTTI for PathMesh and PathMeshRecast
    # =========================================================================
    print("\n" + "=" * 80)
    print("5. RTTI Search for PathMesh and PathMeshRecast")
    print("=" * 80)

    rdata = dll[RDATA_RAW:RDATA_RAW+RDATA_SIZE]
    rdata_base_va = IMAGE_BASE + RDATA_RVA

    # Also search in .data section
    # Get data section size - read to end of file from DATA_RAW
    data_section = dll[DATA_RAW:]
    data_base_va = IMAGE_BASE + DATA_RVA

    for class_name in [b'.?AVPathMesh@GAME@@', b'.?AVPathMeshRecast@GAME@@',
                       b'.?AVPathMesh@@', b'.?AVPathMeshRecast@@',
                       b'.?AVCPathMesh@@', b'.?AVCPathMeshRecast@@',
                       b'.?AVPathFinder@GAME@@', b'.?AVPathFinder@@',
                       b'.?AVCPathFinder@@']:
        # Search in rdata
        for section_data, section_name, section_base in [
            (rdata, '.rdata', rdata_base_va),
            (data_section, '.data', data_base_va)
        ]:
            idx = section_data.find(class_name)
            if idx != -1:
                td_va = section_base + idx
                # TypeDescriptor starts 8 bytes before the name
                td_start = idx - 8
                if td_start >= 0:
                    td_data = section_data[td_start:td_start+64]
                    td_start_va = section_base + td_start
                    print(f"\n  Found RTTI TypeDescriptor for {class_name.decode()} in {section_name}:")
                    print(f"  TypeDescriptor VA: 0x{td_start_va:08X}")
                    print(hexdump(td_data, td_start_va))

                    # vtable ptr is first DWORD of TypeDescriptor
                    vfptr = struct.unpack_from('<I', td_data, 0)[0]
                    print(f"  vfTablePtr (type_info vtable): 0x{vfptr:08X}")

                    # Search for Complete Object Locator that references this TypeDescriptor
                    td_bytes = struct.pack('<I', td_start_va)
                    # COL is in .rdata typically
                    col_idx = rdata.find(td_bytes)
                    while col_idx != -1:
                        col_va = rdata_base_va + col_idx
                        # COL structure: signature, offset, cdOffset, pTypeDescriptor, pClassHierarchyDescriptor
                        # TypeDescriptor is at offset +12 in COL
                        if col_idx >= 12:
                            # Check if this looks like a COL (pTypeDescriptor at offset +12)
                            potential_col_start = col_idx - 12
                            col_data = rdata[potential_col_start:potential_col_start+20]
                            sig = struct.unpack_from('<I', col_data, 0)[0]
                            ptd = struct.unpack_from('<I', col_data, 12)[0]
                            if ptd == td_start_va:
                                col_real_va = rdata_base_va + potential_col_start
                                print(f"  Complete Object Locator at VA 0x{col_real_va:08X}:")
                                print(hexdump(col_data, col_real_va))

                                # Now find vtable: vtable[-1] = &COL
                                col_ptr_bytes = struct.pack('<I', col_real_va)
                                vt_idx = rdata.find(col_ptr_bytes)
                                while vt_idx != -1:
                                    vtable_start = vt_idx + 4  # vtable entries start after COL ptr
                                    vtable_va = rdata_base_va + vtable_start
                                    print(f"  Vtable at VA 0x{vtable_va:08X} (COL ptr at 0x{rdata_base_va + vt_idx:08X}):")
                                    # Dump first 20 vtable entries
                                    vt_data = rdata[vtable_start:vtable_start+80]
                                    for vi in range(0, min(80, len(vt_data)), 4):
                                        entry = struct.unpack_from('<I', vt_data, vi)[0]
                                        slot = vi // 4
                                        # Check if entry is in .text (valid function)
                                        entry_rva = entry - IMAGE_BASE
                                        if TEXT_RVA <= entry_rva < TEXT_RVA + TEXT_SIZE:
                                            print(f"    [{slot:2d}] 0x{entry:08X} (.text)")
                                        else:
                                            print(f"    [{slot:2d}] 0x{entry:08X}")
                                            if entry_rva < TEXT_RVA or entry_rva >= TEXT_RVA + TEXT_SIZE:
                                                # Probably past end of vtable
                                                if slot > 2:
                                                    break

                                    vt_idx = rdata.find(col_ptr_bytes, vt_idx + 1)

                        col_idx = rdata.find(td_bytes, col_idx + 1)
                else:
                    print(f"\n  Found class name {class_name.decode()} in {section_name} at VA 0x{td_va:08X} (too close to section start for TypeDescriptor)")

    # Also try broader search
    print(f"\n--- Broader RTTI name search ---")
    for pattern in [b'PathMesh', b'PathFinder', b'Recast', b'pathfind', b'PATHFIND']:
        for section_data, section_name, section_base in [
            (rdata, '.rdata', rdata_base_va),
            (data_section, '.data', data_base_va)
        ]:
            idx = 0
            while True:
                idx = section_data.find(pattern, idx)
                if idx == -1:
                    break
                # Get surrounding context
                ctx_start = max(0, idx - 4)
                ctx_end = min(len(section_data), idx + len(pattern) + 40)
                ctx = section_data[ctx_start:ctx_end]
                ctx_va = section_base + ctx_start
                # Only show if it looks like a string (printable chars around it)
                text_region = section_data[max(0,idx-16):min(len(section_data),idx+60)]
                # Find the string boundaries
                str_start = idx
                while str_start > 0 and section_data[str_start-1] >= 0x20 and section_data[str_start-1] < 0x7F:
                    str_start -= 1
                str_end = idx
                while str_end < len(section_data) and section_data[str_end] >= 0x20 and section_data[str_end] < 0x7F:
                    str_end += 1
                full_str = section_data[str_start:str_end].decode('ascii', errors='replace')
                if len(full_str) > 3:  # Skip tiny fragments
                    print(f"  {section_name} VA 0x{section_base+str_start:08X}: \"{full_str}\"")
                idx += 1

    print("\n" + "=" * 80)
    print("Analysis complete.")
    print("=" * 80)


if __name__ == '__main__':
    main()
