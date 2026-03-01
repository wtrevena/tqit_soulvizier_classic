#!/usr/bin/env python3
"""
Forensic comparison of the original SVAERA DelphiLowlands04 blob vs our
surgically modified version. Compare every byte to find what differs.
"""
import struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_DATA

svaera_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
merged_arc = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

TARGET = 'levels/world/greece/delphi/delphilowlands04.lvl'


def parse_blob_sections(blob):
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
        sections.append({
            'type': st, 'size': ss, 'header_pos': pos,
            'data_pos': pos + 8, 'data': blob[pos + 8:pos + 8 + ss]
        })
        pos += 8 + ss
    return sections, magic


def parse_0x14_records(data):
    records = []
    pos = 0
    while pos + 8 <= len(data):
        idx = struct.unpack_from('<I', data, pos)[0]
        payload_size = struct.unpack_from('<I', data, pos + 4)[0]
        if payload_size > 1000 or pos + 8 + payload_size > len(data):
            print(f'    0x14 parse stopped at pos {pos}: idx={idx}, payload_size={payload_size}')
            break
        payload = data[pos + 8:pos + 8 + payload_size]
        records.append({'index': idx, 'payload_size': payload_size, 'payload': payload, 'pos': pos})
        pos += 8 + payload_size
    return records


def main():
    print('Loading SVAERA map...')
    ae_arc_obj = ArcArchive.from_file(svaera_arc)
    ae_data = ae_arc_obj.decompress([e for e in ae_arc_obj.entries if e.entry_type == 3][0])
    ae_secs = parse_sections(ae_data)
    ae_sec_map = {s['type']: s for s in ae_secs}
    ae_levels = parse_level_index(ae_data, ae_sec_map[SEC_LEVELS])
    ae_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(ae_levels)}

    print('Loading merged map...')
    mg_arc_obj = ArcArchive.from_file(merged_arc)
    mg_data = mg_arc_obj.decompress([e for e in mg_arc_obj.entries if e.entry_type == 3][0])
    mg_secs = parse_sections(mg_data)
    mg_sec_map = {s['type']: s for s in mg_secs}
    mg_levels = parse_level_index(mg_data, mg_sec_map[SEC_LEVELS])
    mg_by_name = {lv['fname'].replace('\\', '/').lower(): i for i, lv in enumerate(mg_levels)}

    if TARGET not in ae_by_name or TARGET not in mg_by_name:
        print(f'Target not found!')
        return

    ae_lv = ae_levels[ae_by_name[TARGET]]
    mg_lv = mg_levels[mg_by_name[TARGET]]

    print(f'\n=== Level Entry Comparison: {TARGET} ===')
    print(f'  SVAERA: offset={ae_lv["data_offset"]}, length={ae_lv["data_length"]}')
    print(f'  Merged: offset={mg_lv["data_offset"]}, length={mg_lv["data_length"]}')
    print(f'  ints_raw match: {ae_lv["ints_raw"] == mg_lv["ints_raw"]}')

    if ae_lv['ints_raw'] != mg_lv['ints_raw']:
        for i in range(13):
            av = struct.unpack_from('<I', ae_lv['ints_raw'], i*4)[0]
            mv = struct.unpack_from('<I', mg_lv['ints_raw'], i*4)[0]
            if av != mv:
                print(f'    ints_raw[{i}]: SVAERA=0x{av:08x}, merged=0x{mv:08x}')

    ae_blob = ae_data[ae_lv['data_offset']:ae_lv['data_offset'] + ae_lv['data_length']]
    mg_blob = mg_data[mg_lv['data_offset']:mg_lv['data_offset'] + mg_lv['data_length']]

    print(f'\n  Blob sizes: SVAERA={len(ae_blob)}, merged={len(mg_blob)}')
    print(f'  Blob magic: SVAERA=0x{struct.unpack("<I", ae_blob[:4])[0]:08x}, merged=0x{struct.unpack("<I", mg_blob[:4])[0]:08x}')

    ae_bsecs, _ = parse_blob_sections(ae_blob)
    mg_bsecs, _ = parse_blob_sections(mg_blob)

    print(f'\n=== Section-by-section comparison ===')
    for i in range(max(len(ae_bsecs), len(mg_bsecs))):
        ae_s = ae_bsecs[i] if i < len(ae_bsecs) else None
        mg_s = mg_bsecs[i] if i < len(mg_bsecs) else None

        if ae_s and mg_s:
            match = ae_s['data'] == mg_s['data']
            print(f'  [{i}] type=0x{ae_s["type"]:02x}: SVAERA={ae_s["size"]} bytes, merged={mg_s["size"]} bytes, match={match}')
            if not match and ae_s['type'] == 0x05:
                # Detailed 0x05 comparison
                ae_count = struct.unpack_from('<I', ae_s['data'], 0)[0]
                mg_count = struct.unpack_from('<I', mg_s['data'], 0)[0]
                print(f'    0x05 count: SVAERA={ae_count}, merged={mg_count}')
                # Check that SVAERA's strings are a prefix of merged's
                ae_pos = 4
                mg_pos = 4
                for j in range(ae_count):
                    ae_slen = struct.unpack_from('<I', ae_s['data'], ae_pos)[0]
                    mg_slen = struct.unpack_from('<I', mg_s['data'], mg_pos)[0]
                    ae_str = ae_s['data'][ae_pos+4:ae_pos+4+ae_slen]
                    mg_str = mg_s['data'][mg_pos+4:mg_pos+4+mg_slen]
                    if ae_str != mg_str:
                        print(f'    MISMATCH at object {j}: ae={ae_str[:60]}, mg={mg_str[:60]}')
                        break
                    ae_pos += 4 + ae_slen
                    mg_pos += 4 + mg_slen
                else:
                    print(f'    First {ae_count} objects match (SVAERA prefix preserved)')
                    # Show new objects
                    for j in range(ae_count, mg_count):
                        slen = struct.unpack_from('<I', mg_s['data'], mg_pos)[0]
                        s = mg_s['data'][mg_pos+4:mg_pos+4+slen].decode('ascii', errors='replace')
                        mg_pos += 4 + slen
                        print(f'    NEW [{j}]: {s}')

            if not match and ae_s['type'] == 0x14:
                # Detailed 0x14 comparison
                ae_recs = parse_0x14_records(ae_s['data'])
                mg_recs = parse_0x14_records(mg_s['data'])
                print(f'    0x14 records: SVAERA={len(ae_recs)}, merged={len(mg_recs)}')
                # Check original records preserved
                mismatch = 0
                for j in range(min(len(ae_recs), len(mg_recs))):
                    if j < len(ae_recs):
                        ar = ae_recs[j]
                        mr = mg_recs[j]
                        if ar['index'] != mr['index'] or ar['payload'] != mr['payload']:
                            if mismatch < 3:
                                print(f'    Record {j} MISMATCH: ae_idx={ar["index"]}, mg_idx={mr["index"]}')
                            mismatch += 1
                if mismatch == 0:
                    print(f'    First {len(ae_recs)} records match (SVAERA preserved)')
                else:
                    print(f'    {mismatch} records differ!')
                # Show new records
                for j in range(len(ae_recs), len(mg_recs)):
                    r = mg_recs[j]
                    print(f'    NEW record: idx={r["index"]}, payload_size={r["payload_size"]}')

        elif ae_s:
            print(f'  [{i}] type=0x{ae_s["type"]:02x}: SVAERA only ({ae_s["size"]} bytes)')
        elif mg_s:
            print(f'  [{i}] type=0x{mg_s["type"]:02x}: Merged only ({mg_s["size"]} bytes)')

    # Check overall blob structure validity
    print(f'\n=== Blob structure validation ===')
    total_ae = 4 + sum(8 + s['size'] for s in ae_bsecs)
    total_mg = 4 + sum(8 + s['size'] for s in mg_bsecs)
    print(f'  SVAERA: calculated={total_ae}, actual={len(ae_blob)}, match={total_ae == len(ae_blob)}')
    print(f'  Merged: calculated={total_mg}, actual={len(mg_blob)}, match={total_mg == len(mg_blob)}')

    del ae_data, mg_data


if __name__ == '__main__':
    main()
