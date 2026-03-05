"""
Find all spawn pool records for Act 2 Egypt that are in underground caves,
tombs, or contain insectoid/cryptworm monsters.

Goal: identify pools suitable for adding the Cold Worm boss.

Usage:
    py tools/find_egypt_pools.py <database.arz>
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase, DATA_TYPE_STRING, DATA_TYPE_INT, DATA_TYPE_FLOAT


def get_field_val(fields, field_name):
    """Get a field value by base name, handling ### suffixes."""
    if field_name in fields:
        return fields[field_name]
    for key, tf in fields.items():
        if key.split('###')[0] == field_name:
            return tf
    return None


def get_all_nameN_fields(fields):
    """Extract all nameN and weightN pairs from a spawn pool record."""
    names = {}
    weights = {}
    champions = {}

    for key, tf in fields.items():
        rk = key.split('###')[0]
        # name1, name2, ... nameN
        m = re.match(r'^name(\d+)$', rk)
        if m:
            idx = int(m.group(1))
            if tf.values:
                val = tf.values[0] if len(tf.values) == 1 else tf.values
                names[idx] = (val, tf.dtype)
            continue
        # weight1, weight2, ... weightN
        m = re.match(r'^weight(\d+)$', rk)
        if m:
            idx = int(m.group(1))
            if tf.values:
                weights[idx] = tf.values[0]
            continue
        # nameChampion1, nameChampion2, ...
        m = re.match(r'^nameChampion(\d+)$', rk, re.IGNORECASE)
        if m:
            idx = int(m.group(1))
            if tf.values:
                val = tf.values[0] if len(tf.values) == 1 else tf.values
                champions[idx] = (val, tf.dtype)
            continue

    return names, weights, champions


def get_spawn_params(fields):
    """Extract spawn control parameters."""
    params = {}
    for fname in ['spawnMin', 'spawnMax', 'championChance',
                   'championMin', 'championMax']:
        tf = get_field_val(fields, fname)
        if tf is not None and tf.values:
            params[fname] = tf.values[0]
    return params


def is_pool_record(fields):
    """Check if a record looks like a spawn pool (has nameN fields)."""
    for key in fields:
        rk = key.split('###')[0]
        if re.match(r'^name\d+$', rk):
            return True
    return False


def contains_insectoid_ref(names):
    """Check if any nameN value references insectoid-type monsters."""
    insectoid_keywords = [
        'cryptworm', 'scarab', 'spider', 'scorpion', 'insect',
        'beetle', 'sandwraith', 'worm', 'antlion', 'mantis',
        'arachnid', 'centipede', 'larva', 'maggot',
    ]
    for idx, (val, dtype) in names.items():
        if isinstance(val, str):
            vl = val.lower()
            for kw in insectoid_keywords:
                if kw in vl:
                    return True
        elif isinstance(val, list):
            for v in val:
                if isinstance(v, str):
                    vl = v.lower()
                    for kw in insectoid_keywords:
                        if kw in vl:
                            return True
    return False


def print_pool_details(name, fields, category):
    """Print detailed info about a spawn pool."""
    names, weights, champions = get_all_nameN_fields(fields)
    params = get_spawn_params(fields)

    print(f"\n{'='*80}")
    print(f"CATEGORY: {category}")
    print(f"RECORD:   {name}")
    print(f"{'-'*80}")

    if params:
        print(f"  Spawn params: {params}")

    if names:
        print(f"  Monster entries ({len(names)}):")
        for idx in sorted(names.keys()):
            val, dtype = names[idx]
            w = weights.get(idx, '?')
            dtype_str = {0: 'INT', 1: 'FLOAT', 2: 'STRING', 3: 'BOOL'}.get(dtype, f'?{dtype}')
            print(f"    name{idx} [{dtype_str}] = {val}")
            print(f"    weight{idx} = {w}")
    else:
        print("  (no nameN fields found)")

    if champions:
        print(f"  Champion entries ({len(champions)}):")
        for idx in sorted(champions.keys()):
            val, dtype = champions[idx]
            dtype_str = {0: 'INT', 1: 'FLOAT', 2: 'STRING', 3: 'BOOL'}.get(dtype, f'?{dtype}')
            print(f"    nameChampion{idx} [{dtype_str}] = {val}")


def main():
    if len(sys.argv) < 2:
        print("Usage: py tools/find_egypt_pools.py <database.arz>")
        sys.exit(1)

    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    # Location keywords for underground/cave/tomb areas in Egypt
    underground_keywords = ['cave', 'tomb', 'underground', 'crypt', 'dungeon',
                            'passage', 'burial', 'catacomb', 'labyrinth',
                            'cellar', 'lair', 'den', 'pit']

    # Categories for organizing results
    results = defaultdict(list)  # category -> [(name, fields)]

    all_record_names = db.record_names()
    print(f"\nSearching {len(all_record_names)} records...", file=sys.stderr)

    # ---- PASS 1: Find all spawn pool records ----
    pool_records = {}  # name -> fields for all pool-type records
    proxy_records = {}  # name -> fields for proxy records referencing pools
    pool_count = 0

    for name in all_record_names:
        fields = db.get_fields(name)
        if fields is None:
            continue

        if is_pool_record(fields):
            pool_records[name] = fields
            pool_count += 1

    print(f"Found {pool_count} total pool records", file=sys.stderr)

    # ---- PASS 2: Filter for Egypt-relevant pools ----
    egypt_pools_found = 0

    for name, fields in pool_records.items():
        nl = name.lower().replace('\\', '/')

        names, weights, champions = get_all_nameN_fields(fields)

        # Criterion A: Path contains "egypt" AND underground/cave/tomb keywords
        is_egypt = 'egypt' in nl
        is_underground = any(kw in nl for kw in underground_keywords)
        is_proxy_egypt = 'proxies' in nl and 'egypt' in nl

        # Criterion B: Contains insectoid monster references (anywhere, not just Egypt)
        has_insectoid = contains_insectoid_ref(names)

        # Criterion C: Is a proxy record for Egypt pools
        is_egypt_pool_proxy = is_proxy_egypt and 'pool' in nl

        if is_egypt and is_underground:
            results['EGYPT_UNDERGROUND'].append((name, fields))
            egypt_pools_found += 1
        elif is_egypt and has_insectoid:
            results['EGYPT_INSECTOID'].append((name, fields))
            egypt_pools_found += 1
        elif is_egypt_pool_proxy:
            results['EGYPT_PROXY_POOL'].append((name, fields))
            egypt_pools_found += 1
        elif has_insectoid and is_egypt:
            results['INSECTOID_IN_EGYPT'].append((name, fields))
            egypt_pools_found += 1
        elif is_egypt and 'pool' in nl:
            results['EGYPT_OTHER_POOL'].append((name, fields))
            egypt_pools_found += 1

    # ---- PASS 3: Find insectoid pools anywhere (for reference) ----
    for name, fields in pool_records.items():
        nl = name.lower().replace('\\', '/')
        names, weights, champions = get_all_nameN_fields(fields)

        if contains_insectoid_ref(names):
            # Skip ones we already found in Egypt categories
            already = False
            for cat_list in results.values():
                if any(n == name for n, _ in cat_list):
                    already = True
                    break
            if not already:
                results['INSECTOID_NON_EGYPT'].append((name, fields))

    # ---- PASS 4: Find proxy records that reference insectoid pools ----
    for name in all_record_names:
        nl = name.lower().replace('\\', '/')
        if 'prox' not in nl:
            continue
        if 'egypt' not in nl:
            continue

        fields = db.get_fields(name)
        if fields is None:
            continue

        # Check all STRING fields for references to pool records
        for key, tf in fields.items():
            if tf.dtype != DATA_TYPE_STRING:
                continue
            for val in tf.values:
                if isinstance(val, str) and 'pool' in val.lower():
                    vl = val.lower()
                    if any(kw in vl for kw in ['cryptworm', 'scarab', 'spider',
                                                'scorpion', 'insect', 'beetle',
                                                'sandwraith', 'cave', 'tomb',
                                                'underground', 'crypt']):
                        already = False
                        for cat_list in results.values():
                            if any(n == name for n, _ in cat_list):
                                already = True
                                break
                        if not already:
                            results['EGYPT_PROXY_REF_INSECTOID'].append((name, fields))

    # ---- Print results ----
    print(f"\n{'#'*80}")
    print(f"# EGYPT SPAWN POOL ANALYSIS")
    print(f"# Database: {sys.argv[1]}")
    print(f"{'#'*80}")

    # Print categories in priority order
    category_order = [
        ('EGYPT_UNDERGROUND', 'Egypt Underground/Cave/Tomb Pools'),
        ('EGYPT_INSECTOID', 'Egypt Pools with Insectoid Monsters'),
        ('INSECTOID_IN_EGYPT', 'Insectoid References in Egypt'),
        ('EGYPT_PROXY_POOL', 'Egypt Proxy Pool Records'),
        ('EGYPT_PROXY_REF_INSECTOID', 'Egypt Proxies Referencing Insectoid Pools'),
        ('EGYPT_OTHER_POOL', 'Other Egypt Pool Records'),
        ('INSECTOID_NON_EGYPT', 'Insectoid Pools Outside Egypt (reference)'),
    ]

    total = 0
    for cat_key, cat_label in category_order:
        items = results.get(cat_key, [])
        if not items:
            continue

        print(f"\n\n{'*'*80}")
        print(f"* {cat_label} ({len(items)} records)")
        print(f"{'*'*80}")

        for name, fields in sorted(items, key=lambda x: x[0]):
            print_pool_details(name, fields, cat_label)
            total += 1

    print(f"\n\n{'#'*80}")
    print(f"# SUMMARY")
    print(f"# Total matching records: {total}")
    for cat_key, cat_label in category_order:
        items = results.get(cat_key, [])
        if items:
            print(f"#   {cat_label}: {len(items)}")
    print(f"{'#'*80}")

    # ---- Bonus: Scan for any Egypt records with "pool" in path ----
    print(f"\n\n{'*'*80}")
    print(f"* ALL Egypt records with 'pool' in path (complete listing)")
    print(f"{'*'*80}")
    egypt_pool_paths = []
    for name in all_record_names:
        nl = name.lower().replace('\\', '/')
        if 'egypt' in nl and 'pool' in nl:
            egypt_pool_paths.append(name)

    for p in sorted(egypt_pool_paths):
        fields = db.get_fields(p)
        if fields is None:
            print(f"\n  {p}  (could not decode)")
            continue

        names, weights, champions = get_all_nameN_fields(fields)
        print(f"\n  {p}")
        if names:
            for idx in sorted(names.keys()):
                val, dtype = names[idx]
                w = weights.get(idx, '?')
                print(f"    name{idx} = {val}  (weight={w})")
        if champions:
            for idx in sorted(champions.keys()):
                val, dtype = champions[idx]
                print(f"    nameChampion{idx} = {val}")

        params = get_spawn_params(fields)
        if params:
            print(f"    params: {params}")


if __name__ == '__main__':
    main()
