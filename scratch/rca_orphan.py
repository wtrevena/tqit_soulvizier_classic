import sys
from pathlib import Path
REPO = Path(r"C:/Users/willi/repos/tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / "tools"))
from arz_patcher import ArzDatabase
DEV = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassicDEV")
db = ArzDatabase.from_arz(DEV / "Database" / "SoulvizierClassicDEV.arz")
names = db.record_names()
nl = [n.lower().replace('/', '\') for n in names]
# all skillpanebasebitmap under scroll skills\masteries
print("scroll skills\masteries\* skillpane records:")
for n in sorted(names):
    l = n.lower().replace('/','\')
    if 'scroll skills\masteries' in l and 'skillpane' in l:
        print("   ", n, "->", db.get_field_value(n,'bitmapName'))
# 11-15-06 liveness: is it referenced by any panectrl / field value?
tgt = "mastery 9\11-15-06"
refs = [(n,k.split('###')[0],v) for n in names for k,tf in (db.get_fields(n) or {}).items() for v in tf.values if isinstance(v,str) and tgt in v.lower()]
print("\n11-15-06 referenced by (field values):", len(refs))
for r in refs[:10]: print("   ", r)
# Is scroll-earth panectrl referenced anywhere (is the whole orphan tree reachable)?
for probe in ["scroll skills\masteries\earth\panectrl", "scroll skills\masteries\earth\mastery.dbr"]:
    refs2=[(n,k.split('###')[0]) for n in names for k,tf in (db.get_fields(n) or {}).items() for v in tf.values if isinstance(v,str) and probe in v.lower()]
    print("refs to %r: %d"%(probe,len(refs2)), refs2[:5])
