# -*- coding: utf-8 -*-
"""EXHAUSTIVE: every uber (um_*) record we ship that carries a perPartyMemberDropItemName.

Will found two quest-item leaks by playing (Charon's Oar, Key of the Warden of Souls). Two is
a class, so this enumerates the whole surface rather than fixing the two he happened to meet.
Read-only.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, r'C:\Users\willi\repos\tqit_soulvizier_classic\tools')
from arz_patcher import ArzDatabase  # noqa: E402

db = ArzDatabase.from_arz(Path(
    r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz'))
SEP = os.sep  # backslash, without embedding one in a literal


def txt(n, k):
    try:
        v = db.get_field_value(n, k)
    except Exception:
        return ''
    if v is None:
        return ''
    if isinstance(v, (list, tuple)):
        return ' '.join(str(i) for i in v)
    return str(v)


# quest-classified item paths, lowercased
quest = set()
for n in db.record_names():
    if txt(n, 'itemClassification').strip().lower() == 'quest':
        quest.add(n.lower())

rows = []
for n in db.record_names():
    base = n.lower().split(SEP)[-1]
    if not base.startswith('um_'):
        continue
    q = txt(n, 'perPartyMemberDropItemName').strip()
    if q:
        rows.append((n, q, txt(n, 'perPartyMemberDropChance'), txt(n, 'description'),
                     q.lower() in quest))

print()
print('EVERY um_* RECORD CARRYING perPartyMemberDropItemName')
print('total:', len(rows), ' of which point at a QUEST-classified item:',
      sum(1 for r in rows if r[4]))
for n, q, c, d, isq in sorted(rows, key=lambda r: (not r[4], r[0])):
    print()
    print(('  *** QUEST-ITEM LEAK ***' if isq else '  (non-quest drop)'))
    print('   record:', n)
    print('   drops :', q)
    print('   chance:', c, '| desc:', d)
