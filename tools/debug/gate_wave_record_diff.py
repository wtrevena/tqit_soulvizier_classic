r"""WAVE GATE: record-diff the fix build against the lane's own baseline and prove
EVERY change is ATTRIBUTED to one of this wave's two modules - and that nothing
was REMOVED.

The wave contract (task law): "record-diff against a baseline YOU build from main
in the same environment: ZERO unattributed changes and 0 REMOVED records."

Attribution model, derived from the modules themselves (never hand-listed, so it
cannot drift from what the code actually does):
  ADDED     -> exactly `thrown_anim_rig.FAMILIES[*]["clone"]`
  MODIFIED  -> `thrown_restore.ROSTER[*]["record"]`  (charAnimationTableName +
               that family's thrown clips, from thrown_anim_rig)
            -> `uber_quest_drops.LEAKS[*]["record"]` (perPartyMemberDropItemName
               cleared)
  REMOVED   -> nothing, ever.
Per-record the FIELD SET is checked too: a roster record may only differ in
`charAnimationTableName` + its own family's clip keys, and a leak record only in
`perPartyMemberDropItemName`. A change to any other field on an expected record
is reported as unattributed, exactly like a change to an unexpected record.

Also prints the DONOR PROOF: the 5 R-101 donor records must appear in NEITHER
the modified nor the removed set.

Usage:
  py tools/debug/gate_wave_record_diff.py <baseline.arz> <fix.arz>
Exit 0 == every change attributed, 0 removed. Exit 1 == gate RED.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # tools/
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "patches"))
from arz_patcher import ArzDatabase  # noqa: E402
import thrown_restore                # noqa: E402
import thrown_anim_rig               # noqa: E402
import uber_quest_drops              # noqa: E402


def norm(s):
    return str(s).replace("/", "\\").lower()


def fields(db, name):
    out = {}
    ff = db.get_fields(name)
    for k, tf in (ff or {}).items():
        out.setdefault(k.split("###")[0], tf.values)
    return out


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    old = ArzDatabase.from_arz(Path(sys.argv[1]))
    new = ArzDatabase.from_arz(Path(sys.argv[2]))
    on = {norm(n): n for n in old.record_names()}
    nn = {norm(n): n for n in new.record_names()}

    # ---- expected attribution, derived from the modules --------------------
    exp_added = {norm(f["clone"]): "thrown_anim_rig (cloned %s anim table)" % f["key"]
                 for f in thrown_anim_rig.FAMILIES}
    exp_mod = {}
    for e in thrown_restore.ROSTER:
        fam = thrown_anim_rig._family_for(e)
        allowed = {"charAnimationTableName"} | set(fam["clips"])
        exp_mod[norm(e["record"])] = ("thrown_anim_rig (repoint + %s clips)" % fam["key"],
                                      allowed)
    for leak in uber_quest_drops.LEAKS:
        key = norm(leak["record"])
        label = "uber_quest_drops (cleared %s)" % leak["item_label"]
        if key in exp_mod:
            exp_mod[key] = (exp_mod[key][0] + " + " + label,
                            exp_mod[key][1] | {uber_quest_drops._DROP_FIELD})
        else:
            exp_mod[key] = (label, {uber_quest_drops._DROP_FIELD})

    added = sorted(set(nn) - set(on))
    removed = sorted(set(on) - set(nn))

    modified = []
    for k in sorted(set(on) & set(nn)):
        of, nf = fields(old, on[k]), fields(new, nn[k])
        deltas = sorted(fk for fk in (set(of) | set(nf)) if of.get(fk) != nf.get(fk))
        if deltas:
            modified.append((nn[k], deltas))

    print("=" * 78)
    print("WAVE RECORD-DIFF GATE")
    print("  OLD (baseline from main): %s  (%d records)" % (sys.argv[1], len(on)))
    print("  NEW (this wave)         : %s  (%d records)" % (sys.argv[2], len(nn)))
    print("  ADDED %d   REMOVED %d   MODIFIED %d" % (len(added), len(removed), len(modified)))
    print("=" * 78)

    bad = []

    print("\n-- ADDED --")
    for k in added:
        why = exp_added.get(k)
        print("  + %-72s %s" % (nn[k], why or "*** UNATTRIBUTED ***"))
        if not why:
            bad.append("ADDED unattributed: %s" % nn[k])
    for k in exp_added:
        if k not in added:
            bad.append("EXPECTED-ADDED missing: %s" % k)

    print("\n-- REMOVED --")
    if not removed:
        print("  (none)")
    for k in removed:
        print("  - %s   *** RECORDS MUST NEVER BE REMOVED ***" % on[k])
        bad.append("REMOVED: %s" % on[k])

    print("\n-- MODIFIED --")
    for name, deltas in modified:
        k = norm(name)
        exp = exp_mod.get(k)
        if exp is None:
            print("  ~ %-72s *** UNATTRIBUTED ***" % name)
            print("      fields: %s" % ", ".join(deltas))
            bad.append("MODIFIED unattributed: %s (%s)" % (name, ", ".join(deltas)))
            continue
        why, allowed = exp
        stray = [d for d in deltas if d not in allowed]
        print("  ~ %-72s %s" % (name, why))
        print("      %d field(s): %s" % (len(deltas), ", ".join(deltas)))
        if stray:
            print("      *** UNEXPECTED FIELDS: %s ***" % ", ".join(stray))
            bad.append("MODIFIED %s changed unexpected field(s): %s" % (name, ", ".join(stray)))
    for k in exp_mod:
        if k not in {norm(n) for n, _ in modified}:
            bad.append("EXPECTED-MODIFIED missing: %s" % k)

    print("\n-- R-101 DONOR PROOF (must be in NEITHER list) --")
    mod_keys = {norm(n) for n, _ in modified}
    for item, donors in uber_quest_drops.DONORS.items():
        for d in donors:
            k = norm(d)
            state = ("MODIFIED" if k in mod_keys else
                     "REMOVED" if k in removed else "unchanged")
            print("  %-9s %s" % (state, d))
            if state != "unchanged":
                bad.append("DONOR %s is %s - the real quest is at risk" % (d, state))

    print("\n" + "=" * 78)
    if bad:
        print("GATE RED (%d finding(s)):" % len(bad))
        for b in bad:
            print("   - %s" % b)
        raise SystemExit(1)
    print("GATE GREEN: %d added / %d removed / %d modified - every change attributed "
          "to this wave's two modules, 0 unattributed, 0 removed, all %d donors unchanged."
          % (len(added), len(removed), len(modified),
             sum(len(v) for v in uber_quest_drops.DONORS.values())))
    raise SystemExit(0)


if __name__ == "__main__":
    main()
