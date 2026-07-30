r"""PROBE (read-only): the exact THROWN-STANCE gap between base TQAE and our build,
plus the SHARED-RECORD carrier census for every animation table involved.

Findings this probe is built to make reproducible (R-100 #15):
  * base TQAE animation tables BIND the thrown stance
    (`rangedOneHand*` for maenad/tigerman/machae, `dualRanged*` for duneraider);
  * SV 0.98i replaces those table records WHOLESALE with pre-thrown-weapon
    versions that bind ZERO thrown-stance clips;
  * our build inherits SV's, so a creature that equips a thrown weapon enters a
    stance with no run/walk/attack animation -> it can neither move nor attack.

Modes:
  --dump-block   emit the base thrown-stance block per table (name, dtype, value)
  --carriers     every record in the mod DB naming each table (SHARED-RECORD LAW)
  --anm-files    every distinct .anm path in the base thrown block (for arc check)

Usage:
  py tools/debug/probe_thrown_stance_gap.py <base.arz> <mod.arz> [modes...]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # tools/
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "patches"))
from arz_patcher import ArzDatabase  # noqa: E402
import thrown_restore  # noqa: E402

# stance prefix per animation table (which weapon-class block a thrown weapon
# selects: a single-hand thrower uses rangedOneHand, a dual thrower dualRanged).
DTYPE = {0: "INT", 1: "FLOAT", 2: "STRING", 3: "BOOL"}


def norm(s):
    return str(s).replace("/", "\\").lower()


def load(p):
    db = ArzDatabase.from_arz(Path(p))
    return db, {norm(n): n for n in db.record_names()}


def ff_of(pair, path):
    db, idx = pair
    real = idx.get(norm(path))
    return db.get_fields(real) if real else None


def val(ff, key):
    for k, tf in (ff or {}).items():
        if k.lower() == key.lower():
            v = tf.value
            return v[0] if isinstance(v, list) and v else v
    return None


def tables_and_stances(base):
    """[(table_path, stance_prefix, [roster records that use it])]"""
    out = []
    order = []
    for e in thrown_restore.ROSTER:
        ff = ff_of(base, e["record"])
        t = val(ff, "charAnimationTableName")
        stance = "dualRanged" if e["dual"] else "rangedOneHand"
        key = (norm(t), stance)
        for row in out:
            if (norm(row[0]), row[1]) == key:
                row[2].append(e["record"])
                break
        else:
            out.append([t, stance, [e["record"]]])
            order.append(key)
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    base = load(sys.argv[1])
    mod = load(sys.argv[2])
    modes = set(a for a in sys.argv[3:] if a.startswith("--")) or {
        "--dump-block", "--carriers", "--anm-files"}

    rows = tables_and_stances(base)
    anm_all = set()

    for tbl, stance, users in rows:
        bff = ff_of(base, tbl)
        mff = ff_of(mod, tbl)
        nb = sum(1 for k in (bff or {}) if k.lower().startswith(stance.lower()))
        nm = sum(1 for k in (mff or {}) if k.lower().startswith(stance.lower()))
        print("\n" + "=" * 92)
        print("TABLE %s   stance=%s" % (tbl, stance))
        print("  used by roster records: %s" % ", ".join(u.split("\\")[-1] for u in users))
        print("  base fields under stance: %d   mod fields under stance: %d" % (nb, nm))

        if "--dump-block" in modes and bff is not None:
            print("  --- BASE stance block (the data to restore) ---")
            for k, tf in bff.items():
                if not k.lower().startswith(stance.lower()):
                    continue
                v = tf.value
                print("    %-44s %-6s %r" % (k, DTYPE.get(tf.dtype, tf.dtype), v))
                if isinstance(v, str) and v.lower().endswith(".anm"):
                    anm_all.add(v)
                elif isinstance(v, list):
                    for x in v:
                        if isinstance(x, str) and x.lower().endswith(".anm"):
                            anm_all.add(x)

        if "--carriers" in modes:
            db, idx = mod
            carriers = []
            for n in db.record_names():
                v = db.get_field_value(n, "charAnimationTableName")
                if isinstance(v, list):
                    v = v[0] if v else None
                if v and norm(v) == norm(tbl):
                    carriers.append(n)
            print("  --- SHARED-RECORD carrier census (mod DB) ---")
            print("  carriers naming this table: %d" % len(carriers))
            tgt = set(norm(u) for u in users)
            non_target = [c for c in carriers if norm(c) not in tgt]
            print("  of which NON-TARGET carriers: %d" % len(non_target))
            for c in sorted(carriers):
                print("      %s%s" % (c, "   <== ROSTER TARGET" if norm(c) in tgt else ""))

    if "--anm-files" in modes:
        print("\n" + "=" * 92)
        print("DISTINCT .anm CLIPS REFERENCED BY THE BASE THROWN BLOCKS: %d" % len(anm_all))
        for a in sorted(anm_all):
            print("    %s" % a)


if __name__ == "__main__":
    main()
