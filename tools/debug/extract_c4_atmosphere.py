"""Extract EXACT SV float32 coords + rotation matrices for every C4 dropped-atmosphere record,
so the injected records are byte-shape identical to SV's own placement (position + rotation + flags).

For each target level, for each dropped atmosphere record, print the full-precision (x,y,z), the 9-float
rotation matrix, and the flags - ready to paste into INJECT_SPECS.

Also emits the C4 records for C2 (mc_hades_anouranfirepit02 rot at the wagon-side scene, for consistency).
"""
import sys, struct
from pathlib import Path
REPO = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'debug'))
import recon_doors_hub as R

# level -> set of record substrings to extract (the DROPPED ones from the C4 recon)
TARGETS = {
    'levels/world/orient/silkroad/hiddenvalley01.lvl': [
        b'dress2\\totem', b'15mlight_simple_purple', b'camps\\setdress\\campfire01',
        b'5mlight_dyn_orange', b'10mlight_simple_red',
        # ROUND-2 (vet fix): the totem UNDER-LIGHTS (2 purple + 2 red) round-1 omitted. SV
        # places them ~0.3-0.5u XZ / ~4u above each totem. Restored in INJECT_SPECS.
        b'10mlight_dyn_purple', b'10mlight_dyn_red',
    ],
    'levels/world/greece/delphi/delphilowlands04.lvl': [
        b'merchant_delphi_occulttent01', b'fog_occult_fx01', b'10mlight_statnl_blue', b'5mlight_dyn_green',
    ],
    'levels/world/greece/delphi/delphilowlands02.lvl': [
        b'fog_occult_fx01', b'pit_fx01', b'pit_fx02', b'anouranfirepitmd01', b'anouranfirepit03',
        b'bugcloud_smallfx',
    ],
    'levels/world/greece/delphi/delphilowlands03.lvl': [
        b'bugcloud_smallfx',
    ],
}


def main():
    sv_data, _, sv_levels = R.load_world(R.SV_ARC)
    sv_by = {lv['fname'].replace('\\', '/').lower(): lv for lv in sv_levels}
    for key, subs in TARGETS.items():
        lv = sv_by.get(key)
        if not lv:
            print(f'# {key}: NOT in SV'); continue
        corner = R.ints_of(lv)[0]
        strings, insts, ver = R.parse_0x05(R.blob_of(sv_data, lv))
        print(f'\n# ==== {key} (SV corner {corner}, v0x{ver:02x}) ====')
        for it in insts:
            low = it['dbr'].lower()
            if any(s in low for s in subs):
                rot = it['rot']
                # is rotation identity?
                ident = all(abs(rot[i] - (1.0 if i in (0, 4, 8) else 0.0)) < 1e-6 for i in range(9))
                rotstr = 'IDENTITY' if ident else f'({", ".join(repr(v) for v in rot)})'
                print(f"  {it['dbr'].decode('ascii','replace')}")
                print(f"    coord=({it['x']!r}, {it['y']!r}, {it['z']!r}) flags={it['flags']} rot={'identity' if ident else rotstr}")


if __name__ == '__main__':
    main()
