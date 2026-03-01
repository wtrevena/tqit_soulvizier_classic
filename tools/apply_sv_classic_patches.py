"""
Apply SoulvizierClassic patches to the upstream SV 0.98i database.

Patches:
1. Restore potion drop rates from SV 0.9 loot tables (0.98i zeroed them all)
2. Set soul drop rates: 66% for rare monsters, 25% for farmable bosses
3. Remove non-level requirements from all souls (no str/int/dex)
4. Make everything enchantable (souls, epic/legendary/forged weapons)

Usage:
  python apply_sv_classic_patches.py <sv098i.arz> <sv09.arz> <output.arz>
"""
import sys
import re
import copy
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def patch_potion_drops(db098: ArzDatabase, db09: ArzDatabase):
    """Restore potion drop weights from SV 0.9 into the 0.98i database.

    SV 0.98i zeroed all potion weights in records/item/loottables/raremisc/*.
    We restore the SV 0.9 values for:
    - potionattri (attribute potions) in commonmisc_boss_drop and commonmisc_drop
    - potionskill (skill potions) in commonmisc_boss_drop and commonmisc_drop
    - potionexp (xp potions) in rarepotions_new_drop
    """
    print("\n=== Restoring potion drop rates from SV 0.9 ===")

    potion_loot_tables = []
    for name in db098.records:
        if 'loottables\\raremisc\\' not in name.lower() and 'loottables/raremisc/' not in name.lower():
            continue
        fields = db098.records[name]
        has_potion = False
        for key, val in fields.items():
            if isinstance(val, str) and 'potion' in val.lower():
                has_potion = True
                break
        if has_potion:
            potion_loot_tables.append(name)

    restored = 0
    for name in potion_loot_tables:
        if name not in db09.records:
            continue

        fields098 = db098.records[name]
        fields09 = db09.records[name]

        for key in list(fields098.keys()):
            if not key.startswith('lootWeight'):
                continue
            idx = key[10:]
            loot_key = f'lootName{idx}'
            loot_val = str(fields098.get(loot_key, '')).lower()

            if 'potion' not in loot_val:
                continue

            old_weight = fields098[key]
            new_weight = fields09.get(key, old_weight)

            if isinstance(old_weight, (int, float)) and old_weight == 0 and \
               isinstance(new_weight, (int, float)) and new_weight > 0:
                fields098[key] = new_weight
                restored += 1

    print(f"  Potion loot tables found: {len(potion_loot_tables)}")
    print(f"  Weights restored from SV 0.9: {restored}")


def patch_potion_merchants(db098: ArzDatabase, db09: ArzDatabase):
    """Ensure merchants sell potions by restoring merchant table weights from SV 0.9."""
    print("\n=== Restoring potion merchant availability ===")

    merchant_tables = []
    for name in db098.records:
        name_lower = name.lower()
        if 'merchant' not in name_lower:
            continue
        if 'potion' not in name_lower and 'misc' not in name_lower:
            continue
        fields = db098.records[name]
        has_potion = False
        for key, val in fields.items():
            if isinstance(val, str) and 'potion' in val.lower():
                has_potion = True
                break
        if has_potion:
            merchant_tables.append(name)

    restored = 0
    for name in merchant_tables:
        if name not in db09.records:
            continue

        fields098 = db098.records[name]
        fields09 = db09.records[name]

        for key in list(fields098.keys()):
            if not key.startswith('lootWeight'):
                continue
            old = fields098[key]
            new = fields09.get(key, old)
            if isinstance(old, (int, float)) and old == 0 and \
               isinstance(new, (int, float)) and new > 0:
                fields098[key] = new
                restored += 1

    print(f"  Merchant tables with potions: {len(merchant_tables)}")
    print(f"  Merchant weights restored: {restored}")


def patch_soul_drop_rates(db: ArzDatabase, boss_rate=25.0, rare_rate=66.0):
    """Adjust soul drop weights in monster loot tables.

    Strategy: Find loot tables attached to monsters that reference soul items.
    Set weights to target rates based on whether the monster is a boss.
    """
    print("\n=== Patching soul drop rates ===")

    boss_keywords = [
        'boss', 'quest', 'hero', 'champion', 'unique', 'uber',
        'typhon', 'hades', 'hydra', 'chimera', 'minotaurlord',
        'talos', 'manticore', 'scarabaeus', 'megalesios',
        'aktaios', 'alastor', 'nessus', 'ormenos',
        'dragonliche', 'gorgonqueen', 'pharaoh',
    ]

    soul_loot_adjusted = 0
    tables_checked = 0

    for name, fields in db.records.items():
        name_lower = name.lower()

        if 'loottable' not in name_lower and 'lootmastertable' not in name_lower:
            template = str(fields.get('templateName', '')).lower()
            if 'loottable' not in template and 'lootmastertable' not in template:
                continue

        tables_checked += 1

        for key in list(fields.keys()):
            if not key.startswith('lootName'):
                continue
            val = str(fields[key]).lower()
            if 'soul' not in val:
                continue

            if '\\soul\\' not in val and '/soul/' not in val:
                if not val.endswith('soul.dbr') and 'soul_' not in val:
                    continue

            idx = key[8:]
            weight_key = f'lootWeight{idx}'

            is_boss = any(kw in name_lower for kw in boss_keywords)
            target = boss_rate if is_boss else rare_rate

            if weight_key in fields:
                old_w = fields[weight_key]
                if isinstance(old_w, (int, float)):
                    fields[weight_key] = target
                    soul_loot_adjusted += 1

    print(f"  Loot tables checked: {tables_checked}")
    print(f"  Soul weight entries adjusted: {soul_loot_adjusted}")


def patch_soul_requirements(db: ArzDatabase):
    """Remove all non-level requirements from soul items."""
    print("\n=== Removing non-level requirements from souls ===")

    req_fields = ['strengthRequirement', 'intelligenceRequirement', 'dexterityRequirement']
    patched = 0

    for name in db.records:
        name_lower = name.lower()
        if '\\soul\\' not in name_lower and '/soul/' not in name_lower:
            continue

        fields = db.records[name]
        changed = False
        for rf in req_fields:
            if rf in fields:
                val = fields[rf]
                if isinstance(val, (int, float)) and val > 0:
                    fields[rf] = 0
                    changed = True

        if changed:
            patched += 1

    print(f"  Souls with requirements removed: {patched}")


def patch_enchantability(db: ArzDatabase):
    """Make all equipment enchantable by ensuring numRelicSlots >= 1.

    Targets: souls, weapons (all rarities), armor, shields, jewelry.
    Skips: non-equipment records, quest items, things that can't be picked up.
    """
    print("\n=== Making equipment enchantable ===")

    target_templates = {
        'weapon', 'armor', 'shield', 'jewelry', 'ring', 'amulet',
        'helm', 'torso', 'leg', 'arm', 'greave', 'bracer',
    }

    patched = 0
    for name, fields in db.records.items():
        template = str(fields.get('templateName', '')).lower()
        cls = str(fields.get('Class', '')).lower()

        if not template:
            continue
        if fields.get('cannotPickUp') == 1:
            continue
        if fields.get('quest') == 1 or 'quest' in cls:
            continue

        is_equipment = any(t in template for t in target_templates) or \
                       any(t in cls for t in target_templates) or \
                       'itemrelic' in template or \
                       'oneshot_scroll' in cls

        if '\\soul\\' in name.lower() or '/soul/' in name.lower():
            is_equipment = True

        if not is_equipment:
            continue

        current_slots = fields.get('numRelicSlots', 0)
        if isinstance(current_slots, (int, float)) and current_slots < 1:
            fields['numRelicSlots'] = 1
            patched += 1

    print(f"  Items made enchantable: {patched}")


def find_soul_coverage(db: ArzDatabase):
    """Analyze which monsters have souls and which don't."""
    print("\n=== Soul coverage analysis ===")

    soul_items = set()
    for name in db.records:
        name_lower = name.lower()
        if '\\soul\\' in name_lower or '/soul/' in name_lower:
            if name_lower.endswith('.dbr'):
                filename = name_lower.replace('\\', '/').split('/')[-1]
                if not filename.startswith(('01_', '02_', '03_', '04_')):
                    soul_items.add(name)

    print(f"  Unique soul item records: {len(soul_items)}")
    for s in sorted(soul_items)[:20]:
        print(f"    {s}")
    if len(soul_items) > 20:
        print(f"    ... and {len(soul_items) - 20} more")

    return soul_items


def main():
    if len(sys.argv) < 4:
        print("Usage: apply_sv_classic_patches.py <sv098i.arz> <sv09.arz> <output.arz>")
        print("  sv098i.arz: SV 0.98i database (base for patching)")
        print("  sv09.arz:   SV 0.9 database (source for potion drop rates)")
        print("  output.arz: Output patched database")
        sys.exit(1)

    sv098_path = Path(sys.argv[1])
    sv09_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    print(f"Loading SV 0.98i: {sv098_path}")
    db098 = ArzDatabase.from_arz(sv098_path)

    print(f"\nLoading SV 0.9: {sv09_path}")
    db09 = ArzDatabase.from_arz(sv09_path)

    patch_potion_drops(db098, db09)
    patch_potion_merchants(db098, db09)
    patch_soul_drop_rates(db098)
    patch_soul_requirements(db098)
    patch_enchantability(db098)
    find_soul_coverage(db098)

    print(f"\nWriting patched database...")
    db098.write_arz(output_path)
    print("\nDone.")


if __name__ == '__main__':
    main()
