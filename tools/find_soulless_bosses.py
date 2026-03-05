"""
Thorough audit of ALL Boss-classified monsters: which have souls, which don't.

Checks:
  1. Every record with monsterClassification = 'Boss'
  2. Equipment finger slots (chanceToEquipFinger1/2) for soul ring wiring
  3. Loot finger slots (lootFinger1Item*/lootFinger2Item*) for soul references
  4. Whether a matching soul record exists in the database
  5. Resolves description tags to human-readable names via text files
  6. Special attention to flagged bosses (Cold Worm, Hades variants, etc.)

Usage:
    py tools/find_soulless_bosses.py
"""
import sys
import os
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from arz_patcher import ArzDatabase


# ---------------------------------------------------------------------------
# Tag resolution
# ---------------------------------------------------------------------------

def load_tags(text_dir: Path) -> dict[str, str]:
    """Load all tag=value pairs from text files (UTF-16-LE with BOM)."""
    tags = {}
    for txt_file in sorted(text_dir.glob('*.txt')):
        try:
            with open(txt_file, 'r', encoding='utf-16-le') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('//'):
                        continue
                    if '=' in line:
                        tag, _, value = line.partition('=')
                        tag = tag.strip()
                        value = value.strip()
                        if tag and value:
                            tags[tag] = value
        except Exception:
            pass
    return tags


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------

def fv(fields, name):
    """Get first field value or None."""
    if fields is None:
        return None
    if name in fields:
        v = fields[name].values
        return v[0] if len(v) == 1 else v
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            v = tf.values
            return v[0] if len(v) == 1 else v
    return None


def fvl(fields, name):
    """Get field value as list."""
    if fields is None:
        return []
    if name in fields:
        return fields[name].values
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            return tf.values
    return []


def all_field_values(fields, prefix):
    """Get all field values whose key starts with prefix."""
    results = {}
    if fields is None:
        return results
    for key, tf in fields.items():
        rk = key.split('###')[0]
        if rk.startswith(prefix) and tf.values:
            results[rk] = tf.values
    return results


def resolve_tag(tag, tags_db):
    """Resolve a tag to its display name, or return the tag itself."""
    if not tag or not isinstance(tag, str):
        return str(tag) if tag else '(none)'
    resolved = tags_db.get(tag, None)
    if resolved:
        return resolved
    # Try without leading/trailing whitespace
    resolved = tags_db.get(tag.strip(), None)
    if resolved:
        return resolved
    return tag


# ---------------------------------------------------------------------------
# Soul detection
# ---------------------------------------------------------------------------

def is_soul_path(path_str):
    """Check if a path string looks like a soul record."""
    if not path_str or not isinstance(path_str, str):
        return False
    pl = path_str.lower().replace('/', '\\')
    return ('soul' in pl and 'equipmentring' in pl and pl.endswith('.dbr'))


def extract_soul_refs_from_fields(fields):
    """Extract all soul references from a monster's loot/equip finger fields."""
    soul_refs = []

    # Check lootFinger*Item* fields (lootFinger1Item1..6, lootFinger2Item1..6)
    for slot in ['1', '2']:
        for item_idx in range(1, 7):
            field_name = f'lootFinger{slot}Item{item_idx}'
            vals = fvl(fields, field_name)
            for v in vals:
                if is_soul_path(v):
                    soul_refs.append(('loot', slot, item_idx, str(v)))

    # Check equipFinger*Item* fields (equipFinger1Item1..6, equipFinger2Item1..6)
    for slot in ['1', '2']:
        for item_idx in range(1, 7):
            field_name = f'equipFinger{slot}Item{item_idx}'
            vals = fvl(fields, field_name)
            for v in vals:
                if is_soul_path(v):
                    soul_refs.append(('equip', slot, item_idx, str(v)))

    # Also scan for any field containing a soul path (catch-all)
    for key, tf in fields.items():
        rk = key.split('###')[0]
        # Skip already-checked fields
        if rk.startswith('lootFinger') or rk.startswith('equipFinger'):
            continue
        for v in tf.values:
            if is_soul_path(v):
                soul_refs.append(('other', rk, 0, str(v)))

    return soul_refs


def get_equip_chances(fields):
    """Get equipment chances for finger slots."""
    chances = {}
    for slot in ['1', '2']:
        chance = fv(fields, f'chanceToEquipFinger{slot}')
        if chance is not None:
            chances[f'finger{slot}'] = float(chance)
    return chances


# ---------------------------------------------------------------------------
# Soul catalog builder
# ---------------------------------------------------------------------------

def build_soul_catalog(db):
    """Build a catalog of all soul records in the database.
    Returns dict: normalized_name -> list of soul record paths
    """
    catalog = {}  # full_path -> True
    by_name = defaultdict(list)  # monster_name_part -> [paths]

    for name in db.record_names():
        nl = name.lower().replace('/', '\\')
        if 'soul' in nl and 'equipmentring' in nl and nl.endswith('.dbr'):
            catalog[name] = True
            # Extract monster name portion
            parts = nl.split('\\')
            filename = parts[-1].replace('.dbr', '')
            # Strip _soul_n, _soul_e, _soul_l suffixes
            base = re.sub(r'_soul_[nel]$', '', filename)
            base = re.sub(r'_soul$', '', base)
            by_name[base].append(name)

            # Also index by parent folder name
            if len(parts) >= 2:
                parent = parts[-2]
                by_name[parent].append(name)

    return catalog, by_name


def find_matching_souls(monster_record, monster_name, soul_by_name, soul_catalog):
    """Try to find soul records that match a monster by name patterns."""
    matches = []

    # Extract the monster filename without extension
    parts = monster_record.lower().replace('/', '\\').split('\\')
    filename = parts[-1].replace('.dbr', '')

    # Strip common prefixes
    clean = re.sub(r'^(u_|um_|uw_|qm_|bm_|cb_|am_|ar_|as_|em_|vampiric_|boss_)', '', filename)
    # Strip numeric suffixes (level variants like _38, _01)
    clean = re.sub(r'_\d+$', '', clean)
    clean = clean.strip('_')

    # Try exact match
    if clean in soul_by_name:
        matches.extend(soul_by_name[clean])

    # Try with the parent folder name
    if len(parts) >= 2:
        parent = parts[-2]
        if parent in soul_by_name:
            matches.extend(soul_by_name[parent])

    # Try partial matches
    for soul_key in soul_by_name:
        if soul_key in clean or clean in soul_key:
            if soul_key not in [clean, parts[-2] if len(parts) >= 2 else '']:
                matches.extend(soul_by_name[soul_key])

    # Deduplicate
    seen = set()
    unique = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            unique.append(m)

    return unique


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    repo_root = Path(__file__).parent.parent
    db_path = repo_root / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'
    text_dir = repo_root / 'local' / 'tmp_text_build' / 'text'
    output_path = repo_root / 'work' / 'soulless_bosses_output.txt'

    print(f'Loading database: {db_path}')
    db = ArzDatabase.from_arz(db_path)

    print(f'Loading text tags from: {text_dir}')
    tags = load_tags(text_dir)
    print(f'  Loaded {len(tags)} tags')

    print(f'Building soul catalog...')
    soul_catalog, soul_by_name = build_soul_catalog(db)
    print(f'  Found {len(soul_catalog)} soul records')
    print(f'  Indexed {len(soul_by_name)} unique name keys')

    # -------------------------------------------------------------------
    # Find ALL Boss-classified monsters
    # -------------------------------------------------------------------
    print(f'\nScanning for Boss-classified monsters...')

    all_bosses = []
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue

        mc = fv(fields, 'monsterClassification')
        if mc != 'Boss':
            continue

        # Skip obvious junk
        nl = name.lower()
        if any(skip in nl for skip in ['backup_', 'copy of ', 'conflicted copy']):
            continue

        desc_tag = fv(fields, 'description') or ''
        race = fv(fields, 'characterRacialProfile') or ''
        levels = fvl(fields, 'charLevel')
        file_desc = fv(fields, 'FileDescription') or ''

        # Resolve name
        display_name = resolve_tag(desc_tag, tags) if desc_tag else file_desc or '(unnamed)'

        # Get soul references
        soul_refs = extract_soul_refs_from_fields(fields)
        equip_chances = get_equip_chances(fields)

        # Find matching souls in catalog
        catalog_matches = find_matching_souls(name, display_name, soul_by_name, soul_catalog)

        all_bosses.append({
            'record': name,
            'desc_tag': desc_tag,
            'display_name': display_name,
            'race': race,
            'levels': levels,
            'file_desc': file_desc,
            'soul_refs': soul_refs,
            'equip_chances': equip_chances,
            'catalog_matches': catalog_matches,
            'has_soul_drop': len(soul_refs) > 0,
        })

    print(f'  Found {len(all_bosses)} Boss-classified records')

    # -------------------------------------------------------------------
    # Build output
    # -------------------------------------------------------------------
    lines = []

    def out(s=''):
        lines.append(s)

    out('=' * 120)
    out('SOULVIZIER CLASSIC - BOSS SOUL AUDIT (COMPREHENSIVE)')
    out('=' * 120)
    out(f'Database: {db_path}')
    out(f'Total Boss records found: {len(all_bosses)}')
    out(f'Total soul records in DB: {len(soul_catalog)}')
    out()

    # Sort by display name
    all_bosses.sort(key=lambda b: (b['display_name'].lower(), b['record'].lower()))

    # -------------------------------------------------------------------
    # Section 1: ALL bosses grouped by soul status
    # -------------------------------------------------------------------
    with_souls = [b for b in all_bosses if b['has_soul_drop']]
    without_souls = [b for b in all_bosses if not b['has_soul_drop']]

    out('=' * 120)
    out(f'SECTION 1: BOSSES WITH SOUL DROPS ({len(with_souls)} records)')
    out('=' * 120)
    out()

    for i, b in enumerate(with_souls, 1):
        lvl_str = ', '.join(str(int(l)) for l in b['levels']) if b['levels'] else '?'
        out(f'  {i:3d}. {b["display_name"]}')
        out(f'       Tag: {b["desc_tag"]}  |  Race: {b["race"]}  |  Levels: {lvl_str}')
        out(f'       Record: {b["record"]}')
        out(f'       Equip chances: {b["equip_chances"]}')
        for ref_type, slot, idx, path in b['soul_refs']:
            out(f'       Soul ({ref_type} finger{slot} item{idx}): {path}')
        out()

    out()
    out('=' * 120)
    out(f'SECTION 2: BOSSES WITHOUT SOUL DROPS ({len(without_souls)} records)')
    out('=' * 120)
    out()

    for i, b in enumerate(without_souls, 1):
        lvl_str = ', '.join(str(int(l)) for l in b['levels']) if b['levels'] else '?'
        out(f'  {i:3d}. {b["display_name"]}')
        out(f'       Tag: {b["desc_tag"]}  |  Race: {b["race"]}  |  Levels: {lvl_str}')
        out(f'       Record: {b["record"]}')
        out(f'       Equip chances: {b["equip_chances"]}')
        if b['catalog_matches']:
            out(f'       ** SOUL RECORDS EXIST BUT NOT WIRED:')
            for sp in b['catalog_matches']:
                out(f'          -> {sp}')
        else:
            out(f'       No matching soul records found in DB')
        out()

    # -------------------------------------------------------------------
    # Section 3: Summary by unique boss name
    # -------------------------------------------------------------------
    out()
    out('=' * 120)
    out('SECTION 3: SUMMARY BY UNIQUE BOSS (grouped by display name)')
    out('=' * 120)
    out()

    boss_groups = defaultdict(list)
    for b in all_bosses:
        boss_groups[b['display_name']].append(b)

    for name in sorted(boss_groups.keys(), key=str.lower):
        variants = boss_groups[name]
        has_any_soul = any(v['has_soul_drop'] for v in variants)
        all_have_souls = all(v['has_soul_drop'] for v in variants)

        total_variants = len(variants)
        with_count = sum(1 for v in variants if v['has_soul_drop'])
        without_count = total_variants - with_count

        if all_have_souls:
            status = 'ALL WIRED'
        elif has_any_soul:
            status = f'PARTIAL ({with_count}/{total_variants} wired, {without_count} MISSING)'
        else:
            status = 'NO SOULS'

        # Collect all races
        races = set(v['race'] for v in variants if v['race'])
        race_str = ', '.join(sorted(races)) if races else '(none)'

        # Collect all levels
        all_levels = set()
        for v in variants:
            all_levels.update(int(l) for l in v['levels'])
        level_range = f'{min(all_levels)}-{max(all_levels)}' if all_levels else '?'

        out(f'  {name:55s} | {status:30s} | Race: {race_str:25s} | Levels: {level_range:10s} | Variants: {total_variants}')

        # Show individual variants if partially wired
        if has_any_soul and not all_have_souls:
            for v in variants:
                soul_status = 'HAS SOUL' if v['has_soul_drop'] else '** NO SOUL **'
                vl = ', '.join(str(int(l)) for l in v['levels']) if v['levels'] else '?'
                out(f'      -> [{soul_status:13s}] Lvl {vl:10s}  {v["record"]}')

    # -------------------------------------------------------------------
    # Section 4: Flagged boss deep-dive
    # -------------------------------------------------------------------
    out()
    out('=' * 120)
    out('SECTION 4: DEEP DIVE ON FLAGGED BOSSES')
    out('=' * 120)

    flagged_searches = [
        ('Cold Worm', ['cold_worm', 'coldworm', 'cold worm'], ['insectoid']),
        ('Blood Witch Leinth', ['blood_witch', 'bloodwitch', 'leinth'], ['olympian']),
        ('Dagon', ['dagon'], ['olympian']),
        ('Hades', ['hades'], ['olympian']),
        ('Murder Bunny', ['murder_bunny', 'murderbunny', 'murder bunny'], ['olympian']),
        ('Uber Naiad', ['uber_naiad', 'ubernaiad', 'naiad'], []),
        ('Ink-Eyes', ['ink-eyes', 'ink_eyes', 'inkeyes'], []),
        ('Grimshell', ['grimshell'], []),
        ('Palai / Sepulchral Wyrm', ['palai', 'sepulchral', 'wyrm'], []),
        ('Blood Crow', ['blood_crow', 'bloodcrow', 'blood crow'], []),
    ]

    for search_label, search_terms, race_hints in flagged_searches:
        out()
        out(f'  --- {search_label} ---')
        out()

        # Find all matching boss records
        matched = []
        for b in all_bosses:
            rec_lower = b['record'].lower().replace('/', '\\')
            name_lower = b['display_name'].lower()
            tag_lower = b['desc_tag'].lower()
            desc_lower = b['file_desc'].lower()

            for term in search_terms:
                if (term in rec_lower or term in name_lower or
                    term in tag_lower or term in desc_lower):
                    if b not in matched:
                        matched.append(b)
                    break

        if not matched:
            out(f'    ** NO BOSS RECORDS FOUND matching: {search_terms}')
            # Try broader search across ALL records
            out(f'    Searching all records (not just Boss class)...')
            broader = []
            for name in db.record_names():
                nl = name.lower()
                for term in search_terms:
                    if term in nl:
                        broader.append(name)
                        break
            if broader:
                out(f'    Found {len(broader)} records containing search terms:')
                for rn in broader[:20]:
                    fields = db.get_fields(rn)
                    mc = fv(fields, 'monsterClassification') if fields else '(no fields)'
                    desc = fv(fields, 'description') if fields else ''
                    out(f'      {rn}  [class={mc}]  [desc={desc}]')
                if len(broader) > 20:
                    out(f'      ... and {len(broader) - 20} more')
            else:
                out(f'    No records found at all with terms: {search_terms}')
            out()
            continue

        out(f'    Found {len(matched)} matching Boss record(s):')
        out()

        for b in matched:
            lvl_str = ', '.join(str(int(l)) for l in b['levels']) if b['levels'] else '?'
            soul_status = 'HAS SOUL DROP' if b['has_soul_drop'] else '** NO SOUL DROP **'

            out(f'    [{soul_status}]')
            out(f'      Name: {b["display_name"]}')
            out(f'      Tag:  {b["desc_tag"]}')
            out(f'      Race: {b["race"]}')
            out(f'      Levels: {lvl_str}')
            out(f'      Record: {b["record"]}')
            out(f'      FileDesc: {b["file_desc"]}')
            out(f'      Equip chances: {b["equip_chances"]}')

            if b['soul_refs']:
                out(f'      Soul drops:')
                for ref_type, slot, idx, path in b['soul_refs']:
                    # Check if the soul record actually exists
                    exists = db.has_record(path)
                    out(f'        ({ref_type} finger{slot} item{idx}): {path}  [exists={exists}]')
            else:
                out(f'      Soul drops: NONE')

            if b['catalog_matches']:
                out(f'      Catalog soul matches (exist but not wired):')
                for sp in b['catalog_matches']:
                    out(f'        -> {sp}')

            # Dump all finger-related fields for debugging
            fields = db.get_fields(b['record'])
            if fields:
                finger_fields = {}
                for key, tf in fields.items():
                    rk = key.split('###')[0]
                    if 'finger' in rk.lower() and tf.values:
                        # Only show non-trivial values
                        non_trivial = any(
                            v is not None and str(v).strip() and
                            str(v) != '0' and str(v) != '0.0'
                            for v in tf.values
                        )
                        if non_trivial:
                            finger_fields[rk] = tf.values
                if finger_fields:
                    out(f'      Non-trivial finger fields:')
                    for fk in sorted(finger_fields.keys()):
                        vals = finger_fields[fk]
                        out(f'        {fk} = {vals}')

            out()

    # -------------------------------------------------------------------
    # Section 5: HADES special deep-dive (ALL variants)
    # -------------------------------------------------------------------
    out()
    out('=' * 120)
    out('SECTION 5: HADES - ALL VARIANTS (COMPREHENSIVE)')
    out('=' * 120)
    out()

    hades_records = []
    for name in db.record_names():
        nl = name.lower()
        if 'hades' in nl and '\\creature' in nl.replace('/', '\\'):
            fields = db.get_fields(name)
            if not fields:
                continue
            mc = fv(fields, 'monsterClassification')
            desc = fv(fields, 'description') or ''
            race = fv(fields, 'characterRacialProfile') or ''
            levels = fvl(fields, 'charLevel')
            file_desc = fv(fields, 'FileDescription') or ''
            display = resolve_tag(desc, tags) if desc else file_desc or '(unnamed)'

            soul_refs = extract_soul_refs_from_fields(fields)
            equip_chances = get_equip_chances(fields)

            hades_records.append({
                'record': name,
                'mc': mc or '(none)',
                'display_name': display,
                'desc_tag': desc,
                'race': race,
                'levels': levels,
                'file_desc': file_desc,
                'soul_refs': soul_refs,
                'equip_chances': equip_chances,
                'has_soul_drop': len(soul_refs) > 0,
            })

    hades_records.sort(key=lambda h: (h['mc'] or '', h['record']))

    out(f'  Total Hades creature records found: {len(hades_records)}')
    out()

    # Group by classification
    hades_by_class = defaultdict(list)
    for h in hades_records:
        hades_by_class[h['mc']].append(h)

    for mc_val in sorted(hades_by_class.keys()):
        group = hades_by_class[mc_val]
        out(f'  --- Classification: {mc_val} ({len(group)} records) ---')
        out()

        for h in group:
            lvl_str = ', '.join(str(int(l)) for l in h['levels']) if h['levels'] else '?'
            status = 'HAS SOUL' if h['has_soul_drop'] else '** NO SOUL **'

            out(f'    [{status:12s}] {h["display_name"]:40s} Lvl: {lvl_str:10s} Race: {h["race"]}')
            out(f'                 Record: {h["record"]}')
            out(f'                 Tag: {h["desc_tag"]}  FileDesc: {h["file_desc"]}')
            out(f'                 Equip chances: {h["equip_chances"]}')

            if h['soul_refs']:
                for ref_type, slot, idx, path in h['soul_refs']:
                    out(f'                 Soul: ({ref_type} finger{slot} item{idx}) {path}')
            out()

    # Also search for Hades soul records in the DB
    out(f'  --- Hades Soul Records in Database ---')
    out()
    hades_souls = []
    for name in db.record_names():
        nl = name.lower()
        if 'hades' in nl and 'soul' in nl and 'equipmentring' in nl:
            hades_souls.append(name)
    hades_souls.sort()
    out(f'  Found {len(hades_souls)} Hades soul records:')
    for sp in hades_souls:
        out(f'    {sp}')

    # -------------------------------------------------------------------
    # Section 6: Soul records that exist but NO boss drops them
    # -------------------------------------------------------------------
    out()
    out('=' * 120)
    out('SECTION 6: ORPHANED SOULS (soul record exists, no Boss drops it)')
    out('=' * 120)
    out()

    # Collect all soul paths that ARE referenced by any boss
    referenced_souls = set()
    for b in all_bosses:
        for _, _, _, path in b['soul_refs']:
            referenced_souls.add(path.lower().replace('/', '\\'))

    orphaned = []
    for soul_path in sorted(soul_catalog.keys()):
        sp_lower = soul_path.lower().replace('/', '\\')
        if sp_lower not in referenced_souls:
            # Check if ANY creature references it (not just bosses)
            is_referenced = False
            orphaned.append(soul_path)

    out(f'  Total soul records in DB: {len(soul_catalog)}')
    out(f'  Referenced by a Boss: {len(referenced_souls)}')
    out(f'  Not referenced by any Boss: {len(orphaned)}')
    out()

    # Show the orphaned ones (but this could be huge, so filter to interesting ones)
    # Show only souls that look like they should belong to a boss
    boss_soul_keywords = ['boss', 'quest', 'typhon', 'hydra', 'cerberus', 'cyclops',
                          'minotaur', 'medusa', 'talos', 'dragon', 'wyrm', 'liche',
                          'hades', 'polyphemus', 'megalesios', 'telkine', 'fafnir',
                          'nessus', 'chimera', 'manticore', 'scarabaeus', 'ammit',
                          'actaeon', 'tigerman', 'yaoguai', 'bloodwitch', 'leinth',
                          'dagon', 'bunny', 'naiad', 'ink', 'grimshell', 'palai',
                          'crow', 'worm']
    interesting_orphans = []
    for sp in orphaned:
        sp_lower = sp.lower()
        if any(kw in sp_lower for kw in boss_soul_keywords):
            interesting_orphans.append(sp)

    if interesting_orphans:
        out(f'  Interesting orphaned souls (boss-related keywords):')
        for sp in interesting_orphans:
            out(f'    {sp}')
        out()

    # -------------------------------------------------------------------
    # Section 7: Final summary table
    # -------------------------------------------------------------------
    out()
    out('=' * 120)
    out('SECTION 7: FINAL SUMMARY')
    out('=' * 120)
    out()

    total = len(all_bosses)
    with_count = len(with_souls)
    without_count = len(without_souls)

    out(f'  Total Boss records:          {total}')
    out(f'  With soul drops:             {with_count} ({100*with_count/total:.1f}%)')
    out(f'  Without soul drops:          {without_count} ({100*without_count/total:.1f}%)')
    out()

    unique_names = set(b['display_name'] for b in all_bosses)
    unique_with = set(b['display_name'] for b in with_souls)
    unique_without = set(b['display_name'] for b in without_souls)
    unique_partial = unique_with & unique_without

    out(f'  Unique boss names:           {len(unique_names)}')
    out(f'  Unique names with souls:     {len(unique_with)}')
    out(f'  Unique names without souls:  {len(unique_without - unique_with)}')
    out(f'  Partially wired (some variants have, some dont): {len(unique_partial)}')
    out()

    if unique_partial:
        out(f'  Partially wired bosses:')
        for name in sorted(unique_partial):
            variants = boss_groups[name]
            with_c = sum(1 for v in variants if v['has_soul_drop'])
            total_c = len(variants)
            out(f'    {name}: {with_c}/{total_c} variants have soul drops')
        out()

    out(f'  Bosses with NO soul drop at all (unique names):')
    pure_without = unique_without - unique_with
    for name in sorted(pure_without):
        variants = boss_groups[name]
        races = set(v['race'] for v in variants if v['race'])
        race_str = ', '.join(sorted(races)) if races else '(none)'
        all_levels = set()
        for v in variants:
            all_levels.update(int(l) for l in v['levels'])
        level_range = f'{min(all_levels)}-{max(all_levels)}' if all_levels else '?'
        has_catalog = any(v['catalog_matches'] for v in variants)
        catalog_note = ' [SOUL RECORDS EXIST IN DB]' if has_catalog else ''
        out(f'    {name:50s} Race: {race_str:25s} Levels: {level_range}{catalog_note}')

    # -------------------------------------------------------------------
    # Write output
    # -------------------------------------------------------------------
    output_text = '\n'.join(lines)

    # Print to stdout
    print('\n' + output_text)

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output_text)

    print(f'\n\nOutput written to: {output_path}')


if __name__ == '__main__':
    main()
