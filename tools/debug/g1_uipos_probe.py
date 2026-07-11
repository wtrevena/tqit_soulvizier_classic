"""G1 UI-position probe (LANE B, read-only): dump every occupied skill-slot grid
cell (bitmapPositionX/Y + isCircular) for the mastery UI folders the graft
touches, so new buttons land on FREE cells (no overlap). Warfare=ingameui M1,
Defense=M2, Earth=M3, Storm=M4, Nature=ingameui M8, Dream=xpack M9.

Usage: py tools/debug/g1_uipos_probe.py [our_arz]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

OUR = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz"


def norm(s):
    return s.replace('/', '\\').lower().strip()


def gv(db, name, f):
    v = db.get_field_value(name, f)
    return (v[0] if isinstance(v, list) and v else v)


def main():
    our = ArzDatabase.from_arz(Path(OUR))
    m = {norm(n): n for n in our.record_names()}
    # (label, folder-prefix)
    folders = [
        ('Warfare', r'records\ingameui\player skills\mastery 1'),
        ('Defense', r'records\ingameui\player skills\mastery 2'),
        ('Earth',   r'records\ingameui\player skills\mastery 3'),
        ('Storm',   r'records\ingameui\player skills\mastery 4'),
        ('Nature',  r'records\ingameui\player skills\mastery 8'),
        ('Dream',   r'records\xpack\ui\skills\mastery 9'),
    ]
    for label, base in folders:
        print(f"\n=== {label}  ({base}) ===")
        cells = []
        for si in range(1, 40):
            n = m.get(norm(r'%s\skill%02d.dbr' % (base, si)))
            if not n:
                continue
            x = gv(our, n, 'bitmapPositionX')
            y = gv(our, n, 'bitmapPositionY')
            circ = gv(our, n, 'isCircular')
            cells.append((si, x, y, circ))
        # group by column (x), list y's occupied
        for si, x, y, circ in cells:
            print(f"   skill{si:02d}: X={x:>4} Y={y:>4} circ={circ}")
        xs = sorted(set(c[1] for c in cells if c[1] is not None))
        print(f"   -> columns(X) used: {xs}")
        # per-column occupied Ys
        for xx in xs:
            ys = sorted(c[2] for c in cells if c[1] == xx and c[2] is not None)
            print(f"      X={xx}: Ys={ys}")


if __name__ == '__main__':
    main()
