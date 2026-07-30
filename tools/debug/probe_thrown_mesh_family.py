r"""probe_thrown_mesh_family.py - "resolve on its ACTUAL MESH", not merely
"the file exists".

`tools/gate_thrown_anim_assets.py` proves every thrown clip RESOLVES in the
shipped arc set. That is necessary and not sufficient: an `.anm` is
skeleton-bound, so a maenad handed a tigerman clip would resolve perfectly and
still animate wrong (or not at all). R-100 #15's brief asks specifically to
*"prove for each that its attack/move animations resolve on its actual mesh"*.

The database-side test that actually bears on that: for every roster record,
does each thrown-stance clip come from the SAME creature-family directory as the
`mesh` that record renders? And where it does not, is that OUR choice or a value
copied VERBATIM from what base TQAE itself binds?

That second question is what makes the probe usable rather than noisy - base is
itself cross-family in places (tigerman's death clip is a BoarMan clip; the two
share a rig), and reproducing base's own binding is correct by definition. Only
an off-family clip that is NOT base's own is a finding.

exit 0 = every CRITICAL clip is on the record's own family AND every off-family
         clip is verbatim base
exit 1 = a critical off-family clip, or an off-family clip we invented

usage: py tools/debug/probe_thrown_mesh_family.py <base.arz> <mod.arz>
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "patches"))
from arz_patcher import ArzDatabase   # noqa: E402
import thrown_anim_rig                # noqa: E402
import thrown_restore                 # noqa: E402

CRITICAL = thrown_anim_rig.CRITICAL_SLOTS


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


def family_of(path):
    """the creature-family directory component of a mesh or .anm path"""
    parts = _n(path).split("\\")
    for i, p in enumerate(parts):
        if p == "monster" and i + 1 < len(parts):
            return parts[i + 1]
    return parts[-2] if len(parts) > 1 else "?"


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    base = ArzDatabase.from_arz(Path(argv[1]))
    mod = ArzDatabase.from_arz(Path(argv[2]))
    bi = {_n(x): x for x in base.record_names()}
    mi = {_n(x): x for x in mod.record_names()}

    print("%-26s %-12s %-14s %s" % ("roster record", "mesh family", "stance", "verdict"))
    print("-" * 92)
    findings = []
    for entry in thrown_restore.ROSTER:
        rec = mi.get(_n(entry["record"]))
        if rec is None:
            print("%-26s MISSING FROM THE MOD" % entry["record"])
            findings.append((entry["record"], "record", "missing", True, False))
            continue
        mesh = _fv(mod, rec, "mesh")
        mfam = family_of(mesh) if mesh else "?"
        fam = thrown_anim_rig._family_for(entry)
        off = []
        for field, clip in fam["clips"].items():
            cfam = family_of(clip)
            if cfam != mfam:
                off.append((field, clip, cfam))
        n_crit = sum(1 for f, _c, _x in off if any(f.endswith(s) for s in CRITICAL))
        verdict = "ALL clips on own family" if not off else \
                  "%d off-family (%d CRITICAL)" % (len(off), n_crit)
        print("%-26s %-12s %-14s %s"
              % (rec.split("\\")[-1], mfam, fam["stance"], verdict))
        btbl = bi.get(_n(fam["table"]))
        for field, clip, cfam in off:
            is_crit = any(field.endswith(s) for s in CRITICAL)
            bval = _fv(base, btbl, field) if btbl else None
            verbatim = bval is not None and _n(bval) == _n(clip)
            print("      %-34s -> %-11s %-9s %s"
                  % (field, cfam, "CRITICAL" if is_crit else "cosmetic",
                     "VERBATIM from base" if verbatim
                     else "*** OURS - not base's own binding ***"))
            findings.append((rec, field, cfam, is_crit, verbatim))

    crit = [f for f in findings if f[3]]
    invented = [f for f in findings if not f[4]]
    print("\noff-family clips total       : %d" % len(findings))
    print("  of which CRITICAL slots    : %d" % len(crit))
    print("  of which NOT verbatim base : %d" % len(invented))
    if not crit and not invented:
        print("\nRESULT: PASS - every CRITICAL (run/walk/attack) clip plays on the "
              "record's\n        own creature family, and every off-family clip is "
              "copied VERBATIM from\n        what base TQAE itself binds. No animation "
              "was invented and none was\n        re-pointed onto a foreign skeleton by "
              "this wave.")
        return 0
    print("\nRESULT: FAIL - review the starred rows above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
