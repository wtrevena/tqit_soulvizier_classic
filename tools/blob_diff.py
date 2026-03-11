#!/usr/bin/env python3
"""
Level blob comparison and inspection tooling.

Parses LVL blobs into sections, compares two blobs, and emits reports.
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_section_surgery import parse_blob_sections


SECTION_NAMES = {
    0x05: 'Entities',
    0x06: 'Unknown_06',
    0x09: 'Grid',
    0x0a: 'PTH_04 (TQIT pathfinding)',
    0x0b: 'REC_02 (TQAE pathfinding)',
    0x14: 'Metadata',
    0x17: 'Unknown_17',
}

LVL_VERSION_NAMES = {
    0x0e: 'v0x0e (TQIT)',
    0x0f: 'v0x0f',
    0x11: 'v0x11 (TQAE)',
}


def inspect_blob(blob, label='blob'):
    """Parse a blob and return a structured report dict."""
    if len(blob) < 4 or blob[:3] != b'LVL':
        return {'label': label, 'error': 'Not a valid LVL blob', 'size': len(blob)}

    version = blob[3]
    secs, magic = parse_blob_sections(blob)

    sections = []
    for s in secs:
        h = hashlib.sha256(s['data']).hexdigest()[:16]
        sections.append({
            'type': s['type'],
            'type_hex': f"0x{s['type']:02x}",
            'name': SECTION_NAMES.get(s['type'], f'Unknown_{s["type"]:02x}'),
            'size': len(s['data']),
            'hash': h,
        })

    return {
        'label': label,
        'total_size': len(blob),
        'version': version,
        'version_name': LVL_VERSION_NAMES.get(version, f'v0x{version:02x}'),
        'section_count': len(sections),
        'sections': sections,
    }


def compare_blobs(blob_a, blob_b, label_a='A', label_b='B'):
    """Compare two blobs and return a structured diff report."""
    report_a = inspect_blob(blob_a, label_a)
    report_b = inspect_blob(blob_b, label_b)

    if 'error' in report_a or 'error' in report_b:
        return {'a': report_a, 'b': report_b, 'error': 'One or both blobs invalid'}

    # Section presence comparison
    types_a = {s['type'] for s in report_a['sections']}
    types_b = {s['type'] for s in report_b['sections']}
    only_a = types_a - types_b
    only_b = types_b - types_a
    common = types_a & types_b

    # Per-section comparison for common sections
    sec_map_a = {s['type']: s for s in report_a['sections']}
    sec_map_b = {s['type']: s for s in report_b['sections']}

    section_diffs = []
    for t in sorted(common):
        sa = sec_map_a[t]
        sb = sec_map_b[t]
        section_diffs.append({
            'type_hex': f"0x{t:02x}",
            'name': SECTION_NAMES.get(t, f'Unknown_{t:02x}'),
            'size_a': sa['size'],
            'size_b': sb['size'],
            'size_delta': sb['size'] - sa['size'],
            'hash_a': sa['hash'],
            'hash_b': sb['hash'],
            'identical': sa['hash'] == sb['hash'],
        })

    return {
        'a': report_a,
        'b': report_b,
        'version_match': report_a['version'] == report_b['version'],
        'size_delta': report_b['total_size'] - report_a['total_size'],
        'only_in_a': [f"0x{t:02x} ({SECTION_NAMES.get(t, '?')})" for t in sorted(only_a)],
        'only_in_b': [f"0x{t:02x} ({SECTION_NAMES.get(t, '?')})" for t in sorted(only_b)],
        'common_sections': section_diffs,
        'all_common_identical': all(d['identical'] for d in section_diffs),
    }


def compare_levels_records(rec_a, rec_b, label_a='A', label_b='B'):
    """Compare two LEVELS index records (ints_raw, fname, etc.)."""
    ir_a = struct.unpack_from('<13i', rec_a['ints_raw'], 0)
    ir_b = struct.unpack_from('<13i', rec_b['ints_raw'], 0)
    return {
        'fname_a': rec_a['fname'],
        'fname_b': rec_b['fname'],
        'fname_match': rec_a['fname'].lower() == rec_b['fname'].lower(),
        'grid_a': list(ir_a[6:9]),
        'grid_b': list(ir_b[6:9]),
        'grid_match': ir_a[6:9] == ir_b[6:9],
        'dims_a': [ir_a[3], ir_a[5]],
        'dims_b': [ir_b[3], ir_b[5]],
        'dims_match': (ir_a[3], ir_a[5]) == (ir_b[3], ir_b[5]),
        'guid_a': list(ir_a[9:13]),
        'guid_b': list(ir_b[9:13]),
        'guid_match': ir_a[9:13] == ir_b[9:13],
        'ints_raw_identical': rec_a['ints_raw'] == rec_b['ints_raw'],
    }


def format_report_text(diff):
    """Format a comparison report as readable text."""
    lines = []
    a = diff['a']
    b = diff['b']
    lines.append(f"=== Blob Comparison: {a['label']} vs {b['label']} ===")
    lines.append(f"  {a['label']}: {a['total_size']} bytes, {a['version_name']}, {a['section_count']} sections")
    lines.append(f"  {b['label']}: {b['total_size']} bytes, {b['version_name']}, {b['section_count']} sections")
    lines.append(f"  Size delta: {diff['size_delta']:+d} bytes")
    lines.append(f"  Version match: {diff['version_match']}")

    if diff['only_in_a']:
        lines.append(f"  Only in {a['label']}: {', '.join(diff['only_in_a'])}")
    if diff['only_in_b']:
        lines.append(f"  Only in {b['label']}: {', '.join(diff['only_in_b'])}")

    lines.append(f"  Common sections ({len(diff['common_sections'])}):")
    for sd in diff['common_sections']:
        status = 'IDENTICAL' if sd['identical'] else f"DIFFER (delta={sd['size_delta']:+d})"
        lines.append(f"    {sd['type_hex']} {sd['name']}: {sd['size_a']} vs {sd['size_b']} -- {status}")

    lines.append(f"  All common identical: {diff['all_common_identical']}")
    return '\n'.join(lines)


def format_inspect_text(report):
    """Format an inspection report as readable text."""
    lines = []
    lines.append(f"=== Blob: {report['label']} ===")
    lines.append(f"  Size: {report['total_size']} bytes")
    lines.append(f"  Version: {report['version_name']}")
    lines.append(f"  Sections ({report['section_count']}):")
    for s in report['sections']:
        lines.append(f"    {s['type_hex']} {s['name']}: {s['size']} bytes (hash: {s['hash']})")
    return '\n'.join(lines)


if __name__ == '__main__':
    from arc_patcher import ArcArchive
    from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

    svaera_path = Path(r'reference_mods\SVAERA_customquest\Resources\Levels.arc')
    sv_path = Path(r'upstream\soulvizier_098i\Resources\Levels.arc')

    print('Loading maps...')
    ae_arc = ArcArchive.from_file(svaera_path)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sec = {s['type']: s for s in parse_sections(ae_data)}
    ae_levels = parse_level_index(ae_data, ae_sec[SEC_LEVELS])

    sv_arc = ArcArchive.from_file(sv_path)
    sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
    sv_sec = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec[SEC_LEVELS])

    # Compare RuinedCity02 between SVAERA and SV
    ae_idx = 30
    sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}
    ae_lv = ae_levels[ae_idx]
    ae_key = ae_lv['fname'].replace('\\', '/').lower()
    sv_idx = sv_by_name.get(ae_key)

    if sv_idx is not None:
        sv_lv = sv_levels[sv_idx]
        ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
        sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]

        diff = compare_blobs(ae_blob, sv_blob, f'SVAERA idx={ae_idx}', f'SV idx={sv_idx}')
        print(format_report_text(diff))
        print()

        rec_diff = compare_levels_records(ae_lv, sv_lv, 'SVAERA', 'SV')
        print('LEVELS record comparison:')
        for k, v in rec_diff.items():
            print(f'  {k}: {v}')
