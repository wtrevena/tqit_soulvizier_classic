#!/usr/bin/env python3
"""
Section-level surgery: inject drxmap objects into SVAERA levels.

Strategy: MERGE SV's drxmap object strings into SVAERA's 0x05 section (append only),
and extend SVAERA's 0x14 section with default entries for the new objects.
This keeps all existing objects and their per-object metadata (0x14) in sync.

Also appends 46 SV-only levels and patches DATA2 count.
"""
import sys, struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (
    parse_sections, parse_level_index, build_level_index,
    parse_quests, build_quests, parse_bitmap_index, build_bitmap_index,
    SEC_LEVELS, SEC_DATA, SEC_DATA2, SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_BITMAPS,
    MAP_MAGIC
)

svaera_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
sv_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
output_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')


def parse_blob_sections(blob):
    """Parse internal sections of a level blob."""
    sections = []
    if len(blob) < 4:
        return sections, b''
    magic = blob[:4]
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            break
        sections.append({'type': st, 'size': ss, 'data': blob[pos + 8:pos + 8 + ss]})
        pos += 8 + ss
    return sections, magic


def rebuild_blob(magic, sections):
    """Rebuild a level blob from magic + sections."""
    out = bytearray(magic)
    for s in sections:
        out += struct.pack('<II', s['type'], len(s['data']))
        out += s['data']
    return bytes(out)


def parse_0x05_strings(data):
    """Parse 0x05 section as flat list of length-prefixed DBR strings."""
    if len(data) < 4:
        return []
    count = struct.unpack_from('<I', data, 0)[0]
    strings = []
    pos = 4
    for _ in range(count):
        if pos + 4 > len(data):
            break
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        if pos + slen > len(data):
            break
        strings.append(data[pos:pos + slen])
        pos += slen
    return strings


def build_0x05_data(string_list):
    """Build 0x05 section data from list of raw byte strings."""
    buf = bytearray()
    buf += struct.pack('<I', len(string_list))
    for s in string_list:
        buf += struct.pack('<I', len(s))
        buf += s
    return bytes(buf)


def parse_0x14_records(data):
    """Parse 0x14 section as variable-length records: index(4) + size(4) + payload."""
    records = []
    pos = 0
    while pos + 8 <= len(data):
        idx = struct.unpack_from('<I', data, pos)[0]
        payload_size = struct.unpack_from('<I', data, pos + 4)[0]
        if pos + 8 + payload_size > len(data):
            break
        payload = data[pos + 8:pos + 8 + payload_size]
        records.append({'index': idx, 'payload_size': payload_size, 'payload': payload})
        pos += 8 + payload_size
    return records


def build_0x14_data(records):
    """Build 0x14 section data from record list."""
    buf = bytearray()
    for r in records:
        buf += struct.pack('<II', r['index'], r['payload_size'])
        buf += r['payload']
    return bytes(buf)


# Default 0x14 record payload (20 bytes): flags=2, 0, 1, 1, 0
DEFAULT_0x14_PAYLOAD = struct.pack('<IIIII', 2, 0, 1, 1, 0)


ENTRANCE_NPC_DBR = b'records\\quests\\portal_uberdungeon_entrance.dbr'
RETURN_NPC_DBR = b'records\\quests\\portal_uberdungeon_return.dbr'
BLOODCAVE_ENTRANCE_NPC_DBR = b'records\\quests\\portal_bloodcave_entrance.dbr'
BLOODCAVE_RETURN_NPC_DBR = b'records\\quests\\portal_bloodcave_return.dbr'

# Injection specs: level name key -> list of (dbr_bytes, x, y, z) to inject
# DelphiLowlands04: merchant tent at (12.88, 9.98, 2.52), quest NPC at (14.03, 10.16, 6.15)
# crypt_floor1: minotaur statue at (139.73, 11.84, 212.30), existing arena portal at (139.94, 10.01, 231.94)
# HiddenValley01: cave entrance at (14.0, 18.0, 26.0), POI at (15.84, 18.0, 26.58)
# BC_initialpathway: SV blood cave entrance level
INJECT_SPECS = {
    'levels/world/greece/delphi/delphilowlands04.lvl': [
        (ENTRANCE_NPC_DBR, 4.0, 10.0, 14.0),
    ],
    'levels/world/uberdungeon/crypt_floor1.lvl': [
        (RETURN_NPC_DBR, 140.0, 10.0, 215.0),
    ],
    'levels/world/orient/silkroad/hiddenvalley01.lvl': [
        (BLOODCAVE_ENTRANCE_NPC_DBR, 16.0, 18.0, 26.0),
    ],
    'levels/world/xbloodcave/bc_initialpathway.lvl': [
        (BLOODCAVE_RETURN_NPC_DBR, 20.0, 5.0, 12.0),
    ],
}

UBER_DUNGEON_QUEST_NAMES = ['Quests/uberdungeon_entrance.qst', 'Quests/uberdungeon_return.qst']
BLOODCAVE_QUEST_NAMES = ['Quests/bloodcave_entrance.qst', 'Quests/bloodcave_return.qst']
ALL_CUSTOM_QUEST_NAMES = UBER_DUNGEON_QUEST_NAMES + BLOODCAVE_QUEST_NAMES


def inject_into_0x05(section_data, injections):
    """Append new objects to a v0x0e 0x05 section.

    section_data: raw bytes of the 0x05 section
    injections: list of (dbr_bytes, x, y, z) to add

    Returns modified section_data with new strings and instance records appended.

    v0x0e 0x05 format:
      uint32 string_count
      string_count * {uint32 length, char[length] dbr_path}
      uint32 instance_count
      instance_count * 56-byte records:
        +0:  uint32  string_index
        +4:  float[9] rotation_matrix (3x3, flat row-major, no padding)
        +40: float   world_x
        +44: float   world_y
        +48: float   world_z
        +52: uint32  flags (0 = normal)
    """
    if not injections:
        return section_data

    pos = 0
    string_count = struct.unpack_from('<I', section_data, pos)[0]
    pos += 4

    existing_strings = []
    for _ in range(string_count):
        slen = struct.unpack_from('<I', section_data, pos)[0]
        pos += 4
        existing_strings.append(section_data[pos:pos + slen])
        pos += slen

    strings_end = pos
    instance_count = struct.unpack_from('<I', section_data, strings_end)[0]
    instances_start = strings_end + 4
    instances_data = section_data[instances_start:]

    new_strings = list(existing_strings)
    new_instances = bytearray(instances_data)
    new_instance_count = instance_count

    for dbr_bytes, x, y, z in injections:
        if dbr_bytes in new_strings:
            str_idx = new_strings.index(dbr_bytes)
        else:
            str_idx = len(new_strings)
            new_strings.append(dbr_bytes)

        # Identity rotation matrix: flat 3x3 row-major, no padding
        record = struct.pack('<I', str_idx)              # string_index
        record += struct.pack('<fffffffff',              # 3x3 rotation matrix
                              1.0, 0.0, 0.0,            # row0
                              0.0, 1.0, 0.0,            # row1
                              0.0, 0.0, 1.0)            # row2
        record += struct.pack('<fff', x, y, z)            # world position
        record += struct.pack('<I', 0)                    # flags
        new_instances += record
        new_instance_count += 1

    out = bytearray()
    out += struct.pack('<I', len(new_strings))
    for s in new_strings:
        out += struct.pack('<I', len(s))
        out += s
    out += struct.pack('<I', new_instance_count)
    out += new_instances
    return bytes(out)


def inject_into_sv_only_blob(blob, injections, level_name):
    """Inject objects into an SV-only level blob by modifying its 0x05 section."""
    secs, magic = parse_blob_sections(blob)
    if not secs:
        return blob

    modified = False
    new_secs = []
    for s in secs:
        if s['type'] == 0x05 and injections:
            new_data = inject_into_0x05(s['data'], injections)
            new_secs.append({'type': 0x05, 'data': new_data})
            modified = True
            print(f'    Injected {len(injections)} object(s) into SV-only {level_name}')
        else:
            new_secs.append(s)

    if modified:
        return rebuild_blob(magic, new_secs)
    return blob


V0E_RECORD_SIZE = 56
V11_RECORD_SIZE = 72
V0E_MAGIC = struct.pack('<I', 0x0e4c564c)
V11_MAGIC = struct.pack('<I', 0x114c564c)


def convert_0x05_v0e_to_v11(data):
    """Convert v0x0e 0x05 section data (56-byte records) to v0x11 format (72-byte records).

    The string table is identical between formats. Only the instance records differ:
    v0x11 has 16 extra zero bytes appended to each 56-byte v0x0e record.
    """
    pos = 0
    string_count = struct.unpack_from('<I', data, pos)[0]
    pos += 4

    # Skip past string table (identical format)
    for _ in range(string_count):
        if pos + 4 > len(data):
            return None
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4 + slen

    strings_end = pos
    if strings_end + 4 > len(data):
        return None

    instance_count = struct.unpack_from('<I', data, strings_end)[0]
    instances_start = strings_end + 4
    instances_data = data[instances_start:]

    expected = instance_count * V0E_RECORD_SIZE
    if len(instances_data) < expected:
        return None

    # Build v0x11 instance data: each v0x0e 56-byte record + 16 zero bytes
    v11_instances = bytearray()
    for i in range(instance_count):
        offset = i * V0E_RECORD_SIZE
        v11_instances += instances_data[offset:offset + V0E_RECORD_SIZE]
        v11_instances += b'\x00' * 16

    # Reassemble: string table (unchanged) + v0x11 instance records
    out = bytearray(data[:strings_end])
    out += struct.pack('<I', instance_count)
    out += v11_instances
    # Include any trailing data after instances (unlikely but safe)
    trailing_start = instances_start + expected
    if trailing_start < len(data):
        out += data[trailing_start:]
    return bytes(out)


def inject_into_0x05_v11(section_data, injections):
    """Append new objects to a v0x11 0x05 section (72-byte records).

    Same as inject_into_0x05 but produces 72-byte records (56 + 16 zero bytes).
    """
    if not injections:
        return section_data

    pos = 0
    string_count = struct.unpack_from('<I', section_data, pos)[0]
    pos += 4

    existing_strings = []
    for _ in range(string_count):
        slen = struct.unpack_from('<I', section_data, pos)[0]
        pos += 4
        existing_strings.append(section_data[pos:pos + slen])
        pos += slen

    strings_end = pos
    instance_count = struct.unpack_from('<I', section_data, strings_end)[0]
    instances_start = strings_end + 4
    instances_data = section_data[instances_start:instances_start + instance_count * V11_RECORD_SIZE]

    new_strings = list(existing_strings)
    new_instances = bytearray(instances_data)
    new_instance_count = instance_count

    for dbr_bytes, x, y, z in injections:
        if dbr_bytes in new_strings:
            str_idx = new_strings.index(dbr_bytes)
        else:
            str_idx = len(new_strings)
            new_strings.append(dbr_bytes)

        # 56-byte v0x0e record + 16 zero bytes = 72-byte v0x11 record
        record = struct.pack('<I', str_idx)
        record += struct.pack('<fffffffff',              # 3x3 rotation matrix
                              1.0, 0.0, 0.0,            # row0
                              0.0, 1.0, 0.0,            # row1
                              0.0, 0.0, 1.0)            # row2
        record += struct.pack('<fff', x, y, z)             # world position
        record += struct.pack('<I', 0)                     # flags
        record += b'\x00' * 16                             # v0x11 extra bytes
        new_instances += record
        new_instance_count += 1

    out = bytearray()
    out += struct.pack('<I', len(new_strings))
    for s in new_strings:
        out += struct.pack('<I', len(s))
        out += s
    out += struct.pack('<I', new_instance_count)
    out += new_instances
    return bytes(out)


def count_0x05_instances(data):
    """Count instances in a 0x05 section (works for both v0x0e and v0x11)."""
    pos = 0
    string_count = struct.unpack_from('<I', data, pos)[0]
    pos += 4
    for _ in range(string_count):
        if pos + 4 > len(data):
            return 0
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4 + slen
    if pos + 4 > len(data):
        return 0
    return struct.unpack_from('<I', data, pos)[0]


def generate_default_0x14(instance_count):
    """Generate default 0x14 records for all instances.

    Each record: index(4) + payload_size(4) + payload(20).
    Default payload: flags=2, 0, 1, 1, 0.
    """
    buf = bytearray()
    for i in range(instance_count):
        buf += struct.pack('<II', i, len(DEFAULT_0x14_PAYLOAD))
        buf += DEFAULT_0x14_PAYLOAD
    return bytes(buf)


def convert_v0e_blob_to_v11(blob, level_name=''):
    """Convert an entire v0x0e level blob to v0x11 format.

    Used for SV-only levels and shared levels where AE is also v0x0e.
    - Converts 0x05 instance records (56→72 bytes)
    - Removes 0x09 grid section (v0x0e-only, replaced by DATA2 in v0x11)
    - Adds 0x14 metadata section (required for v0x11 interactivity)
    - Changes blob magic from v0x0e to v0x11
    """
    secs, magic = parse_blob_sections(blob)
    if not secs:
        return None

    new_secs = []
    instance_count = 0
    has_0x14 = False

    for s in secs:
        if s['type'] == 0x05:
            # Convert 0x05 from 56-byte to 72-byte records
            converted = convert_0x05_v0e_to_v11(s['data'])
            if converted is None:
                return None
            new_secs.append({'type': 0x05, 'data': converted})
            instance_count = count_0x05_instances(converted)
        elif s['type'] == 0x09:
            # Skip 0x09 grid section (v0x0e-only)
            continue
        elif s['type'] == 0x14:
            has_0x14 = True
            new_secs.append(s)
        else:
            new_secs.append(s)

    # Add 0x14 metadata if not already present
    if not has_0x14 and instance_count > 0:
        new_secs.append({'type': 0x14, 'data': generate_default_0x14(instance_count)})

    return rebuild_blob(V11_MAGIC, new_secs)


def perform_section_surgery(ae_blob, sv_blob, level_name):
    """
    Hybrid blob: inject SV's drxmap objects into SVAERA's level blob.

    Format-aware: detects AE blob's version (v0x11 vs v0x0e) and handles accordingly:
    - v0x11 AE blob: Convert SV's v0x0e 0x05 records (56-byte) to v0x11 (72-byte),
      keep v0x11 magic and all SVAERA terrain/pathfinding sections.
      Generates default 0x14 metadata for all instances (required for v0x11 interactivity).
    - v0x0e AE blob (e.g. Random09A): Return 'use_sv_blob' signal to caller,
      since both versions share the same format and SV's blob has the grid connection.
    """
    ae_secs, ae_magic = parse_blob_sections(ae_blob)
    sv_secs, sv_magic = parse_blob_sections(sv_blob)

    if not ae_secs or not sv_secs:
        return None, "empty sections"

    sv_05 = [s for s in sv_secs if s['type'] == 0x05]
    if not sv_05:
        return None, "SV has no 0x05 section"
    if b'drxmap' not in sv_05[0]['data']:
        return None, "SV 0x05 has no drxmap"

    ae_version = struct.unpack_from('<B', ae_magic, 3)[0] if len(ae_magic) >= 4 else 0

    # v0x0e AE blobs (e.g. Random09A): use SV's full blob instead of surgery.
    # Both versions share the same format and SV's blob has grid connections (0x09).
    if ae_version != 0x11:
        return None, "use_sv_blob"

    # v0x11 AE blob: convert SV's v0x0e 0x05 data to v0x11 format
    sv_05_data = sv_05[0]['data']

    # First convert 56-byte records to 72-byte records
    v11_05_data = convert_0x05_v0e_to_v11(sv_05_data)
    if v11_05_data is None:
        return None, "failed to convert 0x05 v0e->v11"

    # Inject any new objects (portals, targets) using v0x11 format
    level_key = level_name.replace('\\', '/').lower()
    if level_key in INJECT_SPECS:
        v11_05_data = inject_into_0x05_v11(v11_05_data, INJECT_SPECS[level_key])
        print(f'    Injected {len(INJECT_SPECS[level_key])} object(s) into 0x05 (v0x11)')

    # Generate default 0x14 metadata for all instances in the new 0x05
    # v0x11 levels require 0x14 records for objects to be interactive (fountains, etc.)
    instance_count = count_0x05_instances(v11_05_data)
    new_0x14_data = generate_default_0x14(instance_count)

    new_secs = []
    for s in ae_secs:
        if s['type'] == 0x05:
            new_secs.append({'type': 0x05, 'data': v11_05_data})
        elif s['type'] == 0x14:
            new_secs.append({'type': 0x14, 'data': new_0x14_data})
        else:
            new_secs.append(s)

    # Keep v0x11 magic — matching SVAERA's terrain/pathfinding format
    result = rebuild_blob(ae_magic, new_secs)

    sv_05_count = struct.unpack_from('<I', sv_05[0]['data'], 0)[0]
    ae_05 = [s for s in ae_secs if s['type'] == 0x05]
    ae_05_count = struct.unpack_from('<I', ae_05[0]['data'], 0)[0] if ae_05 else 0
    drx_count = result.count(b'drxmap')
    return result, f"hybrid v11: strings {ae_05_count}->{sv_05_count}, 0x14: {instance_count} records, drxmap: {drx_count}"


def main():
    print('Loading SVAERA...')
    ae_arc = ArcArchive.from_file(svaera_arc_path)
    ae_data = ae_arc.decompress([e for e in ae_arc.entries if e.entry_type == 3][0])
    ae_sections = parse_sections(ae_data)
    ae_sec_map = {s['type']: s for s in ae_sections}
    ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
    ae_quests = parse_quests(ae_data, ae_sec_map[SEC_QUESTS])
    ae_bitmaps = parse_bitmap_index(ae_data, ae_sec_map[SEC_BITMAPS])
    bmp_unknown = struct.unpack_from('<I', ae_data, ae_sec_map[SEC_BITMAPS]['data_offset'])[0]
    print(f'  {len(ae_levels)} levels')

    print('Loading SV...')
    sv_arc = ArcArchive.from_file(sv_arc_path)
    sv_data = sv_arc.decompress([e for e in sv_arc.entries if e.entry_type == 3][0])
    sv_sec_map = {s['type']: s for s in parse_sections(sv_data)}
    sv_levels = parse_level_index(sv_data, sv_sec_map[SEC_LEVELS])
    sv_quests = parse_quests(sv_data, sv_sec_map[SEC_QUESTS])
    print(f'  {len(sv_levels)} levels')

    # Build name lookups
    ae_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(ae_levels)}
    sv_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(sv_levels)}

    # Identify levels
    sv_only = []
    sv_shared_drx = []
    for lv in sv_levels:
        key = lv['fname'].replace('\\', '/').lower()
        chunk = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if key not in ae_by_name:
            sv_only.append(lv)
        elif b'drxmap' in chunk:
            sv_shared_drx.append((lv, ae_by_name[key]))

    print(f'\n  SV-only: {len(sv_only)} levels to append')
    print(f'  Shared with drxmap: {len(sv_shared_drx)} levels for section surgery')

    # Perform section surgery on shared levels
    print('\n=== Section Surgery ===')
    surgery_blobs = {}  # ae_idx -> new blob
    sv_full_blob_levels = {}  # ae_idx -> (sv_blob, sv_lv) for v0x0e levels
    for sv_lv, ae_idx in sv_shared_drx:
        ae_lv = ae_levels[ae_idx]
        ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
        sv_blob = sv_data[sv_lv['data_offset']:sv_lv['data_offset'] + sv_lv['data_length']]

        result, info = perform_section_surgery(ae_blob, sv_blob, ae_lv['fname'])
        if result:
            surgery_blobs[ae_idx] = result
            print(f'  OK: {ae_lv["fname"]} ({info})')
        elif info == "use_sv_blob":
            sv_full_blob_levels[ae_idx] = (sv_blob, sv_lv)
            print(f'  FULL: {ae_lv["fname"]} (using SV full blob + ints_raw)')
        else:
            print(f'  SKIP: {ae_lv["fname"]} ({info})')

    # Merge quests
    ae_quest_set = set(q.lower() for q in ae_quests)
    new_quests = [q for q in sv_quests if q.lower() not in ae_quest_set]
    merged_quests = ae_quests + new_quests

    # Add custom quests for Uber Dungeon portal wiring
    existing_lower = set(q.lower() if isinstance(q, str) else q.decode('ascii', errors='replace').lower()
                         for q in merged_quests)
    added = 0
    for qname in UBER_DUNGEON_QUEST_NAMES:
        if qname.lower() not in existing_lower:
            merged_quests.append(qname.encode('ascii'))
            existing_lower.add(qname.lower())
            added += 1
    print(f'\n  Quests: {len(ae_quests)} + {len(new_quests)} new + {added} custom = {len(merged_quests)}')

    # Collect blobs to append (SV-only + surgically modified shared levels)
    append_blobs = []
    sv_only_blob_indices = []
    for lv in sv_only:
        sv_only_blob_indices.append(len(append_blobs))
        blob = sv_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]

        # Inject objects into SV-only levels if specified
        lv_key = lv['fname'].replace('\\', '/').lower()
        if lv_key in INJECT_SPECS:
            blob = inject_into_sv_only_blob(blob, INJECT_SPECS[lv_key], lv['fname'])

        append_blobs.append(blob)

    surgery_blob_indices = {}
    for ae_idx, blob in surgery_blobs.items():
        surgery_blob_indices[ae_idx] = len(append_blobs)
        append_blobs.append(blob)

    sv_full_blob_indices = {}
    for ae_idx, (sv_blob, sv_lv) in sv_full_blob_levels.items():
        sv_full_blob_indices[ae_idx] = len(append_blobs)
        append_blobs.append(sv_blob)

    total_append = sum(len(b) for b in append_blobs)
    print(f'  Total append data: {total_append/(1024**2):.1f} MB')

    # Build new sections
    print('\nBuilding merged map...')
    merged_levels = [dict(lv) for lv in ae_levels]
    for lv in sv_only:
        merged_levels.append(dict(lv))

    merged_bitmaps = [dict(b) for b in ae_bitmaps]
    for _ in sv_only:
        merged_bitmaps.append({'offset': 0, 'length': 0})

    new_quests_data = build_quests(merged_quests)
    new_levels_data = build_level_index(merged_levels)
    new_bitmaps_data = build_bitmap_index(merged_bitmaps, bmp_unknown)

    groups_data = ae_data[ae_sec_map[SEC_GROUPS]['data_offset']:ae_sec_map[SEC_GROUPS]['data_offset'] + ae_sec_map[SEC_GROUPS]['size']]
    sd_data = ae_data[ae_sec_map[SEC_SD]['data_offset']:ae_sec_map[SEC_SD]['data_offset'] + ae_sec_map[SEC_SD]['size']]

    unknown_sec = [s for s in ae_sections if s['type'] not in
                   (SEC_QUESTS, SEC_GROUPS, SEC_SD, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2, SEC_DATA)]
    unknown_sections_data = [(s['type'], ae_data[s['data_offset']:s['data_offset'] + s['size']]) for s in unknown_sec]

    # Calculate offsets
    orig_pre_data_size = ae_sec_map[SEC_DATA2]['header_offset']
    new_pre_data_size = 8
    new_pre_data_size += 8 + len(new_quests_data)
    new_pre_data_size += 8 + len(groups_data)
    new_pre_data_size += 8 + len(sd_data)
    new_pre_data_size += 8 + len(new_levels_data)
    new_pre_data_size += 8 + len(new_bitmaps_data)
    for _, ud in unknown_sections_data:
        new_pre_data_size += 8 + len(ud)

    offset_shift = new_pre_data_size - orig_pre_data_size

    data2_raw = bytearray(ae_data[ae_sec_map[SEC_DATA2]['data_offset']:ae_sec_map[SEC_DATA2]['data_offset'] + ae_sec_map[SEC_DATA2]['size']])
    data_raw = ae_data[ae_sec_map[SEC_DATA]['data_offset']:ae_sec_map[SEC_DATA]['data_offset'] + ae_sec_map[SEC_DATA]['size']]

    struct.pack_into('<I', data2_raw, 4, len(merged_levels))
    data2_raw = bytes(data2_raw)

    # Calculate append start
    append_start = new_pre_data_size + 8 + len(data2_raw) + 8 + len(data_raw)

    # Fix offsets
    for i in range(len(ae_levels)):
        merged_levels[i]['data_offset'] = ae_levels[i]['data_offset'] + offset_shift

    # Surgically modified shared levels: point to appended blob
    for ae_idx, blob_idx in surgery_blob_indices.items():
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(blob_idx))
        merged_levels[ae_idx]['data_offset'] = blob_offset
        merged_levels[ae_idx]['data_length'] = len(append_blobs[blob_idx])

    # Full SV blob levels (v0x0e): use SV's ints_raw + full blob
    for ae_idx, blob_idx in sv_full_blob_indices.items():
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(blob_idx))
        sv_lv = sv_full_blob_levels[ae_idx][1]
        merged_levels[ae_idx]['data_offset'] = blob_offset
        merged_levels[ae_idx]['data_length'] = len(append_blobs[blob_idx])
        merged_levels[ae_idx]['ints_raw'] = sv_lv['ints_raw']

    # SV-only levels: point to appended data
    for i, sv_blob_idx in enumerate(sv_only_blob_indices):
        lv_idx = len(ae_levels) + i
        blob_offset = append_start + sum(len(append_blobs[j]) for j in range(sv_blob_idx))
        merged_levels[lv_idx]['data_offset'] = blob_offset

    # Fix bitmap offsets
    for i in range(len(ae_bitmaps)):
        if merged_bitmaps[i]['offset'] > 0:
            merged_bitmaps[i]['offset'] = ae_bitmaps[i]['offset'] + offset_shift

    # Zero bitmap entries for sv_full_blob levels (e.g. Random09A)
    for ae_idx in sv_full_blob_levels:
        merged_bitmaps[ae_idx]['offset'] = 0
        merged_bitmaps[ae_idx]['length'] = 0

    new_levels_data = build_level_index(merged_levels)
    new_bitmaps_data = build_bitmap_index(merged_bitmaps, bmp_unknown)

    # Write
    out = bytearray()
    header2 = new_pre_data_size - 8
    out += struct.pack('<II', MAP_MAGIC, header2)
    out += struct.pack('<II', SEC_QUESTS, len(new_quests_data)) + new_quests_data
    out += struct.pack('<II', SEC_GROUPS, len(groups_data)) + groups_data
    out += struct.pack('<II', SEC_SD, len(sd_data)) + sd_data
    out += struct.pack('<II', SEC_LEVELS, len(new_levels_data)) + new_levels_data
    out += struct.pack('<II', SEC_BITMAPS, len(new_bitmaps_data)) + new_bitmaps_data
    for utype, udata in unknown_sections_data:
        out += struct.pack('<II', utype, len(udata)) + udata
    out += struct.pack('<II', SEC_DATA2, len(data2_raw)) + data2_raw
    extended_data_size = len(data_raw) + total_append
    out += struct.pack('<II', SEC_DATA, extended_data_size) + data_raw
    for blob in append_blobs:
        out += blob

    result = bytes(out)

    # Verify
    print('\n=== Verification ===')
    v_sections = parse_sections(result)
    v_sec_map = {s['type']: s for s in v_sections}
    v_levels = parse_level_index(result, v_sec_map[SEC_LEVELS])

    bad_offsets = sum(1 for lv in v_levels if lv['data_offset'] + lv['data_length'] > len(result))
    bad_magic = sum(1 for lv in v_levels if result[lv['data_offset']:lv['data_offset'] + 3] != b'LVL')
    d2_count = struct.unpack_from('<I', result, v_sec_map[SEC_DATA2]['data_offset'] + 4)[0]

    # Verify surgery levels still have correct LVL version (should be 0x11)
    surgery_vers = {}
    for ae_idx in surgery_blobs:
        lv = v_levels[ae_idx]
        ver = result[lv['data_offset'] + 3]
        surgery_vers[ae_idx] = ver
    for ae_idx in sv_full_blob_levels:
        lv = v_levels[ae_idx]
        ver = result[lv['data_offset'] + 3]
        surgery_vers[ae_idx] = ver

    print(f'  Levels: {len(v_levels)}')
    print(f'  DATA2 count: {d2_count}')
    print(f'  Bad offsets: {bad_offsets}')
    print(f'  Bad magic: {bad_magic}')
    print(f'  drxmap refs: {result.count(b"drxmap")}')
    print(f'  Surgery level versions: {set(f"0x{v:02x}" for v in surgery_vers.values())}')
    print(f'  Size: {len(result)/(1024**2):.1f} MB, under 2GB: {len(result) < 2147483647}')

    # Package into ARC
    print(f'\nPackaging into ARC...')
    arc = ArcArchive.from_file(svaera_arc_path)
    arc.set_file('world/world01.map', result)
    arc.write(output_arc)
    print(f'  ARC: {output_arc.stat().st_size/(1024**2):.1f} MB')

    del ae_data, sv_data, result
    print('Done!')


if __name__ == '__main__':
    main()
