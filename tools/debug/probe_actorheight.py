r"""probe_actorheight - the measurement behind R-126.

Answers ONE question with data instead of intuition: is `actorHeight` a size
knob that should move with `scale`, or a per-RIG constant that a clone must
inherit from its donor?

Run it against any built arz:

    py tools/debug/probe_actorheight.py work/SoulvizierClassic/Database/SoulvizierClassic.arz

It groups every record by its `mesh` (the rig), then reports how often
actorHeight varies inside one rig, how much of that variance is just the 0.0
"no-height" class, and - the decisive number - in how many rigs actorHeight is
actually PROPORTIONAL to scale. On the b102 arz that last number is 0 out of
2,122, which is why devourer_kit stopped writing the field.

`--record <path>` prints one record against its own rig, which is the shape the
devourer_kit gate enforces.
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase                              # noqa: E402

BS = chr(92)


def _rigs(db):
    """{mesh: {record: (scale, actorHeight)}} for every record carrying both."""
    out = defaultdict(dict)
    for n in db.record_names():
        mesh = ah = sc = None
        for k, tf in (db.get_fields(n) or {}).items():
            b = k.split('###')[0]
            if not tf.values:
                continue
            if b == 'mesh':
                mesh = str(tf.values[0]).lower()
            elif b == 'actorHeight':
                ah = round(float(tf.values[0]), 3)
            elif b == 'scale':
                sc = round(float(tf.values[0]), 3)
        if mesh and ah is not None and sc is not None:
            out[mesh][n] = (sc, ah)
    return out


def survey(db):
    rigs = _rigs(db)
    multi = {m: v for m, v in rigs.items() if len(v) > 1}
    both = nonzero = proportional = 0
    for v in multi.values():
        ss = {x[0] for x in v.values()}
        hs = {x[1] for x in v.values()}
        if len(ss) < 2 or len(hs) < 2:
            continue
        both += 1
        if len({h for h in hs if h != 0.0}) < 2:
            continue          # the whole variance was the 0.0 no-height class
        nonzero += 1
        ratios = [h / s for s, h in v.values() if s and h]
        if ratios and (max(ratios) - min(ratios)) / (sum(ratios) / len(ratios)) < 0.05:
            proportional += 1
    print('rigs (distinct `mesh` values) carrying actorHeight on >1 record : %d'
          % len(multi))
    print('  ... where BOTH scale and actorHeight vary                     : %d' % both)
    print('  ... still varying after dropping the 0.0 no-height class      : %d' % nonzero)
    print('  ... where actorHeight is PROPORTIONAL to scale                : %d' % proportional)
    print()
    print('VERDICT: actorHeight is a per-RIG constant, not a size knob.'
          if proportional == 0 else
          'VERDICT: %d rig(s) DO scale actorHeight - re-read R-126 before trusting it.'
          % proportional)
    return proportional


def one(db, rec):
    for mesh, v in _rigs(db).items():
        if rec in v:
            others = {n: hv for n, hv in v.items() if n != rec}
            print('record : %s' % rec)
            print('rig    : %s  (%d other record(s) on it)' % (mesh, len(others)))
            print('  rig actorHeight values : %s' % sorted({h for _, h in others.values()}))
            print('  rig scale values       : %s' % sorted({s for s, _ in others.values()}))
            print('  THIS RECORD            : scale=%s actorHeight=%s' % v[rec])
            return 0
    print('record not found, or it carries no mesh/actorHeight/scale triple: %s' % rec)
    return 1


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    db = ArzDatabase.from_arz(Path(args[0]))
    if '--record' in args:
        raise SystemExit(one(db, args[args.index('--record') + 1]))
    survey(db)
