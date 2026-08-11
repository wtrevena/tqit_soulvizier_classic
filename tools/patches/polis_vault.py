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
import svc_armor_breadth as SAB
import svc_loot_breadth as SLB
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

# ── WILL 2026-08-08: THE GAOLER-CHEST DIFFICULTY-TIER CONVERSION ─────────────
# R-100 #17 matched the guaranteed slot to the chest's OTHER slots, but the whole
# chest was legendary on EVERY difficulty (the vault loot tables are clones of the
# fully-legendary loottable_hidden_bloodcave_03). So Alkyoneus's cage dropped
# Incarnation relics ("incarnation of ...") on Normal and Epic, where Will wants
# Essence on Normal and Embodiment on Epic. A flat FixedItemContainer CANNOT
# difficulty-scale its own loot (FixedItemContainer.tpl has no per-difficulty
# fields; ZERO of the 53,520 difficulty-indexed loot arrays in the base+DLC db are
# on any container - they are ALL on Monster records). The ONLY base-game-proven,
# mod-precedented container difficulty branch is a Class=Proxy record with
# accessory1 / accessoryEpic1 / accessoryLegendary1 (the esti/hidden-bloodcave
# chest = proxy_hidden_bloodcave_chest already does exactly this). So the 2 MAP-
# PLACED chests (svc_polisvault_chest_01 + _03) are CONVERTED IN PLACE from
# FixedItemContainer to Proxy at their existing paths: the engine reads accessory1
# on Normal, accessoryEpic1 on Epic, accessoryLegendary1 on Legendary; each -> a
# ProxyAccessoryPool -> a per-difficulty golden FixedItemContainer -> its single-
# tier FixedItemLoot table. The Boss-lock survives proxy-spawn (base
# BossChest05_Hades_01 and mod svc_charonhoard_01 are both proxy-spawned AND
# LockedClassification=Boss). Container/proxy 0x05 placements share byte-shape, so
# the Class swap at the SAME path needs NO Levels edit (canonical Levels md5 stays
# 78a3e263). The LEGENDARY chain REUSES the existing polisvault_0N table verbatim
# so Will's Legendary farm payout is byte-preserved.
# The per-difficulty donor maps this conversion is built on. Since 2026-08-10 the
# guaranteed slot is written by svc_loot_breadth.set_guaranteed_theme, whose kind_path()
# resolves the SAME tables through the SAME tier keys (kinds 'unique_1h' and 'relic');
# these two maps are kept as the readable statement of the tier law they encode
# (01=Essence/Normal, 02=Embodiment/Epic, 03=Incarnation/Legendary) and as the
# cross-check a reviewer reads next to the shared resolver.
_UNIQUE_TIER = {
    'n': r'records\xpack\item\loottables\weapons\mastertables\unique_1h_n01.dbr',
    'e': r'records\xpack\item\loottables\weapons\mastertables\unique_1h_e01.dbr',
    'l': r'records\xpack\item\loottables\weapons\mastertables\unique_1h_l01.dbr',
}
_RELIC_TIER = {  # 01=Essence(Normal), 02=Embodiment(Epic), 03=Incarnation(Legendary)
    'n': r'records\xpack\item\loottables\relics\01_act4_relics.dbr',
    'e': r'records\xpack\item\loottables\relics\02_act4_relics.dbr',
    'l': r'records\xpack\item\loottables\relics\03_act4_relics.dbr',
}
# The proven esti-chest chain donors (proxy_hidden_bloodcave_chest ->
# pool_hidden_0N -> hidden_bloodcave_chest_0N -> loottable_hidden_bloodcave_0N).
_PROXY_DON = r'records\drxitem\container\proxy_hidden_bloodcave_chest.dbr'
_POOL_HIDDEN = {'n': r'records\drxitem\container\pool_hidden_01.dbr',
                'e': r'records\drxitem\container\pool_hidden_02.dbr',
                'l': r'records\drxitem\container\pool_hidden_03.dbr'}
_BC_LOOT_DON = {'n': r'records\drxitem\container\loottable_hidden_bloodcave_01.dbr',
                'e': r'records\drxitem\container\loottable_hidden_bloodcave_02.dbr',
                'l': r'records\drxitem\container\loottable_hidden_bloodcave_03.dbr'}
# ── WILL 2026-08-10: THE BREADTH + DIFFERENTIATION WAVE ─────────────────────
# WILL, VERBATIM: "we need to update the chests in the test hub in the place where
# the Polybotes Soul drops in the prison of souls so that they drop different items
# since right now I am seeing every chest drop the same items pretty much ever
# playthrough, there are never any legendary spears dropped it is basically the same
# items dropped over and over by all chests. we need to expand the bredth of the
# legendary items dropped in the testhub chests and also in the steam version."
#
# The cage has SIX physical chests (2 canonical placements + the 4 TESTHUB farm
# duplicates, commit 7d6e276) but only TWO records, and those two were near-clones
# (70 of 74 fields identical), so every open drew from the same collapsed pool. The
# missing-spear half is the shared DRX weapon row and is fixed for every mod chest by
# tools/svc_loot_breadth.py. The SAMENESS half is fixed HERE, with no map edit at all:
# each placed chest's per-difficulty ProxyAccessoryPool now names THREE themed
# containers instead of one, so every physical chest resolves its own theme at spawn
# and re-rolls on a later playthrough. That is the base game's own cave-boss-chest
# construction (952 shipped ProxyAccessoryPools name more than one container; e.g.
# legendary_01_cavebosschest_01 picks among 3 chests at 75/50/25), so it needs no new
# mechanism and no Levels rebuild - the placements still point at the same 2 records.
#
# NON-REDUCTION: every variant inherits its PLACED chest's numSpawn richness and its
# guaranteed weapon:relic weight split, so the Legendary farm payout is preserved
# (R-100 #17 / Will 2026-08-08) while the classes it can pay widen from 3 to 6.
#
# (chest_NN, numSpawn min, numSpawn max, [theme per variant a/b/c], [pool weights])
_PLACED_TIERED = [
    ('01', 2.4, 2.8, ['martial', 'hunter', 'warden'], [50, 25, 25]),
    ('03', 2.8, 3.2, ['apex', 'adept', 'sovereign'], [50, 25, 25]),
]
_VARIANTS = ('a', 'b', 'c')          # 'a' KEEPS the shipped record paths (T5 / diffs)
_DIFFEQ_FIELDS = ('difficultyEquationFile', 'difficultyLimitsFile')


def _tier_table(N, tier, variant):
    r"""Loot-table path for one (chest, difficulty, variant). Variant 'a' reuses the
    SHIPPED paths so the Legendary chain still reaches polisvault_0N (verify T5) and
    the record diff stays readable."""
    L = r'records\item\loottables\svc'
    if variant == 'a':
        return rf'{L}\polisvault_{N}.dbr' if tier == 'l' else rf'{L}\polisvault_{N}_{tier}.dbr'
    return rf'{L}\polisvault_{N}_{tier}{variant}.dbr'


def _tier_container(N, tier, variant):
    C = r'records\drxitem\container'
    suffix = tier if variant == 'a' else '%s%s' % (tier, variant)
    return rf'{C}\svc_polisvault_chest_{N}_{suffix}.dbr'

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


def _build_tier_loot(db, dest, tier, nmin, nmax, theme, clone=True):
    """One THEMED single-tier FixedItemLoot table for a placed chest.

    Clone the TIER-MATCHING bloodcave loot donor (so every base slot is already the
    right tier: bloodcave_01 = all _n01 + 01_act4_relics, _02 = _e01 + 02, _03 = _l01
    + 03) - that is why Normal drops Essence (01), Epic Embodiment (02), Legendary
    Incarnation (03) - then apply the polisvault richness (the placed chest's
    numSpawn), the chest's THEME on the guaranteed loot3 slot, and the shared weapon-
    row breadth (the aggregate master in the one free loot1 slot + the raised weapon /
    shield group chances). `clone=False` re-themes an EXISTING table in place, which
    is how the shipped Legendary polisvault_0N keeps its path (verify T5)."""
    if clone:
        db.clone_record(_BC_LOOT_DON[tier], dest)
    sf = db.set_field
    sf(dest, 'numSpawnMinEquation', '(3+(1.8*numberOfPlayers))*%s' % nmin)
    sf(dest, 'numSpawnMaxEquation', '(3+(1.8*numberOfPlayers))*%s' % nmax)
    SLB.set_guaranteed_theme(db, dest, tier, theme)
    SLB.widen_weapon_row(db, dest, tier)
    db._modified.add(dest)


def _convert_placed_chest_to_proxy(db, N, nmin, nmax, themes, weights):
    """Convert svc_polisvault_chest_NN from Class=FixedItemContainer to Class=Proxy
    IN PLACE at its existing path, building the 3-tier chain modeled on
    proxy_hidden_bloodcave_chest + _svc_build_dedicated_hoard. The per-difficulty
    containers are clones of the CURRENT golden chest, so the Majestic-Chest look,
    the Boss/100u Gaoler-death unlock, Hero loot classification and gold generator
    are all byte-preserved; only the loot table differs by difficulty.

    Will 2026-08-10: each difficulty now carries THREE themed variants behind one
    ProxyAccessoryPool (the base game's cave-boss-chest construction), so the six
    physical chests in the cage stop mirroring one another. Variant 'a' keeps the
    shipped record paths and the shipped richness."""
    sf = db.set_field
    C = r'records\drxitem\container'
    L = r'records\item\loottables\svc'
    chest = rf'{C}\svc_polisvault_chest_{N}.dbr'      # the placed record -> becomes a Proxy
    l_loot = rf'{L}\polisvault_{N}.dbr'               # shipped Legendary table (path preserved)

    # Fail-loud: the whole fix depends on the proven esti-chest chain donors.
    need = [_PROXY_DON, chest, l_loot] + list(_POOL_HIDDEN.values()) + list(_BC_LOOT_DON.values())
    missing = [d for d in need if not db.has_record(d)]
    if missing:
        raise SystemExit("polis_vault: Gaoler chest %s cannot be tiered - donor(s) "
                         "missing: %s" % (N, ', '.join(missing)))

    # 1. per-difficulty x per-variant FixedItemLoot tables. Variant 'a' at Legendary
    #    is the SHIPPED polisvault_0N record, re-themed in place (never re-cloned), so
    #    the Legendary chain still lands on the record verify T5 names.
    loot = {}
    for tier in ('n', 'e', 'l'):
        for v, theme in zip(_VARIANTS, themes):
            dest = _tier_table(N, tier, v)
            reuse = (v == 'a' and tier == 'l')
            _build_tier_loot(db, dest, tier, nmin, nmax, theme, clone=not reuse)
            loot[(tier, v)] = dest

    # 2. per-difficulty x per-variant FixedItemContainers (clone the golden chest for
    #    identical look + lock; retarget the loot table). LockedRadius 100 = the Gaoler
    #    100u unlock, NOT the 50 hoard default.
    cont = {}
    for tier in ('n', 'e', 'l'):
        for v in _VARIANTS:
            cpath = _tier_container(N, tier, v)
            db.clone_record(chest, cpath)             # golden FixedItemContainer donor (still intact here)
            sf(cpath, 'locked', 1)
            sf(cpath, 'LockedClassification', 'Boss')
            sf(cpath, 'LockedRadius', 100.0)
            sf(cpath, 'goldGeneratorChance', 100.0)
            sf(cpath, 'lootClassification', 'Hero')
            sf(cpath, 'tables', loot[(tier, v)])
            db._modified.add(cpath)
            cont[(tier, v)] = cpath

    # 3. per-difficulty ProxyAccessoryPools (clone the tier-matching hidden pool), each
    #    naming all THREE themed variants at 50/25/25 (the shipped theme stays the most
    #    common roll). fixedItemChance stays 100 so a chest always spawns.
    pool = {}
    for tier in ('n', 'e', 'l'):
        ppath = rf'{C}\svc_polisvault_pool_{N}_{tier}.dbr'
        db.clone_record(_POOL_HIDDEN[tier], ppath)
        sf(ppath, 'fixedItemChance', 100)
        for i, v in enumerate(_VARIANTS, start=1):
            sf(ppath, 'fixedItemName%d' % i, cont[(tier, v)], S)
            sf(ppath, 'fixedItemWeight%d' % i, int(weights[i - 1]))
        db._modified.add(ppath)
        pool[tier] = ppath

    # 4. CONVERT the placed chest IN PLACE: clone the proven esti-chest Proxy over
    #    the same path (record_type -> 'Proxy', Class -> 'Proxy', templateName ->
    #    Proxy.tpl, no FixedItemContainer field residue; difficultyEquationFile /
    #    difficultyLimitsFile = ContainerDifficultyEquation / ContainerLimitEquation
    #    ride the donor verbatim), then wire the 3 difficulty pools.
    db.clone_record(_PROXY_DON, chest)
    sf(chest, 'accessory1', pool['n'], S)
    sf(chest, 'accessoryEpic1', pool['e'], S)
    sf(chest, 'accessoryLegendary1', pool['l'], S)
    db._modified.add(chest)


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

    # ── WILL 2026-08-08: convert the 2 MAP-PLACED chests to per-difficulty
    #    Proxy chains so Normal drops Essence, Epic Embodiment, Legendary
    #    Incarnation (the Legendary chain keeps the polisvault_0N record). The 3
    #    unplaced chests (02/04/05) stay flat legendary FixedItemContainers -
    #    they are never placed, so they need no difficulty branch (and the
    #    retirement protocol keeps their records alive for verify T1). Their
    #    guaranteed weapon slot is still widened, by the build-wide
    #    chest_loot_breadth sweep, so a future placement inherits the breadth.
    # ── WILL 2026-08-10: each difficulty branch now carries 3 THEMED variants.
    # R-181 (Will 2026-08-10, "i am not really seeing armor drops"): the warden theme
    # now names the aggregate ARMOUR master, so that master must exist BEFORE any theme
    # is written - a theme member whose donor does not resolve is dropped, and a
    # silently dropped warden armour member is exactly the class of hole this wave is
    # closing. Both ensure_* helpers are idempotent, so armor_loot_breadth's own later
    # call is a no-op.
    SLB.ensure_masters(db)
    SAB.ensure_armor_masters(db)
    for N, nmin, nmax, themes, weights in _PLACED_TIERED:
        _convert_placed_chest_to_proxy(db, N, nmin, nmax, themes, weights)
    print("  POLIS VAULT: chest_01 + chest_03 (the placed pair) converted to "
          "Class=Proxy difficulty chains (accessory1/Epic1/Legendary1 -> pool -> "
          "3 THEMED golden FixedItemContainers -> single-tier loot; Essence/"
          "Embodiment/Incarnation on Normal/Epic/Legendary; guaranteed weapon:relic "
          "split preserved, weapon classes widened 3 -> 6 incl. SPEAR).")
    for N, _nmin, _nmax, themes, _w in _PLACED_TIERED:
        print("    chest_%s themes: %s" % (N, '; '.join(
            SLB.THEME_LABEL[t] for t in themes)))


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
# GAOLER-CHEST GATE (Will 2026-08-08, supersedes the R-100 #17 flat-chest gate).
# Runs in the registry's POST-FINALIZATION verify phase, i.e. over the FINAL
# assembled db, so a later writer cannot re-flatten the chests behind this
# module's back. The per-difficulty TIER-CORRECTNESS check is delegated to
# tools/gate_relic_difficulty_tiers.audit_proxy_chain so the in-build gate and the
# standalone audit share ONE implementation and cannot disagree. Negative tests:
# tools/debug/negtest_gaoler_chests.py.
# ─────────────────────────────────────────────────────────────────────────────
def _scalar(v):
    return v[0] if isinstance(v, list) and v else v


def verify(db, tags):
    """T1  all 5 chest records + 5 Legendary loot tables still EXIST (retirement
            protocol: halving the count withdrew PLACEMENTS, it never deleted a
            record). The 3 unplaced chests (02/04/05) stay FixedItemContainers.
        T2  each PLACED chest (01, 03) is Class=Proxy with all three difficulty
            accessory tiers wired AND difficultyEquationFile/difficultyLimitsFile
            set (so the engine actually branches on difficulty).
        T3  each placed chest's accessory1/Epic1/Legendary1 chain resolves
            proxy -> pool -> container -> loot table, and every relic + unique slot
            names the tier matching the accessory slot (accessory1 = Essence/01/n,
            accessoryEpic1 = Embodiment/02/e, accessoryLegendary1 = Incarnation/
            03/l). This is the Will 2026-08-08 order and the R-100 #17 successor.
        T4  EVERY per-difficulty container (all 3 themed variants of all 3
            difficulties) keeps the Boss lock (LockedClassification = Boss,
            LockedRadius = 100) so the Gaoler-death unlock survives, and its loot
            table's guaranteed loot3 slot stays 100%.
        T5  the Legendary chain still reaches the polisvault_0N table (Will's
            Legendary farm record + its numSpawn richness are unchanged), and every
            Legendary variant carries that same richness.
        T6  the map lane places exactly chest_01 + chest_03. Source-level assertion
            against build_section_surgery.B41_SPECS so DB + map cannot drift apart.
        T7  (Will 2026-08-10) DIFFERENTIATION + BREADTH: the 6 tables a placed chest
            can spawn per difficulty are not field-identical to one another, and
            every one of them can pay every weapon class at its own tier, SPEAR
            included. Delegated to svc_loot_breadth so gate, sweep and negtests
            share one implementation.
    """
    import gate_relic_difficulty_tiers as grdt
    problems = []
    placed_ids = {N for (N, *_r) in _PLACED_TIERED}

    # T1 - every chest record + Legendary loot table survives.
    for chest, loot in zip(_CHEST, _CHEST_LOOT):
        if not db.has_record(chest):
            problems.append("T1 chest record MISSING (never delete): %s" % chest)
        if not db.has_record(loot):
            problems.append("T1 Legendary loot table MISSING (never delete): %s" % loot)

    for N, nmin, nmax, themes, weights in _PLACED_TIERED:
        C = r'records\drxitem\container'
        L = r'records\item\loottables\svc'
        chest = rf'{C}\svc_polisvault_chest_{N}.dbr'
        if not db.has_record(chest):
            continue
        # T2 - it is a Proxy with the full difficulty branch.
        cls = str(_scalar(db.get_field_value(chest, 'Class')) or '')
        rtype = db._record_types.get(chest, '')
        if cls != 'Proxy' or rtype != 'Proxy':
            problems.append("T2 %s is not a Proxy (Class=%r, record_type=%r) - the "
                            "flat-container leak is back" % (chest, cls, rtype))
        for slot in ('accessory1', 'accessoryEpic1', 'accessoryLegendary1'):
            if not _scalar(db.get_field_value(chest, slot)):
                problems.append("T2 %s missing %s (no difficulty branch)" % (chest, slot))
        for f in _DIFFEQ_FIELDS:
            if not _scalar(db.get_field_value(chest, f)):
                problems.append("T2 %s missing %s" % (chest, f))
        # T3 - the tier-correctness of every difficulty branch (shared audit).
        problems.extend("T3 " + p for p in grdt.audit_proxy_chain(db, chest))
        # T4 - Boss lock survives + guaranteed slot stays on, on EVERY variant.
        for tier in ('n', 'e', 'l'):
            for v in _VARIANTS:
                cpath = _tier_container(N, tier, v)
                if not db.has_record(cpath):
                    problems.append("T4 per-difficulty container MISSING: %s" % cpath)
                    continue
                lc = str(_scalar(db.get_field_value(cpath, 'LockedClassification')) or '')
                lr = _scalar(db.get_field_value(cpath, 'LockedRadius'))
                if lc != 'Boss':
                    problems.append("T4 %s LockedClassification=%r, expected Boss" % (cpath, lc))
                if lr is None or abs(float(lr) - 100.0) > 0.01:
                    problems.append("T4 %s LockedRadius=%r, expected 100 (Gaoler unlock)" % (cpath, lr))
                lt = _scalar(db.get_field_value(cpath, 'tables'))
                ch3 = _scalar(db.get_field_value(grdt.real(db, lt), 'loot3Chance')) if lt else None
                if ch3 is None or abs(float(ch3) - 100.0) > 0.01:
                    problems.append("T4 %s -> %s loot3Chance=%r, expected 100"
                                    % (cpath, lt, ch3))
        # T5 - the Legendary chain reaches polisvault_0N (variant a), and every
        #      Legendary variant carries the placed chest's numSpawn richness.
        leg_cont = _tier_container(N, 'l', 'a')
        leg_tbl = _scalar(db.get_field_value(leg_cont, 'tables')) if db.has_record(leg_cont) else None
        want_leg = rf'{L}\polisvault_{N}.dbr'
        if str(leg_tbl or '').replace('/', '\\').lower() != want_leg.lower():
            problems.append("T5 %s Legendary tables=%r, expected the shipped %s"
                            % (leg_cont, leg_tbl, want_leg))
        for tier in ('n', 'e', 'l'):
            for v in _VARIANTS:
                tbl = grdt.real(db, _tier_table(N, tier, v))
                if not tbl:
                    problems.append("T5 loot table MISSING: %s" % _tier_table(N, tier, v))
                    continue
                for field, want in (('numSpawnMinEquation', nmin),
                                    ('numSpawnMaxEquation', nmax)):
                    got = str(_scalar(db.get_field_value(tbl, field)) or '')
                    if not got.endswith('*%s' % want):
                        problems.append("T5 %s %s=%r, expected the placed chest's "
                                        "richness *%s (payout must never shrink)"
                                        % (tbl, field, got, want))

    # T6 - the map half.
    try:
        import build_section_surgery as _bss
        placed = [p.decode('latin-1') if isinstance(p, bytes) else str(p)
                  for (p, *_rest) in _bss.B41_SPECS[_bss.B41_POLIS_KEY]]
        chests = [p for p in placed if 'svc_polisvault_chest' in p.lower()]
        want = ['svc_polisvault_chest_%s' % N for N in sorted(placed_ids)]
        got = [p.replace('/', '\\').lower().rsplit('\\', 1)[-1].replace('.dbr', '')
               for p in chests]
        if got != want:
            problems.append("T6 map places %r, expected %r" % (got, want))
    except Exception as exc:                      # pragma: no cover - import guard
        problems.append("T6 could not read build_section_surgery.B41_SPECS: %s" % exc)

    # T7 - differentiation + per-table breadth of everything the cage can spawn.
    lk = SLB.Lookup(db)
    ex = SLB.Expander(db, lk)
    families = {}
    for tier in ('n', 'e', 'l'):
        tables = [_tier_table(N, tier, v)
                  for (N, *_r) in _PLACED_TIERED for v in _VARIANTS]
        families['Gaoler cage [%s tier]' % tier] = tables
        for t in tables:
            if lk.real(t):
                problems.extend("T7 " + p for p in SLB.audit_table(db, t, tier, ex))
    problems.extend("T7 " + p for p in SLB.differentiation_problems(db, families, lk))

    if problems:
        for p in problems[:16]:
            print("  POLIS VAULT GATE OFFENDER: %s" % p)
        raise SystemExit("polis_vault gate FAILED: %d problem(s) (Gaoler tiering + "
                         "chest breadth)" % len(problems))
    print("  polis_vault gate PASS (Gaoler tiering + breadth): chest_01 + chest_03 "
          "are per-difficulty Proxies; Essence/Embodiment/Incarnation on Normal/Epic/"
          "Legendary; Boss-lock + 100u unlock intact on all 18 variant containers; "
          "Legendary record + numSpawn richness preserved; every cage table pays "
          "every weapon class (SPEAR included) and no two mirror each other; map "
          "places exactly the placed pair; 5 records + 5 Legendary tables retained.")
