r"""GATE (R-260): every re-homed drop is MEASURED at its intended rate on a declared slot.

For each of the 31 roster records in `tools/svc_loot_slots.ROSTER` (the 32 build102
`Misc4` carriers minus the withheld Devourer) the gate re-derives, from the final bytes,

        measured % = chanceToEquip<S> x weight(row) / sum(weights of the slot's rows)

summed over every real slot/row that names the item, and FAILS on any mismatch with the
intended % (100 for the guaranteed six, 7-10 for the 25 relic sources), on a wrong
slot/row, on a competing live row beside a guaranteed one, on a skewed pre-existing row
beside a shared one, on `dropItems` off, or on a phantom field. The withheld Devourer
channel must stay withheld (no phantom, no reference to the master, master still present)
and his Finger2 + Misc1 must be exactly R-258's (the BL-R258-DEBT-1 freeze).

    py tools/gate_guaranteed_drops_measured.py [arz]                 # exit 1 on any mismatch
    py tools/gate_guaranteed_drops_measured.py [arz] --control <arz> # ALSO prove the control arz
                                                                     # (build102) REDs on all 31
    py tools/gate_guaranteed_drops_measured.py [arz] --negtest       # planted negatives, in memory
    py tools/gate_guaranteed_drops_measured.py [arz] --table         # print the rewire table

ANTI-INERT: on the shipped build102 arz `7dad9a8ad377ff9a65d17c144a57dde3` every roster
record measures 0.0000% - the item rides the phantom `Misc4` and no declared slot - so
`--control` demands 31 of 31 RED there and exits 1 otherwise. In-build twin:
`tools/patches/phantom_loot_slots.verify` arm B; the post-write battery in
`tools/build_svc_database.py` calls `validate()` below on the written artifact.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from arz_patcher import ArzDatabase          # noqa: E402
import svc_loot_slots as SLS                  # noqa: E402

DEFAULT_ARZ = HERE.parent / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'


def problems_for(db):
    return (['B ' + p for p in SLS.check_roster(db)]
            + ['F ' + p for p in SLS.check_devourer_freeze(db)])


def table(db):
    """[(label, record, intended, measured, slot/row it rides)] for the roster."""
    out = []
    for e in SLS.ROSTER:
        rec = SLS.resolve(db, e['record'])
        if rec is None:
            out.append((e['label'], SLS.short(e['record']), e['pct'], None, 'MISSING'))
            continue
        shares = SLS.item_shares(db, rec, e['tables'])
        out.append((e['label'], SLS.short(e['record']), e['pct'],
                    sum(p for _s, _r, p in shares),
                    ','.join('%s row %d' % (s, r) for s, r, _p in shares) or 'no declared slot'))
    return out


def print_table(db, title):
    print("  %s" % title)
    print("  %-28s %-30s %9s %10s  %s" % ('item', 'record', 'intended', 'measured', 'rides'))
    for lab, rec, want, got, rides in table(db):
        print("  %-28s %-30s %8g%% %9s  %s"
              % (lab, rec, want, ('%.4f%%' % got) if got is not None else '-', rides))


def validate(arz_path):
    """Builder entry point: 0 = PASS, 1 = FAIL, 2 = cannot run."""
    arz = Path(arz_path)
    if not arz.exists():
        print("gate_guaranteed_drops_measured: arz not found: %s" % arz)
        return 2
    db = ArzDatabase.from_arz(arz)
    P = problems_for(db)
    if P:
        for p in P[:60]:
            print("  R-260 OFFENDER: %s" % p)
        print("gate_guaranteed_drops_measured: FAIL (%d problem(s))" % len(P))
        return 1
    print("gate_guaranteed_drops_measured: PASS - %d roster records deliver at their intended "
          "MEASURED rate on a declared slot; the Devourer's channel is withheld with no phantom "
          "field and his Finger2 + Misc1 are R-258's" % len(SLS.ROSTER))
    return 0


def control(arz_path):
    """The anti-inert half: the pre-R-260 arz must measure 0 on EVERY roster record."""
    db = ArzDatabase.from_arz(Path(arz_path))
    rows = table(db)
    zero = [r for r in rows if r[3] is not None and SLS.close(r[3], 0.0)]
    print_table(db, "CONTROL (expected: every row measures 0.0000%% and rides no declared slot)")
    if len(zero) == len(rows) and problems_for(db):
        print("gate_guaranteed_drops_measured: ANTI-INERT CONTROL OK - %d/%d roster records "
              "measure 0.0000%% on the control arz (they ride the phantom Misc4), and the "
              "gate is RED there" % (len(zero), len(rows)))
        return 0
    print("gate_guaranteed_drops_measured: ANTI-INERT CONTROL FAILED - %d/%d measure 0 "
          "(gate red: %s)" % (len(zero), len(rows), bool(problems_for(db))))
    return 1


def negtest(arz_path):
    """Planted negatives on the REAL arz in memory (plus the stub battery of the module)."""
    db = ArzDatabase.from_arz(Path(arz_path))
    if problems_for(db):
        print("  negtest: the input arz is already RED; point it at a post-R-260 arz")
        return 1
    bad = 0
    from patches import phantom_loot_slots as PLS
    ens = SLS.resolve(db, PLS._entry('um_toxeus_enslaver_99.dbr')['record'])
    b05 = SLS.resolve(db, PLS._entry('ar_archer_05.dbr')['record'])
    plants = (
        ("the Enslaver's rite row weight zeroed", ens, 'chanceToEquipMisc1Item3', 0),
        ("a muted potion row un-muted beside the rite", ens, 'chanceToEquipMisc1Item1', 80),
        ("the Enslaver's slot chance halved", ens, 'chanceToEquipMisc1', 50.0),
        ("a shared slot's amulet row weight changed (skew)", b05, 'chanceToEquipMisc3Item1', 2500),
        ("a shared slot's chance moved", b05, 'chanceToEquipMisc3', 9.0),
        ("a phantom Misc4 grows back", ens, 'chanceToEquipMisc4', 100.0),
        ("the Devourer's R-258 chute diluted", SLS.resolve(db, SLS.DEVOURER), 'chanceToEquipMisc1Item1', 80),
    )
    for label, rec, field, value in plants:
        before = db.get_field_value(rec, field)
        db.set_field(rec, field, value)
        got = problems_for(db)
        if got:
            print("  negtest OK  (caught): %-52s -> %s" % (label, got[0][:80]))
        else:
            print("  negtest FAIL (MISSED): %s" % label)
            bad += 1
        if before is None:
            db.remove_field(rec, field)
        else:
            db.set_field(rec, field, before)
        if problems_for(db):
            print("  negtest FAIL: restoration after '%s' left the arz RED" % label)
            bad += 1
    if PLS._negtest() != 0:
        bad += 1
    print("negtest: %s" % ('PASS' if not bad else 'FAIL (%d)' % bad))
    return 1 if bad else 0


def main(argv):
    args = [a for a in argv[1:] if not a.startswith('--')]
    arz = args[0] if args else DEFAULT_ARZ
    if '--negtest' in argv:
        return negtest(arz)
    if '--table' in argv:
        db = ArzDatabase.from_arz(Path(arz))
        print_table(db, "REWIRE TABLE on %s" % arz)
        return 0
    rc = validate(arz)
    if '--control' in argv:
        ctl = argv[argv.index('--control') + 1]
        crc = control(ctl)
        return rc or crc
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv))
