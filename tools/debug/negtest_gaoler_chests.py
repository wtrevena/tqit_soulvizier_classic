"""negtest_gaoler_chests.py - PLANTED NEGATIVES for the Gaoler-chest tiering gate.

Proves tools/patches/polis_vault.verify() actually fires after the Will 2026-08-08
conversion of svc_polisvault_chest_01 + _03 to per-difficulty Proxy chains. Each case
breaks ONE invariant on a fresh in-memory copy of a real BUILT arz (post-fix) and
asserts the gate raises; the positive control asserts the unmodified build passes.

Usage: py tools/debug/negtest_gaoler_chests.py <built.arz>   (a POST-FIX build)
Exit 0 = every negative fired and the positive control passed.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_TOOLS))
sys.path.insert(0, str(_TOOLS / 'patches'))
from arz_patcher import ArzDatabase
import polis_vault as pv

C = r'records\drxitem\container'
L = r'records\item\loottables\svc'
CHEST01 = rf'{C}\svc_polisvault_chest_01.dbr'
CHEST03 = rf'{C}\svc_polisvault_chest_03.dbr'
E_LOOT_03 = rf'{L}\polisvault_03_e.dbr'      # chest_03 Epic table (has a relic slot)
N_LOOT_01 = rf'{L}\polisvault_01_n.dbr'      # chest_01 Normal table
L_LOOT_03 = rf'{L}\polisvault_03.dbr'        # chest_03 byte-preserved Legendary table
POOL01_N = rf'{C}\svc_polisvault_pool_01_n.dbr'
CONT01_L = rf'{C}\svc_polisvault_chest_01_l.dbr'
NORMAL_RELIC = r'records\xpack\item\loottables\relics\01_act4_relics.dbr'
EPIC_UNIQUE = r'records\xpack\item\loottables\weapons\mastertables\unique_1h_e01.dbr'


def load(p):
    return ArzDatabase.from_arz(Path(p))


def fires(db):
    try:
        pv.verify(db, {})
        return False
    except SystemExit:
        return True


def main(argv):
    arz = argv[1]
    fails = []

    db = load(arz)
    ok = not fires(db)
    print("%s POSITIVE CONTROL: unmodified post-fix build passes the gate"
          % ('OK ' if ok else 'XX '))
    if not ok:
        fails.append('positive control failed')

    def check(label, mutate):
        d = load(arz)
        mutate(d)
        hit = fires(d)
        if not hit:
            fails.append(label)
        print("%s %-64s -> %s" % ('OK ' if hit else 'XX ', label,
                                  'RED (correct)' if hit else 'GREEN (BLIND)'))

    # T3 - the exact shipped defect class: a NORMAL relic on the EPIC branch
    #      (the "essence of ... on epic" bug, now on the general-guard pattern).
    check("T3 normal relic (01_act4_relics) planted on chest_03 Epic table",
          lambda d: d.set_field(E_LOOT_03, 'loot3Name2', NORMAL_RELIC))
    # T3 - an EPIC unique smuggled into the byte-preserved LEGENDARY table.
    check("T3 epic unique (unique_1h_e01) planted on chest_03 Legendary table",
          lambda d: d.set_field(L_LOOT_03, 'loot3Name1', EPIC_UNIQUE))
    # T3 - a Normal-branch pool repointed at the LEGENDARY container (Normal now
    #      spawns the legendary chest -> its 03/_l01 loot on Normal).
    check("T3 chest_01 Normal pool repointed at the Legendary container",
          lambda d: d.set_field(POOL01_N, 'fixedItemName1', CONT01_L))
    # T2 - a placed chest's Epic difficulty branch removed entirely.
    check("T2 chest_01 accessoryEpic1 slot cleared (no Epic branch)",
          lambda d: d.set_field(CHEST01, 'accessoryEpic1', ''))
    # T2 - a placed chest flattened back to a FixedItemContainer.
    check("T2 chest_01 Class flipped back to FixedItemContainer",
          lambda d: d.set_field(CHEST01, 'Class', 'FixedItemContainer'))
    # T4 - the guaranteed slot silently switched off on the Normal container's table.
    check("T4 chest_01 Normal table loot3Chance turned off (100 -> 0)",
          lambda d: d.set_field(N_LOOT_01, 'loot3Chance', 0.0))
    # T4 - the Boss lock stripped off a per-difficulty container (Gaoler unlock dies).
    check("T4 chest_03 Legendary container LockedClassification -> Champion",
          lambda d: d.set_field(rf'{C}\svc_polisvault_chest_03_l.dbr',
                                'LockedClassification', 'Champion'))

    # T6 - the map half: the halved placement list quietly grown back.
    import build_section_surgery as bss
    _saved = list(bss.B41_SPECS[bss.B41_POLIS_KEY])
    try:
        bss.B41_SPECS[bss.B41_POLIS_KEY] = _saved + [
            (b'records\\drxitem\\container\\svc_polisvault_chest_05.dbr',
             78.8, 3.6, 32.6, {})]
        d = load(arz)
        hit = fires(d)
        if not hit:
            fails.append('T6 placement count')
        print("%s %-64s -> %s"
              % ('OK ' if hit else 'XX ',
                 'T6 a 3rd chest placement added back to the halved map list',
                 'RED (correct)' if hit else 'GREEN (BLIND)'))
    finally:
        bss.B41_SPECS[bss.B41_POLIS_KEY] = _saved
    # T6 positive control the other way: with the list restored the gate is green
    d = load(arz)
    ok2 = not fires(d)
    if not ok2:
        fails.append('T6 restore control')
    print("%s %-64s -> %s"
          % ('OK ' if ok2 else 'XX ',
             'T6 control: restored 2-chest list is accepted',
             'GREEN (correct)' if ok2 else 'RED (false positive)'))

    print()
    if fails:
        print("NEGTEST FAILED: %d" % len(fails))
        for f in fails:
            print("   - %s" % f)
        return 1
    print("NEGTEST PASS: every planted violation reds the Gaoler tiering gate and "
          "the unmodified build is green.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
