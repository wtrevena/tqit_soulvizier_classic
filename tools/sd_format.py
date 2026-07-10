#!/usr/bin/env python3
"""
tools/sd_format.py - reverse-engineered reader/writer for the SD (0x18) section of
TQAE world maps (world01.map inside Levels.arc).

Full reverse-engineering write-up: docs/SD_FORMAT_RE.md. Companion of the qst_format
/ merge_levels_binary parsers (same "parse -> objects -> byte-identical rebuild" idiom).

WHAT THE SD SECTION IS
----------------------
SD is the world's ENVIRONMENT / ZONE table: named world regions, each carrying
lighting + fog colors, a display-name text tag (tagRegionName..), and audio/miniboss
zone bindings. It is NOT pathfinding data. Editing SD changes region names on the
minimap-legend / on-screen zone banner and the per-zone fog/light/music, nothing that
affects walkability.

TOP-LEVEL LAYOUT (little-endian throughout)
-------------------------------------------
  u32 magic  = 2            (constant; also the record-format tag reused by lists)
  u32 version                (6 = classic TQIT/SV maps; 7 = TQAE base / SVAERA)
  then a POSITION-ORDERED sequence of typed lists, each:
      u32 listTag           (NOT a reliable schema key - reused; see below)
      u32 count
      count records          (record schema is determined by LIST POSITION, not tag)

  The list sequence observed in every base/SV/SVAERA map is, in order:
      [0] ENVIRONMENT/FOG   (listTag 1 on v6, 3 on v7)
      [1] REGION/ZONE-LABEL (listTag 2)   <-- the SV zone labels live here
      [2] AUDIO ZONES       (listTag 2)
      [3] MINIBOSS ZONES    (listTag 1)   <-- tag 1 reused; proves tag != schema
      [..] possibly more zone-binding lists
  Because tags are reused (1 = env AND miniboss; 2 = region AND audio) the schema is
  keyed off ORDER. This module therefore fully decodes ONLY the two lists M13b needs
  (ENV[0] and REGION[1]); every list after REGION is preserved VERBATIM as an opaque
  "tail" blob. That is enough to (a) round-trip byte-identically and (b) add/remove/
  convert REGION records (the SV zone-label restoration).

RECORD SCHEMAS (fully RE'd)
---------------------------
ENV record (list 0):
  u32   a            (=1)
  u32   nameLen; char name[nameLen]
  u8    guid[16]
  <fixed param block>            v6: 120 bytes ; v7: 148 bytes (fog/light colors, fog
                                 distances, flags; the +28-byte v7 delta = extra env
                                 fields, see docs)
  ONLY on v7 (version 7):
    u32 effectPathLen; char effectPath[effectPathLen]   (weather effect .dbr, e.g.
                                 records/xpack2/effects/blizzard01.dbr with backslash
                                 separators; len 0 = none)
  (v6 has no trailing effect-path field; its whole payload is the 120-byte block.)

REGION record (list 1) - IDENTICAL schema on v6 and v7:
  u32   a            (=1)
  u32   nameLen; char name[nameLen]        (internal name, e.g. "Village of Helos")
  u8    guid[16]                            (world-unique region id)
  f32   color1[4]                           (RGBA - fog/tint color A)
  f32   color2[4]                           (RGBA - color B)
  u32   tagLen; char tag[tagLen]            (display-name text tag, e.g.
                                             "tagRegionName01"; may be empty)
  u32   t1                                  (trailer field, =1 in all observed)
  u32   t2                                  (trailer field, =1 in all observed)

The AUDIO (music/ambient/event .dbr slots) and MINIBOSS record schemas were also
decoded (see docs) but are intentionally kept in the opaque tail here.

USAGE
-----
  py tools/sd_format.py --roundtrip <Levels.arc> [<Levels.arc> ...]
  py tools/sd_format.py --diff <baseSV.arc.or.map> <svaeraBase.arc.or.map>
  (programmatic) SDSection.from_map_bytes(...) / .build() / .region_records
"""
import sys, os, struct
from pathlib import Path

# --- section-id constant (matches tools/merge_levels_binary.py) ---
SEC_SD = 0x18


# ------------------------------------------------------------------ low-level io
def _rd_u32(b, p):
    return struct.unpack_from('<I', b, p)[0]

def _rd_str(b, p):
    """length-prefixed latin-1 string: [u32 len][bytes]. Returns (str, new_pos)."""
    n = struct.unpack_from('<I', b, p)[0]
    if n > 4096 or p + 4 + n > len(b):
        raise ValueError(f'bad string length {n} at {p}')
    return b[p + 4:p + 4 + n].decode('latin-1'), p + 4 + n

def _wr_str(s):
    raw = s.encode('latin-1')
    return struct.pack('<I', len(raw)) + raw


# ------------------------------------------------------------------ record types
class EnvRecord:
    """Environment/fog record (list 0). Fixed param block kept as raw bytes so the
    rebuild is byte-exact; only name/guid/effectPath are structurally decoded."""
    __slots__ = ('a', 'name', 'guid', 'block', 'effect_path', 'has_effect_field')

    def __init__(self, a, name, guid, block, effect_path, has_effect_field):
        self.a = a
        self.name = name
        self.guid = guid                    # bytes[16]
        self.block = block                  # raw fixed param block (120 v6 / 148 v7)
        self.effect_path = effect_path      # str ('' if none), only meaningful on v7
        self.has_effect_field = has_effect_field  # bool: v7 has the len-prefixed path

    def build(self):
        out = struct.pack('<I', self.a) + _wr_str(self.name) + self.guid + self.block
        if self.has_effect_field:
            out += _wr_str(self.effect_path)
        return out


class RegionRecord:
    """Region / zone-label record (list 1). Fully decoded; the piece M13b edits."""
    __slots__ = ('a', 'name', 'guid', 'color1', 'color2', 'tag', 't1', 't2')

    def __init__(self, a, name, guid, color1, color2, tag, t1, t2):
        self.a = a
        self.name = name                    # internal region name
        self.guid = guid                    # bytes[16]
        self.color1 = color1                # bytes[16] (4 floats, kept raw)
        self.color2 = color2                # bytes[16]
        self.tag = tag                      # display-name text tag (may be '')
        self.t1 = t1
        self.t2 = t2

    def build(self):
        return (struct.pack('<I', self.a) + _wr_str(self.name) + self.guid +
                self.color1 + self.color2 + _wr_str(self.tag) +
                struct.pack('<II', self.t1, self.t2))

    def __repr__(self):
        return f'RegionRecord({self.name!r}, tag={self.tag!r})'


# ------------------------------------------------------------------ the section
class SDSection:
    """Parsed SD section: header + env list + region list + opaque tail.

    The tail is every byte from the end of the REGION list to the end of the section
    (audio + miniboss + any further zone lists), preserved verbatim.
    """
    def __init__(self, magic, version, env_tag, env_records,
                 region_tag, region_records, tail):
        self.magic = magic
        self.version = version
        self.env_tag = env_tag
        self.env_records = env_records          # list[EnvRecord]
        self.region_tag = region_tag
        self.region_records = region_records    # list[RegionRecord]
        self.tail = tail                        # bytes

    # ---- parse ----
    @classmethod
    def parse(cls, sd):
        magic, version = struct.unpack_from('<II', sd, 0)
        if magic != 2:
            raise ValueError(f'unexpected SD magic {magic} (expected 2)')
        if version not in (6, 7):
            raise ValueError(f'unsupported SD version {version} (expected 6 or 7)')
        pos = 8

        # --- list 0: environment/fog ---
        env_tag, env_count = struct.unpack_from('<II', sd, pos)
        pos += 8
        v7 = (version == 7)
        env_block = 148 if v7 else 120
        env_records = []
        for _ in range(env_count):
            a = _rd_u32(sd, pos)
            name, q = _rd_str(sd, pos + 4)
            guid = sd[q:q + 16]; q += 16
            block = sd[q:q + env_block]; q += env_block
            if v7:
                effect_path, q = _rd_str(sd, q)
            else:
                effect_path = ''
            env_records.append(EnvRecord(a, name, guid, block, effect_path, v7))
            pos = q

        # --- list 1: region / zone labels ---
        region_tag, region_count = struct.unpack_from('<II', sd, pos)
        pos += 8
        region_records = []
        for _ in range(region_count):
            a = _rd_u32(sd, pos)
            name, q = _rd_str(sd, pos + 4)
            guid = sd[q:q + 16]; q += 16
            color1 = sd[q:q + 16]; q += 16
            color2 = sd[q:q + 16]; q += 16
            tag, q = _rd_str(sd, q)
            t1, t2 = struct.unpack_from('<II', sd, q); q += 8
            region_records.append(RegionRecord(a, name, guid, color1, color2, tag, t1, t2))
            pos = q

        # --- everything after the region list = opaque tail ---
        tail = sd[pos:]
        return cls(magic, version, env_tag, env_records,
                   region_tag, region_records, tail)

    # ---- build ----
    def build(self):
        out = struct.pack('<II', self.magic, self.version)
        out += struct.pack('<II', self.env_tag, len(self.env_records))
        for r in self.env_records:
            out += r.build()
        out += struct.pack('<II', self.region_tag, len(self.region_records))
        for r in self.region_records:
            out += r.build()
        out += self.tail
        return out

    # ---- convenience ----
    def region_by_tag(self):
        d = {}
        for r in self.region_records:
            if r.tag:
                d.setdefault(r.tag, []).append(r)
        return d


# ------------------------------------------------------------------ map helpers
def sd_from_map_bytes(map_bytes):
    """Extract the raw SD-section bytes from a world01.map byte string."""
    from merge_levels_binary import parse_sections
    secs = parse_sections(map_bytes)
    for s in secs:
        if s['type'] == SEC_SD:
            return map_bytes[s['data_offset']:s['data_offset'] + s['size']]
    raise ValueError('no SD (0x18) section in map')


def load_sd(path):
    """Load the SD section bytes from an .arc (Levels.arc) or a raw .map file."""
    from arc_patcher import ArcArchive
    path = Path(path)
    if path.suffix.lower() == '.map':
        return sd_from_map_bytes(path.read_bytes())
    arc = ArcArchive.from_file(path)
    data = arc.get_file('world/world01.map')
    if data is None:
        for e in arc.entries:
            if e.name.lower().endswith('world01.map'):
                data = arc.get_file(e.name); break
    if data is None:
        raise ValueError(f'no world01.map in {path}')
    return sd_from_map_bytes(data)


# ------------------------------------------------------------------ cli
def _roundtrip(paths):
    ok_all = True
    for p in paths:
        sd = load_sd(p)
        sec = SDSection.parse(sd)
        rebuilt = sec.build()
        identical = rebuilt == sd
        ok_all &= identical
        n_tag = sum(1 for r in sec.region_records if r.tag)
        print(f'{p}')
        print(f'  version={sec.version} env={len(sec.env_records)} '
              f'region={len(sec.region_records)} (tagged={n_tag}) tail={len(sec.tail)}B '
              f'total={len(sd)}B')
        print(f'  ROUND-TRIP byte-identical = {identical}')
        if not identical:
            # precise diff account
            n = min(len(sd), len(rebuilt))
            first = next((i for i in range(n) if sd[i] != rebuilt[i]), n)
            print(f'    len(orig)={len(sd)} len(rebuilt)={len(rebuilt)} first_diff={first}')
    return ok_all


def _diff(base_sv, svaera):
    a = SDSection.parse(load_sd(base_sv))    # SV/ours (v6)
    b = SDSection.parse(load_sd(svaera))     # SVAERA/base (v7)
    an = {r.name for r in a.region_records}
    bn = {r.name for r in b.region_records}
    at = {r.tag for r in a.region_records if r.tag}
    bt = {r.tag for r in b.region_records if r.tag}
    print(f'SV/ours (v{a.version}): env={len(a.env_records)} region={len(a.region_records)}')
    print(f'SVAERA  (v{b.version}): env={len(b.env_records)} region={len(b.region_records)}')
    print(f'\nregion NAMES only in SV/ours ({len(an - bn)}):')
    for n in sorted(an - bn):
        recs = [r for r in a.region_records if r.name == n]
        print(f'   {n!r:40} tag={recs[0].tag!r}')
    print(f'\nregion display-TAGS only in SV/ours ({len(at - bt)}):')
    for t in sorted(at - bt):
        print(f'   {t}')
    print(f'\nregion NAMES only in SVAERA ({len(bn - an)}) (first 30):')
    for n in sorted(bn - an)[:30]:
        print(f'   {n!r}')


def main(argv):
    if len(argv) >= 2 and argv[1] == '--roundtrip':
        ok = _roundtrip(argv[2:])
        sys.exit(0 if ok else 1)
    elif len(argv) == 4 and argv[1] == '--diff':
        _diff(argv[2], argv[3])
    else:
        print(__doc__)
        print('usage:')
        print('  py tools/sd_format.py --roundtrip <Levels.arc|world01.map> ...')
        print('  py tools/sd_format.py --diff <SV_or_ours> <SVAERA_base>')


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent))
    main(sys.argv)
