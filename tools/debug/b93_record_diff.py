#!/usr/bin/env python3
r"""b93 record-diff: prove the death-XP lane changed EXACTLY the intended records/fields.

Usage:
  py tools/debug/b93_record_diff.py <baseline.arz> <built.arz>

Prints added / removed / changed records and, for each changed record, the exact
field-level before -> after (with dtypes). Exits 1 if anything outside the b93
intent moved, or if an intended change is missing.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase

INTENDED = {
    r'records\xpack\game\gameengine.dbr': {'deathPenaltyEquation', 'deathPenaltyMax'},
}


def norm(s):
    return s.lower().replace('/', '\\')


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    a = ArzDatabase.from_arz(Path(argv[0]))
    b = ArzDatabase.from_arz(Path(argv[1]))
    na = {norm(n): n for n in a.record_names()}
    nb = {norm(n): n for n in b.record_names()}
    added = sorted(set(nb) - set(na))
    removed = sorted(set(na) - set(nb))
    print('records: baseline=%d built=%d  added=%d removed=%d'
          % (len(na), len(nb), len(added), len(removed)))
    for n in added:
        print('  ADDED   %s' % nb[n])
    for n in removed:
        print('  REMOVED %s' % na[n])

    changed = {}
    for low in sorted(set(na) & set(nb)):
        fa = a.get_fields(na[low]) or {}
        fb = b.get_fields(nb[low]) or {}
        diffs = []
        for k in sorted(set(fa) | set(fb)):
            va = (fa[k].dtype, list(fa[k].values)) if k in fa else None
            vb = (fb[k].dtype, list(fb[k].values)) if k in fb else None
            if va != vb:
                diffs.append((k, va, vb))
        if diffs:
            changed[low] = (nb[low], diffs)

    print('changed records: %d' % len(changed))
    bad = bool(added or removed)
    for low, (rec, diffs) in sorted(changed.items()):
        want = INTENDED.get(low)
        if want is None:
            bad = True
        print('  [%s] %s' % ('INTENDED' if want else 'UNINTENDED', rec))
        for k, va, vb in diffs:
            if want is not None and k not in want:
                bad = True
                print('      !! field outside intent: %s' % k)
            print('      %-24s %r  ->  %r' % (k, va, vb))
        if want is not None:
            missing = want - {k for k, _, _ in diffs}
            if missing:
                bad = True
                print('      !! intended field(s) did NOT move: %s'
                      % ', '.join(sorted(missing)))
    for rec in INTENDED:
        if norm(rec) not in changed:
            bad = True
            print('  !! intended record did NOT change: %s' % rec)

    print('\nRESULT: %s' % ('FAIL - diff exceeds the b93 intent' if bad
                            else 'PASS - diff == the b93 intent exactly'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
