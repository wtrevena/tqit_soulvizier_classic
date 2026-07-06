import sys
from pathlib import Path
sys.path.insert(0, r'C:\Users\willi\repos\tqit_soulvizier_classic\tools')
from arz_patcher import ArzDatabase
BS = chr(92)
_dbpath = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz'
db = ArzDatabase.from_arz(Path(_dbpath))
rows = []
for name in db.record_names():
    nl = name.lower()
    if 'yeti' not in nl:
        continue
    if BS + 'creature' not in nl and '/creature' not in nl:
        continue
    cls = db.get_field_value(name, 'monsterClassification')
    loot = db.get_field_value(name, 'lootFinger2Item1')
    chance = db.get_field_value(name, 'chanceToEquipFinger2')
    rows.append((str(cls), chance, name, loot))
rows.sort(key=lambda r: (r[0], r[2]))
print(f"{'CLASSIFICATION':14s} {'chanceF2':9s} RECORD")
for cls, chance, name, loot in rows:
    ln = name.split(BS)[-1].replace('.dbr', '')
    lootn = ''
    if loot:
        lootn = (loot[0] if isinstance(loot, list) else str(loot)).split(BS)[-1]
    drops = chance is not None and str(chance) not in ('', 'None') and float(chance) > 0 and loot
    flag = '  <== DROPS' if drops else ''
    print(f"{cls:14s} {str(chance):9s} {ln:38s} loot={lootn}{flag}")
