import sys
from pathlib import Path
sys.path.insert(0, 'tools')
from arc_patcher import ArcArchive
from merge_levels_binary import parse_sections, parse_level_index, parse_bitmap_index, SEC_LEVELS, SEC_BITMAPS, SEC_DATA2, SEC_GROUPS, SEC_SD

# Load the DEPLOYED arc
deployed = Path(r"C:\Users\willi\OneDrive\Documents\My Games\Titan Quest - Immortal Throne\CustomMaps\SoulvizierClassic\Resources\Levels.arc")
arc = ArcArchive.from_file(deployed)
print(f"Entries: {len(arc.entries)}")
for e in arc.entries:
    print(f"  {e.name} type={e.entry_type} stored_size={e.stored_size}")

data = arc.decompress([e for e in arc.entries if e.entry_type == 3][0])
print(f"\nMap size: {len(data)} bytes ({len(data)/(1024**2):.1f} MB)")

# Verify sections
secs = parse_sections(data)
sec_map = {s['type']: s for s in secs}
print(f"Sections: {[(hex(s['type']), s['size']) for s in secs]}")

levels = parse_level_index(data, sec_map[SEC_LEVELS])
bitmaps = parse_bitmap_index(data, sec_map[SEC_BITMAPS])
print(f"Levels: {len(levels)}")
print(f"Bitmaps: {len(bitmaps)}")
print(f"Bitmaps with data: {sum(1 for b in bitmaps if b['length'] > 0)}")

# Check SV-only levels (last 46)
ae_count = len(levels) - 46  # First 2235 are SVAERA
sv_only_with_bm = sum(1 for i in range(ae_count, len(levels)) if bitmaps[i]['length'] > 0)
print(f"\nSV-only levels ({len(levels) - ae_count}):")
print(f"  With bitmap data: {sv_only_with_bm}")

# Verify key levels
for i, lv in enumerate(levels):
    fname = lv['fname'].replace(chr(92), '/').lower()
    if any(k in fname for k in ['hiddenvalley01', 'random09a', 'bc_initial', 'uberdungeon', 'crypt_floor']):
        bm = bitmaps[i]
        blob = data[lv['data_offset']:lv['data_offset']+4]
        print(f"  [{i}] {fname.split('/')[-1]}: offset={lv['data_offset']}, len={lv['data_length']}, magic={blob.hex()}, bm_len={bm['length']}")

# Compare with local merged output
local = Path(r"c:\Users\willi\repos\tqit_soulvizier_classic\local\Levels_merged.arc")
local_arc = ArcArchive.from_file(local)
local_data = local_arc.decompress([e for e in local_arc.entries if e.entry_type == 3][0])
print(f"\nLocal merged map size: {len(local_data)}")
print(f"Deployed == Local: {data == local_data}")
