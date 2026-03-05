"""Find all spawn pool records containing Ichthian monsters.

Scans the entire database for any record where a field value contains
"ichthian" (case-insensitive), then finds proxy records that reference
those pool paths.

Usage:
    py tools/find_ichthian_pools.py <database.arz>
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # ---- Phase 1: Find all records that reference ichthian monsters ----
    print("=" * 70)
    print("PHASE 1: Records containing 'ichthian' in any field value")
    print("=" * 70)

    ichthian_records = {}  # record_name -> {field_name: [values]}

    for record_name in db.record_names():
        fields = db.get_fields(record_name)
        if not fields:
            continue

        has_ichthian = False
        ichthian_fields = {}

        for key, tf in fields.items():
            fn = key.split('###')[0]
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'ichthian' in v.lower():
                        has_ichthian = True
                        ichthian_fields[fn] = tf.values
                        break

        if has_ichthian:
            ichthian_records[record_name] = ichthian_fields

    print(f"\nFound {len(ichthian_records)} records referencing ichthian monsters.\n")

    # Separate pool records (those with nameN fields) from others
    pool_records = {}
    other_records = {}

    for record_name, ich_fields in ichthian_records.items():
        fields = db.get_fields(record_name)
        has_name_fields = any(
            key.split('###')[0].startswith('name') and
            key.split('###')[0][4:].isdigit()
            for key in fields
        )
        if has_name_fields:
            pool_records[record_name] = ich_fields
        else:
            other_records[record_name] = ich_fields

    # ---- Print pool records in detail ----
    print("-" * 70)
    print(f"SPAWN POOL RECORDS (with nameN fields): {len(pool_records)}")
    print("-" * 70)

    pool_paths = set()
    for record_name in sorted(pool_records.keys()):
        fields = db.get_fields(record_name)
        pool_paths.add(record_name)

        print(f"\n  POOL: {record_name}")

        # Print all nameN fields (monster entries)
        name_fields = {}
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn.startswith('name') and fn[4:].isdigit():
                name_fields[fn] = tf.values

        for fn in sorted(name_fields, key=lambda x: int(x[4:])):
            vals = name_fields[fn]
            marker = " <-- ICHTHIAN" if any(
                isinstance(v, str) and 'ichthian' in v.lower() for v in vals
            ) else ""
            print(f"    {fn}: {vals}{marker}")

        # Print spawn min/max
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn in ('spawnMin', 'spawnMax'):
                print(f"    {fn}: {tf.values}")

        # Print champion fields
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if fn in ('championChance', 'championMin', 'championMax'):
                print(f"    {fn}: {tf.values}")

    # ---- Print other (non-pool) records ----
    print("\n" + "-" * 70)
    print(f"OTHER RECORDS referencing ichthian: {len(other_records)}")
    print("-" * 70)

    for record_name in sorted(other_records.keys()):
        fields = db.get_fields(record_name)
        print(f"\n  RECORD: {record_name}")
        for key, tf in fields.items():
            fn = key.split('###')[0]
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and 'ichthian' in v.lower():
                        print(f"    {fn}: {tf.values}")
                        break

    # ---- Phase 2: Find proxy records referencing pool paths ----
    print("\n" + "=" * 70)
    print("PHASE 2: Proxy records referencing ichthian pool paths")
    print("=" * 70)

    if not pool_paths:
        print("\n  No pool records found, skipping proxy search.")
        return

    print(f"\nSearching for references to {len(pool_paths)} pool paths...")

    proxy_fields_of_interest = [
        'poolNormal1', 'poolNormal2', 'poolNormal3',
        'poolEpic1', 'poolEpic2', 'poolEpic3',
        'poolLegendary1', 'poolLegendary2', 'poolLegendary3',
        'pool1', 'pool2', 'pool3',
    ]

    proxy_records = defaultdict(dict)  # record_name -> {field: value}

    for record_name in db.record_names():
        fields = db.get_fields(record_name)
        if not fields:
            continue

        for key, tf in fields.items():
            fn = key.split('###')[0]
            if tf.values:
                for v in tf.values:
                    if isinstance(v, str) and v in pool_paths:
                        proxy_records[record_name][fn] = v

    print(f"\nFound {len(proxy_records)} proxy records referencing ichthian pools.\n")

    for record_name in sorted(proxy_records.keys()):
        fields = db.get_fields(record_name)
        print(f"  PROXY: {record_name}")
        for fn, val in sorted(proxy_records[record_name].items()):
            print(f"    {fn}: {val}")

        # Also print other pool fields from this proxy for context
        if fields:
            for key, tf in fields.items():
                fn_full = key.split('###')[0]
                if fn_full not in proxy_records[record_name]:
                    if any(fn_full.startswith(p) for p in
                           ('poolNormal', 'poolEpic', 'poolLegendary', 'pool')):
                        if tf.values and isinstance(tf.values[0], str) and tf.values[0]:
                            print(f"    {fn_full}: {tf.values[0]}  (other pool)")
        print()

    # ---- Summary ----
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Ichthian pool records: {len(pool_records)}")
    print(f"  Other ichthian records: {len(other_records)}")
    print(f"  Proxy records pointing to ichthian pools: {len(proxy_records)}")


if __name__ == '__main__':
    main()
