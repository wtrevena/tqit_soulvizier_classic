"""
Build Resources/Text.arc for AE Custom Quest deployment.

AE Custom Quest mods load text from Resources/Text.arc containing a single
modstrings.txt file. The game loads base game text first, then overlays mod
text. We only need mod-specific tags in modstrings.txt.

Pipeline:
1. Extract all text from SV 0.98i's Text_EN.arc
2. Consolidate into modstrings.txt (deduplicating tag definitions)
3. Apply Occult mastery label fix
4. Append uber soul tags
5. Pack into Text.arc
"""
import sys
from pathlib import Path
from collections import OrderedDict

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive


def extract_tags(text: str) -> OrderedDict:
    """Parse tag=value lines from a text file, preserving order."""
    tags = OrderedDict()
    for line in text.split('\n'):
        line = line.strip('\r')
        if not line or line.startswith('//'):
            continue
        if '=' in line:
            key, _, value = line.partition('=')
            tags[key.strip()] = value
    return tags


def build_modstrings(sv_arc_path: Path, uber_tags_path: Path = None,
                     extra_tags: dict = None) -> str:
    """Build modstrings.txt content from SV 0.98i Text_EN.arc."""
    arc = ArcArchive.from_file(sv_arc_path)

    text_files = [
        'commonequipment.txt',
        'monsters.txt',
        'skills.txt',
        'uniqueequipment.txt',
        'ui.txt',
        'dialog.txt',
        'install.txt',
        'menu.txt',
        'npc.txt',
        'quest.txt',
        'tutorial.txt',
        'xcommonequipment.txt',
        'xdialog.txt',
        'xinstall.txt',
        'xmenu.txt',
        'xmonsters.txt',
        'xnpc.txt',
        'xquest.txt',
        'xskills.txt',
        'xtutorial.txt',
        'xui.txt',
        'xuniqueequipment.txt',
    ]

    all_tags = OrderedDict()
    sections = []

    for fname in text_files:
        text = arc.get_text(fname)
        if text is None:
            print(f"  WARNING: {fname} not found in arc")
            continue

        tags = extract_tags(text)
        print(f"  {fname}: {len(tags)} tags")

        section_lines = [f'//{fname} - START']
        for key, value in tags.items():
            if key not in all_tags:
                all_tags[key] = value
                section_lines.append(f'{key}={value}')
            elif all_tags[key] != value:
                all_tags[key] = value
                section_lines.append(f'{key}={value}')
        section_lines.append(f'//{fname} - END')
        sections.append('\r\n'.join(section_lines))

    # Apply Occult mastery fixes (label + missing skill descriptions)
    occult_fixes = {
        'tagMasteryBrief05': 'Occult',
        'tagMasteryTitle05': 'Occult Mastery',
        'tagSkillName050': 'Occult Mastery',
        'tagNewSkill321DESC': 'Infusing the Breach with shadow energy, the Occultist reaches through and grasps enemies, immobilizing them as dark forces sap their life force.',
    }
    fix_lines = ['//Occult mastery label fix - START']
    for key, value in occult_fixes.items():
        all_tags[key] = value
        fix_lines.append(f'{key}={value}')
    fix_lines.append('//Occult mastery label fix - END')
    sections.append('\r\n'.join(fix_lines))
    print(f"  Applied Occult mastery fixes ({len(occult_fixes)} tags)")

    # Add uber soul tags
    uber_count = 0
    if uber_tags_path and uber_tags_path.exists():
        uber_text = uber_tags_path.read_text(encoding='utf-8')
        uber_lines = ['//uber_soul_tags - START']
        for line in uber_text.strip().split('\n'):
            line = line.strip()
            if line and '=' in line:
                key, _, value = line.partition('=')
                all_tags[key.strip()] = value
                uber_lines.append(f'{key.strip()}={value}')
                uber_count += 1
        uber_lines.append('//uber_soul_tags - END')
        sections.append('\r\n'.join(uber_lines))
    print(f"  Added {uber_count} uber soul tags")

    # Add any extra tags
    if extra_tags:
        extra_lines = ['//extra_tags - START']
        for key, value in extra_tags.items():
            all_tags[key] = value
            extra_lines.append(f'{key}={value}')
        extra_lines.append('//extra_tags - END')
        sections.append('\r\n'.join(extra_lines))
        print(f"  Added {len(extra_tags)} extra tags")

    print(f"  Total unique tags: {len(all_tags)}")

    return '\r\n'.join(sections) + '\r\n'


def build_text_arc(sv_arc_path: Path, output_path: Path,
                   uber_tags_path: Path = None):
    """Build the final Text.arc file."""
    print(f"Building modstrings.txt from: {sv_arc_path}")
    modstrings = build_modstrings(sv_arc_path, uber_tags_path)

    print(f"\nBuilding Text.arc...")
    # We need to create a new arc with just modstrings.txt
    # Use SVAERA's Text.arc as a template for the structure
    encoded = b'\xff\xfe' + modstrings.encode('utf-16-le')
    print(f"  modstrings.txt: {len(modstrings)} chars, {len(encoded)} bytes")

    # Create arc from scratch - we need a minimal arc with one file
    arc = create_single_file_arc(encoded, 'modstrings.txt')
    size = arc.write(output_path)
    print(f"  Written: {output_path} ({size} bytes)")

    # Verify
    arc2 = ArcArchive.from_file(output_path)
    data = arc2.get_file('modstrings.txt')
    if data and len(data) == len(encoded):
        text_back = arc2.get_text('modstrings.txt')
        if 'tagNewHero' in text_back and 'tagMasteryBrief05=Occult' in text_back:
            print("  Verification: OK (tags found)")
        else:
            print("  WARNING: Tags not found in verification read")
    else:
        print(f"  WARNING: Size mismatch in verification ({len(data) if data else 0} vs {len(encoded)})")

    return output_path


def create_single_file_arc(data: bytes, filename: str) -> ArcArchive:
    """Create a new ArcArchive with a single file entry.

    AE expects a specific structure with empty entries for each directory
    level in the file path (even though modstrings.txt has no path).
    """
    import struct
    import zlib

    arc = ArcArchive()
    arc.version = 1

    # Build string table
    name_bytes = filename.encode('utf-8') + b'\x00'
    arc.raw_string_table = name_bytes

    # Compress data into parts
    PART_SIZE = 262144
    parts = []
    pos = 0
    while pos < len(data):
        chunk = data[pos:pos + PART_SIZE]
        compressed = zlib.compress(chunk, 6)
        parts.append(type('Part', (), {
            'offset': 0, 'comp_size': len(compressed),
            'decomp_size': len(chunk), 'compressed_data': compressed
        })())
        pos += PART_SIZE

    total_comp = sum(p.comp_size for p in parts)

    # Create file entry with proper 44-byte record
    raw_record = bytearray(44)
    struct.pack_into('<I', raw_record, 0, 3)  # entry_type = file
    struct.pack_into('<I', raw_record, 4, 0)  # data_offset (set by write)
    struct.pack_into('<I', raw_record, 8, total_comp)
    struct.pack_into('<I', raw_record, 12, len(data))
    # bytes 16-27: metadata (zeros)
    struct.pack_into('<I', raw_record, 28, len(parts))  # num_parts
    struct.pack_into('<I', raw_record, 32, 0)  # file_index
    struct.pack_into('<I', raw_record, 36, len(filename.encode('utf-8')))
    struct.pack_into('<I', raw_record, 40, 0)  # string_offset

    from arc_patcher import ArcEntry
    entry = ArcEntry(bytes(raw_record))
    entry.name = filename
    entry.parts = []

    for p in parts:
        from arc_patcher import FilePart
        entry.parts.append(FilePart(0, p.comp_size, p.decomp_size, p.compressed_data))

    arc.entries = [entry]
    return arc


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: build_text_arc.py <sv_text_en.arc> <output_text.arc> [uber_tags.txt]")
        sys.exit(1)

    sv_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    uber_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    build_text_arc(sv_path, out_path, uber_path)
