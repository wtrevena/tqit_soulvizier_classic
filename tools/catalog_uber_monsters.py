"""
Catalog all uber/boss/hero monsters in SV 0.98i and identify which have
souls and which need new ones created.

Also extracts monster abilities, descriptions, and stats to inform
soul design decisions.
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase, DATA_TYPE_STRING


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))

    boss_indicators = [
        'boss', 'hero', 'uber', 'named', 'quest',
        'typhon', 'hades', 'hydra', 'chimera', 'cyclops',
        'minotaur', 'talos', 'manticore', 'scarabaeus',
        'megalesios', 'aktaios', 'alastor', 'arachne',
        'nessus', 'ormenos', 'cerberus', 'medusa',
        'sstheno', 'euryale', 'polyphemus', 'yaoguai',
        'barmanu', 'bandari', 'dragonliche', 'pharaoh',
        'sandwraithlord', 'scorposking', 'nehebkau',
        'gorgonqueen', 'toxeus', 'telkine',
    ]

    soul_catalog = {}
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            soul_catalog[nl] = name

    print(f"Total soul items: {len(soul_catalog)}")

    uber_monsters = []
    for name in db.record_names():
        nl = name.lower()
        if '\\creature\\' not in nl and '/creature/' not in nl and \
           '\\creatures\\' not in nl and '/creatures/' not in nl:
            continue

        fields = db.get_fields(name)
        if fields is None:
            continue

        cls = ''
        tmpl = ''
        desc = ''
        skills = []
        mesh = ''
        level = 0

        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'Class' and tf.values:
                cls = str(tf.values[0])
            elif rk == 'templateName' and tf.values:
                tmpl = str(tf.values[0])
            elif rk == 'FileDescription' and tf.values:
                desc = str(tf.values[0])
            elif rk == 'mesh' and tf.values:
                mesh = str(tf.values[0])
            elif rk == 'charLevel' and tf.values:
                level = tf.values[0]
            elif rk.startswith('skillName') and tf.values:
                for v in tf.values:
                    if isinstance(v, str) and v:
                        skills.append(v)
            elif rk == 'attackSkillName' and tf.values:
                for v in tf.values:
                    if isinstance(v, str) and v:
                        skills.append(v)

        if 'monster' not in cls.lower() and 'monster' not in tmpl.lower():
            continue

        is_boss = any(kw in nl for kw in boss_indicators)
        if not is_boss and desc:
            is_boss = any(kw in desc.lower() for kw in ['boss', 'hero', 'uber', 'quest', 'named', 'unique'])

        if not is_boss:
            continue

        has_soul = db.get_field_value(name, 'lootFinger2Item1') is not None
        existing_soul = db.get_field_value(name, 'lootFinger2Item1')
        if existing_soul:
            has_soul = str(existing_soul) != '' and existing_soul != 0

        # Check if a matching soul exists in the catalog
        parts = nl.replace('\\', '/').split('/')
        filename = parts[-1].replace('.dbr', '')
        monster_dir = parts[-2] if len(parts) >= 2 else ''
        clean = re.sub(r'^(u_|um_|uw_|qm_|bm_|cb_|am_|ar_|as_|em_|vampiric_)', '', filename)
        clean = re.sub(r'_?\d+$', '', clean).strip('_')

        soul_exists = False
        for soul_path in soul_catalog:
            if clean in soul_path and len(clean) >= 4:
                soul_exists = True
                break

        uber_monsters.append({
            'name': name,
            'clean_name': clean,
            'dir': monster_dir,
            'level': level,
            'desc': desc,
            'skills': skills[:5],
            'mesh': mesh,
            'has_soul_drop': has_soul,
            'soul_exists_in_catalog': soul_exists,
        })

    uber_monsters.sort(key=lambda x: (x['dir'], x['clean_name']))

    print(f"\nUber/Boss monsters found: {len(uber_monsters)}")

    needs_soul = [m for m in uber_monsters if not m['soul_exists_in_catalog']]
    has_soul_no_drop = [m for m in uber_monsters if m['soul_exists_in_catalog'] and not m['has_soul_drop']]
    fully_wired = [m for m in uber_monsters if m['has_soul_drop']]

    print(f"  Fully wired (has soul drop): {len(fully_wired)}")
    print(f"  Soul exists but not wired: {len(has_soul_no_drop)}")
    print(f"  Needs new soul created: {len(needs_soul)}")

    print("\n" + "=" * 80)
    print("UBER MONSTERS NEEDING NEW SOULS")
    print("=" * 80)

    seen_names = set()
    for m in needs_soul:
        if m['clean_name'] in seen_names:
            continue
        seen_names.add(m['clean_name'])

        skill_names = []
        for s in m['skills']:
            sn = s.replace('\\', '/').split('/')[-1].replace('.dbr', '')
            skill_names.append(sn)

        print(f"\n  {m['name']}")
        print(f"    Clean name: {m['clean_name']}")
        print(f"    Dir: {m['dir']}, Level: {m['level']}")
        print(f"    Desc: {m['desc']}")
        print(f"    Mesh: {m['mesh']}")
        if skill_names:
            print(f"    Skills: {', '.join(skill_names[:5])}")

    print(f"\n{'=' * 80}")
    print(f"Total unique uber names needing new souls: {len(seen_names)}")


if __name__ == '__main__':
    main()
