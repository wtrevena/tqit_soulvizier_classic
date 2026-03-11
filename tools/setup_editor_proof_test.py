"""
Set up a TQAE Art Manager project for the Editor normalization proof test.

Creates a minimal mod project with one SV-sourced level (RuinedCity02),
ready for the Editor to open and Rebuild All Pathing.

After this script:
1. Open Art Manager -> Mod -> New -> "PathingTest"
   (or if already created, just open it)
2. Open Editor -> select PathingTest mod -> open world01
3. In Layout Mode: Build -> Rebuild Selected Pathing (or Rebuild All Pathing)
4. Verify path mesh preview appears (Pathing -> First Pass to toggle visibility)
5. File -> Save All
6. Close Editor
7. Run verify_editor_output.py to check the result
"""
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_GROUPS, SEC_SD

# Paths
REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
TQ_DOCS = Path(r'C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne')
WORKING = TQ_DOCS / 'Working'
MOD_NAME = 'PathingTest'
MOD_DIR = WORKING / MOD_NAME

SVAERA_ARC = REPO / r'reference_mods\SVAERA_customquest\Resources\Levels.arc'
SV_DECOMP = REPO / 'local' / 'decompiled_sv'

# Target level
TARGET_FNAME = 'Levels/World/Greece/Area004/RuinedCity02.LVL'
TARGET_AE_IDX = 30


def build_minimal_wrl(level_entry, groups_raw, output_path):
    """Build a minimal WRL file with just one level."""
    wrl = bytearray()
    wrl += struct.pack('<I', 0x074C5257)  # WRL magic

    # LEVELS section (type 0x13): 1 level
    levels_payload = bytearray()
    levels_payload += struct.pack('<I', 1)  # count = 1
    lv = level_entry
    fname_bytes = lv['fname_raw']
    levels_payload += struct.pack('<I', len(fname_bytes))
    levels_payload += fname_bytes
    # ints_raw: first 6 as float, rest as-is
    raw = lv['ints_raw']
    for j in range(6):
        int_val = struct.unpack_from('<I', raw, j * 4)[0]
        levels_payload += struct.pack('<f', float(int_val))
    levels_payload += raw[24:52]  # remaining 7 ints as-is
    # dbr
    dbr_bytes = lv['dbr_raw']
    levels_payload += struct.pack('<I', len(dbr_bytes))
    levels_payload += dbr_bytes

    wrl += struct.pack('<II', 0x13, len(levels_payload))
    wrl += levels_payload

    # QUESTS section (type 0x1B): empty
    quests_payload = struct.pack('<I', 0)
    wrl += struct.pack('<II', 0x1B, len(quests_payload))
    wrl += quests_payload

    # GROUPS section (type 0x11): use SVAERA's
    wrl += struct.pack('<II', 0x11, len(groups_raw))
    wrl += groups_raw

    # BITMAPS section (type 0x15): 1 empty entry
    bmp_payload = struct.pack('<4I', 0, 0, 0, 0)
    wrl += struct.pack('<II', 0x15, len(bmp_payload))
    wrl += bmp_payload

    output_path.write_bytes(bytes(wrl))
    return len(wrl)


def main():
    print('=== TQAE Editor Proof Test Setup ===')
    print(f'Mod: {MOD_NAME}')
    print(f'Target: {TARGET_FNAME} (SVAERA idx {TARGET_AE_IDX})')
    print()

    # Load SVAERA metadata for the WRL
    print('Loading SVAERA metadata...')
    ae_arc = ArcArchive.from_file(SVAERA_ARC)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sec = {s['type']: s for s in parse_sections(ae_data)}
    ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
    groups_raw = ae_data[ae_sec[SEC_GROUPS]['data_offset']:
                         ae_sec[SEC_GROUPS]['data_offset'] + ae_sec[SEC_GROUPS]['size']]
    ae_lv = ae_levels[TARGET_AE_IDX]
    del ae_data

    # Create mod directory structure
    maps_dir = MOD_DIR / 'Source' / 'Maps'
    maps_dir.mkdir(parents=True, exist_ok=True)
    print(f'Created: {maps_dir}')

    # Build minimal WRL
    wrl_path = maps_dir / 'world01.wrl'
    wrl_size = build_minimal_wrl(ae_lv, groups_raw, wrl_path)
    print(f'WRL: {wrl_path} ({wrl_size} bytes)')

    # Copy SV source .lvl file
    src_lvl = SV_DECOMP / TARGET_FNAME.replace('/', '\\')
    dst_lvl = maps_dir / TARGET_FNAME.replace('/', '\\')
    dst_lvl.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_lvl, dst_lvl)
    print(f'Copied SV .lvl: {dst_lvl} ({src_lvl.stat().st_size} bytes)')

    # Copy .tga (minimap bitmap)
    src_tga = src_lvl.with_suffix('.tga')
    if src_tga.exists():
        shutil.copy2(src_tga, dst_lvl.with_suffix('.tga'))
        print(f'Copied .tga: {src_tga.name}')

    # Copy .rlv (region layout — Editor may need this)
    src_rlv = src_lvl.with_suffix('.rlv')
    if src_rlv.exists():
        shutil.copy2(src_rlv, dst_lvl.with_suffix('.rlv'))
        print(f'Copied .rlv: {src_rlv.name}')

    # Verify the source blob sections
    from build_section_surgery import parse_blob_sections
    blob = src_lvl.read_bytes()
    secs, _ = parse_blob_sections(blob)
    sec_types = [s['type'] for s in secs]
    has_0a = 0x0a in sec_types
    has_0b = 0x0b in sec_types
    ver = blob[3] if len(blob) > 3 else 0
    print(f'\nSV source blob: v0x{ver:02x}, {len(blob)} bytes')
    print(f'  Sections: {[f"0x{t:02x}" for t in sec_types]}')
    print(f'  Has 0x0a (PTH): {has_0a}')
    print(f'  Has 0x0b (REC): {has_0b}')

    print(f'\n{"="*60}')
    print(f'Setup complete. Now do these steps:')
    print(f'')
    print(f'1. Open Art Manager:')
    print(f'   "{Path(r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Titan Quest Anniversary Edition\\ArtManager.exe")}"')
    print(f'   -> Mod -> New -> "{MOD_NAME}"')
    print(f'   (If it asks for working directory, use: {WORKING})')
    print(f'')
    print(f'2. Open Editor:')
    print(f'   "{Path(r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Titan Quest Anniversary Edition\\Editor.exe")}"')
    print(f'   -> Select mod "{MOD_NAME}" when prompted')
    print(f'   -> Open world01.wrl from the Maps folder')
    print(f'   -> You should see RuinedCity02 in the layout')
    print(f'')
    print(f'3. Rebuild pathing:')
    print(f'   -> In Layout Mode tab (bottom of window)')
    print(f'   -> Select the level tile')
    print(f'   -> Build -> Rebuild All Pathing')
    print(f'   -> Wait for it to complete')
    print(f'   -> Optional: Pathing -> First Pass to see path mesh preview')
    print(f'')
    print(f'4. Save and exit:')
    print(f'   -> File -> Save All')
    print(f'   -> Close Editor')
    print(f'')
    print(f'5. Verify:')
    print(f'   py tools/verify_editor_output.py')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
