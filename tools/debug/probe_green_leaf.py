# -*- coding: utf-8 -*-
"""Narrow the green: the Enslaver and the Devourer wear the SAME mesh, but only the Enslaver
is reported green. So the source is more likely something the Enslaver has and the Devourer
does not. Dump both skill lists and the colour channels of every FX record they reach.
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

ENS = r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'
DEV = r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr'
LEAF = r'records\skills\stealth\drxpet\drx_pet_fx\drxshadowcloakrunning_fx.dbr'

COLOUR_HINTS = ('color', 'colour', 'red', 'green', 'blue', 'tint', 'rgb', 'alpha')


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


def fields(n):
    try:
        return db.get_fields(n) or {}
    except Exception:
        return {}


def skills_of(rec, label):
    print()
    print('=' * 96)
    print('SKILL LIST:', label)
    print('=' * 96)
    fl = fields(rec)
    out = []
    for i in range(1, 40):
        k = 'skillName%d' % i
        if k in fl:
            v = txt(rec, k).strip()
            if v:
                out.append((i, v, txt(rec, 'skillLevel%d' % i)))
    for i, v, lvl in out:
        print(f'  [{i:2}] lvl={lvl:6} {v}')
    return {v.lower() for _, v, _ in out}


ens = skills_of(ENS, 'Enslaver (reported GREEN)')
dev = skills_of(DEV, 'Devourer (same mesh, NOT reported green)')

print()
print('=' * 96)
print('SKILLS THE ENSLAVER HAS AND THE DEVOURER DOES NOT  <-- prime suspects')
print('=' * 96)
for s in sorted(ens - dev):
    print(' ', s)
    fl = fields(s)
    for k in sorted(fl):
        v = txt(s, k)
        if v.strip() and any(h in k.lower() for h in ('fx', 'particle', 'mesh', 'texture', 'color', 'colour', 'tint')):
            print(f'      {k:34} = {v}')

print()
print('=' * 96)
print('LEAF FX the Enslaver emits while running:', LEAF)
print('=' * 96)
if db.has_record(LEAF):
    for k in sorted(fields(LEAF)):
        v = txt(LEAF, k)
        if v.strip() and any(h in k.lower() for h in COLOUR_HINTS + ('texture', 'particle', 'shader')):
            print(f'  {k:38} = {v}')
else:
    print('  RECORD NOT PRESENT')
