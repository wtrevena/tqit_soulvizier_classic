"""Build-time validator: every mod name/description tag in the .arz must
resolve to a string in the final Text.arc.

Root problem this guards against: create_uber_souls.py regenerates a different
tag->monster mapping on every build (as the candidate pool shrinks), while
build_text_arc.py is a separate invocation with no staleness coupling. If
Text.arc is built against an older tag list than the .arz, a soul item ends up
referencing a tag (e.g. tagSoulSVC9005 / tagSoulSVC9006) that is absent from
Text.arc, so the raw tag string shows in-game instead of the soul name.

What "mod-owned" means (the design that keeps this false-positive-free):
  A tag is MOD-OWNED iff the mod's build actually AUTHORS it into its own
  Text.arc. The build now emits that authoritative set to a manifest
  (mod_authored_tags.txt, written by build_text_arc.py next to Text.arc) which
  is the union of every tag the build's emitters source:
    - build_text_arc.py OCCULT_FIX_TAGS + QUEST_INTEGRATION_TAGS
    - build_svc_database.py MOD_DESC_FIX_TAGS values (tagbreachDESC, ...)
    - uber_soul_tags.txt keys (soul + legacy + extended, incl. tagD2Boss*)
  Membership in that written set - NOT a hard-coded tag prefix - decides
  mod-ownership. Base-game tags the .arz merely carries forward
  (tagNewMonster*, tagItem*, tagMonsterNameSFM*, ...) are overlaid on the
  engine's own text and are NOT in the manifest, so they never produce false
  positives even though they are referenced by the .arz.

  If the manifest is absent (e.g. running against an older build), the validator
  falls back to a prefix allowlist. That list contains ONLY prefixes confirmed
  to be authored into the mod's Text.arc (never base-game namespaces), so the
  fallback is also false-positive-free; it is just coarser than the manifest.

What it does:
  1. Loads the final .arz and collects every name/description-like tag
     reference (itemNameTag, description, skillDisplayName, ...).
  2. Loads the final Text.arc (modstrings.txt) and collects every defined tag.
  3. Determines which referenced tags are MOD-OWNED (manifest membership, or the
     prefix fallback) and requires every mod-owned referenced tag to be defined
     in Text.arc.
  4. Optionally cross-checks an authoritative tag list (uber_soul_tags.txt,
     written by build_svc_database.py) against Text.arc.

On any miss it prints a clear list and exits non-zero so the build/bootstrap
can gate on it.

Usage:
  py tools/validate_tags.py <final.arz> <final_text.arc> [authoritative_tags.txt]
                            [mod_authored_tags.txt]

If the 4th argument is omitted, the manifest is auto-discovered as
'mod_authored_tags.txt' next to the Text.arc.

Exit codes:
  0 = all referenced mod tags present in Text.arc
  1 = one or more mod tags missing (details printed)
  2 = usage / input error (could not read an input file)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase
from arc_patcher import ArcArchive


# Name/description-like fields whose string values are text tags that must
# resolve to a Text.arc entry for the item/skill to display correctly.
TAG_FIELDS = frozenset({
    'itemNameTag',
    'description',
    'itemText',
    'skillDisplayName',
    'skillBaseDescription',
    'FileTextTag',
    'lootRandomizerName',
    'ActorName',
})

# Fallback only. Prefixes of tags this mod pipeline OWNS, used when the
# authoritative manifest (mod_authored_tags.txt) is not available. Every prefix
# here has been confirmed to be authored into the mod's OWN Text.arc (not a
# base-game namespace that resolves from the engine), so the fallback stays
# false-positive-free. The manifest supersedes this list when present.
#
# Confirmed against the built Text.arc (see the D3 verification):
#   tagSoulSVC*      - create_uber_souls.py auto-generated soul names
#   tagSVCSoul*      - apply_svc_patches.py hand-authored soul names
#   tagSVCSummon*    - apply_svc_patches.py summon-skill names/descriptions
#   tagDarkAperture* - build_svc_database.py legacy-skill tags
#   xtagMysteriousPortal* - build_svc_database.py custom portal description tag
#   tagD2Boss004     - apply_svc_patches.py boss rename (Cold Worm). EXACT, not
#                      the tagD2Boss* prefix.
#                      HISTORICAL NOTE (b52, corrected): an earlier comment here
#                      claimed the .arz's other tagD2Boss* ref, tagD2Boss033
#                      (records\test\boss_dagon_66.dbr = Dagon), "resolves from the
#                      base game". That was FACTUALLY WRONG: tagD2Boss033 is defined
#                      in NEITHER the mod Text.arc, SV 0.98i upstream, NOR base
#                      Text_EN.arc - so Dagon shipped with a RAW display name. This
#                      mod-owned-only filter is exactly why the gate missed it (a
#                      non-mod-owned tag was assumed base-resolved and never checked).
#                      The blind spot is now closed by check_monster_name_tags()
#                      below, which cross-checks every spawn-referenced monster's name
#                      against the mod Text.arc AND base Text_EN.arc. Dagon's monster
#                      is now named tagSVCMonsterDagon (mod-owned) by apply_svc_patches.
#   tagSkillName050  - build_text_arc.py Occult mastery title (exact tag)
#   tagNewSkill321DESC - build_text_arc.py Occult skill description (exact tag)
#   tagbreachDESC    - build_svc_database.py MOD_DESC_FIX_TAGS (exact tag; the
#                      string is sourced from SV 0.98i's own extracted text)
# NOTE: these are deliberately NOT broadened to whole base-game families such as
# tagNewSkill* / tagSkillName* / tagMastery* / tagNewMonster* / tagD2Boss*,
# because the .arz references many base-game members of those families that
# resolve from the base game and are absent from the mod Text.arc (they would
# false-positive). Each entry above was checked to startswith-match ONLY the
# mod-authored tag(s), never a base-game tag.
MOD_TAG_PREFIXES = (
    'tagSoulSVC',
    'tagSVCSoul',
    'tagSVCSummon',
    'tagSVCMonster',   # b52: mod-authored monster display names (tagSVCMonsterDagon)
    'tagDarkAperture',
    'xtagMysteriousPortal',
    'tagD2Boss004',
    'tagSkillName050',
    'tagNewSkill321DESC',
    'tagbreachDESC',
)


def is_mod_tag_by_prefix(tag):
    """Fallback ownership test: True if the tag matches a mod-owned prefix."""
    return tag.startswith(MOD_TAG_PREFIXES)


# Spawn-pool fields: a monster record referenced through one of these (as a .dbr
# value) can actually SPAWN in-game, so a raw/unresolved display name on it is
# visible. Used to scope the monster-name gate to monsters that can appear.
_SPAWN_FIELD_RE = __import__('re').compile(r'^(name|nameChampion|partyMember)\d*$')


def _field_first(fields, field_name):
    """First value of `field_name` in an already-fetched get_fields() dict (keys may
    carry a '###n' suffix), or None."""
    for key, tf in fields.items():
        if key.split('###')[0] == field_name and tf.values:
            return tf.values[0]
    return None


def collect_arz_tag_refs(arz_path):
    """Single load of the .arz -> (all_refs, monster_names, spawn_referenced).

    all_refs        : {tag: [(record, field), ...]} for ALL string tag-field refs
                      (ownership filtering is applied by the caller).
    monster_names   : [(record, description_tag), ...] for every Class==Monster
                      record whose `description` is a tag-like string (its display
                      name). Fed to the monster-name blind-spot cross-check.
    spawn_referenced: set of lowercased .dbr paths referenced by any spawn-pool
                      field (name*/nameChampion*/partyMember*) - i.e. monsters that
                      can appear in-game.
    """
    db = ArzDatabase.from_arz(arz_path)
    refs = {}
    monster_names = []
    spawn_referenced = set()
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        is_monster = (_field_first(fields, 'Class') == 'Monster')
        for key, tf in fields.items():
            field_name = key.split('###')[0]
            if tf.values and _SPAWN_FIELD_RE.match(field_name):
                for val in tf.values:
                    if isinstance(val, str) and val.lower().endswith('.dbr'):
                        spawn_referenced.add(val.replace('/', '\\').lower())
            if field_name not in TAG_FIELDS or not tf.values:
                continue
            for val in tf.values:
                if not isinstance(val, str) or not val:
                    continue
                refs.setdefault(val, []).append((name, field_name))
                if is_monster and field_name == 'description' and val.startswith('tag'):
                    monster_names.append((name, val))
    return refs, monster_names, spawn_referenced


def load_base_en_tag_set(base_text_en_path=None):
    """Return the set of tag keys defined in the player's base-game Text_EN.arc, or
    None if it cannot be located/loaded (the caller then SKIPS the base cross-check
    rather than false-failing). Reuses build_text_arc's discovery + loader so the
    gate reads exactly the base text the build's i18n de-clobber reads."""
    try:
        import build_text_arc as _bta
    except Exception as exc:
        print(f"  Base Text_EN: build_text_arc import failed ({exc})")
        return None
    arc = None
    if base_text_en_path and Path(base_text_en_path).exists():
        arc = Path(base_text_en_path)
    else:
        try:
            arc = _bta.discover_base_text_en()
        except Exception:
            arc = None
    if not arc or not Path(arc).exists():
        return None
    try:
        return set(_bta.load_base_en_tags(Path(arc)).keys()), str(arc)
    except Exception as exc:
        print(f"  Base Text_EN: load failed ({exc})")
        return None


# Monster display names known to resolve NOWHERE (mod, SV upstream, base) as a
# PRE-EXISTING base/SV affix-variant class (tagNewMonster*/tagMonsterNameSFM*), NOT
# introduced by this mod. They are surfaced as WARNINGS (a separate backlog item),
# never a hard build-fail - fixing ~90 base affix-variant names is out of scope for a
# mod content gate. The HARD fail is scoped to records\test\ cut-content bosses the
# mod PROMOTES into spawn pools (the Dagon blind-spot class).
_MONSTER_NAME_HARD_FAIL_PREFIX = 'records\\test\\'


def collect_text_arc_tags(arc_path):
    """Return the set of tag keys defined in the Text.arc modstrings.txt."""
    arc = ArcArchive.from_file(arc_path)
    text = arc.get_text('modstrings.txt')
    if text is None:
        # Fall back to any single text file present in the arc.
        for entry in arc.entries:
            if getattr(entry, 'name', '').lower().endswith('.txt'):
                text = arc.get_text(entry.name)
                if text is not None:
                    break
    if text is None:
        return None
    defined = set()
    for line in text.split('\n'):
        line = line.strip('\r').strip()
        if not line or line.startswith('//'):
            continue
        if '=' in line:
            key, _, _ = line.partition('=')
            defined.add(key.strip())
    return defined


def load_authoritative_tags(tags_path):
    """Return the set of tag keys from an authoritative tag list file."""
    defined = set()
    text = Path(tags_path).read_text(encoding='utf-8')
    for line in text.split('\n'):
        line = line.strip('\r').strip()
        if not line or line.startswith('//'):
            continue
        if '=' in line:
            key, _, _ = line.partition('=')
            defined.add(key.strip())
    return defined


def load_mod_manifest(manifest_path):
    """Return the set of mod-owned tag keys from mod_authored_tags.txt.

    The manifest is one tag key per line (comments start with //). It also
    tolerates key=value lines so it can share the tag-list format.
    """
    keys = set()
    text = Path(manifest_path).read_text(encoding='utf-8')
    for line in text.split('\n'):
        line = line.strip('\r').strip()
        if not line or line.startswith('//'):
            continue
        key = line.partition('=')[0] if '=' in line else line
        key = key.strip()
        if key:
            keys.add(key)
    return keys


def validate(arz_path, text_arc_path, authoritative_tags_path=None,
             manifest_path=None, base_text_en_path=None):
    """Validate mod tag references against Text.arc. Returns True if all pass."""
    arz_path = Path(arz_path)
    text_arc_path = Path(text_arc_path)

    print("=== Tag validation ===")
    print(f"  .arz     : {arz_path}")
    print(f"  Text.arc : {text_arc_path}")

    if not arz_path.exists():
        print(f"  ERROR: .arz not found: {arz_path}")
        return None
    if not text_arc_path.exists():
        print(f"  ERROR: Text.arc not found: {text_arc_path}")
        return None

    # Resolve the mod-owned tag set. Prefer the written manifest (written-set
    # membership); auto-discover it next to Text.arc if not passed explicitly.
    if manifest_path is None:
        candidate = text_arc_path.parent / 'mod_authored_tags.txt'
        if candidate.exists():
            manifest_path = candidate
    mod_tags = None
    if manifest_path and Path(manifest_path).exists():
        mod_tags = load_mod_manifest(manifest_path)
        print(f"  Mod-tag manifest: {Path(manifest_path).name} "
              f"({len(mod_tags)} mod-owned tags) -> written-set membership")
    else:
        print(f"  Mod-tag manifest: (none found) -> prefix fallback "
              f"{MOD_TAG_PREFIXES}")

    def is_mod_owned(tag):
        if mod_tags is not None:
            return tag in mod_tags
        return is_mod_tag_by_prefix(tag)

    defined = collect_text_arc_tags(text_arc_path)
    if defined is None:
        print("  ERROR: could not read modstrings.txt from Text.arc")
        return None
    print(f"  Text.arc defines {len(defined)} tags")

    all_refs, monster_names, spawn_referenced = collect_arz_tag_refs(arz_path)
    refs = {t: r for t, r in all_refs.items() if is_mod_owned(t)}
    print(f"  .arz references {len(all_refs)} distinct tag values; "
          f"{len(refs)} are mod-owned (via {sorted(TAG_FIELDS)})")

    missing = sorted(t for t in refs if t not in defined)

    ok = True

    if missing:
        ok = False
        print("")
        print(f"  FAIL: {len(missing)} mod tag(s) referenced by the .arz are "
              f"MISSING from Text.arc:")
        for tag in missing:
            examples = refs[tag]
            first = examples[0][0]
            more = f" (+{len(examples) - 1} more)" if len(examples) > 1 else ""
            print(f"    - {tag}   e.g. {first}{more}")
    else:
        print(f"  OK: all {len(refs)} referenced mod tags are present in Text.arc")

    # ── MONSTER-NAME BLIND-SPOT CROSS-CHECK (b52) ──────────────────────────────
    # The mod-owned filter above INTENTIONALLY skips non-mod-owned tags, assuming
    # they resolve from the base game. That assumption shipped Dagon with a raw name
    # (tagD2Boss033 resolves in NEITHER the mod Text.arc NOR base Text_EN.arc). Close
    # it: a monster's display name is its `description` tag; require every
    # SPAWN-REFERENCED monster's name to resolve in the mod Text.arc OR the base
    # Text_EN.arc. HARD-FAIL for records\test\ cut-content bosses the mod promotes
    # (the exact Dagon class); WARN for pre-existing base/SV affix variants so a
    # ~90-record base-naming backlog never blocks a mod build.
    base_loaded = load_base_en_tag_set(base_text_en_path)
    if base_loaded is None:
        print("")
        print("  Monster-name cross-check: SKIPPED (base Text_EN.arc not found; set "
              "SVC_TQAE_ROOT or pass it as arg 5). Non-fatal.")
    else:
        base_en, base_src = base_loaded
        print("")
        print(f"  Monster-name cross-check: base Text_EN {Path(base_src).name} "
              f"({len(base_en)} tags); {len(spawn_referenced)} spawn-referenced "
              f"records; {len(monster_names)} monster name tags")
        hard, warn = [], []
        for rec, tag in monster_names:
            if rec.replace('/', '\\').lower() not in spawn_referenced:
                continue  # inert record (never spawns) -> its raw name is never shown
            if tag in defined or tag in base_en:
                continue  # resolves in mod or base -> fine
            if rec.replace('/', '\\').lower().startswith(_MONSTER_NAME_HARD_FAIL_PREFIX):
                hard.append((rec, tag))
            else:
                warn.append((rec, tag))
        if warn:
            print(f"  WARN: {len(warn)} pre-existing base/SV monster name(s) resolve "
                  f"in neither mod nor base Text_EN (backlog, non-blocking):")
            for rec, tag in sorted(warn):
                print(f"    ~ {tag}   {rec}")
        if hard:
            ok = False
            print(f"  FAIL: {len(hard)} PROMOTED records\\test\\ monster(s) have a "
                  f"display name resolving in NEITHER mod Text.arc NOR base Text_EN "
                  f"(a RAW tag would show in-game):")
            for rec, tag in sorted(hard):
                print(f"    - {tag}   {rec}")
        else:
            print(f"  OK: every spawn-referenced records\\test\\ monster name resolves "
                  f"in mod Text.arc or base Text_EN")

    # Optional authoritative cross-check: every tag the DB build claims to have
    # emitted must also be in Text.arc. Catches a stale Text.arc even for tags
    # that (for any reason) are not referenced through the scanned fields.
    if authoritative_tags_path and Path(authoritative_tags_path).exists():
        auth = load_authoritative_tags(authoritative_tags_path)
        auth_missing = sorted(t for t in auth if t not in defined)
        print("")
        print(f"  Authoritative list: {Path(authoritative_tags_path).name} "
              f"({len(auth)} tags)")
        if auth_missing:
            ok = False
            print(f"  FAIL: {len(auth_missing)} authoritative tag(s) missing "
                  f"from Text.arc:")
            for tag in auth_missing:
                print(f"    - {tag}")
        else:
            print(f"  OK: all {len(auth)} authoritative tags are present in Text.arc")

    print("")
    print("  RESULT:", "PASS" if ok else "FAIL")
    return ok


def main():
    if len(sys.argv) < 3:
        print("Usage: validate_tags.py <final.arz> <final_text.arc> "
              "[authoritative_tags.txt] [mod_authored_tags.txt] [base_Text_EN.arc]")
        sys.exit(2)

    arz_path = sys.argv[1]
    text_arc_path = sys.argv[2]
    auth_path = sys.argv[3] if len(sys.argv) > 3 else None
    manifest_path = sys.argv[4] if len(sys.argv) > 4 else None
    base_text_en = sys.argv[5] if len(sys.argv) > 5 else None

    result = validate(arz_path, text_arc_path, auth_path, manifest_path,
                      base_text_en)
    if result is None:
        sys.exit(2)
    sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
