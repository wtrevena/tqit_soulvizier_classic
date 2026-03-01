#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive

xp_quests = ArcArchive.from_file(Path(r'c:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Resources\XPack\Quests.arc'))
for entry in xp_quests.entries:
    if 'bloodcave' in entry.name.lower():
        data = xp_quests.decompress(entry)
        print(f'=== {entry.name} ({len(data)} bytes) ===')
        # Extract readable strings
        strings = []
        current = []
        for b in data:
            if 32 <= b < 127:
                current.append(chr(b))
            else:
                if len(current) >= 4:
                    strings.append(''.join(current))
                current = []
        if len(current) >= 4:
            strings.append(''.join(current))
        for s in strings:
            print(s)
