"""Finding (2): where does SVAERA MATERIALLY diverge from BOTH base AND SV098?
Sample-classify by family. For records common to all three, compare a stable
field signature; flag SVAERA-authored divergence (differs from base AND sv098).
Keep it light: cap per-family sample. Also probe the MP RunEquation angle.
"""
import sys, random
from pathlib import Path
from collections import defaultdict, Counter

TOOLS = r"C:\Users\willi\repos\tqit_soulvizier_classic\tools"
sys.path.insert(0, TOOLS)
from arz_patcher import ArzDatabase

SVAERA_ARZ = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest\Database\SVAERA_customquest.arz")
SV098 = Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz")
BASE  = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz")

def log(*a): print(*a, file=sys.stderr)
def norm(s): return str(s).replace('/', '\\').lower().strip()

log("loading 3 DBs...")
SV=ArzDatabase.from_arz(SVAERA_ARZ); SVN={norm(n):n for n in SV.record_names()}
B =ArzDatabase.from_arz(BASE);       BNN={norm(n):n for n in B.record_names()}
S =ArzDatabase.from_arz(SV098);      SNN={norm(n):n for n in S.record_names()}

def sig(db, real):
    ff=db.get_fields(real)
    if not ff: return None
    out={}
    for k,tf in ff.items():
        b=k.split('###')[0]
        if b not in out:
            out[b]=tuple(str(x) for x in tf.values)
    return out

def diff_fields(a,b):
    if a is None or b is None: return None
    keys=set(a)|set(b)
    d=[]
    for k in keys:
        if a.get(k)!=b.get(k):
            d.append(k)
    return d

common = [k for k in SVN if k in BNN and k in SNN]
log(f"common to all three: {len(common)}")

# family bucket
def fam(nname):
    parts=nname.split('\\')
    if not nname.startswith('records\\'): return 'other'
    a=parts[1] if len(parts)>1 else '?'
    b=parts[2] if len(parts)>2 else '?'
    if a in ('item','creature','skills'): return f'{a}\\{b}'
    return a

by_fam=defaultdict(list)
for k in common: by_fam[fam(k)].append(k)

FAMILIES = ['creature\\monster','item\\equipmentweapon','item\\equipmentring',
            'item\\equipmentarmor','skills\\nature','skills\\stealth','skills\\warfare',
            'skills\\hunting','skills\\earth','skills\\storm','skills\\spirit',
            'item\\loottables','game']
random.seed(7)
print("FAMILY DIVERGENCE (SVAERA vs base AND sv098), sampled:")
FIELD_HEAT=Counter()
for f in FAMILIES:
    recs=by_fam.get(f,[])
    if not recs:
        print(f"  {f:26} (none common)"); continue
    sample=random.sample(recs, min(120,len(recs)))
    div_both=0; div_from_sv098=0; identical=0
    for k in sample:
        sv=sig(SV,SVN[k]); bb=sig(B,BNN[k]); ss=sig(S,SNN[k])
        db_b=diff_fields(sv,bb); db_s=diff_fields(sv,ss)
        if db_b and db_s:
            div_both+=1
            for fld in db_s: FIELD_HEAT[f"{f}:{fld}"]+=1
        elif not db_s:
            identical+=1
        if db_s: div_from_sv098+=1
    print(f"  {f:26} common={len(recs):5} sampled={len(sample):3}  diverge-from-BOTH={div_both:3}  ==SV098:{identical:3}")

print("\nTop divergent fields (SVAERA vs SV098) in sampled content families:")
for k,c in FIELD_HEAT.most_common(30):
    print(f"  {c:3}  {k}")

# ---- MP RunEquation probe: does SVAERA use spawnObjectsLevelEquation style AE fields? ----
print("\nMP spawn-equation probe (AE-compat):")
def scan_field(db, names, field):
    hit=0; tot=0
    for k in names:
        ff=db.get_fields(names[k])
        if not ff: continue
        tot+=1
        for kk in ff:
            if field.lower() in kk.lower():
                hit+=1; break
    return hit
for fld in ['spawnLimit','RunEquation','numSpawnLimit','spawnObjectsLevelEq']:
    print(f"  field '{fld}': present in some records? (spot only) -- skipped heavy scan")
