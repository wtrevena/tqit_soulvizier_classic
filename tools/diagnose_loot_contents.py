"""
Trace what items the pet equipment loot tables actually produce.

For each loot table assigned to Rakanizeus and Boneash pets, reads the record,
shows its structure (template, lootName/lootWeight fields), then follows
references one level deeper to see what actual items or sub-tables they point to.
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase, DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

DTYPE_NAMES = {0: "INT", 1: "FLOAT", 2: "STRING", 3: "BOOL"}

DB_PATH = Path(__file__).parent.parent / "work" / "SoulvizierClassic" / "Database" / "SoulvizierClassic.arz"


def sep(title, char="=", width=100):
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}")


def get_field(fields, name):
    """Get TypedField by base name (ignoring ### suffix). Returns None if missing."""
    if fields is None:
        return None
    if name in fields:
        return fields[name]
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            return tf
    return None


def get_val(fields, name, default=None):
    """Get value(s) for a field by base name."""
    tf = get_field(fields, name)
    if tf is None:
        return default
    return tf.values


def find_record_ci(db, path):
    """Find a record by case-insensitive path match."""
    if db.has_record(path):
        return path
    path_norm = path.lower().replace('/', '\\')
    for name in db.record_names():
        if name.lower().replace('/', '\\') == path_norm:
            return name
    return None


def get_all_fields_matching(fields, prefix):
    """Get all fields whose base name starts with prefix. Returns [(base_name, TypedField)]."""
    results = []
    if fields is None:
        return results
    for key, tf in fields.items():
        base = key.split('###')[0]
        if base.lower().startswith(prefix.lower()):
            results.append((base, tf))
    return results


def dump_all_nonzero(fields, label=""):
    """Dump all non-zero/non-empty fields."""
    if fields is None:
        print(f"    [RECORD NOT FOUND]")
        return
    if label:
        print(f"    --- {label} ---")
    for key, tf in fields.items():
        base = key.split('###')[0]
        dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
        vals = tf.values
        # Skip empty/zero
        if all(v == 0 or v == '' or v == 0.0 for v in vals):
            continue
        if len(vals) > 10:
            val_str = str(vals[:10]) + f"... ({len(vals)} total)"
        else:
            val_str = str(vals)
        print(f"      {base:45s} [{dtype:6s}] = {val_str}")


def analyze_loot_table(db, path, indent=0):
    """
    Analyze a loot table record. Returns a dict with structured info.
    Shows template, lootName*/lootWeight*, numItems, and follows references.
    """
    prefix = "  " * indent + "  "
    record_name = find_record_ci(db, path)
    if record_name is None:
        print(f"{prefix}[NOT FOUND IN DB: {path}]")
        return None

    fields = db.get_fields(record_name)
    if fields is None:
        print(f"{prefix}[EMPTY RECORD: {record_name}]")
        return None

    # Template / Class
    tpl = get_val(fields, 'templateName', ['?'])
    cls = get_val(fields, 'Class', ['?'])
    print(f"{prefix}Record: {record_name}")
    print(f"{prefix}  templateName: {tpl}")
    print(f"{prefix}  Class: {cls}")

    # numItems / numberOfItems
    for nf in ['numItems', 'numberOfItems', 'numRandItems']:
        v = get_val(fields, nf)
        if v is not None:
            print(f"{prefix}  {nf}: {v}")

    # Show all lootName* and lootWeight* fields
    loot_names = get_all_fields_matching(fields, 'lootName')
    loot_weights = get_all_fields_matching(fields, 'lootWeight')

    # Also check for bellWeight / bellSlope / etc (DynWeight params)
    for dyn_field in ['bellSlope', 'bellWeight', 'itemLevel', 'itemLevelVariance',
                      'bellCenterLevel', 'bellCenterVariance']:
        v = get_val(fields, dyn_field)
        if v is not None:
            print(f"{prefix}  {dyn_field}: {v}")

    # Check for lootRandomizerName / lootRandomizerWeight (FixedWeight)
    rand_names = get_all_fields_matching(fields, 'lootRandomizerName')
    rand_weights = get_all_fields_matching(fields, 'lootRandomizerWeight')

    if rand_names:
        print(f"{prefix}  [Has lootRandomizerName fields: {len(rand_names)}]")
        for base, tf in rand_names:
            print(f"{prefix}    {base}: {tf.values}")
        for base, tf in rand_weights:
            print(f"{prefix}    {base}: {tf.values}")

    # Show loot entries
    entries = []
    if loot_names:
        print(f"{prefix}  lootName/lootWeight entries:")
        # Pair them up
        weight_dict = {}
        for base, tf in loot_weights:
            weight_dict[base] = tf.values
        for base, tf in loot_names:
            # Get corresponding weight
            weight_key = base.replace('lootName', 'lootWeight')
            weight = weight_dict.get(weight_key, ['?'])
            vals = tf.values
            for v in vals:
                if isinstance(v, str) and v.strip():
                    print(f"{prefix}    {base}: {v}  (weight: {weight})")
                    entries.append((v, weight))

    # Also check tablelootName / tablelootWeight (some tables use this format)
    table_names = get_all_fields_matching(fields, 'tablelootName')
    table_weights = get_all_fields_matching(fields, 'tablelootWeight')
    if table_names:
        print(f"{prefix}  [Also has tablelootName fields]")
        tw_dict = {}
        for base, tf in table_weights:
            tw_dict[base] = tf.values
        for base, tf in table_names:
            wk = base.replace('tablelootName', 'tablelootWeight')
            w = tw_dict.get(wk, ['?'])
            for v in tf.values:
                if isinstance(v, str) and v.strip():
                    print(f"{prefix}    {base}: {v}  (weight: {w})")
                    entries.append((v, w))

    # Check for any other non-zero fields we might have missed
    known_prefixes = ['lootname', 'lootweight', 'templatename', 'class', 'numitems',
                      'numberofitems', 'numranditems', 'bellslope', 'bellweight',
                      'itemlevel', 'itemlevelvariance', 'bellcenterlevel',
                      'bellcentervariance', 'lootrandomizername', 'lootrandomizerweight',
                      'tablelootname', 'tablelootweight']
    other_fields = []
    for key, tf in fields.items():
        base = key.split('###')[0]
        bl = base.lower()
        if not any(bl.startswith(p) for p in known_prefixes):
            vals = tf.values
            if not all(v == 0 or v == '' or v == 0.0 for v in vals):
                other_fields.append((base, tf))
    if other_fields:
        print(f"{prefix}  Other non-zero fields:")
        for base, tf in other_fields:
            dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
            print(f"{prefix}    {base:40s} [{dtype}] = {tf.values}")

    return entries


def analyze_item_record(db, path, indent=0):
    """
    Analyze an actual item (equipment) record. Shows key stats.
    """
    prefix = "  " * indent + "  "
    record_name = find_record_ci(db, path)
    if record_name is None:
        print(f"{prefix}[NOT FOUND: {path}]")
        return

    fields = db.get_fields(record_name)
    if fields is None:
        print(f"{prefix}[EMPTY RECORD: {record_name}]")
        return

    cls = get_val(fields, 'Class', ['?'])
    tpl = get_val(fields, 'templateName', ['?'])
    print(f"{prefix}Record: {record_name}")
    print(f"{prefix}  Class: {cls}")
    print(f"{prefix}  templateName: {tpl}")

    # Item identity
    for f in ['itemNameTag', 'description', 'itemText', 'itemClassification',
              'itemNameOrder', 'FileDescription']:
        v = get_val(fields, f)
        if v is not None and v != [''] and v != [0]:
            print(f"{prefix}  {f}: {v}")

    # Level / requirements
    for f in ['levelRequirement', 'itemLevel', 'Act', 'itemCost']:
        v = get_val(fields, f)
        if v is not None and v != [0] and v != [0.0]:
            print(f"{prefix}  {f}: {v}")

    # Damage stats
    damage_prefixes = ['offensivePhys', 'offensiveFire', 'offensiveCold', 'offensiveLightning',
                       'offensivePoison', 'offensiveLife', 'offensivePierce', 'offensiveElemental',
                       'offensiveBaseFire', 'offensiveBaseCold', 'offensiveBaseLightning',
                       'offensiveBasePoison', 'offensiveBaseLife', 'offensiveManaBurn',
                       'retaliationPhys', 'retaliationFire',
                       'offensiveSlowAttackSpeed', 'offensiveSlowDefensiveAbility',
                       'characterOffensiveAbility', 'characterDefensiveAbility',
                       'characterStrength', 'characterDexterity', 'characterIntelligence',
                       'characterLife', 'characterMana',
                       'offensiveTotalDamageModifier',
                       'defensivePhysical', 'defensiveFire', 'defensiveCold', 'defensiveLightning',
                       'defensivePoison', 'defensiveLife', 'defensivePierce', 'defensiveElemental',
                       'defensiveProtection', 'defensiveAbsorption',
                       'offensiveGlobalChance', 'skillCooldownReduction']

    shown_any = False
    for key, tf in fields.items():
        base = key.split('###')[0]
        bl = base.lower()
        if any(bl.startswith(dp.lower()) for dp in damage_prefixes):
            vals = tf.values
            if not all(v == 0 or v == 0.0 for v in vals):
                dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
                if not shown_any:
                    print(f"{prefix}  -- Combat stats --")
                    shown_any = True
                print(f"{prefix}    {base:40s} [{dtype}] = {vals}")

    # Check for skill grants
    for f in ['itemSkillName', 'itemSkillAutoController', 'augmentSkillName1',
              'augmentSkillLevel1', 'skillName', 'petSkillName']:
        v = get_val(fields, f)
        if v is not None and v != [''] and v != [0]:
            print(f"{prefix}  {f}: {v}")


def is_loot_table(db, path):
    """Check if a record is a loot table (vs an actual item)."""
    record_name = find_record_ci(db, path)
    if record_name is None:
        return None  # unknown
    fields = db.get_fields(record_name)
    if fields is None:
        return None
    cls = get_val(fields, 'Class', ['?'])
    tpl = get_val(fields, 'templateName', ['?'])
    cls_str = cls[0] if cls else '?'
    tpl_str = str(tpl[0]) if tpl else '?'
    # Loot tables have LootItemTable or similar class, or template path contains loottable
    if 'loot' in cls_str.lower() and 'table' in cls_str.lower():
        return True
    if 'loottable' in tpl_str.lower():
        return True
    # Check for lootName fields
    loot_names = get_all_fields_matching(fields, 'lootName')
    if loot_names:
        return True
    return False


def trace_loot_table(db, path, depth=0, max_depth=3, visited=None):
    """
    Recursively trace a loot table, following references.
    Shows the full tree of what a table produces.
    """
    if visited is None:
        visited = set()

    path_key = path.lower().replace('/', '\\')
    if path_key in visited:
        prefix = "  " * depth + "  "
        print(f"{prefix}[ALREADY VISITED - circular reference]")
        return
    visited.add(path_key)

    if depth > max_depth:
        prefix = "  " * depth + "  "
        print(f"{prefix}[MAX DEPTH REACHED]")
        return

    # Check if this is a loot table or an item
    is_table = is_loot_table(db, path)

    if is_table:
        entries = analyze_loot_table(db, path, indent=depth)
        if entries:
            for ref_path, weight in entries:
                print()
                sub_is_table = is_loot_table(db, ref_path)
                if sub_is_table:
                    trace_loot_table(db, ref_path, depth + 1, max_depth, visited)
                elif sub_is_table is False:
                    analyze_item_record(db, ref_path, indent=depth + 1)
                else:
                    prefix = "  " * (depth + 1) + "  "
                    print(f"{prefix}[RECORD NOT FOUND: {ref_path}]")
    elif is_table is False:
        analyze_item_record(db, path, indent=depth)
    else:
        prefix = "  " * depth + "  "
        print(f"{prefix}[RECORD NOT FOUND: {path}]")


def main():
    print(f"Loading database: {DB_PATH}")
    db = ArzDatabase.from_arz(DB_PATH)
    print(f"Total records: {len(db.record_names())}")

    # =========================================================================
    # Define all the loot tables we need to trace
    # =========================================================================

    rakanizeus_tables = {
        "LeftHand (Swords)": [
            "records/item/loottables/weapons/commondynamic/sword_n01.dbr",
            "records/item/loottables/weapons/commondynamic/sword_e01.dbr",
            "records/item/loottables/weapons/commondynamic/sword_l01.dbr",
        ],
        "Forearm (Lyia default - armbands)": [
            # We'll discover these from the pet record
        ],
        "Finger1 (Lyia default - rings)": [
            # We'll discover these from the pet record
        ],
        "Finger2 (Rakanizeus soul rings)": [
            "records/item/loottables/equipmentring/soul/satyr/rakanizeus_soul_n.dbr",
            "records/item/loottables/equipmentring/soul/satyr/rakanizeus_soul_e.dbr",
            "records/item/loottables/equipmentring/soul/satyr/rakanizeus_soul_l.dbr",
        ],
    }

    boneash_tables = {
        "LeftHand (Staves)": [
            "records/item/loottables/weapons/mastertables/staff_dyn_n02.dbr",
            "records/item/loottables/weapons/mastertables/staff_dyn_e02.dbr",
            "records/item/loottables/weapons/mastertables/staff_dyn_l02.dbr",
        ],
        "Forearm (Bracelets)": [
            "records/item/loottables/arms/commondynamic/bracelet_n02.dbr",
            "records/item/loottables/arms/commondynamic/bracelet_e02.dbr",
            "records/item/loottables/arms/commondynamic/bracelet_l02.dbr",
        ],
        "Finger1 (Lyia default - rings)": [
            # We'll discover these from the pet record
        ],
        "Finger2 (Boneash soul rings)": [
            "records/item/loottables/equipmentring/soul/skeleton/boneash_soul_n.dbr",
            "records/item/loottables/equipmentring/soul/skeleton/boneash_soul_e.dbr",
            "records/item/loottables/equipmentring/soul/skeleton/boneash_soul_l.dbr",
        ],
    }

    # =========================================================================
    # SECTION 0: Find the actual pet records and discover Lyia's defaults
    # =========================================================================
    sep("SECTION 0: PET RECORDS - DISCOVERING LYIA DEFAULTS FOR SHARED SLOTS")

    all_records = db.record_names()

    # Find Lyia pet records to get her default forearm/finger loot tables
    lyia_pets = [r for r in all_records
                 if 'lyia' in r.lower() and ('pet' in r.lower() or 'soulskill' in r.lower())
                 and r.lower().endswith('.dbr')]
    print(f"  Lyia pet records: {lyia_pets}")

    # Find Rakanizeus and Boneash pet records
    rakan_pets = [r for r in all_records
                  if 'rakanizeus' in r.lower() and ('pet' in r.lower() or 'soulskill' in r.lower())
                  and r.lower().endswith('.dbr')]
    boneash_pets = [r for r in all_records
                    if 'boneash' in r.lower() and ('pet' in r.lower() or 'soulskill' in r.lower())
                    and r.lower().endswith('.dbr')]

    print(f"  Rakanizeus pet records: {rakan_pets}")
    print(f"  Boneash pet records: {boneash_pets}")

    # Extract Lyia's loot tables
    lyia_forearm_tables = []
    lyia_finger1_tables = []

    for rec in lyia_pets:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        print(f"\n  --- {rec} ---")
        # Show ALL equipment-related fields
        for key, tf in fields.items():
            base = key.split('###')[0]
            bl = base.lower()
            if (bl.startswith('chancetoequip') or
                bl.startswith('loot') and 'item' in bl or
                bl.startswith('equip') and 'item' in bl):
                dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
                print(f"    {base:45s} [{dtype}] = {tf.values}")

                if bl == 'lootforearmitem1' and tf.dtype == DATA_TYPE_STRING:
                    lyia_forearm_tables = [v for v in tf.values if isinstance(v, str) and v.strip()]
                if bl == 'lootfinger1item1' and tf.dtype == DATA_TYPE_STRING:
                    lyia_finger1_tables = [v for v in tf.values if isinstance(v, str) and v.strip()]

    print(f"\n  Lyia forearm tables (default): {lyia_forearm_tables}")
    print(f"  Lyia finger1 tables (default): {lyia_finger1_tables}")

    # Also show the actual Rakanizeus and Boneash pet record equipment fields
    for label, recs in [("RAKANIZEUS", rakan_pets), ("BONEASH", boneash_pets)]:
        for rec in recs:
            fields = db.get_fields(rec)
            if fields is None:
                continue
            print(f"\n  --- {label}: {rec} ---")
            for key, tf in fields.items():
                base = key.split('###')[0]
                bl = base.lower()
                if (bl.startswith('chancetoequip') or
                    (bl.startswith('loot') and 'item' in bl) or
                    (bl.startswith('equip') and 'item' in bl)):
                    dtype = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
                    print(f"    {base:45s} [{dtype}] = {tf.values}")

                    # Capture actual tables for the "Lyia default" slots
                    if label == "RAKANIZEUS":
                        if bl == 'lootforearmitem1' and tf.dtype == DATA_TYPE_STRING:
                            vals = [v for v in tf.values if isinstance(v, str) and v.strip()]
                            if vals:
                                rakanizeus_tables["Forearm (Lyia default - armbands)"] = vals
                        if bl == 'lootfinger1item1' and tf.dtype == DATA_TYPE_STRING:
                            vals = [v for v in tf.values if isinstance(v, str) and v.strip()]
                            if vals:
                                rakanizeus_tables["Finger1 (Lyia default - rings)"] = vals
                    elif label == "BONEASH":
                        if bl == 'lootfinger1item1' and tf.dtype == DATA_TYPE_STRING:
                            vals = [v for v in tf.values if isinstance(v, str) and v.strip()]
                            if vals:
                                boneash_tables["Finger1 (Lyia default - rings)"] = vals

    # =========================================================================
    # SECTION 1: TRACE RAKANIZEUS LOOT TABLES
    # =========================================================================
    sep("SECTION 1: RAKANIZEUS (WARRIOR SATYR) - LOOT TABLE CONTENTS")

    for slot_label, paths in rakanizeus_tables.items():
        if not paths:
            print(f"\n  [{slot_label}] - NO TABLES (empty slot)")
            continue
        print(f"\n{'~' * 90}")
        print(f"  SLOT: {slot_label}")
        print(f"  Tables: {paths}")
        print(f"{'~' * 90}")

        for i, path in enumerate(paths):
            suffix = ""
            if len(paths) == 3:
                suffix = ["[NORMAL]", "[EPIC]", "[LEGENDARY]"][i]
            elif len(paths) == 1:
                suffix = "[ALL DIFFICULTIES]"
            print(f"\n  === {suffix} {path} ===")
            trace_loot_table(db, path, depth=0)

    # =========================================================================
    # SECTION 2: TRACE BONEASH LOOT TABLES
    # =========================================================================
    sep("SECTION 2: BONEASH (SKELETON CASTER) - LOOT TABLE CONTENTS")

    for slot_label, paths in boneash_tables.items():
        if not paths:
            print(f"\n  [{slot_label}] - NO TABLES (empty slot)")
            continue
        print(f"\n{'~' * 90}")
        print(f"  SLOT: {slot_label}")
        print(f"  Tables: {paths}")
        print(f"{'~' * 90}")

        for i, path in enumerate(paths):
            suffix = ""
            if len(paths) == 3:
                suffix = ["[NORMAL]", "[EPIC]", "[LEGENDARY]"][i]
            elif len(paths) == 1:
                suffix = "[ALL DIFFICULTIES]"
            print(f"\n  === {suffix} {path} ===")
            trace_loot_table(db, path, depth=0)

    # =========================================================================
    # SECTION 3: COMPARE _n01 vs _n02 NUMBERING
    # =========================================================================
    sep("SECTION 3: COMPARE _n01 vs _n02 NUMBERING")

    # Find all records matching these patterns
    patterns_to_compare = [
        ("sword_n01", "sword_n02"),
        ("sword_e01", "sword_e02"),
        ("sword_l01", "sword_l02"),
        ("staff_dyn_n01", "staff_dyn_n02"),
        ("staff_dyn_e01", "staff_dyn_e02"),
        ("staff_dyn_l01", "staff_dyn_l02"),
        ("bracelet_n01", "bracelet_n02"),
        ("bracelet_e01", "bracelet_e02"),
        ("bracelet_l01", "bracelet_l02"),
    ]

    for name1, name2 in patterns_to_compare:
        # Find records
        recs1 = [r for r in all_records if name1 + '.dbr' in r.lower()]
        recs2 = [r for r in all_records if name2 + '.dbr' in r.lower()]

        if recs1 or recs2:
            print(f"\n  --- {name1} vs {name2} ---")
            for r in recs1:
                print(f"    {name1}: {r}")
                fields = db.get_fields(r)
                if fields:
                    cls = get_val(fields, 'Class', ['?'])
                    num = get_val(fields, 'numItems', get_val(fields, 'numberOfItems', ['?']))
                    print(f"      Class: {cls}, numItems: {num}")
                    # Count loot entries
                    loot_names = get_all_fields_matching(fields, 'lootName')
                    entries = []
                    for base, tf in loot_names:
                        for v in tf.values:
                            if isinstance(v, str) and v.strip():
                                entries.append(v)
                    print(f"      lootName entries: {len(entries)}")
                    for e in entries[:5]:
                        print(f"        -> {e}")
                    if len(entries) > 5:
                        print(f"        ... and {len(entries) - 5} more")
            for r in recs2:
                print(f"    {name2}: {r}")
                fields = db.get_fields(r)
                if fields:
                    cls = get_val(fields, 'Class', ['?'])
                    num = get_val(fields, 'numItems', get_val(fields, 'numberOfItems', ['?']))
                    print(f"      Class: {cls}, numItems: {num}")
                    loot_names = get_all_fields_matching(fields, 'lootName')
                    entries = []
                    for base, tf in loot_names:
                        for v in tf.values:
                            if isinstance(v, str) and v.strip():
                                entries.append(v)
                    print(f"      lootName entries: {len(entries)}")
                    for e in entries[:5]:
                        print(f"        -> {e}")
                    if len(entries) > 5:
                        print(f"        ... and {len(entries) - 5} more")

            if not recs1:
                print(f"    {name1}: NOT FOUND")
            if not recs2:
                print(f"    {name2}: NOT FOUND")

    # =========================================================================
    # SECTION 4: HOW THE 3-VALUE DIFFICULTY ARRAY WORKS
    # =========================================================================
    sep("SECTION 4: THE 3-VALUE DIFFICULTY ARRAY MECHANISM")

    print("""
  In TQ:IT, pet loot table fields like lootLeftHandItem1 store an array of 3
  string values: [normal_path, epic_path, legendary_path].

  Let's verify this by checking:
  1. The actual array values on our pet records
  2. What the game's Pet.tpl template says about these fields
  3. How other working pets handle difficulty scaling
    """)

    # Show the actual arrays from our pet records
    for label, recs in [("RAKANIZEUS", rakan_pets), ("BONEASH", boneash_pets)]:
        for rec in recs:
            fields = db.get_fields(rec)
            if fields is None:
                continue
            print(f"\n  {label}: {rec}")
            for key, tf in fields.items():
                base = key.split('###')[0]
                bl = base.lower()
                if bl.startswith('loot') and 'item' in bl and tf.dtype == DATA_TYPE_STRING:
                    vals = tf.values
                    if any(isinstance(v, str) and v.strip() for v in vals):
                        print(f"    {base}: ({len(vals)} values)")
                        for i, v in enumerate(vals):
                            diff_label = ["Normal", "Epic", "Legendary"][i] if i < 3 else f"idx{i}"
                            print(f"      [{i}] {diff_label}: {v}")

    # Also check how many values chanceToEquip fields have
    print(f"\n  chanceToEquip array sizes (should match difficulty count):")
    for label, recs in [("RAKANIZEUS", rakan_pets), ("BONEASH", boneash_pets)]:
        for rec in recs:
            fields = db.get_fields(rec)
            if fields is None:
                continue
            for key, tf in fields.items():
                base = key.split('###')[0]
                bl = base.lower()
                if bl.startswith('chancetoequip'):
                    print(f"    {label} {base}: {tf.values} ({len(tf.values)} values, dtype={DTYPE_NAMES.get(tf.dtype,'?')})")

    # Check what vanilla game pets do
    print(f"\n  Checking vanilla Nature Nymph for comparison:")
    nymph_recs = [r for r in all_records
                  if 'nymph' in r.lower() and 'pet' in r.lower() and r.lower().endswith('.dbr')]
    if not nymph_recs:
        nymph_recs = [r for r in all_records if 'nymph' in r.lower() and r.lower().endswith('.dbr')]
    for rec in nymph_recs[:3]:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        has_loot = False
        for key, tf in fields.items():
            base = key.split('###')[0]
            bl = base.lower()
            if bl.startswith('loot') and 'item' in bl and tf.dtype == DATA_TYPE_STRING:
                vals = tf.values
                if any(isinstance(v, str) and v.strip() for v in vals):
                    if not has_loot:
                        print(f"\n    {rec}")
                        has_loot = True
                    print(f"      {base}: ({len(vals)} values) {vals}")

    # Also check core dweller
    print(f"\n  Checking Core Dweller for comparison:")
    cd_recs = [r for r in all_records
               if 'coredweller' in r.lower() and r.lower().endswith('.dbr')]
    if not cd_recs:
        cd_recs = [r for r in all_records if 'core_dweller' in r.lower() and r.lower().endswith('.dbr')]
    for rec in cd_recs[:3]:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        has_loot = False
        for key, tf in fields.items():
            base = key.split('###')[0]
            bl = base.lower()
            if (bl.startswith('loot') and 'item' in bl and tf.dtype == DATA_TYPE_STRING):
                vals = tf.values
                if any(isinstance(v, str) and v.strip() for v in vals):
                    if not has_loot:
                        print(f"\n    {rec}")
                        has_loot = True
                    print(f"      {base}: ({len(vals)} values) {vals}")
            elif bl.startswith('chancetoequip'):
                vals = tf.values
                if any(v != 0 and v != 0.0 for v in vals):
                    if not has_loot:
                        print(f"\n    {rec}")
                        has_loot = True
                    print(f"      {base}: {vals}")

    # =========================================================================
    # SECTION 5: WHAT DO "commondynamic" vs "mastertables" MEAN?
    # =========================================================================
    sep("SECTION 5: DIRECTORY STRUCTURE - commondynamic vs mastertables vs soul")

    # Count how many tables are in each directory
    dirs = defaultdict(list)
    for r in all_records:
        rl = r.lower().replace('\\', '/')
        if 'loottables/' in rl:
            parts = rl.split('/')
            # Get the parent directories
            try:
                lt_idx = parts.index('loottables')
                if lt_idx + 2 < len(parts):
                    dir_path = '/'.join(parts[lt_idx:lt_idx+3])
                    dirs[dir_path].append(r)
            except ValueError:
                pass

    print(f"\n  Loot table directory structure:")
    for d in sorted(dirs.keys()):
        print(f"    {d:50s} ({len(dirs[d])} records)")

    # Specifically compare commondynamic vs mastertables for weapons
    print(f"\n  Specifically for weapons:")
    weapon_cd = [r for r in all_records
                 if 'loottables' in r.lower() and 'weapons' in r.lower()
                 and 'commondynamic' in r.lower()]
    weapon_mt = [r for r in all_records
                 if 'loottables' in r.lower() and 'weapons' in r.lower()
                 and 'mastertable' in r.lower()]

    print(f"    commondynamic weapons: {len(weapon_cd)}")
    for r in sorted(weapon_cd)[:10]:
        print(f"      {r.split('/')[-1] if '/' in r else r.split(chr(92))[-1]}")
    if len(weapon_cd) > 10:
        print(f"      ... and {len(weapon_cd) - 10} more")

    print(f"    mastertables weapons: {len(weapon_mt)}")
    for r in sorted(weapon_mt)[:10]:
        print(f"      {r.split('/')[-1] if '/' in r else r.split(chr(92))[-1]}")
    if len(weapon_mt) > 10:
        print(f"      ... and {len(weapon_mt) - 10} more")

    # Pick one commondynamic and one mastertable sword to compare structure
    cd_sword = None
    mt_sword = None
    for r in weapon_cd:
        if 'sword' in r.lower() and '_n' in r.lower():
            cd_sword = r
            break
    for r in weapon_mt:
        if 'sword' in r.lower() and '_n' in r.lower():
            mt_sword = r
            break

    if cd_sword:
        print(f"\n  SAMPLE commondynamic sword: {cd_sword}")
        fields = db.get_fields(cd_sword)
        if fields:
            dump_all_nonzero(fields, "commondynamic sword")

    if mt_sword:
        print(f"\n  SAMPLE mastertables sword: {mt_sword}")
        fields = db.get_fields(mt_sword)
        if fields:
            dump_all_nonzero(fields, "mastertables sword")

    # =========================================================================
    # SECTION 6: SUMMARY & ANALYSIS
    # =========================================================================
    sep("SECTION 6: SUMMARY AND ANALYSIS")

    print("""
  KEY QUESTIONS TO ANSWER:

  1. Are these DYNAMIC tables (random items with random stats)?
     Or do they point to specific fixed items?

  2. What level range are the items?

  3. Are _n01/_e01/_l01 really Normal/Epic/Legendary difficulty tiers?

  4. What kind of swords does the sword table produce?
     What kind of staves does the staff table produce?

  5. How does the 3-value difficulty array work?
     - Is it game difficulty (Normal/Epic/Legendary)?
     - Or is it per-pet-level (levels 1/2/3)?

  6. What's the difference between _n01 and _n02 numbering?

  (See the trace output above for the data to answer these questions.)
    """)

    print(f"\n{'=' * 100}")
    print(f"  DIAGNOSTIC COMPLETE")
    print(f"{'=' * 100}")


if __name__ == '__main__':
    main()
