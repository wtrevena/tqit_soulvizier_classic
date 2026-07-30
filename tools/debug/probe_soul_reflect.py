# -*- coding: utf-8 -*-
"""Precise version. lootFinger2Item1 is a THREE-VALUE array (n/e/l in one field), which broke the
first probe's has_record() call. Split it, then read defensiveReflect* off each soul the champions
actually wear - and keep %-REFLECT separate from flat RETALIATION, because they are different
mechanics and only one of them scales with the player's own hit.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, r'C:\Users\willi\repos\tqit_soulvizier_classic\tools')
from arz_patcher import ArzDatabase  # noqa: E402

db = ArzDatabase.from_arz(Path(
    r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz'))
SEP = os.sep

CHAMPS = {
    'Enslaver': r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr',
    'Devourer': r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr',
    'Hunt': r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr',
    'Hunt(L)': r'records\creature\monster\shadowstalker\um_toxeus_hunt_l_99.dbr',
}


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


def split_paths(raw):
    out = []
    for chunk in raw.replace(';', ' ').split():
        c = chunk.strip()
        if c.lower().endswith('.dbr'):
            out.append(c)
    return out


print('%-REFLECT (scales with the PLAYER hit) vs flat RETALIATION (does not) on the worn souls')
print()
for label, rec in CHAMPS.items():
    print('=' * 92)
    print(label, '  equips at', t(rec, 'chanceToEquipFinger2'), 'percent')
    for soul in split_paths(t(rec, 'lootFinger2Item1')):
        if not db.has_record(soul):
            print('   ', soul.split(SEP)[-1], '-> RECORD NOT PRESENT')
            continue
        fl = flds(soul)
        pct = {k: t(soul, k) for k in fl if 'reflect' in k.lower()
               and t(soul, k).strip() not in ('', '0', '0.0', '0.000000')}
        ret = {k: t(soul, k) for k in fl if 'retaliation' in k.lower()
               and t(soul, k).strip() not in ('', '0', '0.0', '0.000000')}
        print('   ', soul.split(SEP)[-1])
        print('        %-REFLECT :', pct if pct else 'none')
        if ret:
            keys = sorted(ret)[:6]
            print('        retaliation (flat):', {k: ret[k] for k in keys},
                  ('... +%d more' % (len(ret) - len(keys))) if len(ret) > len(keys) else '')
        else:
            print('        retaliation (flat): none')
    print()

print('=' * 92)
print('FOR SCALE - the shared skill both stacks with:')
sk = r'records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr'
print('  ', sk)
print('     defensiveReflect       =', t(sk, 'defensiveReflect'))
print('     defensiveReflectChance =', t(sk, 'defensiveReflectChance'))
