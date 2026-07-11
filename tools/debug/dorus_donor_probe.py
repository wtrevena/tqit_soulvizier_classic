r"""Probe the Dorus donor's skill slots + attackSkillName (A5 curiosity: is
skillName6=boss_conversionimmunity a true duplicate of an existing donor slot,
and what melee does the king inherit). usage: py dorus_donor_probe.py <arz>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase  # noqa: E402

DONOR = r'records\xpack\creatures\monster\lostsoul\xsq06_king_dorus_41.dbr'
RAV = r'records\skills\spirit\drxdeathchillaura_ravagesoftime.dbr'


def main(arz):
    db = ArzDatabase.from_arz(Path(arz))
    names = {n.replace('/', '\\').lower(): n for n in db.record_names()}
    real = names.get(DONOR.lower())
    print("DONOR", real)
    if real:
        for f in ['attackSkillName'] + [f'skillName{i}' for i in range(1, 21)]:
            v = db.get_field_value(real, f)
            if v and str(v[0] if isinstance(v, list) else v).strip():
                lv = db.get_field_value(real, f.replace('skillName', 'skillLevel')) if f.startswith('skillName') else None
                print(f"  {f:14s} = {v}    {('lvl=' + str(lv)) if lv else ''}")
    # is Ravages of Time present + what class (augment validity)?
    rr = names.get(RAV.lower())
    print("\nRavages of Time:", rr)
    if rr:
        print("  Class:", db.get_field_value(rr, 'Class'))
        print("  templateName:", db.get_field_value(rr, 'templateName'))


if __name__ == '__main__':
    main(sys.argv[1])
