"""
Create thematic souls for uber/boss monsters that don't have them.

Each soul is designed based on the monster's:
- Actual skill damage types (analyzed from skill records)
- Role (melee/caster/ranged/summoner) from skills and descriptions
- Monster type and lore significance
- Level scaling

Outputs:
- New soul records added to the database
- Text tags for localization (written to a file for Text_EN.arc)
- Tracking document listing all created souls
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase, TypedField, DATA_TYPE_INT, DATA_TYPE_FLOAT, DATA_TYPE_STRING
from uber_soul_designs import SOUL_DESIGNS


SOUL_TEMPLATE = 'database\\Templates\\Jewelry_Ring.tpl'
SOUL_CLASS = 'ArmorJewelry_Ring'
SOUL_BITMAP = 'Items\\miscellaneous\\n_soul.tex'
SOUL_MESH = 'drx\\meshes\\n_soulmesh.msh'
SOUL_COST = 'records/game/itemcost_soul.dbr'
SOUL_DROP_SOUND = 'records/sounds/soundpak/Items/SoulDropPak.dbr'
SOUL_DROP_3D = 'records/sounds/soundpak/Items/SoulDrop3DPak.dbr'
SOUL_DROP_WATER = 'Records\\Sounds\\SoundPak\\Items\\WaterSmDropPak.dbr'

SKIP_NAMES = [
    'test', 'zzdev', 'old_', 'copy of', 'conflicted', 'minion',
    '_ambush', 'drownedsailor', '_bones', '_decoration',
    'controller_', '_spirit', '_obelisk', 'obeliska', 'obeliskb',
    'obeliskc', 'obeliskd', 'form2', 'form3', 'pcos ', 'pcos\t',
    'modstridende', '_old\\', '_old/', '\\old\\', '/old/',
    'audiotestboss', 'nessusminion',
]

SKIP_EXACT = {
    'typhon_bones', 'talos_decoration', 'controller_spider',
    'manticore_bones', 'boss_pharaohshonorguard_spirit',
    'boss_charonform2', 'skeletaltyphon',
    'xhero_helike_controller_lildudes',
    'qs_minotaurconqueror', 'ghosthero', 'eldercyclops',
    'elderminotaur', 'elderminotaurlord',
    'typhon_chains', 'thetrap',
}

SKIP_COMMON_VARIANTS = {
    'hydradon_scorcher', 'hydradon_blacktongue',
    'stygianhydradon_scorcher', 'stygianhydradon_blacktongue',
    'monstrous_hydradon_scorcher', 'monstrous_hydradon_blacktongue',
    'hellgore',
    'egypt_bm_soldier', 'egypt_bm_mummycaptainspawn',
    'greece_bm_captain', 'orient_bm_captain', 'orient_bm_soldier',
    'savage_bm_marauder', 'savage_bm_soldier',
    'iceheart_bm_snapper', 'elder_um_boarmonstrous',
    'orient_um_shadowstalker', 'greece_um_tombrot',
    'creepingslime', 'repugnantdecay',
    'bm_shadowskeleton_warrior', 'murklord_babylon',
    'xsq17_uw_am_scavenger', 'xsq17_uw_as_witch',
    'as_witchqueen', 'elysium_ss_siegestrider',
    'z_toxeus', 'old_z_toxeus',
    'prox',
}


def analyze_skill_damage(db, skill_path):
    """Analyze a skill record to determine its damage types."""
    if not db.has_record(skill_path):
        return {}

    elements = {}
    fields = db.get_fields(skill_path)
    if not fields:
        return {}

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
                    sub_elems = analyze_skill_damage(db, v)
                    for elem, val in sub_elems.items():
                        elements[elem] = elements.get(elem, 0) + val

    return elements


def infer_element_from_data(db, skill_paths, skill_names, desc, monster_name):
    """Determine element from actual skill data first, then keywords as fallback."""
    all_elements = {}
    for sp in skill_paths:
        elems = analyze_skill_damage(db, sp)
        for elem, val in elems.items():
            all_elements[elem] = all_elements.get(elem, 0) + val

    if all_elements:
        primary = max(all_elements, key=all_elements.get)
        if all_elements[primary] > 0:
            return primary, all_elements

    text = ' '.join(skill_names + [desc, monster_name]).lower()

    KEYWORD_MAP = [
        ('fire', ['firebreath', 'fireball', 'flamestrike', 'flame', 'flamethrower',
                   'pillarofflame', 'eruption', 'meteor', 'lava', 'magma', 'volcanic',
                   'inferno', 'blaze', 'pyro', 'burn', 'combustion', 'fire']),
        ('cold', ['freezingbreath', 'frostbreath', 'iceshard', 'frostball', 'blizzard',
                   'frost', 'frozen', 'ice', 'cold', 'arctic', 'chill', 'frostbite',
                   'frostslow', 'iceball', 'heartoffrost', 'glacial']),
        ('lightning', ['lightningbreath', 'lightningbolt', 'thunderball', 'lightningSurge',
                       'stormorb', 'chainlightning', 'lightning', 'thunder', 'storm',
                       'electric', 'shock', 'bolt', 'static', 'tempest', 'blitz',
                       'enchantment_lightning', 'stormnimbus']),
        ('poison', ['venombolt', 'poisonsurge', 'poisonshot', 'venomnova', 'toxicbite',
                     'causticSputum', 'poisongasball', 'envenom', 'poison', 'venom',
                     'toxic', 'plague', 'disease', 'acid', 'blight', 'corruption', 'decay']),
        ('life', ['spiritbolt', 'deathnova', 'deathchill', 'consumelife', 'bloodburst',
                   'bloodboil', 'spectralblast', 'necrosis', 'undead', 'soul', 'spirit',
                   'death', 'necrotic', 'drain', 'wraith', 'ghost', 'liche', 'vitality',
                   'shadow']),
    ]

    best_elem = 'physical'
    best_score = 0
    for elem, keywords in KEYWORD_MAP:
        score = 0
        for kw in keywords:
            if kw in text:
                score += (3 if len(kw) > 5 else 2)
        if score > best_score:
            best_score = score
            best_elem = elem

    return best_elem, all_elements


def infer_role(skill_names, desc, monster_name, monster_dir):
    """Determine combat role from skills, description, and monster type."""
    text = ' '.join(skill_names + [desc, monster_name]).lower()
    desc_lower = desc.lower() if desc else ''

    melee_types = ['cyclops', 'minotaur', 'gigantes', 'odontotyrranus',
                   'bonescourge', 'limos', 'archlimos']
    if any(mt in monster_dir.lower() or mt in monster_name.lower() for mt in melee_types):
        if 'staff' not in desc_lower and 'caster' not in desc_lower:
            return 'melee'

    if 'bow' in desc_lower or 'archer' in desc_lower:
        return 'caster'
    if 'staff' in desc_lower or 'caster' in desc_lower:
        return 'caster'

    if any(w in text for w in ['summon', 'spawn', 'minion', 'pet', 'summonskeleton']):
        has_combat = any(w in text for w in ['melee', 'attack', 'strike', 'onslaught', 'charge'])
        if not has_combat:
            return 'summoner'

    ranged_skills = ['projectile', 'bolt', 'fireball', 'lightningbolt', 'iceshard',
                     'spiritbolt', 'rangedblast', 'frostball', 'stormorb', 'venombolt']
    if any(w in text for w in ranged_skills):
        return 'caster'

    if any(w in text for w in ['charge', 'onslaught', 'strike', 'cleave', 'dualweapon',
                                'bash', 'smash', 'stomp', 'clubslam']):
        return 'melee'

    if any(w in text for w in ['aura', 'reflection', 'shield', 'defense', 'passive',
                                'stoneform', 'colossusform']):
        return 'tank'

    return 'melee'


def _infer_data_type(value):
    """Map Python types to TQ data types."""
    if isinstance(value, str):
        return DATA_TYPE_STRING
    if isinstance(value, float):
        return DATA_TYPE_FLOAT
    return DATA_TYPE_INT


def _base_soul_fields(level):
    """Common boilerplate fields shared by all souls."""
    fields = {}
    fields['templateName'] = (DATA_TYPE_STRING, SOUL_TEMPLATE)
    fields['Class'] = (DATA_TYPE_STRING, SOUL_CLASS)
    fields['bitmap'] = (DATA_TYPE_STRING, SOUL_BITMAP)
    fields['mesh'] = (DATA_TYPE_STRING, SOUL_MESH)
    fields['itemCostName'] = (DATA_TYPE_STRING, SOUL_COST)
    fields['dropSound'] = (DATA_TYPE_STRING, SOUL_DROP_SOUND)
    fields['dropSound3D'] = (DATA_TYPE_STRING, SOUL_DROP_3D)
    fields['dropSoundWater'] = (DATA_TYPE_STRING, SOUL_DROP_WATER)
    fields['itemClassification'] = (DATA_TYPE_STRING, 'Magical')
    fields['characterBaseAttackSpeedTag'] = (DATA_TYPE_STRING, 'CharacterAttackSpeedAverage')
    fields['castsShadows'] = (DATA_TYPE_INT, 1)
    fields['maxTransparency'] = (DATA_TYPE_FLOAT, 0.5)
    fields['scale'] = (DATA_TYPE_FLOAT, 1.0)
    fields['shadowBias'] = (DATA_TYPE_FLOAT, 0.01)
    fields['cannotPickUp'] = (DATA_TYPE_INT, 0)
    fields['cannotPickUpMultiple'] = (DATA_TYPE_INT, 0)
    fields['hidePrefixName'] = (DATA_TYPE_INT, 0)
    fields['hideSuffixName'] = (DATA_TYPE_INT, 0)
    fields['quest'] = (DATA_TYPE_INT, 0)
    item_level = max(1, min(level, 80))
    fields['itemLevel'] = (DATA_TYPE_INT, item_level)
    fields['strengthRequirement'] = (DATA_TYPE_INT, 0)
    fields['intelligenceRequirement'] = (DATA_TYPE_INT, 0)
    fields['dexterityRequirement'] = (DATA_TYPE_INT, 0)
    fields['levelRequirement'] = (DATA_TYPE_INT, max(1, item_level - 5))
    fields['numRelicSlots'] = (DATA_TYPE_INT, 1)
    return fields


def design_soul(level, element, role, clean_name=''):
    """Design soul stats. Uses explicit hand-crafted designs from SOUL_DESIGNS
    when available, falling back to generic stats for unknown monsters."""
    fields = _base_soul_fields(level)

    if clean_name in SOUL_DESIGNS:
        for field_name, value in SOUL_DESIGNS[clean_name].items():
            fields[field_name] = (_infer_data_type(value), value)
        return fields

    power = max(1.0, level / 10.0)

    if role == 'melee':
        fields['characterStrength'] = (DATA_TYPE_INT, int(5 * power))
        fields['characterLife'] = (DATA_TYPE_INT, int(30 * power))
        fields['characterLifeRegen'] = (DATA_TYPE_FLOAT, round(1.0 * power, 1))
        fields['offensivePhysicalMin'] = (DATA_TYPE_FLOAT, round(3 * power, 1))
        fields['offensivePhysicalMax'] = (DATA_TYPE_FLOAT, round(8 * power, 1))
        fields['characterAttackSpeedModifier'] = (DATA_TYPE_INT, int(3 * min(power, 5)))
    elif role == 'caster':
        fields['characterIntelligence'] = (DATA_TYPE_INT, int(5 * power))
        fields['characterMana'] = (DATA_TYPE_INT, int(30 * power))
        fields['characterManaRegenModifier'] = (DATA_TYPE_INT, int(5 * min(power, 8)))
        fields['characterSpellCastSpeedModifier'] = (DATA_TYPE_INT, int(3 * min(power, 6)))
    elif role == 'summoner':
        fields['characterLife'] = (DATA_TYPE_INT, int(20 * power))
        fields['characterMana'] = (DATA_TYPE_INT, int(20 * power))
        fields['characterLifeRegen'] = (DATA_TYPE_FLOAT, round(0.5 * power, 1))
        fields['characterManaRegenModifier'] = (DATA_TYPE_INT, int(3 * min(power, 6)))
    elif role == 'tank':
        fields['characterStrength'] = (DATA_TYPE_INT, int(3 * power))
        fields['characterLife'] = (DATA_TYPE_INT, int(50 * power))
        fields['characterLifeRegen'] = (DATA_TYPE_FLOAT, round(2.0 * power, 1))
        fields['defensiveProtection'] = (DATA_TYPE_INT, int(5 * power))

    if element == 'fire':
        fields['offensiveFireMin'] = (DATA_TYPE_FLOAT, round(4 * power, 1))
        fields['offensiveFireMax'] = (DATA_TYPE_FLOAT, round(10 * power, 1))
        fields['offensiveFireModifier'] = (DATA_TYPE_INT, int(5 * min(power, 6)))
        fields['defensiveFire'] = (DATA_TYPE_INT, int(5 * min(power, 10)))
        fields['defensiveCold'] = (DATA_TYPE_INT, int(-3 * min(power, 5)))
    elif element == 'cold':
        fields['offensiveColdMin'] = (DATA_TYPE_FLOAT, round(4 * power, 1))
        fields['offensiveColdMax'] = (DATA_TYPE_FLOAT, round(10 * power, 1))
        fields['offensiveColdModifier'] = (DATA_TYPE_INT, int(5 * min(power, 6)))
        fields['defensiveCold'] = (DATA_TYPE_INT, int(5 * min(power, 10)))
        fields['defensiveFire'] = (DATA_TYPE_INT, int(-3 * min(power, 5)))
    elif element == 'lightning':
        fields['offensiveLightningMin'] = (DATA_TYPE_FLOAT, round(3 * power, 1))
        fields['offensiveLightningMax'] = (DATA_TYPE_FLOAT, round(12 * power, 1))
        fields['offensiveLightningModifier'] = (DATA_TYPE_INT, int(5 * min(power, 6)))
        fields['defensiveLightning'] = (DATA_TYPE_INT, int(5 * min(power, 10)))
    elif element == 'poison':
        fields['offensiveSlowPoisonMin'] = (DATA_TYPE_FLOAT, round(5 * power, 1))
        fields['offensiveSlowPoisonMax'] = (DATA_TYPE_FLOAT, round(12 * power, 1))
        fields['offensiveSlowPoisonDurationMin'] = (DATA_TYPE_FLOAT, 3.0)
        fields['offensiveSlowPoisonModifier'] = (DATA_TYPE_INT, int(5 * min(power, 6)))
        fields['defensivePoison'] = (DATA_TYPE_INT, int(5 * min(power, 10)))
    elif element == 'life':
        fields['offensiveLifeMin'] = (DATA_TYPE_FLOAT, round(3 * power, 1))
        fields['offensiveLifeMax'] = (DATA_TYPE_FLOAT, round(8 * power, 1))
        fields['offensiveLifeModifier'] = (DATA_TYPE_INT, int(5 * min(power, 6)))
        fields['defensiveLife'] = (DATA_TYPE_INT, int(5 * min(power, 10)))
        fields['characterLifeRegen'] = (DATA_TYPE_FLOAT, round(1.5 * power, 1))
    else:
        fields['offensivePhysicalMin'] = (DATA_TYPE_FLOAT, round(5 * power, 1))
        fields['offensivePhysicalMax'] = (DATA_TYPE_FLOAT, round(12 * power, 1))
        fields['offensivePhysicalModifier'] = (DATA_TYPE_INT, int(5 * min(power, 6)))

    return fields


def make_display_name(clean_name):
    """Convert clean_name to a human-readable display name."""
    name = clean_name
    for prefix in ['boss_', 'xhero_', 'xsecrethero_', 'hero_', 'uber_',
                    'named_', 'qm_', 'u_', 'um_', 'uw_', 'ur_', 'us_',
                    'xsq01_am_', 'xsq07_', 'xsq11_', 'xsq12_', 'xsq13_',
                    'xsq14_', 'xsq15_', 'xsq17_', 'xsq18_', 'xsq19_',
                    'xsq24_', 'xsq27_',
                    'namedhero_', 'namedcaptain', 'namedfrost', 'namedpyro',
                    'namedsoul', 'namedvenom', 'named']:
        if name.lower().startswith(prefix):
            name = name[len(prefix):]

    for suffix in ['_controller_lildudes']:
        if name.lower().endswith(suffix):
            name = name[:-len(suffix)]

    parts = re.findall(r"[A-Z][a-z']+|[a-z']+|[A-Z]+", name)
    if not parts:
        parts = [name]
    return ' '.join(p.capitalize() for p in parts)


FORCE_INCLUDE = {
    'frost',
}

MANUAL_OVERRIDES = {
    'frost':                     ('cold', 'melee'),
    'boss_sandwraithlord':       ('physical', 'caster'),
    'boss_cyclops_polyphemus':   ('physical', 'melee'),
    'boss_gorgon_sstheno':       ('poison', 'melee'),
    'boss_gorgon_euryale':       ('cold', 'caster'),
    'boss_gorgon_medusa':        ('fire', 'caster'),
    'boss_dragonliche':          ('cold', 'caster'),
    'boss_manticore':            ('lightning', 'melee'),
    'boss_scarabaeus':           ('physical', 'melee'),
    'boss_scorposking':          ('poison', 'melee'),
    'boss_chimaera':             ('fire', 'melee'),
    'boss_hydra':                ('fire', 'melee'),
    'boss_titan_typhon':         ('fire', 'caster'),
    'boss_talos':                ('fire', 'melee'),
    'boss_xiao':                 ('lightning', 'melee'),
    'boss_minotaurlord':         ('physical', 'melee'),
    'boss_spartacentaur':        ('physical', 'melee'),
    'boss_necromancer_alastor':  ('life', 'caster'),
    'boss_gargantuanyeti':       ('cold', 'melee'),
    'boss_neanderthalchief_barmanu': ('cold', 'melee'),
    'boss_daemonbull_yaoguai':   ('fire', 'melee'),
    'boss_egypttelkine_aktaios': ('fire', 'caster'),
    'boss_deino':                ('lightning', 'caster'),
    'boss_enyo':                 ('lightning', 'caster'),
    'boss_pemphredo':            ('lightning', 'caster'),
    'boss_charon':               ('fire', 'caster'),
    'boss_skeletaltyphon':       ('physical', 'melee'),
    'boss_satyrshaman':          ('fire', 'caster'),
    'boss_spiderqueen_arachne':  ('poison', 'melee'),
    'hero_hanifthecruel':        ('lightning', 'tank'),
    'hero_reshef':               ('life', 'melee'),
    'hero_thetombkeeper':        ('fire', 'summoner'),
    'hero_sandqueenmasika':      ('physical', 'melee'),
    'hero_miaomiao':             ('lightning', 'caster'),
    'hero_shaohsin':             ('lightning', 'caster'),
    'ubericeraptor':             ('cold', 'melee'),
    'eldercyclops':              ('physical', 'melee'),
    'elderminotaurlord':         ('physical', 'melee'),
    'elderminotaur':             ('physical', 'melee'),
    'trachius':                  ('physical', 'melee'),
    'conqueror':                 ('physical', 'melee'),
    'juggernaught':              ('physical', 'melee'),
    'groundbreaker':             ('physical', 'melee'),
    'ghosthero':                 ('life', 'caster'),
    'stonhide':                  ('physical', 'tank'),
    'shadowhero':                ('life', 'caster'),
    'spiderblackwidow':          ('poison', 'melee'),
    'uber':                      ('cold', 'melee'),
    'ur_uber':                   ('lightning', 'caster'),
    'us_hero':                   ('poison', 'caster'),
    'frostmagi':                 ('cold', 'caster'),
    'assassin':                  ('poison', 'melee'),
    'qs_minotaurconqueror':      ('physical', 'melee'),
}


def create_uber_souls(db: ArzDatabase):
    """Identify uber monsters without souls and create thematic ones."""
    print("\n=== Creating uber monster souls ===")

    boss_indicators = [
        'boss', 'hero', 'uber', 'named', 'quest',
        'um_',
        'typhon', 'hades', 'hydra', 'chimera', 'cyclops',
        'minotaur', 'talos', 'manticore', 'scarabaeus',
        'megalesios', 'aktaios', 'alastor', 'arachne',
        'nessus', 'ormenos', 'cerberus', 'medusa',
        'sstheno', 'euryale', 'polyphemus', 'yaoguai',
        'barmanu', 'bandari', 'dragonliche', 'pharaoh',
        'sandwraithlord', 'scorposking', 'nehebkau',
        'gorgonqueen', 'toxeus', 'telkine',
    ]

    existing_souls = set()
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            if 'svc_uber' not in nl:
                existing_souls.add(nl)

    # Pre-scan: collect all clean names where ANY variant already has a soul ref.
    # This prevents creating duplicate souls when monster has multiple records
    # and only some of them have lootFinger2Item1 set.
    names_with_souls = set()
    for name in db.record_names():
        nl = name.lower()
        if '\\creature\\' not in nl and '/creature/' not in nl and \
           '\\creatures\\' not in nl and '/creatures/' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'lootFinger2Item1' and tf.values:
                v = tf.values[0]
                if isinstance(v, str) and v and 'soul' in v.lower():
                    parts = nl.replace('\\', '/').split('/')
                    filename = parts[-1].replace('.dbr', '')
                    clean = re.sub(r'^(u_|um_|uw_|qm_|bm_|cb_|am_|ar_|as_|em_|vampiric_)', '', filename)
                    clean = re.sub(r'_?\d+$', '', clean).strip('_')
                    names_with_souls.add(clean)
                    break
    print(f"  Pre-scan: {len(names_with_souls)} monster types already have soul refs")

    tag_counter = 9000
    text_tags = []
    created_souls = []
    seen_names = set()
    skipped = []

    for name in db.record_names():
        nl = name.lower()
        if '\\creature\\' not in nl and '/creature/' not in nl and \
           '\\creatures\\' not in nl and '/creatures/' not in nl:
            continue

        if any(skip in nl for skip in SKIP_NAMES):
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

        if clean in SKIP_EXACT or clean in SKIP_COMMON_VARIANTS:
            skipped.append(f"  [exact skip] {clean}")
            continue

        if '(' in clean:
            skipped.append(f"  [conflict copy] {clean}")
            continue

        if level <= 1 and len(skills_paths) <= 1:
            skipped.append(f"  [lvl {level}, no skills] {clean}")
            continue

        is_common_mob = classification in ('Common', 'Champion', '') and \
            not any(kw in clean.lower() for kw in ['boss', 'hero', 'uber', 'named', 'elder',
                                                     'queen', 'king', 'lord', 'chief', 'general'])
        if is_common_mob and 'um_' not in filename.lower():
            has_boss_keyword = any(kw in clean.lower() for kw in boss_indicators)
            if not has_boss_keyword:
                skipped.append(f"  [common/champion variant] {clean} ({classification})")
                continue

        if clean in seen_names:
            continue

        # Skip if ANY variant of this monster already has a soul reference
        if clean in names_with_souls:
            continue

        # Also check soul record paths by name substring
        if clean not in FORCE_INCLUDE:
            has_matching_soul = False
            for sp in existing_souls:
                if clean in sp and len(clean) >= 4:
                    has_matching_soul = True
                    break
            if has_matching_soul:
                continue

        seen_names.add(clean)

        if clean in MANUAL_OVERRIDES:
            element, role = MANUAL_OVERRIDES[clean]
            all_elements = {}
        else:
            element, all_elements = infer_element_from_data(db, skills_paths, skills_names, desc, clean)
            role = infer_role(skills_names, desc, clean, monster_dir)

        display_name = make_display_name(clean)
        soul_fields = design_soul(level, element, role, clean)

        tag_name = f'tagSoulSVC{tag_counter}'
        soul_fields['itemNameTag'] = (DATA_TYPE_STRING, tag_name)
        soul_fields['FileDescription'] = (DATA_TYPE_STRING, f'{display_name} Soul')

        text_tags.append((tag_name, '{^F}' + f'{display_name} Soul'))
        tag_counter += 1

        # Scale stats by difficulty: N=60%, E=80%, L=100%
        _DIFF_SCALE = {'n': 0.6, 'e': 0.8, 'l': 1.0}
        # Fields that should NOT be scaled (identity, skills, strings, booleans)
        _NO_SCALE = {
            'templateName', 'Class', 'bitmap', 'mesh', 'itemCostName',
            'dropSound', 'dropSound3D', 'dropSoundWater',
            'itemClassification', 'characterBaseAttackSpeedTag',
            'itemNameTag', 'FileDescription',
            'itemSkillName', 'itemSkillAutoController',
            'augmentSkillName1', 'augmentSkillName2',
            'castsShadows', 'cannotPickUp', 'cannotPickUpMultiple',
            'hidePrefixName', 'hideSuffixName', 'quest', 'numRelicSlots',
        }

        for diff in ('n', 'e', 'l'):
            soul_path = f'records\\item\\equipmentring\\soul\\svc_uber\\{clean}_soul_{diff}.dbr'
            scale = _DIFF_SCALE[diff]

            typed_fields = {}
            for k, (dtype, val) in soul_fields.items():
                if k in _NO_SCALE or dtype == DATA_TYPE_STRING:
                    typed_fields[k] = TypedField(dtype, [val])
                elif k == 'itemLevel':
                    scaled_lv = max(1, int(val * scale))
                    typed_fields[k] = TypedField(dtype, [scaled_lv])
                elif k == 'levelRequirement':
                    base_lv = soul_fields.get('itemLevel', (DATA_TYPE_INT, 1))[1]
                    scaled_lv = max(1, int(base_lv * scale))
                    typed_fields[k] = TypedField(dtype, [max(1, scaled_lv - 5)])
                elif dtype == DATA_TYPE_INT:
                    typed_fields[k] = TypedField(dtype, [max(0, int(val * scale))] if val >= 0 else [int(val * scale)])
                elif dtype == DATA_TYPE_FLOAT:
                    typed_fields[k] = TypedField(dtype, [round(val * scale, 1)])
                else:
                    typed_fields[k] = TypedField(dtype, [val])

            db.ensure_string(soul_path)
            db._raw_records[soul_path] = (db.ensure_string(soul_path), b'')
            db._record_types[soul_path] = SOUL_TEMPLATE
            db._record_timestamps[soul_path] = 0
            db._decoded_cache[soul_path] = typed_fields
            db._modified.add(soul_path)

        soul_n = f'records\\item\\equipmentring\\soul\\svc_uber\\{clean}_soul_n.dbr'
        soul_e = f'records\\item\\equipmentring\\soul\\svc_uber\\{clean}_soul_e.dbr'
        soul_l = f'records\\item\\equipmentring\\soul\\svc_uber\\{clean}_soul_l.dbr'
        db.set_field(name, 'lootFinger2Item1', [soul_n, soul_e, soul_l], DATA_TYPE_STRING)
        db.set_field(name, 'chanceToEquipFinger2', 66.0, DATA_TYPE_FLOAT)
        db.set_field(name, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
        db.set_field(name, 'dropItems', 1, DATA_TYPE_INT)

        created_souls.append({
            'monster': name,
            'clean_name': clean,
            'display_name': display_name,
            'level': level,
            'element': element,
            'role': role,
            'skills': skills_names[:3],
            'tag': tag_name,
        })

    print(f"  Uber souls created: {len(created_souls)}")
    print(f"  Soul records added: {len(created_souls) * 3} (n/e/l variants)")
    if skipped:
        print(f"  Skipped {len(skipped)} non-monster/garbage records")
    return created_souls, text_tags


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: create_uber_souls.py <input.arz> <output.arz>")
        sys.exit(1)

    db = ArzDatabase.from_arz(Path(sys.argv[1]))
    souls, tags = create_uber_souls(db)

    report_path = Path(sys.argv[2]).parent / 'uber_souls_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# SoulvizierClassic - New Uber Monster Souls\n\n")
        f.write(f"Total new souls: {len(souls)}\n\n")
        f.write("| Monster | Display Name | Level | Element | Role | Skills | Tag |\n")
        f.write("|---------|-------------|-------|---------|------|--------|-----|\n")
        for s in sorted(souls, key=lambda x: x['level']):
            sk = ', '.join(s['skills'][:3]) if s['skills'] else '-'
            f.write(f"| {s['clean_name']} | {s['display_name']} | {s['level']} | {s['element']} | {s['role']} | {sk} | {s['tag']} |\n")

    tags_path = Path(sys.argv[2]).parent / 'uber_soul_tags.txt'
    with open(tags_path, 'w', encoding='utf-8') as f:
        for tag, value in tags:
            f.write(f"{tag}={value}\n")

    print(f"\n  Report: {report_path}")
    print(f"  Tags: {tags_path}")

    db.write_arz(Path(sys.argv[2]))
    print("Done.")
