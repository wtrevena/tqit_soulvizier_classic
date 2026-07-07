#!/usr/bin/env python3
"""DIAGNOSTIC (scratch): dump + compare the QUESTS(0x1b) section across
SVAERA original, SV upstream, and the merged output. Root-cause the
'4 SV questlines never load' bug at the byte level. Read-only."""
import sys, struct, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive
from merge_levels_binary import (parse_sections, parse_quests, SEC_QUESTS,
    SEC_LEVELS, parse_level_index)

SVAERA = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
SV     = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc')
MERGED = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

FOUR = ['widowletter', 'urder', 'bossarena', 'open_bloodcave_portal']


def load_map(arc_path):
    arc = ArcArchive.from_file(arc_path)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    return data


def raw_quests_section(data):
    secs = {s['type']: s for s in parse_sections(data)}
    s = secs[SEC_QUESTS]
    buf = data[s['data_offset']:s['data_offset'] + s['size']]
    return buf, s


def dump_quests(label, data):
    buf, s = raw_quests_section(data)
    count = struct.unpack_from('<I', buf, 0)[0]
    print(f'\n===== {label} =====')
    print(f'  section header_offset={s["header_offset"]} data_offset={s["data_offset"]} size={s["size"]}')
    print(f'  declared count(u32 @0) = {count}')
    idx = 4
    entries = []
    bad = 0
    for i in range(count):
        if idx + 4 > len(buf):
            print(f'  !! ran off end at entry {i} (idx={idx} > len={len(buf)})')
            bad += 1
            break
        qlen = struct.unpack_from('<I', buf, idx)[0]
        name = buf[idx+4:idx+4+qlen]
        entries.append((i, idx, qlen, name))
        idx += 4 + qlen
    # bytes consumed vs section size
    print(f'  parsed {len(entries)} entries; bytes consumed = {idx}; section size = {s["size"]}; '
          f'trailing = {s["size"] - idx}')
    # trailing bytes after the last entry (terminator?)
    if idx < len(buf):
        tail = buf[idx:idx+64]
        print(f'  TRAILING BYTES after parse ({len(buf)-idx} total): {tail.hex()}')
    return buf, s, count, entries


def find_hits(entries, needles):
    hits = {}
    for (i, off, qlen, name) in entries:
        low = name.decode('ascii', 'replace').lower()
        for nd in needles:
            if nd in low:
                hits.setdefault(nd, []).append((i, off, qlen, name.decode('ascii','replace')))
    return hits


def main():
    ae = load_map(SVAERA)
    sv = load_map(SV)
    mg = load_map(MERGED)

    ae_buf, ae_s, ae_ct, ae_e = dump_quests('SVAERA original', ae)
    sv_buf, sv_s, sv_ct, sv_e = dump_quests('SV upstream 0.98i', sv)
    mg_buf, mg_s, mg_ct, mg_e = dump_quests('MERGED output', mg)

    print('\n\n########## FOUR-QUEST LOCATIONS ##########')
    for lbl, entries in [('SVAERA', ae_e), ('SV', sv_e), ('MERGED', mg_e)]:
        print(f'\n--- {lbl} ---')
        h = find_hits(entries, FOUR)
        for nd in FOUR:
            for (i, off, qlen, nm) in h.get(nd, []):
                print(f'  [{nd:24s}] index={i:4d} off={off:6d} len={qlen:3d} name={nm!r}')
            if nd not in h:
                print(f'  [{nd:24s}] ABSENT')

    # Byte-parity: is the first min(ae_ct) region of MERGED identical to SVAERA?
    print('\n\n########## SVAERA-prefix byte-parity in MERGED ##########')
    # Compare the entry region (after the u32 count) up to SVAERA's consumed bytes.
    ae_body_end = 4
    for (i, off, qlen, name) in ae_e:
        ae_body_end = off + 4 + qlen
    ae_body = ae_buf[4:ae_body_end]
    mg_body_sameregion = mg_buf[4:4+len(ae_body)]
    if ae_body == mg_body_sameregion:
        print(f'  MERGED[4:{4+len(ae_body)}] == SVAERA entry region ({len(ae_body)} bytes) -> IDENTICAL prefix')
    else:
        # find first diff
        d = next((k for k in range(min(len(ae_body), len(mg_body_sameregion)))
                  if ae_body[k] != mg_body_sameregion[k]), None)
        print(f'  PREFIX DIFFERS at body offset {d}')

    # Field-by-field grammar check on MERGED: every entry len sane, name ascii-printable
    print('\n\n########## MERGED grammar audit (every entry) ##########')
    weird = 0
    for (i, off, qlen, name) in mg_e:
        ok_ascii = all(32 <= b < 127 for b in name)
        if qlen == 0 or qlen > 200 or not ok_ascii:
            weird += 1
            print(f'  WEIRD entry {i}: off={off} len={qlen} ascii_ok={ok_ascii} name={name[:40]!r}')
    print(f'  weird entries: {weird} / {len(mg_e)}')
    print(f'  MERGED declared count={mg_ct}, parsed={len(mg_e)}  (match={mg_ct==len(mg_e)})')

    # Cross-check: number of quest entries in each
    print('\n\n########## COUNTS ##########')
    print(f'  SVAERA count={ae_ct}, SV count={sv_ct}, MERGED count={mg_ct}')
    print(f'  MERGED - SVAERA = {mg_ct - ae_ct} appended')

    # Also parse LEVELS count for context
    for lbl, data in [('SVAERA', ae), ('SV', sv), ('MERGED', mg)]:
        secs = {s['type']: s for s in parse_sections(data)}
        lv = parse_level_index(data, secs[SEC_LEVELS])
        print(f'  {lbl} LEVELS count = {len(lv)}')


if __name__ == '__main__':
    main()
