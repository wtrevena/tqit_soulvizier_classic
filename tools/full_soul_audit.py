"""Comprehensive audit of ALL souls in SoulvizierClassic.

Audits:
  Part A: New uber souls (140) - element/role accuracy, stat balance, thematic fit
  Part B: Existing SV souls (~808 types) - which monsters drop them, classifications
  Part C: Drop rate summary - who drops what at what rate
  Part D: Orphan/issue detection

Outputs a detailed markdown document for human review and tuning.
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


DAMAGE_FIELDS = {
    'offensiveFireMin': 'fire', 'offensiveFireMax': 'fire',
    'offensiveBurnMin': 'fire', 'offensiveBurnMax': 'fire',
    'offensiveColdMin': 'cold', 'offensiveColdMax': 'cold',
    'offensiveFrostbiteMin': 'cold', 'offensiveFrostbiteMax': 'cold',
    'offensiveLightningMin': 'lightning', 'offensiveLightningMax': 'lightning',
    'offensiveElectricalBurnMin': 'lightning', 'offensiveElectricalBurnMax': 'lightning',
    'offensivePoisonMin': 'poison', 'offensivePoisonMax': 'poison',
    'offensiveSlowPoisonMin': 'poison', 'offensiveSlowPoisonMax': 'poison',
    'offensiveLifeMin': 'life', 'offensiveLifeMax': 'life',
    'offensiveLifeLeechMin': 'life', 'offensiveLifeLeechMax': 'life',
    'offensivePhysicalMin': 'physical', 'offensivePhysicalMax': 'physical',
    'offensivePierceMin': 'physical', 'offensivePierceMax': 'physical',
    'offensiveBleedingMin': 'physical', 'offensiveBleedingMax': 'physical',
}


def analyze_skill_damage(db, skill_path, depth=0):
    if depth > 3 or not db.has_record(skill_path):
        return {}
    fields = db.get_fields(skill_path)
    if not fields:
        return {}
    elements = {}
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if rk in DAMAGE_FIELDS and tf.values and tf.values[0] is not None:
            val = float(tf.values[0]) if isinstance(tf.values[0], (int, float)) else 0
            if val > 0:
                elem = DAMAGE_FIELDS[rk]
                elements[elem] = elements.get(elem, 0) + val
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if rk in ('buffSkillName', 'petSkillName', 'skillName1') and tf.values:
            for v in tf.values:
                if isinstance(v, str) and v:
                    sub = analyze_skill_damage(db, v, depth + 1)
                    for elem, val in sub.items():
                        elements[elem] = elements.get(elem, 0) + val
    return elements


def get_monster_data(db, name, fields):
    """Extract all relevant data from a monster record."""
    data = {
        'name': name,
        'cls': '', 'tmpl': '', 'desc': '', 'classification': '',
        'level': 0, 'skills': [], 'skill_paths': [],
        'soul_ref': '', 'equip_chance': 0, 'drop_items': 0,
        'actual_elements': {},
    }
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if not tf.values:
            continue
        v0 = tf.values[0]
        if rk == 'Class':
            data['cls'] = str(v0)
        elif rk == 'templateName':
            data['tmpl'] = str(v0)
        elif rk == 'FileDescription':
            data['desc'] = str(v0)
        elif rk == 'monsterClassification':
            data['classification'] = str(v0)
        elif rk == 'charLevel' and isinstance(v0, (int, float)):
            data['level'] = int(v0)
        elif rk.startswith('skillName') and isinstance(v0, str) and v0:
            for v in tf.values:
                if isinstance(v, str) and v:
                    data['skill_paths'].append(v)
                    data['skills'].append(v.replace('\\', '/').split('/')[-1].replace('.dbr', ''))
        elif rk == 'attackSkillName' and isinstance(v0, str) and v0:
            for v in tf.values:
                if isinstance(v, str) and v:
                    data['skill_paths'].append(v)
                    data['skills'].append(v.replace('\\', '/').split('/')[-1].replace('.dbr', ''))
        elif rk == 'lootFinger2Item1':
            refs = [str(v) for v in tf.values if v and 'soul' in str(v).lower()]
            if refs:
                data['soul_ref'] = refs[0]
        elif rk == 'chanceToEquipFinger2' and isinstance(v0, (int, float)):
            data['equip_chance'] = float(v0)
        elif rk == 'dropItems' and isinstance(v0, (int, float)):
            data['drop_items'] = int(v0)

    for sp in data['skill_paths']:
        elems = analyze_skill_damage(db, sp)
        for elem, val in elems.items():
            data['actual_elements'][elem] = data['actual_elements'].get(elem, 0) + val

    return data


def get_soul_stats(db, soul_path):
    """Extract stat summary from a soul record."""
    if not db.has_record(soul_path):
        return None
    fields = db.get_fields(soul_path)
    if not fields:
        return None
    stats = {}
    interesting = [
        'characterStrength', 'characterIntelligence', 'characterDexterity',
        'characterLife', 'characterMana', 'characterLifeRegen',
        'characterManaRegenModifier', 'characterAttackSpeedModifier',
        'characterSpellCastSpeedModifier',
        'offensivePhysicalMin', 'offensivePhysicalMax',
        'offensiveFireMin', 'offensiveFireMax', 'offensiveFireModifier',
        'offensiveColdMin', 'offensiveColdMax', 'offensiveColdModifier',
        'offensiveLightningMin', 'offensiveLightningMax', 'offensiveLightningModifier',
        'offensiveSlowPoisonMin', 'offensiveSlowPoisonMax', 'offensiveSlowPoisonModifier',
        'offensiveLifeMin', 'offensiveLifeMax', 'offensiveLifeModifier',
        'offensivePhysicalModifier',
        'defensiveFire', 'defensiveCold', 'defensiveLightning',
        'defensivePoison', 'defensiveLife', 'defensiveProtection',
        'itemLevel', 'levelRequirement',
        'strengthRequirement', 'intelligenceRequirement', 'dexterityRequirement',
        'itemNameTag', 'FileDescription',
    ]
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if rk in interesting and tf.values and tf.values[0] is not None:
            stats[rk] = tf.values[0]
    return stats


def primary_element(elements):
    if not elements:
        return 'physical'
    return max(elements, key=elements.get)


def format_elements(elements):
    if not elements:
        return '(none - physical default)'
    parts = []
    for elem in sorted(elements, key=elements.get, reverse=True):
        parts.append(f'{elem}={elements[elem]:.0f}')
    return ', '.join(parts)


def main():
    if len(sys.argv) < 2:
        print("Usage: full_soul_audit.py <database.arz> [output.md]")
        sys.exit(1)

    db = ArzDatabase.from_arz(Path(sys.argv[1]))
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('soul_audit_full.md')

    # =========================================================================
    # Phase 1: Index all soul items
    # =========================================================================
    print("Phase 1: Indexing soul items...")
    soul_items = {}
    uber_soul_items = {}
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if 'svc_uber' in nl:
                uber_soul_items[nl] = name
            else:
                soul_items[nl] = name

    print(f"  Existing SV souls: {len(soul_items)}")
    print(f"  New uber souls: {len(uber_soul_items)}")

    # Group souls by type (strip _n/_e/_l suffix)
    def soul_type_key(path):
        p = path.lower().replace('\\', '/').split('/')[-1].replace('.dbr', '')
        p = re.sub(r'_[nel]$', '', p)
        return p

    sv_soul_types = defaultdict(list)
    for nl, name in soul_items.items():
        sk = soul_type_key(nl)
        sv_soul_types[sk].append(name)

    uber_soul_types = defaultdict(list)
    for nl, name in uber_soul_items.items():
        sk = soul_type_key(nl)
        uber_soul_types[sk].append(name)

    print(f"  SV soul types (unique): {len(sv_soul_types)}")
    print(f"  Uber soul types (unique): {len(uber_soul_types)}")

    # =========================================================================
    # Phase 2: Index all monsters with soul references
    # =========================================================================
    print("Phase 2: Indexing monsters...")
    monsters_with_souls = []
    monsters_by_soul = defaultdict(list)
    all_monsters = []

    for name in db.record_names():
        nl = name.lower()
        if '\\creature' not in nl and '/creature' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        data = get_monster_data(db, name, fields)
        if 'monster' not in data['cls'].lower() and 'monster' not in data['tmpl'].lower():
            continue
        all_monsters.append(data)
        if data['soul_ref']:
            monsters_with_souls.append(data)
            soul_key = soul_type_key(data['soul_ref'])
            monsters_by_soul[soul_key].append(data)

    print(f"  Total monsters: {len(all_monsters)}")
    print(f"  Monsters with soul refs: {len(monsters_with_souls)}")

    # =========================================================================
    # Phase 3: Classify drop status
    # =========================================================================
    print("Phase 3: Classifying drop rates...")

    active_droppers = []
    inactive_souls = []
    for m in monsters_with_souls:
        if m['equip_chance'] > 0 and m['drop_items'] >= 1:
            active_droppers.append(m)
        else:
            inactive_souls.append(m)

    drop_by_class = defaultdict(lambda: {'active': 0, 'inactive': 0})
    for m in active_droppers:
        drop_by_class[m['classification'] or '(none)']['active'] += 1
    for m in inactive_souls:
        drop_by_class[m['classification'] or '(none)']['inactive'] += 1

    print(f"  Active droppers (equip chance > 0): {len(active_droppers)}")
    print(f"  Inactive (soul ref but no equip chance): {len(inactive_souls)}")

    # =========================================================================
    # Phase 4: Detailed uber soul audit
    # =========================================================================
    print("Phase 4: Auditing uber souls...")

    uber_audit = []
    for soul_key, soul_names in sorted(uber_soul_types.items()):
        stats = get_soul_stats(db, soul_names[0])
        if not stats:
            continue

        monster_matches = monsters_by_soul.get(soul_key, [])
        if not monster_matches:
            for sk2, mlist in monsters_by_soul.items():
                if soul_key in sk2 or sk2 in soul_key:
                    monster_matches = mlist
                    break

        m_data = monster_matches[0] if monster_matches else None

        inferred_elem = 'physical'
        if stats:
            if any(k.startswith('offensiveFire') and not k.endswith('Modifier') for k in stats):
                inferred_elem = 'fire'
            elif any(k.startswith('offensiveCold') and not k.endswith('Modifier') for k in stats):
                inferred_elem = 'cold'
            elif any(k.startswith('offensiveLightning') and not k.endswith('Modifier') for k in stats):
                inferred_elem = 'lightning'
            elif any(k.startswith('offensiveSlowPoison') or k.startswith('offensivePoison') for k in stats):
                inferred_elem = 'poison'
            elif any(k.startswith('offensiveLife') and not k.endswith('Modifier') for k in stats):
                inferred_elem = 'life'

        inferred_role = 'melee'
        if stats:
            if 'characterIntelligence' in stats:
                inferred_role = 'caster'
            elif 'defensiveProtection' in stats and 'characterStrength' in stats:
                inferred_role = 'tank'
            elif 'characterStrength' in stats:
                inferred_role = 'melee'

        actual_elem = primary_element(m_data['actual_elements']) if m_data else '?'
        mismatch = m_data and actual_elem != 'physical' and inferred_elem != actual_elem

        uber_audit.append({
            'soul_key': soul_key,
            'display': stats.get('FileDescription', soul_key),
            'level': stats.get('itemLevel', '?'),
            'lvl_req': stats.get('levelRequirement', '?'),
            'str_req': stats.get('strengthRequirement', 0),
            'int_req': stats.get('intelligenceRequirement', 0),
            'dex_req': stats.get('dexterityRequirement', 0),
            'soul_element': inferred_elem,
            'soul_role': inferred_role,
            'actual_element': actual_elem,
            'actual_elements': m_data['actual_elements'] if m_data else {},
            'monster_class': m_data['classification'] if m_data else '?',
            'monster_level': m_data['level'] if m_data else '?',
            'monster_skills': m_data['skills'][:6] if m_data else [],
            'monster_name': m_data['name'].replace('\\', '/').split('/')[-1].replace('.dbr', '') if m_data else '?',
            'drop_chance': m_data['equip_chance'] if m_data else 0,
            'mismatch': mismatch,
            'stats': stats,
            'num_monsters': len(monster_matches),
        })

    uber_audit.sort(key=lambda x: (x.get('level', 0) if isinstance(x.get('level'), int) else 0))

    # =========================================================================
    # Phase 5: Existing soul audit
    # =========================================================================
    print("Phase 5: Auditing existing SV souls...")

    sv_audit = []
    for soul_key, soul_names in sorted(sv_soul_types.items()):
        stats = get_soul_stats(db, soul_names[0])
        monster_matches = monsters_by_soul.get(soul_key, [])

        active_monsters = [m for m in monster_matches if m['equip_chance'] > 0]
        inactive_monsters = [m for m in monster_matches if m['equip_chance'] <= 0]

        classes = defaultdict(int)
        for m in monster_matches:
            classes[m['classification'] or '(none)'] += 1

        sv_audit.append({
            'soul_key': soul_key,
            'display': stats.get('FileDescription', soul_key) if stats else soul_key,
            'level': stats.get('itemLevel', '?') if stats else '?',
            'num_variants': len(soul_names),
            'total_monsters': len(monster_matches),
            'active_monsters': len(active_monsters),
            'inactive_monsters': len(inactive_monsters),
            'classes': dict(classes),
            'has_stats': stats is not None,
        })

    # =========================================================================
    # Write report
    # =========================================================================
    print(f"Writing report to {out_path}...")

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# SoulvizierClassic - Comprehensive Soul Audit\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Existing SV soul types**: {len(sv_soul_types)}\n")
        f.write(f"- **New uber soul types**: {len(uber_soul_types)}\n")
        f.write(f"- **Total monsters with soul refs**: {len(monsters_with_souls)}\n")
        f.write(f"- **Active droppers** (Hero/Boss/Quest with equip chance): {len(active_droppers)}\n")
        f.write(f"- **Inactive** (Common/Champion with soul ref but no equip): {len(inactive_souls)}\n\n")

        f.write("### Drop rates by classification\n\n")
        f.write("| Classification | Active Droppers | Inactive (no equip chance) |\n")
        f.write("|---------------|----------------|---------------------------|\n")
        for cls in sorted(drop_by_class.keys()):
            d = drop_by_class[cls]
            f.write(f"| {cls} | {d['active']} | {d['inactive']} |\n")

        # === PART A: NEW UBER SOULS ===
        f.write("\n\n---\n\n")
        f.write("## Part A: New Uber Souls (140 created)\n\n")

        mismatches = [a for a in uber_audit if a['mismatch']]
        f.write(f"**Element mismatches** (soul element != monster's actual primary element): **{len(mismatches)}**\n\n")

        if mismatches:
            f.write("### Element Mismatches\n\n")
            f.write("These souls have an element that differs from the monster's actual damage output:\n\n")
            f.write("| Soul | Level | Soul Element | Actual Element | Monster Skills | Classification |\n")
            f.write("|------|-------|-------------|---------------|----------------|----------------|\n")
            for a in mismatches:
                skills = ', '.join(a['monster_skills'][:3])
                f.write(f"| {a['display']} | {a['level']} | **{a['soul_element']}** | **{a['actual_element']}** | {skills} | {a['monster_class']} |\n")
            f.write("\n")

        f.write("### Full Uber Soul Catalog\n\n")
        for a in uber_audit:
            flag = ""
            if a['mismatch']:
                flag = " :warning: ELEMENT MISMATCH"
            f.write(f"#### {a['display']}{flag}\n\n")
            f.write(f"- **Monster**: `{a['monster_name']}` (classification: {a['monster_class']}, level: {a['monster_level']})\n")
            f.write(f"- **Soul level**: {a['level']} (req: {a['lvl_req']})\n")
            f.write(f"- **Soul element**: {a['soul_element']} | **Role**: {a['soul_role']}\n")
            f.write(f"- **Monster's actual elements**: {format_elements(a['actual_elements'])}\n")
            f.write(f"- **Monster skills**: {', '.join(a['monster_skills']) if a['monster_skills'] else '(none found)'}\n")
            f.write(f"- **Drop chance**: {a['drop_chance']}% | **# monsters with this soul**: {a['num_monsters']}\n")
            f.write(f"- **Requirements**: STR={a['str_req']}, INT={a['int_req']}, DEX={a['dex_req']}\n")

            if a['stats']:
                bonus_parts = []
                s = a['stats']
                if 'characterStrength' in s:
                    bonus_parts.append(f"+{s['characterStrength']} Str")
                if 'characterIntelligence' in s:
                    bonus_parts.append(f"+{s['characterIntelligence']} Int")
                if 'characterLife' in s:
                    bonus_parts.append(f"+{s['characterLife']} HP")
                if 'characterMana' in s:
                    bonus_parts.append(f"+{s['characterMana']} MP")
                if 'characterLifeRegen' in s:
                    bonus_parts.append(f"+{s['characterLifeRegen']} HP/s")
                if 'characterAttackSpeedModifier' in s:
                    bonus_parts.append(f"+{s['characterAttackSpeedModifier']}% atk spd")
                if 'characterSpellCastSpeedModifier' in s:
                    bonus_parts.append(f"+{s['characterSpellCastSpeedModifier']}% cast spd")
                if 'characterManaRegenModifier' in s:
                    bonus_parts.append(f"+{s['characterManaRegenModifier']}% mana regen")
                if 'defensiveProtection' in s:
                    bonus_parts.append(f"+{s['defensiveProtection']} armor")

                off_parts = []
                for elem_name in ['Physical', 'Fire', 'Cold', 'Lightning', 'Life']:
                    mn = s.get(f'offensive{elem_name}Min')
                    mx = s.get(f'offensive{elem_name}Max')
                    if mn and mx:
                        off_parts.append(f"{mn:.0f}-{mx:.0f} {elem_name.lower()}")
                for k in ['offensiveSlowPoisonMin']:
                    if k in s:
                        mx = s.get('offensiveSlowPoisonMax', s[k])
                        off_parts.append(f"{s[k]:.0f}-{mx:.0f} poison/s")

                mod_parts = []
                for elem_name in ['Physical', 'Fire', 'Cold', 'Lightning', 'Life']:
                    mod = s.get(f'offensive{elem_name}Modifier')
                    if mod:
                        mod_parts.append(f"+{mod}% {elem_name.lower()}")
                if 'offensiveSlowPoisonModifier' in s:
                    mod_parts.append(f"+{s['offensiveSlowPoisonModifier']}% poison")

                res_parts = []
                for elem_name in ['Fire', 'Cold', 'Lightning', 'Poison', 'Life']:
                    rk = f'defensive{elem_name}'
                    if rk in s:
                        v = s[rk]
                        res_parts.append(f"{v:+d}% {elem_name.lower()} res")

                f.write(f"- **Stat bonuses**: {', '.join(bonus_parts) if bonus_parts else '(none)'}\n")
                f.write(f"- **Offensive**: {', '.join(off_parts) if off_parts else '(none)'}\n")
                f.write(f"- **Damage modifiers**: {', '.join(mod_parts) if mod_parts else '(none)'}\n")
                f.write(f"- **Resistances**: {', '.join(res_parts) if res_parts else '(none)'}\n")
            f.write("\n")

        # === PART B: EXISTING SV SOULS ===
        f.write("\n---\n\n")
        f.write("## Part B: Existing SV Soul Catalog\n\n")
        f.write(f"Total unique soul types: {len(sv_audit)}\n\n")

        orphaned = [a for a in sv_audit if a['total_monsters'] == 0]
        no_active = [a for a in sv_audit if a['total_monsters'] > 0 and a['active_monsters'] == 0]

        f.write(f"- **Orphaned souls** (no monster references them): {len(orphaned)}\n")
        f.write(f"- **Dormant souls** (monsters have ref but no equip chance): {len(no_active)}\n")
        f.write(f"- **Active souls** (at least one monster actively drops): {len(sv_audit) - len(orphaned) - len(no_active)}\n\n")

        if orphaned:
            f.write("### Orphaned Souls (no monster drops them)\n\n")
            f.write("| Soul | Level | Variants |\n")
            f.write("|------|-------|----------|\n")
            for a in orphaned[:50]:
                f.write(f"| {a['display']} | {a['level']} | {a['num_variants']} |\n")
            if len(orphaned) > 50:
                f.write(f"\n... and {len(orphaned) - 50} more\n")
            f.write("\n")

        f.write("### Active Existing Souls (monsters actually drop these)\n\n")
        f.write("| Soul | Level | Active Monsters | Inactive Monsters | Monster Classes |\n")
        f.write("|------|-------|----------------|-------------------|----------------|\n")
        active_sv = [a for a in sv_audit if a['active_monsters'] > 0]
        active_sv.sort(key=lambda x: -x['active_monsters'])
        for a in active_sv:
            cls_str = ', '.join(f'{c}:{n}' for c, n in sorted(a['classes'].items()))
            f.write(f"| {a['display']} | {a['level']} | {a['active_monsters']} | {a['inactive_monsters']} | {cls_str} |\n")

        if no_active:
            f.write(f"\n### Dormant Souls (monsters reference but no equip chance = no drops)\n\n")
            f.write("These souls existed in original SV but won't drop in AE because the monsters\n")
            f.write("holding them are Common/Champion/none classification.\n\n")
            f.write("| Soul | Level | # Monsters | Monster Classes |\n")
            f.write("|------|-------|-----------|----------------|\n")
            no_active.sort(key=lambda x: x['soul_key'])
            for a in no_active[:80]:
                cls_str = ', '.join(f'{c}:{n}' for c, n in sorted(a['classes'].items()))
                f.write(f"| {a['display']} | {a['level']} | {a['total_monsters']} | {cls_str} |\n")
            if len(no_active) > 80:
                f.write(f"\n... and {len(no_active) - 80} more\n")
            f.write("\n")

        # === PART C: DROP RATE ANALYSIS ===
        f.write("\n---\n\n")
        f.write("## Part C: Drop Rate Analysis\n\n")

        rate_buckets = defaultdict(list)
        for m in active_droppers:
            rate = m['equip_chance']
            fn = m['name'].replace('\\', '/').split('/')[-1].replace('.dbr', '')
            rate_buckets[rate].append(f"{fn} ({m['classification']})")

        f.write("| Drop Rate | # Monsters | Examples |\n")
        f.write("|-----------|-----------|----------|\n")
        for rate in sorted(rate_buckets.keys()):
            monsters = rate_buckets[rate]
            examples = ', '.join(monsters[:5])
            if len(monsters) > 5:
                examples += f', ... (+{len(monsters)-5} more)'
            f.write(f"| {rate}% | {len(monsters)} | {examples} |\n")

        # === PART D: ISSUES & RECOMMENDATIONS ===
        f.write("\n---\n\n")
        f.write("## Part D: Issues & Recommendations\n\n")

        issues = []
        for a in uber_audit:
            if a['mismatch']:
                issues.append(f"- **{a['display']}**: Soul element is **{a['soul_element']}** but monster actually deals **{a['actual_element']}** damage ({format_elements(a['actual_elements'])})")

        req_issues = [a for a in uber_audit if a['str_req'] or a['int_req'] or a['dex_req']]
        if req_issues:
            for a in req_issues:
                reqs = []
                if a['str_req']:
                    reqs.append(f"STR={a['str_req']}")
                if a['int_req']:
                    reqs.append(f"INT={a['int_req']}")
                if a['dex_req']:
                    reqs.append(f"DEX={a['dex_req']}")
                issues.append(f"- **{a['display']}**: Has non-zero stat requirements ({', '.join(reqs)}) -- should be 0 per mod goals")

        no_monster = [a for a in uber_audit if a['num_monsters'] == 0]
        if no_monster:
            for a in no_monster:
                issues.append(f"- **{a['display']}**: Soul created but no monster found to drop it")

        if issues:
            f.write(f"### Found {len(issues)} issue(s)\n\n")
            for issue in issues:
                f.write(f"{issue}\n")
        else:
            f.write("No issues found.\n")

        f.write("\n### Tuning Notes\n\n")
        f.write("1. **Element mismatches**: Consider updating `MANUAL_OVERRIDES` in `create_uber_souls.py` for flagged souls\n")
        f.write("2. **Dormant souls**: ~{} soul types only exist on Common/Champion monsters and will never drop in AE\n".format(len(no_active)))
        f.write("3. **Orphaned souls**: {} soul items exist with no monster referencing them\n".format(len(orphaned)))
        f.write("4. **Stat requirements**: All souls should have 0 stat requirements per mod goals\n")

    print(f"Done. Report: {out_path}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
