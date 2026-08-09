"""negtest_gaoler_chests.py - PLANTED NEGATIVES for the Gaoler-vault difficulty
gate (Will 2026-08-08).

Proves tools/patches/polis_vault.verify() actually fires. Each case breaks ONE
difficulty-correctness invariant on a fresh in-memory copy of a real BUILT arz
(one whose vault loot tables already carry the [normal,epic,legendary] arrays)
and asserts the gate raises; the positive control asserts the unmodified build
passes.

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

_L01 = pv._CHEST_LOOT[0]      # polisvault_01.dbr
_L03 = pv._CHEST_LOOT[2]      # polisvault_03.dbr (the apex; has the guaranteed relic)
_LEG_RELIC = pv._DIFF_RELIC[2]                       # 03_act4_relics (legendary)
_LEG_UNIQUE = pv._DIFF_UNIQUE_1H[2]                  # unique_1h_l01 (legendary)


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
        print("%s %-64s -> %s" % ('OK ' if hit else 'XX ', label,
                                  'RED (correct)' if hit else 'GREEN (BLIND)'))

    # T2 - the exact shipped defect: a relic slot FLATTENED back to a scalar tier
    # (drops that one tier on every difficulty). Both directions of the leak:
    check("T2 guaranteed relic array flattened to scalar 03_act4_relics (legendary)",
          lambda d: d.set_field(_L03, 'loot3Name2', _LEG_RELIC))
    check("T2 the inherited relic slot flattened to scalar legendary",
          lambda d: d.set_field(_L01, 'loot4Name2', _LEG_RELIC))
    # T2 - a relic array present but in the WRONG game-mode order (legendary first ->
    # Incarnation on Normal, the exact over-tier Will is closing).
    check("T2 relic array reversed to [legendary, epic, normal] (wrong game order)",
          lambda d: d.set_field(_L03, 'loot4Name2', list(reversed(pv._DIFF_RELIC))))
    # T2 - a GEAR (unique-weapon) slot flattened to a scalar legendary tier.
    check("T2 gear (unique_1h) slot flattened to scalar legendary",
          lambda d: d.set_field(_L01, 'loot1Name3', _LEG_UNIQUE))
    # T4 - the guaranteed slot silently switched off.
    check("T4 the guaranteed slot turned off (loot3Chance 100 -> 0)",
          lambda d: d.set_field(_L03, 'loot3Chance', 0.0))
    # T3 - a chest repointed away from its own table (collapses independent rolls).
    check("T3 a chest repointed at another chest's loot table",
          lambda d: d.set_field(pv._CHEST[3], 'tables', _L01))

    # T5 - the map half: the halved placement list quietly grown back.
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
        print("%s %-64s -> %s"
              % ('OK ' if hit else 'XX ',
                 'T5 a 3rd chest placement added back to the halved map list',
                 'RED (correct)' if hit else 'GREEN (BLIND)'))
    finally:
        bss.B41_SPECS[bss.B41_POLIS_KEY] = _saved
    # T5 positive control the other way: with the list restored the gate is green.
    d = load(arz)
    ok2 = not fires(d)
    if not ok2:
        fails.append('T5 restore control')
    print("%s %-64s -> %s"
          % ('OK ' if ok2 else 'XX ',
             'T5 control: restored 2-chest list is accepted',
             'GREEN (correct)' if ok2 else 'RED (false positive)'))

    print()
    if fails:
        print("NEGTEST FAILED: %d" % len(fails))
        for f in fails:
            print("   - %s" % f)
        return 1
    print("NEGTEST PASS: every planted violation reds the Gaoler difficulty gate and "
          "the unmodified build is green.")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
