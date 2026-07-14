"""Spot-check: (1) the nature of the dropped drx_bladehoning_running_fx (is it smoke?),
(2) full-record integrity of a fog_occult_fx01 instance SV(v0e,56B) vs build40(v11,72B):
rotation matrix non-degenerate, flags, and the 16-byte v11 tail decoded."""
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import atmos_rca_lib as A
MAIN = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(MAIN / 'tools'))
from arz_patcher import ArzDatabase

# (1) bladehoning record
dep = ArzDatabase.from_arz(MAIN / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz')
for needle in ['drx_bladehoning_running_fx', 'occultfog', 'fog_occult']:
    keys = [k for k in dep._raw_records if needle in k.lower()]
    print(f'\n== {needle}: {keys[:3]}')
    if keys:
        k = keys[0]
        flds = dep.get_fields(k)
        typ = dep._record_types.get(k)
        print(f'   type={typ}')
        if flds:
            for name, tf in flds.items():
                real = name.split('###')[0]
                if real in ('Class', 'effectFile', 'templateName', 'ActorName', 'description'):
                    print(f'     {real:16s} {tf.values}')

# (2) fog_occult_fx01 instance full-record dump SV vs build40, delphilowlands02
KEY = 'levels/world/greece/delphi/delphilowlands02.lvl'
sv_data, _, sv_by = A.load_world(A.SV_ARC)
b40_data, _, b40_by = A.load_world(A.BUILD40_ARC)


def dump_fog(label, data, by):
    lv = by[KEY]
    blob = A.blob_of(data, lv)
    ver = A.blob_version(blob)
    strings, insts = A.parse_0x05(blob)
    fogs = [it for it in insts if b'fog_occult_fx01' in it['dbr']]
    print(f'\n== {label} v0x{ver:02x}: {len(fogs)} fog_occult_fx01 instances')
    for it in fogs[:2]:
        rot = it['rot']
        # det of the 3x3 rotation (rows are rot[0:3],[3:6],[6:9])
        m = rot
        det = (m[0]*(m[4]*m[8]-m[5]*m[7]) - m[1]*(m[3]*m[8]-m[5]*m[6])
               + m[2]*(m[3]*m[7]-m[4]*m[6]))
        print(f'   i={it["i"]} pos=({it["x"]:.2f},{it["y"]:.2f},{it["z"]:.2f}) flags={it["flags"]} '
              f'rotdet={det:.4f} uid={it["uid"]}')
        print(f'      rot={[round(x,3) for x in rot]}')


dump_fog('SV', sv_data, sv_by)
dump_fog('BUILD40', b40_data, b40_by)
