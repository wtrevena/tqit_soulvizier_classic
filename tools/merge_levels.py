#!/usr/bin/env python3
"""
Merge Soulvizier custom map content into SVAERA's AE-compatible map.

Takes two decompiled map directories (from map_decompiler.py):
  - SVAERA base (AE pathfinding, but all custom SV content stripped)
  - SV 0.98i source (all custom content, but TQIT-era pathfinding)

Produces a merged decompiled map that can be compiled with MapCompiler.exe.

Steps:
  1. Copy SVAERA decompiled as the base (preserves AE pathfinding for shared levels)
  2. Copy SV-only levels (.lvl/.rlv/.tga) into the merged output
  3. For shared levels that had SV custom objects, replace with SV versions
  4. Merge WRL: add SV-only level entries + SV-only quests
"""

import struct
import shutil
import sys
from pathlib import Path
from collections import OrderedDict


WRL_MAGIC = 0x074C5257


def read_uint32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def parse_wrl(wrl_path):
    """Parse a WRL file into its components."""
    data = wrl_path.read_bytes()
    magic = read_uint32(data, 0)
    assert magic == WRL_MAGIC, f"Not a WRL file (magic=0x{magic:08X})"

    pos = 4
    sections = []
    while pos + 8 <= len(data):
        sec_type = read_uint32(data, pos)
        sec_size = read_uint32(data, pos + 4)
        sec_data = data[pos + 8:pos + 8 + sec_size]
        sections.append((sec_type, sec_data))
        pos += 8 + sec_size

    levels = []
    quests_data = None
    groups_data = None
    bitmap_data = None

    for sec_type, sec_data in sections:
        if sec_type == 0x13:  # Level index in WRL
            count = read_uint32(sec_data, 0)
            idx = 4
            for _ in range(count):
                fname_len = read_uint32(sec_data, idx); idx += 4
                fname = sec_data[idx:idx + fname_len].decode('ascii', errors='replace')
                idx += fname_len
                floats = list(struct.unpack_from('<6f', sec_data, idx))
                idx += 24
                ints = list(struct.unpack_from('<7I', sec_data, idx))
                idx += 28
                dbr_len = read_uint32(sec_data, idx); idx += 4
                dbr = sec_data[idx:idx + dbr_len].decode('ascii', errors='replace')
                idx += dbr_len
                levels.append({
                    'filename': fname,
                    'floats': floats,
                    'ints': ints,
                    'dbr': dbr,
                })
        elif sec_type == 0x1B:
            quests_data = sec_data
        elif sec_type == 0x11:
            groups_data = sec_data
        elif sec_type == 0x15:
            bitmap_data = sec_data

    return {
        'levels': levels,
        'quests': quests_data,
        'groups': groups_data,
        'bitmaps': bitmap_data,
        'sections': sections,
    }


def write_wrl(wrl_path, levels, quests_data, groups_data, bitmap_data):
    """Write a WRL file from components."""
    wrl = bytearray()
    wrl += struct.pack('<I', WRL_MAGIC)

    # Write levels section (type 0x13)
    body = bytearray()
    body += struct.pack('<I', len(levels))
    for lv in levels:
        fname_bytes = lv['filename'].encode('ascii')
        dbr_bytes = lv['dbr'].encode('ascii')
        body += struct.pack('<I', len(fname_bytes))
        body += fname_bytes
        body += struct.pack('<6f', *lv['floats'])
        body += struct.pack('<7I', *lv['ints'])
        body += struct.pack('<I', len(dbr_bytes))
        body += dbr_bytes
    wrl += struct.pack('<II', 0x13, len(body))
    wrl += body

    if quests_data:
        wrl += struct.pack('<II', 0x1B, len(quests_data))
        wrl += quests_data
    if groups_data:
        wrl += struct.pack('<II', 0x11, len(groups_data))
        wrl += groups_data
    if bitmap_data:
        wrl += struct.pack('<II', 0x15, len(bitmap_data))
        wrl += bitmap_data

    wrl_path.write_bytes(bytes(wrl))
    return len(wrl)


def parse_quest_list(quest_data):
    """Parse quest section into list of quest filenames."""
    quests = []
    idx = 0
    count = read_uint32(quest_data, idx); idx += 4
    for _ in range(count):
        qlen = read_uint32(quest_data, idx); idx += 4
        qname = quest_data[idx:idx + qlen].decode('ascii', errors='replace')
        idx += qlen
        quests.append(qname)
    return quests


def build_quest_data(quests):
    """Build quest section binary from list of quest filenames."""
    data = bytearray()
    data += struct.pack('<I', len(quests))
    for q in quests:
        qb = q.encode('ascii')
        data += struct.pack('<I', len(qb))
        data += qb
    return bytes(data)


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <svaera_dir> <sv_dir> <output_dir>")
        print("  svaera_dir: decompiled SVAERA map directory")
        print("  sv_dir:     decompiled SV 0.98i map directory")
        print("  output_dir: merged output directory")
        sys.exit(1)

    svaera_dir = Path(sys.argv[1])
    sv_dir = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])

    print("=== Merge Levels ===")
    print(f"  SVAERA base: {svaera_dir}")
    print(f"  SV source:   {sv_dir}")
    print(f"  Output:      {output_dir}")

    # Parse both WRL files
    print("\nParsing SVAERA WRL...")
    ae_wrl = parse_wrl(svaera_dir / 'world01.wrl')
    print(f"  {len(ae_wrl['levels'])} levels")

    print("Parsing SV WRL...")
    sv_wrl = parse_wrl(sv_dir / 'world01.wrl')
    print(f"  {len(sv_wrl['levels'])} levels")

    # Build lookup by normalized filename
    ae_by_name = OrderedDict()
    for lv in ae_wrl['levels']:
        key = lv['filename'].replace('\\', '/').lower()
        ae_by_name[key] = lv

    sv_by_name = OrderedDict()
    for lv in sv_wrl['levels']:
        key = lv['filename'].replace('\\', '/').lower()
        sv_by_name[key] = lv

    only_sv = set(sv_by_name.keys()) - set(ae_by_name.keys())
    both = set(sv_by_name.keys()) & set(ae_by_name.keys())

    # Identify shared levels where SV has custom drxmap objects
    print("\nScanning SV levels for custom content...")
    sv_custom_shared = []
    for key in sorted(both):
        sv_lv = sv_by_name[key]
        fname = sv_lv['filename']
        base = fname[:-4] if fname.lower().endswith(('.lvl', '.rlv')) else fname
        rlv_path = sv_dir / (base + '.rlv')
        if rlv_path.exists():
            rlv_data = rlv_path.read_bytes()
            if b'drxmap' in rlv_data:
                sv_custom_shared.append(key)

    print(f"  {len(only_sv)} SV-only levels")
    print(f"  {len(sv_custom_shared)} shared levels with SV custom objects")

    # Step 1: Copy SVAERA base
    print(f"\nStep 1: Copying SVAERA base to {output_dir}...")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(svaera_dir, output_dir)
    # Remove SVAERA's test map output if present
    test_map = output_dir / 'output_test.map'
    if test_map.exists():
        test_map.unlink()
    print("  Done")

    # Step 2: Copy SV-only level files
    print(f"\nStep 2: Copying {len(only_sv)} SV-only levels...")
    copied = 0
    for key in sorted(only_sv):
        sv_lv = sv_by_name[key]
        fname = sv_lv['filename']
        base = fname[:-4] if fname.lower().endswith(('.lvl', '.rlv')) else fname

        for ext in ('.lvl', '.rlv', '.tga'):
            src = sv_dir / (base + ext)
            dst = output_dir / (base + ext)
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
    print(f"  Copied {copied} files")

    # Step 3: Replace shared levels that have SV custom objects
    print(f"\nStep 3: Replacing {len(sv_custom_shared)} shared levels with SV versions (custom objects)...")
    replaced = 0
    for key in sv_custom_shared:
        sv_lv = sv_by_name[key]
        fname = sv_lv['filename']
        base = fname[:-4] if fname.lower().endswith(('.lvl', '.rlv')) else fname

        for ext in ('.lvl', '.rlv'):
            src = sv_dir / (base + ext)
            dst = output_dir / (base + ext)
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                replaced += 1
        print(f"  Replaced: {fname}")
    print(f"  Replaced {replaced} files")

    # Step 4: Merge WRL - add SV-only levels and quests
    print("\nStep 4: Merging WRL...")

    # Start with all SVAERA levels
    merged_levels = list(ae_wrl['levels'])

    # Add SV-only levels
    for key in sorted(only_sv):
        sv_lv = sv_by_name[key]
        merged_levels.append(sv_lv)
    print(f"  Merged level count: {len(merged_levels)}")

    # Merge quests
    ae_quests = parse_quest_list(ae_wrl['quests']) if ae_wrl['quests'] else []
    sv_quests = parse_quest_list(sv_wrl['quests']) if sv_wrl['quests'] else []
    ae_quest_set = set(q.lower() for q in ae_quests)
    new_quests = [q for q in sv_quests if q.lower() not in ae_quest_set]
    merged_quests = ae_quests + new_quests
    if new_quests:
        print(f"  Added {len(new_quests)} SV-only quests:")
        for q in new_quests:
            print(f"    {q}")
    merged_quest_data = build_quest_data(merged_quests)

    # Write merged WRL
    wrl_size = write_wrl(
        output_dir / 'world01.wrl',
        merged_levels,
        merged_quest_data,
        ae_wrl['groups'],
        ae_wrl['bitmaps'],
    )
    print(f"  Wrote merged world01.wrl ({wrl_size} bytes)")

    # Copy SV's .sd file (contains scene data with SV custom areas)
    sv_sd = sv_dir / 'world01.sd'
    ae_sd = output_dir / 'world01.sd'
    if sv_sd.exists() and ae_sd.exists():
        sv_sd_size = sv_sd.stat().st_size
        ae_sd_size = ae_sd.stat().st_size
        if sv_sd_size != ae_sd_size:
            print(f"  Note: SD files differ (SV={sv_sd_size}, SVAERA={ae_sd_size})")
            print(f"  Keeping SVAERA's SD (AE-compatible)")

    print(f"\n=== Merge complete ===")
    print(f"  Total levels: {len(merged_levels)}")
    print(f"  Total quests: {len(merged_quests)}")
    print(f"  SV-only levels added: {len(only_sv)}")
    print(f"  Shared levels replaced: {len(sv_custom_shared)}")
    print(f"\nNext: compile with MapCompiler.exe")
    print(f'  MapCompiler.exe "{output_dir}\\world01.wrl" "{output_dir}\\\\" "{output_dir}\\world01.map"')


if __name__ == '__main__':
    main()
