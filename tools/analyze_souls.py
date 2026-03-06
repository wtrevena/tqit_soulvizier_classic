"""Analyze all soul records in the database to find generic/weak souls needing overhaul.

Filters out:
- Soul templates (soultemplate.dbr) and dummy souls (anysoul.dbr etc.)
- Test souls (records in \test\ paths)
- Only analyzes normal-difficulty variants (_n.dbr or non-variant)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

BS = chr(92)  # backslash

db = ArzDatabase.from_arz(Path('work/SoulvizierClassic/Database/SoulvizierClassic.arz'))

# =============================================================================
# 1. Find ALL soul records, filtering junk
# =============================================================================

all_souls = []
skipped_templates = 0
skipped_test = 0
skipped_variants = 0

for name in db.record_names():
    nl = name.lower()
    if 'equipmentring' not in nl or 'soul' not in nl or not nl.endswith('.dbr'):
        continue

    # Skip soul templates
    if 'soultemplate' in nl or nl.endswith('anysoul.dbr') or 'anycentaur' in nl or 'anymaenad' in nl or 'anysatyr' in nl or 'dummy' in nl.replace(BS, '/').split('/')[-1]:
        skipped_templates += 1
        continue

    # Skip test directory
    if (BS + 'test' + BS) in nl or ('/test/') in nl:
        skipped_test += 1
        continue

    # Only analyze normal difficulty variants (or non-variant souls)
    # Skip _e.dbr and _l.dbr
    fname = nl.replace(BS, '/').split('/')[-1]
    if fname.endswith('_e.dbr') or fname.endswith('_l.dbr'):
        skipped_variants += 1
        continue

    all_souls.append(name)

print(f"\nTotal soul records analyzed: {len(all_souls)}")
print(f"  Skipped: {skipped_templates} templates, {skipped_test} test souls, {skipped_variants} E/L variants")

# =============================================================================
# 2. Analyze each soul
# =============================================================================

SKILL_FIELDS = {'itemSkillName', 'augmentSkillName1', 'augmentSkillName2', 'petBonusName'}

DAMAGE_TYPE_MAP = {
    'offensivePhysicalMin': 'phys', 'offensivePhysicalMax': 'phys',
    'offensivePierceMin': 'pierce', 'offensivePierceMax': 'pierce',
    'offensiveFireMin': 'fire', 'offensiveFireMax': 'fire',
    'offensiveColdMin': 'cold', 'offensiveColdMax': 'cold',
    'offensiveLightningMin': 'light', 'offensiveLightningMax': 'light',
    'offensivePoisonMin': 'poison', 'offensivePoisonMax': 'poison',
    'offensiveLifeMin': 'life', 'offensiveLifeMax': 'life',
    'offensiveSlowPoisonMin': 'psnDot', 'offensiveSlowPoisonMax': 'psnDot',
    'offensiveSlowFireMin': 'fireDot', 'offensiveSlowFireMax': 'fireDot',
    'offensiveSlowColdMin': 'coldDot', 'offensiveSlowColdMax': 'coldDot',
    'offensiveSlowLifeLeechMin': 'leech', 'offensiveSlowLifeLeechMax': 'leech',
    'offensiveSlowBleedingMin': 'bleed', 'offensiveSlowBleedingMax': 'bleed',
    'offensiveSlowElectricalBurnMin': 'lghtDot', 'offensiveSlowElectricalBurnMax': 'lghtDot',
}

INTERESTING_MOD_FIELDS = {
    'characterStrength', 'characterDexterity', 'characterIntelligence',
    'characterStrengthModifier', 'characterDexterityModifier', 'characterIntelligenceModifier',
    'characterLife', 'characterLifeModifier', 'characterLifeRegen',
    'characterMana', 'characterManaModifier', 'characterManaRegenModifier',
    'characterAttackSpeedModifier', 'characterSpellCastSpeedModifier',
    'characterRunSpeedModifier', 'characterTotalSpeedModifier',
    'characterOffensiveAbility', 'characterDefensiveAbility',
    'characterDodgePercent',
    'defensiveProtection',
    'defensiveFire', 'defensiveCold', 'defensiveLightning', 'defensivePoison', 'defensiveLife',
    'defensiveStun', 'defensivePierce',
    'offensivePhysicalModifier', 'offensiveFireModifier', 'offensiveColdModifier',
    'offensiveLightningModifier', 'offensiveSlowPoisonModifier',
    'offensiveLifeModifier', 'offensiveTotalDamageModifier',
    'offensivePierceRatioModifier',
    'offensiveFreezeChance', 'offensiveStunChance',
    'racialBonusRace', 'racialBonusPercentDamage',
}

soul_data = []

for rec in all_souls:
    fields = db.get_fields(rec)
    if not fields:
        continue

    info = {
        'path': rec,
        'itemLevel': 0,
        'fileDescription': '',
        'skills': {},
        'damage_types': {},
        'modifiers': {},
        'has_skills': False,
        'is_svc_uber': 'svc_uber' in rec.lower(),
    }

    for key, tf in fields.items():
        rk = key.split('###')[0]

        if rk == 'itemLevel' and tf.values:
            try:
                info['itemLevel'] = int(tf.values[0])
            except (ValueError, TypeError):
                pass

        if rk == 'FileDescription' and tf.values:
            info['fileDescription'] = str(tf.values[0])

        if rk in SKILL_FIELDS and tf.values:
            val = tf.values[0]
            if isinstance(val, str) and val.strip():
                info['skills'][rk] = val
                info['has_skills'] = True

        if rk in DAMAGE_TYPE_MAP and tf.values:
            try:
                val = float(tf.values[0])
                if val > 0:
                    dtype = DAMAGE_TYPE_MAP[rk]
                    info['damage_types'][dtype] = max(info['damage_types'].get(dtype, 0), val)
            except (ValueError, TypeError):
                pass

        if rk in INTERESTING_MOD_FIELDS and tf.values:
            try:
                val = tf.values[0]
                if isinstance(val, str):
                    info['modifiers'][rk] = val
                else:
                    val = float(val)
                    if val != 0:
                        info['modifiers'][rk] = val
            except (ValueError, TypeError):
                pass

    soul_data.append(info)

# =============================================================================
# 3. Extract monster name
# =============================================================================

def get_soul_name(path, file_desc):
    """Get human-readable name from path."""
    if file_desc and file_desc.strip() and file_desc != '44' and file_desc != '59':
        return file_desc.replace(' - Normal', '').replace(' Soul', '').strip()

    parts = path.replace(BS, '/').split('/')
    filename = parts[-1].replace('.dbr', '')
    for suffix in ('_soul_n', '_soul_e', '_soul_l', '_soul', '_n'):
        if filename.endswith(suffix):
            filename = filename[:-len(suffix)]
    # Get the folder name for context
    folder = parts[-2] if len(parts) >= 2 else ''
    if folder == 'soul' and len(parts) >= 3:
        folder = parts[-3]
    return f"{filename} ({folder})"

# =============================================================================
# 4. Classify souls
# =============================================================================

generic_souls = []
enhanced_souls = []

for s in soul_data:
    path_lower = s['path'].lower()

    # Skip totally empty records (template placeholders)
    if not s['damage_types'] and not s['modifiers'] and not s['has_skills'] and not s['fileDescription']:
        continue

    is_generic = not s['has_skills']

    # Check for non-basic damage types (fire, cold, lightning, poison, life = interesting)
    non_phys_damage = set(s['damage_types'].keys()) - {'phys', 'pierce', 'bleed'}
    if non_phys_damage:
        is_generic = False

    if is_generic:
        generic_souls.append(s)
    else:
        enhanced_souls.append(s)

generic_souls.sort(key=lambda x: x['itemLevel'])
enhanced_souls.sort(key=lambda x: x['itemLevel'])

# =============================================================================
# 5. Print GENERIC souls - these are the overhaul candidates
# =============================================================================

print("\n" + "=" * 140)
print("GENERIC/WEAK SOULS NEEDING OVERHAUL")
print("These souls have NO skills (proc/augment/summon) and only physical/pierce/bleed damage + basic stat mods")
print("=" * 140)

# Group by level range for easier reading
level_groups = {
    'EARLY GAME (1-20)': [],
    'MID GAME (21-35)': [],
    'LATE GAME (36-43)': [],
    'END GAME (44+)': [],
    'LEVEL 0 (unused/test?)': [],
}

for s in generic_souls:
    lvl = s['itemLevel']
    if lvl == 0:
        level_groups['LEVEL 0 (unused/test?)'].append(s)
    elif lvl <= 20:
        level_groups['EARLY GAME (1-20)'].append(s)
    elif lvl <= 35:
        level_groups['MID GAME (21-35)'].append(s)
    elif lvl <= 43:
        level_groups['LATE GAME (36-43)'].append(s)
    else:
        level_groups['END GAME (44+)'].append(s)

overall_idx = 0
for group_name, souls in level_groups.items():
    if not souls:
        continue
    print(f"\n--- {group_name} ({len(souls)} souls) ---")
    print(f"{'#':<4} {'Name':<42} {'Lvl':<5} {'Path':<75} {'Damage':<20} {'Key Mods'}")
    print("-" * 180)

    for s in souls:
        overall_idx += 1
        name = get_soul_name(s['path'], s['fileDescription'])
        dmg = ', '.join(sorted(s['damage_types'].keys())) if s['damage_types'] else 'none'

        # Show only interesting modifiers, abbreviated
        mod_parts = []
        for mk, mv in sorted(s['modifiers'].items()):
            short = mk.replace('character', '').replace('Modifier', '%').replace('defensive', 'def').replace('offensive', 'off').replace('Protection', 'Armor')
            if isinstance(mv, float) and mv == int(mv):
                mod_parts.append(f"{short}={int(mv)}")
            elif isinstance(mv, float):
                mod_parts.append(f"{short}={mv:.1f}")
            else:
                mod_parts.append(f"{short}={mv}")
        mods = ', '.join(mod_parts[:6])
        if len(mod_parts) > 6:
            mods += f" +{len(mod_parts)-6} more"

        print(f"{overall_idx:<4} {name:<42} {s['itemLevel']:<5} {s['path']:<75} {dmg:<20} {mods}")

# =============================================================================
# 6. Summary
# =============================================================================

print("\n" + "=" * 140)
print("SUMMARY")
print("=" * 140)
print(f"  Total souls analyzed (after filtering templates/test/E-L variants): {len(soul_data)}")
print(f"  Souls with content (non-empty): {len(generic_souls) + len(enhanced_souls)}")
print(f"  GENERIC/WEAK (overhaul candidates): {len(generic_souls)}")
print(f"  Enhanced (have skills/elemental damage): {len(enhanced_souls)}")
print(f"  Ratio: {100*len(generic_souls)/(len(generic_souls)+len(enhanced_souls)):.1f}% generic")

# Separate counts
orig_generic = [s for s in generic_souls if not s['is_svc_uber']]
uber_generic = [s for s in generic_souls if s['is_svc_uber']]
orig_enhanced = [s for s in enhanced_souls if not s['is_svc_uber']]
uber_enhanced = [s for s in enhanced_souls if s['is_svc_uber']]

print(f"\n  --- By origin ---")
print(f"  Original SV souls:     {len(orig_generic)} generic, {len(orig_enhanced)} enhanced")
print(f"  SVC auto-gen (uber):   {len(uber_generic)} generic, {len(uber_enhanced)} enhanced")

# Level distribution
print(f"\n  --- Generic soul level distribution ---")
for group_name, souls in level_groups.items():
    if souls:
        print(f"    {group_name}: {len(souls)} souls")

# Most impactful overhaul targets: level 44+ original souls with actual names
print(f"\n  --- HIGH-PRIORITY OVERHAUL TARGETS ---")
print(f"  (Original SV souls at level 30+ with real names, no skills)")
priority = [s for s in orig_generic
            if s['itemLevel'] >= 30
            and s['fileDescription']
            and 'Dummy' not in s['fileDescription']
            and s['fileDescription'] not in ('44', '59', 'Hades', 'Orient', 'Egypt', 'Greece', 'Olympus')]
priority.sort(key=lambda x: x['itemLevel'])
for s in priority:
    name = get_soul_name(s['path'], s['fileDescription'])
    dmg = ', '.join(sorted(s['damage_types'].keys())) if s['damage_types'] else 'none'
    print(f"    Lvl {s['itemLevel']:>3}: {name:<45} dmg={dmg:<15} path={s['path']}")
