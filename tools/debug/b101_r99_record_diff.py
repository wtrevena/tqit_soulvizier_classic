#!/usr/bin/env python3
r"""b101 (R-99) record-diff: every delta must be ATTRIBUTABLE to the R-99 roster.

Usage:
  py tools/debug/b101_r99_record_diff.py <baseline.arz> <built.arz>

Baseline = a build of `main` in THIS environment (the pre-R-99 arz). The measured
tip baseline is **aea688b23acefe1b48ae31a0df4cc423**, 55,475,172 B, 51,124 records,
a fully gated exit-0 build of `main` @ `b376b61`. Built = a build of
`feat/toxeus-apex-roster`, **6a3a491db546b603c52132237c40aa63**, 55,475,226 B.

⚠️ An earlier revision of this docstring cited `967b1f97137bf6479c18c08e9dd6ffc4`
as the baseline. That artifact is a 44-MODULE PRE-merge build (its log reads
"[37/44] uber_apex_orb" and never reaches `weapon_gate_truth`), which the BACKLOG
gate record explicitly disowns as a baseline of the tip. Do not diff against it.

WHY THE EXPECTED DIFF IS SO SMALL, and why that is the point. The whole
`genericbossorb_05` chain (proxy + 3 pools + 3 chests + 3 loot tables) and
Leinth's in-place chest re-tier ALREADY exist on `main` - they shipped with b94
(R-72/R-75). R-99 changes only WHO sits on that tier. So the ONLY legitimate
delta in the entire 51,124-record database is `treasureProxyName` on the Toxeus
roster records that were not already on orb05:

    um_toxeus_hunt_99      field ABSENT      -> genericbossorb_05
    um_toxeus_hunt_l_99    field ABSENT      -> genericbossorb_05  (clone-inherited)
    um_toxeus_99           field ABSENT      -> genericbossorb_05
    z_toxeus               field ABSENT      -> genericbossorb_05
    old_z_toxeus           field ABSENT      -> genericbossorb_05
    um_toxeus_21           genericbossorb_01 -> genericbossorb_05

`um_toxeus_enslaver_99` and `um_bloodtoxeus_99` were already on orb05 (b94), so
they must show ZERO delta - if they move, something re-pointed them.

ATTRIBUTION IS DELIBERATELY STRICT, in both directions:
  * the record must be in the DERIVED Toxeus roster (derived live from the built
    db by `uber_apex_orb.toxeus_roster`, never a list typed into this file);
  * the ONLY field allowed to differ on it is `treasureProxyName`, and the new
    value must be `genericbossorb_05`;
  * ANY other changed record, ANY added record and ANY removed record is
    UNATTRIBUTED and fails.
A REMOVED record is always a failure: b98's 15 new records and b99's
`summon_sargoth` + pets must survive this lane untouched.

Exit 0 = every delta attributed. Exit 1 = at least one unattributed delta.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'patches'))

from arz_patcher import ArzDatabase  # noqa: E402


def norm(s):
    return str(s).lower().replace('/', '\\')


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    base = ArzDatabase.from_arz(Path(argv[0]))
    built = ArzDatabase.from_arz(Path(argv[1]))

    from patches import uber_apex_orb as M  # noqa: E402
    roster = {norm(r) for r in M.toxeus_roster(built)}
    orb05 = norm(M.ORB05)

    bmap = {norm(n): n for n in base.record_names()}
    tmap = {norm(n): n for n in built.record_names()}
    bnames, tnames = set(bmap), set(tmap)
    added = sorted(tnames - bnames)
    removed = sorted(bnames - tnames)

    def val(f, k):
        return (f[k].dtype, list(f[k].values)) if k in f else None

    changed = {}
    for n in sorted(bnames & tnames):
        fb = base.get_fields(bmap[n]) or {}
        ft = built.get_fields(tmap[n]) or {}
        d = {}
        for k in sorted(set(fb) | set(ft)):
            vb, vt = val(fb, k), val(ft, k)
            if vb != vt:
                d[k] = (vb, vt)
        if d:
            changed[n] = d

    print('=' * 78)
    print('b101 R-99 RECORD DIFF (all-Toxeus apex orb)')
    print('  baseline : %s' % argv[0])
    print('  built    : %s' % argv[1])
    print('  records  : baseline %d -> built %d' % (len(bnames), len(tnames)))
    print('  DERIVED Toxeus roster in the built db: %d record(s)' % len(roster))
    print('  ADDED %d / REMOVED %d / CHANGED %d'
          % (len(added), len(removed), len(changed)))
    print('=' * 78)

    attributed, unattributed = [], []

    for n in added:
        unattributed.append(('ADDED', n, set(),
                             'R-99 authors NO new records - the orb05 chain '
                             'already shipped with b94'))
    for n in removed:
        unattributed.append(('REMOVED', n, set(),
                             'R-99 removes NOTHING - b98/b99 records must survive'))

    for n, d in sorted(changed.items()):
        fields = set(d)
        if n not in roster:
            unattributed.append(('CHANGED', n, fields,
                                 'not in the DERIVED Toxeus roster'))
            continue
        extra = fields - {'treasureProxyName'}
        if extra:
            unattributed.append(('CHANGED', n, extra,
                                 'only treasureProxyName may move on a roster record'))
            continue
        _vb, vt = d['treasureProxyName']
        newval = norm(vt[1][0]) if vt and vt[1] else None
        if newval != orb05:
            unattributed.append(('CHANGED', n, fields,
                                 'treasureProxyName landed on %r, not genericbossorb_05'
                                 % newval))
            continue
        attributed.append((n, d['treasureProxyName']))

    print('\n--- ATTRIBUTED TO R-99 (roster treasureProxyName) : %d record(s) ---'
          % len(attributed))
    for n, (vb, vt) in attributed:
        before = 'FIELD ABSENT' if vb is None else vb[1][0]
        print('  %-62s %-24s -> %s'
              % (n, str(before).rsplit('\\', 1)[-1], str(vt[1][0]).rsplit('\\', 1)[-1]))

    unchanged_roster = sorted(r for r in roster if r not in {n for n, _ in attributed})
    print('\n--- ROSTER RECORDS WITH ZERO DELTA (already on orb05 before R-99) : %d ---'
          % len(unchanged_roster))
    for r in unchanged_roster:
        cur = built.get_field_value(tmap[r], 'treasureProxyName')
        cur = cur[0] if isinstance(cur, list) and cur else cur
        print('  %-62s %s' % (r, str(cur).rsplit('\\', 1)[-1]))

    print('\n' + '=' * 78)
    if unattributed:
        print('UNATTRIBUTED DELTAS: %d  ** NO-GO **' % len(unattributed))
        for kind, n, bad, why in unattributed:
            print('   %-8s %s  %s  (%s)'
                  % (kind, n, ('fields=' + ','.join(sorted(bad))) if bad else '', why))
        return 1
    print('RESULT: PASS - 0 ADDED, 0 REMOVED, %d CHANGED and every one of them is a '
          'DERIVED Toxeus roster record whose ONLY moved field is treasureProxyName '
          '-> genericbossorb_05. Zero unattributed changes.' % len(changed))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
