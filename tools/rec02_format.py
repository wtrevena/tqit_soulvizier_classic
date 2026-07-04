"""Reference implementation of the TQAE 0x0b (REC\x02 / RLTD) navmesh section format.

Byte-accurate parse + serialize, proven by round-trip identity over 370 Editor-baked
levels and 300 pristine SVAERA levels (plus FastLZ payload identity separately).

FORMAT (all little-endian):
  container:
    +0   b'REC\x02'
    +4   uint32 version            == 1 (engine skips payload otherwise)
    +8   uint32 payload_size       == total_size - 12
    +12  uint32 guid_count         (1..13 observed)
    +16  guid_count * 16B GUIDs    (own level GUID + geometry-contributing neighbor
                                    level GUIDs; engine REQUIRES each to resolve in
                                    the loaded world's level-GUID map)
    +..  int32  center[3]          world-space center (= map grid corner + half-extents)
    +..  uint32 dims[3]            half-extents in world units (x/z: level half-extent
                                    + 16 padding; grid spans local [0, 2*dims])
    +..  3 x tileset               difficulty sets: Normal / Epic / Legendary
  tileset:
    52B  dtTileCacheParams:
         float orig[3]             (0,0,0)
         float cs, ch              0.2, 0.2
         int32 width, height       64, 64          (cells per tile)
         float walkableHeight      2.0
         float walkableRadius      0.4
         float walkableClimb       1.0
         float maxSimplificationError 1.3
         int32 maxTiles            2 * ceil(2*dims_x/12.8) * ceil(2*dims_z/12.8)
         int32 maxObstacles        128 (IGNORED by engine; forced to 256 at load)
    +52  int32 numTiles
    then numTiles * record:
         int32 dataSize
         data[dataSize]:
             dtTileCacheLayerHeader (56B):
                int32 magic        'DTLR' = bytes b'RLTD'
                int32 version      1
                int32 tx, ty, tlayer
                float bmin[3], bmax[3]    (level-local; x=tx*12.8, z=ty*12.8,
                                           y=hmin*ch / hmax*ch)
                uint16 hmin, hmax
                uint8 width=64, height=64, minx, maxx, miny, maxy (usable sub-rect)
                uint8 pad[2] = 0
             fastlz level-1 compressed (heights[w*h] + areas[w*h] + cons[w*h])
                heights: cell y index - hmin; 0xff = empty
                areas:   0 = unwalkable; 1..6 = walkable classes (terrain types)
                cons:    low nibble = intra-layer 4-dir connectivity,
                         high nibble = tile-border portals; Detour dirs
                         bit0=W(x-1) bit1=N(z+1) bit2=E(x+1) bit3=S(z-1)
         int32 tx, ty               (repeated; engine uses to call getTilesAt)

Engine load path (ProcessRLTD VA 0x101f4ba0, dtTileCache::addTile VA 0x101002b0):
  per set: dtTileCache::init(params, maxObstacles=256); dtNavMesh::init(orig,
  tileWidth=width*cs, tileHeight=height*cs, maxTiles, maxPolys=1000);
  per record: addTile(data) then buildNavMeshTile for all layers at (tx,ty).
  Success requires all 3 sets present.  Polys are built AT LOAD from the layers,
  so a generator only needs rasterized layer data.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fastlz import fastlz1_compress, fastlz1_decompress

PARAMS_FMT = '<3f2f2i4f2i'
LHDR_FMT = '<5i6f2H6B2s'


def parse_rec02(d, decompress=False):
    assert d[:4] == b'REC\x02', 'bad magic'
    version, payload_size, guid_count = struct.unpack_from('<3I', d, 4)
    assert version == 1
    assert payload_size == len(d) - 12, (payload_size, len(d))
    pos = 16
    guids = [d[pos + i*16: pos + (i+1)*16] for i in range(guid_count)]
    pos += guid_count * 16
    center = struct.unpack_from('<3i', d, pos)
    dims = struct.unpack_from('<3I', d, pos + 12)
    pos += 24
    sets = []
    while pos < len(d):
        pv = struct.unpack_from(PARAMS_FMT, d, pos)
        params = dict(orig=pv[0:3], cs=pv[3], ch=pv[4], width=pv[5], height=pv[6],
                      walkableHeight=pv[7], walkableRadius=pv[8], walkableClimb=pv[9],
                      maxSimplificationError=pv[10], maxTiles=pv[11], maxObstacles=pv[12])
        num_tiles = struct.unpack_from('<i', d, pos + 52)[0]
        pos += 56
        recs = []
        for _ in range(num_tiles):
            dsize = struct.unpack_from('<i', d, pos)[0]
            pos += 4
            data = d[pos:pos + dsize]
            pos += dsize
            tx, ty = struct.unpack_from('<2i', d, pos)
            pos += 8
            hv = struct.unpack_from(LHDR_FMT, data, 0)
            hdr = dict(magic=hv[0], version=hv[1], tx=hv[2], ty=hv[3], tlayer=hv[4],
                       bmin=hv[5:8], bmax=hv[8:11], hmin=hv[11], hmax=hv[12],
                       width=hv[13], height=hv[14], minx=hv[15], maxx=hv[16],
                       miny=hv[17], maxy=hv[18], pad=hv[19])
            assert hdr['magic'] == 0x44544c52 and hdr['version'] == 1
            assert hdr['tx'] == tx and hdr['ty'] == ty
            rec = dict(hdr=hdr, trail_tx=tx, trail_ty=ty)
            if decompress:
                g = hdr['width'] * hdr['height']
                raw = fastlz1_decompress(data[56:], g * 3 + 64)
                assert raw is not None and len(raw) == g * 3
                rec['heights'] = raw[:g]
                rec['areas'] = raw[g:2*g]
                rec['cons'] = raw[2*g:]
            else:
                rec['comp'] = data[56:]
            recs.append(rec)
        sets.append(dict(params=params, records=recs))
    assert pos == len(d)
    return dict(version=version, guids=guids, center=center, dims=dims, sets=sets)


def serialize_rec02(doc):
    out = bytearray()
    out += b'REC\x02'
    out += struct.pack('<3I', doc['version'], 0, len(doc['guids']))
    for g in doc['guids']:
        assert len(g) == 16
        out += g
    out += struct.pack('<3i', *doc['center'])
    out += struct.pack('<3I', *doc['dims'])
    for s in doc['sets']:
        p = s['params']
        out += struct.pack(PARAMS_FMT, *p['orig'], p['cs'], p['ch'], p['width'],
                           p['height'], p['walkableHeight'], p['walkableRadius'],
                           p['walkableClimb'], p['maxSimplificationError'],
                           p['maxTiles'], p['maxObstacles'])
        out += struct.pack('<i', len(s['records']))
        for r in s['records']:
            h = r['hdr']
            hdr_bytes = struct.pack(LHDR_FMT, h['magic'], h['version'], h['tx'],
                                    h['ty'], h['tlayer'], *h['bmin'], *h['bmax'],
                                    h['hmin'], h['hmax'], h['width'], h['height'],
                                    h['minx'], h['maxx'], h['miny'], h['maxy'],
                                    h['pad'])
            comp = r['comp'] if 'comp' in r else fastlz1_compress(
                bytes(r['heights']) + bytes(r['areas']) + bytes(r['cons']))
            data = hdr_bytes + comp
            out += struct.pack('<i', len(data))
            out += data
            out += struct.pack('<2i', r['trail_tx'], r['trail_ty'])
    struct.pack_into('<I', out, 8, len(out) - 12)
    return bytes(out)


if __name__ == '__main__':
    import time
    scratch = Path(__file__).parent
    corpora = [('baked', sorted((scratch / 'corpus' / 'baked').glob('*.0b.bin'))),
               ('svaera', sorted((scratch / 'corpus' / 'svaera').glob('*.0b.bin')))]
    for label, files in corpora:
        t0 = time.time()
        ok = 0
        for f in files:
            d = f.read_bytes()
            doc = parse_rec02(d)
            out = serialize_rec02(doc)
            if out == d:
                ok += 1
            else:
                print(f'MISMATCH {f.name} len {len(d)} vs {len(out)}')
        print(f'{label}: {ok}/{len(files)} byte-identical round-trips '
              f'({time.time()-t0:.1f}s)')
    # full recompression round-trip on 3 files
    for name in ('Babylon__HangingGardensExit01.lvl.0b.bin',
                 'Greece__Area004__RuinedCity02.lvl.0b.bin',
                 'Egypt__Thebes__Thebes02.lvl.0b.bin'):
        f = scratch / 'corpus' / 'baked' / name
        if not f.exists():
            print(f'skip {name} (absent)')
            continue
        d = f.read_bytes()
        doc = parse_rec02(d, decompress=True)
        out = serialize_rec02(doc)
        print(f'FULL decompress->recompress round-trip {name}: '
              f'{"BYTE-IDENTICAL" if out == d else "MISMATCH"}')
