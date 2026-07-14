"""B40 READ-ONLY FX RCA: enumerate EVERY FX-relevant field on the Enslaver family
and chase referenced skills to find every GREEN-producing FX source.

Usage: py tools/debug/b40_probe_enslaver_fx.py <arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

# Monster records + donors + FX paks of interest.
MONSTERS = [
    (r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr', 'ENSLAVER BOSS (fix target)'),
    (r'records\creature\monster\shadowstalker\um_enslaver_marauder_99.dbr', 'ENSLAVER MARAUDER (summoned; fix target)'),
    (r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr', 'DEVOURER (crimson; PRESERVE, comparison)'),
    (r'records\xpack\creatures\monster\skeleton\um_toxeus_99.dbr', 'SKELETON DONOR (boss clones this)'),
    (r'records\creature\monster\shadowstalker\am_deathstalker_55_ambush.dbr', 'MARAUDER RIG DONOR'),
]
# also try the Athens green Toxeus (reference for the original green)
EXTRA_MONSTERS = [
    r'records\xpack\creatures\monster\skeleton\um_toxeus_21.dbr',
    r'records\creature\monster\skeleton\um_toxeus_21.dbr',
]

FX_PAKS = [
    r'records\skills\monster skills\buff_self\svc_enslaver_darksmoke_charfxpak.dbr',
    r'records\drxcreatures\bloodwitch\skills\skilleffects\charfxpak_leinth_aura.dbr',
    r'records\effects\custom\343_dark_smoke.dbr',
    r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx_pak.dbr',
]

# value substrings that flag a GREEN/poison FX asset
GREEN_HINT = ('green', 'grean', 'poison', 'toxic', 'plague', 'acid', 'envenom',
              'revenantpoison', 'nature', 'venom')
# field-name substrings that indicate an FX / visual field
FX_FIELD_HINT = ('fx', 'pak', 'particle', 'effect', 'mesh', 'texture', 'skin',
                 'initialskill', 'skillname', 'attackskill', 'bloodcolor',
                 'glow', 'aura', 'petskill', 'shroud')


def norm(p):
    return str(p).replace('/', '\\').lower().strip()


def resolve(db, path):
    want = norm(path)
    for n in db.record_names():
        if norm(n) == want:
            return n
    return None


def flag_green(vals):
    for v in vals:
        if isinstance(v, str) and any(h in v.lower() for h in GREEN_HINT):
            return True
    return False


def dump_fx_fields(db, rec, label=''):
    real = resolve(db, rec)
    print(f"\n===== {rec}")
    if label:
        print(f"      [{label}]")
    if not real:
        print("  *** NOT PRESENT in arz ***")
        return None
    f = db.get_fields(real)
    print(f"  Class/tpl: {db._record_types.get(real)}")
    fx_refs = []
    for key, tf in f.items():
        base = key.split('###')[0]
        vals = tf.values or []
        is_fx = any(h in base.lower() for h in FX_FIELD_HINT)
        green = flag_green(vals)
        if is_fx or green:
            mark = '  <<< GREEN' if green else ''
            print(f"    {base:34s} = {vals}{mark}")
            for v in vals:
                if isinstance(v, str) and v.lower().endswith('.dbr'):
                    fx_refs.append((base, v))
    return fx_refs


def dump_full(db, rec):
    """Dump ALL fields of a (usually skill/pak) record."""
    real = resolve(db, rec)
    print(f"\n----- FULL: {rec}")
    if not real:
        print("  *** NOT PRESENT ***")
        return
    f = db.get_fields(real)
    print(f"  Class/tpl: {db._record_types.get(real)}")
    for key, tf in f.items():
        base = key.split('###')[0]
        vals = tf.values or []
        green = flag_green(vals)
        mark = '  <<< GREEN' if green else ''
        print(f"    {base:34s} = {vals}{mark}")


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        'work/SoulvizierClassic/Database/SoulvizierClassic.arz'
    db = ArzDatabase.from_arz(Path(arz))
    print(f"ARZ: {arz}  ({len(db.record_names())} records)")

    all_skill_refs = set()
    print("\n############ MONSTER RECORDS: FX-relevant fields ############")
    for rec, label in MONSTERS:
        refs = dump_fx_fields(db, rec, label)
        if refs:
            for fld, v in refs:
                all_skill_refs.add(v)
    for rec in EXTRA_MONSTERS:
        if resolve(db, rec):
            dump_fx_fields(db, rec, 'ATHENS GREEN TOXEUS (reference)')

    print("\n\n############ FX PAK / SMOKE RECORDS (full dump) ############")
    for p in FX_PAKS:
        dump_full(db, p)

    # chase every skill referenced by the two fix-target monsters, dump their FX fields
    print("\n\n############ SKILLS referenced by Enslaver+Marauder: FX fields ############")
    for skref in sorted(all_skill_refs):
        real = resolve(db, skref)
        if not real:
            print(f"\n----- {skref}  *** UNRESOLVED ***")
            continue
        f = db.get_fields(real)
        cls = db._record_types.get(real)
        # collect any FX-ish field or green value
        rows = []
        for key, tf in f.items():
            base = key.split('###')[0]
            vals = tf.values or []
            is_fx = any(h in base.lower() for h in FX_FIELD_HINT)
            green = flag_green(vals)
            if is_fx or green:
                rows.append((base, vals, green))
        green_here = any(g for _, _, g in rows)
        tag = '  <<< HAS GREEN VALUE' if green_here else ''
        print(f"\n----- {skref}  ({cls}){tag}")
        for base, vals, green in rows:
            mark = '  <<< GREEN' if green else ''
            print(f"    {base:34s} = {vals}{mark}")


if __name__ == '__main__':
    main()
