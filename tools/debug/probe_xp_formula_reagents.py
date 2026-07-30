"""probe_xp_formula_reagents.py - R-100 #11 recon, step 2.

The 12 SV "Lesser Potion of Experience" forge formulas
(records\\item\\formulas\\{n,e,l}_{01..04}_lesserpotionofexperience_formula.dbr)
carry an ENUMERATED reagent list. This probe measures, per formula:
  - how many soul paths the reagent slots enumerate
  - the difficulty suffix distribution of those paths (_n/_e/_l)
  - which of OUR souls (present in the arz) are absent from EVERY list

Usage: py tools/debug/probe_xp_formula_reagents.py <arz> [--full]
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase

FORMULA_DIR = r'records\item\formulas'


def norm(s):
    return str(s).replace('/', '\\').lower()


def main(argv):
    arz = argv[1]
    full = '--full' in argv
    db = ArzDatabase.from_arz(Path(arz))
    names = db.record_names()
    forms = sorted(n for n in names
                   if 'lesserpotionofexperience_formula' in n.lower())
    print(f"arz={arz}  records={len(names)}  xp formulas={len(forms)}")
    listed = set()
    for f in forms:
        ff = db.get_fields(f) or {}
        row = {}
        for k, tf in ff.items():
            b = k.split('###')[0]
            if b.startswith('reagent') and b.endswith('BaseName'):
                row[b] = [v for v in tf.values if isinstance(v, str) and v]
        art = db.get_field_value(f, 'artifactName')
        print(f"\n{f}")
        print(f"    artifactName={art}")
        for b in sorted(row):
            vals = row[b]
            sfx = Counter()
            for v in vals:
                stem = norm(v).rsplit('\\', 1)[-1].replace('.dbr', '')
                sfx[stem[-2:]] += 1
            print(f"    {b}: {len(vals)} entries  suffixes={dict(sfx)}")
            if vals:
                print(f"        [0] = {vals[0]}")
                if len(vals) > 1:
                    print(f"        [1] = {vals[1]}")
                    print(f"        [-1]= {vals[-1]}")
            for v in vals:
                listed.add(norm(v))
    # every soul record in the arz
    souls = [n for n in names
             if 'equipmentring\\soul\\' in norm(n) or 'equipmentring/soul/' in norm(n)]
    souls_n = set(norm(s) for s in souls)
    missing = sorted(souls_n - listed)
    print(f"\n\nsoul records in arz: {len(souls_n)}")
    print(f"soul paths listed by the 12 formulas: {len(listed & souls_n)}")
    print(f"souls NOT listed anywhere: {len(missing)}")
    byfolder = Counter(m.split('\\')[4] if len(m.split('\\')) > 5 else m for m in missing)
    print("\nmissing by soul folder (top 40):")
    for k, v in byfolder.most_common(40):
        print(f"    {v:5d}  {k}")
    if full:
        print("\nALL MISSING:")
        for m in missing:
            print("   ", m)
    # any soul filler items
    print("\nanysoul records:")
    for n in sorted(names):
        if 'anysoul' in n.lower():
            print("   ", n, "  Class=", db.get_field_value(n, 'Class'),
                  " nameTag=", db.get_field_value(n, 'itemNameTag'))


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
