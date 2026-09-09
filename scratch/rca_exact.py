import sys
from pathlib import Path
REPO = Path(r"C:/Users/willi/repos/tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / "tools"))
from arz_patcher import ArzDatabase
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition")
DEV = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassicDEV")
base = ArzDatabase.from_arz(GAME / "Database" / "database.arz")
mod = ArzDatabase.from_arz(DEV / "Database" / "SoulvizierClassicDEV.arz")
def full(d, rec, tag):
    print("== %s :: %s" % (tag, rec))
    print("   _record_types =", repr(d._record_types.get(rec)))
    ff = d.get_fields(rec)
    if ff is None:
        print("   <NO REC>"); return
    for k, tf in ff.items():
        print("   [dtype=%d] %-22s = %s" % (tf.dtype, k.split('###')[0], tf.values))
for rec in (r"records\ingameui\player skills\mastery 1\skillpanebasebitmap.dbr",
            r"records\ingameui\player skills\mastery 1\skillpanereallocationbitmap.dbr"):
    full(base, rec, "BASE"); full(mod, rec, "MOD "); print()
full(base, r"records\xpack\ui\skills\mastery 9\skillpanebasebitmap.dbr", "BASE m9")
full(mod, r"records\xpack\ui\skills\mastery 9\skillpanebasebitmap.dbr", "MOD  m9")
