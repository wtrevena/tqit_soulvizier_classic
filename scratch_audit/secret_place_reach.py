"""Secret Place / boat-route reachability (read-only) - the RIGHT lens.

(1) SECRET PLACE cluster: enumerate every secret_place/darkforest/murder* level, its corner,
    0x14 portal-record count, and any crow/murder/zilla/boss proxy placed in it -> is the crow
    boss reachable by walking from the darkforestenter traveler landing, or sealed?
(2) BOAT-ROUTE REACHABILITY: for every restored area, does ANY boat-dialog route (build_quest_files)
    land inside it, and is that route's NPC PLACED in the TESTHUB map? (the correct post-build36a
    reachability model - travel is quest-teleport, not 0x14 portals).
"""
import sys, struct
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "debug"))
sys.path.insert(0, str(REPO / "tools" / "contracts"))
from contracts_map import parse_blob_sections
import build_quest_files as bqf
import build_section_surgery as bss

VER_BASE = {0x0e: 56, 0x0f: 72, 0x11: 72, 0x10: 72, 0x0d: 56}
MAP = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged_TESTHUB.arc")


def load_world(path):
    import survey_uberboss_spots as S
    return S.load_world(path)


def instances(blob, base):
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


def sec_count(blob, sectype):
    return sum(1 for t, _ in parse_blob_sections(blob) if t == sectype)


def main():
    data, levels = load_world(str(MAP))
    boxes = []  # (fname, corner, dims-from-ints, guid)
    for lv in levels:
        boxes.append(lv)

    print("=" * 96)
    print("PART 1 - SECRET PLACE cluster: levels, 0x14 portal-record count, crow/boss proxies placed")
    print("=" * 96)
    KW = ("crow", "murder", "zilla", "bunny", "boar", "q_", "boss", "hero")
    for lv in levels:
        fn = lv['fname'].replace('\\', '/').lower()
        if not ("secret_place" in fn or "darkforest" in fn or "murderboss" in fn):
            continue
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if blob[:3] != b'LVL':
            continue
        base = VER_BASE.get(blob[3], 72)
        insts = instances(blob, base)
        n14 = sec_count(blob, 0x14)
        hits = [(dbr, x, y, z) for (dbr, x, y, z, fl) in insts
                if any(k in dbr.lower() for k in KW)]
        print(f"\n  [{lv['fname']}] ver=0x{blob[3]:02x} corner={lv['corner']} 0x14-sections={n14} insts={len(insts)}")
        for dbr, x, y, z in hits[:20]:
            print(f"       {dbr}")

    # ---- PART 2: boat-route reachability ----
    print("\n" + "=" * 96)
    print("PART 2 - BOAT-ROUTE reachability: which restored areas have a PLACED-NPC route landing inside")
    print("=" * 96)
    # build level boxes (corner + dims) via the 13-int header
    def ints13(lv):
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        for t, d in parse_blob_sections(blob):
            if t == 0x01 and len(d) >= 52:
                return struct.unpack_from('<13i', d, 0)
        return None

    # placement set (TESTHUB): npc_short -> set(level fname lower)
    from collections import defaultdict
    placed = defaultdict(set)
    boxlist = []
    for lv in levels:
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if blob[:3] != b'LVL':
            continue
        base = VER_BASE.get(blob[3], 72)
        cx, cy, cz = lv['corner']
        # box from tile dims (ints[0..2] tile counts * tile size? use simple corner+span via instances bbox fallback)
        for dbr, x, y, z, fl in instances(blob, base):
            dl = dbr.lower().replace('/', '\\').split('\\')[-1]
            if dl.startswith(('svc_helos_trav', 'svc_area_return', 'svc_testhub', 'portal_master_helos')):
                placed[dl].add(lv['fname'].replace('\\', '/').lower())

    # routes from the tooling tables (TESTHUB registration): Almyros + per-area returns + hub
    routes = []
    for xyz, tag in bqf.HELOS_PORTAL_DESTS:
        routes.append((bqf.HELOS_PORTAL_NPC.split('\\')[-1].lower(), xyz, tag))
    for npc in bqf.TESTHUB_AREA_RETURN_NPCS:
        for xyz, tag in bqf.TESTHUB_RETURN_DESTS:
            routes.append((npc.split('\\')[-1].lower(), xyz, tag))
    for npc, xyz, tag in bqf.HELOS_HUB_TRAVEL:
        routes.append((npc.split('\\')[-1].lower(), xyz, tag))

    def resolve_level(wx, wy, wz):
        best = None
        for lv in levels:
            it = ints13(lv)
            if not it:
                continue
            # corner = it[6,7,8]; tile dims it[0,1,2] (x,y,z tile counts); tile size 256? use generous 2u pad on span
            cx, cy, cz = it[6], it[7], it[8]
            # span: approximate via tile counts * 128 (loose). We only need coarse containment.
            sx, sz = it[0], it[2]
            if 0 < sx < 100000 and 0 < sz < 100000:
                if cx <= wx <= cx + sx and cz <= wz <= cz + sz:
                    return lv['fname']
        return None

    AREAS = {"spartacryptlevel2": "spartacryptlevel2", "crypt_floor1": "uberdungeon/crypt_floor1",
             "gardenofmerchants": "gardenofmerchants", "darkforestenter": "darkforestenter",
             "murderbossroom": "murderbossroom", "catacube02_floorlast": "catacube02_floorlast",
             "maze03": "maze03"}
    # For each route, resolve landing level by nearest-corner (coarse): find level whose corner is closest and route is within its instance bbox.
    for name, sub in AREAS.items():
        lv = next((l for l in levels if sub in l['fname'].replace('\\', '/').lower()), None)
        if not lv:
            print(f"  [{name}] not in index"); continue
        cx, cy, cz = lv['corner']
        # collect route dests whose nearest level corner is this level (coarse: within 400u of corner in x,z and closest)
        landed = []
        for npc, (rx, ry, rz), tag in routes:
            # nearest level to (rx,ry,rz) by corner distance in xz
            nearest = min(levels, key=lambda L: (L['corner'][0]-rx)**2 + (L['corner'][2]-rz)**2)
            if nearest['fname'] == lv['fname']:
                is_placed = npc in placed and len(placed[npc]) > 0
                landed.append((npc, (rx, ry, rz), tag, is_placed))
        any_placed = any(p for *_x, p in landed)
        print(f"\n  [{name}] {lv['fname']} corner=({cx},{cy},{cz})")
        if not landed:
            print(f"       NO boat route lands here")
        for npc, xyz, tag, p in landed:
            print(f"       route {npc:32s} {tag:26s} dest={xyz} placed_in_TESTHUB={p}")
        print(f"       => REACHABLE in TESTHUB: {any_placed}")


if __name__ == "__main__":
    main()
