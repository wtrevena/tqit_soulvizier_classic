import sys
from pathlib import Path
REPO = Path(r"C:/Users/willi/repos/tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / "tools"))
from arz_patcher import ArzDatabase
DEV = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassicDEV")
db = ArzDatabase.from_arz(DEV / "Database" / "SoulvizierClassicDEV.arz")
names = db.record_names()


def norm(s):
    return s.lower().replace("/", "\\")


print("scroll skills masteries skillpane records:")
for n in sorted(names):
    l = norm(n)
    if "scroll skills\\masteries" in l and "skillpane" in l:
        print("   ", n, "->", db.get_field_value(n, "bitmapName"))

# any OTHER mastery-pane records (besides the 9 + orphan) with skillpanebasebitmap?
print("\nALL skillpanebasebitmap records + template:")
for n in sorted(names):
    if norm(n).endswith("skillpanebasebitmap.dbr"):
        print("   ", n, "| tpl=", db.get_field_value(n, "templateName"))


def refs_to(sub):
    out = []
    for n in names:
        for k, tf in (db.get_fields(n) or {}).items():
            for v in tf.values:
                if isinstance(v, str) and sub in v.lower():
                    out.append((n, k.split("###")[0], v))
    return out


print("\n11-15-06 referenced by:", len(refs_to("mastery 9\\11-15-06")))
for r in refs_to("mastery 9\\11-15-06")[:8]:
    print("   ", r)
print("scroll-earth panectrl referenced by:", len(refs_to("scroll skills\\masteries\\earth\\panectrl")))
