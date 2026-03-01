"""Investigate SV's soul skill mechanism and compare SV 0.9 vs 0.98i wiring."""
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

sv09_path = Path(sys.argv[1])
sv098_path = Path(sys.argv[2])

print("=== Loading SV 0.9 ===")
db09 = ArzDatabase.from_arz(sv09_path)

print("\n=== SV 0.9: Soul skill records ===")
for name in sorted(db09.records):
    nl = name.lower()
    if 'soulskill' in nl:
        fields = db09.records[name]
        print(f"\n{name}")
        print(f"  Class={fields.get('Class', '?')}, template={fields.get('templateName', '?')}")
        for k, v in sorted(fields.items()):
            if isinstance(v, str) and 'soul' in v.lower():
                print(f"  {k} = {v}")
            elif k in ('skillChance', 'skillActiveDuration', 'spawnObjects', 'spawnObjectsCount',
                       'projectileName', 'skillDisplayName', 'FileDescription'):
                print(f"  {k} = {v}")

print("\n=== SV 0.9: How many monsters reference soul items ===")
soul_path = 'equipmentring\\soul'
soul_path2 = 'equipmentring/soul'
sv09_soul_monsters = 0
sv09_soul_assignments = 0
for name, fields in db09.records.items():
    found = False
    for key, val in fields.items():
        if isinstance(val, str):
            vl = val.lower()
            if ('\\soul\\' in vl or '/soul/' in vl) and 'equipmentring' in vl:
                sv09_soul_assignments += 1
                found = True
    if found:
        sv09_soul_monsters += 1

print(f"  Monsters/records with soul assignments: {sv09_soul_monsters}")
print(f"  Total soul assignment fields: {sv09_soul_assignments}")

# Count soul items in 0.9
sv09_souls = set()
for name in db09.records:
    nl = name.lower()
    if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
        sv09_souls.add(nl)
print(f"  Soul items in SV 0.9: {len(sv09_souls)}")

# Check how soulskills reference soul items
print("\n=== SV 0.9: Soulskill -> soul item linkage ===")
for name in sorted(db09.records):
    nl = name.lower()
    if 'soulskill' in nl:
        fields = db09.records[name]
        for k, v in fields.items():
            if isinstance(v, str) and 'equipmentring' in v.lower():
                print(f"  {name}: {k} = {v}")
            if isinstance(v, list):
                for vi in v:
                    if isinstance(vi, str) and 'equipmentring' in vi.lower():
                        print(f"  {name}: {k}[] = {vi}")

# Check for proxy/spawner records
print("\n=== SV 0.9: Monster proxy/spawner records referencing souls ===")
for name, fields in db09.records.items():
    nl = name.lower()
    if 'proxy' in nl or 'spawn' in nl or 'pool' in nl:
        for key, val in fields.items():
            if isinstance(val, str) and 'soul' in val.lower() and 'equipmentring' in val.lower():
                print(f"  {name}: {key} = {val}")

# Check if there's a global soul loot skill or on-death mechanism
print("\n=== SV 0.9: Records with 'soul' in skill/buff fields ===")
soul_skill_refs = 0
for name, fields in db09.records.items():
    for key, val in fields.items():
        if isinstance(val, str) and 'soulskill' in val.lower():
            soul_skill_refs += 1
            if soul_skill_refs <= 30:
                print(f"  {name}: {key} = {val}")
print(f"Total references to soulskill records: {soul_skill_refs}")
