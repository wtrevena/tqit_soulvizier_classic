# -*- coding: utf-8 -*-
"""Green glow on the Enslaver: dump EVERY visual-bearing field on him and his pets.

Will has now retracted his own "it was my skill" resolution, so this is live again after four
failed fix waves. Those waves all chased FX *fields*. The prime suspect this time is the MESH:
he wears RevenantPoison.msh, a poison-themed asset that may carry green in the mesh/texture
itself - which no FX-field change could ever fix. Read-only; prints evidence, decides nothing.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, r'C:\Users\willi\repos\tqit_soulvizier_classic\tools')
from arz_patcher import ArzDatabase  # noqa: E402

db = ArzDatabase.from_arz(Path(
    r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz'))
SEP = os.sep

TARGETS = [
    r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr',
    r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr',
    r'records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr',
]

VISUAL_HINTS = ('mesh', 'texture', 'fx', 'particle', 'glow', 'tint', 'colour', 'color',
                'shader', 'bloom', 'light', 'aura', 'skin', 'trail', 'emit')


def fields(n):
    try:
        return db.get_fields(n) or {}
    except Exception:
        return {}


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


for t in TARGETS:
    if not db.has_record(t):
        print('MISSING RECORD:', t)
        continue
    print()
    print('=' * 100)
    print(t.split(SEP)[-1], ' -- desc:', txt(t, 'description'))
    print('=' * 100)
    fl = fields(t)
    hits = [k for k in fl if any(h in k.lower() for h in VISUAL_HINTS)]
    for k in sorted(hits):
        v = txt(t, k)
        if v.strip():
            print(f'  {k:38} = {v}')

    # follow every charFxPak* reference one level down - that is where a green particle would live
    print('  --- referenced FX paks, one level down:')
    for k in sorted(fl):
        if 'charfxpak' not in k.lower():
            continue
        for tok in txt(t, k).replace(';', ' ').split():
            tok = tok.strip()
            if not tok.lower().endswith('.dbr') or not db.has_record(tok):
                continue
            print(f'    [{k}] {tok}')
            sub = fields(tok)
            for sk in sorted(sub):
                sv = txt(tok, sk)
                if sv.strip() and any(h in sk.lower() for h in VISUAL_HINTS):
                    print(f'        {sk:34} = {sv}')
