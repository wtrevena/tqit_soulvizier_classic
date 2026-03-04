"""
Diagnostic script to investigate pet equipment fields in the .arz database.

Compares working pet (Lyia Leafsong) against broken pets (Boneash, Rakanizeus)
to understand why equipment is not appearing.
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

ARZ_PATH = Path(__file__).parent.parent / "work" / "SoulvizierClassic" / "Database" / "SoulvizierClassic.arz"

# Keywords to search for in field names (case insensitive)
EQUIP_KEYWORDS = re.compile(
    r'equip|loot|weapon|armor|staff|shield|item|attach', re.IGNORECASE
)
SUMMON_KEYWORDS = re.compile(
    r'summon|spawn|pet|skill|minion', re.IGNORECASE
)


def norm(path):
    """Normalize path to lowercase with backslashes (matching .arz record names)."""
    return path.replace('/', '\\').lower()


def find_record(db, substring, prefix=None):
    """Find a record whose name contains `substring` (and optionally starts with prefix).
    All comparisons are case-insensitive and slash-normalized."""
    substring_lower = norm(substring)
    prefix_lower = norm(prefix) if prefix else None
    matches = []
    for name in db.record_names():
        name_norm = norm(name)
        if substring_lower in name_norm:
            if prefix_lower is None or name_norm.startswith(prefix_lower):
                matches.append(name)
    return matches


def find_record_exact(db, path):
    """Find a record by exact path, normalizing slashes."""
    path_norm = norm(path)
    for name in db.record_names():
        if norm(name) == path_norm:
            return name
    return None


def dump_matching_fields(db, record_name, pattern, label=""):
    """Dump all fields matching `pattern` regex that have non-empty/non-zero values."""
    fields = db.get_fields(record_name)
    if fields is None:
        print(f"  [ERROR] Record not found: {record_name}")
        return

    print(f"\n{'='*80}")
    if label:
        print(f"  {label}")
    print(f"  Record: {record_name}")
    print(f"  Total fields: {len(fields)}")
    print(f"  Searching for: {pattern.pattern}")
    print(f"{'='*80}")

    found = 0
    for key, tf in fields.items():
        real_name = key.split('###')[0]
        if pattern.search(real_name):
            # Check if non-empty / non-zero
            val = tf.value
            if isinstance(val, list):
                if all(v == 0 or v == '' or v == 0.0 for v in val):
                    continue
            else:
                if val == 0 or val == '' or val == 0.0:
                    continue

            dtype_names = {0: 'int', 1: 'float', 2: 'string', 3: 'bool'}
            dtype_str = dtype_names.get(tf.dtype, f'?{tf.dtype}')
            print(f"  {real_name:40s} [{dtype_str:6s}] = {tf.values}")
            found += 1

    if found == 0:
        print(f"  (no non-empty/non-zero matching fields found)")
    print()


def dump_all_fields(db, record_name, label=""):
    """Dump ALL fields for a record (for deep investigation)."""
    fields = db.get_fields(record_name)
    if fields is None:
        print(f"  [ERROR] Record not found: {record_name}")
        return

    print(f"\n{'='*80}")
    if label:
        print(f"  {label}")
    print(f"  Record: {record_name}")
    print(f"  ALL FIELDS ({len(fields)} total):")
    print(f"{'='*80}")

    dtype_names = {0: 'int', 1: 'float', 2: 'string', 3: 'bool'}
    for key, tf in fields.items():
        real_name = key.split('###')[0]
        dtype_str = dtype_names.get(tf.dtype, f'?{tf.dtype}')
        val = tf.value
        # Skip truly empty stuff to reduce noise, but be less aggressive
        if isinstance(val, list):
            if all(v == 0 or v == '' or v == 0.0 for v in val):
                continue
        else:
            if val == 0 or val == '' or val == 0.0:
                continue
        print(f"  {real_name:45s} [{dtype_str:6s}] = {tf.values}")
    print()


def main():
    print(f"Loading database: {ARZ_PATH}")
    db = ArzDatabase.from_arz(ARZ_PATH)

    # ---------------------------------------------------------------
    # 1. Find Lyia Leafsong pet record (the one in soulskills/pets/)
    # ---------------------------------------------------------------
    print("\n\n" + "#"*80)
    print("# STEP 1: LYIA LEAFSONG PET (working - has equipment)")
    print("#"*80)

    lyia_pet_matches = find_record(db, 'lyialeafsong_1', 'records\\skills\\soulskills\\pets\\')
    print(f"  Found lyia pet records: {lyia_pet_matches}")
    # Also find the real monster
    lyia_monster_matches = find_record(db, 'um_lyialeafsong', 'records\\creature\\monster\\maenad\\')
    print(f"  Found lyia monster records: {lyia_monster_matches}")

    # Show the pet version
    for rec in lyia_pet_matches:
        dump_matching_fields(db, rec, EQUIP_KEYWORDS, "Lyia Leafsong PET - Equipment fields")

    # ---------------------------------------------------------------
    # 2. Real Boneash monster
    # ---------------------------------------------------------------
    print("\n\n" + "#"*80)
    print("# STEP 2: REAL BONEASH MONSTER")
    print("#"*80)

    boneash_monster = find_record_exact(db, "records\\creature\\monster\\skeleton\\um_boneash_30.dbr")
    if not boneash_monster:
        # Try broader search
        boneash_monster_matches = find_record(db, 'boneash', 'records\\creature\\')
        print(f"  Broader search for boneash in creature: {boneash_monster_matches}")
        if boneash_monster_matches:
            boneash_monster = boneash_monster_matches[0]
            for rec in boneash_monster_matches:
                dump_matching_fields(db, rec, EQUIP_KEYWORDS, f"Boneash Monster - Equipment fields")
    else:
        dump_matching_fields(db, boneash_monster, EQUIP_KEYWORDS, "Real Boneash Monster - Equipment fields")

    # ---------------------------------------------------------------
    # 3. Our Boneash pet
    # ---------------------------------------------------------------
    print("\n\n" + "#"*80)
    print("# STEP 3: OUR BONEASH PET")
    print("#"*80)

    boneash_pet = find_record_exact(db, "records\\skills\\soulskills\\pets\\boneash_1.dbr")
    if not boneash_pet:
        boneash_pet_matches = find_record(db, 'boneash', 'records\\skills\\soulskills\\pets\\')
        print(f"  Search for boneash in soulskills/pets: {boneash_pet_matches}")
        if boneash_pet_matches:
            boneash_pet = boneash_pet_matches[0]
            for rec in boneash_pet_matches:
                dump_matching_fields(db, rec, EQUIP_KEYWORDS, f"Boneash Pet - Equipment fields")
        else:
            # Even broader
            boneash_all = find_record(db, 'boneash')
            print(f"  ALL records containing 'boneash': {boneash_all}")
    else:
        dump_matching_fields(db, boneash_pet, EQUIP_KEYWORDS, "Our Boneash Pet - Equipment fields")

    # ---------------------------------------------------------------
    # 4. Real Rakanizeus monster
    # ---------------------------------------------------------------
    print("\n\n" + "#"*80)
    print("# STEP 4: REAL RAKANIZEUS MONSTER")
    print("#"*80)

    rakan_monster = find_record_exact(db, "records\\creature\\monster\\satyr\\um_rakanizeus.dbr")
    if not rakan_monster:
        rakan_monster_matches = find_record(db, 'rakanizeus', 'records\\creature\\')
        print(f"  Search for rakanizeus in creature: {rakan_monster_matches}")
        if rakan_monster_matches:
            rakan_monster = rakan_monster_matches[0]
            for rec in rakan_monster_matches:
                dump_matching_fields(db, rec, EQUIP_KEYWORDS, f"Rakanizeus Monster - Equipment fields")
        else:
            # Even broader
            rakan_all = find_record(db, 'rakanizeus')
            print(f"  ALL records containing 'rakanizeus': {rakan_all}")
    else:
        dump_matching_fields(db, rakan_monster, EQUIP_KEYWORDS, "Real Rakanizeus Monster - Equipment fields")

    # ---------------------------------------------------------------
    # 5. Our Rakanizeus pet
    # ---------------------------------------------------------------
    print("\n\n" + "#"*80)
    print("# STEP 5: OUR RAKANIZEUS PET")
    print("#"*80)

    rakan_pet = find_record_exact(db, "records\\skills\\soulskills\\pets\\rakanizeus_1.dbr")
    if not rakan_pet:
        rakan_pet_matches = find_record(db, 'rakanizeus', 'records\\skills\\soulskills\\pets\\')
        print(f"  Search for rakanizeus in soulskills/pets: {rakan_pet_matches}")
        if rakan_pet_matches:
            rakan_pet = rakan_pet_matches[0]
            for rec in rakan_pet_matches:
                dump_matching_fields(db, rec, EQUIP_KEYWORDS, f"Rakanizeus Pet - Equipment fields")
        else:
            rakan_all = find_record(db, 'rakanizeus')
            print(f"  ALL records containing 'rakanizeus': {rakan_all}")
    else:
        dump_matching_fields(db, rakan_pet, EQUIP_KEYWORDS, "Our Rakanizeus Pet - Equipment fields")

    # ---------------------------------------------------------------
    # 6. Summon fields on real Boneash (does it summon an earth pet?)
    # ---------------------------------------------------------------
    print("\n\n" + "#"*80)
    print("# STEP 6: REAL BONEASH - SUMMON/SKILL FIELDS")
    print("#"*80)

    if boneash_monster:
        dump_matching_fields(db, boneash_monster, SUMMON_KEYWORDS, "Real Boneash Monster - Summon/Skill fields")
    else:
        print("  [SKIP] No boneash monster record found")

    # ---------------------------------------------------------------
    # 7. Compare: dump ALL non-zero fields for key records
    # ---------------------------------------------------------------
    print("\n\n" + "#"*80)
    print("# STEP 7: FULL FIELD COMPARISON")
    print("#"*80)

    # Lyia pet version - all fields
    if lyia_pet_matches:
        # Just dump the first pet variant (_1) to keep output manageable
        dump_all_fields(db, lyia_pet_matches[0], "Lyia Leafsong PET (soulskills) - ALL non-zero fields")

    # Boneash pet - all fields
    if boneash_pet:
        dump_all_fields(db, boneash_pet, "Our Boneash Pet - ALL non-zero fields")

    # Rakanizeus pet - all fields
    if rakan_pet:
        dump_all_fields(db, rakan_pet, "Our Rakanizeus Pet - ALL non-zero fields")

    # Real Boneash - all fields (to see equipment setup)
    if boneash_monster:
        dump_all_fields(db, boneash_monster, "Real Boneash Monster - ALL non-zero fields")

    # Real Rakanizeus - all fields
    if rakan_monster:
        dump_all_fields(db, rakan_monster, "Real Rakanizeus Monster - ALL non-zero fields")


if __name__ == '__main__':
    main()
