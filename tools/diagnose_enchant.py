"""
Diagnostic script: Why can't the Obsidian Breastplate be enchanted with Mechanical Parts?

Checks:
1. Find the Obsidian Breastplate record and dump enchant-related fields
2. Find a known enchantable common armor for comparison (same fields side-by-side)
3. Find the Mechanical Parts record and check what it requires/targets
4. Check for record path issues (duplicate records under different prefixes)
5. Look for any charm/relic slot type mismatch
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

DB_PATH = Path(__file__).parent.parent / "work" / "SoulvizierClassic" / "Database" / "SoulvizierClassic.arz"

ENCHANT_KEYWORDS = re.compile(r'(charm|relic|enchant|socket|completion)', re.IGNORECASE)

# Equipment slot booleans used by ItemCharm template
SLOT_BOOLS = (
    'amulet', 'armband', 'axe', 'bodyArmor', 'bow', 'bracelet',
    'club', 'greaves', 'headArmor', 'helmet', 'mace', 'medal',
    'ring', 'shield', 'spear', 'staff', 'sword', 'thrown',
    'dagger', 'scepter',
)


def dump_enchant_fields(db, record_name, label=""):
    """Print all fields related to enchantability for a given record."""
    fields = db.get_fields(record_name)
    if fields is None:
        print(f"  [ERROR] Could not decode fields for: {record_name}")
        return

    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"  Record: {record_name}")
    print(f"  Total fields: {len(fields)}")

    context_keys = ('templateName', 'Class', 'cannotPickUp', 'numRelicSlots',
                    'itemClassification', 'description', 'bitmap',
                    'itemNameTag', 'itemText', 'FileDescription')
    print(f"\n  --- Context Fields ---")
    for key, tf in fields.items():
        real_key = key.split('###')[0]
        if real_key.lower() in [k.lower() for k in context_keys]:
            print(f"    {real_key} (dtype={tf.dtype}): {tf.values}")

    print(f"\n  --- Enchant-Related Fields ---")
    found = 0
    for key, tf in fields.items():
        real_key = key.split('###')[0]
        if ENCHANT_KEYWORDS.search(real_key):
            print(f"    {real_key} (dtype={tf.dtype}): {tf.values}")
            found += 1

    if found == 0:
        print(f"    (none found)")

    print(f"{'='*80}")


def find_obsidian_breastplate(db):
    """Search for records matching 'obsidian' that look like armor/breastplate."""
    print("\n\n### STEP 1: Finding Obsidian Breastplate ###")
    candidates = []
    for name in db.record_names():
        nl = name.lower()
        if 'obsidian' in nl and ('breast' in nl or 'armor' in nl or 'torso' in nl):
            candidates.append(name)

    if not candidates:
        print("  No breastplate/armor match. Broadening to all 'obsidian' records...")
        for name in db.record_names():
            if 'obsidian' in name.lower():
                candidates.append(name)

    print(f"  Found {len(candidates)} candidate(s):")
    for c in candidates:
        print(f"    - {c}")

    return candidates


def find_common_armor(db):
    """Find a common/normal armor piece that should be enchantable."""
    print("\n\n### STEP 3: Finding a known enchantable common armor for comparison ###")
    item_prefixes = ('records\\item\\', 'records/item/',
                     'records\\drxitem\\', 'records/drxitem/')
    candidates = []
    for name in db.record_names():
        nl = name.lower()
        if not any(nl.startswith(p) for p in item_prefixes):
            continue
        if 'equipmentarmor' not in nl:
            continue
        if 'obsidian' in nl:
            continue
        if 'default' in nl:
            continue

        fields = db.get_fields(name)
        if fields is None:
            continue

        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'numRelicSlots' and tf.values and tf.values[0] >= 1:
                candidates.append(name)
                break

        if len(candidates) >= 5:
            break

    if candidates:
        print(f"  Found {len(candidates)} enchantable armor(s). Using first:")
        print(f"    {candidates[0]}")
        return candidates[0]
    else:
        print("  WARNING: Could not find any enchantable armor for comparison!")
        return None


def find_mechanical_parts(db):
    """Find the Mechanical Parts relic/charm record."""
    print("\n\n### STEP 4: Finding Mechanical Parts ###")
    candidates = []
    for name in db.record_names():
        nl = name.lower()
        if 'mechanical' in nl and 'part' in nl:
            candidates.append(name)

    if not candidates:
        for name in db.record_names():
            nl = name.lower()
            if 'mechpart' in nl or 'mechanicalpart' in nl:
                candidates.append(name)

    print(f"  Found {len(candidates)} candidate(s):")
    for c in candidates:
        print(f"    - {c}")

    return candidates


def dump_all_fields(db, record_name, label=""):
    """Dump every single field of a record."""
    fields = db.get_fields(record_name)
    if fields is None:
        print(f"  [ERROR] Could not decode: {record_name}")
        return

    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"  Record: {record_name}")
    print(f"  Total fields: {len(fields)}")
    print(f"  --- ALL Fields ---")
    for key, tf in fields.items():
        real_key = key.split('###')[0]
        print(f"    {real_key} (dtype={tf.dtype}): {tf.values}")
    print(f"{'='*80}")


def get_field(fields, name):
    """Get field value by name from decoded fields dict."""
    if name in fields:
        return fields[name].values
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            return tf.values
    return None


def main():
    print(f"Loading database: {DB_PATH}")
    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)

    db = ArzDatabase.from_arz(DB_PATH)
    print(f"Database loaded: {len(db._raw_records)} records, {len(db.strings)} strings")

    # =========================================================================
    # STEP 1: Find and dump all Obsidian candidates
    # =========================================================================
    obsidian_candidates = find_obsidian_breastplate(db)
    for c in obsidian_candidates:
        dump_enchant_fields(db, c, label="OBSIDIAN CANDIDATE")

    # Identify the actual breastplate (UpperBody armor under records\item\)
    breastplate = None
    for c in obsidian_candidates:
        fields = db.get_fields(c)
        if fields is None:
            continue
        tmpl_vals = get_field(fields, 'templateName')
        cls_vals = get_field(fields, 'Class')
        if tmpl_vals and 'UpperBody' in str(tmpl_vals[0]):
            # Prefer the one under records\item\ (the actual game item, not default)
            if 'default' not in c.lower():
                breastplate = c
                break
            elif breastplate is None:
                breastplate = c

    if breastplate is None:
        # Fallback: any equipmentarmor record
        for c in obsidian_candidates:
            if 'equipmentarmor' in c.lower() and 'default' not in c.lower():
                breastplate = c
                break

    if breastplate:
        print(f"\n  >>> Best breastplate match: {breastplate}")
    else:
        print(f"\n  >>> WARNING: Could not identify the actual breastplate record!")

    # =========================================================================
    # STEP 2: Full field dump of breastplate
    # =========================================================================
    if breastplate:
        print(f"\n\n### STEP 2: Full field dump of Obsidian Breastplate ###")
        dump_all_fields(db, breastplate, label="FULL DUMP - Obsidian Breastplate")

    # =========================================================================
    # STEP 3: Comparison with a known working enchantable armor
    # =========================================================================
    comparison_armor = find_common_armor(db)
    if comparison_armor:
        dump_enchant_fields(db, comparison_armor, label="COMPARISON: Enchantable Armor")

    # =========================================================================
    # STEP 4: Find and dump Mechanical Parts
    # =========================================================================
    mech_candidates = find_mechanical_parts(db)

    # Separate actual charm items from loot tables
    mech_items = [c for c in mech_candidates if 'animalrelics\\' in c.lower() or 'animalrelics/' in c.lower()]
    mech_items = [c for c in mech_items if 'loottable' not in c.lower() and 'lootmagical' not in c.lower()]

    print(f"\n  Mechanical Parts ITEM records (not loot tables): {len(mech_items)}")
    for c in mech_items:
        print(f"    - {c}")

    # Dump the first actual charm item fully
    if mech_items:
        dump_all_fields(db, mech_items[0], label="MECHANICAL PARTS (Charm Item)")

    # =========================================================================
    # STEP 5: Deep comparison & diagnosis
    # =========================================================================
    print("\n\n" + "=" * 80)
    print("  DEEP DIAGNOSIS")
    print("=" * 80)

    # --- Check the breastplate ---
    if breastplate:
        obs_fields = db.get_fields(breastplate)
        slots = get_field(obs_fields, 'numRelicSlots')
        tmpl = get_field(obs_fields, 'templateName')
        cls_val = get_field(obs_fields, 'Class')
        cannot_pick = get_field(obs_fields, 'cannotPickUp')
        classification = get_field(obs_fields, 'itemClassification')

        print(f"\n  Obsidian Breastplate: {breastplate}")
        print(f"    templateName      = {tmpl}")
        print(f"    Class             = {cls_val}")
        print(f"    cannotPickUp      = {cannot_pick}")
        print(f"    numRelicSlots     = {slots}")
        print(f"    itemClassification= {classification}")

        has_slot = slots and slots[0] >= 1
        print(f"    Has relic slot?   = {has_slot}")

        if not has_slot:
            # WHY wasn't it patched?
            print(f"\n    !!! PROBLEM: numRelicSlots is missing or 0 !!!")
            nl = breastplate.lower()
            item_prefixes = ('records\\item\\', 'records/item/',
                             'records\\drxitem\\', 'records/drxitem/')
            in_item_path = any(nl.startswith(p) for p in item_prefixes)
            print(f"    Path starts with item prefix? {in_item_path} (path: {breastplate})")
            if not in_item_path:
                print(f"    >>> ROOT CAUSE: Record is NOT under records/item/ or records/drxitem/")
                print(f"    >>> Patch 3 only patches items under those prefixes!")

    # --- Check the Mechanical Parts targeting ---
    if mech_items:
        mech = mech_items[0]
        mech_fields = db.get_fields(mech)
        print(f"\n  Mechanical Parts: {mech}")
        print(f"    Template: {get_field(mech_fields, 'templateName')}")
        print(f"    Class:    {get_field(mech_fields, 'Class')}")

        print(f"\n    Equipment slot targeting:")
        enabled_slots = []
        for slot in SLOT_BOOLS:
            val = get_field(mech_fields, slot)
            if val:
                status = "ENABLED" if val[0] == 1 else "disabled"
                if val[0] == 1:
                    enabled_slots.append(slot)
                print(f"      {slot:20s} = {val[0]} ({status})")

        print(f"\n    Enabled slots: {enabled_slots}")

        if 'bodyArmor' in enabled_slots:
            print(f"    Mechanical Parts CAN target body armor.")
        else:
            print(f"    !!! Mechanical Parts CANNOT target body armor!")

    # --- Check for record duplication issues ---
    print(f"\n\n  --- Record path analysis ---")
    print(f"  Checking for records under different path prefixes...")
    obsidian_under_item = [c for c in obsidian_candidates
                           if c.lower().startswith('records\\item\\') or c.lower().startswith('records/item/')]
    obsidian_outside_item = [c for c in obsidian_candidates
                              if not (c.lower().startswith('records\\item\\') or c.lower().startswith('records/item/'))]

    print(f"  Under records/item/ ({len(obsidian_under_item)}):")
    for c in obsidian_under_item:
        fields = db.get_fields(c)
        slots = get_field(fields, 'numRelicSlots') if fields else None
        print(f"    {c}  [numRelicSlots={slots}]")

    print(f"  Outside records/item/ ({len(obsidian_outside_item)}):")
    for c in obsidian_outside_item:
        fields = db.get_fields(c)
        slots = get_field(fields, 'numRelicSlots') if fields else None
        print(f"    {c}  [numRelicSlots={slots}]")

    if obsidian_outside_item:
        print(f"\n  !!! WARNING: There are Obsidian records OUTSIDE records/item/")
        print(f"  !!! These records were NOT touched by Patch 3 (make_enchantable)")
        print(f"  !!! If the game resolves the item via one of these paths,")
        print(f"  !!! it would have numRelicSlots=0 and be non-enchantable!")

    # --- Side-by-side field comparison ---
    if breastplate and comparison_armor:
        print(f"\n\n  --- Side-by-side: Obsidian vs Comparison Armor ---")
        obs_f = db.get_fields(breastplate)
        cmp_f = db.get_fields(comparison_armor)

        # Collect all field names from both
        obs_keys = {k.split('###')[0] for k in obs_f} if obs_f else set()
        cmp_keys = {k.split('###')[0] for k in cmp_f} if cmp_f else set()

        # Fields in comparison but missing from obsidian
        missing_in_obs = cmp_keys - obs_keys
        enchant_missing = [k for k in missing_in_obs if ENCHANT_KEYWORDS.search(k)]
        if enchant_missing:
            print(f"    Enchant fields in comparison but MISSING in Obsidian:")
            for k in sorted(enchant_missing):
                cmp_val = get_field(cmp_f, k)
                print(f"      {k} = {cmp_val} (in comparison)")

        # Fields in obsidian but missing from comparison
        missing_in_cmp = obs_keys - cmp_keys
        enchant_extra = [k for k in missing_in_cmp if ENCHANT_KEYWORDS.search(k)]
        if enchant_extra:
            print(f"    Enchant fields in Obsidian but MISSING in comparison:")
            for k in sorted(enchant_extra):
                obs_val = get_field(obs_f, k)
                print(f"      {k} = {obs_val} (in obsidian)")

        # Compare shared enchant fields
        shared = obs_keys & cmp_keys
        enchant_shared = [k for k in shared if ENCHANT_KEYWORDS.search(k)]
        if enchant_shared:
            print(f"    Shared enchant fields:")
            for k in sorted(enchant_shared):
                obs_val = get_field(obs_f, k)
                cmp_val = get_field(cmp_f, k)
                match = "MATCH" if obs_val == cmp_val else "DIFFER"
                print(f"      {k}: obs={obs_val}  cmp={cmp_val}  [{match}]")

    print(f"\n\n  === FINAL VERDICT ===")
    if breastplate:
        obs_fields = db.get_fields(breastplate)
        slots = get_field(obs_fields, 'numRelicSlots')
        has_slot = slots and slots[0] >= 1

        if has_slot and mech_items:
            mech_fields = db.get_fields(mech_items[0])
            body_armor_val = get_field(mech_fields, 'bodyArmor')
            mech_targets_body = body_armor_val and body_armor_val[0] == 1

            if mech_targets_body:
                print(f"  The breastplate record ({breastplate}) HAS numRelicSlots=1")
                print(f"  and Mechanical Parts DOES target bodyArmor.")
                print(f"  The database records look correct.")
                print(f"")
                print(f"  POSSIBLE CAUSES:")
                print(f"  1. The game may be loading the record from a DIFFERENT path")
                if obsidian_outside_item:
                    print(f"     >>> LIKELY: records\\equipmentweapon\\axe\\us_n_obsidianarmor.dbr")
                    print(f"     >>> is outside records/item/ and has NO numRelicSlots field!")
                    print(f"     >>> If the game resolves the Obsidian item via that path,")
                    print(f"     >>> it would appear non-enchantable.")
                print(f"  2. The item may need a completedRelicBitmap or relicShard1 field")
                print(f"  3. Relic slot only works when the item actually has the slot in its template")
                print(f"  4. The ItemCharm's completedRelicLevel may not match the item's expected level")
            else:
                print(f"  Mechanical Parts does NOT target bodyArmor - that's the issue!")
        elif not has_slot:
            print(f"  The breastplate DOES NOT have numRelicSlots >= 1.")
            print(f"  Patch 3 failed to add a relic slot to this item.")
        else:
            print(f"  Could not find Mechanical Parts item records for analysis.")
    else:
        print(f"  Could not find the Obsidian Breastplate record.")

    print("\n  Done.")


if __name__ == '__main__':
    main()
