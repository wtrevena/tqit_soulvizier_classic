#!/usr/bin/env python3
"""
DOMAIN D - MAP CONTRACTS for Soulvizier Classic (TQAE mod).

Permanent, precedent-derived invariants over the shipped world map
(local/Levels_merged.arc -> world01.map) plus the coupled Quests.arc, Text.arc
and the compiled .arz. Every contract derives its "what a functioning X needs"
from NATIVE base-game precedent (the vanilla TQAE Levels.arc / database.arz)
and/or the pristine SV 0.98i upstream, then asserts it over OUR shipped map.

Self-contained: this module copies the small read-only .arc / .arz loaders it
needs (it does NOT import or edit any shared build/gate script). It re-implements
the map-section parsers documented in docs/MODDING_PLAYBOOK.md,
docs/CROSS_LEVEL_STITCH_RE.md and docs/DYNGRID_GATE_RCA.md.

INTERFACE (shared across the 5 parallel contract modules):
    run(cfg: dict) -> list[dict]
    CONTRACTS = [ {id, name, asserts, derived_from}, ... ]
  cfg = {'arz','text_arc','levels_arc','quests_arc','resource_arc_dir',
         'base_game_dir','upstream_dir'}
  violation = {'contract','severity','subject','message','evidence'}
  severity in {'P0','P1','P2'}.

Standalone:
    python tools/contracts/contracts_map.py <arz> <text_arc> <levels_arc>
            <quests_arc> <resource_arc_dir> <base_game_dir> <upstream_dir>
  prints violations as JSON lines, exits 1 if any P0/P1 remains (after
  whitelist), else 0.

Whitelist: tools/contracts/whitelist_map.txt, one "<CONTRACT-ID> <subject>" per
line (# comments allowed). Matching (contract,subject) violations are suppressed.

No em dashes anywhere (house rule).
"""
import json
import os
import re
import struct
import sys
import zlib
from collections import OrderedDict, Counter
from pathlib import Path


# ============================================================================
# Section 1: minimal, read-only .arc loader (copied, not imported)
# ============================================================================
class _ArcEntry:
    __slots__ = ('entry_type', 'comp_size', 'decomp_size', 'num_parts',
                 'file_index', 'name', 'parts')


class Arc:
    """Read-only TQ .arc archive: enough to decompress named files + the map."""

    def __init__(self):
        self.entries = []

    @classmethod
    def from_file(cls, path):
        arc = cls()
        raw = Path(path).read_bytes()
        assert raw[0:4] == b'ARC\x00', f'not an .arc: {path}'
        num_entries = struct.unpack_from('<I', raw, 8)[0]
        num_data = struct.unpack_from('<I', raw, 0x0C)[0]
        toc_size = struct.unpack_from('<I', raw, 0x10)[0]
        string_size = struct.unpack_from('<I', raw, 0x14)[0]
        toc_offset = struct.unpack_from('<I', raw, 0x18)[0]
        string_start = toc_offset + toc_size
        records_start = string_start + string_size
        st = raw[string_start:string_start + string_size]
        names_by_off = {}
        pos = 0
        while pos < len(st):
            nul = st.find(b'\x00', pos)
            if nul < 0:
                break
            nm = st[pos:nul].decode('utf-8', 'replace')
            if nm:
                names_by_off[pos] = nm
            pos = nul + 1
        toc = []
        for i in range(num_data):
            tp = toc_offset + i * 12
            off = struct.unpack_from('<I', raw, tp)[0]
            comp = struct.unpack_from('<I', raw, tp + 4)[0]
            decomp = struct.unpack_from('<I', raw, tp + 8)[0]
            toc.append((off, comp, decomp, raw[off:off + comp]))
        for i in range(num_entries):
            rp = records_start + i * 44
            e = _ArcEntry()
            e.entry_type = struct.unpack_from('<I', raw, rp)[0]
            e.comp_size = struct.unpack_from('<I', raw, rp + 8)[0]
            e.decomp_size = struct.unpack_from('<I', raw, rp + 12)[0]
            e.num_parts = struct.unpack_from('<I', raw, rp + 28)[0]
            e.file_index = struct.unpack_from('<I', raw, rp + 32)[0]
            str_off = struct.unpack_from('<I', raw, rp + 40)[0]
            e.name = names_by_off.get(str_off, '')
            e.parts = []
            if e.entry_type == 3 and e.num_parts > 0:
                for pi in range(e.num_parts):
                    if e.file_index + pi < len(toc):
                        e.parts.append(toc[e.file_index + pi])
            arc.entries.append(e)
        return arc

    @staticmethod
    def _inflate(data):
        for wbits in (15, -15, zlib.MAX_WBITS):
            try:
                return zlib.decompress(data, wbits)
            except zlib.error:
                continue
        return zlib.decompress(data)

    def decompress(self, entry):
        out = bytearray()
        for _off, comp, decomp, data in entry.parts:
            out += data if comp == decomp else self._inflate(data)
        return bytes(out)

    def world_map(self):
        """The world01.map blob = first type-3 entry (matches project tooling)."""
        cands = [e for e in self.entries if e.entry_type == 3]
        for e in cands:
            if e.name.lower().endswith('world01.map'):
                return self.decompress(e)
        return self.decompress(cands[0])

    def get_file(self, name):
        for e in self.entries:
            if e.entry_type == 3 and e.name.lower() == name.lower():
                return self.decompress(e)
        return None

    def text_keys(self):
        """Union of all key= definitions across every .txt file in the arc."""
        keys = set()
        values = {}
        for e in self.entries:
            if e.entry_type != 3 or not e.name.lower().endswith('.txt'):
                continue
            raw = self.decompress(e)
            if raw[:2] == b'\xff\xfe':
                txt = raw[2:].decode('utf-16-le', 'replace')
            elif raw[:3] == b'\xef\xbb\xbf':
                txt = raw[3:].decode('utf-8', 'replace')
            else:
                txt = raw.decode('utf-8', 'replace')
            for line in txt.split('\n'):
                line = line.strip('\r').strip()
                if not line or line.startswith('//') or '=' not in line:
                    continue
                k, _, v = line.partition('=')
                k = k.strip()
                keys.add(k)
                values.setdefault(k, v.strip())
        return keys, values


# ============================================================================
# Section 2: minimal, read-only .arz loader (copied, not imported)
# ============================================================================
class Arz:
    """Read-only .arz: record names, per-record Class string, and field decode."""

    def __init__(self):
        self.strings = []
        self._raw = OrderedDict()        # name -> compressed bytes
        self._class = {}                 # name -> record_type (Class) string
        self._fields_cache = {}

    @classmethod
    def from_arz(cls, path):
        db = cls()
        raw = Path(path).read_bytes()
        magic, _ver, rt_off, _rt_size, rt_count, st_off, st_size = \
            struct.unpack_from('<HHiiiii', raw, 0)
        is_tqit = (magic == 2)
        st = raw[st_off:st_off + st_size]
        pos = 0
        n = struct.unpack_from('<i', st, 0)[0]
        pos = 4
        for _ in range(n):
            ln = struct.unpack_from('<i', st, pos)[0]
            pos += 4
            db.strings.append(st[pos:pos + ln].decode('latin-1'))
            pos += ln
        pos = rt_off
        for _ in range(rt_count):
            name_id = struct.unpack_from('<i', raw, pos)[0]
            pos += 4
            tlen = struct.unpack_from('<i', raw, pos)[0]
            pos += 4
            rtype = raw[pos:pos + tlen].decode('latin-1')
            pos += tlen
            data_off = struct.unpack_from('<i', raw, pos)[0]
            pos += 4
            csize = struct.unpack_from('<i', raw, pos)[0]
            pos += 4
            if is_tqit:
                pos += 4
            pos += 8  # timestamp
            name = db.strings[name_id] if name_id < len(db.strings) else f'?{name_id}'
            abs_off = 24 + data_off
            db._raw[name] = raw[abs_off:abs_off + csize]
            db._class[name] = rtype
        return db

    def record_names(self):
        return list(self._raw.keys())

    def record_class(self):
        return self._class

    @staticmethod
    def _inflate(data):
        for wbits in (15, -15, zlib.MAX_WBITS):
            try:
                return zlib.decompress(data, wbits)
            except zlib.error:
                continue
        try:
            return zlib.decompress(data[2:], -15)
        except zlib.error:
            return data

    def get_fields(self, name):
        if name in self._fields_cache:
            return self._fields_cache[name]
        if name not in self._raw:
            return None
        raw = self._inflate(self._raw[name])
        fields = {}
        pos = 0
        while pos + 8 <= len(raw):
            dtype = struct.unpack_from('<H', raw, pos)[0]
            num = struct.unpack_from('<H', raw, pos + 2)[0]
            var_id = struct.unpack_from('<i', raw, pos + 4)[0]
            pos += 8
            vname = self.strings[var_id] if var_id < len(self.strings) else f'?{var_id}'
            vals = []
            ok = True
            for _ in range(num):
                if pos + 4 > len(raw):
                    ok = False
                    break
                if dtype == 1:
                    vals.append(struct.unpack_from('<f', raw, pos)[0])
                elif dtype == 2:
                    sid = struct.unpack_from('<i', raw, pos)[0]
                    vals.append(self.strings[sid] if sid < len(self.strings) else f'?{sid}')
                else:
                    vals.append(struct.unpack_from('<i', raw, pos)[0])
                pos += 4
            if vname not in fields:
                fields[vname] = vals
            if not ok:
                break
        self._fields_cache[name] = fields
        return fields

    def field(self, name, field):
        f = self.get_fields(name)
        if not f or field not in f or not f[field]:
            return None
        v = f[field]
        return v[0] if len(v) == 1 else v


# ============================================================================
# Section 3: world01.map section + level-blob parsers (self-contained)
# ============================================================================
SEC_LEVELS = 0x01
SEC_GROUPS = 0x11
SEC_SD = 0x18
SEC_QUESTS = 0x1B


def parse_top_sections(data):
    """Top-level world01.map sections: type(4)+size(4)+data, from offset 8."""
    secs = {}
    pos = 8
    while pos + 8 <= len(data):
        st = struct.unpack_from('<I', data, pos)[0]
        ss = struct.unpack_from('<I', data, pos + 4)[0]
        if ss > len(data) - pos - 8:
            break
        secs[st] = (pos + 8, ss)
        pos += 8 + ss
    return secs


def sec_bytes(data, secs, t):
    if t not in secs:
        return b''
    off, size = secs[t]
    return data[off:off + size]


def parse_level_index(buf):
    """LEVELS(0x01): count then per level ints_raw(52)+dbr+fname+dataoff+datalen."""
    count = struct.unpack_from('<I', buf, 0)[0]
    levels = []
    idx = 4
    for _ in range(count):
        ints_raw = buf[idx:idx + 52]
        idx += 52
        dl = struct.unpack_from('<I', buf, idx)[0]
        idx += 4
        idx += dl  # dbr
        fl = struct.unpack_from('<I', buf, idx)[0]
        idx += 4
        fname = buf[idx:idx + fl]
        idx += fl
        do = struct.unpack_from('<I', buf, idx)[0]
        idx += 4
        dlen = struct.unpack_from('<I', buf, idx)[0]
        idx += 4
        levels.append({
            'ints_raw': ints_raw,
            'fname': fname.decode('ascii', 'replace'),
            'guid': ints_raw[36:52],
            'corner': struct.unpack_from('<iii', ints_raw, 24),
            'data_offset': do, 'data_length': dlen,
        })
    return levels


def parse_quests(buf):
    """QUESTS(0x1b): count then count x (u32 len + name bytes)."""
    if len(buf) < 4:
        return []
    n = struct.unpack_from('<I', buf, 0)[0]
    out = []
    pos = 4
    for _ in range(n):
        if pos + 4 > len(buf):
            break
        ln = struct.unpack_from('<I', buf, pos)[0]
        pos += 4
        out.append(buf[pos:pos + ln])
        pos += ln
    return out


def parse_blob_sections(blob):
    """Level-blob internal sections: magic(4) then type(4)+size(4)+data."""
    secs = []
    if len(blob) < 4:
        return secs
    pos = 4
    while pos + 8 <= len(blob):
        st = struct.unpack_from('<I', blob, pos)[0]
        ss = struct.unpack_from('<I', blob, pos + 4)[0]
        if ss > len(blob) - pos - 8:
            break
        secs.append((st, blob[pos + 8:pos + 8 + ss]))
        pos += 8 + ss
    return secs


def blob_section_types(blob):
    return set(t for t, _ in parse_blob_sections(blob))


def parse_0x05(blob):
    """0x05 placed-instance section. Returns (strings, instances).

    instance = {i, dbr(bytes), flags, uid(bytes|None)}. Record size = 72 for
    blob version 0x11/0x0f, else 56; a flagged (flags!=0) record carries a
    trailing 16-byte UniqueId.
    """
    ver = blob[3]
    base = 72 if ver in (0x11, 0x0f) else 56
    d = None
    for t, sd in parse_blob_sections(blob):
        if t == 0x05:
            d = sd
            break
    if d is None:
        return [], []
    pos = 0
    sc = struct.unpack_from('<I', d, 0)[0]
    pos = 4
    strings = []
    for _ in range(sc):
        if pos + 4 > len(d):
            return strings, []
        sl = struct.unpack_from('<I', d, pos)[0]
        pos += 4
        strings.append(d[pos:pos + sl])
        pos += sl
    if pos + 4 > len(d):
        return strings, []
    ic = struct.unpack_from('<I', d, pos)[0]
    pos += 4
    insts = []
    for i in range(ic):
        if pos + base > len(d):
            break
        sidx = struct.unpack_from('<I', d, pos)[0]
        flags = struct.unpack_from('<I', d, pos + 52)[0]
        uid = d[pos + 56:pos + 72] if flags != 0 else None
        insts.append({'i': i, 'dbr': strings[sidx] if sidx < len(strings) else b'?',
                      'flags': flags, 'uid': uid})
        pos += base + (16 if flags != 0 else 0)
    return strings, insts


def parse_0x14(d):
    """0x14 per-instance metadata: {instance_index: payload_bytes}."""
    recs = {}
    pos = 0
    while pos + 8 <= len(d):
        idx = struct.unpack_from('<I', d, pos)[0]
        psz = struct.unpack_from('<I', d, pos + 4)[0]
        if pos + 8 + psz > len(d):
            break
        recs[idx] = d[pos + 8:pos + 8 + psz]
        pos += 8 + psz
    return recs


def blob_0x14_map(blob):
    for t, sd in parse_blob_sections(blob):
        if t == 0x14:
            return parse_0x14(sd)
    return {}


# --- GROUPS(0x11): record list; member block = member_count x 44B --------------
def _groups_next_record(data, start, end_limit):
    for scan in range(start, min(end_limit, len(data) - 12)):
        if struct.unpack_from('<I', data, scan)[0] > 20:
            continue
        slen = struct.unpack_from('<I', data, scan + 4)[0]
        if slen < 3 or slen > 200 or scan + 8 + slen > len(data):
            continue
        if not all(32 <= b < 127 for b in data[scan + 8:scan + 8 + slen]):
            continue
        p2 = scan + 8 + slen
        if p2 + 4 > len(data):
            continue
        s2 = struct.unpack_from('<I', data, p2)[0]
        if s2 < 3 or s2 > 200 or p2 + 4 + s2 > len(data):
            continue
        if all(32 <= b < 127 for b in data[p2 + 4:p2 + 4 + s2]):
            return scan
    return None


def parse_groups(data):
    """GROUPS(0x11): [u32 val0][u32 count] then per record:
    [u32 sub_count][lp name][lp category][u32 member_count][member block].
    Member block = member_count x 44B record = uid(16)+level_guid(16)+pos(12).
    """
    if len(data) < 8:
        return []
    _val0, count = struct.unpack_from('<II', data, 0)
    pos = 8
    recs = []
    for i in range(count):
        if pos + 4 > len(data):
            break
        sub = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        nl = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        name = data[pos:pos + nl].decode('ascii', 'replace')
        pos += nl
        cl = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        cat = data[pos:pos + cl].decode('ascii', 'replace')
        pos += cl
        mc = struct.unpack_from('<I', data, pos)[0]
        pos += 4
        ds = pos
        if i < count - 1:
            nxt = _groups_next_record(data, pos, pos + 200000)
            dl = (nxt - pos) if nxt else (len(data) - pos)
        else:
            dl = len(data) - pos
        recs.append({'sub_count': sub, 'name': name, 'category': cat,
                     'member_count': mc, 'raw': data[ds:ds + dl]})
        pos = ds + dl
    return recs


# --- REC\x02 (0x0b) navmesh container header ----------------------------------
def rec02_header(d):
    """Parse just the REC\\x02 container header. Returns dict or raises on bad."""
    if d[:4] != b'REC\x02':
        raise ValueError('bad magic')
    version, payload_size, guid_count = struct.unpack_from('<3I', d, 4)
    guids = [d[16 + i * 16:16 + (i + 1) * 16] for i in range(guid_count)]
    return {'version': version, 'payload_size': payload_size,
            'guid_count': guid_count, 'guids': guids, 'total': len(d)}


# --- REC\x02 (0x0b) FULL container structure walk (MAP-NAV-5) ------------------
# A header-only parse cannot see the defect that killed two runtime sessions on
# 2026-07-27 (b89): the dead Approach-22 148-byte stub had a perfectly valid header
# (version 1, correct payload_size, guid_count 3, every GUID resolving) but a BODY
# holding ONE TRUNCATED tileset instead of the three complete ones the engine parses,
# so ProcessRLTD ran off the end of the section into the heap. This walk covers the
# body the same way tools/rec02_format.parse_rec02 does (that parser is proven by
# byte-identical round-trips over 670 real sections) but never raises on bad input.
REC02_PARAMS_LEN = 52          # dtTileCacheParams
REC02_TILESET_HDR = REC02_PARAMS_LEN + 4   # + int32 numTiles
REC02_N_SETS = 3               # Normal / Epic / Legendary - engine requires all three
REC02_TILE_MAGIC = b'RLTD'     # dtTileCacheLayerHeader magic ('DTLR' as int32)


def rec02_structure(d):
    """Walk a whole REC\\x02 section. Returns (errors, sets) - errors is a list of
    human-readable structural defects, empty iff the container is well-formed."""
    errs = []
    if len(d) < 16 or d[:4] != b'REC\x02':
        return (['bad REC\\x02 magic'], [])
    guid_count = struct.unpack_from('<I', d, 12)[0]
    pos = 16 + guid_count * 16 + 24                     # guids + center + dims
    if guid_count > 64 or pos > len(d):
        return ([f'guid_count={guid_count} does not fit in a {len(d)}-byte section'], [])
    sets = []
    while pos < len(d):
        if pos + REC02_TILESET_HDR > len(d):
            errs.append(f'tileset #{len(sets) + 1} TRUNCATED: {len(d) - pos} bytes '
                        f'left, a tileset header needs {REC02_TILESET_HDR}')
            break
        num_tiles = struct.unpack_from('<i', d, pos + REC02_PARAMS_LEN)[0]
        max_tiles, max_obstacles = struct.unpack_from('<2i', d, pos + 44)
        sets.append({'numTiles': num_tiles, 'maxTiles': max_tiles,
                     'maxObstacles': max_obstacles})
        pos += REC02_TILESET_HDR
        if not (0 <= num_tiles <= 100000):
            errs.append(f'tileset #{len(sets)} has an out-of-range numTiles={num_tiles}')
            break
        broke = False
        for t in range(num_tiles):
            if pos + 4 > len(d):
                errs.append(f'tileset #{len(sets)} tile {t}: truncated dataSize')
                broke = True
                break
            dsize = struct.unpack_from('<i', d, pos)[0]
            pos += 4
            if dsize < 56 or pos + dsize + 8 > len(d):
                errs.append(f'tileset #{len(sets)} tile {t}: bad dataSize={dsize} '
                            f'({len(d) - pos} bytes remain)')
                broke = True
                break
            if d[pos:pos + 4] != REC02_TILE_MAGIC:
                errs.append(f'tileset #{len(sets)} tile {t}: bad dtTileCacheLayerHeader '
                            f'magic {d[pos:pos + 4]!r} (expected {REC02_TILE_MAGIC!r})')
                broke = True
                break
            pos += dsize + 8                            # data + trailing tx,ty
        if broke:
            break
    if not errs:
        if len(sets) != REC02_N_SETS:
            errs.append(f'{len(sets)} tileset(s); the engine loads exactly '
                        f'{REC02_N_SETS} (Normal/Epic/Legendary)')
        if pos != len(d):
            errs.append(f'{len(d) - pos} trailing byte(s) after the last tileset')
    return (errs, sets)


# --- SD(0x18) tag scan ---------------------------------------------------------
def sd_tag_refs(sd):
    """Length-prefixed ASCII strings in the SD section that are display-tag
    references (tag* / xtag*). Returns list of (offset, tag)."""
    out = []
    pos = 0
    n = len(sd)
    while pos + 4 <= n:
        ln = struct.unpack_from('<I', sd, pos)[0]
        if 2 <= ln <= 96 and pos + 4 + ln <= n:
            s = sd[pos + 4:pos + 4 + ln]
            if re.fullmatch(rb'[\x20-\x7e]+', s):
                txt = s.decode('ascii')
                low = txt.lower()
                if low.startswith('tag') or low.startswith('xtag'):
                    out.append((pos, txt))
                pos += 4 + ln
                continue
        pos += 1
    return out


# ============================================================================
# Section 4: shared helpers
# ============================================================================
def norm_rec(p):
    """Normalize a .dbr reference to arz-record key form (backslash, lower)."""
    if isinstance(p, bytes):
        p = p.decode('latin-1')
    return p.replace('/', '\\').strip().lower()


# Declared-unreachable-by-design levels: EXACT basenames, never substrings.
# See docs/CUT_CONTENT.md for the per-level justification.
#
# HISTORY (BL-b89-DEBT-3, corrected 2026-07-28): this used to be a SUBSTRING tuple
# ('ocean_extension', 'coldtombs'), which swept the WHOLE ocean_extension family into
# the exemption. That was factually wrong and it is how the malformed-container class
# hid for weeks: `ocean_extension01`-`04`, `x02` and `x08` carry REAL generated
# navmeshes (397KB/232KB/238KB/165KB/106KB/56KB, 531/318/294/237/141/75 tiles) and are
# listed as area-owners inside `drxBC3`'s and `drxBC_Finale`'s navmesh GUID lists -
# i.e. the player walks on cells those meshes own. Only the 8 genuinely geometry-less
# members below (0 tiles in all three tilesets, and no other mesh lists their GUID)
# are cut. Proven on the shipped map by tools/audit_navmesh_guid_lists.py; the
# live-vs-dead split is asserted by _negtest_map.test_cut_levels().
#
# NOTE this exemption is deliberately NARROW and is only consulted by MAP-NAV-3.
# MAP-NAV-1/-4/-5/-6 ignore cut-ness BY DESIGN: a cut level still streams in by grid
# proximity, so its container must still be structurally valid (that is the whole b89
# lesson - "declared cut" buys nothing at runtime).
CUT_LEVELS = frozenset({
    # Ocean scenery tiles with no walkable floor (no 0x0a geometry to rasterize).
    'ocean_extension05',
    'ocean_extensionx01',
    'ocean_extensionx03',
    'ocean_extensionx04',
    'ocean_extensionx05',
    'ocean_extensionx06',
    'ocean_extensionx07',
    # Cold Tombs: SV shipped it with no 0x0a pathing layer at all (ON HOLD per Will,
    # task #36 - do NOT retire the level, the hold is a design question not a deletion).
    'coldtombs',
})


def level_basename(fname):
    """'Levels\\World\\xBloodCave\\ocean_extension05.lvl' -> 'ocean_extension05'."""
    if isinstance(fname, bytes):
        fname = fname.decode('latin-1')
    b = fname.replace('\\', '/').split('/')[-1]
    if b.lower().endswith('.lvl'):
        b = b[:-4]
    return b.lower()


def is_cut(fname):
    return level_basename(fname) in CUT_LEVELS


def V(cid, sev, subject, message, evidence):
    return {'contract': cid, 'severity': sev, 'subject': subject,
            'message': message, 'evidence': evidence}


# ============================================================================
# Section 5: shared load context
# ============================================================================
class Ctx:
    def __init__(self, cfg):
        self.cfg = cfg
        # merged world map
        self.map_data = Arc.from_file(cfg['levels_arc']).world_map()
        self.secs = parse_top_sections(self.map_data)
        self.levels = parse_level_index(sec_bytes(self.map_data, self.secs, SEC_LEVELS))
        self.level_guids = set(lv['guid'] for lv in self.levels)
        self.merged_quests = parse_quests(sec_bytes(self.map_data, self.secs, SEC_QUESTS))
        self._blob_cache = {}
        # arz (mod)
        self.arz = Arz.from_arz(cfg['arz'])
        self.arz_names = set(norm_rec(n) for n in self.arz.record_names())
        self.arz_class = {norm_rec(n): t for n, t in self.arz.record_class().items()}
        # base game (optional but expected)
        self.base_arz = None
        self.base_arz_names = set()
        self.base_class = {}
        self.base_quests = None
        # Own-GUID set of every level in the STOCK base-game Levels.arc. Used by
        # MAP-NAV-4 to tell SV-custom (grid-shifted, our-generated) levels from
        # inherited base/IT/XPack levels by PROVENANCE (a base level's GUID is in
        # this set); empty if the base map could not be loaded.
        self.base_level_guids = set()
        bg = cfg.get('base_game_dir')
        if bg:
            bg = Path(bg)
            barz = bg / 'Database' / 'database.arz'
            if barz.exists():
                self.base_arz = Arz.from_arz(barz)
                self.base_arz_names = set(norm_rec(n) for n in self.base_arz.record_names())
                self.base_class = {norm_rec(n): t for n, t in self.base_arz.record_class().items()}
            blv = bg / 'Resources' / 'Levels.arc'
            if blv.exists():
                try:
                    bmap = Arc.from_file(blv).world_map()
                    bsecs = parse_top_sections(bmap)
                    self.base_quests = parse_quests(sec_bytes(bmap, bsecs, SEC_QUESTS))
                    self.base_level_guids = set(
                        lv['guid'] for lv in parse_level_index(
                            sec_bytes(bmap, bsecs, SEC_LEVELS)))
                except Exception:
                    self.base_quests = None
        # text keys (mod union base)
        mk, mv = Arc.from_file(cfg['text_arc']).text_keys()
        self.text_keys = set(mk)
        self.text_values = dict(mv)
        if bg:
            btxt = Path(bg) / 'Text' / 'Text_EN.arc'
            if btxt.exists():
                bk, bv = Arc.from_file(btxt).text_keys()
                self.text_keys |= bk
                for k, v in bv.items():
                    self.text_values.setdefault(k, v)
        # all placed flagged instance uids (for GROUPS binding checks)
        self._all_uids = None

    def blob(self, lv):
        key = lv['data_offset']
        b = self._blob_cache.get(key)
        if b is None:
            b = self.map_data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
            self._blob_cache[key] = b
        return b

    def all_instance_uids(self):
        if self._all_uids is None:
            s = set()
            for lv in self.levels:
                for it in parse_0x05(self.blob(lv))[1]:
                    if it['uid']:
                        s.add(it['uid'])
            self._all_uids = s
        return self._all_uids

    def rec_resolves(self, norm_path):
        return norm_path in self.arz_names or norm_path in self.base_arz_names

    def class_of(self, norm_path):
        return self.arz_class.get(norm_path) or self.base_class.get(norm_path)


# ============================================================================
# Section 6: the contracts
# ============================================================================
SV_PORTED_QUESTS = ('widowletter', 'urder', 'bossarena', 'open_bloodcave_portal')
QUEST_LOAD_WINDOW = 254   # engine loads QUESTS entries at index < 254 (docs/QUEST_STATE_INJECT.md)
ENTRANCE_CLASSES = {'GridEntrance', 'GridEntranceDynamic', 'FixedItemTeleport'}
LANDING_CLASSES = {'GridExitOneWay'}
GRIDENTRANCE_PREFIX = struct.pack('<III', 2, 0, 1)   # (2,0,1) 12B static-GridEntrance 0x14 prefix
SHRINE_BIND_CATEGORIES = {'RespawnShrine', 'TeleportShrine'}
# Our invented cross-level portals reuse these two records (docs/DYNGRID_GATE_RCA.md):
OUR_PORTAL_MARKERS = ('olympianarena',)


def _is_our_content(npath, blob_has_drxmap):
    """True if a placed record belongs to OUR restored/SV content (not vanilla).

    Vanilla / DLC placements are engine-tolerated and out of scope for the hard
    (gating) severities; ours must be correct. A record is "ours" if it is an
    SV-namespace record, one of our invented portal records, or it sits in an
    SV drxmap level blob.
    """
    if blob_has_drxmap:
        return True
    if any(m in npath for m in OUR_PORTAL_MARKERS):
        return True
    return any(m in npath for m in SV_NAMESPACE_MARKERS)


# Restored-area zone display tags (as referenced in the SD section) mapped to the
# keyword(s) their visible label MUST contain (the intended region name). This is
# the oracle for the "restored area mislabeled with another zone's name" defect
# (B-AREA-NAME-1). Derived from the shipped restored-area zone-tag families
# (tagMZone*/tagBCX*/tagSP*/tagNewMZone*); extend when a new restored area is added.
RESTORED_ZONE_LABEL_EXPECT = {
    'tagMZoneGoM': ('garden', 'merchant'),   # Garden of Merchants (currently -> "Duister")
}


def _qname(qb):
    return qb.decode('ascii', 'replace').replace('\\', '/')


def contract_quests(ctx):
    """(1) QUESTS section: <=256 entries; SV-ported quests inside the load
    window (idx < 254); boundary entries (254,255) match vanilla parity."""
    v = []
    q = ctx.merged_quests
    n = len(q)
    if n > 256:
        v.append(V('MAP-QUESTS-1', 'P1', 'world01.map/QUESTS',
                   f'QUESTS has {n} entries, exceeds the 256 load window',
                   f'count={n} > 256 (vanilla count)'))
    # SV-ported quest load-window
    lc = [_qname(x).lower() for x in q]
    for sv in SV_PORTED_QUESTS:
        target = f'quests/{sv}.qst'
        idxs = [i for i, name in enumerate(lc)
                if name == target or name.endswith('/' + sv + '.qst') or name == sv + '.qst']
        if not idxs:
            v.append(V('MAP-QUESTS-2', 'P0', f'QUESTS/{sv}',
                       f'ported SV quest {sv}.qst is not registered in QUESTS',
                       f'no entry matching quests/{sv}.qst'))
        elif min(idxs) >= QUEST_LOAD_WINDOW:
            v.append(V('MAP-QUESTS-2', 'P0', f'QUESTS/{sv}',
                       f'ported SV quest {sv}.qst sits at idx {min(idxs)} >= '
                       f'{QUEST_LOAD_WINDOW}; engine never loads it (never tracks)',
                       f'min index={min(idxs)}; forms={[q[i].decode("ascii","replace") for i in idxs]}'))
    # boundary parity vs vanilla
    if ctx.base_quests and len(ctx.base_quests) >= 256 and n >= 256:
        for bi in (254, 255):
            ours = q[bi] if bi < n else b''
            van = ctx.base_quests[bi]
            if ours != van:
                v.append(V('MAP-QUESTS-3', 'P1', f'world01.map/QUESTS[{bi}]',
                           f'QUESTS boundary entry {bi} differs from vanilla parity',
                           f'ours={ours.decode("ascii","replace")!r} vanilla={van.decode("ascii","replace")!r}'))
    return v


def _collect_portals(ctx):
    """Two-pass: return (entrances, landing_mouths, entrance_mouths, need_06).
    entrance = dict(fname, idx, rec, cls, mouth, exit, dest, size)."""
    entrances = []
    landing_mouths = set()
    entrance_mouths = []
    for lv in ctx.levels:
        blob = ctx.blob(lv)
        _s, insts = parse_0x05(blob)
        if not insts:
            continue
        x14 = blob_0x14_map(blob)
        if not x14:
            continue
        drx = b'drxmap' in blob
        for it in insts:
            npath = norm_rec(it['dbr'])
            cls = ctx.class_of(npath)
            if cls not in ENTRANCE_CLASSES and cls not in LANDING_CLASSES:
                continue
            pl = x14.get(it['i'])
            if not pl:
                continue
            if len(pl) == 60 and pl[:12] == GRIDENTRANCE_PREFIX:
                binding = pl[12:]
            elif len(pl) == 48:
                binding = pl
            else:
                continue
            if len(binding) != 48:
                continue
            mouth, exit_, dest = binding[0:16], binding[16:32], binding[32:48]
            if cls in LANDING_CLASSES or dest == b'\x00' * 16:
                landing_mouths.add(mouth)
            else:
                entrances.append({'fname': lv['fname'], 'idx': it['i'],
                                  'rec': npath.split('\\')[-1], 'cls': cls,
                                  'mouth': mouth, 'exit': exit_, 'dest': dest,
                                  'size': len(pl),
                                  'ours': _is_our_content(npath, drx)})
                entrance_mouths.append(mouth)
    return entrances, landing_mouths, entrance_mouths


def contract_portals(ctx):
    """(2) Every portal mouth has a resolvable destination GUID and a paired
    landing/exit; no dangling or colliding mouth UIDs."""
    v = []
    entrances, landing_mouths, entrance_mouths = _collect_portals(ctx)
    entrance_mouth_set = set(entrance_mouths)
    # MAP-PORTAL-1: dest GUID resolves. Ours = P0 (reachable, must work); a
    # native/DLC dangling portal (unreachable base content) is reported at P2.
    for e in entrances:
        if e['dest'] not in ctx.level_guids:
            sev = 'P0' if e['ours'] else 'P2'
            tag = '' if e['ours'] else ' [native/DLC content, informational]'
            v.append(V('MAP-PORTAL-1', sev,
                       f'{e["fname"]}#0x05[{e["idx"]}] {e["rec"]}',
                       'portal entrance destination GUID resolves to no level in the world' + tag,
                       f'dest={e["dest"].hex()} not in {len(ctx.level_guids)} level GUIDs'))
    # MAP-PORTAL-2: mouth UID collisions
    mc = Counter(entrance_mouths)
    for mouth, cnt in mc.items():
        if cnt > 1:
            who = [f'{e["fname"].split("/")[-1]}#{e["idx"]}' for e in entrances if e['mouth'] == mouth]
            v.append(V('MAP-PORTAL-2', 'P1', f'mouth {mouth.hex()[:16]}',
                       f'portal mouth UID shared by {cnt} entrances (collision)',
                       f'entrances={who[:6]}'))
    # MAP-PORTAL-3: exit paired via landing OR 0x06 reciprocal OR bidirectional mouth
    unresolved_exits = []
    for e in entrances:
        ex = e['exit']
        if ex in landing_mouths:
            continue
        if ex in entrance_mouth_set and ex != e['mouth']:
            continue
        unresolved_exits.append(e)
    if unresolved_exits:
        # only these need the (expensive) 0x06 scan; build once
        blob06 = b''.join(sd for lv in ctx.levels for t, sd in parse_blob_sections(ctx.blob(lv)) if t == 0x06)
        for e in unresolved_exits:
            if blob06.find(e['exit']) >= 0:
                continue
            sev = 'P1' if e['ours'] else 'P2'
            tag = '' if e['ours'] else ' [native/DLC content, informational]'
            v.append(V('MAP-PORTAL-3', sev,
                       f'{e["fname"]}#0x05[{e["idx"]}] {e["rec"]}',
                       'portal entrance exit UID has no paired landing / 0x06 reciprocal (dangling hop)' + tag,
                       f'exit={e["exit"].hex()} dest={e["dest"].hex()[:16]}'))
    return v


def contract_navmesh(ctx):
    """(3) Every walkable restored level carries a valid 0x0b RLTD navmesh whose
    GUID list resolves in the merged world; no level keeps a stale 0x0a.

    NAV-1 header sanity + GUID resolvability, NAV-2 no stale 0x0a beside a 0x0b,
    NAV-3 restored SV level must have a navmesh, NAV-5 the container BODY is exactly
    three complete tilesets (b89), NAV-6 the GUID list is not self-duplicated (b89).
    NAV-5/NAV-6 apply to EVERY level including declared-cut ones: the engine streams a
    level by grid proximity whether or not the design calls it reachable, so a
    malformed container in a "cut" level is still a live crash."""
    v = []
    for lv in ctx.levels:
        blob = ctx.blob(lv)
        types = {}
        for t, sd in parse_blob_sections(blob):
            types.setdefault(t, sd)
        has_0a = 0x0a in types
        has_0b = 0x0b in types
        fname = lv['fname']
        # NAV-1: 0x0b container valid + all GUIDs resolve
        if has_0b:
            d = types[0x0b]
            try:
                h = rec02_header(d)
            except Exception as ex:
                v.append(V('MAP-NAV-1', 'P0', fname,
                           'level 0x0b navmesh has a malformed REC\\x02 container',
                           f'parse error: {ex}; head={d[:8].hex()}'))
                h = None
            if h is not None:
                if h['version'] != 1:
                    v.append(V('MAP-NAV-1', 'P0', fname,
                               'navmesh REC\\x02 version != 1 (engine skips payload)',
                               f'version={h["version"]}'))
                if h['payload_size'] != h['total'] - 12:
                    v.append(V('MAP-NAV-1', 'P0', fname,
                               'navmesh payload_size mismatch (truncated/corrupt section)',
                               f'payload_size={h["payload_size"]} expected={h["total"] - 12}'))
                if not (1 <= h['guid_count'] <= 16):
                    v.append(V('MAP-NAV-1', 'P0', fname,
                               'navmesh GUID count out of sane range (1..16)',
                               f'guid_count={h["guid_count"]}'))
                else:
                    bad = [g.hex() for g in h['guids'] if g not in ctx.level_guids]
                    if bad:
                        v.append(V('MAP-NAV-1', 'P0', fname,
                                   'navmesh GUID list has entries that resolve to no loaded '
                                   'level; engine GUID-gate rejects the whole navmesh (invisible wall)',
                                   f'{len(bad)} unresolved of {h["guid_count"]}: {bad[:4]}'))
                    # NAV-6: DEGENERATE list - >1 entry, every entry the same GUID.
                    # Stock TQAE ships ZERO of these in 2235 levels; ours were the
                    # fingerprint of the malformed 148-byte stub (b89 crash).
                    if h['guid_count'] > 1 and len(set(h['guids'])) == 1:
                        v.append(V('MAP-NAV-6', 'P0', fname,
                                   'navmesh GUID list is DEGENERATE (every entry is the same '
                                   'GUID); stock ships no such list and ours only ever came '
                                   'from a malformed generated container',
                                   f'guid_count={h["guid_count"]} all == '
                                   f'{h["guids"][0].hex()}'))
            # NAV-5: the container BODY must be exactly 3 complete tilesets and end
            # cleanly. A valid header over a truncated body is what ProcessRLTD reads
            # past the end of (b89: two Frida sessions died entering ocean_extension05).
            serrs, _sets = rec02_structure(d)
            if serrs:
                v.append(V('MAP-NAV-5', 'P0', fname,
                           'navmesh REC\\x02 container body is structurally invalid; '
                           'ProcessRLTD parses tilesets until the section ends, so a short '
                           'or malformed body makes it read past the section (crash on '
                           'stream-in)',
                           f'size={len(d)}: ' + '; '.join(serrs[:3])))
        # NAV-2: no level keeps both 0x0a and 0x0b (stale legacy not stripped)
        if has_0a and has_0b:
            v.append(V('MAP-NAV-2', 'P1', fname,
                       'level carries BOTH a legacy 0x0a PTH and a 0x0b RLTD navmesh '
                       '(stale 0x0a not stripped)',
                       'has 0x0a and 0x0b'))
        # NAV-3: SV/drxmap restored walkable level must have a 0x0b
        if b'drxmap' in blob and not is_cut(fname) and not has_0b:
            v.append(V('MAP-NAV-3', 'P1', fname,
                       'restored SV (drxmap) level has NO 0x0b navmesh; the TQAE engine '
                       'cannot pathfind it (invisible wall)',
                       f'has_0a={has_0a} bloblen={len(blob)}'))
    return v


def contract_groups(ctx):
    """(4) GROUPS respawn/teleport-binding records reference real map content:
    non-empty, structurally intact, and bound to at least one placed instance."""
    v = []
    gd = sec_bytes(ctx.map_data, ctx.secs, SEC_GROUPS)
    groups = parse_groups(gd)
    all_uids = ctx.all_instance_uids()
    for g in groups:
        if g['category'] not in SHRINE_BIND_CATEGORIES:
            continue
        mc = g['member_count']
        raw = g['raw']
        subj = f'GROUPS/{g["name"]} [{g["category"]}]'
        if mc < 1:
            v.append(V('MAP-GROUPS-1', 'P1', subj,
                       'respawn/teleport-binding group has zero members (dead binding)',
                       f'member_count={mc}'))
            continue
        if len(raw) < mc * 44:
            v.append(V('MAP-GROUPS-1', 'P1', subj,
                       'binding group member block is truncated (cannot hold member_count records)',
                       f'raw_len={len(raw)} < member_count*44={mc * 44}'))
            continue
        resolved = 0
        for k in range(mc):
            off = k * 44
            if raw[off:off + 16] in all_uids:
                resolved += 1
        if resolved == 0:
            v.append(V('MAP-GROUPS-1', 'P1', subj,
                       'binding group has NO member UID matching any placed map instance '
                       '(wholly stale binding; respawn/teleport point is inert)',
                       f'member_count={mc}, resolved=0'))
    return v


def contract_doors(ctx):
    """(5) Every locked FixedItemDoor placed in the map has a live unlock path:
    some quest in Quests.arc has Action_UnlockFixedItem naming its record."""
    v = []
    # 1. door record paths referenced by an unlock-bearing quest
    qarc = Arc.from_file(ctx.cfg['quests_arc'])
    unlock_refs = set()
    for e in qarc.entries:
        if e.entry_type != 3 or not e.name.lower().endswith('.qst'):
            continue
        data = qarc.decompress(e)
        if b'UnlockFixedItem' not in data:
            continue
        for m in re.finditer(rb'[ -~]{4,}\.dbr', data):
            unlock_refs.add(norm_rec(m.group(0)))
    # 2. every LOCKED placed FixedItemDoor that is OUR restored content, scoped by
    # the DOOR RECORD's SV namespace (records\drxmap\ / all_sv\ / \sv\ / svitems\),
    # NOT by "the level blob contains 'drxmap'". This scope-by-record is deliberate
    # and mirrors MAP-REF-1's _sv_scope guard: a base-game / DLC door record (e.g.
    # records\xpack\quests\objects\xsq06_leverdoora) is unlocked by its own
    # base-game lever/key/quest mechanic that the mod does not carry, so it must
    # stay out of scope wherever it is placed. The old blob-level "drxmap present"
    # heuristic misfired: injecting a lone drxmap proxy placement (a boss marker,
    # records\drxmap\proxy\q_*_lone) into a base xpack host put 'drxmap' in that
    # blob and reclassified its NATIVE xsq06 lever/key doors as "ours" -> false
    # P1s. Every genuine SV door record is SV-namespace (records\drxmap\bloodcave\*
    # / records\drxmap\xurder\*), so record-namespace scoping keeps the real
    # temple-door class (B-TEMPLE-DOOR-1) fully covered while being robust to any
    # placed-proxy injection into a base-game host level.
    door_records = {p for p, c in ctx.arz_class.items() if c == 'FixedItemDoor'}
    door_records |= {p for p, c in ctx.base_class.items() if c == 'FixedItemDoor'}
    seen = set()
    for lv in ctx.levels:
        blob = ctx.blob(lv)
        _s, insts = parse_0x05(blob)
        for it in insts:
            npath = norm_rec(it['dbr'])
            if npath not in door_records:
                continue
            if not any(m in npath for m in SV_NAMESPACE_MARKERS):
                continue
            locked = ctx.arz.field(npath, 'locked')
            if locked is None and ctx.base_arz is not None:
                locked = ctx.base_arz.field(npath, 'locked')
            if locked != 1:
                continue
            if npath in unlock_refs:
                continue
            key = (lv['fname'], npath)
            if key in seen:
                continue
            seen.add(key)
            v.append(V('MAP-DOOR-1', 'P1',
                       f'{lv["fname"]}#0x05[{it["i"]}] {npath.split(chr(92))[-1]}',
                       'locked FixedItemDoor placed in an SV/restored level has NO '
                       'Action_UnlockFixedItem referencing it in any quest (can never '
                       'unseal; the temple-door class)',
                       f'record={npath}; locked=1; not referenced by any UnlockFixedItem quest'))
    return v


def contract_sd_tags(ctx):
    """(6) SD zone display-name integrity: every tag-form display reference in
    the SD section resolves in Text.arc; flag cross-zone label collisions."""
    v = []
    sd = sec_bytes(ctx.map_data, ctx.secs, SEC_SD)
    refs = sd_tag_refs(sd)
    # MAP-SD-1: display tag resolves
    seen_unres = set()
    for _off, tag in refs:
        if tag not in ctx.text_keys and tag not in seen_unres:
            seen_unres.add(tag)
            v.append(V('MAP-SD-1', 'P1', f'SD tag {tag}',
                       'SD zone display tag does not resolve to any Text.arc string '
                       '(raw tag would render as the region label)',
                       f'{tag} absent from Text.arc (mod+base, {len(ctx.text_keys)} keys)'))
    # MAP-SD-2: restored-area zone-label sanity (the Garden-labeled-Duister class).
    # Base-game region labels duplicate legitimately (many sub-areas share a name),
    # so a blind collision check false-positives. Instead we scope to the labels WE
    # authored for restored areas (RESTORED_ZONE_LABEL_EXPECT, keyed on the SD-
    # referenced display tag) and assert the visible label actually names that area.
    # tagMZoneGoM (the Garden-of-Merchants zone) currently resolves to "Duister"
    # (the Secret Place's name) - exactly B-AREA-NAME-1.
    referenced = {tag for _off, tag in refs}
    for tag, expect in RESTORED_ZONE_LABEL_EXPECT.items():
        if tag.lower() not in {t.lower() for t in referenced}:
            continue
        # find the actual referenced tag (preserve original case) + its value
        actual = next((t for _o, t in refs if t.lower() == tag.lower()), tag)
        val = ctx.text_values.get(actual)
        if val is None:
            continue   # unresolved is MAP-SD-1's job
        low = val.strip().lower()
        if not any(kw in low for kw in expect):
            v.append(V('MAP-SD-2', 'P2', f'SD tag {actual}',
                       'restored-area zone display tag resolves to a label that does not name '
                       'its area (a restored area mislabeled with another zone name)',
                       f'{actual} = {val!r}; expected the label to contain one of {list(expect)}'))
    return v


SV_NAMESPACE_MARKERS = ('all_sv\\', 'drxmap\\', '\\sv\\', 'records\\sv', 'svitems\\')


def _sv_scope(npath, blob_has_drxmap):
    return blob_has_drxmap or any(m in npath for m in SV_NAMESPACE_MARKERS)


# --- blood-cave crash cluster (b82): the SV blood-cave levels + entrance/host ---
# Substring match on the level fname. Kept in sync with
# tools/contracts/gate_placed_record_resolution.py (the standalone diagnostic).
BLOODCAVE_SUBSTRINGS = (
    'xbloodcave', 'bloodcave', 'bossarena', 'secret_place',
    'hiddenvalley01', 'hiddenvalleyborder04',
)
# ArtManager-format record path embedded anywhere in a level blob. NON-space body
# ([!-~]) so the non-greedy match cannot bridge a length-prefix byte between two
# adjacent strings and fabricate a phantom ref (TQ record paths never contain spaces).
_DBR_BLOB_RE = re.compile(rb'records[\\/][!-~]*?\.dbr', re.IGNORECASE)


def contract_placed_refs(ctx):
    """(7) Placed-entity record references resolve: every 0x05 instance .dbr
    exists in the arz (mod or base). Scoped to SV/restored content so
    base-game engine-tolerated placements are not false-positived."""
    v = []
    seen = set()
    for lv in ctx.levels:
        blob = ctx.blob(lv)
        blob_drx = b'drxmap' in blob
        strings, insts = parse_0x05(blob)
        # only strings actually referenced by an instance are placed entities
        ref_paths = set()
        for it in insts:
            d = it['dbr']
            if d.lower().endswith(b'.dbr'):
                ref_paths.add(norm_rec(d))
        for npath in sorted(ref_paths):
            if ctx.rec_resolves(npath):
                continue
            if not _sv_scope(npath, blob_drx):
                continue   # base-game / non-SV placement: engine-tolerated, out of scope
            key = (lv['fname'], npath)
            if key in seen:
                continue
            seen.add(key)
            v.append(V('MAP-REF-1', 'P1',
                       f'{lv["fname"]} -> {npath}',
                       'placed SV/restored entity references a record absent from the arz '
                       '(entity silently fails to spawn; naked/missing content)',
                       f'record {npath} not in mod arz ({len(ctx.arz_names)}) nor base arz '
                       f'({len(ctx.base_arz_names)})'))
    return v


def contract_bloodcave_placed(ctx):
    """(8) BLOOD-CAVE crash-class gate (b82): every SV/restored record referenced
    ANYWHERE in a blood-cave-cluster level blob EXISTS in the arz union.

    MAP-REF-1 covers SV 0x05 PLACED instances map-wide; this contract adds a
    WHOLE-BLOB scan (every embedded records\\...\\.dbr, not only 0x05 instances)
    over the blood-cave cluster. Rationale (docs/reports/b82_bloodcave_crash_rca.md):
    a placed/referenced record that does NOT exist is instantiated with a null
    record pointer and dereferenced on zone/region teardown -> the near-null READ
    access violation (0xc0000005) in every blood-cave crash dump (the placed-record
    NON-EXISTENCE crash class). Scoped to SV-namespace records so base/DLC engine-
    tolerated refs are not false-positived. Dangling ASSET / transitive CHILD refs
    (skills/effects/loot/mesh/tex) are deliberately OUT of scope here: the engine
    logs-and-continues on those (proven by the crash dump's own log tail), so they
    are enumerated only by the standalone gate's --chain diagnostic, never gated."""
    v = []
    seen = set()
    for lv in ctx.levels:
        fn = lv['fname'].lower()
        if not any(s in fn for s in BLOODCAVE_SUBSTRINGS):
            continue
        blob = ctx.blob(lv)
        for m in _DBR_BLOB_RE.finditer(blob):
            npath = norm_rec(m.group(0))
            if ctx.rec_resolves(npath):
                continue
            if not any(mk in npath for mk in SV_NAMESPACE_MARKERS):
                continue   # base/DLC ref: engine-tolerated, out of scope
            key = (lv['fname'], npath)
            if key in seen:
                continue
            seen.add(key)
            v.append(V('MAP-BCREF-1', 'P1',
                       f'{lv["fname"]} -> {npath}',
                       'SV/restored record referenced in a blood-cave-cluster level blob '
                       'does NOT exist in the arz (null instantiation pointer; near-null '
                       'deref on zone teardown = the deterministic blood-cave crash class)',
                       f'record {npath} not in mod arz ({len(ctx.arz_names)}) nor base '
                       f'arz ({len(ctx.base_arz_names)})'))
    return v


def _zone_override_targets():
    """The authoritative set of b46 LEVELS-entry teleport-map zone `dbr` override
    targets, read live from tools/svaera_plus_portals.py so this gate cannot drift
    from the map builder. Lazy import (heavy module) - only touched when the
    contract runs. Fails loud if the source table is gone."""
    import importlib
    tools_dir = str(Path(__file__).resolve().parent.parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    spp = importlib.import_module('svaera_plus_portals')
    table = getattr(spp, 'LEVEL_ZONE_DBR_OVERRIDES', None)
    if not table:
        raise RuntimeError('svaera_plus_portals.LEVEL_ZONE_DBR_OVERRIDES missing/empty')
    return sorted(set(table.values()))


def contract_zone_overrides(ctx, _inject_targets=None):
    """(9) b46 minimap zone-override RESOLUTION gate (MAP-ZONE-1).

    Every b46 LEVELS-entry teleport-map zone `dbr` override target must EXIST in
    the arz union (mod over base). A LEVELS entry whose `dbr` points at a zone
    record absent from the DB has its minimap TGA composited against a null zone
    (the Uber Dungeon "black void" class the b46 wave fixed), and the b82/b86 crash
    hypothesis specifically feared a b46 zone-override target that the engine
    region/minimap path dereferences null on. This gate proves that class cannot
    exist for any override target. Extends MAP-NAV-1 (navmesh-GUID resolution) to
    the zone-dbr surface. (`_inject_targets`: test-only override for the negative
    test; production runs read the live override table.)"""
    v = []
    targets = _inject_targets if _inject_targets is not None else _zone_override_targets()
    for dbr in targets:
        npath = norm_rec(dbr)
        if not ctx.rec_resolves(npath):
            v.append(V('MAP-ZONE-1', 'P1', npath,
                       'b46 LEVELS-entry zone-override `dbr` target does NOT exist in the '
                       'arz union (minimap composites against a null zone; the region/minimap '
                       'null-deref class the b82/b86 crash hypothesis flagged)',
                       f'zone dbr {npath} not in mod arz ({len(ctx.arz_names)}) nor base '
                       f'arz ({len(ctx.base_arz_names)})'))
    return v


# The record class the engine treats as a save/respawn point. A level hosting one
# can be loaded in ISOLATION (fresh save-load / respawn) before its grid neighbours
# stream in - the exact condition that detonates a multi-GUID navmesh (b87).
RESPAWN_SHRINE_CLASS = 'StrategicMovementRespawnShrine'


def _respawn_shrines_in_blob(class_of, blob):
    """Set of placed StrategicMovementRespawnShrine record refs in a level blob.
    Class-resolved via `class_of` (arz union; robust, not a name heuristic)."""
    out = set()
    for m in _DBR_BLOB_RE.finditer(blob):
        npath = norm_rec(m.group(0))
        if class_of(npath) == RESPAWN_SHRINE_CLASS:
            out.add(npath)
    return out


def scan_isolated_load_risk(levels, blob_of, class_of, base_level_guids):
    """SHARED classifier for the b87 isolated-load navmesh crash class. Used by BOTH
    the battery contract (contract_navmesh_coresidency) and the standalone gate
    (gate_navmesh_coresidency.py) so their scope can never drift apart.

    A chamber is flagged iff ALL of:
      (1) it hosts a StrategicMovementRespawnShrine  -> can be loaded in ISOLATION
          (a fresh save-load / death-respawn instantiates the player's current level
          before its grid-neighbour levels stream in), AND
      (2) its 0x0b RLTD navmesh is MULTI-GUID (own + grid-seam neighbours), AND
      (3) it is SV-CUSTOM: its own level GUID is ABSENT from the stock base-game
          Levels.arc index (`base_level_guids`).

    Why (3) is the true discriminator (not "respawn + multi-GUID"): the stock game
    ships 264 respawn chambers with multi-GUID navmeshes (DelphiTownStart gc=12,
    Memphis gc=13, ...) that save/reload fine, because a base region keeps its
    navmesh-neighbour levels co-RESIDENT (region-packed) so ProcessRLTD's live-
    residency gate (Engine 0x101f4ba0) completes on isolated load. The SV blood-cave
    / secret-place clusters are grid-shifted into empty world space with offline-
    generated navmeshes, so on an isolated respawn their listed neighbours are NOT
    resident -> the navmesh load fails (Level+0x6a48 stays 0) and the region code
    dereferences the absent navmesh (near-null 0xc0000005; RVA 0x20e270). Provenance
    by own-GUID cleanly excludes every inherited base/IT/XPack respawn chamber
    (incl. the byte-identical Silk Road HiddenValley01 spawn hub) name-free, and
    surfaces exactly the SV-custom respawn chambers our pipeline generates.
    Static GUID resolution (MAP-NAV-1) is GREEN for these - every listed GUID resolves
    in the LEVELS index - so this is the RESIDENCY half MAP-NAV-1 cannot see.
    docs/reports/b87_bloodcave_navok_rca.md.

    Returns list of dicts {level, guid, shrines, guid_count, neighbours}."""
    out = []
    for lv in levels:
        blob = blob_of(lv)
        shrines = _respawn_shrines_in_blob(class_of, blob)
        if not shrines:
            continue
        if lv['guid'] in base_level_guids:
            continue                       # base/IT/XPack provenance -> region-packed, safe
        types = {t: sd for t, sd in parse_blob_sections(blob)}
        d0b = types.get(0x0b)
        if not d0b:
            continue
        try:
            h = rec02_header(d0b)
        except Exception:
            continue
        if h['guid_count'] > 1:
            nbrs = [g.hex()[:8] for g in h['guids'] if g != lv['guid']]
            out.append({'level': lv['fname'], 'guid': lv['guid'],
                        'shrines': sorted(shrines), 'guid_count': h['guid_count'],
                        'neighbours': nbrs})
    return out


def contract_navmesh_coresidency(ctx):
    """(10) MAP-NAV-4: isolated-load navmesh co-residency safety (b87, runtime-proven).

    Every SV-CUSTOM level (own GUID absent from the stock base-game Levels.arc) that
    hosts a StrategicMovementRespawnShrine MUST carry a navmesh loadable in isolation
    (guid_count == 1). A multi-GUID navmesh there re-arms ProcessRLTD's LIVE-residency
    gate on a fresh spawn (the grid neighbours are not resident), so the navmesh load
    fails (navOK=0) and the region code null-derefs the absent navmesh (Engine RVA
    0x20e270) - the crash the 2026-07-17 Frida probe pinned live at
    new_secretdoor_transitionhallway (respawn_hadescave01). See scan_isolated_load_risk
    for the full mechanism + why base/IT/XPack respawn chambers (region-packed, GUID in
    stock) are the proven-safe control. Run the battery against BOTH the canonical and
    TESTHUB arc for runtime parity. docs/reports/b87_bloodcave_navok_rca.md."""
    if not ctx.base_level_guids:
        # Fail loud, never pass blind: the provenance exclusion needs the stock
        # base-game Levels.arc (cfg base_game_dir). run_contracts supplies it by default.
        return [V('MAP-NAV-4', 'P1', '(base-game Levels.arc unavailable)',
                  'cannot verify isolated-load navmesh safety: the stock base-game '
                  'Levels.arc was not loaded, so SV-custom vs base/XPack level provenance '
                  'cannot be established - failing loud rather than passing blind',
                  'set cfg base_game_dir to the TQAE install (Resources/Levels.arc)')]
    v = []
    for c in scan_isolated_load_risk(ctx.levels, ctx.blob, ctx.class_of, ctx.base_level_guids):
        v.append(V('MAP-NAV-4', 'P0', c['level'],
                   'SV-custom save/respawn chamber has a MULTI-GUID navmesh: it can load '
                   'in isolation on spawn, but ProcessRLTD\'s live-residency gate needs '
                   'grid-neighbour levels resident that are NOT loaded on a fresh spawn '
                   '-> navmesh load fails (navOK=0) and the region code null-derefs the '
                   'absent navmesh = the deterministic blood-cave crash (b87)',
                   f'shrine(s)={c["shrines"]}; navmesh guid_count={c["guid_count"]} '
                   f'neighbour-deps={c["neighbours"]}; own GUID {c["guid"].hex()[:8]} absent '
                   f'from stock base-game Levels.arc (SV-custom, not region-packed)'))
    return v


# ============================================================================
# Section 7: metadata, whitelist, runner, CLI
# ============================================================================
CONTRACTS = [
    {'id': 'MAP-QUESTS-1', 'name': 'QUESTS load-window size',
     'asserts': 'world01.map QUESTS section has <= 256 entries (the vanilla load window).',
     'derived_from': 'vanilla TQAE world01.map registers exactly 256 quests (docs/QUEST_STATE_INJECT.md sec 2).'},
    {'id': 'MAP-QUESTS-2', 'name': 'SV-ported quests inside the load window',
     'asserts': 'each ported SV quest (widowletter/urder/bossarena/open_bloodcave_portal) is '
                'registered at an index < 254 so the engine loads/tracks it.',
     'derived_from': 'no QUESTS entry at index >= 254 ever produced state for any character (build22 RCA).'},
    {'id': 'MAP-QUESTS-3', 'name': 'QUESTS boundary parity',
     'asserts': 'QUESTS[254] and QUESTS[255] byte-match the vanilla base-game map (proven-loading boundary).',
     'derived_from': 'vanilla world01.map QUESTS[254]=x4_other_002_hcdungeon_control, [255]=x2_StartQuest.'},
    {'id': 'MAP-PORTAL-1', 'name': 'portal destination resolves',
     'asserts': 'every portal entrance 0x14 binding has a destination GUID that resolves to a level in the world.',
     'derived_from': 'native cave mouths (302 base-game GridEntrance) all resolve dest to a loaded level GUID.'},
    {'id': 'MAP-PORTAL-2', 'name': 'no colliding portal mouth UIDs',
     'asserts': 'no two portal entrances share a mouth UniqueId.',
     'derived_from': 'each base-game portal instance carries a distinct mouth UID (Region::GetPortal keys on it).'},
    {'id': 'MAP-PORTAL-3', 'name': 'portal exit is paired',
     'asserts': "every entrance's exit UID pairs with a landing mouth, a 0x06 reciprocal, or a bidirectional mouth.",
     'derived_from': 'the cross-region linker (Engine 0x101f3680) requires the paired portal on the dest side (docs/DYNGRID_GATE_RCA.md sec 4-5).'},
    {'id': 'MAP-NAV-1', 'name': 'navmesh container valid + GUIDs resolve',
     'asserts': 'every 0x0b RLTD navmesh has valid magic/version/size and every GUID in its list resolves in the world.',
     'derived_from': 'ProcessRLTD (Engine 0x101f4ba0) rejects the whole navmesh unless every listed GUID resolves (docs/CROSS_LEVEL_STITCH_RE.md).'},
    {'id': 'MAP-NAV-2', 'name': 'no stale 0x0a alongside 0x0b',
     'asserts': 'no level carries both a legacy 0x0a PTH and a 0x0b RLTD navmesh.',
     'derived_from': 'the offline pipeline strips 0x0a when it injects 0x0b (tools/verify_merged_bc_navmeshes.py invariant).'},
    {'id': 'MAP-NAV-3', 'name': 'restored SV levels have a navmesh',
     'asserts': 'every non-cut SV (drxmap) level carries a 0x0b navmesh (else invisible wall).',
     'derived_from': 'the TQAE LVL parser only loads 0x0b; a walkable SV level with none is unreachable (docs/HANDOFF map RCA).'},
    {'id': 'MAP-GROUPS-1', 'name': 'shrine-binding group integrity',
     'asserts': 'every RespawnShrine/TeleportShrine GROUP is non-empty, structurally intact, and bound to '
                '>= 1 placed instance UID.',
     'derived_from': 'the respawn shrine binds by 16-byte member UID -> placed 0x05 instance (the rebirth-fountain fix, build18/F1).'},
    {'id': 'MAP-DOOR-1', 'name': 'locked door has a live unlock path',
     'asserts': 'every locked FixedItemDoor placed in the map is named by some quest Action_UnlockFixedItem.',
     'derived_from': 'base-game locked doors (Q01/Q02/Q06...) are each unlocked by a quest Action_UnlockFixedItem (the temple-door class, B-TEMPLE-DOOR-1).'},
    {'id': 'MAP-SD-1', 'name': 'SD display tags resolve',
     'asserts': 'every tag-form display reference in the SD zone section resolves to a Text.arc string.',
     'derived_from': 'SD zones reference tagRegionName*/tagM* display tags that must resolve (else raw tag renders).'},
    {'id': 'MAP-SD-2', 'name': 'restored-area zone label names its area',
     'asserts': "each restored-area SD zone display tag (RESTORED_ZONE_LABEL_EXPECT) resolves to a "
                "label that actually names that area (not another zone's name).",
     'derived_from': 'the Garden-of-Merchants zone tag tagMZoneGoM resolves to "Duister" (B-AREA-NAME-1).'},
    {'id': 'MAP-REF-1', 'name': 'placed SV records resolve',
     'asserts': 'every SV/restored placed 0x05 instance .dbr resolves in the arz (mod or base).',
     'derived_from': 'a placed record absent from the DB silently fails to spawn (the naked-summon/missing-entity class).'},
    {'id': 'MAP-BCREF-1', 'name': 'blood-cave placed records exist (crash class)',
     'asserts': 'every SV/restored record referenced ANYWHERE in a blood-cave-cluster level '
                'blob exists in the arz union (whole-blob scan, superset of the 0x05 check).',
     'derived_from': 'a non-existent placed record is instantiated with a null pointer and '
                     'dereferenced on zone teardown -> the deterministic 0xc0000005 blood-cave '
                     'crash (docs/reports/b82_bloodcave_crash_rca.md; the placed-record '
                     'NON-EXISTENCE class).'},
    {'id': 'MAP-NAV-4', 'name': 'SV-custom respawn chamber navmesh is isolated-load-safe (crash class)',
     'asserts': 'every SV-CUSTOM level (own GUID absent from the stock base-game Levels.arc) '
                'that hosts a StrategicMovementRespawnShrine (a save/respawn point loadable in '
                'isolation) has a single-own-GUID navmesh (guid_count == 1). Inherited base/IT/'
                'XPack respawn chambers (GUID present in stock, region-packed so neighbours stay '
                'co-resident) are the proven-safe control and are excluded by provenance.',
     'derived_from': 'the 2026-07-17 Frida probe pinned the recurring blood-cave crash at '
                     'new_secretdoor_transitionhallway (respawn_hadescave01): its 3-GUID '
                     'grid-seam navmesh fails ProcessRLTD\'s live-residency gate on isolated '
                     'load (navOK=0) and the region code null-derefs the absent navmesh '
                     '(Engine RVA 0x20e270) - docs/reports/b87_bloodcave_navok_rca.md. The stock '
                     'game ships 264 respawn+multi-GUID chambers that reload fine (region-packed, '
                     'co-resident), so "respawn + multi-GUID" is NOT the crash law; the SV-custom '
                     'grid-shifted provenance is. This is the RESIDENCY half MAP-NAV-1 (static '
                     'GUID resolution) cannot see.'},
    {'id': 'MAP-ZONE-1', 'name': 'b46 zone-override targets resolve',
     'asserts': 'every b46 LEVELS-entry teleport-map zone `dbr` override target '
                '(svaera_plus_portals.LEVEL_ZONE_DBR_OVERRIDES) exists in the arz union.',
     'derived_from': 'a LEVELS zone `dbr` pointing at an absent record composites the minimap '
                     'against a null zone (the Uber Dungeon black-void class the b46 wave fixed; '
                     'the region/minimap null-deref the b82/b86 crash hypothesis flagged and '
                     'the b86 bisect ruled out - docs/reports/b86_bloodcave_bisect.md).'},
]

_CONTRACT_FUNCS = [
    contract_quests, contract_portals, contract_navmesh, contract_groups,
    contract_doors, contract_sd_tags, contract_placed_refs,
    contract_bloodcave_placed, contract_zone_overrides,
    contract_navmesh_coresidency,
]


def load_whitelist(path):
    wl = set()
    p = Path(path)
    if not p.exists():
        return wl
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            wl.add((parts[0], parts[1].strip()))
        elif len(parts) == 1:
            wl.add((parts[0], None))   # whole-contract suppression
    return wl


def run(cfg):
    """Run every map contract. Returns a list of violation dicts."""
    ctx = Ctx(cfg)
    viols = []
    for fn in _CONTRACT_FUNCS:
        try:
            viols.extend(fn(ctx))
        except Exception as ex:
            viols.append(V(fn.__name__, 'P1', '(contract crash)',
                           f'contract {fn.__name__} raised {type(ex).__name__}: {ex}',
                           'internal error'))
    # whitelist
    wl = load_whitelist(Path(__file__).with_name('whitelist_map.txt'))
    if wl:
        kept = []
        for vi in viols:
            if (vi['contract'], vi['subject']) in wl or (vi['contract'], None) in wl:
                continue
            kept.append(vi)
        viols = kept
    return viols


def _cfg_from_argv(argv):
    keys = ['arz', 'text_arc', 'levels_arc', 'quests_arc', 'resource_arc_dir',
            'base_game_dir', 'upstream_dir']
    cfg = {}
    for i, k in enumerate(keys):
        cfg[k] = argv[i] if i < len(argv) else None
    return cfg


def main(argv):
    if len(argv) < 4:
        print('usage: contracts_map.py <arz> <text_arc> <levels_arc> <quests_arc> '
              '[resource_arc_dir] [base_game_dir] [upstream_dir]', file=sys.stderr)
        return 2
    cfg = _cfg_from_argv(argv)
    viols = run(cfg)
    for vi in viols:
        print(json.dumps(vi, ensure_ascii=True))
    hard = [x for x in viols if x['severity'] in ('P0', 'P1')]
    sys.stderr.write(f'\n{len(viols)} violation(s); {len(hard)} P0/P1.\n')
    return 1 if hard else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
