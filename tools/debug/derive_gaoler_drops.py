"""derive_gaoler_drops.py - re-derive, from a BUILT arz, the full per-difficulty
drop table of both placed Gaoler chests: relic tier + unique tier + gear tier +
numSpawn, on Normal/Epic/Legendary. Proof the proxy conversion tiers correctly.

Usage: py tools/debug/derive_gaoler_drops.py <arz>
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase
import gate_relic_difficulty_tiers as g


def n(s):
    return str(s).replace('/', '\\').lower()


def sc(v):
    return v[0] if isinstance(v, list) and v else v


def gear_tier(pl):
    m = re.search(r'_([nel])0\d[a-z]?\.dbr$', pl)
    return m.group(1) if m else '?'


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))
    lk = g._Lookup(db)
    C = r'records\drxitem\container'
    ACC = [('accessory1', 'Normal '), ('accessoryEpic1', 'Epic   '),
           ('accessoryLegendary1', 'Legend ')]
    for N in ('01', '03'):
        chest = rf'{C}\svc_polisvault_chest_{N}.dbr'
        real = lk.real(chest)
        cls = sc(db.get_field_value(real, 'Class'))
        rtype = db._record_types.get(real)
        print("\n==================================================================")
        print("CHEST svc_polisvault_chest_%s   Class=%s  record_type=%s" % (N, cls, rtype))
        deq = sc(db.get_field_value(real, 'difficultyEquationFile'))
        dlf = sc(db.get_field_value(real, 'difficultyLimitsFile'))
        print("   difficultyEquationFile=%s" % (n(deq).rsplit('\\', 1)[-1] if deq else None))
        print("   difficultyLimitsFile  =%s" % (n(dlf).rsplit('\\', 1)[-1] if dlf else None))
        for slot, label in ACC:
            pool = sc(db.get_field_value(real, slot))
            cont = sc(db.get_field_value(lk.real(pool), 'fixedItemName1')) if pool else None
            cr = lk.real(cont) if cont else None
            loot = sc(db.get_field_value(cr, 'tables')) if cr else None
            lr = lk.real(loot) if loot else None
            lc = sc(db.get_field_value(cr, 'LockedClassification'))
            lrad = sc(db.get_field_value(cr, 'LockedRadius'))
            gold = sc(db.get_field_value(cr, 'goldGeneratorChance'))
            lclass = sc(db.get_field_value(cr, 'lootClassification'))
            nmin = sc(db.get_field_value(lr, 'numSpawnMinEquation')) if lr else None
            nmax = sc(db.get_field_value(lr, 'numSpawnMaxEquation')) if lr else None
            relics, uniques, statics, guar = set(), set(), set(), []
            ff = db.get_fields(lr) or {}
            for k, tf in ff.items():
                b = k.split('###')[0]
                if not b.lower().startswith('loot'):
                    continue
                for v in tf.values:
                    if not isinstance(v, str) or not v:
                        continue
                    pl = n(v)
                    if g.is_relic(pl):
                        relics.add(g.relic_tier(pl))
                    elif 'unique' in pl:
                        uniques.add(gear_tier(pl))
                    elif '\\static' in pl or re.search(r'_[nel]0\dc?\.dbr$', pl):
                        statics.add(gear_tier(pl))
                    if b.startswith('loot3Name'):
                        guar.append(n(v).rsplit('\\', 1)[-1])
            print("   %s: cont=%s" % (label, n(cont).rsplit('\\', 1)[-1]))
            print("        loot table   : %s" % (n(loot).rsplit('\\', 1)[-1] if loot else None))
            print("        lock         : %s r=%s gold%%=%s lootClass=%s"
                  % (lc, lrad, gold, lclass))
            print("        numSpawn     : min=%s max=%s" % (nmin, nmax))
            print("        RELIC tier   : %s" % sorted(relics))
            print("        UNIQUE tier  : %s" % sorted(uniques))
            print("        STATIC gear  : %s" % sorted(statics))
            print("        guaranteed   : %s" % guar)


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
