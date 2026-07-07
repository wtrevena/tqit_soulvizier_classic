r"""Build-time validator: every SOUL's granted-skill reference in the .arz must
resolve to a real record in the same .arz.

Root problem this guards against: soul rings grant skills by writing a DBR path
verbatim into augmentSkillName1..4 / itemSkillName / itemSkillAutoController
(apply_svc_patches.py `_set_soul_fields` does NO path resolution - it stores the
string as-is). If that path is wrong (e.g. `records\skills\dream\drxphantomstrike.dbr`
when the real record is `records\xpack\skills\dream\drxphantomstrike.dbr`, or a
skill that simply does not exist in TQAE like a Runemaster skill), the engine
silently grants NOTHING for that augment - the soul looks fine in the tooltip
lists but the bonus never applies. This bit "the strongest soul in the game"
(SP Toxeus) whose Phantom Strike + Distortion Wave augments were both dead.

What it does:
  1. Loads the final .arz.
  2. Finds every SOUL record (path under records\item\...\soul\...).
  3. For each, decodes the skill-granting string fields (see SOUL_SKILL_FIELDS)
     and requires each non-empty value to resolve to a real record in the .arz.
     Resolution is case-insensitive and slash-insensitive, matching how the
     TQAE engine resolves DBR references.
  4. On any unresolved reference it prints the soul + field + dead path and
     exits non-zero so the build / bootstrap can gate on it.

Scope note: only SOUL records are checked (that is the mod's own content). The
base game and SV upstreams carry a couple of dev/test items (e.g.
records\xpack\item\equipmentweapons\testweapon02.dbr) with their own dangling
test-skill refs; those are not souls, are not authored by this mod, and are
deliberately out of scope so they cannot produce a false build failure.

Usage:
  py tools/validate_soul_augments.py <final.arz>

Exit codes:
  0 = every soul skill reference resolves
  1 = one or more soul skill references dangle (details printed)
  2 = usage / input error (could not read the .arz)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase


# String fields on a soul (Jewelry_Ring) whose value is a DBR path to a skill /
# skill-controller record the item grants. Each must resolve to a real record or
# the granted skill / proc silently does nothing in-game.
SOUL_SKILL_FIELDS = (
    'itemSkillName',           # the active proc skill the ring casts
    'augmentSkillName1',       # +N to an existing skill (1..4)
    'augmentSkillName2',
    'augmentSkillName3',
    'augmentSkillName4',
    'itemSkillAutoController',  # AI controller that fires itemSkillName
)

# A record is a SOUL iff its path sits under an ...\soul\... item folder.
SOUL_MARKERS = ('\\soul\\', '/soul/')


def _norm(path):
    """Normalize a DBR path the way the engine resolves references:
    lowercase, backslash separators, trimmed."""
    return path.replace('/', '\\').lower().strip()


def is_soul_record(name):
    low = name.lower()
    return any(m in low for m in SOUL_MARKERS)


def validate(arz_path):
    db = ArzDatabase.from_arz(Path(arz_path))

    # Full normalized resolution set of every record name in the .arz.
    recset = {_norm(n) for n in db.record_names()}

    def resolves(path):
        return _norm(path) in recset

    souls = [n for n in db.record_names() if is_soul_record(n)]

    dangling = {}          # dead_path -> [(soul, field), ...]
    refs_checked = 0
    for name in souls:
        fields = db.get_fields(name)
        if not fields:
            continue
        for key, tf in fields.items():
            fname = key.split('###')[0]
            if fname not in SOUL_SKILL_FIELDS or not tf.values:
                continue
            for val in tf.values:
                if not isinstance(val, str) or not val.strip():
                    continue
                refs_checked += 1
                if not resolves(val):
                    dangling.setdefault(_norm(val), []).append((name, fname))

    print("=" * 72)
    print("SOUL AUGMENT / PROC VALIDATOR")
    print(f"  .arz             : {arz_path}")
    print(f"  records total    : {len(recset)}")
    print(f"  soul records     : {len(souls)}")
    print(f"  skill refs check : {refs_checked}")
    print(f"  DANGLING refs    : {len(dangling)}")
    print("=" * 72)

    if dangling:
        print("\nFAIL - the following soul skill references do NOT resolve to a")
        print("record in the .arz (the granted skill silently does nothing):\n")
        for dead in sorted(dangling):
            users = sorted(set(dangling[dead]))
            print(f"[DANGLING] {dead}   ({len(users)} soul field(s))")
            for soul, field in users:
                print(f"    {soul}  <{field}>")
            print()
        return 1

    print("\nPASS - every soul augment / proc / item-skill reference resolves.")
    return 0


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        print("ERROR: expected exactly one argument (the final .arz path).")
        return 2
    arz = Path(argv[1])
    if not arz.is_file():
        print(f"ERROR: .arz not found: {arz}")
        return 2
    return validate(arz)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
