"""
Set up a TQAE Art Manager project for the Editor normalization proof test.

For imported/decompiled worlds, the correct source tree layout is:
  source/Levels/World/world01.wrl
  source/Levels/World/world01.sd
  source/Levels/World/<area>/<level>.lvl
  source/XPack/Levels/<area>/<level>.lvl
  source/XPack2/Levels/<area>/<level>.lvl
  ...

This script creates directory junctions from the mod's source tree to the
SVAERA decompiled level directories, with world01.wrl and world01.sd copied
into source/Levels/World/.

Usage modes:
  py tools/setup_editor_proof_test.py                # Pure SVAERA (validation)
  py tools/setup_editor_proof_test.py --swap-sv      # Swap RuinedCity02 with SV version

After this script:
1. Open Editor -> select PathingTest mod
2. Open world01 from source/Levels/World/
3. In Layout Mode: Build -> Rebuild All Pathing (or Rebuild Selected Pathing)
4. File -> Save All
5. Close Editor
6. Run verify_editor_output.py to check the result
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_section_surgery import parse_blob_sections

# Paths
REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
TQ_DOCS = Path(r'C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne')
WORKING = TQ_DOCS / 'Working'
MOD_NAME = 'PathingTest'
MOD_DIR = WORKING / 'CustomMaps' / MOD_NAME

SVAERA_DECOMP = REPO / 'local' / 'decompiled_svaera'
SV_DECOMP = REPO / 'local' / 'decompiled_sv'

# Target level for SV swap
TARGET_FNAME = 'Levels/World/Greece/Area004/RuinedCity02.LVL'
TARGET_AE_IDX = 30


def make_junction(link_path, target_path):
    """Create a Windows directory junction. Remove existing if present."""
    link = Path(link_path)
    target = Path(target_path)
    if link.exists() or link.is_symlink():
        # Remove junction/symlink (os.rmdir for junctions, shutil.rmtree for real dirs)
        try:
            os.rmdir(str(link))
        except OSError:
            shutil.rmtree(str(link))
    subprocess.run(
        ['cmd', '/c', 'mklink', '/J', str(link), str(target)],
        check=True, capture_output=True,
    )


def clean_source_dir(source_dir):
    """Remove old source layout (Maps/ and any stale junctions)."""
    maps_dir = source_dir / 'Maps'
    if maps_dir.exists():
        # Remove junctions first, then the directory
        for child in maps_dir.iterdir():
            if child.is_dir():
                try:
                    os.rmdir(str(child))  # junction
                except OSError:
                    pass
        shutil.rmtree(str(maps_dir), ignore_errors=True)
        print(f'Cleaned old: {maps_dir}')

    # Remove old source/Levels junction or directory
    for d in ['Levels', 'XPack', 'XPack2', 'XPack3', 'XPack4']:
        p = source_dir / d
        if p.exists() or p.is_symlink():
            try:
                os.rmdir(str(p))
            except OSError:
                shutil.rmtree(str(p), ignore_errors=True)
            print(f'Cleaned old: {p}')


def setup_imported_world(source_dir, decomp_dir, swap_sv=False):
    """
    Set up the imported-world source tree layout.

    source/
      Levels/World/
        world01.wrl         (copied from decomp)
        world01.sd          (copied from decomp)
        Babylon/ -> junction (to decomp/Levels/World/Babylon)
        Egypt/   -> junction
        Greece/  -> junction
        ...
      XPack/  -> junction (to decomp/XPack)
      XPack2/ -> junction (to decomp/XPack2)
      XPack3/ -> junction (to decomp/XPack3)
      XPack4/ -> junction (to decomp/XPack4)
    """
    levels_world = source_dir / 'Levels' / 'World'
    levels_world.mkdir(parents=True, exist_ok=True)

    # Copy world01.wrl and world01.sd into source/Levels/World/
    for fname in ['world01.wrl', 'world01.sd']:
        src = decomp_dir / fname
        dst = levels_world / fname
        if src.exists():
            shutil.copy2(str(src), str(dst))
            print(f'Copied: {fname} ({src.stat().st_size:,} bytes)')
        else:
            print(f'WARNING: {src} not found')

    # Junction each area subdir in Levels/World/ (Greece, Babylon, etc.)
    decomp_world = decomp_dir / 'Levels' / 'World'
    for area_dir in sorted(decomp_world.iterdir()):
        if area_dir.is_dir():
            link = levels_world / area_dir.name
            make_junction(link, area_dir)
            print(f'Junction: Levels/World/{area_dir.name}/')

    # Junction XPack, XPack2, XPack3, XPack4 at source root
    for xp in ['XPack', 'XPack2', 'XPack3', 'XPack4']:
        src = decomp_dir / xp
        if src.exists():
            link = source_dir / xp
            make_junction(link, src)
            print(f'Junction: {xp}/')

    # If swap_sv, replace RuinedCity02 with SV version
    if swap_sv:
        ae_lvl = levels_world / TARGET_FNAME.replace('Levels/World/', '').replace('/', '\\')
        sv_lvl = SV_DECOMP / TARGET_FNAME.replace('/', '\\')

        if not sv_lvl.exists():
            # Try lowercase
            sv_lvl = SV_DECOMP / TARGET_FNAME.lower().replace('/', '\\')

        if not ae_lvl.exists():
            print(f'ERROR: SVAERA level not found at {ae_lvl}')
            return False

        if not sv_lvl.exists():
            print(f'ERROR: SV level not found at {sv_lvl}')
            return False

        # Backup SVAERA version
        backup = ae_lvl.with_suffix('.lvl.svaera_bak')
        if not backup.exists():
            # The junction means this modifies the decompiled_svaera dir
            # Make a backup in local/sv_originals/ instead
            backup_dir = REPO / 'local' / 'sv_originals'
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup = backup_dir / 'RuinedCity02_svaera.lvl.bak'
            if not backup.exists():
                shutil.copy2(str(ae_lvl), str(backup))
                print(f'Backed up SVAERA version: {backup}')

        shutil.copy2(str(sv_lvl), str(ae_lvl))
        print(f'Swapped: {ae_lvl.name} with SV version ({sv_lvl.stat().st_size:,} bytes)')

    return True


def verify_level(lvl_path):
    """Print section info for a level file."""
    if not lvl_path.exists():
        print(f'  Not found: {lvl_path}')
        return
    blob = lvl_path.read_bytes()
    secs, _ = parse_blob_sections(blob)
    sec_types = [s['type'] for s in secs]
    ver = blob[3] if len(blob) > 3 else 0
    has_0a = 0x0a in sec_types
    has_0b = 0x0b in sec_types
    print(f'  v0x{ver:02x}, {len(blob):,} bytes')
    print(f'  Sections: {[f"0x{t:02x}" for t in sec_types]}')
    print(f'  Has 0x0a (PTH): {has_0a}')
    print(f'  Has 0x0b (REC): {has_0b}')


def main():
    swap_sv = '--swap-sv' in sys.argv

    print('=== TQAE Editor Proof Test Setup ===')
    print(f'Mod: {MOD_NAME}')
    print(f'Mode: {"SVAERA + SV swap" if swap_sv else "Pure SVAERA (validation)"}')
    print(f'Decomp source: {SVAERA_DECOMP}')
    print()

    source_dir = MOD_DIR / 'source'

    # Step 1: Clean old layout
    print('--- Cleaning old source layout ---')
    clean_source_dir(source_dir)
    print()

    # Step 2: Set up imported-world layout
    print('--- Setting up imported-world layout ---')
    if not setup_imported_world(source_dir, SVAERA_DECOMP, swap_sv=swap_sv):
        return
    print()

    # Step 3: Verify the target level
    levels_world = source_dir / 'Levels' / 'World'
    rc_path = levels_world / TARGET_FNAME.replace('Levels/World/', '').replace('/', '\\')
    print(f'--- RuinedCity02 at: {rc_path} ---')
    verify_level(rc_path)
    print()

    # Step 4: Print directory tree summary
    print('--- Source tree ---')
    for item in sorted(source_dir.iterdir()):
        if item.is_symlink() or item.is_dir():
            kind = 'junction' if item.is_symlink() else 'dir'
            print(f'  {item.name}/ ({kind})')
            if item.name == 'Levels':
                world_dir = item / 'World'
                if world_dir.exists():
                    for sub in sorted(world_dir.iterdir()):
                        if sub.is_dir():
                            kind2 = 'junction' if sub.is_symlink() else 'dir'
                            print(f'    Levels/World/{sub.name}/ ({kind2})')
                        else:
                            print(f'    Levels/World/{sub.name} ({sub.stat().st_size:,} bytes)')
    print()

    print(f'{"="*60}')
    print(f'Setup complete.')
    print()
    print(f'Next steps:')
    print(f'1. Open Editor:')
    print(f'   "{Path(r"C:\\Program Files (x86)\\Steam\\steamapps\\common\\Titan Quest Anniversary Edition\\Editor.exe")}"')
    print(f'   -> Select mod "{MOD_NAME}"')
    print(f'   -> Open world01 from Levels/World/ (NOT from Maps/)')
    print()
    print(f'2. Switch to Layout Mode (tab at bottom)')
    print(f'   -> You should see level tiles in the layout view')
    print()
    if swap_sv:
        print(f'3. Select RuinedCity02 tile -> Build -> Rebuild Selected Pathing')
        print(f'4. File -> Save All')
        print(f'5. Close Editor')
        print(f'6. Verify: py tools/verify_editor_output.py')
    else:
        print(f'3. If layout tiles are visible: SUCCESS')
        print(f'   Run again with --swap-sv to swap RuinedCity02')
        print(f'   py tools/setup_editor_proof_test.py --swap-sv')
    print(f'{"="*60}')


if __name__ == '__main__':
    main()
