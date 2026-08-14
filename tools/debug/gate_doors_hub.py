#!/usr/bin/env python3
"""gate_doors_hub - THE GRAVEYARD TOMBSTONE GATE (2026-08-14, R-248).

LINEAGE (four eras, all deliberate):
  1. build24/25: verified the original invented door pairs + the 20-portal born-open
     TESTHUB hub. 2. 2026-07-12 P0: every authored walk-through portal was stripped;
     this file became a tombstone. 3. 2026-08-13 R-246: doors were resurrected as
     native travel devices; this file delegated to gate_device_resolution.
  4. 2026-08-14 R-248: Will refuted the devices IN-GAME ("the new portals you made
     dont work and they lag the game out and break everything") - the SECOND failure
     of the class (doors-hub 2026-07 was the first). Born-open GridEntrance travel
     devices are PERMANENTLY GRAVEYARDED: the 0x14 dest-GUID binding is a standing
     streaming edge; N doors in one host = N remote clusters resident in a 32-bit
     process, detonating the ProcessRLTD heap path (MODDING_PLAYBOOK sec 10/10a).
     gate_device_resolution is RETIRED with its device class.

THIS GATE IS NOW THE GRAVEYARD'S PLANTED NEGATIVE: it scans built map arcs and FAILS
if any door-class travel device is ever placed again.

  G1 ZERO portal_olympianarena1 (born-open GridEntrance entrance) instances anywhere,
     either variant. Doors remain legitimate ONLY as native single-cave-mouth
     GridEntrance art (a different record class entirely).
  G2 portal_olympianarena2 (GridExitOneWay landing) instances: ONLY the SV-NATIVE
     inventory (inert props inside upstream SV blobs, shipped since P0):
     crypt_floor1 x1 (mouth uid 6e513e90..) + boss_arena x2 (SV's own vestigial
     dais return portals - the b43 comment documents them; never wired by us).
     Any OTHER instance is a door-class landing returning.
  G3 map_portal_aura swirls: ONLY the SV-native blood-cave connector dressing
     (yet_another_fucking_connector x1, upstream bytes). The R-246 court/door
     swirls were OURS and must stay gone.

Usage: py tools/debug/gate_doors_hub.py <canonical.arc> [<testhub.arc>]
Exit 0 = PASS (the graveyard holds).
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools'))
sys.path.insert(0, str(REPO / 'tools' / 'contracts'))

_LEGACY_SUBGATES = {'collateral', 'hubidentity', 'placement', 'c1', 'c3', 'c4',
                    'crosstalk', 'all'}
# The SV-NATIVE device-record inventory (upstream-authentic bytes inside SV blobs,
# ships since P0 - never placed by INJECT_SPECS): (level_key, record_suffix) -> count.
NATIVE_ALLOWED = {
    ('levels/world/uberdungeon/crypt_floor1.lvl', 'portal_olympianarena2.dbr'): 1,
    ('levels/world/bossarena/boss_arena.lvl', 'portal_olympianarena2.dbr'): 2,
    ('levels/world/xbloodcave/yet_another_fucking_connector.lvl', 'map_portal_aura.dbr'): 1,
}


def scan(path):
    import gate_travel_y_terrain as g
    from collections import Counter
    data, levels = g.load_map(path)
    fails = []
    n1 = n2 = n3 = 0
    seen = Counter()
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if (b'portal_olympianarena' not in blob and b'map_portal_aura' not in blob):
            continue
        key = lv['fname'].replace(chr(92), '/').lower()
        for (nm, x, _y, z, _f, _u, _i) in g.parse_0x05(blob):
            if nm.endswith('portal_olympianarena1.dbr'):
                n1 += 1
                fails.append(f'G1 {key}: born-open door ENTRANCE placed at ({x},{z}) - '
                             f'the graveyarded device class is BACK (R-248 sec 10/10a)')
            elif nm.endswith('portal_olympianarena2.dbr'):
                n2 += 1
                seen[(key, 'portal_olympianarena2.dbr')] += 1
                if seen[(key, 'portal_olympianarena2.dbr')] > \
                        NATIVE_ALLOWED.get((key, 'portal_olympianarena2.dbr'), 0):
                    fails.append(f'G2 {key}: door LANDING placed at ({x},{z}) beyond '
                                 f'the SV-native inventory')
            elif nm.endswith('map_portal_aura.dbr'):
                n3 += 1
                seen[(key, 'map_portal_aura.dbr')] += 1
                if seen[(key, 'map_portal_aura.dbr')] > \
                        NATIVE_ALLOWED.get((key, 'map_portal_aura.dbr'), 0):
                    fails.append(f'G3 {key}: door swirl FX placed at ({x},{z}) beyond '
                                 f'the SV-native inventory')
    for (k, want) in NATIVE_ALLOWED.items():
        if seen.get(k, 0) != want:
            fails.append(f'G2/G3 native-inventory drift: {k[0].split("/")[-1]} '
                         f'{k[1]} x{seen.get(k, 0)}, expected exactly {want} '
                         f'(upstream bytes changed?)')
    return fails, (n1, n2, n3)


def main(argv):
    args = [a for a in argv[1:] if a not in _LEGACY_SUBGATES]
    if not args:
        print('usage: gate_doors_hub.py <canonical.arc> [<testhub.arc>]  '
              '(the graveyard tombstone gate: zero door-class travel devices)')
        return 2
    print('=== gate_doors_hub (R-248): door-class travel devices are GRAVEYARDED - '
          'asserting none is placed ===')
    rc = 0
    for path in args:
        fails, (n1, n2, n3) = scan(path)
        label = Path(path).name
        if fails:
            print(f'  {label}: {len(fails)} FAILURE(S)')
            for f in fails:
                print(f'    FAIL {f}')
            rc = 1
        else:
            print(f'  {label}: PASS (entrances={n1}, landings={n2} [native crypt prop '
                  f'only], swirls={n3})')
    print('GRAVEYARD GATE: ' + ('FAIL' if rc else 'PASS - the R-248 graveyard holds'))
    return rc


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
