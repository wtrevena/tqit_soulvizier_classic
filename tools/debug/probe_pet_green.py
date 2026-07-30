# -*- coding: utf-8 -*-
"""WILL SAYS "when i SUMMON him" - so the green is on the summoned PET, not the monster.

Every prior wave (and my own probe minutes ago) audited um_toxeus_enslaver_99, the MONSTER.
The pet the soul summons is a SEPARATE set of records: soulskills\pets\toxeus_enslaver_{1,2,3}.
If those carry their own FX, that explains four "fixed" waves and a still-green summon.

Green smoke + black smoke together, brightness varying with lighting = two particle emitters,
one of them additive. So dump every FX/particle/tint field on the pets and follow the paks down.
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

PETS = [
    r'records\skills\soulskills\pets\toxeus_enslaver_1.dbr',
    r'records\skills\soulskills\pets\toxeus_enslaver_2.dbr',
    r'records\skills\soulskills\pets\toxeus_enslaver_3.dbr',
    r'records\skills\soulskills\pets\bloodtoxeus_1.dbr',
    r'records\skills\soulskills\pets\toxeus_eoat_1.dbr',
]
HINT = ('fx', 'particle', 'mesh', 'texture', 'tint', 'color', 'colour', 'glow', 'shader', 'skin')
COLOUR = ('color', 'colour', 'red', 'green', 'blue', 'tint', 'alpha', 'texture', 'particle', 'shader')


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


def dump(rec, depth, seen):
    if rec.lower() in seen or depth > 2 or not db.has_record(rec):
        return
    seen.add(rec.lower())
    pad = '   ' * depth
    fl = fields(rec)
    for k in sorted(fl):
        v = txt(rec, k)
        if not v.strip():
            continue
        kl = k.lower()
        if any(h in kl for h in (HINT if depth == 0 else COLOUR)):
            green = ''
            if 'green' in kl and v.strip() not in ('0', '0.0', '0.000000'):
                green = '   <<<< NON-ZERO GREEN'
            if any(g in v.lower() for g in ('poison', 'green', 'venom', 'acid', 'toxic', 'nature')):
                green = '   <<<< GREEN-ISH ASSET'
            print(f'{pad}  {k:36} = {v}{green}')
    for k in sorted(fl):
        if 'fxpak' not in k.lower() and 'particleeffect' not in k.lower():
            continue
        for tok in txt(rec, k).replace(';', ' ').split():
            tok = tok.strip()
            if tok.lower().endswith('.dbr') and db.has_record(tok):
                print(f'{pad}    -> [{k}] {tok}')
                dump(tok, depth + 1, seen)


for p in PETS:
    print()
    print('=' * 96)
    if not db.has_record(p):
        print('MISSING:', p)
        continue
    print(p.split(SEP)[-1], ' desc:', txt(p, 'description'))
    print('=' * 96)
    dump(p, 0, set())
