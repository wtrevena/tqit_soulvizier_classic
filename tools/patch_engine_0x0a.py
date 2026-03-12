"""Patch Engine.dll to handle section type 0x0a (PTH pathfinding) in the LVL parser.

Problem: The TQAE LVL parser only handles section type 0x0b (REC/RLTD pathfinding).
Section type 0x0a (PTH/tok pathfinding from TQIT) is silently SKIPPED.
This causes SV-only levels to have no pathfinding data => can't move / crash.

Patch: Add a check for section type 0x0a in the LVL parser's section dispatch.
When 0x0a is found, redirect to the existing 0x0b handler. ProcessRLTD will:
  1. Call its init function (handler gets initialized!)
  2. Fail the REC\x02 magic check (data starts with PTH\x04)
  3. Return false - LVL parser logs error and continues
  4. Handler is in "initialized but empty" state => prevents crash

Key addresses (Engine.dll, ImageBase=0x10000000):
  LVL parser function:     VA 0x101b3fb0
  Section dispatch loop:   VA 0x101b40c0
  0x0b handler entry:      VA 0x101b412e
  Default skip (0x0a now): VA 0x101b40f7
  Last type check (0x17):  VA 0x101b4347 (jne -> default skip)
  Code cave (51 bytes):    VA 0x1024a1bd

Patch points:
  1. Change jne target at 0x101b4347 from default_skip to code_cave
  2. Write code_cave: cmp edx,0x0a; je 0x0b_handler; jmp default_skip
"""
import struct
import shutil
import sys
from pathlib import Path

TQAE_DIR = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition')
ENGINE_DLL = TQAE_DIR / 'Engine.dll'
BACKUP_DIR = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\backups\game_dll')

IMAGE_BASE = 0x10000000
TEXT_RVA = 0x1000
TEXT_RAW = 0x400

def va_to_fo(va):
    """Convert virtual address to file offset (.text section)."""
    return va - IMAGE_BASE - TEXT_RVA + TEXT_RAW

def fo_to_va(fo):
    """Convert file offset to virtual address (.text section)."""
    return fo - TEXT_RAW + TEXT_RVA + IMAGE_BASE

def rel32(from_va, to_va):
    """Calculate relative offset for a JMP/Jcc instruction.
    from_va is the VA of the byte AFTER the instruction (next instruction)."""
    offset = to_va - from_va
    return struct.pack('<i', offset)

# Key addresses
VA_PATCH_POINT = 0x101b4347   # The jne instruction to modify
VA_0B_HANDLER  = 0x101b412e   # Existing 0x0b handler we redirect 0x0a to
VA_DEFAULT_SKIP = 0x101b40f7  # Original default skip target
VA_CODE_CAVE   = 0x1024a1bd   # 51-byte code cave

def verify_original(data):
    """Verify the original bytes at patch points to ensure we have the right DLL."""
    # At VA_PATCH_POINT: should be 0F 85 AA FD FF FF (jne default_skip)
    # preceded by 83 FA 17 (cmp edx, 0x17)
    fo = va_to_fo(VA_PATCH_POINT - 3)
    expected = bytes([0x83, 0xFA, 0x17, 0x0F, 0x85, 0xAA, 0xFD, 0xFF, 0xFF])
    actual = data[fo:fo+9]
    if actual != expected:
        print(f'ERROR: Unexpected bytes at patch point!')
        print(f'  Expected: {expected.hex()}')
        print(f'  Actual:   {actual.hex()}')
        print(f'  File offset: 0x{fo:06x}')
        return False

    # Code cave should be all 0xCC
    cave_fo = va_to_fo(VA_CODE_CAVE)
    cave_bytes = data[cave_fo:cave_fo+14]
    if not all(b == 0xCC for b in cave_bytes):
        print(f'ERROR: Code cave at 0x{cave_fo:06x} is not all 0xCC!')
        print(f'  Actual: {cave_bytes.hex()}')
        return False

    return True

def is_already_patched(data):
    """Check if the DLL is already patched."""
    fo = va_to_fo(VA_PATCH_POINT)
    # If patched, the jne target is the code cave, not default_skip
    current_rel32 = struct.unpack_from('<i', data, fo + 2)[0]
    current_target = (VA_PATCH_POINT + 6) + current_rel32
    return current_target == VA_CODE_CAVE

def build_code_cave():
    """Build the code cave bytes."""
    cave = bytearray()

    # cmp edx, 0x0a
    cave += bytes([0x83, 0xFA, 0x0A])  # 3 bytes

    # je VA_0B_HANDLER (6 bytes: 0F 84 rel32)
    je_next_va = VA_CODE_CAVE + 3 + 6  # VA after the je instruction
    cave += bytes([0x0F, 0x84])
    cave += rel32(je_next_va, VA_0B_HANDLER)  # 4 bytes

    # jmp VA_DEFAULT_SKIP (5 bytes: E9 rel32)
    jmp_next_va = VA_CODE_CAVE + 3 + 6 + 5  # VA after the jmp instruction
    cave += bytes([0xE9])
    cave += rel32(jmp_next_va, VA_DEFAULT_SKIP)  # 4 bytes

    assert len(cave) == 14
    return bytes(cave)

def apply_patch(data):
    """Apply the patch and return modified data."""
    data = bytearray(data)

    # Patch 1: Change jne target at VA_PATCH_POINT from default_skip to code_cave
    fo = va_to_fo(VA_PATCH_POINT)
    # The jne is 0F 85 rel32 (6 bytes), rel32 starts at offset +2
    jne_next_va = VA_PATCH_POINT + 6
    new_rel = rel32(jne_next_va, VA_CODE_CAVE)
    data[fo+2:fo+6] = new_rel

    # Patch 2: Write code cave
    cave_fo = va_to_fo(VA_CODE_CAVE)
    cave_code = build_code_cave()
    data[cave_fo:cave_fo+len(cave_code)] = cave_code

    return bytes(data)

def main():
    print('=== Engine.dll 0x0a Pathfinding Patch ===\n')

    if not ENGINE_DLL.exists():
        print(f'ERROR: Engine.dll not found at {ENGINE_DLL}')
        return 1

    data = ENGINE_DLL.read_bytes()
    print(f'Read {len(data)} bytes from {ENGINE_DLL}')

    # Check if already patched
    if is_already_patched(data):
        print('Engine.dll is ALREADY PATCHED. Nothing to do.')
        return 0

    # Verify original bytes
    if not verify_original(data):
        print('\nEngine.dll does not match expected layout. Cannot patch.')
        return 1

    print('Original bytes verified OK.')

    # Show what we're doing
    print(f'\nPatch details:')
    print(f'  Redirect: jne at VA 0x{VA_PATCH_POINT:08X} -> code cave at VA 0x{VA_CODE_CAVE:08X}')
    print(f'  Code cave: cmp edx,0x0a; je 0x{VA_0B_HANDLER:08X}; jmp 0x{VA_DEFAULT_SKIP:08X}')
    print(f'  Effect: Section type 0x0a now routes to existing 0x0b handler')
    print(f'          ProcessRLTD init runs but magic check fails -> handler initialized')

    # Build and show the code cave
    cave = build_code_cave()
    print(f'\nCode cave ({len(cave)} bytes): {cave.hex()}')

    # Backup
    backup_path = BACKUP_DIR / 'Engine.dll.pre_0x0a_patch'
    if not backup_path.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ENGINE_DLL, backup_path)
        print(f'\nBackup saved to: {backup_path}')
    else:
        print(f'\nBackup already exists: {backup_path}')

    # Apply patch
    patched = apply_patch(data)

    # Verify patch
    if not is_already_patched(patched):
        print('ERROR: Patch verification failed!')
        return 1

    # Write patched DLL
    ENGINE_DLL.write_bytes(patched)
    print(f'\nPatched Engine.dll written to: {ENGINE_DLL}')
    print('Patch applied successfully!')

    # Show restore command
    print(f'\nTo restore original: copy "{backup_path}" "{ENGINE_DLL}"')

    return 0

if __name__ == '__main__':
    sys.exit(main())
