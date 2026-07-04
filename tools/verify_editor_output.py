"""
Verify that the TQAE Editor baked a real 0x0b (REC\\x02 / RLTD) navmesh into a
Soulvizier-only level.

Default target: BC_initialpathway (the minimal navmesh-bake repro; see
tools/setup_bc_bake_tree.py). PASS = a 0x0b section is now present in the
Editor-re-saved .lvl, whereas the pre-bake baseline (local/decompiled_sv) has
0x0a (PTH) only and NO 0x0b.

The Editor's optimized output location is version dependent, so this script
searches EVERY plausible location and reports each hit:
  - the re-saved source .lvl:      Working/CustomMaps/<mod>/source/Levels/World/.../<lvl>
  - a "LevelsOptimized\\" sibling:  Working/CustomMaps/<mod>/LevelsOptimized/Levels/World/.../<lvl>
  - the assets build dir:          Working/CustomMaps/<mod>/assets/Levels/World/.../<lvl>
  - anywhere else under the mod dir (recursive fallback glob)
  - the built Levels.arc world01.map (after Build -> Rebuild All Maps), by level name

Standalone runnable:
  py tools/verify_editor_output.py                       # BCBake mod, BC_initialpathway
  py tools/verify_editor_output.py --mod PathingTest --level RuinedCity02
  py tools/verify_editor_output.py --lvl "C:\\path\\to\\some.lvl"   # check one explicit file
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_section_surgery import parse_blob_sections

# --- Paths ---
REPO = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic')
TQ_DOCS = Path(r'C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne')
WORKING = TQ_DOCS / 'Working'
SV_DECOMP = REPO / 'local' / 'decompiled_sv'

DEFAULT_MOD = 'BCBake'
DEFAULT_LEVEL = 'BC_initialpathway'

# Level -> relative path under Levels/World/ (for source/optimized lookups + baseline)
LEVEL_REL = {
    'BC_initialpathway': 'Levels/World/xBloodCave/BC_initialpathway.lvl',
    'RuinedCity02': 'Levels/World/Greece/Area004/RuinedCity02.LVL',
}


def get_arg(flag, default=None):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def blob_report(blob):
    """Return (version, [(type,size)...], has_0a, has_0b, size_0b)."""
    secs, _ = parse_blob_sections(blob)
    types = [(s['type'], len(s['data'])) for s in secs]
    has_0a = any(t == 0x0a for t, _ in types)
    has_0b = any(t == 0x0b for t, _ in types)
    size_0b = next((sz for t, sz in types if t == 0x0b), 0)
    ver = blob[3] if len(blob) > 3 else 0
    return ver, types, has_0a, has_0b, size_0b


def print_blob(label, blob):
    ver, types, has_0a, has_0b, size_0b = blob_report(blob)
    print(f'  [{label}] v0x{ver:02x}, {len(blob):,} bytes')
    print(f'    sections: ' + ', '.join(f'0x{t:02x}({sz:,})' for t, sz in types))
    print(f'    0x0a (PTH): {has_0a}    0x0b (REC): {has_0b}' + (f'  size={size_0b:,}' if has_0b else ''))
    return has_0b, size_0b


def candidate_lvl_paths(mod, level):
    """All plausible on-disk locations for the Editor-re-saved <level>.lvl."""
    rel = LEVEL_REL.get(level, f'Levels/World/xBloodCave/{level}.lvl')
    rel_win = rel.replace('/', '\\')
    mod_dir = WORKING / 'CustomMaps' / mod
    bases = [
        ('source', mod_dir / 'source'),
        ('LevelsOptimized', mod_dir / 'LevelsOptimized'),
        ('assets', mod_dir / 'assets'),
        ('mod-root', mod_dir),
        # legacy uppercase layout used by the old setup script
        ('legacy-Source-Maps', WORKING / mod / 'Source' / 'Maps'),
    ]
    seen = set()
    out = []
    for tag, base in bases:
        for cand in [base / rel_win, base / rel_win.replace('.lvl', '.LVL')]:
            key = str(cand).lower()
            if key not in seen:
                seen.add(key)
                out.append((tag, cand))
    # recursive fallback: any <level>.lvl anywhere under the mod dir
    if mod_dir.exists():
        for hit in list(mod_dir.rglob(f'{level}.lvl')) + list(mod_dir.rglob(f'{level}.LVL')):
            key = str(hit).lower()
            if key not in seen:
                seen.add(key)
                out.append(('rglob', hit))
    return out


def check_in_levels_arc(mod, level):
    """Look for the level's blob inside the mod's built Resources/Levels.arc world01.map."""
    arc_path = TQ_DOCS / 'CustomMaps' / mod / 'Resources' / 'Levels.arc'
    if not arc_path.exists():
        arc_path = WORKING / 'CustomMaps' / mod / 'Resources' / 'Levels.arc'
    if not arc_path.exists():
        return None
    try:
        from arc_patcher import ArcArchive
        from merge_levels_binary import parse_sections, parse_level_index, SEC_LEVELS
        arc = ArcArchive.from_file(arc_path)
        data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
        sec = {s['type']: s for s in parse_sections(data)}
        for lv in parse_level_index(data, sec[SEC_LEVELS]):
            if level.lower() in lv['fname'].lower():
                return arc_path, data[lv['data_offset']:lv['data_offset'] + lv['data_length']]
    except Exception as e:
        print(f'  (Levels.arc probe failed: {e})')
    return None


def main():
    explicit = get_arg('--lvl')
    mod = get_arg('--mod', DEFAULT_MOD)
    level = get_arg('--level', DEFAULT_LEVEL)

    print('=== Verify Editor navmesh bake (0x0b / REC\\x02) ===')

    # Baseline (pre-bake): the untouched SV source blob.
    baseline_path = SV_DECOMP / LEVEL_REL.get(level, f'Levels/World/xBloodCave/{level}.lvl').replace('/', '\\')
    baseline_0b = None
    if baseline_path.exists():
        print(f'\nBaseline (pre-bake) {baseline_path.name}:')
        b_has_0b, _ = print_blob('baseline', baseline_path.read_bytes())
        baseline_0b = b_has_0b
    else:
        print(f'\n(No baseline found at {baseline_path})')

    # Gather candidate re-saved blobs.
    hits = []  # (source_desc, blob)
    if explicit:
        p = Path(explicit)
        if p.exists():
            hits.append((f'explicit:{p}', p.read_bytes()))
        else:
            print(f'\nERROR: --lvl not found: {p}')
            return
    else:
        print(f'\nSearching mod "{mod}" for re-saved {level}.lvl ...')
        for tag, cand in candidate_lvl_paths(mod, level):
            if cand.exists():
                # Skip the junction-resolved source copy if it is byte-identical to baseline
                # (i.e. the Editor has not re-saved it yet).
                blob = cand.read_bytes()
                hits.append((f'{tag}:{cand}', blob))
        arc_hit = check_in_levels_arc(mod, level)
        if arc_hit:
            hits.append((f'Levels.arc:{arc_hit[0]}', arc_hit[1]))

    if not hits:
        print('\nNO candidate .lvl found. Did the Editor run + Save All? Locations searched:')
        for tag, cand in candidate_lvl_paths(mod, level):
            print(f'   [{tag}] {cand}')
        print('   Levels.arc: CustomMaps/<mod>/Resources/Levels.arc (world01.map)')
        return

    # Report each hit; determine overall pass.
    print(f'\nFound {len(hits)} candidate blob(s):')
    any_pass = False
    best = None
    for desc, blob in hits:
        print(f'\n- {desc}')
        has_0b, size_0b = print_blob('candidate', blob)
        if has_0b:
            any_pass = True
            if best is None or size_0b > best[1]:
                best = (desc, size_0b, blob)

    print('\n' + '=' * 64)
    if any_pass:
        print(f'PASS: a baked 0x0b (REC\\x02) navmesh is present.')
        print(f'  best: {best[0]}  (0x0b size {best[1]:,} bytes)')
        if baseline_0b is False:
            print(f'  baseline had NO 0x0b -> the Editor generated it. Good to harvest.')
        # Save the winning blob for the inject pipeline.
        out = REPO / 'local' / 'editor_normalized' / f'{level}.lvl'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(best[2])
        print(f'  saved harvested blob -> {out}')
        print(f'\n  Next: inject via build_section_surgery.inject_rec02_into_blob(')
        print(f'          blob, ints_raw, donor_data=<this 0x0b>, use_stub=False)')
        print(f'        (option A: transplant_rec02 repositions header center to the')
        print(f'         merged shifted grid; option B WRL-shift bake needs no reposition.)')
    else:
        print('FAIL: no 0x0b (REC\\x02) section in any candidate.')
        print('  If candidates still have 0x0a only: Rebuild Pathing did not run, or the')
        print('  level was not selected in EDITOR MODE with terrain rendered (black view =>')
        print('  CreatePathMesh skipped). Re-check Tools.ini additionalbuilddirs + terrain GO/NO-GO.')
    print('=' * 64)


if __name__ == '__main__':
    main()
