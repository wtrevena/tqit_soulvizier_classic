r"""Planted negative test for the R-51 Sargoth Manbane leg of the SHARED summon
chain gate (`tools/patches/enslaver_pet_fx.py` `_CHAIN` / `_verify_chain`).

WHY HERE: R-51 is the same ruling class as R-43, so it was added to the EXISTING
chain-gate family rather than getting a bespoke gate (CLAUDE.md law #4 wants a
gate, not a gate SPRAWL). This script is the gate's proof-of-teeth for the new
leg: it breaks each link of
    soul item -> granted skill -> skill icon -> spawnObjects -> pet -> portrait
in memory, one at a time, and asserts `enslaver_pet_fx.verify()` FAILS on each,
then restores and asserts it passes again.

Usage:
    py tools/patches/_negtest_sargoth_chain.py <SoulvizierClassic.arz>

Exit 0 iff the gate is green on the unmodified arz AND fires on every planted
break. Requires an arz built WITH the sargoth_soul_summon module registered.
"""
import sys
import contextlib
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))
if str(_TOOLS / 'patches') not in sys.path:
    sys.path.insert(0, str(_TOOLS / 'patches'))

from arz_patcher import ArzDatabase           # noqa: E402
import enslaver_pet_fx as EPF                 # noqa: E402
import sargoth_soul_summon as SGS             # noqa: E402


def _gate_fails(db):
    """True iff the shared chain gate raises (i.e. catches the planted break)."""
    try:
        with contextlib.redirect_stdout(sys.stderr):
            EPF.verify(db, {})
        return False
    except SystemExit:
        return True


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    arz = Path(argv[0])
    print('=== R-51 Sargoth chain-gate negative test ===')
    print('arz: %s' % arz)
    with contextlib.redirect_stdout(sys.stderr):
        db = ArzDatabase.from_arz(arz)

    soul_n = SGS.SOULS[0]
    skill = SGS.SUMMON_SKILL
    pet_1 = SGS.PETS[0]

    # baseline: the gate must be GREEN before we break anything, or the test is
    # meaningless (a gate that is already red proves nothing).
    if _gate_fails(db):
        print('  BASELINE: gate ALREADY FAILING on the unmodified arz -> cannot '
              'run the negative test. Fix the build first.')
        return 1
    print('  BASELINE: chain gate green on the unmodified arz  OK')

    def plant(label, rec, field, bad):
        orig = db.get_field_value(rec, field)
        db.set_field(rec, field, bad)
        caught = _gate_fails(db)
        db.set_field(rec, field, orig if orig is not None else '')
        restored_ok = not _gate_fails(db)
        verdict = 'PASS' if (caught and restored_ok) else \
                  'FAIL(caught=%s,restored=%s)' % (caught, restored_ok)
        print('  %-46s %s' % (label, verdict))
        return caught and restored_ok

    results = [
        # link 1: the soul item stops granting the summon
        plant('soul item -> skill (itemSkillName cleared)',
              soul_n, 'itemSkillName', ''),
        # link 2: the soul grants some OTHER summon (cross-wire)
        plant('soul item -> skill (cross-wired to summon_vort)',
              soul_n, 'itemSkillName',
              r'records\skills\soulskills\summon_vort.dbr'),
        # link 3: the skill icon regresses (b40 class)
        plant('skill -> icon (Lyia nymph icon planted)',
              skill, 'skillUpBitmapName',
              r'DRXtextures\skill icons\soul\summonlyiaup.tex'),
        # link 4: spawnObjects no longer points at the Sargoth pets
        plant('skill -> spawnObjects (repointed to vort pets)',
              skill, 'spawnObjects',
              [r'records\skills\soulskills\pets\vort_%d.dbr' % i for i in (1, 2, 3)]),
        # link 5: the pet-bar portrait regresses to Lyia (b71 class)
        plant('pet -> portrait (Lyia party portrait planted)',
              pet_1, 'StatusIcon',
              r'DRXtextures\skill icons\soul\lyia_party_up.tex'),
        # link 6: pet identity/race regresses (b81 class, R-11)
        plant('pet -> race (Beastman -> Undead)',
              pet_1, 'characterRacialProfile', 'Undead'),
    ]

    ok = all(results)
    print('ALL PASS' if ok else 'SOME FAILED')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
