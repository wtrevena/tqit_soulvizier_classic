# -*- coding: utf-8 -*-
"""Will: "the reflect damage is what makes these variants nearly unkillable since i one shot
myself when i hit them". Find every reflect/retaliation source on the Toxeus champions - on the
creature records AND on the passive skills they carry, since that is where a shared buff would hide.
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
HINT = ('reflect', 'retaliation', 'retal')

CHAMPS = {
    'Enslaver  ': r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr',
    'Devourer  ': r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr',
    'EndlessHnt': r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr',
    'Leinth    ': r'records\drxcreatures\bloodwitch\q_leinth_50.dbr',
}


def t(n, k):
    try:
        v = db.get_field_value(n, k)
    except Exception:
        return ''
    if v is None:
        return ''
    if isinstance(v, (list, tuple)):
        return ' '.join(str(i) for i in v)
    return str(v)


def flds(n):
    try:
        return db.get_fields(n) or {}
    except Exception:
        return {}


def show(rec, indent):
    fl = flds(rec)
    found = False
    for k in sorted(fl):
        if any(h in k.lower() for h in HINT):
            v = t(rec, k)
            if v.strip() and v.strip() not in ('0', '0.0', '0.000000'):
                print(f'{indent}{k:44} = {v}')
                found = True
    return found


for label, rec in CHAMPS.items():
    print()
    print('=' * 96)
    print(label, rec)
    print('=' * 96)
    if not db.has_record(rec):
        print('  MISSING RECORD')
        continue
    print('  -- on the creature record itself:')
    if not show(rec, '     '):
        print('     (none non-zero)')
    print('  -- on the skills it carries:')
    fl = flds(rec)
    any_skill = False
    for i in range(1, 40):
        k = 'skillName%d' % i
        if k not in fl:
            continue
        s = t(rec, k).strip()
        if not s or not db.has_record(s):
            continue
        # does this skill carry reflect/retaliation?
        sub = flds(s)
        hits = [x for x in sub if any(h in x.lower() for h in HINT)
                and t(s, x).strip() and t(s, x).strip() not in ('0', '0.0', '0.000000')]
        if hits:
            any_skill = True
            print(f'     [{i}] {s}')
            for x in sorted(hits):
                print(f'          {x:40} = {t(s, x)}')
    if not any_skill:
        print('     (no skill carries a non-zero reflect/retaliation)')
