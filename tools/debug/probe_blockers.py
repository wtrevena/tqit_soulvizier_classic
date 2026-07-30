# -*- coding: utf-8 -*-
"""Two blocking questions, answered together.

1. Who else carries toxeus_passiveproperties? If anything outside the Toxeus champions uses it,
   the reflect cut must go into a champion-specific passive instead of editing in place (the
   genericbossorb_04 lesson).
2. The Gaoler ruling: base um_polisgaoler_99 must NOT drop its soul, only um_polisgaoler_unbound_99.
   What are their current rates?

Also dumps the Devourer's defensive block, since Will reports he is unkillable even with pets.
Read-only.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, r'C:\Users\willi\repos\tqit_soulvizier_classic\tools')
from arz_patcher import ArzDatabase  # noqa: E402

db = ArzDatabase.from_arz(Path(
    r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz'))
SEP = os.sep
PASSIVE = r'records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr'


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


print('=' * 92)
print('1. EVERY record that references toxeus_passiveproperties')
print('=' * 92)
carriers = []
for n in db.record_names():
    fl = flds(n)
    for k in fl:
        if not k.lower().startswith('skillname'):
            continue
        if PASSIVE.lower() in t(n, k).lower():
            carriers.append((n, k))
            break
print('count:', len(carriers))
for n, k in sorted(carriers):
    print(f'   [{k}] {n}')
print()
print('  VERDICT:', 'SAFE to edit in place (Toxeus champions only)'
      if all('toxeus' in n.lower() or 'bloodtoxeus' in n.lower() for n, _ in carriers)
      else 'DO NOT edit in place - non-Toxeus carriers present, mint a champion-specific passive')

print()
print('=' * 92)
print('2. THE GAOLER PAIR - current soul equip rates')
print('=' * 92)
for rec in (r'records\xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr',
            r'records\xpack\creatures\monster\gigantes\um_polisgaoler_unbound_99.dbr'):
    if not db.has_record(rec):
        print('  MISSING', rec)
        continue
    print(' ', rec.split(SEP)[-1])
    print('     class            :', t(rec, 'monsterClassification'))
    print('     soul equip chance:', t(rec, 'chanceToEquipFinger2'))
    print('     soul slot        :', t(rec, 'lootFinger2Item1'))
    print('     quest drop       :', t(rec, 'perPartyMemberDropItemName'))

print()
print('=' * 92)
print('3. THE DEVOURER DEFENSIVE BLOCK (Will: unkillable even with two pets, on Epic)')
print('=' * 92)
dev = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'
for k in sorted(flds(dev)):
    kl = k.lower()
    if kl.startswith(('defensive', 'character')) or 'life' in kl or 'health' in kl:
        v = t(dev, k)
        if v.strip() and v.strip() not in ('0', '0.0', '0.000000'):
            print(f'   {k:44} = {v}')
print()
print('   and the shared passive it wears:')
for k in sorted(flds(PASSIVE)):
    v = t(PASSIVE, k)
    if v.strip() and v.strip() not in ('0', '0.0', '0.000000') and k.lower().startswith(('defensive', 'character')):
        print(f'   {k:44} = {v}')
