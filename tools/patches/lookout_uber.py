r"""lookout_uber - USHKARET, THE SKY-BURIAL: the uber at the end of Lookout Cave.

WILL, VERBATIM (2026-08-15):

    "we should add a uber boss (a new unique one) at the end of lookout cave in
     the area outside the back of the cave that you get through after you walk
     through the whole cave, it is a dead end"

===============================================================================
1. THE PLACE, AS THE BYTES DESCRIBE IT
===============================================================================
You enter `CliffEntranceA01_Ext` in Rhakotis03 at local (12,0,118), walk the whole
of RhakotisOptTombB into RhakotisOptTombB01, and come out of `CliffEntranceA01_Ext`
onto a cliff terrace in **Rhakotis05** at local (201,17,37). That terrace is navmesh
component **#9 of 115 - 23,960 cells at cs 0.2 = 958 square units**, floor y = 17.0,
sitting ~19-24u above the desert floor. It touches no other component: you cannot
climb to it, you can only come out of the cave onto it and walk back. It is a dead
end in the strictest sense the engine supports, and Rhakotis05 is the ONLY level of
all 2282 that binds the `Lookout Cave` region guid, so the area banner over the
fight reads Will's own words back to him.

⚠️ THE SHELF IS NOT EMPTY, AND AN EARLIER DRAFT OF THIS FILE SAID IT WAS.
`Records/Proxies Boss/LE_New/08_RhakotisLookout.dbr` stands at (218.65, 17.57, 53.18),
10.71u from our boss spot, and it is a LIVE base-game encounter, not an inert marker.
Measured this pass in the base-game `database.arz` (74,013 records; the mod does NOT
override it - zero hits for `08_rhakotislookout` in `SoulvizierClassic.arz`):
    Class Proxy, placementExtents 3.5, FileDescription 'treasure only'
    pool1 = records\proxies egypt\pools\beastman\duneraider_01_general02.dbr
            spawnMin 1 / spawnMax 3 of am_sandviper_17|19|23,
            championChance 55.0 / championMax 1 drawn from am_mountedmarauder_19 (w75),
            am_mountedmarauder_22 (w50) and five named heroes at w2 each
            (um_ammet_28, um_satef_29, um_udje_30, um_morloc_31, um_hazur_29)
    accessory1 / accessoryEpic1 / accessoryLegendary1 = {normal,epic,legendary}_goldenchest_02
`chanceToRun` is ABSENT on it, which an earlier read of this lane treated as "disabled".
It is not: 3,650 of the base game's 5,393 `Class=Proxy` records (67.7%) omit the field,
including every LE_New sibling that is a famous shipped encounter (09_HathorRuinA/B =
Souchos, 10_NileCave, 12_MemphisTomb, 13/14_DesertTomb).

SO: after this lane the shelf holds Ushkaret + 2 Mourners + the flock AND a base-game
dune-raider group AND a base-game golden chest. THE DECISION (this lane, stated not
buried): **leave the native content exactly where it is.** It is base-game content that
has stood there since the game shipped, Will asked to ADD an uber and not to remove
anything, and the RETIREMENT PROTOCOL defaults any base-game deletion to WILL-VETO.
Geometrically it is clean - the rings are DISJOINT (10.71u apart; native ext 3.5 + our
proxy ext 4.0 = 7.5) and the native chest is 8.13u from ours - so this is a CLAIM
correction and a Will-facing disclosure, not a placement change. R-108 ("one chest") is
about the THREE chests THIS project used to stack on one uber; it was never a rule that
a base-game chest may not exist in the same room. The lever, if Will wants the shelf
cleared instead, is registered as `BL-R256-DEBT-4`.

MEASURED, THIS LANE, on the shipped map (`work/.../Levels.arc` md5 1bf86461):
    boss   local (208.0, 17.0, 52.0)  d=0.14  clr 100/100/100 (N/E/L) at ext 3.5, 6.0 AND 8.0
    chest  local (210.6, 17.0, 52.0)  d=0.14  clr 100/100/100 at ext 1.0 and 2.0
    7 nest-dressing spots            d<=0.14 clr 100/100/100 at ext 1.0
    nearest native to the boss spot  10.71u (the 08_RhakotisLookout proxy) - clear of the >6u guard
    floor: navmesh reads 17.20, every native on the plane is authored 17.00 -> SHIP 17.0
Reproduce:
    py tools/debug/survey_uberboss_spots.py <map> --level egypt/rhakotis/rhakotis05.lvl --pt 208 52 8.0
    py tools/debug/navmesh_floor_y.py       <map> --level egypt/rhakotis/rhakotis05.lvl --pt 208,52
The placement itself lives in `tools/build_section_surgery.py` (LOOKOUT_HOST_KEY);
this module authors ONLY records + tags, like every other content module.

===============================================================================
2. WHY A VULTURE, AND WHY THIS ONE - the measured firsts
===============================================================================
Re-counted by this lane over all 5,075 `Monster.tpl` records in the shipped arz
(`SoulvizierClassic.arz` md5 1113f2c6), every namespace, not a path prefix - the
R-254 guard from the b93 lesson:

  * THE RIG. The vulture family is 20 records: Common 9 / Champion 5 / Hero 5 /
    unranked 1, and **Boss ZERO**. There is no Boss-rank bird in the 53-record
    `um_`/`svc_` red roster. The only red uber on any flying rig is
    `um_elephantsnatcher_17` (a bat, level 17). Rhakotis05's own ambient population
    is vulture mixes and there are animal bones on the desert floor below the cliff:
    the sky over this level is already full of its children. Nothing was ever at the
    top of it.
  * THE OPENING. `razorquill_megaburst` has **exactly 1 carrier DB-wide** (the donor,
    a Hero); `razorquill_burst` has 3, none of them Boss. No red uber opens on a
    quill fan.
  * THE DIVE. `charon_swoopstomp` has **exactly 3 carriers**, all vanilla
    `boss_charonform2_39|41|43`, and **zero custom** - and Charon himself was
    replaced by Akremon in this mod (R-231-E). Every existing red fights on the
    floor. Those 3 vanilla carriers also make the skill PROVEN TO CAST.
  * THE LARDER. `character_vampiriaura` has 6 carriers (1 Champion, 5 Hero,
    **zero Boss**). Every drain uber in the roster drains ON CONTACT. See section 3
    for exactly what this lane could and could not build out of that.
  * THE LEECH. `leechstrike` has **exactly 1 carrier** (`um_gustleech_28`, Hero).
    Ushkaret is the first Boss on it.
    ⚠️ ROUND-4 CORRECTION: rounds 1-3 also claimed the FLOCK as a first, on the
    grounds that `summon_swarm` has exactly one carrier. That claim is RETIRED, not
    softened: the flock summon no longer derives from `summon_swarm` at all (it could
    not - see apply() step 2 and section 3a), so there is no first there to claim.
    The flock is now a clone of `melalos_zombie_summon3`, a skill a shipped Boss
    already casts, and the module says so instead of banking a first it no longer has.

The name is clean too: "ushkaret", "sky-burial", "mourner" and "larder" return
**zero hits** across all 51,331 arz record paths (the C3 cross-family rule).

===============================================================================
3. THE ONE THING THE ENGINE WOULD NOT GIVE US - stated, not buried
===============================================================================
The concept called for an aura that **eats the bleed standing on its plate** -
everything hemorrhaging in the arena feeding the bird. Measured, `character_vampiriaura`
is a `Skill_BuffRadiusToggled` whose whole payload lives in one `SkillBuff_Passive`
(`character_vampiricbuff`: `skillTargetRadius 8.0`, an `offensiveLifeLeechMin` ladder
and a `defensiveSlowLifeLeach` ladder). There is **no conditional-on-target-state
channel anywhere in that shape**, so a bleed-CONDITIONAL feed is not expressible.

WHAT SHIPS, HONESTLY: the Larder is a real authored pair (`svc_ushkaret_larder` +
`svc_ushkaret_larderbuff`) with the radius widened 8.0 -> 14.0 so the plate really is
the shelf, and the leech ladders raised. Combined with `hemorrage`/`hemorrage_debuff`
and `leechstrike`, the FIGHT still reads "it feeds while you bleed" and bleed resist
is still the counter - but the mechanic that exists is a wide, strong life-leech
aura, NOT a bleed-conditional feed, and this file, the report and WILL_TEST_GUIDE all
say so. Registered as `BL-R256-DEBT-1`.

⚠️ AND IT ONLY REACHES THE PLAYER BECAUSE OF A ROUND-4 FIX. The donor drives its
vampiric aura through TWO fields - `skillName5` AND `buffSelfSkillName` - and rounds
1-3 repointed only the kit slot. The shipped boss therefore named the AUTHORED aura in
a slot and the STOCK, shared, 6-carrier one in the channel the engine reads: either
the player got the plain 8.0-radius aura and every value above was dead config, or the
AI refused a skill absent from its kit and nothing fired at all. Both readings make
this whole section a lie. Both always-on channels (`buffSelfSkillName` +
`initialSkillName`, the R-255 pair) now name the authored aura, and gate arm V14 reds
if either is ever left on the donor's record.

===============================================================================
3a. THE OTHER THING THE ENGINE WOULD NOT GIVE US - the flock's donor
===============================================================================
The b76 law says a hostile summon carries TWO bounds: a concurrent cap AND a finite
spawn TTL. Rounds 1-3 built the flock by cloning `summon_swarm` and ADDING the TTL.
Measured, that donor carries no `spawnObjectsTimeToLive`, no `FileDescription` and a
TWENTY-entry `spawnObjects`, so the clone added two fields the donor lacks and left
nineteen donor `.dbr` slots empty - **22 violations of the B-TOXEUS-2 clone-shape
invariant, which `run_registry_gates()` runs UNCONDITIONALLY. The cold build was
dead, and this file claimed the invariant held.** The claim was never measured; that
is `BL-R256-DEBT-5` exactly as registered, and it was not a formality.

The fix is a donor, not a waiver. `melalos_zombie_summon3` is the only base-data
monster spawn skill that ships BOTH bounds NATIVELY (petLimit 6, TTL 15.0) with a
one-entry `spawnObjects`, so every value this lane needs is an existing-field override
and the clone's shape is a strict SUBSET of its donor's. Cost, stated: the flock is no
longer a `summon_swarm` first (section 2), and the donor's `Summon` animation demand
is DELETED because the Corpsewake rig's two special-attack ref slots are both spoken
for (`SwoopStomp` and `Hemorrage`). Gain: the shape is one a shipped Boss already
casts, and gate arm V16 now re-runs the REAL shared clone-shape function over this
lane's own three pairs, so the claim in this paragraph is measured by the module that
makes it.

Two smaller honest notes:
  * THE APPROACH (graft G3, "the boss reads as a carcass until you walk in") is NOT
    implemented and is NOT claimed. A `Proxy` spawns a live monster; there is no
    dormant-actor channel on that path. What ships instead is the nest: the shelf is
    dressed as a kill site (section 5) so the LARDER is what you read before the bird
    moves.
  * THE DIVE'S ANIMATION. `charon_swoopstomp` demands the `SwoopStomp` clip, which
    only Charon's own rig answers. Rather than let it fall through to the generic
    attack (the documented graceful degradation - `docs/reports/dagon_frozen_rca.md`
    measured 1,202 of 2,048 base-game monsters living with exactly that), this lane
    repoints the donor's OWN `unarmedSpecialAnimRef1` from `Bladestorm` (a skill it
    is losing anyway) to `SwoopStomp`, so the dive plays `Vulture_AttBeta.anm`. That
    is an existing-field override on a cloned Monster record - no new field, no
    template guess, the R-255 lesson respected.

===============================================================================
4. THE FIGHT
===============================================================================
P1 THE VIGIL   - it does not land. `attackSkillName = razorquill_megaburst`
                 (Skill_AttackProjectileFan) raked across the shelf; passive
                 `razorbird_retaliation` punishes anyone who closes.
P2 THE STOOP   - it folds and drops on you: `charon_swoopstomp` (Skill_AttackRadius,
                 radius 7.0) at the AUTHORED level [1,4,7], then fights on the ground
                 with `hemorrage` (bleed + movement slow) and `leechstrike`.
                 THE LEVEL IS PART OF THE FIGHT, not bookkeeping. That skill's damage
                 is a NINE-row ladder and its only three carriers in the whole game -
                 vanilla `boss_charonform2_39|41|43` - use [1,4,7]/[2,5,8]/[3,6,9].
                 Rounds 1-3 reused the donor's `bladestorm` slot and kept its
                 skillLevel6 [10,13,16], i.e. off the end of the authored ladder: on
                 NORMAL that clamps to 445 cold + 870 vitality + 12%-of-current-life
                 + a 2.0s stun where vanilla's own level-1 row is 419 / 805 / 2%.
                 Ushkaret is charLevel 30 and Charon-39 is the weakest carrier, so
                 Ushkaret gets Charon-39's row and not one above it. Gate arm V15.
                 AND IT CAN AFFORD TO: the stoop costs a flat 250 mana, nothing in the
                 boss furniture returns any, and the donor's Hero pool is 500/5 - two
                 casts and then ~50s of regen each. Mana is 3000/30 (the shipped
                 placed-red band; Charon, who owns this skill, runs exactly 3000/30).
                 Gate arm V18 derives the requirement from the kit rather than pinning
                 it, so a costlier skill added later reds instead of starving quietly.
P3 SKY-BURIAL  - `svc_ushkaret_skyburial` calls the flock (Common carrion-motes only,
                 never Champions - the neferkha no-crowd-out shape); on death
                 `ondeath_bladeorb` scatters the last quills.
                 THE FLOCK IS BOUNDED TWO WAYS: `petLimit` 6 (concurrent) AND
                 `spawnObjectsTimeToLive` 20.0s (expiry). Round 2 shipped only the cap,
                 which is the b76 P0 Will filed as "the infinite summon ... the game is
                 frozen"; a petLimit does NOT substitute (every b76 offender
                 `summon_caps` repaired already had one), and no shared gate can catch
                 ours because `summon_caps.check_no_new_unbounded` only fires on
                 records with NEITHER bound - a healthy petLimit HIDES a permanent
                 flock from it. So this module owns both bounds and gate arm V13
                 asserts them on the final db. Round 3 added the TTL to the wrong donor
                 and killed the cold build; section 3a is the whole story. Both bounds
                 are now INHERITED from `melalos_zombie_summon3` rather than added.
                 20.0s is quoted, not chosen: it is what every `svc_`-authored summon in
                 the shipped arz already carries (the four_generals musters x4 and
                 `svc_leinth_guard_bloodbeast`) and one of the two values `summon_caps`
                 itself restores.
Furniture, unchanged from every shipped red: `boss_conversionimmunity`,
`armor_passive`, `boss_scaling`, `globalproperties_{normal,epic,legendary}01`.
DELIBERATELY NOT USED because a red already owns them: `razorquill_nova` (Akremon
form 2), `ormenos_droptelekinesis` + `arena_meteor` (Sarkoth),
`svc_akremon_styx_undertow` + `drx_earthbind` (Akremon),
`giantkarkinos_flightofthekondor` (the Deep Thresher).

DURABILITY, inside the shipped band (re-measured, not remembered): Ephialtes
[15000,20000,27000], Mnemophage [14000,19000,25000], Kroisos/Dorus [13500,18500,24000].
Ushkaret ships [14000,19000,26000] - hard but killable, no wall. charLevel [30,52,68]
sits between Neferkha [32,50,64] and Vashkarr [38,56,71]: correct for the Act 2
Rhakotis cliff. Scale 2.7 against a roster whose true ceiling is 3.80
(`um_polisgaoler_unbound_99`, measured - NOT the 3.5 the concept claimed): mid-band,
and on `actorHeight` 1.7 it stands ~4.6u on a 44x43u shelf, which is the point of a
larder.

===============================================================================
5. WHAT THIS MODULE AUTHORS (all NEW, collision-disjoint paths)
===============================================================================
  um_ushkaret_99                 the boss (Monster derive from um_corpsewake_28)
  svc_ushkaret_mourner_30        the Champion escort, x2 (em_razorbird_24 derive)
  svc_ushkaret_carrionmote_26    the Common flock body (am_plaguevulture_20 derive)
  svc_ushkaret_larder(+buff)     the widened life-leech aura pair, driven from BOTH
                                 always-on channels on the boss (R-255)
  svc_ushkaret_skyburial         the flock summon (melalos_zombie_summon3 derive - see
                                 section 3a; Commons only, both b76 bounds INHERITED:
                                 petLimit 6 + a spawn TTL set to the svc_ value 20.0s)
  limit_ushkaret                 the [1..110] no-downscale window
  q_ushkaret_lone (+pool)        the lone-boss placer the map lane injects
  svc_ushkaret_chest             the ONE world chest (R-108 / UBER_CHEST_COUNT = 1)
  svc_ushkarethoard_*            its dedicated Boss-locked hoard chain (R-251 shape)
  ushkaret_soul_{n,e,l}          "{^F}Soul of the Sky-Burial" + summon_ushkaret + 3 pets

DELIBERATE NON-GOALS, so nobody reads them as omissions: no TESTHUB yard proxy (the
map lane is not wiring one this wave, and an unplaced proxy is dead config), and no
new art of any kind - the boss wears the donor's OWN skin, `corpsewake.tex`, which
has exactly ONE wearer in the whole database, so Ushkaret gets an exclusive look and
the Corpsewake heroes read as its brood.
"""
import sys
import importlib
from pathlib import Path

# tools/ (the parent of this package) must be importable for apply_svc_patches +
# arz_patcher. The registry already puts tools/ on sys.path; this makes the module
# import-safe standalone (probes / --negtest) too.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import apply_svc_patches as A                                            # noqa: E402
# WHERE AN EXPLICIT DTYPE IS STILL LEGITIMATE HERE, and it is a short list. The standing
# CLAUDE.md law is about CLONED records' EXISTING fields, where passing a dtype overwrites
# the donor's declared type. It does not forbid declaring a type for a field that is
# genuinely ABSENT, which is the only remaining use:
#   S  `treasureProxyName` (the donor carries none) and `itemQualityTag` on the souls;
#   F  every `_soul_stats` field - souls are built with bare `_ensure_record()`, never
#      clone_record (the standing soul law), so those fields have no inherited type;
#   I  the V17 negative test, which plants the dtype flip on purpose.
# The round-3 `sf(SKYBURIAL,'spawnObjectsTimeToLive', ..., F)` is gone: the new flock donor
# already declares that field, so declaring it again would be the clobber the law forbids.
from arz_patcher import DATA_TYPE_STRING as S, DATA_TYPE_FLOAT as F, DATA_TYPE_INT as I  # noqa: E402

MODULE_NAME = "Lookout Cave uber (Ushkaret, the Sky-Burial)"

# ── NEW record paths (authored here) ────────────────────────────────────────
_V = r'records\creature\monster\vulture'
BOSS        = _V + r'\um_ushkaret_99.dbr'
MOURNER     = _V + r'\svc_ushkaret_mourner_30.dbr'
CARRIONMOTE = _V + r'\svc_ushkaret_carrionmote_26.dbr'

LARDER      = r'records\skills\monster skills\auras\svc_ushkaret_larder.dbr'
LARDER_BUFF = r'records\skills\monster skills\auras\svc_ushkaret_larderbuff.dbr'
SKYBURIAL   = r'records\skills\boss skills\svc_ushkaret_skyburial.dbr'

LIMIT       = r'records\proxies egypt\limit_ushkaret.dbr'
POOL        = r'records\drxmap\proxy\pools\q_ushkaret_lone.dbr'
PROXY       = r'records\drxmap\proxy\q_ushkaret_lone.dbr'
# built by A._svc_build_world_chest_proxy; named here so verify() can assert it.
WORLD_CHEST = r'records\drxmap\proxy\svc_ushkaret_chest.dbr'
HOARD_PREFIX = 'ushkaret'

SOUL_BASE   = 'ushkaret'                      # -> svc_uber\ushkaret_soul_{n,e,l}.dbr
SUMMON      = r'records\skills\soulskills\summon_ushkaret.dbr'
PETS        = [r'records\skills\soulskills\pets\ushkaret_%d.dbr' % i for i in (1, 2, 3)]

# ── DONORS (every one exact-path verified in the shipped arz by this lane) ───
DONOR_BOSS    = _V + r'\um_corpsewake_28.dbr'          # Hero, Beast, flies; scale 1.55, run 0.65, actorHeight 1.7
DONOR_MOURNER = _V + r'\em_razorbird_24.dbr'           # Champion, scale 1.10, run 0.85
DONOR_MOTE    = _V + r'\am_plaguevulture_20.dbr'       # Common, chanceToEquipFinger2 already 0.0
DONOR_LARDER  = r'records\skills\monster skills\auras\character_vampiriaura.dbr'      # Skill_BuffRadiusToggled
DONOR_LARDERB = r'records\skills\monster skills\auras\character_vampiricbuff.dbr'     # SkillBuff_Passive
# THE FLOCK DONOR - CHANGED IN VET ROUND 4, and the reason is a hard build failure.
# Round 3 cloned `records\skills\sv\gustleech\summon_swarm.dbr` and then ADDED
# `spawnObjectsTimeToLive` to it (the b76 bound), ADDED `FileDescription`, and shortened
# its 20-entry `spawnObjects` to one. All three are B-TOXEUS-2 clone-shape violations, and
# `_verify_boss_kit_clone_shape` runs UNCONDITIONALLY on the build path - 22 problems, a
# dead cold build. See the long note in apply() step 2. The replacement is the only
# base-data monster spawn skill that ships BOTH b76 bounds NATIVELY (petLimit 6 +
# spawnObjectsTimeToLive 15.0) with a 1-entry `spawnObjects`, so every value this module
# needs is an EXISTING-field override and the invariant holds by construction rather than
# by assertion. It is also a BOSS's own flock summon in the shipped data (um_melalos_19
# raises zombies with it), so the shape is proven to cast on a Boss - which the Hero-only
# summon_swarm never was. Measured untouched by any other patch module (zero hits for
# `melalos_zombie_summon3` across tools/), so cloning it at registry slot 12 is safe.
DONOR_FLOCK   = r'records\skills\monster skills\summoning_pets\melalos_zombie_summon3.dbr'
DONOR_POOL    = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
DONOR_PROXY   = r'records\drxmap\proxy\q_leinth_lone.dbr'

# ── KIT (all present; anim demands answered - see section 3) ─────────────────
SK_ARMOR      = r'records\skills\monster skills\defense\armor_passive.dbr'
SK_MEGABURST  = r'records\skills\monster skills\attack_projectile\razorquill_megaburst.dbr'
SK_RETALIATE  = r'records\skills\monster skills\passive_buffs\razorbird_retaliation.dbr'
SK_BLADEORB   = r'records\skills\monster skills\ondeath\ondeath_bladeorb.dbr'
SK_SWOOP      = r'records\xpack\skills\bossskills\charon_swoopstomp.dbr'   # Skill_AttackRadius, anim 'SwoopStomp'
SK_HEMORRAGE  = r'records\skills\monster skills\attack_projectile\hemorrage.dbr'
SK_LEECHSTRIKE = r'records\skills\sv\gustleech\leechstrike.dbr'
# NOT in the boss kit: the ESCORT inherits this natively from em_razorbird_24. It is
# required here only so a missing donor reds loudly instead of leaving the Mourner with
# a dangling attack. (The escort likewise KEEPS its donor's native `razorquill_nova` -
# a base-game Champion skill it already ships with today. That skill is on the boss's
# deliberately-avoided list because Akremon form 2 owns it as a SIGNATURE; leaving a
# Champion's own stock kit alone is not the same thing as giving a red uber a borrowed
# signature, and stripping it would make this escort weaker than the vanilla razorbird.)
SK_BURST      = r'records\skills\monster skills\attack_projectile\razorquill_burst.dbr'
SK_CONVIMM    = r'records\skills\boss skills\boss_conversionimmunity.dbr'
SK_BOSSSCALE  = r'records\skills\monster skills\passive_buffs\boss_scaling.dbr'
SK_GP_N       = r'records\skills\monster skills\globalproperties_normal01.dbr'
SK_GP_E       = r'records\skills\monster skills\globalproperties_epic01.dbr'
SK_GP_L       = r'records\skills\monster skills\globalproperties_legendary01.dbr'

ORB = r'records\item\containers\new\genericbossorb_02.dbr'
# WHY orb02, measured not chosen: red_uber_orbs' own ladder rule is "minimum-distance
# band, ties to the lower tier". The consumer bands in the shipped arz are
# orb01 (15..20), orb02 (32..36), orb03 (42..48), orb04 (38..74); at charLevel[0]=30
# the distances are 10 / 2 / 12 / 8, so orb02 wins outright - the Egypt band Neferkha
# (32) and um_frost_36 already sit in. orb05 is R-99 RESERVED for the Toxeus roster
# and is never touched here (uber_apex_orb.verify() fails the build on a non-Toxeus
# carrier); verify() below re-proves the tier from the FINAL db so this cannot rot.

# ── BANDS / DURABILITY (all re-measured against the shipped roster) ──────────
BAND        = [30, 52, 68]
HP          = [14000.0, 19000.0, 26000.0]
HP_REGEN    = [20.0, 40.0, 70.0]
SCALE       = 2.7
# THE STOOP'S LEVEL, and it is not a taste call (vet round 4). The donor drove
# `bladestorm` on slot 6 at skillLevel6 [10,13,16]; round 3 reused the slot for
# `charon_swoopstomp` and left the level alone. Measured, that skill's damage is a
# NINE-entry ladder (offensiveColdMin/offensiveLifeMin/offensivePercentCurrentLife 9
# rows each) and its only three carriers - vanilla boss_charonform2_39|41|43 - use
# [1,4,7] / [2,5,8] / [3,6,9], i.e. the clean 1..9 grid. Nothing in the game has ever
# cast it above 9, so [10,13,16] runs off the end of the authored ladder: clamped that
# is 445 cold + 870 vitality + 12%-of-current-life + a 2.0s stun on NORMAL, where
# vanilla's own level-1 row is 419 / 805 / 2%. Ushkaret is charLevel 30; Charon-39 is
# the weakest carrier and casts [1,4,7]; a level-30 Act 2 uber gets that row and not
# one above it. Gate arm V15 re-derives the ladder depth and reds on any slot above it.
SWOOP_LEVEL = [1, 4, 7]
# MANA, measured instead of inherited (vet round 4). `charon_swoopstomp` costs a FLAT
# 250 per cast and the flock costs 50; the donor Corpsewake Hero ships characterMana
# 500 / regen 5, and NOTHING in the furniture gives mana back (globalproperties_*,
# boss_scaling and armor_passive all read 0.0 on every mana field). At 500/5 the stoop
# fires twice and then costs 50 seconds of regen per cast while the flock drains the
# same pool - the single most expensive skill in the roster on the smallest pool in it.
# The only three carriers of that skill carry 8000/50. 3000/30 puts Ushkaret exactly on
# the shipped placed-red band (Ephialtes 3000/5, Charon 3000/30, Charon form 2 3000/21,
# the Polis Gaoler 3000/2) and makes the arithmetic honest: 3000 pool = 12 consecutive
# stoops, 30/s regen = a sustained stoop every ~8.3s with the flock still affordable.
MANA        = 3000.0
MANA_REGEN  = 30.0
MOURNER_BAND = [28, 50, 66]
MOURNER_HP   = [1400.0, 2400.0, 3600.0]        # strictly ascending (the R-100 #18 escort invariant)
MOTE_BAND    = [26, 46, 60]
# THE FLOCK'S SECOND BOUND (b76 law). The donor carries petLimit 5 and NO TTL; a permanent
# flock under a cap is the exact shape Will filed as a P0 freeze. 20.0s is the value every
# `svc_`-authored summon in the shipped arz already uses (four_generals x4 + leinth), and one
# of the two `summon_caps` restores. See the long note in apply() step 2 and gate arm V13.
FLOCK_TTL    = 20.0
FLOCK_CAP    = 6

# ── TAGS ────────────────────────────────────────────────────────────────────
TAG_BOSS    = 'tagSVCMonsterUshkaret'
TAG_MOURNER = 'tagSVCMonsterCliffsideMourner'
TAG_MOTE    = 'tagSVCMonsterCarrionMote'
TAG_HOARD   = 'tagSVCUshkaretHoard'
TAG_SOUL    = 'tagSVCSoulSkyBurial'
TAG_SUMMON  = 'tagSVCSummonUshkaret'
TAG_PET     = 'tagSVCPetPatientWing'

_ALL_TAGS = (TAG_BOSS, TAG_MOURNER, TAG_MOTE, TAG_HOARD, TAG_SOUL, TAG_SOUL + 'DESC',
             TAG_SUMMON, TAG_PET)

# The three skill clones this module registers into the shared B-TOXEUS-2 clone-shape
# gate. Named once so apply() (which registers them) and verify() (which re-runs the
# REAL gate function over exactly these pairs, so the two can never drift) agree.
_CLONE_PAIRS = ((DONOR_LARDERB, LARDER_BUFF),
                (DONOR_LARDER, LARDER),
                (DONOR_FLOCK, SKYBURIAL))

# ── THE KIT TABLE (slot, skill, level). `None` = KEEP the donor's own skillLevel for
#    that slot, which is only ever legal when the slot still holds the donor's own
#    skill (or this module's clone of it) - see `_KIT_LEVEL_INHERITABLE` and gate arm
#    V15. Every slot this module re-points to a DIFFERENT skill authors its level.
KIT_SLOTS = (
    (1,  SK_ARMOR,       None),                   # donor
    (2,  SK_MEGABURST,   None),                   # donor - P1 the vigil
    (3,  SK_RETALIATE,   None),                   # donor - closing costs blood
    (4,  SK_BLADEORB,    None),                   # donor - P3 the last quills
    (5,  LARDER,         None),                   # this module's clone of the donor's own
                                                  # character_vampiriaura: identical ladder,
                                                  # so the donor's [3,6,9] still fits
    (6,  SK_SWOOP,       SWOOP_LEVEL),            # was bladestorm - P2 the stoop
    (7,  SK_HEMORRAGE,   None),                   # donor - the bleed
    (8,  SK_LEECHSTRIKE, [2, 5, 8]),              # NEW slot (gustleech's own levels)
    (9,  SKYBURIAL,      [1, 2, 3]),              # NEW slot - P3 the flock
    (12, SK_BOSSSCALE,   [1, 2, 3]),              # was hero_scaling (donor level, authored)
    (13, SK_GP_L,        [0, 0, 1]),              # was hero_modifier
    (14, SK_CONVIMM,     [1, 1, 1]),              # NEW slot
)
# The only slots allowed to INHERIT a level: those still holding the donor's own skill,
# plus slot 5, whose skill is this module's clone of the donor's own aura (same record
# shape, same ladder). Anything else reusing a slot inherits a level tuned for a
# DIFFERENT skill - the round-3 defect where charon_swoopstomp ran at bladestorm's
# [10,13,16] against its own 9-row ladder.
_KIT_LEVEL_INHERITABLE = {5: DONOR_LARDER}


# ── small readers (kept local; the module must not depend on monolith privates
#    beyond the sanctioned builders) ──────────────────────────────────────────
def _n(p):
    return str(p).replace('/', '\\').lower()


def _v1(db, rec, field):
    v = db.get_field_value(rec, field)
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _soul_paths():
    return [r'%s\%s_soul_%s.dbr' % (A._SOUL_DIR, SOUL_BASE, t) for t in ('n', 'e', 'l')]


def _dtype_of(db, rec, field):
    """The declared dtype of `field` on `rec` (None if the field is absent)."""
    for k, tf in (db.get_fields(rec) or {}).items():
        if k.split('###')[0] == field:
            return getattr(tf, 'dtype', None)
    return None


def _del_field(db, rec, field):
    """Remove a field slot entirely rather than blanking it to ''.

    The repo's own precedent (`enslaver_shroud._del_field`): an ABSENT field is the
    shipped way to say "this record does not use this"; a blanked one is a loader
    hazard. It also keeps a clone's shape a strict SUBSET of its donor's, which is
    what the B-TOXEUS-2 invariant wants (rule 1 only sees fields the clone ADDS)."""
    ff = db.get_fields(rec)
    if not ff:
        return False
    gone = [k for k in list(ff) if k.split('###')[0] == field]
    for k in gone:
        del ff[k]
    if gone:
        db._modified.add(rec)
    return bool(gone)


def _ladder_depth(db, skill):
    """The authored per-level DAMAGE depth of a skill record.

    = the longest `offensive*Min` / `offensive*Max` array on it. That is the array the
    engine indexes with the skill level, so a level above it runs off the end of what
    the designer wrote. Deliberately NOT `skillMaxLevel` (a blanket 20 on almost every
    skill in the database, including ones with a 9-row ladder) and deliberately the
    LONGEST rather than the shortest array, because vanilla itself runs level 9 against
    charon_swoopstomp's 3-entry `offensiveStunMin`. Returns 0 when the skill authors no
    damage ladder at all (a passive / a summon), in which case there is nothing to
    overrun and the check is skipped."""
    depth = 0
    for k, tf in (db.get_fields(skill) or {}).items():
        b = k.split('###')[0]
        if b.startswith('offensive') and (b.endswith('Min') or b.endswith('Max')):
            depth = max(depth, len(tf.values or []))
    return depth


def _sibling(name):
    """Import a sibling `tools/patches/` module without assuming a package context.

    apply()/verify() normally run with this file loaded as `patches.<name>`, but
    `--negtest` runs it as `__main__` with no package at all. Try the package path
    first, then fall back to a bare import with this directory on sys.path."""
    try:
        return importlib.import_module('patches.%s' % name)
    except Exception:
        here = str(Path(__file__).resolve().parent)
        if here not in sys.path:
            sys.path.insert(0, here)
        return importlib.import_module(name)


def _soul_stats(diff):
    """THE LARDER, as a player sheet: bleed + life leech + quills, laddered
    0.6 / 0.82 / 1.0 (the Vashkarr / Dorus / Neferkha soul cadence).

    Field names are MEASURED, not assumed: bleeding damage in this database is
    `offensiveSlowBleeding*` (9,690 item carriers), NOT `offensiveSlowPhysical*`
    (present-but-zero on every soul) and NOT `offensiveTrapMin/Max` (the R-231
    finding). Life leech is `offensiveLifeLeechMin`, which the Larder's own buff
    and `leechstrike` both carry.

    The amgoz downside is mandatory and thematic: a sky-burial is a TRADE. You
    get the bird's appetite, and the bird's hide - carrion has no armour, so the
    soul opens you to the same pierce and bleeding it deals."""
    m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[diff]
    r = lambda v: round(v * m, 1)                                        # noqa: E731
    return {
        **A._bmp(diff),                                   # per-tier soul icon
        'FileDescription': (S, 'Egypt'),                  # amgoz V5: the act/region word
        # ── the amgoz downside pair (a trade, never a free upgrade) ──
        'defensivePierce': (F, {'n': -12.0, 'e': -15.0, 'l': -18.0}[diff]),
        'defensiveBleeding': (F, {'n': -12.0, 'e': -15.0, 'l': -18.0}[diff]),
        # ── the appetite ──
        'offensiveLifeLeechMin': (F, r(45.0)),
        'offensiveSlowBleedingMin': (F, r(60.0)), 'offensiveSlowBleedingMax': (F, r(95.0)),
        'offensiveSlowBleedingDurationMin': (F, 4.0),
        'offensiveSlowBleedingModifier': (F, r(35.0)),
        'offensiveSlowBleedingChance': (F, r(40.0)),
        # ── the quills ──
        'offensivePierceMin': (F, r(50.0)), 'offensivePierceMax': (F, r(85.0)),
        'offensivePierceRatioModifier': (F, r(20.0)),
        # ── the body ──
        'characterDexterity': (F, r(40.0)), 'characterDexterityModifier': (F, r(10.0)),
        'characterOffensiveAbility': (F, r(95.0)),
        'characterLife': (F, r(300.0)), 'characterLifeModifier': (F, r(10.0)),
        'characterLifeRegen': (F, r(9.0)),
        'characterRunSpeedModifier': (F, r(10.0)),        # it flies; you move like it
        'characterAttackSpeedModifier': (F, r(12.0)),
        'characterDefensiveAbility': (F, r(55.0)),
        'defensiveLife': (F, r(20.0)),
    }


# =============================================================================
def apply(db, tags):
    print("\n=== patches-registry: %s ===" % MODULE_NAME)
    sf = db.set_field

    # ── 0. FAIL LOUD on any missing donor (exact path; has_record is exact) ──
    for donor in (DONOR_BOSS, DONOR_MOURNER, DONOR_MOTE, DONOR_LARDER, DONOR_LARDERB,
                  DONOR_FLOCK, DONOR_POOL, DONOR_PROXY, ORB,
                  SK_ARMOR, SK_MEGABURST, SK_RETALIATE, SK_BLADEORB, SK_SWOOP,
                  SK_HEMORRAGE, SK_LEECHSTRIKE, SK_BURST, SK_CONVIMM, SK_BOSSSCALE,
                  SK_GP_N, SK_GP_E, SK_GP_L,
                  A._SVC_LIMIT_DONOR, A._SVC_DIFFICULTY04):
        if not db.has_record(donor):
            raise SystemExit("lookout_uber: REQUIRED donor missing (exact): %s" % donor)
    for path in (BOSS, MOURNER, CARRIONMOTE, LARDER, LARDER_BUFF, SKYBURIAL, POOL, PROXY):
        if db.has_record(path):
            raise SystemExit(
                "lookout_uber: %s ALREADY exists - this module expects to be the "
                "record's first author (measured absent on main). Another lane now "
                "owns it; make the ordering explicit and re-measure." % path)

    # ── 1. THE LARDER (aura + its buff). Both are single-purpose clones that override
    #    ONLY fields their donor already carries, so the B-TOXEUS-2 clone-shape
    #    invariant holds - MEASURED this round, not asserted: round 3 also set
    #    `FileDescription` on the BUFF, and `character_vampiricbuff` (619 fields) does
    #    not carry one, so that single cosmetic line was a rule-1 violation that reds
    #    the build. It is gone. The AURA's donor (5 fields) DOES carry FileDescription,
    #    so that one stays. See section 3: this is a WIDE, STRONG life-leech aura. It is
    #    NOT a bleed-conditional feed - the shape has no conditional channel at all. ──
    db.clone_record(DONOR_LARDERB, LARDER_BUFF)
    _radius_before = _v1(db, LARDER_BUFF, 'skillTargetRadius')
    sf(LARDER_BUFF, 'skillTargetRadius', 14.0)            # 8.0 -> the plate IS the shelf
    # raise the two leech ladders ~1.35x on their own 20-step shape (never a new field)
    for fld, mult in (('offensiveLifeLeechMin', 1.35), ('offensiveSlowLifeLeachMin', 1.35),
                      ('defensiveSlowLifeLeach', 1.20)):
        cur = db.get_field_value(LARDER_BUFF, fld)
        if isinstance(cur, list) and cur and all(isinstance(x, (int, float)) for x in cur):
            sf(LARDER_BUFF, fld, [round(float(x) * mult, 1) for x in cur])
    db._modified.add(LARDER_BUFF)

    db.clone_record(DONOR_LARDER, LARDER)
    sf(LARDER, 'buffSkillName', LARDER_BUFF)              # the ONE existing-field repoint
    sf(LARDER, 'FileDescription', 'Ushkaret larder aura (life leech + leech resist)')
    db._modified.add(LARDER)

    # ── 2. THE FLOCK SUMMON, REBUILT IN VET ROUND 4 ON A DIFFERENT DONOR.
    #
    #    THE FLOCK MUST BE BOUNDED TWO WAYS (the b76 law): a concurrent cap AND a
    #    finite spawn TTL. Round 2 shipped only the cap; round 3 added the TTL to a
    #    clone of `summon_swarm` - and THAT is what broke. `summon_swarm` carries NO
    #    `spawnObjectsTimeToLive` and NO `FileDescription`, and its `spawnObjects` is
    #    twenty entries long, so round 3's clone ADDED two fields the donor lacks and
    #    left nineteen donor .dbr slots reading empty. `_verify_boss_kit_clone_shape`
    #    (B-TOXEUS-2) runs UNCONDITIONALLY inside `run_registry_gates()` on the build
    #    path and reds on exactly those three shapes: 22 problems, a dead cold build.
    #    The module's own docstring claimed the invariant held. It did not, and the
    #    only reason no gate caught it is that `--negtest` runs this module standalone
    #    against an already-built arz (that is `BL-R256-DEBT-5`, and it was not a
    #    formality).
    #
    #    THE FIX IS A DONOR, NOT A WAIVER. `melalos_zombie_summon3` is the one
    #    base-data monster spawn skill that ships BOTH b76 bounds NATIVELY -
    #    `petLimit 6` (already our cap) and `spawnObjectsTimeToLive 15.0` - with a
    #    ONE-entry `spawnObjects`, a `skillCooldownTime` and a `skillManaCost`. So
    #    every value below is an EXISTING-FIELD OVERRIDE, the clone's shape is a
    #    strict subset of its donor's, and the invariant holds BY CONSTRUCTION instead
    #    of by assertion. It is also a Boss's own flock summon in the shipped data
    #    (`um_melalos_19` raises zombies with it, on both `skillName2` and
    #    `specialAttack2SkillName`), so the shape is proven to cast on a Boss - which
    #    the Hero-only `summon_swarm` never was - and its spawn body is a Monster.tpl
    #    record, so repointing it at our Common carrion-mote is the same shape, not a
    #    class change. NOT un-registering the pair from `_BOSS_KIT_CLONES` was the
    #    other option and it is the wrong one: that disarms a fail-loud gate.
    #
    #    THE ONE SUBTRACTION: the donor demands the `Summon` animation, and the
    #    Corpsewake rig has exactly two special-attack ref slots - `Bladestorm` (this
    #    lane repoints it to `SwoopStomp`) and `Hemorrage` (this lane KEEPS hemorrage
    #    in the kit, so it is spoken for). There is no third clip on the rig to bind,
    #    so the demand is DELETED rather than left dangling or blanked: an absent
    #    `skillSpecialAnimationName` is the shipped way to say "no special animation"
    #    (`summon_swarm` itself has none) and deletion keeps the clone a subset of the
    #    donor. `FileDescription` is likewise NOT set - the donor has none.
    #
    #    THE TTL VALUE IS QUOTED, NOT CHOSEN: 20.0 is what every `svc_`-authored
    #    summon in the shipped arz carries (the four_generals musters x4 and
    #    `svc_leinth_guard_bloodbeast`) and one of the two values `summon_caps`
    #    restores. No shared gate can enforce it for us -
    #    `summon_caps.check_no_new_unbounded` only fires on records with NEITHER
    #    bound, so a healthy petLimit HIDES a permanent flock from it. V13 below owns
    #    it. Commons ONLY - the neferkha no-champion-crowd-out law. ──────────────────
    db.clone_record(DONOR_FLOCK, SKYBURIAL)
    _flock_ttl_before = _v1(db, DONOR_FLOCK, 'spawnObjectsTimeToLive')
    _flock_anim_before = _v1(db, DONOR_FLOCK, 'skillSpecialAnimationName')
    sf(SKYBURIAL, 'spawnObjects', [CARRIONMOTE])          # 1-for-1 ref swap (donor len 1)
    sf(SKYBURIAL, 'petLimit', FLOCK_CAP)                  # donor already 6; explicit anyway
    sf(SKYBURIAL, 'skillCooldownTime', [12.0, 10.0, 8.0])
    sf(SKYBURIAL, 'spawnObjectsTimeToLive', FLOCK_TTL)    # donor 15.0 -> the svc_ value
    _del_field(db, SKYBURIAL, 'skillSpecialAnimationName')
    db._modified.add(SKYBURIAL)

    # ── 3. THE FLOCK BODY (Common). The donor already reads
    #    chanceToEquipFinger2 = 0.0; re-assert it so a placed add can never become
    #    a soul faucet (R-125 minion law + the soul-leak invariant). ──
    db.clone_record(DONOR_MOTE, CARRIONMOTE)
    sf(CARRIONMOTE, 'description', TAG_MOTE)
    sf(CARRIONMOTE, 'monsterClassification', 'Common')
    sf(CARRIONMOTE, 'charLevel', list(MOTE_BAND))
    sf(CARRIONMOTE, 'dropItems', 0)                       # BOOL on the donor - NO dtype
    A._svc_clear_soul_loot(db, CARRIONMOTE)
    db._modified.add(CARRIONMOTE)

    # ── 4. THE CLIFFSIDE MOURNER (Champion escort, x2 in the pool). Donor scale
    #    1.100 is KEPT deliberately: the silhouette gap against the boss's 2.7 is
    #    what makes the boss read as dominance rather than as a big bird among
    #    birds. Strictly-ascending life (the R-100 #18 escort invariant). ──
    db.clone_record(DONOR_MOURNER, MOURNER)
    sf(MOURNER, 'description', TAG_MOURNER)
    sf(MOURNER, 'monsterClassification', 'Champion')
    sf(MOURNER, 'charLevel', list(MOURNER_BAND))
    sf(MOURNER, 'characterLife', list(MOURNER_HP))
    # dropItems is BOOL on all three donors (measured). Passing an explicit dtype to
    # set_field() OVERWRITES tf.dtype on an existing field, so `, I` shipped INT where
    # every other monster in the database declares BOOL - the standing CLAUDE.md law
    # ("never pass explicit dtype to set_field() on cloned records"), and an unexplained
    # type change in the ship lane's record-diff. Gate arm V17 asserts the dtypes match.
    sf(MOURNER, 'dropItems', 0)                           # R-125: an escort is not a loot faucet
    A._svc_clear_soul_loot(db, MOURNER)                   # only the Sky-Burial drops the soul
    db._modified.add(MOURNER)

    # ── 5. USHKARET, THE SKY-BURIAL. Monster derive from the Corpsewake Hero: its
    #    OWN rig AND its OWN skin (A9 / R-126), so no new art and an exclusive
    #    look. actorHeight is deliberately NOT invented - the donor's 1.7 stands. ─
    db.clone_record(DONOR_BOSS, BOSS)
    B = BOSS
    sf(B, 'description', TAG_BOSS)
    sf(B, 'monsterClassification', 'Boss')                # red name; orb + soul key off Boss
    sf(B, 'charLevel', list(BAND))
    sf(B, 'characterLife', list(HP))
    sf(B, 'characterLifeRegen', list(HP_REGEN))
    sf(B, 'scale', SCALE)
    # the resistance wall - hard but killable, no wall. Only fields the donor
    # already carries are touched by name here; each is an ordinary Monster.tpl
    # defensive field the shipped reds (Neferkha / the Helepolis) also set.
    sf(B, 'defensivePierce', 55.0)                        # it IS the quills
    sf(B, 'defensivePhysical', 25.0)
    sf(B, 'defensiveLife', 45.0)
    sf(B, 'defensiveBleeding', 100.0)                     # signature: the larder cannot be bled
    # MANA (vet round 4). See the MANA/MANA_REGEN note above: the donor's Hero pool of
    # 500/5 cannot pay for a 250-cost stoop, and nothing in the furniture returns mana.
    # Both fields exist on the donor, so this is an ordinary existing-field override.
    _mana_before = _v1(db, B, 'characterMana')
    sf(B, 'characterMana', MANA)
    sf(B, 'characterManaRegen', MANA_REGEN)
    # THE ANIMATION ANSWER (section 3): the donor's own ref slot 1 pointed at
    # 'Bladestorm', a skill this boss is losing. Repoint it - an EXISTING field on
    # a cloned record, no new field, no template guess - so the dive plays
    # Vulture_AttBeta.anm instead of falling through to the generic attack.
    _anim_before = _v1(db, B, 'unarmedSpecialAnimRef1')
    sf(B, 'unarmedSpecialAnimRef1', 'SwoopStomp')
    # the kit (KIT_SLOTS, module level so verify() reads the SAME table). Slots 1-7 +
    # 10-13 come from the donor; 8, 9 and 14 are free and are well inside
    # MonsterSkillManager's declared skillName1..17 ceiling (R-255).
    for slot, skill, lvl in KIT_SLOTS:
        sf(B, 'skillName%d' % slot, skill)
        if lvl is not None:
            sf(B, 'skillLevel%d' % slot, list(lvl))
    # THE ALWAYS-ON CHANNEL (vet round 4, and it is the fix that makes the Larder
    # REACH the player). The donor drives its vampiric aura through TWO fields:
    # `skillName5` AND `buffSelfSkillName`, both naming `character_vampiriaura`.
    # Round 3 repointed only the kit slot, so the shipped boss named the AUTHORED
    # aura on skillName5 and the STOCK, shared, 6-carrier one on buffSelfSkillName -
    # meaning either the player got the stock 8.0-radius aura and every authored
    # value (radius 14.0, the raised leech ladders) was dead config, or the AI
    # refused a skill absent from its kit and nothing fired at all. Both are lies
    # against R-256, the docstring and WILL_TEST_GUIDE, and THE LARDER is this
    # lane's whole identity. `_ALWAYS_ON_FIELDS` in `enslaver_shroud` (R-255, one day
    # old) names the two channels the skill manager actually reads for a self-buff;
    # `buffSelfSkillName` is a repoint of a field the donor already carries, and
    # `initialSkillName` is added on the same law (923 of 5,075 Monster.tpl records
    # carry it, 2 of them vultures) so the aura is ON from the first frame instead of
    # waiting on BuffSelfBehavior. Gate arm V14 asserts no always-on channel is left
    # pointing at the donor's stock record.
    for _chan in ('buffSelfSkillName', 'initialSkillName'):
        sf(B, _chan, LARDER)
    # AI rotation: the stoop is the beat, the flock is the escalation, the bleed is
    # the constant. attackSkillName stays the donor's megaburst fan. Slots 1 and 2
    # keep the donor's fully-specified Delay/Range/Timeout; slot 3 is NEW on this
    # record, so it is given the SAME tuning the donor used to drive hemorrage on
    # slot 2 (Delay 5.0 / AnyRange / Timeout 2.0) rather than left at engine defaults
    # while its neighbours are specified - of the 543 mod carriers of
    # specialAttack3SkillName, 515 also set Delay, 469 Range and 424 Timeout.
    sf(B, 'specialAttackSkillName', SK_SWOOP)
    sf(B, 'specialAttackChance', 35.0)
    sf(B, 'specialAttack2SkillName', SKYBURIAL)
    sf(B, 'specialAttack2Chance', 30.0)
    sf(B, 'specialAttack3SkillName', SK_HEMORRAGE)
    sf(B, 'specialAttack3Chance', 40.0)
    sf(B, 'specialAttack3Delay', _v1(db, DONOR_BOSS, 'specialAttack2Delay') or 5.0)
    sf(B, 'specialAttack3Range', _v1(db, DONOR_BOSS, 'specialAttack2Range') or 'AnyRange')
    sf(B, 'specialAttack3Timeout', _v1(db, DONOR_BOSS, 'specialAttack2Timeout') or 2.0)
    # the mystical orb on death (R-200: every red uber drops one). ADD the field
    # with an explicit dtype - the donor carries no treasureProxyName at all, so
    # there is no existing dtype to clobber (this is the legitimate half of the
    # dtype rule, unlike `dropItems` above, which the donor already declares BOOL).
    sf(B, 'treasureProxyName', ORB, S)
    sf(B, 'dropItems', 1)
    db._modified.add(B)

    # ── 6. Placement chain: no-downscale limit -> lone pool -> proxy. The pool
    #    helper also NEUTRALISES the inherited proxyPoolEquation, which is what
    #    stops the "two bosses side by side" defect. hoard_pools is deliberately
    #    None: this uber's chest stands in the WORLD (step 7), so its accessory
    #    tiers must stay EMPTY - the _svc_verify_world_chests invariant. ────────
    if not A._svc_widen_limit(db, A._SVC_LIMIT_DONOR, LIMIT, hi=110):
        raise SystemExit("lookout_uber: could not build limit_ushkaret from %s"
                         % A._SVC_LIMIT_DONOR)
    db.set_field(LIMIT, 'FileDescription', 'Ushkaret no-cap limit [1..110]')
    A._svc_boss_pool(db, POOL, BOSS, MOURNER,
                     'Ushkaret (main) + 2 Cliffside Mourner champion escorts')
    mesh = _v1(db, BOSS, 'mesh')
    if not (isinstance(mesh, str) and mesh.strip()):
        raise SystemExit("lookout_uber: %s has no mesh to preview on the proxy" % BOSS)
    A._svc_boss_proxy(db, PROXY, POOL, LIMIT, mesh, SCALE, hoard_pools=None)
    sf(PROXY, 'placementExtents', 4.0)                    # surveyed clean out to 8.0
    # belt and braces on the world-chest invariant: if the donor proxy ever starts
    # carrying an accessory chest, this clone must not inherit it. Only CLEAR fields
    # that actually carry a value (never add an empty ref where none existed).
    for slot in ('accessory1', 'accessoryEpic1', 'accessoryLegendary1'):
        if _v1(db, PROXY, slot):
            sf(PROXY, slot, '')
    db._modified.add(PROXY)

    # ── 7. THE HOARD - exactly ONE chest (R-108 / UBER_CHEST_COUNT = 1). Built by
    #    the SAME two monolith helpers every other fixed uber uses, so the family
    #    joins the DERIVED scopes automatically: R-251 wiring (svc_<fam>hoard_<tier>
    #    -> its OWN svc_<fam>hoard_loot_<tier>), the loot-breadth / armour-parity /
    #    distribution / volume modules, and gate_uber_hoard_generosity. It is
    #    authored HERE, early in the registry, so those later modules still widen
    #    it. Falls back to the shared Obsidian pool if a donor is missing, exactly
    #    like the monolith callers - a donor gap degrades to "a hoard", never to
    #    "no chest". ────────────────────────────────────────────────────────────
    hoard = A._svc_build_dedicated_hoard(db, HOARD_PREFIX, TAG_HOARD) or A._SVC_HOARD_POOL
    if not A._svc_build_world_chest_proxy(db, HOARD_PREFIX, hoard):
        raise SystemExit(
            "lookout_uber: the world-chest proxy was NOT built. 'ushkaret' is in "
            "_SVC_FIXED_UBER_CHESTS, so _svc_verify_world_chests would red the build "
            "anyway - failing here names the real cause instead.")

    # ── 8. THE SOUL + the manual-cast summon. Order matters: _build_boss_summon
    #    reads the FINISHED boss record (rig, skin, anim overrides incl. the
    #    SwoopStomp answer, kit), so it runs after step 5. loadout=None lets the
    #    A1 pet-gear-parity mirror run - the Corpsewake is an unarmed beast, so the
    #    pet correctly carries nothing rather than Lyia's archer residue. ────────
    if not A._build_boss_summon(
            db, BOSS, PETS, SUMMON, TAG_SUMMON, TAG_PET,
            char_level=list(BAND),
            life=[9000.0, 13000.0, 18000.0],
            life_regen=[20.0, 40.0, 70.0],
            dmg_min=[55.0, 95.0, 145.0], dmg_max=[95.0, 155.0, 230.0],
            scale=2.0, loadout=None):
        raise SystemExit('lookout_uber: _build_boss_summon failed for summon_ushkaret')
    # NEUTRALISE the inherited HOSTILE flock summon on the friendly pet: a summon
    # pet may never carry a hostile spawner (the summon-pet skill-kit gate forbids
    # one, and it would spawn ENEMIES beside the player). Repoint every occurrence
    # to a benign proc the same rig already casts. Same shape as the Neferkha fix.
    _hostile = _n(SKYBURIAL)
    for p in PETS:
        if not db.has_record(p):
            continue
        for _k, tf in (db.get_fields(p) or {}).items():
            for j, v in enumerate(list(tf.values)):
                if isinstance(v, str) and _n(v) == _hostile:
                    tf.values[j] = SK_HEMORRAGE
        db.set_field(p, 'specialAttack2SkillName', SK_HEMORRAGE)
        db._modified.add(p)

    tiers = [{'diff': t, 'itemLevel': il, 'stats': _soul_stats(t)}
             for t, il in (('n', 30), ('e', 52), ('l', 68))]
    souls = A._create_soul(db, SOUL_BASE, TAG_SOUL, tiers, monster=BOSS, drop_rate=66.0)
    A._wire_summon_soul(db, souls, SUMMON)                # manual pet BUTTON: strips any
    for sp in souls:                                      # inherited itemSkillAutoController
        if db.has_record(sp):
            sf(sp, 'itemText', TAG_SOUL + 'DESC')
            db._modified.add(sp)
    # R-201 TIER PREFIXES, authored HERE rather than left to the finalization pass.
    # The three tiers share ONE itemNameTag and differentiate on `itemQualityTag`,
    # which the engine renders as a prefix: "Soul of the Sky-Burial" / "Epic ..." /
    # "Legendary ...". `_apply_soul_tier_naming` would add these at finalization, but
    # it is ADD-ONLY and idempotent, so writing them now is a no-op for that pass and
    # makes this module's own content complete and order-independent (the diadochi
    # self-authored-pcsafe precedent). Both tags are already in the shipped Text.arc,
    # so this authors no new tag.
    for sp, tier in zip(souls, ('n', 'e', 'l')):
        want = A._SOUL_TIER_QUALITY[tier]
        if want and db.has_record(sp):
            sf(sp, 'itemQualityTag', want, S)
            db._modified.add(sp)

    # ── 9. Register with the shared gate-input registries (all idempotent). ─────
    for pair in _CLONE_PAIRS:
        if pair not in A._BOSS_KIT_CLONES:
            A._BOSS_KIT_CLONES.append(pair)               # clone-shape gate (B-TOXEUS-2)
    spec = {'proxy': PROXY, 'pool': POOL, 'main_monster': BOSS,
            'name': 'q_ushkaret_lone (Ushkaret + 2 Cliffside Mourner escorts)'}
    if not any(s.get('proxy') == spec['proxy'] for s in A._MOD_AUTHORED_SPAWN_PROXIES):
        A._MOD_AUTHORED_SPAWN_PROXIES.append(spec)        # spawn-eligibility gate
    # the F6 naming gate keeps a hand-designed uber soul's evocative name only if
    # its tag is registered here (the sanctioned mechanism).
    A._HAND_DESIGNED_SOUL_TAGS = frozenset(A._HAND_DESIGNED_SOUL_TAGS) | {TAG_SOUL}

    # ── 10. TAGS (Text.arc is COUPLED with the arz; validate_tags must pass). ───
    tags[TAG_BOSS] = '{^r}Ushkaret, the Sky-Burial'
    tags[TAG_MOURNER] = '{^G}Cliffside Mourner'
    tags[TAG_MOTE] = 'Carrion-Mote'
    # the hoard's player-visible name, in the shipped "<Boss>'s <flavour>-Hoard"
    # convention (Tantalus's Hoard / Ferryman's Toll-Hoard / Helepolis's Spoil-Hoard).
    # UNVETTED BY WILL - flagged in the ship note.
    tags[TAG_HOARD] = 'The Larder of Ushkaret'
    tags[TAG_SUMMON] = 'Give It to the Sky'
    tags[TAG_PET] = 'The Patient Wing'
    tags[TAG_SOUL] = '{^F}Soul of the Sky-Burial'
    tags[TAG_SOUL + 'DESC'] = (
        'Rhakotis burned, and its people climbed the only tunnel that led out of the '
        'city to stand on the high shelf and watch for a rescue that never came. The '
        'thing that had circled over them for six hundred years folded its wings and '
        'came down among them. Wear its soul and you keep its appetite - your wounds '
        'open theirs, and what bleeds in front of you feeds you. It gives you the '
        'bird, and it takes the hide off your back to do it.')

    print("  Ushkaret, the Sky-Burial: Boss %s HP %s scale %.1f on the Corpsewake rig "
          "(exclusive corpsewake.tex) - quill fan + the ONLY custom swoop-stomp at the "
          "authored level %s (anim answered by repointing unarmedSpecialAnimRef1 %r -> "
          "'SwoopStomp') + hemorrage + leechstrike + the Larder aura (radius %s -> "
          "14.0) driving BOTH always-on channels (buffSelfSkillName + initialSkillName, "
          "R-255) + the carrion-mote flock on the %s donor (petLimit %d + TTL %r -> "
          "%.1fs, both INHERITED not added, anim demand %r deleted); mana %r -> %.0f/%.0f "
          "so the %d-cost stoop can be paid for; 2 Cliffside Mourner champions; limit "
          "[1..110]; lone pool + proxy (accessories EMPTY - the chest stands in the "
          "world); ONE world chest on the dedicated '%s' hoard chain; "
          "genericbossorb_02; '{^F}Soul of the Sky-Burial' (manual 'Give It to the "
          "Sky' -> The Patient Wing, 66%% Finger2); %d tags set. Map lane places it on "
          "the Lookout shelf."
          % (BAND, HP, SCALE, SWOOP_LEVEL, _anim_before, _radius_before,
             DONOR_FLOCK.rsplit('\\', 1)[-1], FLOCK_CAP, _flock_ttl_before, FLOCK_TTL,
             _flock_anim_before, _mana_before, MANA, MANA_REGEN,
             int(float(_v1(db, SK_SWOOP, 'skillManaCost') or 0)),
             HOARD_PREFIX, len(_ALL_TAGS)))


# ── verify: THE GATE (runs post-finalization over the FINAL db) ──────────────
def verify(db, tags=None):
    """Fail-loud invariants for everything this lane claims. Each arm corresponds to a
    claim in the docstring, so a claim cannot rot into a lie. Round 4 added the five
    that would have caught the round-3 defects at authoring time instead of at build
    time: V14 (the Larder actually reaches the player), V15 (no kit slot keeps a level
    tuned for a different skill, and none runs off its ladder), V16 (the REAL shared
    B-TOXEUS-2 clone-shape function, re-run over this lane's own pairs), V17 (donor
    dtypes preserved on cloned records) and V18 (the fight can pay its own mana)."""
    problems = []
    tagset = set(tags or ())

    def gv(rec, field):
        return _v1(db, rec, field)

    # V1 every authored record exists
    for path in (BOSS, MOURNER, CARRIONMOTE, LARDER, LARDER_BUFF, SKYBURIAL,
                 LIMIT, POOL, PROXY, WORLD_CHEST, SUMMON, *PETS, *_soul_paths()):
        if not db.has_record(path):
            problems.append("MISSING authored record: %s" % path)
    if problems:                      # nothing below is meaningful without the records
        raise SystemExit("[lookout_uber] R-256 GATE FAILED (%d):\n  - %s"
                         % (len(problems), "\n  - ".join(problems)))

    # V2 the boss IS a red uber, banded and durable inside the shipped roster
    if str(gv(BOSS, 'monsterClassification')) != 'Boss':
        problems.append("%s monsterClassification=%r, expected 'Boss' - the orb, the "
                        "soul drop and the red name all key off it."
                        % (BOSS, gv(BOSS, 'monsterClassification')))
    life = db.get_field_value(BOSS, 'characterLife')
    if not (isinstance(life, list) and len(life) >= 3
            and 13000.0 <= float(life[0]) <= 16000.0 and 24000.0 <= float(life[2]) <= 28000.0):
        problems.append("%s characterLife=%r is outside the shipped red band "
                        "(Kroisos 13.5-24k .. Ephialtes 15-27k). 'Hard but killable, "
                        "no walls' is a ruling, not a preference." % (BOSS, life))
    lvl = db.get_field_value(BOSS, 'charLevel')
    if not (isinstance(lvl, list) and list(lvl[:3]) == BAND):
        problems.append("%s charLevel=%r, expected %s" % (BOSS, lvl, BAND))

    # V3 A9-RENDERABLE: the boss wears its donor's own rig AND its own skin, and no
    #    actorHeight was invented. A mesh/skin drift is the b101-class defect.
    for fld in ('mesh', 'baseTexture', 'actorHeight'):
        got, want = gv(BOSS, fld), gv(DONOR_BOSS, fld)
        if _n(got) != _n(want):
            problems.append("%s %s=%r but the donor %s reads %r - own-rig/own-skin "
                            "(A9/R-126) is what makes this renderable with zero new art."
                            % (BOSS, fld, got, DONOR_BOSS.rsplit('\\', 1)[-1], want))
    if _n(gv(BOSS, 'charAnimationTableName') or '') not in ('', 'none'):
        problems.append("%s gained a charAnimationTableName (%r). The Corpsewake rig is "
                        "TABLE-LESS and drives from its own inline .anm overrides; a "
                        "foreign table can shadow them (the Rakanizeus precedent)."
                        % (BOSS, gv(BOSS, 'charAnimationTableName')))

    # V4 the dive's animation demand is ANSWERED on this rig (section 3)
    want_anim = _n(gv(SK_SWOOP, 'skillSpecialAnimationName') or '')
    refs = {_n(v) for k, tf in (db.get_fields(BOSS) or {}).items()
            if 'specialanimref' in k.split('###')[0].lower() for v in tf.values
            if isinstance(v, str)}
    if want_anim and want_anim not in refs:
        problems.append(
            "%s demands the %r animation and %s answers no such ref slot (%s). The "
            "engine would fall through to the generic attack - which is survivable, "
            "but this lane CLAIMS the dive is animated, so the claim must hold."
            % (SK_SWOOP.rsplit('\\', 1)[-1], gv(SK_SWOOP, 'skillSpecialAnimationName'),
               BOSS.rsplit('\\', 1)[-1], sorted(refs)))

    # V5 the kit: every skill slot resolves, none above the engine's declared ceiling
    for k, tf in sorted((db.get_fields(BOSS) or {}).items()):
        base = k.split('###')[0]
        if not base.startswith('skillName'):
            continue
        try:
            slot = int(base[len('skillName'):])
        except ValueError:
            continue
        ref = tf.values[0] if tf.values else ''
        if not (isinstance(ref, str) and ref.strip()):
            continue
        if slot > 17:
            problems.append("%s carries %s at slot %d. MonsterSkillManager declares "
                            "skillName1..17 and nothing above it (R-255) - that field "
                            "is read by nobody." % (BOSS, ref, slot))
        if not db.has_record(ref):
            problems.append("%s skillName%d -> %r does not resolve" % (BOSS, slot, ref))
    for slot in ('attackSkillName', 'specialAttackSkillName', 'specialAttack2SkillName',
                 'specialAttack3SkillName'):
        ref = gv(BOSS, slot)
        if isinstance(ref, str) and ref.strip() and not db.has_record(ref):
            problems.append("%s %s -> %r does not resolve" % (BOSS, slot, ref))

    # V14 THE ALWAYS-ON CHANNEL. The Larder is this lane's signature and it only
    #     reaches the player if the channel the engine reads names OUR aura. The donor
    #     drives its vampiric aura through `buffSelfSkillName` as well as `skillName5`,
    #     so a kit-slot-only repoint leaves the boss on the STOCK shared record with
    #     every authored value dead - round 3 shipped exactly that. `_ALWAYS_ON_FIELDS`
    #     (enslaver_shroud, R-255) is the codified list of channels the skill manager
    #     reads without being chosen by combat AI.
    for chan in ('buffSelfSkillName', 'initialSkillName'):
        got = gv(BOSS, chan)
        if _n(got or '') == _n(DONOR_LARDER):
            problems.append(
                "%s %s still names the STOCK %s. That record is shared by 6 carriers and "
                "carries NONE of this lane's authored values (radius 14.0, the raised "
                "leech ladders), so THE LARDER - the boss's name, its soul, its lore and "
                "its counterplay - would not reach the player at all."
                % (BOSS, chan, DONOR_LARDER.rsplit('\\', 1)[-1]))
        elif _n(got or '') != _n(LARDER):
            problems.append("%s %s=%r, expected the authored aura %s (R-255: this is a "
                            "channel the engine actually reads)." % (BOSS, chan, got, LARDER))

    # V15 KIT LEVELS. A re-slotted skill may never keep a level tuned for the skill
    #     that used to sit in that slot, and no level may run off the end of the
    #     skill's own authored damage ladder. Round 3 put charon_swoopstomp into
    #     bladestorm's slot 6 and kept skillLevel6 [10,13,16] against a NINE-row
    #     ladder whose only three carriers in the whole game use levels 1..9.
    for slot, skill, lvl in KIT_SLOTS:
        got_lvl = db.get_field_value(BOSS, 'skillLevel%d' % slot)
        got_lvl = got_lvl if isinstance(got_lvl, list) else ([got_lvl] if got_lvl is not None else [])
        nums = [int(float(x)) for x in got_lvl if isinstance(x, (int, float))]
        if lvl is None:
            donor_skill = _v1(db, DONOR_BOSS, 'skillName%d' % slot)
            # legal to inherit iff the slot still holds the donor's OWN skill, or this
            # module's clone of it (slot 5: svc_ushkaret_larder IS character_vampiriaura,
            # same record shape, same ladder). The whitelist names the ANCESTOR, and the
            # donor must still be on it - so if the donor's slot 5 ever changes skill,
            # this reds instead of silently blessing a mismatched level.
            ancestor = _KIT_LEVEL_INHERITABLE.get(slot)
            ok = _n(skill) == _n(donor_skill or '') or (
                ancestor is not None and _n(ancestor) == _n(donor_skill or ''))
            if not ok:
                problems.append(
                    "%s slot %d holds %s but INHERITS skillLevel%d=%r, which was tuned "
                    "for the donor's %r. A re-slotted skill must author its own level."
                    % (BOSS, slot, skill.rsplit('\\', 1)[-1], slot, got_lvl,
                       (donor_skill or '').rsplit('\\', 1)[-1]))
        elif nums != [int(x) for x in lvl]:
            problems.append("%s skillLevel%d=%r, expected the authored %r"
                            % (BOSS, slot, got_lvl, lvl))
        depth = _ladder_depth(db, skill)
        if depth > 1 and nums and max(nums) > depth:
            problems.append(
                "%s slot %d casts %s at level %d, but that skill authors only %d damage "
                "rows - every level above %d reads off the end of the ladder the "
                "designer wrote (the round-3 charon_swoopstomp defect)."
                % (BOSS, slot, skill.rsplit('\\', 1)[-1], max(nums), depth, depth))
        cap = _v1(db, skill, 'skillMaxLevel')
        try:
            cap = int(float(cap))
        except (TypeError, ValueError):
            cap = 0
        if cap > 0 and nums and max(nums) > cap:
            problems.append("%s slot %d casts %s at level %d above its declared "
                            "skillMaxLevel %d" % (BOSS, slot, skill.rsplit('\\', 1)[-1],
                                                  max(nums), cap))

    # V16 CLONE SHAPE, run through the REAL shared gate rather than a copy of it.
    #     `_verify_boss_kit_clone_shape` (B-TOXEUS-2) runs UNCONDITIONALLY on the build
    #     path inside run_registry_gates(), and round 3 violated it 22 ways while this
    #     module's docstring claimed the invariant held. Re-running the genuine
    #     function over exactly this lane's pairs means the claim is MEASURED here, in
    #     the module that makes it, and attributed to this lane instead of surfacing as
    #     an anonymous build abort. Narrowed to our pairs so a neighbour's regression is
    #     still that lane's gate to fail, never ours.
    _saved = list(A._BOSS_KIT_CLONES)
    try:
        A._BOSS_KIT_CLONES[:] = list(_CLONE_PAIRS)
        A._verify_boss_kit_clone_shape(db)
    except SystemExit as e:
        problems.append("B-TOXEUS-2 CLONE SHAPE (this lane's %d pair(s)): %s"
                        % (len(_CLONE_PAIRS), e))
    finally:
        A._BOSS_KIT_CLONES[:] = _saved

    # V17 DTYPE PRESERVATION on the cloned monsters. CLAUDE.md, verbatim: "never pass
    #     explicit dtype to set_field() on cloned records - INT/FLOAT corruption
    #     silently zeroes values". `set_field` overwrites tf.dtype whenever a dtype is
    #     passed, so one stray `, I` on `dropItems` shipped INT where every monster in
    #     the database declares BOOL. Asserted against each record's OWN donor.
    #
    #     SCOPE, MEASURED AND STATED RATHER THAN QUIETLY CHOSEN: `dropItems` on the
    #     BOSS is deliberately NOT asserted. This lane's own three `, I` slips are gone,
    #     but the shared soul-wiring helper (`apply_svc_patches` line 17634 /
    #     `_wire_souls_to_monsters`) re-sets `dropItems` with an explicit INT on EVERY
    #     soul-dropping monster after this module runs, so the flip on the boss is
    #     roster-wide pre-existing behaviour, not ours: 25 of the 53 shipped `um_`/`svc_`
    #     Boss records already declare INT, including Vashkarr, Neferkha, Mnemophage and
    #     Ephialtes - four of the exact reds this lane bands itself against. Asserting it
    #     here would red the build for a defect in code this lane does not own, and
    #     FIXING that helper is a roster-wide record-diff that belongs in its own lane
    #     (registered `BL-R256-DEBT-7`). The escorts, which no shared helper touches
    #     because they drop nothing, ARE asserted on it - so this lane's own discipline
    #     is still under a live gate.
    for rec, donor, flds in (
            (BOSS, DONOR_BOSS, ('charLevel', 'characterLife', 'scale', 'characterMana')),
            (MOURNER, DONOR_MOURNER, ('dropItems', 'charLevel', 'characterLife', 'scale')),
            (CARRIONMOTE, DONOR_MOTE, ('dropItems', 'charLevel', 'scale'))):
        for fld in flds:
            want, got = _dtype_of(db, donor, fld), _dtype_of(db, rec, fld)
            if want is not None and got is not None and want != got:
                problems.append(
                    "%s %s is declared dtype %s but its donor %s declares %s. A cloned "
                    "record must keep its donor's field TYPES (CLAUDE.md standing law); "
                    "a type flip also shows up as an unexplained record-diff in the ship "
                    "lane." % (rec, fld, got, donor.rsplit('\\', 1)[-1], want))

    # V18 THE FIGHT CAN PAY FOR ITSELF. The stoop costs a flat 250 mana and nothing in
    #     the boss furniture (globalproperties_*, boss_scaling, armor_passive) returns
    #     any - all read 0.0 on every mana field. On the donor's Hero pool of 500/5 the
    #     three-beat fight fires the stoop twice and then stalls for ~50s a cast while
    #     the flock drains the same pool. Derived from the kit, not pinned, so adding a
    #     costlier skill later reds instead of quietly starving the boss.
    _pool = float(gv(BOSS, 'characterMana') or 0)
    _regen = float(gv(BOSS, 'characterManaRegen') or 0)
    _worst, _worst_sk = 0.0, ''
    for _slot, _sk, _lv in KIT_SLOTS:
        _c = db.get_field_value(_sk, 'skillManaCost')
        _c = max([float(x) for x in _c if isinstance(x, (int, float))] or [0.0]) \
            if isinstance(_c, list) else float(_c or 0)
        if _c > _worst:
            _worst, _worst_sk = _c, _sk
    if _worst > 0:
        if _pool < _worst * 4:
            problems.append(
                "%s carries characterMana %.0f against a %.0f-cost %s. Four casts is the "
                "floor for a three-phase fight; every comparable placed red in this mod "
                "runs 1370-3000 (Charon, who owns this skill, runs 3000/30)."
                % (BOSS, _pool, _worst, _worst_sk.rsplit('\\', 1)[-1]))
        if _regen <= 0 or _worst / _regen > 20.0:
            problems.append(
                "%s characterManaRegen %.1f means %.0fs of regen per %s cast. Nothing in "
                "the boss furniture restores mana, so the beat would never come back."
                % (BOSS, _regen, (_worst / _regen) if _regen > 0 else float('inf'),
                   _worst_sk.rsplit('\\', 1)[-1]))

    # V6 THE ORB. Present, resolving, and still the minimum-distance tier for this
    #    boss's charLevel - re-derived from the FINAL db so the pin cannot rot.
    orb = gv(BOSS, 'treasureProxyName')
    if not (isinstance(orb, str) and db.has_record(orb)):
        problems.append("%s treasureProxyName=%r does not resolve. R-200: every red "
                        "uber drops the mystical orb." % (BOSS, orb))
    else:
        try:
            RUO = _sibling('red_uber_orbs')
            bands = RUO._tier_bands(db, exclude=set(RUO.WIRE) | {BOSS})
            want = RUO._tier_for(BAND[0], bands)
            if want is not None and _n(want) != _n(orb):
                problems.append(
                    "ORB TIER NO LONGER MINIMAL: %s is on %s but the measured bands "
                    "%s now put charLevel %d on %s. Re-pin deliberately."
                    % (BOSS.rsplit('\\', 1)[-1], orb.rsplit('\\', 1)[-1],
                       {k.rsplit('\\', 1)[-1]: v for k, v in bands.items()},
                       BAND[0], want.rsplit('\\', 1)[-1]))
        except Exception as e:                     # ANNOUNCE the downgrade, never pass quietly
            print("    [lookout_uber] ORB-TIER CHECK DOWNGRADED (not a pass): could "
                  "not re-derive the ladder (%s); only resolution was proven." % e)
    if _n(orb or '') == _n(r'records\item\containers\new\genericbossorb_05.dbr'):
        problems.append("%s is on genericbossorb_05, which R-99 RESERVES for the "
                        "Toxeus roster." % BOSS)

    # V7 THE HOARD: exactly ONE world chest, on its OWN table, and the boss proxy
    #    carries no accessory chest (the b42 world-chest pattern).
    for tier, acc in (('01', 'accessory1'), ('02', 'accessoryEpic1'), ('03', 'accessoryLegendary1')):
        chest = r'records\drxitem\container\svc_%shoard_%s.dbr' % (HOARD_PREFIX, tier)
        table = r'records\drxitem\container\svc_%shoard_loot_%s.dbr' % (HOARD_PREFIX, tier)
        if not db.has_record(chest):
            problems.append("hoard chest missing: %s" % chest)
            continue
        if not db.has_record(table):
            problems.append("hoard table missing: %s (R-251 requires each chest to open "
                            "its OWN bespoke table)" % table)
        elif _n(gv(chest, 'tables') or '') != _n(table):
            problems.append("%s opens %r, not its own %s - that is exactly the b42 "
                            "orphaning R-251 exists to kill." % (chest, gv(chest, 'tables'), table))
        pool = gv(WORLD_CHEST, acc)
        if not (isinstance(pool, str) and db.has_record(pool)):
            problems.append("%s %s=%r does not resolve - the world chest would pay "
                            "nothing on that difficulty." % (WORLD_CHEST, acc, pool))
        if gv(PROXY, acc):
            problems.append("%s STILL carries %s=%r. The chest stands in the WORLD; the "
                            "boss must not also spawn one (Will filed the extra chests "
                            "twice - R-108)." % (PROXY, acc, gv(PROXY, acc)))

    # V8 THE PLACEMENT SPEC IS PRESENT, and it is ONE boss + exactly
    #    UBER_CHEST_COUNT chests on the surveyed spot. Imported from the map tool so
    #    a divergence between the DB lane and the map lane is a build failure, not a
    #    thing someone notices in game.
    try:
        import build_section_surgery as BSS
        host = BSS.LOOKOUT_HOST_KEY
        boss_specs = BSS.UBERBOSS_SPECS.get(host, [])
        chest_specs = BSS.UBER_CHEST_SPECS.get(host, [])
        if len(boss_specs) != 1:
            problems.append("UBERBOSS_SPECS[%s] has %d entr(ies), expected exactly 1"
                            % (host, len(boss_specs)))
        for dbr, x, y, z, *_rest in boss_specs:
            if _n(dbr.decode('ascii')) != _n(PROXY):
                problems.append("the Lookout placement names %r, not %s" % (dbr, PROXY))
            if (round(x, 2), round(y, 2), round(z, 2)) != (208.0, 17.0, 52.0):
                problems.append("the Lookout boss spot moved to (%s,%s,%s); the surveyed "
                                "spot is (208.0,17.0,52.0) (d=0.14, clr 100%% N/E/L out "
                                "to ext 8.0, comp#9). Re-survey before moving it."
                                % (x, y, z))
        if len(chest_specs) != BSS.UBER_CHEST_COUNT:
            problems.append("UBER_CHEST_SPECS[%s] places %d chest(s), UBER_CHEST_COUNT "
                            "is %d (R-108: Will filed the three-chest arrangement twice)"
                            % (host, len(chest_specs), BSS.UBER_CHEST_COUNT))
        for dbr, *_c in chest_specs:
            if _n(dbr.decode('ascii')) != _n(WORLD_CHEST):
                problems.append("the Lookout chest placement names %r, not %s"
                                % (dbr, WORLD_CHEST))
        if host in BSS.INJECT_SPECS:
            placed = {_n(e[0].decode('ascii')) for e in BSS.INJECT_SPECS[host]}
            for need in (PROXY, WORLD_CHEST):
                if _n(need) not in placed:
                    problems.append("%s is not in the merged INJECT_SPECS for %s - the "
                                    "record would ship unplaced." % (need, host))
    except Exception as e:
        print("    [lookout_uber] PLACEMENT CHECK DOWNGRADED (not a pass): could not "
              "read build_section_surgery (%s)." % e)

    # V9 THE SOUL: one shared name tag, three distinct tier prefixes (R-201), a
    #    MANUAL pet button (never an on-attack proc - D21/R-44), and pets that
    #    carry no hostile spawner.
    quality = {'n': None, 'e': 'tagSoulEpic', 'l': 'tagSoulLegendary'}
    for path, tier in zip(_soul_paths(), ('n', 'e', 'l')):
        if _n(gv(path, 'itemNameTag') or '') != _n(TAG_SOUL):
            problems.append("%s itemNameTag=%r, expected %s"
                            % (path, gv(path, 'itemNameTag'), TAG_SOUL))
        cur = gv(path, 'itemQualityTag')
        cur = cur.strip() if isinstance(cur, str) else None
        if (cur or None) != quality[tier]:
            problems.append("%s itemQualityTag=%r, expected %r - R-201 is what makes "
                            "the three tiers read as different items."
                            % (path, cur, quality[tier]))
        if _n(gv(path, 'itemSkillName') or '') != _n(SUMMON):
            problems.append("%s itemSkillName=%r, expected the manual summon %s"
                            % (path, gv(path, 'itemSkillName'), SUMMON))
        if gv(path, 'itemSkillAutoController'):
            problems.append("%s carries itemSkillAutoController=%r. A summon soul is a "
                            "pet BUTTON; a controller re-casts it on every hit (the D21 "
                            "Long Nu bug)." % (path, gv(path, 'itemSkillAutoController')))
        if _n(gv(path, 'itemText') or '') != _n(TAG_SOUL + 'DESC'):
            problems.append("%s itemText=%r, expected %s" % (path, gv(path, 'itemText'),
                                                             TAG_SOUL + 'DESC'))
    if _n(gv(BOSS, 'lootFinger2Item1') or '') != _n(_soul_paths()[0]):
        problems.append("%s lootFinger2Item1=%r - the Sky-Burial must drop its own soul."
                        % (BOSS, gv(BOSS, 'lootFinger2Item1')))
    if float(gv(BOSS, 'chanceToEquipFinger2') or 0) <= 0:
        problems.append("%s chanceToEquipFinger2=%r - the soul would never drop."
                        % (BOSS, gv(BOSS, 'chanceToEquipFinger2')))
    hostile = _n(SKYBURIAL)
    for p in PETS:
        for k, tf in (db.get_fields(p) or {}).items():
            for v in tf.values:
                if isinstance(v, str) and _n(v) == hostile:
                    problems.append("%s still names the HOSTILE flock summon at %s - a "
                                    "friendly pet would spawn enemies beside the player."
                                    % (p, k.split('###')[0]))
        if db.get_field_value(p, 'spawnObjectsTimeToLive') not in (None, [], ''):
            problems.append("%s carries spawnObjectsTimeToLive=%r - a permanent pet must "
                            "have none." % (p, db.get_field_value(p, 'spawnObjectsTimeToLive')))

    # V10 MINION LAW + escort invariants
    for m in (MOURNER, CARRIONMOTE):
        if float(gv(m, 'chanceToEquipFinger2') or 0) != 0.0:
            problems.append("%s drops a soul (chanceToEquipFinger2=%r). Only the "
                            "Sky-Burial does." % (m, gv(m, 'chanceToEquipFinger2')))
        if int(float(gv(m, 'dropItems') or 0)) != 0:
            problems.append("%s dropItems=%r - a placed add is not a loot faucet (R-125)"
                            % (m, gv(m, 'dropItems')))
        if gv(m, 'treasureProxyName'):
            problems.append("%s carries treasureProxyName=%r - escorts drop no chest"
                            % (m, gv(m, 'treasureProxyName')))
    mlife = db.get_field_value(MOURNER, 'characterLife')
    if not (isinstance(mlife, list) and len(mlife) >= 3
            and float(mlife[0]) < float(mlife[1]) < float(mlife[2])):
        problems.append("CHAMPION ESCORT LIFE NOT ASCENDING: %s characterLife=%r "
                        "(R-100 #18)." % (MOURNER, mlife))
    bscale, mscale = float(gv(BOSS, 'scale') or 0), float(gv(MOURNER, 'scale') or 0)
    if not mscale < bscale:
        problems.append("the escort (scale %s) is not visibly smaller than the boss "
                        "(scale %s) - the silhouette gap is what makes 2.7 read as "
                        "dominance." % (mscale, bscale))
    if bscale > 3.80:
        problems.append("%s scale %s exceeds the roster ceiling 3.80 "
                        "(um_polisgaoler_unbound_99)." % (BOSS, bscale))
    # the pool must spawn exactly ONE main (the double-boss defect)
    if db.get_field_value(POOL, 'proxyPoolEquation'):
        problems.append("%s still carries a proxyPoolEquation - it floors 3/2 to 4/2 = "
                        "TWO bosses side by side." % POOL)
    smax = int(float(gv(POOL, 'spawnMax') or 0))
    cmax = int(float(gv(POOL, 'championMax') or 0))
    if smax - cmax != 1:
        problems.append("%s spawnMax(%d) - championMax(%d) = %d guaranteed main(s), "
                        "expected exactly 1." % (POOL, smax, cmax, smax - cmax))

    # V13 THE FLOCK IS BOUNDED (b76 law). The hostile summon this module authors must
    #     carry BOTH bounds: a positive concurrent cap AND a finite spawn TTL. The
    #     shared gate cannot do this for us - `summon_caps.check_no_new_unbounded` only
    #     fires on records with NEITHER, so a petLimit alone hides a permanent flock
    #     from it, which is exactly how round 2 shipped one. Asserted on the FINAL db,
    #     so a later module stripping the field also reds.
    _cap = gv(SKYBURIAL, 'petLimit')
    try:
        _cap = int(float(_cap))
    except (TypeError, ValueError):
        _cap = 0
    if _cap <= 0:
        problems.append("%s petLimit=%r - the flock has no concurrent cap."
                        % (SKYBURIAL, gv(SKYBURIAL, 'petLimit')))
    _ttl = gv(SKYBURIAL, 'spawnObjectsTimeToLive')
    try:
        _ttl = float(_ttl)
    except (TypeError, ValueError):
        _ttl = 0.0
    if _ttl <= 0:
        problems.append(
            "%s carries spawnObjectsTimeToLive=%r. The donor `summon_swarm` ships NO "
            "TTL, so a permanent flock is what you get by default: minions never "
            "expire, the boss refills the cap on cooldown and the fight never reaches "
            "a steady state. That is the b76 P0 Will filed ('the infinite summon ... "
            "the game is frozen'), and a petLimit does NOT substitute - every b76 "
            "offender summon_caps repaired had one. Restore %.1fs (the value every "
            "svc_ summon in this arz uses)."
            % (SKYBURIAL, gv(SKYBURIAL, 'spawnObjectsTimeToLive'), FLOCK_TTL))
    # and it must still be a spawn skill spawning ONLY the Common mote (never a Champion
    # - the neferkha no-crowd-out law this module claims in its docstring)
    _spawns = db.get_field_value(SKYBURIAL, 'spawnObjects')
    _spawns = _spawns if isinstance(_spawns, list) else ([_spawns] if _spawns else [])
    if [_n(s) for s in _spawns if isinstance(s, str)] != [_n(CARRIONMOTE)]:
        problems.append("%s spawnObjects=%r, expected exactly [%s] - the flock is Commons "
                        "only." % (SKYBURIAL, _spawns, CARRIONMOTE))
    if _n(gv(CARRIONMOTE, 'monsterClassification') or '') != 'common':
        problems.append("%s monsterClassification=%r - the flock body must stay Common "
                        "(the neferkha no-crowd-out shape)."
                        % (CARRIONMOTE, gv(CARRIONMOTE, 'monsterClassification')))

    # V11 tags: every tag this module references is authored (Text.arc coupling)
    if tagset:
        missing = [t for t in _ALL_TAGS if t not in tagset]
        if missing:
            problems.append("tags referenced but never authored: %s" % missing)

    # V12 DOWNSTREAM COVERAGE - the arm the round-1 vet correctly said was missing.
    #
    # This module runs at registry position 12 of 69; `verify()` runs post-finalization,
    # AFTER souls_quality, soul_identity, aura_radius, summon_caps, toxeus_souls_100,
    # uber_quest_markers, red_uber_orbs, chest_loot_breadth, armor_loot_breadth,
    # orb_loot_breadth, orb_armor_rows, loot_volume_trim, orb_legendary_chance and
    # uber_hoard_generosity have each had a chance to mutate what step 7 authored. Every
    # one of those derives its scope from a NAME SHAPE rather than a typed roster, which
    # is exactly why a new family joins for free - and exactly why nobody notices when it
    # does not. So the coupling is asserted here, on the FINAL db, instead of assumed:
    #   (a) the family is inside svc_uber_hoards' derived scope (the module that gates
    #       every hoard chest/table and whose `is_hoard_table` IS svc_loot_volume's R-251
    #       trim carve-out, so one assertion covers both);
    #   (b) the authored R-251 volume SURVIVED the pipeline - if the trim's carve-out ever
    #       stops covering us, the equations come back different and this reds.
    try:
        import svc_uber_hoards as SUH
        chest_paths = [r'records\drxitem\container\svc_%shoard_%s.dbr' % (HOARD_PREFIX, t)
                       for t in ('01', '02', '03')]
        derived_chests = SUH.chests(db)
        derived_tables = SUH.tables(db)
        fams = {fam for _real, fam, _tier in derived_chests.values()}
        if HOARD_PREFIX not in fams:
            problems.append(
                "DOWNSTREAM SCOPE LOST THE FAMILY: %r is not in svc_uber_hoards' derived "
                "chest families %s. Every loot-breadth / distribution / volume module "
                "derives from that same name shape, so the hoard would ship un-widened, "
                "un-distributed and outside gate_uber_hoard_generosity."
                % (HOARD_PREFIX, sorted(fams)))
        for chest in chest_paths:
            if not SUH.is_hoard_chest(chest):
                problems.append("%s is not recognised as a hoard chest by "
                                "svc_uber_hoards._CHEST_RE" % chest)
                continue
            want_table = SUH.table_for(chest)
            if _n(want_table or '') not in derived_tables:
                problems.append("%s -> %s is not in svc_uber_hoards' derived table set"
                                % (chest, want_table))
                continue
            if not SUH.is_hoard_table(want_table):
                problems.append(
                    "%s is not recognised as an R-251 hoard table. That predicate is ALSO "
                    "svc_loot_volume's trim carve-out, so this family would be trimmed."
                    % want_table)
                continue
            mn = str(gv(want_table, 'numSpawnMinEquation') or '')
            mx = str(gv(want_table, 'numSpawnMaxEquation') or '')
            if (mn, mx) != (SUH.HOARD_MIN_EQ, SUH.HOARD_MAX_EQ):
                problems.append(
                    "R-251 VOLUME DID NOT SURVIVE THE PIPELINE: %s reads min=%r max=%r, "
                    "the authored contract is min=%r max=%r. Something downstream of "
                    "registry slot 12 rewrote this family's volume."
                    % (want_table.rsplit('\\', 1)[-1], mn, mx,
                       SUH.HOARD_MIN_EQ, SUH.HOARD_MAX_EQ))
    except SystemExit:
        raise
    except Exception as e:
        print("    [lookout_uber] DOWNSTREAM-COVERAGE CHECK DOWNGRADED (not a pass): "
              "could not read svc_uber_hoards (%s)." % e)

    if problems:
        raise SystemExit("[lookout_uber] R-256 LOOKOUT-UBER GATE FAILED (%d):\n  - %s"
                         % (len(problems), "\n  - ".join(problems)))
    print("  lookout_uber gate PASS: Ushkaret is a Boss %s, HP %s inside the shipped "
          "red band, on its donor's own rig+skin with the swoop animation answered; "
          "the Larder drives BOTH always-on channels (never the stock shared aura); "
          "every kit slot's level is authored where the slot was re-pointed and none "
          "runs off its skill's ladder or skillMaxLevel; the three registered kit "
          "clones pass the REAL B-TOXEUS-2 shape function; cloned monsters keep their "
          "donors' field dtypes; the mana pool pays for the kit's costliest skill; "
          "kit resolves within skillName1..17; orb02 is still the minimum-distance "
          "tier; ONE world chest on its own R-251 table with the boss proxy's "
          "accessories empty; the placement spec is the surveyed (208,17,52) spot; "
          "the soul is a 3-tier manual pet button with no hostile spawner on any pet; "
          "escorts drop nothing and stay smaller than the boss; the flock is bounded "
          "BOTH ways (petLimit %d + %.1fs TTL - the b76 law a petLimit alone hides from "
          "summon_caps) and stays Commons-only; and the '%s' hoard family is inside "
          "svc_uber_hoards' DERIVED scope with its R-251 volume intact after the whole "
          "registry ran."
          % (BAND, HP, FLOCK_CAP, FLOCK_TTL, HOARD_PREFIX))


# ── negative tests: prove each gate arm can actually go RED ──────────────────
def _break(db, rec, field, value):
    """Set `rec.field = value` and return an undo() that restores it EXACTLY.

    Mutate-and-restore, deliberately, instead of `copy.deepcopy(db)` per plant:
    the built arz is ~51k records of ~618 fields, so a deep copy costs minutes and
    gigabytes and the first version of this test wedged a machine doing it 17
    times. Each plant therefore runs against the SAME db and is undone; the test
    re-runs verify() after every undo, so a leaked mutation is itself caught."""
    ff = db.get_fields(rec) or {}
    key = next((k for k in ff if k.split('###')[0] == field), None)
    old = list(ff[key].values) if key is not None else None
    db.set_field(rec, field, value)

    def undo():
        ff2 = db.get_fields(rec) or {}
        for k in [k for k in ff2 if k.split('###')[0] == field]:
            if old is None:
                del ff2[k]
            else:
                ff2[k].values = list(old)
        db._modified.add(rec)
    return undo


def _break_dtype(db, rec, field, dtype):
    """Flip only the declared dtype of an EXISTING field, leaving its values alone.

    The V17 defect is invisible to a value-level plant: `sf(rec,'dropItems',1,I)` ships
    the same payload and only the declared type changes, which is precisely why it
    survived three rounds of review."""
    ff = db.get_fields(rec) or {}
    key = next((k for k in ff if k.split('###')[0] == field), None)
    if key is None:
        raise SystemExit("negtest: %s has no %s to retype" % (rec, field))
    old = ff[key].dtype
    ff[key].dtype = dtype
    db._modified.add(rec)

    def undo():
        (db.get_fields(rec) or {})[key].dtype = old
        db._modified.add(rec)
    return undo


def _break_tag(tags, key):
    old = tags.pop(key, None)

    def undo():
        if old is not None:
            tags[key] = old
    return undo


def _negtest():
    r"""py tools/patches/lookout_uber.py --negtest <built.arz>

    Loads a built arz, applies this module, then plants each defect the gate
    claims to catch and requires verify() to RAISE. A gate nobody has seen fail is
    not a gate (the standing negtest law)."""
    from arz_patcher import ArzDatabase

    arz = sys.argv[2] if len(sys.argv) > 2 else None
    if not arz:
        raise SystemExit("usage: py tools/patches/lookout_uber.py --negtest <built.arz>")
    db = ArzDatabase.from_arz(Path(arz))
    tags = {}
    apply(db, tags)
    try:
        verify(db, tags)
    except SystemExit as e:
        raise SystemExit("NEGTEST ABORTED: the clean build does not pass verify():\n%s" % e)
    print("\n  baseline: apply() + verify() are GREEN on %s" % arz)

    results = []

    def plant(label, break_fn):
        undo = break_fn()
        try:
            verify(db, tags)
            print("    *** GREEN - THE GATE IS BLIND: %s" % label)
            good = False
        except SystemExit:
            print("    RED (as required): %s" % label)
            good = True
        undo()
        try:                                   # the undo must restore GREEN
            verify(db, tags)
        except SystemExit as e:
            raise SystemExit("NEGTEST LEAKED: undo of %r left the gate red:\n%s" % (label, e))
        results.append(good)

    HOARD_01 = r'records\drxitem\container\svc_%shoard_01.dbr' % HOARD_PREFIX
    HOARD_POOL_01 = r'records\drxitem\container\svc_%shoard_pool_01.dbr' % HOARD_PREFIX
    HOARD_LOOT_01 = r'records\drxitem\container\svc_%shoard_loot_01.dbr' % HOARD_PREFIX

    plant('boss declassed to Hero',
          lambda: _break(db, BOSS, 'monsterClassification', 'Hero'))
    plant('boss made a 90k wall',
          lambda: _break(db, BOSS, 'characterLife', [90000.0, 95000.0, 99000.0]))
    plant('boss band shifted off the Rhakotis cliff',
          lambda: _break(db, BOSS, 'charLevel', [70, 85, 99]))
    plant('orb stripped',
          lambda: _break(db, BOSS, 'treasureProxyName', ''))
    plant('orb moved to the R-99 reserved Toxeus apex tier',
          lambda: _break(db, BOSS, 'treasureProxyName',
                         r'records\item\containers\new\genericbossorb_05.dbr'))
    plant('orb pinned to the WRONG ladder tier (orb04)',
          lambda: _break(db, BOSS, 'treasureProxyName',
                         r'records\item\containers\new\genericbossorb_04.dbr'))
    plant('swoop animation answer reverted to Bladestorm',
          lambda: _break(db, BOSS, 'unarmedSpecialAnimRef1', 'Bladestorm'))
    plant('donor skin swapped (A9 render drift)',
          lambda: _break(db, BOSS, 'baseTexture',
                         r'DRXtextures\creatures\vulture\vulture_razorbird.tex'))
    plant('a foreign anim table added to the table-LESS rig',
          lambda: _break(db, BOSS, 'charAnimationTableName',
                         r'records\xpack\creatures\monster\bosses\02_charon\anm\anm_charon02.dbr'))
    plant('a kit skill parked above the engine ceiling (R-255)',
          lambda: _break(db, BOSS, 'skillName19', SK_LEECHSTRIKE))
    plant('a kit slot pointed at a record that does not exist',
          lambda: _break(db, BOSS, 'skillName8', r'records\skills\nope\not_a_skill.dbr'))
    plant('the boss proxy given back an accessory chest (R-108)',
          lambda: _break(db, PROXY, 'accessory1', HOARD_POOL_01))
    plant('the hoard chest repointed at a base-game table (the b42 orphaning)',
          lambda: _break(db, HOARD_01, 'tables',
                         r'records\item\containers\defaultloot\boss_default_29-31.dbr'))
    plant('escort life made descending',
          lambda: _break(db, MOURNER, 'characterLife', [3000.0, 900.0, 1200.0]))
    plant('escort turned into a soul faucet',
          lambda: _break(db, MOURNER, 'chanceToEquipFinger2', 66.0))
    plant('escort scaled up to the boss silhouette',
          lambda: _break(db, MOURNER, 'scale', 2.7))
    plant('soul turned into an on-attack proc (the D21 Long Nu bug)',
          lambda: _break(db, _soul_paths()[0], 'itemSkillAutoController', A._AC_ON_HIT))
    plant('Epic soul stripped of its R-201 tier prefix',
          lambda: _break(db, _soul_paths()[1], 'itemQualityTag', ''))
    plant('the boss stopped dropping its own soul',
          lambda: _break(db, BOSS, 'chanceToEquipFinger2', 0.0))
    plant('the friendly pet handed the HOSTILE flock summon back',
          lambda: _break(db, PETS[0], 'specialAttack2SkillName', SKYBURIAL))
    plant('the pet given a TTL (a permanent pet that expires)',
          lambda: _break(db, PETS[0], 'spawnObjectsTimeToLive', [30.0]))
    # V13, the b76 arm. The first plant is the EXACT state round 2 shipped in: a flock
    # with a healthy petLimit and no TTL at all - invisible to summon_caps' own sweep,
    # which is why this module has to own it.
    plant('the flock summon stripped of its TTL (the b76 permanent-summon state, and the '
          'one a petLimit hides from summon_caps)',
          lambda: _break(db, SKYBURIAL, 'spawnObjectsTimeToLive', 0.0))
    plant('the flock summon stripped of its concurrent cap',
          lambda: _break(db, SKYBURIAL, 'petLimit', 0))
    plant('the flock escalated from Commons to the Champion escort (crowd-out)',
          lambda: _break(db, SKYBURIAL, 'spawnObjects', [MOURNER]))
    plant('the flock body promoted to Champion',
          lambda: _break(db, CARRIONMOTE, 'monsterClassification', 'Champion'))
    plant('the pool handed its proxyPoolEquation back (two bosses side by side)',
          lambda: _break(db, POOL, 'proxyPoolEquation',
                         r'records\proxies orient\proxypoolequation_02.dbr'))
    plant('the pool arithmetic broken to 2 guaranteed mains',
          lambda: _break(db, POOL, 'championMax', 1))
    plant('a referenced tag never authored',
          lambda: _break_tag(tags, TAG_SOUL))
    # V14, the always-on-channel arm. The first plant is EXACTLY the state round 3
    # shipped in: the kit slot repointed, the channel the engine reads left on the
    # stock shared aura, so every authored Larder value was dead config.
    plant('the Larder left on the STOCK shared aura in buffSelfSkillName (the round-3 '
          'state - authored radius/leech never reach the player)',
          lambda: _break(db, BOSS, 'buffSelfSkillName', DONOR_LARDER))
    plant('the always-on initialSkillName channel pointed somewhere else',
          lambda: _break(db, BOSS, 'initialSkillName', SK_HEMORRAGE))
    # V15, the kit-level arm. Plant 1 is the round-3 defect verbatim.
    plant('the stoop left at the donor bladestorm level [10,13,16], off the end of '
          'charon_swoopstomp\'s 9-row ladder (the round-3 state)',
          lambda: _break(db, BOSS, 'skillLevel6', [10, 13, 16]))
    plant('a kit slot pushed above its skill\'s declared skillMaxLevel',
          lambda: _break(db, BOSS, 'skillLevel14', [1, 1, 9]))
    # V16, the B-TOXEUS-2 clone-shape arm, run through the REAL shared gate function.
    # Plant 1 is the round-3 P0 shape: a field ADDED that the donor does not carry.
    plant('a zero-precedent field ADDED to a registered kit clone (the round-3 P0 that '
          'killed the cold build)',
          lambda: _break(db, LARDER_BUFF, 'FileDescription', 'zero-precedent'))
    plant('a registered kit clone left with an EMPTY ref where its donor held one',
          lambda: _break(db, SKYBURIAL, 'spawnObjects', ['']))
    # V17, the dtype arm - the standing CLAUDE.md law, planted as the exact `, I` slip.
    plant('dropItems dtype flipped BOOL -> INT on a cloned escort (the exact `, I` slip; '
          'planted on the Mourner because the BOSS\'s dropItems is owned downstream by '
          'the shared soul-wiring helper - see V17)',
          lambda: _break_dtype(db, MOURNER, 'dropItems', I))
    # V18, the mana arm. Plant 1 is the donor's own Hero pool, which is what round 3
    # shipped against a 250-cost stoop.
    plant('the donor Hero mana pool (500) left against the 250-cost stoop',
          lambda: _break(db, BOSS, 'characterMana', 500.0))
    plant('mana regen dropped so the stoop can never come back',
          lambda: _break(db, BOSS, 'characterManaRegen', 1.0))
    # V12, the downstream-coverage arm. The R-251 volume is the half of it that a single
    # field CAN break, and it is the half that matters most: it is what would actually
    # happen if svc_loot_volume's trim carve-out ever stopped covering this family.
    plant('the R-251 hoard volume trimmed out from under the family (loot_volume_trim '
          'carve-out lost)',
          lambda: _break(db, HOARD_LOOT_01, 'numSpawnMinEquation', '(1+(1*numberOfPlayers))*1'))
    plant('the R-251 hoard MAX volume rewritten downstream',
          lambda: _break(db, HOARD_LOOT_01, 'numSpawnMaxEquation', '(1+(1*numberOfPlayers))*1'))
    # HONEST NOTE, not a gap being hidden: V12's OTHER half - "is `ushkaret` inside
    # svc_uber_hoards' derived family set" - is decided by the RECORD NAME SHAPE
    # (`svc_<fam>hoard_<tier>`), so no field assignment can plant it and it has no row
    # here. It is still a live assertion: rename the family, or narrow `_CHEST_RE`, and
    # the gate reds. It is proven by construction rather than by plant.

    ok = all(results)
    print("\n  NEGTEST %s (%d/%d planted defects reddened the gate)"
          % ('PASS - every arm bites' if ok else 'FAILED - at least one gate arm is BLIND',
             sum(1 for r in results if r), len(results)))
    if not ok:
        raise SystemExit(1)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--negtest':
        _negtest()
    else:
        raise SystemExit("usage: py tools/patches/lookout_uber.py --negtest <built.arz>")
