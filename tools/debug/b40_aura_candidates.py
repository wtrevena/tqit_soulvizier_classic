"""Dump candidate persistent-aura CharFxPaks + their Effect boneLists, plus the
envenom-buff donor, to pick a full-body dark shroud + build the aura buff safely."""
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


def dump(db, rec, chase=True, seen=None):
    if seen is None:
        seen = set()
    real = resolve(db, rec)
    print(f"\n----- {rec}")
    if not real:
        print("  *** NOT PRESENT ***")
        return
    if real in seen:
        print("  (already dumped)")
        return
    seen.add(real)
    f = db.get_fields(real)
    print(f"  Class/tpl: {db._record_types.get(real)}")
    refs = []
    for key, tf in f.items():
        b = key.split('###')[0]
        print(f"    {b:30s} = {tf.values}")
        for v in (tf.values or []):
            if isinstance(v, str) and v.lower().endswith('.dbr'):
                refs.append(v)
    if chase:
        for r in refs:
            dump(db, r, chase=False, seen=seen)


def main():
    arz = sys.argv[1]
    db = ArzDatabase.from_arz(Path(arz))
    print("################ Devourer aura (full-body reference) ################")
    dump(db, r'records\drxcreatures\bloodwitch\skills\skilleffects\charfxpak_leinth_aura.dbr')

    print("\n\n################ candidate dark/shadow full-body shroud paks ################")
    for r in [
        r'records\xpack\effects\boss effects\hades2_shadowcloud_charfxpak.dbr',
        r'records\skills\monster skills\buff_self\svc_ashsmoke_charfxpak.dbr',
        r'records\skills\monster skills\buff_self\svc_enslaver_darksmoke_charfxpak.dbr',
    ]:
        dump(db, r)

    print("\n\n################ envenom-buff donor (build the aura buff from this) ################")
    for r in [
        r'records\skills\monster skills\buff_self\bloodtoxeus_envenomweapon.dbr',
        r'records\skills\monster skills\buff_self\toxeus_envenomweapon.dbr',
    ]:
        dump(db, r, chase=False)


if __name__ == '__main__':
    main()
