r"""STANDALONE GATE + PLANTED NEGATIVES for `tools/patches/charon_rework.py` (R-231).

Runs the module's `apply()` and then its fail-loud `verify()` over a BUILT arz,
then plants **42** defects one at a time and proves the gate REDs on each with
restoration verified GREEN in between, plus **two apply-time asserts** (the scaler
swap refusing a non-`hero_scaling` incumbent, and a declared-slot swap refusing a
missing incumbent) that no verify() gate can express. This is the static proof the
lane ships with the new surface (process law #4) - it needs no DB build, no
deploy, and it writes nothing: the arz is loaded into memory and thrown away.

Round 3 added the eight that cover the two surfaces the PLAYER KEEPS - the soul's
stat block and the granted summon's skill-bar face - where round 2 shipped Charon
residue under a green gate.

Round 4 added thirteen for one defect class: A DONOR'S OWN PAYLOAD RIDING ALONG
UNDER A CLAIM THAT DID NOT MENTION IT. Beat 2's clone of
`lowhealth_berserkerrage01` was silently granting 36% damage absorption, 8/s life
regen and **+60% physical damage** (the last one still unmeasured after the vet's
report) under a repeated claim of exact Gaoler durability parity; the terminal
inherited the DRX emberoak's act-2/3 loot tables; the shell inherited a 75/13/1.6
roll it had never had; the escort inherited a beetle-bile burst; and the soul pets
lost the difficulty rows the SHIPPED pets carried.

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


# ── ROUND-3 NEGATIVES: one per finding the round-2 vet raised ──────────────
# The two P1s were both "a superseded writer's output surviving under the new
# writer's at a frozen path", on the two surfaces the PLAYER KEEPS: the soul's
# stat block and the granted summon's skill-bar face.
neg('P1 ferryman COLD block back on the soul',
    lambda: (CR._sf(db, CR._SOUL_TIERS[1], 'offensiveColdMin', 46.8,
                    CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: [ff.pop(k) for ff in [db.get_fields(CR._SOUL_TIERS[1])]
                for k in list(ff) if k.split('###')[0] == 'offensiveColdMin'])
neg("P1 Charon's OWN lever back on the soul (%CurrentLife)",
    lambda: (CR._sf(db, CR._SOUL_TIERS[2], 'offensivePercentCurrentLifeMin', 3.9,
                    CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: [ff.pop(k) for ff in [db.get_fields(CR._SOUL_TIERS[2])]
                for k in list(ff)
                if k.split('###')[0] == 'offensivePercentCurrentLifeMin'])
neg('P1 life-leech + vitality back on the soul',
    lambda: (CR._sf(db, CR._SOUL_TIERS[0], 'offensiveLifeLeechMin', 39.0,
                    CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: [ff.pop(k) for ff in [db.get_fields(CR._SOUL_TIERS[0])]
                for k in list(ff) if k.split('###')[0] == 'offensiveLifeLeechMin'])
neg('P1 stale itemSkillAutoController on the soul',
    lambda: (CR._sf(db, CR._SOUL_TIERS[1], 'itemSkillAutoController',
                    r'records\x_controller.dbr', CR.DATA_TYPE_STRING), None)[1],
    lambda _p: [ff.pop(k) for ff in [db.get_fields(CR._SOUL_TIERS[1])]
                for k in list(ff)
                if k.split('###')[0] == 'itemSkillAutoController'])
neg("P1 Charon's drowned-spirit glyph back on the summon",
    lambda: (db.set_field(CR._SUMMON, 'skillUpBitmapName',
                          r'SVTextures\skills\drownedspiritup.tex'), None)[1],
    lambda _p: db.set_field(CR._SUMMON, 'skillUpBitmapName', CR._SUMMON_ICON[0]))
neg('P1 Lyia Maenad cast sound back on the summon',
    lambda: (db.set_field(
        CR._SUMMON, 'skillHitSound',
        r'records\sounds\soundpak\monstersgreek\maenadalertpak.dbr'), None)[1],
    lambda _p: db.set_field(CR._SUMMON, 'skillHitSound', CR._SUMMON_HIT_SOUND))
neg('P2 hero_scaling survives alongside boss_scaling',
    lambda: (CR._sf(db, CR._ORM, 'skillName20', CR._SK_HERO_SCALING,
                    CR.DATA_TYPE_STRING), None)[1],
    lambda _p: db.set_field(CR._ORM, 'skillName20', ''))
neg('P2 the boss carries no boss_scaling at all',
    lambda: (db.set_field(CR._BLOOM, 'skillName12', CR._SK_HPSCALING), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'skillName12', CR._SK_BOSS_SCALING))


# ── ROUND-4 NEGATIVES: one per finding the round-3 vet raised, plus the one it
# missed. All the same defect class - A DONOR'S OWN PAYLOAD RIDING ALONG UNDER A
# CLAIM THAT DID NOT MENTION IT - so every gate below reads the FINAL record.
neg("P1 beat 2's inherited 36% damage shield is back",
    lambda: (db.set_field(CR._SPLIT, 'damageAbsorptionPercent',
                          [10.0, 12.0, 15.0, 18.0, 22.0, 24.0, 26.0, 29.0, 32.0,
                           36.0, 38.0, 40.0, 43.0, 46.0, 50.0, 52.0, 54.0, 57.0,
                           60.0, 65.0]), None)[1],
    lambda _p: db.set_field(CR._SPLIT, 'damageAbsorptionPercent',
                            CR._flat(CR._SPLIT_ABSORB)))
neg("P1 beat 2 heals the boss in its own last third",
    lambda: (db.set_field(CR._SPLIT, 'characterLifeRegen',
                          CR._flat(8.0)), None)[1],
    lambda _p: db.set_field(CR._SPLIT, 'characterLifeRegen',
                            CR._flat(CR._SPLIT_REGEN)))
neg("P1 beat 2's UNAUTHORED +60% physical (the one the vet missed)",
    lambda: (db.set_field(CR._SPLIT, 'offensivePhysicalModifier',
                          CR._flat(60.0)), None)[1],
    lambda _p: db.set_field(CR._SPLIT, 'offensivePhysicalModifier',
                            CR._flat(CR._SPLIT_PHYSMOD)))
neg("P1 beat 2 wired past the end of its own array",
    lambda: (db.set_field(CR._SPLIT, 'damageAbsorptionPercent', [0.0, 0.0]),
             None)[1],
    lambda _p: db.set_field(CR._SPLIT, 'damageAbsorptionPercent',
                            CR._flat(CR._SPLIT_ABSORB)))
neg('P2 terminal loot back on the act-2/3 band',
    lambda: (db.set_field(CR._BLOOM, 'lootMisc3Item2',
                          [r'records\xpack\item\loottables\arcaneformulae'
                           r'\0%d_act2_arcaneformulae.dbr' % i
                           for i in (1, 2, 3)]), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'lootMisc3Item2', list(CR._ACT4_FORMULAE)))
neg('P2 terminal unique table dropped an act (n_03_unique_all)',
    lambda: (db.set_field(CR._BLOOM, 'lootMisc1Item1',
                          [r'records\item\loottables\raremisc\%s_03_unique_all.dbr'
                           % t for t in ('n', 'e', 'l')]), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'lootMisc1Item1', list(CR._ACT4_UNIQUE)))
neg('P2 the act-3 jungleroot row un-muted at the Styx',
    lambda: (db.set_field(CR._BLOOM, 'chanceToEquipMisc1Item5', 4), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'chanceToEquipMisc1Item5', 0))
neg("P2 the SHELL's undisclosed 75% loot roll is back",
    lambda: (db.set_field(CR._ORM, 'chanceToEquipMisc3', 75.0), None)[1],
    lambda _p: db.set_field(CR._ORM, 'chanceToEquipMisc3', 0.0))
neg('P3 the escort is a beetle-bile spitter again (cast)',
    lambda: (db.set_field(CR._BRIAR, 'specialAttackSkillName',
                          CR._DEAD_BRIAR_SKILL), None)[1],
    lambda _p: db.set_field(CR._BRIAR, 'specialAttackSkillName', CR._SK_QUILLBARB))
neg('P3 the escort is a beetle-bile spitter again (declared slot)',
    lambda: (db.set_field(CR._BRIAR, 'skillName1', CR._DEAD_BRIAR_SKILL), None)[1],
    lambda _p: db.set_field(CR._BRIAR, 'skillName1', CR._SK_QUILLBARB))
neg("P3 a monster's hero_scaling back on the player's permanent pet",
    lambda: (db.set_field(CR._PETS[0], 'skillName12', CR._SK_HERO_SCALING),
             None)[1],
    lambda _p: db.set_field(CR._PETS[0], 'skillName12',
                            CR._PET_DIFFICULTY_ROWS[0][0]))
neg('P3 a soul pet loses a shipped difficulty row',
    lambda: (db.set_field(CR._PETS[2], 'skillName13', ''), None)[1],
    lambda _p: db.set_field(CR._PETS[2], 'skillName13',
                            CR._PET_DIFFICULTY_ROWS[1][0]))
neg('P2 the traveler NPC still sends you to "(Charon)"',
    lambda: tags.__setitem__(CR._TAG_TRAVELER, 'Traveler: Golden Bough (Charon)'),
    lambda _p: tags.pop(CR._TAG_TRAVELER, None))
neg('P3 a soul pet difficulty row has the wrong vector',
    lambda: (db.set_field(CR._PETS[1], 'skillLevel12', [1, 1, 1]), None)[1],
    lambda _p: db.set_field(CR._PETS[1], 'skillLevel12',
                            list(CR._PET_DIFFICULTY_ROWS[0][1])))

# ══════════════════════════════════════════════════════════════════════════════
# ROUND 5: one planted negative per fixed vet finding, so every claim this round
# makes is a claim a gate can catch losing. The two P1s are covered three ways
# each, because both were shipped GREEN by round 4's gates.
# ══════════════════════════════════════════════════════════════════════════════
_SOUL_L = CR._SOUL_TIERS[2]

# ---- P1 (a): the soul's downside back on the CREATURE locomotion field -------
neg('P1 soul carries characterRunSpeed (item!)',
    lambda: (db.set_field(_SOUL_L, 'characterRunSpeed', -5.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: (db.get_fields(_SOUL_L).pop('characterRunSpeed', None),
                db._modified.add(_SOUL_L)))
# ---- P1 (b): the dead offensiveSlowPhysical family comes back ----------------
neg('P1 soul back on offensiveSlowPhysical*',
    lambda: (db.set_field(_SOUL_L, 'offensiveSlowPhysicalMin', 40.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: (db.get_fields(_SOUL_L).pop('offensiveSlowPhysicalMin', None),
                db._modified.add(_SOUL_L)))
# ---- P1 (c): a real field at a value no peer soul reaches --------------------
neg('P1 an authored soul stat leaves its band',
    lambda: (db.get_field_value(_SOUL_L, 'offensiveSlowRunSpeedMin'),
             db.set_field(_SOUL_L, 'offensiveSlowRunSpeedMin', 900.0,
                          CR.DATA_TYPE_FLOAT))[0],
    lambda p: db.set_field(_SOUL_L, 'offensiveSlowRunSpeedMin', p,
                           CR.DATA_TYPE_FLOAT))
# ---- P1 (d): a stat field no other soul in the mod carries at all ------------
neg('P1 a soul stat unknown to the roster',
    lambda: (db.set_field(_SOUL_L, 'offensiveTrapMin', 30.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: (db.get_fields(_SOUL_L).pop('offensiveTrapMin', None),
                db._modified.add(_SOUL_L)))

# ---- P1 (e): the terminal's ordinary loot volume comes back ------------------
neg('P1 terminal Misc1 un-muted (the 176.6)',
    lambda: (db.set_field(CR._BLOOM, 'chanceToEquipMisc1', 1.6,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'chanceToEquipMisc1', 0.0,
                            CR.DATA_TYPE_FLOAT))
neg('P1 terminal guarantees a potion again',
    lambda: (db.set_field(CR._BLOOM, 'chanceToEquipMisc2', 100.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'chanceToEquipMisc2', 0.0,
                            CR.DATA_TYPE_FLOAT))
neg('P1 the mute eats the Golden Bough too',
    lambda: (db.set_field(CR._BLOOM, 'chanceToEquipMisc4', 0.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'chanceToEquipMisc4', 100.0,
                            CR.DATA_TYPE_FLOAT))
# ---- P3: the retinue disclosure goes stale under us --------------------------
neg('P3 retinue faucet moves off its disclosed 3.0',
    lambda: (db.get_field_value(CR._RETINUE_PETS[0], 'chanceToEquipMisc1'),
             db.set_field(CR._RETINUE_PETS[0], 'chanceToEquipMisc1', 25.0,
                          CR.DATA_TYPE_FLOAT))[0],
    lambda p: db.set_field(CR._RETINUE_PETS[0], 'chanceToEquipMisc1', p,
                           CR.DATA_TYPE_FLOAT))

# ---- P2: mana -----------------------------------------------------------------
neg('P2 phase 1 back to zero mana regen',
    lambda: (db.set_field(CR._ORM, 'characterManaRegen', 0.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._ORM, 'characterManaRegen', CR._ORM_MANA_REGEN,
                            CR.DATA_TYPE_FLOAT))
neg('P2 the terminal keeps the inherited 1177',
    lambda: (db.set_field(CR._BLOOM, 'characterMana', 1177.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'characterMana', CR._BLOOM_MANA,
                            CR.DATA_TYPE_FLOAT))
# ...and the STARVATION half: the constants stay put, the ROTATION outgrows them.
neg('P2 a retune outgrows the funded rotation',
    lambda: (db.get_field_value(CR._ORM, 'skillLevel7'),
             db.set_field(CR._ORM, 'skillLevel7', 20))[0],
    lambda p: db.set_field(CR._ORM, 'skillLevel7', p))

# ---- P2: the CC / elemental profile ------------------------------------------
neg('P2 freeze-lock reopens on phase 1',
    lambda: (db.set_field(CR._ORM, 'defensiveFreeze', 0.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._ORM, 'defensiveFreeze',
                            CR._CC_TARGET['defensiveFreeze'], CR.DATA_TYPE_FLOAT))
neg('P2 the 300% stun wall comes back',
    lambda: (db.get_field_value(CR._BLOOM, 'skillName13'),
             db.set_field(CR._BLOOM, 'skillName13', CR._DEAD_BLOOM_SKILL_FIRE,
                          CR.DATA_TYPE_STRING))[0],
    lambda p: db.set_field(CR._BLOOM, 'skillName13', p, CR.DATA_TYPE_STRING))
neg('P2 the terminal stops resisting its own fire',
    lambda: (db.set_field(CR._BLOOM, 'defensiveFire', 60.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._BLOOM, 'defensiveFire', CR._BLOOM_FIRE_RES,
                            CR.DATA_TYPE_FLOAT))
neg('P2 phase 1 loses its deliberate fire weakness',
    lambda: (db.set_field(CR._ORM, 'defensiveFire', 30.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: (db.get_fields(CR._ORM).pop('defensiveFire', None),
                db._modified.add(CR._ORM)))
neg('P2 the petrify disclosure goes stale',
    lambda: (db.get_field_value(CR._ORM, 'skillName14'),
             db.set_field(CR._ORM, 'skillName14', '', CR.DATA_TYPE_STRING))[0],
    lambda p: db.set_field(CR._ORM, 'skillName14', p, CR.DATA_TYPE_STRING))

# ---- P3: beat 2's face --------------------------------------------------------
neg('P3 beat 2 wears Adrenaline again',
    lambda: (db.set_field(CR._SPLIT, 'skillActivatedAuraName',
                          r'Records\Effects\Combat\Skill_Adrenaline_FX01.dbr',
                          CR.DATA_TYPE_STRING), None)[1],
    lambda _p: db.set_field(CR._SPLIT, 'skillActivatedAuraName', CR._SPLIT_FX,
                            CR.DATA_TYPE_STRING))
neg('P3 beat 2 keeps the Buff07 target pak',
    lambda: (db.set_field(CR._SPLIT, 'targetFxPakName',
                          r'Records\Effects\Default\Buff07.dbr',
                          CR.DATA_TYPE_STRING), None)[1],
    lambda _p: db.set_field(CR._SPLIT, 'targetFxPakName', CR._SPLIT_FX,
                            CR.DATA_TYPE_STRING))
neg('P3 beat 2 FX points at an unrendered path',
    lambda: (db.set_field(CR._SPLIT, 'skillActivatedAuraName',
                          r'Records\Effects\Nature\NotAThing_FX99.dbr',
                          CR.DATA_TYPE_STRING), None)[1],
    lambda _p: db.set_field(CR._SPLIT, 'skillActivatedAuraName', CR._SPLIT_FX,
                            CR.DATA_TYPE_STRING))
neg('P3 beat 2 keeps the donor ActorName',
    lambda: (db.set_field(CR._SPLIT, 'ActorName', 'DefensiveMastery_Adrenaline',
                          CR.DATA_TYPE_STRING), None)[1],
    lambda _p: db.set_field(CR._SPLIT, 'ActorName', CR._SPLIT_ACTOR_NAME,
                            CR.DATA_TYPE_STRING))

# ---- P3: R-126 on the pets ----------------------------------------------------
neg('P3 a soul pet keeps the Lyia actorHeight 2.0',
    lambda: (db.set_field(CR._PETS[0], 'actorHeight', 2.0,
                          CR.DATA_TYPE_FLOAT), None)[1],
    lambda _p: db.set_field(CR._PETS[0], 'actorHeight', 1.0, CR.DATA_TYPE_FLOAT))
neg('P3 a soul pet drifts off the dropper rig',
    lambda: (db.get_field_value(CR._PETS[1], 'mesh'),
             db.set_field(CR._PETS[1], 'mesh',
                          r'XPack\Creatures\Monster\CharonGhost\CharonGhost.msh',
                          CR.DATA_TYPE_STRING))[0],
    lambda p: db.set_field(CR._PETS[1], 'mesh', p, CR.DATA_TYPE_STRING))

# ── APPLY-TIME assert (not a verify() gate): a declared-slot swap is never blind
print("\n--- APPLY-TIME ASSERT: _swap_declared_skill refuses a missing incumbent ---")
try:
    CR._swap_declared_skill(db, CR._BRIAR, CR._DEAD_BRIAR_SKILL, CR._SK_QUILLBARB,
                            [1, 1, 1], 'the incumbent is already gone')
except SystemExit as e:
    print("  RED (correct) blind declared-slot overwrite -> %s"
          % str(e).split('\n')[0][:118])
else:
    print("  ** GREEN (GATE HOLE) ** _swap_declared_skill wrote a slot blind")
CR.verify(db, tags)

# ── APPLY-TIME assert (not a verify() gate): the scaler swap is no longer blind
print("\n--- APPLY-TIME ASSERT: _swap_scaler refuses a non-hero_scaling slot ---")
_prev = CR._one(db, CR._BRIAR, 'skillName12')
try:
    CR._swap_scaler(db, CR._BRIAR)          # junglecreep carries globalproperties_*
except SystemExit as e:
    print("  RED (correct) blind scaler overwrite -> %s"
          % str(e).split('\n')[0][:118])
else:
    print("  ** GREEN (GATE HOLE) ** _swap_scaler overwrote %r blind" % _prev)
    db.set_field(CR._BRIAR, 'skillName12', _prev)
CR.verify(db, tags)

print("\nHARNESS COMPLETE: apply + verify GREEN on the live arz, and the gate "
      "REDs on every planted defect with restoration proved each time.")
