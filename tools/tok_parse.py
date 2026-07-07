"""PathEngine .tok tokenizer with pluggable value widths; validate hypotheses by
full-stream parse + semantic checks (tri indices < nverts etc.).
"""
import re
import struct
import sys
from pathlib import Path

# tok attr value widths by type id (signed LE): 1=cstring, 2=int32, 3=int16,
# 4=int8, 7=int8. Single source of truth for the width map every caller uses.
TOK_WIDTHS = {2: 4, 3: 2, 4: 1, 7: 1}

def read_tables(tok):
    pos = 0
    elems = []
    while True:
        e = tok.find(b'\x00', pos)
        name = tok[pos:e]
        pos = e + 1
        if not name:
            break
        elems.append(name.decode())
    attrs = []
    while True:
        t = tok[pos]
        if t == 0:
            pos += 1
            break
        e = tok.find(b'\x00', pos + 1)
        attrs.append((t, tok[pos + 1:e].decode()))
        pos = e + 1
    return elems, attrs, pos

def parse_stream(tok, pos, elems, attrs, widths, leaf_close=True, debug=False):
    """widths: dict type->byte width (signed LE); type 1 = cstring."""
    root = []
    stack = [('<root>', None, root)]
    n = len(tok)
    while pos < n:
        b = tok[pos]
        pos += 1
        if b == 0:
            # close current element
            if len(stack) == 1:
                # trailing padding? require all zeros to end
                if all(x == 0 for x in tok[pos:]):
                    return root, pos, None
                return None, pos, f'close at root with data left @{pos}'
            stack.pop()
            continue
        if b - 1 >= len(elems):
            return None, pos, f'bad element id {b} @{pos-1}'
        name = elems[b - 1]
        node = {'tag': name, 'attrs': {}, 'children': []}
        stack[-1][2].append(node)
        # read attributes until 0x00
        while True:
            a = tok[pos]
            if a == 0:
                pos += 1
                break
            pos += 1
            if a - 1 >= len(attrs):
                return None, pos, f'bad attr id {a} @{pos-1} in <{name}>'
            at, aname = attrs[a - 1]
            if at == 1:
                e = tok.find(b'\x00', pos)
                node['attrs'][aname] = tok[pos:e].decode()
                pos = e + 1
            else:
                w = widths.get(at)
                if w is None:
                    return None, pos, f'no width for type {at} ({aname})'
                v = int.from_bytes(tok[pos:pos+w], 'little', signed=True)
                node['attrs'][aname] = v
                pos += w
        # leaf-close convention: next byte 0 closes it immediately if children
        # follow otherwise element becomes container; we model uniformly:
        stack.append((name, node, node['children']))
    if len(stack) > 1:
        return None, pos, f'unclosed elements {[s[0] for s in stack[1:]]}'
    return root, pos, None

def validate(root):
    """Return (ok, info) checking mesh3D/verts/tris semantics."""
    try:
        mesh = root[0]
        assert mesh['tag'] == 'mesh'
        m3 = [c for c in mesh['children'] if c['tag'] == 'mesh3D'][0]
        verts_el = [c for c in m3['children'] if c['tag'] == 'verts'][0]
        tris_el = [c for c in m3['children'] if c['tag'] == 'tris'][0]
        verts = [(c['attrs']['x'], c['attrs']['y'], c['attrs'].get('z', 0))
                 for c in verts_el['children']]
        tris = []
        for c in tris_el['children']:
            a = c['attrs']
            tris.append((a['edge0StartVert'], a['edge1StartVert'], a['edge2StartVert'],
                         a.get('edge0Connection', -1), a.get('edge1Connection', -1),
                         a.get('edge2Connection', -1)))
        nv, nt = len(verts), len(tris)
        idx_ok = all(0 <= t[i] < nv for t in tris for i in range(3))
        con_ok = all(-1 <= t[i] < nt for t in tris for i in range(3, 6))
        xs = [v[0] for v in verts]; ys = [v[1] for v in verts]; zs = [v[2] for v in verts]
        return idx_ok and con_ok, dict(nv=nv, nt=nt, idx_ok=idx_ok, con_ok=con_ok,
                                       x=(min(xs), max(xs)), y=(min(ys), max(ys)),
                                       z=(min(zs), max(zs)))
    except Exception as ex:
        return False, {'err': repr(ex)}

def extract_mesh(lvl_path):
    sys.path.insert(0, r'C:\Users\willi\repos\tqit_soulvizier_classic\tools')
    from build_section_surgery import parse_blob_sections
    blob = Path(lvl_path).read_bytes()
    secs, _ = parse_blob_sections(blob)
    d = [s for s in secs if s['type'] == 0x0a][0]['data']
    # container: PTH\x04 + {type,size,payload}*
    ptype, psize = struct.unpack_from('<2I', d, 4)
    assert ptype == 1
    p = 12
    gc = struct.unpack_from('<I', d, p)[0]
    guids = [d[p + 4 + i*20: p + 4 + i*20 + 16] for i in range(gc)]
    off = p + 4 + gc * 20
    center = struct.unpack_from('<3i', d, off)
    dims = struct.unpack_from('<3I', d, off + 12)
    tok = d[off + 24: 12 + psize]
    return guids, center, dims, tok


def parse_obstacles(tok):
    """Return the ground mesh's baseObstacle polygons as LEVEL-LOCAL (x,z) point
    lists (world units, relative to the 0x0a corner = header center - dims).

    Each `<obstacle>` under `mesh/baseObstacles` carries two cstring attrs:
      position = 'FACE:x,z'                       (x,z in centi-units, level-local)
      vertices = 'vx0,vz0,vx1,vz1,vx2,vz2,vx3,vz3' (4 offsets, centi-units)
    so the polygon is [(px+vx_i, pz+vz_i)] with px,pz = position/100 and each
    offset/100 (exactly batch_validate.parse_ground / the RCA FIX SPEC formula).
    The leading FACE index (the tri the obstacle sits on) is NOT a coordinate and
    is skipped. Returns [] when the tok has no baseObstacles element.

    This is the ONLY encoding of the SV rock/wall footprints (RCA Measurement 6:
    there is no carved alternate mesh); gen_rec02 subtracts these from the
    walkable set so the player cannot walk through solid rocks.
    """
    elems, attrs, pos = read_tables(tok)
    root, _endpos, err = parse_stream(tok, pos, elems, attrs, TOK_WIDTHS)
    assert root is not None, f'tok parse failed: {err}'
    mesh = root[0]
    bo = [c for c in mesh['children'] if c['tag'] == 'baseObstacles']
    if not bo:
        return []
    polys = []
    for ob in bo[0]['children']:
        if ob['tag'] != 'obstacle':
            continue
        p = [int(n) for n in re.findall(r'-?\d+', ob['attrs']['position'])]  # [face,x,z]
        v = [int(n) for n in re.findall(r'-?\d+', ob['attrs']['vertices'])]  # 8 offsets
        if len(p) < 3 or len(v) < 8:
            continue
        px, pz = p[1] / 100.0, p[2] / 100.0
        poly = [(px + v[i] / 100.0, pz + v[i + 1] / 100.0)
                for i in range(0, len(v) - 1, 2)]
        polys.append(poly)
    return polys


def load_tok_obstacles(lvl_path):
    """Convenience: extract the 0x0a container from a .lvl and return its
    baseObstacle polygons (level-local x,z). See parse_obstacles."""
    _guids, _center, _dims, tok = extract_mesh(lvl_path)
    return parse_obstacles(tok)


if __name__ == '__main__':
    lvl = sys.argv[1] if len(sys.argv) > 1 else \
        r'C:\Users\willi\repos\tqit_soulvizier_classic\local\decompiled_sv\Levels\World\xBloodCave\BC_initialpathway.lvl'
    guids, center, dims, tok = extract_mesh(lvl)
    print(f'center={center} dims={dims} tok={len(tok)}b guids={len(guids)}')
    elems, attrs, pos = read_tables(tok)
    print('attr types:', sorted({t for t, _ in attrs}))
    for label, widths in [('A t3=2 t4=1 t7=1', {3: 2, 4: 1, 7: 1}),
                          ('B t3=2 t4=1 t7=2', {3: 2, 4: 1, 7: 2}),
                          ('C t3=2 t4=2 t7=2', {3: 2, 4: 2, 7: 2}),
                          ('D t3=2 t4=4 t7=1', {3: 2, 4: 4, 7: 1}),
                          ('E t3=4 t4=1 t7=1', {3: 4, 4: 1, 7: 1})]:
        root, endpos, err = parse_stream(tok, pos, elems, attrs, widths)
        if root is None:
            print(f'{label}: FAIL {err}')
            continue
        ok, info = validate(root)
        print(f'{label}: parsed to {endpos}/{len(tok)} valid={ok} {info}')
