"""Gather base-game repoint targets for the residual 'mastery base' chrome +
the orphan earth scroll pane, and confirm arz-patcher can rewrite template/fields.
"""
import sys
from pathlib import Path

REPO = Path(r"C:/Users/willi/repos/tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / "tools"))
from arz_patcher import ArzDatabase   # noqa
from arc_patcher import ArcArchive    # noqa

GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition")
BASE_ARZ = GAME / "Database" / "database.arz"
base = ArzDatabase.from_arz(BASE_ARZ)


def dumpall(d, rec):
    ff = d.get_fields(rec)
    print("  ", rec)
    if ff is None:
        print("       <NO REC>")
        return
    for k, tf in ff.items():
        kf = k.split("###")[0]
        j = ",".join(str(x) for x in tf.values)
        if "bitmap" in kf.lower() or ".tex" in j.lower() or kf.lower() == "templatename":
            print("       %-30s = %s" % (kf, tf.values))


print("=== BASE-GAME 'mastery base' chrome (the repoint targets) ===")
for leaf in ("undobutton.dbr", "undomasteryselectionbutton.dbr",
             "costperpointnumberbitmap.dbr", "playergoldnumberbitmap.dbr",
             "reallocationbitmap.dbr", "confirmbutton.dbr"):
    dumpall(base, "records\\ingameui\\player skills\\mastery base\\" + leaf)

print("\n=== arc: confirm those base textures exist in base InGameUI.arc ===")
arc = ArcArchive.from_file(GAME / "Resources" / "InGameUI.arc")
names = {e.name.lower().replace("\\", "/") for e in arc.entries if e.name}
print("   count InGameUI entries under skills/ :", sum(1 for n in names if n.startswith("skills/")))
for probe in ["skills/undobtnup01.tex", "skills/undobtnupdiablo01.tex",
              "skills/costperpoint01.tex", "skills/currentgold01.tex",
              "skills/undomasterybtnup01.tex"]:
    print("   %-34s : %s" % (probe, probe in names))
# show what undo/gold/cost tex actually exist
print("   --- skills/*undo* / *gold* / *costperpoint* entries in base InGameUI.arc ---")
for n in sorted(names):
    if n.startswith("skills/") and ("undo" in n or "gold" in n or "costperpoint" in n or "currentgold" in n):
        print("      ", n)
