"""Search the SoulvizierClassic database for Pharaoh's Honor Guard info."""
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

DB_PATH = Path(__file__).parent.parent / "work/SoulvizierClassic/Database/SoulvizierClassic.arz"

def main():
    print(f"Loading database: {DB_PATH}")
    db = ArzDatabase.from_arz(DB_PATH)
    names = db.record_names()
    print(f"Total records: {len(names)}")

    # --- 1. Search record names for pharaoh / honor / honorguard ---
    print("\n" + "=" * 80)
    print("1. RECORD NAME SEARCH: 'pharaoh', 'honor', 'honorguard'")
    print("=" * 80)

    patterns = [re.compile(r'pharaoh', re.IGNORECASE),
                re.compile(r'honor', re.IGNORECASE),
                re.compile(r'honorguard', re.IGNORECASE)]

    matched_records = []
    for name in names:
        for pat in patterns:
            if pat.search(name):
                matched_records.append(name)
                break

    print(f"Found {len(matched_records)} matching records:")
    for r in sorted(matched_records):
        print(f"  {r}")

    # --- 2. Dump creature/monster fields for matching records ---
    print("\n" + "=" * 80)
    print("2. CREATURE/MONSTER RECORD DETAILS")
    print("=" * 80)

    creature_keywords = ['monster', 'creature', 'proxy', 'boss', 'hero', 'champion', 'npc']
    key_fields = [
        'templateName', 'description', 'descriptionTag', 'Description',
        'characterRacialProfile', 'monsterClassification',
        'charLevel', 'characterLife',
    ]

    for rec in sorted(matched_records):
        rec_lower = rec.lower()
        is_creature = any(kw in rec_lower for kw in creature_keywords)
        # Also check if it has creature-like fields
        fields = db.get_fields(rec)
        if fields is None:
            continue

        field_names = [k.split('###')[0] for k in fields.keys()]
        has_creature_fields = any(f in field_names for f in ['charLevel', 'characterLife', 'monsterClassification', 'characterRacialProfile'])

        if not is_creature and not has_creature_fields:
            continue

        print(f"\n--- {rec} ---")
        print(f"  [Record type in DB: {db._record_types.get(rec, '?')}]")

        # Key fields
        for fname in key_fields:
            val = db.get_field_value(rec, fname)
            if val is not None:
                print(f"  {fname}: {val}")

        # Fields containing 'soul'
        soul_fields = [(k, fields[k]) for k in fields if 'soul' in k.split('###')[0].lower()]
        if soul_fields:
            print("  -- Soul-related fields --")
            for k, tf in soul_fields:
                print(f"    {k.split('###')[0]}: {tf.values} (dtype={tf.dtype})")

        # Fields containing 'loot'
        loot_fields = [(k, fields[k]) for k in fields if 'loot' in k.split('###')[0].lower()]
        if loot_fields:
            print("  -- Loot-related fields --")
            for k, tf in loot_fields:
                print(f"    {k.split('###')[0]}: {tf.values} (dtype={tf.dtype})")

        # Skills/attacks
        print("  -- Skills/Attacks --")
        skill_patterns = ['skillname', 'attackskillname', 'specialattack']
        for k in fields:
            real = k.split('###')[0].lower()
            if any(sp in real for sp in skill_patterns):
                print(f"    {k.split('###')[0]}: {fields[k].values}")

    # --- 3. Soul item records containing pharaoh or honor ---
    print("\n" + "=" * 80)
    print("3. SOUL ITEM RECORDS CONTAINING 'pharaoh' OR 'honor'")
    print("=" * 80)

    soul_pat = re.compile(r'soul', re.IGNORECASE)
    pharaoh_pat = re.compile(r'pharaoh|honor', re.IGNORECASE)
    soul_matches = [n for n in names if soul_pat.search(n) and pharaoh_pat.search(n)]
    if soul_matches:
        for r in sorted(soul_matches):
            print(f"  {r}")
            fields = db.get_fields(r)
            if fields:
                for k, tf in fields.items():
                    print(f"    {k.split('###')[0]}: {tf.values}")
    else:
        print("  (none found)")

    # --- 4. String table search ---
    print("\n" + "=" * 80)
    print("4. STRING TABLE SEARCH: 'Pharaoh' or 'Honor Guard'")
    print("=" * 80)

    str_patterns = [re.compile(r'pharaoh', re.IGNORECASE),
                    re.compile(r'honor\s*guard', re.IGNORECASE)]

    str_matches = []
    for i, s in enumerate(db.strings):
        for pat in str_patterns:
            if pat.search(s):
                str_matches.append((i, s))
                break

    print(f"Found {len(str_matches)} matching strings:")
    for idx, s in str_matches:
        print(f"  [{idx}] {s}")

    # --- 5. Soul ring records ---
    print("\n" + "=" * 80)
    print("5. SOUL RING RECORDS (equipmentring paths with pharaoh/honor)")
    print("=" * 80)

    ring_pat = re.compile(r'(equipmentring|ring)', re.IGNORECASE)
    ring_matches = [n for n in names if ring_pat.search(n) and pharaoh_pat.search(n)]
    if ring_matches:
        for r in sorted(ring_matches):
            print(f"  {r}")
            fields = db.get_fields(r)
            if fields:
                for k, tf in fields.items():
                    print(f"    {k.split('###')[0]}: {tf.values}")
    else:
        print("  (none found)")
        # Also search all ring paths for reference
        print("\n  Searching ALL equipmentring paths with 'soul' in the name:")
        soul_ring_matches = [n for n in names if 'ring' in n.lower() and 'soul' in n.lower()]
        for r in sorted(soul_ring_matches)[:30]:
            print(f"    {r}")
        if len(soul_ring_matches) > 30:
            print(f"    ... and {len(soul_ring_matches) - 30} more")

    # --- 6. Full field dump for ALL matching records (non-creature too) ---
    print("\n" + "=" * 80)
    print("6. FULL FIELD DUMP FOR ALL MATCHING RECORDS")
    print("=" * 80)

    for rec in sorted(matched_records):
        fields = db.get_fields(rec)
        if fields is None:
            continue
        print(f"\n--- {rec} ---")
        print(f"  [Record type: {db._record_types.get(rec, '?')}]")
        for k, tf in fields.items():
            real = k.split('###')[0]
            dtype_name = {0: 'INT', 1: 'FLOAT', 2: 'STRING', 3: 'BOOL'}.get(tf.dtype, '?')
            print(f"    {real}: {tf.values}  [{dtype_name}]")

    print("\n" + "=" * 80)
    print("DONE")
    print("=" * 80)


if __name__ == '__main__':
    main()
