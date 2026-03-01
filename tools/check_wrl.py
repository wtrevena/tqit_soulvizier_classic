#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive

sv_arc = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\Levels.arc'))
for entry in sv_arc.entries:
    fn = entry.name.lower()
    if '.wrl' in fn:
        print(f'WRL: {entry.name} (type: {entry.entry_type}, size: {entry.decomp_size})')
        data = sv_arc.decompress(entry)
        text = data.decode('ascii', errors='replace')
        lines = text.split('\n')
        # Find lines referencing bloodcave or secret_place
        for i, line in enumerate(lines):
            ll = line.lower()
            if 'bloodcave' in ll or 'xbloodcave' in ll or 'secret_place' in ll:
                # Print surrounding context
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                for j in range(start, end):
                    marker = ' >> ' if j == i else '    '
                    print(f'{marker}{j}: {lines[j][:200]}')
                print()
