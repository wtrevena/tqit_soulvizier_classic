"""Dump all fields for Secret Place portal NPC records."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

db = ArzDatabase.from_arz(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz'))

# Collect matching records
matches = []
for name in db.record_names():
    lower = name.lower()
    if 'portal to act' in lower:
        matches.append(name)
    elif 'portal to hallway' in lower:
        matches.append(name)
    elif name.lower().replace('/', '\\') == r'records\drxmap\xurder\portaldudes\warriv.dbr':
        matches.append(name)

# Also try exact path in case of different slash style
warriv_paths = [
    r'records\drxmap\xurder\portaldudes\warriv.dbr',
    'records/drxmap/xurder/portaldudes/warriv.dbr',
]
for p in warriv_paths:
    if db.has_record(p) and p not in matches:
        matches.append(p)

matches = sorted(set(matches))

for record_path in matches:
    rec_type = db._record_types.get(record_path, '(unknown)')
    fields = db.get_fields(record_path)
    if fields is None:
        print(f"\n{'='*80}")
        print(f"RECORD: {record_path}")
        print(f"TYPE: {rec_type}")
        print("(no fields / failed to decode)")
        continue

    print(f"\n{'='*80}")
    print(f"RECORD: {record_path}")
    print(f"TYPE: {rec_type}")
    print("-" * 40)
    for key, tf in fields.items():
        real_name = key.split('###')[0]
        val = tf.value
        if isinstance(val, list):
            val_str = repr(val)
        else:
            val_str = repr(val)
        print(f"  {real_name}: {val_str}")
    print()
