"""
Compare potion-related records between SV 0.9, SV beta04.1, and SV 0.98i.

Traces: potion items -> loot tables -> merchant tables
to find where potions were removed from drops and merchants.
"""
import struct
import zlib
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def find_potion_records(db: ArzDatabase):
    """Find all potion item records."""
    potions = {}
    for name, fields in db.records.items():
        name_lower = name.lower()
        if 'potion' not in name_lower:
            continue
        if any(kw in name_lower for kw in ('potionskill', 'potionexp', 'potionattri',
                                             'skillpotion', 'exppotion', 'attributepotion',
                                             'xppotion', 'statpotion')):
            potions[name] = fields
    return potions


def find_loot_tables_referencing(db: ArzDatabase, target_pattern: str):
    """Find loot tables that reference records matching pattern."""
    pattern = re.compile(target_pattern, re.IGNORECASE)
    results = {}
    for name, fields in db.records.items():
        template = str(fields.get('templateName', '')).lower()
        if 'loottable' not in template and 'lootitemtable' not in template:
            if 'table' not in name.lower():
                continue

        for key, val in fields.items():
            vals = val if isinstance(val, list) else [val]
            for v in vals:
                if isinstance(v, str) and pattern.search(v):
                    if name not in results:
                        results[name] = {}
                    results[name][key] = v
                    break
    return results


def find_merchant_tables(db: ArzDatabase):
    """Find merchant/vendor table records."""
    merchants = {}
    for name, fields in db.records.items():
        name_lower = name.lower()
        if 'merchant' in name_lower or 'vendor' in name_lower:
            merchants[name] = fields
    return merchants


def find_all_references_to(db: ArzDatabase, target_names: set):
    """Find all records that reference any of the target record names."""
    refs = defaultdict(list)
    target_lower = {t.lower() for t in target_names}
    for name, fields in db.records.items():
        for key, val in fields.items():
            vals = val if isinstance(val, list) else [val]
            for v in vals:
                if isinstance(v, str) and v.lower() in target_lower:
                    refs[name].append((key, v))
    return dict(refs)


def analyze_version(label: str, db: ArzDatabase):
    """Analyze potions in a single version."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")

    potions = find_potion_records(db)
    print(f"\nPotion item records: {len(potions)}")
    for name in sorted(potions):
        fields = potions[name]
        cls = fields.get('Class', '?')
        desc = fields.get('FileDescription', '')
        level = fields.get('levelRequirement', '?')
        print(f"  {name}")
        print(f"    Class={cls}, Level={level}, Desc={desc}")

    potion_names = set(potions.keys())

    refs = find_all_references_to(db, potion_names)
    print(f"\nRecords referencing potions: {len(refs)}")
    for ref_name in sorted(refs):
        ref_fields = refs[ref_name]
        ref_name_lower = ref_name.lower()
        category = "LOOT" if "loot" in ref_name_lower else \
                   "MERCHANT" if "merchant" in ref_name_lower or "vendor" in ref_name_lower else \
                   "OTHER"
        print(f"  [{category}] {ref_name}")
        for key, val in ref_fields:
            print(f"    {key} = {val}")

    loot_refs = find_loot_tables_referencing(db, r'potion(?:skill|exp|attri)')
    print(f"\nLoot tables with potion refs: {len(loot_refs)}")
    for lt_name in sorted(loot_refs):
        print(f"  {lt_name}")
        for k, v in loot_refs[lt_name].items():
            weight_key = k.replace('lootName', 'lootWeight')
            weight = db.records.get(lt_name, {}).get(weight_key, '?')
            print(f"    {k}={v}  (weight: {weight})")

    return potions, refs, loot_refs


def main():
    versions = {}

    if len(sys.argv) < 2:
        print("Usage: compare_potion_drops.py <sv09.arz> [sv04.arz] [sv098.arz]")
        sys.exit(1)

    labels = ['SV 0.9', 'SV beta04.1', 'SV 0.98i']
    for i, path_str in enumerate(sys.argv[1:]):
        path = Path(path_str)
        label = labels[i] if i < len(labels) else f"Version {i}"
        print(f"\nLoading {label}: {path}")
        db = ArzDatabase.from_arz(path)
        potions, refs, loot_refs = analyze_version(label, db)
        versions[label] = (db, potions, refs, loot_refs)

    if len(versions) >= 2:
        print(f"\n{'='*60}")
        print(f"  COMPARISON")
        print(f"{'='*60}")

        all_labels = list(versions.keys())
        first_label = all_labels[0]
        last_label = all_labels[-1]

        first_potions = versions[first_label][1]
        last_potions = versions[last_label][1]
        first_refs = versions[first_label][2]
        last_refs = versions[last_label][2]
        first_loot = versions[first_label][3]
        last_loot = versions[last_label][3]

        print(f"\nPotion items in {first_label} but not {last_label}:")
        for name in sorted(set(first_potions) - set(last_potions)):
            print(f"  REMOVED: {name}")

        print(f"\nPotion items in {last_label} but not {first_label}:")
        for name in sorted(set(last_potions) - set(first_potions)):
            print(f"  ADDED: {name}")

        print(f"\nLoot table references in {first_label} but not {last_label}:")
        for name in sorted(set(first_loot) - set(last_loot)):
            print(f"  REMOVED: {name}")

        print(f"\nLoot table refs in both but with different weights:")
        common_loot = set(first_loot) & set(last_loot)
        for name in sorted(common_loot):
            db_first = versions[first_label][0]
            db_last = versions[last_label][0]
            for key in first_loot[name]:
                weight_key = key.replace('lootName', 'lootWeight')
                w1 = db_first.records.get(name, {}).get(weight_key, '?')
                w2 = db_last.records.get(name, {}).get(weight_key, '?')
                if w1 != w2:
                    print(f"  {name}: {key} weight {w1} -> {w2}")

        print(f"\nAll references in {first_label} but not {last_label}:")
        for name in sorted(set(first_refs) - set(last_refs)):
            category = "LOOT" if "loot" in name.lower() else \
                       "MERCHANT" if "merchant" in name.lower() or "vendor" in name.lower() else \
                       "OTHER"
            print(f"  [{category}] {name}")


if __name__ == '__main__':
    main()
