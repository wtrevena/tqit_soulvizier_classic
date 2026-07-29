#!/usr/bin/env python3
"""Negative + positive tests for the B100 weapon/hand gate honesty gate
(tools/patches/weapon_gate_truth.py verify() = the DB half, and
tools/validate_weapon_gate_text.py = the Text half).

The gate exists to make a future edit to ONE side of the tooltip<->gating-field
pair red the build. These subtests prove it actually fires, in both directions.

DB HALF
  POSITIVE 1  real shipped arz AFTER apply()                      -> verify PASS
  POSITIVE 2  apply() is idempotent (run twice)                   -> verify PASS
  NEGATIVE 1  drop dualWieldOnly on Blade Mastery (mechanics moved
              without the text)                                   -> verify FAIL
  NEGATIVE 2  add Mace to Blade Mastery's qualifying weapons       -> verify FAIL
  NEGATIVE 3  repoint Parry back onto the shared base tag          -> verify FAIL
  NEGATIVE 4  plant a NEW player-surface skill with dualWieldOnly=1
              that is neither contracted nor waived                -> verify FAIL
  NEGATIVE 5  raw pre-fix arz (Parry still on the shared tag)      -> verify FAIL

TEXT HALF (needs a built Text.arc; skipped with a loud note if absent)
  POSITIVE 3  shipped arz + shipped Text.arc                       -> validate PASS
  NEGATIVE 6  a Text.arc whose tagBladeMasteryDESC has the dual-wield
              clause stripped (text edited without the record)     -> validate FAIL
  NEGATIVE 7  same, weapon-class clause stripped                   -> validate FAIL

Usage:
    py tools/debug/negtest_weapon_gate_truth.py [<built.arz>] [<built Text.arc>]
Exit 0 = every subtest behaved as specified.
"""
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))              # tools/
sys.path.insert(0, str(HERE.parent / 'patches'))  # tools/patches/

from arz_patcher import ArzDatabase              # noqa: E402
from arc_patcher import ArcArchive               # noqa: E402
import weapon_gate_truth as WGT                  # noqa: E402
import validate_weapon_gate_text as VWG          # noqa: E402

REPO = HERE.parents[1]
DEFAULT_ARZ = REPO / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'
DEFAULT_TEXT = REPO / 'work' / 'SoulvizierClassic' / 'Resources' / 'Text.arc'


def run_verify(db):
    try:
        WGT.verify(db, {})
        return 'PASS'
    except SystemExit:
        return 'FAIL'


def fresh(arz, applied=True):
    db = ArzDatabase.from_arz(Path(arz))
    if applied:
        WGT.apply(db, {})
    return db


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_ARZ)
    text = sys.argv[2] if len(sys.argv) > 2 else str(DEFAULT_TEXT)
    if not Path(arz).exists():
        print(f"ERROR: no arz at {arz}")
        return 2
    results = []

    # ── DB half ────────────────────────────────────────────────────────────
    db = fresh(arz)
    results.append(('positive 1 (shipped arz, post-apply)', run_verify(db), 'PASS'))

    db2 = fresh(arz)
    WGT.apply(db2, {})          # second apply -> must be a no-op
    results.append(('positive 2 (apply idempotent)', run_verify(db2), 'PASS'))

    db3 = fresh(arz)
    db3.set_field(WGT.BLADE_MASTERY, 'dualWieldOnly', 0)
    results.append(('negative 1 (dualWieldOnly dropped)', run_verify(db3), 'FAIL'))

    db4 = fresh(arz)
    db4.set_field(WGT.BLADE_MASTERY, 'Mace', 1)
    results.append(('negative 2 (Mace added to the gate)', run_verify(db4), 'FAIL'))

    db5 = fresh(arz)
    db5.set_field(WGT.PARRY, 'skillBaseDescription', WGT.PARRY_SHARED_TAG)
    results.append(('negative 3 (Parry back on the shared tag)',
                    run_verify(db5), 'FAIL'))

    # negative 4: plant a stray. Reuse a real player-surface record so the
    # sweep's "is it on the player surface" test is genuinely exercised: the
    # Occult tree's own Nether Strike sits in a UI slot and carries no dual gate.
    db6 = fresh(arz)
    surface = sorted(WGT.player_surface_skills(db6) | WGT.tree_listed_skills(db6))
    victim = next((r for r in surface
                   if db6.has_record(r)
                   and r.lower() not in {x.lower() for x in WGT.CONTRACT}
                   and r.lower() not in {x.lower() for x in WGT.DUAL_WIELD_SWEEP_WAIVERS}
                   and not WGT._flag(db6, r, 'dualWieldOnly')
                   and isinstance(WGT._get_field(db6, r, 'Class'), str)
                   and str(WGT._get_field(db6, r, 'Class')).startswith('Skill')), None)
    if victim is None:
        results.append(('negative 4 (planted stray dual-wield skill)',
                        'SKIPPED (no victim record found)', 'FAIL'))
    else:
        db6.set_field(victim, 'dualWieldOnly', 1)
        print(f"  [negtest] planted dualWieldOnly=1 on {victim}")
        results.append(('negative 4 (planted stray dual-wield skill)',
                        run_verify(db6), 'FAIL'))

    db7 = ArzDatabase.from_arz(Path(arz))   # RAW, no apply()
    raw_tag = WGT._get_field(db7, WGT.PARRY, 'skillBaseDescription')
    if raw_tag == WGT.PARRY_SHARED_TAG:
        results.append(('negative 5 (raw pre-fix arz)', run_verify(db7), 'FAIL'))
    else:
        print(f"  NOTE: input arz already carries the fix (Parry desc = "
              f"{raw_tag!r}); negative-5 not exercisable against this input, "
              f"SKIPPED.")

    # ── Text half ──────────────────────────────────────────────────────────
    if not Path(text).exists():
        print(f"  NOTE: no Text.arc at {text}; the TEXT-half subtests "
              f"(positive 3, negatives 6-7) are SKIPPED. Build Text.arc and "
              f"re-run for full coverage.")
    else:
        results.append(('positive 3 (shipped arz + shipped Text.arc)',
                        'PASS' if VWG.validate(arz, text) == 0 else 'FAIL', 'PASS'))
        tmp = Path(tempfile.mkdtemp(prefix='b100_negtest_'))
        try:
            for label, clause, name in (
                    ('negative 6 (dual-wield clause stripped from the text)',
                     WGT.CLAUSE_DUAL_WIELD, 'no_dual.arc'),
                    ('negative 7 (weapon-class clause stripped from the text)',
                     WGT.CLAUSE_SWORD_OR_AXE, 'no_weapons.arc')):
                dst = tmp / name
                shutil.copyfile(text, dst)
                arc = ArcArchive.from_file(dst)
                body = arc.get_text('modstrings.txt')
                if clause not in body:
                    print(f"  NOTE: clause {clause!r} not present in the built "
                          f"Text.arc; {label} not exercisable, SKIPPED.")
                    continue
                arc.set_text('modstrings.txt', body.replace(clause, ''))
                arc.write(dst)
                results.append((label,
                                'PASS' if VWG.validate(arz, str(dst)) == 0 else 'FAIL',
                                'FAIL'))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 72)
    bad = 0
    for name, got, want in results:
        ok = (got == want)
        bad += (not ok)
        print(f"  [{'ok ' if ok else 'BAD'}] {name}: got {got}, expected {want}")
    print("=" * 72)
    if bad:
        print(f"NEGTEST FAILED: {bad} subtest(s) did not behave as specified - "
              f"the B100 gate does not actually guard what it claims to.")
        return 1
    print(f"NEGTEST OK: all {len(results)} subtests behaved as specified.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
