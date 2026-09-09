"""COMPLETE unresolved-UI sweep + cross-namespace shadow check.

(1) Every record in the DEPLOYED arz named skillpanebasebitmap.dbr /
    skillpanereallocationbitmap.dbr (ANY namespace) -> bitmapName + resolution.
    Reveals xpack/xpack2/xpack3 shadow panes that may still point at broken art.
(2) Every mastery-UI record (any '\player skills\' or 'ui\skills\mastery' path)
    with ANY bitmap* field that DOES NOT resolve -> the full residual break list.
(3) Base-game database.arz: what does vanilla point these at? (proves the target).
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
BASE_ARZ = GAME / "Database" / "database.arz"
XPACK_SCOPES = ("xpack", "xpack2", "xpack3", "xpack4")
_arc_cache = {}


def arc_names(folder, arcname):
    key = (str(folder).lower(), arcname.lower())
    if key in _arc_cache:
        return _arc_cache[key]
    names = None
    cand = folder / (arcname + ".arc")
    if not cand.exists() and folder.is_dir():
        hits = [p for p in folder.glob("*.arc") if p.stem.lower() == arcname.lower()]
        cand = hits[0] if hits else None
    if cand and cand.exists():
        try:
            arc = ArcArchive.from_file(cand)
            names = {e.name.lower().replace("\\", "/") for e in arc.entries if e.name}
        except Exception:
            names = None
    _arc_cache[key] = names
    return names


def resolve(ref):
    parts = str(ref).replace("/", "\\").split("\\")
    if len(parts) < 2:
        return (False, "too-short")
    p0 = parts[0].lower()
    if p0 in XPACK_SCOPES and len(parts) >= 3:
        names = arc_names(GAME / "Resources" / parts[0], parts[1])
        inner = "/".join(parts[2:]).lower()
        if names is None:
            return (False, "no base %s\\%s.arc" % (parts[0], parts[1]))
        return (inner in names, "base:%s\\%s.arc" % (parts[0], parts[1]))
    inner = "/".join(parts[1:]).lower()
    mod = arc_names(MOD_RES, parts[0])
    if mod is not None and inner in mod:
        return (True, "MOD:%s.arc" % parts[0])
    base = arc_names(GAME / "Resources", parts[0])
    if base is not None and inner in base:
        return (True, "base:%s.arc" % parts[0])
    return (False, "UNRESOLVED(mod=%s base=%s)" % (
        "absent" if mod is None else "no-entry",
        "absent" if base is None else "no-entry"))


db = ArzDatabase.from_arz(ARZ)


def fvals(d, recname, field):
    fields = d.get_fields(recname) or {}
    for k, tf in fields.items():
        if k.split("###")[0] == field:
            return list(tf.values)
    return None


print("=" * 80)
print("(1) EVERY skillpanebasebitmap / skillpanereallocationbitmap RECORD (all namespaces)")
print("=" * 80)
pane_recs = [n for n in db.record_names()
             if n.lower().endswith("skillpanebasebitmap.dbr")
             or n.lower().endswith("skillpanereallocationbitmap.dbr")]
for n in sorted(pane_recs):
    bn = fvals(db, n, "bitmapName")
    if not bn:
        print("  %-70s bitmapName=<none>" % n)
        continue
    for v in bn:
        if str(v).strip():
            ok, where = resolve(v)
            print("  %-6s %-66s -> %s   [%s]" % ("OK" if ok else "!!MISS", n, v, where))

print("\n" + "=" * 80)
print("(2) ALL mastery-UI records with an UNRESOLVED bitmap* ref (residual break list)")
print("=" * 80)
missing = []
for n in db.record_names():
    nl = n.lower().replace("/", "\\")
    if ("\\player skills\\" not in nl and "ui\\skills\\mastery" not in nl
            and "\\masteries\\" not in nl and "ui\\skills\\select" not in nl):
        continue
    fields = db.get_fields(n) or {}
    for k, tf in fields.items():
        kf = k.split("###")[0]
        if not kf.lower().startswith("bitmap") and kf.lower() not in ("bitmapname",):
            # only bitmap-bearing fields (bitmapName, bitmapNameUp/Down/InFocus/Disabled)
            if "bitmap" not in kf.lower():
                continue
        for v in tf.values:
            s = str(v)
            if s.lower().endswith(".tex"):
                ok, where = resolve(s)
                if not ok:
                    missing.append((n, kf, s, where))
seen = set()
for n, kf, s, where in missing:
    key = (n, kf, s)
    if key in seen:
        continue
    seen.add(key)
    print("  %-64s %-22s %s" % (n[:64], kf, s))
print("\n  distinct broken (record,field,tex) refs:", len(seen))
# group by tex
from collections import Counter
byt = Counter(s for _, _, s, _ in missing)
print("  broken textures (by frequency):")
for t, c in byt.most_common():
    print("     %3d  %s" % (c, t))

print("\n" + "=" * 80)
print("(3) BASE GAME vanilla values for the 9 mastery panes (the render target)")
print("=" * 80)
try:
    base_db = ArzDatabase.from_arz(BASE_ARZ)
    for slot in range(1, 9):
        rn = "records\\ingameui\\player skills\\mastery %d\\skillpanebasebitmap.dbr" % slot
        bn = fvals(base_db, rn, "bitmapName")
        print("  base m%d skillpanebasebitmap.bitmapName = %s" % (slot, bn))
    rn9 = "records\\xpack\\ui\\skills\\mastery 9\\skillpanebasebitmap.dbr"
    print("  base m9 (xpack) skillpanebasebitmap.bitmapName = %s" % fvals(base_db, rn9, "bitmapName"))
    # Does base game have xpack3 shadow panes for masteries 1-8?
    print("\n  --- base-game xpack3/xpack2/xpack mastery-pane shadow records? ---")
    for n in base_db.record_names():
        nl = n.lower()
        if nl.endswith("skillpanebasebitmap.dbr") and ("xpack" in nl):
            print("     base has:", n, "->", fvals(base_db, n, "bitmapName"))
except Exception as ex:
    print("  base arz load failed:", ex)
