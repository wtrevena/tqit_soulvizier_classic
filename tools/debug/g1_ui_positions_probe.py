"""Dump existing UI skill-slot bitmap positions per mastery folder (to pick
non-overlapping cells for the G1 grafts) + dreamcopypet skillName* (difficulty
scaling remap check). Read-only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

OUR = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz"
SVAERA = r"C:/Program Files (x86)/Steam/steamapps/workshop/content/475150/2076433374/SVAERA_customquest/Database/SVAERA_customquest.arz"


def norm(s):
    return s.replace('/', '\\').lower().strip()


def gv(db, name, f):
    v = db.get_field_value(name, f)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def main():
    our = ArzDatabase.from_arz(Path(OUR))
    om = {norm(n): n for n in our.record_names()}
    for mi in (1, 2, 3, 4, 8, 9):
        print(f"\n=== mastery {mi} UI slot positions ===")
        for si in range(1, 40):
            key = norm(r'records\ingameui\player skills\mastery %d\skill%02d.dbr' % (mi, si))
            n = om.get(key)
            if not n:
                continue
            x = gv(our, n, 'bitmapPositionX')
            y = gv(our, n, 'bitmapPositionY')
            circ = gv(our, n, 'isCircular')
            skill = gv(our, n, 'skillName')
            print(f"  skill{si:02d}: X={x} Y={y} circ={circ}  -> {skill}")

    print("\n=== SVAERA dreamcopypet skillName* (difficulty scaling remap) ===")
    sv = ArzDatabase.from_arz(Path(SVAERA))
    sm = {norm(n): n for n in sv.record_names()}
    dn = sm.get(norm(r'records\xpack\skills\dream\pet\dreamcopypet.dbr'))
    if dn:
        fields = sv.get_fields(dn)
        for k, tf in fields.items():
            bk = k.split('###')[0]
            if bk.startswith('skillName') or bk.startswith('skillLevel'):
                print(f"  {bk} = {tf.values}")
    # does our base pet_difficultydamagescaling exist?
    print("\n=== our nightmare pet difficulty-scaling reference ===")
    for k, n in sm.items():
        if 'pet_difficultydamagescaling' in k:
            print(f"  (svaera has) {n}")


if __name__ == '__main__':
    main()
