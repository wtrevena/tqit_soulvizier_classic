"""
Investigate specific monster groups for soul gap analysis.

Queries the .arz database for detailed information about:
  1. Hydra variants (boss-classified)
  2. Ormenos variants (boss-classified)
  3. Yaoguai variants (boss-classified)
  4. Charon variants (boss-classified)
  5. Toxeus variants (all records)
  6. Secret Passage bosses (drxcreatures)
  7. Leinth (full dump)
  8. Murder Bunny (full dump)

Usage:
    py tools/investigate_soul_gaps.py <database.arz>
"""
import sys
import os
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from arz_patcher import ArzDatabase


# ---------------------------------------------------------------------------
# Field helpers (adapted from find_soulless_bosses.py)
# ---------------------------------------------------------------------------

def fv(fields, name):
    """Get first field value or None."""
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


def fvl(fields, name):
    """Get field value as list."""
    if fields is None:
        return []
    if name in fields:
        return fields[name].values
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            return tf.values
    return []


def fmt_levels(levels):
    """Format charLevel list for display."""
    if not levels:
        return '?'
    return ', '.join(str(int(l)) for l in levels)


def fmt_val(v):
    """Format a field value for display."""
    if v is None:
        return '(none)'
    if isinstance(v, list):
        if len(v) == 0:
            return '(empty)'
        if len(v) == 1:
            return str(v[0])
        return str(v)
    return str(v)


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

lines = []

def out(s=''):
    lines.append(s)


def print_monster_basics(record, fields):
    """Print standard monster info fields."""
    levels = fvl(fields, 'charLevel')
    soul_item = fv(fields, 'lootFinger2Item1')
    drop_rate = fv(fields, 'chanceToEquipFinger2')
    mc = fv(fields, 'monsterClassification')

    out(f'  Record: {record}')
    out(f'    monsterClassification: {fmt_val(mc)}')
    out(f'    charLevel:             {fmt_levels(levels)}')
    out(f'    lootFinger2Item1:      {fmt_val(soul_item)}')
    out(f'    chanceToEquipFinger2:  {fmt_val(drop_rate)}')

    has_soul = soul_item is not None and soul_item != '' and 'soul' in str(soul_item).lower()
    return has_soul


def print_full_dump(record, fields):
    """Print ALL fields for a record."""
    out(f'  Record: {record}')
    if not fields:
        out(f'    (no fields)')
        return

    # Sort fields alphabetically
    sorted_keys = sorted(fields.keys(), key=lambda k: k.split('###')[0].lower())
    for key in sorted_keys:
        tf = fields[key]
        field_name = key.split('###')[0]
        vals = tf.values
        if len(vals) == 1:
            out(f'    {field_name} = {vals[0]}')
        elif len(vals) == 0:
            out(f'    {field_name} = (empty)')
        else:
            out(f'    {field_name} = {vals}')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <database.arz>', file=sys.stderr)
        sys.exit(1)

    db_path = Path(sys.argv[1])
    print(f'Loading database: {db_path}', file=sys.stderr)
    db = ArzDatabase.from_arz(db_path)
    print(f'Database loaded. Scanning records...', file=sys.stderr)

    # Pre-scan: collect all records with their fields for targeted searches
    all_records = list(db.record_names())
    print(f'Total records: {len(all_records)}', file=sys.stderr)

    out('=' * 120)
    out('SOULVIZIER CLASSIC - SOUL GAP INVESTIGATION')
    out('=' * 120)
    out(f'Database: {db_path}')
    out(f'Total records: {len(all_records)}')
    out()

    # ===================================================================
    # SECTION 1: HYDRA VARIANTS
    # ===================================================================
    out('=' * 120)
    out('SECTION 1: HYDRA VARIANTS (Boss-classified)')
    out('=' * 120)
    out()

    hydra_with_souls = []
    hydra_without_souls = []

    for name in all_records:
        if 'hydra' not in name.lower():
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        mc = fv(fields, 'monsterClassification')
        if mc != 'Boss':
            continue

        has_soul = print_monster_basics(name, fields)
        if has_soul:
            hydra_with_souls.append(name)
        else:
            hydra_without_souls.append(name)
        out()

    out(f'  --- Summary ---')
    out(f'  Hydra bosses with souls:    {len(hydra_with_souls)}')
    out(f'  Hydra bosses without souls: {len(hydra_without_souls)}')
    if hydra_without_souls:
        out(f'  Missing souls:')
        for r in hydra_without_souls:
            out(f'    {r}')
    out()

    # ===================================================================
    # SECTION 2: ORMENOS VARIANTS
    # ===================================================================
    out('=' * 120)
    out('SECTION 2: ORMENOS VARIANTS (Boss-classified)')
    out('=' * 120)
    out()

    ormenos_with_souls = []
    ormenos_without_souls = []

    for name in all_records:
        if 'ormenos' not in name.lower():
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        mc = fv(fields, 'monsterClassification')
        if mc != 'Boss':
            continue

        has_soul = print_monster_basics(name, fields)
        if has_soul:
            ormenos_with_souls.append(name)
        else:
            ormenos_without_souls.append(name)
        out()

    out(f'  --- Summary ---')
    out(f'  Ormenos bosses with souls:    {len(ormenos_with_souls)}')
    out(f'  Ormenos bosses without souls: {len(ormenos_without_souls)}')
    if ormenos_without_souls:
        out(f'  Missing souls:')
        for r in ormenos_without_souls:
            out(f'    {r}')
    out()

    # ===================================================================
    # SECTION 3: YAOGUAI VARIANTS
    # ===================================================================
    out('=' * 120)
    out('SECTION 3: YAOGUAI VARIANTS (Boss-classified)')
    out('=' * 120)
    out()

    yaoguai_with_souls = []
    yaoguai_without_souls = []

    for name in all_records:
        if 'yaoguai' not in name.lower():
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        mc = fv(fields, 'monsterClassification')
        if mc != 'Boss':
            continue

        has_soul = print_monster_basics(name, fields)
        if has_soul:
            yaoguai_with_souls.append(name)
        else:
            yaoguai_without_souls.append(name)
        out()

    out(f'  --- Summary ---')
    out(f'  Yaoguai bosses with souls:    {len(yaoguai_with_souls)}')
    out(f'  Yaoguai bosses without souls: {len(yaoguai_without_souls)}')
    if yaoguai_without_souls:
        out(f'  Missing souls:')
        for r in yaoguai_without_souls:
            out(f'    {r}')
    out()

    # ===================================================================
    # SECTION 4: CHARON VARIANTS
    # ===================================================================
    out('=' * 120)
    out('SECTION 4: CHARON VARIANTS (Boss-classified)')
    out('=' * 120)
    out()

    charon_with_souls = []
    charon_without_souls = []

    for name in all_records:
        if 'charon' not in name.lower():
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        mc = fv(fields, 'monsterClassification')
        if mc != 'Boss':
            continue

        has_soul = print_monster_basics(name, fields)
        if has_soul:
            charon_with_souls.append(name)
        else:
            charon_without_souls.append(name)
        out()

    out(f'  --- Summary ---')
    out(f'  Charon bosses with souls:    {len(charon_with_souls)}')
    out(f'  Charon bosses without souls: {len(charon_without_souls)}')
    if charon_without_souls:
        out(f'  Missing souls:')
        for r in charon_without_souls:
            out(f'    {r}')
    out()

    # ===================================================================
    # SECTION 5: TOXEUS VARIANTS (ALL records, not just Boss)
    # ===================================================================
    out('=' * 120)
    out('SECTION 5: TOXEUS VARIANTS (ALL records)')
    out('=' * 120)
    out()

    for name in sorted(all_records):
        if 'toxeus' not in name.lower():
            continue
        fields = db.get_fields(name)
        if not fields:
            continue

        mc = fv(fields, 'monsterClassification')
        levels = fvl(fields, 'charLevel')
        soul_item = fv(fields, 'lootFinger2Item1')
        drop_rate = fv(fields, 'chanceToEquipFinger2')

        # Combat stats
        char_life = fv(fields, 'characterLife')
        off_phys_min = fv(fields, 'offensivePhysMin')
        off_phys_max = fv(fields, 'offensivePhysMax')
        char_str = fv(fields, 'characterStrength')
        char_dex = fv(fields, 'characterDexterity')
        char_int = fv(fields, 'characterIntelligence')

        # Skills
        skills = []
        for i in range(1, 6):
            sk = fv(fields, f'skillName{i}')
            if sk:
                skills.append((f'skillName{i}', sk))

        out(f'  Record: {name}')
        out(f'    monsterClassification: {fmt_val(mc)}')
        out(f'    charLevel:             {fmt_levels(levels)}')
        out(f'    --- Combat Stats ---')
        out(f'    characterLife:         {fmt_val(char_life)}')
        out(f'    offensivePhysMin:      {fmt_val(off_phys_min)}')
        out(f'    offensivePhysMax:      {fmt_val(off_phys_max)}')
        out(f'    characterStrength:     {fmt_val(char_str)}')
        out(f'    characterDexterity:    {fmt_val(char_dex)}')
        out(f'    characterIntelligence: {fmt_val(char_int)}')
        out(f'    --- Skills ---')
        if skills:
            for sk_name, sk_val in skills:
                out(f'    {sk_name}: {fmt_val(sk_val)}')
        else:
            out(f'    (no skillName1-5 found)')
        out(f'    --- Soul ---')
        out(f'    lootFinger2Item1:      {fmt_val(soul_item)}')
        out(f'    chanceToEquipFinger2:  {fmt_val(drop_rate)}')
        out()

    # ===================================================================
    # SECTION 6: SECRET PASSAGE BOSSES (drxcreatures)
    # ===================================================================
    out('=' * 120)
    out('SECTION 6: SECRET PASSAGE BOSSES (drxcreatures)')
    out('=' * 120)
    out()

    drx_by_class = defaultdict(list)

    for name in sorted(all_records):
        if 'drxcreatures' not in name.lower():
            continue
        fields = db.get_fields(name)
        if not fields:
            continue

        mc = fv(fields, 'monsterClassification') or '(none)'
        levels = fvl(fields, 'charLevel')
        desc = fv(fields, 'description') or ''
        soul_item = fv(fields, 'lootFinger2Item1')
        drop_rate = fv(fields, 'chanceToEquipFinger2')

        drx_by_class[mc].append({
            'record': name,
            'mc': mc,
            'levels': levels,
            'desc': desc,
            'soul_item': soul_item,
            'drop_rate': drop_rate,
        })

    total_drx = sum(len(v) for v in drx_by_class.values())
    out(f'  Total drxcreatures records: {total_drx}')
    out()

    for mc_val in sorted(drx_by_class.keys()):
        group = drx_by_class[mc_val]
        out(f'  --- Classification: {mc_val} ({len(group)} records) ---')
        out()

        for entry in group:
            out(f'  Record: {entry["record"]}')
            out(f'    monsterClassification: {entry["mc"]}')
            out(f'    charLevel:             {fmt_levels(entry["levels"])}')
            out(f'    description:           {fmt_val(entry["desc"])}')
            out(f'    lootFinger2Item1:      {fmt_val(entry["soul_item"])}')
            out(f'    chanceToEquipFinger2:  {fmt_val(entry["drop_rate"])}')
            out()

    # ===================================================================
    # SECTION 7: LEINTH (full dump)
    # ===================================================================
    out('=' * 120)
    out('SECTION 7: LEINTH (full field dump)')
    out('=' * 120)
    out()

    leinth_count = 0
    for name in sorted(all_records):
        if 'leinth' not in name.lower():
            continue
        fields = db.get_fields(name)
        if not fields:
            out(f'  Record: {name}')
            out(f'    (no fields)')
            out()
            continue

        print_full_dump(name, fields)
        out()
        leinth_count += 1

    if leinth_count == 0:
        out(f'  No records found containing "leinth" in path.')
    out()

    # ===================================================================
    # SECTION 8: MURDER BUNNY (full dump)
    # ===================================================================
    out('=' * 120)
    out('SECTION 8: MURDER BUNNY (full field dump)')
    out('=' * 120)
    out()

    bunny_count = 0
    for name in sorted(all_records):
        if 'murderbunny' not in name.lower():
            continue
        fields = db.get_fields(name)
        if not fields:
            out(f'  Record: {name}')
            out(f'    (no fields)')
            out()
            continue

        print_full_dump(name, fields)
        out()
        bunny_count += 1

    if bunny_count == 0:
        out(f'  No records found containing "murderbunny" in path.')
    out()

    # ===================================================================
    # Output
    # ===================================================================
    output_text = '\n'.join(lines)
    print(output_text)


if __name__ == '__main__':
    main()
