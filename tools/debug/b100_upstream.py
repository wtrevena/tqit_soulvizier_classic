#!/usr/bin/env python3
"""Cause (d) test: did the MERGE drop the Sanctuary's population?

Compare the 0x05 placed-instance census of drxBC3 + the ocean ring in OUR
canonical map against the PRISTINE SV 0.98i upstream Levels.arc (the merge donor).
If upstream has the same counts, nothing was dropped -> cause (a), not (d).
"""
import sys, hashlib
from pathlib import Path
from collections import Counter
REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO/'tools')); sys.path.insert(0, str(REPO/'tools'/'contracts'))
import contracts_map as CM

OURS = r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Resources\Levels.arc'
# SV 0.98i merge donor. Prefer $SVC_SV_ARC (the documented build-input env var);
# the literal below is only the path check_build_inputs.py resolved on this machine
# (the build36-map worktree cache) and is not guaranteed to exist elsewhere.
import os
SV = os.environ.get('SVC_SV_ARC') or \
    r'C:\Users\willi\repos\tqit_soulvizier_classic\.claude\worktrees\build36-map\upstream\soulvizier_098i\Resources\Levels.arc'
SVAERA = r'C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest\Resources\Levels.arc'

arz = CM.Arz.from_arz(r'C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz')
cls = {CM.norm_rec(k): v for k, v in arz.record_class().items()}

WANT = ['drxbc3','ocean_extension01','ocean_extension02','ocean_extension03',
        'ocean_extension04','drxbc_finale','drxfirstroom','drxbc2']

def census(path, label):
    p = Path(path)
    print('\n===', label)
    print('  ', p)
    if not p.exists():
        print('   MISSING'); return {}
    print('   size', p.stat().st_size, 'md5', hashlib.md5(p.read_bytes()).hexdigest())
    arc = CM.Arc.from_file(str(p)); mp = arc.world_map()
    secs = CM.parse_top_sections(mp)
    levels = CM.parse_level_index(CM.sec_bytes(mp, secs, 0x01))
    print('   levels', len(levels))
    out = {}
    for lv in levels:
        nm = lv['fname'].split('/')[-1].split('\\')[-1].replace('.lvl','').lower()
        if nm not in WANT: continue
        blob = mp[lv['data_offset']:lv['data_offset']+lv['data_length']]
        _s, insts = CM.parse_0x05(blob)
        prox = [i for i in insts
                if cls.get(CM.norm_rec(i['dbr'].decode('latin-1'))) == 'Proxy'
                and 'shrine' not in i['dbr'].decode('latin-1').lower()]
        out[nm] = dict(inst=len(insts), prox=len(prox), corner=lv['corner'],
                       roster=Counter(i['dbr'].decode('latin-1').split('\\')[-1] for i in prox))
    return out

a = census(OURS, 'OURS (canonical merged map)')
b = census(SV, 'SV 0.98i UPSTREAM (merge donor)')
c = census(SVAERA, 'SVAERA base (merge base)')

print('\n%-22s | %-22s | %-22s | %s' % ('level','OURS inst/proxy','SV098i inst/proxy','verdict'))
print('-'*95)
for n in WANT:
    A = a.get(n); B = b.get(n)
    va = '%d / %d' % (A['inst'], A['prox']) if A else 'absent'
    vb = '%d / %d' % (B['inst'], B['prox']) if B else 'absent'
    if A and B:
        v = 'IDENTICAL - merge dropped NOTHING' if (A['inst'], A['prox']) == (B['inst'], B['prox']) \
            else 'DELTA inst %+d proxy %+d' % (A['inst']-B['inst'], A['prox']-B['prox'])
    else:
        v = 'not comparable'
    print('%-22s | %-22s | %-22s | %s' % (n, va, vb, v))

print('\n== per-proxy roster diff for drxbc3 ==')
A = a.get('drxbc3', {}).get('roster', Counter()); B = b.get('drxbc3', {}).get('roster', Counter())
for k in sorted(set(A) | set(B)):
    m = 'same' if A[k] == B[k] else '*** DIFF ***'
    print('   %-42s ours=%-3d sv098i=%-3d %s' % (k, A[k], B[k], m))
