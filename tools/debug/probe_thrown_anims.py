r"""PROBE (read-only, no build): why are the restored thrown-wielders FROZEN?

R-100 #15 - Will: the restored thrown-object monsters "spawn and they cant move
or attack or anything they are broken".

A TQ creature record carries ONE ANIMATION BLOCK PER WEAPON CLASS
(`bow*`, `oneHanded*`, `dHanded*`, `rangedOneHand*`, `dualRanged*`, `unarmed*`
...). The engine selects the block matching the weapon the creature actually
equips. If the creature equips a `WeaponHunting_RangedOneHand` (a thrown
weapon) but its record defines NO `rangedOneHand*` block - no run anim, no walk
anim, no attack anim - it has nothing to play and nothing to drive locomotion.

This probe prints, per roster record and per weapon-class prefix, how many anim
fields the record defines and which locomotion/attack anims resolve, on BOTH
the base-game record and the SV 0.98i overlay record (and the built mod arz if
given). It also resolves each record's `charAnimationTableName` and prints
which `.anm` files that table binds.

Usage:
  py tools/debug/probe_thrown_anims.py <base.arz> <sv098i.arz> [<mod.arz>]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # tools/
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "patches"))
from arz_patcher import ArzDatabase  # noqa: E402
import thrown_restore  # noqa: E402

# every weapon-class animation-block prefix a TQ creature record can carry.
PREFIXES = ["unarmed", "oneHanded", "dHanded", "bow", "spear", "staff",
            "rangedOneHand", "dualRanged", "shield", "dualWield"]
# the anim slots that decide whether a creature can MOVE and ATTACK at all.
CRITICAL = ["RunAnim", "WalkAnim", "AttackAnim1", "IdleAnim", "AttackIdleAnim"]


def norm(s):
    return str(s).replace("/", "\\").lower()


def load(p):
    db = ArzDatabase.from_arz(Path(p))
    return db, {norm(n): n for n in db.record_names()}


def fields(pair, path):
    if pair is None:
        return None
    db, idx = pair
    real = idx.get(norm(path))
    return db.get_fields(real) if real else None


def val(ff, key):
    if ff is None:
        return None
    for k, tf in ff.items():
        if k.lower() == key.lower():
            return tf.value
    return None


def count_prefix(ff, prefix):
    if ff is None:
        return 0
    p = prefix.lower()
    return sum(1 for k in ff if k.lower().startswith(p))


def block_report(ff, prefix):
    """(nfields, {critical slot -> value or None})"""
    got = {}
    for slot in CRITICAL:
        got[slot] = val(ff, prefix + slot)
    return count_prefix(ff, prefix), got


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    base = load(sys.argv[1])
    sv = load(sys.argv[2])
    mod = load(sys.argv[3]) if len(sys.argv) > 3 else None
    print("base   records: %d" % len(base[1]))
    print("sv098i records: %d" % len(sv[1]))
    if mod:
        print("mod    records: %d" % len(mod[1]))

    for e in thrown_restore.ROSTER:
        rec = e["record"]
        print("\n" + "=" * 90)
        print("%s   [%s / %s / dual=%s]" % (rec, e["family"], e["rank"], e["dual"]))
        for label, pair in (("base", base), ("sv098i", sv), ("mod", mod)):
            ff = fields(pair, rec)
            if ff is None:
                print("  %-7s <record absent>" % label)
                continue
            tbl = val(ff, "charAnimationTableName")
            print("  %-7s fields=%d  animTable=%s" % (label, len(ff), tbl))
            for p in PREFIXES:
                n, got = block_report(ff, p)
                if n == 0:
                    continue
                crit = " ".join(
                    "%s=%s" % (s, "MISSING" if got[s] is None else "ok")
                    for s in CRITICAL)
                print("      %-16s n=%-4d %s" % (p, n, crit))
            # what the record would actually equip
            print("      equip R=%s L=%s  lootR1=%s"
                  % (val(ff, "chanceToEquipRightHand"),
                     val(ff, "chanceToEquipLeftHand"),
                     (val(ff, "lootRightHandItem1") or [None])[0]
                     if isinstance(val(ff, "lootRightHandItem1"), list)
                     else val(ff, "lootRightHandItem1")))


if __name__ == "__main__":
    main()
