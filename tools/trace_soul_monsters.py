"""Deep trace of soul-to-monster assignments in SV 0.98i.

The soul system assigns souls directly to monster records via loot
equipment slots, not through loot tables. This script maps which
monsters drop which souls and identifies gaps.
"""
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

db = ArzDatabase.from_arz(Path(sys.argv[1]))

print("=== Looking for all soul-bearing loot fields in monsters ===")

soul_assignment_fields = defaultdict(list)  # field_name -> [(monster, soul_path)]
monster_soul_map = {}  # monster_name -> (field, soul_path, soul_chance)
orphan_souls = set()  # souls that aren't assigned to any monster

all_soul_items = set()
for name in db.records:
    nl = name.lower()
    if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
        all_soul_items.add(name.lower())

print(f"Total soul items: {len(all_soul_items)}")

assigned_souls = set()
monsters_with_souls = 0

# Check ALL monster/creature records for ANY field referencing soul items
for name, fields in db.records.items():
    cls = str(fields.get('Class', '')).lower()
    template = str(fields.get('templateName', '')).lower()

    # We want Monster and creature records
    is_monster = 'monster' in cls or 'monster' in template or \
                 'creature' in name.lower().replace('\\', '/').split('/')[1:2]

    if not is_monster:
        continue

    found_soul = False
    for key, val in fields.items():
        if isinstance(val, str):
            vl = val.lower()
            if ('\\soul\\' in vl or '/soul/' in vl) and 'equipmentring' in vl:
                found_soul = True
                assigned_souls.add(vl)
                soul_assignment_fields[key].append((name, val))

    if found_soul:
        monsters_with_souls += 1

print(f"\nMonster/creature records with soul drops: {monsters_with_souls}")
print(f"Unique souls assigned to monsters: {len(assigned_souls)}")
print(f"\nLoot fields used for soul assignments:")
for field, entries in sorted(soul_assignment_fields.items()):
    print(f"  {field}: {len(entries)} assignments")

# Now check ALL records, not just monsters
print("\n=== Checking ALL record types for soul references ===")
all_refs = defaultdict(list)
for name, fields in db.records.items():
    for key, val in fields.items():
        if isinstance(val, str):
            vl = val.lower()
            if ('\\soul\\' in vl or '/soul/' in vl) and 'equipmentring' in vl:
                all_refs[key].append((name, val))
                assigned_souls.add(vl)

print(f"All records with soul refs: {sum(len(v) for v in all_refs.values())}")
print(f"Unique souls referenced anywhere: {len(assigned_souls)}")
for field, entries in sorted(all_refs.items(), key=lambda x: -len(x[1])):
    print(f"  {field}: {len(entries)}")

orphans = all_soul_items - assigned_souls
print(f"\nOrphan souls (not referenced by anything): {len(orphans)}")
for s in sorted(orphans)[:30]:
    print(f"  {s}")
if len(orphans) > 30:
    print(f"  ... and {len(orphans) - 30} more")

# Check the xpack creature records specifically
print("\n=== xpack creature records with souls ===")
for name, fields in db.records.items():
    nl = name.lower()
    if 'xpack' in nl and ('creature' in nl or 'monster' in nl):
        for key, val in fields.items():
            if isinstance(val, str) and 'soul' in val.lower():
                print(f"  {name}: {key} = {val}")
