"""B40 READ-ONLY: settle the FX-resolution questions.
  1. Which charFxPak* FIELD NAMES do base-game MONSTER records use? (prove
     charFxPakSelfNames is a valid, persistent Monster field with precedent)
  2. What does drxshadowcloakrunning_fx resolve to (is it green)?
  3. What ShadowStalker skins / textures exist (for a black marauder skin)?
  4. Who else uses RevenantPoison.msh and with what skin? (mesh-green evidence)
  5. Dump 343_dark_smoke + the shadowcloak fx chain fully.
Usage: py tools/debug/b40_probe_fx_resolution.py <arz>
"""
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


def dump_full(db, rec):
    real = resolve(db, rec)
    print(f"\n----- FULL: {rec}")
    if not real:
        print("  *** NOT PRESENT ***")
        return
    f = db.get_fields(real)
    print(f"  Class/tpl: {db._record_types.get(real)}")
    for key, tf in f.items():
        print(f"    {key.split('###')[0]:32s} = {tf.values}")


def main():
    arz = sys.argv[1]
    db = ArzDatabase.from_arz(Path(arz))
    names = list(db.record_names())
    low = {n: norm(n) for n in names}

    # 1) charFxPak* field usage on Monster records
    print("############ 1. charFxPak* FIELD NAMES used on Monster records ############")
    from collections import Counter
    fieldcnt = Counter()
    self_examples = []
    for n in names:
        if db._record_types.get(n) != 'Monster':
            continue
        f = db.get_fields(n)
        if not f:
            continue
        for key, tf in f.items():
            base = key.split('###')[0]
            if base.lower().startswith('charfxpak'):
                fieldcnt[base] += 1
                if base.lower() == 'charfxpakselfnames' and len(self_examples) < 12:
                    self_examples.append((n, tf.values))
    for fld, c in fieldcnt.most_common():
        print(f"    {fld:32s} used on {c} Monster records")
    print("\n  Sample charFxPakSelfNames Monster users (proof of persistent-aura precedent):")
    for n, v in self_examples:
        print(f"    {n}\n        = {v}")

    # 2) shadowcloak fx chain
    print("\n\n############ 2. shadowcloak FX chain (marauder charFxPakRunningNames) ############")
    for r in [
        r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx_pak.dbr',
        r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx.dbr',
    ]:
        dump_full(db, r)

    # 3) ShadowStalker + deathstalker skins/textures referenced anywhere
    print("\n\n############ 3. ShadowStalker skins (baseTexture on shadowstalker-mesh monsters) ############")
    skins = Counter()
    for n in names:
        if db._record_types.get(n) != 'Monster':
            continue
        f = db.get_fields(n)
        if not f:
            continue
        mesh = None
        tex = None
        for key, tf in f.items():
            b = key.split('###')[0].lower()
            if b == 'mesh' and tf.values:
                mesh = str(tf.values[0])
            if b == 'basetexture' and tf.values:
                tex = str(tf.values[0])
        if mesh and 'shadowstalker' in mesh.lower():
            skins[tex or '(no baseTexture -> mesh default)'] += 1
    for tex, c in skins.most_common():
        print(f"    {c:4d} x  {tex}")

    # 4) RevenantPoison.msh users + their skins
    print("\n\n############ 4. RevenantPoison.msh users + baseTexture (mesh-green evidence) ############")
    rp = Counter()
    rp_examples = {}
    for n in names:
        if db._record_types.get(n) != 'Monster':
            continue
        f = db.get_fields(n)
        if not f:
            continue
        mesh = None
        tex = None
        for key, tf in f.items():
            b = key.split('###')[0].lower()
            if b == 'mesh' and tf.values:
                mesh = str(tf.values[0])
            if b == 'basetexture' and tf.values:
                tex = str(tf.values[0])
        if mesh and 'revenantpoison' in mesh.lower():
            key = tex or '(no baseTexture -> mesh default)'
            rp[key] += 1
            rp_examples.setdefault(key, n)
    for tex, c in rp.most_common():
        print(f"    {c:4d} x  {tex}    e.g. {rp_examples[tex]}")

    # 5) 343_dark_smoke + a couple candidate black paks
    print("\n\n############ 5. 343_dark_smoke + candidate black/smoke FX ############")
    dump_full(db, r'records\effects\custom\343_dark_smoke.dbr')
    # list charfxpak candidates that read black/smoke/shadow/dark
    print("\n  charfxpak/fx records reading dark/smoke/shadow:")
    for n in sorted(names):
        l = low[n]
        if ('charfxpak' in l or 'fx_pak' in l or 'fxpak' in l) and \
                any(k in l for k in ('dark', 'smoke', 'shadow', 'black', 'charcoal', 'nether', 'void')):
            print(f"    {n}")


if __name__ == '__main__':
    main()
