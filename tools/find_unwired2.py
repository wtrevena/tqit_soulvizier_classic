#!/usr/bin/env python3
"""Check .arz database for references to custom areas and find unwired content."""
import sys
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

print("Loading SV 0.98i database...")
sv_arz = ArzDatabase.from_arz(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz'))

keywords = ['bossarena', 'boss_arena', 'uberdungeon', 'uber_dungeon', 'crypt_floor',
            'secret_place', 'gardenofmerchants', 'garden_of_merchants',
            'bloodcave', 'blood_cave', 'xbloodcave', 'coldtombs', 'spartacrypt']

print("\n" + "="*80)
print("PART 1: DATABASE RECORDS whose PATH matches custom area keywords")
print("="*80)

for record_path in sv_arz._raw_records:
    rp_lower = record_path.lower()
    for kw in keywords:
        if kw in rp_lower:
            print(f"  {record_path}")
            break

print("\n" + "="*80)
print("PART 2: DATABASE RECORDS referencing custom areas in FIELD VALUES")
print("="*80)

area_refs = {}
count = 0
for record_path in sv_arz._raw_records:
    name_id, compressed = sv_arz._raw_records[record_path]
    fields = sv_arz._decode_fields(compressed)
    for field_name, typed_field in fields.items():
        if typed_field.dtype == 2:  # string type
            for val in typed_field.values:
                if isinstance(val, str):
                    vl = val.lower()
                    for kw in keywords:
                        if kw in vl:
                            if kw not in area_refs:
                                area_refs[kw] = []
                            area_refs[kw].append((record_path, field_name, val))
                            break
    count += 1
    if count % 10000 == 0:
        print(f"  Scanned {count} records...")

for kw in sorted(area_refs.keys()):
    refs = area_refs[kw]
    print(f"\n  '{kw}' referenced by {len(refs)} record fields:")
    for rp, fn, val in refs[:20]:
        print(f"    {rp} -> {fn}: {val}")
    if len(refs) > 20:
        print(f"    ... and {len(refs) - 20} more")

print("\n" + "="*80)
print("PART 3: WIP/DRAFT RECORDS (test, temp, wip, unused, placeholder, old_)")
print("="*80)

wip_keywords = ['test_level', 'test_area', 'temp_', '_temp/', 'wip_', '/wip/',
                'placeholder', 'dummy/', 'unused/', 'old_/', 'backup_', '/draft/']
wip_found = []
for record_path in sv_arz._raw_records:
    rp_lower = record_path.lower()
    for kw in wip_keywords:
        if kw in rp_lower:
            wip_found.append((record_path, kw))
            break

if wip_found:
    for rp, kw in wip_found[:30]:
        print(f"  [{kw}] {rp}")
else:
    print("  None found")

print("\n" + "="*80)
print("PART 4: DRX RECORD CATEGORIES")
print("="*80)

drx_categories = Counter()
for record_path in sv_arz._raw_records:
    if record_path.lower().startswith('records/drx'):
        parts = record_path.split('/')
        if len(parts) >= 3:
            cat = '/'.join(parts[:3])
        else:
            cat = record_path
        drx_categories[cat] += 1

for cat, count in sorted(drx_categories.items()):
    print(f"  {cat}: {count} records")
print(f"\n  Total drx records: {sum(drx_categories.values())}")

print("\n" + "="*80)
print("PART 5: PROXIES CUSTOM (boss proxies and custom spawns)")
print("="*80)

for record_path in sv_arz._raw_records:
    if 'proxies custom' in record_path.lower() or 'proxies_custom' in record_path.lower():
        print(f"  {record_path}")
