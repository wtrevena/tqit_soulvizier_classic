# -*- coding: utf-8 -*-
"""Will's criterion is a DISPLAY one: "only guys with stars above their heads or better should
drop souls, or guys with purple names". He also doubts the gigantic bats qualify.

So: print the engine's monsterClassification for the exact creatures I quoted at him, and split
the 210 hero-class-at-zero group by class, so his visual rule can be mapped onto real field
values instead of my assumptions. Read-only.
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


NAMED = ['am_giganticbat_12', 'am_giganticbat_14', 'am_giganticbat_16',
         'am_carrionlord_12', 'bm_plaguelord_10', 'em_sirenofthedeep_37',
         'us_mormo_16', 'hero_adarathelovely_43', 'um_legion_28',
         'ar_slayer_11', 'elite_ar_slayer_14', 'ember_satyr_warden_55',
         'us_frostscarab_35', 'carrioncrow_05', 'swift_ar_archer_08']

index = {}
for n in db.record_names():
    index.setdefault(n.lower().split(SEP)[-1].replace('.dbr', ''), n)

print('THE CREATURES I QUOTED - what the engine actually classifies them as')
print(f'{"record":34} {"classification":14} {"soulChance":>10}  nameTag')
for want in NAMED:
    rec = index.get(want.lower())
    if not rec:
        print(f'{want:34} (not found)')
        continue
    print(f'{want:34} {t(rec, "monsterClassification").split(";")[0] or "(unset)":14} '
          f'{t(rec, "chanceToEquipFinger2").split(";")[0] or "-":>10}  {t(rec, "description")}')

print()
print('=' * 92)
print('THE 210 SOUL-CARRIERS AT 0% THAT ARE NOT COMMON - split by class')
print('=' * 92)
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
    if ch == 0 and cls.lower() not in ('common', '(unset)'):
        rows.append((cls, n))
by = collections.Counter(c for c, _ in rows)
for c in sorted(by):
    print(f'  {c:12} {by[c]:5}')
print()
for c in sorted(by):
    print(f'--- {c} examples:')
    for n in sorted(x for cc, x in rows if cc == c)[:10]:
        print('     ', n.split(SEP)[-1])
