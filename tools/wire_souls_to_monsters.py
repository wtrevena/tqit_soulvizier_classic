"""
Wire soul items to their corresponding monster records.

In SV, soul items exist under records/item/equipmentring/soul/{type}/{name}_soul_{n|e|l}.dbr
but most are not connected to any monster's loot table. This tool:

1. Parses all soul items to extract monster type and name
2. Finds matching monster records
3. Assigns soul drops via lootFinger2Item1 with appropriate chances

Usage:
  python wire_souls_to_monsters.py <database.arz> <output.arz>
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


def parse_soul_name(soul_path: str) -> tuple[str, str, str]:
    """Extract (monster_type, monster_name, difficulty) from soul path.

    Example: records\\item\\equipmentring\\soul\\gorgon\\gorgonslayer_soul_n.dbr
    Returns: ('gorgon', 'gorgonslayer', 'n')
    """
    parts = soul_path.lower().replace('\\', '/').split('/')
    filename = parts[-1].replace('.dbr', '')
    monster_type = parts[-2] if len(parts) >= 2 else ''

    diff = ''
    name = filename
    if filename.endswith('_soul_n') or filename.endswith('_soul_e') or filename.endswith('_soul_l'):
        diff = filename[-1]
        name = filename[:-7]
    elif filename.endswith('_soul'):
        name = filename[:-5]
        diff = 'n'
    elif '_soul_' in filename:
        idx = filename.index('_soul_')
        name = filename[:idx]
        diff = filename[idx + 6:]
    elif 'soul' in filename:
        name = filename.replace('soul', '').strip('_')
        diff = 'n'

    return monster_type, name, diff


def build_soul_catalog(db: ArzDatabase):
    """Build catalog: monster_type -> {monster_name -> {difficulty -> soul_record_path}}"""
    catalog = defaultdict(lambda: defaultdict(dict))
    soul_dir = 'item\\equipmentring\\soul\\'
    soul_dir2 = 'item/equipmentring/soul/'

    count = 0
    for name in db.records:
        nl = name.lower()
        if soul_dir not in nl and soul_dir2 not in nl:
            continue

        parts = nl.replace('\\', '/').split('/')
        filename = parts[-1].replace('.dbr', '')

        if filename.startswith(('01_', '02_', '03_', '04_')):
            continue

        monster_type, monster_name, diff = parse_soul_name(name)
        if monster_name and diff:
            catalog[monster_type][monster_name][diff] = name
            count += 1

    print(f"  Soul catalog: {count} entries across {len(catalog)} monster types")
    return catalog


def find_monster_matches(db: ArzDatabase, soul_catalog):
    """Match soul items to monster records by name similarity."""
    print("\n=== Matching souls to monsters ===")

    monster_records = []
    for name, fields in db.records.items():
        nl = name.lower()
        cls = str(fields.get('Class', '')).lower()
        template = str(fields.get('templateName', '')).lower()

        if 'monster' not in cls and 'monster' not in template:
            continue
        if '\\creature\\' not in nl and '/creature/' not in nl:
            if '\\xpack\\creatures\\' not in nl and '/xpack/creatures/' not in nl:
                continue

        monster_records.append(name)

    print(f"  Total monster records: {len(monster_records)}")

    matches = {}  # monster_record -> (soul_type, soul_name, {diff: soul_path})
    unmatched_monsters = []
    matched_souls = set()

    for mon_name in monster_records:
        mn_lower = mon_name.lower().replace('\\', '/')
        parts = mn_lower.split('/')
        filename = parts[-1].replace('.dbr', '')
        monster_dir = parts[-2] if len(parts) >= 2 else ''

        clean = re.sub(r'^(u_|um_|uw_|qm_|bm_|cb_|am_|ar_|as_|em_|vampiric_)', '', filename)
        clean = re.sub(r'_\d+$', '', clean)
        clean = re.sub(r'\d+$', '', clean)
        clean = clean.strip('_')

        best_match = None
        best_score = 0

        for soul_type, names in soul_catalog.items():
            type_match = (soul_type == monster_dir)

            for soul_name, diffs in names.items():
                score = 0

                if soul_name == clean:
                    score = 100
                elif clean.startswith(soul_name) or soul_name.startswith(clean):
                    overlap = min(len(soul_name), len(clean))
                    score = overlap * 2
                elif clean in soul_name or soul_name in clean:
                    score = len(min(clean, soul_name, key=len))

                if type_match and score > 0:
                    score += 30

                if score > best_score:
                    best_score = score
                    best_match = (soul_type, soul_name, diffs)

        if best_match and best_score >= 6:
            soul_type, soul_name, diffs = best_match
            matches[mon_name] = best_match
            for d, sp in diffs.items():
                matched_souls.add(sp)

    print(f"  Monsters matched to souls: {len(matches)}")
    print(f"  Unique soul items matched: {len(matched_souls)}")

    return matches


def wire_soul_drops(db: ArzDatabase, matches: dict,
                    boss_chance=0.25, rare_chance=0.66):
    """Add soul drop fields to monster records."""
    print("\n=== Wiring soul drops ===")

    boss_keywords = [
        'boss', 'quest', 'hero', 'champion', 'unique', 'uber',
        'named', 'typhon', 'hades', 'hydra',
    ]

    wired = 0
    already_had = 0

    for mon_name, (soul_type, soul_name, diffs) in matches.items():
        fields = db.records[mon_name]

        if 'lootFinger2Item1' in fields:
            val = fields['lootFinger2Item1']
            if val and val != '' and val != 0:
                already_had += 1
                continue

        soul_n = diffs.get('n', '')
        soul_e = diffs.get('e', '')
        soul_l = diffs.get('l', '')

        if not soul_n and not soul_e and not soul_l:
            continue

        if soul_n and soul_e and soul_l:
            fields['lootFinger2Item1'] = [soul_n, soul_e, soul_l]
        elif soul_n:
            fields['lootFinger2Item1'] = soul_n
        else:
            best = soul_n or soul_e or soul_l
            fields['lootFinger2Item1'] = best

        mn_lower = mon_name.lower()
        is_boss = any(kw in mn_lower for kw in boss_keywords)
        chance = boss_chance if is_boss else rare_chance

        fields['lootFinger2Chance'] = chance

        wired += 1

    print(f"  Newly wired: {wired}")
    print(f"  Already had souls: {already_had}")
    return wired


def main():
    if len(sys.argv) < 3:
        print("Usage: wire_souls_to_monsters.py <database.arz> <output.arz>")
        sys.exit(1)

    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    catalog = build_soul_catalog(db)
    matches = find_monster_matches(db, catalog)
    wired = wire_soul_drops(db, matches)

    if '--report' in sys.argv:
        print("\n=== Wiring report ===")
        for mon, (st, sn, diffs) in sorted(matches.items()):
            soul_paths = ', '.join(f"{d}:{p.split('/')[-1]}" for d, p in sorted(diffs.items()))
            print(f"  {mon}")
            print(f"    -> {st}/{sn}: {soul_paths}")

    print(f"\nWriting output...")
    db.write_arz(Path(sys.argv[2]))
    print("Done.")


if __name__ == '__main__':
    main()
