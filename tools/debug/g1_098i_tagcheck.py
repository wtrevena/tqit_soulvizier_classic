"""Check which of the 12 graft tags already exist in the mod's SV 0.98i Text_EN.arc
(build_modstrings' base source), with their existing values, so the graft only
adds genuinely-new tags (avoid the duplicate-tag gate conflict)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arc_patcher import ArcArchive

SV098 = sys.argv[1] if len(sys.argv) > 1 else \
    r"C:/Users/willi/repos/tqit_soulvizier_classic/upstream/soulvizier_098i/Resources/Text_EN.arc"

WANT = ['tagSlam_NAME', 'tagSlam_DESC', 'tagSlam_FissureNAME', 'tagSlam_FissureDESC',
        'tagRuptureNAME', 'tagRuptureDESC', 'tagBurningBoltsNAME', 'tagBurningBoltsDESC',
        'tagFlareNAME', 'tagFlareDESC', 'tagSVAERSkillStorm001', 'tagSVAERSkillStormDescription001']


def main():
    arc = ArcArchive.from_file(Path(SV098))
    found = {}
    for e in arc.entries:
        nm = getattr(e, 'name', '')
        if not nm.lower().endswith('.txt'):
            continue
        t = arc.get_text(nm)
        if not t:
            continue
        for line in t.split('\n'):
            line = line.strip('\r').strip()
            if '=' in line and not line.startswith('//'):
                k, _, v = line.partition('=')
                if k.strip() in WANT:
                    found.setdefault(k.strip(), (nm, v.strip()))
    print("=== which graft tags PRE-EXIST in SV 0.98i Text (the mod base source) ===")
    for w in WANT:
        if w in found:
            nm, v = found[w]
            print(f"  PRE-EXISTS  {w}  [{nm}]\n      = {v}")
        else:
            print(f"  new (safe)  {w}")


if __name__ == '__main__':
    main()
