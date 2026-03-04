"""
Diagnose why the Obsidian Breastplate cannot be enchanted with Mechanical Parts.

Deep investigation:
1. Find ALL records with "obsidian" in the name (case-insensitive)
2. Check for unique/set versions with different record paths
3. Check armor/torso paths specifically
4. Dump key fields for each match
5. Analyze whether make_enchantable() would have patched each record
"""

import sys
import os

# Ensure UTF-8 output on Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(__file__))

from pathlib import Path
from arz_patcher import ArzDatabase

ARZ_PATH = Path(__file__).resolve().parent.parent / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'


def get_field(fields, name):
    """Get a field value by base name (ignoring ### suffix)."""
    if fields is None:
        return None
    if name in fields:
        v = fields[name].values
        return v[0] if len(v) == 1 else v
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            v = tf.values
            return v[0] if len(v) == 1 else v
    return None


def classify_make_enchantable(name, fields):
    """Simulate make_enchantable logic and return why a record would or would not be patched."""
    item_path_prefixes = (
        'records\\item\\', 'records/item/',
        'records\\drxitem\\', 'records/drxitem/',
    )
    equip_templates = (
        'armor', 'weapon', 'shield',
        'jewelry_ring', 'jewelry_amulet', 'jewelry_medal',
        'itemrelic',
    )
    equip_classes = (
        'armorprotective', 'armorjewelry', 'weaponmelee',
        'weaponhunting', 'weaponmage', 'weaponstaff',
        'shield',
    )

    nl = name.lower()
    is_item_path = any(nl.startswith(p) for p in item_path_prefixes)
    is_soul_path = '\\soul\\' in nl or '/soul/' in nl
    if not is_item_path and not is_soul_path:
        return "SKIP: path doesn't start with records/item/ or records/drxitem/ and not a soul path"

    if fields is None:
        return "SKIP: no fields"

    tmpl = get_field(fields, 'templateName') or ''
    cls = get_field(fields, 'Class') or ''
    cannot_pick = get_field(fields, 'cannotPickUp') or 0
    current_slots = get_field(fields, 'numRelicSlots')
    if current_slots is None:
        current_slots = -1

    if not tmpl:
        return "SKIP: no templateName"
    if cannot_pick == 1:
        return "SKIP: cannotPickUp=1"

    tmpl_lower = str(tmpl).lower()
    cls_lower = str(cls).lower()
    tmpl_base = tmpl_lower.replace('\\', '/').split('/')[-1].replace('.tpl', '')
    is_equip = any(tmpl_base.startswith(t) for t in equip_templates) or \
               any(cls_lower.startswith(c) for c in equip_classes) or \
               is_soul_path

    if not is_equip:
        return f"SKIP: not equipment (tmpl_base='{tmpl_base}', cls='{cls_lower}')"

    if isinstance(current_slots, (int, float)) and current_slots >= 1:
        return f"SKIP: already has numRelicSlots={current_slots} (no patch needed)"

    return f"WOULD PATCH: numRelicSlots was {current_slots}"


def main():
    print(f"Loading: {ARZ_PATH}")
    print(f"File size: {ARZ_PATH.stat().st_size / 1024 / 1024:.1f} MB")
    db = ArzDatabase.from_arz(ARZ_PATH)

    all_names = db.record_names()
    print(f"\nTotal records in database: {len(all_names)}")

    # =========================================================================
    # PART 1: Find ALL records with "obsidian" in the name
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 1: ALL records containing 'obsidian' (case-insensitive)")
    print("=" * 80)

    obsidian_records = [n for n in all_names if 'obsidian' in n.lower()]
    print(f"Found {len(obsidian_records)} records with 'obsidian' in name\n")

    for rec in sorted(obsidian_records):
        fields = db.get_fields(rec)
        tmpl = get_field(fields, 'templateName') or '(none)'
        cls = get_field(fields, 'Class') or '(none)'
        print(f"  Path: {rec}")
        print(f"    templateName: {tmpl}")
        print(f"    Class: {cls}")
        print()

    # =========================================================================
    # PART 2: Check for unique/set versions of obsidian armor
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 2: Unique/Set versions - records matching obsidian in armor paths")
    print("=" * 80)

    armor_keywords = ['equipmentarmor', 'armor', 'torso', 'breastplate']
    obsidian_armor = []
    for rec in all_names:
        rl = rec.lower()
        if 'obsidian' not in rl:
            continue
        if any(kw in rl for kw in armor_keywords):
            obsidian_armor.append(rec)

    # Also check broader: any obsidian equipment record
    obsidian_equip = []
    equip_keywords = ['equipment', 'armor', 'weapon', 'shield', 'helm',
                      'greave', 'armband', 'ring', 'amulet', 'medal']
    for rec in all_names:
        rl = rec.lower()
        if 'obsidian' not in rl:
            continue
        if any(kw in rl for kw in equip_keywords):
            obsidian_equip.append(rec)

    print(f"\nObsidian records in armor-related paths: {len(obsidian_armor)}")
    for rec in sorted(obsidian_armor):
        fields = db.get_fields(rec)
        print(f"\n  Path: {rec}")
        for fname in ['Class', 'numRelicSlots', 'itemClassification',
                      'itemNameTag', 'itemLevel', 'templateName',
                      'itemSetName', 'cannotPickUp', 'itemText',
                      'description', 'levelRequirement', 'itemCost']:
            val = get_field(fields, fname)
            if val is not None:
                print(f"    {fname}: {val}")

        # Run make_enchantable simulation
        reason = classify_make_enchantable(rec, fields)
        print(f"    [make_enchantable verdict]: {reason}")

    print(f"\n\nAll obsidian EQUIPMENT records: {len(obsidian_equip)}")
    for rec in sorted(obsidian_equip):
        if rec in obsidian_armor:
            continue  # already printed above
        fields = db.get_fields(rec)
        print(f"\n  Path: {rec}")
        for fname in ['Class', 'numRelicSlots', 'itemClassification',
                      'itemNameTag', 'itemLevel', 'templateName',
                      'cannotPickUp']:
            val = get_field(fields, fname)
            if val is not None:
                print(f"    {fname}: {val}")
        reason = classify_make_enchantable(rec, fields)
        print(f"    [make_enchantable verdict]: {reason}")

    # =========================================================================
    # PART 3: Search by alternate name patterns
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 3: Records matching obsidianbreastplate / obsidian_breastplate")
    print("=" * 80)

    patterns = ['obsidianbreastplate', 'obsidian_breastplate', 'obsidian_armor',
                'obsidian_chest', 'obsidianchest']
    for pat in patterns:
        matches = [n for n in all_names if pat in n.lower()]
        if matches:
            print(f"\n  Pattern '{pat}': {len(matches)} matches")
            for m in matches:
                print(f"    {m}")
        else:
            print(f"\n  Pattern '{pat}': no matches")

    # =========================================================================
    # PART 4: Check the Mechanical Parts relic record
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 4: Mechanical Parts relic / charm records")
    print("=" * 80)

    mech_records = [n for n in all_names if 'mechanical' in n.lower()]
    print(f"Found {len(mech_records)} records with 'mechanical' in name")
    for rec in sorted(mech_records):
        fields = db.get_fields(rec)
        cls = get_field(fields, 'Class') or '(none)'
        tmpl = get_field(fields, 'templateName') or '(none)'
        print(f"\n  Path: {rec}")
        print(f"    Class: {cls}")
        print(f"    templateName: {tmpl}")
        # Check what item types it can be applied to
        for fname in ['itemClassification', 'numRelicSlots',
                      'relicSlotType', 'relicBonusTableName',
                      'itemSkillName', 'itemLevel',
                      'charLevel', 'levelRequirement',
                      'allowableEquipment']:
            val = get_field(fields, fname)
            if val is not None:
                print(f"    {fname}: {val}")

    # Also check for general relic / charm naming
    relic_records = [n for n in all_names if 'mechanical' in n.lower() or
                     ('relic' in n.lower() and 'parts' in n.lower())]
    extra = [r for r in relic_records if r not in mech_records]
    if extra:
        print(f"\nAdditional relic/parts records: {len(extra)}")
        for rec in sorted(extra):
            print(f"  {rec}")

    # =========================================================================
    # PART 5: Check if item classification affects enchantability
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 5: Check the specific record mentioned by user")
    print("=" * 80)

    target = 'records\\item\\equipmentarmor\\us_n_obsidianarmor.dbr'
    alt_targets = [
        'records/item/equipmentarmor/us_n_obsidianarmor.dbr',
        'records\\item\\equipmentarmor\\us_n_obsidianarmor.dbr',
    ]

    found = False
    for t in [target] + alt_targets:
        if db.has_record(t):
            print(f"\n  Record FOUND: {t}")
            fields = db.get_fields(t)
            if fields:
                print(f"  Total fields: {len(fields)}")
                print(f"\n  ALL FIELDS:")
                for key, tf in fields.items():
                    real_name = key.split('###')[0]
                    print(f"    {real_name} = {tf.values}  (type={tf.dtype})")
            reason = classify_make_enchantable(t, fields)
            print(f"\n  [make_enchantable verdict]: {reason}")
            found = True
            break

    if not found:
        print(f"\n  WARNING: Record not found with exact paths tried:")
        for t in [target] + alt_targets:
            print(f"    {t}")
        # Try fuzzy match
        close = [n for n in all_names if 'obsidianarmor' in n.lower() and 'equipmentarmor' in n.lower()]
        if close:
            print(f"\n  Close matches found:")
            for c in close:
                print(f"    {c}")
                fields = db.get_fields(c)
                if fields:
                    for fname in ['Class', 'numRelicSlots', 'templateName',
                                  'itemClassification', 'cannotPickUp']:
                        val = get_field(fields, fname)
                        print(f"      {fname}: {val}")
                reason = classify_make_enchantable(c, fields)
                print(f"      [make_enchantable verdict]: {reason}")

    # =========================================================================
    # PART 6: Analysis of make_enchantable path filtering
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 6: make_enchantable() path filter analysis")
    print("=" * 80)

    print("""
    The make_enchantable() function in build_svc_database.py filters records by:

    1. PATH PREFIX: Must start with one of:
       - records\\item\\   or  records/item/
       - records\\drxitem\\ or  records/drxitem/
       OR contain \\soul\\ or /soul/

    2. TEMPLATE: templateName base must start with one of:
       armor, weapon, shield, jewelry_ring, jewelry_amulet,
       jewelry_medal, itemrelic

    3. CLASS: OR Class must start with one of:
       armorprotective, armorjewelry, weaponmelee,
       weaponhunting, weaponmage, weaponstaff, shield

    4. EXCLUSIONS:
       - cannotPickUp = 1 -> skipped
       - numRelicSlots >= 1 -> skipped (already enchantable)
       - no templateName -> skipped

    Records under 'records\\equipmentarmor\\' (without 'item\\' prefix)
    would be MISSED by this filter!
    """)

    # Check if any obsidian records fall outside the item prefix
    print("  Checking obsidian records against path filter:")
    item_prefixes = ('records\\item\\', 'records/item/',
                     'records\\drxitem\\', 'records/drxitem/')
    for rec in sorted(obsidian_records):
        rl = rec.lower()
        is_item = any(rl.startswith(p) for p in item_prefixes)
        is_soul = '\\soul\\' in rl or '/soul/' in rl
        if not is_item and not is_soul:
            fields = db.get_fields(rec)
            cls = get_field(fields, 'Class') or ''
            tmpl = get_field(fields, 'templateName') or ''
            if cls or tmpl:
                print(f"    OUTSIDE item prefix: {rec}")
                print(f"      Class={cls}, templateName={tmpl}")

    # =========================================================================
    # PART 7: Check for "breastplate" in tag strings
    # =========================================================================
    print("\n" + "=" * 80)
    print("PART 7: Search string table for 'obsidian' + 'breastplate' tags")
    print("=" * 80)

    obsidian_strings = [s for s in db.strings if 'obsidian' in s.lower()]
    breastplate_strings = [s for s in db.strings if 'breastplate' in s.lower()]

    print(f"  Strings containing 'obsidian': {len(obsidian_strings)}")
    for s in sorted(obsidian_strings)[:30]:
        print(f"    {s}")

    print(f"\n  Strings containing 'breastplate': {len(breastplate_strings)}")
    for s in sorted(breastplate_strings)[:30]:
        print(f"    {s}")

    # Check what record references the itemNameTag with obsidian breastplate
    print("\n  Checking which records reference obsidian name tags...")
    obsidian_equip_all = [n for n in all_names if 'obsidian' in n.lower() and
                          ('equipment' in n.lower() or 'armor' in n.lower())]
    for rec in sorted(obsidian_equip_all):
        fields = db.get_fields(rec)
        tag = get_field(fields, 'itemNameTag')
        style = get_field(fields, 'itemStyleTag')
        qual = get_field(fields, 'itemQualityTag')
        if tag or style or qual:
            print(f"    {rec}")
            if tag: print(f"      itemNameTag: {tag}")
            if style: print(f"      itemStyleTag: {style}")
            if qual: print(f"      itemQualityTag: {qual}")


if __name__ == '__main__':
    main()
