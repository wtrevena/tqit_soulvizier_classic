"""Capture the base game's exact BitmapUIAware record structure (record_type +
ordered fields + dtypes) for a skill-pane bg record, the mod's current record_type,
and controller-variant resolution for all 9 mastery classes. Read-only."""
import sys
from pathlib import Path
TOOLS = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\tools")
sys.path.insert(0, str(TOOLS))
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive

MOD = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz")
BASE = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
            r"\Titan Quest Anniversary Edition\Database\database.arz")
INGAMEUI = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
                r"\Titan Quest Anniversary Edition\Resources\InGameUI.arc")

DT = {1: "INT", 2: "FLOAT", 4: "STRING", 3: "BOOL"}  # DATA_TYPE_* from arz_patcher

def dump_struct(db, idx, name, label):
    r = idx.get(name.lower().replace("/", "\\"))
    print("\n== %s :: %s ==" % (label, name))
    if not r:
        print("   <ABSENT>"); return
    print("   record_type = %r" % db._record_types.get(r))
    for k, tf in db.get_fields(r).items():
        real = k.split("###")[0]
        print("   %-22s dtype=%-7s values=%r" % (real, DT.get(tf.dtype, tf.dtype), tf.values))

print("loading ...")
bdb = ArzDatabase.from_arz(BASE); BI = {n.lower().replace("/","\\"): n for n in bdb.record_names()}
mdb = ArzDatabase.from_arz(MOD);  MI = {n.lower().replace("/","\\"): n for n in mdb.record_names()}

dump_struct(bdb, BI, r"records\ingameui\player skills\mastery 1\skillpanebasebitmap.dbr", "BASE")
dump_struct(mdb, MI, r"records\ingameui\player skills\mastery 1\skillpanebasebitmap.dbr", "MOD")
dump_struct(bdb, BI, r"records\ingameui\player skills\mastery 1\skillpanereallocationbitmap.dbr", "BASE-realloc")

# controller variant resolution for the classes the mod uses (1-8 + Dream=Spirit)
print("\n== controller-variant textures in base InGameUI.arc ==")
arc = ArcArchive.from_file(INGAMEUI)
ent = set(e.name.lower().replace("/","\\") for e in arc.entries if e.entry_type == 3)
CLASSES = ["Warfare","Defense","Earth","Storm","Stealth","Hunting","Spirit","Nature"]
for cls in CLASSES:
    for kind in ("SkillBackground01", "SkillReallocationBackground01"):
        p_ctrl = ("controller\\skills\\%s%s.tex" % (cls, kind)).lower()
        p_mouse = ("skills\\%s%s.tex" % (cls, kind)).lower()
        print("   %-10s %-30s mouse=%s controller=%s"
              % (cls, kind, "Y" if p_mouse in ent else "N", "Y" if p_ctrl in ent else "N"))
