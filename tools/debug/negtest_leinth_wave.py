#!/usr/bin/env python3
r"""Planted negative + positive tests for the b94 PART B gate
(tools/patches/leinth_wave.py :: verify).

POSITIVE 1: the real built .arz must PASS.
NEGATIVE 1: her physical resist reverted to the old 10 must FAIL (the real lever).
NEGATIVE 2: her poison weakness "fixed" to 0 must FAIL (identity law).
NEGATIVE 3: a new skill dropped to level 0 must FAIL (level-0 never fires).
NEGATIVE 4: Crimson Tithe unwired from specialAttack5 must FAIL (never cast).
NEGATIVE 5: the Choir summon's TTL removed must FAIL (b76 chumbi-freeze law).
NEGATIVE 6: her guaranteed veil drop cut must FAIL (drop wiring must not move).
NEGATIVE 7: her bespoke chest proxy repointed must FAIL (no nerf, no repoint).
NEGATIVE 8: the ugly-summon petLimit back at 16 must FAIL (density law).
NEGATIVE 9: her physical resist pushed ABOVE the Enslaver's must FAIL (ordering).
NEGATIVE 10: her charLevel pushed to uber tier must FAIL (she is not an uber).

Usage: py tools/debug/negtest_leinth_wave.py [<built.arz>]
Exit 0 = every subtest behaves as specified.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))                 # tools/
from arz_patcher import ArzDatabase                  # noqa: E402
from patches import leinth_wave as M                 # noqa: E402


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        str(HERE.parents[1] / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
    p = Path(arz)
    if not p.exists():
        print(f'ERROR: arz not found: {arz}')
        return 2
    db = ArzDatabase.from_arz(p)
    tags = dict(M.TAGS)

    def run_gate():
        try:
            M.verify(db, tags)
            return 'PASS'
        except SystemExit:
            return 'FAIL'

    results = []

    def sub(label, rec, field, value, want='FAIL'):
        saved = db.get_field_value(rec, field)
        db.set_field(rec, field, value)
        got = run_gate()
        db.set_field(rec, field, saved)
        results.append((label, got, want))

    V0, V1, V2 = M.VARIANTS

    results.append(('positive 1 (real built arz)', run_gate(), 'PASS'))

    sub('negative 1 (defensivePhysical reverted to 10)', V0, 'defensivePhysical', 10.0)
    sub('negative 2 (poison weakness "fixed" to 0)', V0, 'defensivePoison', 0.0)
    sub('negative 3 (Crimson Tithe dropped to level 0)',
        V1, 'skillLevel%d' % M.TITHE_SLOT, [0, 0, 0])
    sub('negative 4 (Crimson Tithe unwired from specialAttack5)',
        V2, 'specialAttack%sSkillName' % M.TITHE_SPECIAL, '')
    sub('negative 5 (Choir summon TTL removed - b76 law)',
        M.CHOIR, 'spawnObjectsTimeToLive', 0.0)
    sub('negative 6 (guaranteed veil drop cut to 50%)', V0, 'chanceToEquipHead', 50.0)
    sub('negative 7 (her bespoke chest proxy repointed)',
        V1, 'treasureProxyName', r'records\item\containers\new\genericbossorb_04.dbr')
    sub('negative 8 (ugly-summon petLimit back at 16)', M.UGLIES, 'petLimit', 16)
    sub('negative 9 (physical resist pushed above the Enslaver\'s)',
        V0, 'defensivePhysical', 99.0)
    sub('negative 10 (charLevel pushed to uber tier)', V2, 'charLevel', [100, 100, 100])

    results.append(('positive 2 (all mutations restored)', run_gate(), 'PASS'))

    ok = 0
    print()
    for label, got, want in results:
        good = got == want
        ok += good
        print(f'  [{"PASS" if good else "FAIL"}] {label}: gate={got} (expected {want})')
    print(f'\n{ok}/{len(results)} subtests behaved as specified')
    return 0 if ok == len(results) else 1


if __name__ == '__main__':
    sys.exit(main())
