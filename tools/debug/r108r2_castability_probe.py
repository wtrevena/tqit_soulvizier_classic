r"""INDEPENDENT castability probe for the six Guardians of the General (R-100 #18).

Deliberately duplicated rather than imported: `general_guardians.verify()` proves
the invariant using the module's own helpers, so a bug in those helpers would
make the module agree with itself. This file re-derives everything from a bare
`ArzDatabase` read of a BUILT `.arz` - no lane code in the loop, no expected-value
table - and answers ONE question per cast slot:

    can this creature actually PLAY the special animation this skill names?

MECHANISM (this repo's crash-law RE; the b42 Ephialtes Dread Nova fix rests on
the same finding): Game.dll's `SkillManager::StartSkill` aborts the cast SILENTLY
when the caster's animation table declares no clip matching the skill's
`skillSpecialAnimationName`. A creature's table is whatever its own
`charAnimationTableName` points at, and the engine reads `<row>SpecialAnimRef1..15`
(disasm va 0x1025622a, the same bound `_pc_universal_special_anims` uses).

An empty/absent `skillSpecialAnimationName` is always fine: the cast then rides
the default attack clip, which every rig has.

usage:  py tools/debug/r108r2_castability_probe.py <built.arz>
exit 0 = every cast slot on all six Guardians can fire; exit 1 = at least one cannot.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from arz_patcher import ArzDatabase  # noqa: E402

ANIM_IDX_CAP = 15
GUARDS = [r'records\xpack\creatures\monster\machae\svc_general_%s_guard%d.dbr' % (g, i)
          for g in ('a', 'b', 'c') for i in (1, 2)]
GENERALS = [r'records\xpack\creatures\monster\machae\xsq27_namedhero_%s_machae_%d.dbr' % (g, n)
            for g in ('a', 'b', 'c') for n in (45, 47)]


def main(argv):
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    db = ArzDatabase.from_arz(Path(argv[0]))
    recmap = {n.replace('/', '\\').lower(): n for n in db.record_names()}

    def R(p):
        return recmap.get(str(p).replace('/', '\\').strip().lower()) if p else None

    def fields(r):
        return db.get_fields(r) or {}

    def s(r, name):
        if not r:
            return None
        for k, tf in fields(r).items():
            if k.split('###')[0] == name and tf.values:
                return str(tf.values[0])
        return None

    def clips(monster):
        tbl = R(s(monster, 'charAnimationTableName'))
        if not tbl:
            return None, None
        out = set()
        for k, tf in fields(tbl).items():
            m = re.match(r'(.+?)SpecialAnimRef(\d+)$', k.split('###')[0])
            if m and int(m.group(2)) <= ANIM_IDX_CAP and tf.values \
                    and str(tf.values[0]).strip():
                out.add(str(tf.values[0]).strip().lower())
        return tbl, out

    def cast_slots(monster):
        out = set()
        for k, tf in fields(monster).items():
            f = k.split('###')[0]
            if not (re.fullmatch(r'skillName\d+', f)
                    or re.fullmatch(r'specialAttack\d*SkillName', f)):
                continue
            for v in (tf.values or []):
                if isinstance(v, str) and v.strip():
                    out.add((f, v.strip()))
        return sorted(out)

    print('ARZ: %s' % argv[0])
    total = dead = 0
    for path in GUARDS + GENERALS:
        rec = R(path)
        role = 'GUARD' if path in GUARDS else 'general (read-only cross-check)'
        if not rec:
            print('\n=== %s : ABSENT ===' % path)
            dead += 1
            continue
        tbl, cl = clips(rec)
        print('\n=== %s   [%s] ===' % (path.split('\\')[-1], role))
        print('    charAnimationTableName -> %s' % (tbl or 'UNRESOLVED'))
        print('    clips it can play      : %s'
              % (', '.join(sorted(cl)) if cl else '(none)'))
        for slot, skill in cast_slots(rec):
            sk = R(skill)
            if not sk:
                print('    [MISSING ] %-24s %s' % (slot, skill))
                dead += 1
                continue
            anim = s(sk, 'skillSpecialAnimationName')
            total += 1
            if not anim or not anim.strip():
                print('    [CAN FIRE] %-24s %-46s no special anim -> default attack clip'
                      % (slot, skill.split('\\')[-1]))
                continue
            ok = cl is not None and anim.strip().lower() in cl
            if not ok:
                dead += 1
            print('    [%s] %-24s %-46s anim %r %s'
                  % ('CAN FIRE' if ok else '  DEAD  ', slot, skill.split('\\')[-1],
                     anim, 'IS declared' if ok else 'is NOT declared'))

    print('\n%s' % ('=' * 78))
    print('%d cast slot(s) inspected; %d CANNOT FIRE.' % (total, dead))
    print('RESULT: %s' % ('PASS' if dead == 0 else 'FAIL'))
    return 1 if dead else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
