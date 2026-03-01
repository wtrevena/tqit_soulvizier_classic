"""Trace how souls get dropped by monsters in SV 0.98i."""
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

db = ArzDatabase.from_arz(Path(sys.argv[1]))

soul_path = 'equipmentring\\soul'
soul_path2 = 'equipmentring/soul'

soul_refs = {}
for name, fields in db.records.items():
    for key, val in fields.items():
        if isinstance(val, str) and (soul_path in val.lower() or soul_path2 in val.lower()):
            if name not in soul_refs:
                soul_refs[name] = []
            soul_refs[name].append((key, val))

print(f"Records referencing soul items: {len(soul_refs)}")
categories = Counter()
for name in soul_refs:
    parts = name.lower().replace('\\', '/').split('/')
    if len(parts) >= 3:
        cat = '/'.join(parts[1:3])
    else:
        cat = parts[0] if parts else 'unknown'
    categories[cat] += 1

for cat, count in categories.most_common(20):
    print(f"  {cat}: {count}")

print("\n=== Sample soul drop chains ===")
shown = 0
for name in sorted(soul_refs):
    if shown >= 20:
        break
    refs = soul_refs[name]
    template = db.records[name].get('templateName', '?')
    cls = db.records[name].get('Class', '?')
    print(f"\n{name}")
    print(f"  template={template}, Class={cls}")
    for key, val in refs[:5]:
        weight_key = key.replace('lootName', 'lootWeight')
        weight = db.records[name].get(weight_key, '?')
        chance_key = key.replace('lootName', 'lootChance')
        chance = db.records[name].get(chance_key, '?')
        print(f"  {key} = {val}")
        print(f"    weight={weight}, chance={chance}")
    shown += 1

print("\n=== Soul loot tables with weights ===")
soul_tables = [n for n in soul_refs if 'loottable' in n.lower() or 'loot' in n.lower()]
print(f"Soul-related loot tables: {len(soul_tables)}")
for name in sorted(soul_tables)[:30]:
    fields = db.records[name]
    cls = fields.get('Class', '?')
    print(f"\n  {name} [{cls}]")
    for key, val in sorted(fields.items()):
        if key.startswith('lootName') or key.startswith('lootWeight') or key.startswith('lootChance'):
            print(f"    {key} = {val}")
