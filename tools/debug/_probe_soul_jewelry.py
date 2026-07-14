"""Print the jewelry bitmap + granted-skill icon for a set of soul base names."""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from arz_patcher import ArzDatabase

NAMES = sys.argv[2:]  # base names like blood_toxeus, enslaver, phagia


def field0(fields, name):
    if not fields:
        return None
    for key, tf in fields.items():
        if key.split('###')[0] == name and tf.values and str(tf.values[0]).strip():
            return str(tf.values[0])
    return None


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))
    names = list(db.record_names())
    low = {n.lower(): n for n in names}

    def resolve(ref):
        r = (ref or '').replace('/', '\\').lower()
        return low.get(r)

    for base in NAMES:
        print(f"\n### {base}")
        for tier in ('n', 'e', 'l'):
            key = None
            for n in names:
                nl = n.lower()
                if (f'\\{base}_soul_{tier}.dbr' in nl or nl.endswith(f'\\{base}_soul_{tier}.dbr')) \
                        and 'equipmentring\\soul' in nl:
                    key = n
                    break
            if not key:
                continue
            f = db.get_fields(key)
            bitmap = field0(f, 'bitmap')
            isk = field0(f, 'itemSkillName')
            up = None
            sk = resolve(isk)
            if sk:
                up = field0(db.get_fields(sk), 'skillUpBitmapName')
            print(f"  [{tier}] jewelry bitmap = {bitmap}")
            print(f"      itemSkillName   = {isk}")
            print(f"      skill up icon   = {up}")


if __name__ == '__main__':
    main()
