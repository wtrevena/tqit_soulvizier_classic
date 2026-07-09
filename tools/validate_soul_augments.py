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



# Template path of a skill auto-cast controller (controllers carry NO Class
# field, so template identity is the check).
_CTRL_TEMPLATE = 'database\\templates\\skillautocastcontroller.tpl'

# The shipped PC animation tables (SV 0.98i's own). B-SOUL-PROC-2: Game.dll
# SkillManager::StartSkill ABORTS a cast whose skillSpecialAnimationName the
# caster's table cannot start ("Animation failed to start in
# SkillManager::StartSkill", string va 0x1035c3b0, gate at va 0x102561d4), so
# a soul-granted skill is reliably castable only when its special anim is
# EMPTY or present in EVERY weapon row of BOTH tables.
_PC_ANM_TABLES = (
    'records\\creature\\pc\\anm\\anm_malepc01.dbr',
    'records\\creature\\pc\\anm\\anm_femalepc.dbr',
)


def _pc_universal_anims(db, recmap):
    import re
    universal = None
    for tbl in _PC_ANM_TABLES:
        rec = recmap.get(_norm(tbl))
        if not rec:
            print(f"ERROR: PC animation table missing from .arz: {tbl}")
            return None
        rows = {}
        for key, tf in (db.get_fields(rec) or {}).items():
            fname = key.split('###')[0]
            m = re.match(r'(.+?)SpecialAnimRef(\d+)$', fname)
            if m and tf.values and str(tf.values[0]).strip():
                rows.setdefault(m.group(1), set()).add(str(tf.values[0]).lower())
        for names in rows.values():
            universal = set(names) if universal is None else (universal & names)
    return universal or set()


def validate(arz_path):
    db = ArzDatabase.from_arz(Path(arz_path))

    # Full normalized resolution map of every record name in the .arz.
    recmap = {_norm(n): n for n in db.record_names()}

    universal_anims = _pc_universal_anims(db, recmap)
    if universal_anims is None:
        return 2

    def resolves(path):
        return _norm(path) in recmap

    def field_of(rec, name):
        ff = db.get_fields(rec)
        if not ff:
            return None
        for key, tf in ff.items():
            if key.split('###')[0] == name and tf.values:
                return tf.values
        return None

    souls = [n for n in db.record_names() if is_soul_record(n)]

    dangling = {}          # dead_path -> [(soul, field), ...]
    inactive = []          # (soul, reason) - B-SOUL-PROC-1 activation-chain problems
    refs_checked = 0
    grants_checked = 0
    for name in souls:
        # Skip the few Monster records parked under soul\test\ paths.
        if db._record_types.get(name) == 'Monster':
            continue
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

        # ── B-SOUL-PROC-1 activation-chain checks: a RESOLVING grant can still
        # be a silent no-op. A granted item skill instantiates at
        # itemSkillLevel; absent or 0 = level-0 = INACTIVE (the tooltip renders
        # 'Grants Skill' but the auto-controller has nothing castable - the
        # Crommyonian Sow bug, 219 souls). Also verify the granted record is a
        # real Skill_* and the controller is a live SkillAutoCastController. ──
        isn = field_of(name, 'itemSkillName')
        if isn and str(isn[0]).strip():
            grants_checked += 1
            skill_path = str(isn[0]).strip()
            skill_rec = recmap.get(_norm(skill_path))
            if skill_rec:
                cls = field_of(skill_rec, 'Class')
                if not cls or not str(cls[0]).startswith('Skill_'):
                    inactive.append((name, f"itemSkillName is not a Skill_* record "
                                           f"(Class={cls[0] if cls else None}): "
                                           f"{skill_path}"))
                # B-SOUL-PROC-2: castability - the special anim must be empty
                # or universally playable, or StartSkill aborts the cast.
                anim = field_of(skill_rec, 'skillSpecialAnimationName')
                if anim and str(anim[0]).strip() and \
                        str(anim[0]).lower() not in universal_anims:
                    inactive.append((name,
                                     f"granted skill {skill_path} carries special "
                                     f"anim '{anim[0]}' NOT universally playable "
                                     f"by the PC (SkillManager::StartSkill aborts "
                                     f"the cast; B-SOUL-PROC-2)"))
            lvl = field_of(name, 'itemSkillLevel')
            if lvl is None:
                inactive.append((name, "itemSkillLevel ABSENT (granted skill "
                                       "instantiates at level 0 = inactive, "
                                       "never procs)"))
            elif int(lvl[0]) < 1:
                inactive.append((name, f"itemSkillLevel == {int(lvl[0])} "
                                       f"(level-0 grant = inactive, never procs)"))
            ctl = field_of(name, 'itemSkillAutoController')
            if ctl and str(ctl[0]).strip():
                ctl_rec = recmap.get(_norm(str(ctl[0])))
                if ctl_rec:  # unresolved controllers already reported as dangling
                    tpl = field_of(ctl_rec, 'templateName')
                    if not tpl or _norm(str(tpl[0])) != _CTRL_TEMPLATE:
                        inactive.append((name, f"controller {ctl[0]} has wrong "
                                               f"template {tpl[0] if tpl else None}"))
                    chance = field_of(ctl_rec, 'chanceToRun')
                    if not chance or float(chance[0]) <= 0:
                        inactive.append((name, f"controller {ctl[0]} chanceToRun "
                                               f"{chance[0] if chance else None} "
                                               f"(never fires)"))
                    trig = field_of(ctl_rec, 'triggerType')
                    if not trig or not str(trig[0]).strip():
                        inactive.append((name, f"controller {ctl[0]} has empty "
                                               f"triggerType"))
                    # B-SOUL-PROC-2: Enemy-targeted controllers need a target
                    # acquisition radius (base concrete controllers: 10-15).
                    tt = field_of(ctl_rec, 'targetType')
                    if tt and str(tt[0]) == 'Enemy':
                        rad = field_of(ctl_rec, 'autoTargetRadius')
                        if not rad or float(rad[0]) < 1.0:
                            inactive.append((name,
                                             f"Enemy controller {ctl[0]} has "
                                             f"autoTargetRadius "
                                             f"{rad[0] if rad else 'ABSENT'} "
                                             f"(no target acquisition; "
                                             f"B-SOUL-PROC-2)"))

    print("=" * 72)
    print("SOUL AUGMENT / PROC VALIDATOR")
    print(f"  .arz             : {arz_path}")
    print(f"  records total    : {len(recmap)}")
    print(f"  soul records     : {len(souls)}")
    print(f"  skill refs check : {refs_checked}")
    print(f"  granted-skill souls (activation-chain checked): {grants_checked}")
    print(f"  DANGLING refs    : {len(dangling)}")
    print(f"  INACTIVE grants  : {len(inactive)}")
    print("=" * 72)

    ok = True
    if dangling:
        ok = False
        print("\nFAIL - the following soul skill references do NOT resolve to a")
        print("record in the .arz (the granted skill silently does nothing):\n")
        for dead in sorted(dangling):
            users = sorted(set(dangling[dead]))
            print(f"[DANGLING] {dead}   ({len(users)} soul field(s))")
            for soul, field in users:
                print(f"    {soul}  <{field}>")
            print()

    if inactive:
        ok = False
        print("\nFAIL - the following souls grant a skill whose ACTIVATION chain is")
        print("broken (resolves, but can never actually proc - B-SOUL-PROC-1):\n")
        for soul, why in inactive:
            print(f"[INACTIVE] {soul}")
            print(f"    {why}\n")

    if not ok:
        return 1

    print("\nPASS - every soul augment / proc / item-skill reference resolves "
          "and every granted skill's activation chain is live.")
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
