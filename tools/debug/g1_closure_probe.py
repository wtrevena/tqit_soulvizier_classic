"""G1 recursive-closure probe for the two graft subtrees that need porting
(Storm frostnova FX, Dream doppelganger pet). Read-only. Walks .dbr refs from a
set of roots, classifies each referenced record as resolves-in-base+our (no port)
vs port-from-SVAERA, and dumps all mesh/texture refs so the D5 (invisible-pet)
risk can be eyeballed (xpack/xpack2/xpack3 = shippable; _DRX = NOT shipped).

Usage: py tools/debug/g1_closure_probe.py [our_arz] [svaera_arz] [base_arz]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

OUR = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Users/willi/repos/tqit_soulvizier_classic/work/SoulvizierClassic/Database/SoulvizierClassic.arz"
SVAERA = sys.argv[2] if len(sys.argv) > 2 else \
    r"C:/Program Files (x86)/Steam/steamapps/workshop/content/475150/2076433374/SVAERA_customquest/Database/SVAERA_customquest.arz"
BASE = sys.argv[3] if len(sys.argv) > 3 else \
    r"C:/Program Files (x86)/Steam/steamapps/common/Titan Quest Anniversary Edition/Database/database.arz"

ROOTS = [
    r'records\effects\_drx_effects\storm\storm_frostnova_fxpak.dbr',
    r'records\xpack\skills\dream\pet\dreamcopypet.dbr',
]

ART_EXT = ('.msh', '.tex', '.anm', '.ssh')


def norm(s):
    return s.replace('/', '\\').lower().strip()


def load(p):
    print(f"loading {p} ...", flush=True)
    return ArzDatabase.from_arz(Path(p))


def refs_of(db, name):
    out = []
    fields = db.get_fields(name)
    if not fields:
        return out
    for k, tf in fields.items():
        base = k.split('###')[0]
        for v in tf.values:
            if isinstance(v, str):
                vl = v.strip().lower()
                if vl.endswith('.dbr'):
                    out.append(('dbr', base, v.strip()))
                elif vl.endswith(ART_EXT):
                    out.append(('art', base, v.strip()))
    return out


def main():
    sv = load(SVAERA)
    sv_map = {norm(n): n for n in sv.record_names()}
    our = load(OUR)
    our_names = {norm(n) for n in our.record_names()}
    base = load(BASE)
    base_names = {norm(n) for n in base.record_names()}
    resolved = base_names | our_names

    seen = set()
    to_port = []          # (name) present only in svaera
    dangling = []         # not anywhere
    art_refs = set()      # every art ref encountered across the closure
    tpl_of = {}

    work = [norm(r) for r in ROOTS]
    while work:
        n = work.pop()
        if n in seen:
            continue
        seen.add(n)
        # where does it resolve?
        in_base_our = n in resolved
        in_sv = n in sv_map
        if not in_base_our:
            if in_sv:
                to_port.append(n)
            else:
                dangling.append(n)
        # only expand via SVAERA fields (need a source); prefer svaera copy
        src_db, src_name = None, None
        if in_sv:
            src_db, src_name = sv, sv_map[n]
        elif in_base_our and n in our_names:
            src_db, src_name = our, n  # unlikely path
        if src_db is None:
            continue
        fields = src_db.get_fields(src_name)
        if fields:
            for k, tf in fields.items():
                if k.split('###')[0] == 'templateName' and tf.values:
                    tpl_of[n] = str(tf.values[0])
        for kind, fld, v in refs_of(src_db, src_name):
            if kind == 'dbr':
                # do NOT expand base/our records (they resolve; treat as leaves)
                nv = norm(v)
                if nv not in seen:
                    # expand only if we might need to port it (i.e. not resolved here)
                    if nv not in resolved:
                        work.append(nv)
                    else:
                        seen.add(nv)  # leaf
            else:
                art_refs.add((norm(v), fld))

    print("\n" + "=" * 72)
    print(f"CLOSURE from roots: {ROOTS}")
    print("=" * 72)
    print(f"\nRecords to PORT from SVAERA ({len(to_port)}):")
    for n in sorted(to_port):
        print(f"    {n}   [{tpl_of.get(n,'?')}]")
    print(f"\nDANGLING (not in base+our+svaera) ({len(dangling)}):")
    for n in sorted(dangling):
        print(f"    {n}")

    # Art resolvability: we cannot open arcs here, so classify by namespace.
    print(f"\nART refs across the closure ({len(art_refs)}):")
    drx_art = [a for a in art_refs if '_drx' in a[0] or a[0].startswith('_drx')
               or '\\_drx' in a[0]]
    for a, fld in sorted(art_refs):
        flag = ''
        low = a
        if low.startswith('_drx') or '\\_drx_meshes' in low or '_drx_meshes' in low \
                or '_drx_textures' in low:
            flag = '  <-- _DRX (NOT shipped: D5 risk)'
        print(f"    [{fld}] {a}{flag}")

    # Also: dump dreamcopypet's key fields (mesh via which field? actorname/mesh)
    print("\n" + "=" * 72)
    print("dreamcopypet.dbr full field dump (SVAERA)")
    print("=" * 72)
    dn = sv_map.get(norm(r'records\xpack\skills\dream\pet\dreamcopypet.dbr'))
    if dn:
        for k, tf in sv.get_fields(dn).items():
            base_k = k.split('###')[0]
            print(f"    {base_k} = {tf.values}")
    else:
        print("   NOT FOUND")


if __name__ == '__main__':
    main()
