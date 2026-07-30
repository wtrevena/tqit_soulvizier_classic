#!/usr/bin/env python3
"""b100 PLAYER-SURFACE CHECKLIST (CLAUDE.md law #3).

The lane creates no record, so every player-visible surface it exposes belongs to
content that already ships. This enumerates EXACTLY what the 14 new encounters can
put on screen and proves each creature (a) resolves in the arz, (b) has a name tag
that resolves in Text.arc, and (c) ALREADY spawns somewhere else in this same cave -
so nothing new, unseen or untested appears.

⚠️ RUN IT AGAINST THE **BASELINE** MAP. Round 1 ran it against the POST-change map,
where this lane's own roster is in drxBC3 by construction, so check (c) could not
fail - the proof as run was circular. It is not circular against the baseline, and
the substantive conclusion survived the honest test (0 problems, 21 of 39 creature
records already reachable from a proxy placed in drxBC3 itself before this lane
touched anything). The module now REFUSES a map that already carries the placements,
rather than quietly re-running the circular version.

Usage:
  py tools/debug/b100_player_surfaces.py <arz> <Text.arc> <BASELINE Levels.arc>
  py tools/debug/b100_player_surfaces.py <arz> <Text.arc> <map> --allow-postchange
"""
import sys
from pathlib import Path
from collections import Counter, defaultdict
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / 'tools')); sys.path.insert(0, str(REPO / 'tools' / 'contracts'))
import contracts_map as CM
from arc_patcher import ArcArchive

ARZ = sys.argv[1]
TEXT = sys.argv[2]
MAP = sys.argv[3]
ALLOW_POST = '--allow-postchange' in sys.argv[4:]

arz = CM.Arz.from_arz(ARZ)
names = {CM.norm_rec(x): x for x in arz.record_names()}
cls = {CM.norm_rec(k): v for k, v in arz.record_class().items()}

def f(rec, key):
    n = CM.norm_rec(rec)
    if n not in names:
        return None
    v = arz.field(names[n], key)
    return v[0] if isinstance(v, list) and v else (None if isinstance(v, list) else v)

# --- text tags (use the repo's OWN reader, not a hand-rolled one) ---
sys.path.insert(0, str(REPO / 'tools'))
import validate_tags as VT
tags = VT.collect_text_arc_tags(Path(TEXT)) or set()
print('Text.arc tags loaded: %d' % len(tags))

ROSTER = ['bw_acolyte_lone', 'zparty_witchfest_2099', 'bw_acolyte_clutch',
          'bw_priest_houndmaster', 'bw_priest_lone', 'hound_01_pack',
          'abom_dancer_spear_mix', 'abom_ravager_lone', 'q_shaman_lone']
P = 'records\\drxmap\\proxy\\'

def pool_slots(pool):
    """Every nameN / nameChampionN a pool actually declares. NOT range(1,9):
    zparty_witchfest_2099's pool carries a name9 (c_bloodhound_44), so a fixed 1..8
    loop silently omits creature records from this very checklist."""
    n = CM.norm_rec(pool or '')
    if n not in names:
        return []
    flds = arz.get_fields(names[n]) or {}
    out = []
    for k in flds:
        for pre in ('nameChampion', 'name'):
            if k.startswith(pre) and k[len(pre):].isdigit():
                out.append(k)
                break
    return sorted(set(out))


creatures = {}
for w in ROSTER:
    pool = f(P + w + '.dbr', 'pool1')
    for slot in pool_slots(pool):
        c = f(pool, slot)
        if c:
            creatures.setdefault(CM.norm_rec(c), c)
print('distinct creature records the 14 new encounters can spawn: %d\n' % len(creatures))

# --- where each creature already spawns in the shipped map ---
arcm = CM.Arc.from_file(MAP)
mp = arcm.world_map(); secs = CM.parse_top_sections(mp)
levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
# build proxy -> levels placed
proxy_levels = defaultdict(set)
n_drxbc3 = 0
for lv in levels:
    blob = mp[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    try:
        items = CM.parse_0x05(blob)[1]
    except Exception:
        continue
    base = lv['fname'].replace('\\', '/').split('/')[-1].replace('.lvl', '')
    if base.lower() == 'drxbc3':
        n_drxbc3 = len(items)
    for it in items:
        d = CM.norm_rec(it['dbr'].decode('latin-1'))
        if cls.get(d) == 'Proxy':
            proxy_levels[d].add(base)

# CIRCULARITY GUARD - see the module docstring.
if n_drxbc3 != 281 and not ALLOW_POST:
    print('\nREFUSING TO RUN: drxBC3 in %s carries %d instances, not the shipped 281, so\n'
          'this map already contains this lane\'s placements and check (c) "already spawns\n'
          'elsewhere in this cave" would be satisfied BY OUR OWN INJECTION - a circular\n'
          'proof. Pass a baseline map, or --allow-postchange if you want the circular run\n'
          'anyway (and then do not cite it as evidence).' % (MAP, n_drxbc3))
    sys.exit(2)
print('map is %s (drxBC3 has %d instances)\n'
      % ('a BASELINE - the non-circular test' if n_drxbc3 == 281
         else 'POST-CHANGE - CIRCULAR, forced with --allow-postchange', n_drxbc3))

# creature -> levels via any proxy pool that contains it
creature_levels = defaultdict(set)
for pd, lvs in proxy_levels.items():
    pool = f(pd, 'pool1')
    if not pool:
        continue
    for slot in pool_slots(pool):
        c = f(pool, slot)
        if c:
            creature_levels[CM.norm_rec(c)] |= lvs

bad = 0
print('%-42s %-8s %-22s %-6s %s' % ('creature', 'class', 'name tag', 'tagOK', 'already spawns in'))
for n, orig in sorted(creatures.items()):
    k = cls.get(n)
    tag = f(orig, 'description')
    tl = {t.lower().strip() for t in tags}
    tok = (str(tag).strip().lower() in tl) if tag else False
    lvs = sorted(creature_levels.get(n, set()))
    bc = [x for x in lvs if x.lower().startswith(('drx', 'bc_', 'yet_', 'new_secret', 'xpassage', 'ocean', 'bossfight'))]
    ok = (n in names) and tok and bool(bc)
    if not ok:
        bad += 1
    print('%-42s %-8s %-22s %-6s %s'
          % (orig.split('\\')[-1], k, tag, 'YES' if tok else 'NO',
             ('%d blood-cave level(s): %s' % (len(bc), ', '.join(bc[:4]))) if bc else 'NOWHERE ELSE'))
print('\nPLAYER-SURFACE CHECKLIST: %s (%d problem record(s))'
      % ('PASS' if bad == 0 else 'FAIL', bad))
