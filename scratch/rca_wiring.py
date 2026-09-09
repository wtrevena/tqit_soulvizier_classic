"""Definitive wiring dump: base-game vs mod arz for the mastery-pane background
mechanism, plus the shared 'mastery base' folder, plus base InGameUI.arc entry proof.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from arz_patcher import ArzDatabase   # noqa
from arc_patcher import ArcArchive    # noqa

DEV = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassicDEV")
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition")
ARZ = DEV / "Database" / "SoulvizierClassicDEV.arz"
BASE_ARZ = GAME / "Database" / "database.arz"


def dump(d, rec, label):
    print("  [%s] %s" % (label, rec))
    fields = d.get_fields(rec)
    if fields is None:
        print("      <NO RECORD>")
        return
    for k, tf in fields.items():
        kf = k.split("###")[0]
        vals = tf.values
        # only show interesting (bitmap / bg / pane / tex / template) fields
        joined = ",".join(str(x) for x in vals)
        if ("bitmap" in kf.lower() or "pane" in kf.lower() or "background" in kf.lower()
                or ".tex" in joined.lower() or kf.lower() in ("templatename", "class", "actorname")):
            print("      %-34s = %s" % (kf, vals))


mod = ArzDatabase.from_arz(ARZ)
base = ArzDatabase.from_arz(BASE_ARZ)

print("=" * 80)
print("A) MASTERY 1 pane wiring: panectrl + leaf bitmap records (BASE vs MOD)")
print("=" * 80)
for rec in ("records\\ingameui\\player skills\\mastery 1\\panectrl.dbr",
            "records\\ingameui\\player skills\\mastery 1\\skillpanebasebitmap.dbr",
            "records\\ingameui\\player skills\\mastery 1\\masterybitmap.dbr"):
    dump(base, rec, "BASE")
    dump(mod, rec, "MOD ")
    print()

print("=" * 80)
print("B) SHARED 'mastery base' folder - every record + its bitmap fields (MOD)")
print("=" * 80)
mb = sorted(n for n in mod.record_names()
            if n.lower().replace("/", "\\").startswith("records\\ingameui\\player skills\\mastery base\\"))
for n in mb:
    dump(mod, n, "MOD ")
print("  --- same folder in BASE game (for the two suspicious leaves) ---")
for n in ("records\\ingameui\\player skills\\mastery base\\undobutton.dbr",
          "records\\ingameui\\player skills\\mastery base\\costperpointnumberbitmap.dbr"):
    dump(base, n, "BASE")

print("=" * 80)
print("C) Does base InGameUI.arc actually carry the mastery background + panel entries?")
print("=" * 80)
arc = ArcArchive.from_file(GAME / "Resources" / "InGameUI.arc")
names = {e.name.lower().replace("\\", "/") for e in arc.entries if e.name}
for probe in ["skills/warfareskillbackground01.tex",
              "skills/stealthskillbackground01.tex",
              "skills/spiritskillbackground01.tex",
              "skills/warfareskillreallocationbackground01.tex",
              "skills/warfarepanel01.tex"]:
    print("   %-52s in base InGameUI.arc: %s" % (probe, probe in names))
# how many skill backgrounds does base ship?
bgs = sorted(n for n in names if "skillbackground01" in n)
print("   base InGameUI.arc skillbackground01 entries: %d" % len(bgs))
for b in bgs:
    print("      ", b)

print("=" * 80)
print("D) Is 'scroll skills\\masteries\\earth' live? What references it?")
print("=" * 80)
target = "scroll skills\\masteries\\earth"
refs = []
for n in mod.record_names():
    fields = mod.get_fields(n) or {}
    for k, tf in fields.items():
        for v in tf.values:
            if isinstance(v, str) and target in v.lower():
                refs.append((n, k.split("###")[0], v))
print("  records whose FIELD VALUE references 'scroll skills\\masteries\\earth': %d" % len(refs))
for n, k, v in refs[:20]:
    print("     %s :: %s = %s" % (n, k, v))
# also list the full scroll skills\masteries\earth folder
print("  --- full 'scroll skills\\masteries\\earth' folder records ---")
for n in sorted(mod.record_names()):
    if "scroll skills\\masteries\\earth" in n.lower().replace("/", "\\"):
        print("     ", n)
