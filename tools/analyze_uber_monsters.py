"""Analyze all um_ (uber) monsters: level, HP, stats, classification.
Output a full report to help decide which should be Boss vs Hero."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


STAT_FIELDS = [
    'monsterClassification', 'charLevel',
    'characterLife', 'characterMana',
    'offensivePhysMin', 'offensivePhysMax',
    'defensiveProtection', 'defensiveAbsorption',
    'characterOffensiveAbility', 'characterDefensiveAbility',
    'characterStrength', 'characterIntelligence', 'characterDexterity',
    'handHitDamageMin', 'handHitDamageMax',
    'characterRunSpeed', 'characterAttackSpeed',
]


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    monsters = []
    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl and '/creature' not in nl:
            continue
        fn = nl.replace('\\', '/').split('/')[-1]
        if not fn.startswith('um_'):
            continue

        fields = db.get_fields(name)
        if not fields:
            continue

        cls_val = ''
        for key, tf in fields.items():
            if key.split('###')[0] == 'Class' and tf.values:
                cls_val = str(tf.values[0])
        if 'Monster' not in cls_val and 'monster' not in cls_val:
            continue

        stats = {'name': name, 'filename': fn.replace('.dbr', '')}
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk in STAT_FIELDS and tf.values:
                val = tf.values[0]
                if val is not None and str(val).strip():
                    stats[rk] = val

        # Count number of skills
        skill_count = 0
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk.startswith('skillName') and tf.values and tf.values[0]:
                skill_count += 1
        stats['skill_count'] = skill_count

        monsters.append(stats)

    # Sort by level then HP
    def sort_key(m):
        lvl = float(m.get('charLevel', 0) or 0)
        hp = float(m.get('characterLife', 0) or 0)
        return (lvl, hp)

    monsters.sort(key=sort_key, reverse=True)

    print(f'Total uber monsters: {len(monsters)}\n')

    # Summary by current classification
    class_counts = {}
    for m in monsters:
        c = m.get('monsterClassification', '(none)')
        class_counts[c] = class_counts.get(c, 0) + 1
    print('Current classifications:')
    for c, cnt in sorted(class_counts.items(), key=lambda x: -x[1]):
        print(f'  {c:15s} {cnt}')

    # Print full table
    print(f'\n{"Filename":<45s} {"Class":>10s} {"Lvl":>4s} {"HP":>10s} {"OA":>6s} {"DA":>6s} {"Str":>6s} {"Int":>6s} {"Dex":>6s} {"Skills":>6s}')
    print('-' * 120)

    for m in monsters:
        fn = m['filename'][:44]
        cls = str(m.get('monsterClassification', ''))[:10]
        lvl = str(m.get('charLevel', ''))[:4]
        hp = str(m.get('characterLife', ''))[:10]
        oa = str(m.get('characterOffensiveAbility', ''))[:6]
        da = str(m.get('characterDefensiveAbility', ''))[:6]
        str_val = str(m.get('characterStrength', ''))[:6]
        int_val = str(m.get('characterIntelligence', ''))[:6]
        dex_val = str(m.get('characterDexterity', ''))[:6]
        sk = str(m.get('skill_count', 0))
        print(f'{fn:<45s} {cls:>10s} {lvl:>4s} {hp:>10s} {oa:>6s} {da:>6s} {str_val:>6s} {int_val:>6s} {dex_val:>6s} {sk:>6s}')

    # Identify potential Boss candidates: highest HP, highest level, most skills
    print('\n\n=== TOP 30 BY HP (Boss candidates) ===')
    by_hp = sorted(monsters, key=lambda m: float(m.get('characterLife', 0) or 0), reverse=True)
    for m in by_hp[:30]:
        fn = m['filename'][:44]
        cls = str(m.get('monsterClassification', ''))
        lvl = str(m.get('charLevel', '?'))
        hp = str(m.get('characterLife', '?'))
        sk = m.get('skill_count', 0)
        print(f'  {fn:<44s} class={cls:10s} lvl={lvl:<5s} hp={hp:<12s} skills={sk}')

    print('\n=== TOP 30 BY LEVEL ===')
    by_lvl = sorted(monsters, key=lambda m: float(m.get('charLevel', 0) or 0), reverse=True)
    for m in by_lvl[:30]:
        fn = m['filename'][:44]
        cls = str(m.get('monsterClassification', ''))
        lvl = str(m.get('charLevel', '?'))
        hp = str(m.get('characterLife', '?'))
        sk = m.get('skill_count', 0)
        print(f'  {fn:<44s} class={cls:10s} lvl={lvl:<5s} hp={hp:<12s} skills={sk}')

    print('\n=== MONSTERS CURRENTLY NOT HERO/BOSS (need reclassification) ===')
    for m in monsters:
        cls = str(m.get('monsterClassification', '')).lower()
        if cls in ('hero', 'boss'):
            continue
        fn = m['filename'][:44]
        lvl = str(m.get('charLevel', '?'))
        hp = str(m.get('characterLife', '?'))
        sk = m.get('skill_count', 0)
        cur = str(m.get('monsterClassification', '(none)'))
        print(f'  {fn:<44s} current={cur:10s} lvl={lvl:<5s} hp={hp:<12s} skills={sk}')


if __name__ == '__main__':
    main()
