r"""tools/patches/charon_rework.py - the Golden Bough forecourt uber, REWORKED.

WILL, VERBATIM (2026-08-11):

    "the charon uber boss we created needs to be re-worked, he is pretty much
     identical to the base game charon boss we cloned him off. maybe we can
     replace him with a different uber monster that is more unique"

He is right, and the artifact says so in one table. The shipped uber was NOT
"the same guy, bigger" - `um_charon_ferryman_99` (Charon01.msh, sc 1.7) already
rig-swapped to `um_charonform2_ferryman_99` (Charon02.msh, sc 1.2). The defect
is the KIT, byte-for-byte against the base bosses it was cloned from:

    | slot            | ours F1                 | boss_charon_43          |
    | skillName1      | charon_projectiletrigger| charon_projectiletrigger|
    | skillName4      | charon_selfbuff         | charon_selfbuff         |
    | skillName6      | charon_geyserform1      | charon_geyserform1      |
    | skillName7      | charon_summon           | charon_summon           |
    | specialAttack*  | identical               | identical               |

...and the same for form 2 vs `boss_charonform2_43`. The only authored deltas
were `characterLife`, four resist floats, `scale`, `actorHeight`, one aura and a
`deathEffect`. `apply_svc_patches._create_goldenbough_boss` says it out loud:
*"Keep Charon02's own kit verbatim"*. There was nothing to salvage.

================================================================================
WHAT SHIPS: ORMENOS, THE GILDED ROOT
================================================================================
Every hand that ever reached for the Golden Bough is still at the shrine, grown
through and held fast, because the black tree those wrists are grown into is what
the forecourt actually keeps. Ormenos does not ferry, does not bargain and does
not bleed. It takes the toll in arms. And when the trunk finally splits, the
gold-burning bloom that grows the boughs steps out of it to take yours.

Three beats, two bodies, the SAME proven `actorToSpawnOnDeath` link.

  BEAT 1 - THE ROOTED WARDEN (phase 1, `Ascacophus02.msh`, PLANT)
    * THE WOOD DOES NOT BLEED - the donor's native `ascacophus_bleeddamageimmunity`
      (Skill_Passive, `defensiveBleeding 100.0`) stays. The mod's marquee weapons
      are bleed spears; half this fight tells that build to sit down.
      HONEST: NOT a roster first - `um_helepolis_99` already carries the identical
      record. It is a first for a LIVING boss, and it is what makes beat 3 land.
    * ROOT-SNARE - `drx_earthbind` (Skill_AttackRadius, radius 22.0, cd 20).
      You do not kite this fight.
    * THE THICKET - `quillwards` (Skill_DefensiveWall, cd 20, spawns
      `pets\quillvine_12` on a 10->30s TTL ladder). **ZERO other uber in the mod
      fields a Skill_DefensiveWall.** It grows cover between you and it.
    * QUILL VOLLEY - `razorquill_megaburst` (Skill_AttackProjectileFan): the
      reach that makes the snare a threat instead of a nap.
    * RETINUE FROM ITS OWN FAMILY (the R-125 bar, satisfied literally): the
      donor's native `hero_quillvines` (Skill_SpawnPet) keeps firing, untouched.

  BEAT 2 - THE SPLITTING (`svc_bough_splitting`)
    A clone of `lowhealth_berserkerrage01` (Skill_PassiveOnLifeBuffSelf,
    `lifeMonitorPercent 33.0`, `skillActiveDuration 12.0`, cd 5.0) - it fires
    ITSELF at 33% life with zero AI wiring, the pattern `um_vashkarr_99` already
    ships. At the trigger the bark splits and the THORNS COME OUT: this lane
    moves the thorn coat onto the trigger record as `retaliationPierce`, so it is
    a phase-gated beat rather than a random cast (see CORRECTION 1).

  BEAT 3 - THE BOUGH IN BLOOM (phase 2, terminal, SV `hellflower.msh`, PLANT)
    The trunk bursts and amgoz1's OWN SV hellflower walks out of it. Slow
    physical/pierce zoning inverts into fast fire burst; SV's kit rides verbatim
    (`quilvine_barb`, `sv\hellflower\firedart`, `volcanicorb`, `flamesurge`) plus
    `razorquill_nova` (Skill_AttackProjectileRing) and the thorn coat.
    **BLEED IMMUNITY DOES NOT CARRY.** The wood was immune; the flower is not.
    The build you shelved in beat 1 comes back for the kill. That is the whole
    shape of the fight in one sentence.

  THE HANDBRIAR (Champion escort x2, `QuilVine01.msh`, PLANT)
    A ground-hugging whipping vine: maximum silhouette contrast against a
    2.8-scale trunk. That IS R-100 #18 ("they appear just like normal guys").

================================================================================
HOW IT SHIPS: ARZ-ONLY, IN PLACE, AT THE FROZEN RECORD PATHS
================================================================================
HARD CONSTRAINT from the order: the Golden Bough forecourt placement and its
spawn/proxy chain are REUSED. No map rebuild. `build_section_surgery.INJECT_SPECS`
places `q_goldenbough_lone` and `svc_charon_chest` BY NAME, so those names are
frozen. This module therefore REPLACES THE CONTENTS of the three monster records
the chain already names, rather than authoring new paths and repointing:

    um_charon_ferryman_99.dbr      <- xhero_strongbark_44   (Ormenos)
    um_charonform2_ferryman_99.dbr <- us_hellflower_37      (the Bloom)
    svc_charon_wraith_99.dbr       <- am_quillvine_35       (the Handbriar)

MEASURED reason this is the ONLY safe shape (not a preference - three hard-coded
gates key on those exact basenames, and authoring new paths reds all three):

  1. `tools/verify_soul_drop_rates.py` EXPECT pins
     `um_charonform2_ferryman_99 -> ('PLACED', 33.0)`. A new terminal at a new
     path leaves the old record un-PLACED, so its klass flips and the spot test
     fails.
  2. `tools/build_svc_database.py:SOUL_RATE_ZERO_PINS` pins the chain HEAD
     `um_charon_ferryman_99` at 0.
  3. `tools/patches/uber_quest_drops.LEAKS[0]` and
     `tools/patches/red_uber_orbs.EXEMPT` both key on the pair by path.

Monster record paths are NOT baked into TQ saves (only ITEM paths are), so
replacing their contents is save-safe. The names now lie; that is registered as
BACKLOG debt for a future breaking build, exactly as the item paths are.

================================================================================
CORRECTIONS TO THE RATIFIED SPEC - each one measured on the LIVE arz
(work/SoulvizierClassic/Database/SoulvizierClassic.arz, 51,253 records, build83)
================================================================================
1. CAST SLOTS: the spec allocated FOUR new casts on phase 1 and there are only
   THREE free. Measured on `xhero_strongbark_44`: `specialAttackSkillName` =
   `hero_ascacophus_stumpstomp` (chance 30) and `specialAttack3SkillName` =
   `hero_quillvines` (chance 70) are OCCUPIED - both are the donor's own-family
   signature, which the R-125 bar forbids displacing. The engine caps at five
   slots, so exactly `2`, `4`, `5` are free.
   RESOLUTION: earthbind / quillwards / megaburst take the three cast slots, and
   `typhon_thornyaura` is NOT cast by phase 1 at all - its retaliation is folded
   into `svc_bough_splitting`, so the thorns arrive WITH the splitting instead of
   on a random 20s roll. Strictly better design; costs nothing. The thorn coat
   still ships as a real cast on the BLOOM (a free slot exists there).

2. SKILL SLOTS: the spec said phase 1's donor "occupies 1-6, 10, 11, 12". It also
   occupies **15** (`elementalresistance_10xlevel`) and **17** (`racial_plant`).
   The spec separately claimed the donor "does NOT carry racial_plant as a skill" -
   it does, at `skillName17`. Nothing breaks: `_svc_add_skill` takes the first
   EMPTY slot, so the additions land on 7/8/9/13/14/16.

3. `boss_conversionimmunity` IS resolvable - `records\skills\boss skills\
   boss_conversionimmunity.dbr` exists and both shipped Charon forms carry it.
   The spec told the implementer to probe and skip it. It ships.
   Real paths, measured: `boss_scaling` = `records\skills\monster skills\
   passive_buffs\boss_scaling.dbr`; `all_hpscaling_passive` =
   `records\xpack\skills\bossskills\all_hpscaling_passive.dbr`.

4. **THE TERMINAL KEEPS `bosschest02_charon`, AND THIS IS A HARD GATE, NOT TASTE.**
   The spec's lore reading wants the Charon-named orb gone (b53 did exactly that
   for Dagon). MEASURED: `tools/svc_orb_breadth.py` sets `MIN_PROXIES = 6` /
   `MIN_TABLES = 18` and `orb_loot_breadth.apply` RAISES below either floor. That
   scope is DERIVED as "every proxy an UBER names", and
   `um_charonform2_ferryman_99` is the only uber naming `bosschest02_charon` - so
   retargeting it drops the scope to 5 proxies / 15 tables and REDS THE BUILD, and
   would additionally orphan three tables that `orb_loot_breadth` + `orb_armor_rows`
   already widened (the BL-R181-DEBT-7 ownership gate). The donor
   `us_hellflower_37` carries no `treasureProxyName`, so this module SETS it
   explicitly. Registered as `BL-BOUGH-DEBT-4`: the encounter still drops an orb
   whose shared base-game display string reads "Charon's Essence", and retargeting
   it needs a coordinated floor re-measure in its own wave.

5. `offensiveTrapMin/Max` (the spec's "you start rooting what you hit") is carried
   by **ZERO** of the 2,095 soul records in the DB and by only 32 records DB-wide -
   it is not part of the soul template's shape. The field that IS
   (2,095 souls carry it) and that means the same thing is
   `offensiveSlowPhysicalMin` + `offensiveSlowPhysicalDurationMin`. That ships
   instead, with the amgoz1-tradition downside (negative `characterRunSpeed`,
   2,158 souls carry the field) intact.

6. b86 SOUL-RENAME ROW 7 STANDS - NO SUPERSEDE WAS NEEDED. Verified in
   `docs/SOUL_RENAME_PROPOSAL.md`: row 7 governs `tagSoulSVC9005` on
   `records\item\equipmentring\soul\svc_uber\boss_charon_soul_{n,e,l}.dbr`, the
   GENERATED soul of the BASE-GAME `boss_charon_{39,41,43}`. Our uber's soul is
   `...\svc_uber\ferryman_soul_{n,e,l}.dbr` on `tagSVCSoulFerryman`. Different
   record, different tag; they never collided. Our uber vacating the ferryman
   display namespace entirely STRENGTHENS row 7's primary. b86 ships row 7
   unchanged. (WILL_RULINGS R-231-C records this so it cannot be re-litigated.)

7. THE LIVE DEFECT NOBODY FILED: the shipped Champion escort
   `svc_charon_wraith_99` has `characterLife = [878.0, 300.0, 400.0]` - life FALLS
   from Normal to Epic. That is R-100 #18 as a measurable field. It dies with this
   wave and `verify()` carries a strictly-ascending gate so it cannot come back.

================================================================================
CRASH-LAW COMPLIANCE, ITEMISED
================================================================================
* FX via MONSTER-RECORD FIELDS ONLY (`spawnEffect` / `deathEffect`); all four
  targets verified `Class == EffectEntity` in the arz. This module authors NO
  `charFxPak*` anywhere, and `verify()` fails if any `Skill_SpawnPet` we reference
  grew `charFxPakSelfNames`. The one charFxPak in play
  (`Typhon_Thorn_CharFXPak`, inside the base `typhon_thornyaura` record) is
  referenced and never mutated.
* NO `clone_record` FOR SOULS - `_create_soul` / `_ensure_record` only. Monsters
  may clone (the `mnemophage_mindshroud` precedent).
* NO Monster.tpl -> Pet.tpl equipment copy - `_build_boss_summon` with
  `loadout=None` (correct: a flower equips nothing).
* PERMANENT PET TTL = `[]` - the Lyia baseline carries none; `verify()` asserts it.
* A9 RENDER CHAIN - every form clones the donor that OWNS its rig. NO cross-rig
  mesh swap and NO new art: each mesh/texture already has live carriers.
  Correction to the spec: `xhero_strongbark_44` declares **752** animation fields,
  not zero - which is exactly why cloning it wholesale is safe (the full anim
  table comes with the clone, so the B-SOUL-PROC-2 class cannot arise).
* SOUL-LEAK INVARIANT - **both** donors ship `chanceToEquipFinger2 = 33.0` with
  their OWN soul in `lootFinger2Item1` (`strongbark_soul_*`, `hellflower_soul_*`).
  A raw clone therefore inherits a FOREIGN soul drop (the R-42/R-106 class).
  `_svc_clear_soul_loot` runs on all three BEFORE `_create_soul` rewires the Bloom.

ORDERING: registered immediately AFTER `uber_quest_drops` and BEFORE every
breadth/derivation module (`chest_loot_breadth`, `armor_loot_breadth`,
`red_uber_orbs`, `orb_loot_breadth`, `orb_armor_rows`), so those derive their
scope from the FINAL records at apply() AND verify() time and cannot disagree.
`uber_quest_markers` (earlier) writes `DisplayAsQuestItem` on these records and
its verify() re-derives on the final db, so this module re-asserts that field
explicitly after the re-clone.

NAMES ARE THIS LANE'S INVENTION AND SHIP AS DEFAULTS FLAGGED FOR WILL VETO
(the standing creative-bar rule, R-125 precedent).
"""
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parents[1]          # tools/
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import apply_svc_patches as asp                       # noqa: E402
from apply_svc_patches import (                       # noqa: E402
    DATA_TYPE_FLOAT, DATA_TYPE_INT, DATA_TYPE_STRING,
    _bmp, _build_boss_summon, _create_soul, _svc_add_skill,
    _svc_clear_soul_loot, _svc_guarantee_unique,
)

MODULE_NAME = ("Golden Bough uber rework (Will 2026-08-11): Charon out, "
               "Ormenos the Gilded Root in - arz-only, frozen proxy chain")

S, F, I = DATA_TYPE_STRING, DATA_TYPE_FLOAT, DATA_TYPE_INT

# ── FROZEN PATHS (the map places these by name; see the header) ──────────────
_CH = r'records\xpack\creatures\monster\bosses\02_charon'
_ORM = _CH + r'\um_charon_ferryman_99.dbr'          # LEGACY PATH: phase 1
_BLOOM = _CH + r'\um_charonform2_ferryman_99.dbr'   # LEGACY PATH: phase 2, terminal
_BRIAR = _CH + r'\svc_charon_wraith_99.dbr'         # LEGACY PATH: Champion escort

_POOL = r'records\drxmap\proxy\pools\q_goldenbough_lone.dbr'
_PROXY = r'records\drxmap\proxy\q_goldenbough_lone.dbr'
_YARD_POOL = r'records\drxmap\proxy\pools\q_yard_goldenbough.dbr'
_YARD_PROXY = r'records\drxmap\proxy\q_yard_goldenbough.dbr'
_WORLD_CHEST = r'records\drxmap\proxy\svc_charon_chest.dbr'
_HOARD = [r'records\drxitem\container\svc_charonhoard_%s.dbr' % t
          for t in ('01', '02', '03')]

_AMULET = [r'records\item\equipmentamulet\svc_goldenbough_%s.dbr' % t
           for t in ('n', 'e', 'l')]
_SUMMON = r'records\skills\soulskills\summon_charon_oarsman.dbr'
_PETS = [r'records\skills\soulskills\pets\charon_oarsman_%d.dbr' % i
         for i in (1, 2, 3)]
_SOUL_BASENAME = 'ferryman'      # LEGACY PATH, frozen for save-compat (TQ bakes
                                 # item paths at pickup; renaming orphans looted souls)
_SOUL_TIERS = [r'records\item\equipmentring\soul\svc_uber\%s_soul_%s.dbr'
               % (_SOUL_BASENAME, t) for t in ('n', 'e', 'l')]

# ── DONORS (each OWNS the rig its clone renders on - no cross-rig swap) ──────
_D_ORM = r'records\xpack\creatures\monster\ascacophus\xhero_strongbark_44.dbr'
_D_BLOOM = r'records\creature\monster\quilvine\us_hellflower_37.dbr'
_D_BRIAR = r'records\creature\monster\quilvine\am_quillvine_35.dbr'
_D_SPLIT = r'records\skills\monster skills\lowhealth_berserkerrage01.dbr'

_SPLIT = r'records\skills\monster skills\lowhealth\svc_bough_splitting.dbr'

# ── SKILLS (Class verified in the arz; see the header table) ─────────────────
_SK_EARTHBIND = r'records\skills\nature\drx_earthbind.dbr'                 # Skill_AttackRadius r22 cd20
_SK_QUILLWARDS = r'records\skills\monster skills\summoning_pets\quillwards.dbr'  # Skill_DefensiveWall cd20
_SK_THORNYAURA = r'records\skills\boss skills\typhon_thornyaura.dbr'       # Skill_BuffSelfDuration 6.5s
_SK_MEGABURST = (r'records\skills\monster skills\attack_projectile'
                 r'\razorquill_megaburst.dbr')                             # Skill_AttackProjectileFan
_SK_NOVA = r'records\skills\monster skills\attack_radius\razorquill_nova.dbr'  # Skill_AttackProjectileRing
_SK_BOSS_SCALING = r'records\skills\monster skills\passive_buffs\boss_scaling.dbr'
_SK_HERO_SCALING = r'records\skills\monster skills\passive_buffs\hero_scaling.dbr'
_SK_HPSCALING = r'records\xpack\skills\bossskills\all_hpscaling_passive.dbr'
_SK_CONVIMMUNE = r'records\skills\boss skills\boss_conversionimmunity.dbr'
_SK_HEART_OF_OAK = r'records\skills\nature\drxheartofoak.dbr'              # Skill_BuffRadiusToggled
_SK_PLAGUE = r'records\skills\nature\drxplague.dbr'                        # Skill_AttackBuff

# ── FX: monster-record fields ONLY. All four verified Class == EffectEntity ──
_FX = r'records\xpack\effects\particles\creature'
_FX_ORM_SPAWN = _FX + r'\ascacophus2_ambientfx.dbr'
_FX_ORM_DEATH = _FX + r'\ascacophus2_deathfx.dbr'      # the trunk bursting = the phase turn
_FX_BLOOM_SPAWN = _FX + r'\ascacophus_ambientfx.dbr'
_FX_BLOOM_DEATH = _FX + r'\ascacophus_deathfx.dbr'

_ORB = r'records\xpack\item\containers\proxies\bosschest02_charon.dbr'   # see CORRECTION 4

# ── MESHES (per-rig; each is its own donor's, so A9 is satisfied by construction)
_MESH_ORM = r'XPack\Creatures\Monster\Ascacophus\Ascacophus02.msh'
_MESH_BLOOM = r'SVMesh/meshes/hellflower.msh'
_MESH_BRIAR = r'Creatures\Monster\QuilVine\QuilVine01.msh'
_SKIN_ORM = r'XPack\Creatures\Monster\Ascacophus\Ascacophus01B.tex'      # donor's own, 3 live carriers
# WILL-DECISION 3, shipped OFF: the DRX dead-trunk skin has ONE live baseTexture
# carrier and `ascacophus_evil.tex` has 3 but on Ascacophus01.msh, NOT 02 -
# cross-mesh UV is the 343_dark_smoke / Vort-green trap. TESTHUB-verify first.
_ORM_SKIN_ALT = r'DRXtextures\creatures\ascacophus\ascacophus_deadtrunk.tex'
_ORM_USE_SKIN_ALT = False

# ── THE NUMBERS ─────────────────────────────────────────────────────────────
_BAND = [48, 72, 100]
# Life is EXACT PARITY with the two shipped Charon forms - deliberately zero
# balance drift, so the vet's only job this wave is identity, not numbers.
# Frame of reference: docs/reports/gaoler_variance_rca.md - the Gaoler is
# 15,000/20,000/27,000 + 11,000/15,000/20,000 across two forms (35,000 on Epic
# with a six-strong guard horde) and Will beat him on the second attempt. This
# encounter sits at 28,000 + 30,000 = 58,000 on Epic with two Champions: inside
# the killable-uber band, a hard fight, and - unlike the Gaoler - it has no
# racial pet-damage reduction and no life-drain cascade, which is where the
# Gaoler's real wall came from. No walls; the wall in this fight is literal and
# made of quillvines.
_ORM_LIFE = [22000.0, 28000.0, 34000.0]
_BLOOM_LIFE = [24000.0, 30000.0, 36000.0]
# WILL-DECISION 2: ship 2.8 / 2.0; TESTHUB yard sweep 3.1 and 3.4 before the
# canonical placement is blessed. Measured live scale ranges on the exact rigs:
# Ascacophus02.msh 1.15..1.80 (max = kaets.dbr); hellflower.msh 1.50 on all 4
# carriers. Large scales DO work here (um_polisgaoler_99 ships Gigantes02 at 3.5,
# um_vashkarr_99 at 3.0) so the risk is footprint/clearance, not the renderer.
_ORM_SCALE = 2.8
_BLOOM_SCALE = 2.0
_BRIAR_SCALE = 1.55
# THE R-100 #18 FIX, and the anti-regression gate's reason to exist: the shipped
# escort was [878.0, 300.0, 400.0] - life FALLING from Normal to Epic.
_BRIAR_LIFE = [4200.0, 5800.0, 7600.0]

# `actorHeight` is a per-RIG constant, inherited, NEVER invented (R-126, measured
# over 2,122 rigs). Ascacophus02 = 0.0 on all 4 live carriers; hellflower.msh and
# QuilVine01.msh = 1.0. This module NEVER writes the field; verify() proves it.
_RIG_ACTOR_HEIGHT = {_ORM: 0.0, _BLOOM: 1.0, _BRIAR: 1.0}

# ── TAGS ────────────────────────────────────────────────────────────────────
# KEYS KEPT wherever a key already exists (nothing referenced is retired, so
# validate_tags cannot be handed an orphan); exactly ONE new key is minted, and
# it fixes a real defect: the two shipped forms SHARED one display tag, so the
# phase turn had no name change at all.
_TAG_ORM = 'tagSVCMonsterCharonFerryman'        # KEY KEPT, string rewritten
_TAG_BLOOM = 'tagSVCMonsterOrmenosBloom'        # MINTED (the two forms now differ)
_TAG_BRIAR = 'tagSVCMonsterCharonWraith'        # KEY KEPT, string rewritten
_TAG_HOARD = 'tagSVCCharonHoard'                # KEY KEPT, string rewritten
_TAG_SOUL = 'tagSVCSoulFerryman'                # KEY KEPT (in _HAND_DESIGNED_SOUL_TAGS)
_TAG_SUMMON = 'tagSVCSummonCharonOarsman'       # KEY KEPT, string rewritten
_TAG_PET = 'tagSVCPetOarsman'                   # KEY KEPT, string rewritten
_TAG_AMULET = 'tagSVCitmGoldenBough'            # UNCHANGED
_TAG_AMULET_DESC = 'tagSVCitmGoldenBoughDESC'   # rewritten

_REQUIRED_DONORS = (_D_ORM, _D_BLOOM, _D_BRIAR, _D_SPLIT)
_REQUIRED_SKILLS = (_SK_EARTHBIND, _SK_QUILLWARDS, _SK_THORNYAURA, _SK_MEGABURST,
                    _SK_NOVA, _SK_BOSS_SCALING, _SK_HPSCALING, _SK_CONVIMMUNE,
                    _SK_HEART_OF_OAK, _SK_PLAGUE)
_REQUIRED_FX = (_FX_ORM_SPAWN, _FX_ORM_DEATH, _FX_BLOOM_SPAWN, _FX_BLOOM_DEATH)

# Populated by apply(); read by verify() so the gate proves the ACTUAL writes.
_TOUCHED = set()


# ── helpers ─────────────────────────────────────────────────────────────────
def _n(s):
    return str(s).replace('/', '\\').strip().lower() if s else ''


def _one(db, rec, field):
    v = db.get_field_value(rec, field)
    return v[0] if isinstance(v, list) else v


def _replace_record(db, donor, dest):
    """clone donor -> dest, SAFELY, over an existing record.

    `ArzDatabase.clone_record` only deep-copies the decoded field map when the
    SOURCE is already in `_decoded_cache`; otherwise it rewires the raw blob and
    leaves any STALE `_decoded_cache[dest]` in place, so the very next
    `get_fields(dest)` would hand back the OLD record's fields and every write
    below would land on Charon. Forcing the source to decode first makes the
    deep-copy branch the only branch taken. Then prove it landed.
    """
    db.get_fields(donor)                      # guarantee source is cached
    db.clone_record(donor, dest)
    db._decoded_cache.pop(dest, None)         # belt AND braces: force a re-read
    got, want = _n(_one(db, dest, 'mesh')), _n(_one(db, donor, 'mesh'))
    if got != want:
        raise SystemExit(
            "charon_rework: clone of %s -> %s did not land (mesh %r, expected "
            "%r). The arz clone/cache seam moved; stop and re-measure."
            % (donor, dest, got, want))
    _TOUCHED.add(_n(dest))
    return dest


def _sf(db, rec, field, value, dtype=None):
    """set_field with the dtype-preservation law: NEVER pass an explicit dtype on
    a field the clone already carries (INT/FLOAT corruption silently zeroes it).
    An explicit dtype is passed ONLY when the field is genuinely absent."""
    if dtype is not None and db.get_field_value(rec, field) is None:
        db.set_field(rec, field, value, dtype)
    else:
        db.set_field(rec, field, value)
    _TOUCHED.add(_n(rec))


def _cast(db, rec, suffix, skill, chance, rng, delay, timeout):
    """Wire one AI cast slot. suffix '' = specialAttackSkillName (slot 1)."""
    _sf(db, rec, 'specialAttack%sSkillName' % suffix, skill, S)
    _sf(db, rec, 'specialAttack%sChance' % suffix, float(chance), F)
    _sf(db, rec, 'specialAttack%sRange' % suffix, rng, S)
    _sf(db, rec, 'specialAttack%sDelay' % suffix, float(delay), F)
    _sf(db, rec, 'specialAttack%sTimeout' % suffix, float(timeout), F)


def _free_cast_slots(db, rec):
    """The cast slots with no SkillName. The engine caps at five: '', 2, 3, 4, 5."""
    out = []
    for sfx in ('', '2', '3', '4', '5'):
        v = _one(db, rec, 'specialAttack%sSkillName' % sfx)
        if not (isinstance(v, str) and v.strip()):
            out.append(sfx)
    return out


# ── apply ───────────────────────────────────────────────────────────────────
def apply(db, tags):
    _TOUCHED.clear()

    missing = [p for p in (_REQUIRED_DONORS + _REQUIRED_SKILLS + _REQUIRED_FX
                           + (_ORM, _BLOOM, _BRIAR, _POOL, _PROXY,
                              _YARD_POOL, _YARD_PROXY, _ORB))
               if not db.has_record(p)]
    if missing:
        raise SystemExit(
            "charon_rework: %d required record(s) absent from the DB - this "
            "module rewrites an EXISTING encounter in place, so a missing "
            "donor/skill/FX/anchor means the roster moved and the design must be "
            "re-measured, never silently degraded:\n  %s"
            % (len(missing), "\n  ".join(missing)))

    # ── BEAT 2 SKILL: the self-firing splitting, with the thorns folded in ───
    _replace_record(db, _D_SPLIT, _SPLIT)
    _sf(db, _SPLIT, 'FileDescription',
        'Ormenos: THE SPLITTING - at 33% life the bark comes apart and the '
        'thorns come out (Skill_PassiveOnLifeBuffSelf, self-firing, no AI wiring)')
    _sf(db, _SPLIT, 'lifeMonitorPercent', 33.0)
    _sf(db, _SPLIT, 'skillActiveDuration', 12.0)
    _sf(db, _SPLIT, 'skillCooldownTime', 5.0)
    # CORRECTION 1: the thorn coat lives HERE, not on a random 20s cast roll.
    # Scalars (level-independent) so the wired skillLevel cannot mis-index.
    _sf(db, _SPLIT, 'retaliationPierceMin', 180.0)
    _sf(db, _SPLIT, 'retaliationPierceMax', 260.0)

    # ── BEAT 1: ORMENOS, THE GILDED ROOT (phase 1, the placed head) ─────────
    _replace_record(db, _D_ORM, _ORM)
    _sf(db, _ORM, 'monsterClassification', 'Boss')
    _sf(db, _ORM, 'description', _TAG_ORM)
    _sf(db, _ORM, 'charLevel', list(_BAND))
    _sf(db, _ORM, 'characterLife', list(_ORM_LIFE))
    _sf(db, _ORM, 'scale', _ORM_SCALE)
    # actorHeight DELIBERATELY NOT WRITTEN (R-126: per-rig constant, inherited).
    _sf(db, _ORM, 'defensiveLife', 100.0, F)
    _sf(db, _ORM, 'defensivePierce', 50.0, F)
    _sf(db, _ORM, 'defensivePhysical', 30.0, F)
    _sf(db, _ORM, 'defensivePoison', 60.0, F)
    _sf(db, _ORM, 'actorToSpawnOnDeath', _BLOOM, S)
    _sf(db, _ORM, 'spawnEffect', _FX_ORM_SPAWN, S)
    _sf(db, _ORM, 'deathEffect', _FX_ORM_DEATH, S)
    if _ORM_USE_SKIN_ALT:
        _sf(db, _ORM, 'baseTexture', _ORM_SKIN_ALT)
    # SOUL-LEAK INVARIANT: the donor ships its OWN soul at 33% (R-42/R-106 class).
    _svc_clear_soul_loot(db, _ORM)
    _TOUCHED.add(_n(_ORM))
    # hero -> boss scaling (in place; do NOT add a second scaler)
    _sf(db, _ORM, 'skillName12', _SK_BOSS_SCALING)
    for _sk, _lvl in ((_SK_EARTHBIND, 8), (_SK_QUILLWARDS, 8),
                      (_SK_MEGABURST, 8), (_SK_HPSCALING, 1),
                      (_SK_CONVIMMUNE, 1), (_SPLIT, 10)):
        if not _svc_add_skill(db, _ORM, _sk, _lvl):
            raise SystemExit("charon_rework: no free skillName slot on %s for %s"
                             % (_ORM, _sk))
    # CORRECTION 1: exactly three cast slots are free ('2', '4', '5'); slot 1
    # (stumpstomp) and slot 3 (hero_quillvines) are the donor's own-family
    # signature and the R-125 bar forbids displacing them.
    _free = _free_cast_slots(db, _ORM)
    for _want in ('2', '4', '5'):
        if _want not in _free:
            raise SystemExit(
                "charon_rework: cast slot %r on %s is NOT free (free: %r). The "
                "donor's rotation moved; re-measure before displacing anything - "
                "slots 1 and 3 are its own-family signature (R-125)."
                % (_want, _ORM, _free))
    _cast(db, _ORM, '2', _SK_EARTHBIND, 18.0, 'MediumRange', 6.0, 4.0)
    _cast(db, _ORM, '4', _SK_QUILLWARDS, 15.0, 'ShortRange', 10.0, 6.0)
    _cast(db, _ORM, '5', _SK_MEGABURST, 22.0, 'LongRange', 6.0, 3.0)

    # ── BEAT 3: ORMENOS, THE BOUGH IN BLOOM (phase 2, terminal) ─────────────
    _replace_record(db, _D_BLOOM, _BLOOM)
    _sf(db, _BLOOM, 'monsterClassification', 'Boss')
    _sf(db, _BLOOM, 'description', _TAG_BLOOM)
    _sf(db, _BLOOM, 'charLevel', list(_BAND))
    _sf(db, _BLOOM, 'characterLife', list(_BLOOM_LIFE))
    _sf(db, _BLOOM, 'scale', _BLOOM_SCALE)
    _sf(db, _BLOOM, 'defensiveLife', 100.0, F)
    _sf(db, _BLOOM, 'defensivePierce', 50.0, F)
    _sf(db, _BLOOM, 'defensivePhysical', 30.0, F)
    _sf(db, _BLOOM, 'defensiveFire', 60.0, F)
    # BLEED IMMUNITY DELIBERATELY DOES NOT CARRY - that is the fight's shape.
    _sf(db, _BLOOM, 'actorToSpawnOnDeath', '', S)          # terminal
    _sf(db, _BLOOM, 'spawnEffect', _FX_BLOOM_SPAWN, S)
    _sf(db, _BLOOM, 'deathEffect', _FX_BLOOM_DEATH, S)
    _sf(db, _BLOOM, 'treasureProxyName', _ORB, S)          # CORRECTION 4 (hard gate)
    _svc_clear_soul_loot(db, _BLOOM)                       # before _create_soul rewires
    _sf(db, _BLOOM, 'skillName12', _SK_BOSS_SCALING)
    for _sk, _lvl in ((_SK_NOVA, 8), (_SK_THORNYAURA, 8),
                      (_SK_HPSCALING, 1), (_SK_CONVIMMUNE, 1)):
        if not _svc_add_skill(db, _BLOOM, _sk, _lvl):
            raise SystemExit("charon_rework: no free skillName slot on %s for %s"
                             % (_BLOOM, _sk))
    _free = _free_cast_slots(db, _BLOOM)
    for _want in ('4', '5'):
        if _want not in _free:
            raise SystemExit(
                "charon_rework: cast slot %r on %s is NOT free (free: %r); SV's "
                "own firedart/volcanicorb/flamesurge rotation is kept verbatim "
                "and must not be displaced." % (_want, _BLOOM, _free))
    _cast(db, _BLOOM, '4', _SK_NOVA, 25.0, 'ShortRange', 5.0, 3.0)
    _cast(db, _BLOOM, '5', _SK_THORNYAURA, 15.0, 'AnyRange', 12.0, 8.0)

    # ── THE HANDBRIAR (Champion escort x2) - the R-100 #18 fix ──────────────
    _replace_record(db, _D_BRIAR, _BRIAR)
    _sf(db, _BRIAR, 'monsterClassification', 'Champion', S)   # donor has NO such field
    _sf(db, _BRIAR, 'description', _TAG_BRIAR)
    _sf(db, _BRIAR, 'charLevel', list(_BAND))
    _sf(db, _BRIAR, 'characterLife', list(_BRIAR_LIFE))       # explicit ASCENDING
    _sf(db, _BRIAR, 'scale', _BRIAR_SCALE)
    _sf(db, _BRIAR, 'handHitDamageMin', 180.0)
    _sf(db, _BRIAR, 'handHitDamageMax', 240.0)
    _sf(db, _BRIAR, 'defensivePierce', 25.0, F)
    _sf(db, _BRIAR, 'defensiveBleeding', 50.0, F)
    _sf(db, _BRIAR, 'defensivePoison', 40.0, F)
    # R-125 minion law: a placed add can never become a loot faucet, can never
    # pay a soul (R-42/R-106) and can never enter the uber_quest_markers roster.
    _svc_clear_soul_loot(db, _BRIAR)
    _sf(db, _BRIAR, 'dropItems', 0)
    _sf(db, _BRIAR, 'chanceToEquipMisc1', 0.0)   # donor's act-3 relic table, muted
    _sf(db, _BRIAR, 'DisplayAsQuestItem', 0)
    if not _svc_add_skill(db, _BRIAR, _SK_HPSCALING, 1):
        raise SystemExit("charon_rework: no free skillName slot on %s" % _BRIAR)

    # ── uber_quest_markers (registry index 43) writes DisplayAsQuestItem on
    #    these records and its verify() RE-DERIVES on the final db. The re-clone
    #    above reset the field to the donor's value, so re-assert it here.
    _sf(db, _ORM, 'DisplayAsQuestItem', 1)
    _sf(db, _BLOOM, 'DisplayAsQuestItem', 1)

    # ── THE PROXY CHAIN: REUSED, never rebuilt (arz-only; no map rebuild) ────
    for pool, desc in ((_POOL, 'Ormenos, the Gilded Root (main) + 2 Handbriar '
                               'champion escorts'),
                       (_YARD_POOL, 'YARD: Ormenos + 2 Handbriars @100% '
                                    '(TESTHUB-only, never uploaded)')):
        _sf(db, pool, 'FileDescription', desc)
        for f in ('name1', 'name2', 'name3'):
            _sf(db, pool, f, _ORM)
        for f in ('nameChampion1', 'nameChampion2'):
            _sf(db, pool, f, _BRIAR)
    for proxy in (_PROXY, _YARD_PROXY):
        _sf(db, proxy, 'mesh', _MESH_ORM)
        _sf(db, proxy, 'scale', _ORM_SCALE)

    for entry in asp._MOD_AUTHORED_SPAWN_PROXIES:
        if _n(entry.get('proxy')) == _n(_PROXY):
            entry['main_monster'] = _ORM
            entry['name'] = 'q_goldenbough_lone (Ormenos + 2 Handbriar escorts)'
        elif _n(entry.get('proxy')) == _n(_YARD_PROXY):
            entry['main_monster'] = _ORM
            entry['name'] = 'q_yard_goldenbough (TESTHUB yard)'

    # ── REWARD 1: THE GOLDEN BOUGH, still guaranteed off the terminal ────────
    # `_svc_guarantee_unique` IGNORES its loot_name argument and writes
    # lootMisc{n}Item1 + chanceToEquipMisc{n}=100 straight onto the monster; the
    # `goldenbough_guaranteed.dbr` loot table the old call named DOES NOT EXIST
    # in the arz and never did. Pass None. The donor leaves Misc4 free, so this
    # lands on Misc4 exactly as the shipped encounter did.
    _svc_guarantee_unique(db, _BLOOM, list(_AMULET), None)
    _TOUCHED.add(_n(_BLOOM))

    # ── REWARD 2: THE HOARD - ONE chest. R-108 cut it 3 -> 1 in answer to Will's
    #    OWN R-100 #10 complaint about THIS boss ("the uber monster soul of the
    #    unferried also had three chests"). Chain frozen, loot band untouched
    #    (apply_svc_patches L16948 'svc_charonhoard' keys on the frozen prefix and
    #    needs no change - verify() proves that rather than assuming it).

    # ── REWARD 3: THE SOUL - {^F}Soul of the Gilded Root ─────────────────────
    def _stats(t):
        m = {'n': 0.55, 'e': 0.78, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)                                # noqa: E731
        return {
            **_bmp(t),
            # manual-cast summon grant: NO itemSkillAutoController (D19/D21 law)
            'itemSkillName': (S, _SUMMON),
            'itemSkillLevel': (I, {'n': 1, 'e': 2, 'l': 3}[t]),
            'augmentSkillName1': (S, _SK_HEART_OF_OAK),
            'augmentSkillLevel1': (I, {'n': 3, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _SK_PLAGUE),
            'augmentSkillLevel2': (I, {'n': 2, 'e': 3, 'l': 4}[t]),
            # re-themed off the old cold/vitality soul onto fire + pierce
            'offensiveFireMin': (F, r(64.0)), 'offensiveFireMax': (F, r(102.0)),
            'offensiveFireModifier': (F, r(20.0)),
            'offensivePierceMin': (F, r(48.0)), 'offensivePierceMax': (F, r(78.0)),
            'offensivePierceRatioMin': (F, r(18.0)),
            'retaliationPierceMin': (F, r(70.0)), 'retaliationPierceMax': (F, r(110.0)),
            # THE ONE WEIRD STAT (CORRECTION 5): the boss's own signature as a
            # player stat - the ground takes hold of whatever you strike.
            # `offensiveSlowPhysical*` is the field 2,095 souls actually carry;
            # `offensiveTrapMin` is carried by ZERO of them.
            'offensiveSlowPhysicalMin': (F, r(40.0)),
            'offensiveSlowPhysicalDurationMin': (F, 3.0),
            # ...and the amgoz1 downside, in the Tantalus/Ephialtes tradition:
            # the root takes a little hold of you as well.
            'characterRunSpeed': (F, {'n': -8.0, 'e': -6.0, 'l': -5.0}[t]),
            'characterLife': (F, r(220.0)), 'characterLifeModifier': (F, r(15.0)),
            'characterDefensiveAbility': (F, r(80.0)),
            'defensiveBleeding': (F, r(35.0)),      # the wood's gift
            'defensiveFire': (F, r(30.0)), 'defensiveLife': (F, r(30.0)),
        }

    tiers = [{'diff': t, 'itemLevel': il, 'stats': _stats(t)}
             for t, il in (('n', 48), ('e', 72), ('l', 100))]
    soul_paths = _create_soul(db, _SOUL_BASENAME, _TAG_SOUL, tiers,
                              monster=_BLOOM, drop_rate=66.0)
    for p in soul_paths:
        db.set_field(p, 'FileDescription', 'Hades')
        db._modified.add(p)
        _TOUCHED.add(_n(p))
    # The chain HEAD names OUR soul at chance 0 (it never pays; the terminal
    # does). Strictly cleaner than the shipped shape, where the head named a
    # DIFFERENT soul at 0, and it keeps the record inside verify_soul_drop_rates'
    # index where SOUL_RATE_ZERO_PINS expects to find it at 0.0.
    _sf(db, _ORM, 'lootFinger2Item1', list(soul_paths))
    _sf(db, _ORM, 'chanceToEquipFinger2', 0.0)

    # ── THE SUMMON: same species as the dropper -> the F2 identity gate goes
    #    GREEN WITH NO EXEMPTION, so a sanctioned workaround is RETIRED rather
    #    than carried. The gate compares the SOURCE's mesh to the DROPPER's mesh;
    #    both are now SVMesh/meshes/hellflower.msh.
    _build_boss_summon(
        db, _D_BLOOM, _PETS, _SUMMON, _TAG_SUMMON, _TAG_PET,
        char_level=list(_BAND), life=[5500.0, 8000.0, 11000.0],
        life_regen=[18.0, 36.0, 60.0], dmg_min=[42.0, 72.0, 108.0],
        dmg_max=[66.0, 110.0, 160.0], scale=1.4, loadout=None)
    for p in _PETS + [_SUMMON]:
        _TOUCHED.add(_n(p))
    # The source entry is DELETED in apply_svc_patches by this wave; this pop is
    # the idempotent belt-and-braces so a stale entry can never re-exempt us.
    asp._SUMMON_IDENTITY_ALLOW.pop('ferryman', None)

    # ── TAGS (arz + Text are a COUPLED deploy; validate_tags is a build gate) ─
    tags[_TAG_ORM] = '{^r}Ormenos, the Gilded Root'
    tags[_TAG_BLOOM] = '{^r}Ormenos, the Bough in Bloom'
    tags[_TAG_BRIAR] = '{^G}Handbriar'
    tags[_TAG_HOARD] = 'The Orchard of Hands'
    tags[_TAG_AMULET] = 'The Golden Bough'
    tags[_TAG_AMULET_DESC] = (
        'The tree grew it and would not let it go. Cut it while it still burned, '
        'and the wood it came off is still standing at the shrine with every hand '
        'that tried before yours grown into it.')
    tags[_TAG_SOUL] = '{^F}Soul of the Gilded Root'
    tags[_TAG_SOUL + 'DESC'] = (
        'It never chased anything. It grew where it stood and waited for hands. '
        'Carry its soul and the ground takes hold of whatever you strike, and '
        'takes a little hold of you as well.')
    tags[_TAG_SUMMON] = 'Graft the Gilded Bloom'
    tags[_TAG_SUMMON + 'DESC'] = (
        'The bough that burns is the part of the tree that is still hungry. Speak '
        'its soul and a cutting takes root beside you, opens, and burns for you '
        'until something puts it out.')
    tags[_TAG_PET] = 'Gilded Bloom'

    print("  charon_rework: Charon is OUT of the Golden Bough forecourt. "
          "ORMENOS, THE GILDED ROOT [%s] (Plant, Ascacophus02 @%.1f, bleed-immune, "
          "root-snare + the mod's ONLY Skill_DefensiveWall + quill fan, splits at "
          "33%%) -> THE BOUGH IN BLOOM [%s] (Plant, SV hellflower @%.1f, fire "
          "burst + petal ring, NOT bleed-immune) + 2 Handbriar champions "
          "[%s, ascending]; proxy chain REUSED (no map rebuild); Golden Bough "
          "Misc4 100%%, one hoard chest, soul re-identified; "
          "_SUMMON_IDENTITY_ALLOW['ferryman'] RETIRED; %d record(s) written."
          % (_ORM_LIFE, _ORM_SCALE, _BLOOM_LIFE, _BLOOM_SCALE, _BRIAR_LIFE,
             len(_TOUCHED)))


# ── verify: THE GATE (post-finalization, reads the FINAL assembled db) ──────
def verify(db, tags):
    problems = []

    def gv(rec, field):
        return _one(db, rec, field)

    def resolves(path):
        if not isinstance(path, str) or not path.strip():
            return False
        if db.has_record(path):
            return True
        low = _n(path)
        return any(_n(n) == low for n in db.record_names())

    # ---- 1. THE PROXY CHAIN RESOLVES END TO END (the hard constraint) ------
    for proxy, pool, label in ((_PROXY, _POOL, 'canonical forecourt'),
                               (_YARD_PROXY, _YARD_POOL, 'TESTHUB yard')):
        if not db.has_record(proxy) or not db.has_record(pool):
            problems.append("%s: proxy/pool missing (%s / %s)" % (label, proxy, pool))
            continue
        if _n(gv(proxy, 'pool1')) != _n(pool):
            problems.append("%s: proxy pool1=%r, expected %s"
                            % (label, gv(proxy, 'pool1'), pool))
        for f in ('name1', 'name2', 'name3'):
            if _n(gv(pool, f)) != _n(_ORM):
                problems.append("%s: pool %s=%r, expected the reworked main "
                                "monster %s - the placed encounter would still "
                                "spawn the retired boss."
                                % (label, f, gv(pool, f), _ORM))
        for f in ('nameChampion1', 'nameChampion2'):
            if _n(gv(pool, f)) != _n(_BRIAR):
                problems.append("%s: pool %s=%r, expected %s"
                                % (label, f, gv(pool, f), _BRIAR))
        if _n(gv(proxy, 'mesh')) != _n(_MESH_ORM):
            problems.append("%s: proxy preview mesh=%r, expected %s (the world "
                            "preview would still show Charon)"
                            % (label, gv(proxy, 'mesh'), _MESH_ORM))
        if abs(float(gv(proxy, 'scale') or 0) - _ORM_SCALE) > 1e-4:
            problems.append("%s: proxy scale=%r, expected %s"
                            % (label, gv(proxy, 'scale'), _ORM_SCALE))
    if _n(gv(_ORM, 'actorToSpawnOnDeath')) != _n(_BLOOM):
        problems.append("phase link broken: %s actorToSpawnOnDeath=%r, expected %s"
                        % (_ORM, gv(_ORM, 'actorToSpawnOnDeath'), _BLOOM))
    if str(gv(_BLOOM, 'actorToSpawnOnDeath') or '').strip():
        problems.append("%s must be TERMINAL but actorToSpawnOnDeath=%r"
                        % (_BLOOM, gv(_BLOOM, 'actorToSpawnOnDeath')))

    # ---- 2. THE THREE GUARANTEED REWARDS ARE WIRED -------------------------
    slot = None
    for nsl in (3, 4, 5, 6):
        v = db.get_field_value(_BLOOM, 'lootMisc%dItem1' % nsl)
        v = v if isinstance(v, list) else ([v] if v else [])
        if [_n(x) for x in v] == [_n(a) for a in _AMULET]:
            slot = nsl
            break
    if slot is None:
        problems.append("THE GOLDEN BOUGH is NOT wired on %s: no lootMisc*Item1 "
                        "carries the 3 amulet tiers %s" % (_BLOOM, _AMULET))
    else:
        ch = float(gv(_BLOOM, 'chanceToEquipMisc%d' % slot) or 0)
        if abs(ch - 100.0) > 1e-4:
            problems.append("THE GOLDEN BOUGH is on Misc%d but chanceToEquipMisc%d"
                            "=%r, expected 100.0 (guaranteed)" % (slot, slot, ch))
        if int(gv(_BLOOM, 'dropItems') or 0) != 1:
            problems.append("%s dropItems != 1 - the guaranteed amulet cannot drop"
                            % _BLOOM)
    for a in _AMULET:
        if not resolves(a):
            problems.append("Golden Bough tier record missing: %s" % a)
    # the hoard: ONE chest (R-108 cut it 3 -> 1 for Will's own R-100 #10)
    for h in _HOARD:
        if not resolves(h):
            problems.append("hoard chain record missing: %s (the dedicated "
                            "Boss-locked hoard is a guaranteed reward)" % h)
    if not resolves(_WORLD_CHEST):
        problems.append("world-chest proxy missing: %s - build_section_surgery "
                        "places it BY NAME, so the frozen path must survive."
                        % _WORLD_CHEST)
    if not resolves(_ORB):
        problems.append("terminal orb %s does not resolve - the whole encounter "
                        "would drop no orb (red_uber_orbs shell exemption)." % _ORB)
    if _n(gv(_BLOOM, 'treasureProxyName')) != _n(_ORB):
        problems.append(
            "%s treasureProxyName=%r, expected %s. This is NOT cosmetic: "
            "svc_orb_breadth derives its scope as 'every proxy an UBER names' and "
            "enforces MIN_PROXIES=6 / MIN_TABLES=18; this record is the only uber "
            "naming that proxy, so dropping it reds orb_loot_breadth."
            % (_BLOOM, gv(_BLOOM, 'treasureProxyName'), _ORB))
    # the soul
    got = db.get_field_value(_BLOOM, 'lootFinger2Item1') or []
    got = got if isinstance(got, list) else [got]
    if [_n(x) for x in got] != [_n(s) for s in _SOUL_TIERS]:
        problems.append("%s soul loot=%r, expected the 3 frozen tiers %s"
                        % (_BLOOM, got, _SOUL_TIERS))
    if float(gv(_BLOOM, 'chanceToEquipFinger2') or 0) <= 0:
        problems.append("%s chanceToEquipFinger2=%r - the terminal must pay the "
                        "soul" % (_BLOOM, gv(_BLOOM, 'chanceToEquipFinger2')))
    if float(gv(_ORM, 'chanceToEquipFinger2') or 0) != 0.0:
        problems.append("%s chanceToEquipFinger2=%r - the chain HEAD must stay at "
                        "0 (build_svc_database.SOUL_RATE_ZERO_PINS; a paying head "
                        "makes one encounter drop two souls)"
                        % (_ORM, gv(_ORM, 'chanceToEquipFinger2')))
    if float(gv(_BRIAR, 'chanceToEquipFinger2') or 0) != 0.0:
        problems.append("%s chanceToEquipFinger2=%r - a Champion escort must never "
                        "pay a soul (R-42/R-106)"
                        % (_BRIAR, gv(_BRIAR, 'chanceToEquipFinger2')))
    for s in _SOUL_TIERS:
        if not resolves(s):
            problems.append("soul tier record missing: %s" % s)
        elif _n(gv(s, 'itemNameTag')) != _n(_TAG_SOUL):
            problems.append("soul %s itemNameTag=%r, expected %s"
                            % (s, gv(s, 'itemNameTag'), _TAG_SOUL))

    # ---- 3. A9 RENDER CHAIN: no new art, no cross-rig swap -----------------
    for rec, donor, mesh in ((_ORM, _D_ORM, _MESH_ORM),
                             (_BLOOM, _D_BLOOM, _MESH_BLOOM),
                             (_BRIAR, _D_BRIAR, _MESH_BRIAR)):
        got_m = _n(gv(rec, 'mesh'))
        if got_m != _n(mesh):
            problems.append("A9: %s mesh=%r, expected its OWN donor's rig %s - a "
                            "cross-rig swap is the B-SOUL-PROC-2 defect class."
                            % (rec, gv(rec, 'mesh'), mesh))
        if got_m != _n(gv(donor, 'mesh')):
            problems.append("A9: %s no longer renders on the rig of its donor %s"
                            % (rec, donor))
        tex = gv(rec, 'baseTexture')
        if tex:
            carriers = sum(1 for n in db.record_names()
                           if _n(_one(db, n, 'baseTexture')) == _n(tex))
            if carriers < 2:
                problems.append(
                    "A9: %s baseTexture %r has %d live carrier(s) - a skin with no "
                    "OTHER live carrier on this mesh is the 343_dark_smoke / "
                    "Vort-green trap. Ship the donor's own skin."
                    % (rec, tex, carriers))
        # R-126: actorHeight is a per-rig constant, inherited, never invented
        want_h = _RIG_ACTOR_HEIGHT[rec]
        got_h = gv(rec, 'actorHeight')
        if got_h is not None and abs(float(got_h) - want_h) > 1e-4:
            problems.append("R-126: %s actorHeight=%r, expected its rig constant "
                            "%s (inherit, never write)" % (rec, got_h, want_h))

    # ---- 4. CRASH LAWS -----------------------------------------------------
    for rec in (_ORM, _BLOOM, _BRIAR):
        if gv(rec, 'charFxPakSelfNames'):
            problems.append("CRASH LAW: %s carries charFxPakSelfNames=%r - FX go "
                            "through monster-record fields only"
                            % (rec, gv(rec, 'charFxPakSelfNames')))
        for fld in ('spawnEffect', 'deathEffect'):
            v = gv(rec, fld)
            if not v:
                continue
            if not resolves(v):
                problems.append("%s %s=%r does not resolve" % (rec, fld, v))
            elif _n(_one(db, v, 'Class')) != 'effectentity':
                problems.append("%s %s=%r is Class %r, expected EffectEntity"
                                % (rec, fld, v, _one(db, v, 'Class')))
        # every wired skill + cast resolves
        for i in range(1, 25):
            sk = gv(rec, 'skillName%d' % i)
            if isinstance(sk, str) and sk.strip() and not resolves(sk):
                problems.append("%s skillName%d=%r does not resolve (an authored "
                                "unresolved ref is a P1 on a clone)" % (rec, i, sk))
        for sfx in ('', '2', '3', '4', '5'):
            sk = gv(rec, 'specialAttack%sSkillName' % sfx)
            if isinstance(sk, str) and sk.strip() and not resolves(sk):
                problems.append("%s specialAttack%sSkillName=%r does not resolve"
                                % (rec, sfx, sk))
    # CRASH LAW: no charFxPakSelfNames on ANY Skill_SpawnPet this encounter can
    # reach - the boss kits, the escort, and the soul's own summon skill.
    reachable = {_n(_SUMMON)}
    for rec in (_ORM, _BLOOM, _BRIAR):
        for i in range(1, 25):
            v = gv(rec, 'skillName%d' % i)
            if isinstance(v, str) and v.strip():
                reachable.add(_n(v))
        for sfx in ('', '2', '3', '4', '5'):
            v = gv(rec, 'specialAttack%sSkillName' % sfx)
            if isinstance(v, str) and v.strip():
                reachable.add(_n(v))
    for sk in sorted(reachable):
        if not resolves(sk):
            continue
        if _n(_one(db, sk, 'Class')) == 'skill_spawnpet' and \
                _one(db, sk, 'charFxPakSelfNames'):
            problems.append("CRASH LAW: SpawnPet skill %s carries "
                            "charFxPakSelfNames - that is the shipped crash." % sk)
    # permanent pets: TTL must be empty
    for p in _PETS:
        if not resolves(p):
            problems.append("summon pet tier missing: %s" % p)
            continue
        ttl = db.get_field_value(p, 'spawnObjectsTimeToLive')
        if ttl not in (None, [], '') and any(
                float(x or 0) > 0 for x in (ttl if isinstance(ttl, list) else [ttl])):
            problems.append("PERMANENT PET LAW: %s spawnObjectsTimeToLive=%r, "
                            "expected empty" % (p, ttl))
    if 'ferryman' in asp._SUMMON_IDENTITY_ALLOW:
        problems.append(
            "_SUMMON_IDENTITY_ALLOW still carries 'ferryman'. The summon body is "
            "now the SAME species as the dropper (both SVMesh hellflower), so the "
            "F2 identity gate is green with no exemption - a retired workaround "
            "must not be carried.")

    # ---- 5. THE ESCORT LIFE INVARIANT (the live defect this wave kills) ----
    #        R-100 #18 as a measurable field. Stated over EVERY mod-authored
    #        Champion escort, not just ours, because the roster grows.
    for name in db.record_names():
        base = _n(name).rsplit('\\', 1)[-1]
        if not (base.startswith('svc_') and base.endswith('.dbr')):
            continue
        if _n(_one(db, name, 'monsterClassification')) != 'champion':
            continue
        life = db.get_field_value(name, 'characterLife')
        if not isinstance(life, list) or len(life) < 3:
            continue
        vals = [float(x or 0) for x in life[:3]]
        if not (vals[0] < vals[1] < vals[2]):
            problems.append(
                "CHAMPION ESCORT LIFE NOT ASCENDING: %s characterLife=%r. Life "
                "must rise Normal -> Epic -> Legendary; the shipped Charon escort "
                "was [878, 300, 400] and read to Will as 'super weak ... just like "
                "normal guys' (R-100 #18)." % (name, life))

    # ---- 6. MARKERS + MINION LAW ------------------------------------------
    for rec, want in ((_ORM, 1), (_BLOOM, 1), (_BRIAR, 0)):
        got_v = gv(rec, 'DisplayAsQuestItem')
        if got_v is None or int(float(got_v)) != want:
            problems.append("%s DisplayAsQuestItem=%r, expected %d "
                            "(uber_quest_markers R-100 #7)" % (rec, got_v, want))
    if int(gv(_BRIAR, 'dropItems') or 0) != 0:
        problems.append("%s dropItems=%r - a placed add must not be a loot faucet "
                        "(R-125 minion law)" % (_BRIAR, gv(_BRIAR, 'dropItems')))
    if gv(_BRIAR, 'treasureProxyName'):
        problems.append("%s carries treasureProxyName=%r - escorts drop no chest"
                        % (_BRIAR, gv(_BRIAR, 'treasureProxyName')))

    # ---- 7. TAGS: every referenced display tag has a string ----------------
    for rec, tag in ((_ORM, _TAG_ORM), (_BLOOM, _TAG_BLOOM), (_BRIAR, _TAG_BRIAR)):
        if _n(gv(rec, 'description')) != _n(tag):
            problems.append("%s description=%r, expected %s"
                            % (rec, gv(rec, 'description'), tag))
        if not str(tags.get(tag, '')).strip():
            problems.append("tag %s has no string (arz + Text are a coupled "
                            "deploy; validate_tags is a build gate)" % tag)
    for tag in (_TAG_HOARD, _TAG_SOUL, _TAG_SOUL + 'DESC', _TAG_SUMMON,
                _TAG_SUMMON + 'DESC', _TAG_PET, _TAG_AMULET, _TAG_AMULET_DESC):
        if not str(tags.get(tag, '')).strip():
            problems.append("tag %s has no string" % tag)
    if 'charon' in str(tags.get(_TAG_ORM, '')).lower() or \
            'ferryman' in str(tags.get(_TAG_ORM, '')).lower():
        problems.append("the phase-1 display string %r still reads as Charon - "
                        "this wave exists because Will said the boss is "
                        "indistinguishable from the base Charon."
                        % tags.get(_TAG_ORM))
    if _n(tags.get(_TAG_ORM)) == _n(tags.get(_TAG_BLOOM)):
        problems.append("both forms share one display string - the phase turn "
                        "must read on screen (the shipped encounter's own defect)")

    # ---- 8. THE KIT IS NOT THE BASE BOSS'S KIT (Will's actual complaint) ---
    #
    # Stated precisely, because "zero shared skills" would be WRONG: boss_scaling,
    # all_hpscaling_passive, boss_conversionimmunity, armor_passive and the
    # globalproperties_* rows are universal Boss plumbing that every uber in the
    # mod carries. The complaint was never about plumbing - it was that the
    # SIGNATURE kit was byte-for-byte `boss_charon_43` / `boss_charonform2_43`.
    # So the invariant is: NO `charon_*` signature skill, in any skill slot or any
    # AI cast slot, on either form; and ZERO overlap in the cast ROTATION, which is
    # what a player actually sees the boss do.
    def _sig(rec):
        out = set()
        for i in range(1, 25):
            v = gv(rec, 'skillName%d' % i)
            if isinstance(v, str) and v.strip():
                out.add(_n(v))
        return out

    def _rotation(rec):
        out = set()
        for sfx in ('', '2', '3', '4', '5'):
            v = gv(rec, 'specialAttack%sSkillName' % sfx)
            if isinstance(v, str) and v.strip():
                out.add(_n(v))
        return out

    for rec in (_ORM, _BLOOM, _BRIAR):
        charon_sigs = sorted(p for p in (_sig(rec) | _rotation(rec))
                             if p.rsplit('\\', 1)[-1].startswith('charon_'))
        if charon_sigs:
            problems.append(
                "IDENTITY REGRESSION: %s still carries the base Charon signature "
                "skill(s) %s. Will's order (2026-08-11) was that this boss is "
                "'pretty much identical to the base game charon boss we cloned him "
                "off' - the signature kit is exactly what had to go."
                % (rec, charon_sigs))
    for rec, base in ((_ORM, _CH + r'\boss_charon_43.dbr'),
                      (_BLOOM, _CH + r'\boss_charonform2_43.dbr')):
        if not db.has_record(base):
            continue
        shared = sorted(_rotation(rec) & _rotation(base))
        if shared:
            problems.append(
                "IDENTITY REGRESSION: %s casts %d of the same ability/-ies as the "
                "base boss %s (%s). The AI cast rotation is what the player "
                "actually sees, so it must not overlap." % (rec, len(shared), base, shared))

    if problems:
        raise SystemExit("charon_rework.verify FAILED:\n  " + "\n  ".join(problems))

    print("  charon_rework.verify: OK (proxy chain resolves to Ormenos + 2 "
          "Handbriars on BOTH the forecourt and the TESTHUB yard; Golden Bough "
          "guaranteed on the terminal; hoard + world chest + orb intact; soul "
          "re-identified on the frozen tiers; A9 clean on 3 own-rig clones with "
          "no invented actorHeight; 0 charFxPak, 0 dangling skill refs, permanent "
          "pets TTL-free; no 'ferryman' exemption; every svc_* Champion escort has "
          "strictly ascending life; 0 skills shared with the base Charon forms)")
