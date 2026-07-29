#!/usr/bin/env python3
r"""Planted negative + positive tests for the b94 PART B gate
(tools/patches/leinth_wave.py :: verify).

POSITIVE 1: the real built .arz must PASS.
NEGATIVE 1: her physical resist reverted to the old 10 must FAIL (the real lever).
NEGATIVE 2: her poison weakness restored to -15 must FAIL (Will Q6 removed it).
NEGATIVE 3: a new skill dropped to level 0 must FAIL (level-0 never fires).
NEGATIVE 4: the acid rig unwired from specialAttack5 must FAIL (never cast).
NEGATIVE 5: the guard's bloodbeast TTL removed must FAIL (b76 chumbi-freeze law).
NEGATIVE 6: her guaranteed veil drop cut must FAIL (drop wiring must not move).
NEGATIVE 7: her bespoke chest proxy repointed must FAIL (no nerf, no repoint).
NEGATIVE 8: the ugly-summon petLimit cut to 6 must FAIL (Will Q7 "keep as-is").
NEGATIVE 9: her physical resist pushed ABOVE the Enslaver's must FAIL (ordering).
NEGATIVE 10: her charLevel pushed to uber tier must FAIL (she is not an uber).

ROUND 3 additions (Will's 2026-07-27 answers):
NEGATIVE 11: poison pushed to full immunity must FAIL ("remove the weakness", not immunity).
NEGATIVE 12: the ugly swarm given a TTL must FAIL (Will Q7 "keep the swarm as-is").
NEGATIVE 13: her acid summon re-aimed at the XPACK puddle must FAIL (rig must be self-contained).
NEGATIVE 14: her acid puddle's aura reverted to the XPACK copy must FAIL (Will's 2nd rig dies).
NEGATIVE 15: the pool's proxyPoolEquation restored must FAIL (floors 3*1.357 -> TWO Leinths).
NEGATIVE 16: championMax raised to 3 must FAIL (spawnMax-championMax must be exactly 1).
NEGATIVE 17: a champion slot emptied must FAIL (the honour guard would be half-missing).
NEGATIVE 18: a guard demoted off Champion rank must FAIL (champion slots need champions).
NEGATIVE 19: a guard knocked off her level band must FAIL (free XP or a wall).
NEGATIVE 20: a guard's name tag stripped must FAIL (player-surface checklist).
NEGATIVE 21: a main name slot overwritten must FAIL (her 3-variant roll must survive).

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
    sub('negative 2 (poison weakness restored to -15)', V0, 'defensivePoison', -15.0)
    sub('negative 3 (Crimson Tithe dropped to level 0)',
        V1, 'skillLevel%d' % M.TITHE_SLOT, [0, 0, 0])
    sub('negative 4 (acid rig unwired from specialAttack5)',
        V2, 'specialAttack%sSkillName' % M.ACID_SPECIAL, '')
    sub('negative 5 (guard bloodbeast TTL removed - b76 law)',
        M.GUARD_BEAST_SKILL, 'spawnObjectsTimeToLive', 0.0)
    sub('negative 6 (guaranteed veil drop cut to 50%)', V0, 'chanceToEquipHead', 50.0)
    sub('negative 7 (her bespoke chest proxy repointed)',
        V1, 'treasureProxyName', r'records\item\containers\new\genericbossorb_04.dbr')
    sub('negative 8 (ugly-summon petLimit cut to 6 - Will said keep as-is)',
        M.UGLIES, 'petLimit', 6)
    sub('negative 9 (physical resist pushed above the Enslaver\'s)',
        V0, 'defensivePhysical', 99.0)
    sub('negative 10 (charLevel pushed to uber tier)', V2, 'charLevel', [100, 100, 100])

    # ── ROUND 3: Will's 2026-07-27 answers ──────────────────────────────────
    sub('negative 11 (poison pushed to full immunity)', V1, 'defensivePoison', 100.0)
    sub('negative 12 (ugly swarm given a TTL - Will said keep as-is)',
        M.UGLIES, 'spawnObjectsTimeToLive', 45.0)
    sub('negative 13 (acid summon re-aimed at the XPACK puddle)',
        M.ACID_SUMMON, 'spawnObjects', [M.ACID_XPACK_MONSTER])
    sub('negative 14 (acid puddle aura reverted to the XPACK copy)',
        M.ACID_MONSTER, 'skillName1', M.ACID_XPACK_ATTACK)
    sub('negative 15 (pool proxyPoolEquation restored -> TWO Leinths)',
        M.LEINTH_POOL, 'proxyPoolEquation', r'records\proxies orient\proxypoolequation_02.dbr')
    sub('negative 16 (championMax raised to 3 -> 0 mains)',
        M.LEINTH_POOL, 'championMax', 3)
    sub('negative 17 (a champion slot emptied)', M.LEINTH_POOL, 'nameChampion2', '')
    sub('negative 18 (a guard demoted off Champion rank)',
        M.GUARD_REAVER, 'monsterClassification', 'Common')
    sub('negative 19 (a guard knocked off her level band)',
        M.GUARD_DISCIPLE, 'charLevel', [12, 12, 12])
    sub('negative 20 (a guard\'s name tag stripped)',
        M.GUARD_REAVER, 'description', 'tagBWreaver')
    sub('negative 21 (a main name slot overwritten)',
        M.LEINTH_POOL, 'name2', M.GUARD_REAVER)

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
