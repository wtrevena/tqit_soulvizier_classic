"""probe_xp_formulas.py - R-100 #11 recon.

Will: "there are forge formulas for experience potions that require souls from a
specific act, but the souls that we added for the new monsters we added into those
acts and probably the souls we added that were missing do not have the proper
classification on them so you cant use them in the forge formulas."

This probe answers ONE question with evidence: WHICH FIELD do the base game's
experience-potion formulas key on when they demand "a soul from Act N"?

Usage:  py tools/debug/probe_xp_formulas.py <arz> [more.arz ...]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from arz_patcher import ArzDatabase


def fv(db, name, field):
    v = db.get_field_value(name, field)
    return v


def dump(db, name, label=''):
    print(f"\n--- {name}  {label}")
    ff = db.get_fields(name) or {}
    for k in sorted(ff):
        base = k.split('###')[0]
        vals = ff[k].values
        if not vals or (len(vals) == 1 and vals[0] in ('', 0, 0.0)):
            continue
        print(f"    {base} = {vals}")


def main(argv):
    for arz in argv[1:]:
        print(f"\n================ {arz}")
        db = ArzDatabase.from_arz(Path(arz))
        names = db.record_names()
        print(f"records: {len(names)}")
        # 1. every ItemArtifactFormula whose path or artifact smells of experience
        formulas = []
        for n in names:
            cls = db.get_field_value(n, 'Class')
            if cls and 'formula' in str(cls).lower():
                formulas.append(n)
        print(f"formula-class records: {len(formulas)}")
        xp = [n for n in formulas
              if 'experience' in n.lower() or 'potionofexp' in n.lower()]
        print(f"experience-ish formulas: {len(xp)}")
        for n in sorted(xp)[:40]:
            print('   ', n)
        for n in sorted(xp)[:3]:
            dump(db, n)
        # 2. what do reagent fields ever point at?
        from collections import Counter
        c = Counter()
        reagent_targets = Counter()
        for n in formulas:
            ff = db.get_fields(n) or {}
            for k, tf in ff.items():
                b = k.split('###')[0]
                if 'reagent' in b.lower() or 'artifactname' in b.lower():
                    c[b] += 1
                    for v in tf.values:
                        if isinstance(v, str) and v:
                            reagent_targets[v.lower()] += 1
        print("\nformula fields seen:")
        for k, v in c.most_common():
            print(f"    {k}: {v}")
        print("\ntop reagent targets:")
        for k, v in reagent_targets.most_common(25):
            print(f"    {v:5d}  {k}")


if __name__ == '__main__':
    sys.exit(main(sys.argv) or 0)
