"""Investigation script: Rakanizeus Soul analysis + Mercenary Scroll breakdown."""
import sys
from pathlib import Path
from collections import OrderedDict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase, TypedField
from arc_patcher import ArcArchive

SV_DB_PATH = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz')
BUILT_DB_PATH = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz')
TEXT_ARC_PATH = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Text_EN.arc')


def dump_fields(db, record_name, label=""):
    fields = db.get_fields(record_name)
    if fields is None:
        print(f"  [NOT FOUND] {record_name}")
        return None
    if label:
        print(f"\n{'='*80}")
        print(f"  {label}")
        print(f"  Record: {record_name}")
        print(f"{'='*80}")
    for key, tf in fields.items():
        rk = key.split('###')[0]
        dtype_names = {0: 'int', 1: 'float', 2: 'str', 3: 'bool'}
        dn = dtype_names.get(tf.dtype, f'?{tf.dtype}')
        if len(tf.values) == 1:
            print(f"  {rk:50s} ({dn:5s}) = {tf.values[0]}")
        else:
            print(f"  {rk:50s} ({dn:5s}) = {tf.values}")
    return fields


def dump_key_combat_fields(db, record_name, label=""):
    fields = db.get_fields(record_name)
    if fields is None:
        print(f"  [NOT FOUND] {record_name}")
        return None
    if label:
        print(f"\n{'='*80}")
        print(f"  {label}")
        print(f"  Record: {record_name}")
        print(f"{'='*80}")

    combat_prefixes = [
        'charLevel', 'Class', 'templateName', 'FileDescription',
        'monsterClassification', 'mesh',
        'characterLife', 'characterMana', 'characterStrength',
        'characterIntelligence', 'characterDexterity',
        'characterOffensiveAbility', 'characterDefensiveAbility',
        'offensive', 'defensive', 'retaliation',
        'skillName', 'attackSkillName', 'skillLevel',
        'characterAttackSpeed', 'characterRunSpeed', 'characterSpellCast',
        'lootFinger2', 'chanceToEquip', 'dropItems',
        'damageMin', 'damageMax', 'speed', 'handHitDuration',
        'racialBonus',
    ]

    for key, tf in fields.items():
        rk = key.split('###')[0]
        if any(rk.startswith(p) or rk == p for p in combat_prefixes):
            dtype_names = {0: 'int', 1: 'float', 2: 'str', 3: 'bool'}
            dn = dtype_names.get(tf.dtype, f'?{tf.dtype}')
            if len(tf.values) == 1:
                print(f"  {rk:50s} ({dn:5s}) = {tf.values[0]}")
            else:
                print(f"  {rk:50s} ({dn:5s}) = {tf.values}")
    return fields


def load_text_tags(arc_path):
    """Load all text tags from Text_EN.arc."""
    arc = ArcArchive.from_file(arc_path)
    all_tags = {}
    text_files = [
        'commonequipment.txt', 'monsters.txt', 'skills.txt',
        'uniqueequipment.txt', 'ui.txt', 'dialog.txt',
        'install.txt', 'menu.txt', 'npc.txt', 'quest.txt',
        'tutorial.txt', 'xcommonequipment.txt', 'xdialog.txt',
        'xinstall.txt', 'xmenu.txt', 'xmonsters.txt', 'xnpc.txt',
        'xquest.txt', 'xskills.txt', 'xtutorial.txt', 'xui.txt',
        'xuniqueequipment.txt',
    ]
    for fname in text_files:
        text = arc.get_text(fname)
        if text is None:
            continue
        for line in text.split('\n'):
            line = line.strip('\r')
            if not line or line.startswith('//'):
                continue
            if '=' in line:
                k, _, v = line.partition('=')
                all_tags[k.strip()] = v
    return all_tags


# =============================================================================
# PART 1: RAKANIZEUS INVESTIGATION
# =============================================================================
def investigate_rakanizeus(db):
    print("\n" + "#"*80)
    print("# PART 1: RAKANIZEUS INVESTIGATION")
    print("#"*80)

    # 1a) Find ALL records matching "rakanizeus"
    print("\n--- 1a) ALL records matching 'rakanizeus' (case insensitive) ---")
    rakan_records = []
    for name in db.record_names():
        if 'rakanizeus' in name.lower() or 'rakanizeues' in name.lower():
            rakan_records.append(name)
            print(f"  {name}")

    if not rakan_records:
        print("  NO RECORDS FOUND!")
        return

    # Separate into categories
    soul_records = [r for r in rakan_records if 'soul' in r.lower() or 'equipmentring' in r.lower()]
    monster_records = [r for r in rakan_records if 'creature' in r.lower()]
    item_records = [r for r in rakan_records if 'attachitems' in r.lower() or ('item' in r.lower() and r not in soul_records)]
    other_records = [r for r in rakan_records if r not in soul_records and r not in monster_records and r not in item_records]

    print(f"\n  Soul records: {len(soul_records)}")
    print(f"  Monster records: {len(monster_records)}")
    print(f"  Item records: {len(item_records)}")
    print(f"  Other records: {len(other_records)}")

    # 1b) Dump ALL soul record fields
    print("\n--- 1b) SOUL RECORD(S) - FULL FIELD DUMP ---")
    for r in soul_records:
        dump_fields(db, r, f"RAKANIZEUS SOUL: {r}")

    # Also check ring records
    for r in item_records:
        dump_fields(db, r, f"RAKANIZEUS ITEM: {r}")

    # Check ring records that might be souls
    ring_records = [r for r in rakan_records if 'ring' in r.lower() and r not in soul_records]
    for r in ring_records:
        if r not in item_records:
            dump_fields(db, r, f"RAKANIZEUS RING: {r}")

    # 1c) Dump monster record combat fields
    print("\n--- 1c) MONSTER RECORD(S) - KEY COMBAT FIELDS ---")
    for r in monster_records:
        dump_key_combat_fields(db, r, f"RAKANIZEUS MONSTER: {r}")

    for r in other_records:
        dump_fields(db, r, f"RAKANIZEUS OTHER: {r}")

    # 1d) Find other uber souls for comparison
    print("\n--- 1d) COMPARISON: Other uber monster souls ---")
    uber_souls = []
    for name in db.record_names():
        nl = name.lower()
        if ('\\soul\\' in nl or '/soul/' in nl) and 'equipmentring' in nl:
            fields = db.get_fields(name)
            if fields:
                uber_souls.append((name, fields))

    # Also find souls with um_ or uber in the path
    for name in db.record_names():
        nl = name.lower()
        if ('um_' in nl or 'uber' in nl) and ('ring' in nl or 'soul' in nl) and 'equipmentring' in nl:
            if not any(name == s[0] for s in uber_souls):
                fields = db.get_fields(name)
                if fields:
                    uber_souls.append((name, fields))

    print(f"\n  Total soul-type records found: {len(uber_souls)}")

    # Pick some interesting comparison souls
    interesting_keywords = ['typhon', 'hydra', 'hades', 'cerberus', 'medusa', 'manticore',
                           'chimera', 'chimaera', 'cyclops', 'talos', 'arachne', 'scorpos',
                           'dragon', 'charon']
    comparison_souls = []
    for name, fields in uber_souls:
        nl = name.lower()
        if any(kw in nl for kw in interesting_keywords):
            comparison_souls.append((name, fields))

    # Take first 5
    comparison_souls = comparison_souls[:5]

    if not comparison_souls:
        # Fallback: grab any 5 souls
        comparison_souls = uber_souls[:5]

    for name, fields in comparison_souls:
        print(f"\n{'='*80}")
        print(f"  COMPARISON SOUL: {name}")
        print(f"{'='*80}")
        for key, tf in fields.items():
            rk = key.split('###')[0]
            dtype_names = {0: 'int', 1: 'float', 2: 'str', 3: 'bool'}
            dn = dtype_names.get(tf.dtype, f'?{tf.dtype}')
            if len(tf.values) == 1:
                print(f"  {rk:50s} ({dn:5s}) = {tf.values[0]}")
            else:
                print(f"  {rk:50s} ({dn:5s}) = {tf.values}")

    # Print summary of ALL soul paths for reference
    print(f"\n--- ALL soul records in database ({len(uber_souls)} total) ---")
    for name, _ in sorted(uber_souls):
        print(f"  {name}")


def investigate_rakanizeus_built(built_db):
    """Check if Rakanizeus soul exists in the built database."""
    print("\n--- 1e) RAKANIZEUS IN BUILT DATABASE ---")
    rakan_built = []
    for name in built_db.record_names():
        if 'rakanizeus' in name.lower() or 'rakanizeues' in name.lower():
            rakan_built.append(name)

    if not rakan_built:
        print("  NO Rakanizeus records in built database!")
    else:
        for r in rakan_built:
            dump_fields(built_db, r, f"BUILT DB - RAKANIZEUS: {r}")

    # Check for svc_uber souls
    svc_uber_souls = []
    for name in built_db.record_names():
        if 'svc_uber' in name.lower() and 'soul' in name.lower():
            svc_uber_souls.append(name)

    print(f"\n  Total svc_uber soul records in built DB: {len(svc_uber_souls)}")
    for s in sorted(svc_uber_souls)[:20]:
        print(f"    {s}")
    if len(svc_uber_souls) > 20:
        print(f"    ... and {len(svc_uber_souls) - 20} more")


# =============================================================================
# PART 2: MERCENARY SCROLL BREAKDOWN
# =============================================================================
def investigate_merc_scrolls(db, text_tags):
    print("\n" + "#"*80)
    print("# PART 2: MERCENARY SCROLL BREAKDOWN")
    print("#"*80)

    # Find all merc scroll records
    merc_scroll_records = []
    for name in db.record_names():
        nl = name.lower()
        if 'mercscroll' in nl or 'n_mercscroll' in nl:
            merc_scroll_records.append(name)
        elif 'monsterscrolls' in nl and 'miscellaneous' in nl:
            merc_scroll_records.append(name)

    print(f"\n--- All merc scroll item records ({len(merc_scroll_records)}) ---")
    for r in sorted(merc_scroll_records):
        print(f"  {r}")

    # Find merc scroll loot table records
    merc_loot_records = []
    for name in db.record_names():
        nl = name.lower()
        if 'mercscrolls' in nl and 'loottable' in nl:
            merc_loot_records.append(name)

    print(f"\n--- Merc scroll loot table records ({len(merc_loot_records)}) ---")
    for r in sorted(merc_loot_records):
        print(f"  {r}")

    # Display text tags for merc scrolls
    print("\n--- Merc scroll text tags ---")
    scroll_tags = ['tagMercScroll1', 'tagMercScroll2', 'tagMercScroll3',
                   'tagMercScroll4', 'tagMercScroll5', 'tagMercScroll6',
                   'tagMercScroll7', 'tagMercScroll8', 'tagMercScroll9',
                   'tagMercScroll10', 'tagNewItem80', 'tagNewItem81']
    for tag in scroll_tags:
        val = text_tags.get(tag, '[NOT FOUND]')
        print(f"  {tag:30s} = {val}")

    # Also search for any merc-related tags
    print("\n--- All merc-related text tags ---")
    for k, v in sorted(text_tags.items()):
        if 'merc' in k.lower() or 'mercenary' in v.lower() if isinstance(v, str) else False:
            print(f"  {k:40s} = {v}")

    # Dump each scroll's full fields
    print("\n--- DETAILED SCROLL DUMPS ---")
    scroll_items = []
    for name in db.record_names():
        nl = name.lower()
        if ('miscellaneous' in nl or 'artifacts' in nl) and ('mercscroll' in nl or 'monsterscrolls' in nl):
            if 'formula' not in nl and 'loottable' not in nl:
                scroll_items.append(name)

    for r in sorted(scroll_items):
        fields = dump_fields(db, r, f"MERC SCROLL ITEM: {r}")
        if fields:
            # Check what it summons
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if 'skill' in rk.lower() and tf.values and isinstance(tf.values[0], str) and tf.values[0]:
                    skill_path = tf.values[0]
                    print(f"\n    >>> Following skill reference: {skill_path}")
                    skill_fields = db.get_fields(skill_path)
                    if skill_fields:
                        for sk, stf in skill_fields.items():
                            srk = sk.split('###')[0]
                            if 'pet' in srk.lower() or 'spawn' in srk.lower() or 'summon' in srk.lower() or 'Name' in srk:
                                dtype_names = {0: 'int', 1: 'float', 2: 'str', 3: 'bool'}
                                dn = dtype_names.get(stf.dtype, f'?{stf.dtype}')
                                if len(stf.values) == 1:
                                    print(f"      {srk:46s} ({dn:5s}) = {stf.values[0]}")
                                else:
                                    print(f"      {srk:46s} ({dn:5s}) = {stf.values}")

    # Dump loot tables
    print("\n--- LOOT TABLE DETAILS ---")
    for r in sorted(merc_loot_records):
        dump_fields(db, r, f"MERC LOOT TABLE: {r}")

    # Find ALL loot tables that reference merc scrolls
    print("\n--- COMPREHENSIVE LOOT TABLE CROSS-REFERENCES ---")
    scroll_paths_lower = set()
    for r in scroll_items:
        scroll_paths_lower.add(r.lower())

    referencing_tables = []
    for name in db.record_names():
        nl = name.lower()
        if 'loottable' not in nl and 'loot' not in nl:
            continue
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if isinstance(v, str) and v:
                    vl = v.lower()
                    if 'mercscroll' in vl or 'monsterscrolls' in vl:
                        referencing_tables.append((name, key.split('###')[0], v))
                        break

    print(f"\n  Tables referencing merc scrolls: {len(referencing_tables)}")
    for table_name, field, ref in sorted(referencing_tables):
        print(f"\n  TABLE: {table_name}")
        print(f"    Field: {field}")
        print(f"    References: {ref}")
        # Get the weight/chance
        fields = db.get_fields(table_name)
        if fields:
            for key, tf in fields.items():
                rk = key.split('###')[0]
                if 'weight' in rk.lower() or 'chance' in rk.lower():
                    print(f"    {rk}: {tf.values}")

    # Also check misc loot tables and boss loot tables for merc scroll references
    print("\n--- SEARCHING ALL LOOT/DROP RECORDS FOR MERC SCROLL REFERENCES ---")
    all_merc_refs = []
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if isinstance(v, str) and v:
                    vl = v.lower()
                    if ('mercscroll' in vl or 'monsterscrolls' in vl) and name not in [x[0] for x in all_merc_refs]:
                        all_merc_refs.append((name, key.split('###')[0], v))

    print(f"\n  ALL records referencing merc scrolls: {len(all_merc_refs)}")
    for ref_name, field, ref_val in sorted(all_merc_refs):
        print(f"  {ref_name}")
        print(f"    {field} -> {ref_val}")


# =============================================================================
# PART 3: BLOOD MISTRESS UPGRADE
# =============================================================================
def investigate_blood_mistress(db, text_tags):
    print("\n" + "#"*80)
    print("# PART 3: BLOOD MISTRESS UPGRADE (n_mercscroll_euanthe_bloodupgrade)")
    print("#"*80)

    # 3a) Find and dump the blood upgrade record
    blood_records = []
    for name in db.record_names():
        nl = name.lower()
        if 'bloodupgrade' in nl or 'blood_upgrade' in nl:
            blood_records.append(name)
        elif 'euanthe' in nl:
            blood_records.append(name)

    print(f"\n--- All Euanthe/Blood records ({len(blood_records)}) ---")
    for r in sorted(blood_records):
        print(f"  {r}")

    # Dump each one
    for r in sorted(blood_records):
        dump_fields(db, r, f"EUANTHE/BLOOD RECORD: {r}")

    # Check if the blood upgrade is in any formula
    print("\n--- FORMULA RECORDS for Blood Mistress ---")
    for name in db.record_names():
        nl = name.lower()
        if 'bloodmistress' in nl or ('mercupgrade' in nl and 'blood' in nl):
            dump_fields(db, name, f"BLOOD MISTRESS FORMULA: {name}")

    # Check loot tables for blood upgrade
    print("\n--- LOOT TABLE SEARCH for Blood Mistress Upgrade ---")
    blood_refs = []
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            for v in tf.values:
                if isinstance(v, str) and v and ('bloodupgrade' in v.lower() or 'blood_upgrade' in v.lower()):
                    blood_refs.append((name, key.split('###')[0], v))

    if blood_refs:
        print(f"\n  Found {len(blood_refs)} loot table references:")
        for ref_name, field, ref_val in blood_refs:
            print(f"  {ref_name}")
            print(f"    {field} -> {ref_val}")
    else:
        print("\n  *** NO LOOT TABLE REFERENCES FOUND for blood upgrade! ***")

    # Check text tags
    print("\n--- Blood Mistress Text Tags ---")
    for k, v in sorted(text_tags.items()):
        if 'blood' in k.lower() or 'euanthe' in k.lower():
            print(f"  {k:40s} = {v}")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    print("Loading SV 0.98i database...")
    db = ArzDatabase.from_arz(SV_DB_PATH)

    print("\nLoading text tags...")
    text_tags = load_text_tags(TEXT_ARC_PATH)
    print(f"  Loaded {len(text_tags)} text tags")

    investigate_rakanizeus(db)

    if BUILT_DB_PATH.exists():
        print("\nLoading built database...")
        built_db = ArzDatabase.from_arz(BUILT_DB_PATH)
        investigate_rakanizeus_built(built_db)
    else:
        print(f"\n  Built database not found: {BUILT_DB_PATH}")

    investigate_merc_scrolls(db, text_tags)
    investigate_blood_mistress(db, text_tags)

    print("\n" + "="*80)
    print("INVESTIGATION COMPLETE")
    print("="*80)
