"""
Find Normal and Epic tier equivalents for pet equipment items.

Searches the SoulvizierClassic database for thematically matching items
at each difficulty tier for two pets:
  - Rakanizeus (warrior satyr): physical/STR/OA theme
  - Boneash (fire skeleton caster): fire/INT/cast speed theme
"""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

DB_PATH = Path(__file__).parent.parent / "work/SoulvizierClassic/Database/SoulvizierClassic.arz"

# ---------------------------------------------------------------------------
# Key fields to extract for display
# ---------------------------------------------------------------------------
IDENTITY_FIELDS = [
    "FileDescription", "itemNameTag", "itemClassification",
    "itemLevel", "levelRequirement",
    "strengthRequirement", "dexterityRequirement", "intelligenceRequirement",
]

WARRIOR_FIELDS = [
    # Physical damage
    "offensivePhysicalMin", "offensivePhysicalMax",
    "offensiveBonusPhysicalMin", "offensiveBonusPhysicalMax",
    "offensivePhysicalModifier", "offensivePhysicalModifierChance",
    # Pierce
    "offensivePierceMin", "offensivePierceMax",
    "offensivePierceRatioMin", "offensivePierceRatioMax",
    # Character stats
    "characterStrength", "characterStrengthModifier",
    "characterDexterity", "characterDexterityModifier",
    "characterOffensiveAbility", "characterOffensiveAbilityModifier",
    "characterDefensiveAbility", "characterDefensiveAbilityModifier",
    "characterLife", "characterLifeModifier",
    "characterAttackSpeed", "characterAttackSpeedModifier",
    "characterBaseAttackSpeed", "characterBaseAttackSpeedTag",
    # Defensive
    "defensiveProtection", "defensiveProtectionModifier",
    # Procs / special
    "offensiveSlowBleedingMin", "offensiveSlowBleedingMax",
    "offensiveSlowBleedingDurationMin",
    "offensiveFumbleChance", "offensiveFumbleMin", "offensiveFumbleDurationMin",
    "offensiveSleepChance", "offensiveSleepMin",
    "offensiveStunMin", "offensiveStunChance",
    # Life leech
    "offensiveSlowLifeLeachMin", "offensiveSlowLifeLeachMax",
    "offensiveSlowLifeLeachDurationMin",
    # Resistance reduction
    "offensiveSlowDefensiveReductionMin", "offensiveSlowDefensiveReductionChance",
    "offensiveSlowDefensiveReductionDurationMin",
    # Retaliation
    "retaliationPhysicalMin", "retaliationPhysicalMax",
    # Skills
    "itemSkillName", "itemSkillAutoController",
]

CASTER_FIELDS = [
    # Fire damage
    "offensiveFireMin", "offensiveFireMax",
    "offensiveFireModifier", "offensiveFireModifierChance",
    "offensiveSlowFireMin", "offensiveSlowFireMax",
    "offensiveSlowFireDurationMin", "offensiveSlowFireDurationMax",
    # Burn
    "offensiveBurnMin", "offensiveBurnMax",
    # Lightning (secondary for casters)
    "offensiveLightningMin", "offensiveLightningMax",
    # Character stats
    "characterIntelligence", "characterIntelligenceModifier",
    "characterSpellCastSpeed", "characterSpellCastSpeedModifier",
    "characterMana", "characterManaModifier",
    "characterManaRegen", "characterManaRegenModifier",
    "characterLife", "characterLifeModifier",
    "characterOffensiveAbility", "characterOffensiveAbilityModifier",
    "characterDefensiveAbility", "characterDefensiveAbilityModifier",
    # Defensive / resistances
    "defensiveFire", "defensiveFireModifier",
    # Cooldown reduction
    "characterRechargeModifier",  # cooldown reduction
    # Skills
    "itemSkillName", "itemSkillAutoController",
    # Elemental modifier (generic)
    "offensiveElementalModifier", "offensiveElementalModifierChance",
    # Total damage
    "offensiveTotalDamageModifier",
]


def get_val(fields, name):
    """Get a field value, return None if missing or zero."""
    if fields is None:
        return None
    if name in fields:
        v = fields[name].value
        if isinstance(v, (int, float)) and v == 0:
            return None
        if isinstance(v, str) and v == "":
            return None
        return v
    # Try ###-suffixed keys
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            v = tf.value
            if isinstance(v, (int, float)) and v == 0:
                return None
            if isinstance(v, str) and v == "":
                return None
            return v
    return None


def extract_stats(fields, stat_fields):
    """Extract non-zero stats from a field set."""
    stats = {}
    for f in IDENTITY_FIELDS + stat_fields:
        v = get_val(fields, f)
        if v is not None:
            stats[f] = v
    return stats


def score_warrior(stats):
    """Score an item for warrior/physical theme (higher = better fit)."""
    s = 0.0
    # Physical damage is king
    phys_min = stats.get("offensivePhysicalMin", 0) or 0
    phys_max = stats.get("offensivePhysicalMax", 0) or 0
    s += (phys_min + phys_max) * 0.5
    # Bonus physical
    bonus_phys = stats.get("offensiveBonusPhysicalMin", 0) or 0
    s += bonus_phys * 0.3
    # Physical % modifier
    phys_mod = stats.get("offensivePhysicalModifier", 0) or 0
    if phys_mod > 0:
        s += phys_mod * 0.5
    # Strength
    str_val = stats.get("characterStrength", 0) or 0
    s += str_val * 1.0
    str_mod = stats.get("characterStrengthModifier", 0) or 0
    s += str_mod * 2.0
    # OA
    oa = stats.get("characterOffensiveAbility", 0) or 0
    s += oa * 0.3
    oa_mod = stats.get("characterOffensiveAbilityModifier", 0) or 0
    s += oa_mod * 3.0
    # DA
    da = stats.get("characterDefensiveAbility", 0) or 0
    s += da * 0.15
    # Life
    life = stats.get("characterLife", 0) or 0
    s += life * 0.05
    life_mod = stats.get("characterLifeModifier", 0) or 0
    s += life_mod * 1.0
    # Attack speed
    aspd = stats.get("characterAttackSpeed", 0) or 0
    s += aspd * 2.0
    aspd_mod = stats.get("characterAttackSpeedModifier", 0) or 0
    s += aspd_mod * 2.0
    # Pierce ratio
    pr = stats.get("offensivePierceRatioMin", 0) or 0
    s += pr * 0.3
    # Bleeding DOT
    bleed = stats.get("offensiveSlowBleedingMin", 0) or 0
    s += bleed * 0.1
    # Protection
    prot = stats.get("defensiveProtection", 0) or 0
    s += prot * 0.02
    # Dex (minor)
    dex = stats.get("characterDexterity", 0) or 0
    s += dex * 0.3
    # Penalize INT requirement (warrior shouldn't need INT)
    int_req = stats.get("intelligenceRequirement", 0) or 0
    if int_req > 0:
        s -= int_req * 0.5
    return s


def score_caster(stats):
    """Score an item for fire caster theme (higher = better fit)."""
    s = 0.0
    # Fire damage
    fire_min = stats.get("offensiveFireMin", 0) or 0
    fire_max = stats.get("offensiveFireMax", 0) or 0
    s += (fire_min + fire_max) * 0.5
    # Fire % modifier
    fire_mod = stats.get("offensiveFireModifier", 0) or 0
    if fire_mod > 0:
        s += fire_mod * 1.0
    # Burn DOT
    burn_min = stats.get("offensiveSlowFireMin", 0) or 0
    burn_max = stats.get("offensiveSlowFireMax", 0) or 0
    s += (burn_min + burn_max) * 0.3
    # Intelligence
    int_val = stats.get("characterIntelligence", 0) or 0
    s += int_val * 1.0
    int_mod = stats.get("characterIntelligenceModifier", 0) or 0
    s += int_mod * 3.0
    # Cast speed
    cs = stats.get("characterSpellCastSpeed", 0) or 0
    s += cs * 3.0
    cs_mod = stats.get("characterSpellCastSpeedModifier", 0) or 0
    s += cs_mod * 3.0
    # Mana
    mana = stats.get("characterMana", 0) or 0
    s += mana * 0.05
    mana_mod = stats.get("characterManaModifier", 0) or 0
    s += mana_mod * 1.0
    mana_regen = stats.get("characterManaRegen", 0) or 0
    s += mana_regen * 0.5
    # Life
    life = stats.get("characterLife", 0) or 0
    s += life * 0.03
    life_mod = stats.get("characterLifeModifier", 0) or 0
    s += life_mod * 0.5
    # OA
    oa = stats.get("characterOffensiveAbility", 0) or 0
    s += oa * 0.1
    # DA
    da = stats.get("characterDefensiveAbility", 0) or 0
    s += da * 0.1
    # CDR
    cdr = stats.get("characterRechargeModifier", 0) or 0
    s += cdr * 3.0
    # Elemental % modifier
    elem_mod = stats.get("offensiveElementalModifier", 0) or 0
    s += elem_mod * 0.5
    # Total damage modifier
    total_mod = stats.get("offensiveTotalDamageModifier", 0) or 0
    s += total_mod * 0.5
    # Lightning (secondary caster)
    light_min = stats.get("offensiveLightningMin", 0) or 0
    light_max = stats.get("offensiveLightningMax", 0) or 0
    s += (light_min + light_max) * 0.2
    # Penalize STR requirement (caster shouldn't need STR)
    str_req = stats.get("strengthRequirement", 0) or 0
    if str_req > 200:
        s -= (str_req - 200) * 0.3
    return s


def tier_from_path(path):
    """Extract tier indicator from record path filename."""
    fname = path.rsplit("\\", 1)[-1].lower() if "\\" in path else path.lower()
    # Check for u_n_, u_e_, u_l_, us_n_, us_e_, us_l_, usm_n_, usm_e_, usm_l_, mi_n_, mi_e_, mi_l_
    for prefix in ["usm_", "us_", "u_", "mi_"]:
        if fname.startswith(prefix):
            rest = fname[len(prefix):]
            if rest.startswith("n_"):
                return "Normal"
            elif rest.startswith("e_"):
                return "Epic"
            elif rest.startswith("l_"):
                return "Legendary"
    return None


def find_items_in_category(db, path_patterns, tier_codes, stat_fields, score_fn):
    """
    Find all items matching path patterns and tier codes, score them.

    path_patterns: list of substrings that must appear in the record path (OR logic)
    tier_codes: list of tier filename prefixes like 'u_n_', 'us_e_', etc.
    """
    results = []
    for rec_name in db.record_names():
        rec_lower = rec_name.lower()

        # Check path pattern match
        path_match = False
        for pat in path_patterns:
            if pat.lower() in rec_lower:
                path_match = True
                break
        if not path_match:
            continue

        # Check tier code match
        fname = rec_lower.rsplit("\\", 1)[-1] if "\\" in rec_lower else rec_lower
        tier_match = False
        for tc in tier_codes:
            if fname.startswith(tc.lower()):
                tier_match = True
                break
        if not tier_match:
            continue

        # Decode and score
        fields = db.get_fields(rec_name)
        if fields is None:
            continue

        stats = extract_stats(fields, stat_fields)
        score = score_fn(stats)
        tier = tier_from_path(rec_name)

        results.append({
            "path": rec_name,
            "tier": tier,
            "score": score,
            "stats": stats,
        })

    results.sort(key=lambda x: -x["score"])
    return results


def print_item(item, indent=2):
    """Pretty-print an item's stats."""
    prefix = " " * indent
    print(f"{prefix}Path: {item['path']}")
    print(f"{prefix}Tier: {item['tier']}  |  Score: {item['score']:.1f}")
    s = item["stats"]
    if "FileDescription" in s:
        print(f"{prefix}Desc: {s['FileDescription']}")
    if "itemNameTag" in s:
        print(f"{prefix}Name Tag: {s['itemNameTag']}")
    if "itemClassification" in s:
        print(f"{prefix}Classification: {s['itemClassification']}")
    if "itemLevel" in s:
        print(f"{prefix}Item Level: {s['itemLevel']}")
    if "levelRequirement" in s:
        print(f"{prefix}Level Req: {s['levelRequirement']}")

    # Requirements
    reqs = []
    for rk in ["strengthRequirement", "dexterityRequirement", "intelligenceRequirement"]:
        v = s.get(rk)
        if v:
            reqs.append(f"{rk.replace('Requirement','').replace('character','')}: {v}")
    if reqs:
        print(f"{prefix}Requirements: {', '.join(reqs)}")

    # Interesting stats (skip identity and requirements)
    skip = set(IDENTITY_FIELDS + ["strengthRequirement", "dexterityRequirement", "intelligenceRequirement"])
    interesting = {k: v for k, v in s.items() if k not in skip}
    if interesting:
        print(f"{prefix}Stats:")
        for k, v in interesting.items():
            if isinstance(v, float):
                print(f"{prefix}  {k}: {v:.1f}")
            else:
                print(f"{prefix}  {k}: {v}")
    print()


def main():
    print("Loading database...")
    db = ArzDatabase.from_arz(DB_PATH)
    print()

    # ===================================================================
    # RAKANIZEUS - Warrior Satyr
    # ===================================================================
    print("=" * 90)
    print("RAKANIZEUS (Warrior Satyr) - Physical/STR/OA Theme")
    print("=" * 90)

    # --- SWORDS ---
    # Note: swords can be in equipmentweapons\sword or equipmentweapon\sword
    sword_patterns = ["equipmentweapon\\sword\\", "equipmentweapons\\sword\\"]

    for tier_label, tier_codes in [
        ("NORMAL", ["u_n_", "us_n_", "usm_n_"]),
        ("EPIC", ["u_e_", "us_e_", "usm_e_"]),
        ("LEGENDARY (reference)", ["u_l_", "us_l_", "usm_l_"]),
    ]:
        print(f"\n--- {tier_label} SWORDS ---")
        items = find_items_in_category(db, sword_patterns, tier_codes, WARRIOR_FIELDS, score_warrior)
        if not items:
            print("  No items found.")
        else:
            print(f"  Found {len(items)} items. Top 5:")
            for item in items[:5]:
                print_item(item, indent=4)

    # --- ARMBANDS ---
    armband_patterns = ["equipmentarmband\\"]

    for tier_label, tier_codes in [
        ("NORMAL", ["u_n_", "us_n_", "usm_n_"]),
        ("EPIC", ["u_e_", "us_e_", "usm_e_"]),
    ]:
        print(f"\n--- {tier_label} ARMBANDS (Warrior) ---")
        items = find_items_in_category(db, armband_patterns, tier_codes, WARRIOR_FIELDS, score_warrior)
        if not items:
            print("  No items found.")
        else:
            print(f"  Found {len(items)} items. Top 5:")
            for item in items[:5]:
                print_item(item, indent=4)

    # --- RINGS ---
    ring_patterns = ["equipmentring\\"]

    for tier_label, tier_codes in [
        ("NORMAL", ["u_n_", "us_n_", "usm_n_"]),
        ("EPIC", ["u_e_", "us_e_", "usm_e_"]),
    ]:
        print(f"\n--- {tier_label} RINGS (Warrior) ---")
        items = find_items_in_category(db, ring_patterns, tier_codes, WARRIOR_FIELDS, score_warrior)
        if not items:
            print("  No items found.")
        else:
            print(f"  Found {len(items)} items. Top 5:")
            for item in items[:5]:
                print_item(item, indent=4)

    # ===================================================================
    # BONEASH - Fire Skeleton Caster
    # ===================================================================
    print("\n" + "=" * 90)
    print("BONEASH (Fire Skeleton Caster) - Fire/INT/Cast Speed Theme")
    print("=" * 90)

    # --- STAVES ---
    staff_patterns = ["equipmentweapon\\staff\\", "equipmentweapons\\staff\\"]

    for tier_label, tier_codes in [
        ("NORMAL", ["u_n_", "us_n_", "usm_n_"]),
        ("EPIC (reference: Heka Staff)", ["u_e_", "us_e_", "usm_e_"]),
        ("LEGENDARY (upgrade from Heka)", ["u_l_", "us_l_", "usm_l_"]),
    ]:
        print(f"\n--- {tier_label} STAVES ---")
        items = find_items_in_category(db, staff_patterns, tier_codes, CASTER_FIELDS, score_caster)
        if not items:
            print("  No items found.")
        else:
            print(f"  Found {len(items)} items. Top 5:")
            for item in items[:5]:
                print_item(item, indent=4)

    # --- ARMBANDS (Caster) ---
    for tier_label, tier_codes in [
        ("NORMAL", ["u_n_", "us_n_", "usm_n_"]),
        ("EPIC", ["u_e_", "us_e_", "usm_e_"]),
    ]:
        print(f"\n--- {tier_label} ARMBANDS (Caster) ---")
        items = find_items_in_category(db, armband_patterns, tier_codes, CASTER_FIELDS, score_caster)
        if not items:
            print("  No items found.")
        else:
            print(f"  Found {len(items)} items. Top 5:")
            for item in items[:5]:
                print_item(item, indent=4)

    # --- RINGS (Caster) ---
    for tier_label, tier_codes in [
        ("NORMAL", ["u_n_", "us_n_", "usm_n_"]),
        ("EPIC", ["u_e_", "us_e_", "usm_e_"]),
    ]:
        print(f"\n--- {tier_label} RINGS (Caster) ---")
        items = find_items_in_category(db, ring_patterns, tier_codes, CASTER_FIELDS, score_caster)
        if not items:
            print("  No items found.")
        else:
            print(f"  Found {len(items)} items. Top 5:")
            for item in items[:5]:
                print_item(item, indent=4)

    # ===================================================================
    # SUMMARY: Show current legendary items for reference
    # ===================================================================
    print("\n" + "=" * 90)
    print("REFERENCE: Current Legendary Items")
    print("=" * 90)

    ref_items = {
        "Rakanizeus Sword (Sword of Eternal Darkness)": (
            r"records\xpack\item\equipmentweapons\sword\u_l_002.dbr", WARRIOR_FIELDS, score_warrior),
        "Rakanizeus Armband (Conqueror's Bracers)": (
            r"records\item\equipmentarmband\us_l_conqueror'spanoply.dbr", WARRIOR_FIELDS, score_warrior),
        "Rakanizeus Ring (Mark of Ares)": (
            r"records\item\equipmentring\u_l_markofares.dbr", WARRIOR_FIELDS, score_warrior),
        "Boneash Staff (Heka Staff - EPIC)": (
            r"records\item\equipmentweapon\staff\u_e_hekastaff.dbr", CASTER_FIELDS, score_caster),
        "Boneash Armband (Archmage's Clasp)": (
            r"records\item\equipmentarmband\usm_l_archmage'sregalia.dbr", CASTER_FIELDS, score_caster),
        "Boneash Ring (Seal of Hephaestus)": (
            r"records\item\equipmentring\u_l_sealofhephaestus.dbr", CASTER_FIELDS, score_caster),
    }

    for label, (path, stat_fields, score_fn) in ref_items.items():
        print(f"\n  {label}:")
        fields = db.get_fields(path)
        if fields is None:
            # Try case-insensitive lookup
            found = [r for r in db.record_names() if r.lower() == path.lower()]
            if found:
                fields = db.get_fields(found[0])
                path = found[0]
        if fields is None:
            print(f"    NOT FOUND: {path}")
            continue
        stats = extract_stats(fields, stat_fields)
        score = score_fn(stats)
        item = {"path": path, "tier": tier_from_path(path), "score": score, "stats": stats}
        print_item(item, indent=4)


if __name__ == "__main__":
    main()
