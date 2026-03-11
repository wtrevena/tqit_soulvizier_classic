"""
Verify the Editor proof test output.

Checks if the Editor-saved RuinedCity02.lvl now has 0x0b (REC\x02)
pathfinding section. If yes, replaces SVAERA slot 30 in the merged
map and rebuilds for in-game testing.
"""
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (
    parse_sections, parse_level_index, SEC_LEVELS, SEC_DATA,
)
from build_section_surgery import parse_blob_sections
from blob_diff import inspect_blob, compare_blobs, format_report_text, format_inspect_text

# Paths
REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
TQ_DOCS = Path(r'C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne')
WORKING = TQ_DOCS / 'Working'
MOD_NAME = 'PathingTest'
MOD_DIR = WORKING / 'CustomMaps' / MOD_NAME

SVAERA_ARC = REPO / r'reference_mods\SVAERA_customquest\Resources\Levels.arc'
SV_DECOMP = REPO / 'local' / 'decompiled_sv'

TARGET_FNAME = 'Levels/World/Greece/Area004/RuinedCity02.LVL'
TARGET_AE_IDX = 30

# Art Manager uses Working/CustomMaps/<mod>/source/ (lowercase 'source')
EDITOR_LVL = MOD_DIR / 'source' / 'Maps' / TARGET_FNAME.replace('/', '\\')
# Fallback: our setup script used Working/<mod>/Source/ (uppercase, no CustomMaps)
EDITOR_LVL_ALT = WORKING / MOD_NAME / 'Source' / 'Maps' / TARGET_FNAME.replace('/', '\\')


def main():
    print('=== Verify Editor Proof Test Output ===')
    print(f'Checking: {EDITOR_LVL}')
    print()

    lvl_path = EDITOR_LVL
    if not lvl_path.exists():
        lvl_path = EDITOR_LVL_ALT
    if not lvl_path.exists():
        print(f'ERROR: Level file not found at:')
        print(f'  {EDITOR_LVL}')
        print(f'  {EDITOR_LVL_ALT}')
        print('Did you run setup_editor_proof_test.py and complete the Editor steps?')
        return
    print(f'Found at: {lvl_path}')

    # Read the Editor-saved blob
    editor_blob = lvl_path.read_bytes()
    secs, _ = parse_blob_sections(editor_blob)
    sec_types = [s['type'] for s in secs]
    ver = editor_blob[3] if len(editor_blob) > 3 else 0

    print(f'Editor-saved blob: v0x{ver:02x}, {len(editor_blob)} bytes')
    print(f'  Sections: {[f"0x{t:02x}" for t in sec_types]}')
    for s in secs:
        print(f'    0x{s["type"]:02x}: {s["size"]:,} bytes')

    has_0a = 0x0a in sec_types
    has_0b = 0x0b in sec_types

    print(f'\n  Has 0x0a (PTH\\x04, TQIT pathfinding): {has_0a}')
    print(f'  Has 0x0b (REC\\x02, TQAE pathfinding): {has_0b}')

    # Load original SV and SVAERA blobs for comparison
    print('\nLoading originals for comparison...')
    sv_lvl = SV_DECOMP / TARGET_FNAME.replace('/', '\\')
    sv_blob = sv_lvl.read_bytes()

    ae_arc = ArcArchive.from_file(SVAERA_ARC)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sec = {s['type']: s for s in parse_sections(ae_data)}
    ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
    ae_lv = ae_levels[TARGET_AE_IDX]
    ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
    del ae_data

    print()
    print(format_inspect_text(inspect_blob(sv_blob, 'A: SV original (v0x0d, 0x0a only)')))
    print()
    print(format_inspect_text(inspect_blob(ae_blob, 'B: SVAERA original (v0x0e, 0x0b)')))
    print()
    print(format_inspect_text(inspect_blob(editor_blob, 'C: Editor-saved')))

    if has_0b:
        print()
        print(format_report_text(compare_blobs(ae_blob, editor_blob, 'B: SVAERA', 'C: Editor-saved')))

    # Final verdict
    print(f'\n{"="*60}')
    if has_0b:
        print('SUCCESS: Editor generated 0x0b (REC\\x02) pathfinding!')
        print()
        print('The Editor-normalized blob should work in the SVAERA map.')
        print('Next step: replace SVAERA slot 30 with this blob and test.')
        print()
        # Save a copy for the merge pipeline
        out_path = REPO / 'local' / 'editor_normalized' / 'RuinedCity02.lvl'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(lvl_path, out_path)
        print(f'Saved copy to: {out_path}')
        print()
        print('To test in-game, run:')
        print('  py tools/test_editor_blob_in_map.py')
    elif not has_0a and not has_0b:
        print('UNEXPECTED: No pathfinding section at all.')
        print('The Editor may have stripped it. Check the blob manually.')
    else:
        print('FAILED: Editor did NOT generate 0x0b.')
        if has_0a:
            print('Still has 0x0a only — Rebuild Pathing may not have run.')
        print('Try: select the level tile, then Build > Rebuild All Pathing.')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
