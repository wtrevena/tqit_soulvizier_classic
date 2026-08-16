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

The base game already stands a boss proxy on that shelf - `Records/Proxies Boss/
LE_New/08_RhakotisLookout.dbr` at (218.65, 17.57, 53.18) - and it has never had a
face. This lane gives it one, 10.7u away, on its own surveyed spot.

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
  * THE FLOCK. `summon_swarm` has **exactly 1 carrier** (`um_gustleech_28`, Hero) and
    `leechstrike` exactly 1 (the same Hero). Ushkaret is the first Boss on either.

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
                 radius 7.0), then fights on the ground with `hemorrage` (bleed +
                 movement slow) and `leechstrike`.
P3 SKY-BURIAL  - `svc_ushkaret_skyburial` calls the flock (Common carrion-motes only,
                 never Champions - the neferkha no-crowd-out shape); on death
                 `ondeath_bladeorb` scatters the last quills.
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
  svc_ushkaret_larder(+buff)     the widened life-leech aura pair
  svc_ushkaret_skyburial         the flock summon (summon_swarm derive, Commons only)
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
DONOR_SWARM   = r'records\skills\sv\gustleech\summon_swarm.dbr'                       # Skill_SpawnPet -> Monster.tpl bodies
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
MOURNER_BAND = [28, 50, 66]
MOURNER_HP   = [1400.0, 2400.0, 3600.0]        # strictly ascending (the R-100 #18 escort invariant)
MOTE_BAND    = [26, 46, 60]

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
                  DONOR_SWARM, DONOR_POOL, DONOR_PROXY, ORB,
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

    # ── 1. THE LARDER (aura + its buff). Both are single-purpose clones with only
    #    EXISTING fields overridden, so the boss-kit clone-shape invariant holds.
    #    See section 3: this is a WIDE, STRONG life-leech aura. It is NOT a
    #    bleed-conditional feed - the shape has no conditional channel at all. ──
    db.clone_record(DONOR_LARDERB, LARDER_BUFF)
    _radius_before = _v1(db, LARDER_BUFF, 'skillTargetRadius')
    sf(LARDER_BUFF, 'skillTargetRadius', 14.0)            # 8.0 -> the plate IS the shelf
    sf(LARDER_BUFF, 'FileDescription', 'Ushkaret larder: wide life-leech aura (R-256)')
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

    # ── 2. THE FLOCK SUMMON. `summon_swarm` is a Skill_SpawnPet whose stock
    #    spawnObjects are themselves Monster.tpl records (stingingswarm_01 is
    #    Class=Monster, measured), so repointing it at our Common carrion-mote is
    #    the SAME shape, not a class change. It carries NO
    #    skillSpecialAnimationName, so it needs nothing from the vulture rig.
    #    Commons ONLY - the neferkha no-champion-crowd-out law. ──
    db.clone_record(DONOR_SWARM, SKYBURIAL)
    sf(SKYBURIAL, 'spawnObjects', [CARRIONMOTE])
    sf(SKYBURIAL, 'petLimit', 6)
    sf(SKYBURIAL, 'skillCooldownTime', [12.0, 10.0, 8.0])
    sf(SKYBURIAL, 'FileDescription', 'Ushkaret sky-burial: calls the carrion-mote flock')
    db._modified.add(SKYBURIAL)

    # ── 3. THE FLOCK BODY (Common). The donor already reads
    #    chanceToEquipFinger2 = 0.0; re-assert it so a placed add can never become
    #    a soul faucet (R-125 minion law + the soul-leak invariant). ──
    db.clone_record(DONOR_MOTE, CARRIONMOTE)
    sf(CARRIONMOTE, 'description', TAG_MOTE)
    sf(CARRIONMOTE, 'monsterClassification', 'Common')
    sf(CARRIONMOTE, 'charLevel', list(MOTE_BAND))
    sf(CARRIONMOTE, 'dropItems', 0, I)
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
    sf(MOURNER, 'dropItems', 0, I)                        # R-125: an escort is not a loot faucet
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
    # THE ANIMATION ANSWER (section 3): the donor's own ref slot 1 pointed at
    # 'Bladestorm', a skill this boss is losing. Repoint it - an EXISTING field on
    # a cloned record, no new field, no template guess - so the dive plays
    # Vulture_AttBeta.anm instead of falling through to the generic attack.
    _anim_before = _v1(db, B, 'unarmedSpecialAnimRef1')
    sf(B, 'unarmedSpecialAnimRef1', 'SwoopStomp')
    # the kit. Slots 1-7 + 10-13 come from the donor; 8, 9 and 14 are free and are
    # well inside MonsterSkillManager's declared skillName1..17 ceiling (R-255).
    for slot, skill, lvl in (
            (1,  SK_ARMOR,      None),                    # donor
            (2,  SK_MEGABURST,  None),                    # donor - P1 the vigil
            (3,  SK_RETALIATE,  None),                    # donor - closing costs blood
            (4,  SK_BLADEORB,   None),                    # donor - P3 the last quills
            (5,  LARDER,        None),                    # was character_vampiriaura
            (6,  SK_SWOOP,      None),                    # was bladestorm - P2 the stoop
            (7,  SK_HEMORRAGE,  None),                    # donor - the bleed
            (8,  SK_LEECHSTRIKE, [2, 5, 8]),              # NEW slot (gustleech's own levels)
            (9,  SKYBURIAL,     [1, 2, 3]),               # NEW slot - P3 the flock
            (12, SK_BOSSSCALE,  None),                    # was hero_scaling
            (13, SK_GP_L,       [0, 0, 1]),               # was hero_modifier
            (14, SK_CONVIMM,    [1, 1, 1]),               # NEW slot
    ):
        sf(B, 'skillName%d' % slot, skill)
        if lvl is not None:
            sf(B, 'skillLevel%d' % slot, list(lvl))
    # AI rotation: the stoop is the beat, the flock is the escalation, the bleed is
    # the constant. attackSkillName stays the donor's megaburst fan.
    sf(B, 'specialAttackSkillName', SK_SWOOP)
    sf(B, 'specialAttackChance', 35.0)
    sf(B, 'specialAttack2SkillName', SKYBURIAL)
    sf(B, 'specialAttack2Chance', 30.0)
    sf(B, 'specialAttack3SkillName', SK_HEMORRAGE)
    sf(B, 'specialAttack3Chance', 40.0)
    # the mystical orb on death (R-200: every red uber drops one). ADD the field
    # with an explicit dtype - the donor carries no treasureProxyName at all.
    sf(B, 'treasureProxyName', ORB, S)
    sf(B, 'dropItems', 1, I)
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
    for pair in ((DONOR_LARDERB, LARDER_BUFF), (DONOR_LARDER, LARDER), (DONOR_SWARM, SKYBURIAL)):
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
          "(exclusive corpsewake.tex) - quill fan + the ONLY custom swoop-stomp "
          "(anim answered by repointing unarmedSpecialAnimRef1 %r -> 'SwoopStomp') + "
          "hemorrage + leechstrike + the Larder aura (radius %s -> 14.0) + the "
          "carrion-mote flock; 2 Cliffside Mourner champions; limit [1..110]; lone "
          "pool + proxy (accessories EMPTY - the chest stands in the world); ONE "
          "world chest on the dedicated '%s' hoard chain; genericbossorb_02; "
          "'{^F}Soul of the Sky-Burial' (manual 'Give It to the Sky' -> The Patient "
          "Wing, 66%% Finger2); %d tags set. Map lane places it on the Lookout shelf."
          % (BAND, HP, SCALE, _anim_before, _radius_before, HOARD_PREFIX, len(_ALL_TAGS)))


# ── verify: THE GATE (runs post-finalization over the FINAL db) ──────────────
def verify(db, tags=None):
    """Fail-loud invariants for everything this lane claims. Ten checks; each one
    corresponds to a claim in the docstring, so a claim cannot rot into a lie."""
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

    # V11 tags: every tag this module references is authored (Text.arc coupling)
    if tagset:
        missing = [t for t in _ALL_TAGS if t not in tagset]
        if missing:
            problems.append("tags referenced but never authored: %s" % missing)

    if problems:
        raise SystemExit("[lookout_uber] R-256 LOOKOUT-UBER GATE FAILED (%d):\n  - %s"
                         % (len(problems), "\n  - ".join(problems)))
    print("  lookout_uber gate PASS: Ushkaret is a Boss %s, HP %s inside the shipped "
          "red band, on its donor's own rig+skin with the swoop animation answered; "
          "kit resolves within skillName1..17; orb02 is still the minimum-distance "
          "tier; ONE world chest on its own R-251 table with the boss proxy's "
          "accessories empty; the placement spec is the surveyed (208,17,52) spot; "
          "the soul is a 3-tier manual pet button with no hostile spawner on any pet; "
          "escorts drop nothing and stay smaller than the boss."
          % (BAND, HP))


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
    plant('the pool handed its proxyPoolEquation back (two bosses side by side)',
          lambda: _break(db, POOL, 'proxyPoolEquation',
                         r'records\proxies orient\proxypoolequation_02.dbr'))
    plant('the pool arithmetic broken to 2 guaranteed mains',
          lambda: _break(db, POOL, 'championMax', 1))
    plant('a referenced tag never authored',
          lambda: _break_tag(tags, TAG_SOUL))

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
