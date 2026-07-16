"""Athens-catacomb traveler RCA probe (read-only).

Enumerates every 0x05 instance (dbr + WORLD coords) in the Athens catacomb chain,
the Helos plaza, and SpartaCryptLevel2 in the DEPLOYED TESTHUB map (d4965d29), and
sweeps ALL levels for any traveler/portal/sparta-related NPC placement.

world = level corner + local instance position.
"""
import sys, struct
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "tools" / "debug"))
sys.path.insert(0, str(REPO / "tools" / "contracts"))
from contracts_map import parse_level_index, parse_blob_sections, SEC_LEVELS
from arc_patcher import ArcArchive

VER_BASE = {0x0e: 56, 0x0f: 72, 0x11: 72, 0x10: 72, 0x0d: 56}

MAP = REPO / "local" / "Levels_merged_TESTHUB.arc"

FOCUS = [
    "startingfarmland06d",
    "athens/underground/entrance01",
    "athens/underground/catacube02_floor0",
    "athens/underground/catacube02_floor4",
    "athens/underground/catacube02_floor5",
    "athens/underground/catacube02_floor06",
    "athens/underground/catacube02_floorlast",
    "greece/minidungeons/spartacryptlevel2",
]

# Anything that could be a traveler / portal / hub NPC or a sparta reference
SWEEP_KW = ("svc_helos_trav", "svc_area_return", "svc_testhub", "portal_master",
            "sparta", "boatman", "portal_olympianarena", "gridentrance", "gridexit",
            "map_portal", "boat", "traveler", "portalmaster", "npccaravan")


def load_world(path):
    import survey_uberboss_spots as S
    return S.load_world(path)


def instances(blob, base):
    """[(dbr, lx, ly, lz, flags)] for the level's 0x05 instances (local coords)."""
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


def main():
    print(f"MAP: {MAP}")
    data, levels = load_world(str(MAP))
    print(f"levels in index: {len(levels)}")
    by_fname = {}
    for lv in levels:
        by_fname[lv['fname'].replace('\\', '/').lower()] = lv

    print("\n" + "=" * 90)
    print("PART 1 - FOCUS LEVELS: every 0x05 instance whose dbr matches a traveler/portal keyword")
    print("=" * 90)
    for key in FOCUS:
        lv = by_fname.get(key)
        if lv is None:
            print(f"\n[{key}]  *** NOT IN INDEX ***")
            continue
        cx, cy, cz = lv['corner']
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if blob[:3] != b'LVL':
            print(f"\n[{key}]  (not an LVL blob)")
            continue
        base = VER_BASE.get(blob[3], 72)
        insts = instances(blob, base)
        hits = [(dbr, x, y, z, fl) for (dbr, x, y, z, fl) in insts
                if any(kw in dbr.lower() for kw in SWEEP_KW)]
        print(f"\n[{key}]  ver=0x{blob[3]:02x} corner=({cx},{cy},{cz}) guid={lv['guid'].hex()} "
              f"instances={len(insts)} traveler-hits={len(hits)}")
        for dbr, x, y, z, fl in hits:
            wx, wy, wz = cx + x, cy + y, cz + z
            print(f"    {dbr:60s} local=({x:8.1f},{y:6.1f},{z:8.1f}) "
                  f"WORLD=({wx:8.1f},{wy:6.1f},{wz:8.1f}) flags={fl}")

    print("\n" + "=" * 90)
    print("PART 2 - GLOBAL SWEEP: every level that contains a traveler/portal/sparta NPC dbr")
    print("=" * 90)
    from collections import defaultdict
    where = defaultdict(list)  # dbr_short -> [(fname, wx, wy, wz)]
    for lv in levels:
        fname = lv['fname'].replace('\\', '/')
        cx, cy, cz = lv['corner']
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if blob[:3] != b'LVL':
            continue
        base = VER_BASE.get(blob[3], 72)
        try:
            insts = instances(blob, base)
        except Exception as e:
            continue
        for dbr, x, y, z, fl in insts:
            dl = dbr.lower()
            if any(kw in dl for kw in ("svc_helos_trav", "svc_area_return", "svc_testhub",
                                        "portal_master", "portal_olympianarena")):
                short = dl.replace('\\', '/').split('/')[-1].replace('.dbr', '')
                where[short].append((fname, cx + x, cy + y, cz + z))
    for short in sorted(where):
        locs = where[short]
        print(f"\n  {short}  (x{len(locs)})")
        for fname, wx, wy, wz in locs:
            print(f"      {fname:55s} WORLD=({wx:8.1f},{wy:6.1f},{wz:8.1f})")

    print("\n" + "=" * 90)
    print("PART 3 - SPARTA-specific: which levels reference sparta anywhere in a dbr")
    print("=" * 90)
    for lv in levels:
        fname = lv['fname'].replace('\\', '/')
        cx, cy, cz = lv['corner']
        blob = data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
        if blob[:3] != b'LVL':
            continue
        base = VER_BASE.get(blob[3], 72)
        try:
            insts = instances(blob, base)
        except Exception:
            continue
        shits = [(dbr, cx + x, cy + y, cz + z) for (dbr, x, y, z, fl) in insts
                 if "sparta" in dbr.lower()]
        if shits:
            print(f"\n  [{fname}] corner=({cx},{cy},{cz}) guid={lv['guid'].hex()}")
            for dbr, wx, wy, wz in shits:
                print(f"      {dbr:60s} WORLD=({wx:8.1f},{wy:6.1f},{wz:8.1f})")


if __name__ == "__main__":
    main()
