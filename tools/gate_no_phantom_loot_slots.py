r"""GATE (R-260): no record in the arz carries an UNDECLARED loot-slot variable.

`characterloot.tpl` declares exactly eleven slot groups (Head Torso Forearm LowerBody
LeftHand RightHand Finger1 Finger2 Misc1 Misc2 Misc3). A `chanceToEquipMisc4*`,
`lootMisc4*` (.. Misc9), `chanceToEquipNeck*` or `lootNeck*` field is dead data the
engine never reads - and, from build36 to build102, the place where 32 of this mod's
drops (7 "guaranteed", 25 relic sources) quietly went to die. ZERO TOLERANCE.

    py tools/gate_no_phantom_loot_slots.py [arz]              # exit 1 on any carrier
    py tools/gate_no_phantom_loot_slots.py [arz] --negtest    # plant one in memory, prove RED
    py tools/gate_no_phantom_loot_slots.py [arz] --expect-fail  # anti-inert control on a
                                                                # pre-R-260 arz: exit 0 iff RED

ANTI-INERT: against the shipped build102 arz `7dad9a8ad377ff9a65d17c144a57dde3` this gate
EXITS 1 naming 35 carriers (32 lootMisc4 + the 3 EoAT disciples' chanceToEquipNeck).
In-build twin: `tools/patches/phantom_loot_slots.verify` arm A, and the post-write battery
in `tools/build_svc_database.py` calls `validate()` below on the written artifact.
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
    return SLS.check_no_phantom(db)


def validate(arz_path):
    """Builder entry point: 0 = PASS, 1 = FAIL, 2 = cannot run."""
    arz = Path(arz_path)
    if not arz.exists():
        print("gate_no_phantom_loot_slots: arz not found: %s" % arz)
        return 2
    db = ArzDatabase.from_arz(arz)
    P = problems_for(db)
    if P:
        for p in P[:60]:
            print("  R-260 OFFENDER: %s" % p)
        if len(P) > 60:
            print("  ... %d more" % (len(P) - 60))
        print("gate_no_phantom_loot_slots: FAIL (%d record(s) carry an undeclared loot-slot "
              "variable; the engine reads none of them)" % len(P))
        return 1
    print("gate_no_phantom_loot_slots: PASS - 0 of %d records carry any chanceToEquipMisc4..9* / "
          "lootMisc4..9* / chanceToEquipNeck* / lootNeck* field" % len(db.record_names()))
    return 0


def negtest(arz_path):
    db = ArzDatabase.from_arz(Path(arz_path))
    base = problems_for(db)
    if base:
        print("  negtest: the input arz is already RED (%d carrier(s)); planting on top of a "
              "red baseline proves nothing - point it at a post-R-260 arz" % len(base))
        return 1
    victim = next(n for n in db.record_names() if n.lower().endswith('um_toxeus_enslaver_99.dbr'))
    bad = 0
    for field, value in (('chanceToEquipMisc4', 100.0), ('lootMisc4Item1', ['a', 'b', 'c']),
                         ('chanceToEquipMisc6Item2', 100), ('chanceToEquipNeck', 0.0),
                         ('lootNeckItem1', ['a', 'b', 'c'])):
        db.set_field(victim, field, value)
        got = problems_for(db)
        if any(SLS.short(victim) in p for p in got):
            print("  negtest OK  (caught): planted %s on %s -> %s" % (field, SLS.short(victim), got[0][:80]))
        else:
            print("  negtest FAIL (MISSED): planted %s on %s" % (field, SLS.short(victim)))
            bad += 1
        db.remove_field(victim, field)
        if problems_for(db):
            print("  negtest FAIL: restoration left the arz RED")
            bad += 1
    print("negtest: %s" % ('PASS' if not bad else 'FAIL (%d)' % bad))
    return 1 if bad else 0


def main(argv):
    args = [a for a in argv[1:] if not a.startswith('--')]
    arz = args[0] if args else DEFAULT_ARZ
    if '--negtest' in argv:
        return negtest(arz)
    rc = validate(arz)
    if '--expect-fail' in argv:
        if rc == 1:
            print("gate_no_phantom_loot_slots: ANTI-INERT CONTROL OK - the pre-R-260 arz is RED "
                  "as it must be")
            return 0
        print("gate_no_phantom_loot_slots: ANTI-INERT CONTROL FAILED - expected RED on this arz "
              "(rc=%d)" % rc)
        return 1
    return rc


if __name__ == '__main__':
    sys.exit(main(sys.argv))
