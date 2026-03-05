"""
Find all monsters with soul drops that have a low drop rate.

Scans the .arz database for records where:
  - lootFinger2Item1 contains "soul" in the path
  - chanceToEquipFinger2 is > 0 but < 66%

Groups results by drop-rate range and prints a sorted table.

Usage:
    py tools/find_low_droprate_souls.py <database.arz>
"""
import sys
import os
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from arz_patcher import ArzDatabase


# ---------------------------------------------------------------------------
# Field helpers (from existing scripts)
# ---------------------------------------------------------------------------

def fv(fields, name):
    """Get first field value or None."""
    if fields is None:
        return None
    if name in fields:
        v = fields[name].values
        return v[0] if len(v) == 1 else v
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            v = tf.values
            return v[0] if len(v) == 1 else v
    return None


def fvl(fields, name):
    """Get field value as list."""
    if fields is None:
        return []
    if name in fields:
        return fields[name].values
    for key, tf in fields.items():
        if key.split('###')[0] == name:
            return tf.values
    return []


def fmt_levels(levels):
    """Format charLevel list for display."""
    if not levels:
        return '?'
    return ', '.join(str(int(l)) for l in levels)


# ---------------------------------------------------------------------------
# Drop-rate range classification
# ---------------------------------------------------------------------------

def classify_range(rate):
    """Classify a drop rate into a named range bucket."""
    if rate < 5:
        return '0-5%'
    elif rate < 10:
        return '5-10%'
    elif rate < 25:
        return '10-25%'
    elif rate < 50:
        return '25-50%'
    elif rate < 66:
        return '50-66%'
    else:
        return '66%+'


RANGE_ORDER = ['0-5%', '5-10%', '10-25%', '25-50%', '50-66%']


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <database.arz>', file=sys.stderr)
        sys.exit(1)

    db_path = Path(sys.argv[1])
    print(f'Loading database: {db_path}', file=sys.stderr)
    db = ArzDatabase.from_arz(db_path)

    all_records = list(db.record_names())
    print(f'Database loaded. {len(all_records)} records total.', file=sys.stderr)

    # -----------------------------------------------------------------
    # Scan: find records with soul in lootFinger2Item1 and drop rate < 66%
    # -----------------------------------------------------------------
    entries = []

    for name in all_records:
        fields = db.get_fields(name)
        if not fields:
            continue

        # Check lootFinger2Item1 for a soul path
        soul_vals = fvl(fields, 'lootFinger2Item1')
        if not soul_vals:
            continue

        # At least one value must contain "soul"
        soul_paths = [str(v) for v in soul_vals if v and 'soul' in str(v).lower()]
        if not soul_paths:
            continue

        # Get drop rate
        drop_vals = fvl(fields, 'chanceToEquipFinger2')
        if not drop_vals:
            continue

        # Use first numeric value as the rate
        try:
            drop_rate = float(drop_vals[0])
        except (ValueError, TypeError):
            continue

        # We want > 0 and < 66
        if drop_rate <= 0 or drop_rate >= 66:
            continue

        mc = fv(fields, 'monsterClassification') or '(none)'
        levels = fvl(fields, 'charLevel')
        soul_display = soul_paths[0]
        range_bucket = classify_range(drop_rate)

        entries.append({
            'record': name,
            'classification': mc,
            'charLevel': fmt_levels(levels),
            'soul_item': soul_display,
            'drop_rate': drop_rate,
            'range': range_bucket,
        })

    print(f'Found {len(entries)} records with soul drops and rate in (0%, 66%).', file=sys.stderr)

    # -----------------------------------------------------------------
    # Group by range and sort
    # -----------------------------------------------------------------
    by_range = defaultdict(list)
    for e in entries:
        by_range[e['range']].append(e)

    # Sort each group by drop rate ascending, then by record path
    for rng in by_range:
        by_range[rng].sort(key=lambda e: (e['drop_rate'], e['record']))

    # -----------------------------------------------------------------
    # Output
    # -----------------------------------------------------------------
    lines = []

    def out(s=''):
        lines.append(s)

    out('=' * 160)
    out('SOULVIZIER CLASSIC - LOW DROP-RATE SOUL AUDIT')
    out('=' * 160)
    out(f'Database: {db_path}')
    out(f'Total records scanned: {len(all_records)}')
    out(f'Records with soul drops and rate in (0%, 66%): {len(entries)}')
    out()

    # Summary counts
    out('SUMMARY BY RANGE:')
    for rng in RANGE_ORDER:
        group = by_range.get(rng, [])
        out(f'  {rng:8s}: {len(group):4d} records')
    out()

    # Count by classification across all ranges
    class_counts = defaultdict(int)
    for e in entries:
        class_counts[e['classification']] += 1
    out('SUMMARY BY CLASSIFICATION:')
    for cls in sorted(class_counts.keys()):
        out(f'  {cls:15s}: {class_counts[cls]:4d} records')
    out()

    # Detailed tables per range
    for rng in RANGE_ORDER:
        group = by_range.get(rng, [])
        if not group:
            continue

        out('=' * 160)
        out(f'RANGE: {rng}  ({len(group)} records)')
        out('=' * 160)
        out()

        # Table header
        hdr = f'{"#":>4s}  {"Drop%":>6s}  {"Classification":15s}  {"Levels":12s}  {"Record Path"}'
        out(hdr)
        out('-' * 160)

        for i, e in enumerate(group, 1):
            row = (
                f'{i:4d}  '
                f'{e["drop_rate"]:5.1f}%  '
                f'{e["classification"]:15s}  '
                f'{e["charLevel"]:12s}  '
                f'{e["record"]}'
            )
            out(row)
            # Soul item on next line, indented
            out(f'      {"":6s}  {"":15s}  {"":12s}  Soul: {e["soul_item"]}')

        out()

    # -----------------------------------------------------------------
    # Critical section: just the sub-25% records for quick reference
    # -----------------------------------------------------------------
    critical = [e for e in entries if e['drop_rate'] < 25]
    critical.sort(key=lambda e: (e['drop_rate'], e['record']))

    out('=' * 160)
    out(f'CRITICAL: ALL RECORDS WITH DROP RATE < 25%  ({len(critical)} records)')
    out('=' * 160)
    out()

    if critical:
        hdr = f'{"#":>4s}  {"Drop%":>6s}  {"Classification":15s}  {"Levels":12s}  {"Record Path"}'
        out(hdr)
        out('-' * 160)

        for i, e in enumerate(critical, 1):
            row = (
                f'{i:4d}  '
                f'{e["drop_rate"]:5.1f}%  '
                f'{e["classification"]:15s}  '
                f'{e["charLevel"]:12s}  '
                f'{e["record"]}'
            )
            out(row)
            out(f'      {"":6s}  {"":15s}  {"":12s}  Soul: {e["soul_item"]}')
    else:
        out('  (none)')

    out()

    output_text = '\n'.join(lines)
    print(output_text)


if __name__ == '__main__':
    main()
