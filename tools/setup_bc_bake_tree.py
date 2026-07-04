"""
Build the minimal ArtManager source tree to bake ONE Soulvizier-only level's
Recast navmesh (0x0b / REC\\x02) in the stock TQAE Editor.

Target level: BC_initialpathway (the blood-cave entrance level). This is the
minimal repro for the map-integration blocker: the 46 SV-only levels ship with
0x0a (PTH) pathfinding only, which the stock TQAE engine cannot parse, so the
player hits an invisible wall. The fix is to bake real 0x0b navmeshes with the
Editor's "Build -> Rebuild All Pathing" and inject them via
inject_rec02_into_blob(use_stub=False, donor_data=<editor 0x0b>).

WHY A FULL WORLD, NOT A SINGLE-LEVEL .wrl:
  The WRL (WRL\\x07) is a large inline-record world layout. Each level record is
  <uint32 path_len><path><52-byte ints_raw (13 int32)>, where ints_raw[6,7,8]
  (byte offset +24 after the path) is the grid corner (world x,y,z). Only the
  per-level record portion is understood; the world header / terrain-blend /
  neighbor-grid structures are NOT reverse-engineered. Hand-authoring a
  one-tile .wrl risks corrupting those and producing a black/empty world, which
  is exactly the failure we are trying to eliminate. Instead we reuse the FULL
  SV world01.wrl + world01.sd (which already reference BC_initialpathway and all
  xBloodCave levels), junction every region + XPack dir so all .lvl/.rlv/.tga
  resolve, and in the Editor SELECT ONLY BC_initialpathway to bake. The Editor
  bakes pathing per level; opening a full world and baking one level is the
  intended, lowest-risk path.

WHY THIS MOD RESOLVES TERRAIN (the black-viewport fix):
  BC_initialpathway's 0x05 entity section references 32 records\\drxmap\\bloodcave
  objects and its terrain record is records\\drxmap\\bloodcave\\bloodcave.dbr.
  Those records live in the BUILT SoulvizierClassic.arz, and the blood-cave
  terrain textures (map/bloodcave/*.tex) live in its DRXtextures.arc. Tools.ini
  additionalbuilddirs must therefore include BOTH the game install (base terrain)
  AND CustomMaps\\SoulvizierClassic (drxmap terrain). This script does NOT edit
  Tools.ini (that is done separately); it only lays out the source tree.

COORDINATES (read the report; summarized here):
  Original SV grid corner of BC_initialpathway = (-2101, 18, 1293).
  Merged/shifted grid corner (svaera_plus_portals GRID_SHIFT xbloodcave
  (1663,0,922)) = (-438, 18, 2215).
  The baked 0x0b body (RLTD tiles) is stored in LEVEL-LOCAL coordinates (proven:
  tile bmin/bmax are small 0..80 values, not world ~-6000), so the mesh is
  repositioned entirely by the header center. Two options:
    (A) DEFAULT: bake at ORIGINAL SV coords (no WRL edit), then reposition on
        inject via transplant_rec02 (patches header center = grid + dims). Lowest
        risk to the source tree; header Y is approximate (see report) but X/Z
        exact and Y is the vertical axis.
    (B) --shift-grid: patch the WRL's BC_initialpathway grid corner to the merged
        shifted value so the Editor bakes the header center already at the final
        position; then inject with donor_data unchanged (transplant still safe -
        it just re-patches to the same numbers). Use only if (A) shows a vertical
        offset in-game.
  This script implements BOTH; default is (A).

USAGE:
  py tools/setup_bc_bake_tree.py                 # option A (original coords)
  py tools/setup_bc_bake_tree.py --shift-grid    # option B (WRL patched to shifted grid)
  py tools/setup_bc_bake_tree.py --clean         # remove the bake mod source tree

After this script, drive the Editor per the CLICK-STEPS in the report, then run
  py tools/verify_editor_output.py
to confirm a 0x0b section now exists in the re-saved BC_initialpathway.lvl.
"""
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_section_surgery import parse_blob_sections

# --- Paths ---
REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
TQ_DOCS = Path(r'C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne')
WORKING = TQ_DOCS / 'Working'
GAME = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition')
BUILT_MOD = TQ_DOCS / 'CustomMaps' / 'SoulvizierClassic'

# Dedicated bake mod (isolated; resolves SoulvizierClassic assets via additionalbuilddirs)
MOD_NAME = 'BCBake'
MOD_DIR = WORKING / 'CustomMaps' / MOD_NAME
SOURCE = MOD_DIR / 'source'

SV_DECOMP = REPO / 'local' / 'decompiled_sv'

# The one level we bake.
TARGET_REL = 'Levels/World/xBloodCave/BC_initialpathway.lvl'
TARGET_NAME = 'BC_initialpathway'

# Coordinate shift applied to the merged world (svaera_plus_portals.py GRID_SHIFT['xbloodcave']).
GRID_SHIFT = (1663, 0, 922)  # dx, dy, dz  -> (-2101,18,1293) becomes (-438,18,2215)


def make_junction(link_path, target_path):
    """Create a Windows directory junction, replacing any existing link/dir."""
    link = Path(link_path)
    target = Path(target_path)
    if link.exists() or link.is_symlink():
        try:
            os.rmdir(str(link))          # junction / empty dir
        except OSError:
            shutil.rmtree(str(link), ignore_errors=True)
    subprocess.run(
        ['cmd', '/c', 'mklink', '/J', str(link), str(target)],
        check=True, capture_output=True,
    )


def clean():
    """Remove the bake mod source tree (junctions first, then dirs)."""
    if not SOURCE.exists():
        print(f'Nothing to clean at {SOURCE}')
        return
    levels_world = SOURCE / 'Levels' / 'World'
    if levels_world.exists():
        for child in levels_world.iterdir():
            if child.is_dir():
                try:
                    os.rmdir(str(child))
                except OSError:
                    pass
    for d in ['XPack', 'XPack2', 'XPack3', 'XPack4']:
        p = SOURCE / d
        if p.exists() or p.is_symlink():
            try:
                os.rmdir(str(p))
            except OSError:
                shutil.rmtree(str(p), ignore_errors=True)
    shutil.rmtree(str(MOD_DIR), ignore_errors=True)
    print(f'Removed {MOD_DIR}')


def patch_wrl_grid(wrl_path):
    """Patch BC_initialpathway's grid corner in the WRL to the merged shifted value.

    WRL level record: <uint32 path_len><path bytes><52-byte ints_raw>.
    ints_raw[6,7,8] = grid corner (x,y,z) at byte +24 after the path. We locate
    the record by its path string and rewrite offsets +24/+28/+32.
    Returns (old_grid, new_grid).
    """
    d = bytearray(wrl_path.read_bytes())
    needle = b'BC_initialpathway'
    i = d.lower().find(needle.lower())
    if i < 0:
        raise RuntimeError('BC_initialpathway not found in WRL')
    # Find the length-prefixed path record that contains the needle.
    for back in range(4, 100, 1):
        off = i - back
        if off < 0:
            break
        L = struct.unpack_from('<I', d, off)[0]
        if 30 < L < 80 and off + 4 + L <= len(d):
            s = d[off + 4:off + 4 + L]
            if b'BC_initialpathway' in s:
                after = off + 4 + L
                gx, gy, gz = struct.unpack_from('<iii', d, after + 24)
                nx, ny, nz = gx + GRID_SHIFT[0], gy + GRID_SHIFT[1], gz + GRID_SHIFT[2]
                struct.pack_into('<iii', d, after + 24, nx, ny, nz)
                wrl_path.write_bytes(bytes(d))
                return (gx, gy, gz), (nx, ny, nz)
    raise RuntimeError('Could not locate BC_initialpathway length-prefixed record in WRL')


def read_grid_from_lvl_index():
    """Report the compiled grid corner from the SV Levels.arc (authoritative)."""
    from arc_patcher import ArcArchive
    from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
    arc = ArcArchive.from_file(REPO / 'upstream' / 'soulvizier_098i' / 'Resources' / 'Levels.arc')
    data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
    sec = {s['type']: s for s in parse_sections(data)}
    for lv in parse_level_index(data, sec[SEC_LEVELS]):
        if 'bc_initialpathway' in lv['fname'].lower():
            v = struct.unpack_from('<13i', lv['ints_raw'], 0)
            return v[6], v[7], v[8]
    return None


def verify_target_blob():
    """Print BC_initialpathway.lvl section summary (pre-bake baseline)."""
    p = SV_DECOMP / TARGET_REL.replace('/', '\\')
    blob = p.read_bytes()
    secs, _ = parse_blob_sections(blob)
    types = [s['type'] for s in secs]
    print(f'  {p.name}: v0x{blob[3]:02x}, {len(blob):,} bytes')
    print(f'    sections: {[f"0x{t:02x}" for t in types]}')
    print(f'    has 0x0a (PTH): {0x0a in types}   has 0x0b (REC): {0x0b in types}  <- baseline: expect 0x0a True, 0x0b False')


def build(shift_grid=False):
    print('=== Setup BC_initialpathway navmesh-bake source tree ===')
    print(f'Mod: {MOD_NAME}   (isolated bake mod)')
    print(f'Source root: {SOURCE}')
    print(f'Resolves terrain via Tools.ini additionalbuilddirs = game install ; {BUILT_MOD}')
    print()

    # Preconditions
    missing = [p for p in [SV_DECOMP, GAME, BUILT_MOD] if not p.exists()]
    if missing:
        print('ERROR missing prerequisites:')
        for m in missing:
            print('  ', m)
        return
    if not (BUILT_MOD / 'Resources' / 'DRXtextures.arc').exists():
        print(f'ERROR: built mod has no DRXtextures.arc (blood-cave terrain textures). Build/deploy SoulvizierClassic first.')
        return

    levels_world = SOURCE / 'Levels' / 'World'
    levels_world.mkdir(parents=True, exist_ok=True)

    # 1) Copy world01.wrl + world01.sd (real files, not junctions - the Editor rewrites the .wrl/.sd)
    for fname in ['world01.wrl', 'world01.sd']:
        src = SV_DECOMP / fname
        dst = levels_world / fname
        shutil.copy2(str(src), str(dst))
        print(f'Copied {fname} ({src.stat().st_size:,} bytes)')

    # 2) Junction every region dir under Levels/World (Babylon..xBloodCave)
    decomp_world = SV_DECOMP / 'Levels' / 'World'
    for area in sorted(decomp_world.iterdir()):
        if area.is_dir():
            make_junction(levels_world / area.name, area)
            print(f'Junction Levels/World/{area.name}/  -> decompiled_sv')

    # 3) Junction XPack dirs at source root (decompiled_sv only ships XPack)
    for xp in ['XPack', 'XPack2', 'XPack3', 'XPack4']:
        src = SV_DECOMP / xp
        if src.exists():
            make_junction(SOURCE / xp, src)
            print(f'Junction {xp}/  -> decompiled_sv')

    # 4) Optional: patch WRL grid to merged shifted coords (option B)
    if shift_grid:
        old, new = patch_wrl_grid(levels_world / 'world01.wrl')
        print(f'\nWRL grid patch: BC_initialpathway {old} -> {new}  (merged shifted coords)')
    else:
        print('\nWRL grid: UNCHANGED (original SV coords). Reposition on inject via transplant_rec02.')

    # 5) Report the authoritative grid + baseline blob
    print('\n--- Coordinate context ---')
    g = read_grid_from_lvl_index()
    if g:
        print(f'  SV Levels.arc grid corner (authoritative): {g}')
        print(f'  merged shifted grid corner: {(g[0]+GRID_SHIFT[0], g[1]+GRID_SHIFT[1], g[2]+GRID_SHIFT[2])}')
    print('\n--- Pre-bake baseline (BC_initialpathway.lvl) ---')
    verify_target_blob()

    # 6) Print the created tree
    print('\n--- Created source tree ---')
    for item in sorted(SOURCE.iterdir()):
        kind = 'junction' if item.is_symlink() else ('dir' if item.is_dir() else 'file')
        if item.is_file():
            print(f'  {item.name}  ({item.stat().st_size:,} bytes)')
        else:
            print(f'  {item.name}/  ({kind})')
            if item.name == 'Levels':
                wd = item / 'World'
                if wd.exists():
                    for sub in sorted(wd.iterdir()):
                        if sub.is_file():
                            print(f'    Levels/World/{sub.name}  ({sub.stat().st_size:,} bytes)')
                        else:
                            k = 'junction' if sub.is_symlink() else 'dir'
                            print(f'    Levels/World/{sub.name}/  ({k})')

    print('\nDone. Next: fix Tools.ini (additionalbuilddirs), then drive the Editor per the click-steps.')
    print(f'  Editor level to select: {TARGET_NAME}  (in Levels/World/xBloodCave)')


def main():
    if '--clean' in sys.argv:
        clean()
        return
    build(shift_grid='--shift-grid' in sys.argv)


if __name__ == '__main__':
    main()
