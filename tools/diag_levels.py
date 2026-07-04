#!/usr/bin/env python3
"""
Diagnostic script: analyze 0x14 sections, blob sections, and GROUPS data
across SVAERA, SV, and the merged output.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_GROUPS, SEC_DATA
from build_section_surgery import parse_blob_sections, parse_0x14_records

SVAERA_ARC = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
SV_ARC     = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
MERGED_ARC = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')
RECOMPILED = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_recompiled.map')


def load_map_from_arc(arc_path, label):
    """Load an ARC, extract world01.map, parse sections and level index."""
    print(f'Loading {label} from {arc_path}...')
    arc = ArcArchive.from_file(arc_path)
    map_data = arc.get_file('world/world01.map')
    if map_data is None:
        # try all type-3 entries
        for e in arc.entries:
            if e.entry_type == 3:
                map_data = arc.decompress(e)
                break
    if map_data is None:
        print(f'  ERROR: no map data found in {label}')
        return None, None, None
    sections = parse_sections(map_data)
    sec_map = {s['type']: s for s in sections}
    levels = parse_level_index(map_data, sec_map[SEC_LEVELS])
    print(f'  {len(levels)} levels, map size: {len(map_data)/(1024**2):.1f} MB')
    return map_data, sec_map, levels


def find_level(levels, name_fragment):
    """Find a level whose fname contains name_fragment (case-insensitive)."""
    frag = name_fragment.lower()
    for lv in levels:
        if frag in lv['fname'].lower():
            return lv
    return None


def analyze_0x14(label, map_data, levels, level_name):
    """Analyze 0x14 section for a specific level."""
    lv = find_level(levels, level_name)
    if lv is None:
        print(f'  [{label}] {level_name}: NOT FOUND')
        return
    blob = map_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    secs, magic = parse_blob_sections(blob)
    magic_hex = magic.hex() if magic else 'none'
    print(f'  [{label}] {lv["fname"]} (blob size: {len(blob)}, magic: {magic_hex})')

    sec_0x14 = [s for s in secs if s['type'] == 0x14]
    if not sec_0x14:
        print(f'    0x14: NOT PRESENT')
        return

    data_0x14 = sec_0x14[0]['data']
    print(f'    0x14 section size: {len(data_0x14)} bytes')
    if len(data_0x14) == 0:
        print(f'    0x14 is EMPTY (cleared by surgery)')
        return

    records = parse_0x14_records(data_0x14)
    print(f'    0x14 records: {len(records)}')

    # Show each record
    payload_patterns = set()
    for r in records:
        # First 5 uint32s of payload (or fewer)
        n_ints = min(5, len(r['payload']) // 4)
        first_ints = struct.unpack_from(f'<{n_ints}I', r['payload']) if n_ints > 0 else ()
        int_str = ', '.join(f'{v}' for v in first_ints)
        print(f'      rec[{r["index"]}] payload_size={r["payload_size"]}  first_uint32s: [{int_str}]')
        payload_patterns.add(r['payload'])

    print(f'    Unique payload patterns: {len(payload_patterns)}')


def print_blob_sections(label, map_data, levels, level_name):
    """Print all blob section types and sizes for a level."""
    lv = find_level(levels, level_name)
    if lv is None:
        print(f'  [{label}] {level_name}: NOT FOUND')
        return None, None
    blob = map_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    secs, magic = parse_blob_sections(blob)
    magic_hex = magic.hex() if magic else 'none'
    print(f'  [{label}] {lv["fname"]} (blob size: {len(blob)}, magic: {magic_hex})')
    for s in secs:
        print(f'    section 0x{s["type"]:02x}: {s["size"]} bytes')
    return secs, magic


def hex_dump(data, max_bytes=48):
    """Print hex dump of data."""
    for i in range(0, min(len(data), max_bytes), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f'      {i:04x}: {hex_part:<48s}  {ascii_part}')


def search_groups(label, groups_data, search_terms):
    """Search GROUPS section for byte patterns."""
    print(f'  [{label}] GROUPS section ({len(groups_data)} bytes):')
    for term in search_terms:
        offsets = []
        pos = 0
        while True:
            idx = groups_data.find(term, pos)
            if idx < 0:
                break
            offsets.append(idx)
            pos = idx + 1
        if offsets:
            off_str = ', '.join(f'0x{o:x}' for o in offsets[:10])
            print(f'    {term!r}: FOUND at offsets [{off_str}]')
        else:
            print(f'    {term!r}: NOT FOUND')


def main():
    # ========================================
    # Load all three sources
    # ========================================
    svaera_data, svaera_sec, svaera_levels = load_map_from_arc(SVAERA_ARC, 'SVAERA')
    sv_data, sv_sec, sv_levels = load_map_from_arc(SV_ARC, 'SV')
    merged_data, merged_sec, merged_levels = load_map_from_arc(MERGED_ARC, 'MERGED')

    # ========================================
    # A) 0x14 Analysis for HiddenValley01
    # ========================================
    print('\n' + '='*70)
    print('A) 0x14 Analysis for HiddenValley01')
    print('='*70)
    analyze_0x14('SVAERA', svaera_data, svaera_levels, 'HiddenValley01')
    analyze_0x14('SV', sv_data, sv_levels, 'HiddenValley01')
    analyze_0x14('MERGED', merged_data, merged_levels, 'HiddenValley01')

    # ========================================
    # B) 0x14 Analysis for DelphiLowlands04
    # ========================================
    print('\n' + '='*70)
    print('B) 0x14 Analysis for DelphiLowlands04')
    print('='*70)
    analyze_0x14('SVAERA', svaera_data, svaera_levels, 'DelphiLowlands04')
    analyze_0x14('SV', sv_data, sv_levels, 'DelphiLowlands04')
    analyze_0x14('MERGED', merged_data, merged_levels, 'DelphiLowlands04')

    # ========================================
    # C) Blood cave grid analysis for Random09A
    # ========================================
    print('\n' + '='*70)
    print('C) Blood cave grid analysis for Random09A')
    print('='*70)

    print('\n  --- SV Random09A blob sections ---')
    sv_r09_secs, sv_r09_magic = print_blob_sections('SV', sv_data, sv_levels, 'Random09A')
    if sv_r09_secs:
        sec_09 = [s for s in sv_r09_secs if s['type'] == 0x09]
        if sec_09:
            print(f'    0x09 hex dump ({len(sec_09[0]["data"])} bytes):')
            hex_dump(sec_09[0]['data'])
        else:
            print(f'    0x09: NOT PRESENT in SV')

    print('\n  --- MERGED Random09A blob sections ---')
    merged_r09_secs, merged_r09_magic = print_blob_sections('MERGED', merged_data, merged_levels, 'Random09A')
    if merged_r09_secs and sv_r09_secs:
        sv_09 = [s for s in sv_r09_secs if s['type'] == 0x09]
        merged_09 = [s for s in merged_r09_secs if s['type'] == 0x09]
        if sv_09 and merged_09:
            match = sv_09[0]['data'] == merged_09[0]['data']
            print(f'    0x09 present in MERGED: YES, matches SV: {match}')
        elif sv_09:
            print(f'    0x09 present in SV but MISSING from MERGED')
        elif merged_09:
            print(f'    0x09 present in MERGED but was missing from SV')
        else:
            print(f'    0x09 absent from both')

    # ========================================
    # D) GROUPS section blood cave check
    # ========================================
    print('\n' + '='*70)
    print('D) GROUPS section blood cave check')
    print('='*70)

    search_terms = [b'BloodCave', b'bloodcave', b'xBloodCave', b'BC_initial', b'Random09A']

    # merged_recompiled.map (MapCompiler output)
    print(f'\n  Loading MapCompiler output: {RECOMPILED}')
    recomp_data = RECOMPILED.read_bytes()
    recomp_sections = parse_sections(recomp_data)
    recomp_sec_map = {s['type']: s for s in recomp_sections}
    if SEC_GROUPS in recomp_sec_map:
        recomp_groups = recomp_data[recomp_sec_map[SEC_GROUPS]['data_offset']:
                                     recomp_sec_map[SEC_GROUPS]['data_offset'] + recomp_sec_map[SEC_GROUPS]['size']]
        search_groups('RECOMPILED', recomp_groups, search_terms)
    else:
        print(f'  RECOMPILED: no GROUPS section (0x11) found!')

    # merged output
    if SEC_GROUPS in merged_sec:
        merged_groups = merged_data[merged_sec[SEC_GROUPS]['data_offset']:
                                     merged_sec[SEC_GROUPS]['data_offset'] + merged_sec[SEC_GROUPS]['size']]
        search_groups('MERGED', merged_groups, search_terms)
    else:
        print(f'  MERGED: no GROUPS section (0x11) found!')

    # ========================================
    # E) GROUPS section in SVAERA original
    # ========================================
    print('\n' + '='*70)
    print('E) GROUPS section in SVAERA original')
    print('='*70)

    svaera_search = [b'BloodCave', b'xBloodCave', b'BC_initial', b'Random09A']
    if SEC_GROUPS in svaera_sec:
        svaera_groups = svaera_data[svaera_sec[SEC_GROUPS]['data_offset']:
                                     svaera_sec[SEC_GROUPS]['data_offset'] + svaera_sec[SEC_GROUPS]['size']]
        search_groups('SVAERA', svaera_groups, svaera_search)
    else:
        print(f'  SVAERA: no GROUPS section (0x11) found!')

    print('\nDone.')


if __name__ == '__main__':
    main()
