#!/usr/bin/env python3
r"""b102 (R-102) record-diff: every delta must be attributable to the mesh swap
or to the shroud reaching the pet tiers. Nothing else may move.

Usage:
  py tools/debug/b102_green_mesh_record_diff.py <baseline.arz> <built.arz>

Baseline = a build of `main` @ 7efd107 in THIS environment, measured
**6a3a491db546b603c52132237c40aa63**, 55,475,226 B, 51,124 records, exit 0 with
every gate (SVC_REQUIRE_GATES=1, work/ layout so A9 + the contract suite run).
Built = the same command on `fix/green-mesh-swap`.

THE ONLY LEGITIMATE DELTAS
--------------------------
1. `mesh` on a record of the DERIVED champion roster
   (`patches.champion_mesh.roster`, read live out of the BUILT db - anchors plus
   every pet tier taken from each champion's summon `spawnObjects`), moving
   RevenantPoison.msh -> that family's clean mesh. Nothing else on those records.
2. `skillName<N>` + `skillLevel<N>` appearing on an Enslaver PET TIER
   (`patches.enslaver_shroud.shroud_roster`), granting `svc_enslaver_shroud` in a
   slot that was FREE before. R-102's second amendment: b98 gave the shroud to
   the monster only, which is why Will said it was never implemented.

Everything else - any other changed record, any ADDED record, any REMOVED record
- is UNATTRIBUTED and fails. A REMOVED record is always a failure: this lane
retires nothing (RETIREMENT PROTOCOL), and in particular the base-game revenants
and the ten pharaoh honour-guard summons must still carry RevenantPoison.msh
afterwards (that is asserted here as well as in champion_mesh.verify).

Exit 0 = every delta attributed. Exit 1 = at least one unattributed delta.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'patches'))

from arz_patcher import ArzDatabase  # noqa: E402

_SLOT_RE = re.compile(r'^skill(Name|Level)(\d+)$')


def norm(s):
    return str(s).lower().replace('/', '\\')


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    base = ArzDatabase.from_arz(Path(argv[0]))
    built = ArzDatabase.from_arz(Path(argv[1]))

    from patches import champion_mesh as CM      # noqa: E402
    from patches import enslaver_shroud as ES    # noqa: E402

    # rosters DERIVED from the built db - never a list typed into this file
    mesh_expect = {}
    for fam, members in CM.roster(built):
        for m in members:
            mesh_expect[norm(m)] = norm(fam['mesh'])
    shroud_pets = {norm(r) for r in ES.shroud_roster(built) if norm(r) != norm(ES._ENSLAVER)}
    shroud_skill = norm(ES._SHROUD)

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

    print('=' * 82)
    print('b102 R-102 RECORD DIFF (kill the mesh-embedded green + shroud to every pet tier)')
    print('  baseline : %s' % argv[0])
    print('  built    : %s' % argv[1])
    print('  records  : baseline %d -> built %d' % (len(bnames), len(tnames)))
    print('  DERIVED champion-mesh roster : %d record(s)' % len(mesh_expect))
    print('  DERIVED shroud pet tiers     : %d record(s)' % len(shroud_pets))
    print('  ADDED %d / REMOVED %d / CHANGED %d'
          % (len(added), len(removed), len(changed)))
    print('=' * 82)

    mesh_moves, shroud_moves, unattributed = [], [], []

    for n in added:
        unattributed.append(('ADDED', n, set(),
                             'R-102 authors NO new records - it repoints a field '
                             'and fills free skill slots'))
    for n in removed:
        unattributed.append(('REMOVED', n, set(),
                             'R-102 retires NOTHING (RETIREMENT PROTOCOL)'))

    # Attribution is PER FIELD, not per record. The three Enslaver pet tiers are
    # in BOTH rosters and legitimately carry a delta from each leg in the same
    # record (their mesh moved AND the shroud landed in a free slot), so a
    # per-record "match exactly one leg" rule would call the correct result a
    # violation - it did, on the first run. Partition the fields instead, and
    # require that EVERY field lands in one of the two legs.
    for n, d in sorted(changed.items()):
        leftover = set(d)

        # ── leg 1: the mesh swap ──
        if 'mesh' in leftover:
            if n not in mesh_expect:
                unattributed.append(('CHANGED', n, {'mesh'},
                                     'mesh moved on a record that is NOT in the '
                                     'derived champion roster'))
            else:
                vb, vt = d['mesh']
                old = norm(vb[1][0]) if vb and vb[1] else None
                new = norm(vt[1][0]) if vt and vt[1] else None
                if old != norm(CM.GREEN_MESH):
                    unattributed.append(('CHANGED', n, {'mesh'},
                                         'moved OFF %r, but the only mesh this lane '
                                         'takes a record off is %s'
                                         % (old, CM.GREEN_MESH)))
                elif new != mesh_expect[n]:
                    unattributed.append(('CHANGED', n, {'mesh'},
                                         'landed on %r, expected %r for its family'
                                         % (new, mesh_expect[n])))
                else:
                    mesh_moves.append((n, old, new))
            leftover.discard('mesh')

        # ── leg 2: the shroud reaching a pet tier ──
        slot_fields = {k for k in leftover if _SLOT_RE.match(k)}
        if slot_fields:
            if n not in shroud_pets:
                unattributed.append(('CHANGED', n, slot_fields,
                                     'skill slots moved on a record that is NOT a '
                                     'derived Enslaver pet tier'))
            else:
                slots = {int(_SLOT_RE.match(k).group(2)) for k in slot_fields}
                bad = None
                for s in sorted(slots):
                    nb = d.get('skillName%d' % s)
                    if nb is None:
                        bad = ('skillLevel%d moved with no matching skillName%d'
                               % (s, s))
                        break
                    vb, vt = nb
                    if vb is not None and vb[1] and str(vb[1][0]).strip():
                        bad = ('skillName%d was OCCUPIED (%r) before - this lane '
                               'only fills FREE slots, it never displaces a skill '
                               '(R-26)' % (s, vb[1][0]))
                        break
                    if not vt or not vt[1] or norm(vt[1][0]) != shroud_skill:
                        bad = ('skillName%d landed on %r, not the shroud'
                               % (s, vt[1][0] if vt and vt[1] else None))
                        break
                    # The granted LEVEL must be non-zero in the BUILT db. It may
                    # show no delta: these pets already carried an orphaned
                    # skillLevel13=1 (Lyia-clone residue, a level with no skill),
                    # so filling that slot writes the value it already had. Read
                    # the built record rather than the diff.
                    lv = built.get_field_value(tmap[n], 'skillLevel%d' % s)
                    lvv = lv[0] if isinstance(lv, list) and lv else lv
                    if not lvv:
                        bad = ('skillLevel%d is %r in the built db - level 0 is '
                               'never granted' % (s, lvv))
                        break
                if bad:
                    unattributed.append(('CHANGED', n, slot_fields, bad))
                else:
                    shroud_moves.append((n, sorted(slots)))
            leftover -= slot_fields

        if leftover:
            unattributed.append(('CHANGED', n, leftover,
                                 'field(s) belonging to neither leg of this lane'))

    print('\n--- LEG 1: MESH MOVED OFF THE GREEN MESH : %d record(s) ---' % len(mesh_moves))
    for n, old, new in mesh_moves:
        print('  %-70s %-24s -> %s'
              % (n, old.rsplit('\\', 1)[-1], new.rsplit('\\', 1)[-1]))

    print('\n--- LEG 2: SHROUD GRANTED IN A FREE SLOT ON A PET TIER : %d record(s) ---'
          % len(shroud_moves))
    for n, slots in shroud_moves:
        print('  %-70s slot(s) %s' % (n, slots))

    # RETIREMENT PROTOCOL: the shared mesh must survive on its other carriers.
    green = []
    for n in sorted(tnames):
        v = built.get_field_value(tmap[n], 'mesh')
        v = v[0] if isinstance(v, list) and v else v
        if v and norm(v) == norm(CM.GREEN_MESH):
            green.append(n)
    base_green = []
    for n in sorted(bnames):
        v = base.get_field_value(bmap[n], 'mesh')
        v = v[0] if isinstance(v, list) and v else v
        if v and norm(v) == norm(CM.GREEN_MESH):
            base_green.append(n)
    print('\n--- RETIREMENT PROTOCOL: carriers of %s ---'
          % CM.GREEN_MESH.rsplit('\\', 1)[-1])
    print('  baseline %d -> built %d  (expected drop = %d roster records)'
          % (len(base_green), len(green), len(mesh_moves)))
    lost = [n for n in base_green if n not in green]
    unexpected = [n for n in lost if n not in {m[0] for m in mesh_moves}]
    for n in green:
        print('     KEPT   %s' % n)
    if unexpected:
        unattributed.append(('RETIREMENT', ', '.join(unexpected[:6]), set(),
                             'a NON-roster carrier lost the shared mesh'))
    if not green:
        unattributed.append(('RETIREMENT', CM.GREEN_MESH, set(),
                             'the shared mesh has ZERO carriers left - it was '
                             'retired, not repointed'))

    print('\n' + '=' * 82)
    if unattributed:
        print('UNATTRIBUTED DELTAS: %d  ** NO-GO **' % len(unattributed))
        for kind, n, bad, why in unattributed:
            print('   %-10s %s  %s  (%s)'
                  % (kind, n, ('fields=' + ','.join(sorted(bad))) if bad else '', why))
        return 1
    print('RESULT: PASS - 0 ADDED, 0 REMOVED, %d CHANGED; %d are derived-roster mesh '
          'moves off %s and %d are the shroud landing in a FREE slot on a derived '
          'pet tier. Zero unattributed changes; %d non-roster carriers of the shared '
          'mesh survive untouched.'
          % (len(changed), len(mesh_moves), CM.GREEN_MESH.rsplit('\\', 1)[-1],
             len(shroud_moves), len(green)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
