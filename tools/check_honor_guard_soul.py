"""
Analyze Pharaoh's Honor Guard soul rings: drop rates, full stats, comparisons.
"""
import sys, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase, DATA_TYPE_INT, DATA_TYPE_FLOAT, DATA_TYPE_STRING, DATA_TYPE_BOOL

DTYPE_NAMES = {DATA_TYPE_INT: "INT", DATA_TYPE_FLOAT: "FLOAT", DATA_TYPE_STRING: "STRING", DATA_TYPE_BOOL: "BOOL"}

DB_PATH = Path(__file__).parent.parent / "work/SoulvizierClassic/Database/SoulvizierClassic.arz"

# Field categories for grouping
IDENTITY_FIELDS = {
    'Class', 'templateName', 'FileDescription', 'description', 'itemText',
    'bitmap', 'ShardBitmap', 'itemNameTag', 'itemQualityTag', 'itemStyleTag',
    'itemClassification', 'levelRequirement', 'itemLevel', 'dropSound',
    'dropSoundMaxDistance', 'dropSoundReverbMix', 'mesh', 'baseTexture',
    'bumpTexture', 'glowTexture', 'shader', 'shaderParams',
    'actorHeight', 'actorRadius', 'scale', 'objectManipulatorType',
}

OFFENSIVE_FIELDS_PATTERNS = [
    'offensiv', 'Offensive', 'damage', 'Damage', 'attack', 'Attack',
    'retaliati', 'Retaliati', 'pierce', 'Pierce',
]

DEFENSIVE_FIELDS_PATTERNS = [
    'defensiv', 'Defensive', 'armor', 'Armor', 'resist', 'Resist',
    'absorb', 'Absorb', 'block', 'Block', 'protection', 'Protection',
    'damageAbsorption', 'projectileAvoidance',
]

CHAR_STAT_PATTERNS = [
    'character', 'Character', 'Strength', 'strength', 'Intelligence', 'intelligence',
    'Dexterity', 'dexterity', 'Life', 'life', 'Mana', 'mana', 'Speed', 'speed',
    'health', 'Health', 'energy', 'Energy', 'totalSpeed', 'runSpeed',
    'castSpeed', 'attackSpeed', 'spellCooldown', 'refreshTime',
    'experienceModifier', 'requirements',
]

SKILL_PATTERNS = [
    'skill', 'Skill', 'augmentSkill', 'augmentMastery', 'petBonus',
    'augmentAllLevel',
]

def categorize_field(name):
    base = name.split('###')[0]
    if base in IDENTITY_FIELDS:
        return 'IDENTITY'
    for p in SKILL_PATTERNS:
        if p in base:
            return 'SKILL / AUGMENT'
    for p in OFFENSIVE_FIELDS_PATTERNS:
        if p in base:
            return 'OFFENSIVE'
    for p in DEFENSIVE_FIELDS_PATTERNS:
        if p in base:
            return 'DEFENSIVE'
    for p in CHAR_STAT_PATTERNS:
        if p in base:
            return 'CHARACTER STATS'
    return 'OTHER'

def is_nonzero(tf):
    """Check if a TypedField has meaningful (non-zero/non-empty) values."""
    for v in tf.values:
        if isinstance(v, str):
            if v and v != '0':
                return True
        elif isinstance(v, float):
            if abs(v) > 1e-9:
                return True
        elif v != 0:
            return True
    return False

def format_values(tf):
    dtype_name = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
    if len(tf.values) == 1:
        return f"[{dtype_name}] {tf.values[0]}"
    return f"[{dtype_name}] {tf.values}"

def dump_soul_fields(db, record_path, label):
    """Dump all non-zero fields of a soul ring, grouped by category."""
    fields = db.get_fields(record_path)
    if fields is None:
        print(f"\n  *** RECORD NOT FOUND: {record_path} ***")
        return {}

    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"  Record: {record_path}")
    print(f"{'='*80}")

    categorized = {}
    all_fields = {}
    for key, tf in fields.items():
        if not is_nonzero(tf):
            continue
        base_name = key.split('###')[0]
        cat = categorize_field(key)
        categorized.setdefault(cat, []).append((base_name, tf))
        all_fields[base_name] = tf

    cat_order = ['IDENTITY', 'CHARACTER STATS', 'OFFENSIVE', 'DEFENSIVE', 'SKILL / AUGMENT', 'OTHER']
    for cat in cat_order:
        if cat not in categorized:
            continue
        print(f"\n  --- {cat} ---")
        for name, tf in categorized[cat]:
            print(f"    {name:45s} {format_values(tf)}")

    return all_fields


def main():
    print(f"Loading database: {DB_PATH}")
    db = ArzDatabase.from_arz(DB_PATH)
    all_names = db.record_names()

    # =========================================================================
    # PART 1: Find boss records matching boss_pharaohshonorguard*
    # =========================================================================
    print("\n" + "#"*80)
    print("#  PART 1: Boss records — Pharaoh's Honor Guard drop rates")
    print("#"*80)

    boss_records = [n for n in all_names if 'boss_pharaohshonorguard' in n.lower()]
    boss_records.sort()

    print(f"\nFound {len(boss_records)} boss records matching 'boss_pharaohshonorguard':")

    for rec in boss_records:
        fields = db.get_fields(rec)
        if fields is None:
            continue

        chance = None
        weight = None
        loot = None

        for key, tf in fields.items():
            base = key.split('###')[0]
            if base == 'chanceToEquipFinger2':
                chance = tf
            elif base == 'chanceToEquipFinger2Item1':
                weight = tf
            elif base == 'lootFinger2Item1':
                loot = tf

        print(f"\n  Record: {rec}")
        print(f"    chanceToEquipFinger2       = {format_values(chance) if chance else 'NOT SET'}")
        print(f"    chanceToEquipFinger2Item1   = {format_values(weight) if weight else 'NOT SET'}")
        print(f"    lootFinger2Item1            = {format_values(loot) if loot else 'NOT SET'}")

    # =========================================================================
    # PART 2: Dump all three soul ring records
    # =========================================================================
    print("\n\n" + "#"*80)
    print("#  PART 2: Full stats of Pharaoh's Honor Guard soul rings")
    print("#"*80)

    soul_paths = [
        ("Normal (N)", "records\\item\\equipmentring\\soul\\pharaohshonorguard\\pharaohshonorguard_soul_n.dbr"),
        ("Epic (E)",   "records\\item\\equipmentring\\soul\\pharaohshonorguard\\pharaohshonorguard_soul_e.dbr"),
        ("Legendary (L)", "records\\item\\equipmentring\\soul\\pharaohshonorguard\\pharaohshonorguard_soul_l.dbr"),
    ]

    honor_guard_fields = {}
    for label, path in soul_paths:
        hf = dump_soul_fields(db, path, f"Pharaoh's Honor Guard — {label}")
        honor_guard_fields[label] = hf

    # =========================================================================
    # PART 3: Find tanky boss souls for comparison
    # =========================================================================
    print("\n\n" + "#"*80)
    print("#  PART 3: Comparison with other tanky boss souls")
    print("#"*80)

    # Find all soul ring records
    soul_records = [n for n in all_names
                    if 'equipmentring' in n.lower()
                    and 'soul' in n.lower()
                    and n.lower().endswith('.dbr')
                    and '_l.dbr' in n.lower()]  # legendary only for comparison

    print(f"\nScanning {len(soul_records)} legendary soul records for tanky stats...")

    tanky_candidates = []
    for rec in soul_records:
        fields = db.get_fields(rec)
        if fields is None:
            continue

        tanky_score = 0
        has_armor = False
        has_phys_resist = False
        has_absorb = False
        stats_summary = {}

        for key, tf in fields.items():
            base = key.split('###')[0]
            if not is_nonzero(tf):
                continue

            # Check for armor
            if 'armor' in base.lower() and 'modifier' in base.lower():
                has_armor = True
                tanky_score += 2
                stats_summary['armor'] = tf.values

            # Check for physical resistance
            if 'physic' in base.lower() and 'resist' in base.lower():
                has_phys_resist = True
                tanky_score += 3
                stats_summary['phys_resist'] = tf.values

            # Check for damage absorption
            if 'damageabsorption' in base.lower() or 'absorb' in base.lower():
                has_absorb = True
                tanky_score += 3
                stats_summary['absorb'] = tf.values

            # Defensive stats
            if 'defensiv' in base.lower():
                tanky_score += 1
                stats_summary[base] = tf.values

            # Health/life
            if ('life' in base.lower() or 'health' in base.lower()) and 'modifier' in base.lower():
                tanky_score += 1
                stats_summary[base] = tf.values

            # Resistances
            if 'resist' in base.lower() and is_nonzero(tf):
                tanky_score += 1

        if tanky_score >= 3:
            tanky_candidates.append((rec, tanky_score, stats_summary))

    # Sort by tanky score descending
    tanky_candidates.sort(key=lambda x: -x[1])

    # Pick top 3 that are NOT pharaoh's honor guard
    comparison_souls = []
    for rec, score, summary in tanky_candidates:
        if 'pharaohshonorguard' in rec.lower():
            continue
        comparison_souls.append((rec, score, summary))
        if len(comparison_souls) >= 3:
            break

    print(f"\nTop {len(comparison_souls)} tanky legendary souls for comparison:")
    for rec, score, summary in comparison_souls:
        print(f"\n  {rec} (tanky_score={score})")
        for k, v in summary.items():
            print(f"    {k}: {v}")

    # Dump full stats of comparison souls
    for rec, score, _ in comparison_souls:
        # Extract a readable name from the path
        name = rec.split('\\')[-1].replace('.dbr', '').replace('_soul_l', '')
        dump_soul_fields(db, rec, f"COMPARISON: {name} (Legendary) — tanky_score={score}")

    # =========================================================================
    # PART 4: What does characterTotalSpeedModifier: -15.0 mean?
    # =========================================================================
    print("\n\n" + "#"*80)
    print("#  PART 4: characterTotalSpeedModifier analysis — negative values")
    print("#"*80)

    # First check if the honor guard soul has this field
    print("\nChecking Pharaoh's Honor Guard souls for characterTotalSpeedModifier:")
    for label, path in soul_paths:
        val = db.get_field_value(path, 'characterTotalSpeedModifier')
        print(f"  {label}: characterTotalSpeedModifier = {val}")

    # Find other souls with negative speed modifiers
    print("\nSearching ALL soul ring records for negative characterTotalSpeedModifier...")
    negative_speed_souls = []

    all_soul_records = [n for n in all_names
                        if 'equipmentring' in n.lower()
                        and 'soul' in n.lower()
                        and n.lower().endswith('.dbr')]

    for rec in all_soul_records:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in fields.items():
            base = key.split('###')[0]
            if base == 'characterTotalSpeedModifier' and is_nonzero(tf):
                for v in tf.values:
                    if isinstance(v, (int, float)) and v < 0:
                        negative_speed_souls.append((rec, v))
                        break

    print(f"\nFound {len(negative_speed_souls)} soul records with NEGATIVE characterTotalSpeedModifier:")
    for rec, val in sorted(negative_speed_souls, key=lambda x: x[1]):
        print(f"  {val:+8.1f}%  {rec}")

    # Also show souls with POSITIVE speed modifiers for context
    positive_speed_souls = []
    for rec in all_soul_records:
        fields = db.get_fields(rec)
        if fields is None:
            continue
        for key, tf in fields.items():
            base = key.split('###')[0]
            if base == 'characterTotalSpeedModifier' and is_nonzero(tf):
                for v in tf.values:
                    if isinstance(v, (int, float)) and v > 0:
                        positive_speed_souls.append((rec, v))
                        break

    print(f"\nFor comparison, {len(positive_speed_souls)} souls with POSITIVE characterTotalSpeedModifier:")
    for rec, val in sorted(positive_speed_souls, key=lambda x: -x[1])[:10]:
        print(f"  {val:+8.1f}%  {rec}")

    print("\n" + "="*80)
    print("INTERPRETATION OF characterTotalSpeedModifier:")
    print("="*80)
    print("""
  characterTotalSpeedModifier affects ALL speed types (run, attack, cast) simultaneously.
  A value of -15.0 means: -15% to total speed (run speed, attack speed, cast speed).

  This IS a DEBUFF on the player wearing the soul ring.

  In Titan Quest, 'Total Speed' modifies all speed categories at once. A negative value
  is a significant penalty — the player moves, attacks, and casts 15% slower.

  This is likely a trade-off for the defensive stats the soul provides. Tanky souls
  often come with speed penalties to balance their defensive power.
""")

    # Check what other speed-related fields the honor guard souls have
    print("Other speed-related fields on Pharaoh's Honor Guard souls:")
    for label, path in soul_paths:
        fields = db.get_fields(path)
        if fields is None:
            continue
        print(f"\n  {label}:")
        for key, tf in fields.items():
            base = key.split('###')[0]
            if 'speed' in base.lower() and is_nonzero(tf):
                print(f"    {base:45s} {format_values(tf)}")


if __name__ == '__main__':
    main()
