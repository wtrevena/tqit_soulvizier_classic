r"""PROBE (read-only): what does a creature's ANIMATION TABLE bind per weapon class?

A TQ creature record's `charAnimationTableName` points at an AnimationTable
record (`...\ANM\ANM_<family>.dbr`) that binds the actual `.anm` clip for every
(weapon-class, action) pair. The creature record only OVERRIDES entries. So the
authority on "can this creature move/attack while holding weapon class X" is
the TABLE, not the creature record.

This prints, for every animation table named by `thrown_restore.ROSTER` (plus
any extra tables passed on the command line), how many `.anm` bindings exist per
weapon-class prefix and whether the movement + attack slots are bound.

Usage:
  py tools/debug/probe_anim_tables.py <base.arz> [<sv098i.arz>] [<mod.arz>]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # tools/
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "patches"))
from arz_patcher import ArzDatabase  # noqa: E402
import thrown_restore  # noqa: E402

PREFIXES = ["unarmed", "oneHanded", "dHanded", "bow", "spear", "staff",
            "rangedOneHand", "dualRanged"]
# slots that decide "can it move" and "can it attack"
MOVE = ["RunAnim", "WalkAnim"]
ATTACK = ["AttackAnim1", "AttackAnim2", "AttackAnim3"]
OTHER = ["IdleAnim1", "IdleAnim", "AttackIdleAnim", "DieAnim1", "SpawnAnim"]


def norm(s):
    return str(s).replace("/", "\\").lower()


def load(p):
    db = ArzDatabase.from_arz(Path(p))
    return db, {norm(n): n for n in db.record_names()}


def fields(pair, path):
    db, idx = pair
    real = idx.get(norm(path))
    return db.get_fields(real) if real else None


def val(ff, key):
    if ff is None:
        return None
    for k, tf in ff.items():
        if k.lower() == key.lower():
            v = tf.value
            if isinstance(v, list):
                v = v[0] if v else None
            return v
    return None


def anm_keys(ff, prefix):
    """field names under `prefix` whose value looks like a real .anm path"""
    out = []
    p = prefix.lower()
    for k, tf in (ff or {}).items():
        if not k.lower().startswith(p):
            continue
        v = tf.value
        if isinstance(v, list):
            v = v[0] if v else None
        if isinstance(v, str) and v.lower().endswith(".anm"):
            out.append(k)
    return sorted(out)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    dbs = [(Path(p).name, load(p)) for p in sys.argv[1:]]

    tables = []
    seen = set()
    for e in thrown_restore.ROSTER:
        ff = fields(dbs[0][1], e["record"])
        t = val(ff, "charAnimationTableName")
        if t and norm(t) not in seen:
            seen.add(norm(t))
            tables.append((t, e["family"]))

    for tbl, fam in tables:
        print("\n" + "=" * 90)
        print("%s   [%s]" % (tbl, fam))
        for label, pair in dbs:
            ff = fields(pair, tbl)
            if ff is None:
                print("  %-22s <table record ABSENT>" % label)
                continue
            print("  %-22s fields=%d" % (label, len(ff)))
            for p in PREFIXES:
                ks = anm_keys(ff, p)
                mv = [s for s in MOVE if val(ff, p + s)]
                at = [s for s in ATTACK if val(ff, p + s)]
                ot = [s for s in OTHER if val(ff, p + s)]
                verdict = "OK" if (mv and at) else (
                    "NO-ANM-AT-ALL" if not ks else
                    "NO-MOVE" if not mv else "NO-ATTACK")
                print("      %-16s bound_anms=%-4d move=%-18s attack=%-30s other=%-22s %s"
                      % (p, len(ks), ",".join(mv) or "-", ",".join(at) or "-",
                         ",".join(ot) or "-", verdict))


if __name__ == "__main__":
    main()
