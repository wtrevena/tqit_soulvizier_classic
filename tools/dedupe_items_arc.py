#!/usr/bin/env python3
"""Remove files from Items.arc that already exist in SVItems.arc.

Usage:
    python dedupe_items_arc.py <items_arc_path> <svitems_arc_path>

This prevents duplicate resource loading when both archives are present.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arc_patcher import ArcArchive


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <items.arc> <svitems.arc>")
        sys.exit(1)

    items_path = Path(sys.argv[1])
    svitems_path = Path(sys.argv[2])

    if not items_path.exists():
        print(f"Items.arc not found: {items_path}")
        sys.exit(1)
    if not svitems_path.exists():
        print(f"SVItems.arc not found: {svitems_path}")
        sys.exit(0)  # Not an error, just nothing to dedupe against

    sv_arc = ArcArchive.from_file(svitems_path)
    sv_names = set(e.name for e in sv_arc.entries if e.entry_type == 3)

    items_arc = ArcArchive.from_file(items_path)
    before = len([e for e in items_arc.entries if e.entry_type == 3])

    removed = []
    items_arc.entries = [
        e for e in items_arc.entries
        if e.entry_type != 3 or e.name not in sv_names or not removed.append(e.name)
    ]

    after = len([e for e in items_arc.entries if e.entry_type == 3])

    if removed:
        items_arc.write(items_path)
        for name in removed:
            print(f"  Removed duplicate: {name}")
        print(f"  Items.arc: {before} -> {after} files ({len(removed)} duplicates removed)")
    else:
        print("  No duplicates found")


if __name__ == "__main__":
    main()
