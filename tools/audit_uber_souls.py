"""Deep audit of all created uber souls vs their source monsters.

For each soul, extracts:
- Monster's actual skills (with full paths for context)
- Monster's stats (HP, damage types, resistances)
- Monster's mesh/appearance
- The soul's inferred element and role
- Whether the inference makes sense

Outputs a detailed report for human review.
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


ELEMENT_KEYWORDS = {
    'fire': ['fire', 'flame', 'burn', 'pyro', 'blaze', 'inferno', 'lava', 'magma', 'volcanic', 'meteor'],
    'cold': ['cold', 'frost', 'ice', 'frozen', 'blizzard', 'chill', 'freeze', 'winter', 'arctic', 'frostbite'],
    'lightning': ['lightning', 'thunder', 'storm', 'electric', 'shock', 'bolt', 'static', 'tempest', 'distort'],
    'poison': ['poison', 'venom', 'toxic', 'plague', 'disease', 'acid', 'noxious', 'blight', 'corruption', 'decay'],
    'physical': ['melee', 'sword', 'axe', 'club', 'blunt', 'cleave', 'smash', 'charge', 'warrior', 'brute', 'bash'],
    'life': ['life', 'soul', 'spirit', 'death', 'undead', 'necrotic', 'drain', 'wraith', 'ghost', 'liche', 'vitality'],
}


def get_offensive_elements(fields):
    """Check which offensive elements the monster actually has non-zero values for."""
    elements = {}
    for key, tf in fields.items():
        rk = key.split('###')[0].lower()
        if not tf.values or tf.values[0] is None:
            continue
        val = float(tf.values[0]) if isinstance(tf.values[0], (int, float)) else 0
        if val <= 0:
            continue
        if 'offensivefire' in rk and 'min' in rk:
            elements['fire'] = val
        elif 'offensivecold' in rk and 'min' in rk:
            elements['cold'] = val
        elif 'offensivelightning' in rk and 'min' in rk:
            elements['lightning'] = val
        elif ('offensivepoison' in rk or 'offensiveslowpoison' in rk) and 'min' in rk:
            elements['poison'] = val
        elif 'offensivephysical' in rk and 'min' in rk:
            elements['physical'] = val
        elif 'offensivelife' in rk and 'min' in rk:
            elements['life'] = val
    return elements


def analyze_skill_elements(db, skill_paths):
    """Analyze skill records to determine their element types."""
    skill_elements = {}
    for sp in skill_paths:
        if not db.has_record(sp):
            continue
        fields = db.get_fields(sp)
        if not fields:
            continue
        elems = get_offensive_elements(fields)
        skill_name = sp.replace('\\', '/').split('/')[-1].replace('.dbr', '')
        if elems:
            skill_elements[skill_name] = elems
        # Also check the skill's buff/secondary records
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk in ('buffSkillName', 'petSkillName') and tf.values and tf.values[0]:
                sub_path = str(tf.values[0])
                if db.has_record(sub_path):
                    sub_fields = db.get_fields(sub_path)
                    if sub_fields:
                        sub_elems = get_offensive_elements(sub_fields)
                        if sub_elems:
                            skill_elements[skill_name + ' (buff)'] = sub_elems
    return skill_elements


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
    skip_patterns = ['test', 'zzdev', 'old_', 'copy of', 'conflicted', 'minion',
                     'ambush', 'drownedsailor', 'quest_']

    existing_souls = set()
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if 'svc_uber' not in nl:
                existing_souls.add(nl)

    seen_names = set()
    audit = []

    for name in db.record_names():
        nl = name.lower()
        if '\\creature\\' not in nl and '/creature/' not in nl and \
           '\\creatures\\' not in nl and '/creatures/' not in nl:
            continue
        if any(skip in nl for skip in skip_patterns):
            continue
        is_boss = any(kw in nl for kw in boss_indicators)
        if not is_boss:
            continue

        fields = db.get_fields(name)
        if fields is None:
            continue

        cls = ''
        tmpl = ''
        desc = ''
        skills_paths = []
        skills_names = []
        mesh = ''
        level = 0
        classification = ''

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
                level = int(tf.values[0]) if isinstance(tf.values[0], (int, float)) else 0
            elif rk == 'monsterClassification' and tf.values:
                classification = str(tf.values[0])
            elif rk.startswith('skillName') and tf.values:
                for v in tf.values:
                    if isinstance(v, str) and v:
                        skills_paths.append(v)
                        skills_names.append(v.replace('\\', '/').split('/')[-1].replace('.dbr', ''))
            elif rk == 'attackSkillName' and tf.values:
                for v in tf.values:
                    if isinstance(v, str) and v:
                        skills_paths.append(v)
                        skills_names.append(v.replace('\\', '/').split('/')[-1].replace('.dbr', ''))

        if 'monster' not in cls.lower() and 'monster' not in tmpl.lower():
            continue

        parts = nl.replace('\\', '/').split('/')
        filename = parts[-1].replace('.dbr', '')
        monster_dir = parts[-2] if len(parts) >= 2 else ''
        clean = re.sub(r'^(u_|um_|uw_|qm_|bm_|cb_|am_|ar_|as_|em_|vampiric_)', '', filename)
        clean = re.sub(r'_?\d+$', '', clean).strip('_')

        if clean in seen_names:
            continue

        has_matching_soul = False
        for sp in existing_souls:
            if clean in sp and len(clean) >= 4:
                has_matching_soul = True
                break
        if has_matching_soul:
            continue

        seen_names.add(clean)

        # Get monster's actual offensive elements
        monster_elements = get_offensive_elements(fields)

        # Analyze skill elements
        skill_elements = analyze_skill_elements(db, skills_paths)

        # Determine what the monster ACTUALLY uses
        all_elements = dict(monster_elements)
        for sk_elems in skill_elements.values():
            for elem, val in sk_elems.items():
                all_elements[elem] = all_elements.get(elem, 0) + val

        # Current inference
        text = ' '.join(skills_names + [desc, clean]).lower()
        inferred_element = 'physical'
        best_score = 0
        for elem, keywords in ELEMENT_KEYWORDS.items():
            score = sum(3 if kw in text else 0 for kw in keywords)
            if score > best_score:
                best_score = score
                inferred_element = elem
        if best_score == 0:
            inferred_element = 'physical'

        # Determine actual primary element from data
        actual_primary = 'physical'
        if all_elements:
            actual_primary = max(all_elements, key=all_elements.get)

        # Check role inference
        has_projectile = any(w in text for w in ['projectile', 'bolt', 'bow', 'arrow', 'ranged', 'staff', 'caster', 'spell'])
        has_summon = any(w in text for w in ['summon', 'spawn', 'minion', 'pet'])
        has_aura = any(w in text for w in ['aura', 'buff', 'passive', 'shield'])
        if has_projectile:
            inferred_role = 'caster'
        elif has_summon:
            inferred_role = 'summoner'
        elif has_aura:
            inferred_role = 'tank'
        else:
            inferred_role = 'melee'

        # Flag mismatches
        mismatch = inferred_element != actual_primary and actual_primary != 'physical' and best_score > 0

        audit.append({
            'name': name,
            'clean': clean,
            'level': level,
            'classification': classification,
            'mesh': mesh.replace('\\', '/').split('/')[-1] if mesh else '',
            'monster_dir': monster_dir,
            'skills': skills_names,
            'skill_elements': skill_elements,
            'monster_elements': monster_elements,
            'all_elements': all_elements,
            'inferred_element': inferred_element,
            'actual_primary': actual_primary,
            'inferred_role': inferred_role,
            'mismatch': mismatch,
            'desc': desc,
        })

    # Output report
    audit.sort(key=lambda x: x['level'])

    mismatches = [a for a in audit if a['mismatch']]
    no_data = [a for a in audit if not a['all_elements']]

    print(f'Total souls audited: {len(audit)}')
    print(f'Element mismatches (keyword vs actual data): {len(mismatches)}')
    print(f'No offensive data found (defaulting to physical): {len(no_data)}')

    if mismatches:
        print(f'\n\n===== ELEMENT MISMATCHES (keyword inference != actual damage) =====')
        for a in mismatches:
            print(f'\n  {a["clean"]} (lvl {a["level"]}, {a["classification"] or "?"}, dir: {a["monster_dir"]})')
            print(f'    Inferred: {a["inferred_element"]}  |  Actual primary: {a["actual_primary"]}')
            print(f'    Monster base damage: {a["monster_elements"]}')
            print(f'    Skills: {", ".join(a["skills"][:6])}')
            if a['skill_elements']:
                for sk, elems in list(a['skill_elements'].items())[:4]:
                    print(f'      {sk}: {elems}')

    print(f'\n\n===== FULL AUDIT (all {len(audit)} souls) =====')
    for a in audit:
        flag = ' ** MISMATCH' if a['mismatch'] else ''
        flag += ' ?? NO DATA' if not a['all_elements'] else ''
        print(f'\n  {a["clean"]} (lvl {a["level"]}, {a["classification"] or "none"}, {a["monster_dir"]}){flag}')
        print(f'    Inferred: element={a["inferred_element"]}, role={a["inferred_role"]}')
        if a['all_elements']:
            print(f'    Actual elements: {a["all_elements"]}')
        if a['monster_elements']:
            print(f'    Monster base: {a["monster_elements"]}')
        print(f'    Skills ({len(a["skills"])}): {", ".join(a["skills"][:8])}')
        if a['skill_elements']:
            for sk, elems in list(a['skill_elements'].items())[:5]:
                print(f'      {sk}: {elems}')
        if a['desc']:
            print(f'    Desc: {a["desc"][:80]}')


if __name__ == '__main__':
    main()
