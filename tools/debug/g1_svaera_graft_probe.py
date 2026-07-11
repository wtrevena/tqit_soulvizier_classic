"""G1 SVAERA mastery-graft probe (LANE B, read-only).

Dumps the ground-truth bytes for every G1 graft source in the REAL SVAERA arz
plus the target skill-tree slot occupancy in OUR built arz, so the graft code in
build_svc_database.py can be anchored on verified field values rather than the
proposal doc's prose. No repo record is modified.

Usage:
  py tools/debug/g1_svaera_graft_probe.py [our_arz] [svaera_arz] [base_arz]
Defaults resolve the standard install paths.
"""
import os
import sys
import re
from pathlib import Path
from collections import OrderedDict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

OUR = sys.argv[1] if len(sys.argv) > 1 else \
    r"work/SoulvizierClassic/Database/SoulvizierClassic.arz"
SVAERA = sys.argv[2] if len(sys.argv) > 2 else \
    r"C:/Program Files (x86)/Steam/steamapps/workshop/content/475150/2076433374/SVAERA_customquest/Database/SVAERA_customquest.arz"
BASE = sys.argv[3] if len(sys.argv) > 3 else \
    r"C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz"


def norm(s):
    return s.replace('/', '\\').lower().strip()


def load(p):
    print(f"loading {p} ...", flush=True)
    return ArzDatabase.from_arz(Path(p))


def fmap(db):
    return {norm(n): n for n in db.record_names()}


HUNT = [
    'clubslam', 'ancestralmod', 'activeblock', 'summonphalanx', 'phalanx',
    'firenova', 'rupture', 'lightningdash', 'frostnova', 'earthbind',
    'rootwave', 'summoncopy', 'dreamcopy', 'doppelganger', 'runegolem',
]

SKILL_FIELDS = [
    'templateName', 'Class', 'skillMaxLevel', 'skillUltimateLevel',
    'skillDisplayName', 'skillBaseDescription', 'skillTier',
    'skillSpecialAnimationName', 'skillMasteryLevelRequired',
    'skillConnectionSpacing', 'buffSkillName', 'petSkillName',
    'spawnObjects', 'spawnObjectsTimeToLive', 'petLimit', 'skillActiveDuration',
    'skillCooldownTime', 'skillManaCost', 'skillProjectileNumber',
]


def dump_record(db, name, title=None):
    fields = db.get_fields(name)
    print(f"\n--- {title or name}")
    print(f"    key={name}")
    if not fields:
        print("    (no fields)")
        return
    fm = {k.split('###')[0]: tf for k, tf in fields.items()}
    for f in SKILL_FIELDS:
        if f in fm and fm[f].values:
            v = fm[f].values
            print(f"    {f} = {v if len(v) > 1 else v[0]}")
    refs = []
    for k, tf in fields.items():
        base = k.split('###')[0]
        for v in tf.values:
            if isinstance(v, str) and v.strip().lower().endswith('.dbr'):
                refs.append((base, v.strip()))
    if refs:
        print("    DBR REFS:")
        for base, v in refs:
            print(f"       {base} -> {v}")


def main():
    svaera = load(SVAERA)
    sv_map = fmap(svaera)
    print(f"\nSVAERA records: {len(sv_map)}")

    print("\n" + "=" * 72)
    print("HUNT: SVAERA record names containing graft-source substrings")
    print("=" * 72)
    for h in HUNT:
        allhits = sorted(n for k, n in sv_map.items() if h in k)
        print(f"\n[{h}] {len(allhits)} total match(es):")
        for n in allhits[:40]:
            print(f"    {n}")

    print("\n" + "=" * 72)
    print("DETAIL DUMP of doc-named graft sources (whatever resolves)")
    print("=" * 72)
    CANDIDATES = [
        r'records\skills\warfare\drx_clubslam.dbr',
        r'records\skills\warfare\drx_clubslam_fissure.dbr',
        r'records\skills\warfare\drx_ancestralmod.dbr',
        r'records\skills\defensive\drx_activeblock.dbr',
        r'records\skills\defensive\drx_summonphalanx.dbr',
        r'records\skills\earth\drx_firenova.dbr',
        r'records\skills\earth\drxrupture.dbr',
        r'records\skills\earth\drxrupture_burning.dbr',
        r'records\skills\earth\drxrupture_flare.dbr',
        r'records\skills\storm\drx_lightningdash.dbr',
        r'records\skills\storm\drxfrostnova.dbr',
        r'records\skills\nature\drx_earthbind.dbr',
        r'records\skills\nature\drx_nymph_petmodifier_rootwave.dbr',
        r'records\skills\nature\drx_nymph_petskill_rootwave.dbr',
        r'records\xpack\skills\dream\drx_summoncopy.dbr',
    ]
    for c in CANDIDATES:
        n = sv_map.get(norm(c))
        if n:
            dump_record(svaera, n, title=f"SVAERA {c}")
        else:
            print(f"\n--- SVAERA {c}: NOT FOUND at that exact path")

    print("\n" + "=" * 72)
    print("OUR skill-tree slot occupancy (skillNameN)")
    print("=" * 72)
    our = load(OUR)
    our_map = fmap(our)
    TREES = [
        r'records\skills\warfare\drxwarfareskilltree.dbr',
        r'records\skills\defensive\drxdefensiveskilltree.dbr',
        r'records\skills\earth\drxearthskilltree.dbr',
        r'records\skills\storm\drxstormskilltree.dbr',
        r'records\skills\nature\drxnatureskilltree.dbr',
        r'records\xpack2\skills\runemaster\runemaster_skilltree.dbr',
    ]
    for k, n in sorted(our_map.items()):
        if k.endswith('skilltree.dbr') and ('dream' in k or 'defensive' in k
                                            or 'defense' in k):
            if n not in [our_map.get(norm(t)) for t in TREES]:
                TREES.append(n)
    for t in TREES:
        n = our_map.get(norm(t))
        if not n:
            print(f"\n[TREE MISSING] {t}")
            continue
        fields = our.get_fields(n)
        fm = {k.split('###')[0]: tf for k, tf in fields.items()}
        slots = []
        maxslot = 0
        for i in range(1, 60):
            sk = fm.get(f'skillName{i}')
            val = sk.values[0] if (sk and sk.values) else ''
            if val:
                maxslot = i
                slots.append((i, val))
        print(f"\n[TREE] {n}  (highest occupied skillName = {maxslot})")
        for i, v in slots:
            print(f"    skillName{i} = {v}")

    print("\n" + "=" * 72)
    print("OUR UI slot occupancy (records\\ingameui\\player skills\\mastery N)")
    print("=" * 72)
    for mi in range(1, 13):
        base = r'records\ingameui\player skills\mastery %d' % mi
        present = []
        for si in range(1, 40):
            slot = norm('%s\\skill%02d.dbr' % (base, si))
            if slot in our_map:
                present.append(si)
        xbase = r'records\xpack\ui\skills\mastery %d' % mi
        xpresent = []
        for si in range(1, 40):
            slot = norm('%s\\skill%02d.dbr' % (xbase, si))
            if slot in our_map:
                xpresent.append(si)
        if present or xpresent:
            print(f"  mastery {mi}: ingameui slots {present}  | xpack slots {xpresent}")

    print("\n" + "=" * 72)
    print("Closure resolvability spot-check (base+our vs svaera refs)")
    print("=" * 72)
    base = load(BASE)
    base_names = set(fmap(base).keys())
    our_names = set(our_map.keys())
    resolved_here = base_names | our_names
    for c in CANDIDATES:
        n = sv_map.get(norm(c))
        if not n:
            continue
        fields = svaera.get_fields(n)
        refs = set()
        for k, tf in fields.items():
            for v in tf.values:
                if isinstance(v, str) and v.strip().lower().endswith('.dbr'):
                    refs.add(norm(v))
        missing = sorted(r for r in refs if r not in resolved_here)
        only_svaera = sorted(r for r in missing if r in sv_map)
        truly_missing = sorted(r for r in missing if r not in sv_map)
        print(f"\n{c}: {len(refs)} refs; {len(missing)} not in base+our")
        if only_svaera:
            print(f"   need-port-from-SVAERA ({len(only_svaera)}):")
            for r in only_svaera:
                print(f"      {r}")
        if truly_missing:
            print(f"   DANGLING even in SVAERA ({len(truly_missing)}):")
            for r in truly_missing:
                print(f"      {r}")


if __name__ == '__main__':
    main()
