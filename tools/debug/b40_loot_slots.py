import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase


def norm(p):
    return str(p).replace('/', '\\').lower().strip()


def resolve(db, path):
    want = norm(path)
    for n in db.record_names():
        if norm(n) == want:
            return n
    return None


def main():
    db = ArzDatabase.from_arz(Path(sys.argv[1]))
    BOSS = resolve(db, r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr')
    f = db.get_fields(BOSS)
    print("### Enslaver boss lootMisc / chanceToEquipMisc slots (find FREE) ###")
    for i in range(1, 8):
        ce = db.get_field_value(BOSS, f'chanceToEquipMisc{i}')
        it = db.get_field_value(BOSS, f'lootMisc{i}Item1')
        print(f"  Misc{i}: chanceToEquip={ce!r}  lootMisc{i}Item1={it!r}")
    print(f"  Finger2 (soul): chance={db.get_field_value(BOSS,'chanceToEquipFinger2')} item1={db.get_field_value(BOSS,'lootFinger2Item1')}")
    print(f"  dropItems={db.get_field_value(BOSS,'dropItems')}")

    print("\n### candidate unique mastertable pools per tier (exist?) ###")
    fams = {
        'unique_1h (weapon)': r'records\xpack\item\loottables\weapons\mastertables\unique_1h_{t}01.dbr',
        'unique_2h (weapon)': r'records\xpack\item\loottables\weapons\mastertables\unique_2h_{t}01.dbr',
        'unique amulet': r'records\item\loottables\amulet\mastertables\unique\amulet_{t}01.dbr',
        'unique ring': r'records\item\loottables\finger\mastertables\unique\finger_{t}01.dbr',
        'unique ring2': r'records\item\loottables\ring\mastertables\unique\ring_{t}01.dbr',
        'unique torso': r'records\item\loottables\torso\mastertables\unique\torso_{t}01.dbr',
        'unique head': r'records\item\loottables\head\mastertables\unique\head_{t}01.dbr',
    }
    for label, tmpl in fams.items():
        row = []
        for t in ('n', 'e', 'l'):
            p = tmpl.format(t=t)
            row.append(('OK' if resolve(db, p) else 'NO') + f':{t}')
        print(f"  {label:22s} {row}   ({tmpl})")

    # broad scan: what unique mastertable dirs exist
    print("\n### sample of existing *mastertables*unique* weapon/jewelry pools ###")
    seen = set()
    for n in sorted(db.record_names()):
        nl = n.lower()
        if 'mastertables' in nl and 'unique' in nl and nl.endswith('_n01.dbr'):
            key = nl.rsplit('\\', 1)[0]
            if key not in seen:
                seen.add(key)
                print(f"  {n}")
            if len(seen) >= 25:
                break


if __name__ == '__main__':
    main()
