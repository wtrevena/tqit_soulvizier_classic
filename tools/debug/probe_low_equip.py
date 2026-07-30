# -*- coding: utf-8 -*-
"""Will asked: which soul-bearing creatures sit at 25% or lower? Classify them so he can apply
his own policy (25% for fixed-location bosses, 33% for non-fixed). Read-only.

"Fixed-location boss" is inferred from the record's own naming/folder conventions, which is a
HEURISTIC and is labelled as such - a real fixed/roaming determination needs the proxy+map side.
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


BOSSY = ('boss', 'questbosses', 'uniquemonster', 'secrethero', 'telkine', 'titan')


def classify(path):
    p = path.lower()
    base = p.split(SEP)[-1]
    if base.startswith('um_'):
        return 'UBER (ours, um_*)'
    if any(b in p for b in BOSSY):
        return 'BOSS-ish (name/folder)'
    if 'hero' in p:
        return 'HERO/champion-ish'
    return 'ordinary monster'


rows = []
for n in db.record_names():
    fl = flds(n)
    if 'chanceToEquipFinger2' not in fl:
        continue
    if 'soul' not in t(n, 'lootFinger2Item1').lower():
        continue
    try:
        ch = float(t(n, 'chanceToEquipFinger2').split(';')[0])
    except ValueError:
        continue
    if ch <= 0 or ch > 25.0:
        continue
    rows.append((ch, classify(n), n))

print('SOUL-BEARING CREATURES AT 25% OR LOWER (excluding the 0% group):', len(rows))
print()
by = collections.defaultdict(list)
for ch, kind, n in rows:
    by[(ch, kind)].append(n)

for ch in sorted({c for c, _, _ in rows}, reverse=True):
    tot = sum(1 for c, _, _ in rows if c == ch)
    print('=' * 92)
    print(f'{ch:>6.1f} %   ({tot} creatures)')
    for kind in ('UBER (ours, um_*)', 'BOSS-ish (name/folder)', 'HERO/champion-ish', 'ordinary monster'):
        names = by.get((ch, kind), [])
        if not names:
            continue
        print(f'    {kind}: {len(names)}')
        for n in sorted(names)[:14]:
            print('       ', n.split(SEP)[-1])
        if len(names) > 14:
            print(f'        ... and {len(names) - 14} more')
    print()
