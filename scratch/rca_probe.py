"""MASTERY BACKGROUND RENDER RCA probe (read-only).

Dumps BOTH mastery-UI art chains from the DEPLOYED arz and resolves every
referenced .tex against the SHIPPED mod Resources arcs UNION the base-game arcs,
using the engine-faithful archive rule (first path component = archive name; the
mod arc of that name wins, else the base arc of that name; XPackN is folder-scoped).

  SELECT chain : select mastery\\masterypane.dbr  -> masteryMasterySelectedBitmapNames[N]
                 + select mastery\\mastery{N}button.dbr bitmapName{Up,Down,InFocus,Disabled}
  TREE chain   : mastery {N}\\skillpanebasebitmap.dbr::bitmapName
                 + mastery {N}\\skillpanereallocationbitmap.dbr::bitmapName
                 + mastery {N}\\panectrl.dbr pointer fields + skillPaneMasteryBitmap leaf

For every .tex: report WHICH arc it resolves from (mod / base / NONE) so a
records-point-at-nothing break is visible per-mastery.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from arz_patcher import ArzDatabase   # noqa
from arc_patcher import ArcArchive    # noqa

DEV = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassicDEV")
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition")
MOD_RES = DEV / "Resources"
ARZ = DEV / "Database" / "SoulvizierClassicDEV.arz"

XPACK_SCOPES = ("xpack", "xpack2", "xpack3", "xpack4")

# ---- arc index (engine-faithful; mod wins over base for a plain arc name) ----
_arc_cache = {}


def arc_names(folder: Path, arcname: str):
    key = (str(folder).lower(), arcname.lower())
    if key in _arc_cache:
        return _arc_cache[key]
    names = None
    cand = folder / (arcname + ".arc")
    if not cand.exists():
        hits = [p for p in folder.glob("*.arc") if p.stem.lower() == arcname.lower()] if folder.is_dir() else []
        cand = hits[0] if hits else None
    if cand and cand.exists():
        try:
            arc = ArcArchive.from_file(cand)
            names = set()
            for e in arc.entries:
                if e.name:
                    names.add(e.name.lower().replace("\\", "/"))
        except Exception as ex:
            names = None
            print("   !! arc parse fail %s: %s" % (cand, ex))
    _arc_cache[key] = names
    return names


def resolve(ref: str):
    """Return (ok, where). where names the archive+root it resolved in, or the miss."""
    parts = str(ref).replace("/", "\\").split("\\")
    if len(parts) < 2:
        return (False, "too-short:%r" % ref)
    p0 = parts[0].lower()
    if p0 in XPACK_SCOPES and len(parts) >= 3:
        arcname = parts[1]
        inner = "/".join(parts[2:]).lower()
        names = arc_names(GAME / "Resources" / parts[0], arcname)
        if names is None:
            return (False, "no base %s\\%s.arc" % (parts[0], arcname))
        return (inner in names, "base:%s\\%s.arc" % (parts[0], arcname))
    arcname = parts[0]
    inner = "/".join(parts[1:]).lower()
    mod = arc_names(MOD_RES, arcname)
    if mod is not None and inner in mod:
        return (True, "MOD:%s.arc" % arcname)
    base = arc_names(GAME / "Resources", arcname)
    if base is not None and inner in base:
        return (True, "base:%s.arc" % arcname)
    detail = []
    detail.append("MOD %s.arc %s" % (arcname, "absent" if mod is None else "present-no-entry"))
    detail.append("base %s.arc %s" % (arcname, "absent" if base is None else "present-no-entry"))
    return (False, "UNRESOLVED [" + "; ".join(detail) + "]")


def flag(ok):
    return "OK " if ok else "!! MISS"


db = ArzDatabase.from_arz(ARZ)
recmap = {n.lower().replace("/", "\\"): n for n in db.record_names()}


def rec(path):
    return recmap.get(path.lower().replace("/", "\\"))


def fvals(recname, field):
    fields = db.get_fields(recname) or {}
    for k, tf in fields.items():
        if k.split("###")[0] == field:
            return list(tf.values)
    return None


MASTERY_CLASS = {1: "Warfare", 2: "Defense", 3: "Earth", 4: "Storm",
                 5: "Stealth", 6: "Hunting", 7: "Spirit", 8: "Nature", 9: "Dream"}


def mfolder(slot):
    if slot == 9:
        return "records\\xpack\\ui\\skills\\mastery 9\\"
    return "records\\ingameui\\player skills\\mastery %d\\" % slot


print("=" * 78)
print("ARZ:", ARZ, "\n md5 expect b33c5a44; records:", len(db.record_names()))
print("MOD Resources arcs:", sorted(p.stem for p in MOD_RES.glob("*.arc")))
print("mod ships InGameUI.arc:", (MOD_RES / "InGameUI.arc").exists())
print("mod ships DRXtextures.arc:", (MOD_RES / "DRXtextures.arc").exists())

# ---------------- TREE CHAIN ----------------
print("\n" + "=" * 78)
print("TREE CHAIN  (skill-pane backgrounds, per mastery)")
print("=" * 78)
tree_miss = []
for slot in range(1, 10):
    f = mfolder(slot)
    print("\n-- m%d %s --" % (slot, MASTERY_CLASS[slot]))
    for leaf in ("skillpanebasebitmap.dbr", "skillpanereallocationbitmap.dbr", "skillpanemasterybitmap.dbr"):
        rn = rec(f + leaf)
        if not rn:
            print("   %-32s <NO RECORD in arz>" % leaf)
            continue
        bn = fvals(rn, "bitmapName")
        if not bn:
            print("   %-32s bitmapName=<none>" % leaf)
            continue
        for v in bn:
            if not str(v).strip():
                continue
            ok, where = resolve(v)
            print("   %-32s %-6s %-55s %s" % (leaf, flag(ok), v, where))
            if not ok:
                tree_miss.append((slot, MASTERY_CLASS[slot], leaf, v, where))
    # panectrl pointer fields (informational)
    pc = rec(f + "panectrl.dbr")
    if pc:
        for pf in ("skillPaneBaseBitmap", "skillPaneBaseReallocationBitmap", "skillPaneMasteryBitmap"):
            pv = fvals(pc, pf)
            if pv:
                print("   panectrl.%-28s -> %s" % (pf, pv))

# ---------------- SELECT CHAIN ----------------
print("\n" + "=" * 78)
print("SELECT CHAIN  (choose-a-mastery screen)")
print("=" * 78)
sel_miss = []
for cand in ("records\\ingameui\\player skills\\select mastery\\masterypane.dbr",
             "records\\xpack\\ui\\skills\\select mastery\\masterypane.dbr",
             "records\\xpack3\\ui\\skills\\select mastery\\masterypane.dbr"):
    rn = rec(cand)
    print("\nmasterypane candidate:", cand, "->", "PRESENT in mod arz" if rn else "absent (base-game record)")
    if not rn:
        continue
    for field in ("masteryMasterySelectedBitmapNames", "masteryMasteryButtons",
                  "masteryMasteryText", "masteryMasterySelectedDescriptionTags",
                  "masteryTabTitle", "masteryDefaultTextTag"):
        vv = fvals(rn, field)
        print("  %s = %s" % (field, vv))
        if field == "masteryMasterySelectedBitmapNames" and vv:
            for v in vv:
                if str(v).strip():
                    ok, where = resolve(v)
                    print("       %-6s %-55s %s" % (flag(ok), v, where))
                    if not ok:
                        sel_miss.append(("masterypane", field, v, where))

# select-mastery button records (icons) + their DRX panel backdrops
print("\n-- select mastery\\mastery{N}button.dbr (icons) --")
for base_dir in ("records\\ingameui\\player skills\\select mastery\\",
                 "records\\xpack\\ui\\skills\\select mastery\\"):
    any_here = False
    for slot in range(1, 10):
        rn = rec(base_dir + "mastery%dbutton.dbr" % slot)
        if not rn:
            continue
        any_here = True
        for bf in ("bitmapNameUp", "bitmapNameDown", "bitmapNameInFocus", "bitmapNameDisabled"):
            bv = fvals(rn, bf)
            if bv:
                for v in bv:
                    if str(v).strip():
                        ok, where = resolve(v)
                        tag = flag(ok)
                        if not ok:
                            sel_miss.append((base_dir + "mastery%dbutton" % slot, bf, v, where))
                        print("   m%d %-16s %-6s %-50s %s" % (slot, bf, tag, v, where))
    if not any_here:
        print("   (none present in mod arz under %s)" % base_dir)

# Sweep ALL mod-arz records that reference DRXtextures masterybackdrops / panel art
print("\n" + "=" * 78)
print("DRX MASTERY-PANEL BACKDROP SWEEP (mod-arz records pointing at DRXtextures panel art)")
print("=" * 78)
panel_refs = {}
for n in db.record_names():
    nl = n.lower()
    if "mastery" not in nl and "skillpane" not in nl and "select" not in nl:
        continue
    fields = db.get_fields(n) or {}
    for k, tf in fields.items():
        for v in tf.values:
            s = str(v)
            if s.lower().endswith(".tex") and ("masterybackdrop" in s.lower() or "panel" in s.lower() or "backdrop" in s.lower()):
                panel_refs.setdefault(s, []).append((n, k.split("###")[0]))
for s, uses in sorted(panel_refs.items()):
    ok, where = resolve(s)
    print("  %-6s %-58s %s" % (flag(ok), s, where))
    for n, k in uses[:4]:
        print("        <- %s :: %s" % (n, k))
    if not ok:
        sel_miss.append(("panel-sweep", uses[0][1], s, where))

print("\n" + "=" * 78)
print("SUMMARY")
print("=" * 78)
print("TREE-chain unresolved refs: %d" % len(tree_miss))
for t in tree_miss:
    print("   m%d %s  %s -> %s  [%s]" % t)
print("SELECT-chain unresolved refs: %d" % len(sel_miss))
for s in sel_miss:
    print("   %s :: %s -> %s  [%s]" % s)
