"""Exact-key field diff of the occult FX EffectEntity records: DEPLOYED(build40) vs SV vs BASE.
Also resolves each record's effectFile .pfx and checks it exists in the deployed Resources arcs."""
import sys
from pathlib import Path
MAIN = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(MAIN / 'tools'))
from arz_patcher import ArzDatabase

DEPLOYED = MAIN / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'
SV = MAIN / 'upstream' / 'soulvizier_098i' / 'Database' / 'database.arz'
BASE = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz')

# exact record keys (lowercase backslash) for the occult/smoke FX + companions
KEYS = [
    r'records\drxmap\effects\fog_occult_fx01.dbr',
    r'records\drxmap\effects\pit_fx01.dbr',
    r'records\drxmap\effects\pit_fx02.dbr',
    r'records\xpack\effects\particles\environment\bugcloud_smallfx.dbr',
    r'records\drxmap\effects\occultistaura_fx01.dbr',
    r'records\drxmap\effects\cage_binding_fx01.dbr',
    r'records\drxcreatures\bloodwitch\skills\skilleffects\fx_disciple_aura_eyechantment01.dbr',
    r'records\drxcreatures\bloodwitch\skills\skilleffects\fx_disciple_aura_eyechantment02.dbr',
]

print('Loading deployed...'); dep = ArzDatabase.from_arz(DEPLOYED)
print('Loading SV...'); sv = ArzDatabase.from_arz(SV)
print('Loading base...'); base = ArzDatabase.from_arz(BASE)


def flat(db, key):
    f = db.get_fields(key)
    if not f:
        return None
    return {name.split('###')[0]: tf.values for name, tf in f.items()}


pfx_refs = []
for key in KEYS:
    print(f'\n{"="*78}\n{key}')
    d = flat(dep, key); s = flat(sv, key); b = flat(base, key)
    print(f'  present: DEP={d is not None} SV={s is not None} BASE={b is not None}')
    if d is None:
        print('  ** NOT IN DEPLOYED ARZ **'); continue
    if d.get('effectFile'):
        pfx_refs.append((key, d['effectFile'][0]))
    # DEP vs SV field diff
    if s is not None:
        allk = list(dict.fromkeys(list(d) + list(s)))
        diffs = []
        for fk in allk:
            if d.get(fk) != s.get(fk):
                diffs.append((fk, s.get(fk), d.get(fk)))
        if not diffs:
            print('  DEP==SV: BYTE-IDENTICAL fields (all values match)')
        else:
            print(f'  DEP vs SV DIFFERS ({len(diffs)} field(s)):')
            for fk, sv_v, dv in diffs:
                print(f'     {fk:24s} SV={sv_v!r}  DEP={dv!r}')
    else:
        print('  (not in SV arz; DEP fields:)')
        for fk, v in d.items():
            print(f'     {fk:24s} {v}')

print(f'\n{"#"*78}\n# effectFile .pfx referenced by deployed occult FX records:')
for key, pfx in pfx_refs:
    print(f'   {Path(key).name:34s} -> {pfx}')
