r"""tools/debug/soul_tier_sweep.py - roster-wide soul tier-scaling sweep (b78).

Ground-truth audit over an arz: for EVERY soul equipmentring family, compare its
n/e/l tiers pairwise and flag:
  (a) FLAT  - epic identical-or-nearly to normal (or legendary to epic) on the
              SCALED dimensions (granted-skill/augment levels + character stat
              modifiers). A byte-identical epic passes the old non-strict gate.
  (b) MISSING - family lacks an _e or _l tier record.
  (c) WRONG-LOOT - a monster's per-difficulty soul loot triple points at a
              lower-tier record for a higher difficulty (the coldworm bug shape).

Usage: py tools/debug/soul_tier_sweep.py <arz>
Default arz = work/SoulvizierClassic/Database/SoulvizierClassic.arz
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase

SOUL_PREFIX = r'records\item\equipmentring\soul' + '\\'

# Character stat modifier fields that legitimately SCALE per tier (the design
# dimension the player feels). Cosmetic / structural fields (itemLevel,
# levelRequirement, bitmap, mesh, FileDescription, tags) are excluded from the
# flat test because they either differ trivially or must not.
SCALED_STAT_FIELDS = [
    'characterStrengthModifier', 'characterDexterityModifier',
    'characterIntelligenceModifier', 'characterLifeModifier',
    'characterManaModifier', 'characterLifeModifierAbsolute',
    'characterManaModifierAbsolute', 'characterManaRegenModifier',
    'characterHealthRegenModifier', 'characterSpellCastSpeedModifier',
    'characterAttackSpeedModifier', 'characterRunSpeedModifier',
    'characterTotalSpeedModifier', 'characterDefensiveAbilityModifier',
    'characterOffensiveAbilityModifier', 'characterArmorStrengthModifier',
    'defensiveLife', 'defensiveTotalSpeed',
    'offensiveLifeMin', 'offensiveLifeMax', 'offensiveLifeLeechMin',
    'offensiveLifeLeechMax', 'offensivePhysicalMin', 'offensivePhysicalMax',
    'offensiveElementalMin', 'offensiveElementalMax',
    'offensiveFireMin', 'offensiveFireMax', 'offensiveColdMin', 'offensiveColdMax',
    'offensiveLightningMin', 'offensiveLightningMax',
    'offensivePoisonMin', 'offensivePoisonMax',
    'retaliationFireMin', 'retaliationFireMax',
    'defensiveFireModifier', 'defensiveColdModifier', 'defensiveLightningModifier',
    'defensivePoisonModifier', 'defensivePierceModifier',
]
LEVEL_FIELDS = ['augmentSkillLevel1', 'augmentSkillLevel2', 'augmentSkillLevel3',
                'augmentSkillLevel4', 'itemSkillLevel', 'augmentAllLevel',
                'augmentMasteryLevel1', 'augmentMasteryLevel2']


def norm(p):
    return str(p).replace('/', '\\').lower().strip()


def first(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def sval(db, rec, f):
    v = first(db.get_field_value(rec, f))
    return v.strip() if isinstance(v, str) and v.strip() else None


def fnum(db, rec, f):
    v = first(db.get_field_value(rec, f))
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def tier_of(nn):
    m = re.search(r'_([nel])\.dbr$', nn)
    return m.group(1) if m else None


def family_key(nn):
    rel = nn[len(SOUL_PREFIX):]
    base = rel.rsplit('\\', 1)[-1]
    fam_dir = rel.rsplit('\\', 1)[0] if '\\' in rel else ''
    m = re.match(r'^(.*?)_([nel])\.dbr$', base)
    stem = m.group(1) if m else base[:-4]
    return (fam_dir + '\\' + stem) if fam_dir else stem


def is_soul_ring(db, rec):
    cls = sval(db, rec, 'Class')
    if cls == 'ArmorJewelry_Ring':
        return True
    tpl = norm(sval(db, rec, 'templateName') or '')
    return tpl.endswith('jewelry_ring.tpl')


def main():
    arz = sys.argv[1] if len(sys.argv) > 1 else \
        r'C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz'
    db = ArzDatabase.from_arz(Path(arz))
    nm = {norm(n): n for n in db.record_names()}

    # gather soul-ring tier families
    fam = defaultdict(dict)
    for nn, exact in nm.items():
        if not nn.startswith(SOUL_PREFIX) or not nn.endswith('.dbr'):
            continue
        t = tier_of(nn)
        if not t or not is_soul_ring(db, exact):
            continue
        fam[family_key(nn)][t] = exact

    # loot triple map: soul record path -> list of (monster, difficulty index, tier of drop)
    # scan every monster's lootFinger2Item1 (3-arity = [normal,epic,legendary])
    soul_to_family = {}
    for k, tiers in fam.items():
        for t, exact in tiers.items():
            soul_to_family[norm(exact)] = (k, t)

    wrong_loot = []
    for n in db.record_names():
        fields = db.get_fields(n)
        if not fields:
            continue
        for k, tf in fields.items():
            kk = k.split('###')[0]
            if kk != 'lootFinger2Item1':
                continue
            vals = tf.values
            # only care about drops that are soul rings
            triple = []
            for v in vals:
                if isinstance(v, str) and norm(v) in soul_to_family:
                    triple.append(norm(v))
                else:
                    triple.append(None)
            # expected difficulty->tier: idx0=n, idx1=e, idx2=l
            EXP = {0: 'n', 1: 'e', 2: 'l'}
            for idx, sv_path in enumerate(triple):
                if sv_path is None:
                    continue
                famk, drop_tier = soul_to_family[sv_path]
                exp_tier = EXP.get(idx)
                if exp_tier and drop_tier != exp_tier:
                    # is the correct tier even available in this triple's family?
                    wrong_loot.append((n, kk, idx, famk, drop_tier, exp_tier, vals))

    # flat + missing analysis
    flat = []
    missing = []
    healthy = []
    for k in sorted(fam):
        tiers = fam[k]
        have = [t for t in 'nel' if t in tiers]
        if have != ['n', 'e', 'l']:
            missing.append((k, ''.join(have)))
            continue
        recs = {t: tiers[t] for t in 'nel'}

        def scaled_vec(rec):
            lv = {f: db.get_field_value(rec, f) for f in LEVEL_FIELDS}
            lv = {f: first(v) for f, v in lv.items() if first(v) is not None}
            st = {f: fnum(db, rec, f) for f in SCALED_STAT_FIELDS}
            st = {f: v for f, v in st.items() if v is not None}
            return lv, st

        nlv, nst = scaled_vec(recs['n'])
        elv, est = scaled_vec(recs['e'])
        llv, lst = scaled_vec(recs['l'])

        # granted-skill NAME identity per tier (else not comparable)
        def gskills(rec):
            d = {}
            for f in ['itemSkillName', 'augmentSkillName1', 'augmentSkillName2',
                      'augmentSkillName3', 'augmentSkillName4']:
                v = sval(db, rec, f)
                if v:
                    d[f] = norm(v)
            return d

        # Determine flat: e vs n on scaled dims where BOTH present and same skill names.
        def compare(lo_lv, lo_st, hi_lv, hi_st, lo_rec, hi_rec):
            # any scaled dimension where hi strictly > lo?
            progressed = False
            equal_dims = []
            names_lo = gskills(lo_rec)
            names_hi = gskills(hi_rec)
            for f, lo in lo_lv.items():
                if f in hi_lv:
                    # skill-level fields: only comparable if the paired skill name matches
                    sk_field = {'itemSkillLevel': 'itemSkillName',
                                'augmentSkillLevel1': 'augmentSkillName1',
                                'augmentSkillLevel2': 'augmentSkillName2',
                                'augmentSkillLevel3': 'augmentSkillName3',
                                'augmentSkillLevel4': 'augmentSkillName4'}.get(f)
                    if sk_field and names_lo.get(sk_field) != names_hi.get(sk_field):
                        continue
                    try:
                        loi, hii = int(lo), int(hi_lv[f])
                    except (TypeError, ValueError):
                        continue
                    if hii > loi:
                        progressed = True
                    elif hii == loi:
                        equal_dims.append(f)
            for f, lo in lo_st.items():
                if f in hi_st:
                    if hi_st[f] > lo:
                        progressed = True
                    elif hi_st[f] == lo:
                        equal_dims.append(f)
            return progressed, equal_dims

        e_prog, e_eq = compare(nlv, nst, elv, est, recs['n'], recs['e'])
        l_prog, l_eq = compare(elv, est, llv, lst, recs['e'], recs['l'])

        if not e_prog or not l_prog:
            flat.append((k, e_prog, l_prog, len(e_eq), len(l_eq),
                         nlv, elv, llv))
        else:
            healthy.append(k)

    print("=== SOUL TIER SWEEP over %s ===" % arz)
    print("families total: %d | healthy: %d | flat: %d | missing-tier: %d"
          % (len(fam), len(healthy), len(flat), len(missing)))
    print("\n--- FLAT (no strict progress n->e or e->l on any scaled dim) [%d] ---" % len(flat))
    for k, ep, lp, ne, nl, nlv, elv, llv in flat:
        print("  %-40s e_prog=%s l_prog=%s | itemSkillLevel n/e/l=%s/%s/%s aug1=%s/%s/%s"
              % (k, ep, lp,
                 nlv.get('itemSkillLevel'), elv.get('itemSkillLevel'), llv.get('itemSkillLevel'),
                 nlv.get('augmentSkillLevel1'), elv.get('augmentSkillLevel1'), llv.get('augmentSkillLevel1')))
    print("\n--- MISSING TIER [%d] ---" % len(missing))
    for k, have in missing:
        print("  %-40s have=%s" % (k, have))
    print("\n--- WRONG-TIER LOOT [%d] ---" % len(wrong_loot))
    for mon, fld, idx, famk, dt, et, vals in wrong_loot:
        print("  %s idx%d(%s) drops tier %s expected %s | fam=%s"
              % (mon.rsplit('\\', 1)[-1], idx, {0:'N',1:'E',2:'L'}[idx], dt, et, famk))


if __name__ == '__main__':
    main()
