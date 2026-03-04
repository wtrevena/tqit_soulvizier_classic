"""Deep comparison of working Hydra summon vs broken Rakanizeus summon."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from arz_patcher import ArzDatabase

arz_path = Path(__file__).parent.parent / 'work' / 'SoulvizierClassic' / 'Database' / 'SoulvizierClassic.arz'
print(f"Loading {arz_path}...")
db = ArzDatabase.from_arz(arz_path)


def find_record(name):
    if db.has_record(name):
        return name
    alt = name.replace('\\', '/')
    if db.has_record(alt):
        return alt
    alt = name.replace('/', '\\')
    if db.has_record(alt):
        return alt
    for n in db.record_names():
        if n.replace('\\', '/').lower() == name.replace('\\', '/').lower():
            return n
    return None


def dump_fields(record_path, label, keys_only=False):
    actual = find_record(record_path)
    if not actual:
        print(f"\n--- {label}: NOT FOUND [{record_path}]")
        return None
    fields = db.get_fields(actual)
    rec_type = db._record_types.get(actual, '?')
    print(f"\n--- {label}: {actual}")
    print(f"    Template: {rec_type}")
    print(f"    Fields: {len(fields)}")
    if keys_only:
        return fields
    for key, tf in fields.items():
        fname = key.split('###')[0]
        dtype_name = {0: 'INT', 1: 'FLOAT', 2: 'STR', 3: 'BOOL'}.get(tf.dtype, f'?{tf.dtype}')
        vals = tf.values
        if len(vals) == 1:
            print(f"    {fname} = {vals[0]!r} ({dtype_name})")
        else:
            print(f"    {fname} = {vals!r} ({dtype_name}, {len(vals)} vals)")
    return fields


def compare_records(path_a, label_a, path_b, label_b, show_matching=False):
    """Compare two records field-by-field."""
    actual_a = find_record(path_a)
    actual_b = find_record(path_b)
    if not actual_a:
        print(f"\n  {label_a}: NOT FOUND [{path_a}]")
        return
    if not actual_b:
        print(f"\n  {label_b}: NOT FOUND [{path_b}]")
        return

    fields_a = db.get_fields(actual_a)
    fields_b = db.get_fields(actual_b)

    type_a = db._record_types.get(actual_a, '?')
    type_b = db._record_types.get(actual_b, '?')

    print(f"\n  {label_a}: {len(fields_a)} fields, template={type_a}")
    print(f"  {label_b}: {len(fields_b)} fields, template={type_b}")
    if type_a != type_b:
        print(f"  *** TEMPLATE MISMATCH: {type_a} vs {type_b} ***")

    # Build name->values maps
    map_a = {}
    for key, tf in fields_a.items():
        fname = key.split('###')[0]
        if fname not in map_a:
            map_a[fname] = (tf.dtype, tf.values)
        else:
            # Multiple fields with same name — append to distinguish
            map_a[f"{fname}@{key}"] = (tf.dtype, tf.values)

    map_b = {}
    for key, tf in fields_b.items():
        fname = key.split('###')[0]
        if fname not in map_b:
            map_b[fname] = (tf.dtype, tf.values)
        else:
            map_b[f"{fname}@{key}"] = (tf.dtype, tf.values)

    all_keys = sorted(set(map_a.keys()) | set(map_b.keys()))
    diffs = 0
    only_a = 0
    only_b = 0
    matching = 0

    for k in all_keys:
        in_a = k in map_a
        in_b = k in map_b
        if in_a and not in_b:
            dtype_a, vals_a = map_a[k]
            print(f"  ONLY-{label_a}: {k} = {vals_a!r}")
            only_a += 1
        elif in_b and not in_a:
            dtype_b, vals_b = map_b[k]
            print(f"  ONLY-{label_b}: {k} = {vals_b!r}")
            only_b += 1
        else:
            dtype_a, vals_a = map_a[k]
            dtype_b, vals_b = map_b[k]
            if vals_a != vals_b or dtype_a != dtype_b:
                dt_a = {0:'INT',1:'FLT',2:'STR',3:'BOOL'}.get(dtype_a, '?')
                dt_b = {0:'INT',1:'FLT',2:'STR',3:'BOOL'}.get(dtype_b, '?')
                print(f"  DIFF {k}: {vals_a!r}({dt_a}) vs {vals_b!r}({dt_b})")
                diffs += 1
            else:
                matching += 1
                if show_matching:
                    print(f"  SAME {k}: {vals_a!r}")

    print(f"\n  Summary: {matching} same, {diffs} different, {only_a} only-{label_a}, {only_b} only-{label_b}")


# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART 1: SUMMON SKILL COMPARISON (Hydra vs Rakanizeus)")
print("="*70)
compare_records(
    r'records\skills\soulskills\summon_hydra.dbr', 'HYDRA',
    r'records\skills\soulskills\summon_rakanizeus.dbr', 'RAKAN',
)

# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART 2: PET RECORD COMPARISON (hydra_1 vs rakanizeus_1)")
print("="*70)
compare_records(
    r'records\skills\soulskills\pets\hydra_1.dbr', 'HYDRA',
    r'records\skills\soulskills\pets\rakanizeus_1.dbr', 'RAKAN',
)

# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART 3: SOUL RECORD COMPARISON (Hydra N vs Rakanizeus N)")
print("="*70)

# Find the hydra and rakanizeus soul records
hydra_soul = None
rakan_soul = None
for name in db.record_names():
    nl = name.lower()
    if 'hydra_soul' in nl and 'equipmentring' in nl and '_soul_n.dbr' in nl:
        hydra_soul = name
    if 'rakanizeus_soul' in nl and 'equipmentring' in nl and '_soul_n.dbr' in nl:
        rakan_soul = name

if hydra_soul and rakan_soul:
    compare_records(hydra_soul, 'HYDRA', rakan_soul, 'RAKAN')
else:
    if not hydra_soul:
        print("  Hydra soul N not found!")
    if not rakan_soul:
        print("  Rakanizeus soul N not found!")

# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART 4: EXACT STRING MATCHING — spawnObjects vs record names")
print("="*70)

for skill_path, label in [
    (r'records\skills\soulskills\summon_hydra.dbr', 'Hydra Summon'),
    (r'records\skills\soulskills\summon_rakanizeus.dbr', 'Rakanizeus Summon'),
    (r'records\skills\soulskills\summon_boneash.dbr', 'Boneash Summon'),
]:
    actual = find_record(skill_path)
    if not actual:
        print(f"\n  {label}: NOT FOUND")
        continue
    fields = db.get_fields(actual)
    print(f"\n  {label}: {actual}")
    for key, tf in fields.items():
        fname = key.split('###')[0]
        if fname == 'spawnObjects':
            for i, val in enumerate(tf.values):
                exact = db.has_record(val)
                print(f"    spawnObjects[{i}] = {val!r}  exact_match={exact}")
                if not exact:
                    # Try to find close match
                    for n in db.record_names():
                        if n.lower().replace('/', '\\') == val.lower().replace('/', '\\'):
                            print(f"      CLOSE MATCH: {n!r}")

# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART 5: SOUL → SKILL LINKAGE")
print("="*70)

# Check all Rakanizeus/Boneash soul variants
for pattern, label in [
    ('rakanizeus_soul', 'Rakanizeus'),
    ('boneash_soul', 'Boneash'),
    ('hydra_soul', 'Hydra (ref)'),
    ('chimaera_soul', 'Chimera (ref)'),
]:
    print(f"\n  --- {label} souls ---")
    for name in sorted(db.record_names()):
        nl = name.lower()
        if pattern in nl and 'equipmentring' in nl:
            fields = db.get_fields(name)
            skill_name = None
            skill_level = None
            skill_ctrl = None
            for key, tf in fields.items():
                fname = key.split('###')[0]
                if fname == 'itemSkillName':
                    skill_name = tf.values
                elif fname == 'itemSkillLevel':
                    skill_level = tf.values
                elif fname == 'itemSkillAutoController':
                    skill_ctrl = tf.values
            variant = name.split('/')[-1].split('\\')[-1]
            print(f"    {variant}: itemSkillName={skill_name}, itemSkillLevel={skill_level}, autoCtrl={skill_ctrl}")
            if skill_name and skill_name[0]:
                exact = db.has_record(skill_name[0])
                print(f"      skill exists={exact}")

# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART 6: RECORD TYPE/TEMPLATE CHECK")
print("="*70)

for path, label in [
    (r'records\skills\soulskills\summon_hydra.dbr', 'Hydra summon skill'),
    (r'records\skills\soulskills\summon_rakanizeus.dbr', 'Rakanizeus summon skill'),
    (r'records\skills\soulskills\summon_boneash.dbr', 'Boneash summon skill'),
    (r'records\skills\soulskills\pets\hydra_1.dbr', 'Hydra pet 1'),
    (r'records\skills\soulskills\pets\rakanizeus_1.dbr', 'Rakanizeus pet 1'),
    (r'records\skills\soulskills\pets\boneash_1.dbr', 'Boneash pet 1'),
]:
    actual = find_record(path)
    if actual:
        rec_type = db._record_types.get(actual, '?')
        fields = db.get_fields(actual)
        class_val = None
        tmpl_val = None
        for key, tf in fields.items():
            fname = key.split('###')[0]
            if fname == 'Class':
                class_val = tf.values
            if fname == 'templateName':
                tmpl_val = tf.values
        print(f"  {label}: rec_type={rec_type!r}, Class={class_val}, templateName={tmpl_val}")
    else:
        print(f"  {label}: NOT FOUND")

# ══════════════════════════════════════════════════════════════════════
print("\n" + "="*70)
print("PART 7: ALL WORKING SUMMON SOULS — what fields do they have?")
print("="*70)

# Find ALL souls that have a summon skill (Skill_SpawnPet) as their itemSkillName
# and check what common patterns they share
summon_souls = []
for name in db.record_names():
    nl = name.lower()
    if 'equipmentring' not in nl:
        continue
    if '_soul_n.dbr' not in nl:
        continue
    fields = db.get_fields(name)
    if not fields:
        continue
    skill_name = None
    for key, tf in fields.items():
        if key.split('###')[0] == 'itemSkillName' and tf.values and tf.values[0]:
            skill_name = tf.values[0]
            break
    if not skill_name:
        continue
    # Check if this skill is a Skill_SpawnPet
    skill_actual = find_record(skill_name)
    if not skill_actual:
        continue
    skill_type = db._record_types.get(skill_actual, '')
    if 'SpawnPet' in skill_type or 'Spawn' in skill_type:
        # Check what other fields this soul has related to the skill
        has_auto_ctrl = False
        has_level = False
        for key, tf in fields.items():
            fname = key.split('###')[0]
            if fname == 'itemSkillAutoController' and tf.values and tf.values[0]:
                has_auto_ctrl = True
            if fname == 'itemSkillLevel' and tf.values:
                has_level = True
        basename = name.split('/')[-1].split('\\')[-1]
        summon_souls.append((basename, skill_name, has_auto_ctrl, has_level, skill_type))

print(f"\n  Found {len(summon_souls)} souls with summon (SpawnPet) skills:")
for basename, skill_name, has_auto_ctrl, has_level, skill_type in sorted(summon_souls):
    print(f"    {basename}: skill={skill_name}, hasAutoCtrl={has_auto_ctrl}, hasLevel={has_level}, template={skill_type}")


print("\n=== Deep diagnosis complete ===")
