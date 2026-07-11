"""
Build Resources/Text.arc for AE Custom Quest deployment.

AE Custom Quest mods load text from Resources/Text.arc containing a single
modstrings.txt file. The game loads base game text first, then overlays mod
text. We only need mod-specific tags in modstrings.txt.

Pipeline:
1. Extract all text from SV 0.98i's Text_EN.arc
2. Consolidate into modstrings.txt (deduplicating tag definitions)
3. Apply Occult mastery label fix
4. Append uber soul tags
5. Pack into Text.arc
"""
import os
import sys
from pathlib import Path
from collections import OrderedDict

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive


# Occult mastery fixes (label + missing skill descriptions) authored directly
# into modstrings.txt by this build. Module-level so the mod-tag manifest writer
# can enumerate these as mod-owned tags. The .arz references two of them
# (tagSkillName050 = mastery title, tagNewSkill321DESC = a skill description);
# the two tagMastery* are the mastery-panel labels and tagMasteryDescription05
# is the mastery SELECT-screen blurb.
#
# B-MASTERY-LABEL-1: the ENGINE KEEPS THE FIRST DEFINITION of a duplicated tag
# (byte-proven: with SV's "Rogue Mastery" lines emitted first and this block
# appended at the end, the select screen showed "Rogue"). build_modstrings()
# therefore SKIPS any key in this dict during per-file section emission, making
# this block the SINGLE definition of each key, and a fail-loud duplicate-tag
# gate (check_duplicate_tags) guards the whole file against regressions.
OCCULT_FIX_TAGS = {
    'tagMasteryBrief05': 'Occult',
    'tagMasteryTitle05': 'Occult Mastery',
    # Select-screen mastery description (replaces the vanilla Rogue flavor text
    # SV left in place). Wording drafted from the shipped Occult tree's actual
    # skill set (envenomed blades/knives, Breach + Shadow Grasp, Nether Strike,
    # Darklings + Shadow Stalker summons) - EXACT COPY NEEDS WILL'S SIGN-OFF
    # (Occult is his hand-tuned mastery).
    'tagMasteryDescription05': "The Occultist tempers an assassin's craft with powers drawn from the dark: envenomed blades and flurries of knives for the single kill, and torn-open breaches that grasp, drain, and wither whole packs. Those who walk deepest into the shadow no longer fight alone, for darklings and the shadow stalker answer their call.",
    'tagSkillName050': 'Occult Mastery',
    'tagNewSkill321DESC': 'Infusing the Breach with shadow energy, the Occultist reaches through and grasps enemies, immobilizing them as dark forces sap their life force.',
}

# Non-Occult display-string corrections, same single-definition mechanism as
# OCCULT_FIX_TAGS (skipped during per-file SV emission; emitted once in the fix
# block; guarded by the duplicate-tag gate; folded into the mod-tag manifest).
# B-AREA-NAME-1: SV 0.98i's own text ships tagMZoneGoM=Duister (upstream
# leftover), so the Garden of Merchants zone displayed 'Duister' on the minimap.
# NOTE deliberately NOT touched (out of scope per the area-name audit): the
# sibling tagMPortalGoM still reads 'Duister Portal' - flagged for Will.
TEXT_FIX_TAGS = {
    'tagMZoneGoM': 'Garden of Merchants',
    # D7 (Will 2026-07-09): the hidden blood-cave chest is renamed from "Esti's
    # Chest" to "Toxeus the Murderer's Stash" (now guarded by the Toxeus the
    # Murderer, Devourer of Blood superboss). tagSQECTitle is the chest journal/
    # name tag; single-definition here (skipped during SV emission, dup-gated). The
    # reward-popup mirror tagTitleTagTESTER is updated to match below. No em dashes.
    'tagSQECTitle': "Toxeus the Murderer's Stash",
    # B-SUPRA-NOTIFY-1: the tester-tag notification strings are ALREADY
    # resolved by QUEST_INTEGRATION_TAGS below (tagLOCATIONTAGTESTER /
    # tagTitleTagTESTER); do not redefine them here or the duplicate-tag gate
    # fails (verified 2026-07-08, build29).
    # D15 (Will, build31): Fortitude + skill-point potions get the same dark
    # red ^M color as the experience potions (tagNewItem6=^MPotion of
    # Experience). Each tag is used by EXACTLY ONE record (arz-wide reverse
    # scan, zero sharing - see BACKLOG D15 recon). SV-upstream tags, so the
    # override rides this sanctioned single-definition block.
    'tagNewItem3': '^MLesser Potion of Fortitude',
    'tagNewItem70': '^MPotion of Fortitude',
    'tagNewItem4': '^MLesser Potion of Learning',
    'tagNewItem69': '^MPotion of Learning',
    # build36 A3 (Sanguine Tithe green-name polish, Will's "the blood harness guys
    # with the green name"): the 3 Sileni (DRX bloodabomination) name tags get the
    # {^G} green prefix so they read green in-game, the same way the Emberscale-
    # source Flameguard Slayer is flagged green. Single-definition override here
    # (skipped during SV per-file emission, emitted once in the fix block) so it
    # cannot trip the duplicate-tag gate; folded into the mod-tag manifest via
    # TEXT_FIX_TAGS.keys() so validate_tags treats them as mod-owned + present.
    'tagAbomDW': '{^G}Sileni - Carver',
    'tagAbomSpear': '{^G}Sileni - Impaler',
    'tagAbomBrute': '{^G}Sileni - Butcher',
    # F7b (build36 fix wave): the grafted Earth Rupture skill is Staff-OR-Bow
    # (lane B graft), but its 0.98i tooltip (tagRuptureDESC in xuniqueequipment.txt)
    # reads "^y(Staff Only)". Overriding it here (single-definition; SV emission
    # skips _FIX_BLOCK_TAGS keys, so no duplicate-tag-gate trip - the exact reason
    # lane B could NOT fix it via the uber_soul_tags data path) corrects the
    # weapon restriction to match the skill.
    'tagRuptureDESC': ("Connects the player's tumultuous earth energies to their "
                       "weapon, causing projectiles to explode on impact. "
                       "^y(Staff or Bow)"),
}

# The union skip-set: any key in here is emitted ONLY by the fix block.
_FIX_BLOCK_TAGS = {**OCCULT_FIX_TAGS, **TEXT_FIX_TAGS}


def extract_tags(text: str) -> OrderedDict:
    """Parse tag=value lines from a text file, preserving order."""
    tags = OrderedDict()
    for line in text.split('\n'):
        line = line.strip('\r')
        if not line or line.startswith('//'):
            continue
        if '=' in line:
            key, _, value = line.partition('=')
            tags[key.strip()] = value
    return tags


def build_modstrings(sv_arc_path: Path, uber_tags_path: Path = None,
                     extra_tags: dict = None) -> str:
    """Build modstrings.txt content from SV 0.98i Text_EN.arc."""
    arc = ArcArchive.from_file(sv_arc_path)

    text_files = [
        'commonequipment.txt',
        'monsters.txt',
        'skills.txt',
        'uniqueequipment.txt',
        'ui.txt',
        'dialog.txt',
        'install.txt',
        'menu.txt',
        'npc.txt',
        'quest.txt',
        'tutorial.txt',
        'xcommonequipment.txt',
        'xdialog.txt',
        'xinstall.txt',
        'xmenu.txt',
        'xmonsters.txt',
        'xnpc.txt',
        'xquest.txt',
        'xskills.txt',
        'xtutorial.txt',
        'xui.txt',
        'xuniqueequipment.txt',
    ]

    all_tags = OrderedDict()
    sections = []

    for fname in text_files:
        text = arc.get_text(fname)
        if text is None:
            print(f"  WARNING: {fname} not found in arc")
            continue

        tags = extract_tags(text)
        print(f"  {fname}: {len(tags)} tags")

        section_lines = [f'//{fname} - START']
        for key, value in tags.items():
            # B-MASTERY-LABEL-1 / B-AREA-NAME-1: keys owned by the fix block
            # (Occult labels + text corrections) are NEVER emitted from the SV
            # source files - the fix block below is their single definition.
            # (The engine keeps the FIRST definition of a duplicated tag, so
            # emitting SV's "Rogue Mastery" / "Duister" lines here made the
            # appended fix block a dead letter.)
            if key in _FIX_BLOCK_TAGS:
                continue
            if key not in all_tags:
                all_tags[key] = value
                section_lines.append(f'{key}={value}')
            # A later SV file may redefine a tag with a different value (12
            # such cross-file redefinitions exist, e.g. xui.txt restyling
            # ui.txt format strings). The engine keeps the FIRST definition,
            # so re-emitting the later value is dead weight that would also
            # trip the duplicate-tag gate; drop it. Effective in-game values
            # are IDENTICAL to the previous build (first-wins either way).
        section_lines.append(f'//{fname} - END')
        sections.append('\r\n'.join(section_lines))

    # Apply the fix block: Occult mastery fixes (labels + select-screen
    # description + missing skill descriptions) + text corrections
    # (TEXT_FIX_TAGS, e.g. the tagMZoneGoM 'Duister' -> 'Garden of Merchants'
    # zone-name fix). These keys were SKIPPED during per-file emission above,
    # so each line below is that tag's SINGLE definition (first-wins safe).
    fix_lines = ['//Occult mastery label fix + text corrections - START']
    for key, value in _FIX_BLOCK_TAGS.items():
        all_tags[key] = value
        fix_lines.append(f'{key}={value}')
    fix_lines.append('//Occult mastery label fix + text corrections - END')
    sections.append('\r\n'.join(fix_lines))
    print(f"  Applied fix-block tags ({len(OCCULT_FIX_TAGS)} Occult + "
          f"{len(TEXT_FIX_TAGS)} text corrections)")

    # Add uber soul tags
    uber_count = 0
    if uber_tags_path and uber_tags_path.exists():
        # Staleness guard: the soul tag list (uber_soul_tags.txt) is written by
        # build_svc_database.py alongside SoulvizierClassic.arz. Within one build
        # the tag list is written first, then the (large) .arz seconds later, so
        # the .arz is normally a little newer. A LARGE gap means the .arz was
        # rebuilt in a separate session without regenerating tags, so the tags
        # are stale and Text.arc would be built against an old soul roster (the
        # tagSoulSVC9005/9006 orphan bug). We only warn here; the authoritative
        # content check is the tools/validate_tags.py gate.
        _STALE_GAP_SECONDS = 600  # 10 min: well past a same-build .arz write
        sibling_arz = uber_tags_path.parent / 'SoulvizierClassic.arz'
        if sibling_arz.exists() and \
                sibling_arz.stat().st_mtime - uber_tags_path.stat().st_mtime \
                > _STALE_GAP_SECONDS:
            print(f"  WARNING: {sibling_arz.name} is much newer than "
                  f"{uber_tags_path.name}; soul tags may be stale. "
                  f"Rebuild the .arz and Text.arc together, then run "
                  f"validate_tags.py.")
        uber_text = uber_tags_path.read_text(encoding='utf-8')
        uber_lines = ['//uber_soul_tags - START']
        for line in uber_text.strip().split('\n'):
            line = line.strip()
            if line and '=' in line:
                key, _, value = line.partition('=')
                all_tags[key.strip()] = value
                uber_lines.append(f'{key.strip()}={value}')
                uber_count += 1
        uber_lines.append('//uber_soul_tags - END')
        sections.append('\r\n'.join(uber_lines))
    print(f"  Added {uber_count} uber soul tags")

    # Add any extra tags
    if extra_tags:
        extra_lines = ['//extra_tags - START']
        for key, value in extra_tags.items():
            all_tags[key] = value
            extra_lines.append(f'{key}={value}')
        extra_lines.append('//extra_tags - END')
        sections.append('\r\n'.join(extra_lines))
        print(f"  Added {len(extra_tags)} extra tags")

    print(f"  Total unique tags: {len(all_tags)}")

    return '\r\n'.join(sections) + '\r\n'


def check_duplicate_tags(modstrings: str):
    """FAIL-LOUD duplicate-tag gate (B-MASTERY-LABEL-1 hardening).

    The engine keeps the FIRST definition of a tag duplicated inside
    modstrings.txt, so a second CONFLICTING definition is at best dead weight
    and at worst (when the intended value is the later one, as with the Occult
    mastery fix) a silent display bug. Returns the list of
    (tag, [values...]) conflicts; callers raise on non-empty. Exact-duplicate
    re-definitions (same value twice) are reported as warnings only.
    """
    from collections import OrderedDict
    defs = OrderedDict()
    for line in modstrings.split('\n'):
        line = line.strip('\r').strip()
        if not line or line.startswith('//') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        defs.setdefault(key.strip(), []).append(value)
    conflicts = [(k, vs) for k, vs in defs.items() if len(set(vs)) > 1]
    exact_dups = [(k, vs) for k, vs in defs.items()
                  if len(vs) > 1 and len(set(vs)) == 1]
    for k, vs in exact_dups:
        print(f"  WARNING duplicate tag (same value {len(vs)}x, harmless): {k}")
    return conflicts


# Quest text tags the integrated SV area questlines reference but that are ABSENT
# from SV 0.98i's own Text_EN.arc source. open_bloodcave_portal.qst's hidden-chest
# reward (Action_GiveItem) uses these two as its locationTag/titleTag; upstream left
# them as raw "TESTER" placeholders, so without a definition the reward popup would
# show literal "tagLOCATIONTAGTESTER"/"tagTitleTagTESTER" in-game. We resolve them to
# the same strings the quest's real journal entry uses (tagSQECLocation/tagSQECTitle).
QUEST_INTEGRATION_TAGS = {
    'tagLOCATIONTAGTESTER': 'The Blood Cave',
    # D7 (Will 2026-07-09): mirror the renamed chest title (tagSQECTitle ->
    # "Toxeus the Murderer's Stash") so the reward-popup title matches the journal.
    'tagTitleTagTESTER': "Toxeus the Murderer's Stash",
}


# Manifest of every tag this mod's build AUTHORS into its Text.arc, written next
# to Text.arc so tools/validate_tags.py can gate on "written-set membership"
# (a referenced tag is mod-owned iff it is in this manifest) instead of a fixed
# prefix allowlist. This is what makes the gate false-positive-free: base-game
# tags the .arz merely carries forward (tagNewMonster*, tagItem*, ...) are NOT
# in the manifest, so they are never required to appear in the mod's Text.arc
# even though they are referenced.
MOD_AUTHORED_TAGS_MANIFEST = 'mod_authored_tags.txt'


def _read_tag_keys(path: Path) -> set:
    """Return the set of 'key' tokens from a key=value tag list file."""
    keys = set()
    if not path or not Path(path).exists():
        return keys
    for line in Path(path).read_text(encoding='utf-8').split('\n'):
        line = line.strip('\r').strip()
        if not line or line.startswith('//') or '=' not in line:
            continue
        key, _, _ = line.partition('=')
        keys.add(key.strip())
    return keys


def collect_mod_authored_tags(uber_tags_path: Path = None) -> set:
    """Return the authoritative set of tags this mod build authors into Text.arc.

    Union of the build's own tag emitters, gathered from their single sources of
    truth so the manifest cannot drift from what the build actually writes:
      - build_text_arc.py OCCULT_FIX_TAGS keys (Occult label + skill fixes)
      - build_text_arc.py QUEST_INTEGRATION_TAGS keys (quest-reward placeholders)
      - build_svc_database.py MOD_DESC_FIX_TAGS values (skillBaseDescription tags
        the DB wires onto DRX skills, e.g. tagbreachDESC / tagNewSkill321DESC)
      - uber_soul_tags.txt keys (soul + legacy + extended tags, incl. tagD2Boss*)

    Every member is a tag the mod defines in modstrings.txt; none is a base-game
    tag that resolves from the engine's own text, so requiring these to be
    present in Text.arc yields zero false positives.
    """
    tags = set(OCCULT_FIX_TAGS.keys())
    tags |= set(TEXT_FIX_TAGS.keys())
    tags |= set(QUEST_INTEGRATION_TAGS.keys())

    # Portal description tag referenced by the portal NPC records the DB build
    # creates (build_svc_database.py, description=xtagMysteriousPortal). Its
    # display string comes from the upstream SV text; require it so an orphan is
    # caught (the old prefix validator covered it via the xtagMysteriousPortal prefix).
    tags.add('xtagMysteriousPortal')

    # MOD_DESC_FIX_TAGS lives in build_svc_database.py (the DB build wires these
    # description tags onto skill records). Import defensively so a rename there
    # fails loud rather than silently narrowing the manifest.
    try:
        from build_svc_database import MOD_DESC_FIX_TAGS
        tags |= set(MOD_DESC_FIX_TAGS.values())
    except Exception as exc:  # pragma: no cover - guard against refactors
        print(f"  WARNING: could not import MOD_DESC_FIX_TAGS from "
              f"build_svc_database.py ({exc}); description-fix tags "
              f"(tagbreachDESC, ...) will be omitted from the mod-tag manifest.")

    tags |= _read_tag_keys(uber_tags_path)
    return tags


def write_mod_tag_manifest(output_dir: Path, uber_tags_path: Path = None) -> Path:
    """Write the mod-authored-tag manifest next to Text.arc; return its path."""
    manifest_path = Path(output_dir) / MOD_AUTHORED_TAGS_MANIFEST
    tags = collect_mod_authored_tags(uber_tags_path)
    lines = [
        '// Authoritative list of tags authored into Text.arc by the '
        'SoulvizierClassic build.',
        '// Written by tools/build_text_arc.py; consumed by '
        'tools/validate_tags.py as the',
        '// mod-owned tag set (written-set membership). One tag key per line. '
        'Do not hand-edit.',
    ]
    lines.extend(sorted(tags))
    manifest_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"  Mod-tag manifest: {manifest_path} ({len(tags)} tags)")
    return manifest_path


def build_text_arc(sv_arc_path: Path, output_path: Path,
                   uber_tags_path: Path = None):
    """Build the final Text.arc file."""
    print(f"Building modstrings.txt from: {sv_arc_path}")
    modstrings = build_modstrings(sv_arc_path, uber_tags_path,
                                  extra_tags=QUEST_INTEGRATION_TAGS)

    # ── Duplicate-tag gate (fail-loud, B-MASTERY-LABEL-1 hardening) ─────────
    # The engine keeps the FIRST definition of a duplicated tag, so a second
    # conflicting definition is a silent display bug (the "Rogue" mastery
    # label). A build with any conflicting duplicate does NOT ship.
    conflicts = check_duplicate_tags(modstrings)
    if conflicts:
        for k, vs in conflicts[:20]:
            print(f"  DUPLICATE-TAG OFFENDER: {k} defined {len(vs)}x with "
                  f"conflicting values: {[v[:60] for v in vs]}")
        raise SystemExit(
            f"Duplicate-tag gate FAILED: {len(conflicts)} tag(s) defined more "
            f"than once with conflicting values in modstrings.txt (the engine "
            f"keeps the FIRST, so later intended values are silently dead). "
            f"Fix the emitters; see offenders above.")
    print(f"  Duplicate-tag gate OK: no conflicting duplicate definitions")

    print(f"\nBuilding Text.arc...")
    # We need to create a new arc with just modstrings.txt
    # Use SVAERA's Text.arc as a template for the structure
    encoded = b'\xff\xfe' + modstrings.encode('utf-16-le')
    print(f"  modstrings.txt: {len(modstrings)} chars, {len(encoded)} bytes")

    # Create arc from scratch - we need a minimal arc with one file
    arc = create_single_file_arc(encoded, 'modstrings.txt')
    size = arc.write(output_path)
    print(f"  Written: {output_path} ({size} bytes)")

    # Verify
    arc2 = ArcArchive.from_file(output_path)
    data = arc2.get_file('modstrings.txt')
    if data and len(data) == len(encoded):
        text_back = arc2.get_text('modstrings.txt')
        if 'tagNewHero' in text_back and 'tagMasteryBrief05=Occult' in text_back:
            print("  Verification: OK (tags found)")
        else:
            print("  WARNING: Tags not found in verification read")
    else:
        print(f"  WARNING: Size mismatch in verification ({len(data) if data else 0} vs {len(encoded)})")

    # Emit the authoritative mod-authored-tag manifest alongside Text.arc so the
    # validate_tags.py build gate can use written-set membership.
    write_mod_tag_manifest(Path(output_path).parent, uber_tags_path)

    # ── A7 golden freeze guard, Text half (fail-loud) ───────────────────────
    # The arz build already gated the DB half; with the fresh Text.arc in hand
    # we re-check the FULL pair, so any drift in an Occult/Hunting name/desc
    # tag definition (value, duplication, or definition order - the engine
    # keeps the FIRST definition) fails the Text build too. The arz is derived
    # from the uber_soul_tags.txt location (same Database dir, same build).
    arz_path = Path(uber_tags_path).resolve().parent / 'SoulvizierClassic.arz'
    if arz_path.exists():
        from validate_mastery_golden import validate as _validate_golden
        if _validate_golden(str(arz_path), str(output_path)) != 0:
            raise SystemExit(
                "Occult/Hunting golden freeze guard FAILED on arz + Text.arc; "
                "this Text build does not ship (A7 gate)")
    else:
        print(f"  WARNING: A7 golden guard SKIPPED - no arz at {arz_path} "
              f"(build the database first for the full gate)")

    return output_path


def create_single_file_arc(data: bytes, filename: str) -> ArcArchive:
    """Create a new ArcArchive with a single file entry.

    AE expects a specific structure with empty entries for each directory
    level in the file path (even though modstrings.txt has no path).
    """
    import struct
    import zlib

    arc = ArcArchive()
    arc.version = 1

    # Build string table
    name_bytes = filename.encode('utf-8') + b'\x00'
    arc.raw_string_table = name_bytes

    # Compress data into parts
    PART_SIZE = 262144
    parts = []
    pos = 0
    while pos < len(data):
        chunk = data[pos:pos + PART_SIZE]
        compressed = zlib.compress(chunk, 6)
        parts.append(type('Part', (), {
            'offset': 0, 'comp_size': len(compressed),
            'decomp_size': len(chunk), 'compressed_data': compressed
        })())
        pos += PART_SIZE

    total_comp = sum(p.comp_size for p in parts)

    # Create file entry with proper 44-byte record
    raw_record = bytearray(44)
    struct.pack_into('<I', raw_record, 0, 3)  # entry_type = file
    struct.pack_into('<I', raw_record, 4, 0)  # data_offset (set by write)
    struct.pack_into('<I', raw_record, 8, total_comp)
    struct.pack_into('<I', raw_record, 12, len(data))
    # bytes 16-27: metadata (zeros)
    struct.pack_into('<I', raw_record, 28, len(parts))  # num_parts
    struct.pack_into('<I', raw_record, 32, 0)  # file_index
    struct.pack_into('<I', raw_record, 36, len(filename.encode('utf-8')))
    struct.pack_into('<I', raw_record, 40, 0)  # string_offset

    from arc_patcher import ArcEntry
    entry = ArcEntry(bytes(raw_record))
    entry.name = filename
    entry.parts = []

    for p in parts:
        from arc_patcher import FilePart
        entry.parts.append(FilePart(0, p.comp_size, p.decomp_size, p.compressed_data))

    arc.entries = [entry]
    return arc


if __name__ == '__main__':
    # Reproducible builds: pin PYTHONHASHSEED=0 (see build_svc_database._pin_hashseed).
    # PYTHONHASHSEED must be fixed BEFORE interpreter startup, so re-exec once with
    # it set if it was not already pinned. Text.arc is already order-stable; this
    # keeps the whole DB-lane pipeline uniformly deterministic regardless of the
    # launching environment.
    if os.environ.get('PYTHONHASHSEED') != '0':
        os.environ['PYTHONHASHSEED'] = '0'
        import subprocess
        sys.exit(subprocess.call([sys.executable, *sys.argv]))

    if len(sys.argv) < 3:
        print("Usage: build_text_arc.py <sv_text_en.arc> <output_text.arc> [uber_tags.txt]")
        sys.exit(1)

    sv_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    uber_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    build_text_arc(sv_path, out_path, uber_path)
