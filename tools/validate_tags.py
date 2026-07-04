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
#                      the tagD2Boss* prefix: the .arz also references base-game
#                      tagD2Boss033 (records\test\boss_dagon_66.dbr) which
#                      resolves from the base game and is absent from the mod
#                      Text.arc - a tagD2Boss* prefix would false-positive on it.
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


def collect_arz_tag_refs(arz_path):
    """Return {tag: [(record, field), ...]} for ALL string tag-field refs.

    Ownership filtering is applied by the caller (manifest membership or the
    prefix fallback), so this returns every candidate reference.
    """
    db = ArzDatabase.from_arz(arz_path)
    refs = {}
    for name in db.record_names():
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            field_name = key.split('###')[0]
            if field_name not in TAG_FIELDS or not tf.values:
                continue
            for val in tf.values:
                if not isinstance(val, str) or not val:
                    continue
                refs.setdefault(val, []).append((name, field_name))
    return refs


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
             manifest_path=None):
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

    all_refs = collect_arz_tag_refs(arz_path)
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
              "[authoritative_tags.txt] [mod_authored_tags.txt]")
        sys.exit(2)

    arz_path = sys.argv[1]
    text_arc_path = sys.argv[2]
    auth_path = sys.argv[3] if len(sys.argv) > 3 else None
    manifest_path = sys.argv[4] if len(sys.argv) > 4 else None

    result = validate(arz_path, text_arc_path, auth_path, manifest_path)
    if result is None:
        sys.exit(2)
    sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
