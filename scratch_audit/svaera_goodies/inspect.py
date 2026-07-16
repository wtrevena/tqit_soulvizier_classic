"""Flexible SVAERA record inspector. Loads all 4 DBs once (cached in module
globals across ipython-style reuse is not available, so we reload per run but
that is fine). Usage:

  py inspect.py sample <family-substr> [N]     # sample records in a family
  py inspect.py show <record-name>             # show a record across all DBs
  py inspect.py fields <record-name> <db>      # dump fields (db=sv|our|sv098|base)
  py inspect.py names <family-substr> [N]      # just list names in SVAERA absent-from-ours
"""
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\willi\repos\tqit_soulvizier_classic\tools")
from arz_patcher import ArzDatabase

PATHS = {
    'sv':   Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\475150\2076433374\SVAERA_customquest\Database\SVAERA_customquest.arz"),
    'our':  Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\work\SoulvizierClassic\Database\SoulvizierClassic.arz"),
    'sv098':Path(r"C:\Users\willi\repos\tqit_soulvizier_classic\upstream\soulvizier_098i\Database\database.arz"),
    'base': Path(r"C:\Program Files (x86)\Steam\steamapps\common\Titan Quest Anniversary Edition\Database\database.arz"),
}

_CACHE = {}
def db(k):
    if k not in _CACHE:
        _CACHE[k] = ArzDatabase.from_arz(PATHS[k])
    return _CACHE[k]

def norm(s):
    return str(s).replace('/', '\\').lower().strip()

def flat_fields(d, name):
    ff = d.get_fields(name)
    if not ff:
        return {}
    out = {}
    for k, tf in ff.items():
        base = k.split('###')[0]
        vals = tf.values
        if base not in out:
            out[base] = ';'.join(str(v) for v in vals)
    return out

INTEREST_KEYS = ['Class', 'templateName', 'description', 'itemNameTag', 'itemText',
                 'skillDisplayName', 'itemClassification', 'itemLevel', 'levelRequirement',
                 'characterLevel', 'monsterClassification', 'actorName', 'itemSetName',
                 'baseTexture', 'bitmap', 'skillName', 'buffSkillName', 'petBonusName',
                 'chestName', 'monsterName', 'skillActiveDuration']

def summarize(name):
    key = norm(name)
    print(f"\n=== {name} ===")
    for k in ('sv', 'our', 'sv098', 'base'):
        d = db(k)
        # case-insensitive lookup
        real = None
        for rn in d.record_names():
            if norm(rn) == key:
                real = rn; break
        if real is None:
            print(f"  [{k:5}] ABSENT")
            continue
        ff = flat_fields(d, real)
        cls = ff.get('Class', '?')
        tmpl = ff.get('templateName', '?')
        interesting = {kk: ff[kk] for kk in INTEREST_KEYS if kk in ff and ff[kk] not in ('', '0.000000')}
        print(f"  [{k:5}] Class={cls} tmpl={Path(tmpl).name if tmpl!='?' else '?'} fields={len(ff)}")
        for kk, vv in interesting.items():
            if kk in ('Class', 'templateName'): continue
            print(f"          {kk} = {vv}")

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd = sys.argv[1]
    if cmd == 'sample':
        fam = sys.argv[2].lower()
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
        svd = db('sv')
        base = db('base'); sv098 = db('sv098'); our = db('our')
        base_n = {norm(x) for x in base.record_names()}
        our_n = {norm(x) for x in our.record_names()}
        sv098_n = {norm(x) for x in sv098.record_names()}
        eff = base_n | our_n
        matches = [x for x in svd.record_names() if fam in norm(x) and norm(x) not in eff]
        print(f"SVAERA records matching '{fam}' absent from effective-ours: {len(matches)}")
        for x in matches[:n]:
            ff = flat_fields(svd, x)
            cls = ff.get('Class', '?')
            tmpl = Path(ff.get('templateName', '?')).name
            nametag = ff.get('itemNameTag') or ff.get('description') or ff.get('skillDisplayName') or ff.get('actorName') or ''
            insv098 = 'SV098' if norm(x) in sv098_n else '     '
            print(f"  [{insv098}] {cls:22} {tmpl:26} {x}")
            if nametag:
                print(f"            tag={nametag}")
    elif cmd == 'show':
        summarize(sys.argv[2])
    elif cmd == 'fields':
        name = sys.argv[2]; k = sys.argv[3]
        d = db(k)
        real = None
        for rn in d.record_names():
            if norm(rn) == norm(name):
                real = rn; break
        if real is None:
            print("ABSENT"); return
        ff = flat_fields(d, real)
        for kk, vv in ff.items():
            print(f"  {kk} = {vv}")
    elif cmd == 'names':
        fam = sys.argv[2].lower()
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 40
        svd = db('sv')
        base = db('base'); our = db('our')
        eff = {norm(x) for x in base.record_names()} | {norm(x) for x in our.record_names()}
        matches = [x for x in svd.record_names() if fam in norm(x) and norm(x) not in eff]
        print(f"count={len(matches)}")
        for x in matches[:n]:
            print(f"  {x}")

if __name__ == '__main__':
    main()
