"""Dump the FULL field set of panectrl.dbr + the two bitmap records for a few
masteries, to establish how the engine wires the pane background (direct tex on
panectrl vs a reference to skillpanebasebitmap.dbr). Read-only."""
import sys
from pathlib import Path
TOOLS = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\tools")
sys.path.insert(0, str(TOOLS))
from arz_patcher import ArzDatabase

ARZ = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
           r"\CustomMaps\SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz")
db = ArzDatabase.from_arz(ARZ)
NAMES = {n.lower().replace("/", "\\"): n for n in db.record_names()}
def rec(name): return NAMES.get(name.lower().replace("/", "\\"))

def dump(recname):
    r = rec(recname)
    print("\n==== %s ====" % recname)
    if not r:
        print("   <NO RECORD>"); return
    fl = db.get_fields(r)
    for k, tf in fl.items():
        real = k.split('###')[0]
        vals = tf.values
        show = vals[0] if len(vals) == 1 else vals
        print("   %-34s = %r" % (real, show))

for slot, folder in [(1, r"records\ingameui\player skills\mastery 1"),
                     (3, r"records\ingameui\player skills\mastery 3"),
                     (9, r"records\xpack\ui\skills\mastery 9")]:
    print("\n############### m%d ###############" % slot)
    dump(folder + r"\panectrl.dbr")
    dump(folder + r"\skillpanebasebitmap.dbr")
    dump(folder + r"\skillpanereallocationbitmap.dbr")
