r"""Build gate (Mastery Wave 1, doc MASTERY_AUDIT_2026-07-09 section 4-A):
every CASTABLE player skill in every mastery tree must have a
skillSpecialAnimationName that is EMPTY or present in the PC animation tables.

Root problem this guards against (hard-law #2 / B-SOUL-PROC-2, Game.dll
SkillManager::StartSkill): a cast whose skillSpecialAnimationName the caster's
animation table cannot start ABORTS silently. The SV port grafted monster-only
or dropped anim tokens onto three player nukes (Earth Meteor 'MeteorShower',
Storm Thunderball 'Ensnare', Spirit Bonespire 'BoneSpire') and the mod's
overridden PC anim tables dropped tokens that Neidan/RuneMaster actives name
('Ensnare', 'Flamesurge', 'Barrage', ...). The certified detection logic lived
in validate_soul_augments.py but was scoped to SOULS only, so the mastery
trees shipped broken. This gate closes that hole.

LAW (per the coordinator's directive): FAIL on any castable tree-slot skill
whose non-empty skillSpecialAnimationName is ABSENT FROM BOTH PC anim tables
(any weapon row of either table counts as present). Two inert classes are
reported as INFO, not failed, because they are never cast directly so their
anim field cannot abort anything: modifier records (Class containing
'Modifier'/'Secondary', e.g. Neidan's unattached 'Splash' naming
'PhantomStrike') and passives (Class starting 'Skill_Passive', e.g. the two
Dream passives that ship the literal-'0' token).

Presence-in-one-row is deliberately weaker than the soul gate's UNIVERSAL law:
mastery skills are legitimately weapon-gated (Heave = mace rows only), so
per-row presence cannot be asserted without each skill's weapon mask. Absent
from every row of both tables = provably never castable = the shippable law.

RESOLUTION MODEL: trees 11 (RuneMaster) and 12 (Neidan) resolve from the BASE
game arz, not the mod - pass the base arz as the second argument (or base_db
to check_db) for full coverage; without it those trees are skipped LOUDLY.
The PC anim tables themselves are mod-authored and always read from the mod.

Usage:
  py tools/validate_player_skill_anims.py <final.arz> [<base_game.arz>]
  from validate_player_skill_anims import check_db          # in-build gate

Exit codes: 0 = pass, 1 = violations, 2 = input error.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

PC_RECORD = 'records\\xpack\\creatures\\pc\\malepc01.dbr'
PC_ANM_TABLES = (
    'records\\creature\\pc\\anm\\anm_malepc01.dbr',
    'records\\creature\\pc\\anm\\anm_femalepc.dbr',
)
MAX_TREES = 12
MAX_SLOTS = 40


def _norm(p):
    return str(p).replace('/', '\\').lower().strip()


def _field(db, rec, name):
    fl = db.get_fields(rec)
    if not fl:
        return None
    for k, tf in fl.items():
        if k.split('###')[0] == name and tf.values:
            return tf.values
    return None


def _anim_token_union(db, recmap):
    """Every SpecialAnimRef value present in ANY weapon row of EITHER PC
    animation table (lowercased). None if a table is missing."""
    union = set()
    for tbl in PC_ANM_TABLES:
        rec = recmap.get(_norm(tbl))
        if not rec:
            print(f'  ERROR: PC animation table missing from the .arz: {tbl}')
            return None
        for k, tf in (db.get_fields(rec) or {}).items():
            if re.match(r'.+?SpecialAnimRef\d+$', k.split('###')[0]) \
                    and tf.values and str(tf.values[0]).strip():
                union.add(str(tf.values[0]).strip().lower())
    return union


def check_db(db, base_db=None, fail=True):
    """Core gate. Returns the list of violations; raises SystemExit when
    fail=True and violations exist. base_db extends record resolution to the
    base game (needed for the RuneMaster/Neidan trees)."""
    recmap = {_norm(n): n for n in db.record_names()}
    base_map = {_norm(n): n for n in base_db.record_names()} if base_db else {}
    tokens = _anim_token_union(db, recmap)
    if tokens is None:
        if fail:
            raise SystemExit('player-skill anim gate: PC anim tables missing')
        return [('<tables>', '<missing>', '')]

    def lookup(path):
        """(db_obj, real_name) with mod-first resolution, or (None, None)."""
        key = _norm(path)
        if key in recmap:
            return db, recmap[key]
        if key in base_map:
            return base_db, base_map[key]
        return None, None

    src, pc = lookup(PC_RECORD)
    if not pc:
        if fail:
            raise SystemExit('player-skill anim gate: malepc01.dbr missing')
        return [('<pc>', '<missing>', '')]

    violations = []
    info = []
    checked = 0
    skipped_trees = []
    for t in range(1, MAX_TREES + 1):
        tree_v = _field(src, pc, f'skillTree{t}')
        if not tree_v or not str(tree_v[0]).strip():
            continue
        tdb, tree = lookup(tree_v[0])
        if not tree:
            skipped_trees.append(str(tree_v[0]))
            continue
        for s in range(1, MAX_SLOTS + 1):
            slot_v = _field(tdb, tree, f'skillName{s}')
            if not slot_v or not str(slot_v[0]).strip():
                continue
            sdb, skill = lookup(slot_v[0])
            if not skill:
                continue  # dangling tree slots are another gate's business
            anim_v = _field(sdb, skill, 'skillSpecialAnimationName')
            anim = str(anim_v[0]).strip() if anim_v else ''
            if not anim:
                continue
            checked += 1
            cls_v = _field(sdb, skill, 'Class')
            cls = str(cls_v[0]) if cls_v else ''
            if anim.lower() in tokens:
                continue
            low = cls.lower()
            if 'modifier' in low or 'secondary' in low \
                    or low.startswith('skill_passive'):
                info.append((skill, anim, cls))
            else:
                violations.append((skill, anim, cls))
    if skipped_trees:
        print(f'  WARNING: {len(skipped_trees)} skill tree(s) did not resolve '
              f'(pass the base game arz for full coverage): '
              f'{", ".join(skipped_trees)}')

    for skill, anim, cls in info:
        print(f'  INFO (modifier, never cast directly): {skill} '
              f':: anim {anim!r} not in the PC tables ({cls})')
    if violations:
        for skill, anim, cls in violations:
            print(f'  PLAYER-SKILL-ANIM FAIL: {skill} :: '
                  f"skillSpecialAnimationName={anim!r} absent from BOTH PC "
                  f'anim tables ({cls}) -> cast ABORTS (hard-law #2)')
        if fail:
            raise SystemExit(
                f'Player-skill anim gate FAILED on {len(violations)} '
                f'skill(s); this build does not ship (Mastery Wave 1 gate)')
    else:
        print(f'  Player-skill anim gate: PASS '
              f'({checked} anim-carrying tree skills checked, '
              f'{len(info)} inert modifier note(s))')
    return violations


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    db = ArzDatabase.from_arz(Path(sys.argv[1]))
    base_db = None
    if len(sys.argv) > 2 and Path(sys.argv[2]).is_file():
        base_db = ArzDatabase.from_arz(Path(sys.argv[2]))
    violations = check_db(db, base_db=base_db, fail=False)
    return 1 if violations else 0


if __name__ == '__main__':
    sys.exit(main())
