"""Determine how a Skill_Modifier links to its base skill: dump full fields of an
existing WORKING modifier in our mod vs a SVAERA graft-source modifier, and the
base skill's connector fields. Read-only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase

OUR = r"C:/Users/willi/repos/tqit_soulvizier_classic/.claude/worktrees/wf_2c6626bc-36a-2/local/g1_build/Database/SoulvizierClassic.arz"
SVAERA = r"C:/Program Files (x86)/Steam/steamapps/workshop/content/475150/2076433374/SVAERA_customquest/Database/SVAERA_customquest.arz"


def norm(s):
    return s.replace('/', '\\').lower().strip()


def dump(db, mp, path):
    n = mp.get(norm(path))
    print(f"\n=== {path}  ({'FOUND' if n else 'MISSING'})")
    if not n:
        return
    for k, tf in db.get_fields(n).items():
        bk = k.split('###')[0]
        print(f"    {bk} = {tf.values}")


our = ArzDatabase.from_arz(Path(OUR))
om = {norm(x): x for x in our.record_names()}
# an existing working modifier + its base, in our mod
dump(our, om, r'records\skills\warfare\drxwarwind_lacerate.dbr')
dump(our, om, r'records\skills\warfare\drxwarwind.dbr')

sv = ArzDatabase.from_arz(Path(SVAERA))
sm = {norm(x): x for x in sv.record_names()}
dump(sv, sm, r'records\skills\warfare\drx_clubslam_fissure.dbr')
dump(sv, sm, r'records\skills\warfare\drx_ancestralmod.dbr')
dump(sv, sm, r'records\skills\warfare\drx_clubslam.dbr')
