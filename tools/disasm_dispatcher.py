"""
Disassemble the level blob section dispatcher function at VA 0x101b3fb0
using a simple x86 disassembler (manual decoding of key instructions).

Also examine the second function at 0x101b1d00 which calls the other RLTD handler.
"""

import struct

DLL_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Engine.dll"
IMAGE_BASE = 0x10000000
TEXT_RVA = 0x001000
TEXT_RAW = 0x000400

def va_to_file(va):
    rva = va - IMAGE_BASE
    return rva - TEXT_RVA + TEXT_RAW

def file_to_va(off):
    rva = off - TEXT_RAW + TEXT_RVA
    return IMAGE_BASE + rva

REG_NAMES = ['eax', 'ecx', 'edx', 'ebx', 'esp', 'ebp', 'esi', 'edi']

# Section type names
SECTION_NAMES = {
    0x03: "TERRAIN?",
    0x05: "ENTITIES",
    0x06: "UNKNOWN_06",
    0x09: "GRID",
    0x0a: "PTH_PATHFINDING",
    0x0b: "RLTD_PATHFINDING",
    0x14: "METADATA",
    0x17: "UNKNOWN_17",
}

def decode_modrm(b):
    """Decode ModR/M byte."""
    mod = (b >> 6) & 3
    reg = (b >> 3) & 7
    rm = b & 7
    return mod, reg, rm


def simple_disasm(data, start_va, length):
    """
    Simple x86 disassembler focusing on key instruction patterns:
    - CMP instructions with immediates (to find section type dispatch)
    - CALL/JMP rel32
    - Jcc (conditional jumps)
    - Basic moves and arithmetic
    """
    start_off = va_to_file(start_va)
    end_off = start_off + length

    lines = []
    off = start_off

    while off < end_off:
        va = file_to_va(off)
        instr_start = off
        b = data[off]

        annotation = ""
        instr = ""

        try:
            # === PREFIX HANDLING ===
            prefix = ""
            if b in (0xF2, 0xF3):  # REP/REPNE prefixes (SSE)
                prefix = "f3 " if b == 0xF3 else "f2 "
                off += 1
                b = data[off]

            if b == 0x66:  # Operand size prefix
                prefix += "66 "
                off += 1
                b = data[off]

            if b == 0x0F:
                # Two-byte opcode
                off += 1
                b2 = data[off]

                if b2 in (0x84, 0x85, 0x86, 0x87, 0x8C, 0x8D, 0x8E, 0x8F,
                          0x80, 0x81, 0x82, 0x83, 0x88, 0x89, 0x8A, 0x8B):
                    # Jcc rel32
                    off += 1
                    rel32 = struct.unpack_from('<i', data, off)[0]
                    off += 4
                    target = file_to_va(off) + rel32
                    cc_names = {
                        0x84: 'je', 0x85: 'jne', 0x86: 'jbe', 0x87: 'ja',
                        0x8C: 'jl', 0x8D: 'jge', 0x8E: 'jle', 0x8F: 'jg',
                        0x80: 'jo', 0x81: 'jno', 0x82: 'jb', 0x83: 'jae',
                        0x88: 'js', 0x89: 'jns', 0x8A: 'jp', 0x8B: 'jnp',
                    }
                    name = cc_names.get(b2, f'j?{b2:02x}')
                    instr = f"{name} {target:#010x}"
                else:
                    # Skip SSE and other 0F instructions
                    remaining = min(12, end_off - off)
                    raw = data[instr_start:instr_start + remaining]
                    instr = f"0f {b2:02x} ... (SSE/other)"
                    # Try to advance past the instruction
                    off += 1
                    # Skip ModR/M + possible SIB + displacement
                    if off < end_off:
                        mod, _, rm = decode_modrm(data[off])
                        off += 1
                        if rm == 4 and mod != 3:  # SIB
                            off += 1
                        if mod == 1:
                            off += 1
                        elif mod == 2:
                            off += 4
                        elif mod == 0 and rm == 5:
                            off += 4
                    # Some SSE have immediate
                    # Just skip conservatively

            elif b == 0x83:
                # Group 1 Ev, Ib
                off += 1
                mod, reg_op, rm = decode_modrm(data[off])
                off += 1

                op_names = ['add', 'or', 'adc', 'sbb', 'and', 'sub', 'xor', 'cmp']
                op_name = op_names[reg_op]

                disp = 0
                if mod == 3:
                    reg_name = REG_NAMES[rm]
                    imm = struct.unpack_from('<b', data, off)[0]
                    off += 1
                    instr = f"{op_name} {reg_name}, {imm:#x}"
                    if op_name == 'cmp' and (imm & 0xFF) in SECTION_NAMES:
                        annotation = f"  ; <<< SECTION TYPE {imm:#x} = {SECTION_NAMES[imm & 0xFF]}"
                else:
                    # Memory operand - skip
                    if rm == 4:  # SIB
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    imm = struct.unpack_from('<b', data, off)[0]
                    off += 1
                    instr = f"{op_name} [mem], {imm:#x}"
                    if op_name == 'cmp' and (imm & 0xFF) in SECTION_NAMES:
                        annotation = f"  ; <<< SECTION TYPE {imm:#x} = {SECTION_NAMES[imm & 0xFF]}"

            elif b == 0x81:
                # Group 1 Ev, Iv (32-bit immediate)
                off += 1
                mod, reg_op, rm = decode_modrm(data[off])
                off += 1

                op_names = ['add', 'or', 'adc', 'sbb', 'and', 'sub', 'xor', 'cmp']
                op_name = op_names[reg_op]

                if mod == 3:
                    reg_name = REG_NAMES[rm]
                    if rm == 4:  # SIB
                        off += 1
                    imm = struct.unpack_from('<I', data, off)[0]
                    off += 4
                    instr = f"{op_name} {reg_name}, {imm:#x}"
                else:
                    if rm == 4:  # SIB
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    imm = struct.unpack_from('<I', data, off)[0]
                    off += 4
                    instr = f"{op_name} [mem], {imm:#x}"

            elif b == 0x3C:
                # CMP AL, Ib
                off += 1
                imm = data[off]
                off += 1
                instr = f"cmp al, {imm:#x}"
                if imm in SECTION_NAMES:
                    annotation = f"  ; <<< SECTION TYPE {imm:#x} = {SECTION_NAMES[imm]}"

            elif b == 0x3D:
                # CMP EAX, Id
                off += 1
                imm = struct.unpack_from('<I', data, off)[0]
                off += 4
                instr = f"cmp eax, {imm:#x}"

            elif b == 0xE8:
                # CALL rel32
                off += 1
                rel32 = struct.unpack_from('<i', data, off)[0]
                off += 4
                target = file_to_va(off) + rel32
                instr = f"call {target:#010x}"

                # Annotate known targets
                if target == 0x101f4ba0:
                    annotation = "  ; <<< CALLS RLTD HANDLER #1 (contains 0x101f50f0)"
                elif target == 0x101f6210:
                    annotation = "  ; <<< CALLS RLTD HANDLER #2 (contains 0x101f7feb)"
                elif target == 0x101002b0:
                    annotation = "  ; <<< RLTD VALIDATOR"

            elif b == 0xE9:
                # JMP rel32
                off += 1
                rel32 = struct.unpack_from('<i', data, off)[0]
                off += 4
                target = file_to_va(off) + rel32
                instr = f"jmp {target:#010x}"

            elif b in (0x74, 0x75, 0x76, 0x77, 0x7C, 0x7D, 0x7E, 0x7F,
                       0x70, 0x71, 0x72, 0x73, 0x78, 0x79, 0x7A, 0x7B):
                # Jcc rel8
                cc_names = {
                    0x74: 'je', 0x75: 'jne', 0x76: 'jbe', 0x77: 'ja',
                    0x7C: 'jl', 0x7D: 'jge', 0x7E: 'jle', 0x7F: 'jg',
                    0x70: 'jo', 0x71: 'jno', 0x72: 'jb', 0x73: 'jae',
                    0x78: 'js', 0x79: 'jns', 0x7A: 'jp', 0x7B: 'jnp',
                }
                off += 1
                rel8 = struct.unpack_from('<b', data, off)[0]
                off += 1
                target = file_to_va(off) + rel8
                name = cc_names.get(b, f'j?{b:02x}')
                instr = f"{name} {target:#010x}"

            elif b == 0xEB:
                # JMP rel8
                off += 1
                rel8 = struct.unpack_from('<b', data, off)[0]
                off += 1
                target = file_to_va(off) + rel8
                instr = f"jmp short {target:#010x}"

            elif b == 0xC3:
                off += 1
                instr = "ret"

            elif b == 0xC2:
                off += 1
                imm16 = struct.unpack_from('<H', data, off)[0]
                off += 2
                instr = f"ret {imm16:#x}"

            elif b == 0xCC:
                off += 1
                instr = "int3"

            elif b == 0x55:
                off += 1
                instr = "push ebp"

            elif b == 0x5D:
                off += 1
                instr = "pop ebp"

            elif b >= 0x50 and b <= 0x57:
                off += 1
                instr = f"push {REG_NAMES[b - 0x50]}"

            elif b >= 0x58 and b <= 0x5F:
                off += 1
                instr = f"pop {REG_NAMES[b - 0x58]}"

            elif b == 0x6A:
                # PUSH imm8
                off += 1
                imm = struct.unpack_from('<b', data, off)[0]
                off += 1
                instr = f"push {imm:#x}"

            elif b == 0x68:
                # PUSH imm32
                off += 1
                imm = struct.unpack_from('<I', data, off)[0]
                off += 4
                instr = f"push {imm:#010x}"

            elif b == 0x8B:
                # MOV r32, r/m32
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if mod == 3:
                    instr = f"mov {REG_NAMES[reg]}, {REG_NAMES[rm]}"
                else:
                    # Skip memory operand details for brevity
                    if rm == 4:  # SIB
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    instr = f"mov {REG_NAMES[reg]}, [mem]"

            elif b == 0x89:
                # MOV r/m32, r32
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if mod == 3:
                    instr = f"mov {REG_NAMES[rm]}, {REG_NAMES[reg]}"
                else:
                    if rm == 4:  # SIB
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    instr = f"mov [mem], {REG_NAMES[reg]}"

            elif b == 0xC7:
                # MOV r/m32, imm32
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if rm == 4 and mod != 3:  # SIB
                    off += 1
                if mod == 1:
                    off += 1
                elif mod == 2:
                    off += 4
                elif mod == 0 and rm == 5:
                    off += 4
                imm = struct.unpack_from('<I', data, off)[0]
                off += 4
                instr = f"mov [mem], {imm:#010x}"
                # Check for LVL magic
                if imm == 0x114c564c or (imm & 0x00FFFFFF) == 0x004c564c:
                    annotation = f"  ; <<< LVL MAGIC! ({imm:#010x})"

            elif b == 0xC6:
                # MOV r/m8, imm8
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if rm == 4 and mod != 3:  # SIB
                    off += 1
                if mod == 1:
                    off += 1
                elif mod == 2:
                    off += 4
                elif mod == 0 and rm == 5:
                    off += 4
                imm = data[off]
                off += 1
                instr = f"mov byte [mem], {imm:#x}"

            elif b == 0x8A:
                # MOV r8, r/m8
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if mod == 3:
                    instr = f"mov {REG_NAMES[reg]}l, {REG_NAMES[rm]}l"
                else:
                    if rm == 4 and mod != 3:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    instr = f"mov {REG_NAMES[reg]}l, [mem]"

            elif b == 0x88:
                # MOV r/m8, r8
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if mod != 3:
                    if rm == 4:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                instr = f"mov [mem], {REG_NAMES[reg]}l"

            elif b == 0x80:
                # Group 1 Eb, Ib (byte operations)
                off += 1
                mod, reg_op, rm = decode_modrm(data[off])
                off += 1
                op_names = ['add', 'or', 'adc', 'sbb', 'and', 'sub', 'xor', 'cmp']
                op_name = op_names[reg_op]
                if mod != 3:
                    if rm == 4:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                imm = data[off]
                off += 1
                instr = f"{op_name} byte [mem], {imm:#x}"

            elif b == 0x85:
                # TEST r/m32, r32
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if mod == 3:
                    instr = f"test {REG_NAMES[rm]}, {REG_NAMES[reg]}"
                else:
                    if rm == 4 and mod != 3:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    instr = f"test [mem], {REG_NAMES[reg]}"

            elif b == 0x84:
                # TEST r/m8, r8
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if mod == 3:
                    instr = f"test {REG_NAMES[rm]}l, {REG_NAMES[reg]}l"
                else:
                    if rm == 4 and mod != 3:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    instr = f"test [mem], {REG_NAMES[reg]}l"

            elif b == 0x3B:
                # CMP r32, r/m32
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if mod == 3:
                    instr = f"cmp {REG_NAMES[reg]}, {REG_NAMES[rm]}"
                else:
                    if rm == 4 and mod != 3:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    instr = f"cmp {REG_NAMES[reg]}, [mem]"

            elif b == 0x2C:
                # SUB AL, imm8
                off += 1
                imm = data[off]
                off += 1
                instr = f"sub al, {imm:#x}"
                annotation = f"  ; version_byte - {imm:#x}"

            elif b == 0xFF:
                # Group 5 (call/jmp indirect, push, etc.)
                off += 1
                mod, reg_op, rm = decode_modrm(data[off])
                off += 1
                op_names = {2: 'call', 4: 'jmp', 6: 'push'}
                op_name = op_names.get(reg_op, f'grp5/{reg_op}')
                if mod != 3:
                    if rm == 4:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                instr = f"{op_name} [mem]"

            elif b in (0x01, 0x03, 0x09, 0x0B, 0x21, 0x23, 0x29, 0x2B, 0x31, 0x33):
                # Various ALU r/m32, r32 or r32, r/m32
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if mod != 3:
                    if rm == 4:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                alu_names = {0x01: 'add', 0x03: 'add', 0x09: 'or', 0x0B: 'or',
                            0x21: 'and', 0x23: 'and', 0x29: 'sub', 0x2B: 'sub',
                            0x31: 'xor', 0x33: 'xor'}
                instr = f"{alu_names[b]} ..."

            elif b == 0x8D:
                # LEA r32, m
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if rm == 4 and mod != 3:
                    off += 1
                if mod == 1:
                    off += 1
                elif mod == 2:
                    off += 4
                elif mod == 0 and rm == 5:
                    off += 4
                instr = f"lea {REG_NAMES[reg]}, [mem]"

            elif b == 0xA1:
                # MOV EAX, moffs32
                off += 1
                addr = struct.unpack_from('<I', data, off)[0]
                off += 4
                instr = f"mov eax, [{addr:#010x}]"

            elif b == 0xB8 or (b >= 0xB8 and b <= 0xBF):
                # MOV reg, imm32
                off += 1
                imm = struct.unpack_from('<I', data, off)[0]
                off += 4
                instr = f"mov {REG_NAMES[b - 0xB8]}, {imm:#010x}"

            elif b == 0x32:
                # XOR r8, r/m8
                off += 1
                mod, reg, rm = decode_modrm(data[off])
                off += 1
                if mod == 3:
                    instr = f"xor {REG_NAMES[reg]}l, {REG_NAMES[rm]}l"
                else:
                    if rm == 4 and mod != 3:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    instr = f"xor {REG_NAMES[reg]}l, [mem]"

            elif b == 0x90:
                off += 1
                instr = "nop"

            elif b == 0xD3:
                # Shift group 2 Ev, CL
                off += 1
                mod, reg_op, rm = decode_modrm(data[off])
                off += 1
                shift_names = ['rol', 'ror', 'rcl', 'rcr', 'shl', 'shr', 'sal', 'sar']
                if mod == 3:
                    instr = f"{shift_names[reg_op]} {REG_NAMES[rm]}, cl"
                else:
                    if rm == 4:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    instr = f"{shift_names[reg_op]} [mem], cl"

            elif b == 0xC1:
                # Shift group 2 Ev, Ib
                off += 1
                mod, reg_op, rm = decode_modrm(data[off])
                off += 1
                shift_names = ['rol', 'ror', 'rcl', 'rcr', 'shl', 'shr', 'sal', 'sar']
                if mod == 3:
                    imm = data[off]
                    off += 1
                    instr = f"{shift_names[reg_op]} {REG_NAMES[rm]}, {imm}"
                else:
                    if rm == 4:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    imm = data[off]
                    off += 1
                    instr = f"{shift_names[reg_op]} [mem], {imm}"

            elif b == 0xF7:
                # Unary group 3 Ev
                off += 1
                mod, reg_op, rm = decode_modrm(data[off])
                off += 1
                grp3_names = ['test', 'test', 'not', 'neg', 'mul', 'imul', 'div', 'idiv']
                if mod == 3:
                    instr = f"{grp3_names[reg_op]} {REG_NAMES[rm]}"
                else:
                    if rm == 4:
                        off += 1
                    if mod == 1:
                        off += 1
                    elif mod == 2:
                        off += 4
                    elif mod == 0 and rm == 5:
                        off += 4
                    instr = f"{grp3_names[reg_op]} [mem]"
                if reg_op in (0, 1):  # TEST with immediate
                    imm = struct.unpack_from('<I', data, off)[0]
                    off += 4
                    instr += f", {imm:#x}"

            elif b == 0x48 or (b >= 0x40 and b <= 0x4F):
                # INC/DEC reg
                off += 1
                if b < 0x48:
                    instr = f"inc {REG_NAMES[b - 0x40]}"
                else:
                    instr = f"dec {REG_NAMES[b - 0x48]}"

            else:
                # Unknown - just advance one byte
                off += 1
                instr = f"db {b:#04x}"

        except (IndexError, struct.error):
            off = instr_start + 1
            instr = f"db {data[instr_start]:#04x} (truncated)"

        raw_bytes = data[instr_start:off]
        hex_str = ' '.join(f'{b:02x}' for b in raw_bytes[:8])

        line = f"  {va:#010x}: {hex_str:<24s} {instr}{annotation}"
        lines.append(line)

        # Stop at int3 padding
        if data[instr_start] == 0xCC and off < end_off and data[off] == 0xCC:
            lines.append(f"  ... (int3 padding - function end)")
            break

    return '\n'.join(lines)


def main():
    with open(DLL_PATH, 'rb') as f:
        data = f.read()

    # ===== FUNCTION 1: 0x101b3fb0 - Main blob dispatcher (handles 0x0b directly) =====
    print("=" * 100)
    print("FUNCTION 1: VA 0x101b3fb0 - Level blob section dispatcher")
    print("This function contains CALL to RLTD handler at 0x101b4158")
    print("Section type dispatch: 0x05, 0x06, 0x09, 0x0b, 0x14, 0x17")
    print("=" * 100)

    func1_start = 0x101b3fb0
    func1_size = 0x101b4695 - func1_start + 16

    print(simple_disasm(data, func1_start, func1_size))

    # ===== FUNCTION 2: 0x101b1d00 - Second dispatcher (handles 0x0a?) =====
    print("\n\n" + "=" * 100)
    print("FUNCTION 2: VA 0x101b1d00 - Second level processing function")
    print("This function contains CALL to RLTD handler #2 at 0x101b221a")
    print("=" * 100)

    func2_start = 0x101b1d00
    func2_size = 0x101b23fc - func2_start + 16

    print(simple_disasm(data, func2_start, func2_size))

    # ===== Focus on the LVL magic check and version dispatch =====
    print("\n\n" + "=" * 100)
    print("DETAIL: LVL magic check area (around 0x101b4030)")
    print("=" * 100)

    # Show raw hex of the LVL magic area
    magic_off = va_to_file(0x101b4020)
    print("\nRaw hex dump of LVL magic area:")
    for off in range(magic_off - 16, magic_off + 80, 16):
        va = file_to_va(off)
        chunk = data[off:off+16]
        hex_bytes = ' '.join(f'{b:02x}' for b in chunk)
        ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"  {va:#010x}: {hex_bytes}  {ascii_chars}")

    # ===== Now look at what references the version byte =====
    print("\n\n" + "=" * 100)
    print("DETAIL: Version byte handling (sub al, 0x0a -> switch on version)")
    print("The version byte is subtracted by 0x0a, then compared against 0..7")
    print("This means valid versions are 0x0a through 0x11 (10-17)")
    print("=" * 100)

    # Disassemble the version check area more carefully
    ver_area_start = 0x101b4050
    print(simple_disasm(data, ver_area_start, 0x50))

    # ===== Find the callers of BOTH dispatcher functions =====
    print("\n\n" + "=" * 100)
    print("CALLERS OF THE TWO DISPATCHER FUNCTIONS")
    print("=" * 100)

    for func_va, func_name in [(0x101b3fb0, "Dispatcher1 (section types)"),
                                (0x101b1d00, "Dispatcher2 (RLTD handler #2)")]:
        print(f"\n  Searching for calls to {func_va:#010x} ({func_name})...")
        for off in range(TEXT_RAW, TEXT_RAW + TEXT_SIZE - 5):
            b = data[off]
            if b == 0xE8 or b == 0xE9:
                rel32 = struct.unpack_from('<i', data, off + 1)[0]
                call_va = file_to_va(off)
                dest_va = call_va + 5 + rel32
                if dest_va == func_va:
                    caller_va = call_va
                    instr_type = 'CALL' if b == 0xE8 else 'JMP'
                    print(f"    {instr_type} at {caller_va:#010x}")

                    # Show some context
                    ctx_start = max(TEXT_RAW, va_to_file(caller_va) - 32)
                    ctx_va = file_to_va(ctx_start)
                    print(simple_disasm(data, ctx_va, 80))


if __name__ == '__main__':
    main()
