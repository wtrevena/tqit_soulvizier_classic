"""
List all monsters by classification in the Soulvizier Classic database.

Scans for creature records using Monster.tpl, Pet.tpl, SpiritHost.tpl,
and other monster templates (Cerberus, Hades, Megalesios), plus any record
with a monsterClassification field.

Deduplicates by description tag to count unique monsters.
"""
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

DB_PATH = Path(__file__).parent.parent / "work/SoulvizierClassic/Database/SoulvizierClassic.arz"

# Templates that indicate a monster/creature record
MONSTER_TEMPLATES = {
    "monster.tpl",
    "pet.tpl",
    "petnonscaling.tpl",
    "spirithost.tpl",
    "cerberus.tpl",
    "hades.tpl",
    "megalesios.tpl",
    "megalesiosconduit.tpl",
}


def template_is_monster(tpl_name: str) -> bool:
    """Check if a template name corresponds to a monster-type record."""
    if not tpl_name:
        return False
    basename = tpl_name.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].lower()
    return basename in MONSTER_TEMPLATES


def extract_monster_info(db, record_name):
    """Extract key fields from a monster record. Returns dict or None."""
    fields = db.get_fields(record_name)
    if fields is None:
        return None

    info = {
        "record": record_name,
        "templateName": "",
        "description": "",
        "monsterClassification": "",
        "characterRacialProfile": "",
        "charLevel": [],
        "lootFinger2Item1": "",
        "FileDescription": "",
    }

    for key, tf in fields.items():
        real = key.split("###")[0]
        if real == "templateName" and tf.values:
            info["templateName"] = tf.values[0]
        elif real == "description" and tf.values:
            info["description"] = tf.values[0]
        elif real == "monsterClassification" and tf.values:
            info["monsterClassification"] = tf.values[0]
        elif real == "characterRacialProfile" and tf.values:
            info["characterRacialProfile"] = tf.values[0]
        elif real == "charLevel" and tf.values:
            info["charLevel"] = [v for v in tf.values if v]
        elif real == "lootFinger2Item1" and tf.values:
            info["lootFinger2Item1"] = tf.values[0]
        elif real == "FileDescription" and tf.values:
            info["FileDescription"] = tf.values[0]

    return info


def main():
    print(f"Loading database: {DB_PATH}")
    db = ArzDatabase.from_arz(DB_PATH)
    all_names = db.record_names()
    print(f"Total records in database: {len(all_names)}")

    # ── Phase 1: Find all monster records ─────────────────────────────
    print("\n--- Scanning for monster records ---")
    creature_records = [n for n in all_names if n.lower().endswith(".dbr")]

    monsters = []  # list of info dicts
    processed = 0

    for name in creature_records:
        fields = db.get_fields(name)
        if fields is None:
            continue

        tpl = ""
        has_mc = False
        for key, tf in fields.items():
            real = key.split("###")[0]
            if real == "templateName" and tf.values:
                tpl = tf.values[0]
            if real == "monsterClassification" and tf.values and tf.values[0]:
                has_mc = True

        is_monster = template_is_monster(tpl) or has_mc

        if is_monster:
            info = extract_monster_info(db, name)
            if info:
                monsters.append(info)

        processed += 1
        if processed % 5000 == 0:
            print(f"  Scanned {processed}/{len(creature_records)}...")

    print(f"\nTotal monster records found: {len(monsters)}")

    # ── Phase 2: Build soul ring lookup ───────────────────────────────
    # Build a set of all soul ring record paths for quick lookup
    soul_ring_records = set()
    for n in all_names:
        if "soul" in n.lower() and ("ring" in n.lower() or "equipmentring" in n.lower()):
            soul_ring_records.add(n.lower())

    # Also build a mapping: monster description tag -> has soul
    # by checking lootFinger2Item1 across all monster records
    desc_has_soul = {}
    for m in monsters:
        desc = m["description"]
        if not desc:
            continue
        lf2 = m["lootFinger2Item1"]
        if lf2 and lf2.strip():
            desc_has_soul[desc] = True
        elif desc not in desc_has_soul:
            desc_has_soul[desc] = False

    # ── Phase 3: Deduplicate by description tag ───────────────────────
    # Group by (description, monsterClassification) - pick best representative
    unique_monsters = {}  # key = (desc, classification) -> representative info
    all_records_by_desc = defaultdict(list)

    for m in monsters:
        desc = m["description"] or m["record"]  # fallback to record path
        classification = m["monsterClassification"] or "Unknown"
        key = (desc, classification)
        all_records_by_desc[(desc, classification)].append(m)

        if key not in unique_monsters:
            unique_monsters[key] = m
        else:
            # Keep the one with more info (racial profile, levels, etc.)
            existing = unique_monsters[key]
            if not existing["characterRacialProfile"] and m["characterRacialProfile"]:
                unique_monsters[key] = m
            elif not existing["charLevel"] and m["charLevel"]:
                unique_monsters[key] = m

    # ── Phase 4: Count summary ────────────────────────────────────────
    print("\n" + "=" * 80)
    print("MONSTER CLASSIFICATION SUMMARY")
    print("=" * 80)

    classification_counts = defaultdict(int)
    classification_monsters = defaultdict(list)

    for (desc, cls), info in sorted(unique_monsters.items()):
        classification_counts[cls] += 1
        classification_monsters[cls].append((desc, info))

    total_unique = sum(classification_counts.values())
    print(f"\nTotal unique monsters (by description tag): {total_unique}")
    print(f"Total monster records (including level variants): {len(monsters)}")
    print()

    for cls in ["Boss", "Quest", "Hero", "Champion", "Common", "Unknown"]:
        if cls in classification_counts:
            count = classification_counts[cls]
            records_count = sum(
                len(all_records_by_desc[(desc, cls)])
                for desc, _ in classification_monsters[cls]
            )
            print(f"  {cls:15s}: {count:5d} unique monsters ({records_count:5d} total records)")

    # ── Phase 5: Full Boss list ───────────────────────────────────────
    print("\n" + "=" * 80)
    print("ALL BOSS-CLASSIFIED MONSTERS (deduplicated by description tag)")
    print("=" * 80)

    boss_list = classification_monsters.get("Boss", [])
    # Group by racial profile
    bosses_by_race = defaultdict(list)
    for desc, info in boss_list:
        race = info["characterRacialProfile"] or "Unspecified"
        bosses_by_race[race].append((desc, info))

    for race in sorted(bosses_by_race.keys()):
        race_bosses = bosses_by_race[race]
        print(f"\n  --- {race} ({len(race_bosses)} bosses) ---")
        for desc, info in sorted(race_bosses, key=lambda x: x[0]):
            levels = info["charLevel"]
            if levels:
                level_range = f"{int(min(levels))}-{int(max(levels))}"
            else:
                level_range = "???"
            has_soul = "SOUL" if desc_has_soul.get(desc, False) else "    "
            file_desc = info["FileDescription"] or ""
            record_count = len(all_records_by_desc[(desc, "Boss")])
            print(
                f"    [{has_soul}] {desc:45s} "
                f"Lv {level_range:10s} "
                f"({record_count} variants) "
                f"  {file_desc}"
            )
            print(f"           Record: {info['record']}")

    # ── Phase 6: Quest classification ─────────────────────────────────
    print("\n" + "=" * 80)
    print("QUEST-CLASSIFIED MONSTERS")
    print("=" * 80)

    quest_list = classification_monsters.get("Quest", [])
    quest_by_race = defaultdict(list)
    for desc, info in quest_list:
        race = info["characterRacialProfile"] or "Unspecified"
        quest_by_race[race].append((desc, info))

    print(f"\nTotal unique Quest monsters: {len(quest_list)}")
    for race in sorted(quest_by_race.keys()):
        race_quests = quest_by_race[race]
        print(f"\n  --- {race} ({len(race_quests)} monsters) ---")
        for desc, info in sorted(race_quests, key=lambda x: x[0]):
            levels = info["charLevel"]
            if levels:
                level_range = f"{int(min(levels))}-{int(max(levels))}"
            else:
                level_range = "???"
            has_soul = "SOUL" if desc_has_soul.get(desc, False) else "    "
            file_desc = info["FileDescription"] or ""
            record_count = len(all_records_by_desc[(desc, "Quest")])
            print(
                f"    [{has_soul}] {desc:45s} "
                f"Lv {level_range:10s} "
                f"({record_count} variants) "
                f"  {file_desc}"
            )
            print(f"           Record: {info['record']}")

    # ── Phase 7: Hero classification ──────────────────────────────────
    print("\n" + "=" * 80)
    print("HERO-CLASSIFIED MONSTERS")
    print("=" * 80)

    hero_list = classification_monsters.get("Hero", [])
    hero_by_race = defaultdict(list)
    for desc, info in hero_list:
        race = info["characterRacialProfile"] or "Unspecified"
        hero_by_race[race].append((desc, info))

    print(f"\nTotal unique Hero monsters: {len(hero_list)}")
    for race in sorted(hero_by_race.keys()):
        race_heroes = hero_by_race[race]
        print(f"\n  --- {race} ({len(race_heroes)} monsters) ---")
        for desc, info in sorted(race_heroes, key=lambda x: x[0])[:15]:
            levels = info["charLevel"]
            if levels:
                level_range = f"{int(min(levels))}-{int(max(levels))}"
            else:
                level_range = "???"
            has_soul = "SOUL" if desc_has_soul.get(desc, False) else "    "
            file_desc = info["FileDescription"] or ""
            record_count = len(all_records_by_desc[(desc, "Hero")])
            print(
                f"    [{has_soul}] {desc:45s} "
                f"Lv {level_range:10s} "
                f"({record_count} variants) "
                f"  {file_desc}"
            )
        remaining = len(race_heroes) - 15
        if remaining > 0:
            print(f"    ... and {remaining} more {race} heroes")

    # ── Phase 8: Champion summary ─────────────────────────────────────
    print("\n" + "=" * 80)
    print("CHAMPION-CLASSIFIED MONSTERS (summary + examples)")
    print("=" * 80)

    champ_list = classification_monsters.get("Champion", [])
    champ_by_race = defaultdict(list)
    for desc, info in champ_list:
        race = info["characterRacialProfile"] or "Unspecified"
        champ_by_race[race].append((desc, info))

    print(f"\nTotal unique Champion monsters: {len(champ_list)}")
    for race in sorted(champ_by_race.keys()):
        race_champs = champ_by_race[race]
        print(f"  {race}: {len(race_champs)} champions")
        for desc, info in sorted(race_champs, key=lambda x: x[0])[:5]:
            has_soul = "SOUL" if desc_has_soul.get(desc, False) else "    "
            file_desc = info["FileDescription"] or ""
            print(f"    [{has_soul}] {desc:40s}  {file_desc}")
        remaining = len(race_champs) - 5
        if remaining > 0:
            print(f"    ... and {remaining} more")

    # ── Phase 9: Common summary ───────────────────────────────────────
    print("\n" + "=" * 80)
    print("COMMON-CLASSIFIED MONSTERS (summary + examples)")
    print("=" * 80)

    common_list = classification_monsters.get("Common", [])
    common_by_race = defaultdict(list)
    for desc, info in common_list:
        race = info["characterRacialProfile"] or "Unspecified"
        common_by_race[race].append((desc, info))

    print(f"\nTotal unique Common monsters: {len(common_list)}")
    for race in sorted(common_by_race.keys()):
        race_commons = common_by_race[race]
        soul_count = sum(1 for d, _ in race_commons if desc_has_soul.get(d, False))
        print(f"  {race}: {len(race_commons)} common monsters ({soul_count} with souls)")
        for desc, info in sorted(race_commons, key=lambda x: x[0])[:5]:
            has_soul = "SOUL" if desc_has_soul.get(desc, False) else "    "
            file_desc = info["FileDescription"] or ""
            print(f"    [{has_soul}] {desc:40s}  {file_desc}")
        remaining = len(race_commons) - 5
        if remaining > 0:
            print(f"    ... and {remaining} more")

    # ── Phase 10: Soul coverage stats ─────────────────────────────────
    print("\n" + "=" * 80)
    print("SOUL RING COVERAGE")
    print("=" * 80)

    for cls in ["Boss", "Quest", "Hero", "Champion", "Common", "Unknown"]:
        if cls not in classification_monsters:
            continue
        entries = classification_monsters[cls]
        total = len(entries)
        with_soul = sum(1 for d, _ in entries if desc_has_soul.get(d, False))
        pct = (with_soul / total * 100) if total else 0
        print(f"  {cls:15s}: {with_soul:4d} / {total:4d} have souls ({pct:.1f}%)")

    print(f"\nTotal soul ring records in database: {len(soul_ring_records)}")
    total_with_soul = sum(1 for d in desc_has_soul.values() if d)
    total_monsters_with_desc = len(desc_has_soul)
    print(f"Unique monsters with souls: {total_with_soul} / {total_monsters_with_desc}")

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)


if __name__ == "__main__":
    main()
