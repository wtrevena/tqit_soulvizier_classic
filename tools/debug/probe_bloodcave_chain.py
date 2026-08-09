"""probe_bloodcave_chain.py - dump the proxy_hidden_bloodcave_chest reference chain
and the current polisvault chests/loot, so the Gaoler proxy-conversion is modeled on
exact bytes (record_type string in the table AND the Class field, plus every loot slot).

Usage: py tools/debug/probe_bloodcave_chain.py <arz>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def n(s):
    return str(s).replace('/', '\\').lower()


def dump(db, path, only=None):
    lower = {n(x): x for x in db.record_names()}
    real = lower.get(n(path))
    if not real:
        print("  MISSING: %s" % path)
        return None
    rt = db._record_types.get(real, '<none>')
    ff = db.get_fields(real) or {}
    print("\n=== %s" % real)
    print("    record_type(table) = %r" % rt)
    for k, tf in ff.items():
        b = k.split('###')[0]
        if only and not any(b.lower().startswith(p) for p in only):
            continue
        dt = {1: 'I', 2: 'F', 4: 'S', 8: 'B', 0: '?'}.get(tf.dtype, tf.dtype)
        print("    %-28s %s %r" % (b, dt, tf.values))
    return real


def main(argv):
    db = ArzDatabase.from_arz(Path(argv[1]))

    print("\n##### REFERENCE: proxy_hidden_bloodcave_chest chain #####")
    dump(db, r'records\drxitem\container\proxy_hidden_bloodcave_chest.dbr')
    for t in ('01', '02', '03'):
        dump(db, r'records\drxitem\container\pool_hidden_%s.dbr' % t)
    for t in ('01', '02', '03'):
        dump(db, r'records\drxitem\container\hidden_bloodcave_chest_%s.dbr' % t)
    for t in ('01', '02', '03'):
        dump(db, r'records\drxitem\container\loottable_hidden_bloodcave_%s.dbr' % t)

    print("\n\n##### CURRENT polisvault chests + loot #####")
    for n_ in range(1, 6):
        dump(db, r'records\drxitem\container\svc_polisvault_chest_%02d.dbr' % n_)
    for n_ in range(1, 6):
        dump(db, r'records\item\loottables\svc\polisvault_%02d.dbr' % n_)

    print("\n\n##### base proven Proxy example: BossChest05_Hades #####")
    dump(db, r'records\xpack\item\containers\proxies\bosschest05_hades.dbr')

    print("\n\n##### the difficulty equation/limit reference files #####")
    for p in (r'records\proxies orient\containerdifficultyequation.dbr',
              r'records\proxies orient\containerlimitequation.dbr',
              r'records\proxies boss\containerdifficultyequation.dbr',
              r'records\proxies boss\containerlimitequation.dbr'):
        dump(db, p)


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
