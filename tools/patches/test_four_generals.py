"""Isolated test: apply four_generals over the built build36 arz, then run the
monolith gates that cover this module's records. Read-only vs disk (in-memory db).
  PYTHONIOENCODING=utf-8 py tools/patches/test_four_generals.py <arz>
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from arz_patcher import ArzDatabase
import apply_svc_patches as mono
import four_generals as fg

arz = sys.argv[1]
db = ArzDatabase.from_arz(Path(arz))
print(f"\nLoaded {arz}: {len(db.record_names())} records\n")

tags = {}
fg.apply(db, tags)

print("\n" + "=" * 70)
print("TAGS SET BY MODULE:")
for k, v in tags.items():
    print(f"   {k} = {v}")

print("\n" + "=" * 70)
print("RUNNING MONOLITH GATES OVER THE RESULT")
print("=" * 70)
gates = [
    ('boss-kit clone-shape', lambda: mono._verify_boss_kit_clone_shape(db)),
    ('spawn-eligibility', lambda: mono._verify_mod_spawn_proxies_eligible(db)),
    ('soul-leak', lambda: mono._verify_no_unclassified_soul_leaks(db)),
    ('soul-augment-resolve', lambda: mono._verify_soul_augments_resolve(db)),
    ('soul-itemskill-activation', lambda: mono._verify_soul_itemskill_activation(db)),
    ('granted-skill-diversity', lambda: mono._verify_granted_skill_diversity(db)),
    ('summon-pet parity', lambda: mono._verify_summon_pet_parity(db, mono._SUMMON_PET_BUILDS)),
    ('summon-pet gear', lambda: mono._verify_summon_pet_gear(db, mono._SUMMON_PET_BUILDS)),
    ('summon-pet skill-kit', lambda: mono._verify_summon_pet_skill_kit(db)),
    ('soul-summon-identity', lambda: mono._verify_soul_summon_identity(db, mono._SUMMON_PET_BUILDS)),
]
# apply naming standard (mutates tags) then verify
fails = []
try:
    mono._apply_soul_naming_standard(db, tags)
    mono._verify_soul_naming(db, tags)
    print("  [naming] OK")
except SystemExit as e:
    print(f"  [naming] FAIL: {e}")
    fails.append('naming')

for label, fn in gates:
    try:
        fn()
    except SystemExit as e:
        print(f"  [{label}] FAIL: {e}")
        fails.append(label)
    except Exception as e:
        print(f"  [{label}] ERROR: {type(e).__name__}: {e}")
        fails.append(label)

print("\n" + "=" * 70)
print(f"RESULT: {'ALL GATES PASS' if not fails else 'FAILURES: ' + ', '.join(fails)}")
print("=" * 70)
sys.exit(1 if fails else 0)
