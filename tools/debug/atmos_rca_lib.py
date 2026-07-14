"""B-SMOKE-1 / B54 occult-atmosphere RCA: reusable read-only library.

Loads the SV-original world map (upstream/soulvizier_098i) and the deployed build40
canonical map (work/SoulvizierClassic), enumerates every 0x05 entity instance per
level (dbr + world/local coords + rotation + flags), and classifies atmosphere-class
entities PRESENT / DROPPED / MOVED vs SV.

READ-ONLY. No heavy build. Arcs are read from the MAIN repo (gitignored) by absolute
path; tooling (arc_patcher / merge_levels_binary) is imported from whichever tools/
dir this file lives in (byte-identical at HEAD).
"""
import struct
import sys
from pathlib import Path

MAIN = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic')
sys.path.insert(0, str(MAIN / 'tools'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS

SV_ARC = MAIN / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Levels.arc'
SVAERA_ARC = MAIN / 'reference_mods' / 'SVAERA_customquest' / 'Resources' / 'Levels.arc'
BUILD40_ARC = MAIN / 'work' / 'SoulvizierClassic' / 'Resources' / 'Levels.arc'   # 9981085b == local/Levels_merged.arc
# build36a == what's LIVE on Steam right now (canonical). Located at build time.
LIVE_CANDIDATES = [
    MAIN / 'local' / 'baseline_canonical_b39.arc',
    MAIN / 'local' / 'Levels_deployed_prev.arc',
]


def load_world(arc_path):
    """Return (data, levels, by_name) for a Levels.arc's world01.map (entry_type==3)."""
    arc = ArcArchive.from_file(arc_path)
    entry = [e for e in arc.entries if e.entry_type == 3][0]
    data = arc.decompress(entry)
    sec_map = {s['type']: s for s in parse_sections(data)}
    levels = parse_level_index(data, sec_map[SEC_LEVELS])
    by_name = {lv['fname'].replace('\\', '/').lower(): lv for lv in levels}
    return data, levels, by_name


def blob_of(data, lv):
    return data[lv['data_offset']:lv['data_offset'] + lv['data_length']]


def ints_of(lv):
    """13x int32 header: [0..5] tile dims, [6,7,8] grid corner (world x,y,z), [9..12] GUID."""
    return lv.get('ints_raw')


def blob_sections(blob):
    secs = []
    if len(blob) < 4:
        return secs, None
    magic = blob[:4]
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            break
        secs.append({'type': st, 'size': ss, 'data': blob[pos + 8:pos + 8 + ss]})
        pos += 8 + ss
    return secs, magic


def blob_version(blob):
    """LVL version byte (0x0e SV-only, 0x0f base-AE, 0x11 shared-merged)."""
    return blob[3] if blob[:3] == b'LVL' else None


def base_size_for(ver):
    return 72 if ver in (0x11, 0x0f) else 56


def parse_0x05(blob):
    """Return (strings, insts). Each inst: {i, str_idx, dbr(bytes,lower,backslash), x,y,z,
    rot(9-tuple), flags, uid(hex or None)}. Handles v0e(56)/v0f,v11(72) + flagged +16.
    """
    ver = blob_version(blob)
    base = base_size_for(ver)
    secs, _ = blob_sections(blob)
    s05 = [s for s in secs if s['type'] == 0x05]
    if not s05:
        return [], []
    data = s05[0]['data']
    scount = struct.unpack_from('<I', data, 0)[0]
    pos = 4
    strings = []
    for _ in range(scount):
        slen = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        strings.append(data[pos:pos + slen])
        pos += slen
    inst_count = struct.unpack_from('<I', data, pos)[0]
    pos += 4
    insts = []
    for i in range(inst_count):
        if pos + base > len(data):
            break
        str_idx = struct.unpack_from('<I', data, pos)[0]
        rot = struct.unpack_from('<9f', data, pos + 4)
        x, y, z = struct.unpack_from('<3f', data, pos + 40)
        flags = struct.unpack_from('<I', data, pos + 52)[0]
        rec_size = base + (16 if flags != 0 else 0)
        uid = None
        if flags != 0:
            # UniqueId is the 16 bytes right after the base core.
            uid = data[pos + base:pos + base + 16].hex()
        dbr = b''
        if 0 <= str_idx < len(strings):
            dbr = strings[str_idx].replace(b'/', b'\\').lower()
        insts.append({'i': i, 'str_idx': str_idx, 'dbr': dbr, 'x': x, 'y': y, 'z': z,
                      'rot': rot, 'flags': flags, 'uid': uid})
        pos += rec_size
    return strings, insts


# --- atmosphere classification ---------------------------------------------------
# Substrings (matched on the lowercased backslash dbr) that mark an entity as
# visual-atmospheric / occult-scene. Deliberately inclusive per the RCA brief.
ATMO_SUBS = [
    b'fog_', b'fog', b'smoke', b'aura', b'pit_fx', b'pitfx', b'pitspawner',
    b'lildude', b'vitstaff', b'cage', b'cageglow', b'cage_binding',
    b'firepit', b'anouranfirepit', b'pyre', b'woodpyre', b'totem', b'campfire',
    b'bugcloud', b'soundobject', b'obsidian', b'occult', b'disciple',
    b'demon', b'blooddemon', b'\\effects\\', b'lights\\dynamic', b'lights\\simple',
    b'light_dyn', b'light_simple', b'mlight_dyn', b'mlight_simple', b'mlight_stat',
    b'mlight_statnl', b'nightlight', b'staticlight', b'dynamiclight',
    b'particles\\environment', b'skilleffects', b'objefx',
]
# lights are only atmospheric when coloured/occult; but per brief include all *light* dyn/simple/stat.


def is_atmo(dbr):
    low = dbr.lower()
    if any(s in low for s in ATMO_SUBS):
        return True
    # catch xpack effect lights not covered above
    if b'\\lights\\' in low and (b'purple' in low or b'red' in low or b'blue' in low
                                 or b'green' in low or b'orange' in low):
        return True
    return False


def short(dbr):
    return dbr.decode('ascii', 'replace')


def leaf(dbr):
    return dbr.decode('ascii', 'replace').split('\\')[-1]
