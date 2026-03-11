#!/usr/bin/env python3
"""
Recompile a single level using the TQAE MapCompiler.

Creates a minimal WRL + source directory with just one level,
runs MapCompiler, and extracts the resulting compiled blob.

This tests whether AE-recompiling an SV-sourced level produces
a blob that works in a TQAE-compiled map.
"""
import hashlib
import shutil
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_level_index, SEC_LEVELS, SEC_GROUPS, SEC_SD)
from build_section_surgery import parse_blob_sections
from blob_diff import inspect_blob, compare_blobs, format_report_text, format_inspect_text

MC_EXE = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\MapCompiler.exe')

SVAERA_ARC = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
SV_ARC = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
SV_DECOMP = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\decompiled_sv')
SVAERA_DECOMP = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\decompiled_svaera')
WORK_DIR = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\recompile_test')

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
    print('=== Single-Level AE Recompilation Test ===')
    print(f'Target: {TARGET_FNAME} (SVAERA idx {TARGET_AE_IDX})')

    # Load SVAERA metadata for the WRL
    print('\nLoading SVAERA metadata...')
    ae_arc = ArcArchive.from_file(SVAERA_ARC)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sec = {s['type']: s for s in parse_sections(ae_data)}
    ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])
    groups_raw = ae_data[ae_sec[SEC_GROUPS]['data_offset']:
                         ae_sec[SEC_GROUPS]['data_offset'] + ae_sec[SEC_GROUPS]['size']]
    sd_raw = ae_data[ae_sec[SEC_SD]['data_offset']:
                     ae_sec[SEC_SD]['data_offset'] + ae_sec[SEC_SD]['size']]

    ae_lv = ae_levels[TARGET_AE_IDX]
    ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]

    # Load SV blob for comparison
    print('Loading SV metadata...')
    sv_arc_obj = ArcArchive.from_file(SV_ARC)
    sv_data = sv_arc_obj.decompress([e for e in sv_arc_obj.entries if e.entry_type == 3][0])
    sv_sec = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])
    sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}
    sv_idx = sv_by_name.get(TARGET_FNAME.replace('\\', '/').lower())
    sv_lv = sv_levels[sv_idx]
    sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]

    del ae_data, sv_data  # free memory

    # Prepare work directory
    print(f'\nPreparing work directory: {WORK_DIR}')
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    # Copy SV source .lvl file (this is what we want to recompile)
    src_lvl = SV_DECOMP / TARGET_FNAME.replace('/', '\\')
    dst_lvl = WORK_DIR / TARGET_FNAME.replace('/', '\\')
    dst_lvl.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_lvl, dst_lvl)
    print(f'  Copied SV source: {src_lvl.name} ({src_lvl.stat().st_size} bytes)')

    # Also copy the .tga if it exists (MapCompiler may need it for bitmaps)
    src_tga = src_lvl.with_suffix('.tga')
    if src_tga.exists():
        shutil.copy2(src_tga, dst_lvl.with_suffix('.tga'))
        print(f'  Copied TGA: {src_tga.name} ({src_tga.stat().st_size} bytes)')

    # Do NOT copy the .rlv — we want MapCompiler to generate a fresh one

    # Build minimal WRL
    wrl_path = WORK_DIR / 'world01.wrl'
    wrl_size = build_minimal_wrl(ae_lv, groups_raw, wrl_path)
    print(f'  WRL: {wrl_size} bytes')

    # Write SD file
    sd_path = WORK_DIR / 'world01.sd'
    sd_path.write_bytes(sd_raw)
    print(f'  SD: {len(sd_raw)} bytes')

    # Run MapCompiler
    output_map = WORK_DIR / 'world01.map'
    print(f'\nRunning MapCompiler...')
    print(f'  Exe: {MC_EXE}')
    print(f'  WRL: {wrl_path}')
    print(f'  Source: {WORK_DIR}\\')
    print(f'  Output: {output_map}')

    if not MC_EXE.exists():
        print(f'ERROR: MapCompiler not found at {MC_EXE}')
        return

    result = subprocess.run(
        [str(MC_EXE), str(wrl_path), str(WORK_DIR) + '\\', str(output_map)],
        capture_output=True, text=True, timeout=120
    )
    print(f'\n  Exit code: {result.returncode}')
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        for line in lines[:50]:
            print(f'  {line}')
        if len(lines) > 50:
            print(f'  ... ({len(lines) - 50} more lines)')
    if result.stderr:
        print(f'  STDERR: {result.stderr[:500]}')

    if not output_map.exists():
        print('\nERROR: MapCompiler did not produce output map')

        # Fallback: try with the .rlv file present
        print('\nRetrying with .rlv file present...')
        src_rlv = SV_DECOMP / TARGET_FNAME.replace('/', '\\').replace('.LVL', '.rlv').replace('.lvl', '.rlv')
        if src_rlv.exists():
            dst_rlv = dst_lvl.with_suffix('.rlv')
            shutil.copy2(src_rlv, dst_rlv)
            print(f'  Copied SV .rlv: {src_rlv.name} ({src_rlv.stat().st_size} bytes)')

            result2 = subprocess.run(
                [str(MC_EXE), str(wrl_path), str(WORK_DIR) + '\\', str(output_map)],
                capture_output=True, text=True, timeout=120
            )
            print(f'  Exit code: {result2.returncode}')
            if result2.stdout:
                for line in result2.stdout.strip().split('\n')[:30]:
                    print(f'  {line}')
            if result2.stderr:
                print(f'  STDERR: {result2.stderr[:500]}')

    if not output_map.exists():
        print('\nERROR: MapCompiler failed even with .rlv')
        return

    # Extract the compiled blob from the output map
    print(f'\n=== Extracting compiled blob ===')
    map_data = output_map.read_bytes()
    print(f'  Output map: {len(map_data)} bytes')

    map_sections = parse_sections(map_data)
    map_sec = {s['type']: s for s in map_sections}
    from merge_levels_binary import SEC_DATA
    if SEC_DATA not in map_sec:
        print('ERROR: No DATA section in output map')
        return

    map_levels = parse_level_index(map_data, map_sec[SEC_LEVELS])
    print(f'  Levels in output: {len(map_levels)}')

    if len(map_levels) == 0:
        print('ERROR: No levels in output map')
        return

    recompiled_lv = map_levels[0]
    recompiled_blob = map_data[recompiled_lv['data_offset']:
                               recompiled_lv['data_offset'] + recompiled_lv['data_length']]
    print(f'  Recompiled blob: {len(recompiled_blob)} bytes')

    # Save the recompiled blob for later use
    recompiled_rlv = WORK_DIR / 'RuinedCity02_AE_recompiled.rlv'
    recompiled_rlv.write_bytes(recompiled_blob)
    print(f'  Saved to: {recompiled_rlv}')

    # Three-way comparison
    print(f'\n=== Three-Way Blob Comparison ===')
    print()
    print(format_inspect_text(inspect_blob(ae_blob, 'A: SVAERA compiled (working)')))
    print()
    print(format_inspect_text(inspect_blob(sv_blob, 'B: SV compiled (crashes)')))
    print()
    print(format_inspect_text(inspect_blob(recompiled_blob, 'C: AE-recompiled from SV source')))
    print()
    print(format_report_text(compare_blobs(ae_blob, recompiled_blob, 'A: SVAERA', 'C: AE-recompiled')))
    print()
    print(format_report_text(compare_blobs(sv_blob, recompiled_blob, 'B: SV', 'C: AE-recompiled')))

    # Key question: does C have 0x0b?
    c_secs, _ = parse_blob_sections(recompiled_blob)
    has_0a = any(s['type'] == 0x0a for s in c_secs)
    has_0b = any(s['type'] == 0x0b for s in c_secs)
    print(f'\n=== KEY RESULT ===')
    print(f'  AE-recompiled blob has 0x0a (PTH): {has_0a}')
    print(f'  AE-recompiled blob has 0x0b (REC): {has_0b}')
    if has_0b and not has_0a:
        print(f'  GOOD: MapCompiler generated 0x0b from SV source!')
        print(f'  This blob should work in the SVAERA map.')
    elif has_0a and not has_0b:
        print(f'  BAD: MapCompiler kept 0x0a, did not generate 0x0b.')
    else:
        print(f'  UNEXPECTED: Check sections manually.')


if __name__ == '__main__':
    main()
