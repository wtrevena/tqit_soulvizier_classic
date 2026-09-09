"""Decisive template test: is BitmapSingle.tpl a valid TQAE template? Is
BitmapUIAware.tpl the required structure for the skill-pane background slot?
Also: SV098i origin + base-game structure for all 9 + reallocation + masterybitmap,
and controller-variant texture availability for rebuilding the plural arrays.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from arz_patcher import ArzDatabase   # noqa
from arc_patcher import ArcArchive    # noqa

GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition")
DEV = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassicDEV")
ARZ = DEV / "Database" / "SoulvizierClassicDEV.arz"
BASE_ARZ = GAME / "Database" / "database.arz"
SV098 = Path(r"C:/Users/willi/repos/tqit_soulvizier_classic") / "upstream" / "soulvizier_098i" / "Database" / "database.arz"

print("=" * 78)
print("(1) Template existence: is BitmapSingle.tpl valid in TQAE Templates.arc?")
print("=" * 78)
tpl = ArcArchive.from_file(GAME / "Toolset" / "Templates.arc")
tnames = {e.name.lower().replace("\\", "/") for e in tpl.entries if e.name}
for probe in ["ingameui/bitmapsingle.tpl", "ingameui/bitmapuiaware.tpl",
              "ingameui/skillpanectrl.tpl", "ingameui/skillpanebase.tpl",
              "ingameui/buttonstatictext.tpl", "ingameui/skillbutton.tpl"]:
    print("   %-38s present in Templates.arc: %s" % (probe, probe in tnames))
print("   (all bitmap*.tpl in Templates.arc:)")
for n in sorted(x for x in tnames if "/bitmap" in x or x.startswith("bitmap")):
    print("      ", n)

print("\n" + "=" * 78)
print("(2) SV098i ORIGIN: skillpanebasebitmap.dbr template + fields")
print("=" * 78)
sv = ArzDatabase.from_arz(SV098)
r = "records\\ingameui\\player skills\\mastery 1\\skillpanebasebitmap.dbr"
f = sv.get_fields(r) or {}
for k, tf in f.items():
    print("   SV098i", k.split("###")[0], "=", tf.values)

print("\n" + "=" * 78)
print("(3) BASE-GAME structure for all 9 (template + bitmapNames arity)")
print("=" * 78)
base = ArzDatabase.from_arz(BASE_ARZ)


def show(d, rec, tag):
    ff = d.get_fields(rec)
    if ff is None:
        print("   %s %s <NO REC>" % (tag, rec))
        return None, None
    tpl_ = None
    bn = None
    for k, tf in ff.items():
        kf = k.split("###")[0]
        if kf == "templateName":
            tpl_ = tf.values[0]
        if kf in ("bitmapNames", "bitmapName"):
            bn = (kf, tf.values)
    print("   %s tpl=%s  %s" % (tag, Path(str(tpl_)).name if tpl_ else "?", bn))
    return tpl_, bn


for slot, cls in [(1, "Warfare"), (2, "Defense"), (3, "Earth"), (4, "Storm"),
                  (5, "Stealth"), (6, "Hunting"), (7, "Spirit"), (8, "Nature")]:
    base_dir = "records\\ingameui\\player skills\\mastery %d\\" % slot
    show(base, base_dir + "skillpanebasebitmap.dbr", "m%d base-bg " % slot)
    show(base, base_dir + "skillpanereallocationbitmap.dbr", "m%d realloc " % slot)
r9 = "records\\xpack\\ui\\skills\\mastery 9\\skillpanebasebitmap.dbr"
show(base, r9, "m9 base-bg ")

print("\n" + "=" * 78)
print("(4) Controller-variant textures present in base InGameUI.arc? (for plural arrays)")
print("=" * 78)
arc = ArcArchive.from_file(GAME / "Resources" / "InGameUI.arc")
names = {e.name.lower().replace("\\", "/") for e in arc.entries if e.name}
for cls in ["Warfare", "Defense", "Earth", "Storm", "Stealth", "Hunting", "Spirit", "Nature"]:
    a = ("skills/%sskillbackground01.tex" % cls).lower()
    b = ("controller/skills/%sskillbackground01.tex" % cls).lower()
    ar = ("skills/%sskillreallocationbackground01.tex" % cls).lower()
    br = ("controller/skills/%sskillreallocationbackground01.tex" % cls).lower()
    print("   %-8s mouse=%s controller=%s  |realloc mouse=%s controller=%s"
          % (cls, a in names, b in names, ar in names, br in names))
