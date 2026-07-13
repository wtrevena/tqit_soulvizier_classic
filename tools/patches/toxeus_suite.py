"""build37 registry module -- TOXEUS ENCOUNTER SUITE (backlog #32).

Registry contract (tools/patches/README.md): expose MODULE_NAME + apply(db, tags),
operating on the SAME db/tags objects the monolith (apply_svc_patches.py) already
built. The registry runs this module AFTER the monolith's apply_all_extended_patches,
so um_bloodtoxeus_99, q_bloodtoxeus_lone (_BT_POOL/_BT_PROXY), the Enslaver system,
and the Enslaver roaming sweep already exist + already ran when apply() is called.
Because the monolith's end-of-apply gates ALSO already ran (before this module), every
gate that guards this module's content is RE-RUN at the end of apply() (see _gate),
so the suite is self-validating whether or not the registry re-runs gates last.

WHAT THIS SHIPS (spec: scratchpad/specs/toxeus_encounter_suite_spec.md; decisions:
WILL_DECISIONS_2026-07-11.md; laws: docs/PLAYBOOK.md, amgoz1_design_voice.md):

  PART A - Entrance ambush.  A lone Blood-Toxeus proxy at chanceToRun=15 (Will: 15% in
    drxFirstRoom), a clone of the gate-proven chest proxy q_bloodtoxeus_lone reusing its
    exact pool (_BT_POOL = 1 Toxeus + 2 blood-demon adds). Registered in the monolith's
    _MOD_AUTHORED_SPAWN_PROXIES. MAP DELTA (map lane owns the placement): inject
    q_bloodtoxeus_ambush into levels/world/xbloodcave/drxFirstRoom.lvl.

  PART B - The rant scroll.  A readable Parchment (finalletter chassis) carrying Toxeus's
    blood-cult screed, wired one-per-player onto Blood Toxeus's FREE Misc4 slot @100%
    (Will: "guaranteed one-per-player Misc4 @100%, duplicates on repeat kills accepted").
    Per-player count via a FixedItemLoot.tpl table's numSpawn*Equation='numberOfPlayers*1'
    -> a LootItemTable_FixedWeight inner table -> the item (ADV-FIX §2.2: numSpawn lives
    ONLY on FixedItemLoot.tpl). LORE LAW (Will 2026-07-11): the screed treats the original
    Toxeus the Murderer as THE progenitor/GOAT of the blood-cult line.

  PART C - The Legendary-leaning stalker "the Endless Hunt".  A distinct, brutal roaming
    Toxeus stalker on the ShadowStalker rig (Will OVERRODE the spec's skeleton default:
    "ShadowStalker rig / am_deathstalker donor - distinct silhouette"). Confined to the
    Hades/endgame trash pools via a dedicated roaming sweep (the shipped Enslaver mechanism
    narrowed to Hades) so he reads as the endgame apex hunter - the honest closest thing to
    "Legendary-only" TQAE supports (the true data-only gate is not cleanly supported; §3.1).
    He drops his own granted-MOVE soul (his flash-powder shadow-burst - the Toxeus family
    signature - so the three Toxeus souls are three real builds: summon Devourer / summon
    Enslaver / BECOME the Hunt). The min-player-level experiment artifact limit_legendary_only
    is authored inert for Will's optional §3.4 test.

  PART D - 6-player readiness.  A fail-loud CHAMPION-COUNT-CAP invariant (no Toxeus placement
    may surface >1 of him at any party size) + the per-player scroll drop. The complex is
    otherwise already MP-safe (every placement caps Toxeus via championMax; pools are /-free).

ENGINE LAWS honored: never clone_record a soul (bare _create_soul); {^F} soul-name / {^r}
boss-red; no explicit dtype on cloned-record overrides (INT/FLOAT corruption trap); no em
dashes; castability (the soul proc toxeus_flashpowder has NO special anim -> universally
PC-castable, DB-verified); soul carries a downside (V1); evocative hand-designed name that
passes the {^F}<Monster> Soul standard.
"""

import re as _re
import sys as _sys
from pathlib import Path as _Path

# tools/ on the path so `import apply_svc_patches` + `arz_patcher` resolve regardless of cwd.
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import apply_svc_patches as asp
from arz_patcher import DATA_TYPE_STRING as S, DATA_TYPE_FLOAT as F, DATA_TYPE_INT as I

MODULE_NAME = 'toxeus_suite'

# ── Reused monolith records/constants (all DB-verified present in the build36 arz) ──
_BT_MONSTER = asp._BT_MONSTER          # um_bloodtoxeus_99 (Boss; Misc4 FREE, DB-verified)
_BT_PROXY = asp._BT_PROXY              # q_bloodtoxeus_lone (chest proxy, chanceToRun=100)
_BT_POOL = asp._BT_POOL                # 1 Toxeus + 2 blood-demon adds (spawn=3/champMin=Max=2)
_RIG_DONOR = asp._EN_RIG_DONOR         # am_deathstalker_55_ambush: ShadowStalker.msh, Demon, TABLE-LESS

# ── NEW record paths (all collision-free vs the built arz, probe-verified 2026-07-11) ──
_AMBUSH_PROXY = r'records\drxmap\proxy\q_bloodtoxeus_ambush.dbr'
_RANT_ITEM = r'records\item\svc\svc_toxeus_rant.dbr'
_RANT_TABLE_PERPLAYER = r'records\item\loottables\svc\toxeus_rant_perplayer.dbr'   # FixedItemLoot.tpl (numSpawn)
_RANT_TABLE_ITEM = r'records\item\loottables\svc\toxeus_rant_item.dbr'             # LootItemTable_FixedWeight
_HUNT_MONSTER = r'records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr'
_LEGENDARY_LIMIT = r'records\proxies orient\limit_legendary_only.dbr'

# ── Donors (DB-verified present) ──
_FINALLETTER = r'records\drxmap\quest\finalletter.dbr'                     # Parchment chassis
_FIXEDLOOT_DONOR = r'records\item\loottables\raremisc\01_n_hero_drops.dbr' # FixedItemLoot numSpawn idiom
_FIXEDWEIGHT_DONOR = r'records\item\loottables\svc\crimsonverdict_guaranteed_n.dbr'  # direct-item shape
_HEROLIMIT_DONOR = asp._BT_DONOR_LIMIT                                     # herolimit_all [1..75]

# ── The Hunt's distinct ShadowStalker skin (DB-verified shipped in DRXtextures.arc; used by
#    iceheart_shadowstalker_28_ambush + um_nephi'tek_33). The Enslaver MARAUDER uses the DEFAULT
#    ShadowStalker skin (baseTexture absent) + the shadow-cloak run FX, so pinning this distinct
#    skin (spec §3.2 requirement when the ShadowStalker rig is chosen) + a towering scale keeps the
#    Hunt from reading as a marauder. Cold/spectral = the deathless-pursuit third colour beside the
#    Devourer's crimson and the Enslaver's charcoal. ──
_HUNT_TEX = r'DRXTextures\creatures\shadowstalker\shadowstalker_iceheart.tex'

# ── Hunt kit (all DB-verified: classes + special-anim safety probed 2026-07-11). Paths pinned via
#    the monolith's _EN_SK_* constants (single source; the spec warns several basenames are doubled).
#    Anim-safety on the TABLE-LESS ShadowStalker rig: flashpowder (no special anim), bladestorm
#    (AoE360 - a PC-universal anim), lifedrain (no special anim), speedall/passives (no anim) are all
#    SAFE. netherstrike carries the special anim 'LethalStrike' (NOT PC-universal) -> anim resolution
#    on the table-less rig is the ONE launch-gated item (§3.2). It is production-precedented (the
#    original build32-35 Enslaver ran the Toxeus kit on THIS exact am_deathstalker rig), so it ships as
#    the flavour blink at MODERATE chance while the anim-safe flashpowder+bladestorm+speed carry the
#    "he keeps closing on you" identity. A silent no-op of netherstrike leaves the Hunt fully functional.
_SK_FLASHPOWDER = asp._EN_SK_FLASHPOWDER      # Skill_AttackRadius, no special anim (SAFE) - the core reposition
_SK_BLADESTORM = asp._EN_SK_BLADESTORM        # Skill_AttackProjectileRing, AoE360 (PC-universal, SAFE)
_SK_NETHERSTRIKE = asp._EN_SK_NETHERSTRIKE    # Skill_AttackWeaponBlink, LethalStrike anim (launch-gated)
_SK_LIFEDRAIN = asp._EN_SK_LIFEDRAIN          # Skill_AttackSpellChaos, no special anim (SAFE)
_SK_SPEEDALL = asp._EN_SK_SPEEDALL            # character_speedall aura (SAFE) - he chases
_SK_CONVIMMUNITY = asp._EN_SK_CONVIMMUNITY
_SK_HEROSCALING = asp._EN_SK_HEROSCALING
_SK_TOXEUSPASSIVE = asp._EN_SK_TOXEUSPASSIVE
_SK_ARMORPASSIVE = asp._EN_SK_ARMORPASSIVE
_SK_GP_N = asp._EN_SK_GP_N
_SK_GP_E = asp._EN_SK_GP_E
_SK_GP_L = asp._EN_SK_GP_L

# ── Soul payload (all DB-verified resolve + castability-safe) ──
_SOUL_PROC = asp._SS_FLASH_POWDER     # soulskills\toxeus_flashpowder.dbr: Skill_AttackRadius, NO special
                                      # anim -> universally PC-castable (DB-verified). WARN-listed in the
                                      # diversity gate (won't hard-fail). The Toxeus family signature verb
                                      # (his shadow-burst) -> ties the Hunt to the GOAT progenitor (V2).
_SOUL_AC = asp._AC_ON_HIT             # base_atself_onanyhit: a SELF controller (no autoTargetRadius needed)
_AUG_ANATOMY = asp._EN_AUG_ANATOMY    # drxanatomy: Skill_Modifier (+%vit/pierce) - DB-verified
_AUG_OPENWOUND = asp._BT_AUG_OPENWOUND  # drxopenwound: Skill_Modifier (bleed-on-attack) - DB-verified

# ── Roaming sweep tuning (Hades-only; parallels the Enslaver sweep, reuses its bad-subs) ──
# The Hunt uses its OWN 1/2400 per-slot ceiling (a findable Hades apex), matching this module's
# inject threshold (a pool is populated only when its pre-append wtotal >= 2399, so post-append
# p_slot = 1/(wtotal+1) <= 1/2400) and every docstring below. It does NOT reuse asp._EN_SWEEP_MAX_P:
# the ENSLAVER ceiling is far tighter (build38 BL-ENSLAVER-SPAWNS-V2: 1/2400 -> 1/24000 via
# _EN_SWEEP_CEIL); reusing it here would make the verify (1/24000) reject the very pools the inject
# (1/2400) legitimately populated - the Enslaver reaches 1/24000 by x600'ing (asp._EN_SWEEP_K) member
# weights, which the Hunt deliberately does NOT do (it only appends weight 1 to the existing pool).
# Decoupled so inject and verify agree again.
_LS_ALLOW_PREFIX = ('records\\xpack\\proxieshades',)   # Hades trash pools ONLY (378 ProxyPools present)
_LS_MAX_P = 1.0 / 2400.0                                 # the Hunt's own ceiling (matches the inject)


# =============================================================================
# small helpers
# =============================================================================
def _del_fields(db, rec, names):
    """Delete the given field(s) from a record's decoded dict (NEVER blank a donor
    ref to '' - the B-TOXEUS-2 zero-precedent loader-abort law). names may be exact
    field names or a predicate callable(fieldname)->bool."""
    ff = db.get_fields(rec)
    if not ff:
        return
    pred = names if callable(names) else (lambda fn: fn in names)
    for k in list(ff):
        if pred(k.split('###')[0]):
            del ff[k]
    db._modified.add(rec)


def _gv1(db, rec, f):
    v = db.get_field_value(rec, f)
    return v[0] if isinstance(v, list) else v


# =============================================================================
# PART A - entrance ambush proxy (chanceToRun=15, drxFirstRoom)
# =============================================================================
def _create_ambush_proxy(db):
    """Clone the gate-proven chest proxy q_bloodtoxeus_lone -> q_bloodtoxeus_ambush and set
    chanceToRun=15 (Will's default; a single clean roll per room-load = a reliable 15% spawn
    probability, unlike championChance which would compound across the pool's 8 demon slots).
    Reuses _BT_POOL verbatim (1 Toxeus + 2 blood-demon adds) - no new pool, no new monster.
    Registers the proxy in _MOD_AUTHORED_SPAWN_PROXIES so the spawn-eligibility gate covers it.
    MAP DELTA: the map lane injects this proxy into drxFirstRoom (byte-shape = q_leinth_lone;
    coord derived on-mesh at build time)."""
    if not (db.has_record(_BT_PROXY) and db.has_record(_BT_POOL)):
        raise SystemExit("[toxeus_suite] PART A: q_bloodtoxeus_lone proxy/pool missing "
                         "(monolith must build Blood Toxeus before this module runs)")
    db.clone_record(_BT_PROXY, _AMBUSH_PROXY)
    # chanceToRun exists on the donor (=100.0, FLOAT); override value only (preserve dtype).
    db.set_field(_AMBUSH_PROXY, 'chanceToRun', 15.0)
    db.set_field(_AMBUSH_PROXY, 'pool1', _BT_POOL)   # explicit (the clone already points here)
    db._modified.add(_AMBUSH_PROXY)

    # register for the spawn-eligibility invariant (same pool/boss/limit as the chest proxy).
    already = any(spec.get('proxy') == _AMBUSH_PROXY for spec in asp._MOD_AUTHORED_SPAWN_PROXIES)
    if not already:
        asp._MOD_AUTHORED_SPAWN_PROXIES.append({
            'proxy': _AMBUSH_PROXY,
            'pool': _BT_POOL,
            'main_monster': _BT_MONSTER,
            'name': 'q_bloodtoxeus_ambush (Toxeus entrance ambush @ chanceToRun=15)',
        })
    print("  [A] entrance ambush: q_bloodtoxeus_ambush @ chanceToRun=15 (reuses _BT_POOL = "
          "1 Toxeus + 2 blood demons); registered for spawn-eligibility. "
          "MAP DELTA -> drxFirstRoom.lvl")


# =============================================================================
# PART B - the rant scroll (per-player Misc4 @100%)
# =============================================================================
# The rant body (spec §2.3): a single flowing paragraph led by the ^r colour code (the
# finalletter format, DB-verified - the scroll window word-wraps; no newline tokens). Villain
# monologue in Toxeus's own voice, mythically grounded in the established cauldron/drowned-blood
# lore, MP-aware ("bring your friends"), no memes/anachronism, no em dashes. LORE LAW: it treats
# the original murderer as the eternal progenitor whom the blood form merely continues.
_RANT_TEXT = (
    "^rYou found the wet page. Good. Read it aloud, so the walls remember your voice too. They "
    "called me a murderer as if the word were an insult, as if it were not a crown. I opened "
    "Athens throat by throat, and the city thanked me with its silence. Then your heroes came and "
    "cut me down in the dark and called that the end of the sentence. It was not even the comma. "
    "The cult drowned me in the cauldron beneath the falls and boiled the poison out of my marrow, "
    "and they poured the blood of the drowned back into my dry veins until I was full, fuller than "
    "any living thing has the right to be. I do not kill for coin now, nor for quiet. I kill "
    "because every heartbeat in this cave is a debt, and I have come to collect all of them at "
    "once. You feel it already: the itch beneath the skin, the small wounds that will not close. "
    "That is only me, reading you the way you are reading me. When you bleed, I am taking back what "
    "was always mine. Come to the deep door. Bring your friends. I will open every one of you at "
    "once, and drink the room dry, and leave this page for the next fool who mistakes an ending for "
    "a stop."
)


def _create_rant_scroll(db, tags):
    """Item + 2 loot tables + the Misc4 wire (+ 3 tags). Per-player count via FixedItemLoot's
    numSpawn*Equation='numberOfPlayers*1' -> a direct-item FixedWeight inner table -> the item."""
    if not db.has_record(_FINALLETTER):
        raise SystemExit(f"[toxeus_suite] PART B: finalletter donor missing ({_FINALLETTER})")
    for donor in (_FIXEDLOOT_DONOR, _FIXEDWEIGHT_DONOR):
        if not db.has_record(donor):
            raise SystemExit(f"[toxeus_suite] PART B: loot-table donor missing ({donor})")

    # ── 1. The readable item (clone the widow-letter Parchment chassis, DB-proven readable). ──
    db.clone_record(_FINALLETTER, _RANT_ITEM)
    # itemNameTag is ABSENT on the donor -> a NEW field (set_field infers STRING).
    db.set_field(_RANT_ITEM, 'itemNameTag', 'tagSVCToxeusRantNAME')
    db.set_field(_RANT_ITEM, 'description', 'tagSVCToxeusRantGROUND')   # on-ground pickup label
    db.set_field(_RANT_ITEM, 'itemText', 'tagSVCToxeusRantTEXT')        # the readable body
    db.set_field(_RANT_ITEM, 'FileDescription',
                 'A blood-soaked screed left by Toxeus the Murderer.')
    # Magical (spec §2.2 default): a keepable readable that does NOT clog the quest log AND is
    # vendorable. Parchment.tpl drives the right-click "read", so Magical SHOULD stay readable.
    # ** LAUNCH-GATED (§2.2/§4.2.7c smoke test): confirm read-shows-itemText AND vendorable in
    #    2-player before relying on it; fallback = the donor's Quest classification (readable,
    #    proven, but quest-log clutter + no vendor). ** mesh/baseTexture/bitmap/templateName/Class
    #    all carry over from the donor (all resolve at runtime - the donor ships fine).
    db.set_field(_RANT_ITEM, 'itemClassification', 'Magical')
    db._modified.add(_RANT_ITEM)

    # ── 2. Inner direct-item table (the crimsonverdict_guaranteed shape: a FixedWeight table
    #    whose lootName* point straight at items). Delete the donor's extra 3 item slots so ONLY
    #    the rant drops (delete, never blank to '' - B-TOXEUS-2). ──
    db.clone_record(_FIXEDWEIGHT_DONOR, _RANT_TABLE_ITEM)
    db.set_field(_RANT_TABLE_ITEM, 'lootName1', _RANT_ITEM)
    db.set_field(_RANT_TABLE_ITEM, 'lootWeight1', 100)
    _del_fields(db, _RANT_TABLE_ITEM,
                lambda fn: bool(_re.match(r'loot(Name|Weight)([2-9]|1[0-9])$', fn)))
    db._modified.add(_RANT_TABLE_ITEM)

    # ── 3. Outer per-player table - MUST be FixedItemLoot.tpl (the ONLY template carrying
    #    numSpawn*Equation, DB-verified 311/311). numSpawn = numberOfPlayers*1 (/-free; the item
    #    evaluator accepts numberOfPlayers). loot1 -> the inner table @100%. Zero the donor's other
    #    weights/chances. Satisfies the container loot-slot SHAPE gate (loot1Name1 resolves +
    #    numSpawnMin/MaxEquation non-empty). ──
    db.clone_record(_FIXEDLOOT_DONOR, _RANT_TABLE_PERPLAYER)
    T = _RANT_TABLE_PERPLAYER
    db.set_field(T, 'numSpawnMinEquation', 'numberOfPlayers*1')
    db.set_field(T, 'numSpawnMaxEquation', 'numberOfPlayers*1')
    db.set_field(T, 'loot1Chance', 100.0)
    db.set_field(T, 'loot1Name1', _RANT_TABLE_ITEM)
    db.set_field(T, 'loot1Weight1', 100)
    # zero the donor's remaining loot1 alt-item weights + the loot2..6 slots (dormant shape).
    for j in range(2, 7):
        if db.get_field_value(T, f'loot1Weight{j}') is not None:
            db.set_field(T, f'loot1Weight{j}', 0)
    for n in range(2, 7):
        if db.get_field_value(T, f'loot{n}Chance') is not None:
            db.set_field(T, f'loot{n}Chance', 0.0)
    if db.get_field_value(T, 'goldGeneratorLevel') is not None:
        db.set_field(T, 'goldGeneratorLevel', 0)
    db._modified.add(T)

    # ── 4. Wire to Blood Toxeus's FREE Misc4 slot @100% (Will: guaranteed one-per-player). All
    #    three difficulty columns point at the same table (the rant is difficulty-agnostic).
    #    ** LAUNCH-GATED edge (§2.2): whether a MONSTER equip slot honours the sub-table's numSpawn
    #       is UNPROVEN (proven only for containers). If the 2-player test yields 1 copy, flip to the
    #       per-player-container fallback: a corpse/chest whose loottable=toxeus_rant_perplayer (this
    #       SAME table - already container-ready), spawned on Blood-Toxeus death. That is a one-record
    #       + one-death-skill follow-up; the reusable per-player table is authored here. ── ##
    if db.has_record(_BT_MONSTER):
        db.set_field(_BT_MONSTER, 'chanceToEquipMisc4', 100.0)
        db.set_field(_BT_MONSTER, 'chanceToEquipMisc4Item1', 100)
        db.set_field(_BT_MONSTER, 'lootMisc4Item1', [T, T, T], S)
        db.set_field(_BT_MONSTER, 'dropItems', 1)
        db._modified.add(_BT_MONSTER)
    else:
        raise SystemExit(f"[toxeus_suite] PART B: um_bloodtoxeus_99 missing ({_BT_MONSTER})")

    # ── 5. Tags. {^r} boss-red inventory name; distinct on-ground label (so it does not read as
    #    the widow's "Tattered Parchment"). ──
    tags['tagSVCToxeusRantNAME'] = "{^r}The Murderer's Screed"
    tags['tagSVCToxeusRantGROUND'] = 'A Parchment Slick with Blood'
    tags['tagSVCToxeusRantTEXT'] = _RANT_TEXT
    print("  [B] rant scroll: svc_toxeus_rant (Parchment/Magical) + FixedItemLoot per-player table "
          "(numSpawn='numberOfPlayers*1') -> FixedWeight item table; wired Blood-Toxeus Misc4 @100%; "
          "3 tags. (monster-equip-slot numSpawn = launch-gated; container fallback documented)")


# =============================================================================
# PART C - the Legendary-leaning stalker "the Endless Hunt" (ShadowStalker rig)
# =============================================================================
def _create_legendary_stalker(db, tags):
    """Monster (ShadowStalker rig, distinct skin, brutal Legendary tuning) -> its granted-MOVE
    soul (flash-powder shadow-burst + evasion/pierce stats + a downside) -> Hades-only roaming
    sweep -> fail-loud sweep verify."""
    if not db.has_record(_RIG_DONOR):
        raise SystemExit(f"[toxeus_suite] PART C: ShadowStalker rig donor missing ({_RIG_DONOR})")

    # ── 1. The monster: clone am_deathstalker (ShadowStalker.msh, Demon, TABLE-LESS inline anim -
    #    the rig Will chose for a distinct silhouette), then override to a distinct-skin Boss apex. ──
    db.clone_record(_RIG_DONOR, _HUNT_MONSTER)
    M = _HUNT_MONSTER
    db.set_field(M, 'description', 'tagSVCMonsterToxeusHunt')
    db.set_field(M, 'monsterClassification', 'Boss')
    db.set_field(M, 'characterRacialProfile', 'Demon')          # inherited; explicit
    db.set_field(M, 'baseTexture', _HUNT_TEX)                    # DISTINCT skin (vs the marauder's default)
    db.set_field(M, 'charLevel', [40, 68, 100])
    db.set_field(M, 'characterLife', [16000.0, 22000.0, 30000.0])  # above the Enslaver's 13/18/24k
    db.set_field(M, 'characterStrength', 500.0)
    db.set_field(M, 'characterDexterity', 700.0)
    db.set_field(M, 'characterIntelligence', 440.0)
    db.set_field(M, 'characterLifeRegen', 12.0)
    db.set_field(M, 'handHitDamageMin', 170.0)
    db.set_field(M, 'handHitDamageMax', 280.0)
    db.set_field(M, 'scale', 1.9)               # towering apex (donor/marauder are ~1.1) - reinforces
    db.set_field(M, 'actorHeight', 2.4)          # the distinct silhouette beside the marauder
    db.set_field(M, 'characterRunSpeed', 1.8)    # he chases (donor 1.65)
    # Defensive wall via FLAT resists = pierce/pursuit identity (NOT the Devourer's bleed zpassive).
    db.set_field(M, 'defensiveLife', 100.0)
    db.set_field(M, 'defensivePierce', 80.0)
    db.set_field(M, 'defensivePhysical', 40.0)
    # kit: delete the donor's trash passive skillNames + special-attack slots, then author.
    _del_fields(db, M, lambda fn: bool(_re.match(r'skillName([1-9]|1[0-9]|20)$', fn)))
    _del_fields(db, M, lambda fn: bool(_re.match(r'specialAttack([2-9]?)SkillName$', fn)))
    kit = [
        _SK_FLASHPOWDER, _SK_BLADESTORM, _SK_NETHERSTRIKE, _SK_LIFEDRAIN, _SK_SPEEDALL,
        _SK_CONVIMMUNITY, _SK_HEROSCALING, _SK_TOXEUSPASSIVE, _SK_ARMORPASSIVE,
        _SK_GP_N, _SK_GP_E, _SK_GP_L,
    ]
    for i, sk in enumerate(kit, start=1):
        db.set_field(M, f'skillName{i}', sk, S)
    # special-attack casting: the anim-safe reposition (flashpowder) + AoE (bladestorm) carry the
    # "keeps closing on you" feel at HIGH chance; netherstrike (launch-gated anim) is the flavour
    # blink at MODERATE chance; lifedrain feeds. (specialAttack has no numeric suffix; 2..N do.)
    specials = [(_SK_FLASHPOWDER, 45.0), (_SK_BLADESTORM, 40.0),
                (_SK_NETHERSTRIKE, 30.0), (_SK_LIFEDRAIN, 30.0)]
    for i, (sk, ch) in enumerate(specials, start=1):
        suf = '' if i == 1 else str(i)
        db.set_field(M, f'specialAttack{suf}SkillName', sk, S)
        db.set_field(M, f'specialAttack{suf}Chance', ch, F)
    db.set_field(M, 'dropItems', 1)
    db._modified.add(M)

    # ── 2. His soul: a granted-MOVE (his flash-powder shadow-burst, the Toxeus family signature ->
    #    ties the Hunt to the GOAT progenitor) - DELIBERATELY distinct from the two summon-Toxeus
    #    souls (Devourer/Enslaver) so the family offers three real builds. Pursuit/pierce/evasion
    #    stat signature with a V1 downside (he neglects his own guard for the chase). ──
    def _stats(t):
        m = {'n': 0.6, 'e': 0.82, 'l': 1.0}[t]
        r = lambda v: round(v * m, 1)
        sklvl = {'n': 4, 'e': 6, 'l': 8}[t]
        auglvl = {'n': 3, 'e': 4, 'l': 5}[t]
        return {
            **asp._bmp(t),                                   # per-tier soul icon
            'itemSkillName': (S, _SOUL_PROC), 'itemSkillLevel': (I, sklvl),
            'itemSkillAutoController': (S, _SOUL_AC),
            'augmentSkillName1': (S, _AUG_ANATOMY), 'augmentSkillLevel1': (I, auglvl),
            'augmentSkillName2': (S, _AUG_OPENWOUND), 'augmentSkillLevel2': (I, auglvl),
            # offensive: pierce + physical + lifeleech (feeds on the hunt)
            'offensivePhysicalMin': (F, r(60.0)), 'offensivePhysicalMax': (F, r(95.0)),
            'offensivePhysicalModifier': (I, int(r(35))),
            'offensivePierceRatioMin': (F, r(30.0)),
            'offensivePierceRatioModifier': (I, int(r(22))),
            'offensiveLifeLeechMin': (F, r(40.0)),
            'characterOffensiveAbility': (F, r(90.0)),
            # the hunt itself: run speed + active evasion (dodge/deflect)
            'characterRunSpeedModifier': (F, r(18.0)),
            'characterDodgePercent': (F, r(12.0)),
            'characterDeflectProjectile': (F, r(12.0)),
            'characterDexterityModifier': (F, r(10.0)),
            'characterDexterity': (F, r(35.0)),
            'characterStrength': (F, r(25.0)),
            'characterLife': (F, r(180.0)),
            'defensivePierce': (F, r(25.0)),
            # V1 DOWNSIDE (grows with tier): so bent on the kill he leaves his guard open - he evades
            # by movement, never by blocking. Paired with high dodge/deflect, this IS the identity.
            'characterDefensiveAbility': (F, -{'n': 30.0, 'e': 40.0, 'l': 50.0}[t]),
        }
    tiers = [{'diff': t, 'itemLevel': il, 'stats': _stats(t)}
             for t, il in (('n', 40), ('e', 68), ('l', 100))]
    hunt_souls = asp._create_soul(db, 'toxeus_hunt', 'tagSVCSoulToxeusHunt', tiers,
                                  monster=_HUNT_MONSTER, drop_rate=25.0)   # Boss release rate
    # amgoz1 V5: FileDescription = the region word (he roams Hades), not a lore paragraph.
    for sp in hunt_souls:
        if db.has_record(sp):
            db.set_field(sp, 'FileDescription', 'Hades')
            db._modified.add(sp)

    # ── 3. Roaming sweep into Hades trash pools + fail-loud verify. ──
    touched = _sweep_inject_legendary_stalker(db)
    _verify_legendary_stalker_sweep(db, touched)

    # ── 4. Tags. Name passes the {^F}<Monster> Soul standard (starts {^F}, ends ' Soul', no
    #    'Soul of '). The DESC honours the GOAT progenitor (LORE LAW). ──
    tags['tagSVCMonsterToxeusHunt'] = '{^r}Toxeus the Murderer, the Endless Hunt'
    tags['tagSVCSoulToxeusHunt'] = '{^F}Toxeus the Murderer, the Endless Hunt Soul'
    tags['tagSVCSoulToxeusHuntDESC'] = (
        'The shadow the first murderer casts when he runs you down beyond death. Toxeus the '
        'progenitor does not tire and does not stop; his hunt outlasts the hunted. Its bearer '
        'takes his relentless step, his evasion, and the flash-burst that opens the range.')
    print(f"  [C] stalker: um_toxeus_hunt_99 (ShadowStalker rig, distinct iceheart skin, Boss "
          f"[40,68,100] life 16/22/30k, pierce/pursuit) + granted-MOVE soul (flash-powder @25%) + "
          f"Hades-only sweep touched {len(touched)} pools; 3 tags. (netherstrike anim = launch-gated)")


def _sweep_inject_legendary_stalker(db):
    """Append the stalker at weight 1 to every ELIGIBLE Hades trash pool (allow-prefix =
    xpack\\proxieshades ONLY), so his per-slot probability stays <= 1/2400 (a genuine rare
    hunter). Parallels the Enslaver's _sweep_inject_roaming_rare with two deliberate differences:
      (1) Hades-only prefix (he only appears in Act-4/Hades -> "effectively Legendary" endgame);
      (2) the Enslaver sweep ALREADY RAN (in the monolith) and x600'd (asp._EN_SWEEP_K) these pools'
          member weights + added itself at weight 1, so this sweep does NOT re-multiply (that would
          break the Enslaver's weight-1 invariant + over-inflate); it simply appends the stalker at
          weight 1 into a free slot, which keeps BOTH rares at weight 1 with p_slot <= 1/2400 (a pool
          the Enslaver already qualified has total >= 24000, so 1/(total+1) << 1/2400).
    Reuses the Enslaver's eligibility guards (skip q_/sq/xsq/mq/svc_ + boss/quest/hero/escort/
    summon/... basenames; all resolvable name members Class=Monster; a free name slot). Returns the
    list of touched pool record names. Deterministic (sorted iteration)."""
    if not db.has_record(_HUNT_MONSTER):
        print("  [C] STALKER SWEEP: monster missing; skipped")
        return []
    recmap = {n.replace('/', '\\').lower(): n for n in db.record_names()}
    hunt_lc = _HUNT_MONSTER.replace('/', '\\').lower()

    def gv(n, f):
        v = db.get_field_value(n, f)
        return v[0] if isinstance(v, list) else v

    def is_pool(n):
        t = gv(n, 'templateName')
        return t and 'proxypool.tpl' in str(t).lower()

    def eligible(n):
        nl = n.replace('/', '\\').lower()
        if not any(nl.startswith(p) for p in _LS_ALLOW_PREFIX):
            return False
        base = nl.split('\\')[-1]
        if base.startswith(('q_', 'sq', 'xsq', 'mq', 'svc_')):
            return False
        if any(b in base for b in asp._EN_SWEEP_BAD_SUB):
            return False
        names = [gv(n, 'name%d' % i) for i in range(1, 19)]
        names = [str(x) for x in names if x and str(x).strip()]
        if not names:
            return False
        for m in names:
            r = recmap.get(m.replace('/', '\\').lower())
            if r is not None and str(gv(r, 'Class')) != 'Monster':
                return False
        return True

    touched = []
    for n in sorted(db.record_names()):
        if not is_pool(n) or not eligible(n):
            continue
        used = []
        wtotal = 0
        already = False
        for i in range(1, 19):
            nm = gv(n, 'name%d' % i)
            if nm and str(nm).strip():
                used.append(i)
                if str(nm).replace('/', '\\').lower() == hunt_lc:
                    already = True
                w = gv(n, 'weight%d' % i)
                try:
                    wtotal += int(w) if w else 0
                except (TypeError, ValueError):
                    pass
        if already:                          # idempotence
            continue
        free = next((i for i in range(1, 19) if i not in used), None)
        if free is None:                     # at 18-slot cap
            continue
        if wtotal < 2399:                    # weight-1 append must keep p_slot <= 1/2400
            continue
        db.set_field(n, 'name%d' % free, _HUNT_MONSTER, S)
        db.set_field(n, 'weight%d' % free, 1, I)
        db._modified.add(n)
        touched.append(n)
    print("  [C] STALKER SWEEP: injected the roaming Hunt into %d eligible Hades trash pool(s) "
          "(weight 1; existing weights untouched to preserve the Enslaver's invariant)"
          % len(touched))
    return touched


def _verify_legendary_stalker_sweep(db, touched):
    """FAIL-LOUD gate (parallels _verify_roaming_sweep, Hades-scoped): re-derive the touched set
    from the arz and prove ONLY eligible Hades trash pools carry the stalker, each at weight 1 with
    p_slot <= 1/2400, the monster resolves at band [40,68,100], and there is no leak into a
    non-Hades or boss/quest/hero pool (every stalker-bearing pool must be in `touched` - there is no
    dedicated stalker pool, so no whitelist)."""
    problems = []

    def gv(n, f):
        v = db.get_field_value(n, f)
        return v[0] if isinstance(v, list) else v

    if not db.has_record(_HUNT_MONSTER):
        problems.append(f"{_HUNT_MONSTER} missing")
    else:
        cl = db.get_field_value(_HUNT_MONSTER, 'charLevel')
        cl = cl if isinstance(cl, list) else [cl]
        if [int(x) for x in cl] != [40, 68, 100]:
            problems.append(f"stalker charLevel {cl} != [40, 68, 100]")

    hunt = _HUNT_MONSTER.replace('/', '\\').lower()
    derived = []
    for n in db.record_names():
        t = gv(n, 'templateName')
        if not (t and 'proxypool.tpl' in str(t).lower()):
            continue
        names = [gv(n, 'name%d' % i) for i in range(1, 19)]
        if any(x and str(x).replace('/', '\\').lower() == hunt for x in names):
            derived.append(n)

    if set(derived) != set(touched):
        problems.append(f"touched set mismatch: sweep touched {len(touched)}, arz shows "
                        f"{len(derived)} pools with the stalker")

    for n in derived:
        nl = n.replace('/', '\\').lower()
        base = nl.split('\\')[-1]
        if not any(nl.startswith(p) for p in _LS_ALLOW_PREFIX):
            problems.append(f"STALKER LEAK non-Hades path: {n}")
        if base.startswith(('q_', 'sq', 'xsq', 'mq', 'svc_')) or \
                any(b in base for b in asp._EN_SWEEP_BAD_SUB):
            problems.append(f"STALKER LEAK boss/quest/hero pool: {n}")
        wtotal = 0
        hw = None
        for i in range(1, 19):
            nm = gv(n, 'name%d' % i)
            if not (nm and str(nm).strip()):
                continue
            w = gv(n, 'weight%d' % i)
            try:
                w = int(w) if w else 0
            except (TypeError, ValueError):
                w = 0
            wtotal += w
            if str(nm).replace('/', '\\').lower() == hunt:
                hw = w
        if hw != 1:
            problems.append(f"{n}: stalker weight {hw} != 1")
        elif wtotal <= 0 or (1.0 / wtotal) > _LS_MAX_P + 1e-9:
            problems.append(f"{n}: stalker p_slot {1.0 / max(wtotal, 1):.5f} > "
                            f"{_LS_MAX_P:.5f} (too common)")

    if not derived:
        problems.append("stalker sweep touched ZERO Hades pools (the Hunt would never appear)")

    if problems:
        for p in problems[:20]:
            print(f"  STALKER-SWEEP OFFENDER: {p}")
        raise SystemExit(
            f"Legendary-stalker roaming-sweep gate FAILED: {len(problems)} problem(s)")
    print(f"  [C] stalker-sweep gate OK: {len(derived)} eligible Hades trash pools carry the Hunt "
          f"at weight 1 (p_slot <= 1/2400); 0 non-Hades / boss / quest / hero leaks; band [40,68,100].")


def _author_legendary_only_limit(db):
    """Option-2 experiment artifact (§3.4), authored INERT for Will's optional test: a ProxyLimits
    whose Normal + Epic PLAYER-level windows start at 85 (unreachable on those difficulties) while
    Legendary stays [1..110]. IF the engine treats "player level below the window min" as "proxy
    dormant" (untested; it demonstrably treats ABOVE-max as scale-not-filter), a dedicated stalker
    PROXY carrying this file would spawn ONLY on Legendary = a true data-only Legendary-only gate.
    NOT registered in _MOD_AUTHORED_SPAWN_PROXIES (the eligibility gate would - correctly - reject a
    below-window main), NOT placed on the map. FOLLOW-UP for the experiment (DB one-liner + a map
    INJECT_SPECS entry, out of this module's DB scope): clone q_bloodtoxeus_lone -> q_toxeus_hunt
    with pool1 = a dedicated stalker pool + difficultyLimitsFile = this record, place it at a
    Hades/endgame spot, and test on a Normal character (spawns on Normal -> keep Option 1; never on
    Normal but on Legendary -> promote Option 2)."""
    if not db.has_record(_HEROLIMIT_DONOR):
        print(f"  [C] WARNING: herolimit_all donor missing ({_HEROLIMIT_DONOR}); "
              f"limit_legendary_only experiment record skipped")
        return
    db.clone_record(_HEROLIMIT_DONOR, _LEGENDARY_LIMIT)
    L = _LEGENDARY_LIMIT
    # ProxyLimits equations are STRING fields ('<n> * 1'); keep the donor's STRING dtype.
    db.set_field(L, 'minPlayerLevelEquationNormal', '85 * 1')
    db.set_field(L, 'maxPlayerLevelEquationNormal', '110 * 1')
    db.set_field(L, 'minPlayerLevelEquationEpic', '85 * 1')
    db.set_field(L, 'maxPlayerLevelEquationEpic', '110 * 1')
    db.set_field(L, 'minPlayerLevelEquationLegendary', '1 * 1')
    db.set_field(L, 'maxPlayerLevelEquationLegendary', '110 * 1')
    db._modified.add(L)
    print("  [C] experiment artifact: limit_legendary_only authored INERT (N/E window [85..110]; "
          "L [1..110]); q_toxeus_hunt placement = documented follow-up (out of DB scope)")


# =============================================================================
# PART D - MP champion-count cap invariant (fail-loud)
# =============================================================================
def _verify_toxeus_champion_cap(db):
    """FAIL-LOUD MP invariant (§4.2.2): no Toxeus placement may surface >1 of him at any party
    size. The entrance/chest/parchment single-boss placements ALL reuse _BT_POOL, so proving
    _BT_POOL yields EXACTLY 1 guaranteed Toxeus main (spawnMax - championMax == 1, and every filled
    name slot is Toxeus) makes "one Toxeus per encounter, any party size" a hard invariant (the
    championMax cap is never per-player-multiplied). Complements the spawn-eligibility gate's LOWER
    bound (>= 1 main) with this UPPER bound (== 1 main)."""
    P, Mn = _BT_POOL, _BT_MONSTER
    if not db.has_record(P):
        raise SystemExit(f"[toxeus_suite] PART D: _BT_POOL missing ({P})")

    def gi(f, d=0):
        v = _gv1(db, P, f)
        return d if v is None else v

    sm = int(gi('spawnMax', 0))
    cc = float(gi('championChance', 0.0) or 0.0)
    cmax = int(gi('championMax', 0))
    mains = sm if cc <= 0 else (sm - cmax)
    names = [_gv1(db, P, f'name{i}') for i in range(1, 7)]
    names = [str(n) for n in names if n and str(n).strip()]
    problems = []
    if not names or any(n.replace('/', '\\').lower() != Mn.replace('/', '\\').lower() for n in names):
        problems.append(f"_BT_POOL name slots are not all Toxeus: "
                        f"{[n.split(chr(92))[-1] for n in names]}")
    if mains != 1:
        problems.append(f"_BT_POOL guaranteed Toxeus mains = {mains} != 1 "
                        f"(spawnMax={sm}, championChance={cc}, championMax={cmax}); a party could "
                        f"surface >1 Toxeus")
    if problems:
        for p in problems:
            print(f"  CHAMPION-CAP OFFENDER: {p}")
        raise SystemExit(f"Toxeus champion-count-cap invariant FAILED: {len(problems)} problem(s)")
    print("  [D] champion-count-cap invariant OK: exactly 1 Toxeus per encounter (any party size); "
          "the per-player scroll is the only new MP surface (live-test-gated).")


# =============================================================================
# self-gating: re-run every invariant that guards this module's content
# =============================================================================
def _gate(db, tags):
    """Re-run the monolith gates relevant to this suite (they ran in the monolith BEFORE this
    module, so they must be re-run over the final db to cover this module's records) + this
    module's own invariants. Each monolith gate is called defensively so an upstream rename WARNS
    (never silently skips a real failure: a present gate still fails loud)."""
    # this module's own invariants (always run; fail loud).
    _verify_toxeus_champion_cap(db)

    # monolith invariants re-run over the final db. Pure verifications (raise SystemExit on a real
    # failure); safe + idempotent to re-run. _verify_soul_naming needs the shared tags dict.
    monolith_gates = [
        ('_verify_mod_spawn_proxies_eligible', (db,)),      # covers q_bloodtoxeus_ambush
        ('_verify_no_slash_in_spawn_equations', (db,)),
        ('_verify_no_unclassified_soul_leaks', (db,)),
        ('_verify_soul_augments_resolve', (db,)),           # covers the Hunt soul refs
        ('_verify_soul_itemskill_activation', (db,)),       # covers the Hunt soul proc chain
        ('_verify_granted_skill_diversity', (db,)),
        ('_verify_soul_naming', (db, tags)),                # covers tagSVCSoulToxeusHunt
    ]
    for fn_name, args in monolith_gates:
        fn = getattr(asp, fn_name, None)
        if fn is None:
            print(f"  [toxeus_suite] WARNING: monolith gate {fn_name} not found (API drift?); "
                  f"skipped its re-run")
            continue
        fn(*args)
    print("  [toxeus_suite] self-gate PASS: champion-cap + spawn-eligibility + soul (leak/augment/"
          "activation/diversity/naming) + no-slash re-verified over the final db.")


# =============================================================================
# registry entry point
# =============================================================================
def apply(db, tags):
    """Registry entry point. db + tags are the SAME objects the monolith built; mutate them in
    place. Order: ambush proxy -> rant scroll -> stalker (monster -> soul -> sweep -> internal
    sweep verify) -> experiment artifact.

    The champion-count-cap invariant (D) + the re-run of the monolith gates that guard this
    suite's content live in verify() (the registry's POST-FINALIZATION phase), NOT here. Reason:
    run_registry_gates has not yet de-filled Ground Smash, fixed the MP spawn equations, or
    applied the soul-naming standard when apply() runs mid-registry - so re-running those monolith
    gates here would trip on ordering artifacts the finalization later clears (e.g. the 8 dev-soul
    cyclops_groundsmash grants -> _verify_granted_skill_diversity GS-roster failure). This is the
    build37 gate-relocation law (see patches.run_registry_verifies + skill_quality)."""
    print("\n=== [toxeus_suite] build37 TOXEUS ENCOUNTER SUITE (backlog #32) ===")
    _create_ambush_proxy(db)             # A
    _create_rant_scroll(db, tags)        # B
    _create_legendary_stalker(db, tags)  # C (monster -> soul -> Hades sweep -> internal sweep verify)
    _author_legendary_only_limit(db)     # C experiment artifact (inert)
    print("=== [toxeus_suite] done (D + guarding gates run in verify(), post-finalization) ===\n")
    return tags


def verify(db, tags=None):
    """POST-FINALIZATION registry verify hook (patches.run_registry_verifies). Runs D (the
    champion-count-cap MP invariant) + re-runs the monolith gates that guard this suite's content
    (spawn-eligibility, soul leak/augment/activation/diversity/naming, no-slash MP equations) over
    the FINAL assembled db - AFTER run_registry_gates' finalization. Running them here rather than in
    apply() is what keeps them from tripping on the mid-registry ordering artifacts the finalization
    clears. Fail-loud (SystemExit) on any real violation, which run_registry_verifies propagates."""
    _gate(db, tags if tags is not None else {})
    return tags
