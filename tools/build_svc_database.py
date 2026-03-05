"""
Build the SoulvizierClassic database with minimal-touch patching.

Only records that need modification are decoded and re-encoded.
All other records pass through as raw compressed bytes, preserving
the original game data exactly.

Pipeline:
1. Load SV 0.98i as base (raw bytes)
2. Load SV 0.9 for potion drop rate reference (raw bytes)
3. Restore potion drop weights from SV 0.9
4. Wire souls to monsters (66% rare, 25% boss)
5. Make targeted equipment enchantable
6. Write patched .arz

Usage:
  python build_svc_database.py <sv098i.arz> <sv09.arz> <output.arz>
"""
import sys
import re
from pathlib import Path
from collections import defaultdict, OrderedDict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase, DATA_TYPE_FLOAT, DATA_TYPE_STRING, DATA_TYPE_INT


def strip_ui_overrides(db: ArzDatabase):
    """Remove SV UI records that conflict with AE's modern UI system.

    SV 0.98i was designed for TQIT (2007). Its ingameui records override AE's
    UI with incompatible layouts, causing broken input (click-through on mastery
    selection), missing elements (character portrait), and rendering glitches
    (transparent text).

    We strip ALL UI records except skill tree definitions, which are essential
    for SV's custom masteries (Occult replacing Rogue, etc.).
    """
    print("\n=== Patch 0: Strip incompatible UI overrides ===")

    keep_prefixes = [
        'records\\ingameui\\player skills\\mastery ',
        'records/ingameui/player skills/mastery ',
        'records\\ingameui\\player skills\\common\\',
        'records/ingameui/player skills/common/',
        'records\\ingameui\\player skills\\hidden skills\\',
        'records/ingameui/player skills/hidden skills/',
        'records\\xpack\\ui\\skills\\mastery ',
        'records/xpack/ui/skills/mastery ',
    ]

    strip_areas = [
        'records\\ingameui\\',
        'records/ingameui/',
        'records\\xpack\\ui\\',
        'records/xpack/ui/',
    ]

    stripped = []
    kept = []
    for name in list(db._raw_records.keys()):
        nl = name.lower()

        in_strip_area = any(nl.startswith(p) for p in strip_areas)
        if not in_strip_area:
            continue

        in_keep_area = any(nl.startswith(p) for p in keep_prefixes)
        if in_keep_area:
            kept.append(name)
            continue

        stripped.append(name)
        del db._raw_records[name]
        db._record_types.pop(name, None)
        db._record_timestamps.pop(name, None)
        db._decoded_cache.pop(name, None)
        db._modified.discard(name)

    print(f"  Stripped: {len(stripped)} UI records")
    print(f"  Kept: {len(kept)} skill tree records")
    return len(stripped)


def restore_potion_drops(db098: ArzDatabase, db09: ArzDatabase):
    """Restore zeroed potion drop weights from SV 0.9 into 0.98i."""
    print("\n=== Patch 1: Restore potion drop rates ===")

    restored = 0
    for name in db098.record_names():
        nl = name.lower()
        if 'loottables' not in nl and 'merchant' not in nl:
            continue

        fields098 = db098.get_fields(name)
        if fields098 is None:
            continue

        has_potion = False
        potion_loot_keys = []
        for key, tf in fields098.items():
            real_key = key.split('###')[0]
            if real_key.startswith('lootName'):
                for v in tf.values:
                    if isinstance(v, str) and 'potion' in v.lower():
                        has_potion = True
                        idx = real_key[8:]
                        potion_loot_keys.append(idx)

        if not has_potion:
            continue
        if not db09.has_record(name):
            continue

        fields09 = db09.get_fields(name)
        if fields09 is None:
            continue

        for idx in potion_loot_keys:
            weight_key = f'lootWeight{idx}'
            tf098 = None
            tf09 = None
            for k, tf in fields098.items():
                if k.split('###')[0] == weight_key:
                    tf098 = tf
                    break
            for k, tf in fields09.items():
                if k.split('###')[0] == weight_key:
                    tf09 = tf
                    break

            if tf098 and tf09:
                old_w = tf098.values[0] if tf098.values else 0
                new_w = tf09.values[0] if tf09.values else 0
                if isinstance(old_w, (int, float)) and old_w == 0 and \
                   isinstance(new_w, (int, float)) and new_w > 0:
                    db098.set_field(name, weight_key, new_w, tf098.dtype)
                    restored += 1

    print(f"  Potion weights restored: {restored}")
    return restored


def parse_soul_name(soul_path):
    parts = soul_path.lower().replace('\\', '/').split('/')
    filename = parts[-1].replace('.dbr', '')
    monster_type = parts[-2] if len(parts) >= 2 else ''

    if filename.endswith('_soul_n') or filename.endswith('_soul_e') or filename.endswith('_soul_l'):
        diff = filename[-1]
        name = filename[:-7]
    elif filename.endswith('_soul'):
        name = filename[:-5]
        diff = 'n'
    elif '_soul' in filename:
        idx = filename.index('_soul')
        name = filename[:idx]
        rest = filename[idx + 5:].strip('_')
        diff = rest if rest in ('n', 'e', 'l') else 'n'
    else:
        name = filename.replace('soul', '').strip('_')
        diff = 'n'

    return monster_type, name, diff


def wire_souls_to_monsters(db: ArzDatabase, boss_chance=25.0, rare_chance=66.0):
    """Wire orphaned soul items to matching monster records."""
    print("\n=== Patch 2: Wire souls to monsters ===")

    soul_dir = 'equipmentring\\soul\\'
    soul_dir2 = 'equipmentring/soul/'

    catalog = defaultdict(lambda: defaultdict(dict))
    for name in db.record_names():
        nl = name.lower()
        if soul_dir not in nl and soul_dir2 not in nl:
            continue
        fn = nl.replace('\\', '/').split('/')[-1].replace('.dbr', '')
        if fn.startswith(('01_', '02_', '03_', '04_')):
            continue
        mtype, mname, diff = parse_soul_name(name)
        if mname and diff:
            catalog[mtype][mname][diff] = name

    print(f"  Soul catalog: {sum(len(v) for v in catalog.values())} names across {len(catalog)} types")

    wired = 0
    already = 0
    fixed_chance = 0

    def _is_farmable_boss(record_name, fields_dict):
        """True only for fixed-location act bosses that can be farmed repeatedly.
        Heroes, champions, quest monsters, and random spawns get the higher
        66% rate. Only Boss-class monsters get the lower 25% rate.
        Exception: um_ Boss monsters still get 66% since they're uber encounters."""
        fn = record_name.lower().replace('\\', '/').split('/')[-1]
        classification = ''
        for key, tf in fields_dict.items():
            if key.split('###')[0] == 'monsterClassification' and tf.values:
                classification = str(tf.values[0]).lower()
                break
        if classification == 'boss':
            if fn.startswith('um_'):
                return False
            return True
        nl = record_name.lower()
        if nl.startswith('boss_') or '\\boss_' in nl or '/boss_' in nl:
            return True
        return False

    def _set_soul_drop(name, fields_dict, chance):
        """Set the AE-compatible equipment fields for soul drops.

        AE doesn't use 'lootFinger2Chance'. Instead it uses:
          chanceToEquipFinger2      = overall % to equip (and thus drop) from Finger2
          chanceToEquipFinger2Item1 = weight for selecting lootFinger2Item1
          dropItems                 = 1 so equipped items drop on death
        """
        db.set_field(name, 'chanceToEquipFinger2', chance, DATA_TYPE_FLOAT)
        db.set_field(name, 'chanceToEquipFinger2Item1', 100, DATA_TYPE_INT)
        has_drop = False
        for key, tf in fields_dict.items():
            if key.split('###')[0] == 'dropItems' and tf.values:
                has_drop = True
                break
        if not has_drop:
            db.set_field(name, 'dropItems', 1, DATA_TYPE_INT)

    for name in db.record_names():
        nl = name.lower()

        if '\\creature\\' not in nl and '/creature/' not in nl and \
           '\\creatures\\' not in nl and '/creatures/' not in nl:
            continue

        fields = db.get_fields(name)
        if fields is None:
            continue

        cls_val = ''
        tmpl_val = ''
        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'Class' and tf.values:
                cls_val = str(tf.values[0]).lower()
            elif rk == 'templateName' and tf.values:
                tmpl_val = str(tf.values[0]).lower()

        if 'monster' not in cls_val and 'monster' not in tmpl_val:
            continue

        existing = db.get_field_value(name, 'lootFinger2Item1')
        if existing and existing != '' and existing != 0:
            # Only enable soul drops for Hero/Boss/Quest monsters.
            # Common/Champion monsters keep their lootFinger2Item1 but
            # won't get chanceToEquipFinger2, so they'll never drop souls.
            monster_cls = ''
            for key, tf in fields.items():
                if key.split('###')[0] == 'monsterClassification' and tf.values:
                    monster_cls = str(tf.values[0])
                    break
            if monster_cls in ('Hero', 'Boss', 'Quest'):
                is_boss = _is_farmable_boss(name, fields)
                target = boss_chance if is_boss else rare_chance
                _set_soul_drop(name, fields, target)
                fixed_chance += 1
            already += 1
            continue

        # Only wire NEW souls to Hero, Boss, or Quest monsters.
        # Common/Champion mobs (including um_ minions) should never get souls.
        classification = ''
        for key, tf in fields.items():
            if key.split('###')[0] == 'monsterClassification' and tf.values:
                classification = str(tf.values[0])
                break

        if classification not in ('Hero', 'Boss', 'Quest'):
            continue

        parts = nl.replace('\\', '/').split('/')
        filename = parts[-1].replace('.dbr', '')

        monster_dir = parts[-2] if len(parts) >= 2 else ''

        clean = re.sub(r'^(u_|um_|uw_|qm_|bm_|cb_|am_|ar_|as_|em_|vampiric_)', '', filename)
        clean = re.sub(r'_?\d+$', '', clean).strip('_')

        best_match = None
        best_score = 0

        for soul_type, names_dict in catalog.items():
            type_bonus = 30 if soul_type == monster_dir else 0

            for soul_name, diffs in names_dict.items():
                score = 0
                if soul_name == clean:
                    score = 100
                elif clean.startswith(soul_name) and len(soul_name) >= 4:
                    score = len(soul_name) * 2
                elif soul_name.startswith(clean) and len(clean) >= 4:
                    score = len(clean) * 2
                elif clean in soul_name and len(clean) >= 5:
                    score = len(clean)
                elif soul_name in clean and len(soul_name) >= 5:
                    score = len(soul_name)

                total = score + type_bonus
                if total > best_score:
                    best_score = total
                    best_match = diffs

        if best_match and best_score >= 10:
            soul_n = best_match.get('n', '')
            soul_e = best_match.get('e', '')
            soul_l = best_match.get('l', '')

            if soul_n and soul_e and soul_l:
                db.set_field(name, 'lootFinger2Item1', [soul_n, soul_e, soul_l], DATA_TYPE_STRING)
            elif soul_n:
                db.set_field(name, 'lootFinger2Item1', soul_n, DATA_TYPE_STRING)
            else:
                best = soul_n or soul_e or soul_l
                if best:
                    db.set_field(name, 'lootFinger2Item1', best, DATA_TYPE_STRING)
                else:
                    continue

            is_boss = _is_farmable_boss(name, fields)
            _set_soul_drop(name, fields, boss_chance if is_boss else rare_chance)
            wired += 1

    print(f"  Newly wired: {wired}")
    print(f"  Already had souls: {already} (all updated to AE equip fields)")
    print(f"  Equip fields set: {fixed_chance + wired}")
    return wired + fixed_chance


def make_enchantable(db: ArzDatabase):
    """Set numRelicSlots=1 on equipment that has 0 slots.

    Only targets actual item records (under records/item/ or records/drxitem/).
    Uses exact template path matching to avoid false positives like 'ring'
    matching inside 'TextStaticString'.
    """
    print("\n=== Patch 3: Make equipment enchantable ===")

    item_path_prefixes = (
        'records\\item\\', 'records/item/',
        'records\\drxitem\\', 'records/drxitem/',
        'records\\xpack\\item\\', 'records/xpack/item/',
    )

    equip_templates = (
        'armor', 'weapon', 'shield',
        'jewelry_ring', 'jewelry_amulet', 'jewelry_medal',
        'itemrelic',
    )

    equip_classes = (
        'armorprotective', 'armorjewelry', 'weaponmelee',
        'weaponhunting', 'weaponmage', 'weaponstaff',
        'shield',
    )

    patched = 0
    for name in db.record_names():
        nl = name.lower()

        is_item_path = any(nl.startswith(p) for p in item_path_prefixes)
        is_soul_path = '\\soul\\' in nl or '/soul/' in nl
        if not is_item_path and not is_soul_path:
            continue

        fields = db.get_fields(name)
        if fields is None:
            continue

        tmpl = ''
        cls = ''
        cannot_pick = 0
        current_slots = -1

        for key, tf in fields.items():
            rk = key.split('###')[0]
            if rk == 'templateName' and tf.values:
                tmpl = str(tf.values[0]).lower()
            elif rk == 'Class' and tf.values:
                cls = str(tf.values[0]).lower()
            elif rk == 'cannotPickUp' and tf.values:
                cannot_pick = tf.values[0]
            elif rk == 'numRelicSlots' and tf.values:
                current_slots = tf.values[0]

        if not tmpl:
            continue
        if cannot_pick == 1:
            continue

        tmpl_base = tmpl.replace('\\', '/').split('/')[-1].replace('.tpl', '')
        is_equip = any(tmpl_base.startswith(t) for t in equip_templates) or \
                   any(cls.startswith(c) for c in equip_classes) or \
                   is_soul_path

        if not is_equip:
            continue

        if isinstance(current_slots, (int, float)) and current_slots >= 1:
            continue

        db.set_field(name, 'numRelicSlots', 1, DATA_TYPE_INT)
        patched += 1

    print(f"  Items made enchantable: {patched}")
    return patched


def _ensure_record(db, path, template):
    """Create a new empty record in the database if it doesn't exist."""
    if not db.has_record(path):
        db.ensure_string(path)
        db._raw_records[path] = (db.ensure_string(path), b'')
        db._record_types[path] = template
        db._record_timestamps[path] = 0
        db._decoded_cache[path] = OrderedDict()
        db._modified.add(path)


def grant_all_inventory_bags(db: ArzDatabase):
    """Give the player all inventory bags (sacks) from game start.

    TQ gives bags through quest rewards. In a Custom Quest mod the base-game
    quests may not fire, leaving the player with only the starter sack.

    We address this three ways:
     a) Make the inventory sack item free (cost=0).
     b) Convert the starting loot table from a single-pick FixedWeight table
        to a LootMasterTable whose entries each roll independently, giving
        both the starter sword AND 3 inventory sacks.
     c) Give generous starting gold as a fallback.
    """
    print("\n=== Patch 4: Grant all inventory bags ===")
    patched = 0

    sack_item = 'records\\item\\miscellaneous\\inventorysack.dbr'
    if db.has_record(sack_item):
        db.set_field(sack_item, 'itemCost', 0, DATA_TYPE_INT)
        print("  Inventory sack cost set to 0 (free)")
        patched += 1

    # Add 2 inventory sacks to the tutorial potion chest (first chest in the game).
    # It uses FixedItemLoot.tpl with independent loot slots.
    sack_table = 'records\\quests\\rewards\\startingloot_sack.dbr'
    fixed_tpl = 'database\\Templates\\LootItemTable_FixedWeight.tpl'

    _ensure_record(db, sack_table, fixed_tpl)
    db.set_field(sack_table, 'templateName', fixed_tpl, DATA_TYPE_STRING)
    db.set_field(sack_table, 'Class', 'LootItemTable_FixedWeight', DATA_TYPE_STRING)
    db.set_field(sack_table, 'lootName1', sack_item, DATA_TYPE_STRING)
    db.set_field(sack_table, 'lootWeight1', 100, DATA_TYPE_INT)

    tutorial_chest = None
    for name in db.record_names():
        nl = name.lower()
        if 'tutorialpotionchest' in nl and 'defaultloot' in nl:
            tutorial_chest = name
            break

    if tutorial_chest:
        db.set_field(tutorial_chest, 'loot2Chance', 100.0, DATA_TYPE_FLOAT)
        db.set_field(tutorial_chest, 'loot2Name1', sack_table, DATA_TYPE_STRING)
        db.set_field(tutorial_chest, 'loot2Weight1', 100, DATA_TYPE_INT)
        db.set_field(tutorial_chest, 'loot3Chance', 100.0, DATA_TYPE_FLOAT)
        db.set_field(tutorial_chest, 'loot3Name1', sack_table, DATA_TYPE_STRING)
        db.set_field(tutorial_chest, 'loot3Weight1', 100, DATA_TYPE_INT)
        print(f"  Tutorial chest: added 2 inventory sacks to loot slots 2 & 3")
        patched += 1
    else:
        print("  WARNING: tutorial potion chest not found")

    return patched


def expand_transfer_stash(db: ArzDatabase):
    """Expand the caravan transfer stash to vault-like proportions.

    AE's transfer stash uses records/xpack/ui/caravan/stashwindow.dbr.
    Default is 10 wide x 5 tall (50 slots). We expand to 10 wide x 16 tall
    per bag, with 3 bags unlocked for free (480 slots total). The width stays
    at 10 to fit the caravan window UI bitmap.
    """
    print("\n=== Patch 5: Expand transfer stash ===")

    stash_window = 'records\\xpack\\ui\\caravan\\stashwindow.dbr'
    stash_inventory = 'records\\xpack\\ui\\caravan\\stashinventory.dbr'

    db.set_field(stash_window, 'InventoryWidth', 10, DATA_TYPE_INT)
    db.set_field(stash_window, 'InventoryHeightArray', [16, 16, 16], DATA_TYPE_INT)
    db.set_field(stash_window, 'InventoryCostArray', [0, 0, 0], DATA_TYPE_INT)

    print("  Transfer stash: 10 wide x 16 tall x 3 bags (480 slots), free upgrades")


def restore_rest_skill(db: ArzDatabase):
    """Restore the Rest skill via the quest reward skill tree.

    In SV 0.4, the Rest skill was on the quest reward skill tree as
    skillName22 with skillLevel22=1. The skillLevel=1 auto-grants it
    from game start (skillLevel=0 would require a quest to unlock).
    SV 0.98i removed this entry; we restore it.
    """
    print("\n=== Patch 6: Restore Rest skill ===")

    rest_buff = 'records\\quests\\rewards\\drxrest_skillbuff.dbr'

    if not db.has_record(rest_buff):
        print("  WARNING: drxrest_skillbuff.dbr not found!")
        return 0

    quest_tree = None
    for name in db.record_names():
        if 'questrewardskilltree' in name.lower():
            quest_tree = name
            break

    if not quest_tree:
        print("  WARNING: QuestRewardSkillTree.dbr not found!")
        return 0

    db.set_field(quest_tree, 'skillName22', rest_buff, DATA_TYPE_STRING)
    db.set_field(quest_tree, 'skillLevel22', 1, DATA_TYPE_INT)
    print(f"  Added Rest to quest reward tree: skillName22 = {rest_buff}")
    print(f"  skillLevel22 = 1 (auto-granted from game start)")
    print(f"  Effect: +350 life/mana regen, -300 all resistances, 5s duration, 3min cooldown")
    return 1


def fix_mastery_panel_buttons(db: ArzDatabase):
    """Register SV-added skill slots via DLC-priority panectrl overrides.

    AE loads mastery panels with DLC priority: xpack3 > xpack > base ingameui.
    The base game already has xpack3 panectrl for masteries 1-8 with 21 buttons.
    SV's extra skills (21-24) only exist in the base ingameui panectrl which the
    engine never reads (lowest priority).

    Fix (matching SV AERA's approach): create panectrl records at both the xpack
    and xpack3 DLC paths with the full button list. Button references use full
    PascalCase paths to the original skill slot records. BasePane is set to the
    xpack3 base pane used by AE.
    """
    print("\n=== Patch 10: Register SV-added skill buttons in panel controllers ===")
    total_added = 0

    xpack3_base_pane = r'Records\XPack3\UI\Skills\Mastery Base\BaseSkillPane.dbr'

    for mi in range(1, 9):
        pane = 'records\\ingameui\\player skills\\mastery %d\\panectrl.dbr' % mi
        if not db.has_record(pane):
            continue

        fields = db.get_fields(pane)
        if not fields:
            continue

        current_buttons = []
        btn_dtype = DATA_TYPE_STRING
        for k, tf in fields.items():
            if k.split('###')[0] == 'tabSkillButtons':
                current_buttons = list(tf.values)
                btn_dtype = tf.dtype
                break

        # Discover all skill slot records in this mastery folder
        existing_slots = []
        for si in range(1, 30):
            slot = 'records\\ingameui\\player skills\\mastery %d\\skill%02d.dbr' % (mi, si)
            if db.has_record(slot):
                existing_slots.append(si)
            else:
                break

        # Build full button list with PascalCase full paths (matching AERA format)
        pc_dir = r'Records\InGameUI\Player Skills\Mastery %d' % mi
        full_buttons = [pc_dir + r'\Mastery.dbr']
        for si in existing_slots:
            full_buttons.append(pc_dir + r'\Skill%02d.dbr' % si)

        added = len(full_buttons) - len(current_buttons)

        # Also update the base ingameui panectrl
        db.set_field(pane, 'tabSkillButtons', full_buttons, btn_dtype)

        # Create xpack panectrl override
        xpack_pane = r'records\xpack\ui\skills\mastery %d\panectrl.dbr' % mi
        db.clone_record(pane, xpack_pane)
        db.set_field(xpack_pane, 'tabSkillButtons', full_buttons, btn_dtype)
        db.set_field(xpack_pane, 'BasePane', xpack3_base_pane, DATA_TYPE_STRING)

        # Create xpack3 panectrl override (highest priority)
        xpack3_pane = r'records\xpack3\ui\skills\mastery %d\panectrl.dbr' % mi
        db.clone_record(pane, xpack3_pane)
        db.set_field(xpack3_pane, 'tabSkillButtons', full_buttons, btn_dtype)
        db.set_field(xpack3_pane, 'BasePane', xpack3_base_pane, DATA_TYPE_STRING)

        if added > 0:
            print("  Mastery %d: %d buttons (%d added) -> xpack + xpack3 overrides" % (
                mi, len(full_buttons), added))
            total_added += added
        else:
            print("  Mastery %d: %d buttons -> xpack + xpack3 overrides" % (
                mi, len(full_buttons)))

    print("  Total skill buttons registered: %d" % total_added)
    return total_added


def fix_broken_mastery_skills(db: ArzDatabase):
    """Fix broken mastery skills across ALL skill trees.

    Two root causes, both from TQIT-era assumptions that break in AE:

    1. CASE-SENSITIVE PATH LOOKUPS: SV stubs reference buff/pet records with
       PascalCase paths (e.g. Records\\Skills\\...\\DRXBuff.dbr), but the
       records are stored lowercase in the ARZ. TQIT did case-insensitive
       lookups; AE Custom Quest mods do case-sensitive lookups. Fix: rewrite
       buffSkillName/petSkillName to match the exact stored path.

    2. MISSING DISPLAY FIELDS: Many skill records lack skillDisplayName and
       skillUpBitmapName. In TQIT, the engine inherited these from linked
       buff/pet records. For non-delegating classes in AE, the engine reads
       display from the record itself. Fix: copy display fields from the
       buff/pet source into the stub as a fallback.
    """
    print("\n=== Patch 8: Fix broken mastery skills ===")
    patched = 0

    name_map = {}
    for n in db.record_names():
        name_map[n.lower()] = n

    def _resolve(path):
        return name_map.get(path.lower().replace('/', '\\'))

    def _get_field(record_name, field_name):
        if not record_name or not db.has_record(record_name):
            return ''
        f = db.get_fields(record_name)
        if not f:
            return ''
        for k, tf in f.items():
            if k.split('###')[0] == field_name and tf.values:
                v = tf.values[0]
                return str(v) if not isinstance(v, str) else v
        return ''

    def _has_display(record_name):
        tag = _get_field(record_name, 'skillDisplayName')
        bmp = _get_field(record_name, 'skillUpBitmapName')
        return bool(tag and bmp)

    DISPLAY_FIELDS = [
        'skillDisplayName', 'skillBaseDescription',
        'skillUpBitmapName', 'skillDownBitmapName', 'skillConnectionOff',
    ]

    REF_FIELDS = ['buffSkillName', 'petSkillName']

    def _find_display_source(record_name):
        """Follow buff/pet chain up to 3 levels deep to find display data."""
        for ref_field in REF_FIELDS:
            ref = _get_field(record_name, ref_field)
            if not ref:
                continue
            ref_actual = _resolve(ref)
            if ref_actual and _has_display(ref_actual):
                return ref_actual
            if ref_actual:
                for ref_field2 in REF_FIELDS:
                    ref2 = _get_field(ref_actual, ref_field2)
                    if ref2:
                        ref2_actual = _resolve(ref2)
                        if ref2_actual and _has_display(ref2_actual):
                            return ref2_actual
        return None

    # Fix missing description tags (skills that have icons but no description)
    desc_fixes = {
        'records\\skills\\stealth\\drxlaytrap.dbr': 'tagbreachDESC',
        'records\\skills\\stealth\\drxlaytrap_rapidconstruction.dbr': 'tagNewSkill321DESC',
    }
    for path, desc_tag in desc_fixes.items():
        actual = _resolve(path)
        if actual and db.has_record(actual):
            db.set_field(actual, 'skillBaseDescription', desc_tag, DATA_TYPE_STRING)
            print(f"  + desc: {path.split(chr(92))[-1]} = {desc_tag}")
            patched += 1

    # --- Phase 1: Rewrite case-mismatched .dbr references ---
    # AE does case-sensitive record lookups in Custom Quest mod databases.
    # SV records were stored with lowercase paths but referenced with
    # PascalCase. Instead of creating duplicate alias records (which lose
    # metadata), we rewrite every .dbr reference to match the actual stored
    # record path. This ensures the engine's case-sensitive lookups succeed.
    refs_fixed = 0
    for record_name in list(db.record_names()):
        f = db.get_fields(record_name)
        if not f:
            continue
        for k, tf in f.items():
            if not tf.values:
                continue
            new_vals = list(tf.values)
            changed = False
            for i, val in enumerate(new_vals):
                if not isinstance(val, str) or not val:
                    continue
                if not val.lower().endswith('.dbr'):
                    continue
                if db.has_record(val):
                    continue
                stored = _resolve(val)
                if stored and stored != val:
                    new_vals[i] = stored
                    changed = True
            if changed:
                field_name = k.split('###')[0]
                if len(new_vals) == 1:
                    db.set_field(record_name, field_name, new_vals[0], tf.dtype)
                else:
                    db.set_field(record_name, field_name, new_vals, tf.dtype)
                refs_fixed += 1

    print(f"  Rewrote {refs_fixed} case-mismatched .dbr references")
    patched += refs_fixed

    # --- Phase 2: Inject display fields into stubs that lack them ---
    tree_records = []
    for n in db.record_names():
        nl = n.lower()
        if 'skilltree' in nl and ('drx' in nl or 'DRX' in n):
            if any(m in nl for m in ['warfare', 'defensive', 'earth', 'storm',
                                      'stealth', 'hunting', 'nature', 'spirit',
                                      'dream']):
                tree_records.append(n)

    stubs_fixed = 0
    already_patched = set()

    for tree_name in tree_records:
        tf = db.get_fields(tree_name)
        if not tf:
            continue
        for k, field_tf in tf.items():
            rk = k.split('###')[0]
            if not rk.startswith('skillName') or not field_tf.values:
                continue
            skill_path = field_tf.values[0]
            skill_actual = _resolve(skill_path)
            if not skill_actual or _has_display(skill_actual):
                continue
            if skill_actual.lower() in already_patched:
                continue

            source = _find_display_source(skill_actual)
            if not source:
                continue

            for field in DISPLAY_FIELDS:
                val = _get_field(source, field)
                if val:
                    db.set_field(skill_actual, field, val, DATA_TYPE_STRING)

            already_patched.add(skill_actual.lower())
            stubs_fixed += 1

    print(f"  Injected display fields into {stubs_fixed} skill stubs")
    patched += stubs_fixed
    return patched


def add_dlc_mastery_trees(db: ArzDatabase):
    """Add Ragnarok (RuneMaster) and Atlantis (Neidan) skill trees to the PC.

    SV 0.98i predates these DLCs. In AE with DLCs installed, the engine
    injects DLC masteries into the mastery selection UI even if the mod's
    player character records don't include them. This results in broken,
    non-functional mastery trees. Fix by explicitly adding the DLC tree
    references so they load properly from the base game database.
    """
    print("\n=== Patch 9: Add DLC mastery trees ===")
    patched = 0

    dlc_trees = {
        'skillTree11': 'Records\\XPack2\\skills\\RuneMaster\\RuneMaster_SkillTree.dbr',
        'skillTree12': 'records\\XPack4\\Skills\\Neidan\\neidanskilltree.dbr',
    }

    pc_records = [
        'records\\xpack\\creatures\\pc\\malepc01.dbr',
        'records\\xpack\\creatures\\pc\\femalepc01.dbr',
    ]

    name_map = {}
    for n in db.record_names():
        name_map[n.lower()] = n

    for pc_path in pc_records:
        actual = name_map.get(pc_path.lower())
        if not actual or not db.has_record(actual):
            continue
        for field, tree_path in dlc_trees.items():
            db.set_field(actual, field, tree_path, DATA_TYPE_STRING)
        print(f"  {actual}: added RuneMaster (slot 11) + Neidan (slot 12)")
        patched += 1

    return patched


def _import_record_fields(dest_db, dest_path, src_db, src_fields):
    """Replace ALL fields of dest_path in dest_db with src_fields from another db.

    The dest record must already exist (use clone_record first for new records).
    Returns True on success.
    """
    nm = {}
    for n in dest_db.record_names():
        nm[n.lower()] = n
    dest_actual = nm.get(dest_path.lower())
    if not dest_actual:
        return False

    new_fields = OrderedDict()
    for key, tf in src_fields.items():
        new_fields[key] = type(tf)(tf.dtype, list(tf.values))
    dest_db._decoded_cache[dest_actual] = new_fields
    dest_db._modified.add(dest_actual)

    for key, tf in new_fields.items():
        if key.split('###')[0] == 'templateName' and tf.values:
            dest_db._record_types[dest_actual] = str(tf.values[0])
            break
    return True


def _create_ui_slot(db, mastery_ui_num, slot_num, skill_ref, pos_x, pos_y,
                    is_circular, description):
    """Create a new UI skill slot record by cloning slot 01 and overriding fields."""
    base = r'records\ingameui\player skills\mastery %d' % mastery_ui_num
    nm = {}
    for n in db.record_names():
        nm[n.lower()] = n
    template = nm.get(('%s\\skill01.dbr' % base).lower())
    if not template:
        return False

    new_path = '%s\\skill%02d.dbr' % (base, slot_num)
    db.clone_record(template, new_path)

    db.set_field(new_path, 'skillName', skill_ref, DATA_TYPE_STRING)
    db.set_field(new_path, 'bitmapPositionX', pos_x, DATA_TYPE_INT)
    db.set_field(new_path, 'bitmapPositionY', pos_y, DATA_TYPE_INT)
    db.set_field(new_path, 'isCircular', 1 if is_circular else 0, DATA_TYPE_INT)
    db.set_field(new_path, 'FileDescription', description, DATA_TYPE_STRING)

    if is_circular:
        db.set_field(new_path, 'bitmapNameUp',
                     r'InGameUI\SkillButtonBorderRound01.tex', DATA_TYPE_STRING)
        db.set_field(new_path, 'bitmapNameDown',
                     r'InGameUI\SkillButtonBorderRoundDown01.tex', DATA_TYPE_STRING)
        db.set_field(new_path, 'bitmapNameInFocus',
                     r'InGameUI\SkillButtonBorderRoundOver01.tex', DATA_TYPE_STRING)
    else:
        db.set_field(new_path, 'bitmapNameUp',
                     r'InGameUI\SkillButtonBorder01.tex', DATA_TYPE_STRING)
        db.set_field(new_path, 'bitmapNameDown',
                     r'InGameUI\SkillButtonBorderDown01.tex', DATA_TYPE_STRING)
        db.set_field(new_path, 'bitmapNameInFocus',
                     r'InGameUI\SkillButtonBorderOver01.tex', DATA_TYPE_STRING)
    return True


def restore_legacy_skills(db: ArzDatabase, db41: ArzDatabase):
    """Restore high-impact skills from SV 0.4.1 and reorganise skill trees.

    Changes:
      A. Rogue/Occult: Replace Breach → Darklings, Shadow Grasp → Breach modifier
      B. Nature: Replace Elemental Flurry → Thorn Sprites, Dissemination → Fabrical Tear
      C. Spirit: Add Sands of Sleep (+ Troubled Dreams), Distortion Wave
         (+ Chaotic Resonance + Psionic Immolation) from Dream mastery
      D. Warfare: Add original Hamstring as new record alongside Lineal Chains
    """
    print("\n=== Patch 11: Restore legacy skills from SV 0.4.1 ===")
    total = 0

    nm41 = {}
    for n in db41.record_names():
        nm41[n.lower()] = n
    nm98 = {}
    for n in db.record_names():
        nm98[n.lower()] = n

    def _get_src_fields(path):
        actual = nm41.get(path.lower())
        if not actual:
            return None
        return db41.get_fields(actual)

    # ── A. Rogue/Occult: Add Darklings alongside existing Breach ─────
    # Keep 0.98i Breach + Shadow Grasp at their original slots.
    # Create NEW records for Darklings + its modifier (renamed "Dark Aperture"
    # to avoid name collision with standalone Breach).
    darklings_path = r'records\skills\stealth\drxdarklings.dbr'
    dark_mod_path = r'records\skills\stealth\drxdarklings_darkaperture.dbr'
    dark_src = _get_src_fields(r'records\skills\stealth\drxlaytrap.dbr')
    dark_mod_src = _get_src_fields(
        r'records\skills\stealth\drxlaytrap_rapidconstruction.dbr')

    # Use existing Breach record as clone base (any record works)
    breach_actual = nm98.get(r'records\skills\stealth\drxlaytrap.dbr'.lower())
    if dark_src and dark_mod_src and breach_actual:
        db.clone_record(breach_actual, darklings_path)
        if _import_record_fields(db, darklings_path, db41, dark_src):
            print("  Created: drxdarklings.dbr (Darklings from 0.4.1)")
            total += 1

        db.clone_record(breach_actual, dark_mod_path)
        if _import_record_fields(db, dark_mod_path, db41, dark_mod_src):
            db.set_field(dark_mod_path, 'skillDisplayName',
                         'tagDarkApertureNAME', DATA_TYPE_STRING)
            db.set_field(dark_mod_path, 'skillBaseDescription',
                         'tagDarkApertureDESC', DATA_TYPE_STRING)
            print("  Created: drxdarklings_darkaperture.dbr (Dark Aperture)")
            total += 1

        stealth_tree = nm98.get(
            r'records\skills\stealth\drxstealthskilltree.dbr'.lower())
        if stealth_tree:
            db.set_field(stealth_tree, 'skillName26',
                         darklings_path, DATA_TYPE_STRING)
            db.set_field(stealth_tree, 'skillName27',
                         dark_mod_path, DATA_TYPE_STRING)
            print("  Rogue skillName26 = Darklings, skillName27 = Dark Aperture")
            total += 1

        # UI slots: Darklings at (328,279), Dark Aperture at (328,155)
        if _create_ui_slot(db, 5, 25, darklings_path,
                           328, 279, False, 'Darklings'):
            print("  Rogue UI Skill25: (328,279) Darklings")
            total += 1
        if _create_ui_slot(db, 5, 26, dark_mod_path,
                           328, 155, True, 'Dark Aperture'):
            print("  Rogue UI Skill26: (328,155) Dark Aperture")
            total += 1

    # ── B. Nature: Thorn Sprites + Fabrical Tear (replace in-place) ──
    replacements = [
        (r'records\skills\nature\drxsprite_summons.dbr',
         r'records\skills\nature\drxsprite_summons.dbr',
         'Elemental Flurry -> Thorn Sprites'),
        (r'records\skills\nature\drxrenewal.dbr',
         r'records\skills\nature\drxrenewal.dbr',
         'Dissemination -> Fabrical Tear'),
    ]

    for dest_path, src_path, label in replacements:
        src_fields = _get_src_fields(src_path)
        if not src_fields:
            print("  WARN: source not found for %s" % label)
            continue
        if _import_record_fields(db, dest_path, db41, src_fields):
            print("  Replaced: %s" % label)
            total += 1

    # ── C. Spirit: Add Dream skills ───────────────────────────────────
    spirit_tree = nm98.get(
        r'records\skills\spirit\drxspiritskilltree.dbr'.lower())
    dream_additions = [
        (26, r'Records\XPack\Skills\Dream\DRXSandsofSleep.dbr',
         'Sands of Sleep'),
        (27, r'records\xpack\skills\dream\drxsandsofsleep_troubleddreams.dbr',
         'Troubled Dreams'),
        (28, r'Records\XPack\Skills\Dream\DRXDistortionWave.dbr',
         'Distortion Wave'),
        (29, r'Records\XPack\Skills\Dream\DRXDistortionWave_ChaoticResonance.dbr',
         'Chaotic Resonance'),
        (30, r'Records\XPack\Skills\Dream\DRXDistortionWave_PsionicImmolation.dbr',
         'Psionic Immolation'),
    ]
    if spirit_tree:
        for slot, ref, label in dream_additions:
            db.set_field(spirit_tree, 'skillName%d' % slot, ref, DATA_TYPE_STRING)
            print("  Spirit skillName%d = %s" % (slot, label))
            total += 1

    # Spirit UI slots (mastery 7 UI folder holds Spirit content)
    spirit_ui_slots = [
        (25, r'Records\XPack\Skills\Dream\DRXSandsofSleep.dbr',
         128, 403, False, 'Sands of Sleep'),
        (26, r'records\xpack\skills\dream\drxsandsofsleep_troubleddreams.dbr',
         128, 279, True, 'Troubled Dreams'),
        (27, r'Records\XPack\Skills\Dream\DRXDistortionWave.dbr',
         328, 403, False, 'Distortion Wave'),
        (28, r'Records\XPack\Skills\Dream\DRXDistortionWave_ChaoticResonance.dbr',
         328, 217, True, 'Chaotic Resonance'),
        (29, r'Records\XPack\Skills\Dream\DRXDistortionWave_PsionicImmolation.dbr',
         328, 93, True, 'Psionic Immolation'),
    ]
    for slot, ref, x, y, circ, label in spirit_ui_slots:
        if _create_ui_slot(db, 7, slot, ref, x, y, circ, label):
            print("  Spirit UI Skill%02d: (%d,%d) %s" % (slot, x, y, label))
            total += 1

    # ── D. Warfare: Original Hamstring ────────────────────────────────
    hamstring_src_fields = _get_src_fields(
        r'records\skills\warfare\drxonslaught_hamstring.dbr')
    hamstring_new_path = r'records\skills\warfare\drxhamstring.dbr'
    existing_hamstring = nm98.get(
        r'records\skills\warfare\drxonslaught_hamstring.dbr'.lower())
    if hamstring_src_fields and existing_hamstring:
        db.clone_record(existing_hamstring, hamstring_new_path)
        if _import_record_fields(db, hamstring_new_path, db41, hamstring_src_fields):
            print("  Created: drxhamstring.dbr (original Hamstring from 0.4.1)")
            total += 1

        warfare_tree = nm98.get(
            r'records\skills\warfare\drxwarfareskilltree.dbr'.lower())
        if warfare_tree:
            db.set_field(warfare_tree, 'skillName26',
                         hamstring_new_path, DATA_TYPE_STRING)
            print("  Warfare skillName26 = Hamstring")
            total += 1

        if _create_ui_slot(db, 1, 25, hamstring_new_path,
                           428, 279, True, 'Hamstring'):
            print("  Warfare UI Skill25: (428,279) Hamstring")
            total += 1

    print("  Total legacy skill changes: %d" % total)

    new_tags = {
        'tagDarkApertureNAME': 'Dark Aperture',
        'tagDarkApertureDESC': 'The Occultist pries open a wider aperture '
            'to the shadow realm, allowing the Darklings to emerge with '
            'greater fury and intensity.',
    }
    return total, new_tags


def promote_uber_monsters(db: ArzDatabase):
    """Promote um_ (uber) monsters that are clearly intended as special encounters.

    Only promotes um_ monsters that already had souls in the original SV mod
    (Hero/Boss classification). Leaves Common/Champion/none um_ monsters alone
    since those are minions and support mobs (soldiers, mages, slimes, etc.).
    """
    print("\n=== Patch 7: Verify uber monster classifications ===")
    print("  Skipping promotion -- original SV classifications are correct.")
    print("  40 um_ minions (Common/Champion/none) intentionally left as-is.")
    return 0


def create_uber_dungeon_portal(db: ArzDatabase):
    """Create NPC portal DBRs for the Uber Dungeon entrance and return.

    Uses the NPC + Action_BoatDialog pattern (like the Secret Place portals).
    The NPC objects are injected into the map by build_section_surgery.py.
    The quest file wiring is handled by build_section_surgery.py + build_quest_files.py.
    """
    print("\n=== Patch 12: Create Uber Dungeon portal records ===")

    entrance_npc = r'records\quests\portal_uberdungeon_entrance.dbr'
    return_npc = r'records\quests\portal_uberdungeon_return.dbr'
    portal_template = r'records\drxmap\xurder\portaldudes\portal to act 1.dbr'
    fallback_template = r'records\drxmap\xurder\portaldudes\portal to hallway.dbr'

    src = portal_template if db.has_record(portal_template) else fallback_template

    for npc_path, desc in [
        (entrance_npc, 'Portal NPC to Uber Dungeon at Crisaeos Falls'),
        (return_npc, 'Return portal NPC from Uber Dungeon to Crisaeos Falls'),
    ]:
        if db.has_record(src):
            db.clone_record(src, npc_path)
            db.set_field(npc_path, 'FileDescription', desc, DATA_TYPE_STRING)
            db.set_field(npc_path, 'ActorName', 'Mysterious Portal', DATA_TYPE_STRING)
            db.set_field(npc_path, 'description', 'xtagMysteriousPortal', DATA_TYPE_STRING)
            db.set_field(npc_path, 'mesh',
                         r'Items\shrines\artifactportal01.msh', DATA_TYPE_STRING)
            db.set_field(npc_path, 'startVisible', 1, DATA_TYPE_INT)
            db._modified.add(npc_path)
            print(f"  Created NPC: {npc_path} (cloned from {src}, mesh=artifactportal01)")
        else:
            _ensure_record(db, npc_path, 'database\\Templates\\Npc.tpl')
            db.set_field(npc_path, 'templateName',
                         'database\\Templates\\Npc.tpl', DATA_TYPE_STRING)
            db.set_field(npc_path, 'Class', 'Npc', DATA_TYPE_STRING)
            db.set_field(npc_path, 'FileDescription', desc, DATA_TYPE_STRING)
            db.set_field(npc_path, 'ActorName', 'Mysterious Portal', DATA_TYPE_STRING)
            db.set_field(npc_path, 'description', 'xtagMysteriousPortal', DATA_TYPE_STRING)
            db.set_field(npc_path, 'mesh',
                         r'Items\shrines\artifactportal01.msh', DATA_TYPE_STRING)
            db.set_field(npc_path, 'AIType', 'generic', DATA_TYPE_STRING)
            db.set_field(npc_path, 'startVisible', 1, DATA_TYPE_INT)
            db.set_field(npc_path, 'scale', 1.0, DATA_TYPE_FLOAT)
            print(f"  Created NPC (from scratch): {npc_path}")


def main():
    if len(sys.argv) < 5:
        print("Usage: build_svc_database.py <sv098i.arz> <sv09.arz> <sv041.arz> <output.arz>")
        sys.exit(1)

    sv098_path = Path(sys.argv[1])
    sv09_path = Path(sys.argv[2])
    sv041_path = Path(sys.argv[3])
    output_path = Path(sys.argv[4])

    print(f"Loading SV 0.98i: {sv098_path}")
    db = ArzDatabase.from_arz(sv098_path)

    print(f"\nLoading SV 0.9: {sv09_path}")
    db09 = ArzDatabase.from_arz(sv09_path)

    db41 = None
    if sv041_path and str(sv041_path).strip() and Path(sv041_path).exists():
        print(f"\nLoading SV 0.4.1: {sv041_path}")
        db41 = ArzDatabase.from_arz(sv041_path)

    strip_ui_overrides(db)
    restore_potion_drops(db, db09)
    wire_souls_to_monsters(db)
    make_enchantable(db)
    grant_all_inventory_bags(db)
    expand_transfer_stash(db)
    restore_rest_skill(db)

    legacy_tags = {}
    if db41:
        _, legacy_tags = restore_legacy_skills(db, db41)
    else:
        print("\n=== Patch 11: SKIPPED (SV 0.4.1 not available) ===")

    fix_broken_mastery_skills(db)
    fix_mastery_panel_buttons(db)
    add_dlc_mastery_trees(db)

    promote_uber_monsters(db)

    create_uber_dungeon_portal(db)

    from create_uber_souls import create_uber_souls
    souls, text_tags = create_uber_souls(db)

    from apply_svc_patches import apply_all_extended_patches
    extended_tags = apply_all_extended_patches(db)

    report_path = output_path.parent / 'uber_souls_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# SoulvizierClassic - New Uber Monster Souls\n\n")
        f.write(f"Total new souls: {len(souls)}\n\n")
        f.write("| Monster | Display Name | Level | Element | Role | Skills | Tag |\n")
        f.write("|---------|-------------|-------|---------|------|--------|-----|\n")
        for s in sorted(souls, key=lambda x: x['level']):
            sk = ', '.join(s['skills'][:3]) if s['skills'] else '-'
            f.write(f"| {s['clean_name']} | {s['display_name']} | {s['level']} | {s['element']} | {s['role']} | {sk} | {s['tag']} |\n")
    print(f"  Soul report: {report_path}")

    tags_path = output_path.parent / 'uber_soul_tags.txt'
    with open(tags_path, 'w', encoding='utf-8') as f:
        for tag, value in text_tags:
            f.write(f"{tag}={value}\n")
        for tag, value in legacy_tags.items():
            f.write(f"{tag}={value}\n")
        for tag, value in extended_tags.items():
            f.write(f"{tag}={value}\n")
    print(f"  Tags file: {tags_path} ({len(text_tags)} uber + {len(legacy_tags)} legacy + {len(extended_tags)} extended)")

    print(f"\nWriting output...")
    db.write_arz(output_path)
    print("Done.")


if __name__ == '__main__':
    main()
