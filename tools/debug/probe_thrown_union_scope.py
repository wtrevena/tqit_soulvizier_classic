r"""probe_thrown_union_scope.py - the check that the round-1 R-140 work did NOT
do, and the one that produced the R-140 AMENDMENT.

THE BLIND SPOT IT CLOSES
------------------------
The mod `.arz` is an **OVERLAY**, not a full merge: ~41,226 base-game records
are absent from it and the engine reads those straight from base. Every census
in the original R-140 walked `db.record_names()` on the MOD, so:

  * "10 thrown wielders in the entire database" was really *10 in the mod's own
    records* - the engine-visible union is 78;
  * the shared-carrier counts (168 / 68 / 64 / 30) were mod-only and understated
    the true blast radius of editing those tables (174 / 85 / 65 / 30).

Neither error changed the fix, but the FIRST one hid a question that could have:
**is there a base-only thrown wielder that names one of the four SV-stripped
animation tables?** If one existed it would inherit our broken table, ship
frozen, and be invisible to every mod-only scan. This probe answers that by
construction rather than by assumption.

WHAT IT REPORTS
---------------
  1. overlay shape (how many base records the mod does NOT override)
  2. the union thrower roster, resolved the way the engine resolves
     (mod overlay first, base as pass-through), split by record source
  3. every FROZEN thrower in the union, with the surface that failed
  4. the TRUE shared-carrier census for the four animation tables
  5. the load-bearing answer: base-only throwers naming a stripped table

Thrown weapons are identified from GROUND TRUTH - base records whose `Class` is
`WeaponHunting_RangedOneHand`, plus the loot tables that can yield one - never
from a filename heuristic, so it is an independent check on the path test used
by `patches/thrown_anim_rig._is_thrown_loot`.

exit 0 = no frozen thrower that this mod is responsible for
exit 1 = a frozen thrower attributable to the mod

usage: py tools/debug/probe_thrown_union_scope.py <base.arz> <mod.arz>
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from arz_patcher import ArzDatabase   # noqa: E402

CRITICAL = ("RunAnim", "WalkAnim", "AttackAnim1")

# The four tables SV 0.98i replaced with pre-thrown-weapon versions (R-140).
STRIPPED = {
    r"records\creature\monster\maenad\anm\anm_maenad.dbr": "rangedOneHand",
    r"records\creature\monster\tigerman\anm\anm_tiger.dbr": "rangedOneHand",
    r"records\xpack\creatures\monster\machae\anm\anm_machae.dbr": "rangedOneHand",
    r"records\creature\monster\duneraider\anm\anm_duneraider.dbr": "dualRanged",
}

# Known PRE-EXISTING stock-game breakage - not ours, must never be "fixed".
# See BL-R140-STOCKANM-1: base's own ANM_MalePC01 binds no rangedOneHandWalkAnim.
STOCK_WAIVERS = {
    r"records\xpack2\creatures\npc\corinth\fighting\ss_porcusroh2_die.dbr",
}


def _n(s):
    return str(s).replace("/", "\\").lower()


def _sc(v):
    return v[0] if isinstance(v, list) and v else v


def _fv(db, rec, key):
    if rec is None:
        return None
    f = db.get_fields(rec)
    if not f:
        return None
    tf = f.get(key)
    if tf is None:
        for k, v in f.items():
            if "###" in k and k.split("###")[0] == key:
                tf = v
                break
    return _sc(tf.value) if tf is not None else None


def thrown_weapon_ground_truth(base):
    """(weapon paths, loot-table paths) - both from base's own Class values."""
    weapons = set()
    for rec in base.record_names():
        c = _fv(base, rec, "Class")
        if c and str(c).strip() == "WeaponHunting_RangedOneHand":
            weapons.add(_n(rec))
    tables = set()
    for rec in base.record_names():
        c = _fv(base, rec, "Class")
        if not c or "LootItemTable" not in str(c):
            continue
        for k, tf in (base.get_fields(rec) or {}).items():
            key = k.split("###")[0]
            if not (key.startswith("lootName") or key.startswith("bonusTableName")):
                continue
            vals = tf.value if isinstance(tf.value, list) else [tf.value]
            if any(v and _n(v) in weapons for v in vals):
                tables.add(_n(rec))
                break
    return weapons, tables


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    base = ArzDatabase.from_arz(Path(argv[1]))
    mod = ArzDatabase.from_arz(Path(argv[2]))
    bi = {_n(x): x for x in base.record_names()}
    mi = {_n(x): x for x in mod.record_names()}

    print("=== 1. OVERLAY SHAPE ===")
    only_base = set(bi) - set(mi)
    print("  base records        : %d" % len(bi))
    print("  mod records         : %d" % len(mi))
    print("  base-only (NOT overridden by the mod, read straight from base): %d"
          % len(only_base))

    def pick(path):
        """engine resolution: mod overlay first, base as pass-through"""
        r = mi.get(_n(path))
        if r is not None:
            return mod, r, "mod"
        r = bi.get(_n(path))
        if r is not None:
            return base, r, "base"
        return None, None, "absent"

    def eff(path, key):
        db, rec, _src = pick(path)
        return _fv(db, rec, key) if rec is not None else None

    weapons, loot = thrown_weapon_ground_truth(base)
    print("\n=== 2. THROWN WIELDERS in the UNION (ground-truth weapon resolution) ===")
    print("  base WeaponHunting_RangedOneHand records: %d ; loot tables yielding one: %d"
          % (len(weapons), len(loot)))

    def slot_thrown(db, rec, key):
        f = db.get_fields(rec) or {}
        if key not in f:
            return False
        vals = f[key].value if isinstance(f[key].value, list) else [f[key].value]
        return any(v and (_n(v) in weapons or _n(v) in loot) for v in vals)

    throwers, frozen = [], []
    for path in sorted(set(bi) | set(mi)):
        db, rec, src = pick(path)
        if rec is None or _fv(db, rec, "Class") != "Monster":
            continue
        rc = float(_fv(db, rec, "chanceToEquipRightHand") or 0)
        lc = float(_fv(db, rec, "chanceToEquipLeftHand") or 0)
        if rc <= 0 and lc <= 0:
            continue
        rt = rc > 0 and slot_thrown(db, rec, "lootRightHandItem1")
        lt = lc > 0 and slot_thrown(db, rec, "lootLeftHandItem1")
        if not (rt or lt):
            continue
        stance = "dualRanged" if (rt and lt) else "rangedOneHand"
        tbl = _fv(db, rec, "charAnimationTableName")
        throwers.append((path, src, stance, tbl))
        missing = []
        for slot in CRITICAL:
            key = stance + slot
            v = _fv(db, rec, key)
            if isinstance(v, str) and v.lower().endswith(".anm"):
                continue
            tv = eff(tbl, key) if tbl else None
            if not (isinstance(tv, str) and tv.lower().endswith(".anm")):
                missing.append(key)
        if missing:
            frozen.append((path, src, stance, tbl, missing))

    by_src = {}
    for _p, s, _st, _t in throwers:
        by_src[s] = by_src.get(s, 0) + 1
    print("  thrown wielders in the union: %d   by record source: %s"
          % (len(throwers), by_src))

    print("\n=== 3. FROZEN in the union ===")
    ours = [f for f in frozen if _n(f[0]) not in {_n(w) for w in STOCK_WAIVERS}]
    for path, src, stance, tbl, missing in frozen:
        tag = "WAIVED (stock-game, BL-R140-STOCKANM-1)" \
            if _n(path) in {_n(w) for w in STOCK_WAIVERS} else "*** ATTRIBUTABLE TO THIS MOD ***"
        print("  FROZEN [%s] %s" % (src, path))
        print("      stance=%s table=%s missing=%s  %s"
              % (stance, tbl, ",".join(missing), tag))
    if not frozen:
        print("  (none)")

    print("\n=== 4. TRUE shared-carrier census for the 4 SV-stripped tables ===")
    print("  %-24s %10s %10s %10s" % ("table", "mod", "base-only", "TOTAL"))
    for tbl in STRIPPED:
        m = sum(1 for r in mod.record_names()
                if _n(_fv(mod, r, "charAnimationTableName") or "") == _n(tbl))
        b = sum(1 for r in base.record_names()
                if _n(r) not in mi
                and _n(_fv(base, r, "charAnimationTableName") or "") == _n(tbl))
        print("  %-24s %10d %10d %10d" % (tbl.split("\\")[-1], m, b, m + b))

    print("\n=== 5. THE LOAD-BEARING CHECK: base-only throwers on a stripped table ===")
    hits = []
    for path, src, stance, tbl in throwers:
        if src != "base":
            continue
        if tbl and _n(tbl) in {_n(t) for t in STRIPPED}:
            hits.append((path, tbl))
    print("  base-only monsters that BOTH name a stripped table AND equip a thrown "
          "weapon: %d" % len(hits))
    for p, t in hits:
        print("    %s -> %s" % (p, t))
    print("  -> %s" % ("NONE. The mod's own roster is COMPLETE: no monster outside it "
                       "can inherit this defect."
                       if not hits else
                       "ROSTER INCOMPLETE - these ship frozen and must be added."))

    print("\n%s" % ("RESULT: PASS - 0 frozen throwers attributable to this mod"
                    if not ours else
                    "RESULT: FAIL - %d frozen thrower(s) attributable to this mod" % len(ours)))
    return 1 if ours else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
