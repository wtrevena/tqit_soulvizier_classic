#!/usr/bin/env python3
"""b39 HELOS HUB v2 - landing-spot recon.

For a map .arc + level suffix, dump the level's 0x05 instances classified so the
implementer can pick a landing at the AREA ENTRANCE / next to an in-game travel
NPC / amid REGULAR mobs (NOT the boss horde). Also surveys candidate landing
points for on-mesh + main-component reachability (reuses survey_uberboss_spots).

Usage:
  py tools/debug/survey_hub_v2_landings.py <map.arc> --level <suffix> [--pt X Z EXT ...]
  py tools/debug/survey_hub_v2_landings.py <map.arc> --dump <suffix>   # classified 0x05 dump
"""
import sys, os, struct, math, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'contracts'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections
from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS
import survey_uberboss_spots as S

BS = chr(92)
VER_BASE = {0x0e: 56, 0x0f: 72, 0x11: 72, 0x10: 72, 0x0d: 56}

# classification keyword buckets (lowercased dbr)
PORTAL_KW = ('portalgate', 'gridentrance', 'gridexit', 'portal', 'levelentrance',
             'passageway', 'entrance', 'stairs', 'levelchange', 'boatman')
NPC_KW = ('npc', 'speaking', 'portal_master', 'testhub', 'helos_trav', 'area_return',
          'townsperson', 'merchant', 'villager', 'soulcollector', 'quest')
PROXY_KW = ('drxmap' + BS + 'proxy', 'q_', 'lone', 'warband', 'roulette', 'yard',
            'broodmother', 'broodnest')
MON_KW = ('monster', 'hero', 'boss', 'um_', 'am_', 'bm_', 'bs_', 'creature' + BS,
          'spawn', 'generator', 'pool')
DRESS_KW = ('poi', 'containers', 'setdress', 'soundobject', 'light', '_fx', 'fx_',
            'decor', 'scenery', 'flora', 'rock', 'tree', 'wall', 'floor', 'fog',
            'smoke', 'campfire', 'totem', 'brazier', 'pit', 'effect', 'ambient',
            'sound', 'water', 'mist', 'debris', 'bones', 'root', 'boulder', 'chest')


def bucket(dbr_l):
    for kw in PORTAL_KW:
        if kw in dbr_l:
            return 'PORTAL'
    if any(k in dbr_l for k in ('q_', 'drxmap' + BS + 'proxy', 'lone', 'roulette',
                                'warband', 'broodmother', 'broodnest', 'yard')):
        return 'PROXY'
    for kw in NPC_KW:
        if kw in dbr_l:
            return 'NPC'
    for kw in MON_KW:
        if kw in dbr_l:
            return 'MONSTER'
    for kw in DRESS_KW:
        if kw in dbr_l:
            return 'dress'
    return 'other'


def all_instances(blob, base):
    """[(dbr_str, x, y, z, flags)] for every 0x05 instance. Mirrors
    survey_uberboss_spots.native_instances but keeps y + flags."""
    for t, d in parse_blob_sections(blob):
        if t != 0x05:
            continue
        pos = 0
        nstr = struct.unpack_from('<I', d, pos)[0]; pos += 4
        strings = []
        for _ in range(nstr):
            ln = struct.unpack_from('<I', d, pos)[0]; pos += 4
            strings.append(d[pos:pos + ln]); pos += ln
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


def dump(data, levels, suffix):
    lv, blob = S.get_blob(data, levels, suffix)
    ver = blob[3] if blob[:3] == b'LVL' else None
    base = VER_BASE.get(ver, 72)
    corner = struct.unpack_from('<13i', lv['ints_raw'], 0)[6:9]
    insts = all_instances(blob, base)
    b0b = S.get_0x0b(blob)
    print(f"\n=== {suffix}  v0x{ver:02x} base={base} corner={corner} "
          f"0x05={len(insts)} 0x0b={'Y' if b0b else 'N'} ===")
    groups = {}
    for (dbr, x, y, z, fl) in insts:
        groups.setdefault(bucket(dbr.lower()), []).append((dbr, x, y, z, fl))
    for g in ('PORTAL', 'NPC', 'PROXY', 'MONSTER', 'other'):
        rows = groups.get(g, [])
        if not rows:
            continue
        print(f"  --- {g} ({len(rows)}) ---")
        for (dbr, x, y, z, fl) in rows:
            wx, wz = corner[0] + x, corner[2] + z
            short = dbr.split(BS)[-1][:40]
            print(f"    {short:40s} local({x:7.1f},{y:6.1f},{z:7.1f}) "
                  f"world({wx:8.1f},{wz:8.1f}) fl={fl}")
    print(f"  [dress/setdressing suppressed: {len(groups.get('dress', []))}]")
    return corner


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('map')
    ap.add_argument('--level')
    ap.add_argument('--dump')
    ap.add_argument('--pt', nargs=3, action='append', type=float, metavar=('X', 'Z', 'EXT'))
    ap.add_argument('--base', type=int, default=72)
    args = ap.parse_args()
    data, levels = S.load_world(args.map)
    if args.dump:
        dump(data, levels, args.dump)
    if args.level:
        pts = [(f'pt{i}', p[0], p[1], p[2]) for i, p in enumerate(args.pt or [])]
        S.survey_level(data, levels, args.level, pts, args.base)


if __name__ == '__main__':
    main()
