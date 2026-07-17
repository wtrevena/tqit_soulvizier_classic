r"""Which full-3-tier soul families FAIL a STRICT-progress law?

Strict-progress law (anti-flat): for a family with all of n/e/l, there must be at
least one numeric 'power' field that strictly increases n->e, AND at least one that
strictly increases e->l. This is the exact blind spot the old non-strict monotonic
gate (n<=e<=l) allowed: a byte-identical epic passes it, a strict gate fails it.

Any family that FAILS here on the current golden arz must be waivered (genuinely
flat-by-design) before a fail-loud strict gate can ship. Prints the fail list."""
import sys, re
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase

ARZ = sys.argv[1] if len(sys.argv) > 1 else \
    r'C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz'
SOUL_PREFIX = r'records\item\equipmentring\soul' + '\\'

# fields excluded from the power vector: cosmetic / structural / requirement / tags.
IGNORE = {
    'itemLevel', 'levelRequirement', 'bitmap', 'mesh', 'FileDescription',
    'itemNameTag', 'itemText', 'itemCostName', 'itemClassification',
    'strengthRequirement', 'dexterityRequirement', 'intelligenceRequirement',
    'Class', 'templateName', 'numRelicSlots', 'quest', 'scale', 'maxTransparency',
    'shadowBias', 'castsShadows', 'cannotPickUp', 'cannotPickUpMultiple',
    'hidePrefixName', 'hideSuffixName', 'characterBaseAttackSpeedTag',
    'itemQualityTag', 'dropSound', 'dropSound3D', 'dropSoundWater',
    'augmentSkillName1', 'augmentSkillName2', 'augmentSkillName3', 'augmentSkillName4',
    'itemSkillName',
}


def norm(p): return str(p).replace('/', '\\').lower().strip()
def first(v):
    if isinstance(v, list): return v[0] if v else None
    return v
def sval(db, rec, f):
    v = first(db.get_field_value(rec, f)); return v.strip() if isinstance(v,str) and v.strip() else None
def tier_of(nn):
    m = re.search(r'_([nel])\.dbr$', nn); return m.group(1) if m else None
def family_key(nn):
    rel = nn[len(SOUL_PREFIX):]; base = rel.rsplit('\\',1)[-1]
    fam_dir = rel.rsplit('\\',1)[0] if '\\' in rel else ''
    m = re.match(r'^(.*?)_([nel])\.dbr$', base); stem = m.group(1) if m else base[:-4]
    return (fam_dir+'\\'+stem) if fam_dir else stem
def is_soul_ring(db, rec):
    if sval(db, rec, 'Class') == 'ArmorJewelry_Ring': return True
    return norm(sval(db, rec,'templateName') or '').endswith('jewelry_ring.tpl')

def power_vec(db, rec):
    """field -> float for every numeric non-ignored field. Skill LEVEL fields kept."""
    out = {}
    for k, tf in (db.get_fields(rec) or {}).items():
        kk = k.split('###')[0]
        if kk in IGNORE: continue
        v = first(tf.values)
        try: out[kk] = float(v)
        except (TypeError, ValueError): pass
    return out

def skillnames(db, rec):
    d = {}
    for lf, nf in [('itemSkillLevel','itemSkillName'),('augmentSkillLevel1','augmentSkillName1'),
                   ('augmentSkillLevel2','augmentSkillName2'),('augmentSkillLevel3','augmentSkillName3'),
                   ('augmentSkillLevel4','augmentSkillName4')]:
        d[lf] = norm(sval(db, rec, nf) or '')
    return d

def progresses(db, lo, hi):
    """True iff at least one power field strictly increases lo->hi. Skill-level fields
    only count when the paired skill NAME matches across the two tiers."""
    plo, phi = power_vec(db, lo), power_vec(db, hi)
    nlo, nhi = skillnames(db, lo), skillnames(db, hi)
    for f, lv in plo.items():
        if f not in phi: continue
        if f in nlo and nlo.get(f) != nhi.get(f):
            continue  # different granted skill -> not comparable
        if phi[f] > lv:
            return True
    return False

def main():
    db = ArzDatabase.from_arz(Path(ARZ))
    nm = {norm(n): n for n in db.record_names()}
    fam = defaultdict(dict)
    for nn, exact in nm.items():
        if not nn.startswith(SOUL_PREFIX) or not nn.endswith('.dbr'): continue
        t = tier_of(nn)
        if t and is_soul_ring(db, exact): fam[family_key(nn)][t] = exact
    full = {k: v for k, v in fam.items() if all(t in v for t in 'nel')}
    fails = []
    for k in sorted(full):
        r = full[k]
        e_ok = progresses(db, r['n'], r['e'])
        l_ok = progresses(db, r['e'], r['l'])
        if not (e_ok and l_ok):
            fails.append((k, e_ok, l_ok))
    print("full-3-tier families: %d | strict-progress PASS: %d | FAIL: %d"
          % (len(full), len(full)-len(fails), len(fails)))
    for k, e, l in fails:
        print("  FAIL %-45s n->e=%s e->l=%s" % (k, e, l))

if __name__ == '__main__':
    main()
