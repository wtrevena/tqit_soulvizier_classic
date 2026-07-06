"""Static scan: every declared cave-mouth/door record in (a) the DEPLOYED merged map
and (b) the SV upstream map, for the blood-cave cluster + hiddenvalley01.

Record shapes (docs/CAVE_ENTRY_CHAIN_TRACE.md):
  0x14 mouth payload (60B): [12B hdr][mouth GUID][exit GUID][dest LEVEL GUID @44]
  0x06 reciprocal trailer:  [exit GUID][mouth GUID][source LEVEL GUID] near blob tail
Generic approach: scan every 0x14 payload and each 0x06 section for ANY 16-byte
window equal to a known LEVEL GUID -> report (level, section, offset, ref level).
"""
import sys, struct
from pathlib import Path
REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / 'tools'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections

DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc")
UP  = REPO / 'upstream/soulvizier_098i/Resources/Levels.arc'

def load(path):
    arc = ArcArchive.from_file(path)
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec[SEC_LEVELS])
    g2n = {}
    for lv in levels:
        base = lv['fname'].replace('\\','/').lower().split('/')[-1].replace('.lvl','')
        g2n[bytes(lv['ints_raw'][36:52])] = base
    return data, levels, g2n

def interesting(fn):
    base = fn.split('/')[-1]
    return ('randomice03' in base or base == 'valley01b.lvl')

def scan(tag, path):
    print(f"\n######## {tag}: {path.name} ########")
    data, levels, g2n = load(path)
    guids = list(g2n.keys())
    for lv in levels:
        fn = lv['fname'].replace('\\','/').lower()
        if not interesting(fn): continue
        base = fn.split('/')[-1].replace('.lvl','')
        blob = data[lv['data_offset']:lv['data_offset']+lv['data_length']]
        try: secs, _ = parse_blob_sections(blob)
        except Exception as e:
            print(f"  {base}: blob parse fail: {e}"); continue
        hits = []
        for s in secs:
            if s['type'] not in (0x14, 0x06): continue
            sd = s['data']
            for g in guids:
                start = 0
                while True:
                    i = sd.find(g, start)
                    if i < 0: break
                    ref = g2n[g]
                    if ref != base:   # skip self-references
                        hits.append((s['type'], i, ref))
                    start = i + 1
        own_g = None
        for g, n in g2n.items():
            if n == base: own_g = g
        print(f"  {base}  (guid {own_g.hex()[:8] if own_g else '??'}...)")
        if not hits:
            print(f"      no cross-level GUID refs in 0x14/0x06")
        for t, off, ref in sorted(hits):
            print(f"      0x{t:02x} @{off:6d} -> {ref}")

scan("DEPLOYED (AE base levels incl. ice cave)", DEP)
