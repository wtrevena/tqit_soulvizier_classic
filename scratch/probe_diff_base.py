"""Compare the mod arz's mastery-UI records against the BASE game arz, to find any
STRUCTURAL divergence (template, field set, values) that could break rendering even
though the bitmap path resolves. Read-only."""
import sys
from pathlib import Path
TOOLS = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\tools")
sys.path.insert(0, str(TOOLS))
from arz_patcher import ArzDatabase

MOD = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz")
BASE = Path(r"C:\Program Files (x86)\Steam\steamapps\common"
            r"\Titan Quest Anniversary Edition\Database\database.arz")

mdb = ArzDatabase.from_arz(MOD)
bdb = ArzDatabase.from_arz(BASE)
MI = {n.lower().replace("/", "\\"): n for n in mdb.record_names()}
BI = {n.lower().replace("/", "\\"): n for n in bdb.record_names()}

def fields(db, idx, name):
    r = idx.get(name.lower().replace("/", "\\"))
    if not r:
        return None
    out = {}
    for k, tf in db.get_fields(r).items():
        real = k.split('###')[0]
        out[real] = tf.values[0] if len(tf.values) == 1 else list(tf.values)
    return out

def cmp_rec(name):
    m = fields(mdb, MI, name)
    b = fields(bdb, BI, name)
    print("\n==== %s ====" % name)
    print("   MOD present: %s | BASE present: %s" % (m is not None, b is not None))
    if m is None or b is None:
        if m is not None:
            print("   (MOD-only record; template=%r)" % m.get("templateName"))
        if b is not None:
            print("   (BASE-only record; template=%r)" % b.get("templateName"))
        return
    allk = sorted(set(m) | set(b))
    for k in allk:
        mv, bv = m.get(k, "<absent>"), b.get(k, "<absent>")
        if mv != bv:
            print("   DIFF %-28s MOD=%r  BASE=%r" % (k, mv, bv))
    if m == b:
        print("   (identical)")

for slot, folder in [(1, r"records\ingameui\player skills\mastery 1"),
                     (5, r"records\ingameui\player skills\mastery 5"),
                     (9, r"records\xpack\ui\skills\mastery 9")]:
    print("\n############### m%d ###############" % slot)
    for suf in ("panectrl.dbr", "skillpanebasebitmap.dbr",
                "skillpanereallocationbitmap.dbr", "masterybitmap.dbr"):
        cmp_rec(folder + "\\" + suf)

# Base pane (shared) + base-game's own background record to see the vanilla-correct value
print("\n############### shared base pane ###############")
cmp_rec(r"records\ingameui\player skills\mastery base\baseskillpane.dbr")

print("\n############### BASE-GAME vanilla background value (ground truth) ###############")
for slot, folder in [(1, r"records\ingameui\player skills\mastery 1")]:
    b = fields(bdb, BI, folder + r"\skillpanebasebitmap.dbr")
    print("  base m1 skillpanebasebitmap.dbr =", b)
