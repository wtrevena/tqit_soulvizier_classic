r"""negtest_gate_amendments - the R-240/R-241 gate AMENDMENTS still catch drift.

WHY THIS FILE EXISTS
---------------------
R-240/R-241 amended two pre-existing registry gates that would otherwise have aborted
the build on this lane's own output:

  * `polis_vault.verify` T5 - asserted the shipped literal multiplier with the message
    "payout must never shrink". R-240 IS the authorised shrink.
  * `uber_apex_orb.verify` (c) + (h) - proved the apex calibre >= Leinth's frozen b96
    tables, in TWO independent copies. R-240 lowers the shared calibre ~10x and R-241
    demotes loot4Chance 100 -> 21.2.

An amendment that quietly turns a gate into a no-op is worse than the collision it
resolves, because the build goes green and nobody looks again. `NO NEW SURFACE WITHOUT
A GATE` cuts both ways: a gate that CHANGES has to re-earn its teeth. So every clause
of both amended checks is planted against here, in BOTH eras, and a negtest that fails
to red is itself a failure.

  py tools/debug/negtest_gate_amendments.py <arz>

Exit 0 == every planted defect was caught. Exit 1 == a gate slept through one.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
for _p in (str(_TOOLS), str(_TOOLS / 'patches')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from arz_patcher import ArzDatabase           # noqa: E402
import svc_loot_breadth as SLB                # noqa: E402
import svc_loot_volume as SLV                 # noqa: E402
import svc_orb_legendary as SOL               # noqa: E402
import patches.polis_vault as PV              # noqa: E402
import patches.uber_apex_orb as UAO           # noqa: E402


def _fv(db, rec, field):
    v = db.get_field_value(rec, field)
    return v[0] if isinstance(v, list) and v else v


def _set(db, rec, field, val):
    db.set_field(rec, field, val)
    db._modified.add(rec)


class Plant(object):
    """Set fields, run a gate, expect it to RED, then put everything back.

    Restores from the values read at __enter__, so a planted defect can never leak
    into the next case - the failure mode that makes a negative battery lie."""

    def __init__(self, db, edits):
        self.db, self.edits, self.saved = db, edits, []

    def __enter__(self):
        for rec, field, val in self.edits:
            self.saved.append((rec, field, _fv(self.db, rec, field)))
            _set(self.db, rec, field, val)
        return self

    def __exit__(self, *exc):
        for rec, field, val in reversed(self.saved):
            _set(self.db, rec, field, val)
        return False


def _reds(gate, db):
    """(did_it_red, message). Swallows the gate's own stdout noise."""
    import io
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            gate(db, {})
        return False, 'gate PASSED (it should have failed)'
    except SystemExit as exc:
        return True, str(exc).replace('\n', ' | ')[:220]
    except Exception as exc:                    # a crash is not a catch
        return False, 'gate CRASHED: %s: %s' % (type(exc).__name__, exc)


def main(argv):
    if len(argv) < 2:
        print("usage: py tools/debug/negtest_gate_amendments.py <arz>")
        return 2
    db = ArzDatabase.from_arz(Path(argv[1]))

    # Bring the db to the POST-wave era, which is the era the amendments added and
    # therefore the era most of these plants have to be judged in.
    lk = SLB.Lookup(db)
    if not SLV.already_applied(db, lk):
        SLV.apply_wave(db, lk, verbose=False)
        lk.refresh()
        SOL.apply_wave(db, lk, verbose=False)
        lk.refresh()

    cage = SLV.canon_cage_table('01', 'l', 'a')
    cage_b = SLV.canon_cage_table('01', 'l', 'b')
    cage_real = lk.real(cage) or cage
    cage_b_real = lk.real(cage_b) or cage_b
    apex_n = UAO.CHAIN['normal'][5]
    apex_l = UAO.CHAIN['legendary'][5]
    leinth_chest_n = UAO.LEINTH_CHESTS['normal']

    # The pre-R-240 equation for a cage table, rebuilt through the same transform the
    # gate uses, so "revert this one variant" means exactly what the gate calls
    # pre-R-240 and the negtest cannot drift away from the gate it is testing.
    _br = SLV.parse_eq(_fv(db, cage_real, 'numSpawnMinEquation'))[0]
    pre_min = SLV.format_eq(_br, 2.4)
    pre_max = SLV.format_eq(_br, 2.8)

    _abr = SLV.parse_eq(_fv(db, apex_n, 'numSpawnMinEquation'))[0]
    apex_pre_min = SLV.format_eq(_abr, UAO.LEINTH_MIN_MULT)
    apex_pre_max = SLV.format_eq(_abr, UAO.LEINTH_MAX_MULT)

    cases = [
        # ── polis_vault T5 / T5b ─────────────────────────────────────────────
        ('N1 T5  a cage table at a THIRD multiplier (neither era)',
         PV.verify, [(cage_real, 'numSpawnMinEquation', SLV.format_eq(_br, 0.9))]),
        ('N2 T5  a cage table trimmed BELOW the committed value (silent starve)',
         PV.verify, [(cage_real, 'numSpawnMinEquation', SLV.format_eq(_br, 0.05)),
                     (cage_real, 'numSpawnMaxEquation', SLV.format_eq(_br, 0.06))]),
        ('N3 T5  a cage table re-INFLATED past its era (the trim undone on one row)',
         PV.verify, [(cage_real, 'numSpawnMinEquation', SLV.format_eq(_br, 12.0)),
                     (cage_real, 'numSpawnMaxEquation', SLV.format_eq(_br, 14.0))]),
        ('N4 T5b HALF-TRIMMED cage: variant b reverted to pre-R-240, a/c trimmed',
         PV.verify, [(cage_b_real, 'numSpawnMinEquation', pre_min),
                     (cage_b_real, 'numSpawnMaxEquation', pre_max)]),
        ('N5 T5  an unparseable spawn equation is NOT waved through',
         PV.verify, [(cage_real, 'numSpawnMinEquation', '7')]),

        # ── uber_apex_orb (c) + (h) ──────────────────────────────────────────
        ('N6 (c)/(h) an apex table at a THIRD calibre (neither era)',
         UAO.verify, [(apex_l, 'numSpawnMinEquation', SLV.format_eq(_abr, 0.9)),
                      (apex_l, 'numSpawnMaxEquation', SLV.format_eq(_abr, 1.1))]),
        ('N7 (c)/(h) the R-241 demoted row drifts back UP toward the guarantee',
         UAO.verify, [(apex_n, 'loot4Chance', 100.0)]),
        ('N8 (c)/(h) the R-241 demoted row is cut FURTHER by an unmeasured lane',
         UAO.verify, [(apex_n, 'loot4Chance', 2.0)]),
        ('N9 (h) P1 gold nerfed - an axis NEITHER ruling authorised',
         UAO.verify, [(apex_l, 'goldGeneratorLevel', 1.0)]),
        ('N10 (h) P2 a NON-demoted group chance below Leinth\'s original floor',
         UAO.verify, [(apex_l, 'loot1Chance', 0.5)]),
        ('N11 (h) P3 UNITY broken - Leinth repointed off the shared apex table',
         UAO.verify, [(leinth_chest_n, 'tables', UAO.LEINTH_TABLES_BY_DIFF['normal'])]),
        ('N12 era-MIX - Normal reverted to pre-R-240, Epic/Legendary trimmed',
         UAO.verify, [(apex_n, 'numSpawnMinEquation', apex_pre_min),
                      (apex_n, 'numSpawnMaxEquation', apex_pre_max)]),
    ]

    print("\n=== negtest: the R-240/R-241 gate amendments (%d plants) ===" % len(cases))
    bad = []
    for label, gate, edits in cases:
        with Plant(db, edits):
            red, msg = _reds(gate, db)
        print("  %-5s %-68s %s" % ('RED' if red else 'MISS', label, msg[:110]))
        if not red:
            bad.append(label)

    # The battery is only meaningful if the db is CLEAN between plants, so prove the
    # restore actually restores rather than assuming it: both gates must be green now.
    for name, gate in (('polis_vault', PV.verify), ('uber_apex_orb', UAO.verify)):
        red, msg = _reds(gate, db)
        if red:
            bad.append('RESTORE LEAKED: %s still reds after every plant was undone '
                       '(%s)' % (name, msg))
            print("  MISS  RESTORE LEAKED on %s: %s" % (name, msg[:140]))
        else:
            print("  OK    restore clean: %s green again after all plants" % name)

    if bad:
        print("\nNEGTEST FAILED: %d case(s) the amended gates slept through:" % len(bad))
        for b in bad:
            print("  - %s" % b)
        return 1
    print("\nNEGTEST PASS: every planted defect was caught, in both directions, and "
          "the amendments left no clause toothless.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
