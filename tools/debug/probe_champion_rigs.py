r"""probe_champion_rigs - R-102: the full animation surface of the Toxeus champions.

R-102's fourth amendment names ANIMATION, not colour, as the real risk in a mesh
swap: "every skill that names an anim must still resolve or the champion T-poses
or goes uncastable."

This probe enumerates, for each named record, EVERY animation surface that a
mesh swap could break:
  1. `mesh` / `baseTexture` / `charAnimationTableName`
  2. every per-record `*Anim*` field (the inline overrides, which SHADOW the table)
  3. every `.anm` the bound animation TABLE names
  4. every skill in the record's `skillName*` slots that names a
     `skillSpecialAnimationName`, and the `*SpecialAnimRef*` row that must
     provide it (the Ephialtes castability law)
and then resolves every `.anm` against the arcs.

Usage:
  py tools/debug/probe_champion_rigs.py <built .arz>
"""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase  # noqa: E402
from debug.probe_rig_bones import read_asset  # noqa: E402

TARGETS = [
    r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr',
    r'records\skills\soulskills\pets\toxeus_enslaver_1.dbr',
    r'records\skills\soulskills\pets\toxeus_enslaver_2.dbr',
    r'records\skills\soulskills\pets\toxeus_enslaver_3.dbr',
    r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr',
    r'records\skills\soulskills\pets\bloodtoxeus_1.dbr',
    r'records\skills\soulskills\pets\bloodtoxeus_2.dbr',
    r'records\skills\soulskills\pets\bloodtoxeus_3.dbr',
    r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr',
    r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr',
]


def g1(db, n, f):
    v = db.get_field_value(n, f)
    return v[0] if isinstance(v, list) and v else v


def anim_fields(db, rec):
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        b = k.split('###')[0]
        vals = [str(v) for v in (tf.values or []) if str(v).strip()]
        if not vals:
            continue
        if any(v.lower().endswith('.anm') for v in vals):
            out[b] = vals
    return out


def special_refs(db, rec):
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        b = k.split('###')[0]
        if 'SpecialAnimRef' not in b:
            continue
        vals = [str(v) for v in (tf.values or []) if str(v).strip()]
        if vals:
            out[b] = vals
    return out


def skill_slots(db, rec):
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        b = k.split('###')[0]
        if b.startswith('skillName') and b[9:].isdigit() and tf.values \
                and str(tf.values[0]).strip():
            out[int(b[9:])] = str(tf.values[0])
    return out


def main():
    arz = Path(sys.argv[1])
    db = ArzDatabase.from_arz(arz)
    names = {n.lower(): n for n in db.record_names()}
    allanm = collections.Counter()

    for t in TARGETS:
        real = names.get(t.lower())
        print('=' * 92)
        if not real:
            print('MISSING RECORD: %s' % t)
            continue
        print(real)
        print('   mesh        : %s' % g1(db, real, 'mesh'))
        print('   baseTexture : %s' % g1(db, real, 'baseTexture'))
        tab = g1(db, real, 'charAnimationTableName')
        print('   anim table  : %s' % tab)
        print('   scale       : %s' % g1(db, real, 'scale'))
        inline = anim_fields(db, real)
        print('   inline .anm overrides: %d' % len(inline))
        for b in sorted(inline):
            print('        %-28s %s' % (b, inline[b]))
            for v in inline[b]:
                allanm[v.lower()] += 1
        sr = special_refs(db, real)
        if sr:
            print('   SpecialAnimRef rows:')
            for b in sorted(sr):
                print('        %-28s %s' % (b, sr[b]))
        if tab:
            treal = names.get(str(tab).lower())
            if not treal:
                print('   !! anim table record NOT FOUND: %s' % tab)
            else:
                tf = anim_fields(db, treal)
                tsr = special_refs(db, treal)
                print('   table .anm fields: %d   table SpecialAnimRef rows: %d'
                      % (len(tf), len(tsr)))
                for b in sorted(tf):
                    for v in tf[b]:
                        allanm[v.lower()] += 1
                for b in sorted(tsr):
                    print('        TABLE %-24s %s' % (b, tsr[b]))
        # skills that demand a named special animation
        need = []
        for slot, sk in sorted(skill_slots(db, real).items()):
            skr = names.get(sk.lower())
            if not skr:
                need.append((slot, sk, 'SKILL RECORD MISSING', None))
                continue
            sa = g1(db, skr, 'skillSpecialAnimationName')
            if sa and str(sa).strip():
                need.append((slot, sk, str(sa), None))
        if need:
            print('   skills naming a special animation:')
            for slot, sk, sa, _ in need:
                print('        slot %-3d %-70s -> %s' % (slot, sk.rsplit('\\', 1)[-1], sa))

    print()
    print('=' * 92)
    print('DISTINCT .anm REFERENCED BY THE CHAMPION SURFACES: %d' % len(allanm))
    bad = 0
    for a in sorted(allanm):
        data, arcp = read_asset(a)
        ok = data is not None and len(data) > 0
        if not ok:
            bad += 1
        print('  %-4s %-76s x%d' % ('OK' if ok else 'MISS', a, allanm[a]))
    print('UNRESOLVED .anm: %d' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
