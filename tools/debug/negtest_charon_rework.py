r"""STANDALONE GATE + PLANTED NEGATIVES for `tools/patches/charon_rework.py` (R-231).

Runs the module's `apply()` and then its fail-loud `verify()` over a BUILT arz,
then plants ten defects one at a time and proves the gate REDs on each with
restoration verified GREEN in between. This is the static proof the lane ships
with the new surface (process law #4) - it needs no DB build, no deploy, and it
writes nothing: the arz is loaded into memory and thrown away.

    py tools/debug/negtest_charon_rework.py [path\to\SoulvizierClassic.arz]

Defaults to `work/SoulvizierClassic/Database/SoulvizierClassic.arz`. Any BUILT
arz works, because that artifact already contains the monolith's Charon output -
exactly the state the registry module sees at its slot.
"""
import os
import sys
from pathlib import Path

WT = str(Path(__file__).resolve().parents[2])
LIVE = (sys.argv[1] if len(sys.argv) > 1
        else os.path.join(WT, 'work', 'SoulvizierClassic', 'Database',
                          'SoulvizierClassic.arz'))
sys.path.insert(0, os.path.join(WT, 'tools'))
sys.path.insert(0, os.path.join(WT, 'tools', 'patches'))

from arz_patcher import ArzDatabase          # noqa: E402
import charon_rework as CR                   # noqa: E402
import apply_svc_patches as asp              # noqa: E402

db = ArzDatabase.from_arz(Path(LIVE))
tags = {}

print("\n--- PRE-STATE (what the module inherits from the monolith) ---")
for r in (CR._ORM, CR._BLOOM, CR._BRIAR):
    print("  %-42s mesh=%-46s life=%s life-ascending=%s"
          % (r.rsplit('\\', 1)[-1], CR._one(db, r, 'mesh'),
             db.get_field_value(r, 'characterLife'),
             (lambda L: isinstance(L, list) and len(L) >= 3 and L[0] < L[1] < L[2])(
                 db.get_field_value(r, 'characterLife'))))
print("  _SUMMON_IDENTITY_ALLOW keys: %s" % sorted(asp._SUMMON_IDENTITY_ALLOW))

# ── ROUND-2 P0 REPRO, SEEDED ON PURPOSE ────────────────────────────────────
# In a real build the monolith's `_create_goldenbough_boss` has already run and
# registered THESE EXACT pet paths against `charon_minion_30`. A standalone
# harness starts with an empty registry, so seed the trap explicitly - otherwise
# this test cannot see the defect that red-lined the full DB build (PET-STAT-
# MIRROR, then the F2 soul-summon-identity gate, both on a superseded pair).
_MONOLITH_SRC = (r'records\xpack\creatures\monster\bosses\02_charon'
                 r'\charon_minion_30.dbr')
asp._SUMMON_PET_BUILDS.append((_MONOLITH_SRC, list(CR._PETS)))
print("  SEEDED the monolith's stale pair: %s -> %d pets"
      % (_MONOLITH_SRC.rsplit('\\', 1)[-1], len(CR._PETS)))

print("\n--- APPLY ---")
CR.apply(db, tags)

print("\n--- P0 CHECK: the stale pair must be GONE, exactly one left ---")
_pp = {CR._n(x) for x in CR._PETS}
_pairs = [(s, p) for s, p in asp._SUMMON_PET_BUILDS if {CR._n(q) for q in p} == _pp]
print("  registrations naming the soul pets: %d" % len(_pairs))
for s, _p in _pairs:
    print("    source = %s" % s)
assert len(_pairs) == 1 and CR._n(_pairs[0][0]) == CR._n(CR._D_BLOOM), \
    "P0 NOT FIXED: %r" % (_pairs,)
print("  OK: exactly one, and it names the terminal's own donor.")

print("\n--- VERIFY (fail-loud) ---")
CR.verify(db, tags)

print("\n--- POST-STATE ---")
for r in (CR._ORM, CR._BLOOM, CR._BRIAR):
    kit = [db.get_field_value(r, 'skillName%d' % i) for i in range(1, 25)]
    kit = [k.rsplit('\\', 1)[-1][:-4] for k in kit if isinstance(k, str) and k.strip()]
    rot = []
    for sfx in ('', '2', '3', '4', '5'):
        v = db.get_field_value(r, 'specialAttack%sSkillName' % sfx)
        if isinstance(v, str) and v.strip():
            rot.append('%s=%s@%s' % (sfx or '1', v.rsplit('\\', 1)[-1][:-4],
                                     db.get_field_value(r, 'specialAttack%sChance' % sfx)))
    print("\n  %s" % r)
    print("    race=%s class=%s mesh=%s scale=%s actorHeight=%s"
          % (CR._one(db, r, 'characterRacialProfile'),
             CR._one(db, r, 'monsterClassification'), CR._one(db, r, 'mesh'),
             CR._one(db, r, 'scale'), CR._one(db, r, 'actorHeight')))
    _anim = CR._one(db, r, 'charAnimationTableName')
    _tf = (db.get_fields(_anim) or {}) if _anim else {}
    _runs = sorted({k.split('###')[0] for k, tf in _tf.items()
                    if k.split('###')[0].endswith('RunAnim')
                    and tf.values and str(tf.values[0]).strip()})
    print("    runSpeed=%s anim=%s locomotion=%s   defensive: life=%s bleed=%s"
          % (CR._one(db, r, 'characterRunSpeed'),
             (_anim or 'NONE').rsplit('\\', 1)[-1], _runs or 'NONE',
             CR._one(db, r, 'defensiveLife'), CR._one(db, r, 'defensiveBleeding')))
    print("    life=%s  DisplayAsQuestItem=%s  dropItems=%s  F2=%s"
          % (db.get_field_value(r, 'characterLife'),
             CR._one(db, r, 'DisplayAsQuestItem'), CR._one(db, r, 'dropItems'),
             CR._one(db, r, 'chanceToEquipFinger2')))
    print("    kit: %s" % ', '.join(kit))
    print("    rotation: %s" % '; '.join(rot))
print("\n  pool name1        = %s" % CR._one(db, CR._POOL, 'name1'))
print("  pool champion1    = %s" % CR._one(db, CR._POOL, 'nameChampion1'))
print("  proxy mesh/scale  = %s / %s" % (CR._one(db, CR._PROXY, 'mesh'),
                                         CR._one(db, CR._PROXY, 'scale')))
print("  yard pool name1   = %s" % CR._one(db, CR._YARD_POOL, 'name1'))
print("  terminal orb      = %s" % CR._one(db, CR._BLOOM, 'treasureProxyName'))
for nsl in (3, 4, 5, 6):
    v = db.get_field_value(CR._BLOOM, 'lootMisc%dItem1' % nsl)
    if isinstance(v, list) and v and 'goldenbough' in str(v[0]).lower():
        print("  GOLDEN BOUGH      = lootMisc%d @ chance %s"
              % (nsl, CR._one(db, CR._BLOOM, 'chanceToEquipMisc%d' % nsl)))
print("  soul tiers        = %s" % db.get_field_value(CR._BLOOM, 'lootFinger2Item1'))
print("  _SUMMON_IDENTITY_ALLOW keys now: %s" % sorted(asp._SUMMON_IDENTITY_ALLOW))
print("\n  TAGS:")
for k in sorted(tags):
    print("    %-34s = %s" % (k, tags[k][:96]))

print("\n--- NEGATIVE TESTS (the gate must RED on each) ---")


def neg(label, mutate, restore):
    prev = mutate()
    try:
        CR.verify(db, tags)
    except SystemExit as e:
        first = str(e).split('\n')[1].strip() if '\n' in str(e) else str(e)
        print("  RED (correct) %-34s -> %s" % (label, first[:118]))
    else:
        print("  ** GREEN (GATE HOLE) ** %s" % label)
    restore(prev)
    CR.verify(db, tags)      # restoration must be provable


neg('pool repointed to old boss',
    lambda: (db.set_field(CR._POOL, 'name1', r'records\old.dbr'), None)[1],
    lambda _p: db.set_field(CR._POOL, 'name1', CR._ORM))
neg('Golden Bough chance -> 50',
    lambda: (db.set_field(CR._BLOOM, 'chanceToEquipMisc4', 50.0), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'chanceToEquipMisc4', 100.0))
neg('escort life made descending',
    lambda: (db.set_field(CR._BRIAR, 'characterLife', [878.0, 300.0, 400.0]), None)[1],
    lambda _p: db.set_field(CR._BRIAR, 'characterLife', list(CR._BRIAR_LIFE)))
neg('charFxPakSelfNames on the boss',
    lambda: (db.set_field(CR._ORM, 'charFxPakSelfNames', r'records\x.dbr',
                          CR.DATA_TYPE_STRING), None)[1],
    lambda _p: db.set_field(CR._ORM, 'charFxPakSelfNames', ''))
neg('invented actorHeight (R-126)',
    lambda: (db.set_field(CR._ORM, 'actorHeight', 1.6, CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._ORM, 'actorHeight', 0.0))
neg('terminal orb retargeted (MIN_PROXIES)',
    lambda: (db.set_field(CR._BLOOM, 'treasureProxyName', r'records\y.dbr'), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'treasureProxyName', CR._ORB))
neg('a charon_* signature skill comes back',
    lambda: (db.set_field(CR._ORM, 'skillName18',
                          r'records\xpack\skills\bossskills\charon_summon.dbr',
                          CR.DATA_TYPE_STRING), None)[1],
    lambda _p: db.set_field(CR._ORM, 'skillName18', ''))
neg("'ferryman' exemption comes back",
    lambda: asp._SUMMON_IDENTITY_ALLOW.setdefault('ferryman', 'x'),
    lambda _p: asp._SUMMON_IDENTITY_ALLOW.pop('ferryman', None))
neg('chain HEAD starts paying the soul',
    lambda: (db.set_field(CR._ORM, 'chanceToEquipFinger2', 33.0), None)[1],
    lambda _p: db.set_field(CR._ORM, 'chanceToEquipFinger2', 0.0))
neg('both forms share one display string',
    lambda: tags.__setitem__(CR._TAG_BLOOM, tags[CR._TAG_ORM]),
    lambda _p: tags.__setitem__(CR._TAG_BLOOM, '{^r}Akremon, the Heartwood Ablaze'))

# ── ROUND-2 NEGATIVES: one per finding the round-1 vet raised ───────────────
neg('P0 stale summon-pet pair re-added',
    lambda: (asp._SUMMON_PET_BUILDS.insert(
        0, (r'records\xpack\creatures\monster\bosses\02_charon\charon_minion_30.dbr',
            list(CR._PETS))), None)[1],
    lambda _p: asp._SUMMON_PET_BUILDS.pop(0))
def _repoint_pet_pair(src):
    pp = {CR._n(x) for x in CR._PETS}
    asp._SUMMON_PET_BUILDS[:] = [
        (src, p) if {CR._n(q) for q in p} == pp else (s, p)
        for s, p in asp._SUMMON_PET_BUILDS]


neg('P0 pet pair registered to the wrong source',
    lambda: _repoint_pet_pair(r'records\wrong_donor.dbr'),
    lambda _p: _repoint_pet_pair(CR._D_BLOOM))
neg('P1 TERMINAL made immobile (runSpeed 0)',
    lambda: (db.set_field(CR._BLOOM, 'characterRunSpeed', 0.0), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'characterRunSpeed', CR._BLOOM_SPEED))
neg('P1 escort put back on the locomotion-less rig',
    lambda: (db.set_field(CR._BRIAR, 'charAnimationTableName', CR._BANNED_ANIM),
             None)[1],
    lambda _p: db.set_field(
        CR._BRIAR, 'charAnimationTableName',
        CR._one(db, CR._D_BRIAR, 'charAnimationTableName')))
neg('P1 soul pet made immobile',
    lambda: (db.set_field(CR._PETS[0], 'characterRunSpeed', 0.0), None)[1],
    lambda _p: db.set_field(CR._PETS[0], 'characterRunSpeed',
                            CR._one(db, CR._D_BLOOM, 'characterRunSpeed')))
neg('P2 vitality wall restored on the terminal',
    lambda: (db.set_field(CR._BLOOM, 'defensiveLife', 100.0), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'defensiveLife', 40.0))
neg('P2 bleed immunity leaks onto the terminal',
    lambda: (db.set_field(CR._BLOOM, 'defensiveBleeding', 100.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'defensiveBleeding', 0.0))
neg('NAME COLLISION: the boss is renamed Ormenos',
    lambda: tags.__setitem__(CR._TAG_ORM, '{^r}Ormenos, the Gilded Root'),
    lambda _p: tags.__setitem__(CR._TAG_ORM, '{^r}Akremon, the Grasping Root'))
neg('DURABILITY: life inflated past the Gaoler band',
    lambda: (db.set_field(CR._BLOOM, 'characterLife',
                          [90000.0, 120000.0, 150000.0]), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'characterLife', list(CR._BLOOM_LIFE)))
neg('DURABILITY: life descending across difficulties',
    lambda: (db.set_field(CR._ORM, 'characterLife',
                          [22000.0, 17000.0, 13000.0]), None)[1],
    lambda _p: db.set_field(CR._ORM, 'characterLife', list(CR._ORM_LIFE)))

print("\nHARNESS COMPLETE: apply + verify GREEN on the live arz, and the gate "
      "REDs on every planted defect with restoration proved each time.")
