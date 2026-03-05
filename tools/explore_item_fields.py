"""Quick exploration of item fields to understand what's available."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

DB_PATH = Path(__file__).parent.parent / "work/SoulvizierClassic/Database/SoulvizierClassic.arz"
db = ArzDatabase.from_arz(DB_PATH)

# Check known items
items = [
    r"records\xpack\item\equipmentweapons\sword\u_l_002.dbr",
    r"records\item\equipmentring\u_l_markofares.dbr",
    r"records\item\equipmentweapon\staff\u_e_hekastaff.dbr",
    r"records\item\equipmentarmband\us_l_conqueror'spanoply.dbr",
]

for item_path in items:
    print(f"\n{'='*80}")
    print(f"ITEM: {item_path}")
    print(f"{'='*80}")
    fields = db.get_fields(item_path)
    if fields is None:
        # try lowercase
        found = [r for r in db.record_names() if r.lower() == item_path.lower()]
        if found:
            print(f"  Found as: {found[0]}")
            fields = db.get_fields(found[0])
        else:
            print("  NOT FOUND")
            continue
    for key, tf in fields.items():
        name = key.split('###')[0]
        vals = tf.values
        if len(vals) == 1:
            print(f"  {name} = {vals[0]}  (type={tf.dtype})")
        else:
            print(f"  {name} = {vals}  (type={tf.dtype})")
