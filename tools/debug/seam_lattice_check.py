"""Compare WORKING AE grid seams vs OUR generated seams on two axes:
  1. tile-lattice alignment across the seam ((cornerA - cornerB) mod 12.8)
  2. walkable coverage crossing the shared boundary (per side, in world units)
Working set: randomice03* batch + valley01/valley01b (AE editor navmeshes).
Broken set:  blood-cave cluster + random09a (our generated navmeshes).
All read from the DEPLOYED merged map (AE meshes untouched there).
"""
import sys, struct
from pathlib import Path
REPO = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic")
sys.path.insert(0, str(REPO / 'tools'))
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
from build_section_surgery import parse_blob_sections
from rec02_format import parse_rec02

DEP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc")
CS, TILEW = 0.2, 12.8
GATE = '--gate' in sys.argv   # exit 1 unless every parsed OURS seam aligns at 0.000

arc = ArcArchive.from_file(DEP)
data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
sec = {s['type']: s for s in parse_sections(data)}
levels = parse_level_index(data, sec[SEC_LEVELS])

AE_SET = {'randomice03a','randomice03b','randomice03c','randomice03d','randomice03above',
          'randomice03buffera','randomice03bufferb','valley01','valley01b'}

info = {}
for lv in levels:
    fn = lv['fname'].replace('\\','/').lower(); base = fn.split('/')[-1].replace('.lvl','')
    if not (base in AE_SET or 'xbloodcave' in fn or base == 'random09a'): continue
    ints = struct.unpack_from('<13i', lv['ints_raw'], 0)
    cx, cz = ints[6], ints[8]
    bx_t, bz_t = ints[3], ints[5]
    blob = data[lv['data_offset']:lv['data_offset']+lv['data_length']]
    secs, _ = parse_blob_sections(blob)
    nav = None
    for s in secs:
        if s['type'] == 0x0b and s['data'][:4] == b'REC\x02':
            try: nav = parse_rec02(s['data'], decompress=True)
            except Exception as e: nav = f'parse fail: {e}'
    info[base] = dict(base=base, fx0=cx, fx1=cx+bx_t*2, fz0=cz, fz1=cz+bz_t*2,
                      nav=nav, grp=('AE' if base in AE_SET else 'OURS'))

def mesh_corner(nav):
    c = nav['center']; d = nav['dims']
    return (c[0]-d[0], c[2]-d[2])

def walk_cells(nav):
    """yield (world_x, world_z) center of each walkable cell (set 0 = Normal)."""
    cx0, cz0 = mesh_corner(nav)
    ts = nav['sets'][0] if 'sets' in nav else nav['tilesets'][0]
    for rec in ts['records'] if 'records' in ts else ts['tiles']:
        h = rec['hdr']; areas = rec.get('areas')
        if areas is None: continue
        tx, ty = h['tx'], h['ty']
        for lz in range(64):
            row = lz*64
            for lx in range(64):
                if areas[row+lx]:
                    yield (cx0 + (tx*64+lx)*CS + CS/2, cz0 + (ty*64+lz)*CS + CS/2)

def seams(names):
    out = []
    ks = [info[n] for n in names if n in info]
    for i in range(len(ks)):
        for j in range(i+1, len(ks)):
            A, B = ks[i], ks[j]
            xov = min(A['fx1'],B['fx1']) - max(A['fx0'],B['fx0'])
            zov = min(A['fz1'],B['fz1']) - max(A['fz0'],B['fz0'])
            if xov == 0 and zov > 0:
                low, high = (A,B) if A['fx1'] == B['fx0'] else (B,A)
                if low['fx1'] != high['fx0']: continue
                out.append(('x', low, high, low['fx1'], (max(A['fz0'],B['fz0']), min(A['fz1'],B['fz1']))))
            elif zov == 0 and xov > 0:
                low, high = (A,B) if A['fz1'] == B['fz0'] else (B,A)
                if low['fz1'] != high['fz0']: continue
                out.append(('z', low, high, low['fz1'], (max(A['fx0'],B['fx0']), min(A['fx1'],B['fx1']))))
    return out

def crossing(nav, axis, boundary, band, side):
    """max penetration of walkable cells past `boundary` (side='low' means level is
    below the boundary, so penetration = max(coord) - boundary)."""
    best = None
    for wx, wz in walk_cells(nav):
        along = wx if axis=='x' else wz
        perp  = wz if axis=='x' else wx
        if not (band[0]-0.01 <= perp <= band[1]+0.01): continue
        pen = (along - boundary) if side=='low' else (boundary - along)
        if best is None or pen > best: best = pen
    return best

names = list(info)
gate_fail = []
gate_pass = 0
for grp in ('AE','OURS'):
    print(f"\n======== {grp} seams ========")
    got = seams([n for n in names if info[n]['grp']==grp])
    for axis, low, high, boundary, band in got:
        ln, hn = low['base'], high['base']
        navL, navH = low['nav'], high['nav']
        if not isinstance(navL, dict) or not isinstance(navH, dict):
            print(f"  {ln} | {hn}  axis={axis} b={boundary}: nav missing/unparsed ({type(navL).__name__}/{type(navH).__name__})")
            continue
        cL, cH = mesh_corner(navL), mesh_corner(navH)
        ai = 0 if axis=='x' else 1
        d = (cL[ai] - cH[ai]) % TILEW
        mis = min(d, TILEW-d)
        penL = crossing(navL, axis, boundary, band, 'low')
        penH = crossing(navH, axis, boundary, band, 'high')
        print(f"  {ln:28s}|{hn:28s} axis={axis} b={boundary}")
        print(f"      lattice offset mod 12.8 = {mis:.3f}   cornerL={cL}  cornerH={cH}")
        print(f"      walkable crossing: {ln} {'%.2f'%penL if penL is not None else 'NONE'}u past boundary; "
              f"{hn} {'%.2f'%penH if penH is not None else 'NONE'}u past boundary")
        if grp == 'OURS':
            # both-axis phase must coincide (stitching needs the full 2D lattice
            # to line up, not just the seam-perpendicular axis)
            off2 = []
            for k in (0, 1):
                dd = (cL[k] - cH[k]) % TILEW
                off2.append(min(dd, TILEW - dd))
            if max(off2) > 0.001:
                gate_fail.append(f'{ln}|{hn} offsets={tuple(round(o,3) for o in off2)}')
            else:
                gate_pass += 1

if GATE:
    print(f"\nLATTICE GATE: {gate_pass} aligned seams, {len(gate_fail)} misaligned")
    if gate_fail:
        for f in gate_fail: print(f"  MISALIGNED: {f}")
        sys.exit(1)
    if gate_pass < 10:
        print(f"  GATE FAIL: only {gate_pass} parseable cluster seams (expected 15+) - donors missing?")
        sys.exit(1)
    print("  GATE PASS: every parseable cluster seam lattice-aligned (both axes).")
