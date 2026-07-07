#!/usr/bin/env python3
"""Scan the DEPLOYED merged map for the SV shrine UniqueId feeb4bc6... in every level's
0x05 flagged records, to ensure re-injecting it at HV01 creates no UniqueId collision
(the value must be unique across the whole map; the Shrine_Respawn_Orient group binds
to it). Also confirm it's currently ABSENT from any 0x05 in the merged build (build18
injected the shrine with a ZERO uid, so the real uid should appear 0 times). Read-only."""
import sys, struct
from pathlib import Path
REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / 'tools'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections

MAPS = {
    "DEPLOYED_build18": Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc"),
    "SV_098i": REPO / 'upstream/soulvizier_098i/Resources/Levels.arc',
}
UID = bytes.fromhex('feeb4bc6ce4e08c0e279b3824244aeeb')


def load(p):
    arc = ArcArchive.from_file(p)
    return arc.decompress([e for e in arc.entries if e.entry_type == 3][0])


def scan(mapd, label):
    sec = {s['type']: s for s in parse_sections(mapd)}
    levels = parse_level_index(mapd, sec[SEC_LEVELS])
    hits = []
    for i, lv in enumerate(levels):
        blob = mapd[lv['data_offset']:lv['data_offset']+lv['data_length']]
        secs, _ = parse_blob_sections(blob)
        s05 = next((s['data'] for s in secs if s['type']==0x05), None)
        if not s05:
            continue
        # walk instances (handle v0e/v11)
        scount = struct.unpack_from('<I', s05, 0)[0]; pos = 4
        strings = []
        for _ in range(scount):
            slen = struct.unpack_from('<I', s05, pos)[0]; pos += 4
            strings.append(s05[pos:pos+slen]); pos += slen
        icount = struct.unpack_from('<I', s05, pos)[0]; pos += 4
        base = 72 if blob[3] == 0x11 else 56
        p = pos
        for _ in range(icount):
            if p + base > len(s05):
                break
            flags = struct.unpack_from('<I', s05, p+52)[0]
            rlen = base + (16 if flags else 0)
            if flags:
                # The UniqueId always lives at +56..+72 (immediately after the 56-byte core),
                # for BOTH v0e (rlen=72) and v0x11 (rlen=88). In v0x11 the 16-byte zero pad
                # follows the UniqueId at +72..+88 - so reading [+base:+rlen] would read the
                # zero pad on v0x11 (base=72) and MISS a real collision. Always read [+56:+72].
                uid = s05[p+56:p+72]
                if uid == UID:
                    si = struct.unpack_from('<I', s05, p)[0]
                    rec = strings[si].decode('ascii','replace') if si < len(strings) else '?'
                    name = lv['fname'].replace('\\','/').lower().split('/')[-1].replace('.lvl','')
                    hits.append((name, rec))
            p += rlen
    print(f"{label}: UniqueId {UID.hex()} found in {len(hits)} flagged 0x05 record(s): {hits}")


def main():
    for label, p in MAPS.items():
        if not p.exists():
            print(f"{label}: MISSING"); continue
        scan(load(p), label)


if __name__ == '__main__':
    main()
