"""negtest_gaoler_chests.py - PLANTED NEGATIVES for the R-100 #17 Gaoler gate.

Proves tools/patches/polis_vault.verify() actually fires. Each case breaks ONE
invariant on a fresh in-memory copy of a real built arz and asserts the gate
raises; the positive control asserts the unmodified build passes.

Usage: py tools/debug/negtest_gaoler_chests.py <built.arz>
Exit 0 = every negative fired and the control passed.
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_TOOLS))
sys.path.insert(0, str(_TOOLS / 'patches'))
from arz_patcher import ArzDatabase
import polis_vault as pv


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
    print("%s POSITIVE CONTROL: unmodified build passes the gate"
          % ('OK ' if ok else 'XX '))
    if not ok:
        fails.append('positive control failed')

    def check(label, mutate):
        d = load(arz)
        mutate(d)
        hit = fires(d)
        if not hit:
            fails.append(label)
        print("%s %-62s -> %s" % ('OK ' if hit else 'XX ', label,
                                  'RED (correct)' if hit else 'GREEN (BLIND)'))

    # T2 - the exact shipped defect: a normal-tier relic table back in a chest
    check("T2 normal-tier relic table (01_act4_relics) back in a vault chest",
          lambda d: d.set_field(pv._CHEST_LOOT[1], 'loot3Name2', pv._GUAR_RELIC_WRONG))
    # T2 - the same defect on the unique-weapon slot
    check("T2 normal-tier unique table (unique_1h_n01) back in a vault chest",
          lambda d: d.set_field(pv._CHEST_LOOT[0], 'loot3Name1', pv._GUAR_UNIQUE_WRONG))
    # T4 - the guaranteed slot silently switched off
    check("T4 the guaranteed slot turned off (loot3Chance 100 -> 0)",
          lambda d: d.set_field(pv._CHEST_LOOT[2], 'loot3Chance', 0.0))
    # T3 - a chest repointed away from its own table (collapses 5 rolls into 1)
    check("T3 a chest repointed at another chest's loot table",
          lambda d: d.set_field(pv._CHEST[3], 'tables', pv._CHEST_LOOT[0]))

    # T5 - the map half: the halved placement list quietly grown back
    import build_section_surgery as bss
    _saved = list(bss.B41_SPECS[bss.B41_POLIS_KEY])
    try:
        bss.B41_SPECS[bss.B41_POLIS_KEY] = _saved + [
            (b'records\\drxitem\\container\\svc_polisvault_chest_05.dbr',
             78.8, 3.6, 32.6, {})]
        d = load(arz)
        hit = fires(d)
        if not hit:
            fails.append('T5 placement count')
        print("%s %-62s -> %s"
              % ('OK ' if hit else 'XX ',
                 'T5 a 3rd chest placement added back to the halved map list',
                 'RED (correct)' if hit else 'GREEN (BLIND)'))
    finally:
        bss.B41_SPECS[bss.B41_POLIS_KEY] = _saved
    # T5 positive control the other way: with the list restored the gate is green
    d = load(arz)
    ok2 = not fires(d)
    if not ok2:
        fails.append('T5 restore control')
    print("%s %-62s -> %s"
          % ('OK ' if ok2 else 'XX ',
             'T5 control: restored 2-chest list is accepted',
             'GREEN (correct)' if ok2 else 'RED (false positive)'))

    print()
    if fails:
        print("NEGTEST FAILED: %d" % len(fails))
        for f in fails:
            print("   - %s" % f)
        return 1
    print("NEGTEST PASS: every planted violation reds the Gaoler gate and the "
          "unmodified build is green.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
