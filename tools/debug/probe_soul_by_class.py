# -*- coding: utf-8 -*-
"""Will: "most of the monsters that have a soul are probably trash monsters, only hero monsters
should drop their soul."

The engine has an authoritative signal for this - monsterClassification (Common / Champion / Hero /
Quest / Boss) - which beats my earlier name-based guessing. Cross-tabulate soul equip chance
against classification, so the rate policy can be applied to the right creatures instead of
blanket-raising trash. Read-only.
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
    if 'soul' not in t(n, 'lootFinger2Item1').lower():
        continue
    try:
        ch = float(t(n, 'chanceToEquipFinger2').split(';')[0])
    except ValueError:
        continue
    cls = (t(n, 'monsterClassification').split(';')[0] or '(unset)').strip()
    rows.append((ch, cls, n))

print('soul-bearing creatures:', len(rows))
print()
print('=' * 92)
print('CROSS-TAB: equip chance  x  monsterClassification')
print('=' * 92)
rates = sorted({r[0] for r in rows}, reverse=True)
classes = sorted({r[1] for r in rows})
hdr = 'rate'.rjust(8) + ''.join(c[:12].rjust(14) for c in classes) + '     TOTAL'
print(hdr)
for ch in rates:
    line = f'{ch:8.1f}'
    tot = 0
    for c in classes:
        k = sum(1 for a, b, _ in rows if a == ch and b == c)
        tot += k
        line += (str(k) if k else '.').rjust(14)
    print(line + str(tot).rjust(10))
line = 'TOTAL'.rjust(8)
for c in classes:
    line += str(sum(1 for _, b, _ in rows if b == c)).rjust(14)
print(line + str(len(rows)).rjust(10))

print()
print('=' * 92)
print('THE DECISIVE NUMBER: non-zero soul chance on COMMON (trash) monsters')
print('=' * 92)
common_nonzero = [(ch, n) for ch, c, n in rows if c.lower() == 'common' and ch > 0]
print('count:', len(common_nonzero))
byrate = collections.Counter(round(c, 1) for c, _ in common_nonzero)
for r in sorted(byrate, reverse=True):
    print(f'   at {r:6.1f} % : {byrate[r]:5} common monsters')
print()
print('  sample:')
for ch, n in sorted(common_nonzero, reverse=True)[:20]:
    print(f'   {ch:6.1f} %  {n.split(SEP)[-1]}')

print()
print('=' * 92)
print('AND: HERO-class carriers currently at ZERO (would never drop despite being heroes)')
print('=' * 92)
hero_zero = [n for ch, c, n in rows if c.lower() in ('hero', 'champion', 'quest', 'boss') and ch == 0]
print('count:', len(hero_zero))
for n in sorted(hero_zero)[:20]:
    print('   ', n.split(SEP)[-1])
if len(hero_zero) > 20:
    print(f'    ... and {len(hero_zero) - 20} more')
