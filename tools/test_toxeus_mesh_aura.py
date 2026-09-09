r"""b92 NEGATIVE TEST for the toxeus_mesh_aura gate.

Four recurrences of the green glow means the gate itself has to be tested, not
just written. This drives the REAL `toxeus_mesh_aura.verify()` over a shim that
serves records out of a real .arz, mutating one field at a time, and asserts the
gate's verdict on every leg - including the decisive one:

    the arz Will was looking at when he filed the bug MUST FAIL this gate.

Committed (not scratchpad) so the claim is reproducible by anyone:

    py tools/test_toxeus_mesh_aura.py
    py tools/test_toxeus_mesh_aura.py --arz <path>   # default: the deployed DEV arz

Exit 0 = every leg behaved as specified.
"""
import argparse
import os
import sys
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

from arz_patcher import ArzDatabase                      # noqa: E402
from patches import toxeus_mesh_aura as MOD              # noqa: E402

def _default_arz():
    """The PRE-FIX arz Will filed the bug against, md5 1c27d5fa.

    Two wrinkles this has to survive:
      * `local/` is not checked out in linked worktrees, so walk up to the main
        repo (a linked worktree lives at <repo>/.claude/worktrees/<name>);
      * `local/DEV_arz_deployed_prev.arz` is a ROLLING name - any lane that
        deploys to DEV overwrites it (b92 round 2 found it already replaced by a
        parallel lane). So prefer the pinned b92 copy and keep the rolling name
        only as a fallback.
    """
    names = ('b92_ground_truth_1c27d5fa.arz', 'DEV_arz_deployed_prev.arz')
    d = os.path.dirname(_HERE)
    for _ in range(6):
        for nm in names:
            cand = os.path.join(d, 'local', nm)
            if os.path.isfile(cand):
                return cand
        d = os.path.dirname(d)
    return os.path.join(os.path.dirname(_HERE), 'local', names[0])


DEFAULT_ARZ = _default_arz()
GREEN = r'Creatures\Monster\Skeleton\RevenantPoison.msh'
STORM = r'Creatures\Monster\skeleton\revenantstorm.msh'
SPIRIT = r'Creatures\Monster\Skeleton\SkeletonSpirit01.msh'
UNAUDITED = r'Creatures\Monster\Skeleton\SkeletonRumorBoss.msh'


class Shim:
    """Minimal db facade over a real ArzDatabase with an overlay of mesh edits."""

    def __init__(self, db, overlay=None):
        self._db = db
        self._ov = dict(overlay or {})

    def has_record(self, n):
        return self._db.has_record(n)

    def get_field_value(self, n, f):
        if f == 'mesh' and n in self._ov:
            return self._ov[n]
        return self._db.get_field_value(n, f)

    def get_fields(self, n):
        return self._db.get_fields(n)

    def record_names(self):
        return self._db.record_names()

    def with_mesh(self, **_):
        raise NotImplementedError

    def edited(self, rec, mesh):
        ov = dict(self._ov)
        ov[rec] = mesh
        return Shim(self._db, ov)


def _runs_clean(db):
    """True if verify() passes, False if it raises SystemExit."""
    try:
        MOD.verify(db, {})
        return True
    except SystemExit:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arz', default=DEFAULT_ARZ,
                    help='baseline .arz (default: local/DEV_arz_deployed_prev.arz, '
                         'the state Will filed the bug against)')
    args = ap.parse_args()

    if not os.path.isfile(args.arz):
        print(f'SKIP: baseline arz not found: {args.arz}')
        return 0

    print(f'baseline: {args.arz}')
    raw = ArzDatabase.from_arz(Path(args.arz))
    shipped = Shim(raw)

    # The "fixed" state = the shipped arz with every target moved to the clean mesh.
    fixed_ov = {rec: MOD.CLEAN_MESH for _, rec in MOD.TARGETS}
    fixed = Shim(raw, fixed_ov)

    legs = []

    def leg(name, db, expect_pass):
        got = _runs_clean(db)
        ok = (got == expect_pass)
        legs.append((ok, name, 'PASS' if expect_pass else 'FAIL', 'PASS' if got else 'FAIL'))
        return ok

    # 1. the fixed state must pass
    leg('fixed state (all targets -> CLEAN_MESH)', fixed, True)

    # 2. THE DECISIVE LEG: the baseline arz AS-IS. A PRE-FIX arz (any target
    #    still on the green mesh) MUST be rejected; a post-fix one must pass.
    #    The expectation is derived from the bytes so the test stays meaningful
    #    whichever arz it is pointed at.
    def _basename(p):
        return (p or '').lower().replace('/', '\\').rsplit('\\', 1)[-1]

    greens = [rec for _, rec in MOD.TARGETS
              if _basename(shipped.get_field_value(rec, 'mesh') or '') == MOD.GREEN_MESH_BASENAME]
    if greens:
        leg(f'*** the baseline arz as-is - PRE-FIX, {len(greens)}/{len(MOD.TARGETS)} targets '
            f'still on {MOD.GREEN_MESH_BASENAME} (the state Will reported) ***', shipped, False)
    else:
        leg('*** the baseline arz as-is - already FIXED, no target on the green mesh ***',
            shipped, True)

    # 3. replanting the green mesh on any single target must FAIL
    for lbl, rec in MOD.TARGETS:
        leg(f'green mesh replanted on {lbl}', fixed.edited(rec, GREEN), False)

    # 4. an UNAUDITED mesh on any target must FAIL (unknown embedded effect)
    leg('unaudited mesh (SkeletonRumorBoss) on the Devourer',
        fixed.edited(MOD.DEVOURER_FAMILY[0][1], UNAUDITED), False)
    leg('unaudited mesh (SkeletonRumorBoss) on the Enslaver',
        fixed.edited(MOD.ENSLAVER_FAMILY[0][1], UNAUDITED), False)

    # 5. a NON-green audited effect mesh is ALLOWED (the gate encodes the bug,
    #    not an unratified "no aura of any colour" art policy - vet HIGH-3)
    leg('RevenantStorm (audited, NOT green) on the Enslaver - allowed, with a note',
        fixed.edited(MOD.ENSLAVER_FAMILY[0][1], STORM), True)
    leg('SkeletonSpirit01 (audited, no CreateEntity) on the Devourer - allowed',
        fixed.edited(MOD.DEVOURER_FAMILY[0][1], SPIRIT), True)

    # 6. Will's protected records must be protected in BOTH directions
    for lbl, rec, _want in MOD.PROTECTED:
        leg(f'PROTECTED {lbl} moved off its ruled mesh',
            fixed.edited(rec, MOD.CLEAN_MESH if 'Greece' in lbl else GREEN), False)

    print()
    for ok, name, exp, got in legs:
        print(f'  [{"ok " if ok else "BAD"}] expect={exp:4s} got={got:4s}  {name}')
    bad = [x for x in legs if not x[0]]
    print(f'\n{len(legs) - len(bad)}/{len(legs)} legs correct')
    if bad:
        print('NEGATIVE TEST FAILED')
        return 1
    print('NEGATIVE TEST PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
