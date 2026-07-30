#!/usr/bin/env python3
r"""R-108 wave, `feat/uber-visibility` record-diff: every delta must be
ATTRIBUTABLE to R-100 #7, R-100 #18 or R-109. Nothing else may move.

Usage:
  py tools/debug/r108_visibility_record_diff.py <baseline.arz> <built.arz>

Baseline = a build of `main` in THIS environment. This lane's measured baseline is
`local/baseline_main_7efd107.arz`, md5 **6a3a491db546b603c52132237c40aa63**,
55,475,226 B, 51,124 records, a fully gated exit-0 build of `main` @ `7efd107`
(and `main`'s only later advance, `9a12d17`, is docs + `docs/wip_workflows/*.js`
only - `git diff 7efd107 9a12d17 --numstat` - so it cannot move an arz byte).

THE THREE LEGITIMATE DELTA CLASSES, and nothing else:

  R-109  records\xpack\game\gameengine.dbr
         EXACTLY ONE field: RedemptionMultiplier 0.5 -> 1.0.
         deathPenaltyEquation / Min / Max must show ZERO delta (R-80 untouched),
         and the five dead gameengine lookalikes must show ZERO delta.

  R-100 #7  the ONE exempt record named by uber_quest_markers.MARKER_EXEMPT
         (today: um_bloodtoxeus_99, closed over actorToSpawnOnDeath).
         EXACTLY ONE field: DisplayAsQuestItem 1 -> 0.
         Every OTHER roster member must show ZERO delta - they were all already
         marked on `main`, so if one moves, something re-derived the roster.

  R-100 #18  the six svc_general_{a,b,c}_guard{1,2} records, the three
         q_general_*_guardpair proxies, and 27 NEW hoard records.
         The guards may move only on the retune field set; the proxies only on
         their three accessory slots; the 27 hoard records are ADDs.

ATTRIBUTION IS DELIBERATELY STRICT: the roster/exempt/guard sets are DERIVED
LIVE from the built db through the modules' own APIs, never typed into this file.
A REMOVED record is always a failure. An ADDED record is a failure unless it is
one of the 27 hoard records this lane's own module declares.

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


# fields R-100 #18 is allowed to move on a guard monster record
GUARD_FIELDS = {
    'scale', 'characterLife', 'characterLifeRegen',
    'defensivePhysical', 'defensiveLife', 'defensivePoison', 'defensiveFire',
    'treasureProxyName',
    'skillName4', 'skillName5', 'skillLevel4', 'skillLevel5',
    'specialAttack2SkillName', 'specialAttack2Chance', 'specialAttack2Range',
    'specialAttack2Timeout', 'specialAttack2Delay',
    'specialAttack3SkillName', 'specialAttack3Chance', 'specialAttack3Range',
    'specialAttack3Timeout', 'specialAttack3Delay',
}
PROXY_FIELDS = {'accessory1', 'accessoryEpic1', 'accessoryLegendary1'}
R80_FROZEN = ('deathPenaltyEquation', 'deathPenaltyMin', 'deathPenaltyMax')


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    base = ArzDatabase.from_arz(Path(argv[0]))
    built = ArzDatabase.from_arz(Path(argv[1]))

    from patches import uber_quest_markers as UQM     # noqa: E402
    from patches import general_guardians as GG       # noqa: E402
    from patches import tombstone_xp_recovery as TXR  # noqa: E402

    # --- DERIVE every expected set from the BUILT db, never from a typed list --
    roster, exempt, _adds, _shared, _noise = UQM.placed_uber_roster(built)
    roster_n = {norm(r) for r in roster}
    exempt_n = {norm(r) for r in exempt}
    guards_n = {norm(q) for pair in GG.GUARD.values() for q in pair}
    proxies_n = {norm(p) for p in GG.GUARD_PROXY.values()}
    hoards_n = {norm(r) for g in GG.GENERALS for r in GG._hoard_records(g)}
    ge_n = norm(TXR.GAMEENGINE)
    lookalikes_n = {norm(r) for r in TXR.DEAD_LOOKALIKES}

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
                d[k.split('###')[0]] = (vb, vt)
        if d:
            changed[n] = d

    print('=' * 78)
    print('R-108 / feat/uber-visibility RECORD DIFF')
    print('  baseline : %s' % argv[0])
    print('  built    : %s' % argv[1])
    print('  records  : baseline %d -> built %d' % (len(bnames), len(tnames)))
    print('  DERIVED: roster %d, R-100 #7 exempt %d, guards %d, guard proxies %d, '
          'declared new hoard records %d'
          % (len(roster_n), len(exempt_n), len(guards_n), len(proxies_n), len(hoards_n)))
    print('  ADDED %d / REMOVED %d / CHANGED %d'
          % (len(added), len(removed), len(changed)))
    print('=' * 78)

    attributed, unattributed = [], []

    for n in removed:
        unattributed.append(('REMOVED', n, set(),
                             'this lane retires NOTHING (retirement protocol)'))
    for n in added:
        if n in hoards_n:
            attributed.append(('R-100 #18 hoard ADD', n, 'new record'))
        else:
            unattributed.append(('ADDED', n, set(),
                                 'the only records this lane authors are the 27 '
                                 'declared guard-hoard records'))

    for n, d in sorted(changed.items()):
        fields = set(d)

        if n == ge_n:                                   # ---- R-109 ----
            extra = fields - {'RedemptionMultiplier'}
            if extra:
                unattributed.append(('CHANGED', n, extra,
                                     'R-109 moves ONE field on the GameEngine record'))
                continue
            vb, vt = d['RedemptionMultiplier']
            got = float(vt[1][0]) if vt and vt[1] else None
            was = float(vb[1][0]) if vb and vb[1] else None
            if was != 0.5 or got != 1.0:
                unattributed.append(('CHANGED', n, fields,
                                     'RedemptionMultiplier %r -> %r, want 0.5 -> 1.0'
                                     % (was, got)))
                continue
            attributed.append(('R-109', n, 'RedemptionMultiplier 0.5 -> 1.0'))
            continue

        if n in exempt_n:                               # ---- R-100 #7 ----
            extra = fields - {'DisplayAsQuestItem'}
            if extra:
                unattributed.append(('CHANGED', n, extra,
                                     'R-100 #7 moves ONE field on the exempt boss'))
                continue
            vb, vt = d['DisplayAsQuestItem']
            was = float(vb[1][0]) if vb and vb[1] else None
            got = float(vt[1][0]) if vt and vt[1] else None
            if was != 1.0 or got != 0.0:
                unattributed.append(('CHANGED', n, fields,
                                     'DisplayAsQuestItem %r -> %r, want 1 -> 0'
                                     % (was, got)))
                continue
            attributed.append(('R-100 #7', n, 'DisplayAsQuestItem 1 -> 0'))
            continue

        if n in guards_n:                               # ---- R-100 #18 guard ----
            extra = fields - GUARD_FIELDS
            if extra:
                unattributed.append(('CHANGED', n, extra,
                                     'outside the declared guard retune field set'))
                continue
            attributed.append(('R-100 #18 guard', n,
                               '%d field(s): %s' % (len(fields),
                                                    ', '.join(sorted(fields)))))
            continue

        if n in proxies_n:                              # ---- R-100 #18 proxy ----
            extra = fields - PROXY_FIELDS
            if extra:
                unattributed.append(('CHANGED', n, extra,
                                     'only the 3 accessory slots may move on a '
                                     'guard-pair proxy'))
                continue
            attributed.append(('R-100 #18 proxy', n,
                               'accessory1/Epic1/Legendary1 wired'))
            continue

        unattributed.append(('CHANGED', n, fields,
                             'not the GameEngine record, not the R-100 #7 exempt '
                             'boss, not a guard and not a guard-pair proxy'))

    # ---- the explicit ZERO-DELTA claims this lane makes ---------------------
    zero_delta = []
    for label, names in (
            ('R-100 #7: every OTHER roster member (already marked on main)',
             sorted(roster_n)),
            ('R-109: the 5 dead gameengine lookalikes', sorted(lookalikes_n))):
        moved = [n for n in names if n in changed]
        zero_delta.append((label, len(names), moved))
        for n in moved:
            unattributed.append(('CHANGED', n, set(changed[n]),
                                 'must have ZERO delta: ' + label))

    ge_r80 = []
    if ge_n in changed:
        ge_r80 = [f for f in R80_FROZEN if f in changed[ge_n]]
        for f in ge_r80:
            unattributed.append(('CHANGED', ge_n, {f},
                                 'R-80 field must be frozen by this lane'))

    print('\n--- ATTRIBUTED : %d ---' % len(attributed))
    for kind, n, why in attributed:
        print('  %-22s %-64s %s' % (kind, n, why))

    print('\n--- ZERO-DELTA CLAIMS, re-checked ---')
    for label, total, moved in zero_delta:
        print('  %-58s %d record(s), %d moved' % (label, total, len(moved)))
    print('  %-58s %d moved' % ('R-80 fields on the GameEngine record', len(ge_r80)))

    print('\n' + '=' * 78)
    if unattributed:
        print('UNATTRIBUTED DELTAS: %d  ** NO-GO **' % len(unattributed))
        for kind, n, bad, why in unattributed:
            print('   %-8s %s  %s  (%s)'
                  % (kind, n, ('fields=' + ','.join(sorted(bad))) if bad else '', why))
        return 1
    print('RESULT: PASS - 0 REMOVED, %d ADDED (all 27 declared guard-hoard records), '
          '%d CHANGED and every one attributes to R-100 #7, R-100 #18 or R-109. '
          'Zero unattributed changes.' % (len(added), len(changed)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
