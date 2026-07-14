"""B40 READ-ONLY: full field dump of the Enslaver boss + its equipment/aura chain
to pin the boss's residual green."""
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
    print(f"\n===== {rec}")
    if not real:
        print("  *** NOT PRESENT ***")
        return
    f = db.get_fields(real)
    print(f"  Class: {db._record_types.get(real)}")
    for key, tf in f.items():
        base = key.split('###')[0]
        if only and not any(k in base.lower() for k in only):
            continue
        print(f"    {base:32s} = {tf.values}")


def main():
    arz = sys.argv[1]
    db = ArzDatabase.from_arz(Path(arz))
    BOSS = r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
    print("################ ENSLAVER BOSS: equipment/loot/weapon fields ################")
    dump(db, BOSS, only=['loot', 'weapon', 'equip', 'hand', 'chance', 'item', 'bitmap',
                         'skin', 'glow', 'blood', 'petskill', 'controller'])

    print("\n\n################ speedall aura chain (persistent BuffRadiusToggled) ################")
    for r in [
        r'records\skills\monster skills\auras\character_speedall.dbr',
        r'records\skills\monster skills\auras\character_speedallbuff.dbr',
    ]:
        dump(db, r)

    print("\n\n################ chainInitialSkill: phantomstrike (persistent?) ################")
    dump(db, r'records\xpack\skills\dream\phantomstrike.dbr')

    # what weapons does um_toxeus_99 donor equip? (boss inherits its loadout)
    print("\n\n################ DONOR um_toxeus_99: equipment/loot/weapon fields ################")
    dump(db, r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr',
         only=['loot', 'weapon', 'equip', 'hand', 'chance', 'item'])


if __name__ == '__main__':
    main()
