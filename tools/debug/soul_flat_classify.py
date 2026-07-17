r"""Classify each FLAT soul family: true full-field flatness, SV098 presence +
SV098 flatness, and obtainability (which monster drops it + classification).
Determines amgoz1-intended-flat (SV ships flat) vs mod-bug-flat."""
import sys, re
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase

GOLD = r'C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz'
SV098 = r'C:/Users/willi/repos/tqit_soulvizier_classic/upstream/soulvizier_098i/Database/database.arz'
SOUL_PREFIX = r'records\item\equipmentring\soul' + '\\'

FLAT_FAMS = [
 'ascacophus\\gatekeeper_soul','boar\\duskyboar_soul','boar\\ravenousboar_soul',
 'carrionbird\\bloodwing_soul','carrionbird\\carrioncrow_soul','carrionbird\\plaguebird_soul',
 'carrionbird\\plaguelord_soul','giantturtle\\oldsnapper_soul','guardianstatue\\slabskin_soul',
 'hydradon\\shadefeaster_soul','karkinos\\barnacle_soul','limos\\inemios_soul',
 'maenad\\calybe_soul','mountainsatyrelitesoldier_soul','mountainsatyrveteransoldier_soul',
 'odontotyrannus\\beast_soul','raptor\\phyraxus_soul','satyr\\alosstonefist_soul',
 'satyrchampion_soul','satyrpeltast_soul','satyrsoldier_soul','satyrveteranpeltast_soul',
 'satyrveteransoldier_soul','scorpos\\ancientscorpos_soul','skeleton\\awakeneddeadarcher_soul',
 'skeleton\\desecrateddeadarcher_soul','skeleton\\exhumeddeadarcher_soul','terracotta\\qinshi_soul',
]

def norm(p): return str(p).replace('/', '\\').lower().strip()
def first(v):
    if isinstance(v, list): return v[0] if v else None
    return v
def sval(db, rec, f):
    v = first(db.get_field_value(rec, f)); return v.strip() if isinstance(v,str) and v.strip() else None

IGNORE = {'itemLevel','levelRequirement','bitmap','mesh','FileDescription','itemNameTag',
          'itemText','itemCostName','strengthRequirement','dexterityRequirement',
          'intelligenceRequirement'}

def field_dict(db, rec):
    fields = db.get_fields(rec) or {}
    out = {}
    for k, tf in fields.items():
        kk = k.split('###')[0]
        if kk in IGNORE: continue
        out[kk] = tuple(str(x) for x in tf.values)
    return out

def flat_diff(db, ra, rb):
    da, dbb = field_dict(db, ra), field_dict(db, rb)
    diffs = []
    for k in sorted(set(da)|set(dbb)):
        if da.get(k) != dbb.get(k):
            diffs.append((k, da.get(k), dbb.get(k)))
    return diffs

def find_droppers(db, soul_norms):
    hits = defaultdict(list)
    for n in db.record_names():
        fields = db.get_fields(n)
        if not fields: continue
        for k, tf in fields.items():
            if k.split('###')[0] != 'lootFinger2Item1': continue
            for idx, v in enumerate(tf.values):
                if isinstance(v,str) and norm(v) in soul_norms:
                    cls = sval(db, n, 'monsterClassification') or '?'
                    chance = first(db.get_field_value(n,'chanceToEquipFinger2'))
                    hits[soul_norms[norm(v)]].append((n.rsplit('\\',1)[-1], idx, cls, chance))
    return hits

def main():
    gdb = ArzDatabase.from_arz(Path(GOLD))
    gnm = {norm(n): n for n in gdb.record_names()}
    sdb = ArzDatabase.from_arz(Path(SV098))
    snm = {norm(n): n for n in sdb.record_names()}

    # map each flat family's tier records -> family
    soul_norms = {}
    for fam in FLAT_FAMS:
        for t in 'nel':
            p = norm(SOUL_PREFIX + fam + '_%s.dbr' % t)
            if p in gnm: soul_norms[p] = fam
    droppers = find_droppers(gdb, soul_norms)

    for fam in FLAT_FAMS:
        n_p = norm(SOUL_PREFIX+fam+'_n.dbr'); e_p = norm(SOUL_PREFIX+fam+'_e.dbr')
        gn, ge = gnm.get(n_p), gnm.get(e_p)
        ne_diff = flat_diff(gdb, gn, ge) if gn and ge else 'NA'
        sv_present = n_p in snm and e_p in snm
        sv_flat = None
        if sv_present:
            svd = flat_diff(sdb, snm[n_p], snm[e_p])
            sv_flat = (len(svd) == 0)
        drops = droppers.get(fam, [])
        drop_s = '; '.join('%s[i%d %s c=%s]'%(m,i,c,ch) for m,i,c,ch in drops) or 'NO DROPPER'
        print("### %s" % fam)
        print("   golden n-vs-e diff: %s" % ('FLAT(0)' if ne_diff==[] else ('%d fields'%len(ne_diff) if isinstance(ne_diff,list) else ne_diff)))
        if isinstance(ne_diff,list) and ne_diff:
            for k,a,b in ne_diff[:8]: print("       %s: %s -> %s"%(k,a,b))
        print("   SV098: present=%s flat=%s | drops: %s" % (sv_present, sv_flat, drop_s))

if __name__ == '__main__':
    main()
