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
import os
import sys
import re
from pathlib import Path
from collections import defaultdict, OrderedDict

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import (ArzDatabase, TypedField,
                         DATA_TYPE_FLOAT, DATA_TYPE_STRING, DATA_TYPE_INT)


# Description tags this build deliberately WIRES onto skills that ship without a
# usable description (skillBaseDescription points here). The mod is therefore
# responsible for these tag STRINGS resolving in Text.arc (tagbreachDESC comes
# from SV 0.98i's own extracted text; tagNewSkill321DESC is defined by
# build_text_arc.py's Occult fix). Keyed by target .dbr record path; the VALUES
# are the mod-owned Text.arc tags. Exposed at module scope (and iterated by
# fix_broken_mastery_skills below) so build_text_arc.py can fold the values into
# the authoritative mod-authored-tag manifest that validate_tags.py gates on.
# This is the single source of truth for these description-fix tags.
MOD_DESC_FIX_TAGS = {
    'records\\skills\\stealth\\drxlaytrap.dbr': 'tagbreachDESC',
    'records\\skills\\stealth\\drxlaytrap_rapidconstruction.dbr': 'tagNewSkill321DESC',
}


def import_base_game_bosses(db: ArzDatabase, base_db: ArzDatabase):
    """Import specific boss records from the base game that aren't in the SV overlay.

    Some base game bosses (e.g. Aktaios telkine) aren't overridden by SV,
    so they can't get soul wiring. Importing them into the overlay allows
    the soul wiring passes to find and wire them.
    """
    print("\n=== Import base game boss records for soul wiring ===")

    # Boss records to import (only if missing from SV overlay)
    TARGETS = [
        r'records\creature\monster\questbosses\boss_egypttelkine_aktaios_27.dbr',
        r'records\creature\monster\questbosses\boss_egypttelkine_aktaios_30.dbr',
        r'records\creature\monster\questbosses\boss_egypttelkine_aktaios_33.dbr',
    ]

    imported = 0
    for target in TARGETS:
        if db.has_record(target):
            continue
        # Try case-insensitive match in base_db
        source = None
        for name in base_db.record_names():
            if name.lower().replace('/', '\\') == target.lower():
                source = name
                break
            if name.lower() == target.lower():
                source = name
                break
        if not source:
            print(f"  WARNING: {target.split(chr(92))[-1]} not found in base game")
            continue

        # Decode source fields and copy to overlay
        fields = base_db.get_fields(source)
        if not fields:
            print(f"  WARNING: {target.split(chr(92))[-1]} has no fields in base game")
            continue

        # Get template from base_db
        template = ''
        for key, tf in fields.items():
            if key.split('###')[0] == 'templateName' and tf.values:
                template = str(tf.values[0])
                break

        # Create empty record
        from apply_svc_patches import _ensure_record
        _ensure_record(db, target, template)

        # Copy all fields
        for key, tf in fields.items():
            field_name = key.split('###')[0]
            vals = list(tf.values) if tf.values else []
            if len(vals) == 1:
                db.set_field(target, field_name, vals[0], tf.dtype)
            elif len(vals) > 1:
                db.set_field(target, field_name, vals, tf.dtype)

        imported += 1

    print(f"  Imported {imported} base game boss records")
    return imported


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


# Dead orphan records to strip for hygiene: unreferenced SV-passthrough records
# that carry corrupted data. Each MUST be verified to have ZERO inbound references
# in the built DB before being listed here (removing a referenced record would
# dangle that reference).
_DEAD_ORPHAN_RECORDS = (
    # SV 0.98i debug XP potion: ships a corrupted bonusExperiencePoints (a 4e9
    # int32 overflow -> -294967296) and has ZERO inbound references anywhere in the
    # built DB (verified 2026-07-08), so it is pure dead weight. Safe to drop.
    r'records\item\miscellaneous\oneshot\potionexp_test.dbr',
)


def remove_dead_orphan_records(db: ArzDatabase):
    """Strip unreferenced/corrupted dead orphan records (hygiene). Mirrors the
    strip_ui_overrides removal (delete by path from every db index). Each listed
    record was verified to have ZERO inbound references before being added."""
    print("\n=== Patch 0b: Remove dead orphan records ===")
    removed = 0
    for target in _DEAD_ORPHAN_RECORDS:
        rec = None
        want = target.replace('/', '\\').lower()
        for name in list(db._raw_records.keys()):
            if name.replace('/', '\\').lower() == want:
                rec = name
                break
        if rec is None:
            print(f"  SKIP {target}: not present (already absent)")
            continue
        del db._raw_records[rec]
        db._record_types.pop(rec, None)
        db._record_timestamps.pop(rec, None)
        db._decoded_cache.pop(rec, None)
        db._modified.discard(rec)
        removed += 1
        print(f"  Removed dead orphan: {rec}")
    print(f"  Dead orphan records removed: {removed}")
    return removed


def fix_chimera_chest_double_ext(db: ArzDatabase):
    """Q4-3 (build31, dead-content audit Lane D): SV ships the Chimera boss
    chests with double '.dbr.dbr' record names. Two defects, one rename:
    - bosschest13_chimera_epic.dbr.dbr -> .dbr (+ rewrite the accessory pool's
      fixedItemName1, which carried the same typo - self-consistent but wrong);
    - repeatbosschest13_chimera_epic.dbr.dbr -> .dbr: the epic REPEAT pool's
      fixedItemName1 already points at the single-ext name, i.e. a DANGLING
      ref today - the rename makes the epic repeat chest spawnable at all.
    The quest condition is retargeted in the same wave by
    tools/build_quest_files.py (_fix_chimera_chest_typo). Coordinated ship.
    """
    print("\n=== Patch 0c: Chimera chest double-extension rename (Q4-3) ===")
    renames = [
        (r'records\item\containers\boss\bosschest13_chimera_epic.dbr.dbr',
         r'records\item\containers\boss\bosschest13_chimera_epic.dbr'),
        (r'records\item\containers\boss\repeatbosschest13_chimera_epic.dbr.dbr',
         r'records\item\containers\boss\repeatbosschest13_chimera_epic.dbr'),
    ]
    # Q4-3 fallout: both chimera chests carry SV's stock lockedSound string
    # 'Sounds\SoundPaks\Decorations\LockedObjectPak.dbr' (SoundPaks plural, no
    # records\ prefix). That literal is a base-game convention used verbatim by
    # dozens of stock chests and the engine resolves it at runtime, but it does
    # NOT match the actual base record name by exact path
    # (records\sounds\soundpak\decorations\lockedobjectpak.dbr - soundpak
    # singular, records\ prefix). While these chests were sv-provenance
    # (.dbr.dbr) that mismatch was a non-blocking P2; renaming them to single
    # .dbr makes them 'authored', which promotes the same dangling lockedSound to
    # a gate-blocking C-RES-DBR-1 P1. Repoint it at the real base record path (the
    # sibling openSound field on these same records already uses that
    # records\sounds\soundpak\... convention): functionally identical sound,
    # exactly resolvable.
    LOCKED_SOUND_STOCK = r'Sounds\SoundPaks\Decorations\LockedObjectPak.dbr'
    LOCKED_SOUND_RESOLVED = (r'records\sounds\soundpak\decorations'
                             r'\lockedobjectpak.dbr')
    namemap = {n.replace('/', '\\').lower(): n for n in db.record_names()}
    for old, new in renames:
        rec = namemap.get(old.lower())
        if rec is None:
            raise SystemExit(f"Q4-3: expected double-ext record missing: {old}")
        if namemap.get(new.lower()):
            raise SystemExit(f"Q4-3: rename target already exists: {new}")
        db.clone_record(rec, new)
        del db._raw_records[rec]
        db._record_types.pop(rec, None)
        db._record_timestamps.pop(rec, None)
        db._decoded_cache.pop(rec, None)
        db._modified.discard(rec)
        db._modified.add(new)
        # Fix the dangling lockedSound on the renamed (now 'authored') chest.
        ls = db.get_field_value(new, 'lockedSound')
        ls0 = ls[0] if isinstance(ls, list) else ls
        ls_norm = ls0.replace('/', '\\').lower() if isinstance(ls0, str) else ''
        if ls_norm == LOCKED_SOUND_STOCK.lower():
            db.set_field(new, 'lockedSound', LOCKED_SOUND_RESOLVED)
            print(f"  renamed {rec} -> {new} (+ lockedSound -> resolvable base path)")
        elif ls_norm in ('', LOCKED_SOUND_RESOLVED.lower()):
            print(f"  renamed {rec} -> {new}")
        else:
            raise SystemExit(
                f"Q4-3: {new} lockedSound unexpectedly {ls0!r} "
                f"(expected the SV stock LockedObjectPak string) - reconcile")
    # rewrite the one in-arz field ref that carried the typo (the epic pool)
    pool = namemap.get(r'records\item\containers\boss\accessorypools'
                       r'\bosschestpool13_chimera_epic.dbr'.lower())
    if pool is None:
        raise SystemExit("Q4-3: bosschestpool13_chimera_epic.dbr missing")
    cur = db.get_field_value(pool, 'fixedItemName1')
    cur0 = cur[0] if isinstance(cur, list) else cur
    if not (isinstance(cur0, str) and cur0.lower().endswith('.dbr.dbr')):
        raise SystemExit(f"Q4-3: pool fixedItemName1 unexpectedly {cur0!r} "
                         f"(expected the .dbr.dbr typo) - reconcile")
    db.set_field(pool, 'fixedItemName1',
                 r'records\item\containers\boss\bosschest13_chimera_epic.dbr')
    db._modified.add(pool)
    print("  rewrote bosschestpool13_chimera_epic.fixedItemName1 -> single .dbr")
    return len(renames)


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
    zeroed_common = 0

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
            # Defense-in-depth (generalizes the 2026-07-05 normal-yeti fix).
            # Records whose Class/template is not a plain "Monster" (e.g. the
            # SpiritHost possessed-statue props of the Megalesios fight, whose
            # Class=SpiritHost / template=SpiritHost.tpl) are otherwise invisible
            # to the soul passes below. If such a non-Hero/Boss/Quest prop ever
            # arrives here already carrying INHERITED soul loot with a live
            # chance, _force_100_pct_soul_drops would later boost it to 100% -
            # the same classification loophole as the yeti bug, one filter
            # deeper. Zero it here so it can never drop. Only ever ZERO (never
            # raise), so the real Hero/Boss/Quest bosses that legitimately use a
            # non-Monster Class (Megalesios/Ormenos/Typhon/Cerberus/Hades, and
            # the Boss-classed SpiritHost Pharaoh's Honor Guards) keep their
            # inherited drop untouched. NOTE: on the current data the Megalesios
            # statues carry NO soul loot at this stage - their soul is wired
            # later by _wire_missing_boss_souls in apply_svc_patches.py, which is
            # where the actual Inhabited-Statue fix (a classification guard)
            # lives; this pass is the belt-and-suspenders complement.
            existing = db.get_field_value(name, 'lootFinger2Item1')
            if existing and existing != '' and existing != 0:
                fields2 = db.get_fields(name)
                loot_vals = []
                monster_cls = ''
                for key, tf in fields2.items():
                    rk = key.split('###')[0]
                    if rk == 'lootFinger2Item1' and tf.values:
                        loot_vals = tf.values
                    elif rk == 'monsterClassification' and tf.values:
                        monster_cls = str(tf.values[0])
                has_soul_loot = any(
                    isinstance(v, str) and 'soul' in v.lower() for v in loot_vals)
                if has_soul_loot and monster_cls not in ('Hero', 'Boss', 'Quest'):
                    db.set_field(name, 'chanceToEquipFinger2', 0.0, DATA_TYPE_FLOAT)
                    zeroed_common += 1
            continue

        existing = db.get_field_value(name, 'lootFinger2Item1')
        if existing and existing != '' and existing != 0:
            # Only enable soul drops for Hero/Boss/Quest monsters.
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
            else:
                # Common/Champion (incl. um_ minions) must NEVER drop souls.
                # They keep their inherited lootFinger2Item1, but the base SV
                # data can carry a live chanceToEquipFinger2 here (e.g. normal
                # yetis inherit lootFinger2Item1=yeti_soul + a nonzero chance).
                # Force it to 0 - otherwise the 100% test forcer, which keys off
                # the soul-loot field, re-enables the drop (the normal-yeti bug).
                db.set_field(name, 'chanceToEquipFinger2', 0.0, DATA_TYPE_FLOAT)
                zeroed_common += 1
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

                # F1 (build36 fix wave): type_bonus (family membership) and a
                # weak cross-family prefix must NEVER *qualify* a wire on their
                # own - only a real name identity does. Folding type_bonus into
                # the qualifying score is what collapsed every soulless
                # Hero/Boss/Quest onto its family's first soul (the Phantom
                # Weaver -> Ararat-soul + Siege-Strider -> Leveler-soul bug), and
                # a weak prefix (clean "storm" -> carrionbird "stormbird",
                # score 10) re-collapsed the residue. Qualify iff an EXACT name
                # identity (any family) OR a same-family positive NAME match
                # (type_bonus then only disambiguates real name matches).
                qualifies = (score == 100) or (score > 0 and type_bonus > 0)
                total = (score + type_bonus) if qualifies else 0
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
    print(f"  Common/Champion drop-chance zeroed: {zeroed_common} (never drop souls)")
    return wired + fixed_chance


# ── F1 (build36 fix wave): cross-wire regression gate ──────────────────────
# Part A above stops the fuzzy matcher from wiring a soul onto a monster whose
# name does not identify it. This gate is the fail-loud recurrence guard: it
# flags any Hero/Boss/Quest soul drop that is neither an exact name identity
# NOR a same-family positive name match, EXCLUDING the mismatches SV 0.98i
# itself authored (captured as a pristine snapshot before wire_souls mutates
# loot - the "SV membership = whitelist, no hand-list" rule). Post-fix it must
# find ZERO offenders.

def _soul_base_of(path):
    """Soul-item base-name (family-agnostic) used for name matching:
    '...\\spider\\ararat_soul_n.dbr' -> 'ararat'."""
    b = str(path).replace('/', '\\').rsplit('\\', 1)[-1]
    if b.lower().endswith('.dbr'):
        b = b[:-4]
    b = re.sub(r'_(n|e|l)$', '', b, flags=re.IGNORECASE)
    b = re.sub(r'_soul$', '', b, flags=re.IGNORECASE)
    return b.lower().strip('_')


def _soul_family_of(path):
    parts = str(path).replace('/', '\\').lower().split('\\')
    return parts[-2] if len(parts) >= 2 else ''


def _monster_clean_name(monster_path):
    fn = str(monster_path).replace('/', '\\').rsplit('\\', 1)[-1].replace('.dbr', '')
    clean = re.sub(r'^(u_|um_|uw_|qm_|bm_|cb_|am_|ar_|as_|em_|vampiric_)', '', fn)
    clean = re.sub(r'_?\d+$', '', clean).strip('_')
    return clean.lower()


def _soul_name_overlap(clean, soul_base):
    """Mirror wire_souls_to_monsters' name-score tiers (>0 iff a real name
    overlap). Returns (is_exact, has_overlap)."""
    if soul_base == clean:
        return True, True
    if clean.startswith(soul_base) and len(soul_base) >= 4:
        return False, True
    if soul_base.startswith(clean) and len(clean) >= 4:
        return False, True
    if clean in soul_base and len(clean) >= 5:
        return False, True
    if soul_base in clean and len(soul_base) >= 5:
        return False, True
    return False, False


def _capture_sv_soul_drops(db: ArzDatabase):
    """Snapshot monster(lower path) -> {soul base-names it carries} from the
    PRISTINE db (== SV 0.98i, called BEFORE wire_souls_to_monsters). Any final
    Hero/Boss/Quest drop whose soul base is in this set is SV-authored (legit),
    so the cross-wire gate never flags amgoz1's own intentional name-mismatches."""
    out = {}
    for name in db.record_names():
        loot = db.get_field_value(name, 'lootFinger2Item1')
        if not loot:
            continue
        loot = loot if isinstance(loot, list) else [loot]
        bases = {_soul_base_of(s) for s in loot
                 if isinstance(s, str) and 'soul' in s.lower()}
        if bases:
            out[name.replace('/', '\\').lower()] = bases
    return out


def _verify_no_fuzzy_cross_wire(db: ArzDatabase, sv_drops):
    """FAIL-LOUD (F1 Part B). No Hero/Boss/Quest may drop a soul that is neither
    an exact name identity nor a same-family positive name match, unless SV 0.98i
    authored that exact monster->soul pairing (sv_drops). Catches a re-introduced
    fuzzy cross-wire (Phantom Weaver -> Ararat-soul / Siege Strider -> Leveler-soul)."""
    def _is_conflict_junk(p):
        # amgoz's Dropbox git-conflict duplicate records (e.g. '... (amgoz-
        # qosmio's conflicted copy 2013-08-07)', '... modstridende kopi ...')
        # are compiled-in junk duplicates (meritamen verifier F). A duplicate of
        # a monster's OWN soul is identity-correct, not a cross-wire; its garbage
        # filename just defeats name-matching. Exclude both sides from the gate;
        # the junk itself is a separate data-hygiene ticket, out of this wave.
        pl = str(p).lower()
        return 'conflicted copy' in pl or 'kopi' in pl

    offenders = []
    for name in db.record_names():
        nl = name.replace('/', '\\').lower()
        if _is_conflict_junk(nl):
            continue
        cls = db.get_field_value(name, 'monsterClassification')
        cls = cls[0] if isinstance(cls, list) else cls
        if cls not in ('Hero', 'Boss', 'Quest'):
            continue
        chance = db.get_field_value(name, 'chanceToEquipFinger2')
        chance = chance[0] if isinstance(chance, list) else chance
        try:
            if float(chance) <= 0:
                continue
        except (TypeError, ValueError):
            continue
        loot = db.get_field_value(name, 'lootFinger2Item1') or []
        loot = loot if isinstance(loot, list) else [loot]
        clean = _monster_clean_name(name)
        mdir = nl.split('\\')[-2] if len(nl.split('\\')) >= 2 else ''
        sv_bases = sv_drops.get(nl, set())
        seen = set()
        for s in loot:
            if not (isinstance(s, str) and 'soul' in s.lower()):
                continue
            if _is_conflict_junk(s):
                continue  # conflicted-copy duplicate soul record - junk, not a cross-wire
            base = _soul_base_of(s)
            if base in seen:
                continue
            seen.add(base)
            is_exact, has_overlap = _soul_name_overlap(clean, base)
            same_family = (mdir == _soul_family_of(s))
            qualified = is_exact or (has_overlap and same_family)
            if qualified:
                continue
            if base in sv_bases:
                continue  # SV 0.98i authored this exact pairing -> legit
            offenders.append((name.rsplit('\\', 1)[-1], clean, base, mdir))
    if offenders:
        for mon, clean, base, mdir in offenders[:40]:
            print(f"  CROSS-WIRE OFFENDER: {mon} (clean='{clean}', dir='{mdir}') "
                  f"drops soul '{base}' - not exact, not same-family, not SV-authored")
        raise SystemExit(
            f"F1 cross-wire gate FAILED: {len(offenders)} Hero/Boss/Quest soul "
            f"drop(s) are a NEW fuzzy cross-wire (see offenders above)")
    print("  F1 cross-wire gate OK: no NEW fuzzy Hero/Boss/Quest soul cross-wires")


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

    # The tutorial potion chest (first chest in the game, FixedItemLoot.tpl)
    # carries the bags via the mod-only startingloot_sack table (see the
    # build30.2 construct below).
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

    # ── build30.2 / B-STARTER-CHEST-1+2 RESOLUTION (in-game verified on the DEV
    #    entry 2026-07-09, arz c959a372: "that worked perfect, both the inventory
    #    bags and potions dropped" - Will). The co-op kit: E[36 HEALTH POTIONS +
    #    12 INVENTORY BAGS], nothing else. Total = exactly 48 solo.
    #
    #    ROOT CAUSE of the build28/29/30 dead chest (the "opens, drops nothing"
    #    P0): build28 (5af85d3) replaced the record's native RunEquation
    #    numSpawnMin/MaxEquation '3+(2*numberOfPlayers)' with the bare integer
    #    literal '48' -> the engine's equation evaluator yields 0 for the bare-
    #    literal form on this container -> numSpawn 0 -> the whole chest drops
    #    NOTHING (not even the untouched potion slot). Every byte-exoneration
    #    (build30.1) compared build30-vs-build29 = broken-vs-broken. The proof
    #    pair: build27's chest (native equation, sack slots) DROPS; the identical
    #    construct with only numSpawn changed to a literal does not. LESSON:
    #    RunEquation-typed fields require equation-form values; bare literals can
    #    silently evaluate to 0. In-game verification is mandatory for engine-
    #    facing constructs - byte precedent from OTHER records (boss_tartarus
    #    min/max='1') did not transfer to this container.
    #
    #    PROVEN CONSTRUCT (every element is either the record's own native shape
    #    or ubiquitous base FixedItemLoot precedent, e.g. defaultloot\
    #    hiddenchest_greece_00-15 / typhon_default_29-31 = multi-table slots):
    #      numSpawnMin==Max = '46+(2*numberOfPlayers)'  (native equation FORM;
    #                          48 solo, scales co-op like the original)
    #      loot1 = the ONE active slot (chance 100), TWO tables inside it:
    #        loot1Name1 = the chest's own Health_01-05All potion table, w108
    #        loot1Name2 = startingloot_sack (mod-only) -> inventorysack,  w36
    #        -> 108:36 = 3:1 -> E[36 potions : 12 bags] per open (multinomial;
    #           P(zero bags) ~ 1e-6). Weight fields loot1Weight1/2 exist natively
    #           on the record (weight matrix ships even for unused tables).
    #      loot2..6 = the record's native inert shape: chance 0.0, weights 0,
    #        and NO lootNNameM fields AT ALL. Never blank a NameM to '' - an
    #        empty-string .dbr ref is the zero-precedent B-TOXEUS-2 loader-abort
    #        field shape; native inert = field ABSENT (delete, don't blank).
    #      NO soul (Will 2026-07-09; the build29 sow-soul slot stays removed).
    if tutorial_chest:
        db.set_field(tutorial_chest, 'numSpawnMinEquation',
                     '46+(2*numberOfPlayers)', DATA_TYPE_STRING)
        db.set_field(tutorial_chest, 'numSpawnMaxEquation',
                     '46+(2*numberOfPlayers)', DATA_TYPE_STRING)
        db.set_field(tutorial_chest, 'loot1Chance', 100.0, DATA_TYPE_FLOAT)
        db.set_field(tutorial_chest, 'loot1Weight1', 108, DATA_TYPE_INT)   # health potions (loot1Name1 kept = Health_01-05All)
        db.set_field(tutorial_chest, 'loot1Weight2', 36, DATA_TYPE_INT)    # inventory bags (loot1Name2 below)
        # slots 2..6: force the native inert shape defensively (idempotent
        # against any previously-patched input record)
        for _slot in range(2, 7):
            db.set_field(tutorial_chest, f'loot{_slot}Chance', 0.0,
                         DATA_TYPE_FLOAT)
            db.set_field(tutorial_chest, f'loot{_slot}Weight1', 0,
                         DATA_TYPE_INT)
        # insert loot1Name2 right after loot1Name1 (base field adjacency) and
        # DELETE any NameM field on the inert slots (restore native shape)
        _fields = db.get_fields(tutorial_chest)
        _rebuilt = OrderedDict()
        for _k, _tf in _fields.items():
            _base = _k.split('###')[0]
            if _base == 'loot1Name2':
                continue  # re-inserted at the canonical position below
            if any(_base == f'loot{_s}Name{_j}'
                   for _s in range(2, 7) for _j in range(1, 7)):
                continue  # inert slots carry NO Name fields natively
            _rebuilt[_k] = _tf
            if _base == 'loot1Name1':
                _rebuilt['loot1Name2'] = TypedField(DATA_TYPE_STRING,
                                                    [sack_table])
        assert 'loot1Name2' in _rebuilt
        db._decoded_cache[tutorial_chest] = _rebuilt
        db._modified.add(tutorial_chest)
        print("  Starter chest (build30.2): numSpawn='46+(2*numberOfPlayers)' "
              "(equation form, 48 solo); single slot, dual table 108:36 = "
              "E[36 potions + 12 bags]; in-game verified 2026-07-09")
        patched += 1
    else:
        print("  WARNING: tutorial potion chest not found")

    return patched


def _validate_container_loot_shapes(db, base_db=None, base_names=None):
    """P0/build30.1 fail-loud gate: container loot-slot contract, calibrated to
    what the BASE GAME's 611 FixedItemLoot records actually ship (measured):

    FAIL (zero base precedent - the classes that make a chest drop nothing or
    fail to load):
      - a lootN slot whose lootNName1 is present + non-empty but does NOT
        resolve to a record in the mod .arz (dangling loot-table ref);
      - numSpawnMinEquation/numSpawnMaxEquation missing or empty on a modified
        FixedItemLoot record (bare integer constants ARE precedented: the
        Ragnarok boss_tartarus_{n,e,l} chests ship '1'; xpack4 ships '0').

    WARN only (base-PRECEDENTED design idioms, measured in the base arz):
      - ACTIVE slot (chance > 0) without a name: 95 base slots ship this (the
        'chance of nothing' idiom, e.g. the hermit mage chests);
      - DORMANT slot (chance 0) carrying a name: 199 base slots ship this
        (parked tables).
    Raises SystemExit on any FAIL. Cheap: only scans db._modified.
    """
    bad = []
    warned = 0
    all_low = {n.replace('/', '\\').lower() for n in db.record_names()}
    if base_db is not None:
        # runtime resolution model = mod UNION base game (same as the other gates)
        all_low |= {n.replace('/', '\\').lower() for n in base_db.record_names()}
    if base_names:
        # pre-snapshotted lowercase base-game names (main() frees base_db long
        # before this end-of-build gate runs)
        all_low |= set(base_names)
    for rec in sorted(getattr(db, '_modified', set())):
        fields = db.get_fields(rec)
        if not fields:
            continue
        fmap = {}
        for k, tf in fields.items():
            fmap[k.split('###')[0]] = tf
        tpl = fmap.get('templateName')
        tplv = str(tpl.values[0]).lower() if (tpl and tpl.values) else ''
        if not tplv.endswith('fixeditemloot.tpl'):
            continue
        for n in range(1, 7):
            ch_tf = fmap.get(f'loot{n}Chance')
            chance = float(ch_tf.values[0]) if (ch_tf and ch_tf.values) else 0.0
            nm_tf = fmap.get(f'loot{n}Name1')
            name = str(nm_tf.values[0]).strip() if (nm_tf and nm_tf.values) else ''
            if name:
                # the ONE unprecedented killer: a named slot whose table does
                # not exist -> that slot's draws yield nothing (or worse).
                if name.replace('/', '\\').lower() not in all_low:
                    bad.append((rec, f'loot{n}Name1 DANGLING: {name!r} '
                                     f'(table not in the built .arz)'))
            if chance > 0 and not name:
                warned += 1   # base-precedented 'chance of nothing' idiom (95 in base)
            if chance <= 0 and name:
                warned += 1   # base-precedented parked-table idiom (199 in base)
        for eq in ('numSpawnMinEquation', 'numSpawnMaxEquation'):
            eq_tf = fmap.get(eq)
            if not eq_tf or not eq_tf.values or not str(eq_tf.values[0]).strip():
                bad.append((rec, f'{eq} missing/empty'))
    if bad:
        for rec, why in bad:
            print(f'  CONTAINER-SHAPE FAIL: {rec} :: {why}')
        raise SystemExit(
            f'Container loot contract FAILED on {len(bad)} violation(s); '
            f'this build does not ship (P0/build30.1 gate)')
    print(f'  Container loot contract: PASS (modified FixedItemLoot records; '
          f'{warned} base-precedented idiom slot(s) noted)')


def _import_base_game_record(db, base_db, record_name):
    """Import a single record from the base game database into the SV overlay."""
    if db.has_record(record_name):
        return False
    if not base_db:
        return False
    for name in base_db.record_names():
        if name.lower() == record_name.lower():
            fields = base_db.get_fields(name)
            if not fields:
                return False
            template = ''
            for key, tf in fields.items():
                if key.split('###')[0] == 'templateName' and tf.values:
                    template = str(tf.values[0])
                    break
            from apply_svc_patches import _ensure_record
            _ensure_record(db, record_name, template)
            for key, tf in fields.items():
                fn = key.split('###')[0]
                vals = list(tf.values) if tf.values else []
                if len(vals) == 1:
                    db.set_field(record_name, fn, vals[0], tf.dtype)
                elif len(vals) > 1:
                    db.set_field(record_name, fn, vals, tf.dtype)
            return True
    return False


def expand_caravan(db: ArzDatabase, base_db: ArzDatabase = None):
    """Expand all caravan stash areas to maximum size.

    The caravan has 3 tabs (hardcoded in CaravanWindow.tpl):
      - Storage Area (stashwindow.dbr) - private, per-character
      - Transfer Area - shared between characters (not expanded here)
      - Relic Vault (relicvaultwindow.dbr) - per-character

    InventoryHeightArray defines expansion stages for a single grid:
    [5, 10, 15] means start at 5 rows, expand to 10, then 15.
    We set a single large value so the grid starts fully expanded.

    These records only exist in the base game database, so we import
    them first if needed.
    """
    print("\n=== Patch 5: Expand caravan stash ===")

    rows = 50  # 50 rows × 10 wide = 500 slots per tab

    # ── Storage Area (private stash) ──────────────────────────────────
    stash_window = 'records\\xpack\\ui\\caravan\\stashwindow.dbr'
    if _import_base_game_record(db, base_db, stash_window):
        print(f"  Imported stashwindow.dbr from base game")

    if db.has_record(stash_window):
        db.set_field(stash_window, 'InventoryWidth', 10, DATA_TYPE_INT)
        db.set_field(stash_window, 'InventoryHeightArray', [rows], DATA_TYPE_INT)
        db.set_field(stash_window, 'InventoryCostArray', [0], DATA_TYPE_INT)
        print(f"  Storage Area: 10 wide x {rows} tall ({10 * rows} slots)")
    else:
        print(f"  WARNING: stashwindow.dbr not found - cannot expand Storage Area")

    # ── Relic Vault ───────────────────────────────────────────────────
    vault_window = 'records\\xpack\\ui\\caravan\\relicvaultwindow.dbr'
    if _import_base_game_record(db, base_db, vault_window):
        print(f"  Imported relicvaultwindow.dbr from base game")

    if db.has_record(vault_window):
        db.set_field(vault_window, 'InventoryWidth', 10, DATA_TYPE_INT)
        db.set_field(vault_window, 'InventoryHeightArray', [rows], DATA_TYPE_INT)
        print(f"  Relic Vault: 10 wide x {rows} tall ({10 * rows} slots)")
    else:
        print(f"  WARNING: relicvaultwindow.dbr not found - cannot expand Relic Vault")

    # ── Also import caravanwindow.dbr so Relic Vault tab shows up ────
    caravan_window = 'records\\xpack\\ui\\caravan\\caravanwindow.dbr'
    if _import_base_game_record(db, base_db, caravan_window):
        print(f"  Imported caravanwindow.dbr from base game (has Relic Vault tab)")


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


def apply_mastery_wave1_broken_fixes(db: ArzDatabase, base_db=None):
    """MASTERY WAVE 1 broken-class fixes B1-B6 + hygiene
    (docs/MASTERY_AUDIT_2026-07-09.md section 2; Will approved 2026-07-09).

    STANDING RULE (Will): NEVER remove skills from masteries. Everything here
    is a field edit, a ladder restore, or an anim-table RESTORATION of content
    the SV port dropped - zero removals.

    B1 Earth Meteor / B2 Storm Thunderball / B3 Spirit Bonespire: the SV port
    grafted anim tokens absent from the PC anim tables onto these player nukes
    -> SkillManager::StartSkill aborts every cast (hard-law #2). Fix = empty
    string (NOT '0': any non-empty non-resolving token still aborts).

    B4 Defense Shield Smash: port regression zeroed the damage payload
    (base ships a 12->61 ladder). Restore Min + Modifier ladders (FLOAT,
    ult-level length 10).

    B5 Dream Nightmare MasterMind aura: dead 3 ways - skillName1 points at a
    non-resolving path AND skillLevel1=0 on all 20 tiers (the omitted tree-
    modifier slot alternative is deliberately NOT taken: adding a tree slot is
    a Wave-2+ decision). Repoint to the resolving lowercase record + ramp
    skillLevel1 = min(tier, 12).

    B6 PC anim-table restoration (Neidan lane + RuneMaster lane): the mod's
    overridden anm_malepc01/anm_femalepc dropped tokens that Neidan and
    RuneMaster actives name (Ensnare/Flamesurge/ThunderClap/Barrage/Crosscut/
    Hew) -> those casts abort. Port the missing (clip, ref) pairs ROW-MATCHED
    from the base game tables into FREE indices only. HARD CAP: index 15 -
    no record anywhere in base populates SpecialAnim(Ref)N above 15 (measured
    2026-07-09), so writing 16+ would be a zero-precedent field shape (the
    B-TOXEUS-2 loader-abort class). Rows already at 15/15 (dHanded, sHanded,
    spear) are SKIPPED LOUDLY - replacing an existing entry could break other
    skills and is removal-adjacent (forbidden). PhantomStrike is deliberately
    NOT ported: only Neidan's 'Splash' modifier names it, Splash is unattached
    (never cast), and its base rows (dHanded/sHanded) are exactly the full
    ones.

    Hygiene (found by the new gate's negative test): two Dream PASSIVES ship
    the literal-'0' anim token (drxluciddream_premonition,
    drxdistortionfield). Passives never cast so it is inert, but '0' is the
    documented anti-pattern - normalize to ''.
    """
    print("\n=== MASTERY WAVE 1: broken-class fixes (B1-B6) ===")

    def _expect_anim(rec, expected):
        got = db.get_field_value(rec, 'skillSpecialAnimationName')
        got = got[0] if isinstance(got, list) else got
        if str(got) != expected:
            raise SystemExit(
                f"Mastery W1: {rec} skillSpecialAnimationName is {got!r}, "
                f"expected {expected!r} - the tree changed under the fix; "
                f"reconcile the spec before shipping")

    fixed = 0

    # ---- B1 / B2 / B3 + the two '0' passives -------------------------------
    anim_fixes = [
        (r'records\skills\earth\drxmeteor.dbr', 'MeteorShower', 'B1 Meteor'),
        (r'records\skills\storm\drxthunderball.dbr', 'Ensnare',
         'B2 Thunderball (also revives concussiveblast)'),
        (r'records\skills\spirit\drxenslavespirit.dbr', 'BoneSpire',
         'B3 Bonespire'),
        (r'records\xpack\skills\dream\drxluciddream_premonition.dbr', '0',
         "hygiene: literal-'0' anim on a passive"),
        (r'records\xpack\skills\dream\drxdistortionfield.dbr', '0',
         "hygiene: literal-'0' anim on a passive"),
    ]
    for rec, expected, label in anim_fixes:
        if not db.has_record(rec):
            raise SystemExit(f"Mastery W1: target record missing: {rec}")
        _expect_anim(rec, expected)
        db.set_field(rec, 'skillSpecialAnimationName', '', DATA_TYPE_STRING)
        print(f"  {label}: skillSpecialAnimationName {expected!r} -> ''")
        fixed += 1

    # ---- B4 Shield Smash damage-ladder restore ------------------------------
    smash = r'records\skills\defensive\drxweaponpool_shieldsmash.dbr'
    if not db.has_record(smash):
        raise SystemExit(f"Mastery W1: target record missing: {smash}")
    cur = db.get_field_value(smash, 'offensivePhysicalMin')
    cur0 = float(cur[0]) if isinstance(cur, list) and cur else float(cur or 0)
    if cur0 != 0.0:
        raise SystemExit(
            f"Mastery W1 B4: {smash} offensivePhysicalMin already {cur0} "
            f"(expected the zeroed regression) - reconcile before shipping")
    db.set_field(smash, 'offensivePhysicalMin',
                 [12.0, 18.0, 25.0, 31.0, 37.0, 43.0, 49.0, 55.0, 59.0, 61.0])
    db.set_field(smash, 'offensivePhysicalModifier',
                 [20.0, 24.0, 28.0, 32.0, 36.0, 40.0, 44.0, 47.0, 49.0, 50.0])
    print("  B4 Shield Smash: offensivePhysicalMin 0 -> 12..61 ladder; "
          "offensivePhysicalModifier 0 -> 20..50 ladder (len 10 = ult)")
    fixed += 1

    # ---- B5 Nightmare MasterMind aura revive --------------------------------
    mm_target = r'records\xpack\skills\dream\nightmare_petskill_mastermind.dbr'
    if not db.has_record(mm_target):
        raise SystemExit(f"Mastery W1 B5: repoint target missing: {mm_target}")
    nm_fixed = 0
    for tier in range(1, 21):
        rec = (r'records\xpack\skills\dream\pet\nightmare_%02d.dbr' % tier)
        if not db.has_record(rec):
            raise SystemExit(f"Mastery W1 B5: nightmare tier missing: {rec}")
        db.set_field(rec, 'skillName1', mm_target, DATA_TYPE_STRING)
        db.set_field(rec, 'skillLevel1', min(tier, 12), DATA_TYPE_INT)
        nm_fixed += 1
    print(f"  B5 Nightmare MasterMind: skillName1 repointed (resolving "
          f"lowercase path) + skillLevel1 ramp min(tier,12) on "
          f"{nm_fixed} tiers")
    fixed += 1

    # ---- B6 PC anim-table restoration ---------------------------------------
    if base_db is None:
        raise SystemExit(
            "Mastery W1 B6: base game arz REQUIRED to port the dropped PC "
            "anim references (pass the 5th build argument)")
    ported, skipped = _port_pc_anim_tokens(db, base_db)
    print(f"  B6 anim tables: {ported} (clip,ref) pair(s) restored from base "
          f"(row-matched, free indices <= 15 only); {skipped} row(s) full - "
          f"skipped by the conservative <=15 policy (graft #0 below completes "
          f"the melee rows above index 15)")
    fixed += 1

    # ---- GRAFT #0: melee-row completion (docs/SVAERA_MASTERY_COMPARISON.md) ----
    # The three FULL melee rows B6 just skipped (dHanded/sHanded/spear) are the
    # exact rows a Warfare/Neidan/Runemaster player's weapon uses; completing them
    # ABOVE index 15 (SVAERA-proven engine-valid) unblocks the half-casting melee
    # skills (Exploding Strikes/Hail of Axes/Arc Attack/Chi Realignment/Shen Pao/
    # Smoke Cloud) and is the prerequisite for the Warfare Slam graft. ADD-ONLY.
    melee_ported = _complete_pc_anim_melee_rows(db, base_db)
    print(f"  GRAFT #0 melee-row completion: {melee_ported} (clip,ref) pair(s) "
          f"restored onto dHanded/sHanded/spear at indices >15 "
          f"(Hew/Ensnare/Crosscut/Barrage/ThunderClap; 'Rest' preserved)")
    fixed += 1

    print(f"  Mastery Wave 1 broken fixes applied: {fixed} item(s)")
    return fixed


# Anim tokens B6 restores (lowercase). PhantomStrike deliberately excluded -
# see apply_mastery_wave1_broken_fixes docstring. 'taunt' added after the new
# gate's first live run caught mp_taunt (quest-reward tree, Skill_AttackRadius,
# anim 'Taunt'): base ships Taunt 8/8 in BOTH PC tables and the mod's tables
# dropped it - the same regression class as the Neidan tokens.
_B6_PORT_TOKENS = {'ensnare', 'flamesurge', 'thunderclap',
                   'barrage', 'crosscut', 'hew', 'taunt'}
_PC_ANM_TABLES = (r'records\creature\pc\anm\anm_malepc01.dbr',
                  r'records\creature\pc\anm\anm_femalepc.dbr')
_ANIM_IDX_CAP = 15   # measured: no base record populates SpecialAnim(Ref)N > 15


def _port_pc_anim_tokens(db: ArzDatabase, base_db: ArzDatabase):
    """Port missing (SpecialAnimN clip, SpecialAnimRefN name) pairs for the
    B6 tokens from the base game PC anim tables into the mod's, row-matched,
    into free indices only (hard cap 15). Returns (ported, skipped_full)."""
    mod_map = {n.replace('/', '\\').lower(): n for n in db.record_names()}
    base_map = {n.replace('/', '\\').lower(): n for n in base_db.record_names()}
    ported = skipped = 0
    for tbl in _PC_ANM_TABLES:
        key = tbl.lower()
        mrec, brec = mod_map.get(key), base_map.get(key)
        if not mrec or not brec:
            raise SystemExit(f"Mastery W1 B6: anim table missing "
                             f"(mod={mrec}, base={brec}) for {tbl}")
        mf = db.get_fields(mrec)
        bf = base_db.get_fields(brec)
        bmap = {k.split('###')[0]: tf for k, tf in bf.items()}

        # base row -> [(ref, clip)] for the port tokens
        base_pairs = {}
        for fname, tf in bmap.items():
            m = re.match(r'(.+?)SpecialAnimRef(\d+)$', fname)
            if not (m and tf.values):
                continue
            ref = str(tf.values[0]).strip()
            if ref.lower() not in _B6_PORT_TOKENS:
                continue
            row, idx = m.group(1), int(m.group(2))
            clip_tf = bmap.get(f'{row}SpecialAnim{idx}')
            clip = (str(clip_tf.values[0]).strip()
                    if clip_tf and clip_tf.values else '')
            if clip:
                base_pairs.setdefault(row, []).append((ref, clip))

        # mod row state: existing ref tokens + used indices (either field kind)
        mod_refs, used = {}, {}
        for k, tf in mf.items():
            fname = k.split('###')[0]
            m = re.match(r'(.+?)SpecialAnim(Ref)?(\d+)$', fname)
            if m and tf.values and str(tf.values[0]).strip():
                row, isref, idx = m.group(1), m.group(2), int(m.group(3))
                used.setdefault(row, set()).add(idx)
                if isref:
                    mod_refs.setdefault(row, set()).add(
                        str(tf.values[0]).strip().lower())

        for row in sorted(base_pairs):
            for ref, clip in base_pairs[row]:
                if ref.lower() in mod_refs.get(row, set()):
                    continue   # row already carries the token
                free = [i for i in range(1, _ANIM_IDX_CAP + 1)
                        if i not in used.get(row, set())]
                if not free:
                    print(f"    B6 SKIP {mrec.rsplit(chr(92), 1)[-1]} "
                          f"{row}: row FULL (15/15) - cannot port {ref!r} "
                          f"without replacing an entry (forbidden)")
                    skipped += 1
                    continue
                i = free[0]
                db.set_field(mrec, f'{row}SpecialAnim{i}', clip,
                             DATA_TYPE_STRING)
                db.set_field(mrec, f'{row}SpecialAnimRef{i}', ref,
                             DATA_TYPE_STRING)
                used.setdefault(row, set()).add(i)
                mod_refs.setdefault(row, set()).add(ref.lower())
                print(f"    B6 port {mrec.rsplit(chr(92), 1)[-1]} "
                      f"{row}[{i}] = {ref} ({clip.rsplit(chr(92), 1)[-1]})")
                ported += 1
    return ported, skipped


# GRAFT #0 (docs/SVAERA_MASTERY_COMPARISON.md, Will approved 2026-07-10): our PC
# anim tables are a lossy DRX merge that filled the three MELEE weapon rows to
# 15/15 with DRX tokens and DROPPED the vanilla melee clips those rows carry, so
# _port_pc_anim_tokens (cap 15) SKIPS them as "full" - leaving the melee tokens
# (Hew/Ensnare/Crosscut/Barrage/ThunderClap) present only on ranged/staff rows.
# A cast with a MELEE weapon equipped then aborts (StartSkill, hard-law #2). This
# half-casts Exploding Strikes(Hew)/Hail of Axes(Barrage)/Arc Attack(Crosscut)/
# Chi Realignment(ThunderClap)/Shen Pao+Smoke Cloud(Ensnare) and would abort the
# new Warfare Slam(Hew).
#
# BYTE PROOF (throwaway probe, OS temp scratchpad, 2026-07-10): SVAERA's own PC
# tables populate dHanded to index 23, sHanded/spear to 21 - on the SAME TQAE
# engine, in a shipping mod - so SpecialAnim(Ref) indices >15 ARE engine-valid;
# the old "no base record >15" note was a VANILLA-only observation, not an engine
# limit. The vanilla base clips for these (row,token) pairs are BYTE-IDENTICAL to
# SVAERA's (verified), so this restores them ROW-MATCHED FROM BASE into fresh
# CONTIGUOUS indices ABOVE 15. ADD ROWS ONLY: indices 1-15 are never touched, so
# our unique 'Rest' token (sHanded/spear) survives byte-identical. This is exactly
# the doc's graft #0 (row,token) set (no 'taunt' - that stays in the <=15
# non-melee coverage of _port_pc_anim_tokens).
_MELEE_ANIM_TABLES = (r'records\creature\pc\anm\anm_malepc01.dbr',
                      r'records\creature\pc\anm\anm_femalepc.dbr')
_MELEE_ROW_TOKENS = {
    'dHanded': ('Hew', 'Ensnare', 'Barrage', 'ThunderClap'),  # crosscut already 15<=
    'sHanded': ('Hew', 'Ensnare', 'Crosscut'),                # thunderclap already
    'spear':   ('Hew', 'Ensnare', 'Crosscut'),                # thunderclap already
}
_MELEE_PORT_EXPECT = 10   # pairs per table = 4 + 3 + 3


def _complete_pc_anim_melee_rows(db: ArzDatabase, base_db: ArzDatabase):
    """Restore the dropped vanilla melee clips onto the FULL dHanded/sHanded/spear
    rows at fresh contiguous indices >15, row-matched from the base game arz.
    ADD-ONLY. Fail-loud on any spec drift. Returns the total pairs added."""
    mod_map = {n.replace('/', '\\').lower(): n for n in db.record_names()}
    base_map = {n.replace('/', '\\').lower(): n for n in base_db.record_names()}
    total = 0
    for tbl in _MELEE_ANIM_TABLES:
        key = tbl.lower()
        mrec, brec = mod_map.get(key), base_map.get(key)
        if not mrec or not brec:
            raise SystemExit(f"Graft #0: PC anim table missing "
                             f"(mod={mrec}, base={brec}) for {tbl}")
        mf = db.get_fields(mrec)
        bf = base_db.get_fields(brec)
        bmap = {k.split('###')[0]: tf for k, tf in bf.items()}

        # base: row -> {token_lower: (ref_verbatim, clip)}
        base_row_tok = {}
        for fname, tf in bmap.items():
            m = re.match(r'(.+?)SpecialAnimRef(\d+)$', fname)
            if not (m and tf.values and str(tf.values[0]).strip()):
                continue
            row, idx = m.group(1), int(m.group(2))
            if row not in _MELEE_ROW_TOKENS:
                continue
            ref = str(tf.values[0]).strip()
            clip_tf = bmap.get(f'{row}SpecialAnim{idx}')
            clip = (str(clip_tf.values[0]).strip()
                    if clip_tf and clip_tf.values else '')
            if clip:
                base_row_tok.setdefault(row, {})[ref.lower()] = (ref, clip)

        # mod: row -> (existing ref-token set, max index used by EITHER field kind)
        mod_refs, maxidx = {}, {}
        for k, tf in mf.items():
            m = re.match(r'(.+?)SpecialAnim(Ref)?(\d+)$', k.split('###')[0])
            if m and tf.values and str(tf.values[0]).strip():
                row, isref, idx = m.group(1), m.group(2), int(m.group(3))
                if row not in _MELEE_ROW_TOKENS:
                    continue
                maxidx[row] = max(maxidx.get(row, 0), idx)
                if isref:
                    mod_refs.setdefault(row, set()).add(
                        str(tf.values[0]).strip().lower())

        per_table = 0
        for row, tokens in _MELEE_ROW_TOKENS.items():
            nxt = maxidx.get(row, 0) + 1
            if nxt <= 15:
                raise SystemExit(
                    f"Graft #0: {mrec} row {row!r} is NOT full (max idx "
                    f"{nxt - 1} < 15) - the lossy-merge assumption changed; "
                    f"reconcile the spec before shipping")
            for tok in tokens:
                if tok.lower() in mod_refs.get(row, set()):
                    raise SystemExit(
                        f"Graft #0: {mrec} row {row!r} already carries {tok!r} "
                        f"(<=15) - unexpected; reconcile before shipping")
                src = base_row_tok.get(row, {}).get(tok.lower())
                if not src:
                    raise SystemExit(
                        f"Graft #0: base table {brec} row {row!r} lacks a {tok!r} "
                        f"clip - cannot restore it row-matched")
                ref, clip = src
                db.set_field(mrec, f'{row}SpecialAnim{nxt}', clip,
                             DATA_TYPE_STRING)
                db.set_field(mrec, f'{row}SpecialAnimRef{nxt}', ref,
                             DATA_TYPE_STRING)
                mod_refs.setdefault(row, set()).add(tok.lower())
                print(f"    graft#0 {mrec.rsplit(chr(92), 1)[-1]} {row}[{nxt}] "
                      f"= {ref} ({clip.rsplit(chr(92), 1)[-1]})")
                nxt += 1
                per_table += 1
        if per_table != _MELEE_PORT_EXPECT:
            raise SystemExit(
                f"Graft #0: {mrec} added {per_table} pair(s), expected "
                f"{_MELEE_PORT_EXPECT} - spec drift, reconcile before shipping")
        total += per_table
    return total


def apply_mastery_wave1_boosts(db: ArzDatabase):
    """MASTERY WAVE 1 boosts: Defense / Earth / Storm
    (docs/MASTERY_AUDIT_2026-07-09.md section 3 Wave 1; Will approved all
    [WILL] items at the recommended numbers, 2026-07-09; executed under the
    overnight autonomous directive). Field edits + added ladders only - zero
    removals (the standing mastery law). Earth item 6 uses the VERIFIED base
    resist-shred field family offensiveTotalResistanceReductionPercentMin
    (47 base-record precedent; per-element fire fields have ZERO base values
    = zero-precedent shape, avoided)."""
    print("\n=== MASTERY WAVE 1: Defense/Earth/Storm boosts ===")

    def arr(rec, f):
        v = db.get_field_value(rec, f)
        if v is None:
            return None
        return list(v) if isinstance(v, list) else [v]

    def expect(cond, msg):
        if not cond:
            raise SystemExit(f"Mastery W1 boosts: {msg} - spec drift, reconcile")

    def ramp(lo, hi, n):
        if n <= 1:
            return [float(hi)]
        return [lo + (hi - lo) * i / (n - 1) for i in range(n)]

    # ---- DEFENSE ----------------------------------------------------------
    B = r'records\skills\defensive\drxbatter.dbr'
    v = arr(B, 'offensivePhysicalModifier')
    expect(v and abs(v[0] - 3.0) < 0.01 and abs(max(v) - 25.0) < 0.01,
           f"drxbatter offensivePhysicalModifier anchors {v and v[:1]}..{v and max(v)} != 3..25")
    ml = arr(B, 'skillMaxLevel'); ul = arr(B, 'skillUltimateLevel')
    m = int(ml[0]) if ml else 8
    u = int(ul[0]) if ul and int(ul[0]) > 0 else len(v)
    n = max(len(v), u)
    new = ramp(6.0, 40.0, min(m, n))
    if n > m:
        new += ramp(new[-1], 55.0, n - m + 1)[1:]
    db.set_field(B, 'offensivePhysicalModifier', [round(x, 1) for x in new])
    mc = arr(B, 'skillManaCost')
    expect(mc and abs(mc[0] - 18.0) < 0.01, f"drxbatter skillManaCost[0] {mc and mc[0]} != 18")
    db.set_field(B, 'skillManaCost', [max(1.0, round(x - 6.0, 1)) for x in mc])
    print(f"  DEF drxbatter: physMod 3..25 -> 6..55 (len {n}); manaCost -6/lvl")

    SC = r'records\skills\defensive\drxshieldcharge.dbr'
    expect(arr(SC, 'offensivePhysicalModifier') in (None, [0.0]),
           "drxshieldcharge already has a physical modifier ladder")
    scu = arr(SC, 'skillUltimateLevel'); scn = int(scu[0]) if scu else 12
    db.set_field(SC, 'offensivePhysicalModifier',
                 [round(x, 1) for x in ramp(15.0, 80.0, scn)])
    print(f"  DEF drxshieldcharge: +offensivePhysicalModifier 15..80 (len {scn})")

    H = r'records\skills\defensive\drxheave.dbr'
    expect(arr(H, 'offensivePercentCurrentLifeMin') in (None, [0.0]),
           "drxheave already has an execute ladder")
    hu = arr(H, 'skillUltimateLevel'); hn = int(hu[0]) if hu else 12
    hv = [1.0, 1.6, 2.2, 2.8, 3.4, 4.0, 4.4, 4.7, 4.9, 5.0, 5.0, 5.0]
    hv = (hv + [5.0] * hn)[:max(hn, len(hv))]
    db.set_field(H, 'offensivePercentCurrentLifeMin', hv)
    print(f"  DEF drxheave: +offensivePercentCurrentLifeMin 1..5%% (len {len(hv)})")

    CF = r'records\skills\defensive\drxcolossusform.dbr'
    cd = arr(CF, 'skillCooldownTime')
    expect(cd and abs(cd[0] - 360.0) < 0.01, f"colossus cd {cd} != 360")
    db.set_field(CF, 'skillCooldownTime', 180.0)
    sp = arr(CF, 'characterTotalSpeedModifier')
    expect(sp and abs(sp[0] - (-30.0)) < 0.01, f"colossus speed {sp} != -30")
    db.set_field(CF, 'characterTotalSpeedModifier', -15.0)
    ab = arr(CF, 'damageAbsorptionPercent')
    if ab and abs(max(ab) - 35.0) < 0.01:
        db.set_field(CF, 'damageAbsorptionPercent',
                     [round(x * 50.0 / 35.0, 1) for x in ab])
        print("  DEF drxcolossusform: cd 360->180, speed -30->-15, absorb x50/35")
    else:
        print(f"  DEF drxcolossusform: cd 360->180, speed -30->-15 "
              f"(absorb {ab} != 35 anchor; left)")

    DM = r'records\skills\defensive\drxdefensivemastery.dbr'
    er = arr(DM, 'defensiveElementalResistance')
    expect(er and len(er) > 40 and max(er[:40]) == 0.0,
           f"defensivemastery elemRes head not zeroed (len {er and len(er)})")
    db.set_field(DM, 'defensiveElementalResistance',
                 [round(0.2 * (i + 1), 1) for i in range(40)] + er[40:])
    print(f"  DEF drxdefensivemastery: elemRes ML1-40 0 -> 0.2/lvl (8%% @40); "
          f"tail {len(er) - 40} entries kept")

    RA = r'records\skills\defensive\drxbatter_rendarmor.dbr'
    rv = arr(RA, 'offensiveSlowDefensiveReductionMin')
    # stored POSITIVE (the tooltip renders the sign); the audit wrote -115.
    expect(rv and abs(max(rv) - 115.0) < 0.01,
           f"rendarmor ult {rv and max(rv)} != 115")
    db.set_field(RA, 'offensiveSlowDefensiveReductionMin',
                 [round(x * 160.0 / 115.0, 1) for x in rv])
    du = arr(RA, 'offensiveSlowDefensiveReductionDurationMin')
    if du and abs(du[0] - 5.0) < 0.01:
        db.set_field(RA, 'offensiveSlowDefensiveReductionDurationMin',
                     [6.0] * len(du))
        print("  DEF rendarmor: armor-amp x160/115 + duration 5->6s")
    else:
        print(f"  DEF rendarmor: armor-amp x160/115 (duration {du} != 5; left)")

    HC = r'records\skills\defensive\drxheave_cleave.dbr'
    expect(arr(HC, 'offensiveSlowBleedingMin') in (None, [0.0]),
           "heave_cleave already has base bleed")
    hcu = arr(HC, 'skillUltimateLevel'); hcn = int(hcu[0]) if hcu else 12
    db.set_field(HC, 'offensiveSlowBleedingMin',
                 [round(x, 1) for x in ramp(30.0, 120.0, hcn)])
    db.set_field(HC, 'offensiveSlowBleedingDurationMin', 3.0)
    print(f"  DEF heave_cleave: +bleed 30..120 over 3s (len {hcn}; its +245%% "
          f"amp finally has a base)")

    # ---- EARTH ------------------------------------------------------------
    MT = r'records\skills\earth\drxmeteor.dbr'
    mcd = arr(MT, 'skillCooldownTime')
    expect(mcd and abs(mcd[0] - 360.0) < 0.01, f"meteor cd {mcd} != 360")
    db.set_field(MT, 'skillCooldownTime', 60.0)
    VO = r'records\skills\earth\drxvolcanicorb.dbr'
    vcd = arr(VO, 'skillCooldownTime')
    expect(vcd and abs(vcd[0] - 4.0) < 0.01, f"volcanicorb cd {vcd} != 4")
    db.set_field(VO, 'skillCooldownTime', 1.5)
    print("  EARTH: Meteor cd 360->60; Volcanic Orb cd 4->1.5")

    EM = r'records\skills\earth\drxearthmastery.dbr'
    mn = arr(EM, 'characterMana')
    expect(mn and abs(mn[0] - 8.0) < 0.01 and abs(mn[39] - 320.0) < 0.01,
           f"earthmastery mana anchors {mn and (mn[0], mn[39])} != (8, 320)")
    db.set_field(EM, 'characterMana',
                 [float(12 * (i + 1)) for i in range(40)] + mn[40:])
    expect(arr(EM, 'characterSpellCastSpeed') in (None, [0.0]),
           "earthmastery already grants cast speed")
    db.set_field(EM, 'characterSpellCastSpeed',
                 [round(0.5 * (i + 1), 1) for i in range(40)])
    db.set_field(EM, 'characterRunSpeed',
                 [round(0.3 * (i + 1), 1) for i in range(40)])
    print("  EARTH drxearthmastery: mana 8..320 -> 12..480; +castSpeed 0..20%; "
          "+runSpeed 0..12% (ML1-40)")

    ML = r'records\skills\earth\drxeruption_moltenlava.dbr'
    expect(arr(ML, 'offensiveTotalResistanceReductionPercentMin') in (None, [0.0]),
           "moltenlava already has resist shred")
    mlu = arr(ML, 'skillUltimateLevel'); mln = int(mlu[0]) if mlu else 12
    db.set_field(ML, 'offensiveTotalResistanceReductionPercentMin',
                 [round(x, 1) for x in ramp(25.0, 40.0, mln)])
    db.set_field(ML, 'offensiveTotalResistanceReductionPercentDurationMin', 3.0)
    print(f"  EARTH eruption_moltenlava: +total-resist shred 25..40%% over 3s "
          f"(len {mln}; verified base field family, 47-record precedent)")

    # hygiene: dangling SandBox FX + Wildfire sounds (clear = absent, never '')
    for rec, flds in [
        (r'records\skills\earth\drxvolcanicorb.dbr',
         ('particleEffectName2', 'particleEffectName3')),
        (r'records\skills\earth\drxflamesurge.dbr',
         ('particleEffectName2', 'particleEffectName3')),
        (r'records\effects\earth\eruption_aeprojectile.dbr',
         ('projectileHitSound', 'projectileSwipeSound')),
    ]:
        ff = db.get_fields(rec) or {}
        for k, tf in ff.items():
            if k.split('###')[0] in flds and tf.values \
                    and any('sandbox' in str(x).lower() or 'wildfire' in str(x).lower()
                            for x in tf.values):
                tf.values = []
                db._modified.add(rec)
    print("  EARTH hygiene: dangling SandBox FX / Wildfire sound refs cleared")

    # ---- STORM ------------------------------------------------------------
    SM = r'records\skills\storm\drxstormmastery.dbr'
    lf = arr(SM, 'characterLife')
    expect(lf and len(lf) >= 40 and abs(lf[39] - 680.0) < 0.5,
           f"stormmastery life ML40 {lf and lf[39:40]} != 680")
    db.set_field(SM, 'characterLife',
                 [round(22.5 * (i + 1), 1) for i in range(40)] + lf[40:])
    print("  STORM drxstormmastery: life 17/lvl -> 22.5/lvl (ML40 680 -> 900)")

    # wisp ladder: edit the ladder the summon actually spawns
    WS = r'records\skills\storm\drxstormwispsummoning.dbr'
    so = arr(WS, 'spawnObjects')
    expect(so, "stormwispsummoning has no spawnObjects")
    wisp_paths = [str(p) for p in so if 'stormwisp_' in str(p).lower()]
    expect(wisp_paths, f"no stormwisp entries in spawnObjects: {so}")
    namemap = {nn.replace('/', '\\').lower(): nn for nn in db.record_names()}
    edited = 0
    for wp in wisp_paths:
        rec = namemap.get(wp.replace('/', '\\').lower())
        expect(rec, f"wisp record does not resolve: {wp}")
        t = int(rec.rsplit('_', 1)[-1].split('.')[0])
        db.set_field(rec, 'characterLife', float(240 + 50 * (t - 1)))
        edited += 1
    print(f"  STORM wisps: characterLife -> 240 + 50/tier on {edited} tier(s) "
          f"(ult ~{240 + 50 * 19}, kept < Shadow Stalker ~1440)")

    # wisp resist passive: pet-safe Skill_Passive clone wired into a free slot
    donor = (r'records\skills\spirit\drxpet\drxpet_skills'
             r'\bonepet_passive_attributes.dbr')
    newp = r'records\skills\storm\pet\stormwisp_resists_passive.dbr'
    expect(db.has_record(donor), f"passive donor missing: {donor}")
    if not db.has_record(newp):
        db.clone_record(donor, newp)
    for f_, val in [('characterLife', 0.0), ('characterLifeModifier', 0.0),
                    ('defensiveFreeze', 35.0), ('defensiveStun', 35.0),
                    ('defensiveFire', 35.0), ('defensiveLightning', 35.0),
                    ('defensiveCold', 35.0)]:
        db.set_field(newp, f_, val)
    db._modified.add(newp)
    wired = 0
    for wp in wisp_paths:
        rec = namemap[wp.replace('/', '\\').lower()]
        for slot in range(1, 17):
            if not arr(rec, f'skillName{slot}'):
                db.set_field(rec, f'skillName{slot}', newp)
                db.set_field(rec, f'skillLevel{slot}', 1)
                wired += 1
                break
    print(f"  STORM wisps: +resist passive (35%% freeze/stun/fire/lightning/"
          f"cold) wired into a free skill slot on {wired} tier(s)")

    EB = r'records\skills\storm\drxstormwisp_petskill_eyeofthestormbuff.dbr'
    expect(arr(EB, 'characterRunSpeedModifier') in (None, [0.0]),
           "eyeofthestorm already grants run speed")
    db.set_field(EB, 'characterRunSpeedModifier', 12.0)
    print("  STORM eye-of-the-storm aura: +12%% run speed (party-wide)")

    fxv = arr(WS, 'targetFxPakName')
    if fxv and str(fxv[0]).startswith('Records\\Effects\\PetFX\\ '):
        db.set_field(WS, 'targetFxPakName', str(fxv[0]).replace('\\ ', '\\'))
        print("  STORM hygiene: wisp summon targetFxPakName leading space fixed")
    print("  Mastery Wave 1 boosts applied (Defense 7, Earth 5+hyg, Storm 5)")


def apply_mastery_wave2_boosts(db: ArzDatabase, base_db=None):
    """MASTERY WAVE 2 boosts: Warfare / Nature / Spirit / Dream + the two DLC
    masteries RuneMaster (slot 11) / Neidan (slot 12).
    (docs/MASTERY_AUDIT_2026-07-09.md section 3 Wave 2 + PART III per-mastery
    boost lists; Will approved BOTH waves 2026-07-09; build32.)

    STANDING RULE (Will): NEVER remove skills/tree slots from masteries.
    Everything here is a field edit, an added ladder, a base->mod override, or
    dangling-ref cleanup INSIDE a record (the standing rule explicitly allows
    clearing dead particleEffectName / placeholder skillName slots on PET
    records). Borderline no-ops are KEPT, never removed (Spirit bonepet
    skillName6; Dream phantomstrike self-slow is ZEROED in place, field kept).

    ALREADY-SHIPPED (Wave 1 B6): the #1 audited RuneMaster + Neidan fix - the
    dropped Ensnare/Flamesurge/ThunderClap/Barrage/Crosscut/Hew PC anims that
    abort their casts - was ported by _port_pc_anim_tokens and is VERIFIED by
    the player-skill-anim gate that runs AFTER this function. It is NOT
    re-implemented here (BACKLOG: "verify before re-implementing").

    base_db is REQUIRED: RuneMaster + Neidan records resolve ONLY from the base
    game, so they are imported verbatim as mod overrides
    (_import_base_game_record) before the field edits."""
    print("\n=== MASTERY WAVE 2: Warfare/Nature/Spirit/Dream + RuneMaster/Neidan ===")

    def arr(rec, f):
        v = db.get_field_value(rec, f)
        if v is None:
            return None
        return list(v) if isinstance(v, list) else [v]

    def expect(cond, msg):
        if not cond:
            raise SystemExit(f"Mastery W2: {msg} - spec drift, reconcile")

    def need(rec):
        expect(db.has_record(rec), f"target record missing: {rec}")

    def eq(a, b):
        return a is not None and b is not None and len(a) == len(b) \
            and all(abs(float(x) - float(y)) < 1e-4 for x, y in zip(a, b))

    def clear_field(rec, f):
        """Clear a field to ABSENT (tf.values = []) - the base-game 'unused'
        shape for a dangling ref (never '' = a live empty string)."""
        ff = db.get_fields(rec) or {}
        for k, tf in ff.items():
            if k.split('###')[0] == f:
                tf.values = []
                db._modified.add(rec)
                return True
        return False

    namemap = {n.replace('/', '\\').lower(): n for n in db.record_names()}

    # ---- WARFARE ----------------------------------------------------------
    AH = r'records\skills\warfare\drxancestralhorn.dbr'; need(AH)
    for f, old in (('skillCooldownTime', 300.0),
                   ('skillCooldownReductionModifier', 300.0)):
        v = arr(AH, f); expect(v and abs(v[0] - old) < 0.01,
                               f"ancestralhorn {f} {v} != {old}")
        db.set_field(AH, f, 120.0)
    ttl = arr(AH, 'spawnObjectsTimeToLive')
    expect(ttl and abs(ttl[0] - 30.0) < 0.01, f"ancestralhorn TTL {ttl} != 30")
    db.set_field(AH, 'spawnObjectsTimeToLive', 45.0)
    print("  WARFARE ancestralhorn: cd/crm 300->120, TTL 30->45 (~10%->37% pet uptime)")

    BS = r'records\skills\warfare\drxbattlestandard.dbr'; need(BS)
    bt = arr(BS, 'spawnObjectsTimeToLive')
    expect(bt and len(bt) == 10 and abs(bt[0] - 18.0) < 0.01 and abs(bt[-1] - 36.0) < 0.01,
           f"battlestandard TTL {bt and (bt[0], bt[-1], len(bt))} != (18,36,10)")
    db.set_field(BS, 'spawnObjectsTimeToLive',
                 [round(24.0 + 26.0 * i / 9.0, 1) for i in range(10)])
    print("  WARFARE battlestandard: TTL 18..36 -> 24..50 (banner amp ~50%->~70% uptime)")

    WW = r'records\skills\warfare\drxwarwind.dbr'; need(WW)   # OPTIONAL (feel)
    for f in ('skillCooldownTime', 'skillCooldownReductionModifier'):
        v = arr(WW, f); expect(v and abs(v[0] - 12.0) < 0.01, f"warwind {f} {v} != 12")
        db.set_field(WW, f, 8.0)
    print("  WARFARE warwind (optional): cd/crm 12->8 (pre-Refinement AoE feel)")

    armband = 'records\\item\\equipmentarmband\\default\\m_wraitharmband.dbr'
    expect(armband in namemap, f"spectralsoldier armband target missing: {armband}")
    ss_fixed = 0
    for t in range(1, 21):
        rec = r'records\skills\warfare\pets\spectralsoldier_%02d.dbr' % t
        need(rec)
        cur = arr(rec, 'lootForearmItem1')
        if cur and 'armbands\\' in str(cur[0]).lower():
            db.set_field(rec, 'lootForearmItem1', armband, DATA_TYPE_STRING)
            ss_fixed += 1
    expect(ss_fixed == 20, f"spectralsoldier armband fix hit {ss_fixed}/20")
    print(f"  WARFARE spectralsoldier: dangling armband path fixed on {ss_fixed}/20 tiers")

    # ---- NATURE -----------------------------------------------------------
    FN = r'records\skills\nature\drxforceofnature.dbr'; need(FN)
    for f in ('skillCooldownTime', 'skillCooldownReductionModifier'):
        v = arr(FN, f); expect(v and abs(v[0] - 360.0) < 0.01, f"forceofnature {f} {v} != 360")
        db.set_field(FN, f, 180.0)
    print("  NATURE forceofnature: cd/crm 360->180 (~17%->33% treant uptime; 180 not 120 = no Occult overshoot)")

    # petBonus ML1-40 ramp. Overshoot check (audit S4-F, Will-approved): +30%
    # pet total-damage at ML40 is conservative - Occult's mastery grants NO pet
    # damage bonus, so even stacked with Overgrowth(+60%)/Susceptibility(-54%)
    # no Nature pet exceeds Occult's Shadow-Stalker peak.
    NPB = r'records\skills\nature\drxnaturemastery_petbonus.dbr'; need(NPB)
    otd = arr(NPB, 'offensiveTotalDamageModifier')
    expect(otd in (None, [0.0]), f"naturemastery petBonus already has a pet-dmg ladder: {otd}")
    db.set_field(NPB, 'offensiveTotalDamageModifier',
                 [round(0.75 * (i + 1), 2) for i in range(40)])
    dp = arr(NPB, 'defensiveProtection')
    expect(dp in (None, [0.0]), f"naturemastery petBonus already grants protection: {dp}")
    db.set_field(NPB, 'defensiveProtection',
                 [round(4.0 * (i + 1), 1) for i in range(40)])
    print("  NATURE naturemastery petBonus: +pet dmg 0->30%% + protection 0->160 (ML1-40)")

    for rec in (r'records\skills\nature\drxregrowth_acceleratedgrowth.dbr',
                r'records\skills\nature\drxrenewal.dbr'):
        need(rec)
        cd_ = arr(rec, 'skillCooldownTime'); dc = arr(rec, 'defensiveConvert')
        expect(eq(cd_, dc), f"{rec} defensiveConvert != skillCooldownTime (already fixed?)")
        clear_field(rec, 'defensiveConvert')
    print("  NATURE accel-growth+renewal: dangling defensiveConvert (==cooldown ladder, silent charm-res malus) cleared; cooldown kept")

    WM = r'records\skills\nature\drxwolf_petskill_maul.dbr'; need(WM)
    for f in ('particleEffectName1', 'warmUpEffectName'):
        cur = arr(WM, f)
        if cur and 'lethal_strike01' in str(cur[0]).lower():
            db.set_field(WM, f, 'records\\effects\\default\\damage01.dbr', DATA_TYPE_STRING)
    WSI = r'records\skills\nature\drxwolf_petskill_survivalinstinct.dbr'; need(WSI)
    cur = arr(WSI, 'skillActivatedAuraName')
    if cur and 'adrenaline_fx01' in str(cur[0]).lower():
        db.set_field(WSI, 'skillActivatedAuraName',
                     'records\\effects\\default\\buff07.dbr', DATA_TYPE_STRING)
    nymph_ctrl = 'records\\skills\\nature\\pet\\controller_nymph01_aggressive.dbr'
    expect(nymph_ctrl in namemap, f"nymph aggressive controller missing: {nymph_ctrl}")
    ny = 0
    for t in range(1, 21):
        rec = r'records\skills\nature\pet\sylvannymph_%02d.dbr' % t
        if db.has_record(rec):
            cur = arr(rec, 'controllerAggressive')
            if cur and 'controller_nymph01_normal' in str(cur[0]).lower():
                db.set_field(rec, 'controllerAggressive', nymph_ctrl, DATA_TYPE_STRING)
                ny += 1
    print(f"  NATURE wolf/sylvan dangling FX: maul->Damage01, survivalinstinct->Buff07, nymph controllerAggressive repointed on {ny} tier(s)")

    # ---- SPIRIT -----------------------------------------------------------
    OS = r'records\skills\spirit\drxoutsidersummons.dbr'; need(OS)
    ocd = arr(OS, 'skillCooldownTime')
    expect(ocd and abs(ocd[0] - 360.0) < 0.01, f"outsider cd {ocd} != 360")
    db.set_field(OS, 'skillCooldownTime', 120.0)
    ott = arr(OS, 'spawnObjectsTimeToLive')
    expect(ott and abs(ott[0] - 30.0) < 0.01, f"outsider TTL {ott} != 30")
    db.set_field(OS, 'spawnObjectsTimeToLive', 60.0)
    print("  SPIRIT outsidersummons (Ether Lord): cd 360->120, TTL 30->60 (~8%->50% uptime; stays temporary)")

    DW = r'records\skills\spirit\drxdeathward.dbr'; need(DW)
    dcd = arr(DW, 'skillCooldownTime')
    expect(dcd and abs(dcd[0] - 300.0) < 0.01, f"deathward cd {dcd} != 300")
    db.set_field(DW, 'skillCooldownTime', 180.0)
    print("  SPIRIT deathward: cd 300->180 (panic on Cornered-Rage cadence)")

    unpref = plc = 0
    for t in range(1, 21):
        rec = r'records\skills\spirit\drxpet\bonepet%02d.dbr' % t
        need(rec)
        s4 = arr(rec, 'skillName4')
        if s4 and str(s4[0]).lower().startswith('xxx'):
            db.set_field(rec, 'skillName4', str(s4[0])[3:], DATA_TYPE_STRING)
            unpref += 1
        s2 = arr(rec, 'skillName2')
        if s2 and 'drxplaceholder' in str(s2[0]).lower():
            clear_field(rec, 'skillName2'); plc += 1
    print(f"  SPIRIT bonepet: spiritbreath 'xxx' unprefixed on {unpref} tier(s); dangling drxplaceholder skillName2 cleared on {plc} tier(s); skillName6 no-op KEPT")

    SBR = r'records\skills\spirit\drxpet\drxpet_skills\bonescourge_spiritbreath.dbr'
    need(SBR)
    for f in ('particleEffectName2', 'particleEffectName3'):
        cur = arr(SBR, f)
        if cur and 'sandbox' in str(cur[0]).lower():
            clear_field(SBR, f)
    print("  SPIRIT bonescourge_spiritbreath: dangling SandBox particleEffectName2/3 cleared (re-enable is clean)")

    # ── SPIRIT: re-enable the Liche King's signature skeleton summons (GROUP 3,
    # BACKLOG "wraithlord skelly re-enable, pet-cap unverifiable"). The DRX author
    # DISABLED wraithlord_01..20.dbr skillName15/16 by 'xxx'-prefixing their paths
    # (drx_lichskill_skellysummon2/3). Re-enabling DISABLED original content is
    # ENCOURAGED (Will's standing mastery ruling #4); the summon chain is fully
    # built and resolves (Skill_AttackProjectileSpawnPet -> drx_skelly_01..20,
    # rev2skelly.msh; scratchpad/skelly_chain.py). SURGICAL: only the 'xxx' prefix
    # is stripped - skillLevel ladders are left EXACTLY as authored (the original
    # tier ramp), and the redundant soulblight double-slot (skillName4 + 14) is
    # KEPT UNTOUCHED (dropping a duplicate = a slot REMOVAL, forbidden without
    # Will's per-item approval). Revertible before the next Steam ship (re-add the
    # 'xxx' prefix) if Will's in-game pet-cap test shows the capstone over-summons.
    SS2 = r'records\skills\spirit\drxpet\drxpet_skills\drx_lichskill_skellysummon2.dbr'
    SS3 = r'records\skills\spirit\drxpet\drxpet_skills\drx_lichskill_skellysummon3.dbr'
    expect(db.has_record(SS2) and db.has_record(SS3),
           "wraithlord skellysummon2/3 target records missing (re-enable would dangle)")
    wl_reenabled = 0
    for t in range(1, 21):
        rec = r'records\skills\spirit\drxpet\wraithlord_%02d.dbr' % t
        need(rec)
        touched = False
        for slot in ('skillName15', 'skillName16'):
            cur = arr(rec, slot)
            if cur and str(cur[0]).lower().startswith('xxx'):
                db.set_field(rec, slot, str(cur[0])[3:], DATA_TYPE_STRING)
                touched = True
        if touched:
            wl_reenabled += 1
    expect(wl_reenabled == 20,
           f"wraithlord re-enable touched {wl_reenabled}/20 tiers (expected 20 "
           f"'xxx'-disabled skellysummon2/3 pairs)")
    print(f"  SPIRIT wraithlord (Liche King): skellysummon2/3 'xxx' RE-ENABLED on "
          f"{wl_reenabled}/20 tiers (chain resolves to drx_skelly_01..20); soulblight "
          f"double-slot KEPT (removal forbidden); revertible")

    # ---- DREAM (exact numbers from PART III) ------------------------------
    tf_cleared = 0
    for t in range(1, 21):
        rec = r'records\xpack\skills\dream\pet\nightmare_%02d.dbr' % t
        need(rec)
        touched = False
        for f in ('skillName4', 'buffSelfSkillName'):
            cur = arr(rec, f)
            if cur and 'dreampet_timefield' in str(cur[0]).lower():
                clear_field(rec, f); touched = True
        if touched:
            clear_field(rec, 'skillLevel4'); tf_cleared += 1
    print(f"  DREAM nightmare: dangling timefield self-buff cleared on {tf_cleared} tier(s) (MasterMind repoint already shipped W1 B5)")

    PH = r'records\xpack\skills\dream\drxphantasm.dbr'; need(PH)
    pcd = arr(PH, 'skillCooldownTime')
    expect(pcd and abs(pcd[0] - 180.0) < 0.01, f"phantasm cd {pcd} != 180")
    db.set_field(PH, 'skillCooldownTime', 120.0)
    ptt = arr(PH, 'spawnObjectsTimeToLive')
    expect(ptt and len(ptt) == 20 and abs(ptt[0] - 15.0) < 0.01 and abs(ptt[-1] - 25.0) < 0.01,
           f"phantasm TTL {ptt and (ptt[0], ptt[-1], len(ptt))} != (15,25,20)")
    db.set_field(PH, 'spawnObjectsTimeToLive',
                 [round(15.0 + 15.0 * i / 19.0, 1) for i in range(20)])
    print("  DREAM phantasm: cd 180->120; TTL 15..25 -> 15..30 (~14%->~30% uptime)")

    pl_clear = 0
    for t in range(1, 21):
        rec = r'records\xpack\skills\dream\drxpet\phantasm_%02d.dbr' % t
        need(rec)
        lf = arr(rec, 'lootFinger1Item2')
        if lf and 'ringall' in str(lf[0]).lower():
            clear_field(rec, 'lootFinger1Item2'); pl_clear += 1
    print(f"  DREAM phantasm pet: dangling RingAll loot ref cleared on {pl_clear} tier(s)")

    PB = r'records\xpack\skills\dream\pet\drxnightmare_psionicbeam.dbr'; need(PB)
    for f in ('offensivePhysicalMin', 'offensiveLifeMin'):
        v = arr(PB, f)
        expect(v and len(v) == 20 and abs(v[0] - 8.0) < 0.01 and abs(v[-1] - 66.0) < 0.01,
               f"psionicbeam {f} {v and (v[0], v[-1], len(v))} != (8,66,20)")
        db.set_field(PB, f, [round(x * 2.0, 1) for x in v])
    print("  DREAM nightmare psionicbeam: offensivePhysical/LifeMin [8..66] x2 -> [16..132] (elite-pet share)")

    for rec, mx in ((r'records\xpack\skills\dream\drxdistortreality_temporalrift.dbr', 16),
                    (r'records\xpack\skills\dream\drxspellbreaker.dbr', 12),
                    (r'records\xpack\skills\dream\drxspellbreaker_spellshock.dbr', 12)):
        need(rec)
        mc = arr(rec, 'skillManaCost'); ul = arr(rec, 'skillUltimateLevel')
        uln = int(ul[0]) if ul else mx
        expect(mc and len(mc) == 10 and uln == mx,
               f"{rec} manaCost/ult {mc and len(mc)}/{uln} != (10,{mx})")
        step = round(float(mc[-1]) - float(mc[-2]), 2)
        ext = [round(float(x), 1) for x in mc] + \
              [round(float(mc[-1]) + step * (k + 1), 1) for k in range(uln - len(mc))]
        db.set_field(rec, 'skillManaCost', ext)
    print("  DREAM mana ladders: temporalrift 10->16, spellbreaker 10->12, spellshock 10->12 (continued step)")

    PS = r'records\xpack\skills\dream\drxphantomstrike.dbr'; need(PS)
    rs = arr(PS, 'characterRunSpeedModifier')
    expect(rs and abs(rs[0] - (-11.0)) < 0.01 and abs(min(rs) - (-50.0)) < 0.01,
           f"phantomstrike runspeed {rs and (rs[0], min(rs))} != (-11,-50)")
    db.set_field(PS, 'characterRunSpeedModifier', [0.0] * len(rs))
    print(f"  DREAM phantomstrike: self-slow [-11..-50] -> zeroed (len {len(rs)}; blink no longer self-roots; field kept per rule)")

    # ---- RUNEMASTER (slot 11; base-only -> mod overrides) -----------------
    expect(base_db is not None,
           "RuneMaster/Neidan need base_db (5th build arg) to override base-only records")
    RM = r'records\xpack2\skills\runemaster\runemaster_mastery.dbr'
    if not db.has_record(RM):
        _import_base_game_record(db, base_db, RM)
    need(RM)
    rl = arr(RM, 'characterLife')
    expect(rl and len(rl) == 40 and abs(rl[0] - 20.0) < 0.01 and abs(rl[-1] - 800.0) < 0.01,
           f"runemaster life {rl and (rl[0], rl[-1], len(rl))} != (20,800,40)")
    db.set_field(RM, 'characterLife', [round(29.0 * (i + 1), 1) for i in range(40)])
    rmn = arr(RM, 'characterMana')
    expect(rmn in (None, [0.0]) or (rmn and abs(float(rmn[0])) < 0.01),
           f"runemaster mana already granted: {rmn and rmn[:1]}")
    db.set_field(RM, 'characterMana', [round(10.0 * (i + 1), 1) for i in range(40)])
    print("  RUNEMASTER mastery: life 800->1160 (ML40); mana 0->400 (ML40; was the sole 0-mana INT mastery)")

    MA = r'records\xpack2\skills\runemaster\menhiraltar.dbr'
    if not db.has_record(MA):
        _import_base_game_record(db, base_db, MA)
    need(MA)
    mcd = arr(MA, 'skillCooldownTime')
    expect(mcd and abs(mcd[0] - 240.0) < 0.01, f"menhiraltar cd {mcd} != 240")
    db.set_field(MA, 'skillCooldownTime', 120.0)
    mtt = arr(MA, 'spawnObjectsTimeToLive')
    if mtt and abs(mtt[0] - 45.0) < 0.01:
        db.set_field(MA, 'spawnObjectsTimeToLive', 60.0)
    print("  RUNEMASTER menhiraltar (Guardian Stones): cd 240->120, TTL 45->60 (~19%->~50% pet uptime)")

    # ---- NEIDAN (slot 12; base-only -> mod overrides) ---------------------
    NM = r'records\xpack4\skills\neidan\neidanmastery.dbr'
    if not db.has_record(NM):
        _import_base_game_record(db, base_db, NM)
    need(NM)
    nl = arr(NM, 'characterLife')
    expect(nl and len(nl) == 40 and abs(nl[0] - 22.5) < 0.01 and abs(nl[-1] - 900.0) < 0.01,
           f"neidan life {nl and (nl[0], nl[-1], len(nl))} != (22.5,900,40)")
    db.set_field(NM, 'characterLife', [round(26.25 * (i + 1), 2) for i in range(40)])
    print("  NEIDAN mastery: life 900->1050 (ML40; still squishiest/caster-leaning)")

    TS = r'records\xpack4\skills\neidan\terracotta_servant.dbr'
    if not db.has_record(TS):
        _import_base_game_record(db, base_db, TS)
    need(TS)
    pl = arr(TS, 'petLimit')
    expect(pl and len(pl) == 10 and int(pl[0]) == 1 and int(pl[-1]) == 2,
           f"terracotta petLimit {pl} != [1..2] len10")
    db.set_field(TS, 'petLimit', [1, 1, 1, 1, 1, 1, 1, 2, 2, 3])
    print("  NEIDAN terracotta_servant: petLimit [1x9,2] -> [1x7,2,2,3] (2 constructs by skill L8, 3 at L10)")

    DBB = r'records\xpack4\skills\neidan\deathbomb.dbr'
    if not db.has_record(DBB):
        _import_base_game_record(db, base_db, DBB)
    need(DBB)
    sc = arr(DBB, 'skillCastChance')
    expect(sc and len(sc) == 16 and abs(sc[0] - 33.0) < 0.01 and abs(sc[-1] - 33.0) < 0.01,
           f"deathbomb castChance {sc and (sc[0], sc[-1], len(sc))} != (33,33,16)")
    db.set_field(DBB, 'skillCastChance', [45.0] * 16)
    print("  NEIDAN deathbomb: skillCastChance 33 -> 45 (x16; corpse-explosion clear engine)")

    SP = r'records\xpack4\skills\neidan\splash.dbr'
    if not db.has_record(SP):
        _import_base_game_record(db, base_db, SP)
    need(SP)
    dep = arr(SP, 'skillDependancy')
    expect(not dep, f"splash already has skillDependancy: {dep}")
    db.set_field(SP, 'skillDependancy',
                 'records\\xpack4\\skills\\neidan\\shenpao.dbr', DATA_TYPE_STRING)
    print("  NEIDAN splash (Spreading Influence): +skillDependancy=shenpao (attaches the ML40 modifier)")

    print("  Mastery Wave 2 boosts applied "
          "(Warfare 4, Nature 4, Spirit 4, Dream 6, RuneMaster 2, Neidan 4)")


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

    # Fix missing description tags (skills that have icons but no description).
    # MOD_DESC_FIX_TAGS is module-level so build_text_arc.py can reuse it as the
    # authoritative source of these mod-owned description tags for the manifest.
    for path, desc_tag in MOD_DESC_FIX_TAGS.items():
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


def _import_boat_captain(db: ArzDatabase, base_db):
    """Import the Egypt boat captain NPC from base game into SV database.

    This NPC has a humanoid mesh and is known to work with Action_BoatDialog.
    """
    boat = r'records\creature\npc\speaking\greece\knossos_boatmantoegypt.dbr'
    if db.has_record(boat):
        return boat
    if not base_db:
        return None
    for name in base_db.record_names():
        if name.lower() == boat.lower():
            fields = base_db.get_fields(name)
            template = ''
            for key, tf in fields.items():
                if key.split('###')[0] == 'templateName' and tf.values:
                    template = tf.values[0]
                    break
            _ensure_record(db, boat, template or 'database\\Templates\\Npc.tpl')
            for key, tf in fields.items():
                fname = key.split('###')[0]
                db.set_field(boat, fname, tf.values[0] if len(tf.values) == 1 else tf.values, tf.dtype)
            db._modified.add(boat)
            print(f"  Imported boat captain from base game: {boat}")
            return boat
    return None


def _import_dialog_needed(db: ArzDatabase, base_db):
    """Import Dialog Needed.dbr from base game - required for NPC interaction.

    This DialogPak record makes NPCs clickable when assigned via
    Action_UpdateNPCDialog in quest files. Without it, NPCs render
    but have no yellow icon and can't be clicked.
    """
    dialog_path = r'records\dialog\story\dialog needed.dbr'
    if db.has_record(dialog_path):
        return dialog_path
    if not base_db:
        return None
    for name in base_db.record_names():
        if name.lower() == dialog_path.lower():
            fields = base_db.get_fields(name)
            template = ''
            for key, tf in fields.items():
                if key.split('###')[0] == 'templateName' and tf.values:
                    template = tf.values[0]
                    break
            _ensure_record(db, dialog_path, template or 'database\\Templates\\DialogPak.tpl')
            for key, tf in fields.items():
                fname = key.split('###')[0]
                db.set_field(dialog_path, fname, tf.values[0] if len(tf.values) == 1 else tf.values, tf.dtype)
            db._modified.add(dialog_path)
            print(f"  Imported Dialog Needed.dbr from base game")
            return dialog_path
    return None


def create_uber_dungeon_portal(db: ArzDatabase, base_db=None):
    """Create NPC portal DBRs for the Uber Dungeon entrance and return.

    Uses the NPC + Action_BoatDialog pattern (like the Secret Place portals).
    The NPC objects are injected into the map by build_section_surgery.py.
    The quest file wiring is handled by build_section_surgery.py + build_quest_files.py.
    """
    print("\n=== Patch 12: Create Uber Dungeon portal records ===")

    # Import Dialog Needed.dbr (required for NPC clickability)
    _import_dialog_needed(db, base_db)

    entrance_npc = r'records\quests\portal_uberdungeon_entrance.dbr'
    return_npc = r'records\quests\portal_uberdungeon_return.dbr'

    # Import boat captain from base game (humanoid mesh, known clickable)
    boat_template = _import_boat_captain(db, base_db)
    portal_template = r'records\drxmap\xurder\portaldudes\portal to act 1.dbr'
    src = boat_template or portal_template

    for npc_path, desc in [
        (entrance_npc, 'Portal NPC to Uber Dungeon at Crisaeos Falls'),
        (return_npc, 'Return portal NPC from Uber Dungeon to Crisaeos Falls'),
    ]:
        db.clone_record(src, npc_path)
        db.set_field(npc_path, 'FileDescription', desc, DATA_TYPE_STRING)
        db.set_field(npc_path, 'ActorName', 'Mysterious Portal', DATA_TYPE_STRING)
        db.set_field(npc_path, 'description', 'xtagMysteriousPortal', DATA_TYPE_STRING)
        db.set_field(npc_path, 'startVisible', 1, DATA_TYPE_INT)
        db.set_field(npc_path, 'IncludeInMap', 1, DATA_TYPE_INT)
        db._modified.add(npc_path)
        print(f"  Created NPC: {npc_path} (cloned from {src})")


def create_blood_cave_portal(db: ArzDatabase, base_db=None):
    """Create NPC portal DBRs for the Blood Cave entrance and return.

    Clones from the Egypt boat captain NPC (known working interactable NPC)
    and configures for portal teleportation via Action_BoatDialog quest.
    """
    print("\n=== Patch 13: Create Blood Cave portal records ===")

    entrance_npc = r'records\quests\portal_bloodcave_entrance.dbr'
    return_npc = r'records\quests\portal_bloodcave_return.dbr'

    # Boat captain should already be imported by create_uber_dungeon_portal
    boat_template = r'records\creature\npc\speaking\greece\knossos_boatmantoegypt.dbr'
    if not db.has_record(boat_template):
        _import_boat_captain(db, base_db)
    portal_template = r'records\drxmap\xurder\portaldudes\portal to act 1.dbr'
    src = boat_template if db.has_record(boat_template) else portal_template

    for npc_path, desc, name in [
        (entrance_npc, 'Portal NPC to Blood Cave at Hidden Valley', 'Blood Cave Portal'),
        (return_npc, 'Return portal NPC from Blood Cave to Hidden Valley', 'Return Portal'),
    ]:
        db.clone_record(src, npc_path)
        db.set_field(npc_path, 'FileDescription', desc, DATA_TYPE_STRING)
        db.set_field(npc_path, 'ActorName', name, DATA_TYPE_STRING)
        db.set_field(npc_path, 'description', 'xtagMysteriousPortal', DATA_TYPE_STRING)
        db.set_field(npc_path, 'startVisible', 1, DATA_TYPE_INT)
        db.set_field(npc_path, 'IncludeInMap', 1, DATA_TYPE_INT)
        db._modified.add(npc_path)
        print(f"  Created NPC: {npc_path} (cloned from {src})")


def fix_soul_bitmaps(db: ArzDatabase):
    """Fix soul inventory icons by pointing bitmap to SVItems.arc paths.

    The original SV souls reference Items\\miscellaneous\\{n,e,l}_soul.tex
    which doesn't exist in Items.arc. The actual 32x32 icons are in
    SVItems.arc. We rewrite ALL soul bitmap fields to use SVItems paths
    so the game can resolve them.
    """
    print("\n=== Patch: Fix soul inventory icon bitmaps ===")

    # Map old broken paths to correct SVItems paths
    bitmap_fix = {
        'items\\miscellaneous\\n_soul.tex': 'SVItems\\jewelry\\soul_n_icon.tex',
        'items\\miscellaneous\\e_soul.tex': 'SVItems\\jewelry\\soul_e_icon.tex',
        'items\\miscellaneous\\l_soul.tex': 'SVItems\\jewelry\\soul_l_icon.tex',
    }

    patched = 0
    for rname in db.record_names():
        if 'soul' not in rname.lower():
            continue
        fields = db.get_fields(rname)
        if not fields:
            continue
        bmp_tf = fields.get('bitmap')
        if not bmp_tf:
            continue
        old_val = str(bmp_tf.value).lower().replace('/', '\\')
        if old_val in bitmap_fix:
            new_val = bitmap_fix[old_val]
            db.set_field(rname, 'bitmap', new_val, DATA_TYPE_STRING)
            patched += 1

    print(f"  Soul bitmap paths fixed: {patched}")


# ═══════════════════════════════════════════════════════════════════════════
# BUILD36 LANE B: SVAERA mastery-skill graft (18 skills) + Runemaster buffs
# docs/SVAERA_MASTERY_COMPARISON.md (soa gave verbal permission to reuse SVAERA).
#
# SCOPE: 14 player-tree mastery skills (Warfare/Defense/Earth/Storm/Nature/Dream)
# each appended as a NEW tree slot + a NEW mastery-panel UI button, PLUS their
# recursive .dbr closure (4 gameplay support records: a nymph pet-skill, the
# Doppelganger pet + its aura + a pet conversion-immunity passive = 18 grafted
# "skills"), PLUS 3 asset-closure records (2 Frost-Nova FX + 1 Doppelganger anim
# table). The Rune Golem is NOT here (lane A owns it in apply_svc_patches.py).
#
# LAWS honored (verified against the shipped .arz bytes before writing):
#  - ADDITIVE ONLY. Never renumbers/removes an existing tree or UI slot; every
#    graft lands at the next FREE tree slot + a FREE UI grid cell (collision-
#    checked against the live panels). Existing characters keep every point.
#  - Never swaps the RuneMaster/Neidan tree POINTER to SVAERA's _drx copies (that
#    would strand invested points); the Runemaster buffs are field edits on the
#    vanilla-path records only.
#  - Occult (mastery/UI 5) + Hunting (6) are UNTOUCHED (validate_mastery_golden
#    stays green with no re-baseline).
#  - Anim safety: every non-empty skillSpecialAnimationName a grafted skill names
#    already resolves in BOTH PC anim tables (Hew 7 rows, ShieldSkill02 3 incl
#    sHanded, CallOfTheHunt 7, Colossus 8, ThunderClap 8 - verified). Graft #0
#    (build31/build35) already restored the melee rows. Runs BEFORE the player-
#    anim gate so the grafted skills are validated there.
#  - CLOSURE: every .dbr a grafted skill needs that does NOT resolve in the
#    runtime model (mod .arz UNION base game) is imported from the REAL SVAERA
#    arz, recursively, dtype-preserving. Zero _DRX mesh/texture refs across the
#    whole closure (probed) -> no D5 invisible-pet risk; the Doppelganger is a
#    doppelganger.tpl clone of the player mesh (which we ship) and its only _DRX
#    refs are 6 fallback .anm run-fix clips (engine falls back to base cleanly).
#  - TAGS: the 8 base-Atlantis (x3tag*) display tags resolve from the engine's
#    own Text at runtime (no action). The 8 genuinely-new SV-authored tags (Slam/
#    Fissure/Burning Bolts/Frost Nova) are authored into Text.arc via the DATA PATH
#    (uber_soul_tags.txt, read by build_text_arc.py) - no edit to the text pipeline.
#    The Rupture/Flare display tags ALREADY ship in the mod's 0.98i text, so they
#    are NOT re-emitted (would trip the duplicate-tag gate). validate_tags then
#    sees the new tags mod-owned AND defined -> PASS.
# ═══════════════════════════════════════════════════════════════════════════

# SVAERA-internal dangling ref the closure tolerates (absent even in SVAERA - the
# same placeholder our own Volcanic Orb / Flamesurge already carry harmlessly).
# drxrupture's two particleEffectName refs point here; we clear them post-import.
_GRAFT_KNOWN_DANGLING = (
    r'records\sandbox\chris\unarmedprojectile_fx01.dbr',
)

# The 14 player-tree skills. Each becomes a NEW tree slot + a NEW UI button.
# Fields: (svaera_path, tree_path, tree_slot, ui_folder_base, ui_slot,
#          ui_x, ui_y, circular, label). Support records (nymph pet-skill, the
#          Doppelganger pet chain, Frost-Nova FX) ride the recursive closure.
# Tree slots + UI cells were chosen from the LIVE shipped .arz (next free tree
# skillName + a free grid cell in the column with the most room). UI folders are
# NON-STANDARD in this mod (verified via malepc01 skillTreeN + folder slot idents):
#   Warfare->ingameui M1, Defense->M2, Earth->M3, Storm->M4, Nature->M8,
#   Spirit->M7, Dream->xpack M9.
_UI_ING = r'records\ingameui\player skills\mastery %d'
_UI_XP9 = r'records\xpack\ui\skills\mastery 9'
_TREE_WAR = r'records\skills\warfare\drxwarfareskilltree.dbr'
_TREE_DEF = r'records\skills\defensive\drxdefensiveskilltree.dbr'
_TREE_EAR = r'records\skills\earth\drxearthskilltree.dbr'
_TREE_STO = r'records\skills\storm\drxstormskilltree.dbr'
_TREE_NAT = r'records\skills\nature\drxnatureskilltree.dbr'
_TREE_DRE = r'records\xpack\skills\dream\drxdreamskilltree.dbr'

_GRAFT_SKILLS = [
    # --- Warfare (tree drxwarfareskilltree; UI ingameui mastery 1) ---
    (r'records\skills\warfare\drx_clubslam.dbr',          _TREE_WAR, 27, _UI_ING % 1, 26, 328,  31, False, 'Slam'),
    (r'records\skills\warfare\drx_clubslam_fissure.dbr',  _TREE_WAR, 28, _UI_ING % 1, 27, 328, 217, True,  'Fissure'),
    (r'records\skills\warfare\drx_ancestralmod.dbr',      _TREE_WAR, 29, _UI_ING % 1, 28, 328, 341, True,  'Lasting Legacy'),
    # --- Defense (tree drxdefensiveskilltree; UI ingameui mastery 2) ---
    (r'records\skills\defensive\drx_activeblock.dbr',     _TREE_DEF, 26, _UI_ING % 2, 25, 428,  31, False, 'Perfect Block'),
    (r'records\skills\defensive\drx_summonphalanx.dbr',   _TREE_DEF, 27, _UI_ING % 2, 26, 428, 155, False, 'Unyielding Phalanx'),
    # --- Earth (tree drxearthskilltree; UI ingameui mastery 3) ---
    (r'records\skills\earth\drx_firenova.dbr',            _TREE_EAR, 26, _UI_ING % 3, 25, 428,  31, False, 'Fire Nova'),
    (r'records\skills\earth\drxrupture.dbr',              _TREE_EAR, 27, _UI_ING % 3, 26, 428,  93, False, 'Rupture'),
    (r'records\skills\earth\drxrupture_burning.dbr',      _TREE_EAR, 28, _UI_ING % 3, 27, 428, 217, True,  'Burning Bolts'),
    (r'records\skills\earth\drxrupture_flare.dbr',        _TREE_EAR, 29, _UI_ING % 3, 28, 428, 341, True,  'Flare'),
    # --- Storm (tree drxstormskilltree; UI ingameui mastery 4) ---
    (r'records\skills\storm\drx_lightningdash.dbr',       _TREE_STO, 26, _UI_ING % 4, 26, 428,  31, False, 'Lightning Dash'),
    (r'records\skills\storm\drxfrostnova.dbr',            _TREE_STO, 27, _UI_ING % 4, 27, 428, 155, False, 'Frost Nova'),
    # --- Nature (tree drxnatureskilltree; UI ingameui mastery 8) ---
    (r'records\skills\nature\drx_earthbind.dbr',                    _TREE_NAT, 26, _UI_ING % 8, 25, 328,  31, False, 'Earthbind'),
    (r'records\skills\nature\drx_nymph_petmodifier_rootwave.dbr',   _TREE_NAT, 27, _UI_ING % 8, 26, 328, 155, True,  'Sylvan Protection'),
    # --- Dream (tree drxdreamskilltree; UI xpack mastery 9) ---
    (r'records\xpack\skills\dream\drx_summoncopy.dbr',    _TREE_DRE, 26, _UI_XP9,     25, 128,  31, False, 'Dream Image'),
]

# The 8 genuinely-NEW SV-authored display tags (strings ported verbatim from
# SVAERA's Text.arc; fancy quotes normalized to ASCII - house rule: no em dashes).
# Deliberately EXCLUDED (would collide / are already shipped by the mod, so the
# grafted skills' display resolves to the EXISTING definition):
#   - base-Atlantis x3tag* tags (Lasting Legacy/Perfect Block/Unyielding Phalanx/
#     Fire Nova/Lightning Dash/Earthbind/Sylvan Protection/Dream Image) resolve at
#     runtime from the engine's own base-game Text.
#   - tagRuptureNAME/tagRuptureDESC/tagFlareNAME/tagFlareDESC ALREADY exist in the
#     mod's SV 0.98i text (xuniqueequipment.txt). build_text_arc keeps the FIRST
#     definition, so re-adding them either does nothing (Flare/Rupture NAME, Flare
#     DESC = same string) or trips the duplicate-tag gate (0.98i Rupture DESC says
#     "Staff Only" vs SVAERA's "Staff or Bow"). The grafted Earth Rupture/Burning
#     Bolts/Flare skills reference these tags and resolve to the 0.98i definitions.
_GRAFT_TAGS = {
    'tagSlam_NAME': 'Slam',
    'tagSlam_DESC': ('Hit all enemies in a straight line with staggering force. '
                     '{^n}{^y}The length of the line extends with levels. '
                     '{^n}{^y}Melee weapon or Staff required.'),
    'tagSlam_FissureNAME': 'Fissure',
    'tagSlam_FissureDESC': ('Your slam can be cast more frequently, and creates a '
                            'larger and more powerful fissure in the ground, '
                            'disrupting the aim and spellcasting of your enemies. '
                            '^y^n(The width of the line extends with levels. '
                            'Reduced cooldown starts at level 2)'),
    'tagBurningBoltsNAME': 'Burning Bolts',
    'tagBurningBoltsDESC': ('Adds burn damage to staff attacks, and a chance to '
                            'pass through enemies.'),
    'tagSVAERSkillStorm001': 'Frost Nova',
    'tagSVAERSkillStormDescription001': ('Casts an expanding ring of frost that '
                                         'slows and freezes your enemies.'),
}


def _gnorm(s):
    return str(s).replace('/', '\\').lower().strip()


def _gdbr_refs(fields):
    """Every .dbr reference (normalized) held by a decoded fields dict."""
    out = []
    for key, tf in (fields or {}).items():
        for v in tf.values:
            if isinstance(v, str) and v.strip().lower().endswith('.dbr'):
                out.append(_gnorm(v))
    return out


def _graft_store_record(db, store_name, src_fields):
    """Create store_name from src_fields, preserving dtypes exactly (the dtype-
    preservation lesson: never let set_field auto-detect on cloned INT/FLOAT)."""
    template = ''
    for key, tf in src_fields.items():
        if key.split('###')[0] == 'templateName' and tf.values:
            template = str(tf.values[0])
            break
    _ensure_record(db, store_name, template)
    for key, tf in src_fields.items():
        fn = key.split('###')[0]
        vals = list(tf.values) if tf.values else []
        if len(vals) == 1:
            db.set_field(store_name, fn, vals[0], tf.dtype)
        elif len(vals) > 1:
            db.set_field(store_name, fn, vals, tf.dtype)


def _graft_import_closure(db, svaera_db, base_names, roots):
    """Import each root + its recursive .dbr closure from SVAERA into db. A ref is
    imported iff it resolves in NEITHER db NOR the base game (the runtime model);
    otherwise it is a leaf. Existing db records are never overwritten. Refs absent
    even in SVAERA fail loud UNLESS documented in _GRAFT_KNOWN_DANGLING. Records
    are stored under their SVAERA (lowercase-canonical) name. Returns imported."""
    sv_map = {_gnorm(n): n for n in svaera_db.record_names()}
    db_names = {_gnorm(n) for n in db.record_names()}
    dangling = {_gnorm(d) for d in _GRAFT_KNOWN_DANGLING}
    imported, seen = [], set()
    work = list(dict.fromkeys(_gnorm(r) for r in roots))
    while work:
        key = work.pop()
        if key in seen:
            continue
        seen.add(key)
        if key in db_names or key in base_names:
            continue  # resolves at runtime -> leaf, do not import
        sv_name = sv_map.get(key)
        if sv_name is None:
            if key in dangling:
                continue
            raise SystemExit(
                f"build36 graft: closure ref resolves in NO source "
                f"(db/base/SVAERA): {key} - reconcile before shipping")
        src = svaera_db.get_fields(sv_name)
        _graft_store_record(db, sv_name, src)
        db_names.add(_gnorm(sv_name))
        imported.append(sv_name)
        for ref in _gdbr_refs(src):
            if ref not in seen:
                work.append(ref)
    return imported


def _graft_create_ui_slot(db, folder_base, slot_num, skill_ref, x, y, circ, desc):
    """Create a mastery-panel skill button by cloning slot01 of folder_base and
    overriding position/skill/border. Works for BOTH the ingameui and the xpack
    Dream folders (border textures are shared base-game assets). Fail loud if the
    template slot or the destination is unexpected (never overwrite an existing
    slot - that would be removal-adjacent)."""
    nm = {_gnorm(n): n for n in db.record_names()}
    template = nm.get(_gnorm(r'%s\skill01.dbr' % folder_base))
    if not template:
        raise SystemExit(f"build36 graft: UI template slot01 missing in {folder_base}")
    new_path = r'%s\skill%02d.dbr' % (folder_base, slot_num)
    if _gnorm(new_path) in nm:
        raise SystemExit(f"build36 graft: UI slot already exists (refusing to "
                         f"overwrite): {new_path}")
    db.clone_record(template, new_path)
    db.set_field(new_path, 'skillName', skill_ref, DATA_TYPE_STRING)
    db.set_field(new_path, 'bitmapPositionX', x, DATA_TYPE_INT)
    db.set_field(new_path, 'bitmapPositionY', y, DATA_TYPE_INT)
    db.set_field(new_path, 'isCircular', 1 if circ else 0, DATA_TYPE_INT)
    db.set_field(new_path, 'FileDescription', desc, DATA_TYPE_STRING)
    if circ:
        db.set_field(new_path, 'bitmapNameUp', r'InGameUI\SkillButtonBorderRound01.tex', DATA_TYPE_STRING)
        db.set_field(new_path, 'bitmapNameDown', r'InGameUI\SkillButtonBorderRoundDown01.tex', DATA_TYPE_STRING)
        db.set_field(new_path, 'bitmapNameInFocus', r'InGameUI\SkillButtonBorderRoundOver01.tex', DATA_TYPE_STRING)
    else:
        db.set_field(new_path, 'bitmapNameUp', r'InGameUI\SkillButtonBorder01.tex', DATA_TYPE_STRING)
        db.set_field(new_path, 'bitmapNameDown', r'InGameUI\SkillButtonBorderDown01.tex', DATA_TYPE_STRING)
        db.set_field(new_path, 'bitmapNameInFocus', r'InGameUI\SkillButtonBorderOver01.tex', DATA_TYPE_STRING)
    return new_path


def _graft_register_dream_button(db, ui_slot_num):
    """Register the new Dream (xpack mastery 9) skill button into its panectrl's
    tabSkillButtons. fix_mastery_panel_buttons only covers ingameui masteries 1-8;
    the Dream mastery uses the xpack folder + has no xpack3 override, so its single
    panectrl must be appended to directly. Idempotent + fail-loud if absent."""
    pane = r'records\xpack\ui\skills\mastery 9\panectrl.dbr'
    if not db.has_record(pane):
        raise SystemExit(f"build36 graft: Dream panectrl missing: {pane}")
    btns = db.get_field_value(pane, 'tabSkillButtons')
    btns = list(btns) if isinstance(btns, list) else ([btns] if btns else [])
    btn = r'records\xpack\ui\skills\mastery 9\skill%02d.dbr' % ui_slot_num
    if any(_gnorm(b) == _gnorm(btn) for b in btns):
        return 0
    btns.append(btn)
    db.set_field(pane, 'tabSkillButtons', btns, DATA_TYPE_STRING)
    return 1


def graft_svaera_mastery_skills(db: ArzDatabase, base_db, svaera_db):
    """Graft the 18 SVAERA mastery skills onto our tuned trees (additive-only).
    Imports each player-tree skill + its recursive closure from SVAERA, wires a
    new tree slot + a new UI button per player skill, registers the buttons in the
    mastery panels, and returns the 8 genuinely-new SV-authored display tags for
    the Text pipeline (uber_soul_tags.txt). base_db is REQUIRED (closure resolution)."""
    print("\n=== BUILD36 LANE B: SVAERA mastery-skill graft (18 skills) ===")
    if base_db is None:
        raise SystemExit("build36 graft: base game arz REQUIRED (5th build arg) "
                         "for closure resolution")
    base_names = {_gnorm(n) for n in base_db.record_names()}

    # 1) Import every player-skill root + its full recursive closure.
    roots = [g[0] for g in _GRAFT_SKILLS]
    imported = _graft_import_closure(db, svaera_db, base_names, roots)
    print(f"  closure import: {len(imported)} record(s) pulled from SVAERA")

    # sanity: every player-skill root must now exist (fail loud if a root somehow
    # resolved to base and was skipped - would mean a name collision we did not see).
    for r in roots:
        if not db.has_record(r):
            raise SystemExit(f"build36 graft: player-skill root not imported "
                             f"(unexpected base/db collision?): {r}")

    # 2) drxrupture cosmetic fixup: clear the two dangling projectile-FX refs (the
    #    SVAERA placeholder). Equivalent to our existing skills that carry it, but
    #    keeps the freshly-authored record free of any dangling ref.
    rup = r'records\skills\earth\drxrupture.dbr'
    for f in ('particleEffectName2', 'particleEffectName3'):
        cur = db.get_field_value(rup, f)
        if cur:
            db.set_field(rup, f, '', DATA_TYPE_STRING)
    print("  drxrupture: cleared 2 dangling placeholder projectile-FX refs")

    # 3) Wire tree slots + UI buttons (all additive; fail loud on any collision).
    wired = 0
    touched_ing_masteries = set()
    dream_ui_slot = None
    for (svp, tree, tslot, uifolder, uislot, x, y, circ, label) in _GRAFT_SKILLS:
        if not db.has_record(tree):
            raise SystemExit(f"build36 graft: target tree missing: {tree}")
        # tree slot must be FREE (additive law)
        existing = db.get_field_value(tree, f'skillName{tslot}')
        existing = existing[0] if isinstance(existing, list) and existing else existing
        if existing and str(existing).strip():
            raise SystemExit(
                f"build36 graft: tree slot {tree} skillName{tslot} already "
                f"occupied by {existing!r} - the tree changed under the graft; "
                f"reconcile the slot plan before shipping")
        db.set_field(tree, f'skillName{tslot}', svp, DATA_TYPE_STRING)
        _graft_create_ui_slot(db, uifolder, uislot, svp, x, y, circ, label)
        if uifolder.startswith(r'records\ingameui'):
            # recover the mastery number from the folder path tail
            touched_ing_masteries.add(int(uifolder.rsplit(' ', 1)[-1]))
        else:
            dream_ui_slot = uislot
        wired += 1
        print(f"    wired {label}: {tree.rsplit(chr(92),1)[-1]}[skillName{tslot}] "
              f"+ UI {uifolder.rsplit(chr(92),1)[-1]}\\skill{uislot:02d} ({x},{y})")

    # 4) Re-register the ingameui mastery panels (1-8) so the new buttons render.
    #    fix_mastery_panel_buttons rebuilds each panel's contiguous button list +
    #    the xpack/xpack3 overrides from the folder contents; our new slots are
    #    contiguous so they are picked up. (It already ran once earlier; re-running
    #    is idempotent and now includes the grafted slots.)
    print(f"  re-registering ingameui panels for masteries {sorted(touched_ing_masteries)}")
    fix_mastery_panel_buttons(db)

    # 5) Register the Dream button (xpack folder - not covered by the above).
    if dream_ui_slot is not None:
        added = _graft_register_dream_button(db, dream_ui_slot)
        print(f"  Dream panectrl: +{added} button (xpack mastery 9 skill{dream_ui_slot:02d})")

    print(f"  GRAFT COMPLETE: {wired} player-tree skills wired "
          f"({len(imported)} closure records; {len(_GRAFT_TAGS)} SV-authored tags)")
    return dict(_GRAFT_TAGS)


def _apply_runemaster_buffs(db: ArzDatabase, base_db):
    """RUNEMASTER buffs (docs/SVAERA_MASTERY_COMPARISON.md section 5.3, the
    'optional idea-grafts onto our vanilla-path Runemaster records'). Character-
    safe additive EDITS on the vanilla-path skill records (never the tree pointer,
    never SVAERA's _drx copies). Scalar-field edits only (base-precedent shape) so
    no zero-precedent field-shape risk.

    Non-overlap (verified read-only at 88d2b03): wave2 already tunes
    runemaster_mastery (Life 1160/Mana 400) + menhiraltar (Guardian Stones cd/TTL);
    the Rune Golem block (lane A, apply_svc_patches) only REFERENCES menhirwall as
    a prereq and never edits its numbers. These buffs touch DIFFERENT records/fields
    (menhirwall + mines uptime), so nothing is double-applied. base_db REQUIRED (the
    records are base-only -> imported as mod overrides, exactly like wave2)."""
    print("\n=== BUILD36 LANE B: Runemaster buffs (vanilla-path, additive) ===")
    if base_db is None:
        raise SystemExit("build36 Runemaster buffs: base game arz REQUIRED")

    def _scalar(rec, field):
        v = db.get_field_value(rec, field)
        return float(v[0]) if isinstance(v, list) and v else (float(v) if v is not None else None)

    n = 0
    # Menhir Wall (Skill_DefensiveGround): faster + longer-lived wall (uptime).
    mw = r'records\xpack2\skills\runemaster\menhirwall.dbr'
    _import_base_game_record(db, base_db, mw)
    if not db.has_record(mw):
        raise SystemExit(f"build36 Runemaster buffs: {mw} did not import from base")
    cd, ttl = _scalar(mw, 'skillCooldownTime'), _scalar(mw, 'spawnObjectsTimeToLive')
    if cd != 22.0 or ttl != 10.0:
        raise SystemExit(f"build36 Runemaster buffs: menhirwall baseline drifted "
                         f"(cd={cd}, ttl={ttl}; expected 22.0/10.0) - reconcile")
    db.set_field(mw, 'skillCooldownTime', 18.0, DATA_TYPE_FLOAT)
    db.set_field(mw, 'spawnObjectsTimeToLive', 14.0, DATA_TYPE_FLOAT)
    print("  Menhir Wall: cd 22->18, wall TTL 10->14 (+40% uptime)")
    n += 1

    # Mines (Skill_DefensiveProjectileGroundRing): linger longer + slightly faster.
    mn = r'records\xpack2\skills\runemaster\mines.dbr'
    _import_base_game_record(db, base_db, mn)
    if not db.has_record(mn):
        raise SystemExit(f"build36 Runemaster buffs: {mn} did not import from base")
    mcd, mdur = _scalar(mn, 'skillCooldownTime'), _scalar(mn, 'skillActiveDuration')
    if mcd != 9.0 or mdur != 10.0:
        raise SystemExit(f"build36 Runemaster buffs: mines baseline drifted "
                         f"(cd={mcd}, dur={mdur}; expected 9.0/10.0) - reconcile")
    db.set_field(mn, 'skillCooldownTime', 8.0, DATA_TYPE_FLOAT)
    db.set_field(mn, 'skillActiveDuration', 14.0, DATA_TYPE_FLOAT)
    print("  Mines: cd 9->8, active duration 10->14 (mines linger)")
    n += 1

    print(f"  RUNEMASTER buffs applied: {n} vanilla-path record(s)")
    return n


def _fix_storm_panel_icon_overlap(db: ArzDatabase):
    """F7a: de-overlap the Storm mastery-4 panel. Skill06 (Static Charge) and
    Skill25 (Spell Shock) both sit at cell (128,217); move Skill25 to the free
    in-column cell (128,279). Case-insensitive record resolve; cosmetic, so it
    warns (never fails) on drift/absence."""
    ci = {n.replace('/', '\\').lower(): n for n in db.record_names()}
    rec = ci.get(r'records\ingameui\player skills\mastery 4\skill25.dbr')
    if not rec:
        print("  F7a storm panel: Skill25 button not found (skipped)")
        return
    def cur(f):
        v = db.get_field_value(rec, f)
        return v[0] if isinstance(v, list) else v
    px, py = cur('bitmapPositionX'), cur('bitmapPositionY')
    if (px, py) != (128, 217):
        print(f"  F7a storm panel: Skill25 at ({px},{py}) != expected (128,217) "
              f"- layout drifted, skipped (verify manually)")
        return
    db.set_field(rec, 'bitmapPositionY', 279, DATA_TYPE_INT)
    print("  F7a storm panel: Skill25 moved (128,217) -> (128,279) "
          "(was overlapping Skill06 Static Charge)")


def main():
    if len(sys.argv) < 5:
        print("Usage: build_svc_database.py <sv098i.arz> <sv09.arz> <sv041.arz> <output.arz> [base_game.arz]")
        sys.exit(1)

    sv098_path = Path(sys.argv[1])
    sv09_path = Path(sys.argv[2])
    sv041_path = Path(sys.argv[3])
    output_path = Path(sys.argv[4])
    base_path = Path(sys.argv[5]) if len(sys.argv) > 5 else None

    print(f"Loading SV 0.98i: {sv098_path}")
    db = ArzDatabase.from_arz(sv098_path)

    # F6 (build36): capture SV 0.98i soul .dbr paths BEFORE the merge mutates db,
    # so the provenance naming gate (Part E, apply_svc_patches) can whitelist
    # SV-ORIGINAL souls by PATH (the winning verifier correction: a soul whose
    # .dbr is in SV keeps amgoz1's name even if we retagged it - law #2 - and is
    # never forced to a synthesized standard).
    try:
        import apply_svc_patches as _asp_prov
        _asp_prov._SV098I_ALL_PATHS = {
            n.replace('/', '\\').lower() for n in db.record_names()}
        _asp_prov._SV098I_SOUL_PATHS = {
            p for p in _asp_prov._SV098I_ALL_PATHS
            if '\\soul\\' in p and 'equipmentring' in p}
        print(f"  F6 provenance: captured {len(_asp_prov._SV098I_SOUL_PATHS)} "
              f"SV-original soul paths ({len(_asp_prov._SV098I_ALL_PATHS)} total "
              f"SV records) for the naming + mod-authored-summon gates")
    except Exception as _e:  # never block the build on the capture
        print(f"  F6 provenance: SV path capture skipped ({_e})")

    print(f"\nLoading SV 0.9: {sv09_path}")
    db09 = ArzDatabase.from_arz(sv09_path)

    db41 = None
    if sv041_path and str(sv041_path).strip() and Path(sv041_path).exists():
        print(f"\nLoading SV 0.4.1: {sv041_path}")
        db41 = ArzDatabase.from_arz(sv041_path)

    # Import specific base game boss records for soul wiring
    base_db = None
    if base_path and base_path.exists():
        print(f"\nLoading base game: {base_path}")
        base_db = ArzDatabase.from_arz(base_path)
        import_base_game_bosses(db, base_db)

    strip_ui_overrides(db)
    remove_dead_orphan_records(db)   # P3 hygiene: drop the corrupted potionexp_test orphan
    fix_chimera_chest_double_ext(db)  # Q4-3: .dbr.dbr rename (quest retargeted same wave)
    restore_potion_drops(db, db09)
    # F1 Part B: snapshot SV098i's pristine soul-drop pairings BEFORE wiring
    # mutates loot, then wire, then fail loud on any NEW fuzzy cross-wire.
    _sv_soul_drops = _capture_sv_soul_drops(db)
    wire_souls_to_monsters(db)
    _verify_no_fuzzy_cross_wire(db, _sv_soul_drops)
    make_enchantable(db)
    grant_all_inventory_bags(db)
    expand_caravan(db, base_db)
    restore_rest_skill(db)

    legacy_tags = {}
    if db41:
        _, legacy_tags = restore_legacy_skills(db, db41)
    else:
        print("\n=== Patch 11: SKIPPED (SV 0.4.1 not available) ===")

    fix_broken_mastery_skills(db)
    fix_mastery_panel_buttons(db)
    add_dlc_mastery_trees(db)

    # MASTERY WAVE 1 (build31): the six broken-class fixes B1-B6 + hygiene.
    # Needs base_db for the B6 anim-table restoration.
    apply_mastery_wave1_broken_fixes(db, base_db)
    # MASTERY WAVE 1 boosts (Group 2): Defense/Earth/Storm per the audit doc.
    apply_mastery_wave1_boosts(db)
    # MASTERY WAVE 2 (build32, Group D): Warfare/Nature/Spirit/Dream + the two
    # DLC masteries RuneMaster/Neidan per the audit doc S3 Wave 2 + Part III.
    # Needs base_db (still alive here) to import the base-only RuneMaster/Neidan
    # records as mod overrides. Touches NO anim tables / skillSpecialAnimationName
    # (the player-anim gate below still passes) and NO Occult/Hunting records
    # (the golden-freeze gate stays green).
    apply_mastery_wave2_boosts(db, base_db)

    # ── BUILD36 LANE B: graft the 18 SVAERA mastery skills + Runemaster buffs.
    # Runs AFTER all mastery tuning (so it is purely additive on the final trees)
    # and BEFORE the player-anim gate + `del base_db` (both need base_db alive, and
    # the gate must validate the grafted skills). Default ON; SVC_GRAFT_SVAERA=0
    # disables (e.g. a machine without the SVAERA Workshop install). The SVAERA arz
    # is the SOURCE OF TRUTH (the in-repo reference_mods stub is NOT usable); it is
    # resolved via restore_dropped_npcs.find_svaera_arz ($SVC_SVAERA_ARZ or the
    # known Workshop path). graft_tags flows into uber_soul_tags.txt below.
    graft_tags = {}
    _do_graft = os.environ.get('SVC_GRAFT_SVAERA', '1').strip().lower() \
        not in ('0', 'false', 'no', 'off')
    if _do_graft:
        from restore_dropped_npcs import find_svaera_arz
        _graft_svaera_arz = find_svaera_arz()
        if _graft_svaera_arz is None:
            raise SystemExit(
                "build36 graft: the real SVAERA_customquest.arz was not found "
                "(set $SVC_SVAERA_ARZ or install SVAERA Workshop item 2076433374; "
                "the in-repo reference_mods stub is a 2 KB decoy). To build WITHOUT "
                "the graft, set SVC_GRAFT_SVAERA=0.")
        print(f"\nBuild36 graft ON: loading SVAERA source: {_graft_svaera_arz}")
        _graft_svaera_db = ArzDatabase.from_arz(_graft_svaera_arz)
        graft_tags = graft_svaera_mastery_skills(db, base_db, _graft_svaera_db)
        del _graft_svaera_db  # free the ~68 MB source before the rest of the build
        _apply_runemaster_buffs(db, base_db)
    else:
        print("\nBuild36 graft OFF (SVC_GRAFT_SVAERA=0): the 18 SVAERA mastery "
              "skills + Runemaster buffs are NOT applied.")

    # F7a (build36 fix wave): the Storm mastery-4 panel has Skill06 (Static
    # Charge) and Skill25 (Spellbreaker/Spell Shock) both at grid cell (128,217)
    # -> the two icons overlap. Pre-existing bug (lane B curiosity finding).
    # Move Skill25 down to the free in-column cell (128,279). Runs after every
    # panel build (fix_mastery_panel_buttons + the graft) so it wins.
    _fix_storm_panel_icon_overlap(db)

    # ── GROUP E (build32, N5 thrown weapons): both halves need base_db (del'd
    # below), so they run here. (1) faithfully restore the base game's roh
    # (thrown) drops that SV dropped from its defaultloot overrides; (2) author
    # 3 Legendary supra thrown weapons + 3 ItemArtifactFormula recipes wired into
    # the supra tables. thrown_tags is merged into uber_soul_tags.txt below so
    # build_text_arc emits the supra/recipe names (validate_tags gates them).
    from apply_svc_patches import (_restore_thrown_weapon_drops,
                                   _add_supra_thrown_weapons)
    print("\n=== GROUP E: N5 thrown weapons (drop restore + supra) ===")
    _restore_thrown_weapon_drops(db, base_db)
    thrown_tags = _add_supra_thrown_weapons(db, base_db)

    promote_uber_monsters(db)

    create_uber_dungeon_portal(db, base_db)
    create_blood_cave_portal(db, base_db)

    # ── D3 (build30): restore the placed-but-missing SVAERA town NPC records ─────
    # SVAERA's world map PLACES 68 instances (67 distinct records: town dyers, the
    # Great Wall vendor row, a Delphi oceanid proxy) whose .dbr definitions live
    # ONLY in the SVAERA database. restore_dropped_npcs() imports the 65 resolvable
    # records + their full recursive .dbr closure (3169 records) from the SVAERA
    # workshop DB, deterministically, and MAP-REF-1 drops 68 -> 3 on a placing map.
    #
    # DEFAULT OFF (SVC_RESTORE_DROPPED_NPCS unset): the restore is NOT applied.
    # Ground truth (D3 render-risk check, 2026-07-09): 63/65 of these SVAERA NPCs
    # reference art in SVAERA's `_DRX_Meshes`/`_DRX_Textures` arcs and names in
    # `tagNewMerchantName*` tags that our mod does NOT ship, so restoring them makes
    # them LOADABLE but INVISIBLE + RAW-NAMED in-game (worse than absent). The MAP
    # lane already DE-PLACES these instances (MAP-REF-1 -> 0 for them), so the
    # default shippable build leaves them out. Turning the restore ON only helps as
    # part of a future full job that ALSO bundles the SVAERA _DRX art arcs + the
    # merchant name tags (out of DB-lane scope). base_db is REQUIRED when ON (the
    # closure skips refs that already resolve), so it runs BEFORE `del base_db`.
    _restore_npcs = os.environ.get('SVC_RESTORE_DROPPED_NPCS', '').strip().lower() \
        in ('1', 'true', 'yes', 'on')
    if _restore_npcs and base_db is not None:
        from restore_dropped_npcs import restore_dropped_npcs, find_svaera_arz
        _svaera_arz = find_svaera_arz()
        if _svaera_arz is None:
            raise SystemExit(
                "D3: SVC_RESTORE_DROPPED_NPCS=1 but SVAERA_customquest.arz not found "
                "(set $SVC_SVAERA_ARZ or install SVAERA Workshop item 2076433374).")
        print(f"\nD3 restore ON: loading SVAERA source: {_svaera_arz}")
        _svaera_db = ArzDatabase.from_arz(_svaera_arz)
        _closure_dbs = [_svaera_db, db09] + ([db41] if db41 else [])
        restore_dropped_npcs(db, _closure_dbs, base_db=base_db)
        del _svaera_db  # free the ~68 MB source db before the rest of the build
    elif _restore_npcs:
        print("\nD3 restore requested (SVC_RESTORE_DROPPED_NPCS=1) but no base game "
              "arz provided; SKIPPED to avoid over-importing base-resolvable records.")
    else:
        print("\nD3 restore OFF (default; SVC_RESTORE_DROPPED_NPCS unset): dropped "
              "SVAERA town NPCs stay DE-PLACED by the map lane. Restoring them ships "
              "invisible/raw-named without the SVAERA _DRX art arcs + merchant tags.")

    # Snapshot the base-game record names (lowercased) BEFORE freeing the db:
    # the end-of-build container gate resolves loot refs against the runtime
    # model (mod UNION base). Passing the full base_db there is impossible - it
    # is deleted here - and that exact wiring (gate call naming the deleted
    # local) made every full rebuild crash with UnboundLocalError (found on the
    # first real work-layout build after build30.1 wired the gate).
    _base_names_low = {n.replace('/', '\\').lower()
                       for n in base_db.record_names()} if base_db else set()

    # ── MASTERY WAVE 1 gate (fail-loud, 4th DB invariant): every castable
    # mastery-tree skill's skillSpecialAnimationName must be empty or present
    # in the PC anim tables (hard-law #2 / StartSkill abort). Runs while
    # base_db is still alive because the RuneMaster/Neidan trees resolve from
    # the base game. Negative-tested: FAILS on the pre-fix build30.2 arz
    # (Meteor 'MeteorShower' + Thunderball 'Ensnare' + Bonespire 'BoneSpire'),
    # PASSES post-fix. NOTE: no later build stage may touch
    # skillSpecialAnimationName or the anm tables (they run after this gate).
    from validate_player_skill_anims import check_db as _check_player_anims
    print("\n=== Gate: player-skill anim castability (Mastery W1) ===")
    _check_player_anims(db, base_db=base_db, fail=True)

    del base_db  # Free memory

    from create_uber_souls import create_uber_souls
    souls, text_tags = create_uber_souls(db)

    from apply_svc_patches import apply_all_extended_patches
    # ── Soul drop-rate control (RELEASE is the DEFAULT for this repo) ──────────
    # DECISION (2026-07-07, Will, for the public Steam release): the RELEASE build
    # - the tuned 66% (Hero/Quest) / 25% (Boss) soul drop rates - is now the
    # DEFAULT. Building with NO environment override produces a shippable release
    # .arz. The old 100%-everywhere "testing" behavior is now an EXPLICIT opt-in.
    #
    # Two knobs, evaluated with a strict typo-guard (only explicit true/false
    # spellings are honored; anything else WARNS loudly and does NOT silently
    # change the mode - so a typo can never ship the wrong drop rates):
    #   SVC_TESTING_DROPS=1   -> force 100% drops (testing).           [opt-in]
    #   SVC_RELEASE_DROPS=0   -> force 100% drops (testing).  (legacy inverse)
    #   (unset / SVC_RELEASE_DROPS=1) -> tuned 66%/25% RELEASE rates.  [default]
    # SVC_RELEASE_DROPS is kept for backward compatibility with existing scripts
    # and docs; SVC_TESTING_DROPS is the new, clearer way to ask for a test build.
    _TRUE = ('1', 'true', 'yes', 'on')
    _FALSE = ('0', 'false', 'no', 'off')

    def _tri(name):
        """Return True/False for a recognized bool env var, or None if unset.
        Warns (and returns None) on an unrecognized non-empty value."""
        raw = os.environ.get(name)
        if raw is None:
            return None
        v = raw.strip().lower()
        if v == '':
            return None
        if v in _TRUE:
            return True
        if v in _FALSE:
            return False
        print(f"\nWARNING: {name}='{raw}' not recognized (use 1/0); ignoring it.")
        return None

    _testing = _tri('SVC_TESTING_DROPS')            # explicit testing opt-in
    _release = _tri('SVC_RELEASE_DROPS')            # legacy release flag (True=release)

    # Resolve to a single decision. RELEASE is the default; testing must be asked
    # for explicitly via either knob.
    if _testing is True or _release is False:
        force_full_drops = True
        _reason = ("SVC_TESTING_DROPS=1" if _testing is True else "SVC_RELEASE_DROPS=0")
    else:
        force_full_drops = False
        _reason = ("SVC_TESTING_DROPS unset / SVC_RELEASE_DROPS in "
                   "{unset,1}") if (_testing is None and _release in (None, True)) \
            else "default"

    print("\n" + "=" * 70)
    if force_full_drops:
        print("*** TESTING BUILD: soul drops FORCED to 100% "
              f"({_reason}) ***")
        print("*** For the RELEASE .arz (tuned 66%/25%), build with NO override "
              "(or SVC_RELEASE_DROPS=1). ***")
    else:
        print("*** RELEASE BUILD (repo default): tuned soul drop rates kept "
              "(66% Hero/Quest, 25% Boss). ***")
        print("*** For a 100% test build, set SVC_TESTING_DROPS=1. ***")
    print("=" * 70)
    # ── patches-registry (build37) hook ───────────────────────────────────────
    # Run the monolith's content, THEN the ordered patches-registry content
    # modules over the SAME db/tags, THEN the monolith's whole gate battery -
    # so every gate validates the FINAL assembled db (monolith + every module)
    # and nothing a module does escapes the gates. With an EMPTY REGISTRY this
    # is byte-identical to the pre-registry build (tools/patches/README.md S5).
    extended_tags = apply_all_extended_patches(
        db, force_full_drops=force_full_drops, _defer_gates=True)
    from patches import run_registry
    run_registry(db, extended_tags)
    from apply_svc_patches import run_registry_gates
    run_registry_gates(db, extended_tags, force_full_drops=force_full_drops)

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
        for tag, value in thrown_tags.items():   # GROUP E (N5 supra thrown weapons)
            f.write(f"{tag}={value}\n")
        for tag, value in graft_tags.items():     # BUILD36 LANE B (SVAERA mastery graft)
            f.write(f"{tag}={value}\n")
    print(f"  Tags file: {tags_path} ({len(text_tags)} uber + {len(legacy_tags)} legacy + {len(extended_tags)} extended + {len(thrown_tags)} thrown + {len(graft_tags)} graft)")

    fix_soul_bitmaps(db)

    # ── P0/build30.1 gate (fail-loud): container loot-slot SHAPE contract.
    # Every mod-MODIFIED FixedItemLoot record must have base-precedent slot
    # shapes: an ACTIVE slot (lootNChance > 0) must carry a non-empty lootNName1
    # AND a positive weight; a DORMANT slot (chance == 0) must carry NO name
    # (the base game's own unused-slot shape: chance 0 + zero weights + name
    # absent). Also: numSpawnMin/MaxEquation must be non-empty. Born from the
    # build30 starter-chest P0 (the record proved byte-clean, but this contract
    # makes the whole malformed-slot class unshippable). Negative-tested via
    # tools/debug/negtest_container_shape.py.
    _validate_container_loot_shapes(db, base_names=_base_names_low)

    print(f"\nWriting output...")
    db.write_arz(output_path)

    # ── B-SUMMON-1 gate (fail-loud): validate every soul-granted summon chain
    # on the WRITTEN artifact (mesh present, proven rig pairing, resolving
    # equipment with no never-equips player uniques, live controller/skills).
    # Runs against the runtime resolution model (mod UNION base game) with
    # SV-upstream leniency; a broken mod-authored summon can never ship.
    del db, db09, db41  # free memory before the validator reloads from disk
    from validate_summon_pets import validate as _validate_summon_pets
    _rc = _validate_summon_pets(
        output_path,
        str(base_path) if base_path and base_path.exists() else None,
        str(sv098_path))
    if _rc != 0:
        raise SystemExit(
            "Summon-pet validation FAILED on the written .arz (see offenders "
            "above); this build does not ship (B-SUMMON-1 gate)")

    # ── A9 render-chain contract (fail-loud): every soul-granted summon pet's
    # mesh/texture/status icons + the summon skill's bar icons must resolve in
    # the shipped art arcs (mod Resources + game Resources[/XPack*]), or the
    # pet spawns INVISIBLE. Mod-authored pets FAIL the build; upstream = WARN.
    from validate_render_chain import validate as _validate_render
    _mod_resources = output_path.resolve().parent.parent / 'Resources'
    _game_dir = Path(base_path).resolve().parent.parent if base_path else None
    if _game_dir and _game_dir.is_dir() and _mod_resources.is_dir():
        if _validate_render(str(output_path), str(_mod_resources), str(_game_dir)) != 0:
            raise SystemExit(
                "Summon-pet render-chain validation FAILED on the written .arz; "
                "this build does not ship (A9 gate)")
    else:
        # Without BOTH the game dir and the mod's staged Resources beside the
        # output (the standard work/ layout), mod-side art cannot be resolved
        # and every mod ref would false-FAIL (seen on isolated determinism
        # rebuilds writing to a scratch dir). Skip loudly instead.
        print(f"  WARNING: A9 render-chain gate SKIPPED - needs the game dir "
              f"AND a Resources dir beside the output "
              f"(game={_game_dir}, mod_resources={_mod_resources})")

    # ── A7 golden freeze guard (fail-loud): the owner's hand-tuned Occult (UI
    # slot 5) + Hunting (UI slot 6) state must match tools/occult_hunting_golden
    # .json exactly (records/tree/UI bindings; Text tags are re-checked with the
    # full artifact pair by build_text_arc.py). Any drift needs Will's sign-off
    # via the golden's owner_approved_overrides. Missing golden = FAIL (a build
    # must never silently run unguarded); bootstrap it once with --generate.
    from validate_mastery_golden import validate as _validate_golden
    if _validate_golden(str(output_path), None) != 0:
        raise SystemExit(
            "Occult/Hunting golden freeze guard FAILED on the written .arz; "
            "this build does not ship (A7 gate)")

    # ── F2 contract gate (build30, post-vet): the summons contract lane
    # (SUMMON-PET-NAKED et al) must PASS on the written .arz, so a green build
    # is contract-clean by construction (the vet proved the validators above
    # miss the naked-pet class). Same skip rule as A9: needs the game dir AND
    # the staged Resources beside the output (scratch/determinism builds skip
    # loudly - the work/-layout build is the gate of record).
    import subprocess as _sp
    _contracts = Path(__file__).resolve().parent / 'contracts' / 'run_contracts.py'
    if _game_dir and _game_dir.is_dir() and _mod_resources.is_dir() \
            and _contracts.is_file():
        _rc = _sp.call([sys.executable, str(_contracts), '--only', 'summons',
                        '--arz', str(output_path),
                        '--base-game-dir', str(_game_dir),
                        '--resource-arc-dir', str(_mod_resources)])
        if _rc != 0:
            raise SystemExit(
                f"Summons contract lane FAILED on the written .arz (exit {_rc}); "
                f"this build does not ship (F2 gate)")
    else:
        print(f"  WARNING: F2 summons-contract gate SKIPPED - needs the game dir, "
              f"a Resources dir beside the output, and tools/contracts "
              f"(game={_game_dir}, mod_resources={_mod_resources})")
    print("Done.")


def _pin_hashseed():
    """Reproducible builds: pin PYTHONHASHSEED=0 so hash-based ordering is stable.

    Python randomizes str/bytes hashing per process by default, which makes the
    iteration order of any set (and therefore the order strings are first seeded
    into the .arz string table, which feeds every record's encoded string IDs)
    vary run to run. That produced the build29 non-reproducibility (two distinct
    .arz MD5s from one tree). PYTHONHASHSEED must be fixed BEFORE interpreter
    startup to take effect, so when we were launched without it pinned we re-exec
    ourselves once with it set to 0. Deterministic regardless of how invoked.
    """
    if os.environ.get('PYTHONHASHSEED') != '0':
        os.environ['PYTHONHASHSEED'] = '0'
        import subprocess
        sys.exit(subprocess.call([sys.executable, *sys.argv]))


if __name__ == '__main__':
    _pin_hashseed()
    main()
