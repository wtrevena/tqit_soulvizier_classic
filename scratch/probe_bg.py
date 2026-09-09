"""RCA probe: resolve every mastery UI bitmap field in the DEPLOYED arz against the
REAL shipped mod + base arc set. Read-only. No game, no heavy build.

Ground truth:
  arz  = deployed DEV SoulvizierClassicDEV.arz (md5 b33c5a44) - Will's exact load
  arcs = deployed DEV Resources (priority) UNION base-game Resources (fallback)

Resolution model (b43 RCA sec4, verified): a resource path's leading component(s)
name the .arc (root arc = 1 component; XPack DLC arc = 2 components under XPackN\);
a custom map resolves from mod Resources FIRST, then base Resources.
"""
import sys, os
from pathlib import Path

TOOLS = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\tools")
sys.path.insert(0, str(TOOLS))
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive

ARZ = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz")
MOD_RES = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
               r"\CustomMaps\SoulvizierClassicDEV\Resources")
BASE_RES = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
                r"\Titan Quest Anniversary Edition\Resources")

# ---------------------------------------------------------------- arc index
class ArcIndex:
    def __init__(self):
        self.mounts = []   # (priority, mount_prefix_lower, entryset_lower, label)
    def add_dir(self, root: Path, priority: int, label: str):
        for arc_path in root.rglob("*.arc"):
            rel = arc_path.relative_to(root)
            mount = str(rel.with_suffix("")).lower().replace("/", "\\")
            try:
                arc = ArcArchive.from_file(arc_path)
            except Exception as e:
                print("  ! failed to load", arc_path, e); continue
            entries = set()
            for e in arc.entries:
                if e.entry_type == 3 and e.name:
                    entries.add(e.name.lower().replace("/", "\\"))
            self.mounts.append((priority, mount, entries, "%s:%s" % (label, mount)))
    def resolve(self, path):
        """Return list of (priority, label) that provide `path`, best (mod) first."""
        p = str(path).lower().replace("/", "\\").lstrip("\\")
        hits = []
        for priority, mount, entries, label in self.mounts:
            pref = mount + "\\"
            if p.startswith(pref):
                remainder = p[len(pref):]
                if remainder in entries:
                    hits.append((priority, label))
        hits.sort()
        return hits

print("building arc index ...")
IDX = ArcIndex()
IDX.add_dir(MOD_RES, 0, "MOD")
IDX.add_dir(BASE_RES, 1, "BASE")
print("  mounts:", len(IDX.mounts))

# ---------------------------------------------------------------- arz
db = ArzDatabase.from_arz(ARZ)
NAMES = {n.lower().replace("/", "\\"): n for n in db.record_names()}
def rec(name):
    return NAMES.get(name.lower().replace("/", "\\"))

def field_items(recname):
    """Yield (real_field_name, value) for every value in the record."""
    r = rec(recname)
    if not r:
        return None
    fl = db.get_fields(r)
    if fl is None:
        return None
    out = []
    for k, tf in fl.items():
        real = k.split('###')[0]
        for item in tf.values:
            out.append((real, item))
    return out

def is_tex(v):
    return isinstance(v, str) and v.lower().endswith(".tex")

def dump_record(recname):
    items = field_items(recname)
    if items is None:
        print("    <NO RECORD> %s" % recname); return []
    return [(k, v) for k, v in items if is_tex(v)]

def resolve_line(field, tex):
    hits = IDX.resolve(tex)
    if not hits:
        verdict = "*** UNRESOLVED (BLACK) ***"
    else:
        verdict = "OK <- " + ",".join(l for _, l in hits[:3])
    print("      %-32s %-55s %s" % (field, tex, verdict))
    return bool(hits), tex

FOLDERS = {
    1: r"records\ingameui\player skills\mastery 1",
    2: r"records\ingameui\player skills\mastery 2",
    3: r"records\ingameui\player skills\mastery 3",
    4: r"records\ingameui\player skills\mastery 4",
    5: r"records\ingameui\player skills\mastery 5",
    6: r"records\ingameui\player skills\mastery 6",
    7: r"records\ingameui\player skills\mastery 7",
    8: r"records\ingameui\player skills\mastery 8",
    9: r"records\xpack\ui\skills\mastery 9",
}
MNAME = {1:"Warfare",2:"Defense",3:"Earth",4:"Storm",5:"Occult",6:"Hunting",
         7:"Spirit",8:"Nature",9:"Dream"}

unresolved = []
print("\n===================== TREE-PANE (skill selection) chain =====================")
for slot, folder in FOLDERS.items():
    print("\n-- m%d %s  (%s) --" % (slot, MNAME[slot], folder))
    for suf in ("skillpanebasebitmap.dbr", "skillpanereallocationbitmap.dbr",
                "masterybitmap.dbr", "panectrl.dbr", "mastery.dbr"):
        recname = folder + "\\" + suf
        texs = dump_record(recname)
        if texs:
            print("   %s:" % suf)
            for f, t in texs:
                ok, _ = resolve_line(f, t)
                if not ok: unresolved.append((slot, MNAME[slot], "TREE", suf, f, t))

print("\n===================== SELECT-MASTERY chain =====================")
for selfolder in (r"records\ingameui\player skills\select mastery",
                  r"records\xpack\ui\skills\select mastery"):
    print("\n-- select pane: %s --" % selfolder)
    pane = selfolder + r"\masterypane.dbr"
    items = field_items(pane)
    if items is None:
        print("   <NO masterypane.dbr>"); continue
    # dump inline tex fields (e.g. masteryMasterySelectedBitmapNames -> PanelLarge)
    for k, v in items:
        if is_tex(v):
            ok, _ = resolve_line(k, v)
            if not ok: unresolved.append(("sel", selfolder, "SELECT", "masterypane", k, v))
    # button records referenced by any field
    seen_btn = set()
    for k, v in items:
        if isinstance(v, str) and v.lower().endswith(".dbr") and "button" in v.lower():
            if v.lower() in seen_btn:
                continue
            seen_btn.add(v.lower())
            texs = dump_record(v)
            if texs:
                print("   %s:" % v.rsplit("\\",1)[-1])
                for f, t in texs:
                    ok, _ = resolve_line(f, t)
                    if not ok: unresolved.append(("sel", v, "SELECT-BTN", f, f, t))

print("\n===================== SUMMARY =====================")
if not unresolved:
    print("ALL mastery UI bitmaps RESOLVE. (No static unresolved-art break found.)")
else:
    print("UNRESOLVED (render black) count:", len(unresolved))
    for row in unresolved:
        print("  ", row)
