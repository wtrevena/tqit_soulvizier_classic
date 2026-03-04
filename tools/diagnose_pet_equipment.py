"""
Diagnose pet equipment mechanics in the Titan Quest database.

Investigates:
- What equipment fields exist on pet records vs monster records
- What loot table paths they reference
- How working pet equipment differs from monster equipment
- Why copying monster equipment fields to pets crashes the game
"""

import sys
import re
from pathlib import Path

# Add tools dir so we can import arz_patcher
sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

DTYPE_NAMES = {0: "INT", 1: "FLOAT", 2: "STRING", 3: "BOOL"}

DB_PATH = Path(__file__).parent.parent / "work" / "SoulvizierClassic" / "Database" / "SoulvizierClassic.arz"


def print_separator(title, char="=", width=100):
    print(f"\n{char * width}")
    print(f" {title}")
    print(f"{char * width}")


def dump_equipment_fields(db, record_path, label=None):
    """Dump all equipment-related fields from a record."""
    fields = db.get_fields(record_path)
    if fields is None:
        print(f"  [RECORD NOT FOUND: {record_path}]")
        return None

    label = label or record_path

    # Equipment-related field patterns
    equip_patterns = [
        r'^chanceToEquip',
        r'^loot\w*Item',
        r'^loot\w*Name',
        r'^loot\w*Cost',
        r'^itemSlot',
        r'^handHit',
        r'^offhandItem',
        r'^weaponItem',
        r'^shieldItem',
        r'^helmetItem',
        r'^torsoItem',
        r'^legItem',
        r'^armItem',
        r'^ringItem',
        r'^amuletItem',
        r'^artifactItem',
        r'^equipmentSelection',
        r'^useEquipment',
    ]

    equip_fields = {}
    for key, tf in fields.items():
        real_name = key.split('###')[0]
        for pat in equip_patterns:
            if re.match(pat, real_name, re.IGNORECASE):
                equip_fields[key] = tf
                break

    if not equip_fields:
        return {}

    print(f"\n  --- {label} ---")
    for key, tf in sorted(equip_fields.items()):
        real_name = key.split('###')[0]
        dtype_name = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
        vals = tf.values
        # Truncate long value lists
        if len(vals) > 5:
            val_str = str(vals[:5]) + f"... ({len(vals)} total)"
        else:
            val_str = str(vals)
        print(f"    {real_name:40s} [{dtype_name:6s}] = {val_str}")

    return equip_fields


def dump_all_fields(db, record_path, label=None):
    """Dump ALL fields from a record."""
    fields = db.get_fields(record_path)
    if fields is None:
        print(f"  [RECORD NOT FOUND: {record_path}]")
        return None

    label = label or record_path
    print(f"\n  --- ALL FIELDS: {label} ---")
    for key, tf in fields.items():
        real_name = key.split('###')[0]
        dtype_name = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
        vals = tf.values
        if len(vals) > 5:
            val_str = str(vals[:5]) + f"... ({len(vals)} total)"
        else:
            val_str = str(vals)
        print(f"    {real_name:40s} [{dtype_name:6s}] = {val_str}")

    return fields


def get_template(db, record_path):
    """Get the templateName of a record."""
    fields = db.get_fields(record_path)
    if fields is None:
        return None
    for key, tf in fields.items():
        real_name = key.split('###')[0]
        if real_name == 'templateName':
            return tf.values[0] if tf.values else None
    return None


def main():
    print(f"Loading database: {DB_PATH}")
    db = ArzDatabase.from_arz(DB_PATH)

    all_records = db.record_names()
    print(f"Total records in database: {len(all_records)}")

    # =========================================================================
    # 1. FIND ALL PET RECORDS
    # =========================================================================
    print_separator("1. FINDING ALL PET RECORDS")

    # Strategy A: records with 'pets' in the path
    pets_by_path = [r for r in all_records if 'pets' in r.lower()]

    # Strategy B: records whose template contains 'pet'
    pet_templates = set()
    pets_by_template = []

    # Check known pet-related paths
    known_pet_paths = [
        'records/skills/soulskills/pets/',
        'records/xpack/skills/spirit/',
        'records/xpack/skills/nature/',
        'records/xpack/skills/earth/',
        'records/xpack/skills/storm/',
        'records/xpack/skills/warfare/',
        'records/xpack/skills/defense/',
        'records/xpack/skills/hunting/',
        'records/xpack/skills/rogue/',
        'records/xpack/skills/dream/',
        'records/skills/',
    ]

    # Broader: find anything with Pet.tpl template
    print("\n  Scanning all records for Pet.tpl templates...")
    pet_tpl_records = []
    monster_tpl_records_sample = []

    # We'll sample templates from relevant paths
    for rec in all_records:
        rec_lower = rec.lower()
        # Check template for pet-related paths
        if ('pet' in rec_lower or 'summon' in rec_lower or
            'wolf' in rec_lower or 'dweller' in rec_lower or
            'liche' in rec_lower or 'wisp' in rec_lower or
            'nymph' in rec_lower or 'familiar' in rec_lower):
            tpl = get_template(db, rec)
            if tpl and 'pet' in tpl.lower():
                pet_tpl_records.append((rec, tpl))
                pet_templates.add(tpl)

    print(f"\n  Records with 'pets' in path: {len(pets_by_path)}")
    for r in sorted(pets_by_path):
        tpl = get_template(db, r)
        print(f"    {r}  [template: {tpl}]")

    print(f"\n  Records with Pet.tpl-based templates: {len(pet_tpl_records)}")
    for r, tpl in sorted(pet_tpl_records):
        if r not in pets_by_path:  # Avoid duplicates
            print(f"    {r}  [template: {tpl}]")

    print(f"\n  Unique pet templates found: {pet_templates}")

    # Combine all pet records
    all_pet_records = set(pets_by_path)
    all_pet_records.update(r for r, _ in pet_tpl_records)

    # Also search for known game pet patterns
    game_pet_patterns = [
        'coredweller', 'core_dweller', 'dweller',
        'wolf', 'wolves',
        'liche', 'lichking',
        'wisp', 'nymph',
        'familiar',
        'outsider',
        'nightmare',
        'ancestor',
    ]

    extra_pets = []
    for rec in all_records:
        rec_lower = rec.lower()
        for pat in game_pet_patterns:
            if pat in rec_lower and rec not in all_pet_records:
                tpl = get_template(db, rec)
                if tpl and ('pet' in tpl.lower() or 'monster' in tpl.lower()):
                    extra_pets.append((rec, tpl))
                    all_pet_records.add(rec)
                break

    if extra_pets:
        print(f"\n  Additional game pet records found: {len(extra_pets)}")
        for r, tpl in sorted(extra_pets)[:30]:
            print(f"    {r}  [template: {tpl}]")
        if len(extra_pets) > 30:
            print(f"    ... and {len(extra_pets) - 30} more")

    # =========================================================================
    # 2. DUMP EQUIPMENT FIELDS FOR PETS WITH EQUIPMENT
    # =========================================================================
    print_separator("2. PET EQUIPMENT FIELDS (records that have equipment/loot fields)")

    # Focus on soulskills pets first
    soulskill_pets = sorted([r for r in all_pet_records
                              if 'soulskills' in r.lower() or 'soulskill' in r.lower()])

    print(f"\n  Soulskill pets: {len(soulskill_pets)}")
    pets_with_equipment = []

    for rec in soulskill_pets:
        equip = dump_equipment_fields(db, rec, rec)
        if equip:
            pets_with_equipment.append(rec)

    # Now check other game pets
    other_pets = sorted([r for r in all_pet_records if r not in soulskill_pets])

    print(f"\n  Checking other game pets for equipment fields...")
    for rec in other_pets:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        has_equip = False
        for key in fields:
            real_name = key.split('###')[0].lower()
            if ('chancetoequip' in real_name or 'loot' in real_name and 'item' in real_name):
                has_equip = True
                break
        if has_equip:
            equip = dump_equipment_fields(db, rec, f"[GAME PET] {rec}")
            if equip:
                pets_with_equipment.append(rec)

    # =========================================================================
    # 3. MONSTER EQUIPMENT FIELDS (Rakanizeus and Boneash)
    # =========================================================================
    print_separator("3. MONSTER EQUIPMENT FIELDS")

    # Find Rakanizeus records
    rakanizeus_records = [r for r in all_records if 'rakanizeus' in r.lower()]
    print(f"\n  Rakanizeus records found: {len(rakanizeus_records)}")
    for rec in sorted(rakanizeus_records):
        tpl = get_template(db, rec)
        print(f"    {rec}  [template: {tpl}]")
        dump_equipment_fields(db, rec, f"[MONSTER] {rec}")

    # Find Boneash records
    boneash_records = [r for r in all_records if 'boneash' in r.lower()]
    print(f"\n  Boneash records found: {len(boneash_records)}")
    for rec in sorted(boneash_records):
        tpl = get_template(db, rec)
        print(f"    {rec}  [template: {tpl}]")
        dump_equipment_fields(db, rec, f"[MONSTER] {rec}")

    # =========================================================================
    # 4. COMPARE LOOT TABLE PATHS
    # =========================================================================
    print_separator("4. COMPARING LOOT TABLE PATHS (pet vs monster)")

    print("\n  --- Loot paths referenced by PETS ---")
    pet_loot_paths = set()
    for rec in pets_with_equipment:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in fields.items():
            real_name = key.split('###')[0]
            if 'loot' in real_name.lower() and 'item' in real_name.lower():
                for v in tf.values:
                    if isinstance(v, str) and v.strip():
                        pet_loot_paths.add(v)
                        print(f"    {rec}")
                        print(f"      {real_name} -> {v}")

    print("\n  --- Loot paths referenced by MONSTERS (Rakanizeus + Boneash) ---")
    monster_loot_paths = set()
    for rec in rakanizeus_records + boneash_records:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in fields.items():
            real_name = key.split('###')[0]
            if 'loot' in real_name.lower() and 'item' in real_name.lower():
                for v in tf.values:
                    if isinstance(v, str) and v.strip():
                        monster_loot_paths.add(v)
                        print(f"    {rec}")
                        print(f"      {real_name} -> {v}")

    print(f"\n  Unique loot paths from pets: {len(pet_loot_paths)}")
    for p in sorted(pet_loot_paths):
        print(f"    {p}")

    print(f"\n  Unique loot paths from monsters: {len(monster_loot_paths)}")
    for p in sorted(monster_loot_paths):
        print(f"    {p}")

    # Check path patterns
    print("\n  --- Path pattern analysis ---")
    for label, paths in [("PET", pet_loot_paths), ("MONSTER", monster_loot_paths)]:
        if not paths:
            print(f"  {label}: No loot paths found")
            continue
        # Extract directory patterns
        dirs = set()
        for p in paths:
            parts = p.replace('\\', '/').split('/')
            if len(parts) > 2:
                dirs.add('/'.join(parts[:3]))
        print(f"  {label} loot path directories: {sorted(dirs)}")

    # =========================================================================
    # 5. FOLLOW LOOT TABLE REFERENCES
    # =========================================================================
    print_separator("5. FOLLOWING LOOT TABLE REFERENCES")

    # Follow a pet loot reference
    if pet_loot_paths:
        sample_pet_loot = sorted(pet_loot_paths)[0]
        print(f"\n  Following PET loot reference: {sample_pet_loot}")
        if db.has_record(sample_pet_loot):
            dump_all_fields(db, sample_pet_loot, f"[PET LOOT TABLE] {sample_pet_loot}")

            # Also check what THAT record references (it might point to item tables)
            fields = db.get_fields(sample_pet_loot)
            if fields:
                for key, tf in fields.items():
                    real_name = key.split('###')[0]
                    if tf.dtype == 2:  # STRING type
                        for v in tf.values:
                            if isinstance(v, str) and v.endswith('.dbr') and v != sample_pet_loot:
                                print(f"\n      Sub-reference: {real_name} -> {v}")
                                if db.has_record(v):
                                    dump_all_fields(db, v, f"[SUB-REF] {v}")
                                else:
                                    print(f"        [NOT FOUND IN DB]")
        else:
            print(f"    [RECORD NOT FOUND IN DB: {sample_pet_loot}]")
            # Try case-insensitive match
            sample_lower = sample_pet_loot.lower().replace('\\', '/')
            for r in all_records:
                if r.lower().replace('\\', '/') == sample_lower:
                    print(f"    Case-insensitive match found: {r}")
                    dump_all_fields(db, r, f"[PET LOOT TABLE] {r}")
                    break

    # Follow ALL unique pet loot references
    if len(pet_loot_paths) > 1:
        print(f"\n  Following ALL remaining PET loot references:")
        for loot_path in sorted(pet_loot_paths):
            if loot_path == sorted(pet_loot_paths)[0]:
                continue  # Already shown above
            found = False
            if db.has_record(loot_path):
                dump_all_fields(db, loot_path, f"[PET LOOT TABLE] {loot_path}")
                found = True
            else:
                lp_lower = loot_path.lower().replace('\\', '/')
                for r in all_records:
                    if r.lower().replace('\\', '/') == lp_lower:
                        dump_all_fields(db, r, f"[PET LOOT TABLE] {r}")
                        found = True
                        break
            if not found:
                print(f"    [NOT FOUND: {loot_path}]")

    # Follow a monster loot reference
    if monster_loot_paths:
        sample_monster_loot = sorted(monster_loot_paths)[0]
        print(f"\n  Following MONSTER loot reference: {sample_monster_loot}")
        if db.has_record(sample_monster_loot):
            dump_all_fields(db, sample_monster_loot, f"[MONSTER LOOT TABLE] {sample_monster_loot}")

            # Follow sub-references
            fields = db.get_fields(sample_monster_loot)
            if fields:
                for key, tf in fields.items():
                    real_name = key.split('###')[0]
                    if tf.dtype == 2:
                        for v in tf.values:
                            if isinstance(v, str) and v.endswith('.dbr') and v != sample_monster_loot:
                                print(f"\n      Sub-reference: {real_name} -> {v}")
                                if db.has_record(v):
                                    dump_all_fields(db, v, f"[MONSTER SUB-REF] {v}")
                                else:
                                    print(f"        [NOT FOUND IN DB]")
        else:
            print(f"    [RECORD NOT FOUND: {sample_monster_loot}]")
            sample_lower = sample_monster_loot.lower().replace('\\', '/')
            for r in all_records:
                if r.lower().replace('\\', '/') == sample_lower:
                    print(f"    Case-insensitive match found: {r}")
                    dump_all_fields(db, r, f"[MONSTER LOOT TABLE] {r}")
                    break

        # Follow a few more monster loot references to see the pattern
        if len(monster_loot_paths) > 1:
            print(f"\n  Following additional MONSTER loot references (up to 3 more):")
            for i, loot_path in enumerate(sorted(monster_loot_paths)):
                if loot_path == sample_monster_loot:
                    continue
                if i >= 4:
                    break
                found = False
                if db.has_record(loot_path):
                    dump_all_fields(db, loot_path, f"[MONSTER LOOT TABLE] {loot_path}")
                    found = True
                else:
                    lp_lower = loot_path.lower().replace('\\', '/')
                    for r in all_records:
                        if r.lower().replace('\\', '/') == lp_lower:
                            dump_all_fields(db, r, f"[MONSTER LOOT TABLE] {r}")
                            found = True
                            break
                if not found:
                    print(f"    [NOT FOUND: {loot_path}]")

    # =========================================================================
    # 6. CHANCE-TO-EQUIP COMPARISON
    # =========================================================================
    print_separator("6. CHANCE-TO-EQUIP VALUES COMPARISON")

    print("\n  --- Pet chanceToEquip values ---")
    for rec in pets_with_equipment:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in sorted(fields.items()):
            real_name = key.split('###')[0]
            if 'chancetoequip' in real_name.lower():
                dtype_name = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
                print(f"    {rec}")
                print(f"      {real_name:40s} [{dtype_name}] = {tf.values}")

    print("\n  --- Monster chanceToEquip values ---")
    for rec in rakanizeus_records + boneash_records:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in sorted(fields.items()):
            real_name = key.split('###')[0]
            if 'chancetoequip' in real_name.lower():
                dtype_name = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
                print(f"    {rec}")
                print(f"      {real_name:40s} [{dtype_name}] = {tf.values}")

    # =========================================================================
    # BONUS: Template comparison
    # =========================================================================
    print_separator("BONUS: TEMPLATE & FIELD COUNT COMPARISON")

    print("\n  --- Template types used ---")
    # Check what record type string is stored for pet vs monster records
    print("\n  Pet record types (from _record_types):")
    for rec in sorted(pets_with_equipment):
        rt = db._record_types.get(rec, '?')
        tpl = get_template(db, rec)
        fields = db.get_fields(rec)
        nfields = len(fields) if fields else 0
        print(f"    {rec}")
        print(f"      record_type={rt}, templateName={tpl}, field_count={nfields}")

    print("\n  Monster record types:")
    for rec in sorted(rakanizeus_records + boneash_records):
        rt = db._record_types.get(rec, '?')
        tpl = get_template(db, rec)
        fields = db.get_fields(rec)
        nfields = len(fields) if fields else 0
        print(f"    {rec}")
        print(f"      record_type={rt}, templateName={tpl}, field_count={nfields}")

    # =========================================================================
    # BONUS 2: Full field dump of a working pet with equipment
    # =========================================================================
    if pets_with_equipment:
        print_separator("BONUS 2: FULL FIELD DUMP OF A WORKING PET WITH EQUIPMENT")
        sample = pets_with_equipment[0]
        dump_all_fields(db, sample, f"[FULL DUMP] {sample}")

    # =========================================================================
    # BONUS 3: Check for lootName fields (item pool names vs direct items)
    # =========================================================================
    print_separator("BONUS 3: lootName / LOOT POOL FIELDS")

    print("\n  --- Pet lootName fields ---")
    for rec in pets_with_equipment:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in fields.items():
            real_name = key.split('###')[0]
            if 'lootname' in real_name.lower() or 'name' in real_name.lower() and 'loot' in real_name.lower():
                print(f"    {rec}: {real_name} = {tf.values}")

    print("\n  --- Monster lootName fields ---")
    for rec in rakanizeus_records + boneash_records:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in fields.items():
            real_name = key.split('###')[0]
            if 'lootname' in real_name.lower() or 'name' in real_name.lower() and 'loot' in real_name.lower():
                print(f"    {rec}: {real_name} = {tf.values}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_separator("SUMMARY & ANALYSIS")

    print(f"""
  Total pet records found: {len(all_pet_records)}
  Pets with equipment fields: {len(pets_with_equipment)}

  Pet loot paths found: {len(pet_loot_paths)}
  Monster loot paths found: {len(monster_loot_paths)}

  Key questions to answer from the data above:
  1. Do pets and monsters use the SAME loot table template/format?
  2. Are the loot paths pointing to the same directory structures?
  3. Do chanceToEquip dtypes/values differ between pets and monsters?
  4. What templateName do loot records use - are they compatible with Pet.tpl?
  5. Are there fields on monster records that don't exist in Pet.tpl?
""")

    print("Done.")


if __name__ == '__main__':
    main()
