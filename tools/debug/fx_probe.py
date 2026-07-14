"""Probe the FX dbr records across deployed(build40) / SV / base arz: keys, type, fields."""
import sys
from pathlib import Path
MAIN = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(MAIN / 'tools'))
from arz_patcher import ArzDatabase

DEPLOYED = MAIN / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'
SV = MAIN / 'upstream' / 'soulvizier_098i' / 'Database' / 'database.arz'
BASE = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz')

FX = ['fog_occult_fx01', 'pit_fx01', 'pit_fx02', 'bugcloud_smallfx',
      'occultistaura_fx01', 'cage_binding_fx01']

print('Loading deployed...'); dep = ArzDatabase.from_arz(DEPLOYED)
print('Loading SV...'); sv = ArzDatabase.from_arz(SV)
print('Loading base...'); base = ArzDatabase.from_arz(BASE)

def find_keys(db, needle):
    return [k for k in db._raw_records if needle in k.lower()]

for fx in FX:
    print(f'\n{"="*76}\n{fx}')
    for label, db in [('DEP', dep), ('SV', sv), ('BASE', base)]:
        keys = find_keys(db, fx)
        print(f'  [{label}] {len(keys)} key(s): {keys[:4]}')
        if keys:
            k = keys[0]
            typ = db._record_types.get(k)
            flds = db.get_fields(k)
            print(f'       type={typ} nfields={len(flds) if flds else 0}')
            if flds and label == 'DEP':
                for name, tf in flds.items():
                    real = name.split('###')[0]
                    print(f'         {real:34s} {tf.values}')
