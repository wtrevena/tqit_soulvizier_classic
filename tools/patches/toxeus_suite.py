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

  PART A - Parchment ambush.  A lone Blood-Toxeus proxy at chanceToRun=33 (the ONE
    Blood-Toxeus chance in the entrance corridor), a clone of the gate-proven chest proxy
    q_bloodtoxeus_lone reusing its exact pool (_BT_POOL = 1 Toxeus + 2 blood-demon adds - the
    entourage / "his guys" requirement is inherently satisfied). Registered in the monolith's
    _MOD_AUTHORED_SPAWN_PROXIES. This lane only sets the DB chanceToRun field (33), no map
    change here. The map placement is in build_section_surgery.py: b79 (Will 2026-07-16)
    RELOCATED it from drxFirstRoom to drxFirstxistion_connection - right next to the tattered
    parchment + the native demon swarm - because Will's design is that he spawns WITH his guys
    ON the parchment, and drxFirstRoom was a different room. Still exactly ONE ~33% roll
    (relocated, not added); the retired ~50% parchment feature (demon_01_cluster_toxeus50 +
    q_bloodtoxeus_lone_50) stays removed so he cannot spawn twice.

  PART B - The rant scroll.  A readable Parchment (finalletter chassis) carrying Toxeus's
    blood-cult screed, wired one-per-player onto Blood Toxeus's FREE Misc4 slot @100%
    (Will: "guaranteed one-per-player Misc4 @100%, duplicates on repeat kills accepted").
    Per-player count via a FixedItemLoot.tpl table's numSpawn*Equation='numberOfPlayers*1'
    -> a LootItemTable_FixedWeight inner table -> the item (ADV-FIX §2.2: numSpawn lives
    ONLY on FixedItemLoot.tpl). LORE LAW (Will 2026-07-11): the screed treats the original
    Toxeus the Murderer as THE progenitor/GOAT of the blood-cult line.

  PART C - The Legendary-leaning stalker "the Endless Hunt".  A distinct, brutal roaming
    Toxeus stalker on the ShadowStalker rig (Will OVERRODE the spec's skeleton default:
    "ShadowStalker rig / am_deathstalker donor - distinct silhouette"). Roams the
    `records\\xpack\\proxieshades` trash pools via a dedicated roaming sweep (the shipped
    Enslaver mechanism, re-scoped) so he reads as the endgame apex hunter.
    ⚠️ CORRECTION (b98, 2026-07-28) - THIS PARAGRAPH USED TO SAY "confined to Hades" AND
    "narrowed to Hades", AND IT WAS WRONG. `records\\xpack\\proxieshades\\` is the WHOLE
    Immortal Throne proxy namespace, not the Hades act: the base game filed RHODES inside it
    as area001. The 540 proxies this sweep reaches span area001 Rhodes (70), area002 Medea's
    Grove (76), area003 Epirus (55), area004 Styx (78), area005 Plains of Judgement (79),
    area006 Tower of Judgement (49), area007 Elysian Fields (82) and area008 Hades Palace (49).
    365 of them define ONLY poolN (which resolves on ALL THREE difficulties) and ZERO define
    poolLegendaryN, so the roam was never Legendary-leaning either - it has always been
    Normal + Epic + Legendary, everywhere in Act IV and V. Will meeting the roaming Hunt in
    RHODES on EPIC is this sweep working exactly as built, not a defect. What kept him
    invisible on Normal is RARITY, not a difficulty gate: at the shipped flat weight 1 against
    pool totals of 36,000..660,000 he was worth 0.0368 sightings per full Act IV+V pass - ONE
    PER 27 PLAYTHROUGHS. R-96 (Will 2026-07-28, "roughly one sighting per act") retunes that to
    a per-pool NORMALISED weight targeting a constant p_slot of 1/1250: measured 0.955 sightings
    in Act IV, 1.034 in Act V, 1.989 over a full pass. Retune him at _LS_TARGET_P_SLOT and
    nowhere else. The single fixed encounter's Legendary-only
    gate lived on the PROXY and is removed by tools/patches/toxeus_hunt_encounter.py (R-90).
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
                                      # anim -> universally PC-castable (DB-verified).
# ⚠️ b98 ROUND 2 (R-94, feat/endless-hunt): THIS IS NO LONGER THE SHIPPED GRANT.
# `toxeus_hunt_encounter` RETIRES flash powder from the Hunt's own kit (it was one of the
# 9 skills he shared with the Enslaver), so leaving his soul granting it left the one
# player-facing artifact of his identity handing out an ability he no longer has - and
# pointing at an over-shared filler (15 soul records grant it). That module, which runs
# LATER in the registry and authors the replacement, repoints all three tiers to
# `svc_hunt_quarrysmark` at itemSkillLevel 1/2/3 and asserts it fail-loud. The value here
# is deliberately left as the SHIPPED pre-state so that module's "another writer owns his
# soul grant" guard still has something to recognise; do not "tidy" it to the new path
# without moving that guard too.
_SOUL_AC = asp._AC_ON_HIT             # base_atself_onanyhit: a SELF controller (no autoTargetRadius needed)
_AUG_ANATOMY = asp._EN_AUG_ANATOMY    # drxanatomy: Skill_Modifier (+%vit/pierce) - DB-verified
_AUG_OPENWOUND = asp._BT_AUG_OPENWOUND  # drxopenwound: Skill_Modifier (bleed-on-attack) - DB-verified

# ── Roaming sweep tuning (parallels the Enslaver sweep, reuses its bad-subs) ──
# ⚠️ THE ONE LINE THAT CAUSED THE "HADES-ONLY" MYTH (corrected b98, 2026-07-28). This prefix is
# NOT "Hades trash pools ONLY" - `records\xpack\proxieshades\` is the WHOLE Immortal Throne proxy
# namespace (the base game filed Rhodes inside it as area001), so the sweep spans area001..area008:
# Rhodes, Medea's Grove, Epirus, Styx, Plains of Judgement, Tower of Judgement, Elysian Fields and
# Hades Palace. The NAME of the folder is the only thing about it that says "hades". The prefix
# itself is CORRECT and unchanged - only the claim about what it means was wrong.
_LS_ALLOW_PREFIX = ('records\\xpack\\proxieshades',)   # the whole IT proxy namespace (378 ProxyPools present)

# ═════════════════════════════════════════════════════════════════════════════
# THE ROAM RATE - R-96 (Will, 2026-07-28): "roughly one sighting per act".
# ═════════════════════════════════════════════════════════════════════════════
# ⚠️ WILL-VETO CLASS (the R-18 precedent: a rate change on these champions is Will's call, never
# an implementer's). THIS IS THE ONE PLACE TO RETUNE HIM. Change _LS_TARGET_P_SLOT and nothing
# else; the per-pool weights, the inject and the gate all derive from it.
#
# WHAT IT MEANS: the Hunt's slot is normalised so his probability per pool draw is the SAME
# CONSTANT in every pool - _LS_TARGET_P_SLOT - instead of a flat weight. A flat weight cannot
# work here: the pool weight TOTALS span 36,000..660,000 (an 18.3x spread, because the natives
# are x600-scaled by different amounts), so one flat weight makes him 18x rarer in Rhodes than
# in the Hades Palace for no design reason. Normalising is what makes "one per act" mean the
# same thing in all eight areas.
#
# THE DERIVATION (measured 2026-07-28 against the built arz + the shipped world01.map, NOT
# estimated - see docs/reports/b98_endless_hunt.md section 12 for the full table):
#   345 roaming pools carry him; each resolved pool makes k main draws (k = (spawnMin+spawnMax)/2,
#     measured mean 3.19, median 3, max 13.5) and every one of the 539 referencing proxies has
#     chanceToRun = 100.
#   The shipped map places those proxies 797 times across the Immortal Throne:
#     ACT IV  Rhodes 54 + Medea 134 + Epirus 69 + Styx 149            = 406 placements
#     ACT V   Judgement 175 + Elysian 131 + Hades Palace 85           = 391 placements
#   => 2,486 effective main draws over a full Act IV+V pass at 1 player.
#   E[sightings] = SUM over placements of chanceToRun * (1 - (1-p_slot)^k)   [limitN=1 caps the
#   COUNT at 1 per pool per trigger, so each placement contributes at most 1 = P(at least one)].
#   Solving E = 1 per act (2 per pass) gives p_slot = 1/1243; 1/1250 is the round retunable value.
#
# THE RESULT AT 1/1250 (what Will will actually see, per act):
#     ACT IV 0.955 sightings | ACT V 1.034 sightings | FULL PASS 1.989
#   i.e. "reliably met once or twice per playthrough, not never" - 54x the shipped rate.
#   BEFORE (flat weight 1): 0.0368 per pass = one sighting per 27 playthroughs, which is why
#   Will met him once on Epic and never on Normal. He was never Legendary-gated; he was rare.
#
# HE IS FAR RARER THAN THE NATIVES: at 1/1250 his slot weight is 29..528 (median 53) against
# native members carrying 18,000 each. Near-mythical, but no longer effectively invisible.
#
# ⚠️ CORRECTION (round 4, 2026-07-29). Rounds 3 said "still the rarest member of EVERY pool". That
# is FALSE and was caught by the adversarial vet, then re-measured here off the built arz: in
# **63 of the 346** pools he rides, `um_toxeus_enslaver_99` is also a member and is still on the OLD
# FLAT scheme at weight 1, i.e. p_slot 1/60,049..1/66,054 against the Hunt's normalised ~1/1,250.
# In every pool they share, the HUNT IS NOW ~48-53x MORE COMMON THAN THE ENSLAVER. (The other
# "rarer" rows are weight-0 inert members - checked, 0 of them live.) Nothing is broken by this;
# R-96 normalised the Hunt only, and the Enslaver's own sweep rate is WILL-VETO under R-18 so this
# lane must not touch it. But it is a DESIGN QUESTION for Will, registered as BL-b98-DEBT-11: the
# apex Hunt now appears ~50x more often than the champion he is meant to sit alongside.
_LS_TARGET_P_SLOT = 1.0 / 1250.0

# Gate tolerance. Weights are integers, so a pool's realised p_slot cannot land exactly on the
# target; the rounding error is largest in the poorest pools (36,000 -> weight 29). +/-4% covers
# integer rounding with margin and still catches a real mistuning.
_LS_P_SLOT_TOL = 0.04

# ── THE CENSUS THE SIGHTINGS FIGURE RESTS ON (round 4: made machine-readable + gated) ────────
# Rounds 3 carried the placement census as PROSE in the comment above and nothing re-derived the
# headline "one sighting per act" from it. The p_slot invariant was gated; the number Will actually
# approved was not. So if the world ever changed, p_slot would stay green while the sightings claim
# went quietly stale. These constants close that: the gate below recomputes E[sightings] from them
# and fails if it leaves the band the ruling names.
#
# EFFECTIVE MAIN DRAWS per act over a full pass at 1 player = SUM over that act's placements of the
# pool's k (k = (spawnMin+spawnMax)/2), measured 2026-07-28 against the SHIPPED world01.map.
# 797 placements (Act IV 406 / Act V 391) -> 2,486 effective draws.
_LS_CENSUS_DRAWS = {'IV': 1194, 'V': 1292}          # 2,486 total
_LS_CENSUS_PLACEMENTS = {'IV': 406, 'V': 391}       # 797 total
# The census is only valid for the map it was measured on. STAMP IT so a future map change cannot
# silently invalidate the sightings claim. Re-measure with:
#     py tools/debug/census_placements.py <Levels.arc> --dbr um_toxeus_hunt_99
_LS_CENSUS_LEVELS_ARC_MD5 = '943d0ab9516d332db79bd7f9fd2d3ffe'
# "roughly one sighting per act" (R-96), as a band a machine can check rather than a claim a human
# has to re-read. Deliberately wide: the ruling is "roughly one", and Will chose it over both
# "a few per act" and "leave him a rumour", so the band has to exclude BOTH of those neighbours.
_LS_SIGHTINGS_BAND = (0.70, 1.40)


def _ls_expected_sightings(p=None):
    """E[sightings] per act and per full pass, re-derived from the census constants.

    Model (report section 12.2): a placement contributes P(at least one) =
    1 - (1-p)^k, not k*p, because pool main draws are with replacement and
    limitN=1 caps the COUNT at one Hunt per pool per trigger. Aggregated over an
    act's placements this is the act's effective-draw total against p."""
    p = _LS_TARGET_P_SLOT if p is None else p
    out = {}
    for act, draws in _LS_CENSUS_DRAWS.items():
        # 1-(1-p)^draws would model the whole act as ONE placement; the per-placement
        # sum is what the report derives, and at p<<1 it is draws*p to <0.1%.
        out[act] = draws * p
    out['PASS'] = sum(out[a] for a in _LS_CENSUS_DRAWS)
    return out


def _ls_census_gate():
    """R-96 SIGHTINGS GATE (round 4). Two legs, both new.

    LEG 1 (hard): re-derive the sightings figure from _LS_TARGET_P_SLOT + the census
    and require every act to land inside the band the ruling names. This is what makes
    the constant retunable SAFELY - move it too far in either direction and the build
    reds instead of quietly shipping a different design than the one Will approved.

    LEG 2 (loud, not fatal): stamp WHICH Levels.arc the census was measured on and say
    so in every build log. If a Levels.arc is resolvable and is not the stamped one, the
    sightings claim does not apply to it and the log says exactly that, with the remedy.
    It is not fatal because this is a DB-only build that does not own the map, and the
    staged and deployed maps legitimately differ between waves - a red here would be a
    false alarm about somebody else's artifact. SVC_CENSUS_STRICT=1 makes it fatal for
    a map lane that wants the harder contract."""
    import hashlib
    import os

    e = _ls_expected_sightings()
    lo, hi = _LS_SIGHTINGS_BAND
    bad = [a for a in _LS_CENSUS_DRAWS if not (lo <= e[a] <= hi)]
    print(f"  [C] R-96 sightings re-derived from the census: "
          f"Act IV {e['IV']:.3f} | Act V {e['V']:.3f} | full pass {e['PASS']:.3f} "
          f"(p_slot 1/{1.0/_LS_TARGET_P_SLOT:.0f}, {sum(_LS_CENSUS_PLACEMENTS.values())} placements, "
          f"{sum(_LS_CENSUS_DRAWS.values())} effective draws)")
    if bad:
        raise SystemExit(
            f"R-96 SIGHTINGS GATE FAILED: act(s) {sorted(bad)} land outside the "
            f"'roughly one sighting per act' band {_LS_SIGHTINGS_BAND} "
            f"({ {a: round(e[a], 3) for a in sorted(_LS_CENSUS_DRAWS)} }). "
            f"_LS_TARGET_P_SLOT is 1/{1.0/_LS_TARGET_P_SLOT:.0f}. Either retune it back "
            f"inside the ruling or get a NEW ruling from Will - this is WILL-VETO class "
            f"(R-18 precedent).")

    cand = [os.environ.get('SVC_LEVELS_ARC')]
    here = _Path(__file__).resolve().parents[2]
    cand += [str(here / 'work' / 'SoulvizierClassic' / 'Resources' / 'Levels.arc'),
             str(here / 'local' / 'Levels_merged.arc')]
    seen = next((c for c in cand if c and os.path.isfile(c)), None)
    print(f"  [C] R-96 census provenance: measured against Levels.arc "
          f"{_LS_CENSUS_LEVELS_ARC_MD5} - the sightings figure above is valid for THAT map.")
    if not seen:
        print("      (no Levels.arc reachable from this DB-only build; stamp printed, not compared)")
        return
    h = hashlib.md5()
    with open(seen, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    got = h.hexdigest()
    if got == _LS_CENSUS_LEVELS_ARC_MD5:
        print(f"      re-affirmed: {seen} matches the stamp.")
        return
    msg = (f"R-96 CENSUS STAMP MISMATCH: {seen} is {got}, the census was measured on "
           f"{_LS_CENSUS_LEVELS_ARC_MD5}. The p_slot invariant is unaffected (it is per-pool "
           f"and map-independent), but the '~1 sighting per act' figure is NOT proven for this "
           f"map. NOTE this can be a STAGING artifact rather than a real world change - the "
           f"map staged in work/ is not always the map that is deployed - so check WHICH of the "
           f"two moved before assuming the census is stale. Re-measure with: "
           f"py tools/debug/census_placements.py \"{seen}\" "
           f"--dbr um_toxeus_hunt_99, then update _LS_CENSUS_DRAWS / _LS_CENSUS_PLACEMENTS / "
           f"_LS_CENSUS_LEVELS_ARC_MD5 together.")
    if os.environ.get('SVC_CENSUS_STRICT') == '1':
        raise SystemExit(msg)
    print("  ⚠ WARNING " + msg)


_LS_SLOT_LIMIT = 1   # per-slot MAX-count cap on the Hunt's name slot (mirrors asp._EN_SWEEP_SLOT_LIMIT).
                     # Pool MAIN draws are independent WITH REPLACEMENT (proven: vanilla pools spawn more
                     # mains than they have name slots), so a plain weight-1 member in a pack pool with
                     # spawnMax>1 could surface 2+ Hunts in ONE trigger -- the exact "two-in-one-trigger"
                     # defect the Enslaver v2 sweep just fixed. Vanilla ALWAYS caps rare pack members at
                     # limitN=1; this stamps the same cap so at most ONE Hunt spawns per pool per trigger.
                     # It matters MORE at the R-96 rate than it did at weight 1: with p_slot 1/1250 and a
                     # 13-draw pool, P(2+ without the cap) is ~5e-5 per trigger, ~0.04 over a full pass.


def _ls_slot_weight(wtotal):
    """The Hunt's NORMALISED slot weight for a pool whose OTHER members total `wtotal`.

    Solves w / (wtotal + w) == _LS_TARGET_P_SLOT for w, so every pool delivers the same
    per-draw probability regardless of how hard the natives were scaled. Integer, >= 1.
    This is the single source of truth: the inject writes it and the gate re-derives it."""
    p = _LS_TARGET_P_SLOT
    return max(1, int(round(p * wtotal / (1.0 - p))))


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
# PART A - entrance ambush proxy (chanceToRun=33, drxFirstRoom; Will retuned 15->33 2026-07-14)
# =============================================================================
def _create_ambush_proxy(db):
    """Clone the gate-proven chest proxy q_bloodtoxeus_lone -> q_bloodtoxeus_ambush and set
    chanceToRun=33 (Will FINAL DESIGN 2026-07-14, retuned 15 -> 33; a single clean roll per
    room-load = a reliable ~33% spawn probability, unlike championChance which would compound
    across the pool's demon slots). Reuses _BT_POOL verbatim (1 Toxeus + 2 blood-demon adds) -
    no new pool, no new monster. Registers the proxy in _MOD_AUTHORED_SPAWN_PROXIES so the
    spawn-eligibility gate covers it. This is the ONLY Blood-Toxeus chance in the entrance
    corridor: Will retired the never-wired ~50% parchment feature (demon_01_cluster_toxeus50 +
    q_bloodtoxeus_lone_50) and bumped this single ambush to 33 so he cannot spawn twice.
    NO MAP CHANGE this lane - the placement lives in the map lane (build_section_surgery.py);
    b79 relocated it from drxFirstRoom into drxFirstxistion_connection next to the tattered
    parchment so the Devourer spawns WITH his guys ON the parchment. This is a pure DB retune."""
    if not (db.has_record(_BT_PROXY) and db.has_record(_BT_POOL)):
        raise SystemExit("[toxeus_suite] PART A: q_bloodtoxeus_lone proxy/pool missing "
                         "(monolith must build Blood Toxeus before this module runs)")
    db.clone_record(_BT_PROXY, _AMBUSH_PROXY)
    # chanceToRun exists on the donor (=100.0, FLOAT); override value only (preserve dtype).
    # Will retuned 15 -> 33 (final design 2026-07-14): the single entrance Blood-Toxeus roll.
    db.set_field(_AMBUSH_PROXY, 'chanceToRun', 33.0)
    db.set_field(_AMBUSH_PROXY, 'pool1', _BT_POOL)   # explicit (the clone already points here)
    db._modified.add(_AMBUSH_PROXY)

    # register for the spawn-eligibility invariant (same pool/boss/limit as the chest proxy).
    already = any(spec.get('proxy') == _AMBUSH_PROXY for spec in asp._MOD_AUTHORED_SPAWN_PROXIES)
    if not already:
        asp._MOD_AUTHORED_SPAWN_PROXIES.append({
            'proxy': _AMBUSH_PROXY,
            'pool': _BT_POOL,
            'main_monster': _BT_MONSTER,
            'name': 'q_bloodtoxeus_ambush (Toxeus entrance ambush @ chanceToRun=33)',
        })
    print("  [A] entrance ambush: q_bloodtoxeus_ambush @ chanceToRun=33 (reuses _BT_POOL = "
          "1 Toxeus + 2 blood demons); registered for spawn-eligibility. The ONLY corridor "
          "Blood-Toxeus roll (parchment 50% feature retired). NO MAP CHANGE (placement shipped).")


# =============================================================================
# PART B - the rant scroll (per-player Misc4 @100%)
# =============================================================================
# The rant body (spec §2.3): led by the ^r blood-red colour code and broken into 4 beats with ^n^n
# paragraph breaks - matching the finalletter donor (which itself leads ^r and breaks with ^n^n,
# DB-verified) and the vanilla parchment paragraph convention (see docs/reports/rant_scroll_corpus.md;
# the scroll window also word-wraps). Villain
# monologue in Toxeus's own voice, mythically grounded in the established cauldron/drowned-blood
# lore, MP-aware ("bring your friends"), no memes/anachronism, no em dashes. LORE LAW: it treats
# the original murderer as the eternal progenitor whom the blood form merely continues.
_RANT_TEXT = (
    "^rYou found the wet page. Good. Read it aloud, so the walls remember your voice too. They "
    "called me a murderer as if the word were an insult, as if it were not a crown. I opened "
    "Athens throat by throat, and the city thanked me with its silence. ^n^nThen your heroes came and "
    "cut me down in the dark and called that the end of the sentence. It was not even the comma. "
    "The cult drowned me in the cauldron beneath the falls and boiled the poison out of my marrow, "
    "and they poured the blood of the drowned back into my dry veins until I was full, fuller than "
    "any living thing has the right to be. ^n^nI do not kill for coin now, nor for quiet. I kill "
    "because every heartbeat in this cave is a debt, and I have come to collect all of them at "
    "once. You feel it already: the itch beneath the skin, the small wounds that will not close. "
    "That is only me, reading you the way you are reading me. ^n^nWhen you bleed, I am taking back what "
    "was always mine. Come to the deep door. Bring your friends. Bring all of them. There is room "
    "in me. I will open every one of you at "
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
    # b98 ROUND 2 (R-94): the last clause described the FLASH-BURST, which is no longer
    # what this soul grants. `toxeus_hunt_encounter` repoints the grant to Quarry's Mark
    # and its verify() fails the build if this text still advertises the flash powder.
    tags['tagSVCSoulToxeusHuntDESC'] = (
        'The shadow the first murderer casts when he runs you down beyond death. Toxeus the '
        'progenitor does not tire and does not stop; his hunt outlasts the hunted. Its bearer '
        'takes his relentless step, his evasion, and his mark: what you wound, you keep.')
    print(f"  [C] stalker: um_toxeus_hunt_99 (ShadowStalker rig, distinct iceheart skin, Boss "
          f"[40,68,100] life 16/22/30k, pierce/pursuit) + granted-MOVE soul + Immortal-Throne-wide "
          f"roaming sweep touched {len(touched)} pools; 3 tags. (b98 repoints the drop rate to 100 "
          f"[R-91], the soul grant to Quarry's Mark [R-94] and replaces netherstrike outright)")


def _sweep_inject_legendary_stalker(db):
    """Append the stalker to every ELIGIBLE Immortal-Throne trash pool (allow-prefix =
    xpack\\proxieshades ONLY) at the R-96 NORMALISED weight, so his per-draw probability is the
    SAME constant (_LS_TARGET_P_SLOT, 1/1250) in every pool regardless of how hard that pool's
    natives were scaled. Will 2026-07-28: "roughly one sighting per act" - measured 0.955 in Act
    IV, 1.034 in Act V, 1.989 over a full pass. See _LS_TARGET_P_SLOT for the full derivation and
    for the ONE constant to change when retuning him.
    Before R-96 this appended a FLAT weight 1, which (a) left him at ~1 sighting per 27
    playthroughs - Will met him once on Epic and never on Normal - and (b) because pool totals
    span 36,000..660,000, made him 18.3x rarer in Rhodes than in the Hades Palace for no design
    reason. The pool SET is deliberately unchanged; only the weight in the appended slot moved.
    Parallels the Enslaver's _sweep_inject_roaming_rare with two deliberate differences:
      (1) the `xpack\\proxieshades` prefix - which is the WHOLE Immortal Throne proxy namespace
          (area001 Rhodes through area008 Hades Palace), NOT the Hades act, and NOT a difficulty
          gate of any kind. See the _LS_ALLOW_PREFIX comment and the b98 correction above;
      (2) the Enslaver sweep ALREADY RAN (in the monolith). Where the Enslaver is PRESENT (its
          `undead` pools) it already x600'd (asp._EN_SWEEP_K) the member weights, so this sweep
          does NOT re-multiply those (that would double-scale, and the normalised weight is
          derived FROM the post-scale total so a double-scale would silently halve his rate); it
          just appends the stalker at the normalised weight into a free slot.
          Where the Enslaver is ABSENT (b49: it now scales ONLY undead pools, so the ~282 non-undead
          Hades pools it used to scale are back at original weights), this sweep TAKES OVER the same
          x600 itself (same floor) so the Hunt keeps its FULL Hades breadth + identical 1/24000 rarity
          instead of collapsing to the 63 undead pools. Behavior-neutral for those pools (a uniform
          scale preserves relative spawn odds); the ONLY net arz change vs build38 is the Enslaver
          leaving the non-undead pools.
    Like the Enslaver v2 sweep, the appended slot carries a per-slot limit=1 (_LS_SLOT_LIMIT) MAX-count
    cap: pool mains draw WITH REPLACEMENT, so without it a pack pool (spawnMax>1) could surface 2+ Hunts
    in ONE trigger -- the exact "two-in-one-trigger" defect just fixed for the Enslaver. With limit=1 the
    engine spawns AT MOST ONE Hunt per pool per spawn trigger, structurally, at any party size.
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

    enl_lc = asp._EN_BOSS.replace('/', '\\').lower()
    touched = []
    hweights = []
    self_scaled = 0
    for n in sorted(db.record_names()):
        if not is_pool(n) or not eligible(n):
            continue
        used = []
        wtotal = 0
        already = False
        has_enslaver = False
        for i in range(1, 19):
            nm = gv(n, 'name%d' % i)
            if nm and str(nm).strip():
                used.append(i)
                nml = str(nm).replace('/', '\\').lower()
                if nml == hunt_lc:
                    already = True
                elif nml == enl_lc:
                    has_enslaver = True
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
        # b49 BREADTH COUPLING (Will 2026-07-13): the Enslaver sweep now x600's ONLY the
        # `undead` family pools ("FEW deliberate places"), so the non-undead Hades pools it
        # used to scale no longer clear the Hunt's 1/2400 rarity floor. The Hunt's full Hades
        # breadth was previously a SIDE EFFECT of the Enslaver x600'ing EVERY Hades pool; make
        # it self-sufficient so the Hunt is PRESERVED EXACTLY (same ~345 pools, same 1/24000
        # p_slot) instead of collapsing to the 63 undead Hades pools. When the Enslaver is
        # ABSENT (pool not undead-scaled), take over the SAME x600 (asp._EN_SWEEP_K), gated by
        # the Enslaver's OWN qualifier (asp._EN_SWEEP_CEIL over the original wtotal) so the
        # Hades pool SET is identical. When the Enslaver IS present the pool is already x600'd
        # -> do NOT re-scale (no double-scale). Net effect on the Enslaver: NONE (it already
        # left these pools); this is behavior-neutral (a uniform scale preserves relative
        # spawn odds) and just relocates the x600 from the Enslaver sweep to here.
        if not has_enslaver:
            if wtotal <= 0 or (asp._EN_SWEEP_K * wtotal + 1) < asp._EN_SWEEP_CEIL:
                continue                     # below the Enslaver floor -> never x600'd -> skip
            for i in used:
                w = gv(n, 'weight%d' % i)
                try:
                    w = int(w) if w else 0
                except (TypeError, ValueError):
                    w = 0
                db.set_field(n, 'weight%d' % i, w * asp._EN_SWEEP_K, I)
            wtotal *= asp._EN_SWEEP_K
            self_scaled += 1
        if wtotal < 2399:                    # pool-eligibility floor (unchanged: keeps the pool SET
            continue                         # identical to the pre-R-96 sweep; post-x600 totals are
                                             # >= 36,000, so this never binds in practice)
        # R-96 (Will 2026-07-28, "roughly one sighting per act"): the slot weight is NORMALISED
        # per pool so p_slot is the same constant everywhere, instead of the flat weight 1 that
        # made him 18x rarer in Rhodes than in the Hades Palace and ~1-in-27-playthroughs overall.
        # Derivation + measured per-act numbers: see _LS_TARGET_P_SLOT above.
        hw = _ls_slot_weight(wtotal)
        db.set_field(n, 'name%d' % free, _HUNT_MONSTER, S)
        db.set_field(n, 'weight%d' % free, hw, I)
        db.set_field(n, 'limit%d' % free, _LS_SLOT_LIMIT, I)   # structural: <=1 Hunt/trigger (mirrors enslaver v2)
        db._modified.add(n)
        touched.append(n)
        hweights.append(hw)
    _wmin = min(hweights) if hweights else 0
    _wmax = max(hweights) if hweights else 0
    print("  [C] STALKER SWEEP: injected the roaming Hunt into %d eligible Immortal-Throne trash "
          "pool(s) at the R-96 NORMALISED rate p_slot=1/%.0f (weight %d..%d per pool, per-slot "
          "limit 1 = <=1 Hunt/trigger); %d of them self-x600'd here (non-undead pools the b49 "
          "Enslaver breadth-restrict no longer scales -- Hunt breadth preserved, was ~345). "
          "Target: ~1 sighting per act (measured 0.955 Act IV / 1.034 Act V / 1.989 per full pass)."
          % (len(touched), 1.0 / _LS_TARGET_P_SLOT, _wmin, _wmax, self_scaled))
    return touched


def _verify_legendary_stalker_sweep(db, touched):
    """FAIL-LOUD gate (parallels _verify_roaming_sweep, Hades-scoped): re-derive the touched set
    from the arz and prove ONLY eligible Immortal-Throne trash pools carry the stalker, each at the
    R-96 NORMALISED weight so every pool realises the SAME p_slot (1/1250 +/-4% for integer
    rounding) AND a per-slot limit=1 (_LS_SLOT_LIMIT) MAX-count cap (STRUCTURAL no-double:
    <=1 Hunt per pool per trigger), the monster resolves at band [40,68,100], and there is no leak
    into a non-Hades or boss/quest/hero pool (every stalker-bearing pool must be in `touched` - there
    is no dedicated stalker pool, so no whitelist)."""
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
        hidx = None
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
                hidx = i
        # R-96 NORMALISATION GATE. The old gate asserted `weight == 1` plus a 1/2400 ceiling;
        # Will's "roughly one sighting per act" ruling reds that by construction, so it is
        # replaced (not loosened) by the stronger invariant the new scheme actually guarantees:
        # every pool must realise the SAME p_slot, within integer-rounding tolerance. That
        # catches both a mistuned constant AND a pool that silently missed normalisation - the
        # flat-weight bug class this ruling exists to kill.
        others = wtotal - (hw or 0)
        if hw is None or hw < 1:
            problems.append(f"{n}: stalker weight {hw} missing/non-positive")
        elif others <= 0:
            problems.append(f"{n}: pool has no non-Hunt weight (wtotal {wtotal})")
        else:
            want = _ls_slot_weight(others)
            if hw != want:
                problems.append(f"{n}: stalker weight {hw} != normalised {want} "
                                f"(others total {others})")
            realised = hw / float(wtotal)
            if abs(realised - _LS_TARGET_P_SLOT) > _LS_TARGET_P_SLOT * _LS_P_SLOT_TOL:
                problems.append(f"{n}: stalker p_slot 1/{1.0/realised:.0f} outside "
                                f"1/{1.0/_LS_TARGET_P_SLOT:.0f} +/-{_LS_P_SLOT_TOL:.0%}")
        # STRUCTURAL NO-DOUBLE: the Hunt's name slot MUST carry limit=1 (a per-slot MAX-count
        # cap) so the engine spawns at most ONE per pool per trigger. Pool mains draw WITH
        # REPLACEMENT, so without this a pack pool (spawnMax>1) could surface 2+ Hunts in a
        # single spawn -- the exact "two-in-one-trigger" defect fixed for the Enslaver.
        hlimit = None
        if hidx is not None:
            lv = gv(n, 'limit%d' % hidx)
            try:
                hlimit = int(lv) if lv not in (None, '') else None
            except (TypeError, ValueError):
                hlimit = None
        if hlimit != _LS_SLOT_LIMIT:
            problems.append(f"{n}: stalker slot limit{hidx}={hlimit} != "
                            f"{_LS_SLOT_LIMIT} (STRUCTURAL no-double cap missing)")

    if not derived:
        problems.append("stalker sweep touched ZERO Hades pools (the Hunt would never appear)")

    if problems:
        for p in problems[:20]:
            print(f"  STALKER-SWEEP OFFENDER: {p}")
        raise SystemExit(
            f"Legendary-stalker roaming-sweep gate FAILED: {len(problems)} problem(s)")
    print(f"  [C] stalker-sweep gate OK: {len(derived)} eligible Immortal-Throne trash pools carry "
          f"the Hunt at the R-96 NORMALISED rate (every pool p_slot = 1/"
          f"{1.0/_LS_TARGET_P_SLOT:.0f} +/-{_LS_P_SLOT_TOL:.0%}, per-slot limit 1 = <=1 "
          f"Hunt/trigger); 0 non-IT / boss / quest / hero leaks; band [40,68,100].")
    # ROUND 4: the p_slot invariant above is necessary but NOT sufficient - it says every
    # pool is consistent, it says nothing about whether the resulting rate is the one Will
    # ruled. This re-derives the headline number and stamps the map it came from.
    _ls_census_gate()


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
def _bt_pools(db):
    """Derive the FULL roster of ProxyPools that reference Blood Toxeus (_BT_MONSTER =
    um_bloodtoxeus_99) in ANY name slot or champion slot, straight from the assembled db.
    Returns [(pool_name, has_toxeus_main, has_toxeus_champion), ...], sorted. Used by the
    champion-count-cap gate so it covers EVERY Blood-Toxeus surface (the ambush _BT_POOL and
    the deep-chest egg_blooddragon = the TWO live pools after Will retired the parchment
    demon_01_cluster_toxeus50, plus any future M-era pool) rather than just the ambush pool.
    Being roster-DERIVED, the gate self-adjusts when a pool is added or removed (e.g. the
    2026-07-14 parchment retirement shrank this roster 3 -> 2 with no gate code change)."""
    mn = _BT_MONSTER.replace('/', '\\').lower()
    roster = []
    for n in db.record_names():
        t = _gv1(db, n, 'templateName')
        if not (t and 'proxypool.tpl' in str(t).lower()):
            continue
        has_main = any((v := _gv1(db, n, f'name{i}')) and
                       str(v).replace('/', '\\').lower() == mn for i in range(1, 19))
        has_champ = any((v := _gv1(db, n, f'nameChampion{i}')) and
                        str(v).replace('/', '\\').lower() == mn for i in range(1, 19))
        if has_main or has_champ:
            roster.append((n, has_main, has_champ))
    return sorted(roster)


def _verify_toxeus_champion_cap(db):
    """FAIL-LOUD MP invariant (Part D), ROSTER-DERIVED over every Blood-Toxeus pool.

    ROUND-2 VET FIX (HIGH, 2026-07-14): the prior version proved "<= 1 Toxeus at any party
    size" for _BT_POOL (the ambush pool) ALONE and MISSED the two other live/authored pools
    that spawn um_bloodtoxeus_99: egg_blooddragon (the deep-chest Devourer, championChance=100,
    placed live via the native egg_blooddragon_pack) and demon_01_cluster_toxeus50 (the derived
    parchment pool, championChance=50). Both kept the base-game proxyPoolEquation
    (proxypoolequation_02), which FLOORS championMax=1 up to 2 at 4-6 players = TWO Blood Toxeus
    side by side (the exact 2026-07-13 dedup class the mandate centres on). THIS gate makes the
    invariant self-enforcing so a future pool that re-introduces the equation (or an over-count)
    fails the build LOUD.

    WILL FINAL DESIGN (2026-07-14): the parchment pool demon_01_cluster_toxeus50 is now RETIRED
    (never wired to the map; the monolith no longer authors it), so the roster is TWO pools -
    the ambush _BT_POOL (neutralized via _svc_lock_authored_pool_counts) and the deep-chest
    egg_blooddragon (neutralized in _apply_m15_toxeus_group_joins). Being roster-DERIVED, this
    gate follows the shrink automatically and still fails loud on any planted over-count.

    For EVERY pool that references Blood Toxeus in a name or champion slot, assert:
      (1) proxyPoolEquation is neutralized (empty) - else the literal counts do NOT hold and the
          Toxeus count silently scales with party size (the double-spawn root cause); AND
      (2) the LITERAL maximum number of Blood-Toxeus instances the pool can surface is <= 1
          (Toxeus-as-main worst case = spawnMax - championMax mains; Toxeus-as-champion worst
          case = championMax champions when championChance > 0; summed).
    Complements the spawn-eligibility gate's LOWER bound (>= 1 main for _BT_POOL) with this UPPER
    bound over the whole roster. (The roaming Hunt um_toxeus_hunt_99 is a DIFFERENT monster,
    capped to <= 1 per pool per trigger by its own per-slot limit=1 sweep gate.)"""
    Mn = _BT_MONSTER
    mn_lc = Mn.replace('/', '\\').lower()
    if not db.has_record(_BT_POOL):
        raise SystemExit(f"[toxeus_suite] PART D: _BT_POOL missing ({_BT_POOL})")

    def gi(rec, f, d=0):
        v = _gv1(db, rec, f)
        return d if v in (None, '') else v

    def as_int(v, d=0):
        try:
            return int(float(v))
        except (TypeError, ValueError):
            return d

    def as_float(v, d=0.0):
        try:
            return float(v)
        except (TypeError, ValueError):
            return d

    roster = _bt_pools(db)
    problems = []

    if not any(n.replace('/', '\\').lower() == _BT_POOL.replace('/', '\\').lower()
               for n, _, _ in roster):
        problems.append(f"_BT_POOL ({_BT_POOL.split(chr(92))[-1]}) not in the derived Blood-Toxeus "
                        f"roster - the ambush pool must reference him; roster derivation is broken")

    for n, has_main, has_champ in roster:
        base = n.split('\\')[-1]
        eq = gi(n, 'proxyPoolEquation', '')
        if eq:
            problems.append(f"{base}: carries proxyPoolEquation={str(eq).split(chr(92))[-1]} - it "
                            f"FLOORS the literal spawn/champion counts UP with party size "
                            f"(championMax 1 -> 2 at 4-6P = TWO Blood Toxeus). Neutralize it via "
                            f"_svc_neutralize_pool_equation.")
        sm = as_int(gi(n, 'spawnMax', 0))
        cc = as_float(gi(n, 'championChance', 0.0))
        cmax = as_int(gi(n, 'championMax', 0))
        mains = sm if cc <= 0 else max(sm - cmax, 0)
        bound = (mains if has_main else 0) + (cmax if (has_champ and cc > 0) else 0)
        if bound > 1:
            problems.append(f"{base}: can surface up to {bound} Blood Toxeus (spawnMax={sm}, "
                            f"championChance={cc}, championMax={cmax}, Toxeus-as-main={has_main}, "
                            f"Toxeus-as-champion={has_champ}); the MP invariant requires <= 1.")

    # keep the ambush pool's EXACT guarantee (all name slots Toxeus + exactly 1 guaranteed main).
    names = [_gv1(db, _BT_POOL, f'name{i}') for i in range(1, 7)]
    names = [str(x) for x in names if x and str(x).strip()]
    if not names or any(x.replace('/', '\\').lower() != mn_lc for x in names):
        problems.append(f"_BT_POOL name slots are not all Blood Toxeus: "
                        f"{[x.split(chr(92))[-1] for x in names]}")
    sm = as_int(gi(_BT_POOL, 'spawnMax', 0))
    cc = as_float(gi(_BT_POOL, 'championChance', 0.0))
    cmax = as_int(gi(_BT_POOL, 'championMax', 0))
    bt_mains = sm if cc <= 0 else (sm - cmax)
    if bt_mains != 1:
        problems.append(f"_BT_POOL guaranteed Toxeus mains = {bt_mains} != 1 "
                        f"(spawnMax={sm}, championChance={cc}, championMax={cmax}); a party could "
                        f"surface >1 Toxeus")

    if problems:
        for p in problems:
            print(f"  CHAMPION-CAP OFFENDER: {p}")
        raise SystemExit(f"Toxeus champion-count-cap invariant FAILED: {len(problems)} problem(s)")
    print(f"  [D] champion-count-cap invariant OK: {len(roster)} Blood-Toxeus pool(s) "
          f"(ambush + deep-chest; the parchment pool was retired 2026-07-14) each surface <= 1 "
          f"Toxeus at any party size 1-6, all proxyPoolEquation-neutralized; the per-player "
          f"scroll is the only new MP surface (live-test-gated).")


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


# =============================================================================
# PLANTED NEGATIVE TESTS for the R-96 roam-rate normalisation gate
#   py tools/patches/toxeus_suite.py --negtest
# A gate nobody has seen FAIL is not a gate. Each plant is a way the rate could
# silently regress; the gate must catch every one.
# =============================================================================
def _negtest():
    from collections import OrderedDict

    POOL_A = 'records\\xpack\\proxieshades\\pools\\nt_pool_a.dbr'   # poorest band (36,000)
    POOL_B = 'records\\xpack\\proxieshades\\pools\\nt_pool_b.dbr'   # richest band (660,000)
    MON = 'records\\xpack\\creatures\\monster\\nt_native.dbr'

    class _TF(object):
        def __init__(self, v):
            self.values = v

    class _Stub(object):
        def __init__(self):
            self.d = {}
            self._modified = set()

        def has_record(self, n):
            return n in self.d

        def record_names(self):
            return list(self.d)

        def get_fields(self, n):
            f = self.d.get(n)
            return None if f is None else OrderedDict((k, _TF(v)) for k, v in f.items())

        def get_field_value(self, n, f):
            return self.d.get(n, {}).get(f)

        def set_field(self, n, f, v, dt=None):
            self.d.setdefault(n, {})[f] = v if isinstance(v, list) else [v]

    def _pool(db, name, others_total):
        """One native member carrying `others_total`, plus the Hunt at his normalised weight."""
        db.d[name] = {
            'templateName': ['database\\templates\\proxypool.tpl'],
            'name1': [MON], 'weight1': [others_total],
            'name2': [_HUNT_MONSTER], 'weight2': [_ls_slot_weight(others_total)],
            'limit2': [_LS_SLOT_LIMIT],
        }

    def _base():
        db = _Stub()
        db.d[_HUNT_MONSTER] = {'Class': ['Monster'], 'charLevel': [40, 68, 100]}
        db.d[MON] = {'Class': ['Monster']}
        _pool(db, POOL_A, 36000)
        _pool(db, POOL_B, 660000)
        return db, [POOL_A, POOL_B]

    plants = [
        ('the pre-R-96 FLAT weight 1 comes back (1-in-27-playthroughs invisibility)',
         lambda db: db.d[POOL_A].__setitem__('weight2', [1])),
        ('ONE pool misses normalisation (the 18x per-area unfairness this ruling kills)',
         lambda db: db.d[POOL_B].__setitem__('weight2', [_ls_slot_weight(36000)])),
        ('the rate is silently doubled',
         lambda db: db.d[POOL_A].__setitem__('weight2', [_ls_slot_weight(36000) * 2])),
        ('a native member is re-scaled without re-deriving his weight (rate silently halved)',
         lambda db: db.d[POOL_A].__setitem__('weight1', [72000])),
        ('the structural <=1-per-trigger cap is dropped',
         lambda db: db.d[POOL_A].__setitem__('limit2', [None])),
        ('he leaks into a pool outside the Immortal-Throne namespace',
         lambda db: _pool(db, 'records\\creature\\pools\\nt_leak.dbr', 66000)),
        ('he leaks into a BOSS pool',
         lambda db: _pool(db, 'records\\xpack\\proxieshades\\pools\\boss_nt.dbr', 66000)),
        ('the sweep populates ZERO pools (he would never appear at all)',
         lambda db: [db.d.pop(POOL_A), db.d.pop(POOL_B)]),
    ]

    db, touched = _base()
    try:
        _verify_legendary_stalker_sweep(db, touched)
    except SystemExit as e:
        print("NEGTEST SETUP FAIL: the clean stub should PASS but raised: %s" % e)
        return 1
    bad = 0
    for label, plant in plants:
        db, touched = _base()
        plant(db)
        # the gate re-derives the touched set from the db, so a LEAK plant must not be
        # pre-declared in `touched` - that is exactly what makes it a leak.
        try:
            _verify_legendary_stalker_sweep(db, touched)
        except SystemExit:
            print("  negtest OK  (caught): %s" % label)
            continue
        print("  negtest FAIL (missed): %s" % label)
        bad += 1
    print("negtest: %d/%d plants caught" % (len(plants) - bad, len(plants)))
    return 1 if bad else 0


if __name__ == '__main__':
    import sys
    sys.exit(_negtest() if '--negtest' in sys.argv else 0)
