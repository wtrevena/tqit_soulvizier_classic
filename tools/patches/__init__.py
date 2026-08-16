"""patches-registry: an ordered, multi-file content-module manifest for the
SoulvizierClassic DB build (build37 bootstrap).

WHY THIS EXISTS
---------------
`tools/apply_svc_patches.py` is a ~16k-line monolith. To let content waves own
DISJOINT modules and run in parallel, new content is being moved OUT of the
monolith into small sibling modules under this package. Round 1 (this bootstrap)
adds the seam and the coherency machinery; REGISTRY ships EMPTY so the build is
byte-identical to the pre-registry build (the identity proof, README S5).

THE MODULE CONTRACT (what content waves code against - see README.md)
---------------------------------------------------------------------
Every entry in REGISTRY is the base-name of a file `tools/patches/<name>.py`
that defines exactly:

    MODULE_NAME = "<human label>"          # non-empty str, for logs/gates
    def apply(db, tags):                    # required callable
        # mutate `db` (arz_patcher.ArzDatabase) and `tags` (dict) IN PLACE.
        ...

`db` and `tags` are the SAME objects the monolith uses: `db` is the in-memory
ArzDatabase that apply_all_extended_patches() just finished authoring; `tags`
is the dict apply_all_extended_patches() returned (build_text_arc later turns
it into Text.arc). A module adds/edits records via the same idioms the monolith
uses (`from apply_svc_patches import _ensure_record, ...`; `db.set_field(...)`;
`db.clone_record(...)`) and adds Text tags via `tags['tagKey'] = 'value'`.

EXECUTION ORDER (the load-bearing coherency requirement)
--------------------------------------------------------
build_svc_database.py runs, in this exact order:
    1. apply_all_extended_patches(db, ..., _defer_gates=True)   # monolith content
    2. run_registry(db, tags)                                   # THESE modules' apply(), in order
    3. apply_svc_patches.run_registry_gates(db, tags, ...)      # the whole gate battery
    4. run_registry_verifies(db, tags)                          # THESE modules' verify(), in order
So the monolith's entire fail-loud gate battery now runs over the FINAL
assembled db (monolith + every module). Nothing a module does escapes the gates.

A module's OPTIONAL verify(db, tags) hook (step 4) runs AFTER the gate battery's
FINALIZATION (the Ground Smash de-filler, the wave29 placeholder-tag renames, the
soul-naming standard, the MP-equation fix). So a roster/diversity check a module
MUST run over the FINAL assembled db belongs in verify(), NEVER in apply(): an
apply()-time gate (step 2) runs mid-registry, before step 3 clears the ordering
artifacts (cyclops de-filler; satyrmagi/satyrspiritcaller placeholder-tag rename),
and would fail loud on those transient artifacts - the build37 skill_quality
blocker. Modules with no verify() are simply skipped in step 4.

Public API: REGISTRY, run_registry(db, tags), run_registry_verifies(db, tags),
run_registry_gates lives in apply_svc_patches, registry_order_hash(names),
selfcheck().
"""
import hashlib
import importlib

# ── THE MANIFEST ────────────────────────────────────────────────────────────
# Ordered list of module base-names -> files tools/patches/<name>.py.
#
# ORDER MATTERS: modules run top-to-bottom. If two modules write the SAME
# record, the LATER one wins (legal registry semantics) but run_registry emits
# a loud COLLISION warning naming both (never silent).
#
# KEEP THIS EMPTY on `main` until content waves land their modules. An empty
# REGISTRY makes the whole build byte-identical to the pre-registry build
# (README S5 identity proof). Content waves append their own single line here
# (e.g. 'four_generals', 'toxeus_suite') in their own branch.
#
# NOTE: _smoke_example is the template/reference module. It is intentionally
# NOT registered (it stays a copy-me template); see README S6.
# ORDERING NOTE (four_generals, build37 merge UNION resolution): four_generals
# enriches the three EXISTING general souls (soul\machae\{dysnomion,makaria,
# trophonios}) with a light amgoz downside. skill_quality may also touch those
# souls, so four_generals MUST run BEFORE skill_quality: the S4b collision then
# resolves later-wins in the intended direction (skill_quality's skill-grant edits
# win; the four_generals downside sits on a defensive stat neither fully touches).
# 'visuals' stays LAST (DB precondition invariant, writes nothing).
REGISTRY = [
    'hunting_occult_ui',    # build37 backlog #35/#76: O/H mastery-screen UI (shapes/bitmaps)
    'mastery_ui_audit',     # build38: cross-mastery skill-tree UI fix (graft icons, Earth
                            # Rupture de-dup + reflow, Dream bg); disjoint from hunting_occult_ui
                            # (which owns mastery 1-8 backgrounds + O/H button shapes)
    'mastery_bg_render',    # b60 wave (ships build42): mastery pane BLACK-BACKGROUND true render
                            # fix - upgrades the 9 pane records hunting_occult_ui/mastery_ui_audit
                            # repointed from the broken BitmapSingle+bitmapName to the vanilla
                            # BitmapUIAware+bitmapNames (+ controller sibling) the pane slot
                            # actually renders; + chrome repoint (undo buttons/cost/gold numbers
                            # off the dead SkillsPanel arc). MUST run after those two (it reads
                            # the texture they set).
    'oh_pane_art',          # b67 wave (ships build43): Occult (m5) tree-pane BACKGROUND ART fix -
                            # upgrades the texture CHOICE mastery_bg_render's BitmapUIAware
                            # structure fix left as vanilla Stealth (tan) to a bespoke DRX dark
                            # tablet (DRXtextures\masterybackdrops\standardskillbackground_
                            # joanna_ver_dark.tex); verifies Hunting (m6) needs no change. MUST
                            # run after mastery_bg_render (reads/proves its bitmapNames state).
    'four_generals',        # build37: Hades' Generals upgrade (3 general souls); keep ahead of skill_quality
    'skill_quality',        # build37 backlog #31: granted-skill quality pass
    'toxeus_suite',         # build37 backlog #32: Toxeus Encounter Suite
    'toxeus_champion_kits', # b73 (Will 2026-07-16): signature kits for the FOUGHT Toxeus champions -
                            # Devourer of Blood (um_bloodtoxeus_99) gets Tears of Blood (weak,10s) +
                            # Blood Frenzy; Enslaver of Souls (um_toxeus_enslaver_99) gets Soul-Rip +
                            # Chains of Servitude + Unholy Dominion. Edits the two monster records +
                            # 4 NEW skill records; NO pets/souls/pools/map. MUST run after toxeus_suite
                            # (expected S4b collision on um_bloodtoxeus_99 - Misc4 vs skill slots,
                            # later-wins, benign) and BEFORE boss_skill_fix (whose roster scan then
                            # sees these champions' final specials - all level>=1 by construction).
    'diadochi',             # build37: the Helepolis, Taker of Cities (Fields of the Diadochi uber)
    'polis_vault',          # build37: Polis Daemonai Warden's Vault-Cage
    'neferkha',             # build37: Neferkha, the Rimebound Pharaoh (Cold Tombs Tier-1)
    'lookout_uber',         # R-256 (Will 2026-08-15): "a uber boss (a new unique one) at the
                            # end of lookout cave in the area outside the back of the cave ...
                            # it is a dead end" -> Ushkaret, the Sky-Burial, on the Rhakotis05
                            # cliff shelf. Ordered HERE, beside the other content bosses and
                            # well ahead of chest_loot_breadth / armor_loot_breadth /
                            # orb_loot_breadth / orb_armor_rows / loot_volume_trim /
                            # uber_hoard_generosity, because his hoard family is authored in
                            # THIS module and every one of those later modules derives its
                            # scope from the svc_<fam>hoard_* name shape - authored late, the
                            # chest would ship un-widened and un-trimmed (the diadochi note).
    'bossarena',            # b43: Aithon, the Ember-Crowned (Olympian Arena boss finish);
                            # disjoint - upgrades the bossarena chain in place + adds 1 champion + 1 soul
    'hunting_occult_improvements',  # build37: Will-approved H/O skill edits; runs late (was the
                                    # finalization-phase interim call) so it wins any collision
    'damage_display',       # build38: restore AE floating combat-text FontStyles on xpack
                            # gameengine (SV's pre-AE record lacks them; touches only gameengine)
    'death_xp_penalty',     # b93 (Will R-80 2026-07-27) + R-254 (Will 2026-08-14, "another
                            # 50% from what it currently is at"): on-death XP loss cut to
                            # exactly 5% of vanilla - deathPenaltyEquation divisor 9 -> 180
                            # and deathPenaltyMax 500000 -> 25000 on
                            # records\xpack\game\gameengine.dbr (the ONE GameEngine record
                            # Game.dll loads). The SUPERSEDED R-80 pair (90 / 50000, shipped
                            # through build92) stays a RECOGNISED pre-state, so re-running
                            # over any arz already on disk is a legal no-op rather than a
                            # loud failure. deathPenaltyMin stays 0. MUST sit adjacent to
                            # damage_display: they are the only two modules that write that
                            # record, so the S4b collision WARN naming exactly this pair is
                            # EXPECTED and benign - their field sets are disjoint
                            # (Damage*/Healing*/PlayerImpairment styles vs deathPenalty*), and
                            # neither reads the other's fields, so order between them is
                            # immaterial. A collision WARN naming any THIRD module on this
                            # record is a real finding: investigate before shipping.
                            # Negative test: py tools/patches/death_xp_penalty.py --negtest
                            # RULING RENUMBERED AT INTEGRATION (R-251 -> R-254): this lane
                            # also authored itself R-251 off 0ea001a/build92, the same
                            # collision fix/toxeus-boss-equipment-and-soul hit. The SHIPPED
                            # number wins - R-251 is the uber/boss chest generosity (build95)
                            # and R-252/R-253 shipped as build96/build97 - so this ruling and
                            # its debts are R-254 / BL-R254-DEBT-1..2 everywhere. Same
                            # treatment as R-231 -> R-244 (build88), R-250 -> R-251 (build95)
                            # and R-251 -> R-252 (build96). No content changed.
    'tombstone_xp_recovery',  # R-109 (Will 2026-07-30): "lets make the tombstone xp recovery
                            # match the xp lost upon dying". ONE field on the SAME record
                            # death_xp_penalty owns: RedemptionMultiplier 0.5 -> 1.0 on
                            # records\xpack\game\gameengine.dbr. Game.dll computes
                            # recovered = trunc((float)<XP ACTUALLY LOST> * RedemptionMultiplier)
                            # (GetPlayerExperienceRedemptionAmount VA 0x10194f60 reads the amount
                            # RegisterExperienceLoss VA 0x10194540 stored at GraveInfo+0x0C), so
                            # 1.0 makes the marker return exactly what the penalty took, DERIVED
                            # from the penalty rather than hardcoded - retune deathPenalty* and
                            # the marker follows with no edit here. R-254 (2026-08-14) is the
                            # FIRST live exercise of that property: the penalty halved and this
                            # module was not edited at all (negtest plants 7+8 hold the retune
                            # and the exact R-254 halving against an unedited recovery side).
                            # MUST run immediately AFTER death_xp_penalty: apply() refuses to run
                            # unless the penalty is already in its ruled state. Third writer
                            # of gameengine.dbr alongside damage_display (FontStyles) and
                            # death_xp_penalty (deathPenalty*); all three field sets are disjoint,
                            # so the S4b collision WARN naming this TRIO is EXPECTED and benign -
                            # a FOURTH module on this record is a real finding.
                            # Negative test: py tools/patches/tombstone_xp_recovery.py --negtest
                            # Measured before/after table: ... --table <arz>
    'thrown_restore',       # b64: restore base+IT thrown-wielders (maenad/duneraider/tigerman/
                            # machae) our own overlay disarmed, back into their EXISTING pools
                            # in place (no clone, no new pool); disjoint namespace (monster
                            # records only, none touched by any other module) - order-independent.
    'thrown_anim_rig',      # R-100 #15 P0 (Will: the restored throwers "spawn and they cant move
                            # or attack or anything they are broken"). thrown_restore fixed the
                            # EQUIPMENT; the freeze is the ANIMATION side. SV 0.98i replaces the 4
                            # animation tables those families use with pre-thrown-weapon versions
                            # binding ZERO rangedOneHand/dualRanged clips, so an armed wielder
                            # enters a stance with no run/walk/attack anim. This module CLONES each
                            # table (166/66/61/27 NON-TARGET carriers -> SHARED-RECORD LAW forbids
                            # editing in place) into records\creature\monster\svc\thrown_anm\*,
                            # restores the base TQAE stance clips verbatim on the clone, and
                            # repoints charAnimationTableName on the 10 roster records - which it
                            # IMPORTS from thrown_restore.ROSTER so the two can never drift.
                            # MUST run immediately after thrown_restore: it is the other half of
                            # the same restore, and its DB-wide gate ("no monster equips a thrown
                            # weapon on a table that leaves that stance unbound") can only be true
                            # once the equipment half has run. The S4b collision WARN naming
                            # EXACTLY this pair on the 10 monster records is EXPECTED and benign -
                            # their field sets are disjoint (equip/loot/characterLife vs
                            # charAnimationTableName) and neither reads the other's fields. A WARN
                            # naming any THIRD module on those records is a real finding.
    'dagon_anim_rig',       # DAGON FROZEN (Will 2026-08-11: "Dagon, lord of the poisoned deep is
                            # frozen like the maened thrown object guys were"). Same class as
                            # R-100 #15 - the freeze is on the ANIMATION surface and survives a
                            # correct kit fix - but a different mechanism: the WRONG RIG with no
                            # fallback. All 13 clips on records\test\boss_dagon_66.dbr are
                            # Creatures\Monster\HYDRA\ANM\* clips inherited wholesale from
                            # boss_hydra_66 (977 of their 1,043 shared fields are identical), and
                            # they drive a 101-bone hydra skeleton on an IchthianMage01 mesh with
                            # 30 bones and none of that hierarchy (8 of the clip's bones exist on
                            # the mesh; his own rig's clips land 22 of 30). 54 base-game records
                            # carry that mesh and NOT ONE pairs it with a Hydra clip. The only
                            # surface that could have supplied in-rig clips,
                            # charAnimationTableName = ...\d2custom\anm\anm_dagon.dbr, resolves in
                            # NEITHER the mod arz NOR the base game (0 d2custom records exist
                            # anywhere - the same never-shipped SV namespace that made his SKILLS
                            # dead in b52). NOTE: the missing unarmedWalkAnim is NOT the cause -
                            # boss_hydra_66 names no table at all, binds no walk clip in any
                            # stance, and animates fine in the shipping game. Repoints him at
                            # anm_ichthian (the table 43 of his 44 same-mesh siblings use), writes
                            # the full in-rig unarmed stance on the record too per adfda67's
                            # BOTH-surfaces law, and points his four name-keyed special refs at the
                            # skills his kit actually casts (TidalStrike, his WILL_DECISIONS
                            # signature move, previously had no animation of its own). NO CLONE and
                            # NO SHARED-RECORD EDIT: unlike thrown_anim_rig, which had to MODIFY
                            # its tables, this only POINTS AT one. Runs immediately after
                            # thrown_anim_rig - same failure class, and its DB-wide gate
                            # generalizes that module's thrown-only invariant to EVERY
                            # spawn-referenced monster, cross-checking the BASE arz instead of
                            # assuming "absent from the overlay -> the base game has it" (the
                            # assumption that hid this record from BOTH the anim gate and, in b52,
                            # validate_tags). That DB-wide clause closes the DANGLING-TABLE half of
                            # the class only; the cross-rig half is gated PER RECORD here and
                            # registered as BL-DAGON-CROSSRIG-DEBT-1, with the three measurements
                            # showing why no cheap DB-wide form of it survives contact with
                            # build83. ANIMATION FIELDS ONLY on one record. S4b COLLISION,
                            # CORRECTED AT THE build87 MERGE - the earlier note here PREDICTED an
                            # expected WARN naming this module and `red_uber_orbs` on
                            # boss_dagon_66. It was read off rule (b)'s scope prose, never
                            # measured in a build (this lane shipped static gates only), and a
                            # real build says otherwise: `red_uber_orbs` writes ONLY the red
                            # ubers that are MISSING an orb ("scope proof: exactly 8 record(s)
                            # changed treasureProxyName"), and Dagon is not one of them - he
                            # already carries `genericbossorb_04`, byte-identical before and
                            # after this module. So the measured S4b list names
                            # `dagon_anim_rig` on NO record at all, and `boss_dagon_66` appears
                            # in no collision row. The disjointness that made the predicted WARN
                            # benign still holds and is what keeps it safe if a later module
                            # ever does write the record: this module moves
                            # charAnimationTableName + 17 unarmed*Anim* slots and NOTHING else,
                            # so it cannot disturb `treasureProxyName` (the b86 R-242 orb wiring)
                            # or `chanceToEquipFinger2` (the b87 R-243 soul rate 20.0), both
                            # proven byte-unchanged on that record at the merge. ANY collision
                            # row naming boss_dagon_66 is now a real finding, not a known one.
    'boss_skill_fix',       # build39: repair fought-boss skill-USAGE wiring (level-0 specials/
                            # auras/passives + Helepolis displaced turret). Runs LAST among content
                            # modules so it sees the FINAL boss records from every creating module
                            # (four_generals/diadochi/polis_vault/neferkha/toxeus_suite + monolith).
    'legion_soul_stages',   # b56: one soul per death-transform encounter (Legion + any same-soul
                            # actorToSpawnOnDeath chain drops its soul at the FINAL stage only).
                            # Runs after every soul-wiring + boss-creating module so it sees the
                            # FINAL chains; before the drop-rate forcer (run_registry_gates).
    'double_soul_rulings',  # Will's double-soul rulings (delegated to the b56 standing
                            # recommendation): Possessed Boar + Lillued fixed terminal-only
                            # (typo-twin dup / empty-husk soul retired); Charon 39/41/43 +
                            # Hades 54 explicitly UNTOUCHED. verify() also cross-checks that
                            # legion_soul_stages' distinct-soul roster shrinks 6 -> 4.
    'enslaver_pet_fx',      # b55: black-rig the SOUL-SUMMONED Enslaver + the marauders he raises
                            # (strip Lyia-clone green residue: envenom/heartofoak/regrowth/natureswrath;
                            # inherit each pet's source-monster black shroud). PET FX fields only;
                            # runs after every pet-building module so it edits the FINAL pet records.
    'souls_quality',        # backlog #31 round1: fix the 3 DEFICIENT svc_uber souls (Legendary
                            # weaker than Epic - tier-level inversion) + the 54-family svc_uber
                            # e/l per-tier icon law. Disjoint from every module above (touches only
                            # create_uber_souls-generated svc_uber rings; module-authored souls
                            # already obey both invariants). verify() gates the class fail-loud.
    'aura_radius',          # b57 BL-AURA-RADIUS: widen friendly aura RADIUS FIELDS ONLY (party->36u,
                            # pet->18u) so aura bonuses reach pets/MP allies. Runs late so a radius
                            # edit wins any collision on the aura payloads (none observed). Disjoint
                            # from every other module (touches only skillTargetRadius on buff payloads).
    'svaera_sets',          # SVAERA-ADOPT: re-link the 5 SVAERA Greek/Egyptian item sets onto
                            # the 13 already-shipped standalone-unique members (itemSetName only;
                            # no item/loot/map change). Disjoint from every module above.
    'turtleshell_relics',   # NEW-RELIC-DIONYSUS-TRICKSTER + NEW-RELIC-DUNE-FIEND: The Reveler's
                            # Ruse (Satyr Archer family, turtle-shell pattern) + a regression
                            # guard confirming Dune Fiend's pre-existing Fiend Carapace relic
                            # (no duplicate authored). Disjoint from every module above.
    'uber_orphan_weapons',  # B66 UBER FORMULA EXPANSION: 14 orphaned weapons (docs/reports/
                            # orphaned_weapons_curation.md) buffed to the supra uber-forge tier,
                            # cloning the proven svc_thrown_* template; 7 reuse an orphaned
                            # zrecipes\ formula shell (repointed in place), 7 author fresh
                            # zrecipes\svc_<class>_<name>_formula.dbr. Disjoint from every module
                            # above (new records only; touches supra.dbr/supra_special.dbr
                            # lootName slots, additive).
    'formula_names',        # b80 (Will 2026-07-16, R-41): formula-name audit round 1 - Galefury's
                            # Mythic Formula was mislabeled "Crystalline Mask" (a shared donor
                            # tag, pre-b66 SV/DRX authoring debt); repoints ar_hunter_helm_
                            # formula.dbr's description onto its own already-correct, previously-
                            # orphaned SV098i tag. Disjoint from uber_orphan_weapons (touches a
                            # single pre-existing recipes\ record, not any b66 zrecipes\ formula);
                            # placed after it since both live in the supra formula-name domain.
    'mastery_sv_alignment', # b70 (build45): FINAL writer on Occult(m5)/Hunting(m6)/emblem
                            # mastery-UI fields - Occult/Hunting SV-alignment (shape flips,
                            # emblem x9 BitmapSingle->BitmapUIAware, Darklings/Dark Aperture
                            # column move + connectors, Dark Invigoration wire). MUST run after
                            # hunting_occult_ui + mastery_ui_audit + mastery_bg_render +
                            # oh_pane_art + hunting_occult_improvements so it is the ratified
                            # last writer on isCircular/positions/connOn-Off + masterybitmap.
    'summon_caps',          # b76 CHUMBI-FREEZE P0: restore the missing spawnObjectsTimeToLive on
                            # the unbounded boss-summon skills of the sepulcher/tomb-guardian chain
                            # (aktaios_summontombguardians + alastor_summonskeleton{warrior,archer}
                            # + the recursive summonpet_undeadmelee01) that um_voranthys_99 fires.
                            # ADDITIVE (one field; petLimit/spawnObjects untouched). MUST run after
                            # boss_skill_fix (which ENABLED those previously level-0 summon specials)
                            # so it caps the final, active skill records. verify() fails loud if any
                            # target survives uncapped.
    'mastery_unlock_alignment',  # b77 (build45): UNLOCK-ALIGNMENT fix wave - make every
                            # mastery button's real unlock gate (skillTier threshold) match
                            # the row it is drawn on (b74 audit). Touches ONLY m1/m2/m3/m4/m7
                            # (Spirit DW GT-rows, Warfare col3 restack, Earth col4 re-tier,
                            # Defense/Storm gate leans, Storm broken-button retire); disjoint
                            # from mastery_sv_alignment's m5/m6/emblem scope. Registered LAST
                            # among mastery-UI writers so it is the ratified final writer on
                            # skillTier/skillMasteryLevelRequired/bitmapPosition/connOn-Off for
                            # its masteries. Golden (m5/m6) untouched -> A7 stays green.
    'black_poison',         # b83 (Will 2026-07-16, R-1): THE DEVOURER'S BLACK POISON - a new
                            # envenom-lineage svc_black_poison (dark shadow-enchant tint +
                            # dark-smoke weapon pak, poison+vitality) replaces the crimson
                            # bloodtoxeus_envenomweapon on the Devourer fought-monster + his 3
                            # soul pets. MUST run after toxeus_champion_kits (b73 Devourer kit)
                            # and BEFORE toxeus_endofallthings (whose _BLACK_POISON const names
                            # svc_black_poison for the EoAT pet buff). Green-marker safe (name has
                            # no 'envenom'); his crimson identity (skin/bloodboil/aura) untouched.
    'toxeus_endofallthings',# b72 (Will 2026-07-16): TOXEUS, END OF ALL THINGS - the supra
                            # soul crafted from the 3 LEGENDARY Toxeus souls (green-Greece +
                            # Enslaver + Devourer) summoning one apotheosis pet. Clones the
                            # PROVEN Devourer pets; authors summon + soul ring + uber formula +
                            # kit skills + disciple thralls. Runs after enslaver_pet_fx (extends
                            # its b71 chain-gate roster) + uber_orphan_weapons (equips supra
                            # pieces); before visuals. New records only (+ soul-naming exemption).
    'sargoth_soul_summon',  # b95 (Will 2026-07-27, R-51): "backlog item sargath manbane soul
                            # should let you summon him". Same ruling class as R-43 (High Priest),
                            # same SECOND-BUILDER pattern: builds sargoth_1/2/3 + summon_sargoth
                            # from hero_tarthon_na'arak_37 (DISPLAY name "Sargoth Manbane",
                            # tagMonsterName1138) via _build_boss_summon, and wires itemSkillName
                            # onto all 3 SV-original sargoth_soul_{n,e,l} tiers (levels 1/2/3,
                            # manual-cast). Registered LATE among content modules so the builder
                            # mirrors the FINAL source-monster record. New records + 3 soul-field
                            # writes only; disjoint from every other module. Its full
                            # item->skill->icon->spawnObjects->pet->portrait chain is asserted by
                            # the EXISTING enslaver_pet_fx._CHAIN gate (which carries R-43 too).
    # --- content-wave integration round 2 (2026-07-29): feat/endless-hunt (b98) was rebased
    # onto post-b99 main. Its two modules claimed the slot immediately before
    # 'toxeus_souls_100' from a base that predates b95's 'sargoth_soul_summon'. Both
    # constraint sets are satisfied by keeping sargoth first (it only touches the dragonian
    # soul family - disjoint from every Toxeus record) and running the b98 pair immediately
    # after it, still ahead of 'toxeus_souls_100'.
    'toxeus_hunt_encounter',# b98 (Will 2026-07-28, R-90/R-92/R-93/R-94). RENAMED from
                            # 'toxeus_legendary_stalker' under the RETIREMENT PROTOCOL: the old
                            # name described a Legendary-only gate that Will's ruling removes, and
                            # it was only ever true of the FIXED proxy - the ROAMING sweep was
                            # never difficulty-gated at all (the RECORDS q_toxeus_hunt_lone
                            # proxy/pool keep their shipped names, and are not deleted).
                            # Ungates the fixed Hades Palace encounter to N/E/L, adds the Rite of
                            # the Undivided to Misc4 @100 (Enslaver mirror), gives him the
                            # Runbreaker signature spear + a playable spear animation block, and
                            # replaces the 3 cast slots he shared with the Enslaver with his own
                            # pursuit kit.
                            # ORDERING: after toxeus_suite (which authors um_toxeus_hunt_99) AND
                            # after toxeus_endofallthings, which is the author of BOTH
                            # svc_rite_guaranteed and the EoAT formula this module's R-92 wiring
                            # and its recipe-gate assertion read. Also after boss_skill_fix and
                            # toxeus_champion_kits, so it is the ratified last writer of the
                            # Hunt's cast slots - EXCEPT the R-247 surfaces: r247_boss_forms
                            # (registered later) is the ruling-5a/6c amendment layer for his
                            # body/rig/soul-grant, and THIS module's verify() asserts the FINAL
                            # post-R-247 state (soul pin = summon_toxeus_hunt per R-247.6c; the
                            # R-94 quarrysmark pin + b98 Maenad-clip provenance are RETIRED -
                            # see the reconciliation block in its docstring). Negative test:
                            # py tools/patches/toxeus_hunt_encounter.py --negtest
    'enslaver_shroud',      # b98 (Will 2026-07-28, R-95): the Enslaver's PERSISTENT black shroud.
                            # He ALREADY carries the marauders' shadowcloak pak on
                            # charFxPakRunningNames - a channel that only renders while RUNNING,
                            # and he is a caster who stands and casts, so it almost never plays.
                            # Adds the persistent channel the shipped way (a Skill_BuffSelfToggled
                            # with charFxPakSelfNames, the same construction R-7 used for the
                            # Devourer's black poison) in a FREE skill slot - NO skill dropped
                            # (R-26 spirit; ground truth: he uses skillName1..18 and the template
                            # reaches 23, so slot 19 was free all along). Registered after
                            # toxeus_champion_kits / enslaver_pet_fx / toxeus_endofallthings, the
                            # other writers in his kit + FX domain, so it is the ratified last
                            # writer of the slot it claims. Uses ONLY the in-game-CONFIRMED
                            # shadowcloak smoke, never 343_dark_smoke (R-10: green-rendering).
                            # ⚠️ b102 (R-102 SECOND AMENDMENT, Will: "that is still not
                            # implemented"): b98 wired the shroud to the MONSTER ONLY and all three
                            # `pets\toxeus_enslaver_*` tiers were skipped - and the pet is what Will
                            # summons, so from where he stands it was never delivered. The module
                            # now wires a ROSTER = {monster} + {every tier READ from
                            # summon_toxeus_enslaver.spawnObjects}, each in its own lowest free slot
                            # (pets use 1-12 + 15; nothing dropped), and its gate additionally
                            # asserts the pets' controller really fires self-buffs - a toggle the
                            # AI never toggles is an empty slot. Deriving the tiers is what makes
                            # the miss unrepeatable.
                            # ⚠️ b104 (R-250, Will 2026-08-11: "toxeus the murderer, devourer of
                            # souls we need to add the black shadow shroud around him, the same one
                            # that his demon summon guys have" - the THIRD filing). The name fuses
                            # two variants; the demon clause resolves it, because ONLY the
                            # Enslaver's marauders carry a black shadow shroud (the Devourer's
                            # Blood Demons carry FX_blood_CHEST/HANDS/HEAD). And the demons' shroud
                            # was never in a FIELD - it is `CreateEntity{attach="SpecialHit01";
                            # entity="...ShadowStalker_Smoke.dbr"}` compiled INTO ShadowStalker.msh,
                            # which is why it renders every frame and why two waves of field edits
                            # could not match it. champion_mesh (b102) then moved him onto the
                            # FX-free SkeletonGrayBlack01New.msh to kill the green, removing his
                            # last always-on emitter. So b104: (a) svc_enslaver_shroud_fx is a
                            # FIELD-FOR-FIELD MIRROR of the demons' own base-game EffectEntity
                            # (templateName/ActorName/Class/effectFile ->
                            # Effects\MonsterFX\ShadowStalker_Smoke01.pfx); the donor is a shell
                            # and is PRUNED to that set, weapon boneList and all; (b) the pak
                            # attaches it at the demons' OWN SpecialHit01, which his rig DOES
                            # declare, in a byte-identical block (origin (0,0,0), identity axes) -
                            # round 1 refused it on a false measurement, see R-250's ROUND 2
                            # correction; the missing-attach example is Smoke02, which the demons
                            # have and he does not; (c) every roster surface moves to an SVC-OWNED
                            # CLONE of its controller with BuffSelfBehavior=WheneverPossible, so
                            # the shroud is ON out of combat (the shared originals drive the
                            # Devourer and 148 other pets and are NEVER edited). Provably
                            # visual-only: the gate asserts the shroud is the ONLY Skill_BuffSelf*
                            # in either kit. Gates: provenance + attach point DERIVED from the
                            # marauders' mesh binary, EffectEntity mirror derived from the base
                            # .arz, rig-attach checked against each wearer's own mesh across BOTH
                            # name tables (bone + AttachPoint, casefolded - see mesh_assets), A9
                            # render resolution on the .pfx (base-game Effects.arc), donor-residue
                            # check, shared-record leak check, CRASH LAW.
                            # R-255 (b99, Will 2026-08-15, the FOURTH filing: "summoned pets
                            # ... still do not have the black smoke"): b93 put all of the
                            # above in skillName19 (boss) / skillName18 (pet tiers) - slots
                            # MonsterSkillManager.tpl DOES NOT DECLARE. It declares
                            # skillName1..17 and nothing more, and no Monster or Pet in the
                            # 74,013 base-game records ever uses a higher one; "the template
                            # reaches 23" was this mod's own overflow read back as headroom.
                            # So the shroud now rides the two always-on channels that
                            # template really declares - initialSkillName (cast at spawn, ON
                            # from frame one, owes the AI nothing) + buffSelfSkillName (the
                            # controller clones re-apply it) - and this lane's dead slots are
                            # retired (a NEIGHBOUR's skill parked up there is reported only,
                            # RETIREMENT PROTOCOL: see BL-R255-DEBT-1, six such records).
                            # R-255 also WIDENS the parity gate from the boss+pet-tiers to the
                            # whole household: the roster is a bounded WALK (boss -> escorts
                            # -> pet tiers -> pet-of-pet marauders) plus any record wearing a
                            # family name tag, and every member must satisfy one of two
                            # DERIVED routes - MESH (its rig embeds the demons' own
                            # ShadowStalker_Smoke.dbr; that is how the marauders have always
                            # smoked) or FIELD (the shroud in both always-on channels). A
                            # family member with neither FAILS the build.
                            # ⚠️⚠️ R-257 (b101, Will 2026-08-16, the FIFTH filing, WITH A
                            # SCREENSHOT: the Enslaver summoned at Hathor Basin on the
                            # post-b99/b100 DEV arz, standing out of combat, ZERO smoke).
                            # R-255's channels were declared, byte-verified and gate-verified
                            # and the engine still rendered nothing. THE RULING: a channel
                            # being DECLARED in the template does not mean the pet controller
                            # EXECUTES it, or that a CharFxPak ATTACHES on this rig - a
                            # record-level proof is not a rendering proof. Measured: across
                            # all 341 vanilla Pets the exact b99 shape (Pet + always-on
                            # channel + Skill_BuffSelfToggled + body-attach CharFxPak) occurs
                            # ZERO times (R-255's "90 Pets ... 153 on a Skill_BuffSelfToggled"
                            # conflated two pools - all 153 are MONSTERS); the running-FX
                            # field class is declared in ZERO of 566 templates; Pet.tpl has no
                            # ambient-effect field at all; and ShadowStalker_Smoke.dbr is a
                            # deathEffect in all 13 of its base-game references. Its ONLY
                            # persistent rendering anywhere is the CreateEntity block compiled
                            # into a .msh - which is also how EVERY vanilla pet with a
                            # persistent aura gets one (Ancestral Warriors, the Outsider,
                            # Storm Wisps, Spirit Ward, Battle Standard), and how the
                            # marauders Will confirmed by eye have always carried it.
                            # SO THE SHROUD LEAVES THE RECORD LAYER. tools/build_shroud_rig.py
                            # authors Creatures\Monster\Skeleton\svc_enslaver_shroudrig01.msh
                            # = base SkeletonGrayBlack01New.msh + the 115 bytes read VERBATIM
                            # off the end of ShadowStalker.msh + that one chunk-length u32
                            # bumped (a .msh is a self-describing chunk chain with no global
                            # offset table; A1..A9 re-derive every byte, incl. that the
                            # rig-name table is IDENTICAL so animations are untouched). It
                            # ships in the mod's own Resources\Creatures.arc under a NET-NEW
                            # name. THIS MODULE now only RETIRES: it stops authoring
                            # svc_enslaver_shroud/_charfxpak/_fx and the svc_alwayson_
                            # controller clones (cold build -> they never exist), unwires them
                            # when re-run over a built arz, and gates that the whole household
                            # smokes by the MESH route DERIVED from each wearer's .msh binary,
                            # with NO belief channel left anywhere. Removal is not tidiness:
                            # on a member that already smokes from its rig the FIELD route
                            # would DOUBLE the shroud, which b99's own apply() already refused
                            # for the marauders.
                            # 🚨 NEW DEPLOY COUPLING (BL-R257-DEBT-1, P0): the family's `mesh`
                            # now names a MOD-SHIPPED asset. work\<mod>\Resources\Creatures.arc
                            # must be rebuilt + deployed in the SAME ship as the arz or they
                            # resolve NO MESH (an invisible boss). verify() arm M2 reds on
                            # exactly that. Coupling list: Levels+Quests, arz+Text, AND
                            # arz+Creatures.arc.
                            # ORDERING NOTE: this module no longer writes `mesh`; champion_mesh
                            # (registered later, R-102's single-writer law) does, and IMPORTS
                            # SHROUD_RIG from here so asset and wearer cannot drift.
                            # Negative test: py tools/patches/enslaver_shroud.py --negtest
                            # (29 plants, incl. the required "strip" case -> RED and the
                            # "belief-channel-only re-plant" case: a pet back on the FX-free
                            # rig carrying the b99 field route, i.e. exactly what shipped as
                            # build99 -> RED); --selftest re-measures the exemplar, both rigs,
                            # the authored asset and the R-255 slot ceiling against the real
                            # archives (round 1's stub asserted a FALSE premise and its rig
                            # plant certified the error instead of catching it; b93's slot
                            # ceiling was a comment nobody ever re-derived)
    'toxeus_souls_100',     # b90 (Will 2026-07-27, R-48) + b98 (R-91): "increase the drop rate for
                            # the souls
                            # of toxeus the murderer, enslaver of souls and toxeus the murderer,
                            # devourer of blood to 100%". Sets chanceToEquipFinger2=100 on EXACTLY
                            # um_toxeus_enslaver_99 (was 66) + um_bloodtoxeus_99 (was 25) +, per
                            # R-91, um_toxeus_hunt_99 (was 25 - the SOLE reason the Endless Hunt's
                            # soul appeared not to drop; this closes BL-b90-DEBT-4); every
                            # other soul rate untouched (apply() proves it roster-wide). Registered
                            # LAST among content modules so it is the ratified final registry writer
                            # of that field on the two champions - after toxeus_suite /
                            # toxeus_champion_kits / black_poison / toxeus_endofallthings and the
                            # legion_soul_stages + double_soul_rulings rate writers. Mode-independent
                            # (holds under SVC_RELEASE_DROPS=1, which is what ships); verify() fails
                            # loud on the FINAL merged db if either drops below 100.
    # --- b94 round 3 merge reconciliation: the b94 pair (leinth_wave ->
    # uber_apex_orb, that order is load-bearing) and the debt-wave block below
    # both claimed the slot before the no-op 'visuals'. The b94 pair runs FIRST so
    # uber_apex_orb still sees leinth_wave's final Leinth records, and the debt-wave
    # block keeps its own deliberate order with fx_dangling_cleanup LAST - which now
    # also sweeps b94's new guard/skill records on the final assembled db.
    'leinth_wave',          # b94 PART B (R-73): Leinth the Blood Witch buff + 3 cult abilities
                            # (Crimson Tithe / Choir of the Bloodborn / Sanguine Mire, every donor
                            # from her OWN records\drxcreatures\bloodwitch family) + the b76
                            # summon-density cut on leinth_summon_uglies. Touches ONLY the 3
                            # q_leinth_* records, her 2 own skill records and 3 NEW skill records -
                            # disjoint from every module above (no other module names a bloodwitch
                            # record). Placed here so it is the ratified final writer on her stats;
                            # verify() re-asserts every target on the FINAL merged db, including
                            # that her loot wiring never moved.
    'uber_apex_orb',        # b94 PART A (R-72, Will 2026-07-27): ONE apex drop calibre shared by
                            # ALL THREE blood-cave bosses. Authors a new un-named generic apex tier
                            # (genericbossorb_05 + 3 pools + 3 chests + 3 loot tables cloned from the
                            # orb04 chain, carrying Leinth's four generosity knobs on the champions'
                            # Act-4 tables) and repoints treasureProxyName on EXACTLY
                            # um_toxeus_enslaver_99 + um_bloodtoxeus_99; then upgrades Leinth's THREE
                            # sole-owned chests IN PLACE onto the SAME apex tables + level equation
                            # (2 fields each), so she is re-tiered rather than left behind. Her
                            # monster records, proxy and pools are untouched, so R-73's "her bespoke
                            # chest survives" assertion in leinth_wave stays green - which is why
                            # this MUST run AFTER 'leinth_wave'. genericbossorb_04 and its other 19
                            # consumers stay byte-unchanged (apply() proves it). MUST also run after
                            # toxeus_souls_100: EXPECTED S4b record collision on the two champions
                            # (souls_100 writes chanceToEquipFinger2, this writes treasureProxyName -
                            # DIFFERENT fields, later-wins is a no-op on both), and apply()
                            # additionally proves the R-48 soul wiring did not move. Before 'visuals'.
    # --- debt-wave integration 2026-07-28: fix/debt-mixed (coldworm_buffs,
    # uber_quest_markers) and fix/debt-db (emberteeth_summon, fx_dangling_cleanup)
    # each landed a block here claiming the slot immediately before the no-op
    # 'visuals'. The order below is a DELIBERATE reconciliation, not a union:
    #   emberteeth_summon   - after every soul-wiring + drop-rate module (its own
    #                         constraint) and BEFORE uber_quest_markers, so the
    #                         marker roster is derived from the same final soul
    #                         records that the post-finalization verify() sees.
    #   coldworm_buffs      - still after boss_skill_fix, still the last writer of
    #                         Cold Worm's kit (nothing below touches it).
    #   uber_quest_markers  - still after coldworm_buffs and after toxeus_souls_100,
    #                         still the last writer of DisplayAsQuestItem.
    #   fx_dangling_cleanup - LAST content module (its own constraint), so it sweeps
    #                         emberteeth_summon's new skill records AND coldworm_buffs'
    #                         repointed slots on the final assembled db.
    #
    # --- content-wave integration 2026-07-29 (b99): fix/soul-identity landed
    # 'soul_identity' claiming that same pre-'visuals' slot, from a base that
    # predates the four modules above. Its position here is DERIVED from the two
    # colliding constraints, not from either branch's line number:
    #   * soul_identity says "after EVERY soul-wiring + drop-rate module, so
    #     apply() sees the FINAL carrier set" -> it must follow emberteeth_summon
    #     (the last soul-wiring module), sargoth_soul_summon (b95, likewise) and
    #     toxeus_souls_100 (the last chanceToEquipFinger2 writer). It does.
    #   * uber_quest_markers says it "reads chanceToEquipFinger2 ... so the roster
    #     is computed against FINAL rates". soul_identity is the LAST writer of
    #     that field (it zeroes it on the 22 identity thieves), so the marker
    #     roster is only computed against final rates if soul_identity runs
    #     BEFORE uber_quest_markers. Registering it after would leave
    #     uber_quest_markers' apply() deriving from stale pre-detachment rates
    #     while its verify() re-derives on the final db - the two could disagree.
    # This slot is the ONLY position that satisfies both, with coldworm_buffs
    # (Cold Worm's kit, disjoint) and fx_dangling_cleanup (LAST) unmoved.
    # The b99 integration PROVED the two rosters are in fact identical either way
    # (none of the 22 detached records is a placed uber or a chain anchor), so no
    # marker moved; the ordering is the permanent guarantee, not a repair.
    'emberteeth_summon',    # b91 DEBT / QUEUED FEATURE (Will 2026-07-14, verbatim "emberteeth
                            # soul should let you summon him"): converts the 3 pure-fire-stat
                            # emberteeth_soul_{n,e,l} rings into summon-the-boss souls - 3
                            # permanent pets built from um_emberteeth's OWN rig via the shared
                            # _build_boss_summon pipeline + a manual-cast summon button, wired
                            # 1/2/3 so the epic soul spawns the epic pet (R-43 companion check).
                            # Every pre-existing fire benefit is kept (apply() proves it field by
                            # field). Registered after every soul-wiring + drop-rate module so it
                            # sees the FINAL soul records, and before fx_dangling_cleanup so its
                            # new skill records are still swept by the FX hygiene pass.
    'soul_identity',        # b97 (Will 2026-07-27): "some of the heroes are dropping the wrong
                            # souls or souls for other boss monsters". A creature must not drop a
                            # soul whose IDENTITY belongs to a DIFFERENT named creature that also
                            # drops it. Data-derived rule (display-name identity, never the .dbr
                            # filename - the axis that caused the defect); zeroes ONLY
                            # chanceToEquipFinger2, only downward, on the 18 identity thieves,
                            # leaving lootFinger2Item1 intact. Structurally cannot orphan a soul:
                            # a family with NO identity-owning carrier (archetype souls,
                            # name-drift 1:1, mod-themed "Soul of the X") is never touched.
                            # Registered after EVERY soul-wiring + drop-rate module (incl.
                            # toxeus_souls_100, whose two 100% champions are sole carriers and
                            # thus untouched) so apply() sees the FINAL carrier set; verify()
                            # re-runs the rule over the final merged db as the permanent,
                            # list-free regression gate. See docs/reports/b97_soul_identity_audit.md.
    'coldworm_buffs',       # b91 (Will 2026-07-16, R-39): THE COLD WORM BUFFS LANE - 3x
                            # characterLife, +20% armor (defensiveProtection, delivered at the only
                            # layer where monsters carry it: the armor_passive level, whose
                            # defensiveProtection array is exactly linear), the rig-proven
                            # um_coldcreep_29 total-speed profile, and a casting kit that ACTUALLY
                            # CASTS. RCA: boss_coldworm50's entire kit pointed at the
                            # `boss skills\d2custom\coldworm_*` + `Game\D2*` namespace, which exists
                            # in NEITHER the mod arz, NOR upstream SV 098i, NOR the base game - 8/8
                            # active slots dead, the worst record in the whole DB (next-worst: 2).
                            # Every dead slot is repointed at a donor that exists, at that donor's
                            # own level (CryptWorm-rig donors um_coldcreep_29 / am_devourer_27 +
                            # nearest-tier insectoid bosses). Ships its own NEW invariant gate: an
                            # active skill slot must resolve AND, if the skill declares a
                            # skillSpecialAnimationName, the caster must bind that ref (the
                            # monster-side twin of the B-SOUL-PROC-2 StartSkill anim abort) -
                            # negative test `py tools/patches/coldworm_buffs.py --negtest`.
                            # Registered after boss_skill_fix (scoped to um_*_99, disjoint) and
                            # immediately before visuals, so it is the ratified final registry
                            # writer of Cold Worm's kit. Touches exactly ONE record; the 3-tier
                            # soul + loot triple are asserted, never rewritten.
    'general_guardians',    # R-100 #18 (Will 2026-07-29): the six Guardians of the General
                            # ("super weak ... no chests ... no orbs ... small ... look just
                            # like the other guys ... no special skills"). RETUNES the 6
                            # svc_general_{a,b,c}_guard{1,2} records four_generals builds +
                            # their 3 pair proxies, and adds 27 new hoard records (3 dedicated
                            # Champion-locked chests, one per PAIR). Measured on main: they
                            # shipped at scale 1.45 (SMALLER than the 1.5 warden they were
                            # cloned from), life [3200,4200,5400] vs their general's
                            # [20244,25305,30366], and a kit inherited VERBATIM from that
                            # warden - four_generals added zero skills, so all six fought
                            # identically to the trash beside them.
                            # Registered AFTER coldworm_buffs / boss_skill_fix (the
                            # coldworm_buffs precedent) so it is the ratified final registry
                            # writer of the guard records, and BEFORE uber_quest_markers,
                            # which it deliberately does not enter: the guards pay no soul, so
                            # rule A keeps them out of the marker roster and three markers per
                            # war-council room is the map spam rule A exists to prevent. That
                            # one call is FLAGGED FOR WILL, not guessed (R-100 #18 calls these
                            # "the uber bosses we added" while #7 asks for markers on "all the
                            # uber bosses we made").
                            # No pet-spawners by construction, re-asserted mechanically, so
                            # the b76/R-31 density law cannot be touched by this lane.
                            # Orb tier is genericbossorb_03 (the guards' own L45-48 band):
                            # NOT _04 (the marshal tier whose consumer set uber_apex_orb
                            # audits) and NOT _05 (R-99's reserved Toxeus apex).
                            # Negative test: py tools/patches/general_guardians.py --negtest
    'uber_quest_markers',   # b91 (Will 2026-07-16, R-39, 6th sub-item): "the exclamation-marker
                            # mechanism extended to all placed ubers". CORRECTION to b91 round 1,
                            # which recorded this as map-side and BLOCKED: the marker is the
                            # DB-side Monster field DisplayAsQuestItem (145 non-zero carriers,
                            # 124 of them Monster - every base-game quest boss, every xsq named
                            # quest hero, the escort NPCs, the quest chests/doors/objects and the
                            # records\poi\** AreaOfInterest map-marker namespace). It is ALREADY
                            # LIVE in this mod on the very boss the ruling is about
                            # (records\test\boss_coldworm50.dbr = 1) - the mechanism was never
                            # missing, only never extended. No Levels.arc build, no
                            # SVC_SVAERA_ARC/SVC_SV_ARC dependency, no map bytes.
                            # Roster is DERIVED, never hardcoded: build_svc_database.
                            # soul_spawn_provenance_sets()'s placed_members (the same source of
                            # truth as the PLACED_UBER 66% soul rate, R-42), narrowed to the
                            # ENCOUNTERS by rule A (it, or a form in its actorToSpawnOnDeath
                            # chain, actually pays a soul out - which excludes the 26 champion
                            # retinue/adds mechanically) and widened by rule B across DEDICATED
                            # transform forms only (a form whose spawners are ALL in the roster).
                            # Rule B's exclusivity test is load-bearing: as_ghosthero_32 is
                            # Neferkha's terminal form AND five roaming mummy heroes', so a naive
                            # whole-chain walk would spam the marker across the map.
                            # Both rules are DERIVED from shipped content, not invented: the one
                            # placed uber already marked on main is um_polisgaoler_99 AND its
                            # dedicated um_polisgaoler_unbound_99 - exactly rule A + rule B.
                            # Registered after coldworm_buffs (same ruling, same lane) and
                            # immediately before visuals, so it is the ratified final registry
                            # writer of the field; it reads chanceToEquipFinger2, which
                            # toxeus_souls_100 (R-48) writes earlier, so the roster is computed
                            # against final rates. Ships its own gate (every placed uber + every
                            # dedicated chain form must carry DisplayAsQuestItem=1, and no SHARED
                            # form may) - negative test `py tools/patches/uber_quest_markers.py
                            # --negtest`. One field, 0 new records, 0 tags.
    'devourer_kit',         # b102 (Will 2026-07-29, R-100 #1/#12/#13 + R-103 + R-107): the
                            # Devourer + Endless Hunt wave. (a) CLONES a monster-only Toxeus
                            # passive at defensiveReflect 30/33 and repoints ONLY the 6 Toxeus
                            # MONSTERS - the shared toxeus_passiveproperties has 18 carriers and
                            # NINE are Will's own summoned PETS, so the one-line in-place edit
                            # R-107 warns about would have stripped 70 reflect off the pets he is
                            # using to fight the boss (the genericbossorb_04 lesson); pets,
                            # drxcreatures\crowheroes\less.dbr and the 2 zzdev dummies keep 100/33.
                            # (b) Devourer defensivePierce 70 -> 40 (R-107 lever 2, his spear
                            # build); characterLife deliberately untouched (lever 3, held in
                            # reserve). (c) Bloodbath: melinoe_bloodboil is shared with 6 Toxeus
                            # PET records, so the 45s -> 15s cut lands on a CLONE
                            # (svc_devourer_bloodbath) with its 'BloodBoil' skillSpecialAnimation
                            # DELETED - anm_skeleton01 binds no such ref, so B-SOUL-PROC-2 aborted
                            # every cast and the Devourer's 90%-chance signature nova had never
                            # once fired. (d) new summonable minions for BOTH champions (Gorged
                            # Bloodspawn off his own declared blood-demon retinue; Coursers of the
                            # Endless Hunt off the DRX bloodhound rig), petLimit 3 each. Blood
                            # Frenzy is asserted, NOT duplicated (b73 already placed it).
                            # ORDER IS LOAD-BEARING: MUST run BEFORE 'toxeus_hunt_endless', which
                            # generates um_toxeus_hunt_l_99 as a clone-then-override of the base
                            # Hunt and whose verify() asserts the two differ in EXACTLY the
                            # `controller` field - so the Legendary variant inherits the retuned
                            # passive and the courser summon by construction instead of drifting
                            # (and that gate stays green). Also AFTER every other writer of the
                            # two champions' kits (toxeus_suite / toxeus_champion_kits /
                            # boss_skill_fix / black_poison / toxeus_hunt_encounter /
                            # toxeus_souls_100 / uber_apex_orb / uber_quest_markers), so it is the
                            # ratified last writer of the slots it claims, and BEFORE
                            # 'fx_dangling_cleanup' so the FX sweep still covers its new records.
                            # Negative test: py tools/patches/devourer_kit.py --negtest
                            # R-100 #7 (Will 2026-07-29) ADDS ONE RULED EXEMPTION: the Devourer
                            # (um_bloodtoxeus_99) "is sitting on a chest a hidden location and
                            # should not be so easily found", so he is forced to
                            # DisplayAsQuestItem=0 - he ships MARKED on main (b91 put him in the
                            # roster), so this is an UNMARK, not a skip, and the gate asserts the 0
                            # rather than just omitting him. Roster 26 -> 25 + 1 exempt. The
                            # exemption is cross-checked against the derived roster (a stale entry
                            # reds the build) and closed over actorToSpawnOnDeath. Every other
                            # Toxeus variant (Enslaver, both Endless Hunt forms) stays MARKED -
                            # Will asked for those explicitly.
    'r247_boss_forms',      # R-247 rulings 3/5a/6 (Will 2026-08-13): Lethaeus core becomes the
                            # ESCALATION (scale 3.1 / life 16-28k / hand 300-330, kit intact);
                            # the Endless Hunt becomes an Undead GIANT SKELETON
                            # (SkeletonRumorBoss.msh + NewSkeleton_White + anm_skeleton01, all
                            # inline foreign-rig .anm rows cleared - the b98 demon body was the
                            # b98 design, superseded by R-247.5a - then the spear + unarmed rows
                            # REBOUND INLINE from the table's own clips incl. 'AoE360' on both,
                            # r3: the adfda67 both-surfaces law, so toxeus_hunt_encounter's
                            # SPEAR-ANIM-1/CASTABILITY-1 gates pass and bladestorm is castable
                            # on the row he occupies); his soul finally SUMMONS him
                            # (pets toxeus_hunt_1/2/3 via _build_boss_summon from the FIXED
                            # skeleton Hunt + summon_toxeus_hunt granted at tier 1/2/3);
                            # enslaver/blood/hunt tier ladders raised (x1.5 epic / x1.75
                            # legendary) + per-tier display names; +all-skills 1/2/3 law on the
                            # family souls (+EoAT 3); the EoAT formula goes Legendary-classified
                            # (visibility - the 100% drop wiring was measured CORRECT).
                            # ORDER IS LOAD-BEARING, both sides: AFTER devourer_kit (it builds
                            # the huntsman pack + hunt summon this identity pairs with; also
                            # after every enslaver/blood pet writer so the tier retune reads
                            # final values) and BEFORE toxeus_hunt_endless (um_toxeus_hunt_l_99
                            # is a build-time clone of the base, so the Legendary variant
                            # inherits the skeleton identity and the one-field-diff invariant
                            # stays green; the module SystemExits if the clone already exists).
    'toxeus_hunt_endless',  # b98 (Will 2026-07-28, R-90): "yeah lets have the endless pursuit only
                            # be on legendary". Pursuit is a CONTROLLER property and both
                            # MaxPursuitDistance and PursuitTime are declared class="variable" in
                            # the engine's own controllermonster.tpl (scalar, never a per-difficulty
                            # array), so the only honest route is a second monster record selected
                            # by the proxy's poolLegendary1 slot - the shipped djinnsprite
                            # ambush-vs-normal pattern. Authors a dedicated relentless controller
                            # (CLONED, never editing the 15-monster shared donor), a variant monster
                            # and a single-member Legendary pool.
                            # ORDER IS LOAD-BEARING: registered LAST among content modules, after
                            # EVERY writer of the base record (toxeus_hunt_encounter,
                            # toxeus_champion_kits, boss_skill_fix, toxeus_souls_100 AND
                            # uber_quest_markers), because the variant is generated as a
                            # clone-then-override of the base at build time - so it inherits the
                            # R-91 100% soul rate and the DisplayAsQuestItem marker by construction
                            # instead of drifting. verify() asserts base and variant differ in
                            # EXACTLY the `controller` field, which is what makes the doubled record
                            # safe. Placed before fx_dangling_cleanup so the FX hygiene sweep still
                            # covers the new records. Negative test:
                            # py tools/patches/toxeus_hunt_endless.py --negtest
    'champion_mesh',        # b102 (Will 2026-07-29, R-102 + the R-93 remainder): THE ENSLAVER'S
                            # GREEN GLOW. Four waves (b39/b55/b55r2/b92) edited FX FIELDS and none
                            # moved a pixel, because the green is not in a field: it is the
                            # CreateEntity block compiled INTO
                            # Creatures\Monster\Skeleton\RevenantPoison.msh (measured from the
                            # shipped bytes by tools/mesh_assets.embedded_fx_of ->
                            # Records\Effects\MonsterFX\Buffs\RevenantPoison_FX.dbr, an
                            # ADDITIVE-blend .pfx on Bone_R/L_Weapon). baseTexture replaces the
                            # primary skin only, so no .dbr edit can reach it. Moves the Enslaver
                            # family onto SkeletonGrayBlack01New.msh and the Devourer family (incl.
                            # the EoAT pets that clone his) onto GoldenSkeleton01.msh - both
                            # measured FX-FREE with a bone set IDENTICAL to RevenantPoison's, and
                            # DISTINCT from each other and from the Hunt's ShadowStalker.msh, so
                            # R-93's "three champions, three creatures" lands in the same commit
                            # instead of being traded away.
                            # ORDER IS LOAD-BEARING: registered after EVERY module that authors or
                            # rewrites a champion record - toxeus_suite, toxeus_champion_kits,
                            # toxeus_endofallthings (author of the EoAT pets), enslaver_pet_fx,
                            # enslaver_shroud, toxeus_hunt_encounter and toxeus_hunt_endless (which
                            # CLONES um_toxeus_hunt_l_99 at build time, so it must exist before this
                            # roster is resolved) - making this the ratified last writer of `mesh`
                            # on the roster. Still before fx_dangling_cleanup so the FX hygiene
                            # sweep covers the final state. Writes ONLY on a real change, so a
                            # record already carrying the right mesh is not re-encoded.
                            # The roster is DERIVED: only the anchor monsters, the preview proxies
                            # and each champion's own soul-summon skill are named; every pet tier is
                            # read out of that summon's spawnObjects, so a 4th tier is picked up by
                            # the fix AND the gate with no code change (the exact defect class of
                            # R-102's second amendment, where the shroud reached the monster and
                            # none of the three pet tiers).
                            # SHARED-RECORD LAW: RevenantPoison.msh has 30 carriers and only 13 are
                            # ours; the other 17 (base/SV green revenants on newskeleton_grean.tex,
                            # 10 pharaoh honour-guard summons, 1 dev dummy) are untouched, and
                            # verify() fails if the mesh is ever emptied out of the DB entirely
                            # (RETIREMENT PROTOCOL).
                            # ⚠️ R-257 (b101): the Enslaver's destination is no longer the bare
                            # FX-free base rig. ENSLAVER_MESH is IMPORTED from
                            # enslaver_shroud.SHROUD_RIG - a mod-authored byte-copy of that
                            # same rig carrying the demons' OWN CreateEntity block. This
                            # module's b102 swap onto an FX-free mesh is what removed the
                            # Enslaver's last always-on emitter and started five filings of
                            # "he has no black smoke", so the fix belongs here, in the single
                            # writer of `mesh`. Two gate changes: the embedded-FX allow-list is
                            # now PER FAMILY (a shared list would have let the Enslaver satisfy
                            # his gate with the Hunt's Boss Aura), and a family whose allowed
                            # effect is MISSING now REDS - the arm that catches the b102
                            # regression. R-93 distinctness stands three ways; the green ban on
                            # RevenantPoison.msh is untouched; the rig-name table is identical
                            # to the donor's so the animation gate is unaffected by
                            # construction.
                            # Negative test: py tools/patches/champion_mesh.py --negtest
                            # (15 plants; new: the Enslaver family regresses to the plain
                            # FX-free rig, which every pre-R-257 arm was happy with)
    # b104 NOTE (Will 2026-08-11): the 'devourer_shroud' module that briefly sat
    # HERE was deleted, target misidentified. Its own measurement disconfirmed it:
    # the Devourer's Blood Demons carry blood FX, no shadow shroud, so "the same
    # one that his demon summon guys have" cannot be him. The fix moved into
    # `enslaver_shroud` above (R-250). The Devourer's own missing shroud is a
    # QUESTION for Will (BL-R250-DEBT-2), not a change made on our authority.
    'fx_dangling_cleanup',  # b91 DEBT: B-FX-DANGLING-1 (strip the 353 dangling
                            # Chris\UnarmedProjectile_FX01 particleEffectName2/3 slots off 177
                            # records - base-game ABSENCE parity, the same operation build30 F7a
                            # ran on 3 pcsafe clones) + BLOODHOUND-DYINGFX (already resolved in
                            # the arz; this module ships the permanent resolve-or-fail gate the
                            # debt never had) + the F3 leftover DRX skin field on supra wep_spear.
                            # Registered LAST among content modules (before the no-op 'visuals')
                            # so it sweeps the FINAL assembled db and no later module can
                            # reintroduce the class. Deletes only whitelisted field slots; apply()
                            # proves roster-wide that nothing else moved.
    'weapon_gate_truth',    # b100 (Will 2026-07-29, R-100/R-101/R-102): tooltip-vs-gate honesty
                            # for the two dodge passives whose bonuses are silently dead unless
                            # the player dual wields - Occult Blade Mastery (text-only; the record
                            # is deliberately UNTOUCHED, narrowing/widening the gate is Will's
                            # balance call) and Warfare Parry (skillBaseDescription REPOINTED off
                            # the shared base tag tagSkillDescription192 onto the new mod-owned
                            # tagParryDESC, per the R-41 re-point-over-edit-a-shared-tag rule).
                            # Touches exactly ONE field on ONE record, in a namespace no other
                            # module writes (records\skills\warfare\drxdodge attack.dbr), so it is
                            # order-independent; registered here, after mastery_unlock_alignment
                            # and every skill-UI writer, purely so its verify() gate reads the
                            # FINAL assembled skill records. verify() = the DB half of the gate
                            # (contracted records' gating fields must still match the gate their
                            # shipped tooltip describes, plus a sweep for NEW uncontracted
                            # dualWieldOnly player skills); the TEXT half is
                            # tools/validate_weapon_gate_text.py, run by build_text_arc.
    'uber_quest_drops',     # R-101 P0 (Will 2026-07-29, reported TWICE - Charon's Oar, then the
                            # Key of the Warden of Souls): cloning a quest boss to make an uber
                            # copies perPartyMemberDropItemName, so a quest-GATING item became
                            # farmable off a repeatable encounter. Clears the field on the 3
                            # MEASURED clones (um_charonform2_ferryman_99, um_polisgaoler_99,
                            # um_polisgaoler_unbound_99 - the third found by the sweep, not by
                            # play) and NOTHING else: it never writes a donor, an item, or a pool.
                            # Registered LAST among content modules (after polis_vault and every
                            # other boss-creating module, and after the whole monolith) so its
                            # DB-wide gate - "no um_* record may carry a per-party drop resolving
                            # to itemClassification==Quest" - reads the FINAL assembled roster.
                            # S4b COLLISION IS EXPECTED on all 3 and is benign - MEASURED from the
                            # build, not predicted: um_charonform2_ferryman_99 <- uber_quest_markers,
                            # and both Gaolers <- polis_vault. The field sets are disjoint (minimap
                            # marker / boss kit vs perPartyMemberDropItemName) and this module runs
                            # LAST, so it is the ratified final writer on its own field. A WARN
                            # naming a module that also writes perPartyMemberDropItemName on any of
                            # those 3 is a real finding: investigate before shipping.
    'charon_rework',        # WILL 2026-08-11, verbatim: "the charon uber boss we created
                            # needs to be re-worked, he is pretty much identical to the base
                            # game charon boss we cloned him off. maybe we can replace him
                            # with a different uber monster that is more unique". He is right
                            # and the arz proves it: both our forms carried boss_charon_43 /
                            # boss_charonform2_43's kit BYTE-FOR-BYTE (same skillNames, same
                            # specialAttack rotation); the only authored deltas were life,
                            # four resist floats, scale, actorHeight and one aura. Replaces the
                            # encounter IN PLACE at the three frozen record paths with AKREMON,
                            # THE GRASPING ROOT -> THE HEARTWOOD ABLAZE + 2 Handbriar champions:
                            # Plant (race count in the 53-boss uber roster: ZERO), the mod's
                            # ONLY Skill_DefensiveWall carrier, bleed-immune phase 1 that stops
                            # being bleed-immune in phase 2. ARZ-ONLY - the Golden Bough
                            # forecourt placement, its proxy/pool chain and the world chest are
                            # REUSED, never rebuilt, so no map rebuild is implied.
                            # ORDER IS LOAD-BEARING, both sides:
                            #  * AFTER `uber_quest_drops` - that module REQUIRES the pre-rework
                            #    um_charonform2_ferryman_99 to still carry the inherited
                            #    perPartyMemberDropItemName it clears (it SystemExits if the
                            #    field is already absent). Running after it means the leak is
                            #    cleared on the old contents and the new donors carry no such
                            #    field at all, which its verify() accepts.
                            #  * BEFORE every breadth/derivation module (chest_loot_breadth,
                            #    armor_loot_breadth, red_uber_orbs, orb_loot_breadth,
                            #    orb_armor_rows) - those derive their scope FROM these monster
                            #    records, so they must see the final contents at apply() AND
                            #    verify() time or the two disagree.
                            # It re-asserts DisplayAsQuestItem after its re-clone, because
                            # `uber_quest_markers` (earlier) writes that field on these records
                            # and its verify() re-derives on the final db.
                            # Its verify() is the fail-loud gate: the proxy chain resolves to
                            # the new boss on BOTH the forecourt and the TESTHUB yard, all three
                            # guaranteed rewards stay wired (Golden Bough at Misc4 100%, the one
                            # hoard chest, the soul), A9 render chain (own-rig clones only, no
                            # invented actorHeight, no single-carrier skin), the crash laws, the
                            # NEW strictly-ascending-life invariant over every svc_* Champion
                            # escort (the shipped one was [878, 300, 400] - life FELL from Normal
                            # to Epic, R-100 #18 as a measurable field), and an identity gate that
                            # fails if any charon_* signature skill or shared cast rotation ever
                            # comes back.
    'pc_dissolve_restore',  # PR-1 (Steam player fleurydid 2026-07-29, "quand je meurt tombe
                            # invisible"): the PLAYER goes INVISIBLE on death/respawn. The two
                            # ACTIVE PC records (femalepc01/malepc01) are taken verbatim from SV
                            # 0.98i, which STRIPPED the base+SVAERA dissolveTexture
                            # (Effects\Textures\CloudTEST03.tex) that feeds the engine's death/
                            # despawn alpha-FADE pass, while KEEPING female allowTransparency=1
                            # (the enable for that path). With the path enabled and no dissolve
                            # texture the female mesh is left transparent on death and the respawn
                            # never restores it. base (allowTransparency=0 AND texture present) and
                            # SVAERA (allowTransparency=1 BUT texture present) are both safe; only
                            # our lineage has path-on + texture-off. This module restores the
                            # base+SVAERA value on BOTH PC records - strictly additive, matches the
                            # maintained port exactly on the female path, resolves in base
                            # Effects.arc. Disjoint namespace (no other module writes those two
                            # creature records), so order-independent; registered here purely so
                            # verify() reads the final assembled db. In-game confirmation is
                            # launch-gated + gender-dependent (see docs/BACKLOG.md PR-1).
                            # Negative test: py tools/patches/pc_dissolve_restore.py --negtest
    'gorgon_vanilla_names', # PR-4 (Steam player Flozer44 2026-07-28; Will 2026-08-06 "restore
                            # the FULL VANILLA names"): the two gorgon spellcasters show their
                            # vanilla names SWAPPED. SV 0.98i FLIPPED the record->descriptionTag
                            # pointers relative to base TQAE (the STRINGS are byte-identical in
                            # both). Base assigns FIRE ar_pyromancer_13/16 -> tagMonsterName1263
                            # ("Gorgon ~ Geomancer") and POISON ar_venomancer_13/16 ->
                            # tagMonsterName1256 ("Gorgon ~ Profaner"), derived from each
                            # creature's OWN kit (BlazingWeapons vs Arachnos_VenomBolt). This
                            # module repoints description back to the base-game assignment on the
                            # 4 records - smallest correct change: no tag STRING edited, no NEW
                            # tag minted (the two are base-game tags, present in base Text_EN AND
                            # our Text.arc). SHARED-RECORD LAW: verify() asserts the two tags are
                            # carried by EXACTLY these 4 records in the merged DB (XPack4 chaos
                            # gorgons use the DISTINCT x4tagMonsterName*Chaos tags). Name is bound
                            # to identity: apply()/verify() re-check the archetype kit signature.
                            # Disjoint namespace (no other module writes these gorgon records), so
                            # order-independent; registered here purely so verify() reads the final
                            # assembled db. In-game confirmation launch-gated (name read-back proven
                            # from the rebuilt Text.arc in this lane).
                            # Negative test: py tools/patches/gorgon_vanilla_names.py --negtest
    'craft_thrown_breadth', # Will 2026-08-10 ("i meant do the mythic formulas drop. they
                            # can drop in normal as well, but the legendary items should
                            # not drop in normal. All of the reagents need to be droppable
                            # somewhere in the game... Yes we should make the legendary
                            # thrown weapons droppable"): the CRAFT-CHAIN half of the
                            # chest-breadth wave, where R-180 was the WEAPON-CLASS half.
                            # THREE measured defects, all closed here. (1) The 42 uber
                            # "supra" formulas sat on arcaneformulae\supra.dbr, which the
                            # base game wires into the 02_ (Epic, 2%) and 03_ (Legendary,
                            # 5%) act tables ONLY - a Normal chest reached 0 of 42. supra
                            # is added to each 01_act{1..4}_arcaneformulae at ~1% of that
                            # table's own total (rarer than either existing tier);
                            # formulas are itemClassification=Common, so no legendary GEAR
                            # moves and the R-100 #17 tier law is untouched. (2) 36 of the
                            # 78 uber reagents were unreachable from a legendary chest: 19
                            # MI/green (Will's own exemption, each PROVEN monster-farmable
                            # by the gate), 8 ordinary base uniques + 6 IT divine artifacts
                            # (placed into 4 new svc_craft_reagents_*_l01 tables hung off
                            # the legendary hosts unique_torso_l01 / amulet_l01 /
                            # finger_l01 / 04_l_misc - all 14 are Legendary-classified, so
                            # they can only ever enter a legendary branch), and 3 that DO
                            # NOT EXIST: Charon's Toll, Hati, The Last Word and Sanguine
                            # Orbit all named RAGNAROK records
                            # (xpack2\item\equipmentweapons\1hranged\{u_l_08,u_e_06,
                            # mi_l_machae}) that this TQIT-era build never ships, so those
                            # four formulas were uncompletable by anyone; they are
                            # repointed onto thrown records that exist. (3) The THROWN
                            # class had no unique loot table in this era at all, so 0 of 5
                            # legendary thrown were reachable from anything: this module
                            # authors svc_unique_thrown_{n,e,l}01 and svc_loot_breadth
                            # names it as the SEVENTH class of svc_unique_weapons_{tier}01
                            # at weight 250 (the proportional share of a 5-record class
                            # against the 17-24 of the other six). Normal's thrown table
                            # names ONLY the itemLevel-30 Rare/Common wands, so no
                            # legendary thrown can reach Normal.
                            # ORDER IS LOAD-BEARING: it must run immediately BEFORE
                            # chest_loot_breadth, because ensure_masters silently skips a
                            # master member whose donor does not resolve - the thrown
                            # tables have to exist first. polis_vault's earlier call to
                            # the same idempotent builder writes 7-member masters;
                            # chest_loot_breadth's call rewrites them with the eighth.
                            # Writes NO chest/hoard FixedItemLoot record, no orb table and
                            # no weight another lane owns. verify() is the fail-loud
                            # craft-chain gate (standalone twin:
                            # py tools/gate_craft_thrown_breadth.py <arz>; negatives:
                            # py tools/debug/negtest_craft_thrown.py <arz>).
    'supra_recipe_laws',    # Will 2026-08-11, THREE rulings ("one of the items needed to
                            # craft the formula needs to be found in legendary like the
                            # rest of the craftable supra recipes" + "each craftable supra
                            # should have different requirements (we should not have two
                            # formulas that both require stymphalian, plisskey, and
                            # deathweavers legtip)" + "the last word should not be dropped
                            # in epic, only legendary"). FOURTEEN supra formulas each get
                            # ONE reagent slot repointed: 10 collapse the five duplicate
                            # reagent-set groups the build83 arz carried (a SIX-way axe
                            # group, a three-way mace group and three pairs - 15 of the 42
                            # craftables) to 42 distinct sets, and 4 give the thrown
                            # recipes the Legendary-only reagent they lacked. Every
                            # replacement is Legendary-only and already on 19/19 legendary
                            # chest surfaces, so no loot table moves. LAW C's own fix is
                            # four memberships in svc_craft_thrown.THROWN_MEMBERS['e']
                            # (the supra thrown leave svc_unique_thrown_e01 and stay on
                            # svc_unique_thrown_l01), because that module owns the table
                            # and two modules must never write one record. ORDER IS
                            # LOAD-BEARING: immediately AFTER craft_thrown_breadth, which
                            # repoints the four thrown formulas off the Ragnarok ghosts -
                            # this module reads the formula/result map afterwards and
                            # fails loud on a stale one. Writes no loot table at all.
                            # verify() is the fail-loud S1/S2/S3/S4 gate (standalone twin:
                            # py tools/gate_supra_recipe_laws.py <arz>; negatives:
                            # py tools/debug/negtest_supra_recipe_laws.py <arz>).
    'chest_loot_breadth',   # Will 2026-08-10 ("there are never any legendary spears
                            # dropped it is basically the same items dropped over and
                            # over by all chests"): the BLAST-RADIUS half of the chest
                            # breadth wave. Every mod chest is a clone of the DRX donor
                            # loottable_hidden_bloodcave_0N, whose weapon row names
                            # unique_1h_*01 (axe/club/sword ONLY) + bow + staff and
                            # simply forgot the third excluded class, SPEAR - so all 24
                            # legendary spears in the DB were unreachable from all 40 mod
                            # chest tables. This module sweeps every mod-owned gear chest
                            # PLUS the 3 DRX donors and applies the shared
                            # tools/svc_loot_breadth contract: one aggregate weapon master
                            # into the single free loot1 member slot, the dead weapon /
                            # shield group chances raised, and the guaranteed loot3 weapon
                            # member re-aimed from unique_1h_*01 onto that master AT THE
                            # SAME WEIGHT (so every chest's weapon:relic split is exactly
                            # what shipped; only the classes it can pay widen 3 -> 6).
                            # ORDER IS LOAD-BEARING: it must run LAST among content
                            # modules because it sweeps the FINAL table set - the monolith
                            # hoards, general_guardians' 3 guard-pair hoards,
                            # uber_apex_orb's apex tables and polis_vault's cage are all
                            # authored earlier, and a chest authored after this sweep would
                            # keep the collapsed row. Tables polis_vault already widened
                            # (it applies the same helper while writing its per-chest
                            # THEMES) are detected and skipped, so NO S4b collision is
                            # expected between the two; a collision WARN naming them is a
                            # real finding. Its verify() is the build-wide fail-loud
                            # breadth gate (standalone twin:
                            # py tools/gate_chest_loot_breadth.py <arz>; negatives:
                            # py tools/debug/negtest_chest_breadth.py <arz>).
    'armor_loot_breadth',   # R-181 (Will 2026-08-10), TWO reports in one sitting: "also what
                            # about the armor? i am not really seeing armor drops like shields,
                            # chest plates, helmets, etc." and "you overcorrected, that run 4
                            # scorpions tail spears dropped". R-180 answered REACHABILITY; both
                            # of these are RATE reports, and R-180's gate was GREEN while the
                            # Gaoler cage paid 58.5 legendary weapons against 12.4 armour pieces
                            # per six-chest run with SPEAR alone at 24.0% of the legendary mass.
                            # MEASURED on the shipped build76 arz 16994072: zero mod chests have
                            # an unreachable armour slot, so this is not a breadth defect at all -
                            # the torso/head row fired at 33% and put only 200 of its 1888 weight
                            # on unique armour (10.6%), arms/legs 31% and 400 of 2088 (19.2%),
                            # shields 30% and 100 of 931 (10.7%), while the GUARANTEED loot3 slot
                            # fires 100% every spawn iteration and is all weapons/relics.
                            # THREE FIXES, all additive or a strict raise (numSpawn untouched, no
                            # member removed, no chance or weight lowered, guaranteed slot still
                            # 100%, so expected drops per open strictly RISE):
                            # (1) every armour row lifted to the weapon row's own 40%;
                            # (2) unique-armour members raised to 850 and one aggregate ARMOUR
                            #     master (svc_unique_armor_{n,e,l}01 - all five worn slots at
                            #     equal weight, R-180's machinery reused) dropped into the first
                            #     free armour-row member slot at 800;
                            # (3) the "overcorrected" half: unique_1h_*01 pays THREE classes from
                            #     ONE member, so carrying a spear's weight made axe/mace/sword a
                            #     third of a spear each - re-weighted to 3x its single-class
                            #     siblings here AND inside R-180's weapon master, plus softened
                            #     class-bias weights in svc_loot_breadth.THEMES;
                            # (4) WEAPON-ROW SHARE PARITY (added in the round-2 vet fix): the
                            #     weapon row's aggregate master is raised until the row is
                            #     WEAPON_ROW_LEGENDARY_SHARE = 50% legendary, mirroring what
                            #     ARMOR_UNIQUE_WEIGHT already produces on the armour rows. The
                            #     armour constant is an ABSOLUTE derived from ONE donor family;
                            #     the armour statics happen to match across families but the
                            #     WEAPON statics do not (DRX 1500 vs uberorb apex 2500), so
                            #     lifting armour alone inverted the apex tables to 0.17:1 - an
                            #     85%-armour surface. Expressed as a share it self-corrects: the
                            #     cage and blood-cave rows are already above it and 0 records move.
                            # THE GUARANTEED SLOT IS NOT SWEPT. armor_groups() skips any group at
                            # chance >= 100 (read off the chance, NOT hardcoded to g3 - measured,
                            # it is g3 on all 48 chest/hoard tables but g4 on the apex tables).
                            # That row belongs to THEMES, and without the guard the sweep rewrote
                            # the warden theme's documented 50/50 weapon:armour split to 12.8/87.2.
                            # MEASURED six-chest cage run, before -> after: weapon:armour
                            # 4.73:1 -> 1.22:1; armour 12.4 -> 49.4 pieces; SPEAR 24.0% -> 9.8%
                            # and helm 1.6% -> 8.7% (even is 9.1%; after the wave EVERY one of
                            # the 11 classes sits between 7.8% and 10.8%).
                            # P(4 copies of ONE spear in a six-chest run)
                            # 27.0% -> 6.3% and P(4 Scorpion's Tails specifically) 2.07% -> 0.45%
                            # (analytic and Monte Carlo agree). NOT "negligible", and the record
                            # says so: P(SOME single legendary item lands 4x anywhere in the run)
                            # only moves 47.3% -> 39.7%, because total legendary gear per run
                            # RISES 70.8 -> 109.5 while numSpawn is deliberately untouched under
                            # the non-reduction law. numSpawn is the volume lever and it is a WILL
                            # DECISION, logged as BL-R181-DEBT-5, not taken silently here.
                            # ORDER IS LOAD-BEARING: immediately AFTER chest_loot_breadth, for
                            # the same reason that module runs late (it sweeps the FINAL table
                            # set) and because it raises weights R-180 wrote and reads members
                            # R-180 added. polis_vault also calls ensure_armor_masters, because
                            # the warden theme now names the armour master and a theme member
                            # whose donor does not resolve is dropped.
                            # SCOPE: every mod-owned gear chest - INCLUDING the 3
                            # svc_uberorb_apex_* tables - plus the 3 DRX donors. There is NO
                            # owner-based exclusion. An earlier round deferred the apex tables to
                            # the concurrent b79 fix/orb-loot-breadth lane; that lane provably
                            # does not widen armour on them (its own docstring calls them "a
                            # no-op here"), and the exclusion also hid them from the gate, so
                            # three LIVE surfaces - R-200's red-uber Mystical Orb chests and
                            # Leinth's hoards - shipped paying 0.07 helms per open. apply() now
                            # asserts WRITE SET == AUDIT SET and fails the build on any divergence.
                            # General MONSTER armour drops are measured and reported, never
                            # changed here (BL-R181-DEBT-2, a Will decision).
                            # Its verify() is the build-wide fail-loud DISTRIBUTION gate
                            # (standalone twin: py tools/gate_loot_distribution.py <arz>;
                            # calibration mode: --calibrate; negatives:
                            # py tools/debug/negtest_armor_breadth.py <arz>).
    'red_uber_orbs',        # R-200 (Will 2026-08-10): "boar snatcher legendary spider should drop
                            # a mystical orb like the other red uber monsters". "Mystical orb" is
                            # literal - every genericbossorb_0N chest carries description
                            # tagEndChest02, and base Text_EN defines tagEndChest02 = "Mystical
                            # Orb" (b53 predicted this exact sentence). The Boar Snatcher is
                            # um_boareater_40/42/44 (display tag tagAEMonsterName06; the RECORD is
                            # named "boareater", which is why a filename search finds nothing) -
                            # a base-game AE Boss-class SPIDER placed in PineForest04 +
                            # SpartaOptCave03, carrying no treasureProxyName at all.
                            # WHY NO GATE CAUGHT IT - TWO HOLES, BOTH CLOSED HERE. (1) There was
                            # no orb-breadth gate at all: every orb wiring in the repo is a
                            # hand-typed list (_BOSS_ORB_TARGETS, general_guardians, polis_vault,
                            # diadochi, four_generals, devourer_kit, leinth_wave) and the only orb
                            # GATES are uber_apex_orb's (the 8-record Toxeus roster + Leinth) and
                            # general_guardians' own - R-99 already learned in this exact domain
                            # that a typed list is how the Endless Hunt shipped orb-less.
                            # (2) THE HOLE THAT ACTUALLY HID IT: every roster derivation in this
                            # repo runs over the MOD db only, but the runtime resolution universe
                            # is mod UNION BASE. The Boar Snatcher is base-only, so it was
                            # invisible to every derivation and would have survived a naively
                            # written class gate too. This module therefore derives its roster
                            # over the UNION (it loads the base arz itself - 0.6s, cached - since
                            # build_svc_database `del base_db`s long before the registry runs;
                            # apply() REQUIRES it, verify() downgrades LOUDLY to mod-only, the
                            # fx_dangling_cleanup B-GATE-HARDEN-1 idiom, never a silent pass).
                            # CLASS: Monster.tpl + monsterClassification=='Boss' (the repo's own
                            # word for RED - see _amend_boss_loot_orbs) AND (a) basename um_* (the
                            # uber namespace uber_quest_drops swept for R-101) or (b) a
                            # tagSVCMonster* display tag (our own ubers under a donor filename;
                            # adds 3 records - Dagon, the Hades Marshal, Aithon - of which only
                            # Aithon was a miss).
                            # 55 red ubers measured, 41 already orbed, 14 missing -> 8 WIRED
                            # (Boar Snatcher x3 -> orb01; Neferkha 32 -> orb02, whose terminal
                            # as_ghosthero_32 is SHARED with 5 mummy heroes so the orb must ride
                            # the uber; um_frost_36 -> orb02; um_phagia_44 -> orb03, its lower
                            # twin um_phagia_34 was on orb02 already; Aithon 55 -> orb04;
                            # Kravmoloch 74 -> orb04, NOT orb05 which R-99 reserves) + 6 EXEMPT
                            # (4 transform shells whose TERMINAL carries the orb - the
                            # _MN_ORB_SHELL precedent - and 2 dropItems=0 soul-summon copies),
                            # each exemption re-proven mechanically so it cannot rot.
                            # Base-only records are IMPORTED field-for-field first (a mod record
                            # REPLACES its base counterpart wholesale, so a stub would delete the
                            # spider's kit); apply() proves the import is base-identical except
                            # the added field. Tier pins are cross-checked against the MEASURED
                            # consumer bands (minimum distance, ties to the lower tier), so the
                            # ladder is evidence rather than taste. Adds consumers only - never
                            # edits an orb/pool/chest/table - so uber_apex_orb's orb01/orb04
                            # FLOORS and its "orb05 carriers == the Toxeus roster" assertion both
                            # stay green. Registered second-to-last so verify() reads the final
                            # assembled db after every other orb writer.
                            # Negative test: py tools/patches/red_uber_orbs.py --negtest <arz>
    'orb_loot_breadth',     # R-220 (Will 2026-08-10): "for the mystical orbs that the uber
                            # monsters drop, the items should drop with increased breadth as
                            # well so all classes of items could be dropped". The "as well"
                            # points at R-180, which fixed the CHESTS that same morning; this
                            # is the same contract on the other half of the loot economy.
                            # MEASURED on the build76 ship arz: the orb tables carry the
                            # IDENTICAL collapsed weapon row (1h_all_*01 = axe/club/sword, bow
                            # and staff named DIRECTLY, SPEAR forgotten) so 0 spears of any
                            # quality were reachable from 15 of the 18 uber orb tables, at
                            # every tier and every difficulty. The 3 that were already fine
                            # are orb05's svc_uberorb_apex_* - and ONLY because they live in
                            # an \svc\ folder, so chest_loot_breadth's mod-ownership sweep
                            # reached them. This module finishes that sweep on the tables the
                            # ownership rule could not see, from the SAME implementation
                            # (tools/svc_loot_breadth.widen_weapon_row via
                            # tools/svc_orb_breadth.py) - not a second opinion.
                            # SCOPE IS DERIVED, NEVER TYPED (the R-200 lesson, and derived
                            # over mod UNION base for R-200's HOLE 2 reason): every proxy an
                            # UBER names (um_* basename or a tagSVCMonster* display tag), and
                            # every loot table its accessory1/Epic1/Legendary1 slots resolve
                            # to. MEASURED: 51 uber carriers -> 7 proxies (6 IN REACH) -> 18 tables =
                            # genericbossorb_01..05 (the mystical-orb ladder, tagEndChest02)
                            # plus bosschest02_charon, whose terminal Ferryman IS a red uber
                            # and whose 3 tables carry the identical collapse. (R-247.1:
                            # the terminal - now Akremon - names the clone proxy
                            # svc_akremon_orb instead; SAME 3 tables, kept in scope via
                            # svc_orb_breadth.DONOR_TWINS - the story Charon's donor
                            # chests are exempt from the shared-table refusal only while
                            # byte-identical to the clone chests outside `description`;
                            # negtest N10 plants the drift.) The 6 proxies
                            # consumed only by BASE act/quest bosses (Aktaios, Typhon, Black
                            # Widow, coldworm, the wanddrop test proxy) stay OUT - the same
                            # boundary R-200 drew - and are registered as BL-R220-DEBT-1.
                            # Leinth needs nothing: uber_apex_orb repointed her chests onto
                            # the svc_uberorb_apex_* tables, so R-180 already widened them.
                            # WRITES per table: the tier-correct master into the ONE free
                            # loot1 member slot (w800) + loot1Chance 13/14 -> 40 + loot6Chance
                            # 13/14 -> 30, which are the values orb05 has SHIPPED since
                            # build75 - so the ladder becomes self-consistent instead of a new
                            # number being invented. Everything else is proven byte-unchanged
                            # by apply()'s S4 scope proof over the tables AND every proxy /
                            # accessory pool / chest record in every chain: numSpawn equations
                            # (the apex keeps its *2.2/*2.4 edge), the relic/potion/armour
                            # rows, mesh, gold generator, level equation, tagEndChest02. No
                            # member removed, no chance lowered; chances may only RISE.
                            # There is deliberately NO guaranteed-weapon retarget: an orb's
                            # loot3 is potions + rare misc at 10%, not the chests' 100% weapon
                            # slot, and R-180's retargeter only rewrites a loot3 member
                            # matching unique_1h_[nel]0N, which no orb table names.
                            # ORDER IS LOAD-BEARING: after chest_loot_breadth (which authors
                            # the shared masters from the same idempotent builder, and whose
                            # sweep already widened orb05 - so those 3 tables are a NO-OP
                            # here, which is why no S4b collision is expected between the two)
                            # and after red_uber_orbs (which ADDS uber consumers, and the
                            # scope is derived from uber carriers). MEASURED before -> after,
                            # target-classification pool / reachable spears:
                            #   orb01 n 117->195 e  72->99  l 194->260   spear 0 -> 18/9/22
                            #   orb02 n 101->182 e  75->102 l 138->241   spear 0 -> 18/9/22
                            #   orb03 n  96->180 e  71->96  l 196->262   spear 0 -> 18/9/22
                            #   orb04 n  99->181 e  95->116 l 258->308   spear 0 -> 18/9/22
                            #   orb05 n 181 e 116 l 308 (unchanged, already fixed by R-180)
                            #   charon n 99->181 e 95->116 l 258->308    spear 0 -> 18/9/22
                            # Its verify() is the fail-loud gate (standalone twin:
                            # py tools/gate_orb_loot_breadth.py <arz>; negatives:
                            # py tools/debug/negtest_orb_breadth.py <arz>).
    'orb_armor_rows',       # BL-R181-DEBT-7: the OTHER half of Will's "i am not really
                            # seeing armor drops like shields, chest plates, helmets",
                            # on the surface nobody owned. R-181 gave every mod chest
                            # armour at weapon-row parity but keyed ownership off the
                            # \svc\ FOLDER; R-220 then wrote 15 tables in other folders
                            # (uberorb_default_*, boss_charon_*01b) and widened only
                            # their WEAPON row. MEASURED on the shipped build80 arz
                            # c5851a1a, all fifteen starved - weapon:armour 3.45:1 to
                            # 8.38:1, thinnest worn slot 0.007-0.044 per open against
                            # the D7 floor of 0.52 - with BOTH loot gates green, because
                            # a table no module claims is a table no gate audits.
                            # This module applies svc_armor_breadth.widen_armor_rows
                            # (the R-181 treatment verbatim) to R-220's OWN derived
                            # scope, and svc_armor_breadth.all_surfaces now reads that
                            # same derivation, so a 16th orb table is swept AND audited
                            # the day it exists - no list to keep in step.
                            # ORDER IS LOAD-BEARING: immediately AFTER orb_loot_breadth.
                            # The treatment includes the weapon row's own legendary-share
                            # balance, which is computed from the aggregate weapon master
                            # R-220 puts in loot1; running earlier would find no master
                            # and skip the half that stops the surface inverting to
                            # 85% armour (the R-181 D6b defect, shipped once already).
                            # Its verify() is the OWNERSHIP gate - every loot table
                            # WRITTEN in the build must be inside a distribution surface
                            # (tools/svc_loot_ownership.py); the numbers are still
                            # armor_loot_breadth.verify's distribution gate.
                            # Standalone: py tools/gate_loot_distribution.py <arz>;
                            # negatives: py tools/debug/negtest_armor_breadth.py <arz>.
    'loot_volume_trim',     # R-240 (Will 2026-08-11): "we probably need to trip the
                            # loot-volume trim, especially on the steam version where
                            # maybe from the two chests, you get guaranteed 1 legendary
                            # item. on the testhub version we can spawn more that is
                            # fine." This is the say-so BL-R181-DEBT-5 was waiting for:
                            # R-181 named numSpawn as the volume lever and refused to
                            # pull it without Will, so three waves raised COMPOSITION
                            # while volume stood still and the shipped b83 cage paid
                            # 36.4 Legendary gear pieces for two chests opened once.
                            # Non-reduction is suspended for VOLUME ONLY: this module
                            # writes numSpawnMin/MaxEquation and nothing else, and its
                            # own scope proof fails the build if any member, weight or
                            # group chance moves - so every breadth and distribution
                            # property b75-b83 shipped survives at lower volume, which
                            # the two gates running after it re-prove on the same db.
                            # ORDER IS LOAD-BEARING, LAST before the no-op 'visuals',
                            # for two reasons: (1) volume is an OVERRIDE - the monolith
                            # writes *2.4/*2.8 onto 27 hoard tables and polis_vault
                            # writes the cage's own - so running last makes this the
                            # single authority instead of something a later module
                            # silently undoes (the BL-R181-DEBT-7 failure mode);
                            # (2) the TESTHUB cage twin is CLONED from the finished
                            # canonical chain, so it inherits every b75-b83 edit for
                            # free and there is no second copy of the tuning to keep in
                            # step. The twin is how "canonical trims, TESTHUB stays
                            # rich" is expressed at all: one arz serves both map
                            # variants, so the split has to live in the RECORDS, and
                            # build_section_surgery.build_hub_extra_specs points the 4
                            # TESTHUB-only duplicate placements at the twin. Canonical
                            # B41_SPECS is untouched, so Levels_merged.arc stays
                            # byte-identical and the Steam delta stays arz-only.
                            # Its verify() also carries Will's 2026-08-11 artifact
                            # ruling (tools/svc_chest_artifacts.py) - which is NOT a
                            # no-op: 6 equippable artifacts are chest-reachable today
                            # by R-185's design, so the gate pins them by name with a
                            # re-derived rule and the residue is BL-R240-DEBT-2.
                            # Standalone: py tools/gate_loot_volume.py <arz> (--apply
                            # on a pre-wave arz, --calibrate to re-derive thresholds)
                            # and py tools/gate_chest_artifacts.py <arz>; negatives:
                            # py tools/debug/negtest_loot_volume.py <arz>.
    'orb_legendary_chance', # R-241 (Will 2026-08-11), and it SUPERSEDES the b79 "orbs
                            # stay generous" precedent wherever the two collide: "you
                            # made the orbs way too good... those dont need to have
                            # guaranteed legendary drops, they should just have a chance
                            # to drop legendary items, but a low chance."
                            # THE NUMBER HE ASKED FOR, measured on the shipped b83 arz:
                            # THREE guaranteed-legendary rows in the whole orb surface,
                            # one per difficulty, all of them group 4 of
                            # svc_uberorb_apex_{n,e,l}01c at chance 100% where their five
                            # sibling orb tables run the identical amulet/relic/ring row
                            # at 12.7% or 21.2%; none is a PURE legendary row (0.44/5.25/
                            # 6.28% legendary by weight).
                            # THE ROW COUNT IS NOT WHERE THE GUARANTEE LIVED, which is
                            # the finding: per ONE orb open b83 paid 2.58-6.29 legendary
                            # items on Epic (93.6-99.9% chance of at least one) and
                            # 3.74-8.43 on Legendary (98.4-99.99%) - six independent loot
                            # groups over 5.06-10.58 spawn iterations, no 100% row
                            # required. R-220's breadth gate, R-181's distribution gate
                            # and R-240's volume gate were ALL green on that.
                            # This module writes ONE field per census row - loot{g}Chance
                            # - demoted to the richest NON-guaranteed chance that row
                            # already carries in the orb family (21.2%), DERIVED from the
                            # shipped bytes and cross-checked against the value the
                            # contract was measured on. 3 records, 3 fields, 0 members,
                            # 0 weights, 0 spawn equations: breadth and distribution
                            # survive verbatim so the variety still lands WHEN a
                            # legendary rolls.
                            # With R-240's trim in the slot above, one open now pays
                            # Normal 0.001-0.004 legendary / Epic 0.451-0.622 /
                            # Legendary 0.699-0.846 - AT MOST ONE LEGENDARY ITEM PER OPEN
                            # on Legendary difficulty against 8.43 shipped, a 90% cut.
                            # ORDER IS LOAD-BEARING, immediately AFTER loot_volume_trim:
                            # (1) armor_loot_breadth SKIPS the guaranteed row by design
                            # (is_guaranteed_group - the WARDEN-theme lesson) and runs
                            # far earlier, so it must still see group 4 at 100% or the
                            # armour sweep would rewrite a theme row; (2) R-241's
                            # readings are measured against R-240's TRIMMED spawn volume.
                            # HONEST RESIDUE, not hidden: P(>=1 legendary) lands at
                            # 54-61% on Legendary, which is not yet "a low chance". ~40%
                            # of a Legendary orb's drop mass IS legendary-classified
                            # because R-180/R-220 weighted svc_unique_weapons_l01 /
                            # svc_unique_armor_l01 at ~47-50% of the weapon and shield
                            # rows to buy class breadth. Going lower means scaling those
                            # rows' chances, which divides D7b (worn-slot armour per
                            # SPAWN ITERATION, asserted on all 63 surfaces) by the same
                            # factor and reds armour parity on every orb - a COMPOSITION
                            # decision in R-180/R-181/R-220's scope, priced for Will as
                            # BL-R241-DEBT-1 rather than taken by a rate lane.
                            # Standalone: py tools/gate_orb_legendary.py <arz>
                            # (--census for Will's number, --calibrate, --apply);
                            # negatives: py tools/debug/negtest_orb_legendary.py <arz>.
    'r247_bloodcave_rulings',  # R-247 parts 7a/7b/7c (Will 2026-08-13, ANGRY): (a) the
                            # Devourer-stash tables loottable_hidden_bloodcave_01/02/03
                            # reverted to the SV 0.98i ORIGINAL numSpawn volume (*3.8/*4.1,
                            # ~19 iterations - R-240 had trimmed them ~12x; R-242 measured
                            # NOT involved), a Will-ratified R-240 scope carve-out mirrored
                            # in svc_loot_volume.R247_STASH_EXEMPT + the R-240 ledger
                            # amendment; composition (chances/weights/members, all >= SV)
                            # KEPT. (b) the egg_blooddragon stash-guard pool hardened to
                            # the in-game-proven _BT_POOL byte-shape (limit1..3=1 + weight
                            # 150; the bytes already guaranteed 1 Devourer main + 3 dragon
                            # champions on N/E/L - residual runtime channels are
                            # BL-R247-DEBT-6). (c) q_enslaver_warband chanceToRun 100 -> 0
                            # (the A1 set-piece shared the parchment chamber with the 33%
                            # Devourer ambush; R-247.7c supersedes that placement -
                            # relocation is BL-R247-DEBT-7, a Will map-lane decision).
                            # ORDER IS LOAD-BEARING: MUST run after loot_volume_trim (its
                            # apply() FAILS LOUD unless the three tables still carry the
                            # exact R-240-trimmed multipliers - which simultaneously proves
                            # the ordering) and after orb_legendary_chance (its verify()
                            # asserts the ORB sentinels kept their trim - the carve-out
                            # must not leak). Last writer of the three tables' numSpawn
                            # fields, the egg pool's limits/weights and the warband's
                            # chanceToRun. Negative test:
                            # py tools/patches/r247_bloodcave_rulings.py --negtest
    'uber_hoard_generosity',   # R-251 (Will 2026-08-14, FIVE reports in one session:
                            # BL-W0814-2/-5/-7/-11/-13 - "are you kidding me. this is
                            # outrageous ... literally just dropped two items one thing of
                            # gold and incarnation of guan-yu's grace"). THE SHARED CAUSE was
                            # a wire, not a number: the b42 finalization pass repointed every
                            # placed-uber hoard chest's `tables` at a base-game
                            # defaultloot\boss_default_<lo>-<hi>, so on the shipped b888f022
                            # arz 21 of 30 uber chests opened Cyclops-grade base loot and 18
                            # of the 27 svc_*hoard_loot_0N records had ZERO references in
                            # 51,312 - three breadth waves tuned dead records behind four
                            # green gates. Fixed AT the cause, outside this module: the
                            # monolith's `_svc_wire_boss_hoard_chests` now wires every hoard
                            # chest to its OWN table (and `_create_propontis_superboss`
                            # authors the missing Dorus family, which used to SHARE the
                            # Obsidian roulette's records by clone - Will's separation ask),
                            # and `svc_loot_volume._r251_exempt` takes the family out of
                            # R-240's trim so it keeps its authored *2.4/*2.8. What lives
                            # HERE is the one write with no other home - the SV/DRX-original
                            # Secret Present gift box at exactly 3x (BL-W0814-7) - plus the
                            # whole H1-H8 contract as a verify().
                            # ORDER IS LOAD-BEARING: MUST run after `loot_volume_trim` (and
                            # after `r247_bloodcave_rulings`, its sibling carve-out), because
                            # apply() FAILS LOUD unless the hoard family came through the
                            # trim UNTRIMMED - which is the live proof that the R-251
                            # carve-out fired, and can only be checked once the trim has run.
                            # verify() deliberately runs in step 4: the WIRING half lands in
                            # run_registry_gates (step 3), AFTER every registry apply().
                            # NOT TOUCHED, each for a stated reason: the polis-vault cage
                            # (R-240's trim there IS what Will asked for, and its post-trim
                            # volume is what gate_loot_distribution's D7X2 anchor is derived
                            # from - so that anchor stays valid), every orb table (R-242,
                            # frozen apex), the Devourer's stash (R-247.7a owns it), and
                            # COMPOSITION anywhere (R-180/R-181/R-220).
                            # Standalone: py tools/gate_uber_hoard_generosity.py <arz>
                            # (--calibrate); negatives: py tools/debug/negtest_uber_hoards.py
    'toxeus_boss_equipment',  # R-252 (Will 2026-08-14, THREE reports in one sitting, one
                            # boss family, one system): "toxeus the murderer the endless hunt
                            # is not wearing any equipment and i dont think he has a weapon" +
                            # "toxeus the murderer devourer of blood is using a bow which makes
                            # no sense" + "i killed toxeus the murderer devourer of blood and he
                            # did not drop his soul even though he should have 100% chance".
                            # MEASURED: a base-game census (5,556 records whose templateName
                            # BASENAME is Monster.tpl, one tick per record per class its hand
                            # can yield, references resolved
                            # CASE-INSENSITIVELY) proves LeftHand is the shield /
                            # two-handed-ranged slot (Shield 0-to-805, Bow 17-to-514, Staff
                            # 17-to-710) and RightHand the one-handed melee slot (Spear
                            # 493-to-0). Two of those are absolute zeros; the Bow/Staff 17 are
                            # ONE shared set of hand-less monsters (tombrot / creeping slime /
                            # earth elemental) using lootRightHandItem1 as a generic drop chute,
                            # i.e. the very anti-pattern this lane removes. ROUND-3: the census
                            # published at rounds 1-2 (Bow 0-to-49, Shield 0-to-144, Spear
                            # 122-to-0) was this module's own exact-case has_record() bug and is
                            # RETRACTED - see the module docstring. ROUND-4: the DENOMINATOR
                            # published at rounds 1-3 (6,085) was templateName.endswith(
                            # monster.tpl), which also counts 529 ControllerMonster /
                            # SpawnMonster / ControllerStationaryMonster records that are not
                            # monsters and carry no chanceToEquip fields; 5556 + 529 = 6085 and
                            # every per-class tally re-derives EXACTLY as published.
                            # So the Devourer's LeftHand pool bleed_affix_high_{n,l},
                            # which contains a BOW, is exactly an archer wiring, and the Hunt
                            # simply has NO lootTorso/LowerBody/Forearm fields at all with four
                            # more slots at chance 0. Writes: the Devourer's two hand slots (the
                            # weapon hand goes MELEE-ONLY behind a NEW guaranteed veinrender
                            # table, the off hand gets the shield array plus the 4-piece set's
                            # only drop row) and both Hunt records' three armour slots + four
                            # family chances. The gate measures the resulting rolls, so the
                            # player-facing claim cannot drift: armed 100.00%, Vein Render
                            # 72.46%, shield 86.23% (shipped: 36.97 / 21.01 / 15.97).
                            # DISCLOSED BALANCE DELTA, pinned by gate arm E2d: moving the
                            # 4-piece set table out of the weapon hand @100 into the off hand
                            # @19 takes each of the three WORN Crimson Verdict pieces from
                            # 21.0084% to 3.4420% per kill, and that table is their ONLY drop
                            # path in the whole db - a 6.1x farm slowdown on hand-designed
                            # content. E2d is TWO-SIDED against _CRIMSON_MEMBER_PCT and sums
                            # over EVERY slot of the record, so neither a further dilution nor
                            # a later RESTORATION can move the rate without moving the four
                            # documents that publish it. Awaiting Will: BL-R252-DEBT-7, which
                            # costs all three restoration options (Misc2 cannot reach 21% at
                            # any weight; Misc4 can, but only by cutting the rant scroll and
                            # the EoAT formula to 7.99% each).
                            # ORDER IS LOAD-BEARING: this must be the LAST writer of these equip
                            # fields, so it runs after EVERY other writer of the two records
                            # (toxeus_hunt_encounter, enslaver_shroud, devourer_kit,
                            # r247_boss_forms, toxeus_hunt_endless, champion_mesh,
                            # toxeus_champion_kits, r247_bloodcave_rulings); apply() FAILS LOUD
                            # on any pre-state it did not measure. Writes NO 'controller' field
                            # (the R-250 enslaver_shroud lane owns that on the Toxeus roster)
                            # and NO chanceToEquipFinger2 (R-243's pin is asserted only, so
                            # verify_soul_drop_rates stays green by construction).
                            # EVERY gate arm resolves record references CASE-INSENSITIVELY and
                            # compares class stems CASE-FOLDED, so a violating row cannot hide
                            # behind a mixed-case reference (2,436 of those resolve only
                            # case-insensitively in the shipped arz) and a legitimate item
                            # spelled with a lowercase template stem cannot red the build.
                            # Standalone twin: py tools/gate_toxeus_boss_equipment.py [arz]
                            # Negative test: py tools/patches/toxeus_boss_equipment.py --negtest
                            # RULING RENUMBERED AT INTEGRATION (R-251 -> R-252): the lane
                            # authored itself R-251 off 0ea001a/build92 while
                            # fix/chest-generosity-shared-cause shipped a DIFFERENT R-251 (the
                            # uber/boss chest generosity) to Steam as build95. The shipped
                            # number wins; this ruling and its debts are R-252 /
                            # BL-R252-DEBT-1..7 everywhere. Same treatment as R-231 -> R-244
                            # (build88) and R-250 -> R-251 (build95). No content changed.
    'visuals',              # build37: DB precondition invariant (writes nothing) - keep LAST
]


def registry_order_hash(names):
    """Stable content+ORDER hash of a manifest (S4a). Logged and asserted so a
    silent reordering or duplication of REGISTRY is caught at build time."""
    h = hashlib.sha256()
    for n in names:
        h.update(n.encode('utf-8'))
        h.update(b'\x00')
    return h.hexdigest()


class _TrackingModifiedSet(set):
    """Drop-in replacement for ArzDatabase._modified used ONLY while registry
    modules run.

    Why not a plain before/after set delta? `_modified` is a monotonic set:
    once module A adds record X, module B re-writing X is a set no-op, so a
    naive `after - before` for B would MISS the collision. This subclass logs
    EVERY `.add(name)` call against the currently-active module, so the
    collision gate (S4b) sees re-modifications. Only `.add` is instrumented;
    every other set operation (discard/remove/__contains__/iter) keeps stock
    set semantics, so downstream code (write_arz's `name in _modified`) is
    unaffected. After the registry runs, db._modified is restored to a plain
    set with identical membership.
    """

    def __init__(self, iterable=()):
        super().__init__(iterable)
        self._touch_log = []          # list[(module_name, record_name)]
        self._active_module = None    # set by run_registry around each apply()

    def add(self, item):
        if self._active_module is not None:
            self._touch_log.append((self._active_module, item))
        super().add(item)


def _load_module(name):
    """Import tools/patches/<name>.py and validate the module contract.
    Fail-loud (SystemExit) on any violation - a malformed module never ships."""
    try:
        mod = importlib.import_module('%s.%s' % (__name__, name))
    except Exception as e:
        raise SystemExit(
            "patches-registry: REGISTRY entry '%s' failed to import "
            "(tools/patches/%s.py): %r" % (name, name, e))
    module_name = getattr(mod, 'MODULE_NAME', None)
    apply_fn = getattr(mod, 'apply', None)
    if not isinstance(module_name, str) or not module_name.strip():
        raise SystemExit(
            "patches-registry: module '%s' must define a non-empty MODULE_NAME "
            "str (contract violation)" % name)
    if not callable(apply_fn):
        raise SystemExit(
            "patches-registry: module '%s' must define a callable "
            "apply(db, tags) (contract violation)" % name)
    return mod, module_name, apply_fn


def _collisions(per_module):
    """Given {module_name: set(items)} return {item: [modules...]} for every
    item claimed by 2+ modules, sorted for stable output."""
    owners = {}
    for module_name, items in per_module.items():
        for it in items:
            owners.setdefault(it, []).append(module_name)
    return {it: ms for it, ms in owners.items() if len(ms) >= 2}


def _warn_collisions(kind, per_module):
    coll = _collisions(per_module)
    if not coll:
        print("  collision gate (%s): none written by 2+ modules (clean)" % kind)
        return
    print("  WARNING collision gate (%s): %d %s written by 2+ modules "
          "(LATER module wins - legal registry semantics - but is never "
          "silent):" % (kind, len(coll), kind))
    for it in sorted(coll):
        print("    %s  <-  %s" % (it, ', '.join(coll[it])))


def run_registry(db, tags, registry=None):
    """Run every REGISTRY module in manifest order over the shared db/tags,
    then the fail-loud coherency gates. Returns the list of executed names.

    Contract for each module: see this package's docstring / README.md.

    Called by build_svc_database.py AFTER
    apply_all_extended_patches(db, ..., _defer_gates=True) and BEFORE
    apply_svc_patches.run_registry_gates(db, tags, ...), so the monolith's gate
    battery validates the final assembled db (monolith + every module).

    Coherency gates:
      S4a registry-integrity - no duplicate entries; every entry runs exactly
          once, in manifest order (order hash logged + asserted).
      S4b module-collision WARN - after each module, log the records + tags it
          touched; if two modules write the SAME record (or tag), WARN naming
          both (later-wins is legal, but must be VISIBLE, never silent).

    With an EMPTY registry this does not touch db or db._modified at all, so the
    build is byte-identical to the pre-registry build (README S5 identity proof).
    """
    names = list(REGISTRY if registry is None else registry)
    order_hash = registry_order_hash(names)
    print("\n" + "=" * 70)
    print("=== patches-registry: %d module(s), order %s ==="
          % (len(names), order_hash[:12]))
    print("=" * 70)

    # S4a (pre): no duplicate manifest entries.
    if len(set(names)) != len(names):
        seen = set()
        dups = sorted({n for n in names if (n in seen) or seen.add(n)})
        raise SystemExit(
            "patches-registry integrity: REGISTRY has duplicate entries %s; "
            "each module must appear exactly once" % dups)

    if not names:
        print("  (registry empty - no content modules; identity-proof build)")
        print("=" * 70)
        return []

    # Instrument db._modified ONLY while modules run (see _TrackingModifiedSet).
    orig_modified = db._modified
    tracker = _TrackingModifiedSet(orig_modified)
    db._modified = tracker

    per_module_records = {}    # module_name -> set(record_name)
    per_module_tags = {}       # module_name -> set(tag_key)
    executed = []
    try:
        for idx, name in enumerate(names, 1):
            mod, module_name, apply_fn = _load_module(name)
            before_tags = dict(tags)
            mark = len(tracker._touch_log)
            print("\n--- [%d/%d] %s  (%s) ---" % (idx, len(names), name, module_name))
            tracker._active_module = name
            apply_fn(db, tags)
            tracker._active_module = None
            recs = {r for _m, r in tracker._touch_log[mark:]}
            tag_delta = {k for k in tags
                         if (k not in before_tags) or (tags[k] != before_tags[k])}
            per_module_records[name] = recs
            per_module_tags[name] = tag_delta
            print("    %s: modified %d record(s), %d tag(s)"
                  % (name, len(recs), len(tag_delta)))
            executed.append(name)
    finally:
        tracker._active_module = None
        # PERSIST the per-module touch log for the POST-FINALIZATION gates
        # (BL-R181-DEBT-7). The tracker itself must go - downstream consumers need
        # stock set semantics - but "which module wrote this record" is the only
        # evidence that can answer the ownership question, and the gates that ask it
        # run in run_registry_verifies(), long after this finally block. A list of
        # (module, record) pairs, read-only by contract; consumers that find the
        # attribute missing must ANNOUNCE the downgrade rather than pass quietly
        # (see svc_armor_breadth.ownership_problems).
        db._registry_touch_log = list(tracker._touch_log)
        # Restore a plain set with identical membership so all downstream
        # consumers (write_arz, the container-shape gate) see stock semantics.
        db._modified = set(tracker)

    # S4a (post): every entry ran exactly once, in manifest order.
    if executed != names:
        raise SystemExit(
            "patches-registry integrity: executed order %s != manifest order %s "
            "(a module must run exactly once, in order)" % (executed, names))
    if registry_order_hash(executed) != order_hash:
        raise SystemExit(
            "patches-registry integrity: post-run order hash mismatch "
            "(manifest mutated mid-run?)")

    # S4b: cross-module collisions (records AND tags).
    _warn_collisions("record(s)", per_module_records)
    _warn_collisions("tag(s)", per_module_tags)

    print("\n=== patches-registry: %d module(s) OK, order %s ==="
          % (len(executed), order_hash[:12]))
    print("=" * 70)
    return executed


def run_registry_verifies(db, tags, registry=None):
    """POST-FINALIZATION verify phase (step 4; see this package's EXECUTION ORDER).

    Call each REGISTRY module's OPTIONAL `verify(db, tags)` hook, in manifest
    order, AFTER apply_svc_patches.run_registry_gates has finalized the db (the
    Ground Smash de-filler, the wave29 placeholder-tag renames, the soul-naming
    standard, the MP-equation fix). A module puts here any roster/diversity/
    coherency check that MUST see the FINAL assembled db - a check that would
    trip on transient ordering artifacts if it ran at apply() time (step 2),
    mid-registry, before the finalization clears them.

    Fail-loud by construction: a module verify() raising SystemExit propagates
    and aborts the build (exactly like an apply()-time gate would). This is the
    ONLY thing that keeps the relocated gate live - a module that moves its gate
    out of apply() and into verify() is disabled UNLESS this phase runs, so
    build_svc_database.py MUST call it after run_registry_gates.

    Modules with no `verify` attribute (or a non-callable one) are skipped.
    Returns the list of module names whose verify() actually ran.
    """
    names = list(REGISTRY if registry is None else registry)
    print("\n" + "=" * 70)
    print("=== patches-registry: post-finalization verify() hooks ===")
    print("=" * 70)
    ran = []
    for name in names:
        mod, module_name, _apply_fn = _load_module(name)
        verify_fn = getattr(mod, 'verify', None)
        if not callable(verify_fn):
            continue
        print("  verify [%s] (%s) ..." % (name, module_name))
        verify_fn(db, tags)
        ran.append(name)
    if not ran:
        print("  (no registry module defines a verify() hook)")
    else:
        print("  verify hooks OK: %s" % ", ".join(ran))
    print("=" * 70)
    return ran


def selfcheck():
    """Cheap CI check (no DB build): validate that every REGISTRY module imports
    and satisfies the contract, and that the manifest has no duplicates. Prints
    the order hash. Returns 0 on success, raises SystemExit on any violation.

    Run it with: py tools/patches/_check_registry.py
    """
    names = list(REGISTRY)
    if len(set(names)) != len(names):
        raise SystemExit("patches-registry selfcheck FAIL: REGISTRY has "
                         "duplicate entries")
    for n in names:
        _load_module(n)   # fail-loud on any contract violation
    print("patches-registry selfcheck OK: %d module(s), order %s"
          % (len(names), registry_order_hash(names)))
    return 0
