"""b48: hub-NPC placement audit of the DEPLOYED TESTHUB Levels.arc (841c56cd).

Uses the PROVEN survey_uberboss_spots primitives. For EVERY level, list any 0x05
instance whose dbr is a hub NPC (helos_trav / area_return / portal_master / testhub /
svc_). Emits per-record placement COUNT across all levels (warden-mute test:
a boat-dialog record placed >1x binds to ONE entity, rest go mute).
"""
import sys, struct
from pathlib import Path
from collections import defaultdict
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "contracts"))
sys.path.insert(0, str(REPO / "tools" / "debug"))
import survey_uberboss_spots as S
from contracts_map import parse_blob_sections

DEP_LEVELS = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne"
                  r"\CustomMaps\SoulvizierClassicDEV\Resources\Levels.arc")
VER_BASE = {0x0e: 56, 0x0f: 72, 0x11: 72, 0x10: 72, 0x0d: 56}
BS = chr(92)
HUB_KW = ('helos_trav', 'area_return', 'portal_master', 'testhub', 'boatmantoegypt')

def all_instances(blob, base):
    """(dbr, x, y, z, flags) per 0x05 instance. Offsets per survey_hub_v2_landings."""
    for t, d in parse_blob_sections(blob):
        if t != 0x05:
            continue
        pos = 0
        nstr = struct.unpack_from('<I', d, pos)[0]; pos += 4
        strings = []
        for _ in range(nstr):
            ln = struct.unpack_from('<I', d, pos)[0]; pos += 4
            strings.append(d[pos:pos+ln]); pos += ln
        ninst = struct.unpack_from('<I', d, pos)[0]; pos += 4
        out = []
        for _ in range(ninst):
            sid = struct.unpack_from('<I', d, pos)[0]
            x, y, z = struct.unpack_from('<fff', d, pos + 40)
            flags = struct.unpack_from('<I', d, pos + 52)[0]
            dbr = (strings[sid] if sid < len(strings) else b'?').decode('latin1')
            out.append((dbr, x, y, z, flags))
            pos += base + (16 if flags != 0 else 0)
        return out
    return []

def main():
    data, levels = S.load_world(DEP_LEVELS)
    print(f"levels: {len(levels)}")
    per_record = defaultdict(list)   # dbr_lower -> [(level, x,y,z,flags)]
    helos_host_dump = None
    for lv in levels:
        fname = lv['fname'] if 'fname' in lv else lv.get('fname','?')
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if blob[:3] != b'LVL':
            continue
        ver = blob[3]
        base = VER_BASE.get(ver, 72)
        try:
            insts = all_instances(blob, base)
        except Exception as e:
            continue
        for (dbr, x, y, z, fl) in insts:
            dl = dbr.lower()
            if any(kw in dl for kw in HUB_KW):
                per_record[dl].append((fname, x, y, z, fl))
        if 'startingfarmland06d' in fname.lower():
            corner = struct.unpack_from('<13i', lv['ints_raw'], 0)[6:9] if 'ints_raw' in lv else (0,0,0)
            helos_host_dump = (fname, ver, base, corner, insts)

    print("\n" + "="*100)
    print("HUB-NPC placement COUNT across ALL levels (warden-mute test):")
    print("="*100)
    for dbr in sorted(per_record):
        placements = per_record[dbr]
        levels_set = set(p[0] for p in placements)
        warn = ""
        if len(placements) > 1:
            warn = f"  <<<< PLACED {len(placements)}x"
            if len(levels_set) > 1:
                warn += f" ACROSS {len(levels_set)} LEVELS (WARDEN-MUTE RISK)"
            else:
                warn += " (same level - dup)"
        short = dbr.split(BS)[-1]
        print(f"  {short:44s} x{len(placements)}{warn}")
        for (lvl, x, y, z, fl) in placements:
            print(f"       @ {lvl.split(BS)[-1]:38s} local({x:8.1f},{y:6.1f},{z:8.1f}) fl={fl}")

    # Focus: the Helos host level full NPC/quest dump
    if helos_host_dump:
        fname, ver, base, corner, insts = helos_host_dump
        print("\n" + "="*100)
        print(f"HELOS HOST LEVEL: {fname}  v0x{ver:02x} base={base} corner={corner}  0x05={len(insts)}")
        print("="*100)
        for (dbr, x, y, z, fl) in insts:
            dl = dbr.lower()
            if any(kw in dl for kw in ('helos_trav','area_return','portal_master','testhub','npc','speaking','quest','boatman','svc_')):
                wx, wz = corner[0]+x, corner[2]+z
                print(f"    {dbr.split(BS)[-1]:44s} local({x:7.1f},{y:5.1f},{z:7.1f}) world({wx:8.1f},{wz:8.1f}) fl={fl}")

    # Explicitly report the 11 travelers + 6 returns presence
    print("\n" + "="*100)
    print("EXPECTED HUB ROSTER presence (deployed):")
    expect = ['svc_helos_trav_garden','svc_helos_trav_secret','svc_helos_trav_sparta',
              'svc_helos_trav_uber','svc_helos_trav_bossarena','svc_helos_trav_warband',
              'svc_helos_trav_dorus','svc_helos_trav_tantalus','svc_helos_trav_charon',
              'svc_helos_trav_mnemophage','svc_helos_trav_ephialtes',
              'svc_area_return_dorus','svc_area_return_tantalus','svc_area_return_charon',
              'svc_area_return_mnemophage','svc_area_return_ephialtes','svc_area_return_warband',
              'portal_master_helos','svc_testhub_master','svc_testhub_master_helos',
              'svc_testhub_master_cave','svc_testhub_return']
    for name in expect:
        hits = [(k,v) for k,v in per_record.items() if name in k]
        cnt = sum(len(v) for _,v in hits)
        status = "MISSING (unplaced)" if cnt==0 else (f"placed x{cnt}" + ("  <<<< MULTI" if cnt>1 else ""))
        mark = "  <<<< SPARTA" if 'sparta' in name else ""
        print(f"    {name:34s} {status}{mark}")

if __name__ == "__main__":
    main()
