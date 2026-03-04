"""
Diagnose loot table system for pet equipment replacement.

Investigates:
1. Lyia _1 pet's current equipment fields (baseline)
2. Loot table directory structure under records/item/loottables/
3. Available loot tables by equipment slot category
4. Rakanizeus and Boneash MONSTER loot table references
5. Other working armed pets and their loot table references
6. Cross-reference: monster loot tables also used by working pets
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

DTYPE_NAMES = {0: "INT", 1: "FLOAT", 2: "STRING", 3: "BOOL"}

DB_PATH = Path(__file__).parent.parent / "work" / "SoulvizierClassic" / "Database" / "SoulvizierClassic.arz"


def sep(title, char="=", width=100):
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")


def get_field_value(fields, name):
    """Get value of a field by base name (ignoring ### suffix)."""
    if fields is None:
        return None
    if name in fields:
        return fields[name].values
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            return tf.values
    return None


def find_record_ci(db, path):
    """Find a record by case-insensitive path match."""
    path_norm = path.lower().replace('/', '\\')
    for name in db.record_names():
        if name.lower().replace('/', '\\') == path_norm:
            return name
    return None


def dump_equip_fields(db, record_path, label):
    """Dump all chanceToEquip*, loot*Item*, and equip*Item* fields."""
    fields = db.get_fields(record_path)
    if fields is None:
        print(f"  [NOT FOUND: {record_path}]")
        return None

    print(f"\n  --- {label} ---")
    print(f"  Record: {record_path}")

    equip_fields = {}
    for key, tf in fields.items():
        rn = key.split('###')[0]
        rl = rn.lower()
        if (rl.startswith('chancetoequip') or
            (rl.startswith('loot') and 'item' in rl) or
            (rl.startswith('equip') and 'item' in rl) or
            rl.startswith('loot') and 'chance' in rl or
            rl.startswith('loot') and 'name' in rl or
            rl.startswith('loot') and 'cost' in rl):
            equip_fields[key] = tf

    if not equip_fields:
        print(f"  (no equipment/loot fields found)")
        return {}

    for key, tf in sorted(equip_fields.items(), key=lambda x: x[0].split('###')[0]):
        rn = key.split('###')[0]
        dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
        vals = tf.values
        # Show all values, truncate only extremely long lists
        if len(vals) > 10:
            val_str = str(vals[:10]) + f"... ({len(vals)} total)"
        else:
            val_str = str(vals)
        print(f"    {rn:45s} [{dtype:6s}] = {val_str}")

    return equip_fields


def main():
    print(f"Loading database: {DB_PATH}")
    db = ArzDatabase.from_arz(DB_PATH)

    all_records = db.record_names()
    print(f"Total records: {len(all_records)}")

    # ===========================================================================
    # SECTION 1: Dump Lyia _1 pet equipment fields (baseline)
    # ===========================================================================
    sep("SECTION 1: LYIA LEAFSONG _1 PET EQUIPMENT (baseline we're replacing)")

    lyia_pet_path = None
    for name in all_records:
        nl = name.lower().replace('/', '\\')
        if 'soulskills' in nl and 'pets' in nl and 'lyialeafsong_1' in nl:
            lyia_pet_path = name
            break

    if lyia_pet_path:
        dump_equip_fields(db, lyia_pet_path, "Lyia Leafsong _1 PET")
    else:
        print("  [ERROR] Could not find Lyia Leafsong _1 pet record!")
        # Try broader search
        lyia_hits = [r for r in all_records if 'lyia' in r.lower() and 'pet' in r.lower()]
        if not lyia_hits:
            lyia_hits = [r for r in all_records if 'lyia' in r.lower()]
        print(f"  Broader lyia search: {lyia_hits[:10]}")

    # ===========================================================================
    # SECTION 2: Loot table directory structure
    # ===========================================================================
    sep("SECTION 2: LOOT TABLE DIRECTORY STRUCTURE")

    loot_records = [r for r in all_records if r.lower().replace('/', '\\').startswith('records\\item\\loottables\\')]

    if not loot_records:
        # Try alternative paths
        loot_records = [r for r in all_records if 'loottable' in r.lower()]

    print(f"\n  Total loot table records: {len(loot_records)}")

    # Extract top-level categories
    categories = defaultdict(list)
    for r in loot_records:
        parts = r.replace('\\', '/').split('/')
        # Expected: records/item/loottables/<category>/...
        if len(parts) > 3:
            cat = parts[3] if len(parts) > 3 else '(root)'
            categories[cat].append(r)

    print(f"\n  Top-level categories under records/item/loottables/:")
    for cat in sorted(categories.keys()):
        print(f"    {cat:30s} ({len(categories[cat])} records)")

    # Also check for equipment-related loot tables elsewhere
    equip_loot = [r for r in all_records
                  if ('loottable' in r.lower() or 'loot_table' in r.lower())
                  and r not in loot_records]
    if equip_loot:
        print(f"\n  Additional loot table records outside item/loottables/: {len(equip_loot)}")
        # Group by top-level path
        other_cats = defaultdict(int)
        for r in equip_loot:
            parts = r.replace('\\', '/').split('/')
            if len(parts) > 2:
                other_cats['/'.join(parts[:3])] += 1
        for cat, count in sorted(other_cats.items()):
            print(f"    {cat:50s} ({count} records)")

    # ===========================================================================
    # SECTION 3: Available loot tables by slot category
    # ===========================================================================
    sep("SECTION 3: AVAILABLE LOOT TABLES BY EQUIPMENT SLOT")

    # Define the slot categories we care about
    slot_searches = {
        "WEAPONS - Swords": ['sword'],
        "WEAPONS - Axes": ['axe'],
        "WEAPONS - Clubs/Maces": ['club', 'mace'],
        "WEAPONS - Staves": ['staff', 'stave', 'staf'],
        "SHIELDS": ['shield'],
        "TORSO - Heavy Armor": ['torso', 'chest'],
        "TORSO - Robes/Light": ['robe', 'tunic'],
        "HEAD - Helmets": ['helmet', 'helm', 'head'],
        "HEAD - Circlets/Crowns": ['circlet', 'crown', 'tiara'],
        "ARMS/FOREARM": ['arm', 'forearm', 'bracer', 'gauntlet', 'glove'],
        "LEGS/LOWER BODY": ['leg', 'greave', 'shin', 'lowerbody'],
        "RINGS": ['ring', 'finger'],
        "AMULETS": ['amulet', 'necklace'],
        "MISC": ['misc', 'potion', 'scroll', 'relic', 'charm'],
    }

    for slot_label, keywords in slot_searches.items():
        matches = []
        for r in loot_records:
            rl = r.lower()
            if any(kw in rl for kw in keywords):
                matches.append(r)

        if matches:
            print(f"\n  --- {slot_label} ({len(matches)} tables) ---")
            for m in sorted(matches)[:30]:
                print(f"    {m}")
            if len(matches) > 30:
                print(f"    ... and {len(matches) - 30} more")

    # Also list what subcategories exist under each top-level category
    print(f"\n\n  --- DETAILED SUBCATEGORY LISTING ---")
    for cat in sorted(categories.keys()):
        subcats = defaultdict(list)
        for r in categories[cat]:
            parts = r.replace('\\', '/').split('/')
            if len(parts) > 4:
                subcat = parts[4]
            else:
                subcat = '(root)'
            subcats[subcat].append(r)

        print(f"\n  [{cat}] subcategories:")
        for sc in sorted(subcats.keys()):
            print(f"    {sc:40s} ({len(subcats[sc])} records)")
            # Show first 3 file names in each subcategory
            for r in sorted(subcats[sc])[:3]:
                fname = r.replace('\\', '/').split('/')[-1]
                print(f"      -> {fname}")
            if len(subcats[sc]) > 3:
                print(f"      ... and {len(subcats[sc]) - 3} more")

    # ===========================================================================
    # SECTION 4: Rakanizeus and Boneash MONSTER loot tables
    # ===========================================================================
    sep("SECTION 4: RAKANIZEUS & BONEASH MONSTER LOOT TABLE REFERENCES")

    # Find the monster records
    rakan_monsters = [r for r in all_records
                      if 'rakanizeus' in r.lower() and 'creature' in r.lower()]
    boneash_monsters = [r for r in all_records
                        if 'boneash' in r.lower() and 'creature' in r.lower()]

    print(f"\n  Rakanizeus monster records: {len(rakan_monsters)}")
    for rec in sorted(rakan_monsters):
        print(f"    {rec}")

    print(f"\n  Boneash monster records: {len(boneash_monsters)}")
    for rec in sorted(boneash_monsters):
        print(f"    {rec}")

    # Dump equipment fields for each
    all_monster_loot_paths = {}  # slot -> set of paths

    print(f"\n  --- RAKANIZEUS MONSTER EQUIPMENT ---")
    for rec in sorted(rakan_monsters):
        fields = db.get_fields(rec)
        if fields is None:
            continue
        print(f"\n  Record: {rec}")
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
            rn = key.split('###')[0]
            rl = rn.lower()
            if (rl.startswith('chancetoequip') or
                (rl.startswith('loot') and ('item' in rl or 'chance' in rl or 'name' in rl or 'cost' in rl)) or
                (rl.startswith('equip') and 'item' in rl)):
                dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
                print(f"    {rn:45s} [{dtype:6s}] = {tf.values}")
                # Track loot paths
                if tf.dtype == 2 and tf.values:  # STRING type
                    for v in tf.values:
                        if isinstance(v, str) and v.strip() and v.endswith('.dbr'):
                            slot = rn  # e.g. lootRightHandItem1
                            if slot not in all_monster_loot_paths:
                                all_monster_loot_paths[slot] = set()
                            all_monster_loot_paths[slot].add(v)

    print(f"\n  --- BONEASH MONSTER EQUIPMENT ---")
    for rec in sorted(boneash_monsters):
        fields = db.get_fields(rec)
        if fields is None:
            continue
        print(f"\n  Record: {rec}")
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
            rn = key.split('###')[0]
            rl = rn.lower()
            if (rl.startswith('chancetoequip') or
                (rl.startswith('loot') and ('item' in rl or 'chance' in rl or 'name' in rl or 'cost' in rl)) or
                (rl.startswith('equip') and 'item' in rl)):
                dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
                print(f"    {rn:45s} [{dtype:6s}] = {tf.values}")
                if tf.dtype == 2 and tf.values:
                    for v in tf.values:
                        if isinstance(v, str) and v.strip() and v.endswith('.dbr'):
                            slot = rn
                            if slot not in all_monster_loot_paths:
                                all_monster_loot_paths[slot] = set()
                            all_monster_loot_paths[slot].add(v)

    # Summarize monster loot paths
    print(f"\n  --- SUMMARY: Monster loot table paths by slot ---")
    for slot in sorted(all_monster_loot_paths.keys()):
        print(f"    {slot}:")
        for path in sorted(all_monster_loot_paths[slot]):
            print(f"      {path}")

    # ===========================================================================
    # SECTION 5: Other working armed pets
    # ===========================================================================
    sep("SECTION 5: OTHER WORKING ARMED PETS AND THEIR LOOT TABLES")

    # Find all pet records in soulskills/pets/
    soul_pets = [r for r in all_records
                 if 'soulskills' in r.lower() and 'pets' in r.lower()
                 and r.lower().endswith('.dbr')]

    print(f"\n  Total soul pet records: {len(soul_pets)}")

    # Also find vanilla game pets (Nature nymph, wolves, core dweller, etc.)
    vanilla_pet_paths = []
    for r in all_records:
        rl = r.lower().replace('/', '\\')
        # Nature mastery pets
        if ('nature' in rl and ('nymph' in rl or 'wolf' in rl or 'wolves' in rl
                                or 'briar' in rl or 'plague' in rl)):
            if 'pet' in rl or 'summon' in rl:
                vanilla_pet_paths.append(r)
        # Earth mastery
        elif ('earth' in rl and ('coredweller' in rl or 'core_dweller' in rl)):
            if 'pet' in rl or 'summon' in rl:
                vanilla_pet_paths.append(r)
        # Spirit mastery
        elif ('spirit' in rl and ('liche' in rl or 'lichking' in rl or 'outsider' in rl)):
            if 'pet' in rl or 'summon' in rl:
                vanilla_pet_paths.append(r)
        # Dream mastery
        elif ('dream' in rl and ('nightmare' in rl)):
            if 'pet' in rl or 'summon' in rl:
                vanilla_pet_paths.append(r)

    print(f"  Vanilla/game pet records found: {len(vanilla_pet_paths)}")

    # Check all soul pets for equipment
    pets_with_equip = []
    pets_loot_tables = {}  # pet_name -> {slot: [paths]}

    all_pets_to_check = soul_pets + vanilla_pet_paths
    # Also specifically look for known pet records that might be elsewhere
    # (Aletha Darkclaw, warrior pets, caster pets)
    aletha_recs = [r for r in all_records if 'aletha' in r.lower() or 'darkclaw' in r.lower()]
    if aletha_recs:
        print(f"\n  Aletha/Darkclaw records: {aletha_recs}")
        all_pets_to_check.extend(aletha_recs)

    # Also look for chimera
    chimera_recs = [r for r in all_records if 'chimera' in r.lower()
                    and ('pet' in r.lower() or 'soulskill' in r.lower())]
    if chimera_recs:
        print(f"  Chimera pet records: {chimera_recs}")

    print(f"\n  Checking {len(all_pets_to_check)} pet records for equipment fields...")

    for rec in sorted(set(all_pets_to_check)):
        fields = db.get_fields(rec)
        if fields is None:
            continue

        has_equip = False
        pet_loot = {}
        for key, tf in fields.items():
            rn = key.split('###')[0]
            rl = rn.lower()
            if (rl.startswith('chancetoequip') or
                (rl.startswith('loot') and 'item' in rl) or
                (rl.startswith('equip') and 'item' in rl)):
                has_equip = True
                # Track loot paths
                if tf.dtype == 2 and tf.values:
                    for v in tf.values:
                        if isinstance(v, str) and v.strip() and v.endswith('.dbr'):
                            if rn not in pet_loot:
                                pet_loot[rn] = []
                            pet_loot[rn].append(v)

        if has_equip:
            pets_with_equip.append(rec)
            pets_loot_tables[rec] = pet_loot

    print(f"\n  Pets WITH equipment fields: {len(pets_with_equip)}")

    # Dump equipment fields for each armed pet
    for rec in sorted(pets_with_equip):
        # Skip Lyia _1 (already shown in section 1)
        if lyia_pet_path and rec == lyia_pet_path:
            continue
        dump_equip_fields(db, rec, f"ARMED PET: {rec.split('/')[-1].split(chr(92))[-1]}")

    # Collect all pet loot table paths
    print(f"\n\n  --- ALL LOOT TABLES REFERENCED BY PETS ---")
    all_pet_loot_paths = defaultdict(set)  # slot_field -> set of paths
    for rec, slots in pets_loot_tables.items():
        for slot, paths in slots.items():
            for p in paths:
                all_pet_loot_paths[slot].add(p)

    for slot in sorted(all_pet_loot_paths.keys()):
        print(f"\n    {slot}:")
        for p in sorted(all_pet_loot_paths[slot]):
            # Note which pets use this path
            users = [r.replace('\\', '/').split('/')[-1]
                     for r, s in pets_loot_tables.items()
                     if slot in s and p in s[slot]]
            print(f"      {p}")
            print(f"        Used by: {', '.join(users)}")

    # ===========================================================================
    # SECTION 6: Cross-reference monster tables with pet tables
    # ===========================================================================
    sep("SECTION 6: CROSS-REFERENCE - MONSTER TABLES ALSO USED BY PETS")

    print(f"\n  Monster loot paths (from Rakanizeus + Boneash):")
    all_monster_paths = set()
    for paths in all_monster_loot_paths.values():
        all_monster_paths.update(paths)

    all_pet_paths = set()
    for paths in all_pet_loot_paths.values():
        all_pet_paths.update(paths)

    shared = all_monster_paths & all_pet_paths
    monster_only = all_monster_paths - all_pet_paths
    pet_only = all_pet_paths - all_monster_paths

    print(f"\n  SHARED (used by BOTH monsters and pets) - SAFE to use:")
    if shared:
        for p in sorted(shared):
            print(f"    {p}")
    else:
        print(f"    (none)")

    print(f"\n  MONSTER-ONLY (used by monsters but NOT by any pet):")
    for p in sorted(monster_only):
        print(f"    {p}")

    print(f"\n  PET-ONLY (used by pets but NOT by these monsters):")
    for p in sorted(pet_only):
        print(f"    {p}")

    # ===========================================================================
    # SECTION 7: Follow loot table records to see their contents
    # ===========================================================================
    sep("SECTION 7: LOOT TABLE RECORD CONTENTS")

    # Follow all monster loot table paths
    print(f"\n  --- Following MONSTER loot table records ---")
    for slot in sorted(all_monster_loot_paths.keys()):
        for path in sorted(all_monster_loot_paths[slot]):
            record = path
            if not db.has_record(record):
                record = find_record_ci(db, path)
            if record:
                fields = db.get_fields(record)
                print(f"\n  [{slot}] {path}")
                if fields:
                    for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                        rn = key.split('###')[0]
                        dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
                        vals = tf.values
                        # Skip empty/zero
                        if all(v == 0 or v == '' or v == 0.0 for v in vals):
                            continue
                        if len(vals) > 8:
                            val_str = str(vals[:8]) + f"... ({len(vals)} total)"
                        else:
                            val_str = str(vals)
                        print(f"    {rn:45s} [{dtype:6s}] = {val_str}")
            else:
                print(f"\n  [{slot}] {path} -> NOT FOUND IN DB")

    # Follow all pet loot table paths
    print(f"\n  --- Following PET loot table records ---")
    seen = set()
    for slot in sorted(all_pet_loot_paths.keys()):
        for path in sorted(all_pet_loot_paths[slot]):
            if path in seen:
                continue
            seen.add(path)
            record = path
            if not db.has_record(record):
                record = find_record_ci(db, path)
            if record:
                fields = db.get_fields(record)
                print(f"\n  [{slot}] {path}")
                if fields:
                    for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
                        rn = key.split('###')[0]
                        dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
                        vals = tf.values
                        if all(v == 0 or v == '' or v == 0.0 for v in vals):
                            continue
                        if len(vals) > 8:
                            val_str = str(vals[:8]) + f"... ({len(vals)} total)"
                        else:
                            val_str = str(vals)
                        print(f"    {rn:45s} [{dtype:6s}] = {val_str}")
            else:
                print(f"\n  [{slot}] {path} -> NOT FOUND IN DB")

    # ===========================================================================
    # SECTION 8: Deep dive - check Rakanizeus & Boneash pet records
    # ===========================================================================
    sep("SECTION 8: CURRENT RAKANIZEUS & BONEASH PET RECORDS")

    rakan_pets = [r for r in all_records
                  if 'rakanizeus' in r.lower() and 'soulskill' in r.lower()]
    boneash_pets = [r for r in all_records
                    if 'boneash' in r.lower() and 'soulskill' in r.lower()]

    print(f"\n  Rakanizeus pet records: {rakan_pets}")
    for rec in sorted(rakan_pets):
        dump_equip_fields(db, rec, f"RAKANIZEUS PET: {rec}")

    print(f"\n  Boneash pet records: {boneash_pets}")
    for rec in sorted(boneash_pets):
        dump_equip_fields(db, rec, f"BONEASH PET: {rec}")

    # ===========================================================================
    # SECTION 9: Broader loot table search for each slot type
    # ===========================================================================
    sep("SECTION 9: FINDING CANDIDATE LOOT TABLES FOR EACH PET SLOT")

    # For Rakanizeus (melee warrior): sword/axe/club, shield, heavy torso, legs, arms
    # For Boneash (caster skeleton): staff, robes, head piece, rings

    # Let's search more broadly - look at what ALL monster records use for equipment
    print(f"\n  Scanning ALL creature records for loot table patterns...")

    # Collect loot table usage across all creatures
    all_creature_loot = defaultdict(lambda: defaultdict(int))  # slot -> path -> count

    creature_count = 0
    for rec in all_records:
        rl = rec.lower().replace('/', '\\')
        if '\\creature\\' not in rl:
            continue
        creature_count += 1
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in fields.items():
            rn = key.split('###')[0]
            rl2 = rn.lower()
            if rl2.startswith('loot') and 'item' in rl2 and tf.dtype == 2:
                for v in tf.values:
                    if isinstance(v, str) and v.strip() and v.endswith('.dbr'):
                        all_creature_loot[rn][v] += 1

    print(f"  Scanned {creature_count} creature records")

    # Show top loot tables for each slot
    slot_names_of_interest = [
        'lootRightHandItem1', 'lootRightHandItem2', 'lootRightHandItem3',
        'lootLeftHandItem1', 'lootLeftHandItem2', 'lootLeftHandItem3',
        'lootTorsoItem1', 'lootTorsoItem2', 'lootTorsoItem3',
        'lootHeadItem1', 'lootHeadItem2', 'lootHeadItem3',
        'lootForearmItem1', 'lootForearmItem2',
        'lootLowerBodyItem1', 'lootLowerBodyItem2',
        'lootFinger1Item1', 'lootFinger2Item1',
        'lootMiscItem1', 'lootMiscItem2',
    ]

    for slot in slot_names_of_interest:
        if slot in all_creature_loot:
            entries = sorted(all_creature_loot[slot].items(), key=lambda x: -x[1])
            print(f"\n  {slot} (top 15 most-used loot tables):")
            for path, count in entries[:15]:
                # Check if also used by any pet
                pet_marker = " <-- ALSO USED BY PET" if path in all_pet_paths else ""
                print(f"    [{count:4d} uses] {path}{pet_marker}")

    # ===========================================================================
    # SECTION 10: Specific recommendations
    # ===========================================================================
    sep("SECTION 10: ANALYSIS AND RECOMMENDATIONS")

    print("""
  This section identifies the best loot table paths for each pet slot.
  Priority: tables used by BOTH monsters and working pets > tables used by
  similar monster types > commonly-used tables.
  """)

    # Find what slots Lyia uses (the baseline)
    if lyia_pet_path:
        lyia_fields = db.get_fields(lyia_pet_path)
        if lyia_fields:
            print(f"  LYIA BASELINE SLOTS:")
            for key, tf in sorted(lyia_fields.items(), key=lambda x: x[0].split('###')[0]):
                rn = key.split('###')[0]
                rl = rn.lower()
                if rl.startswith('chancetoequip') and tf.values and any(float(v) > 0 for v in tf.values if v):
                    # Find corresponding loot field
                    # e.g., chanceToEquipRightHand -> lootRightHandItem1
                    slot_part = rn.replace('chanceToEquip', '')
                    loot_field = f"loot{slot_part}Item1"
                    loot_val = get_field_value(lyia_fields, loot_field)
                    print(f"    {rn} = {tf.values}  ->  {loot_field} = {loot_val}")

    # Show which slot names Rakanizeus monster uses
    print(f"\n  RAKANIZEUS MONSTER SLOT MAPPING:")
    for rec in sorted(rakan_monsters):
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
            rn = key.split('###')[0]
            rl = rn.lower()
            if rl.startswith('chancetoequip') and tf.values and any(float(v) > 0 for v in tf.values if v):
                slot_part = rn.replace('chanceToEquip', '')
                loot_field = f"loot{slot_part}Item1"
                loot_val = get_field_value(fields, loot_field)
                # Also check equip variant
                equip_field = f"equip{slot_part}Item1"
                equip_val = get_field_value(fields, equip_field)
                print(f"    {rn} = {tf.values}")
                if loot_val:
                    print(f"      {loot_field} = {loot_val}")
                if equip_val:
                    print(f"      {equip_field} = {equip_val}")

    print(f"\n  BONEASH MONSTER SLOT MAPPING:")
    for rec in sorted(boneash_monsters):
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in sorted(fields.items(), key=lambda x: x[0].split('###')[0]):
            rn = key.split('###')[0]
            rl = rn.lower()
            if rl.startswith('chancetoequip') and tf.values and any(float(v) > 0 for v in tf.values if v):
                slot_part = rn.replace('chanceToEquip', '')
                loot_field = f"loot{slot_part}Item1"
                loot_val = get_field_value(fields, loot_field)
                equip_field = f"equip{slot_part}Item1"
                equip_val = get_field_value(fields, equip_field)
                print(f"    {rn} = {tf.values}")
                if loot_val:
                    print(f"      {loot_field} = {loot_val}")
                if equip_val:
                    print(f"      {equip_field} = {equip_val}")

    print(f"\n{'=' * 100}")
    print(f"  DIAGNOSTIC COMPLETE")
    print(f"{'=' * 100}")


if __name__ == '__main__':
    main()
