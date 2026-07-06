"""Fast cross-check: what are GROUPS (0x11)? Do they register level adjacency/zones,
and do overworld levels appear while cluster levels don't? Categories tell us if this
is even the right structure (spawn groups vs region/zone groups)."""
import sys, struct
from pathlib import Path
REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / 'tools'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS, SEC_GROUPS
from svaera_plus_portals import _parse_groups

DEP = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc")
arc = ArcArchive.from_file(DEP)
data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
sec = {s['type']: s for s in parse_sections(data)}

# level GUID -> name and name -> GUID
levels = parse_level_index(data, sec[SEC_LEVELS])
guid2name = {}
name2guid = {}
for lv in levels:
    base = lv['fname'].replace('\\','/').lower().split('/')[-1].replace('.lvl','')
    g = bytes(lv['ints_raw'][36:52])
    guid2name[g] = base
    name2guid[base] = g

g_raw = data[sec[SEC_GROUPS]['data_offset']:sec[SEC_GROUPS]['data_offset']+sec[SEC_GROUPS]['size']]
val0, recs = _parse_groups(g_raw)
print(f"GROUPS: val0={val0}  {len(recs)} records")

# category histogram
from collections import Counter
cats = Counter(r['category'] for r in recs)
print("categories:", dict(cats))

# does any group's raw_data embed level GUIDs? scan each record's raw_data for 16-byte
# windows matching a known level GUID.
INTEREST = {'hiddenvalley01','valley01','valley01b','valleydescent01','random09a',
            'xpassagetransitionstart','bc_initialpathway','drxfirstroom'}
found_levels_in_groups = set()
for r in recs:
    rd = r['raw_data']
    hits = []
    for off in range(0, max(0, len(rd)-16)):
        g = rd[off:off+16]
        if g in guid2name:
            hits.append(guid2name[g]); found_levels_in_groups.add(guid2name[g])
    if any(h in INTEREST for h in hits):
        print(f"  group '{r['name'][:40]}' cat='{r['category']}' members={r['member_count']} "
              f"len={len(rd)} -> INTEREST levels: {sorted(set(h for h in hits if h in INTEREST))}")

print(f"\nAny GUID-embedding group at all? {len(found_levels_in_groups)} distinct levels found in group raw_data")
print("Interest levels present in GROUPS:", {n: (n in found_levels_in_groups) for n in sorted(INTEREST)})
# also show first few group names for flavor
print("\nfirst 12 group names/categories:")
for r in recs[:12]:
    print(f"  '{r['name'][:44]}'  cat='{r['category']}'  members={r['member_count']}  datalen={len(r['raw_data'])}")
