#!/usr/bin/env python3
r"""b101 (R-99) PROOF TABLE, read back OUT of the built arz.

Usage:
  py tools/debug/b101_r99_proof_table.py <built.arz> [<baseline.arz>]

Everything below is READ FROM THE BUILT ARTIFACT, never from the patch module's
intentions - the point is to prove what actually landed in the bytes the player
would get. With a baseline arz given, the donor-tier proofs become before/after
comparisons instead of after-only assertions.

SECTIONS
  1. THE ROSTER TABLE - every DERIVED Toxeus creature record, its charLevel on
     all three difficulties, its rank, and the `treasureProxyName` actually in the
     built db. This is the table R-99 is graded against.
  2. genericbossorb_04 BYTE-UNCHANGED - the proxy AND its whole donor chain
     (3 pools, 3 chests, 3 loot tables) compared field-by-field against the
     baseline, plus the full consumer list. orb05 exists precisely so these
     records do not move.
  3. genericbossorb_01 - the SECOND donor tier, which `um_toxeus_21` leaves under
     R-99. Its other consumers get the same protection.
  4. R-48 / R-91 INDEPENDENCE - the soul wiring (`chanceToEquipFinger2`,
     `lootFinger2Item1`) on every roster record, before and after. Souls are
     Finger2 EQUIPMENT and orbs are `treasureProxyName`; this is where that
     independence is measured rather than asserted.
  5. THE ORB05 CHAIN, resolved end to end on all three difficulties.

Exit 0 always - a measurement tool. The enforcing gate is
`uber_apex_orb.verify()`; the planted negatives are
`tools/debug/negtest_uber_apex_orb.py`.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / 'patches'))

from arz_patcher import ArzDatabase  # noqa: E402


def norm(s):
    return str(s).lower().replace('/', '\\')


def v1(db, rec, field):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def fields(db, rec):
    out = {}
    ff = db.get_fields(rec)
    if not ff:
        return out
    for k, tf in ff.items():
        out.setdefault(k.split('###')[0], (tf.dtype, list(tf.values)))
    return out


def consumers(db, orb):
    low = norm(orb)
    return sorted(n for n in db.record_names()
                  if isinstance(v1(db, n, 'treasureProxyName'), str)
                  and norm(v1(db, n, 'treasureProxyName')) == low)


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    built = ArzDatabase.from_arz(Path(argv[0]))
    base = ArzDatabase.from_arz(Path(argv[1])) if len(argv) > 1 else None

    from patches import uber_apex_orb as M  # noqa: E402
    roster = M.toxeus_roster(built)

    print('=' * 100)
    print('b101 R-99 PROOF TABLE - read OUT of %s' % argv[0])
    if base:
        print('  baseline for the byte-unchanged proofs: %s' % argv[1])
    print('  records in built db: %d' % len(list(built.record_names())))
    print('=' * 100)

    # ── 1. THE ROSTER TABLE ─────────────────────────────────────────────────
    print('\n[1] THE R-99 ROSTER (derived: path contains \'toxeus\' AND '
          'templateName is Monster.tpl)\n')
    print('%-24s %-14s %-10s %-22s %s'
          % ('record', 'charLevel n/e/l', 'rank', 'treasureProxyName', 'name tag'))
    print('-' * 100)
    for rec in roster:
        # charLevel is ONE field holding a 3-element array (normal/epic/legendary),
        # not three fields - reading only [0] silently reports '40/-/-' for a
        # 40/68/100 boss, which is how a proof table starts lying.
        lvv = built.get_field_value(rec, 'charLevel')
        lvv = lvv if isinstance(lvv, list) else ([lvv] if lvv is not None else [])
        lv = [str(int(float(x))) for x in lvv] or ['-']
        rank = v1(built, rec, 'monsterClassification') or '-'
        tp = v1(built, rec, 'treasureProxyName')
        tp = str(tp).rsplit('\\', 1)[-1] if tp else '** NONE **'
        print('%-24s %-14s %-10s %-22s %s'
              % (rec.rsplit('\\', 1)[-1], '/'.join(lv), rank, tp,
                 v1(built, rec, 'description') or '-'))
    print('\nfull paths:')
    for rec in roster:
        print('  %s' % rec)

    # ── 2 + 3. DONOR TIERS ──────────────────────────────────────────────────
    for orb, label in ((M.ORB04, 'genericbossorb_04 (R-47 shared generic apex orb)'),
                       (M.ORB01, 'genericbossorb_01 (um_toxeus_21\'s old tier)')):
        n = 2 if orb == M.ORB04 else 3
        print('\n[%d] DONOR TIER %s' % (n, label))
        chain = [orb]
        if orb == M.ORB04:
            for d in ('normal', 'epic', 'legendary'):
                p, _np, c, _nc, t, _nt = M.CHAIN[d]
                chain += [p, c, t]
        if base:
            moved = []
            for r in chain:
                if not (built.has_record(r) and base.has_record(r)):
                    moved.append('%s (MISSING on one side)' % r)
                elif fields(built, r) != fields(base, r):
                    moved.append(r)
            print('    chain records compared field-by-field vs baseline: %d' % len(chain))
            if moved:
                print('    ** CHANGED (this is a blast-radius violation): %s **' % moved)
            else:
                print('    BYTE-UNCHANGED: all %d record(s) identical to the baseline '
                      '(every field, every value, every dtype)' % len(chain))
        cons_built = consumers(built, orb)
        cons_base = consumers(base, orb) if base else None
        roster_low = {norm(r) for r in roster}
        still = [c for c in cons_built if norm(c) in roster_low]
        print('    consumers: %s%d ; Toxeus record(s) still on it: %d'
              % (('baseline %d -> built ' % len(cons_base)) if cons_base is not None else '',
                 len(cons_built), len(still)))
        if cons_base is not None:
            lost = sorted(set(cons_base) - set(cons_built))
            gained = sorted(set(cons_built) - set(cons_base))
            print('    lost  : %s' % ([x.rsplit('\\', 1)[-1] for x in lost] or 'none'))
            print('    gained: %s' % ([x.rsplit('\\', 1)[-1] for x in gained] or 'none'))
        for c in cons_built:
            print('      still on it: %s' % c)

    # ── 4. R-48 / R-91 INDEPENDENCE ─────────────────────────────────────────
    print('\n[4] R-48 / R-91 SOUL WIRING (Finger2 equipment - independent of the orb)\n')
    print('%-24s %-10s %-10s %s' % ('record', 'chance', 'baseline', 'lootFinger2Item1'))
    print('-' * 100)
    for rec in roster:
        c = v1(built, rec, 'chanceToEquipFinger2')
        cb = v1(base, rec, 'chanceToEquipFinger2') if base and base.has_record(rec) else 'n/a'
        soul = built.get_field_value(rec, 'lootFinger2Item1')
        soul = soul[0] if isinstance(soul, list) and soul else soul
        flag = ''
        if base and base.has_record(rec):
            if fields(built, rec).get('chanceToEquipFinger2') != fields(base, rec).get('chanceToEquipFinger2') \
               or fields(built, rec).get('lootFinger2Item1') != fields(base, rec).get('lootFinger2Item1'):
                flag = '  ** MOVED - COLLATERAL DAMAGE **'
        print('%-24s %-10s %-10s %s%s'
              % (rec.rsplit('\\', 1)[-1], c, cb,
                 str(soul).rsplit('\\', 1)[-1] if soul else '-', flag))
    print('\n  the three FOUGHT champions R-48/R-91 state 100 about:')
    for label, rec in M._SOUL_100_CHAMPIONS:
        print('    %-42s chanceToEquipFinger2 = %s'
              % (label, v1(built, rec, 'chanceToEquipFinger2')))

    # ── 5. THE ORB05 CHAIN ──────────────────────────────────────────────────
    print('\n[5] THE genericbossorb_05 CHAIN, resolved out of the built db\n')
    for d in ('normal', 'epic', 'legendary'):
        _p, pool, _c, chest, _t, table = M.CHAIN[d]
        field = {'normal': 'accessory1', 'epic': 'accessoryEpic1',
                 'legendary': 'accessoryLegendary1'}[d]
        print('  %-10s orb05.%-20s -> %s' % (d, field,
                                             str(v1(built, M.ORB05, field)).rsplit('\\', 1)[-1]))
        print('  %-10s pool.fixedItemName1       -> %s'
              % ('', str(v1(built, pool, 'fixedItemName1')).rsplit('\\', 1)[-1]))
        print('  %-10s chest.tables              -> %s'
              % ('', str(v1(built, chest, 'tables')).rsplit('\\', 1)[-1]))
        print('  %-10s table knobs: min=%s max=%s loot4Chance=%s goldGeneratorLevel=%s'
              % ('', v1(built, table, 'numSpawnMinEquation'),
                 v1(built, table, 'numSpawnMaxEquation'),
                 v1(built, table, 'loot4Chance'),
                 v1(built, table, 'goldGeneratorLevel')))
        print('  %-10s Leinth chest (%s).tables  -> %s'
              % ('', d, str(v1(built, M.LEINTH_CHESTS[d], 'tables')).rsplit('\\', 1)[-1]))
    print('\n  orb05 carriers in the built db: %d'
          % len(consumers(built, M.ORB05)))
    for c in consumers(built, M.ORB05):
        print('    %s' % c)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
