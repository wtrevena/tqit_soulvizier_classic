"""
Diagnostic: compare equipment/loot and skill fields between Lyia pets,
Rakanizeus monster, and Boneash monster.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from arz_patcher import ArzDatabase

DB_PATH = Path(__file__).resolve().parent.parent / "work" / "SoulvizierClassic" / "Database" / "SoulvizierClassic.arz"

RECORDS = {
    # The actual creature records (monster templates used as pet spawns)
    "Lyia (creature)": r"records\creature\monster\maenad\um_lyialeafsong_18.dbr",
    "Rakanizeus (creature)": r"records\creature\monster\satyr\um_rakanizeus_17.dbr",
    "Boneash (creature)": r"records\creature\monster\skeleton\um_boneash_30.dbr",
    # The pet skill spawn records (define the pet when summoned via soul)
    "Lyia pet_1": r"records\skills\soulskills\pets\lyialeafsong_1.dbr",
    "Lyia pet_2": r"records\skills\soulskills\pets\lyialeafsong_2.dbr",
    "Lyia pet_3": r"records\skills\soulskills\pets\lyialeafsong_3.dbr",
    "Rakanizeus pet_1": r"records\skills\soulskills\pets\rakanizeus_1.dbr",
    "Rakanizeus pet_2": r"records\skills\soulskills\pets\rakanizeus_2.dbr",
    "Rakanizeus pet_3": r"records\skills\soulskills\pets\rakanizeus_3.dbr",
    "Boneash pet_1": r"records\skills\soulskills\pets\boneash_1.dbr",
    "Boneash pet_2": r"records\skills\soulskills\pets\boneash_2.dbr",
    "Boneash pet_3": r"records\skills\soulskills\pets\boneash_3.dbr",
}

EQUIP_PREFIXES = ("chancetoequip", "loot")
SKILL_PREFIXES = ("skillname", "skilllevel", "attackskillname", "specialattack", "buffself", "initialskillname")
ALL_PREFIXES = EQUIP_PREFIXES + SKILL_PREFIXES

DTYPE_NAMES = {0: "INT", 1: "FLOAT", 2: "STRING", 3: "BOOL"}


def field_base(key):
    """Strip the ###N suffix used for duplicate field keys."""
    return key.split("###")[0]


def matches_prefix(key):
    base = field_base(key).lower()
    return any(base.startswith(p) for p in ALL_PREFIXES)


def is_equip(key):
    base = field_base(key).lower()
    return any(base.startswith(p) for p in EQUIP_PREFIXES)


def is_skill(key):
    base = field_base(key).lower()
    return any(base.startswith(p) for p in SKILL_PREFIXES)


def print_fields(label, fields_dict):
    """Print matching fields grouped by category."""
    equip_fields = {k: v for k, v in fields_dict.items() if is_equip(k)}
    skill_fields = {k: v for k, v in fields_dict.items() if is_skill(k)}

    print(f"\n{'='*80}")
    print(f"  {label}")
    print(f"{'='*80}")

    if equip_fields:
        print(f"\n  --- Equipment / Loot fields ({len(equip_fields)}) ---")
        for key, tf in equip_fields.items():
            dtype_name = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
            print(f"    {field_base(key):40s}  [{dtype_name:6s}]  {tf.values}")
    else:
        print("\n  --- Equipment / Loot fields: NONE ---")

    if skill_fields:
        print(f"\n  --- Skill fields ({len(skill_fields)}) ---")
        for key, tf in skill_fields.items():
            dtype_name = DTYPE_NAMES.get(tf.dtype, f"?{tf.dtype}")
            print(f"    {field_base(key):40s}  [{dtype_name:6s}]  {tf.values}")
    else:
        print("\n  --- Skill fields: NONE ---")


def main():
    print(f"Opening database: {DB_PATH}")
    db = ArzDatabase.from_arz(DB_PATH)

    # Collect matching fields per record
    all_matched = {}
    for label, rec_path in RECORDS.items():
        fields = db.get_fields(rec_path)
        if fields is None:
            print(f"\n*** RECORD NOT FOUND: {rec_path} ***")
            all_matched[label] = {}
            continue
        matched = {k: v for k, v in fields.items() if matches_prefix(k)}
        all_matched[label] = matched
        print_fields(label, matched)

    # --- Diff analysis ---
    print(f"\n\n{'#'*80}")
    print(f"  DIFF ANALYSIS")
    print(f"{'#'*80}")

    # Group: creature records
    lyia_creature = [l for l in RECORDS if "Lyia (creature)" in l]
    monster_creatures = [l for l in RECORDS if l.endswith("(creature)") and "Lyia" not in l]
    # Group: pet spawn records
    lyia_pets = [l for l in RECORDS if l.startswith("Lyia pet_")]
    monster_pets_rakan = [l for l in RECORDS if l.startswith("Rakanizeus pet_")]
    monster_pets_bone = [l for l in RECORDS if l.startswith("Boneash pet_")]

    lyia_labels = lyia_creature + lyia_pets
    monster_labels = monster_creatures + monster_pets_rakan + monster_pets_bone

    lyia_bases = set()
    for label in lyia_labels:
        for k in all_matched.get(label, {}):
            lyia_bases.add(field_base(k).lower())

    monster_bases = set()
    for label in monster_labels:
        for k in all_matched.get(label, {}):
            monster_bases.add(field_base(k).lower())

    in_monsters_not_lyia = sorted(monster_bases - lyia_bases)
    in_lyia_not_monsters = sorted(lyia_bases - monster_bases)
    in_both = sorted(lyia_bases & monster_bases)

    print(f"\n  Fields in MONSTERS but NOT in any Lyia ({len(in_monsters_not_lyia)}):")
    for f in in_monsters_not_lyia:
        # Show which monster has it and the values
        sources = []
        for label in monster_labels:
            for k, tf in all_matched.get(label, {}).items():
                if field_base(k).lower() == f:
                    dtype_name = DTYPE_NAMES.get(tf.dtype, "?")
                    sources.append(f"{label}: [{dtype_name}] {tf.values}")
        print(f"    {f:40s}")
        for s in sources:
            print(f"      -> {s}")

    print(f"\n  Fields in LYIA but NOT in any monster ({len(in_lyia_not_monsters)}):")
    for f in in_lyia_not_monsters:
        sources = []
        for label in lyia_labels:
            for k, tf in all_matched.get(label, {}).items():
                if field_base(k).lower() == f:
                    dtype_name = DTYPE_NAMES.get(tf.dtype, "?")
                    sources.append(f"{label}: [{dtype_name}] {tf.values}")
        print(f"    {f:40s}")
        for s in sources:
            print(f"      -> {s}")

    print(f"\n  Fields in BOTH Lyia and monsters ({len(in_both)}):")
    for f in in_both:
        print(f"    {f}")

    # Per-record detailed diffs
    def do_detailed_diff(ref_label, compare_labels):
        ref_fields = all_matched.get(ref_label, {})
        ref_bases_map = {}
        for k, tf in ref_fields.items():
            ref_bases_map[field_base(k).lower()] = (k, tf)

        for label in compare_labels:
            print(f"\n  --- Detailed diff: {label} vs {ref_label} ---")
            cmp_fields = all_matched.get(label, {})
            cmp_bases_map = {}
            for k, tf in cmp_fields.items():
                cmp_bases_map[field_base(k).lower()] = (k, tf)

            all_bases = sorted(set(ref_bases_map.keys()) | set(cmp_bases_map.keys()))
            for base in all_bases:
                in_ref = base in ref_bases_map
                in_cmp = base in cmp_bases_map
                if in_ref and in_cmp:
                    rk, rt = ref_bases_map[base]
                    ck, ct = cmp_bases_map[base]
                    rd = DTYPE_NAMES.get(rt.dtype, "?")
                    cd = DTYPE_NAMES.get(ct.dtype, "?")
                    if rt.values != ct.values or rt.dtype != ct.dtype:
                        print(f"    DIFFERS  {base:40s}")
                        print(f"             {ref_label[:20]+':':21s} [{rd}] {rt.values}")
                        print(f"             {label[:20]+':':21s} [{cd}] {ct.values}")
                    else:
                        print(f"    SAME     {base:40s}  [{rd}] {rt.values}")
                elif in_cmp and not in_ref:
                    ck, ct = cmp_bases_map[base]
                    cd = DTYPE_NAMES.get(ct.dtype, "?")
                    print(f"    OTHER+   {base:40s}  [{cd}] {ct.values}")
                elif in_ref and not in_cmp:
                    rk, rt = ref_bases_map[base]
                    rd = DTYPE_NAMES.get(rt.dtype, "?")
                    print(f"    REF+     {base:40s}  [{rd}] {rt.values}")

    # Creature-level comparisons: Lyia creature vs each monster creature
    do_detailed_diff("Lyia (creature)", monster_creatures)

    # Pet spawn comparisons: Lyia pet_1 vs Rakanizeus pet_1 and Boneash pet_1
    do_detailed_diff("Lyia pet_1", ["Rakanizeus pet_1", "Boneash pet_1"])

    print("\nDone.")


if __name__ == "__main__":
    main()
