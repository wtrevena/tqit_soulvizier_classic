"""BUILD37 registry module: POLIS DAEMONAI - the Warden's Vault-Cage (polis_vault).

Spec: scratchpad/specs/polis_cage_uberboss_spec.md (WILL_DECISIONS 2026-07-11 binding).
A 5-chest boss-locked vault in the Hades-Palace prison cell HadesPalace_Floor04_01,
guarded by a 2-form uber Gigantes guardian (Alkyoneus, the Soul-Gaoler) + a mixed
daemon-jailer horde, dropping a downside-bearing soul. DB side ONLY - the map lane
(svaera_plus_portals.py / build_section_surgery.py) owns the 0x05 placements; the
placement coords are reported as map_deltas by this wave's implementer.

Contract (tools/patches/README.md): expose MODULE_NAME + apply(db, tags). The registry
runs this AFTER the apply_svc_patches monolith's content build and BEFORE its gates, so
this module's records are covered by every fail-loud invariant (spawn-eligibility,
boss-kit clone-shape, soul activation/augments/leak/naming, MP-equation, det-2x).

Idiom = _create_tantalus_uberboss / _create_blood_toxeus_monster (clone donors,
override EXISTING fields with NO explicit dtype [set_field preserves the donor dtype;
the INT/FLOAT-corruption trap], author NEW fields with correctly-typed literals,
fail-loud-graceful on missing donors, db._modified.add). Monster.tpl (not Pet.tpl), so
the Monster->Pet crash rule does not apply. Every mesh/anim/skill/loot donor was
byte-verified present in the built mod arz this session
(scratchpad/polis_probes/verify_polis_donors.py + verify_polis_loot.py). House style:
no em dashes.
"""
import sys
from pathlib import Path

# The monolith lives in tools/ (this file is tools/patches/); make it importable
# even if the registry imports us before tools/ is on sys.path.
_TOOLS = Path(__file__).resolve().parent.parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import apply_svc_patches as M
from apply_svc_patches import (
    DATA_TYPE_STRING as S,
    DATA_TYPE_FLOAT as F,
    DATA_TYPE_INT as I,
)

MODULE_NAME = 'polis_vault'

# ─────────────────────────────────────────────────────────────────────────────
# Record paths (spec section 8.1)
# ─────────────────────────────────────────────────────────────────────────────
_PG_DONOR = r'records\xpack\creatures\monster\gigantes\xsecrethero_wardenofsouls_48.dbr'
_PG_FORM1 = r'records\xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr'
_PG_FORM2 = r'records\xpack\creatures\monster\gigantes\um_polisgaoler_unbound_99.dbr'

_PG_POOL = r'records\drxmap\proxy\pools\q_polisgaoler_lone.dbr'
_PG_PROXY = r'records\drxmap\proxy\q_polisgaoler_lone.dbr'
_PG_LIMIT = r'records\proxies boss\limit_polisgaoler.dbr'
_PG_YARD_POOL = r'records\drxmap\proxy\pools\q_yard_polisgaoler.dbr'
_PG_YARD_PROXY = r'records\drxmap\proxy\q_yard_polisgaoler.dbr'

# Horde add proxies/pools (each a single-monster present-at-spawn placer; the map
# lane places one instance of each + 2 native ss_warden_behemoth at H1..H6).
_PG_VIND_POOL = r'records\drxmap\proxy\pools\q_polis_vindicator.dbr'
_PG_VIND_PROXY = r'records\drxmap\proxy\q_polis_vindicator.dbr'
_PG_LT_POOL = r'records\drxmap\proxy\pools\q_polis_lieutenant.dbr'
_PG_LT_PROXY = r'records\drxmap\proxy\q_polis_lieutenant.dbr'
_PG_LIMOS_POOL = r'records\drxmap\proxy\pools\q_polis_limos.dbr'
_PG_LIMOS_PROXY = r'records\drxmap\proxy\q_polis_limos.dbr'
_PG_BW_POOL = r'records\drxmap\proxy\pools\q_polis_bloodwitch.dbr'
_PG_BW_PROXY = r'records\drxmap\proxy\q_polis_bloodwitch.dbr'

# Horde monster records (EXISTING; referenced only, never modified).
_HORDE_VIND = r'records\xpack\creatures\monster\gigantes\am_vindicator_45.dbr'
_HORDE_LT = r'records\xpack\creatures\monster\gigantes\xhero_polybotes_47.dbr'
_HORDE_LIMOS = r'records\xpack\creatures\monster\archlimos\um_prox_47.dbr'
_HORDE_BW = r'records\xpack\creatures\monster\melinoe\as_bloodwitch_43.dbr'

# The 5 majestic chests + their loot tables.
_CHEST = [r'records\drxitem\container\svc_polisvault_chest_%02d.dbr' % n for n in range(1, 6)]
_CHEST_LOOT = [r'records\item\loottables\svc\polisvault_%02d.dbr' % n for n in range(1, 6)]

# Donors (all byte-verified present this session).
_LONE_POOL_DON = r'records\drxmap\proxy\pools\q_leinth_lone.dbr'
_LONE_PROXY_DON = r'records\drxmap\proxy\q_leinth_lone.dbr'
_LIMIT_DON = r'records\proxies boss\herolimit_all.dbr'
_DIFFICULTY04 = r'records\proxies orient\difficulty_04.dbr'
_CHEST_DON = r'records\item\containers\boss\small chests\greece\goldenchest_legendary_01.dbr'
_CHEST_DON_APEX = r'records\item\containers\boss\small chests\greece\goldenchest_legendary_02.dbr'
_LOOT_DON = r'records\drxitem\container\loottable_hidden_bloodcave_03.dbr'  # mega-chest legendary loot
_BOSS_ORB = r'records\item\containers\new\genericbossorb_04.dbr'

# Meshes (preview silhouettes; the pool spawns the real monster at its own scale).
_MESH_GIGANTES2 = r'XPack\Creatures\Monster\Gigantes\Gigantes02.msh'   # Warden / Vindicator rig
_MESH_GIGANTES1 = r'XPack\Creatures\Monster\Gigantes\Gigantes01.msh'   # Polybotes lieutenant rig
_MESH_LIMOS = r'Creatures\Monster\Limos\Limos01.msh'
_MESH_MELINOE = r'XPack\Creatures\Monster\Melinoe\Melinoe01.msh'

# Kit skills (all EXISTING, class-verified this session).
_SK_LIFEDRAIN = r'records\xpack\skills\monsterskills\activeattackdirect\hero_lifedrain.dbr'
_SK_LIFEDRAIN_CASC = r'records\xpack\skills\monsterskills\activeattackdirect\hero_lifedrain_cascade.dbr'
_SK_SPIRITWAVE = r'records\xpack\skills\monsterskills\activeattackwave\hero_spiritwave.dbr'
_SK_DEATHCHILL = r'records\skills\spirit\deathchillaura.dbr'
_SK_KINETIC = r'records\xpack\skills\monsterskills\activeattackradius\gigantes_kineticblast.dbr'
_SK_BONUSPHYS = r'records\xpack\skills\monsterskills\passive\bonusdamage_physical.dbr'
_SK_ARMOR = r'records\skills\monster skills\defense\armor_passive.dbr'
_SK_HEROSCALE = r'records\skills\monster skills\passive_buffs\hero_scaling.dbr'
_SK_BOSSIMMUNE = r'records\skills\boss skills\boss_conversionimmunity.dbr'
_SK_GLOBPROP_L = r'records\skills\monster skills\globalproperties_legendary01.dbr'

# Soul: grant + augments + autocast controller (spec section 6).
_SS_LIFEDRAIN = r'records\skills\spirit\lifedrain.dbr'                   # player-usable soul-drain
_SK_DARK_COVENANT = r'records\skills\spirit\drxdarkcovenant.dbr'
_SK_DEATH_CHILL = r'records\skills\spirit\drxdeathchillaura.dbr'
_AC_ON_ATTACK = r'records\xpack\ai controllers\autocast_items\basetemplates\base_atenemy_onattack.dbr'

# ── R-100 #17 (Will 2026-07-29), THE DIFFICULTY-TIER MIS-WIRE ────────────────
# WILL, VERBATIM: "also his chests on epic are dropping 'essence' like 'essence
# of the chill of tartarus' which should only drop on normal instead of dropping
# the epic version which starts with 'embodiment' like 'embodiment of the chill
# of tartarus'."
#
# ROOT CAUSE, measured (tools/debug/probe_gaoler_chests.py +
# probe_relic_difficulty_tiers.py). The vault's loot tables are clones of the DRX
# mega-chest table `loottable_hidden_bloodcave_03`, whose EVERY slot is
# legendary tier: `..._l01` weapons/armour/jewellery and `03_act4_relics`. On top
# of that clone this module injected its GUARANTEED slots from the monolith's
# shared `_OBS_GUAR_*` donors, and both of those are pinned to the NORMAL tier:
#     unique_1h_n01.dbr   <- `_n01` = normal-tier uniques
#     01_act4_relics.dbr  <- `01_`  = normal-tier relics ("Essence of ...")
# The `01_/02_/03_` prefix IS the tier: 01_act4_relics lists `01_Act*` relics,
# 02_ lists `02_Act*`, 03_ lists `03_Act*` (measured on the base-game arz). So
# the guaranteed slot - the one slot that fires at 100% - handed out normal-tier
# relics on every difficulty while the rest of the same chest paid legendary.
#
# WHY NOT A DIFFICULTY-INDEXED ARRAY: on a Monster.tpl record the loot slots ARE
# difficulty-indexed 3-arrays (2,703 native instances of
# `lootMisc2Item1 = [01_act4, 02_act4, 03_act4]`, e.g. on this very Gaoler's own
# donor xsecrethero_wardenofsouls_48). On a CONTAINER's loot table they are NOT:
# zero `lootNNameM` fields anywhere in the 74,013-record base game carry more
# than one value. A container's tier is fixed by the tables it names, and the
# base game ships a separate chest record per tier
# (goldenchest_normal_/epic_/legendary_01). So the in-scope fix is to stop the
# guaranteed slot from being the odd one out, and match it to the tier the rest
# of the chest already pays. A truly per-difficulty vault needs 3 chest records
# per spot plus map-side placement and is registered as BL-b102-DEBT-3.
#
# SHARED-SYMBOL LAW: `M._OBS_GUAR_UNIQUE` / `M._OBS_GUAR_RELIC` have two OTHER
# carriers inside the monolith (apply_svc_patches lines ~15409 and ~16715, the
# other dedicated-hoard builders). They are deliberately NOT edited here - this
# module now names its own tier-correct donors, and the same mis-wire in those
# two carriers is reported, not silently retuned under a Gaoler ticket
# (docs/BACKLOG.md BL-b102-DEBT-4).
_GUAR_UNIQUE = r'records\xpack\item\loottables\weapons\mastertables\unique_1h_l01.dbr'
_GUAR_RELIC = r'records\xpack\item\loottables\relics\03_act4_relics.dbr'
# The normal-tier donors this module used to inject, kept NAMED (not deleted) so
# the gate below can prove they are gone from the vault's tables.
_GUAR_UNIQUE_WRONG = M._OBS_GUAR_UNIQUE   # ...\mastertables\unique_1h_n01.dbr
_GUAR_RELIC_WRONG = M._OBS_GUAR_RELIC     # ...\relics\01_act4_relics.dbr

# Text tags.
_TAG_G1 = 'tagSVCMonsterPolisGaoler'
_TAG_G2 = 'tagSVCMonsterPolisGaolerUnbound'
_TAG_SOUL = 'tagSVCSoulGaoler'
_TAG_SOUL_DESC = 'tagSVCSoulGaolerDESC'

_SOUL_NAME = '{^F}Soul of the Gaoler'

# Power bands (WILL_DECISIONS: 2-form total [26k,35k,47k]).
_PG_BAND = [50, 72, 90]
_PG_LIFE1 = [15000.0, 20000.0, 27000.0]   # form1
_PG_LIFE2 = [11000.0, 15000.0, 20000.0]   # form2  (totals 26k/35k/47k)


def _lone_pool(db, pool, main, desc):
    """Clone the q_leinth_lone pool (already spawnMin=Max=1, championChance=0) into
    a LONE-boss pool: all 3 name slots = the one main, champion slots cleared. This
    satisfies the spawn-eligibility LAW (guaranteed mains = spawnMax=1 with
    championChance=0). The guardian carries no escort here - the horde is placed as
    its own proxies by the map lane, exactly how the prison places each caged monster."""
    db.clone_record(_LONE_POOL_DON, pool)
    sf = db.set_field
    sf(pool, 'FileDescription', desc)
    sf(pool, 'name1', main); sf(pool, 'name2', main); sf(pool, 'name3', main)
    sf(pool, 'nameChampion1', ''); sf(pool, 'nameChampion2', ''); sf(pool, 'nameChampion3', '')
    sf(pool, 'weightChampion1', 0); sf(pool, 'weightChampion2', 0); sf(pool, 'weightChampion3', 0)
    sf(pool, 'spawnMin', 1); sf(pool, 'spawnMax', 1)
    sf(pool, 'championChance', 0.0); sf(pool, 'championMin', 0); sf(pool, 'championMax', 0)
    db._modified.add(pool)


def _lone_proxy(db, proxy, pool, mesh, scale):
    """Clone q_leinth_lone proxy into a lone placer: chanceToRun=100, our pool, the
    no-cap limit_polisgaoler window, preview mesh/scale. difficultyEquationFile
    (difficulty_04), baseTexture (proxyu_boss.tex) and placementExtents (3.5) ride
    the clone verbatim."""
    db.clone_record(_LONE_PROXY_DON, proxy)
    sf = db.set_field
    sf(proxy, 'chanceToRun', 100.0)
    sf(proxy, 'pool1', pool)
    sf(proxy, 'difficultyLimitsFile', _PG_LIMIT)
    sf(proxy, 'difficultyEquationFile', _DIFFICULTY04)
    sf(proxy, 'mesh', mesh)
    sf(proxy, 'scale', float(scale))
    sf(proxy, 'placementExtents', 3.5)
    db._modified.add(proxy)


def _register_spawn_proxy(proxy, pool, main, name):
    M._MOD_AUTHORED_SPAWN_PROXIES.append(
        {'proxy': proxy, 'pool': pool, 'main_monster': main, 'name': name})


def _guardian_form(db, path, life, scale, desc_tag, kit, special, is_terminal):
    """Clone the Warden of Souls into a guardian form. Overrides EXISTING donor
    fields with no explicit dtype (dtype preserved); authors the resist wall as new
    FLOAT fields. Loot rides the TERMINAL form ONLY (the byte-verified Charon
    precedent): form1 clears its inherited Warden-soul Finger2 (chance 0) and never
    carries the boss orb (donor has no treasureProxyName); form2 gets the orb + the
    Gaoler soul via _create_soul."""
    db.clone_record(_PG_DONOR, path)
    sf = db.set_field
    sf(path, 'monsterClassification', 'Boss')       # souls drop; the 5 chests' Boss-lock keys off this
    sf(path, 'description', desc_tag)
    sf(path, 'charLevel', list(_PG_BAND))            # existing INT array -> INT
    sf(path, 'characterLife', list(life))            # existing FLOAT array -> FLOAT
    sf(path, 'scale', float(scale))
    # Resist wall (spec 3.2): a real boss wall the prison's shades/behemoths lack,
    # deliberately NOT unkillable (fire/cold/lightning left near-normal). NEW fields
    # on the Warden donor -> authored as FLOAT literals.
    sf(path, 'defensiveLife', 70.0)
    sf(path, 'defensivePierce', 45.0)
    sf(path, 'defensivePhysical', 30.0)
    sf(path, 'defensivePoison', 40.0)
    sf(path, 'defensiveBleeding', 30.0)
    # Kit (skillName slots) + blank trailing donor slots up to 24.
    M._svc_set_kit(db, path, kit, [])
    # AI cast rotation: reuse the Warden's two proven specialAttack slots (0 drain /
    # 2 spirit-wave, full Chance/Delay/Range from the clone) and add a slot-3 giant
    # slam WITH complete timing so it actually fires in the confined cell.
    for suffix, skill, chance in special:
        sf(path, 'specialAttack%sSkillName' % suffix, skill)
        if chance is not None:
            sf(path, 'specialAttack%sChance' % suffix, float(chance))
    # slot-3 slam needs its own timing fields (the donor has only slots 0 + 2).
    sf(path, 'specialAttack3Delay', 10.0)
    sf(path, 'specialAttack3Range', 'AnyRange')
    sf(path, 'initialSkillName', _SK_DEATHCHILL)     # buff the withering aura on spawn
    sf(path, 'dropItems', 1)
    if is_terminal:
        sf(path, 'treasureProxyName', _BOSS_ORB)     # the corpse boss-orb, terminal form ONLY
        sf(path, 'actorToSpawnOnDeath', '')          # terminal
    db._modified.add(path)


def _build_guardian(db, tags):
    """The 2-form uber guardian, derived from the actual Warden of Souls (rig +
    anim + soul-warden kit come across render/anim-safe). Form1 [15/20/27k] reforms
    into the terminal form2 [11/15/20k] (totals 26/35/47k per WILL_DECISIONS)."""
    # Guard every donor (fail-loud-graceful, the cohort pattern).
    donors = [_PG_DONOR, _LONE_POOL_DON, _LONE_PROXY_DON, _LIMIT_DON, _BOSS_ORB,
              _SK_LIFEDRAIN, _SK_SPIRITWAVE, _SK_DEATHCHILL, _SK_KINETIC,
              _SK_BONUSPHYS, _SK_ARMOR, _SK_HEROSCALE, _SK_BOSSIMMUNE, _SK_GLOBPROP_L]
    for d in donors:
        if not db.has_record(d):
            print("  POLIS GAOLER: WARNING donor missing: %s; guardian skipped" % d)
            return False

    # Kit filtered to present records (the lifedrain cascade is a secondary that
    # chains off lifedrain, so it rides the kit only if present).
    raw_kit = [
        (_SK_DEATHCHILL, [3, 4, 5]),        # withering gaoler aura (also initialSkill)
        (_SK_LIFEDRAIN, [4, 6, 8]),         # signature soul-drain
        (_SK_LIFEDRAIN_CASC, [4, 6, 8]),    # drain cascade (secondary)
        (_SK_SPIRITWAVE, [4, 6, 8]),        # soul-blast that sweeps the cell
        (_SK_KINETIC, [3, 4, 5]),           # giant ground-slam (tight-cell AoE)
        (_SK_BONUSPHYS, [1, 2, 3]),         # giant-strength passive
        (_SK_ARMOR, [1, 2, 3]),             # armor passive
        (_SK_HEROSCALE, [1, 2, 3]),         # level scaling
        (_SK_BOSSIMMUNE, 1),                # convert/taunt/fear/petrify immunity
        (_SK_GLOBPROP_L, [1, 2, 3]),        # legendary scaling bundle
    ]
    kit = [(p, lv) for (p, lv) in raw_kit if db.has_record(p)]
    special = [('', _SK_LIFEDRAIN, 80.0), ('2', _SK_SPIRITWAVE, 65.0),
               ('3', _SK_KINETIC, 45.0)]
    special2 = [('', _SK_LIFEDRAIN, 85.0), ('2', _SK_SPIRITWAVE, 80.0),
                ('3', _SK_KINETIC, 55.0)]   # form2: a heavier spirit-wave / slam cadence

    # Terminal FORM 2 first (form 1 references it via actorToSpawnOnDeath).
    _guardian_form(db, _PG_FORM2, _PG_LIFE2, 3.8, _TAG_G2, kit, special2, is_terminal=True)
    # FORM 1 (the placed boss; reforms on death). Carries NO orb + NO soul.
    _guardian_form(db, _PG_FORM1, _PG_LIFE1, 3.5, _TAG_G1, kit, special, is_terminal=False)
    db.set_field(_PG_FORM1, 'actorToSpawnOnDeath', _PG_FORM2)
    M._svc_clear_soul_loot(db, _PG_FORM1)   # only the terminal form drops the soul

    # No-cap limit window [1..110] so the L90 boss is never scaled down.
    M._svc_widen_limit(db, _LIMIT_DON, _PG_LIMIT, hi=110)

    # Lone-boss pool + proxy (canonical placement) + TESTHUB yard.
    _lone_pool(db, _PG_POOL, _PG_FORM1, 'Alkyoneus, the Soul-Gaoler (lone vault guardian)')
    _lone_proxy(db, _PG_PROXY, _PG_POOL, _MESH_GIGANTES2, 3.5)
    _register_spawn_proxy(_PG_PROXY, _PG_POOL, _PG_FORM1,
                          'q_polisgaoler_lone (Alkyoneus, vault guardian)')

    _lone_pool(db, _PG_YARD_POOL, _PG_FORM1, 'YARD: Alkyoneus @100% (TESTHUB-only)')
    _lone_proxy(db, _PG_YARD_PROXY, _PG_YARD_POOL, _MESH_GIGANTES2, 3.5)
    _register_spawn_proxy(_PG_YARD_PROXY, _PG_YARD_POOL, _PG_FORM1,
                          'q_yard_polisgaoler (TESTHUB yard)')

    # ── The downside-bearing soul (terminal form2 only, 66% Finger2) ──
    def _pg_stats(t):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]
        lv = {'n': 4, 'e': 6, 'l': 8}[t]
        r = lambda v: round(v * m, 1)
        return {
            **M._bmp(t),
            'itemSkillName': (S, _SS_LIFEDRAIN), 'itemSkillLevel': (I, lv),
            'itemSkillAutoController': (S, _AC_ON_ATTACK),
            'augmentSkillName1': (S, _SK_DARK_COVENANT),
            'augmentSkillLevel1': (I, {'n': 4, 'e': 4, 'l': 5}[t]),
            'augmentSkillName2': (S, _SK_DEATH_CHILL),
            'augmentSkillLevel2': (I, {'n': 3, 'e': 4, 'l': 4}[t]),
            'offensiveLifeMin': (F, r(55.0)), 'offensiveLifeMax': (F, r(90.0)),
            'offensiveLifeModifier': (F, r(30.0)),
            'offensiveLifeLeechMin': (F, r(40.0)),        # the vampiric core (big ADCtH)
            'offensivePercentCurrentLifeMin': (F, r(4.0)),
            'characterStrengthModifier': (F, r(18.0)),    # the giant's strength
            'characterLife': (F, r(320.0)), 'characterLifeModifier': (F, r(12.0)),
            'characterDefensiveAbility': (F, r(70.0)),
            'defensiveLife': (F, r(22.0)),
            # THE amgoz1 lumbering-giant downside: FLAT -4 total speed on all tiers
            # (the verified Polyphemus precedent; WILL_DECISIONS "-4 flat").
            'characterTotalSpeedModifier': (I, -4),
        }
    tiers = [{'diff': t, 'itemLevel': il, 'stats': _pg_stats(t)}
             for t, il in (('n', 50), ('e', 72), ('l', 90))]
    for p in M._create_soul(db, 'polisgaoler', _TAG_SOUL, tiers,
                            monster=_PG_FORM2, drop_rate=66.0):
        db.set_field(p, 'FileDescription', 'Hades')   # amgoz1 V5 region/act sort word
        db._modified.add(p)

    print("  POLIS GAOLER: 2-form guardian (Alkyoneus [15/20/27k] -> Hoard Unbound "
          "[11/15/20k], totals 26/35/47k; soul-warden kit + kinetic slam + resist "
          "wall; orb+soul+chest-lock on terminal form2 only) + lone pool/proxy/limit "
          "+ TESTHUB yard + Soul of the Gaoler (-4 speed downside, 66% Finger2).")
    return True


def _build_horde(db):
    """The 4 NEW single-monster horde proxies (the 2 Behemoth jailers reuse the
    prison's own ss_warden_behemoth proxy - no new record). Each is a lone placer
    (spawn 1/1, champ 0) the map lane injects once at its H-coord. Mixed
    daemon-jailer default per WILL_DECISIONS (Limos + Melinoe among the giant-kin)."""
    adds = [
        (_PG_VIND_POOL, _PG_VIND_PROXY, _HORDE_VIND, _MESH_GIGANTES2, 2.0,
         'q_polis_vindicator (Gigantes Vindicator, H5)'),
        (_PG_LT_POOL, _PG_LT_PROXY, _HORDE_LT, _MESH_GIGANTES1, 3.2,
         'q_polis_lieutenant (Gigantes Hero lieutenant, H6)'),
        (_PG_LIMOS_POOL, _PG_LIMOS_PROXY, _HORDE_LIMOS, _MESH_LIMOS, 1.4,
         'q_polis_limos (Limos hunger-daemon, H3)'),
        (_PG_BW_POOL, _PG_BW_PROXY, _HORDE_BW, _MESH_MELINOE, 1.2,
         'q_polis_bloodwitch (Melinoe blood-witch, H4)'),
    ]
    built = 0
    for pool, proxy, mon, mesh, scale, label in adds:
        if not db.has_record(mon):
            print("  POLIS HORDE: WARNING monster missing: %s; %s skipped" % (mon, label))
            continue
        _lone_pool(db, pool, mon, 'Polis vault horde: %s' % label)
        _lone_proxy(db, proxy, pool, mesh, scale)
        _register_spawn_proxy(proxy, pool, mon, label)
        built += 1
    print("  POLIS HORDE: %d/4 new daemon-jailer proxies built (2 Behemoth jailers "
          "reuse the native ss_warden_behemoth proxy)." % built)


def _build_vault(db, tags):
    """The 5 golden Majestic Chests (ChestTemple01, already Boss-locked, LockedRadius
    100 kept - the base Charon boss-chest value) with per-chest enriched apex loot
    (clone of the mega-chest legendary table, numSpawn just under the mega, a
    guaranteed unique/relic slot varied per spec 5.2). 5 distinct records => 5
    independent rolls. Graceful loot fallback keeps the donor's own legendary table."""
    if not db.has_record(_CHEST_DON):
        print("  POLIS VAULT: WARNING chest donor missing: %s; vault skipped" % _CHEST_DON)
        return
    sf = db.set_field
    loot_ok = (db.has_record(_LOOT_DON) and db.has_record(_GUAR_UNIQUE)
               and db.has_record(_GUAR_RELIC))
    if not loot_ok:
        print("  POLIS VAULT: mega-loot/guaranteed donors missing; keeping the golden "
              "chest's own legendary table (still a rich legendary chest).")

    # Per-chest theme (spec 5.2): (donor, numMin_mult, numMax_mult, guaranteed slots).
    # guar = list of (loot_table, weight); loot3 chance = 100 when present.
    themes = [
        (_CHEST_DON,      2.4, 2.8, [(_GUAR_UNIQUE, 100)]),                    # 1 legendary weapon
        (_CHEST_DON,      2.4, 2.8, [(_GUAR_UNIQUE, 70), (_GUAR_RELIC, 50)]),  # 2 armor/mixed + relic
        (_CHEST_DON_APEX, 2.8, 3.2, [(_GUAR_UNIQUE, 100), (_GUAR_RELIC, 100)]),# 3 apex jewelry/relic + boss roll
        (_CHEST_DON,      2.4, 2.8, [(_GUAR_RELIC, 100)]),                     # 4 mixed + big gold + relic
        (_CHEST_DON,      2.4, 2.8, [(_GUAR_RELIC, 80), (_GUAR_UNIQUE, 50)]),  # 5 mixed + relic/charm
    ]

    for i, (chest, loot, (chest_don, nmin, nmax, guar)) in enumerate(
            zip(_CHEST, _CHEST_LOOT, themes), start=1):
        donor = chest_don if db.has_record(chest_don) else _CHEST_DON
        db.clone_record(donor, chest)
        # Keep the donor's Boss-lock + LockedRadius=100 + ChestTemple01 mesh +
        # tagChest006 ("Majestic Chest") + gold generator; only ensure lock + gold.
        sf(chest, 'locked', 1)
        sf(chest, 'LockedClassification', 'Boss')
        sf(chest, 'LockedRadius', 100.0)
        sf(chest, 'goldGeneratorChance', 100.0)
        if loot_ok:
            # Build the enriched apex loot table (clone mega legendary -> tune down
            # numSpawn below the mega + a guaranteed high-value loot3 slot). The
            # exact proven _svc_build_dedicated_hoard loot recipe.
            db.clone_record(_LOOT_DON, loot)
            sf(loot, 'numSpawnMinEquation', '(3+(1.8*numberOfPlayers))*%s' % nmin)
            sf(loot, 'numSpawnMaxEquation', '(3+(1.8*numberOfPlayers))*%s' % nmax)
            sf(loot, 'loot3Chance', 100.0)
            for j, (tbl, wt) in enumerate(guar, start=1):
                sf(loot, 'loot3Name%d' % j, tbl)
                sf(loot, 'loot3Weight%d' % j, wt)
            db._modified.add(loot)
            sf(chest, 'tables', loot)
        db._modified.add(chest)
    print("  POLIS VAULT: 5 golden Majestic Chests (ChestTemple01, Boss-lock, "
          "LockedRadius 100) with %s apex loot + 5 independent rolls."
          % ('enriched' if loot_ok else 'donor-legendary'))


def _register_naming(db, tags):
    """Register the hand-designed evocative soul name so the F6 naming machinery
    keeps '{^F}Soul of the Gaoler' (exactly as the monolith does for Tantalus /
    Charon). Runtime registration only (no file edit) - the registry runs this
    module BEFORE the naming pass + gate:
      (1) _HAND_DESIGNED_SOUL_TAGS -> the verifier skips the 'Soul of X' form;
      (2) _SOUL_NAME_STANDARD pin -> the auto-transform never rewrites it to
          '{^F}Gaoler Soul' (tags.update restores the evocative value + the
          't in _SOUL_NAME_STANDARD' guard skips it)."""
    M._HAND_DESIGNED_SOUL_TAGS = frozenset(M._HAND_DESIGNED_SOUL_TAGS | {_TAG_SOUL})
    M._SOUL_NAME_STANDARD[_TAG_SOUL] = _SOUL_NAME


def _set_tags(tags):
    tags[_TAG_G1] = '{^r}Alkyoneus, the Soul-Gaoler'
    tags[_TAG_G2] = '{^r}Alkyoneus, the Hoard Unbound'
    tags[_TAG_SOUL] = _SOUL_NAME
    tags[_TAG_SOUL_DESC] = (
        'The Soul-Gaoler kept a hoard he could never open and drank the strength of '
        'any who reached for it. His soul drinks the same way, pouring what it takes '
        'into the wearer, though it drags with a giant\'s slow and heavy tread.')


def apply(db, tags):
    """Registry entrypoint. Build the whole Polis Daemonai vault-cage DB side:
    the 2-form guardian + soul, the mixed daemon-jailer horde proxies, and the 5
    boss-locked Majestic Chests. The map lane places all 0x05 instances in
    HadesPalace_Floor04_01 (coords in the module docstring / spec section 2)."""
    print("\n=== BUILD37 polis_vault: Polis Daemonai Warden's Vault-Cage ===")
    _register_naming(db, tags)
    _set_tags(tags)
    if not _build_guardian(db, tags):
        # Guardian is the keystone (the chests key their Boss-lock off his death);
        # if his donors are missing, do not ship a half-vault.
        print("  POLIS VAULT: guardian skipped -> vault + horde NOT built.")
        return
    _build_horde(db)
    _build_vault(db, tags)
    print("=== polis_vault done ===\n")


# ─────────────────────────────────────────────────────────────────────────────
# R-100 #17 GATE. Runs in the registry's POST-FINALIZATION verify phase, i.e.
# over the FINAL assembled db, so a later writer cannot re-introduce the
# normal-tier donor behind this module's back. Negative tests:
# tools/debug/negtest_gaoler_chests.py.
# ─────────────────────────────────────────────────────────────────────────────
_NORMAL_TIER_MARKERS = ('_n01.dbr', '\\01_act4_relics.dbr')


def _all_loot_strings(db, rec):
    ff = db.get_fields(rec) or {}
    out = []
    for k, tf in ff.items():
        b = k.split('###')[0]
        if not b.lower().startswith('loot'):
            continue
        for v in tf.values:
            if isinstance(v, str) and v:
                out.append((b, v))
    return out


def verify(db, tags):
    """T1  all 5 chest records + 5 loot tables still EXIST (retirement protocol:
            halving the count withdrew PLACEMENTS, it never deleted a record).
        T2  no vault loot table names a NORMAL-tier donor anywhere (R-100 #17:
            "essence of ..." on epic). Both markers are checked, not just the
            relic one, because the guaranteed unique slot had the same defect.
        T3  each chest still points at its own loot table (5 independent rolls).
        T4  the guaranteed slot is still GUARANTEED (loot3Chance == 100) - the
            tier fix must not quietly turn the payoff slot off.
        T5  the map lane places exactly TWO of the five, and they are 01 and 03
            (the apex). Source-level assertion against build_section_surgery's
            own B41_SPECS, so the DB half and the map half cannot drift apart.
    """
    problems = []
    for chest, loot in zip(_CHEST, _CHEST_LOOT):
        if not db.has_record(chest):
            problems.append("T1 chest record MISSING (never delete): %s" % chest)
            continue
        if not db.has_record(loot):
            problems.append("T1 loot table MISSING (never delete): %s" % loot)
            continue
        tv = db.get_field_value(chest, 'tables')
        tv = tv[0] if isinstance(tv, list) and tv else tv
        if str(tv or '').replace('/', '\\').lower() != loot.lower():
            problems.append("T3 %s tables=%r, expected its own %s"
                            % (chest, tv, loot))
        ch3 = db.get_field_value(loot, 'loot3Chance')
        ch3 = ch3[0] if isinstance(ch3, list) and ch3 else ch3
        if ch3 is None or abs(float(ch3) - 100.0) > 0.01:
            problems.append("T4 %s loot3Chance=%r, expected 100 (the guaranteed "
                            "high-value slot)" % (loot, ch3))
        for field, val in _all_loot_strings(db, loot):
            vl = val.replace('/', '\\').lower()
            for marker in _NORMAL_TIER_MARKERS:
                if vl.endswith(marker):
                    problems.append(
                        "T2 %s :: %s = %s - NORMAL-tier donor inside a "
                        "legendary-tier vault chest (R-100 #17: the 'essence "
                        "of ...' bug)" % (loot, field, val))

    # T5 - the map half
    try:
        import build_section_surgery as _bss
        placed = [p.decode('latin-1') if isinstance(p, bytes) else str(p)
                  for (p, *_rest) in _bss.B41_SPECS[_bss.B41_POLIS_KEY]]
        chests = [p for p in placed if 'svc_polisvault_chest' in p.lower()]
        want = ['svc_polisvault_chest_01', 'svc_polisvault_chest_03']
        got = [p.replace('/', '\\').lower().rsplit('\\', 1)[-1].replace('.dbr', '')
               for p in chests]
        if got != want:
            problems.append("T5 map places %r, R-100 #17 halved it to %r"
                            % (got, want))
    except Exception as exc:                      # pragma: no cover - import guard
        problems.append("T5 could not read build_section_surgery.B41_SPECS: %s" % exc)

    if problems:
        for p in problems[:12]:
            print("  POLIS VAULT GATE OFFENDER: %s" % p)
        raise SystemExit("polis_vault gate FAILED: %d problem(s) (R-100 #17)"
                         % len(problems))
    print("  polis_vault gate PASS (R-100 #17): 5 chest records + 5 loot tables "
          "intact, 0 normal-tier donors, guaranteed slots still 100%, map places "
          "exactly chest_01 + the apex chest_03.")
