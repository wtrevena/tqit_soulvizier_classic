r"""PROBE (read-only): is the CREATURE RECORD or the ANIMATION TABLE authoritative
for a stance's `.anm` bindings?

This decides where the R-100 #15 freeze fix has to be written, and it is decided
from SHIPPING base-game data rather than from belief:

  * TABLE-is-consulted is proven if a shipping, working base-game creature binds
    NO stance anms on its own record yet plays that stance (its table binds them).
  * RECORD-is-consulted is proven if shipping base-game creatures bind stance
    anms on the RECORD that their table does NOT bind (the record must be read,
    or those creatures would be frozen in that stance).

Reports the count and examples of each, over every Class=Monster record in the
base game, for every weapon-class stance.

Usage:
  py tools/debug/probe_anim_authority.py <base.arz>
"""
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # tools/
sys.path.insert(0, str(HERE))
from arz_patcher import ArzDatabase  # noqa: E402

PREFIXES = ["unarmed", "oneHanded", "dHanded", "bow", "spear", "staff",
            "rangedOneHand", "dualRanged"]
KEYSLOTS = ["RunAnim", "WalkAnim", "AttackAnim1"]


def norm(s):
    return str(s).replace("/", "\\").lower()


def scalar(v):
    return v[0] if isinstance(v, list) and v else v


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))
    idx = {norm(n): n for n in db.record_names()}

    def ff(p):
        r = idx.get(norm(p))
        return db.get_fields(r) if r else None

    def get(fields, key):
        for k, tf in (fields or {}).items():
            if k.lower() == key.lower():
                return scalar(tf.value)
        return None

    def bound(fields, prefix):
        """set of KEYSLOTS this field-map binds to a real .anm for `prefix`"""
        out = set()
        for s in KEYSLOTS:
            v = get(fields, prefix + s)
            if isinstance(v, str) and v.lower().endswith(".anm"):
                out.add(s)
        return out

    tbl_cache = {}

    def table_bound(tpath, prefix):
        k = (norm(tpath), prefix)
        if k not in tbl_cache:
            tbl_cache[k] = bound(ff(tpath), prefix)
        return tbl_cache[k]

    rec_only = defaultdict(list)   # prefix -> [(record, slots)]
    tbl_only = defaultdict(list)
    n_monsters = 0

    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        cls = get(fields, "Class")
        if cls != "Monster":
            continue
        n_monsters += 1
        tpath = get(fields, "charAnimationTableName")
        if not tpath:
            continue
        for p in PREFIXES:
            rb = bound(fields, p)
            tb = table_bound(tpath, p)
            only_r = rb - tb
            only_t = tb - rb
            if only_r:
                rec_only[p].append((name, sorted(only_r)))
            if only_t:
                tbl_only[p].append((name, sorted(only_t)))

    print("base Class=Monster records scanned: %d\n" % n_monsters)
    print("A) RECORD binds a key slot the TABLE does NOT  ->  the RECORD must be read")
    tot_r = 0
    for p in PREFIXES:
        rows = rec_only[p]
        tot_r += len(rows)
        print("   %-16s %d record(s)" % (p, len(rows)))
        for n, s in rows[:3]:
            print("        e.g. %s  %s" % (n, ",".join(s)))
    print("   TOTAL: %d\n" % tot_r)

    print("B) TABLE binds a key slot the RECORD does NOT  ->  the TABLE must be read")
    tot_t = 0
    for p in PREFIXES:
        rows = tbl_only[p]
        tot_t += len(rows)
        print("   %-16s %d record(s)" % (p, len(rows)))
        for n, s in rows[:3]:
            print("        e.g. %s  %s" % (n, ",".join(s)))
    print("   TOTAL: %d" % tot_t)

    print("\nVERDICT: %s" % (
        "BOTH are consulted (per-field fallback: record overrides, table fills in)"
        if tot_r and tot_t else
        "only the TABLE is evidenced" if tot_t else
        "only the RECORD is evidenced" if tot_r else "inconclusive"))


if __name__ == "__main__":
    main()
