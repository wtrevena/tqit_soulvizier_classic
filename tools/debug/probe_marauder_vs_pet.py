# -*- coding: utf-8 -*-
"""Will confirms the summoned MARAUDER DEMONS have the proper black shroud and NO green.

If the marauders carry the SAME effect record as the green pet, that effect is black - which
kills the .pfx-is-green hypothesis and forces the green to come from whatever the pet has and
the marauder does not. Read-only.
"""
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
        return ' '.join(str(i) for i in v)
    return str(v)


mar = [n for n in db.record_names()
       if 'marauder' in n.lower() and n.lower().split(SEP)[-1].startswith('um_')]
print('marauder records found:', len(mar))
for m in mar:
    print('  ', m)

rows = [('MARAUDER  (BLACK shroud, NO green - Will confirmed in game)', m) for m in mar]
rows.append(('ENSLAVER PET tier1  (GREEN - Will confirmed)',
             r'records\skills\soulskills\pets\toxeus_enslaver_1.dbr'))
rows.append(('ENSLAVER MONSTER',
             r'records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr'))
rows.append(('DEVOURER PET (crimson - never reported green)',
             r'records\skills\soulskills\pets\bloodtoxeus_1.dbr'))

for label, r in rows:
    print()
    print('=' * 92)
    print(label)
    if not db.has_record(r):
        print('  MISSING RECORD:', r)
        continue
    print('  record      :', r)
    print('  mesh        :', t(r, 'mesh'))
    print('  baseTexture :', t(r, 'baseTexture'))
    print('  fx running  :', t(r, 'charFxPakRunningNames'))
    print('  fx self     :', t(r, 'charFxPakSelfNames'))
    print('  fx other    :', t(r, 'charFxPakOtherNames'))
