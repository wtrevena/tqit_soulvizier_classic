"""Bucketed record-diff: build31 baseline arz vs a candidate arz. Confirms the
ONLY changes are the intended Mastery Wave 2 records (0 unbucketed) per the
standing per-group discipline. Usage:
  py tools/debug/diff_wave2.py <baseline.arz> <candidate.arz>
"""
import sys
from pathlib import Path
sys.path.insert(0, 'tools')
from arz_patcher import ArzDatabase

base_arz = Path(sys.argv[1])
cand_arz = Path(sys.argv[2])
A = ArzDatabase.from_arz(base_arz)
B = ArzDatabase.from_arz(cand_arz)

an = {n.replace('/', '\\').lower(): n for n in A.record_names()}
bn = {n.replace('/', '\\').lower(): n for n in B.record_names()}

added = sorted(set(bn) - set(an))
removed = sorted(set(an) - set(bn))


def fields_sig(db, rec):
    ff = db.get_fields(rec) or {}
    out = {}
    for k, tf in ff.items():
        out[k.split('###')[0]] = tuple(tf.values) if tf.values else ()
    return out


changed = []
for k in sorted(set(an) & set(bn)):
    sa = fields_sig(A, an[k])
    sb = fields_sig(B, bn[k])
    if sa != sb:
        changed.append(k)

# ---- expected Wave 2 buckets ----
def bucket(k):
    kl = k.lower()
    warf = ['drxancestralhorn', 'drxbattlestandard', 'drxwarwind']
    if any(w in kl for w in warf) or '\\warfare\\pets\\spectralsoldier_' in kl:
        return 'WARFARE'
    nat = ['drxforceofnature', 'drxnaturemastery_petbonus',
           'drxregrowth_acceleratedgrowth', 'drxrenewal',
           'drxwolf_petskill_maul', 'drxwolf_petskill_survivalinstinct']
    if any(w in kl for w in nat) or '\\nature\\pet\\sylvannymph_' in kl:
        return 'NATURE'
    spi = ['drxoutsidersummons', 'drxdeathward', 'bonescourge_spiritbreath']
    if any(w in kl for w in spi) or '\\spirit\\drxpet\\bonepet' in kl:
        return 'SPIRIT'
    dre = ['drxphantasm', 'drxnightmare_psionicbeam',
           'drxdistortreality_temporalrift', 'drxspellbreaker',
           'drxspellbreaker_spellshock', 'drxphantomstrike']
    if any(w in kl for w in dre) or '\\dream\\pet\\nightmare_' in kl \
            or '\\dream\\drxpet\\phantasm_' in kl:
        return 'DREAM'
    if 'runemaster_mastery' in kl or '\\runemaster\\menhiraltar' in kl:
        return 'RUNEMASTER'
    neid = ['neidanmastery', 'terracotta_servant', '\\neidan\\deathbomb', '\\neidan\\splash']
    if any(w in kl for w in neid):
        return 'NEIDAN'
    return None


from collections import Counter
buckets = Counter()
unbucketed = []
for k in changed + added:
    b = bucket(k)
    if b:
        buckets[b] += 1
    else:
        unbucketed.append(k)

print(f"BASELINE {base_arz}  records={len(an)}")
print(f"CANDIDATE {cand_arz}  records={len(bn)}")
print(f"\nADDED   ({len(added)}):")
for k in added:
    print('   +', bn[k], '  bucket=', bucket(k))
print(f"REMOVED ({len(removed)}):")
for k in removed:
    print('   -', an[k])
print(f"MODIFIED ({len(changed)})")
print("\n=== BUCKET COUNTS (changed + added) ===")
for b, c in sorted(buckets.items()):
    print(f"   {b}: {c}")
print(f"\nUNBUCKETED ({len(unbucketed)}):")
for k in unbucketed:
    print('   !!!', bn.get(k, an.get(k)))
if not unbucketed and not removed:
    print("\nRESULT: PASS - all changes bucketed to Wave 2, 0 unbucketed, 0 removed records")
else:
    print(f"\nRESULT: REVIEW - {len(unbucketed)} unbucketed, {len(removed)} removed")
