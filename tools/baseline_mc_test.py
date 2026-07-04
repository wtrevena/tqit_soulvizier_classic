#!/usr/bin/env python3
"""
Baseline test: package MapCompiler output into ARC with ZERO modifications.
No metadata patching, no format conversion, no NPC injection.
Purpose: determine if the invisible wall comes from MC output or our post-processing.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive

svaera_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\reference_mods\SVAERA_customquest\Resources\Levels.arc')
mc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\merged_recompiled.map')
out_arc_path = Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc')

print('Loading MapCompiler output...')
mc_data = mc_path.read_bytes()
print(f'  Size: {len(mc_data)/(1024**2):.1f} MB')

# Quick format stats
v11 = mc_data.count(b'LVL\x11')
v0e = mc_data.count(b'LVL\x0e')
v0f = mc_data.count(b'LVL\x0f')
print(f'  LVL magic counts: v0x11={v11}, v0x0e={v0e}, v0x0f={v0f}')
print(f'  drxmap refs: {mc_data.count(b"drxmap")}')

# Package raw MC output into ARC — no modifications at all
print('\nPackaging raw MC output into ARC (no patching)...')
arc = ArcArchive.from_file(svaera_path)
arc.set_file('world/world01.map', mc_data)
arc.write(out_arc_path)
print(f'  Written: {out_arc_path.stat().st_size / (1024**2):.1f} MB')
print('\nBaseline test ready. Deploy with:')
print('  powershell -ExecutionPolicy Bypass -File scripts/deploy_to_custommaps.ps1')
