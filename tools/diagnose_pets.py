"""Diagnose pet summon records in the built .arz database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

arz_path = Path(__file__).parent.parent / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'
print(f"Loading {arz_path}...")
db = ArzDatabase.from_arz(arz_path)

# Check what paths exist for our records
print("\n=== Searching for Rakanizeus/Boneash/Hydra records ===")
for name in sorted(db.record_names()):
    nl = name.lower()
    if any(k in nl for k in ('rakanizeus', 'boneash', 'hydra')):
        if 'soulskill' in nl or 'pets' in nl or 'summon' in nl:
            fields = db.get_fields(name)
            fc = len(fields) if fields else 0
            print(f"  {name}  ({fc} fields)")

# Check the summon skill records
for skill_name, label in [
    (r'records\skills\soulskills\summon_rakanizeus.dbr', 'Rakanizeus Summon'),
    (r'records/skills/soulskills/summon_rakanizeus.dbr', 'Rakanizeus Summon (fwd)'),
    (r'records\skills\soulskills\summon_boneash.dbr', 'Boneash Summon'),
    (r'records/skills/soulskills/summon_boneash.dbr', 'Boneash Summon (fwd)'),
    (r'records/skills/soulskills/summon_hydra.dbr', 'Hydra Summon (fwd)'),
    (r'records\skills\soulskills\summon_hydra.dbr', 'Hydra Summon (bk)'),
]:
    exists = db.has_record(skill_name)
    print(f"\n--- {label}: {'EXISTS' if exists else 'NOT FOUND'} [{skill_name}]")
    if exists:
        fields = db.get_fields(skill_name)
        print(f"  Field count: {len(fields)}")
        for key in ('Class', 'templateName', 'spawnObjects', 'skillMaxLevel',
                     'skillManaCost', 'isPetDisplayable', 'petLimit',
                     'skillDisplayName', 'spawnObjectsTimeToLive',
                     'skillCooldownTime'):
            for fk, tf in fields.items():
                if fk.split('###')[0] == key:
                    print(f"  {key} = {tf.values} (dtype={tf.dtype})")
                    break

# Check pet records
for pet_path, label in [
    (r'records/skills/soulskills/pets/rakanizeus_1.dbr', 'Rakanizeus Pet 1 (fwd)'),
    (r'records\skills\soulskills\pets\rakanizeus_1.dbr', 'Rakanizeus Pet 1 (bk)'),
    (r'records/skills/soulskills/pets/boneash_1.dbr', 'Boneash Pet 1 (fwd)'),
    (r'records\skills\soulskills\pets\boneash_1.dbr', 'Boneash Pet 1 (bk)'),
    (r'records/skills/soulskills/pets/hydra_1.dbr', 'Hydra Pet 1 (fwd)'),
    (r'records\skills\soulskills\pets\hydra_1.dbr', 'Hydra Pet 1 (bk)'),
]:
    exists = db.has_record(pet_path)
    if not exists:
        print(f"\n--- {label}: NOT FOUND [{pet_path}]")
        continue
    print(f"\n--- {label}: EXISTS [{pet_path}]")
    fields = db.get_fields(pet_path)
    print(f"  Field count: {len(fields)}")
    for key in ('Class', 'templateName', 'mesh', 'charLevel', 'characterLife',
                'controller', 'description', 'charAnimationTableName',
                'skillName1', 'skillName2', 'dropItems', 'characterRunSpeed',
                'handHitDamageMin', 'handHitDamageMax', 'StatusIcon'):
        for fk, tf in fields.items():
            if fk.split('###')[0] == key:
                print(f"  {key} = {tf.values} (dtype={tf.dtype})")
                break

# Check soul records
print("\n=== Soul records with itemSkillName ===")
for name in sorted(db.record_names()):
    nl = name.lower()
    if ('rakanizeus_soul' in nl or 'boneash_soul' in nl) and 'equipmentring' in nl:
        fields = db.get_fields(name)
        print(f"\n  {name}")
        for key in ('itemSkillName', 'itemSkillLevel', 'itemSkillAutoController'):
            for fk, tf in fields.items():
                if fk.split('###')[0] == key:
                    print(f"    {key} = {tf.values} (dtype={tf.dtype})")
                    break
        # Also check for hydra soul to compare
for name in sorted(db.record_names()):
    nl = name.lower()
    if 'hydra_soul' in nl and 'equipmentring' in nl:
        fields = db.get_fields(name)
        print(f"\n  {name} (REFERENCE)")
        for key in ('itemSkillName', 'itemSkillLevel', 'itemSkillAutoController'):
            for fk, tf in fields.items():
                if fk.split('###')[0] == key:
                    print(f"    {key} = {tf.values} (dtype={tf.dtype})")
                    break

print("\n=== Diagnosis complete ===")
