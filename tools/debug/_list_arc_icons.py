"""List .tex entries in one or more .arc files, optional substring filter.

Usage: py tools/debug/_list_arc_icons.py <substr> <arc1> [arc2 ...]
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from arc_patcher import ArcArchive


def main():
    substr = sys.argv[1].lower()
    for arc_path in sys.argv[2:]:
        arc = ArcArchive.from_file(Path(arc_path))
        hits = sorted(e.name for e in arc.entries
                      if substr in e.name.lower() and e.name.lower().endswith('.tex'))
        print(f"\n### {os.path.basename(arc_path)}: {len(hits)} match '{substr}'")
        for h in hits:
            print("  ", h)


if __name__ == '__main__':
    main()
