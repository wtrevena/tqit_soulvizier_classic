# -*- coding: utf-8 -*-
"""Find QUEST ITEMS that our cloned uber bosses inherited from their donors.

Will reported two instances (Charon's Oar via the Soul of the Unferried, Key of the Warden
of Souls via the Warden clone). Two is a CLASS, not a coincidence, so this enumerates every
quest-classified item in the built database and every record that can lead to one.

Read-only. Prints; changes nothing.
"""
import sys
from pathlib import Path

sys.path.insert(0, r'C:\Users\willi\repos\tqit_soulvizier_classic\tools')
from arz_patcher import ArzDatabase  # noqa: E402

ARZ = Path(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz')

db = ArzDatabase.from_arz(ARZ)
names = list(db.record_names())
print(f'\nloaded {len(names)} records from {ARZ.name}\n')


def fields(n):
    try:
        return db.get_fields(n) or {}
    except Exception:
        return {}


def val(n, k):
    try:
        return db.get_field_value(n, k)
    except Exception:
        return None


def as_text(x):
    if x is None:
        return ''
    if isinstance(x, (list, tuple)):
        return ' '.join(str(i) for i in x)
    return str(x)


# ---- 1. every quest-classified item -------------------------------------------------
quest_items = {}
for n in names:
    fl = fields(n)
    if not fl:
        continue
    cls = as_text(val(n, 'itemClassification'))
    if cls.strip().lower() == 'quest':
        quest_items[n.lower()] = {
            'path': n,
            'tag': as_text(val(n, 'itemNameTag')),
            'desc': as_text(val(n, 'description')) or as_text(val(n, 'FileDescription')),
        }

print(f'QUEST-classified items: {len(quest_items)}')

# ---- 2. reverse index: which records reference a quest item, in which field ----------
refs = {}
for n in names:
    fl = fields(n)
    if not fl:
        continue
    for k in fl:
        v = as_text(val(n, k))
        if not v or '.dbr' not in v.lower():
            continue
        for token in v.replace(';', ' ').split():
            t = token.strip().lower()
            if t in quest_items:
                refs.setdefault(t, []).append((n, k))

print(f'quest items that ANY record points at: {len(refs)}\n')
print('=' * 100)
print('QUEST ITEMS WITH MORE THAN ONE INBOUND REFERENCE  <-- the leak candidates')
print('=' * 100)

multi = {k: v for k, v in refs.items() if len(v) > 1}
for k, v in sorted(multi.items(), key=lambda kv: -len(kv[1])):
    qi = quest_items[k]
    print(f'\n[{len(v)} refs]  {qi["path"]}')
    print(f'          tag={qi["tag"]}  desc={qi["desc"]}')
    for rec, field in sorted(v):
        print(f'    <- {field:28} {rec}')

# ---- 3. the two Will named, traced explicitly ---------------------------------------
print('\n' + '=' * 100)
print('THE TWO WILL NAMED, by tag/description substring')
print('=' * 100)
for needle in ('oar', 'warden', 'key'):
    print(f'\n--- quest items matching "{needle}":')
    for k, qi in sorted(quest_items.items()):
        blob = (qi['path'] + ' ' + qi['tag'] + ' ' + qi['desc']).lower()
        if needle in blob:
            n_refs = len(refs.get(k, []))
            print(f'  {qi["path"]}  tag={qi["tag"]}  inbound_refs={n_refs}')
            for rec, field in sorted(refs.get(k, [])):
                print(f'      <- {field:26} {rec}')
