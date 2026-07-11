r"""Verify Pygmalion replicate per-tier registration in the built arz (P3-1):
pygmalion_1/2/3 must carry replicate in an AI-fired special slot AND register it at
skillLevel 1/2/3 respectively (so replicate.petLimit=3;4;5 indexes to 3/4/5).
Also spot-check a couple of kit skills' per-tier levels. usage: py pygmalion_verify.py <arz>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase  # noqa: E402

AI = ('attackSkillName', 'specialAttackSkillName', 'specialAttack2SkillName',
      'specialAttack3SkillName', 'specialAttack4SkillName', 'specialAttack5SkillName')


def main(arz):
    db = ArzDatabase.from_arz(Path(arz))
    names = {n.replace('/', '\\').lower(): n for n in db.record_names()}
    for tier in (1, 2, 3):
        p = names.get((r'records\skills\soulskills\pets\pygmalion_%d.dbr' % tier).lower())
        print("=" * 60)
        print("pygmalion_%d ->" % tier, 'FOUND' if p else 'MISSING')
        if not p:
            continue
        # which AI slot holds replicate?
        slot_hit = None
        for s in AI:
            v = db.get_field_value(p, s)
            v0 = (v[0] if isinstance(v, list) else v) or ''
            if 'replicate' in str(v0).lower():
                slot_hit = (s, v0)
        print("  replicate AI-slot:", slot_hit)
        # its registered level
        for i in range(1, 25):
            sn = db.get_field_value(p, 'skillName%d' % i)
            sn0 = (sn[0] if isinstance(sn, list) else sn) or ''
            if 'replicate' in str(sn0).lower():
                lv = db.get_field_value(p, 'skillLevel%d' % i)
                print(f"  registered: skillName{i}={sn0} skillLevel{i}={lv}")
        # confirm no buffSelf residue holds replicate
        for s in ('buffSelfSkillName', 'buffSelf2SkillName'):
            v = db.get_field_value(p, s)
            v0 = (v[0] if isinstance(v, list) else v) or ''
            if v0:
                print(f"  (buff slot {s}={v0})")


if __name__ == '__main__':
    main(sys.argv[1])
