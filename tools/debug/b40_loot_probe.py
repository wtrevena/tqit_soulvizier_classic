"""B40 READ-ONLY: boss-orb contents, marauder weapon slots, and reusable good
per-tier loot pools for the Enslaver hoard."""
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


def dump(db, rec, only=None):
    real = resolve(db, rec)
    print(f"\n----- {rec}")
    if not real:
        print("  *** NOT PRESENT ***")
        return None
    f = db.get_fields(real)
    print(f"  Class: {db._record_types.get(real)}")
    for key, tf in f.items():
        b = key.split('###')[0]
        if only and not any(k in b.lower() for k in only):
            continue
        v = tf.values
        if v and any(x not in (0, 0.0, '', None) for x in v):
            print(f"    {b:30s} = {v}")
    return f


def main():
    arz = sys.argv[1]
    db = ArzDatabase.from_arz(Path(arz))

    print("################ boss-orb chest (genericbossorb_04) ################")
    dump(db, r'records\item\containers\new\genericbossorb_04.dbr')

    print("\n\n################ marauder weapon/equip slots ################")
    dump(db, r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr',
         only=['righthand', 'lefthand', 'weapon', 'lootrighthand', 'lootlefthand',
               'chancetoequipright', 'chancetoequipleft', 'chancetoequipweapon'])

    print("\n\n################ marauder RIG DONOR weapon/equip slots ################")
    dump(db, r'records\creature\monster\shadowstalker\am_deathstalker_55_ambush.dbr',
         only=['righthand', 'lefthand', 'weapon', 'lootrighthand', 'lootlefthand',
               'chancetoequipright', 'chancetoequipleft'])

    print("\n\n################ Devourer lootMisc wiring (pattern reference) ################")
    dump(db, r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr',
         only=['lootmisc', 'chancetoequipmisc', 'treasureproxy'])

    # candidate good per-tier unique weapon loot pools (base game boss/hero drop pools)
    print("\n\n################ candidate good weapon/unique loot POOLS (exist? count) ################")
    cands = [
        r'records\item\loottables\weapons\unique\sword_n01.dbr',
        r'records\item\loottables\weapons\unique\sword_e01.dbr',
        r'records\item\loottables\weapons\unique\sword_l01.dbr',
        r'records\item\loottables\weapons\magical\sword_l01.dbr',
        r'records\item\loottables\09b_bosslootnormal.dbr',
        r'records\item\loottables\09b_bosslootepic.dbr',
        r'records\item\loottables\09b_bosslootlegendary.dbr',
    ]
    for c in cands:
        print(f"  {'OK ' if resolve(db, c) else 'NO '} {c}")

    # list some boss-loot master tables that exist (broad scan)
    print("\n  boss-loot-ish master tables present (sample):")
    n = 0
    for name in sorted(db.record_names()):
        nl = name.lower()
        if 'loottables' in nl and ('bossloot' in nl or 'heroloot' in nl or 'uniquedrop' in nl) and nl.endswith('.dbr'):
            print(f"    {name}")
            n += 1
            if n >= 30:
                break


if __name__ == '__main__':
    main()
