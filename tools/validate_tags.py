"""Build-time validator: every mod name/description tag in the .arz must
resolve to a string in the final Text.arc.

Root problem this guards against: create_uber_souls.py regenerates a different
tag->monster mapping on every build (as the candidate pool shrinks), while
build_text_arc.py is a separate invocation with no staleness coupling. If
Text.arc is built against an older tag list than the .arz, a soul item ends up
referencing a tag (e.g. tagSoulSVC9005 / tagSoulSVC9006) that is absent from
Text.arc, so the raw tag string shows in-game instead of the soul name.

What it does:
  1. Loads the final .arz and collects every name/description-like tag
     reference (itemNameTag, description, skillDisplayName, ...).
  2. Loads the final Text.arc (modstrings.txt) and collects every defined tag.
  3. Requires that every MOD-OWNED referenced tag (matching the mod's own tag
     namespaces, e.g. the soul tags this pipeline emits) is defined in Text.arc.
     Base-game tags (tagMonsterName*, tagSkillName*, ...) are overlaid on top of
     the engine's own text and are intentionally NOT required here, so they do
     not produce false positives.
  4. Optionally cross-checks an authoritative tag list (uber_soul_tags.txt,
     written by build_svc_database.py) against Text.arc.

On any miss it prints a clear list and exits non-zero so the build/bootstrap
can gate on it.

Usage:
  py tools/validate_tags.py <final.arz> <final_text.arc> [authoritative_tags.txt]

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

# Prefixes of tags this mod pipeline OWNS (creates and is responsible for
# defining in Text.arc). Only tags matching one of these are required to be
# present, which keeps base-game tags (overlaid by the engine) from producing
# false positives. Keep in sync with the tag emitters in create_uber_souls.py,
# apply_svc_patches.py, and build_svc_database.py.
MOD_TAG_PREFIXES = (
    'tagSoulSVC',            # create_uber_souls.py auto-generated soul names
    'tagSVCSoul',            # apply_svc_patches.py hand-authored soul names
    'tagSVCSummon',          # apply_svc_patches.py summon-skill names/descriptions
    'tagDarkAperture',       # build_svc_database.py legacy-skill tags
    'xtagMysteriousPortal',  # build_svc_database.py custom portal description tag
)


def is_mod_tag(tag):
    """True if the tag is one this mod build is responsible for defining."""
    return tag.startswith(MOD_TAG_PREFIXES)


def collect_arz_tag_refs(arz_path):
    """Return {tag: sorted list of (record, field)} for mod-owned tag refs."""
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
                if not is_mod_tag(val):
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


def validate(arz_path, text_arc_path, authoritative_tags_path=None):
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

    defined = collect_text_arc_tags(text_arc_path)
    if defined is None:
        print("  ERROR: could not read modstrings.txt from Text.arc")
        return None
    print(f"  Text.arc defines {len(defined)} tags")

    refs = collect_arz_tag_refs(arz_path)
    print(f"  .arz references {len(refs)} distinct mod tags "
          f"(via {sorted(TAG_FIELDS)})")

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
              "[authoritative_tags.txt]")
        sys.exit(2)

    arz_path = sys.argv[1]
    text_arc_path = sys.argv[2]
    auth_path = sys.argv[3] if len(sys.argv) > 3 else None

    result = validate(arz_path, text_arc_path, auth_path)
    if result is None:
        sys.exit(2)
    sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
