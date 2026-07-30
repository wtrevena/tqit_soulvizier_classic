# -*- coding: utf-8 -*-
"""Will is right that not every monster wears its soul at full chance. Get the real distribution
of chanceToEquipFinger2 across every soul-bearing creature - and note that in this engine the same
field decides BOTH whether the monster spawns wearing the soul (so gets its stats) AND whether it
drops it. Read-only.
"""
import collections
import os
import sys
from pathlib import Path

sys.path.insert(0, r'C:\Users\willi\repos\tqit_soulvizier_classic\tools')
from arz_patcher import ArzDatabase  # noqa: E402

db = ArzDatabase.from_arz(Path(
    r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz'))
SEP = os.sep


def t(n, k):
    try:
        v = db.get_field_value(n, k)
    except Exception:
        return ''
    if v is None:
        return ''
    if isinstance(v, (list, tuple)):
        return ';'.join(str(i) for i in v)
    return str(v)


def flds(n):
    try:
        return db.get_fields(n) or {}
    except Exception:
        return {}


rows = []
for n in db.record_names():
    fl = flds(n)
    if 'chanceToEquipFinger2' not in fl:
        continue
    slot = t(n, 'lootFinger2Item1')
    if 'soul' not in slot.lower():
        continue
    try:
        ch = float(t(n, 'chanceToEquipFinger2').split(';')[0])
    except ValueError:
        continue
    rows.append((ch, n))

print('soul-bearing creatures with a chanceToEquipFinger2:', len(rows))
print()
dist = collections.Counter(round(c, 1) for c, _ in rows)
print('DISTRIBUTION of chanceToEquipFinger2:')
for val in sorted(dist, reverse=True):
    print(f'   {val:7.1f} %  ->  {dist[val]:5} creatures')

print()
print('the 100% carriers (these are the fixed-spawn ubers - R-48 territory, do NOT retune):')
hundred = sorted(n for c, n in rows if c >= 99.9)
print('   count:', len(hundred))
for n in hundred[:40]:
    print('    ', n.split(SEP)[-1])
if len(hundred) > 40:
    print(f'     ... and {len(hundred) - 40} more')
