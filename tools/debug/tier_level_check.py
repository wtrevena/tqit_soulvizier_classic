r"""Validate _tier_source_level against the real Pygmalion source (base arz)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase  # noqa: E402
import apply_svc_patches as A  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else r'C:/Users/willi/repos/tqit_soulvizier_classic/local/db_backups/pre_runegolem_2026-07-11/SoulvizierClassic.arz'
SRC = r'records\creature\monster\automatoi\um_pygmalion_41.dbr'

db = ArzDatabase.from_arz(Path(BASE))
names = {n.replace('/', '\\').lower(): n for n in db.record_names()}
real = names[SRC.lower()]
sk8 = db.get_field_value(real, 'skillName8')
lv8 = db.get_field_value(real, 'skillLevel8')
print('skillName8 =', sk8, ' skillLevel8 =', lv8)
rep = sk8[0] if isinstance(sk8, list) else sk8
print('_source_skill_level ->', A._source_skill_level(db, real, rep))
for tier in (1, 2, 3):
    print(f'  replicate tier={tier} -> level', A._tier_source_level(db, real, rep, tier))

sk1 = db.get_field_value(real, 'skillName1')
lv1 = db.get_field_value(real, 'skillLevel1')
print('scalar-source skillName1 =', sk1, 'skillLevel1 =', lv1)
sk1v = sk1[0] if isinstance(sk1, list) else sk1
for tier in (1, 2, 3):
    print(f'  scalar tier={tier} -> level', A._tier_source_level(db, real, sk1v, tier))
print('None source (standalone caller) ->', A._tier_source_level(db, None, rep, 2))
