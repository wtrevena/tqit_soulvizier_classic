# WILL RULINGS LEDGER (append-only; THE design law of record)

> **LAW (2026-07-16):** Every implementer brief MUST check this ledger for the domain it touches
> before changing anything. Every vet MUST check the change against it. Nothing here is ever
> silently dropped: a ruling is either IMPLEMENTED (with the build number), PENDING (with the
> owning lane), or SUPERSEDED (by a later ruling, linked). Retiring/deleting any record requires
> checking this ledger for design intent naming it - "unreferenced in code" is NOT sufficient.
> Quote rulings VERBATIM. Newest at the bottom of each section. Historical backfill from wave
> reports: see the backfill entries appended by the b84 sweep.

## Format
`R-<n> [date] [status: IMPLEMENTED bNN / PENDING (lane) / SUPERSEDED by R-m] "verbatim ruling" - context/notes`

## Toxeus arc
- R-1 [2026-07-14] IMPLEMENTED b41, RE-BROKEN, RESTORING (fix/bloodtoxeus-spawns) "For the 33% toxeus devouer of blood parchment room spawn feature, make sure he spawns with all his guys" - the entourage requirement; dropped when the parchment feature was retired and the solo ambush was kept. STANDING: any Blood-Toxeus 33% encounter spawns WITH the pack.
- R-2 [2026-07-14] IMPLEMENTED b41 "yes we can keep 33% chance of toxeus, devourer of blood in the parchment room" - one 33% roll, no double-spawn.
- R-3 [pre-b41, STANDING] IMPLEMENTED b91 (fix/devourer-chest) Blood Toxeus spawns next to the blood-cave hidden chest 100% of the time - the chest encounter is deliberately adjacent-to-chest (exempt from generic clearance). CAUSE CORRECTED TWICE: the ruling's own hypothesis (the q_bloodtoxeus_lone_50 "orphan" retirement / placement loss) was disproven in b79 - the placement and the whole chain were always intact; b79's replacement hypothesis (championMin=0 on the egg pool) shipped and STILL did not spawn (Will re-reported 2026-07-27, R-49). CAUSE (b91) - stated at the confidence the evidence supports, NOT as a proven mechanism: TWO defects were found against the deployed bytes and BOTH were fixed. (a) MECHANICALLY SUFFICIENT ON ITS OWN: the guard proxy carried the area-trash difficultyLimitsFile limit_area002 (N[23-26]/E[38-51]/L[60-65]), a level window that EXCLUDES his charLevel [40,68,100] on every difficulty - docs/BLOOD_TOXEUS_DESIGN.md already mandates limit_bloodtoxeus on every proxy that spawns him. This alone can suppress the spawn and is the leading explanation. (b) SHAPE, by precedent not mechanism: he occupied the pool's CHAMPION slot. Census (numbers below are the VET's independently reproduced figures; the implementer's first-pass counts did NOT reproduce and were wrong): of 1845 shipped ProxyPools, 624 put a Boss in a MAIN nameN slot and 494 put one in a nameChampionN slot (41 of those with championMin>=1). The LOAD-BEARING fact does reproduce exactly: 28 pools make a Boss the sole champion entry and EXACTLY ONE (egg_blooddragon) also carries championMin>=1 - a shape with zero precedent in 51,085 records. ⚠️ HONEST RESIDUAL: under this repo's own documented championChance/championMin semantics the OLD shape should have produced him 100% of the time, and b91 does NOT explain why it did not. The fix therefore rests on defect (a) plus moving him to the empirically-universal guaranteed-boss construction, not on a proven champion-slot mechanism. If he still fails to appear on a FRESH visit, defect (a) was not it either and the remaining unknown is the champion-slot semantics themselves. FIX: name1..3 = um_bloodtoxeus_99 (MAIN), the native blood dragons moved to nameChampion1..3, championMin=championMax=3 with spawnMax=4 -> exactly 1 Devourer + 3 dragons every run at 1..6P; proxy repointed to limit_bloodtoxeus [1..110]; the chest guard REGISTERED in _MOD_AUTHORED_SPAWN_PROXIES and gated forever by the new whole-chain contract MAP-CHESTGUARD-1. docs/reports/b91_devourer_chest_spawn.md.
- R-49 [2026-07-27] IMPLEMENTED b91 (fix/devourer-chest) "toxeus the murderer devourer of blood is not spawning at the proper location next to his chest in the blood cave even though we said he should have a 100% spawn rate there in the existing spawn pool that is there" - the REPEAT of R-3. "the existing spawn pool that is there" is honoured literally: the fix stays inside the native egg_blooddragon pool on the native egg_blooddragon_pack proxy 4.2u from the chest; no new record, no new placement, same 1 Devourer + 3 blood dragons.
- R-4 [2026-07-16] PENDING (fix/bloodtoxeus-spawns) quest rename "Toxeus the Murderer, Devourer of Blood's Stash"; chest rename "Toxeus the Murderer, Devourer of Blood's Hidden Chest" (was Esti's Hidden Chest).
- R-5 [2026-07-16] IMPLEMENTED feat/toxeus-champions (b73) "the blood toxeus should have the Tears of Blood ability granted by the Arcane Formula - Blood of Ares" + "The toxeus devourer of blood should have maybe a 10 second cool down on a weaker version" - NOTE ground truth: corridor + deep boss share ONE record; both currently weak-10s; full-strength corridor variant = OPEN Will decision.
- R-6 [2026-07-16] IMPLEMENTED feat/toxeus-champions (b73) Enslaver + Devourer get unique identity kits ("his abilities are pretty generic") - Soul-Rip / Chains of Servitude / Unholy Dominion; Blood Frenzy. Per-ability veto open on DEV.
- R-7 [2026-07-16] IMPLEMENTED b83 (feat/black-poison, merged to main in the BUILD47 GATE RECORD 2026-07-17) "we have wanted the devourer to have a literal black poison asset from the beginning and use that all along" - CREATE svc_black_poison; it is the Devourer's poison AND End of All Things' strike buff. Colors may only be claimed from in-game-confirmed assets. Owner: `tools/patches/black_poison.py` (registry module, runs after toxeus_champion_kits and before toxeus_endofallthings, whose `_BLACK_POISON` const names it); verify() asserts `buffSelfSkillName` on all 3 Devourer soul-pets and fails on crimson OR base-green. See `docs/reports/b83_black_poison_rite_drop.md`.
- R-8 [2026-07-16] IMPLEMENTED feat/toxeus-undivided (b72) End of All Things: name "Toxeus the Murderer, End of All Things"; ring "Soul of Toxeus, End of All Things"; formula demands LEGENDARY tier of the 3 Toxeus souls; 11-item kit per verbatim rulings (unlimited energy; NetherStrike max 0.5s; max SmokeScreen; max Galefury-granted skill; Tears of Blood 3s; Murderer's Edge + black poison (R-7); Entropy aura; Blood Feast; thralls = blood-cave tall casters w/ bloodhounds; The Ending w/ Light-of-Helios flash visual; Arrat the Corruptor AOE); ash-pale body + per-skill fragment colors; stronger than every Toxeus champion.
- R-9 [2026-07-16] IMPLEMENTED b83 (feat/black-poison, merged to main in the BUILD47 GATE RECORD 2026-07-17) "let the Rite of the Undivided drop wherever else any supra / uber weapons formulas have a chance to drop" - the Rite is wired into BOTH `arcaneformulae\supra.dbr` and `supra_special.dbr` (the same two pools the b66 uber_orphan_weapons module wires every new supra formula into), so it drops wherever ANY supra weapon formula drops, at that same rarest tier. See `docs/reports/b83_black_poison_rite_drop.md`.
- R-13 [2026-07-16] IMPLEMENTED b83 (feat/black-poison, merged to main in the BUILD47 GATE RECORD 2026-07-17) "also make it so if you kill either toxeus the devourer of blood of toxeus the enslaver of souls you also get the formula" - Rite of the Undivided ALSO drops on killing the Devourer OR the Enslaver (read as guaranteed on-kill; implementer flags if convention argues for a chance instead). Extends R-9 (both sources coexist). Shipped via `svc_rite_guaranteed` (FixedWeight 100% Rite) folded into each champion's Misc4 master table, leaving the Finger2 soul drop and the rant-scroll slot undisturbed. See `docs/reports/b83_black_poison_rite_drop.md`.
- R-10 [2026-07-16] IMPLEMENTED fix/runtime-green (b75) + PENDING follow-up: Enslaver summon = BLACK (steal the marauders' shadowcloak smoke). Diadochi generals + Helepolis share the green-rendering 343_dark_smoke - swap after Will confirms the Enslaver reads black.
- R-11 [2026-07-16] IMPLEMENTED b81 (fix/runtime-green pet-identity commit, merged to main in the BUILD47 GATE RECORD 2026-07-17; `docs/reports/b81_pet_identity.md` closes with the explicit instruction "whoever integrates this branch should mark R-11" - done here) "Toxeus the murderer, enslaver of souls is a beastman not a skeleton" - Enslaver family race = skeleton/Undead; all boss-summon pets inherit race/sounds/distress from their SOURCE monster.
- R-12 [2026-07-16] IMPLEMENTED b71 skeleton identity: Enslaver summon-skill icon + pet-bar portrait = one consistent skeleton (deathwalker) identity; marauders do NOT show in the pet bar (no portrait requirement).

## Masteries
- R-20 [2026-07-16] IMPLEMENTED b44/b45 revert + SV alignment: trees match SV ground truth; Will's hand-tuned overlays preserved; shapes = isCircular per SV (PoisonousGas circle; BladeFury, SmokeScreen squares).
- R-21 [2026-07-16] IMPLEMENTED b70 "Hunting eviscerate should be a square".
- R-22 [2026-07-16] IMPLEMENTED b70 (C2) col6 restack verbatim: "lets have darklings be in the same lane as throwing knife, but we will have darklings unlock at 10, dark aperture unlock at 16, and then above it we will have throwing knife at 24 and the augment to throwing knife at 32 so we wont have lines behind one another".
- R-23 [2026-07-16] IMPLEMENTED feat/mastery-sv-fix "so how does dark invigoration work? I think it should augment shadow link" - genuinely augments via SkillTree slot order (proven mechanism); NEVER reorder skillName{N} slots (binding surface).
- R-24 [2026-07-16] IMPLEMENTED b77 (fix/mastery-unlock, merged to main in the BUILD47 GATE RECORD 2026-07-17) "Proceed with fixing the masteries as appropriate" - b74 audit implementation: every button's real unlock == its drawn row (Warfare col3 + Earth col4 ladders as WILL-VETO). Owner: `tools/patches/mastery_unlock_alignment.py` (m1/m2/m3/m4/m7 only; registered LAST among mastery-UI writers; m5/m6 golden untouched so A7 stays green). RESIDUAL, NOT a status blocker: the WILL-VETO ladder designs in `docs/reports/b77_unlock_alignment_fix.md` sec 2 still await Will's DEV pass - they are shipped defaults, vetoable in place.
- R-25 [2026-07-16] STANDING Darklings/DarkAperture/ToxicConcoction/ShadowStalker are PRE-0.98i SV content ("I did not create these by hand") - their canonical layout authority = SV 0.9/0.41 extractions.

## World / placement
- R-30 [2026-07-16] PENDING (fix/chumbi-lag; STATUS RE-VERIFIED 2026-07-28: `fix/chumbi-lag` IS merged to main via the BUILD46 GATE RECORD, but build46 shipped only b76 round 1 [yard removal + summon TTLs] and its own DEBT line still names "placement spacing/clearance gate follow-through" - the permanent SPACING-LAW gate this ruling demands is NOT built, so PENDING stands) verbatim: "you need to space these monsters out instead of putting them all on top of one another" + fountain death-loop = never again: SPACING LAW (fountain/NPC clearance + min inter-encounter distance, permanent placement gate).
- R-31 [2026-07-16] PARTIALLY IMPLEMENTED b46, REMAINDER PENDING (fix/chumbi-lag) boss pileup unstacked to intended locations; the summon issue is CO-PRIMARY ("both are making the game freeze"): tomb-guardian dogs hard-capped + TTL, sepulcher fight playable standing alone.
  - **STATUS 2026-07-28 (branch `fix/debt-gate`, B76-R2-SUMMON-GATE):** the *summon-cap* half is IMPLEMENTED and now **GATED**. b46 restored the finite `spawnObjectsTimeToLive` on the sepulcher/tomb-guardian chain (`tools/patches/summon_caps.py` `_TTL_TARGETS`: tomb guardians 5.0s per SV's own shodema value, alastor skeleton warrior/archer + the recursive `summonpet_undeadmelee01` 20.0s per the four_generals precedent). As of today `summon_caps.verify()` additionally enforces the whole CLASS - no unbounded fast summoner (`Skill_*SpawnPet*` with no petLimit, no TTL, cooldown < 10s) may enter the arz outside an evidenced waiver of 8 base/dead/test records - so a NEW freeze-class summoner can no longer ship unnoticed. Deliberately NOT a blanket petLimit-no-TTL rule (~140 healthy skills have that shape). Planted negative test: `py tools/patches/summon_caps.py --negtest`.
  - **STILL PENDING (do not read the above as R-31 closed):** (a) the *boss pileup* half - unstacking the piled bosses to their intended locations (the b46 Monster Test Yard removal addressed the TESTHUB QA cluster, not the general SPACING LAW of R-30); (b) "sepulcher fight playable standing alone" is a RUNTIME judgement only Will's in-game pass can settle. The ⚠️ WILL-VETO on the exact TTL seconds also stands - the fix is the PRESENCE of a finite TTL, not the value.
  - **STATUS RE-VERIFIED 2026-07-28 (branch `fix/debt-docs`):** b76/build46 DID land both halves in code - the TESTHUB Monster Test Yard was removed [HV01 now == canonical] and the sepulcher-chain summon TTLs were restored via `tools/patches/summon_caps.py` - but "sepulcher fight playable standing alone" is an IN-GAME claim nobody has confirmed, and build46 disclosed a side effect Will may veto [base Aktaios + Alastor minions now despawn]. Kept PENDING on Will's confirmation, not on missing code
  - **STATUS 2026-07-28 (branch `fix/debt-tooling`):** the b76 HiddenValley01 Monster Test Yard removal now has a PERMANENT REGRESSION GUARD - `tools/debug/gate_build32_parseback.py --testhub` asserts the TESTHUB HiddenValley01 blob is byte-identical to canonical, so the yard cannot silently come back. This does NOT implement R-30's spacing law or R-31's summon caps; both stay PENDING.
- R-32 [2026-07-16] PENDING (fix/chumbi-lag; STATUS RE-VERIFIED 2026-07-28: nothing in the b76/build46 contents addresses the widow-quest Dead Adventurer's Chest reuse - genuinely unbuilt) boss reward containers are NEVER quest-gated chests (the widow-quest Dead Adventurer's Chest reuse).

## Souls & items
- R-40 [2026-07-16] IMPLEMENTED b78 (fix/soul-tiers, merged to main in the BUILD47 GATE RECORD 2026-07-17) souls scale across normal/epic/legendary (Blood Cult High Priest epic == normal = the defect class); strict-progress gate. OUTCOME: the roster-wide sweep found **0 flat-tier families / 0 wrong-tier loot triples / 0 real missing tiers** - Will's specific observation was a save-bake + shared-name perception artifact, so the wave made NO data change. The deliverable is the permanent strict-progress gate that closes the blind spot (a genuinely-flat epic now fails the build). See `docs/reports/b78_soul_tier_scaling.md`.
- R-41 [2026-07-16] IMPLEMENTED b80 (fix/formula-names, merged to main in the BUILD47 GATE RECORD 2026-07-17) formula display names match what they craft ("Mythic Formula - Crystalline Mask" crafts Galefury) - fixed by repointing `ar_hunter_helm_formula.dbr`'s description onto SV098i's own already-correct, previously-orphaned `tagRecipe_ar_helm_fix`; full 245-formula sweep found no other instance; permanent gate added (`tools/patches/formula_names.py` verify() + `tools/validate_formula_names.py`). See `docs/reports/b80_formula_names.md`.
- R-42 [earlier, STANDING - PARTIALLY SUPERSEDED by R-48 (2026-07-27) for the two fought Toxeus champions ONLY; every other record's rate stands unchanged] Munderizer over-band damage BLESSED; Shadow Link large radius KEPT; legion terminal drop 66 fine for now (revisit next souls pass); soul drop rates: random 50 / placed 66 / boss 25.
  - **R-42 FOLD-IN: IMPLEMENTED b91 (fix/debt-db, 2026-07-28).** The queued half of R-42 - Will
    2026-07-16 post-build42, verbatim: *"LEGION TERMINAL @66: fine for now. QUEUED: fold 'death-
    transform terminals of RANDOM chains inherit the 50 rate' into the NEXT SOULS PASS"* - is now
    built. Fixed UPSTREAM in the shared classifier, not per record:
    `build_svc_database.soul_spawn_provenance_sets()` closes BOTH membership sets forward over the
    `actorToSpawnOnDeath` graph (`_soul_transform_edges` + `_propagate_transform_provenance`), so a
    death-transform stage inherits its chain HEAD's spawn provenance instead of falling through
    `soul_drop_rate()`'s "not proven to spawn randomly -> keep the PLACED rate" safe-default. Fixing
    it at the provenance source is the b59 `boss_charon_39` lesson: `_soul_release_rate()`,
    `wire_souls_to_monsters()` and `create_uber_souls.py` all route through these sets, so no caller
    can bypass it. Propagation is FORWARD-ONLY and `placed_proxy_members` is still checked before
    `random_pool_members`, so a PLACED chain's terminal can never be over-cut. **Roster-wide proof:
    exactly 2 LIVE movers** - `um_legion_28c` (Will's named case) and `um_possessedboar_spirit`
    (the only sibling; `double_soul_rulings` deliberately keeps it as the surviving dropper), both
    66 -> 50, both terminals of RANDOM chains. 7 other classifier verdicts move but are inert
    (`chanceToEquipFinger2 = 0`). PLACED-chain terminals `um_charonform2_ferryman_99` /
    `um_polisgaoler_unbound_99` / `um_tantalus_unbound_99` correctly stay 66 - now for the right
    reason instead of by fall-through. The R-48 100% carve-outs are untouched (both Boss-class, off
    this graph, and `toxeus_souls_100` remains the final writer). Gated in
    `tools/verify_soul_drop_rates.py` (updated spot tests + the PLACED never-over-cut negative half
    + a planted-regression test that goes red if the closure is deleted). See
    `docs/reports/b91_debt_db.md` sec 4.
- R-43 [2026-07-16] IMPLEMENTED b85 (fix/soul-tiers, MERGED to main in the BUILD47 GATE RECORD 2026-07-17 - the earlier "pending merge" qualifier is now stale) "the high priest soul should allow you to summon the high priest" - the Blood Cult High Priest soul's summon = the HIGH PRIEST himself (his identity/mesh/kit as the pet, all 3 tiers scaled), per boss-summon conventions + the b71/b81 identity laws (icon/portrait/race/sounds = High Priest). Companion check: epic soul must spawn the epic-tier pet (verified true roster-wide in b78, re-proven for this family).

- R-51 [2026-07-27] IMPLEMENTED-NOT-YET-SHIPPED b95 (feat/sargath-soul) "backlog item sargath manbane soul should let you summon him" - FOLLOWS THE R-43 PRECEDENT exactly (same ruling class, same SECOND-BUILDER pattern, same shared chain gate). IDENTIFICATION (proven, not guessed - the record name contains no "Sargoth", which is why the backlog item never matched a grep): "Sargath" is Will's near-spelling of the shipped display string **"Sargoth Manbane"** = `tagMonsterName1138` in the shipped Text.arc; the ONLY record in the 51,085-record deployed arz carrying that tag as its `description` is `records\creature\monster\dragonian\hero_tarthon_na'arak_37.dbr` (Hero, race Beastman, charLevel [37,54,69] = the three difficulty tiers IN ONE record, so there are no separate variant records; Dragonian01.msh / MageB.tex / anm_dragonian; a lightning mage - Lightning Ball, Thunderball + Concussive Blast, lightning-bonus aura, drxenergyshield_aoe). Placement: the `nameChampion7` slot of 9 Orient/Act-3 dragonian pools (`records\proxies orient\pools\beastman\dragonian_0{2,3}_{melee,ranged}0{1,2,3}`) - a roaming Orient hero, not a placed unique. His soul family is the SV-ORIGINAL `records\item\equipmentring\soul\dragonian\sargoth_soul_{n,e,l}.dbr` (`tagSoulName297` = "{^F}Sargoth Manbane Soul"), wired as his `lootFinger2Item1` at `chanceToEquipFinger2` 50.0. BEFORE STATE (premise CONFIRMED): all three tiers had **NO `itemSkillName` at all** - the soul granted no skill of any kind, only stats + two augments (`stafftraining` 5/6/7, `drxthunderball_concussiveblast` 2/3/4); it never summoned anything. FIX: new registry module `tools/patches/sargoth_soul_summon.py` builds `pets\sargoth_{1,2,3}` + `summon_sargoth` from his OWN rig via `_build_boss_summon` (the R-43 builder: Lyia Pet.tpl baseline, anim+skill refs only, strict source gear mirror, permanent/no-TTL) and wires `itemSkillName`/`itemSkillLevel` 1/2/3 onto all three tiers, manual-cast (no `itemSkillAutoController`, the R-44 convention + the Lyia model). Player surfaces all covered per CLAUDE.md law #3: name `tagSVCSummonSargoth` = "Summon Sargoth Manbane"; icon = thunderorb up/down (arc-verified, unclaimed, deliberately NOT sibling Vort's Thunderball icon); pet-bar portrait = neutral `proxy_party` (NO dragonian `*_party_` art ships anywhere - 34 swept - same convention as the Hades Marshal and R-43's High Priest; never the Lyia nymph); pet name = `tagMonsterName1138`; race Beastman + voice/distress paks inherited from the source (R-11); gear = his own LeftHand staff with every unused slot zeroed; kit + mobility mirrored (D19 row 'sHanded' is covered by `anm_dragonian`). Closest shipped precedent is his own SIBLING record: Vort the Red (`hero_tarthon_na'arak_40`, `tagMonsterName1139`) already ships this exact summon shape. GATE: added as a leg of the EXISTING shared chain gate `tools/patches/enslaver_pet_fx.py` `_CHAIN` (the one that already carries R-43), asserting item -> skill -> icon -> spawnObjects -> pet -> portrait, plus a planted negative test `tools/patches/_negtest_sargoth_chain.py`; the module's own `verify()` adds the per-tier grant + 1/2/3 strict-progress leg (R-40). ⚠️ STATUS IS **NOT SHIPPED**: the code is committed on `feat/sargath-soul` but was NOT built, NOT gated and NOT deployed - the DEV deploy target was overwritten mid-session by the concurrent `fix/green-diff` lane (b92, `60d7789`), so the brief's ground-truth anchor went stale and deploying a `main`-based build would have silently reverted that lane. Awaiting Will's sequencing decision. See docs/reports/b95_sargath_soul_summon.md.

## Process (meta-rulings)
- R-50 [2026-07-16] "what do you need to do to manage your tasks better so we dont end up with stuff like this happening over and over" -> THIS LEDGER + retirement protocol + player-surface checklist + no-new-surface-without-a-gate + debt register. See CLAUDE.md standing rules.

---

## HISTORICAL BACKFILL (b84 sweep, round 1, 2026-07-16) - see docs/BACKLOG.md DEBT REGISTER for the
## open-item counterpart of this sweep. Numbering continues each section's existing range; sections
## reserve a decade (Toxeus 1-19, Masteries 20-29, World 30-39, Souls 40-49, Process 50-59); new
## topics get a fresh decade (Legal 60-69, Global balance & progression 80-89). **2026-07-28: Souls & items 40-49 is FULL (R-49 was
## claimed 2026-07-27 by the fix/devourer-chest lane) - its OVERFLOW decade is 70-79.**
## **2026-07-28 (b98 Endless Hunt lane): Toxeus arc 1-19 is FULL - its OVERFLOW decade is 90-99
## (R-90..R-96 claimed). Next free Toxeus number: R-97.**
## > ⚠️ **DECADE CORRECTED 2026-07-29 at integration round 2.** The b98 lane first claimed **80-89**
## > and minted R-80..R-86 there, from a base (`a0276ab`) that predates b99. While it was building,
## > the b99 content wave landed on `main` **and deployed**, and b99 had already opened 80-89 as
## > "Global balance & progression" with **R-80 = the death-XP penalty**. Two live R-80s. On the
## > `fix/debt-docs` LEDGER-HYGIENE precedent the INCUMBENT keeps the number, so b99's R-80 and its
## > whole decade stand and this lane's seven rulings moved wholesale, in order, to the next free
## > decade **90-99**: R-80->R-90, R-81->R-91, R-82->R-92, R-83->R-93, R-84->R-94, R-85->R-95,
## > R-86->R-96. Nothing about any ruling's CONTENT changed; the renumber is purely documentary and
## > was proven so by a byte-identical rebuild (see the b98 report, section 14).
## **2026-07-28 b98 ROUND 2 (adversarial vet) allocated NO new numbers on purpose.** Will made no new
## decision; what changed is what round 1 CLAIMED about the decisions he had already made. R-93 and
## R-94 therefore carry marked "ROUND 2" amendment blocks rather than new rulings, so his words stay
## in one place and the correction sits next to the claim it corrects.
## **2026-07-29 b98 ROUND 3 claimed R-96** - the roam RATE ("roughly one sighting per act"), the one
## genuinely NEW Will decision in this lane since round 1. It closes BL-b98-DEBT-5.

### Toxeus arc (continued)
- R-19 [2026-07-14] IMPLEMENTED (M4 MP-compat sweep, feat/toxeus-encounter-suite) Will's call verbatim:
  "we need to retire the one we are adding and just update the 15% one to 33%." Retires the never-wired
  ~50% parchment-room Toxeus feature (`demon_01_cluster_toxeus50` pool+proxy, `q_bloodtoxeus_lone_50`)
  entirely; the sole corridor Blood-Toxeus roll stays the `drxFirstRoom` ambush, `chanceToRun` retuned
  15->33. SUPERSEDES R-14. Source: docs/MULTIPLAYER_COMPAT.md M4.7 item 5; docs/reports/
  toxeus_suite_recon.md sec 0.
  > ⚠️ **ID CORRECTED 2026-07-28** (`fix/debt-docs` ledger-hygiene pass). The b84 backfill filed this
  > as a SECOND `R-13`, colliding with the live Toxeus-arc R-13 (Rite of the Undivided on-kill drop).
  > Renumbered into the next free slot of the Toxeus decade (1-19). The live R-13 keeps its number -
  > a number in use is NEVER reused or reassigned. Nothing about the ruling itself changed.
  > ⚠️ RETIREMENT-PROTOCOL CROSS-REFERENCE: this ruling is the origin of the `q_bloodtoxeus_lone_50`
  > "orphan" retirement that R-3 records as having broken the 100% hidden-chest spawn. Read R-3
  > before acting on this one; the `fix/devourer-chest` lane owns that repair.
- R-14 [2026-07-09] SUPERSEDED by R-19 (2026-07-14; filed by the b84 backfill as "R-13", renumbered
  2026-07-28 - see the ID CORRECTED note on R-19) "put toxeus devourer of blood there too with 50%
  spawn chance" - the original ask for a second parchment-room Toxeus spawn; never wired to the map,
  then explicitly retired. Source: docs/MULTIPLAYER_COMPAT.md M4.7 item 5.
- R-15 [2026-07-14] IMPLEMENTED "you are good to ship the rant scroll" - amgoz1 creative-text veto
  cleared for `{^r}The Murderer's Screed` / `A Parchment Slick with Blood` + the ~180-word rant text
  (Toxeus's voice). Source: docs/MULTIPLAYER_COMPAT.md M4.7 item 6.
- R-16 [2026-07-14] IMPLEMENTED b65, then SUPERSEDED by R-90 (2026-07-28) Legendary-only
  Toxeus stalker via the proven Hydra fixed-placement pattern (`pool1` empty + `poolLegendary1` = boss
  pool) - APPROVED, QUEUED, not built; the already-shipped roaming Endless Hunt (Hades-confined) stays
  as-is alongside it, Will's call whether it is additive or a replacement. Source: docs/
  MULTIPLAYER_COMPAT.md M4.6-M4.7; docs/reports/toxeus_suite_recon.md sec 5.3.
  > ⚠️ **TWO CORRECTIONS, b98 2026-07-28.** (1) STATUS: it WAS built (b65 lowlift wave,
  > `tools/patches/toxeus_legendary_stalker.py` + the `hadespalace_floor04_04` placement); this entry's
  > "not built" was stale. (2) FACT: **"the already-shipped roaming Endless Hunt (Hades-confined)" is
  > WRONG.** The roam was never Hades-confined and never difficulty-gated - `records\xpack\proxieshades\`
  > is the WHOLE Immortal Throne proxy namespace (Rhodes is filed inside it as area001), the sweep
  > reaches 540 proxies across area001..area008, and 365 of them define only `poolN`, which resolves on
  > all three difficulties. The claim came from one mis-annotated constant in `toxeus_suite.py`, now
  > corrected in place. **SUPERSEDED BY R-90:** Will removed the Legendary-only gate from the fixed
  > encounter (it now resolves on N/E/L) and moved "Legendary-only" onto the endless-pursuit BEHAVIOUR
  > instead. The RECORDS keep their names; the module was renamed to `toxeus_hunt_encounter.py` under
  > the retirement protocol.
- R-17 [pre-M4, STANDING] Duplicate rant-scroll drops on repeat Blood-Toxeus kills are ACCEPTED (Will)
  - the per-player Misc4 fallback (corpse/chest with `loottable=toxeus_rant_perplayer`) need not dedupe
  across kills. Source: docs/MULTIPLAYER_COMPAT.md M4.3.
- R-18 [pre-build40, STANDING] "Will forbade a rate change" [paraphrased] on the Enslaver's roaming
  warband encounter frequency - the weight-1/K=600 rarity (~once per several hundred acts) is
  deliberate design; the dependable per-encounter beat is the PLACED warband set-piece, not the roam.
  Do not tighten/loosen without new Will approval. Source: docs/reports/b49_enslaver_rate.md.
  **HONOURED b91 (2026-07-28):** the debt-clearance lane closed BL-ENSLAVER-SPAWNS without touching
  frequency or breadth. Sub-fix (2) "reduce the spawn rate" is CLOSED BY THIS RULING - no action is
  the correct action. (A per-area pool cap was considered and REJECTED for the same reason: cutting
  the 273 swept pools would be a de-facto frequency cut R-18 forbids.)

### Masteries (continued)
- R-26 [2026-07-09] STANDING (binding on ALL mastery work), verbatim: "editing skills is probably
  preferred, but we can add new skills, i just dont want to arbitrarily delete things for cleanliness,
  i want to be very careful about preserving much of the original work and intent of the original
  devs." NEVER REMOVE SKILLS FROM MASTERIES: (1) EDIT existing skill fields = preferred; (2) ADD new
  skills/tree slots = allowed; (3) REMOVE a skill or tree slot = FORBIDDEN without per-item Will
  approval (proposal list only, never a build); (4) re-enabling DISABLED original content = ENCOURAGED;
  (5) dangling-ref field cleanup INSIDE a record = allowed, but treat as (3) if in doubt whether it
  removes player-facing content. Source: docs/MASTERY_AUDIT_2026-07-09.md header.
- R-27 [2026-07-09] IMPLEMENTED (Wave 1 + Wave 2) Will approved BOTH WAVES of the 11-agent mastery
  audit + boost plan: Wave 1 = 6 broken fixes + Defense/Earth/Storm boosts; Wave 2 = the rest
  (Warfare/Nature/Spirit/Dream/RuneMaster/Neidan). Occult + Hunting = FROZEN benchmarks, never
  modified. Source: docs/MASTERY_AUDIT_2026-07-09.md.
- R-28 [2026-07-10] IMPLEMENTED (build36 Lane B) "yes make them" - Will approved the additive SVAERA
  mastery graft (`docs/SVAERA_MASTERY_COMPARISON.md`: graft #0 PC anim-row completion + 14 additive
  skill grafts + the Rune Golem follow-up). Wholesale SVAERA adoption was REJECTED on all 12 trees per
  the same audit judgment - only additive hybrid grafts taken, never a tree replacement. Source: docs/
  BACKLOG.md ~line 1210; docs/MASTERY_DEVIATIONS_LEDGER.md sec 4/5.
- R-29 [build43] IMPLEMENTED (b67), verbatim: "Go ahead and fix the occultist and hunting mastery
  black-background fixes. You may need to go into SV files to find the appropriate background image
  for the occult mastery skill selection page." Occult tree-pane background repointed to an SV-sourced
  texture (`standardskillbackground_joanna_ver_dark.tex`); Hunting audited already-correct, no action
  needed. Gamepad-parity variant of the art is OUT of round-1 scope (mouse/keyboard only). Source:
  docs/reports/b67_oh_pane_art.md.

### World / placement (continued)
- R-33 [build25, IMPLEMENTED] [paraphrased - DOORS_HUB_LOG.md's author-phrasing of Will's intent,
  line ~162, not a first-person quote] Will wants the wagon on the driver's RIGHT-HAND (screen-right
  = +X = East) side - the Hidden Valley caravan cluster wagon was on the wrong (west/screen-left) side;
  recomposed east of the driver, horse hitched south of the wagon, all >=3.5u apart. Shipped in the
  build25 "C1-C4 fixes" canonical bundle. Source: docs/DOORS_HUB_LOG.md sec C3.
- R-34 [build24/25, IMPLEMENTED per the C1-C4 bundle] Will's C2 feedback wants a SOLID "purple occult
  pyre/volcano-style visual anchor" at the HVBorder04 sprite-spawner site - the bare `pit_fx01` FX
  alone read as insufficient; co-located with a solid Hades firepit/woodpyre mesh
  (`mc_hades_anouranfirepit02` + `mc_hades_woodpyre01`). Shipped in the build25 canonical bundle per
  the doc's deploy-summary line ("A1/A2 doors + C1-C4 fixes"); not independently re-confirmed this
  sweep - UNKNOWN-STATUS beyond that bundle note. Source: docs/DOORS_HUB_LOG.md sec C2.
- R-35 [origin report not located this sweep, STATUS: STILL OPEN as of 2026-07-10] "The Lower Olympus
  respawn trophy Will asked to REMOVE" [paraphrased quote of Will's original instruction; the
  instruction's own source doc was not found in docs/ during this sweep] - `respawn_olympus_new.dbr`
  in `olympusfinal02` was meant to be de-placed (fix already coded) but as of the 2026-07-10 dead-
  content audit was STILL live in the shipped map (needs a map rebuild + redeploy + re-verify it is
  gone). No later doc confirms this shipped. Source: docs/DEAD_CONTENT_AUDIT_2026-07-10.md LANE B.
  Also see the DEBT REGISTER in docs/BACKLOG.md.
- R-36 [2026-07-07ish, IMPLEMENTED per BACKLOG merge] "Polis vault cage interior (Guardian + horde + 5
  majestic chests)" [paraphrased] - Will asked about the Polis Vault cage interior explicitly; the
  `polis_vault` DB module + its map placement merged (b37 map pass). Source: docs/
  HANDOFF_MASTER_2026-07-12.md; docs/BACKLOG.md (polis_vault merge note).
- R-37 [pre-build41, STANDING] The Legendary Warden-of-Souls cage: aggro-through-bars is native to this
  cell's neighbours and was APPROVED by Will (not a defect to fix). Source: docs/reports/
  b42_fixedboss_dedup.md.
- R-38 [2026-07-16] IMPLEMENTED (backlog swap) "Will 2026-07-16: replaced the second crocodile -
  'choose something we dont have an uber hero for yet'" - NEW-HERO-NILE-CROC renamed/retargeted to
  NEW-HERO-NILE-SCORPION (scorpos family; no uber scorpion existed in the roster); alternates if the
  rig disappoints: giant scarab, plague swarm host. Same Nile Floodplain / 'Plight of the Nile
  Farmers' quest-completion spot, same quest-collision-safety requirement. Source: git commit
  `edd30b6` (docs/BACKLOG.md).
- R-39 [2026-07-16] **IMPLEMENTED (b91, branch `fix/debt-mixed`) - all 6 sub-items shipped
  + build-verified.** (Round 1 recorded this as PARTIAL with the exclamation marker BLOCKED; round 2,
  2026-07-28, shipped the marker and PROVED THE BLOCKER ITSELF WRONG - see the last bullet.)
  Ruling text (unchanged): Cold Worm needs ~3x characterLife and +20%
  armor (`defensiveProtection`) ON TOP of the already-queued kit (burrow/frost skills that actually
  cast), a massive total-speed boost, the exclamation-marker mechanism extended to all placed ubers,
  and the 3-tier soul + loot-triple fix + roster drop-slot sweep - ships as ONE lane, not piecemeal.
  Source: git commit `edd30b6` (docs/BACKLOG.md "COLD WORM BUFFS").
  - CORRECTION to this entry's own premise: the worktree `coldworm-markers` had **NO partials**.
    `feat/coldworm-uber-markers` @ `75110bd` is an ANCESTOR of `main` (0 commits ahead, clean tree,
    empty `main...` diff), so the lane was abandoned before anything landed. b91 was built from
    ground truth, not resumed.
  - IMPLEMENTED by `tools/patches/coldworm_buffs.py` (registry module, apply+verify, registered
    after `boss_skill_fix` and immediately before `visuals`): 3x life `[14000,18000,22000] ->
    [42000,54000,66000]`; +20% armor; the rig-proven `um_coldcreep_29` total-speed profile; and a
    kit that actually casts. RCA: Cold Worm's ENTIRE kit pointed at the
    `boss skills\d2custom\coldworm_*` + `Game\D2*` namespace, absent from the mod arz AND upstream
    SV 098i AND the base game - 8/8 active slots dead, the worst record in the whole DB.
  - RECONCILIATION on "+20% armor (`defensiveProtection`)": that field is INERT on monsters
    (0 non-zero carriers of `defensiveProtection` or `defensiveProtectionModifier` DB-wide); monster
    armor comes only from `armor_passive`, whose `defensiveProtection` array is exactly linear
    (level N == N armor). +20% is therefore applied as `armor_passive` level `[60,174,360] ->
    [72,209,432]` - Will's field, at the only layer where the number does anything.
  - The "3-tier soul + loot-triple fix" was ALREADY CORRECT on `main` (3 tiers, strict progression,
    per-tier b40 icons, pcsafe grant, `[n,e,l]` triple @66 PLACED_UBER rate). b91 asserts it in
    `verify()` and rewrites nothing.
  - NEW GATE shipped with the lane: an active skill slot must be CASTABLE, not merely wired - the
    skill must resolve AND its `skillSpecialAnimationName` must be bound by an
    `unarmedSpecialAnimRef` on the caster (the monster-side twin of B-SOUL-PROC-2). Planted negative
    test: `py tools/patches/coldworm_buffs.py --negtest` -> PASS.
  - Roster drop-slot sweep shipped as `tools/sweep_soul_drop_slots.py` (read-only diagnostic,
    encodes rank-gating + terminal-form-chain design rules). Cold Worm is clean; it surfaced 6
    unwaived PRE-EXISTING findings (Leinth x3 + Spinebreaker `dropItems=0`; Typhon + Yaoguai
    `dropItems` absent) which are REPORTED, NOT FIXED - fixing them changes placed-content drop
    behaviour and defaults to WILL-VETO. In the BACKLOG DEBT register.
  - **THE 6th SUB-ITEM (exclamation marker): IMPLEMENTED in round 2 (2026-07-28), and round 1's
    "BLOCKED" verdict was WRONG.** Round 1 claimed two blockers; only the first survives.
    (a) TRUE: the cited "b63 mechanism" does not exist in this repo (no b63 report/commit/code - the
    reports jump b62 -> b64; the only `b63` string is the workflow id `wf_87586bbf-b63`), so the
    mechanism had to be found from ground truth rather than "extended".
    (b) **FALSE**: it is NOT map-side. The exclamation marker is the DB-side Monster field
    **`DisplayAsQuestItem`** - present on all 4,601 Monster records, set to 1 on 124 of them (every
    base-game quest boss, every `xsq` named quest hero, the escort/rescue NPCs, the quest
    chests/doors/objects, and the whole `records\poi\**` `AreaOfInterest` map-marker namespace) -
    and it was **ALREADY LIVE in this mod on Cold Worm himself** (`records\test\boss_coldworm50.dbr`
    = 1 on `main`). That is the marker Will saw. Round 1 scanned only for `miniMapEntity`, found 0
    Monster carriers, and generalised from that one field. No `Levels.arc` build, no
    `SVC_SVAERA_ARC`/`SVC_SV_ARC` dependency, zero map bytes.
    IMPLEMENTED by `tools/patches/uber_quest_markers.py` (registry module, apply+verify, after
    `coldworm_buffs`, before `visuals`). "All placed ubers" is DERIVED, never hardcoded:
    `soul_spawn_provenance_sets()`'s `placed_members` - the same source of truth as the PLACED_UBER
    66% soul rate (R-42) - narrowed by RULE A (the record, or a form in its `actorToSpawnOnDeath`
    chain, actually pays a soul out, which excludes the boss RETINUE mechanically) and widened by
    RULE B (mark every DEDICATED chain form, i.e. one whose spawners are ALL in the roster).
    **Both rules are derived from shipped content:** the one placed uber already marked on `main`
    is `um_polisgaoler_99` AND its dedicated `um_polisgaoler_unbound_99` - literally rule A + rule B.
    Rule B's exclusivity test is load-bearing: `as_ghosthero_32` is Neferkha's terminal form AND
    five ROAMING mummy heroes' (`um_tath_27`/`um_khenti_31`/`um_nebtaan_32`/`um_radementes_31`/
    `us_menkare_33`), so a naive whole-chain walk would spam markers across the map.
    Roster = 25 records (21 encounters + 4 dedicated forms), 23 newly marked; 26 retinue/adds
    excluded - and every excluded record is rank=Champion while every kept record is Boss/Hero, two
    independent signals agreeing on the same cut. NEW GATE (a new content class ships its gate):
    every roster member + dedicated chain form carries `DisplayAsQuestItem=1`, no SHARED form does,
    and 3 pre-existing anchors stay intact; 4-plant negative test
    `py tools/patches/uber_quest_markers.py --negtest` -> PASS. ONE field, 0 new records, 0 tags.
    Report: `docs/reports/b91_coldworm_buffs.md` sec 9 (sec 7 kept, marked SUPERSEDED, as the error
    record). LAUNCH-GATED residual in BL-b91-DEBT-4: nobody has SEEN the marker in-game (the
    player-surface checklist forbids claiming a visual from a non-in-game-confirmed source), and
    Will should judge whether 25 markers is the right density or reads as clutter - narrowing it is
    a two-rule edit in one module, with no map rebuild.

### Souls & items (continued)
- R-70 [2026-07-14] IMPLEMENTED (D2/FIX 5) Will's directive, verbatim: "Do not promote tomb guardian
  and do not have him drop a soul." `um_tombguardian_26` kept Common / `chanceToEquipFinger2=0.0`; the
  attached-but-undroppable `um_tombguardian_soul_{n,e,l}` rings were detached then retired (removed
  from the arz) along with their orphaned name tag. Source: docs/reports/souls_quality_fix.md sec 3
  (P2-a).
  > ⚠️ **ID CORRECTED 2026-07-28** (`fix/debt-docs` ledger-hygiene pass). The b84 backfill filed this
  > as a SECOND `R-43`, colliding with the live Souls R-43 (Blood Cult High Priest summon). The live
  > R-43 keeps its number; this backfill entry moved. **It moved to R-70, not to R-49**: the Souls
  > decade 40-49 is FULL because the parallel `fix/devourer-chest` lane claimed **R-49** on
  > 2026-07-27 for a live Will ruling (the Devourer chest-spawn repeat, IMPLEMENTED b91, cited from
  > R-3's body and from `docs/reports/b91_devourer_chest_spawn.md`). That number was in use first and
  > is load-bearing, so this pass allocated the **Souls & items OVERFLOW decade 70-79** (see the
  > header) rather than take it. The DEBT REGISTER line "Tomb Guardian soul leak - RESOLVED (R-43)"
  > now reads R-70.
- R-44 [2026-07-14] IMPLEMENTED (D3/FIX 4) Will's directive, verbatim: "fix the crowboar soul's
  summoned crow bug ... sweep the roster for any OTHER summon soul with the same broken
  on-attack+petLimit=1 shape and fix those too (same bug = same wave)." Round-2 widened this from 4 to
  a roster-derived 8-family set (manual-cast per the Lyia Leafsong convention). Source: docs/reports/
  souls_quality_fix.md sec 3 (FIX 4/D3).
- R-45 [2026-07-14] IMPLEMENTED (D1, was WILL-VETO, now RATIFIED) "yes fix any blatant errors that you
  detect ... bloodtip 5/7/9 + gustleech 10/12/14 ship as-is" - clears the earlier WILL-VETO flag on
  these two SV-098i-identical `itemSkillLevel` arrays (judged amgoz1 data-entry oversights, not intent;
  fixed raise-only, grant names untouched). The `_SV_INVERSION_FIX` code block is kept as a documented
  historical revert path only. Source: docs/reports/souls_quality_fix.md sec 5 (D1); docs/BACKLOG.md
  ~line 404.
- R-46 [2026-07-14] IMPLEMENTED (D5) Will's directive, verbatim (partial): "classify each ... fix every
  blatant error via the module ... leave polish documented" - every MINOR-GAP class in the 155-item
  souls-quality audit list was classified BLATANT DATA ERROR (fixed) vs SUBJECTIVE POLISH/DESIGN (left
  documented, untouched). Source: docs/reports/souls_quality_fix.md sec 5.5.
- R-48 [2026-07-27] IMPLEMENTED b90 (feat/toxeus-souls-100), verbatim: "increase the drop rate for
  the souls of toxeus the murderer, enslaver of souls and toxeus the murderer, devourer of blood to
  100%" - `chanceToEquipFinger2 = 100.0` on EXACTLY two monster records:
  `records\creature\monster\shadowstalker\um_toxeus_enslaver_99.dbr` (66 -> 100, the PLACED_UBER
  rate) and `records\xpack\creatures\monster\skeleton\um_bloodtoxeus_99.dbr` (25 -> 100, the
  module-owned superboss cap). Owner: `tools/patches/toxeus_souls_100.py` (registry module,
  registered last among content modules; deterministic + idempotent; apply() proves roster-wide that
  ONLY these two records moved; verify() re-asserts 100 on the FINAL merged arz and fails the build
  loud otherwise). Holds in RELEASE mode (`SVC_RELEASE_DROPS=1`), which is what ships - it does NOT
  rely on `_force_100_pct_soul_drops`, the TESTING-only forcer that never runs in a release build.
  RECONCILIATION: PARTIALLY SUPERSEDES R-42's "random 50 / placed 66 / boss 25" split for these two
  records by name only (every other soul rate is untouched, proven in the record-diff); the shared
  classifier `build_svc_database.soul_drop_rate()` is deliberately NOT modified, so both records are
  carried as documented waivers + spot-tests in `tools/verify_soul_drop_rates.py`
  (`_KNOWN_EXCEPTIONS` 25.0 -> 100.0 for the Devourer, new 100.0 entry for the Enslaver). Does NOT
  touch the Hero/Boss/Quest soul-drop gate in `wire_souls_to_monsters` (the yeti Common/Champion
  lesson): both champions are `monsterClassification=Boss`, so the gate never applied to them and
  no Common/Champion is re-enabled. See docs/reports/b90_toxeus_souls_100pct.md.
- R-71 [2026-07-14] IMPLEMENTED b91 (fix/debt-db, 2026-07-28) *(appended by the debt-db lane as a THIRD colliding R-49; renumbered into the Souls overflow decade 70-79 by the debt-wave integration - R-49 belongs to the fix/devourer-chest lane, 2026-07-27)*, verbatim: "emberteeth soul should let
  you summon him." Ground truth first: `emberteeth_soul_{n,e,l}` granted NO skill at all (a pure
  fire-stat ring), so the feature was genuinely unbuilt. Built via the standard boss-summon recipe -
  3 permanent pets from `um_emberteeth`'s OWN rig through the shared `_build_boss_summon` pipeline
  (mesh/anim table/attack skill/attribute cadence/skill kit; race + orthrus vox/alert/death/stun paks
  per the b81 identity law and R-11; gear mirrored through `_set_pet_equipment`, never Monster.tpl
  equipment/loot copies; D19 pet-mobility assert; permanent, no TTL) plus a manual-cast summon
  button, souls wired at `itemSkillLevel` 1/2/3 so the epic soul spawns the epic-tier pet (the R-43
  companion check). Every pre-existing fire benefit is KEPT and proven field-by-field in `apply()`;
  the soul's display name is deliberately NOT renamed (a summon was asked for, not a rename). Owner:
  `tools/patches/emberteeth_summon.py` (registry module + `verify()` hook). Life band derived from
  the roster's lesser-summon life-per-charLevel cluster rather than invented. Player-surface
  checklist in `docs/reports/b91_debt_db.md` sec 3; the pet-bar portrait falls back to the neutral
  summon-proxy (no `chimera_party_*` art ships) - a bespoke portrait is registered as BL-b91-DEBT-8,
  NOT silently deferred. In-game confirmation is launch-gated (BL-b91-DEBT-10): test on a FRESHLY
  DROPPED soul, since TQ bakes item properties at pickup. Source: docs/BACKLOG.md "QUEUED FEATURE:
  SOUL-EMBERTEETH-SUMMON (APPROVED by Will 2026-07-14)".
- R-49a [2026-07-27] IMPLEMENTED b97 (fix/soul-identity), verbatim: "we also need to do an audit of
  the hero monsters vs the souls that they drop since i can see that some of the heroes are dropping
  the wrong souls or souls for other boss monsters i think" - CONFIRMED. **A creature must not drop a
  soul whose identity belongs to a DIFFERENT named creature that also drops it.** 18 records were
  detached (`chanceToEquipFinger2 -> 0`; `lootFinger2Item1` deliberately KEPT, the A4/R-45 shape).
  ROOT CAUSE: a monster's identity is its `description` tag, NOT its .dbr filename - the base game
  reuses ONE hero filename across several named heroes (`hero_wheedletongue_{39,41,43}` =
  Wheedletongue / **Fesil the Quick** / **Sinnet Patchfur**), and `wire_souls_to_monsters` matches by
  filename; our build then ACTIVATED the resulting mis-pairings that SV 0.98i shipped dead at
  chance 0. Owner: `tools/patches/soul_identity.py` (registry module, registered after every
  soul-wiring/drop-rate module). The rule is DATA-DERIVED, not a hand-list, and structurally cannot
  orphan a soul: a family with NO identity-owning carrier (archetype souls like Satyr Fire Magi /
  Sandwraith, name-drift 1:1 like Wither Mound <-> Speckled Jim, mod-themed "Soul of the X") is never
  touched. verify() re-runs the rule over the FINAL merged db as a permanent LIST-FREE gate; planted
  negative test `tools/contracts/tests_soul_identity_negative.py`.
  RECONCILIATION: does NOT overturn any ruling. R-48's two champions are SOLE carriers of their souls
  (untouched, re-proven at 100 by this module's verify()); R-45 tomb guardian stays 0.0; R-42's
  50/66/25 classifier is NOT modified, so all 18 zeroes are carried as documented per-name waivers in
  `tools/verify_soul_drop_rates.py` `_KNOWN_EXCEPTIONS` (the same shape as the legion_soul_stages
  non-terminal zeroes); R-43 / R-44 / bloodtip / gustleech / the legion double-soul chains untouched.
  NOT DONE ON PURPOSE (Will decisions, see report sec 8): no soul was INVENTED for the 18 now-soulless
  creatures (new content = amgoz1 creative bar), no NAME-DRIFT rename (incl. the "The Etheral One
  Soul" misspelling), and the Iron Lore zzdev dev-dummy soul drops were left alone (retirement
  protocol). See docs/reports/b97_soul_identity_audit.md.
  > NUMBERING NOTE: the Souls decade (40-49) is EXHAUSTED (R-49 went to the b91 devourer-chest fix),
  > hence the `a` suffix. The next soul ruling should either continue the letter series (R-49b) or be
  > allocated a fresh decade by whoever files it. Registered as BL-b97-DEBT-5.
  >
  > **ROUND 2 AMENDMENT [2026-07-28] - the round-1 gate was NOT roster-wide.** The vet caught it:
  > both the audit and the shipped gate were scoped by a path predicate requiring `\creature\` or
  > `\creatures\`, so **97 live soul carriers were never judged** - all 25 of `records\drxcreatures\`
  > (shipping DRX/Urder content), `records\test\`, `records\item\equipmentring\soul\test\` and the
  > pet trees. Hiding inside them was a **real 19th mismatch of exactly the reported class**:
  > `records\drxcreatures\xurder\d2npc\01_akara.dbr` displays **"Akara"** and dropped
  > **"Kallixenia ~ Liche Queen Soul"** at 66%, while the real Kallixenia
  > (`xsq02_lichequeen_36`) drops an identically-named soul at the same rate - and the wire is
  > **ours** (`apply_svc_patches._create_kallixenia_soul`). Three more (`soul\test\`
  > `us_lysiaspellbreaker_15{,_e,_l}`, displaying "Nenea Sharpclaw") were hidden the same way.
  > **22 records are now detached, not 18.** Three further defects were found and fixed in the same
  > pass: (a) carriers were grouped by the soul .dbr **filename**, repeating inside the gate the very
  > filename-is-identity mistake it exists to punish - grouping is now by the soul's **display name**;
  > (b) `apply()` judged identity against **pre-F6** soul names while `verify()` saw the final ones,
  > so the two passes could disagree (they did, on Kallixenia) - `_display_tags` now applies the same
  > authoritative `_SOUL_NAME_STANDARD` override both passes will ship with; (c) the ARCHETYPE vs
  > NAME-DRIFT split was decided by a row COUNT, which mislabelled **Cynisca, Princess of Sparta**,
  > **Corpse Wake** and **Meritamen the Shadowcaller** as name drift - it is now decided from the
  > data (does a record owning that soul name exist, gated dead?). **PETS are deliberately NOT
  > carriers**: counting the 0.5% monster-scroll pet "Maenad ~ Sorceress" would crown a player summon
  > rightful owner of an archetype soul and zero the real 50% Boss that drops it. Two new planted
  > tests lock both halves: T6 plants a thief OUTSIDE `\creature(s)\`, T7 proves a pet convicts
  > nobody. NEW WILL DECISION (report sec 8): zeroing Akara leaves our bespoke
  > `soul\svc_uber\kallixenia_soul_*` item undroppable (the NAME stays obtainable from the real
  > Kallixenia); the item is KEPT intact, and re-pointing it - or renaming the record to Kallixenia,
  > which is what our own code comment intends - is Will's call.
- R-47 [pre-build41, STANDING] "the generic orb target Will wants" [paraphrased] - custom Boss-class
  encounters (Blood Toxeus, Enslaver, Vashkarr, Broodmother, Dorus, Sarkoth, Gorrahk, Ilsevar,
  Voranthys, Tantalus, Mnemophage-core, Ephialtes, ...) drop the un-named generic apex orb
  (`genericbossorb_04`, no bespoke "X's Essence" name) as the established convention - NOT a bespoke
  named essence per boss. Source: docs/reports/b53_orb_essence.md sec 4.
- R-72 [2026-07-27] IMPLEMENTED b96 (feat/vashkarr-soul). Will's directive, VERBATIM:
  "Vashkarr, Eldest of the Ancients soul should get +% pierce damage and =% penetration  since he is a spear and shield guy and the soul should give +% boost to movement not have a penalty for speed, this guy should be fast. also he needs to do more damage. we can have the penalty be something like -6-8% reduction in elemental damage or something like that"
  and, on field selection, VERBATIM: "see spawn of chi soul for how to add +% penetration and
  pierce damage"

  READ AS (the "=%" is a typo for "+%"): (a) ADD +% pierce damage and +% pierce PENETRATION;
  (b) the existing movement-speed PENALTY becomes a movement-speed BONUS; (c) raise the soul's
  overall damage; (d) introduce a -6% to -8% elemental-damage drawback in its place. Net: the
  soul trades elemental power for speed and piercing lethality.

  SCOPE: the three tiers of `records\item\equipmentring\soul\svc_uber\vashkarr_soul_{n,e,l}.dbr`
  (name tag `tagSVCSoulVashkarr` = "{^F}Vashkarr, Eldest of the Ancients Soul"), dropped by
  `records\creature\monster\dragonian\um_vashkarr_99.dbr` at 66%.

  IMPLEMENTED AS (`apply_svc_patches._create_vashkarr._vk_stats`), n/e/l:
  - `offensivePierceModifier` 40 / 58 / 78 (was absent) - donor: Spawn of Chi soul, Will's own
    named reference (30/42/58 there).
  - `offensivePierceRatioModifier` 35 / 50 / 65 (was absent) - same donor (40/54/62 there).
    This is TQ's armour-bypass "penetration": it converts part of the ring's large physical
    package into pierce, so the two fields compound into the lancer identity.
  - `characterRunSpeedModifier` +12 / +17 / +22 (WAS -8 / -8 / -8) - donors: sandbeak /
    sandprowler / rakanizeus souls, which carry positive run speed in the same slot.
  - `offensiveElementalModifier` -8 / -7 / -6 - donor: `u_n_ringofzakalwe` (an Epic ring that
    ships +25% physical / -25% elemental: the same trade, larger). The drawback deliberately
    SHRINKS with rarity so every tier stays inside Will's -6..-8% band AND no higher tier is
    strictly worse than the one below it on any power axis.
  - Damage raised: `offensivePhysicalMin/Max` 60-95 -> 78-124, `offensivePhysicalModifier`
    35 -> 46, `characterOffensiveAbility` 90 -> 110, `characterAttackSpeedModifier` 16 -> 18,
    `offensiveSlowBleedingMin` 120 -> 150, `offensiveLifeLeechMin` 25 -> 30 (Legendary anchors;
    n/e follow the existing 0.6 / 0.82 tier ramp). The FIRE package is held FLAT (nothing
    retired, nothing grown) so the soul's centre of gravity shifts off the elemental axis
    without deleting his dragonian heritage.

  PARTIALLY SUPERSEDES the A8/B7 "Eldest+Gorrahk" rebalance
  (`apply_svc_patches._apply_b7_eldest_soul_rebalance`), which is an UNLEDGERED Will decision -
  its only record is the verbatim quote in that function's docstring, "crazy on normal, 74%
  physical damage resistance? doesnt that make you nearly unkillable by physical hits that
  arent piercing?", never assigned an R-number (registered as debt by this lane). That pass ran
  AFTER `_create_vashkarr` and stamped `characterRunSpeedModifier = -8.0` onto both soul
  families as an "ancient and heavy" downside. Its run-speed clause is now scoped to GORRAHK
  ONLY; leaving it in place would have silently clobbered this ruling back out. Superseded for
  VASHKARR ONLY and on the run-speed axis ONLY: the physical-resistance cap (30/45/60), the
  flat-armour conversion (150/260/400) and the +25% HP of that pass are UNCHANGED for both
  families, and Gorrahk keeps its -8% run speed untouched.

  GATE: `contracts_souls.SOUL-IDENTITY-SHAPE` + the declarative `SOUL_IDENTITY_SHAPES` registry
  assert this shape against the FINAL built .arz every run (fields present and in-band, run
  speed positive not negative, mandated tier ordering). `tests_souls_negative.py` case 11b
  plants the pre-R-72 state (-8% run speed on all three tiers) and requires the contract to
  FIRE. Source: docs/reports/b96_vashkarr_soul.md.


### Toxeus arc - OVERFLOW decade 90-99 (allocated 2026-07-28 by the b98 Endless Hunt lane, moved off 80-89 on 2026-07-29)
> The Toxeus decade 1-19 is FULL (R-1..R-19 all in use). Per the header's rule that a number in use
> is NEVER reused, this lane allocated a fresh decade for the Toxeus arc.
>
> ⚠️ **IT ORIGINALLY TOOK 80-89, AND THAT WAS WRONG BY THE TIME IT LANDED.** The check that
> justified 80-89 was run against `a0276ab`, where 80-89 really was free. The b99 content wave then
> merged to `main` and DEPLOYED, taking **R-80 = the death-XP penalty** and reserving 80-89 for
> "Global balance & progression". b99 is the incumbent (on main, and shipped), so at integration
> round 2 these seven rulings moved, in order and without any content change, to the next free
> decade **90-99**: R-80->R-90, R-81->R-91, R-82->R-92, R-83->R-93, R-84->R-94, R-85->R-95,
> R-86->R-96. Re-checked at the time of the move: in use across the whole ledger are 1-19, 20-29,
> 30-39, 40-49, 50-51, 60-61, 70-72 and 80 - and, on the two branches still in flight,
> `feat/leinth-wave` R-73..R-76 and `fix/green-diff` up to R-71. **90-99 is free on main and on
> every in-flight branch**, which is why it was chosen rather than the tail of an existing decade.

- R-90 [2026-07-28] IMPLEMENTED b98 (feat/endless-hunt), verbatim: **"yeah lets have the endless
  pursuit only be on legendary"** - Toxeus the Murderer, the Endless Hunt cannot be kited away from
  his spawn point on LEGENDARY; Normal and Epic keep normal leash behaviour, and that is now
  INTENDED, not a bug.
  MECHANISM (proven, not assumed): leash/pursuit is not a Monster field at all - all 4,600 Monster
  records carry zero leash/aggro/chase/pursuit field. It lives on the CONTROLLER. His
  `controller_shadowstalker01_hidden` carries `MaxPursuitDistance=60` + `PursuitTime=20000` +
  `RoamBehavior=Roam`: that IS the kite, field for field. Per-difficulty pursuit is NOT expressible
  on one record - both fields are array-valued ZERO times across all 504 controller records, and the
  engine's own `Toolset/Templates.arc` declares them `class="variable"` (scalar) while `LeadChance`
  is `class="array"` (the [normal,epic,legendary] triple). `monster.tpl` likewise declares
  `controller` `class="variable"`. A Legendary-gated buff/aura skill cannot do it either (skills move
  STATS, never controller fields). So the ruling is delivered by a SECOND monster record selected
  through the proxy's `poolLegendary1` slot - the shipped per-difficulty-monster-swap pattern (29
  base-game proxies already do exactly this; `ag_demon_djinnsprite_01t_ambush` is the exact shape).
  Owner: `tools/patches/toxeus_hunt_endless.py` - a dedicated relentless controller CLONED from his
  own (never editing the shared donor, which 15 monsters use INCLUDING the Enslaver's marauders),
  `um_toxeus_hunt_l_99`, and a single-member Legendary pool. Values all have named shipped
  precedent: MaxPursuitDistance 1000 (controller_aktaios, the DB's highest), PursuitTime 100000 (21
  carriers incl. hydra/terracotta/typhonminion), RoamBehavior NeverRoam (107 carriers), ForgiveRate
  0.2 (Aktaios). FleeBehavior stays NeverFlee: Aktaios's FleeWhenEnemyClose was deliberately NOT
  copied, because a hunter that flees is nonsense. verify() asserts base and variant differ in
  EXACTLY the `controller` field, which is what makes the doubled record safe from drift.
  ⚠️ LIMIT WILL MUST KNOW (reported, not hidden): the ROAMING spawns cannot be difficulty-split.
  ProxyPool has `nameN` with no `nameEpicN`/`nameLegendaryN`, and the 345 roaming pools he rides are
  NATIVE base-game pools shared across all difficulties. So the roaming Hunt stays kiteable even on
  Legendary; only the FIXED Hades Palace encounter carries the endless variant. That is also the
  SAFEST shape - MaxPursuitDistance 1000 is proven on Aktaios, a FIXED ARENA boss in bounded space.
  ⚠️ ALSO NEEDS WILL: at 1000 units / 100 seconds he effectively cannot be outrun to a town portal
  on Legendary. Confirm that is the intent (BL-b98-DEBT-3).
  SCOPE CORRECTION SHIPPED WITH IT: the ruling's premise ("only on legendary") implies the MONSTER
  is available on all three difficulties. The fixed encounter proxy was Legendary-ONLY, so the same
  lane removed that gate - `q_toxeus_hunt_lone` now names his pool on pool1, poolEpic1 AND
  poolLegendary1. `tools/patches/toxeus_hunt_encounter.py` owns it, and its verify() now FAILS if
  any of the three is empty (the inverse of the assertion the old module shipped).
- R-91 [2026-07-28] IMPLEMENTED b98 (feat/endless-hunt) [paraphrased from the approved design brief;
  no verbatim transcript line] the Endless Hunt's soul drops 100% of the time, like the other two
  fought Toxeus champions. EXTENDS R-48 from two records to three and CLOSES `BL-b90-DEBT-4`, which
  had recorded the carve-out and named Will as its owner/trigger.
  ROOT CAUSE, stated exactly: the ONLY defect was the rate. `chanceToEquipFinger2 = 25.0` on
  `records\creature\monster\shadowstalker\um_toxeus_hunt_99.dbr`. The soul was NOT unwired and NOT
  the wrong record - `lootFinger2Item1` already named the correct `toxeus_hunt_soul_{n,e,l}` triple,
  `chanceToEquipFinger2Item1` was already 100, `dropItems` already 1, and all three soul records
  already existed with their name/desc tags and icon. 25% simply means three kills in four pay
  nothing. Owner: `tools/patches/toxeus_souls_100.py` (the R-48 owner, extended; apply() re-proves
  roster-wide that ONLY the three named records moved, verify() re-asserts 100 on the final merged
  arz). `tools/verify_soul_drop_rates.py`'s waiver for `um_toxeus_hunt_99` moves 25.0 -> 100.0 and a
  matching waiver is added for the R-90 endless variant. Holds under `SVC_RELEASE_DROPS=1`, which is
  what ships. The Hero/Boss/Quest gate in `wire_souls_to_monsters` is untouched (he is Boss-class, so
  the yeti Common/Champion lesson does not apply).
- R-92 [2026-07-28] IMPLEMENTED b98 (feat/endless-hunt) [paraphrased; the ask was to "align with
  however the Enslaver and Devourer already drop it"] killing the Endless Hunt also yields the Rite
  of the Undivided (the End of All Things formula), on ALL THREE difficulties - and the RECIPE keeps
  demanding the LEGENDARY souls. Extends R-13 to the third champion. The Hunt had NO `Misc4` slot at
  all; he now mirrors the ENSLAVER exactly (`chanceToEquipMisc4=100`,
  `chanceToEquipMisc4Item1=100`, `lootMisc4Item1 = svc_rite_guaranteed` on all 3 tiers), using the
  Enslaver's simple FixedWeight form rather than the Devourer's master table because the Hunt has no
  rant scroll to co-schedule. VERIFIED ALREADY-CORRECT, no change needed: `svc_toxeus_eoat_formula`
  names `toxeus_soul_l` + `enslaver_soul_l` + `blood_toxeus_soul_l` by exact path, so the recipe
  cannot be completed with normal- or epic-tier souls and R-8's Legendary gate stands. Because the
  formula ITEM can now drop on Normal/Epic, that recipe gate is load-bearing, so
  `toxeus_hunt_encounter.verify()` now ASSERTS all three reagents stay `_l` records and fails the
  build otherwise.
  ⭐ OPEN WILL QUESTION raised by this: the three reagents are base Toxeus + Enslaver + Devourer.
  The Endless Hunt's own soul is NOT a reagent. Now that he is a full champion dropping the formula
  at 100%, should `toxeus_hunt_soul_l` become one (a 4th, or replacing the base Greece Toxeus's)?
  NOT built - `ItemArtifactFormula` was not confirmed to declare a reagent4 (BL-b98-DEBT-4).
- R-93 [2026-07-28] **PARTIALLY IMPLEMENTED b98 (feat/endless-hunt), REMAINDER OPEN** [paraphrased -
  Will's own idea] the Endless Hunt wields a spear, AND the three Toxeus champions should read as
  three different creatures.
  > ⚠️ **STATUS CORRECTED 2026-07-29 (round 4, adversarial-vet finding). The spear half is DONE; the
  > "three different creatures" half is ONE THIRD done and this ruling must not read IMPLEMENTED.**
  > Read out of the built arz: the Enslaver wears `Creatures\Monster\Skeleton\RevenantPoison.msh`
  > (NewSkeleton_Charcoal.tex) and the Devourer `um_bloodtoxeus_99` wears **the same**
  > `RevenantPoison.msh` (newskeleton_crimson.tex) - two of the three champions share a mesh and
  > differ only by texture and scale. Only the Hunt is visually distinct (`ShadowStalker.msh`).
  > b98 changed NEITHER mesh (both diffed, unmoved), so what shipped here is the Hunt's spear and
  > silhouette, not the champion-distinctness ask. The mesh half is entangled with the b92
  > mesh-embedded green aura and belongs to the `fix/green-diff` lane; it is registered as
  > BL-b98-DEBT-2. **Do not treat "make the three champions look like three creatures" as closed.**
  Spear detail follows. Shipped as **Runbreaker**, a bespoke 3-tier signature weapon following the
  Devourer's Crimson Verdict / Veinrender pattern exactly (`svc_{n,e,l}_runbreaker` +
  `runbreaker_guaranteed_{n,e,l}` FixedWeight tables wired to `lootRightHandItem1` @100%), so he both
  WIELDS and DROPS it instead of the random one-hander he carried.
  THE RIG WAS PROVEN BEFORE THE ITEM WAS SHIPPED. His record was MISSING
  spearAttackAnim1/2/3, spearRunAnim, spearDieAnim1 and spearStunAnim - a spear without those means
  he walks with it and never swings. The ShadowStalker rig ships no spear animation of its own (13
  .anm, 0 spear), so the attack poses are borrowed - which is the base game's NORM (672 shipped
  records play a cross-rig spear anim vs 247 same-rig) and which this mod already does on the Toxeus
  family's own skeleton rig (`boneash_1` carries a complete Maenad-spear block). The graft is
  deliberately MINIMAL: only the 3 attack poses are borrowed (Maenad, the boneash_1 precedent); run,
  die and stun are copied from the animation THIS RECORD ALREADY BINDS for its other weapon classes,
  read at build time so they cannot desync. New gate SPEAR-ANIM-1 + a provenance assertion that each
  borrowed pose is referenced by at least one other shipped record.
  ⚠️ PLAYER SURFACE, UNPROVEN BY EYE: Maenad-spear-on-SHADOWSTALKER has no shipped instance. Only
  Will's in-game look can settle it (BL-b98-DEBT-1). Ranked fallbacks: MedusaMinion_Spear (103
  users), then Machae_Spear (same expansion, same underworld).
  ⚠️ ONE-LINE WILL-VETO, deliberately taken and flagged: the supra spear donor ships
  `CharacterAttackSpeedSlow`, but the Hunt is the FAST champion (run 1.8 / attack 1.3). Runbreaker
  therefore ships `CharacterAttackSpeedAverage` + baseAttackSpeed 0.25 (both inside the shipped spear
  envelope) to KEEP him fast. Flipping those two values back makes him a slow, heavy reach-hunter
  instead; nothing else depends on the choice.
  FIX-UPSTREAM CAUGHT IN PASSING (BL-103): the supra donor still carries the build30-F3
  INVISIBLE-WEAPON DRX mesh at registry time (F3 repoints it in `run_registry_gates`, AFTER every
  module, and by name only), so a naive clone would have shipped an invisible spear. Runbreaker sets
  the F3-corrected base rig explicitly and drops the DRX-only skin, and verify() asserts each tier's
  mesh equals the donor's FINAL post-F3 mesh so the two can never diverge.
  > **ROUND 2 (2026-07-28, adversarial vet) - two additions, no reversal.**
  > 1. `spearSpawnAnim` was the ONE animation slot the new spear row lacked. Both his `sHanded` and
  >    `unarmed` rows bind `ShadowStalker_Spawn.anm`; the `spear` row did not, and the spear row is
  >    now his ONLY row (`chanceToEquipRightHand=100`, Item1 weight 100) while he is a
  >    `ControllerMonsterHidden` ambusher (appearDistance 12.0), so his emerge pose had lost its
  >    binding. Now self-sourced from `sHandedSpawnAnim` like the other three, and added to the
  >    SPEAR-ANIM-1 gate's required list with its own planted negative.
  > 2. THE BORROWED-POSE DEBT IS QUANTIFIED, and the ranked fallbacks are corrected.
  >    `Maenad_Spear_Att{Alpha,Beta,Gamma}.anm` track 26 bones including Bone_Tail01-04;
  >    `ShadowStalker.msh` carries about 30 bones including Bone_L/R_HorseBone, Bone_Neck02,
  >    Bone_L/R_Toe, Bone_L/R_Ear and Bone_Jaw, and NO tails. So during the three swing poses 8
  >    ShadowStalker-only bones get no track and 4 tail tracks hit nothing, while the whole
  >    shoulder/forearm/wrist/Bone_R_Weapon chain IS tracked, and 56 shipped TigerMan records (a rig
  >    that also has HorseBone + Jaw + tails) play these same Maenad anims. He WILL swing; the
  >    freeze is cosmetic. Still BL-b98-DEBT-1, still Will's eye.
  >    TWO CLOSER DATA POINTS the round-1 fallback ranking missed, WITH THE CAVEAT THAT MAKES THEM
  >    NOT A PRECEDENT: `records\skills\stealth\drxpet\anm_shadowstalker.dbr` ships a COMPLETE spear
  >    block on `FemalePC_Spear_*`, and `records\test\outsider_hero_*_46.dbr` use `Neanderthal_Spear_*`.
  >    Neither is proof for THIS rig: the first is the animation table of 42 pets that wear
  >    `DRX\meshes\stalker.msh`, and the second belongs to records wearing
  >    `SummonersDelightTextures\creatures\monsters\shadowstalker\daemon_outsider.msh` whose own
  >    animation table (`records\creature\monster\shadowstalker\anm\anm_shadowstalker.dbr`) is not
  >    even present in the mod arz. Both are DIFFERENT meshes. Ranked fallbacks are therefore
  >    unchanged (MedusaMinion_Spear, then Machae_Spear), with these two recorded as leads.
- R-94 [2026-07-28] IMPLEMENTED b98 (feat/endless-hunt), verbatim: **"he doesnt really have any
  different or unique skills from toxeus the murderer, the enslaver of souls"** - and that was
  LITERALLY TRUE. Ground truth: 9 of his 12 skill slots were the SAME SKILL RECORD as the Enslaver's
  (flashpowder, toxeus_bladestorm, netherstrike, lifedrain, character_speedall,
  boss_conversionimmunity, hero_scaling, toxeus_passiveproperties, armor_passive); his only 3
  non-shared slots are the globalproperties_{normal,epic,legendary}01 per-difficulty STAT hooks. He
  had ZERO unique active abilities, and slot 2 was even the same skill at the same slot index.
  FIX: the three cast slots that overlapped the Enslaver become his own pursuit kit, identity-driven
  per the amgoz1 bar (mark at medium range, reach at long range, kill at short range):
  Quarry's Mark (`svc_hunt_quarrysmark` + `_buff`, from Study Prey - heavy run-speed slow + DA shred
  + bleed: he has your scent and you cannot outrun him), The Long Reach (`svc_hunt_longreach`, from
  the DRX STALKER-namespace shadow blast - a cold spectral spear at range: distance is not safety),
  Run Them Down (`svc_hunt_rundown` - a close-range spear sweep). `toxeus_bladestorm` (the Toxeus
  family signature verb) and EVERY passive are KEPT: this edits 3 slots, it never strips his kit.
  CASTABILITY: every new skill declares NO `skillSpecialAnimationName`, the same law
  `toxeus_champion_kits` already ships for these champions. Gated fail-loud, plus a SAMENESS gate
  that fails the build if every one of his cast slots is an Enslaver cast slot again.
  REPORTED, NOT SILENTLY CLAIMED: the skill this replaces at specialAttack3, `netherstrike`, declares
  skillSpecialAnimationName='LethalStrike' which he does not bind - that slot was very likely dead
  already, so this is a repair as well as a differentiation.
  WILL'S OTHER OBSERVATION IS CONFIRMED BY THE DATA, NO CHANGE NEEDED: "it wasnt a skeleton, it was a
  demon" - `characterRacialProfile = Demon` on his record. That is a data fact, not a perception.
  ⚠️ CORRECTION TO THE DESIGN BRIEF, deliberately NOT actioned: the brief called
  `distressCallGroup='Skeleton'` on a Demon-race boss a clone leftover to fix. Ground truth says
  otherwise - it is the base game's convention for this rig, including on the Enslaver's own
  marauders. There is also no 'Demon' group in the DB (19 monster distress groups exist; Demon is not
  one), so "fixing" it would invent a group of one member and cut him out of the shadowstalker
  distress network.
  > **ROUND 2 (2026-07-28, adversarial vet). THREE CORRECTIONS AND TWO ADDITIONS. Will's words above
  > are untouched; what changes is what round 1 CLAIMED about them.**
  >
  > **CORRECTION 1 - THE CASTABILITY PREMISE WAS INVERTED, and it cost him 40% of his cast budget.**
  > Round 1 wrote "he binds ZERO `unarmedSpecialAnimRef` slots (so do the Enslaver and the
  > Devourer)". The parenthesis is FALSE. `um_toxeus_enslaver_99` and `um_bloodtoxeus_99` both carry
  > `charAnimationTableName = records\creature\monster\skeleton\anm\anm_skeleton01.dbr`, which binds
  > `sHandedSpecialAnimRef1='AoE360'` and `sHandedSpecialAnimRef2='LethalStrike'` - so the other two
  > champions CAN cast bladestorm and netherstrike. The Hunt has NO `charAnimationTableName` at all
  > and bound no `*SpecialAnimRef` on any row, so `toxeus_bladestorm` at specialAttack2 @40% (it
  > declares `skillSpecialAnimationName='AoE360'`) has NEVER been able to fire, in the shipped data
  > or after round 1 - while round 1's report presented it as kept and working. Round 1's gate looped
  > only the skills the module authored, so it could not catch it.
  > **FIX:** the animation is BOUND rather than avoided. `AoE360` is bound on his own inline
  > animation table (which IS his live table, since he has no charAnimationTableName) on TWO rows:
  > `spear*`, the row the engine reads while he holds the R-93 spear, and `unarmed*`, the engine's
  > universal fallback row, so the repair survives any later veto of the spear instead of dying with
  > it. Each bound `.anm` is asserted at build time to be the MODAL shipped binding for AoE360 on
  > that row (spear: `FemalePC_Spear_Skill_Tempest.anm`, 11 of 23 carriers; unarmed:
  > `MalePC_DW_Skill_AOE360.anm`, 5 carriers), so the choice is provenance, not a guess that a file
  > exists. Precedent: `coldworm_buffs.py` binds ref+anim for exactly this reason.
  > **THE GATE IS REBUILT, not patched:** `_castability_violations()` now walks EVERY populated
  > active slot on the record (attack / initial / dying / specialAttack / specialAttack2..6) and
  > derives the animation row from the Class of the item he is GUARANTEED in RightHand, so it follows
  > the weapon instead of assuming 'unarmed'. An unmapped weapon Class fails the gate rather than
  > passing silently. Note this is a genuine cross-rig cosmetic debt of the same class as R-93's:
  > the AoE360 pose is a PC-rig anim on the ShadowStalker rig. It makes the cast FIRE, which is the
  > law; whether the whirl reads right is BL-b98-DEBT-1's question.
  >
  > **CORRECTION 2 - HIS SOUL STILL GRANTED THE SKILL THIS LANE RETIRED.**
  > `toxeus_hunt_soul_{n,e,l}` granted `records\skills\soulskills\toxeus_flashpowder.dbr`, the very
  > skill removed from his kit above as "the Enslaver's". So the one player-facing artifact of his
  > identity, now dropping at 100% (R-91), handed out an ability he no longer has - and an
  > over-shared filler (15 soul records grant it). The other two champion souls summon their
  > champion; his was the odd one out. **FIX:** all three tiers now grant `svc_hunt_quarrysmark` (the
  > "become the Hunt" grant) at itemSkillLevel n/e/l = 1/2/3, the monolith's own established soul
  > tier convention, which also keeps the grant inside the skill's `skillMaxLevel` of 3. Soul and
  > monster share ONE skill record, so player-mark and monster-mark can never diverge. NEW INVARIANT
  > OF THE CLASS: a soul may never grant a level its skill does not have. FIX-UPSTREAM (BL-103): the
  > soul's DESC tag in `toxeus_suite.py` no longer advertises "the flash-burst that opens the range"
  > (and verify() fails the build if it comes back), and `skill_quality.ALLOW['toxeus_flashpowder.dbr']`
  > drops `tagSVCSoulToxeusHunt` from its locked family roster because he left the family.
  >
  > **CORRECTION 3 - CENSUS.** Round 1's "all 28 shipped ShadowStalker-mesh monsters are race=Demon
  > AND distressCallGroup 'Skeleton'". Re-run with the method stated so it reproduces (records whose
  > `mesh` contains 'shadowstalker.msh' AND `Class`=='Monster' in the deployed arz): 30 records, ALL
  > 30 race=Demon, 26 group 'Skeleton' and 4 group 'Jackalman' - and those 4 wear a DIFFERENT mesh
  > path, `Creatures\Monster\jackalman\shadowstalker.msh`. The race half was right, the group half
  > was not exactly right, and the DECISION IS UNCHANGED (no 'Demon' group exists).
  >
  > **ADDITION 1 - THE NEW SKILLS CARRIED UNREPORTED DONOR PAYLOADS.** Cloning brings the donor's
  > whole record, and round 1 shipped the leftovers silently. Now stripped, with a gate and a planted
  > negative for each: `svc_hunt_longreach` inherited `offensivePetrifyMin=2.0` (a 2-second HARD
  > PETRIFY at 30% cast chance on a 5s cooldown at range 12-22, stacked on R-90's unleashable
  > Legendary pursuit - combat-defining and never designed) plus lifedrain's 16-entry
  > `offensiveLifeLeechMin`/`offensiveLifeMin`; `svc_hunt_rundown` inherited flash powder's 12-entry
  > `offensiveConfusionChance`/`offensiveFumbleMin`/`offensiveProjectileFumbleMin`, its flat pierce
  > ladder, AND its white-burst `radiusEffectName` + head attach point + powder cast sound, i.e. the
  > exact audiovisual signature of the skill it replaces. `svc_hunt_quarrysmark_buff` KEEPS the
  > donor's resist shred (marked prey takes the spear harder IS this skill's identity) but on a
  > DESIGNED 3-entry ladder instead of Study Prey's inherited 12-entry one, which `skillLevel [1,2,3]`
  > was reading at its three weakest steps. The lance's `maxDistance` was also raised from the
  > donor's 18 to 22 to cover the LongRange band he is actually told to cast it in, with a gate.
  >
  > **ADDITION 2 - PLAYER SURFACE for the new skill CLASS (process law #3).** Round 1's checklist
  > covered Runbreaker only. "Quarry's Mark", "The Long Reach" and "Run Them Down" existed ONLY in
  > `FileDescription`, a dev-only field, while `svc_hunt_quarrysmark_buff` (which is `debufSkill=1`
  > and therefore lands on the PLAYER's status bar) read "Study Prey" with a description about pierce
  > damage that is not what it does. All four records now carry mod-authored `tagSVCHunt*` name and
  > description tags, gated fail-loud both ways (right tag on the record, tag present in the Text
  > set). REMAINING AND DISCLOSED, NOT FIXED: the two monster-only actives still inherit their
  > donors' icons and sounds (`svc_hunt_longreach` = Life Drain's NegativeEnergyRay icons and
  > lifedrain cast/hit sound paks). They have no UI surface on a monster, and no report from this
  > lane claims how they sound. BL-b98-DEBT-10.
- R-95 [2026-07-28] IMPLEMENTED-IN-DATA b98 (feat/endless-hunt), IN-GAME LOOK NOT CONFIRMED, verbatim fragment: the Enslaver should have
  **"the same black shroud smoke his summoned demons have"**.
  THE FINDING THAT CHANGED THE TASK: he ALREADY carries it. `um_toxeus_enslaver_99` has
  `charFxPakRunningNames = drxshadowcloakrunning_fx_pak` - the SAME pak, the SAME EffectEntity, that
  `um_enslaver_marauder_99` carries; only 14 records in the whole DB carry that field and he is one
  of them. So the ask was "make the FX he already has actually show".
  CAUSE: `charFxPakRunningNames` renders ONLY while RUNNING. The marauders are melee chasers that run
  constantly; the Enslaver is a caster (spell-cast speed 2.0, full armour, run 1.5) who stands and
  casts, so his running FX almost never plays. A bone mismatch was the first hypothesis and it is
  ELIMINATED from the asset bytes: Bone_R_Weapon and Bone_L_Weapon both exist on RevenantPoison.msh.
  FIX: `charFxPakSelfNames` is the PERSISTENT channel and is a SKILL field, never a Monster field
  (184 carriers, zero of them Monster-class), so the shipped way is a self-buff SKILL - exactly what
  R-7 did for the Devourer. `tools/patches/enslaver_shroud.py` authors `svc_enslaver_shroud`
  (Skill_BuffSelfToggled cloned from the ONE zero-payload self-buff toggle in that namespace, so it
  carries NO combat payload, with the donor's purple weapon tint zeroed to the inert NO-TINT default)
  plus its CharFxPak, and wires it into a FREE skill slot. NO SKILL WAS DROPPED: the brief assumed
  all 12 of his slots were full and one would have to be sacrificed under R-26's spirit - ground truth
  is he uses skillName1..18 and the template reaches at least 23, so slot 19 was free all along. His
  `charFxPakRunningNames` is kept, so he smokes harder when he moves and still matches his marauders.
  COLOUR: the ONLY in-game-CONFIRMED black in this area is the shadowcloak smoke Will has SEEN on the
  marauders, so that is the only asset used - never `343_dark_smoke`, which R-10 itself calls
  green-rendering and which no one has confirmed. Gated: the shroud pak may reference nothing else.
  > ⚠️ **SHAPE CORRECTED 2026-07-29 (round 4, adversarial-vet finding).** Rounds 1-3 got the COLOUR
  > half right and the SHAPE half wrong, and no gate noticed because every gate checked particle
  > IDENTITY and none checked emission SHAPE. The new pak was cloned wholesale from the
  > `343_weapon_poisoncharfxpak` structure and kept its `particleEffectAttachPoints = 'R Hand';'L Hand'`,
  > so the Enslaver would have smoked from two FISTS while his marauders smoke from the whole BODY -
  > the demons' own `drxshadowcloakrunning_fx_pak` carries ONE particle and NO attach points at all.
  > "The same black shroud smoke his summoned demons have" means the same shape as well as the same
  > colour. The pak now mirrors the demons' exactly (one body emitter, zero attach points), and
  > `verify()` DERIVES that expectation by reading the demons' live record, so the two cannot drift
  > apart silently. Convention check made before changing it: of the 294 resolvable
  > `charFxPakSelfNames` references in the DB, **248 point at an attach-free pak** and 46 at one with
  > attach points; 86 of the 131 CharFxPak records omit the field entirely and none carries an empty
  > one, so the field is REMOVED rather than blanked. Four new planted negatives cover the shape
  > (hands-only, duplicate emitters, and the reference itself drifting or vanishing): 10/10 caught.
  ⚠️ NO REPORT FROM THIS LANE CLAIMS HE READS BLACK IN GAME. b92 proved from asset bytes that
  `RevenantPoison.msh` - the mesh he wears in the deployed arz - has a GREEN aura compiled into the
  mesh file at his waist. Black hand-smoke over a green waist aura will not read black. That mesh work
  belongs to the green-diff lane and turns on a Will answer (BL-b98-DEBT-2).
- R-96 [2026-07-27] IMPLEMENTED b98 ROUND 3 (feat/endless-hunt, 2026-07-29), verbatim fragment:
  the roaming Endless Hunt's target rate is **"roughly one sighting per act"**. He was offered three
  options and picked this one over both **"a few per act"** and **"frequent stalker"** - so the
  intent is near-mythical but no longer effectively invisible: reliably met once or twice per
  playthrough, never.
  PROVENANCE, stated honestly: this reached the lane through the orchestrator's brief, which dated
  his answer 2026-07-27 and rendered it as the fragment above; there is no raw transcript line in
  this repo, and the question it answers (`BL-b98-DEBT-5`, report section 10 Q3) was filed 07-28.
  The wording is recorded exactly as received rather than smoothed. Same convention as R-91.
  CLASS: **WILL-VETO** (the R-18 precedent - a rate change on these champions is Will's call, never
  an implementer's). This ruling CLOSES `BL-b98-DEBT-5`, which recorded the rate as deliberately
  NOT taken pending exactly this answer.
  WHAT WAS WRONG: the sweep appended him at a FLAT weight 1 against pool totals of 36,000..660,000.
  Measured against the built arz + the shipped `world01.map`, that is **0.0368 expected sightings
  per full Act IV+V pass - ONE PER 27 PLAYTHROUGHS**. That, not any difficulty gate, is why Will met
  him once on Epic and never on Normal (see R-90 and the "Hades-only myth" correction). A flat
  weight was ALSO 18.3x unfair between areas, because the natives are x600-scaled by different
  amounts - he was 18x rarer in Rhodes than in the Hades Palace for no design reason.
  THE FIX: his slot weight is NORMALISED PER POOL to hit a constant per-draw probability
  `_LS_TARGET_P_SLOT = 1/1250` (`tools/patches/toxeus_suite.py`, one named constant with the whole
  derivation beside it - retune him there and nowhere else). Shipped weights are 29..528 per pool
  (median 53), and the realised p_slot spread across all 345 pools collapses from 18.3x to 1.016x.
  THE ARITHMETIC (measured 2026-07-29, not estimated - full per-area table in
  `docs/reports/b98_endless_hunt.md` section 12): 345 roaming pools, mean 3.19 main draws per
  resolved pool, all 539 referencing proxies at chanceToRun 100, and the shipped map places them
  **797 times** (Act IV: Rhodes 54 + Medea 134 + Epirus 69 + Styx 149 = 406; Act V: Judgement 175 +
  Elysian 131 + Hades Palace 85 = 391) = 2,486 effective draws per pass.
  `E = SUM over placements of chanceToRun * (1-(1-p)^k)`, with limitN=1 capping each placement at 1.
  RESULT, read back out of the SHIPPED bytes: **ACT IV 0.955 sightings, ACT V 1.034, full pass
  1.989** - 54x the shipped rate, and "roughly one per act" in both acts rather than on average.
  HE IS FAR RARER THAN THE NATIVES (weight 53 against natives carrying 18,000 each).
  > ⚠️ **CLAIM CORRECTED 2026-07-29 (round 4, adversarial-vet finding, re-measured off the built
  > arz).** Round 3 wrote "still the rarest member of EVERY pool". **False in 63 of the 346 pools he
  > rides:** in those, `um_toxeus_enslaver_99` is also a member and is still on the OLD FLAT scheme at
  > weight 1 (p_slot 1/60,049..1/66,054), so the Hunt at ~1/1,250 is now **48-53x MORE common than
  > the Enslaver** in every pool they share. The other pools' "rarer" rows are weight-0 inert members
  > (checked; 0 live). Nothing about R-96 is invalidated - it normalised the HUNT only - and the
  > Enslaver's sweep rate is WILL-VETO under **R-18**, so this lane deliberately did not touch it.
  > But the apex Hunt now shows up ~50x more often than the champion he is meant to stand beside,
  > which is a question for Will rather than a fact to bury: **BL-b98-DEBT-11**.
  DELIBERATELY UNCHANGED: the pool SET (still the same 345), the x600 self-scaling, the `limitN=1`
  structural cap, and the FIXED Hades Palace encounter, which stays a guaranteed p_slot of 1.000.
  GATE: the old gate asserted `weight == 1` plus a 1/2400 ceiling, which this ruling reds by
  construction, so it was REPLACED (not loosened) in the same commit by the stronger invariant the
  new scheme guarantees - every pool must realise the SAME p_slot within +/-4% (integer rounding).
  8 planted negatives, all caught, including "the flat weight 1 comes back" and "ONE pool misses
  normalisation".
- R-60 [2026-07-04] STANDING "Will's decision, 2026-07-04 - no Lite build" - KEEP DRX (Dragonlord's
  visual overhaul) in the shipped mod; `-LiteMode` is off the table (it strips assets the blood cave
  itself needs). Keeping DRX keeps Dragonlord's permission on the Workshop-publish critical path.
  Source: docs/STEAM_RELEASE.md:33 (the verbatim string); docs/SHARE_AND_PLAY.md; docs/PERMISSIONS.md; CLAUDE.md content-gaps section (same ruling,
  multiply cited).
- R-61 [2026-07-10] STANDING "he said it was cool" (Will relaying soa's verbal permission) - soa
  (SVAERA author) granted verbal permission for the additive mastery-graft reuse (R-28); a written
  confirmation is still an open standing obligation, as is amgoz1's and Dragonlord's written
  permission (neither captured in writing as of 2026-07-10). Source: docs/PERMISSIONS.md.

### Global balance & progression (new section; decade 80-89)
- R-80 [2026-07-27] IMPLEMENTED b93 (feat/death-xp-penalty) verbatim: "also i want to drastically
  reduce the xp penalty for dying. at high levels the penalty is way too crazy, it needs to be cut
  by like 90%" - the on-death EXPERIENCE penalty, cut to exactly 10% of its vanilla value across
  every level and every difficulty. MECHANISM (found in the deployed bytes, not assumed):
  `Game.dll` hard-codes exactly ONE GameEngine path in the whole install - the literal
  `Records/XPack/Game/GameEngine.dbr` - and reads three fields off it: `deathPenaltyEquation`,
  `deathPenaltyMin`, `deathPenaltyMax`. There is no flat-vs-percentage split and no per-difficulty
  variant record: difficulty enters only through the `gameDifficultyDV` term (0 Normal / 1 Epic /
  2 Legendary) inside the one equation. FIVE other records in the arz carry `deathPenalty*` fields
  (`xpack\game\drxgameengine`, `xpack\game\copy of gameengine`, `xpack\game\xxxgameengine`,
  `game\gameengine`, `game\cost backup\gameengine`) and the engine loads NONE of them - the last one
  even carries a different formula (`^2.95 * (1+2*DV)/3`), a decoy that would have been the wrong
  target. BEFORE (pure vanilla TQAE - byte-identical in base TQAE, SV 0.98i, SV 0.9, SV 0.41 and the
  deployed DEV arz `1c27d5fa`; no prior ruling and no pipeline writer ever touched it):
  `deathPenaltyEquation = "(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 9)"`,
  `deathPenaltyMax = 500000`, `deathPenaltyMin = 0`. AFTER:
  `deathPenaltyEquation = "(currentPlayerLevel^3) * ((1+ (3 * gameDifficultyDV)) / 90)"`,
  `deathPenaltyMax = 50000`, `deathPenaltyMin = 0` (UNTOUCHED). The divisor `9 -> 90` is exactly
  x0.1 with no new token for the engine's equation parser to accept; the cap moves in lockstep
  because the penalty is cubic and the OLD 500000 cap already bit above ~L86 on Legendary, so
  scaling the equation alone would have delivered only -84% at L100 - less than the ruled 90% in
  exactly the high-level regime the ruling names. WORKED EXAMPLE (shipped curve
  `E(L) = 65*(L+1)^3.25`): L40 Legendary 49,778 -> 4,978 XP; L60 Legendary 168,000 -> 16,800;
  L85 Legendary 477,653 -> 47,765 (10.2% -> 1.0% of a level band; ~375 -> ~37 same-level trash
  kills). SCOPE: two fields on one record, nothing else - `experienceEquation` (XP GAIN), the level
  curve `records\creature\pc\playerlevels.dbr` and all five dead lookalikes are proven unmoved.
  Implemented as registry module `tools/patches/death_xp_penalty.py` (deterministic, idempotent,
  scope-proving `apply()` + `verify()` re-asserting on the FINAL merged arz) and gated permanently by
  the new contract domain `tools/contracts/contracts_balance.py` (BAL-DEATHXP-1/2/3 + BAL-XPGAIN-1,
  26 planted negative tests in `tests_balance_negative.py`). MULTIPLAYER: shared DATABASE record, no
  party-size term, no `/`-in-spawn-equation hazard - co-op behaves exactly like single-player at the
  new rate. Report: `docs/reports/b93_death_xp_penalty.md`.

---

## LEDGER HYGIENE PASS (2026-07-28, branch `fix/debt-docs`)

One-line summary: **two colliding R-numbers renumbered, six stale statuses flipped to IMPLEMENTED,
zero records deleted.** No ruling text was altered; every change is a status/id correction with the
evidence named inline.

**ID COLLISIONS (the b84 backfill reused two live numbers).** A number in use is NEVER reused or
reassigned, so the LIVE ruling kept its number and the BACKFILL entry moved into the next free slot
of its own reserved decade:
- backfill "R-13" (parchment-room Toxeus retirement) -> **R-19** (Toxeus decade 1-19). The live
  R-13 is the Rite-of-the-Undivided on-kill drop. R-14's `SUPERSEDED by` pointer and the
  `docs/reports/b90_toxeus_souls_100pct.md` cross-reference were updated with it.
- backfill "R-43" (tomb-guardian de-soul) -> **R-70**. The live R-43 is the Blood Cult High Priest
  summon. It did NOT go to R-49: the parallel `fix/devourer-chest` lane claimed R-49 on 2026-07-27
  for a live Will ruling (the Devourer chest-spawn repeat, IMPLEMENTED b91), which fills the Souls
  decade 40-49 - so this pass allocated the **Souls & items OVERFLOW decade 70-79** and took R-70.
  Checked against that branch before choosing: it uses nothing in 70-79, so the two ledgers merge
  without a new collision. The DEBT REGISTER line "Tomb Guardian soul leak - RESOLVED" was updated
  with it. **NOTE for whoever merges the two lanes:** `fix/devourer-chest` still carries the OLD
  duplicate `R-13` pair, since it branched before this pass - take this branch's R-19 renumber.

**STATUS FLIPS.** The BUILD47 GATE RECORD (docs/BACKLOG.md, 2026-07-17) merged `feat/black-poison`,
`fix/soul-tiers`, `fix/formula-names`, `fix/mastery-unlock`, `fix/runtime-green` and
`fix/bloodtoxeus-spawns` into main - re-verified here with `git branch --merged main` (all six
present) plus the shipped owner module for each. PENDING -> IMPLEMENTED: **R-7** (b83), **R-9**
(b83), **R-13** (b83), **R-11** (b81), **R-24** (b77), **R-40** (b78). Status clarified without a
state change: **R-41** (b80) and **R-43** (b85) were already IMPLEMENTED but carried branch-only /
"pending merge" qualifiers that the build47 merge made stale. The matching DEBT REGISTER lines were
struck through in the same commit.

**DELIBERATELY NOT TOUCHED (owned by the parallel `fix/devourer-chest` lane):** **R-1**, **R-3**,
**R-4** - the Blood-Toxeus entourage, the 100% hidden-chest spawn and the chest/quest renames. Their
statuses stay exactly as that lane left them. Note R-19 above is the ruling whose
`q_bloodtoxeus_lone_50` retirement R-3 blames for the lost chest spawn; read both together.

**RE-VERIFIED AND LEFT PENDING (with the evidence recorded inline on each ruling):** **R-30**,
**R-31**, **R-32** (`fix/chumbi-lag` IS merged, but build46 shipped only b76 round 1 - the spacing
gate is unbuilt, the quest-chest reuse is untouched, and R-31's remaining blocker is Will's in-game
confirmation, not missing code) and **R-39** (`feat/coldworm-uber-markers` is an ancestor of main but
its tip carries only BACKLOG doc commits - "branch merged" is NOT evidence the Cold Worm work
shipped). **R-10** and **R-16** were re-read and are correctly PENDING as written.

**RETIREMENT PROTOCOL:** nothing was deleted, retired, or dropped in this pass. Every superseded /
renumbered record is still present with a pointer to its replacement.
### Encounter economy / blood cave (new section, decade 72-79)

> ⚠️ PROVENANCE NOTE (honesty, per the ledger's own "quote rulings VERBATIM" law): the three
> entries below were relayed to the b94 implementer through a design brief, NOT captured as a
> first-person Will quote. They are therefore marked `[paraphrased]` in the same way R-33/R-34/
> R-35 are, and each records exactly what the brief asserted plus what the implementer proved
> against the shipped bytes. If Will's original wording surfaces, replace the paraphrase with the
> verbatim text in place and drop the marker.

- R-72 [2026-07-28] IMPLEMENTED b94 (feat/leinth-wave) [paraphrased] "the orb the two Toxeus
  champions drop is not the same calibre as the one Leinth drops" - CONFIRMED against the deployed
  bytes, and by a wide margin, though not by the mechanism the wording assumes. Neither side drops
  "an orb" in the same sense: Leinth drops a BESPOKE DRX CHEST
  (`records\drxitem\container\bosschestproxy_leinth.dbr`, in-game "Leinth's Essense"), while BOTH
  champions drop the R-47 shared generic apex orb `genericbossorb_04`. The delivery field is
  `treasureProxyName`, the only field in all 51,085 records that ever references an orb. Tracing
  both chains proxy -> ProxyAccessoryPool -> FixedItemContainer -> FixedItemLoot on all three
  difficulties, the raw knobs are: numSpawnMin/Max `(3+1.6P)*2.2 / *2.4` (Leinth) vs `*0.9 / *1.3`
  (orb04); loot4Chance 100.0 vs 12.7; unique-entry lootWeight 50 vs 27. Modelled expected items at
  1 player: Leinth 18.5 vs orb04 5.7 (3.25x) with roughly twice the unique share. HONEST
  COUNTER-AXIS, stated because it cuts the other way: orb04 rolls the HIGHER item tier (the xpack
  Act-4 statics at goldGeneratorLevel 88, plus LockedClassification=Boss) while Leinth's tables are
  the Act-3 63-65 band at gold level 64. FIX: do NOT nerf Leinth (explicit instruction) and do NOT
  edit `genericbossorb_04` in place (it is shared by TWENTY-ONE boss records, so an in-place edit
  would silently buff the mod's whole endgame). Instead author a NEW un-named generic apex TIER
  `genericbossorb_05` (+ 3 pools + 3 chests + 3 loot tables, every one a clone of the orb04 chain)
  carrying Leinth's four calibre knobs on the champions' EXISTING higher Act-4 tables, and repoint
  `treasureProxyName` on EXACTLY `um_toxeus_enslaver_99` + `um_bloodtoxeus_99`. Net: champion orb
  goes from ~5.7 to ~18.5 expected items at 1P on a strictly better item pool. Owner:
  `tools/patches/uber_apex_orb.py` (apply() proves roster-wide that orb04 and its other 19
  consumers are byte-unchanged and that the R-48 soul wiring never moved; verify() re-asserts the
  whole chain on the FINAL merged arz). Planted negative test
  `tools/debug/negtest_uber_apex_orb.py`.
  RECONCILIATION WITH R-47: R-47's substance is intact (still un-named, still generic, still
  shared, still not a bespoke "X's Essence"); R-72 ADDS a tier R-47 does not mention. R-47 is NOT
  superseded.
  ⚠️ **SCOPE SUPERSEDED IN PART BY R-75 (Will 2026-07-27, verbatim).** R-72's ANALYSIS stands
  unchanged and is still the evidence base. What R-75 overrides is R-72's SCOPE DECISION: R-72
  moved only the two champions and deliberately left Leinth's chest untouched, and R-72's open
  question #3 ("should Leinth also get an orb?") is now ANSWERED - yes, she is included. The
  built-out ruling is R-75; read the two together.

- R-75 [2026-07-27, implemented b94 round 2 (feat/leinth-wave)] IMPLEMENTED. Will's decision,
  **VERBATIM** (this one WAS captured as a first-person quote, unlike R-72/R-73/R-74 above, so it
  carries no `[paraphrased]` marker):
  > "increase the tier of the items dropped by leinth's orb to match the tier dropped by the
  > champions' orb and give that to both toxeus variants and also to leinth"

  This SUPERSEDES the design pass's orb plan and R-72's scope. The instruction is not "raise the
  champions to Leinth" but "build ONE apex drop that combines both sides' strengths and give it to
  all three". Each side won a different axis: Leinth had the GENEROSITY (numSpawn `*2.2/*2.4` vs
  `*0.9/*1.3`, loot4Chance 100 vs 12.7, unique weights 50 vs 27) and the champions had the TIER
  (xpack Act-4 static tables vs the Act-3 63-65 band; `containerlevelequation_all` = `1*1` vs
  `c03`/`e_c03`, which DIVIDE the player level on normal/epic; goldGeneratorLevel 47/69/88 vs
  30/50/64). The shared apex loot tables `records\item\loottables\svc\svc_uberorb_apex_{n,e,l}01c`
  carry Leinth's four generosity knobs on the champions' Act-4 tables, and ALL THREE bosses now
  consume them: modelled expected items at 1 player go 5.70 -> 21.16 for each champion (3.71x) and
  18.51 -> 21.16 for Leinth (1.14x) PLUS a full item tier and +56% gold level.

  HOW LEINTH IS INCLUDED, and why not by repointing her: a whole-database scan of EVERY field of
  ALL 51,085 records proves `bosschestproxy_leinth` has EXACTLY THREE referrers, and all three are
  her own variants (`q_leinth_47/49/50`, `treasureProxyName`). She SOLELY OWNS her chain, so it is
  upgraded IN PLACE - `tables` + `levelEquationFile` on her three chests, two fields each, nothing
  else. Her monster records, her proxy and her pools are NOT touched, so R-73's "her bespoke chest
  survives" assertion stays green by construction, and the RETIREMENT PROTOCOL is never engaged
  (nothing of hers is retired; her three original loot tables are deliberately left in the db and
  are what the gate reads as the no-nerf reference). She KEEPS her bespoke player-visible identity
  (`DRX\meshes\leinth_chest.msh`, scale 1.2, `tagLeinthChest` = "Leinth's Essense") and she KEEPS
  her `typhongoldgenerator`, which is RICHER than the champions' `bossgoldgenerator`
  (`(L^1.6)*48` vs `(L^1.6)*24`) - switching her to theirs would have been a gold NERF, so it was
  deliberately not done. `LockedClassification` was also deliberately not copied: it is not an
  item-tier field and is inert while `locked = 0`, which every consumer including orb04's own
  chests carries.

  NO-NERF IS PROVEN, NOT ASSERTED: apply() refuses to move her at all unless the apex table beats
  her original on every one of the six loot-group chances, both spawn multipliers and
  goldGeneratorLevel, and verify() recomputes the same proof on the FINAL merged arz. It holds on
  all three difficulties (12.5->13.0, 25.0->32.0, 0.0->10.0, 100.0->100.0, 25.0->32.0, 12.5->13.0).
  Owner: `tools/patches/uber_apex_orb.py`; planted negative tests for the Leinth half are
  `negative 9-14` in `tools/debug/negtest_uber_apex_orb.py`.
  RECONCILIATION WITH R-47: still intact. No NEW bespoke "X's Essence" is authored; her existing
  one is re-tiered, not created, and the champions' new tier is still un-named, generic and shared.
  See docs/reports/b94_leinth_wave.md.

- R-73 [2026-07-28] IMPLEMENTED b94 (feat/leinth-wave) [paraphrased] "Leinth is too easy and her
  fight has nothing to react to; make her stronger and give her more abilities" - all three
  variants (`q_leinth_47/49/50`) get characterLife +60% (32,481/35,703/38,924 ->
  52,000/57,000/62,000), defensivePhysical 10 -> 35 and defensivePierce 20 -> 45 (THE REAL LEVER:
  her two passive packages already give her bleed 100 / life 160 / convert 100 / elemental 50 /
  stun 100, so physical and pierce were the only damage that touched her), characterAttackSpeed
  0.8 -> 1.0, characterRunSpeed 1.0 -> 1.15, characterLifeRegen 2 -> 10, and her EXISTING poison
  geysers (`cerberus_crackfire`) raised 1;4;7 -> 4;7;9. DELIBERATELY KEPT: defensivePoison stays
  -15 (her amgoz1 identity and the fight's counter-play) and charLevel stays 47-76 (she is the
  blood cave's main-path terminal boss, NOT an uber; pushing her to the champions' 100 would break
  the cave's curve). THREE new abilities, every donor an already-shipping rig from her OWN
  `records\drxcreatures\bloodwitch` cult family, so zero new art/FX/sound: CRIMSON TITHE (the
  Disciple blood-rain -> specialAttack5, the fight's first telegraphed phase moment), CHOIR OF THE
  BLOODBORN (the Disciple-boss Melinoe summon, cut to burst 2;3;4 / petLimit 6 with a finite TTL ->
  buffSelfSkillName) and SANGUINE MIRE (her own SpawnPet rig spawning the Seductress blood puddle
  -> dyingSkillName). WHY THREE AND NOT FOUR (engine ceiling, not a cut): Monster.tpl exposes
  exactly five castable specialAttack slots and Leinth already used four with her own bespoke DRX
  kit, so there was ONE free attack slot plus the two non-attack AI mechanisms with class
  precedent (buffSelf: 9 SpawnPet users; dying: 18 Boss users). A fourth would have had to displace
  one of her own DRX skills, which the retirement protocol forbids without Will.
  ALSO: `leinth_summon_uglies` cut from petBurstSpawn 4;6;8 / petLimit 16 (permanent) to 2;3;4 /
  petLimit 6 with a 45s TTL - the b76 chumbi-freeze density law; the skill is NOT removed and stays
  wired at specialAttack2. NOT TOUCHED: every loot field (her 100% `lenithsveil` head drop, her 66%
  soul at the R-42 PLACED rate, and `bosschestproxy_leinth`), proven field-by-field in apply().
  Owner: `tools/patches/leinth_wave.py`; planted negative test
  `tools/debug/negtest_leinth_wave.py`. ⚠️ OPEN WILL QUESTIONS in the wave report: the two staged
  poison rigs DRX left unwired in her own folder (`cerberus_acidpuddle_summon/attack`) were
  REJECTED as off-identity (poison, on the one boss with a poison weakness), and the Normal-band
  difficulty of the +60% life needs a play check.

- R-74 [2026-07-28] IMPLEMENTED b94 (feat/leinth-wave) [paraphrased] "after you kill Leinth a
  portal should open that takes you back to the occultist merchant outside the blood cave" - the
  machinery was ALREADY built, placed and correctly aimed; one trigger asymmetry stopped it firing.
  `records\drxmap\bloodcave\portals\vortexportal_exit.dbr` is Class=Npc (the traveler/boat-dialog
  pattern) whose own FileDescription reads "Exits the player after the Leinth boss fight", placed
  exactly ONCE across all 2,282 levels (bossfight.lvl, 6.2u from Leinth's proxy, on-navmesh); Text
  already resolves tagLeinthExitPortal = "Mystical Vortex" and tagReturnFromLeinthBattle = "Leave
  the Sanctuary of the Bloodborn?"; and its shipped BoatDialog destination decodes signed to world
  (-90,-103,2321), which is 9.79u from the OCCULTIST MERCHANT outside the cave, on the same
  walkable component as the merchant and his wagon. THE DEFECT: only the ONE-SHOT
  `Condition_KillAllCreaturesFromProxy(q_leinth_lone)` primary carried the full
  OpenDoor+ShowNpc+UpdateNPCDialog+BoatDialog set, while the three `Condition_KillCreature`
  fallbacks added in b48 carried Action_OpenDoor ALONE. So whenever the proxy-wide condition did not
  satisfy (an unaccounted champion blood demon in that pool, a character that did not have the quest
  tracked at kill time, or the one-shot already latched) the boss door opened and no exit portal
  ever appeared. FIX (Quests.arc ONLY, `tools/build_quest_files.py::_promote_leinth_exit_fallbacks`):
  copy the primary's action block VERBATIM onto all three resettable fallbacks and flip the
  primary's isResettable 0 -> 1. No new quest entry, so the ~254-entry load window is NOT engaged
  and the QUESTS section is unchanged; Levels.arc is BYTE-UNCHANGED. Lands in CANONICAL, not
  TESTHUB-only: bossfight.lvl is SV-native in both map variants, the NPC is an SV-native placement,
  and Quests.arc is variant-independent. The Typhon FixedItemTeleport alternative was evaluated and
  REJECTED (it would need two new records plus two new PLACEMENTS and a two-blob Levels rebuild, and
  re-enters the map-portal firing-risk class this project left behind). Permanent gate:
  contract `QST-LEINTH-EXIT` in `tools/contracts/contracts_quests.py` + 6 planted negative tests in
  `tools/contracts/tests_quests_negative.py`. ⚠️ OPEN WILL QUESTIONS in the wave report: the offer
  is one-way (recommended), and a character who already killed her while the one-shot was latched
  and never kills her again is still stranded until a re-kill.

- R-76 [2026-07-27, implemented b94 round 3 (feat/leinth-wave)] IMPLEMENTED. Will answered the four
  design questions R-73 left open. Three of the four answers go AGAINST the implementer's
  recommendation, so R-73 is **SUPERSEDED IN PART** by this entry (its stat work stands; its summon
  cut, its poison-weakness law and two of its three new skills do not). Will's answers, VERBATIM:

  * **Q4, how much stronger:** *"lets give her some guardians like amgoz1 gave hades"*
  * **Q6, the two staged poison rigs:** *"Use them AND remove her poison weakness"*
  * **Q7, the ugly swarm:** *"Keep the swarm as-is"*
  * **Q9, the residual stranded character:** add the no-kill fallback - *"Show the exit whenever the
    boss trap door is already open, regardless of whether the kill trigger latched - so a character
    who already killed her (INCLUDING WILL'S OWN) is rescued rather than stranded."*

  **Q4 - THE HONOUR GUARD, MIRRORED FROM THE REAL THING.** How amgoz1/DRX actually built Hades'
  guardians was traced in the shipped bytes before anything was designed:
  `records\xpack\quests\proxies\main\xq06_boss_hades_champions.dbr` (FileDescription "DRX") is a
  SEPARATE proxy from the boss proxy `xq06_boss_hades.dbr`, carrying the GUARD's own mesh
  (`gigantes01_quest.msh` at scale 2.8), sharing the boss's `hadesdifficulty_01` / `bosslimit_all`,
  `quest = 1`, and pointing at `xq06_boss_hades_champion_pool.dbr` (also "DRX"): `spawnMin =
  spawnMax = 1`, `championMax = 1`, `limit1 = 1`, `name1 =
  records\drxcreatures\drxdishonorguard\anapaest_45.dbr`, `weight1 = 100`. A placement census over
  all 2,282 levels finds that champion proxy placed exactly **TWICE**, both in
  `XPack\Levels\Area08_HadesPalace\HadesPalace_Floor05_04.lvl`. So the pattern is: one dedicated
  elite guard record, spawned from its OWN pool, standing beside the boss, two of them, invisible to
  the boss's own quest proxy.
  The literal mirror would need two new PLACEMENTS in `bossfight.lvl` (a Levels.arc rebuild). It was
  NOT taken, because this repo already ships the DB-side equivalent and **its donor is literally
  Leinth's own pool**: `apply_svc_patches._svc_boss_pool` is documented as "the 1-boss +
  2-guaranteed-champion recipe (spawnMax=3 / championChance=100 / championMin=Max=2 -> 3-2=1
  guaranteed boss; the LAW)", shipping in `neferkha` (2 frozen tomb guardians), `diadochi` (2 strider
  guards) and the Hades Marshal (2 machae escorts). Applied to `q_leinth_lone` IN PLACE: her three
  variant `name` slots, weights and limits are untouched, so the single main is still a random
  `q_leinth_47/49/50`, and the two champion slots become her honour guard. **Levels.arc is
  BYTE-UNCHANGED.**
  `_svc_neutralize_pool_equation` is MANDATORY here, not cosmetic: her pool inherits
  `proxypoolequation_02`, which scales the literal counts by 1.357 and floors them, giving spawnMax
  4 and championMax 2, so 4-2 = **TWO Leinths side by side** - the exact deterministic defect Will
  reported on 2026-07-13. verify() fails the build if that equation ever comes back.
  THE GUARDS (amgoz1 bar: zero new art, FX or sound - both cloned from her OWN cult):
  `svc_leinth_guard_reaver` from `d_reaver_42` ("Blood Reaver of the Sanctuary"; bloodburst +
  bloodboil + sux2buwave + zap, and NO summons at all) and `svc_leinth_guard_disciple` from
  `c_disciple_42` ("Voice of the Bloodborn"; the bloodstare + blood-rain caster). Both raised to HER
  band `[47,62,74]`, Champion rank, scale 1.9, real Text names. The Disciple's inherited
  `disciple_summon_bloodbeast` is petLimit 4 with NO TTL - the exact b76 defect - so the guard gets a
  CLONED copy capped at 2 / 20s and the SHARED original is never written (verify() asserts both).
  EXIT-TRIGGER INTERACTION, deliberate: the guards ride in `q_leinth_lone`, which is the pool R-74's
  primary `Condition_KillAllCreaturesFromProxy` watches, so the primary now needs the whole honour
  guard dead. That is the right reading, and it is exactly why R-74's three per-variant fallbacks
  plus this entry's no-kill fallback are load-bearing rather than belt-and-braces.

  **Q6 - BOTH STAGED RIGS WIRED, AND THE WEAKNESS REMOVED.** R-73 rejected
  `cerberus_acidpuddle_{summon,attack}` as off-identity (poison rigs on the one poison-weak boss);
  Will removed the contradiction from the other end instead. All THREE records DRX staged in her own
  folder (`summon` / `monster` / `attack`) have ZERO referrers anywhere in the 51k-record db, proven
  by exact-path scan rather than substring. THE FREE WIN: the "attack" rig is not a boss self-buff
  competing for a scarce cast slot, it is the PUDDLE's own aura (the xpack twin sits at the puddle
  monster's `initialSkillName` + `skillName1`), so wiring the SUMMON alone brings BOTH of Will's rigs
  live through ONE `specialAttack` slot. Her summon is therefore re-chained onto HER puddle and that
  puddle onto HER aura (DRX had aimed both at the xpack copies), leaving the xpack Cerberus chain
  `boss_cerberus_40/42/44` byte-clean - verify() fails if either xpack record is ever repointed.
  `defensivePoison` **-15 to +15**. The value is not invented: it is EXACTLY her own cult heavy
  `d_reaver_42`'s `defensivePoison`, so she is anchored to her family's norm. It removes the weakness
  (no more bonus poison damage) and makes her coherent now that she wields both the geysers and the
  puddles, while deliberately NOT granting immunity - at +15 poison is still by far her softest
  resist (bleed 100 / life 160 / convert 100 / elemental 50 / stun 100), so the counter-play R-73
  valued survives in relative terms. verify() fails on a negative value AND on immunity.

  **Q7 - THE SWARM IS RESTORED, AND THE RISK IS REPORTED NOT PATCHED.** R-73's cut of
  `leinth_summon_uglies` (4;6;8 / petLimit 16 / permanent, cut to 2;3;4 / 6 / 45s TTL) is
  **REVERTED IN FULL**. The module now writes NOTHING to that record, so it keeps its shipped values
  by construction, and verify() PINS `petBurstSpawn [4,6,8]`, `petLimit 16` and the ABSENCE of a TTL
  - the assertion is now the exact reverse of R-73's. Will was warned that guardians and acid puddles
  are being added on top, and asked for the number; it is measured, not estimated:
  **1 Leinth + 2 guards + 16 uglies (PERMANENT) + 10 heatseeker pets (PERMANENT) + 10 acid puddles
  (6s) + 2 guard bloodbeasts (20s) = 41 concurrent entities, 26 of them PERMANENT.** The b76
  chumbi-freeze RCA measures the standalone offender `um_voranthys_99` at 25 PERMANENT summons
  (petLimit 9 + 8 + 8) and states that even standing alone that "degrades over a long fight".
  **26 EXCEEDS it.** WARNING FLAGGED FOR WILL: nothing he told me to keep was reduced. The only
  density lever pulled was retiring two of the implementer's OWN round-1 skills (below).

  **RETIREMENT (protocol engaged explicitly, because R-73 names them).**
  `svc_leinth_choir_bloodborn` and `svc_leinth_sanguine_mire` are retired. Both were the
  implementer's own round-1 inventions, authored on this unmerged branch and never shipped to Will or
  seen in game, so no player-facing content is removed. CHOIR summoned cult bodies - the HONOUR GUARD
  is Will's own answer to that need and does it better; SANGUINE MIRE existed solely because she had
  no zone control - the ACID PUDDLE is the authentic DRX-staged rig for that job. Their records are
  simply never authored.
  SLOT ACCOUNTING: Monster records expose five castable `specialAttack` slots (census
  3164/1602/894/300/170 users; the only three `specialAttack6` users in the whole db are `Pet.tpl`
  records from our own prior wave, so slot 6 is not a Monster precedent). Her four bespoke DRX
  specials hold slots 1-4 and the retirement protocol forbids displacing them, so there is exactly
  ONE free attack slot. Will's instruction outranks the implementer's invention: `specialAttack5`
  takes the acid rig, and CRIMSON TITHE moves to `dyingSkillName` (79 shipping records carry its
  class there). `numAttackSlots` stays 4 - it is NOT a special-attack cap (46 shipping records run
  `numAttackSlots = 4` with five wired specials, and 3 with six).

  **Q9 - THE NO-KILL EXIT FALLBACK.** The `.qst` condition vocabulary has no door-state test (the
  supported classes are listed in `qst_format.CONDITION_FIELDS`, and none reads a `FixedItemDoor`;
  the primary's `Action_OpenDoor` grants no token either), so Will's literal "whenever the boss trap
  door is already open" is not directly expressible. `Condition_OnLevelLoad` is the only mechanism
  that satisfies his actual REQUIREMENT - that nobody, including his own already-latched character,
  is ever stranded. `tools/build_quest_files.py::_add_leinth_exit_nokill_fallback` appends ONE
  trigger to the "Boss Room Crystal Gate" step carrying `Action_ShowNpc` + `Action_UpdateNPCDialog` +
  `Action_BoatDialog` harvested VERBATIM from the promoted primary, with `Action_OpenDoor`
  deliberately STRIPPED so the boss trap door stays earned. Quests.arc only; no new quest entry, so
  the ~254 load window is not engaged. THE ONE COST, STATED FOR WILL: because OnLevelLoad fires on
  every entry, the vortex is visible from the moment the player walks into the Sanctuary rather than
  appearing at the instant she dies. That trades R-74's reveal for his guarantee; if he prefers the
  reveal, deleting this single trigger restores it and the three kill fallbacks still cover every
  case except the already-latched character he asked to rescue.
  Permanent gate: new contract `QST-LEINTH-NOKILL` in `tools/contracts/contracts_quests.py` + 6
  planted negatives in `tools/contracts/tests_quests_negative.py`. **It fires P0 on the PRE-WAVE
  bytes and is silent on the built bytes** - the fix is proven against real bytes, not asserted.

  Owners: `tools/patches/leinth_wave.py`, `tools/build_quest_files.py`. Negative tests:
  `tools/debug/negtest_leinth_wave.py` (31/31), `tools/contracts/tests_quests_negative.py` (31/31).
  R-NUMBER NOTE: the b94 entries were authored as R-70..R-73 before `main` independently landed its
  own R-70/R-71 in the 2026-07-28 ledger-hygiene pass. On merge the b94 half was renumbered +2
  (R-72..R-76) following that pass's own renumber-on-collision precedent; no ruling TEXT was altered.

  ### ⚠️ R-76 CORRECTIONS (2026-07-29, after an independent adversarial vet returned NO-GO)
  The RULINGS above are Will's and stand unchanged. Three IMPLEMENTATION CLAIMS recorded beside them
  were wrong, and one number was unreproducible. Every correction below was decoded from the
  deployed artifacts, and the corrected state is now gated so it cannot regress.

  1. **"BOTH staged acid rigs live" was FALSE as shipped in round 1.** DRX's staged copy
     `leinth_skills\cerberus_acidpuddle_summon.dbr` carries `skillSpecialAnimationName='AcidPuddle'`,
     a token owned DB-wide only by the xpack Cerberus chain and the DRX Bastien records, and absent
     from EVERY row of her own table `anm_leinth` (unarmed row: SpitSummon, 2, BloodBall01,
     SummonTormentedSouls, TelekinesisLoop, TelekinesisEnd, ThunderClap; her three variants carry no
     own `*SpecialAnimRef`). By this repo's own hard-law #2 the cast ABORTS, and because the poison
     aura lives only on the spawned puddle, BOTH of Will's Q6 rigs died with it. So Q6 was HALF
     delivered: the weakness removal landed, the visible half did not.
     **FIXED (round 2):** the token is repointed to `'SpitSummon'`, which DRX bound themselves at
     `anm_leinth unarmedSpecialAnimRef1 -> empusa_staff_skill_frostspit.anm` and then left
     referenced by no skill of hers - staged in the same breath as the rig. Her copy has zero other
     referrers, so the xpack chain stays byte-clean. verify() now asserts the token.
  2. **The honour guard's summon was a LEVEL-0 SUMMON, which never fires.** Round 1 wrote the
     TTL-capped clone into `specialAttackSkillName` but left `skillName4` on the SHARED donor, so the
     clone had exactly ONE referrer in the whole db and no `skillLevel` anywhere. By the b39 RCA law
     quoted verbatim in `tools/patches/boss_skill_fix.py` ("a level-0 summon NEVER fires ... an
     unambiguous boss never summons defect") the Voice of the Bloodborn lost her entire summon kit,
     and the advertised petLimit 2 / TTL 20s cap was moot.
     **FIXED (round 2):** `skillName4` now holds the clone at the donor's own `[5,10,15]`. gated.
  3. **The geyser raise was NOT a delivered buff.** `cerberus_crackfire` sits ONLY in `skillName13`
     with no cast mechanism of any kind (the original `boss_cerberus_40/42/44` wire it at BOTH
     `skillName4` AND `specialAttack4SkillName`), and its own token `'Roar'` is likewise unbound in
     `anm_leinth`. It is dormant twice over, so R-76's "poison 800/850/950 and the 5% current-life
     component ON at every difficulty" was never true.
     **CORRECTED (round 2):** the raise is REVERTED (the module writes nothing to the slot) and
     verify() PINS the shipped `[1,4,7]`, so nobody can raise an inert number and believe they
     shipped something. It cannot be delivered inside this wave: all five castable slots are spoken
     for and slot 6 has no Monster precedent. Registered as debt `BL-b94-DEBT-12`.
  4. **THREE MORE dead abilities, found by the new roster-wide sweep and fixed.** Adding hard-law #2
     as an invariant over all five records this wave writes (following `charAnimationTableName`, which
     the pre-existing coldworm gate did not do) exposed: `q_leinth_*` specialAttack1 and
     `svc_leinth_guard_reaver` specialAttack1 both on `melinoe_bloodboil` (`'BloodBoil'`, bound
     DB-wide by exactly 2 records, neither of them hers), and the Reaver's specialAttack3 on
     `reaver_zap` (`'Zappity'`, bound by exactly 1). **Blood Boil is her SIGNATURE AoE life-leech -
     the skill her own soul is built around - and it has never fired in this mod.** That is a direct,
     measurable cause of Will's R-73 complaint that she is too easy and the fight is attrition
     sludge, and it is worth more to the encounter than any stat in this wave. Both donors are
     SHARED (20 records / 3 records) so both are CLONED, never written; the clones use
     `'ThunderClap'`, bound in ALL SIX weapon rows of all three tables the wave casts from.
     (Her SOUL is unaffected and was never at risk: `leinth_soul_{n,e,l}` proc the
     `records\skills\soulskills\pcsafe\melinoe_bloodboil.dbr` copy, which has the anim field removed.)
  5. **THE ENTITY BUDGET, RE-MEASURED so Will does not rule on a phantom.** The headline figure is
     unchanged at **41 concurrent / 26 PERMANENT**, but round 1's version was not real: its 10 acid
     puddles could not spawn and its 2 guard bloodbeasts were level-0, so what round 1 would actually
     have shipped is **29 concurrent / 26 permanent**. Round 2 makes the 41 real. The permanent half
     is 26 either way, because both newly-live rigs are the TTL-capped ones. The b76 comparison and
     the flag to Will are therefore UNCHANGED: 26 permanent still exceeds `um_voranthys_99`'s 25, and
     she now also peaks 12 transient bodies on top. Nothing Will asked to keep was reduced.
  6. **The `numAttackSlots` census was unreproducible and is CORRECTED.** Not "46 records run
     `numAttackSlots=4` with five wired specials (and 3 with six)". Measured on the deployed arz: 170
     records carry a non-empty `specialAttack5`, split `numAttackSlots` 4 -> **76** and 6 -> **94**.
     Of the 76: 62 `Pet.tpl`, **12 `Monster.tpl`**, 1 `Hades.tpl`, 1 `Megalesios.tpl`. The 12 include
     the base-game `em_monolith_45`, the mod's `boss_coldworm50` and `boss_dagon_66`, and - decisively
     - HER OWN CULT'S `b_seductress_39/41/43`. The conclusion is unchanged and is better proved
     structurally: `numAttackSlots` is defined in `Templates/character.tpl` beside `numDefenseSlots`
     and `combatManagerRecord` (defaultValue 4), i.e. a combat positional-slot count and NOT a
     special-attack cap, while `specialAttack5SkillName` and `dyingSkillName` are both defined in
     `templates/templatebase/monsterskillmanager.tpl`.
  7. **Attribution correction (round 1's COLLATERAL SENTINEL).** The `Skeleton01.msh ->
     RevenantPoison.msh` delta on 12 records and `DisplayAsQuestItem 0 -> 1` were blamed on the
     pre-existing `fix/green-diff` DEV collision. They are in fact written by this branch's own merged
     build code (`tools/apply_svc_patches.py` sets `RevenantPoison.msh`;
     `tools/patches/uber_quest_markers.py` owns `DisplayAsQuestItem`). The CONCLUSION is unchanged
     (not this wave's edits, and no FX/skin/texture/soul-drop field moved), but the attribution was
     wrong and is corrected here so a future vet is not misled.
  8. **Open for Will, not a defect (R-75 companion).** Item parity across the three blood-cave bosses
     is exact, but GOLD parity is not: all three now consume the same `svc_uberorb_apex_{n,e,l}01c`
     tables, yet Leinth keeps `typhongoldgenerator` ((L^1.6)*48) while the two champions keep
     `bossgoldgenerator` ((L^1.6)*24), so a charLevel 74 mid boss still drops roughly twice the gold
     of the charLevel 100 ubers. R-75 records this as a deliberate no-nerf consequence and Will's ask
     was about item tier, so nothing is changed. Flagged for his ruling.


---

## R-98 [2026-07-29] PENDING - the Hunt is exactly 5x the Enslaver in the pools they share

**WILL, VERBATIM (do not paraphrase this into the implementation):**

> "Make the hunt be 5 times as likely to appear than the enslaver in the areas that they share. do not
> adjust the enslaver spawn rates, adjust the hunt spawn rate accordingly. the enslaver spawn rate is
> appropriate currently based on my playthroughs of the game so far"

**SCOPE:** `um_toxeus_hunt_99` (and its Legendary endless variant where it shares a pool) versus the roaming
`um_toxeus_enslaver_99`, in the pools that carry BOTH. b98 measured that set as **63 pools** and measured the
current ratio at **48-53x in the Hunt's favour**, filed as `BL-b98-DEBT-11`. Target is **5x**, so this is
roughly a 10x reduction of the Hunt - the real factor must be DERIVED from the built bytes, not assumed.

**THE ENSLAVER IS FROZEN.** R-18 already forbade changing his rate; Will has now re-affirmed it and given the
reason (his own playthroughs). Any write to an Enslaver weight fails this ruling. Move the Hunt only.

**KNOWN COLLISION, to be resolved with measurement rather than preference:** R-96 gates the build on the Hunt
producing "roughly one sighting per act" (b98: Act IV 0.955 / Act V 1.034 / full pass 1.989 at p_slot 1/1250).
Lowering the Hunt in the shared pools pushes on that figure. Will's wording scopes this ruling to "the areas
that they share", so the shared-pools-only reading is the default, and because the shared set is a minority of
the Hunt's 346 pools the two rulings may well both hold - but that must be MEASURED both ways before anything
is changed. **The R-96 gate must not be loosened to accommodate this change.** A gate relaxed to fit the change
it exists to catch is worthless. If the two genuinely cannot both hold, that is a WILL DECISION with numbers
attached, not an implementer's judgement call.

**STATUS: WITHDRAWN BY WILL THE SAME DAY, BEFORE ANY CODE WAS WRITTEN.** Nothing was implemented. The
Hunt's rate is UNCHANGED and stays as b98 shipped it.

**WILL, VERBATIM (2026-07-29, minutes after giving R-98):**

> "oh ok i didnt know the hunt only had 346 possible pools, since there are so few pools for the hunt we can
> leave the rate higher"

**⚠️ CORRECTION TO THE PREMISE, recorded so nobody re-acts on the withdrawn ruling OR on the misreading that
withdrew it.** 346 is not a smallness. It is the number of ProxyPools that carry `um_toxeus_hunt_99`, spread
across all eight Immortal Throne areas (area001 Rhodes through area008 Hades Palace), reached by 540 proxies.
**The pool COUNT is not the rarity knob** - the rarity is the per-slot WEIGHT inside each pool. Before b98 he
sat at 1 weight against pool totals of 36,001-660,001, i.e. a per-slot probability of about 1/66,667, which
is why Will met him once on Epic and never on Normal. b98 normalised that to about **1/1250**, which is what
produces the "roughly one sighting per act" figure R-96 gates (Act IV 0.955 / Act V 1.034 / full pass 1.989).

**NET EFFECT: the withdrawal and the status quo agree.** Leaving the rate alone IS "leaving it higher", and it
keeps R-96 satisfied. No work is owed. `BL-b98-DEBT-11` (the Hunt sits 48-53x above the Enslaver in the 63
pools they share) therefore stays OPEN as a known, accepted asymmetry rather than a defect - Will has now
declined to close it in the Hunt's direction, and R-18 plus his own playthrough evidence keep the Enslaver
frozen, so there is no remaining lever either side of it.

**IF THIS IS EVER REVIVED:** the design brief is committed at
`docs/wip_workflows/R-98_hunt_enslaver_ratio_5x.js` and is still valid - it measures both readings before
touching a weight and forbids loosening the R-96 gate to fit its own change.

---

## R-99 [2026-07-29] IMPLEMENTED b101 - the apex orb covers EVERY Toxeus variant, not just the two we wired

**WILL, VERBATIM:**

> "i didnt tell you to increase the drop of all the champions, just the toxeus variants (all variants we made
> and didnt make) and leinth. they should drop more items than the normal champions"

**FIRST, THE REASSURANCE, because the wording implies a fear that did not happen.** We did NOT raise all
champions. `uber_apex_orb` deliberately minted a NEW tier `genericbossorb_05` precisely so the shared
`genericbossorb_04` could stay byte-unchanged for its other 19 consumers (Sarkoth, Vashkarr, Bloodcrow,
Voranthys, Broodmother, Gorrahk, Ilsevar, Dagon, Ephialtes, Mnemophage-core, Antaeus, Polis Gaoler, Deep
Thresher, Meglograi, bloodcrow_soul, Dorus, Tantalus, Hades Marshal, Helepolis). The gate proves it, and
negative 8 fires if the orb04 donor chain is tampered with.

**BUT THE RULING EXPOSES A REAL GAP, measured in the merged build (arz `967b1f97137bf6479c18c08e9dd6ffc4`,
51,124 records) - only TWO of the Toxeus variants were covered:**

| record | charLevel | `treasureProxyName` today | verdict |
|---|---|---|---|
| `um_toxeus_enslaver_99` (Enslaver of Souls) | 40/68/100 | `genericbossorb_05` | ✅ covered |
| `um_bloodtoxeus_99` (Devourer of Blood) | 40/68/100 | `genericbossorb_05` | ✅ covered |
| `um_toxeus_hunt_99` (**The Endless Hunt**) | 40/68/100 | **NONE - no orb at all** | ❌ **MISSED, ours** |
| `um_toxeus_hunt_l_99` (endless Legendary variant) | 40/68/100 | **NONE - no orb at all** | ❌ **MISSED, ours** |
| `um_toxeus_99` (`tagMonsterName190`, inherited) | 33/66/99 | **NONE** | ❌ MISSED, not ours |
| `um_toxeus_21` (inherited, low-level) | 25/45/65 | `genericbossorb_01` (LOWEST tier) | ⚠️ see judgement call |
| `z_toxeus`, `old_z_toxeus` (zzdev dev dummies) | 40/56/71 | NONE | ⚠️ see judgement call |

**The headline: the third champion Will actually met in play - the Endless Hunt - drops NO orb whatsoever.**
b98 gave him a 100% soul and the EoAT formula but never an orb, and b94 wired only the two "fought
champions". Nobody noticed because the two lanes ran in parallel and neither owned the other's roster.

**TWO JUDGEMENT CALLS THIS RULING DOES NOT SETTLE - do not decide these silently:**
1. `um_toxeus_21` is a charLevel 25/45/65 early-game Toxeus on the lowest orb tier. "All variants" reads as
   including him, but handing an Act-4 apex orb to a level-25 encounter is a real balance change that would
   let a new character farm endgame-tier loot. RECOMMEND: cover him with a scaled tier, or leave him and say
   so - Will's call.
2. `z_toxeus` / `old_z_toxeus` are Iron Lore **zzdev dev dummies** (already `BL-b97-DEBT-3`). They are not
   placed encounters. RECOMMEND: exclude, and record the exclusion rather than silently skipping them.

**IMPLEMENTATION CONSTRAINT:** `uber_apex_orb.verify()` currently hardcodes EXACTLY TWO champions and
`negtest` NEGATIVE 2 asserts that a third record on `genericbossorb_05` must FAIL as scope creep. Extending
the roster therefore REQUIRES rewriting that gate to be **roster-derived** (every Toxeus variant + Leinth),
not merely widening a constant - otherwise the build reds the moment the ruling is implemented. Same commit.

**"MORE ITEMS THAN THE NORMAL CHAMPIONS" is already satisfied by the orb05 calibre** (21.16 expected items
vs orb04's 5.70); this ruling is about WHO is on it, not about re-tuning it.

**STATUS:** PENDING - measured and specified, not implemented. Deferred only because the weekly model budget
was exhausted; the two judgement calls above should be answered before or during implementation.

---

## Player-surface truthfulness / skill tooltips (decade 100-109, opened 2026-07-29, branch `fix/blade-mastery-truth`)

> **DECADE CLAIM.** 100-109 was proven free before minting: `git grep -oE "R-[0-9]+" <every local
> branch> -- docs/WILL_RULINGS.md` over ALL branches (incl. `main`, `feat/endless-hunt`,
> `feat/leinth-wave`, `fix/green-diff`, `feat/sanctuary-populate`) returns a maximum of **R-99**,
> so nothing above 99 was claimed anywhere. Next free number in this decade: **R-103**.
> ⚠️ **RE-CHECKED AFTER THE REBASE (2026-07-29, `main` @ `e2a3b1e`) - the claim HELD, but it was a
> race.** `feat/sanctuary-populate` had independently taken R-100..R-109 at almost the same moment;
> its own recon doc records that it re-ran the freshness check, saw this branch, and YIELDED to
> **R-110..R-119**. So 100-102 are this lane's and 103-109 remain free. Anyone opening a decade
> should RE-RUN the census immediately before minting rather than trusting any written line here -
> concurrent lanes make decade-freeness a race, and this is now the second lane in two days to hit
> it (see also the b98 R-80 collision above).
> ⚠️ HONESTY NOTE ON THIS WHOLE SECTION: Will asked a QUESTION here, he did not hand down a
> decision. R-100 records his verbatim words and the answer the evidence supports; the STANDING
> LAW in R-100 and the wording in R-102 are this lane's DERIVATION from that exchange and are
> marked as awaiting his ratification. R-101 is a genuine open Will decision, not something this
> lane settled.

- R-100 [2026-07-29] IMPLEMENTED b100 (fix/blade-mastery-truth) - QUESTION, verbatim: "does the occult skill blade mastery chance to dodge attacks bonus apply if you are using any weapon or only if you are using a sword dagger or axe as the skill description says?"
  **ANSWER (evidence, not opinion): NEITHER. It is NARROWER than the description says, in a way the description never mentioned.** All four of Blade Mastery's bonuses - chance to dodge attacks, defensive ability, attack speed and offensive ability - sit on ONE record (`records\skills\stealth\drx_dual_blade.dbr`, a single `Skill_Passive`, no attached records) behind ONE availability gate, so they are all alive or all dead together; dodge is not special-cased. That gate is `Sword=1, Axe=1, dualWieldOnly=1`. In Game.dll, `Skill::SetAvailability` (0x10245BC0) makes the skill unavailable (reason 4 = the "Skill Requires Equipment" state) unless BOTH `Skill::QualifyingWeapon()` (0x1023F570 -> `IsQualifyingWeapons` 0x1023F510, an **OR over the two equipped weapon types**) AND `Skill::QualifyingHandState()` (0x1023F410, which for `dualWieldOnly` demands `EquipManager::GetHandState()` 0x101792A0 in {2,7} - reachable only when `GetWeaponIdLeft()` returns an actual WEAPON in the off hand) hold; `Skill_Passive` does NOT override `SetAvailability` (its vtable at 0x1037C2B0 slot 54 is byte-identical to `Skill`'s at 0x1036C1F0), so a passive's stat modifiers obey both gates exactly like an attack does. **What Will must equip for the dodge bonus to be live: a weapon in EACH hand, at least one of which is a sword/dagger or an axe.** A shield in the off hand, or an empty off hand, kills all four bonuses even with a sword equipped. A club/mace in the other hand is fine as long as the first hand holds a sword/dagger/axe. "Dagger" is not a separate weapon class in TQAE - every dagger/knife in this mod, including the mod's own `records\drxitem\supra\wep_dagger.dbr`, is `Class=WeaponMelee_Sword`, so daggers qualify AS swords. Learning the skill at all DOES grant the ability to dual wield (`SkillManager::Update` 0x10254E93 ORs `dualWieldOnly` across every skill with `GetCurrentLevel()!=0` into `Character::AllowDualWieldWeapons`), which is why the old first sentence was true - it just read as flavour rather than as the requirement it is.
  **DERIVED STANDING LAW (awaiting Will's ratification):** a player-facing skill whose bonuses are silently dead unless the player holds a particular weapon or hand configuration MUST say so on its own tooltip, in the game's own wording. Enforced permanently by the two-half gate `tools/patches/weapon_gate_truth.py` verify() (DB half: the contracted records' gating fields must still match the gate their shipped tooltip describes, plus a sweep that fails on any NEW uncontracted `dualWieldOnly=1` player skill) and `tools/validate_weapon_gate_text.py` (Text half, run by `build_text_arc`: each contracted tag must resolve and must still contain the clauses its live gating fields demand). Negative tests: `tools/debug/negtest_weapon_gate_truth.py` (9/9).
- R-101 [2026-07-29] **PENDING - OPEN WILL DECISION (balance, deliberately NOT taken by this lane).** The FIX shipped in b100 changed the TEXT to match the mechanics, never the mechanics to match the text, because widening or narrowing a gate is a balance change and therefore Will's call. The open question is whether Blade Mastery's gate is what he wants: (a) keep it as-is (dual-wield-only, sword/dagger/axe) - the honest text now shipping; (b) drop `dualWieldOnly` so the bonuses work with any single weapon, matching how the old tooltip read to a player; (c) keep dual-wield-only but widen the weapon list (e.g. add Mace) so any two one-handers qualify. RECOMMENDATION: **(a), keep it.** The gate is upstream SV/DRX design, it is the same shape the base game uses for its own Dual Wield ladder, and it is what makes the skill a dual-wield identity node in the Occult tree rather than a free stat stick. Changing it also devalues the Warfare Dual Wield line by making the Occult passive strictly better. If Will wants (b) or (c), the record change is one field and the gate will FORCE the tooltip to be rewritten with it - which is the point.
- R-102 [2026-07-29] IMPLEMENTED b100 (fix/blade-mastery-truth) - DERIVED-BY-PRECEDENT (not a Will decision; flagged for veto). The standing sibling sweep found the SAME defect class one mastery over: Warfare **"Parry"** (`records\skills\warfare\drxdodge attack.dbr`) is a `Skill_Passive` whose ONLY bonus is `characterDodgePercent` (3..30) and which carries `dualWieldOnly=1` with an EMPTY qualifying-weapon list - so its dodge is dead unless the player holds a weapon in each hand, and its shipped description (`tagSkillDescription192`, "Even the sturdiest armor has its chinks...") never said so. Since Will's question was specifically about a chance-to-dodge bonus, shipping the Blade Mastery fix while leaving this one lying would be exactly the "triaged-into-follow-up = NOT done" failure. Its old tag is SHARED with `records\skills\nature\pet\naturepetdodge_1%perlevelx100.dbr` (no dual gate), so per the standing re-point-over-edit-a-shared-tag preference (R-41 / `formula_names`) the record's `skillBaseDescription` is REPOINTED onto a new mod-owned `tagParryDESC` carrying the vanilla body text byte-for-byte plus the gate clause, and the shared tag is left untouched. Mechanics unchanged; one field on one record.

**BOTH JUDGEMENT CALLS ANSWERED BY WILL, same day. WILL, VERBATIM:**

> "give all versions of toxeus the new apex orb, if some good items drop since someone got lucky and found
> and killed the low-level Toxeus with no fixed spawn and they get some great items, so be it"

**SCOPE IS THEREFORE SETTLED AND MAXIMAL: every Toxeus creature record goes on `genericbossorb_05`.**
- `um_toxeus_hunt_99` + `um_toxeus_hunt_l_99` - the missed champion and his endless variant. **Highest value
  item in this ruling**: this is the one Will has actually fought, and he currently gets no orb at all.
- `um_toxeus_99` (inherited) - add.
- `um_toxeus_21` (charLevel 25/45/65, inherited) - **add, and the balance objection is OVERRULED WITH
  REASONS.** Will's reasoning is recorded because it is the precedent for future "is this too generous"
  calls: the low-level Toxeus has **no fixed spawn**, so reaching him is already a lucky accident, and Will
  would rather reward that accident than protect the curve. Do NOT quietly scale him down to a lesser tier
  "in the spirit of" the ruling - he asked for the apex orb, on a record he knows is low-level, having been
  told exactly what it means.
- `z_toxeus` / `old_z_toxeus` (zzdev dev dummies) - "all versions" is unambiguous, so **include them**
  rather than silently excluding. First VERIFY whether either is actually placed anywhere; if they are
  unreachable dev leftovers the wiring is inert, which is a fine outcome - but record the placement finding
  either way. RETIREMENT PROTOCOL: do not delete or retire them; code-unreferenced is not proof of dead.

**REMAINING WORK IS MECHANICAL AND FULLY SPECIFIED:** extend the roster, make `verify()` roster-derived
(it hardcodes exactly two champions and planted NEGATIVE 2 asserts a third is scope creep, so that test must
be re-authored to assert the *whole* roster instead of a count), rebuild, re-run all 16 subtests plus new
ones covering the added variants, record-diff for zero unattributed change, confirm `genericbossorb_04` and
its 19 other consumers stay byte-unchanged.

**STATUS: IMPLEMENTED b101 (branch `feat/toxeus-apex-roster`), 2026-07-29. NOT DEPLOYED - no tag
shipped bytes; the orchestrator owns every deploy.** Owner module `tools/patches/uber_apex_orb.py`
(the R-72/R-75 owner, roster EXTENDED); planted negatives `tools/debug/negtest_uber_apex_orb.py`;
placement census `tools/debug/b101_toxeus_placement_census.py`; record-diff
`tools/debug/b101_r99_record_diff.py`; read-back proof table `tools/debug/b101_r99_proof_table.py`.
See docs/reports/b101_toxeus_apex_roster.md and the BUILD69-DEV GATE RECORD in docs/BACKLOG.md.

**MEASURED RESULT (read back OUT of the built arz, not asserted from the patch's intentions).**
Build exit 0 with `SVC_REQUIRE_GATES=1`; arz **`6a3a491db546b603c52132237c40aa63`**, 55,475,226 B,
**51,124 records**. Baseline for every comparison below is a build of `main` @ `e014ef8` made in the
same environment: **`aea688b23acefe1b48ae31a0df4cc423`**, 51,124 records (independently corroborated -
it reproduces the md5 the b100 gate record published for that base).

| record | charLevel n/e/l | rank | before | after |
|---|---|---|---|---|
| `um_toxeus_enslaver_99` | 40/68/100 | Boss | `genericbossorb_05` | `genericbossorb_05` (already, b94) |
| `um_bloodtoxeus_99` | 40/68/100 | Boss | `genericbossorb_05` | `genericbossorb_05` (already, b94) |
| `um_toxeus_hunt_99` | 40/68/100 | Boss | **field absent** | `genericbossorb_05` ← the headline fix |
| `um_toxeus_hunt_l_99` | 40/68/100 | Boss | **field absent** | `genericbossorb_05` (clone-inherited) |
| `um_toxeus_99` | 33/66/99 | Hero | **field absent** | `genericbossorb_05` |
| `um_toxeus_21` | 25/45/65 | Boss | `genericbossorb_01` | `genericbossorb_05` (OVERRULED call honoured) |
| `z_toxeus` | 40/56/71 | Champion | **field absent** | `genericbossorb_05` |
| `old_z_toxeus` | 40/56/71 | Champion | **field absent** | `genericbossorb_05` |

Every charLevel above matches this ruling's own table exactly, re-measured rather than copied.

**THE ROSTER IS DERIVED, NOT TYPED** (`uber_apex_orb.toxeus_roster`: path contains `toxeus` AND
`templateName` is `Monster.tpl`) and cross-checked TWO ways - against `ROSTER_PINNED` (so a new
variant REDS the build instead of being silently dropped, which is how the Endless Hunt shipped
orb-less for two waves) and against a second name-tag derivation. The nine `Pet.tpl` Toxeus summons
are excluded by the `Monster.tpl` half, deliberately: `treasureProxyName` on `Pet.tpl` is the
documented crash trap.

**PROVEN, each against artifacts built for this ruling:**
- Record-diff vs the `main` baseline: **0 ADDED, 0 REMOVED, 6 CHANGED**, and every one of the 6 is a
  derived-roster record whose ONLY moved field is `treasureProxyName` → `genericbossorb_05`. **Zero
  unattributed changes.** 0 REMOVED means b98's 15 records and b99's `summon_sargoth` + pets survived.
- `genericbossorb_04` **BYTE-UNCHANGED**: the proxy plus its whole donor chain (3 pools, 3 chests, 3
  loot tables) = 10 records compared field-by-field, value-by-value, dtype-by-dtype against the
  baseline - all identical; consumers 19 → 19, **nothing lost, nothing gained**, 0 Toxeus records left
  on it. This is the entire reason a new tier was minted, and it is measured, not asserted.
- `genericbossorb_01` (the SECOND donor tier, which `um_toxeus_21` leaves) byte-unchanged; consumers
  11 → 10, losing exactly `um_toxeus_21` and nothing else; its other 10 stay put.
- **R-48/R-91 independence PROVEN, not asserted:** `chanceToEquipFinger2` on all 8 roster records is
  bit-identical to the baseline - the three fought champions still 100.0, `um_toxeus_99` still 66.0,
  `um_toxeus_21` still 50.0, the zzdev pair still 0.0. Souls are Finger2 equipment, orbs are
  `treasureProxyName`; the orb change moved neither.
- Planted negatives: **29/29 as specified** (1 positive + 22 negatives + R1-R5 + 1 restore positive),
  including ONE PER ROSTER RECORD proving the gate fires if that record loses its orb.
- The new gate correctly **REDS the pre-R-99 baseline** with exactly the 6 gaps this ruling enumerated.

**TWO THINGS THIS IMPLEMENTATION FOUND THAT THE RULING ASSUMED OTHERWISE - read them, they change the
answer to judgement call #2:**
1. **`z_arthur` IS PLACED, so `z_toxeus` is NOT inert.** This ruling's recommendation and the first
   implementation pass both recorded the zzdev chain as unreachable. Re-measured with a MULTI-HOP walk
   (the first census was one hop, and placement here is a two-hop placed-proxy → pool → monster chain),
   `z_arthur` has exactly ONE static `0x05` instance in
   `XPack\Levels\Area01_Rhodes\Undergrounds\ScrabledEggs_Floor06.lvl`, and its
   `actorToSpawnOnDeath` is `z_toxeus`. So a Champion-rank Act-1 dev dummy now drops the Act-4 apex
   orb. Will's words pre-authorise it ("if some good items drop since someone got lucky ... so be
   it"), so it is RECORDED, not reversed - but it is a live consequence, not a no-op, and he should
   know. Honest limit: static placement proves the record is in the level, NOT that a player can walk
   to it; player reachability is launch-gated (registered as debt).
2. **`um_toxeus_99` and `old_z_toxeus` are genuinely inert in this map** (0 static placements, 0 db
   referrers, no placed ancestor within 3 hops). Their orbs are wired per "all versions" and are simply
   dormant. Recorded so the dormancy is known rather than silent.

**NOTHING WAS DELETED, RETIRED, BLANKED OR RENAMED** (RETIREMENT PROTOCOL): the zzdev pair is wired
per Will's explicit inclusion, `genericbossorb_01`/`_04` and Leinth's three original loot tables all
stay in the db, and `um_toxeus_21` was NOT quietly scaled to a lesser tier "in the spirit of" the
ruling - the ban in this ruling is honoured literally.

---

## R-100 [2026-07-29] PLAY-SESSION BATCH - 19 items, CAPTURED VERBATIM, none implemented yet

> 🚩 **NUMBER COLLISION FLAGGED BY b101 (`feat/toxeus-apex-roster`), NOT RESOLVED HERE.** There are
> now TWO live R-100s in this file: `- R-100 ... IMPLEMENTED b100 (fix/blade-mastery-truth)` in the
> "Player-surface truthfulness" decade above, and this section. Both were written the same day by
> parallel lanes. This lane deliberately did NOT renumber either one - reassigning another lane's
> ruling number from a third lane is the same class of silent cross-lane edit the ledger law exists to
> prevent. The file's own `fix/debt-docs` LEDGER-HYGIENE precedent (the INCUMBENT keeps the number,
> the other lane's rulings move wholesale to the next free decade) is the tie-breaker to apply, but
> picking the incumbent between two same-day lanes is the orchestrator's call. Registered as
> `BL-b101-DEBT-1`.
>
> 🛑 **RETRACTION (b101 round 2, 2026-07-29). AN EARLIER ANNOTATION HERE CLAIMED THIS SECTION HAD BEEN
> "SILENTLY DELETED BY MERGE `4748e93` AND RESTORED". THAT CLAIM WAS FALSE AND IS WITHDRAWN.** Nothing
> was ever lost. The independent vet caught it and I reproduced every command:
> * `git diff e014ef8 4748e93 --numstat -- docs/WILL_RULINGS.md` -> **empty**. The merge result is
>   byte-identical to the `main` it merged; it dropped nothing.
> * `for c in d7c9aee e014ef8 4748e93 60a3bfb~1 60a3bfb 0c4e9a2; do git show $c:docs/WILL_RULINGS.md |
>   grep -c "PLAY-SESSION BATCH"; done` -> `0 0 0 0 1 1`. This section did not exist on EITHER side of
>   that merge.
> * `git log -1 --format="%h %ad %s" --date=iso 0c4e9a2` -> `2026-07-29 18:18:15 R-100: capture Will's
>   19-item play-session batch VERBATIM` vs `4748e93` -> `2026-07-29 12:57:15`. R-100 was authored on
>   `main` **5h21m AFTER** the merge it was accused of destroying. `git merge-base --is-ancestor
>   0c4e9a2 e014ef8` -> exit `1` (not an ancestor).
> * `git diff 60a3bfb~1 60a3bfb --numstat` -> `101 0 docs/WILL_RULINGS.md`: commit `60a3bfb` was an
>   ordinary catch-up **ADD** of `main`'s newer text, not a restore, and its commit subject
>   ("RESTORE the 101 ruling lines this branch's merge silently dropped") is likewise wrong.
>
> ROOT CAUSE OF THE FALSE REPORT: `git diff main..HEAD --numstat` shows a file `main` added after the
> merge base as pure DELETIONS on the branch side. That is a two-dot-diff artifact, not data loss.
> Reproduced live today: `git diff main..HEAD --numstat` reports `0 96 tools/debug/probe_blockers.py`,
> `0 86 …probe_class_examples.py`, `0 101 …probe_soul_by_class.py` - three files `main` ADDED at
> `fc7a886`, which this branch has never touched. **The real lesson, and the one worth keeping: read
> `git diff <mergebase>..HEAD` (three-dot `main...HEAD`) before accusing a commit of losing anything,
> and check the accused commit's own `--numstat` against BOTH its parents.** A fabricated incident in
> the design law of record is itself a violation of CLAUDE.md law #1.

Will played and reported a large batch in one message. Recorded verbatim FIRST, before any triage, because
losing an item off a list this long is exactly the failure the DONE-MEANS-DONE rule exists to prevent.
The numbering is mine; the words are his.

**WILL, VERBATIM (single message, 2026-07-29):**

> "We should grant the skill Bloodbath from the Erebenea the Bloodletter Soul to toxeus the devourer of blood
> but lets reduce the cooldown on the skill from 45s to like 15s. Also when you cloned the monster to create
> the Soul of the Unferried, you literally clone another monster in the game who is a quest monster who drops
> Charon's Oar, and now this monster is also dropping Charon's Oar. Furthermore, the monster that you created
> is literally a clone of the other one with no new skills or anything, its like playing the same monster
> twice. Also I just faced toxeus the murderer, the endless hunt again and he was still a demon not a
> skeleton, he didnt drop a soul, he didnt drop an orb. also toxeus the murderer the endless hunt had an
> exclamation mark on him on the minimap but the other major bosses you have made, including the toxeus the
> murderer variants do not have one. we should give an exclamation mark over their head to all the uber
> bosses we made with the exception of toxeus the murderer, devourer of blood since he is sitting on a chest
> a hidden location and should not be so easily found. also tantalus the hunger unbound is not inside the den
> of tantalus like he is supposed to be, he is sitting right in front of the den of tantalus outside of it.
> also he has three chests, all of them tantalus hoard where he should only have one. the uber monster soul
> of the unferried also had three chests. Also there are forge formulas for experience potions that require
> souls from a specific act, but the souls that we added for the new monsters we added into those acts and
> probably the souls we added that were missing do not have the proper classification on them so you cant
> use them in the forge formulas. We should also give the skill Blood Frenzy to the devourer of blood
> (activated on low health), see Chief Bullfrog Quak soul for this skill. also we need to give toxeus the
> murderer devourer of blood and toxeus the murderer endless hunt some guys they can summon like toxeus the
> murderer enslaver of souls has. also the uber boss in the lower city of lost souls has no chest that he is
> guarding and the orb he drops is trash. also all of the guys that we brought back into the game which
> utilize thrown objects are all frozen in the game, they spawn and they cant move or attack or anything they
> are broken. the machine uber boss destroyer of cities i think he is called doesnt have a chest that he
> drops either. also he is right in the walking path, he should be moved off of the main walking path. the
> main walking path is not the appropriate place for uber monsters we are placing in the game. The Soul
> Gaoler boss chests are too much, we need to cut the number of chests in half for him (round down if
> needed), also his chests on epic are dropping "essence" like "essence of the chill of tartarus" which
> should only drop on normal instead of dropping the epic version which starts with "embodiment" like
> "embodiment of the chill of tartarus". also the guys who are the guardians of the general the uber bosses
> we added are super weak and they dont have any chests and dont drop any orbs or anything. also they are
> small and they look just like the other guys and i killed them so fast they are so weak they appear just
> like normal guys they are not big with no special skills or anything to make them even noticeable besides
> their red names
>
> Also lets decrease the general soul drop rate for monsters who dont have a fixed spawn from 50% to 33%"

### READ THIS BEFORE TRIAGING ANY OF IT: TWO OF HIS REPORTS ARE EXPLAINED BY A DEPLOY THAT NEVER RAN

Measured, not assumed:
- Deployed DEV arz = `06de12d4491a51cfe38bd321774a96b2` (the b94 Leinth lane's own round-2 write).
- Merged main's build = `967b1f97137bf6479c18c08e9dd6ffc4` (51,124 records) - built, gate-green, and
  **NEVER DEPLOYED**.
- The canonical `CustomMaps\SoulvizierClassic` entry does not exist on this machine at all, so the Steam
  build is further behind still.

So when he says the Endless Hunt "didnt drop a soul, he didnt drop an orb": the 100% soul fix (R-91, b98) is
on `main` and not on his disk, and the orb (R-99) is not merged yet. Those two are NOT new defects and must
NOT be re-investigated as such - they are one un-run deploy. Deploy the coupled arz+Text, have him re-fight,
and only then believe any residual.

### THE ITEMS

| # | item | class | notes |
|---|---|---|---|
| 1 | Grant **Bloodbath** (from the Erebenea the Bloodletter soul) to the **Devourer**; cooldown 45s -> **15s** | content | 15 is his number |
| 2 | **Soul of the Unferried** was cloned from a QUEST monster and inherited its **Charon's Oar** drop | **P0 defect** | a quest item is now farmable |
| 3 | That same monster is a bare clone - "like playing the same monster twice" | content | needs its own kit, held to the amgoz1 bar |
| 4 | Endless Hunt "**still a demon not a skeleton**" | **CONTRADICTS an earlier ruling - see below** | do not guess |
| 5 | Endless Hunt dropped no soul | **NOT A DEFECT** | un-deployed R-91 |
| 6 | Endless Hunt dropped no orb | **NOT A DEFECT** | R-99 not merged yet |
| 7 | **Exclamation mark over the head of EVERY uber boss we made**, EXCEPT the Devourer (hidden chest, must stay hard to find) | content | the Hunt already has one; b91's `uber_quest_markers` is the existing rig - copy it, do not invent |
| 8 | **Tantalus the Hunger Unbound is OUTSIDE the Den of Tantalus**, sitting in front of it | **P1 regression** | b45 claimed exactly this fix; internal task "b45 FIX: re-place Tantalus encounter inside Den of Tantalus" is marked COMPLETED. Re-open and find out why it did not hold |
| 9 | Tantalus has **3 chests, all "Tantalus Hoard"**; should have **1** | defect | b50's "3 majestic chests per boss" is the likely author; that decision now needs scoping |
| 10 | Soul of the Unferried **also has 3 chests** | defect | same root as #9 |
| 11 | **Forge formulas for XP potions require souls from a specific act**, and our added souls lack the act classification, so they cannot be used | **P1 defect** | affects every soul we minted, including the missing-souls wave |
| 12 | Grant **Blood Frenzy** (low-health trigger) to the Devourer - see the **Chief Bullfrog Quak** soul | content | |
| 13 | Give the **Devourer AND the Endless Hunt summonable minions**, like the Enslaver has | content | `svc_enslaver_summonmarauders` is the pattern |
| 14 | Uber boss in the **Lower City of Lost Souls**: guards **no chest**, and his **orb is trash** | defect | orb tier probably wants the R-99 apex treatment |
| 15 | **EVERY thrown-object monster we restored is FROZEN** - spawns, cannot move or attack | **P0 defect** | `thrown_wielders.py`. Multiple internal tasks claimed this rig was proven on 3 families and re-verified. It ships broken. Most serious item in the batch |
| 16 | Machine uber boss (**Destroyer of Cities**) drops **no chest**, and stands **in the main walking path** | defect | |
| 16b | **STANDING RULE: the main walking path is never an appropriate place for an uber monster we place.** Applies to every existing and future placement - audit them all | **standing** | |
| 17 | **Soul Gaoler**: halve his chest count (round down). His **Epic** chests drop Normal-tier "essence of..." instead of Epic-tier "embodiment of..." | defect | difficulty-tier mis-wire in his loot chain |
| 18 | **Guardians of the General** are weak, small, chest-less, orb-less, indistinguishable from trash except for red names | content | must READ as uber: size, kit, drops |
| 19 | **General soul drop rate for monsters with NO fixed spawn: 50% -> 33%** | balance | this is the DROP-50 constant. It must NOT touch R-48 (the fixed 100% Toxeus souls) |

### ITEM 4 IS A DIRECT CONTRADICTION AND MUST GO BACK TO WILL, NOT BE GUESSED

On 2026-07-27 the recorded ruling behind R-90..R-96 was that the Endless Hunt should be a **DEMON, not a
skeleton**, explicitly so that he would stop reading as a copy of the undead Enslaver - and b98 implemented
exactly that (`ShadowStalker.msh`, race Demon, against the Enslaver's `RevenantPoison.msh`, race Undead).
He now reports "he was still a demon not a skeleton" as a complaint.

Either the 07-27 ruling was recorded backwards, or he has changed his mind, or he means something narrower
(the Hunt should be a skeleton and some other axis should carry his identity). **Do not pick one.** Ask, and
quote both of his statements back to him. Guessing means redoing a mesh and race change twice, and risks
re-breaking the b92 mesh-green work (`BL-b98-DEBT-2`).

**STATUS:** captured verbatim, decomposed, NOT implemented. Order of operations: deploy first (items 5 and 6
evaporate), ask about item 4, then lane the rest by class - the two P0s (#2 Charon's Oar, #15 frozen thrown
monsters) go first.

---

## R-101 [2026-07-29] P0 - our uber clones inherited their donors' QUEST-ITEM drops. Swept exhaustively: 3 records.

**WILL, VERBATIM (second report of the same defect, which is what turned it into a class):**

> "Same thing with the Key of the Warden of Souls, that is now a farmable item from the uber boss you made
> that you cloned from the warden of souls, they now drop the key of the warden of souls which they should not"

(The first, from the R-100 batch: *"when you cloned the monster to create the Soul of the Unferried, you
literally clone another monster in the game who is a quest monster who drops Charon's Oar, and now this
monster is also dropping Charon's Oar."*)

**MECHANISM:** cloning a quest boss copies `perPartyMemberDropItemName`, the field the base game uses to hand
out quest keys and journal items. Our clone keeps pointing at the donor's quest item, so a unique,
quest-gating item becomes farmable from a repeatable uber encounter.

**THE SWEEP - measured against the merged build `967b1f97137bf6479c18c08e9dd6ffc4` (51,124 records), not
inferred. This is a CLOSED SET, not a sample:**

Every `um_*` record in the database that carries `perPartyMemberDropItemName` is **3**, and **all 3 of them
point at a quest-classified item.** There are no non-quest uses of the field on our ubers at all, which makes
the invariant trivially clean to state and to gate.

| # | our uber record | leaked quest item | how Will found it |
|---|---|---|---|
| 1 | `records\xpack\creatures\monster\bosses\02_charon\um_charonform2_ferryman_99.dbr` (`tagSVCMonsterCharonFerryman`) | `xsq12_charonsoar.dbr` - **Charon's Oar** | reported (R-100 #2) |
| 2 | `records\xpack\creatures\monster\gigantes\um_polisgaoler_99.dbr` (`tagSVCMonsterPolisGaoler`) | `z_wardenofsoulskey.dbr` - **Key of the Warden of Souls** | reported (this ruling) |
| 3 | `records\xpack\creatures\monster\gigantes\um_polisgaoler_unbound_99.dbr` (`tagSVCMonsterPolisGaolerUnbound`) | `z_wardenofsoulskey.dbr` - **Key of the Warden of Souls** | **NOT reported - found by the sweep.** He met one Gaoler; the "unbound" variant leaks the same key |

Cross-check from the other direction (inbound references per quest item) agrees exactly:
- `xsq12_charonsoar` has 5 inbound refs - 4 legitimate base-game Charon forms
  (`boss_charonform2_39/41/43`, `testcharon01`) plus our `um_charonform2_ferryman_99`.
- `z_wardenofsoulskey` has 3 - the legitimate `xsecrethero_wardenofsouls_48` plus BOTH of our Gaolers.
- No other quest item anywhere in the database has an inbound reference from a `um_*` record.

**THE FIX:** clear `perPartyMemberDropItemName` (and any matching chance field) on all three. Do NOT touch the
donors - `boss_charonform2_*`, `testcharon01` and `xsecrethero_wardenofsouls_48` must stay byte-identical, or
the actual quests break. That is the whole risk in this change and it must be proven, not asserted.

**THE GATE (required, process law #4):** no `um_*` record may carry a `perPartyMemberDropItemName` that
resolves to an item with `itemClassification == Quest`. State it as a general invariant over the roster, not
as three named exceptions - the roster grows, and this defect class arrived precisely because a clone was
assumed to be safe. Plant negatives: re-add each of the three and confirm the build reds; and add a
non-quest per-party drop to confirm the gate does NOT fire on that (it must stay a quest-only ban, since the
field itself is legitimate).

**RELATED, same monster:** R-100 #17 (Soul Gaoler / Polis Gaoler chest count too high, and his EPIC chests
dropping Normal-tier "essence of..." instead of "embodiment of...") is the SAME creature family as leaks 2
and 3. One lane should own the Gaoler end to end.

**WIDER LESSON, worth acting on beyond this fix:** we have cloned base-game quest bosses repeatedly to make
ubers, and nobody enumerated what else a quest boss carries that a repeatable encounter must not inherit.
`perPartyMemberDropItemName` is one field. The lane should also sweep our clones for other quest-coupled
fields (quest triggers, one-shot flags, journal hooks, `questItem*`-style references) and report what it
finds, even where it changes nothing.

**STATUS:** measured and specified, NOT implemented. P0 - a quest-gating item is farmable in the shipped mod.

---

## R-102 [2026-07-29] REOPENED - the Enslaver's green glow is REAL. Will retracted his own explanation.

**WILL, VERBATIM:**

> "ok i was wrong, toxeus the murderer enslaver of souls are still having a green glow and it is not a skill
> of mine"

**HISTORY, and why this matters procedurally.** Four fix waves chased this green (b39/b55/b55r2/b92). Earlier
on 2026-07-27 Will resolved it himself - he concluded his own character's skill was propagating onto the
monster - and on that basis I STOPPED a fifth lane (`fix/green-diff`, still parked at `a0276ab`). That
resolution is now withdrawn by the person who made it. **The lane must be restarted, and the four prior
waves' "fixed" claims should be treated as unproven rather than as evidence the FX surface is clean.**

**FRESH DIFFERENTIAL, measured against merged main `967b1f97137bf6479c18c08e9dd6ffc4`. The decisive move was
comparing him to the Devourer, who wears THE SAME MESH and is NOT reported green.**

Creature-level visuals on the Enslaver are now genuinely spare - the earlier waves did land:
- `mesh` = `Creatures\Monster\Skeleton\RevenantPoison.msh`
- `baseTexture` = `NewSkeleton_Charcoal.tex` (charcoal - not a green skin)
- `charFxPakRunningNames` = the demons' own `drxshadowcloakrunning_fx_pak` (the black smoke Will asked for)
- no other FX, tint, glow or particle field on the record at all

**THE MESH HYPOTHESIS IS WEAKENED, NOT DEAD.** `RevenantPoison.msh` is a poison-themed asset and was the
obvious suspect - but `um_bloodtoxeus_99` (the Devourer) wears the *same* mesh with a crimson texture and Will
has not reported green on him. If the green were baked into the mesh, both should glow. Keep it on the list
(he may simply not have scrutinised the Devourer), but rank it below the differential below.

**PRIME SUSPECTS - skills the Enslaver has that the Devourer does NOT, filtered to those carrying FX:**

| skill | FX it pulls in | why suspect |
|---|---|---|
| `records\skills\spirit\svc_enslaver_soulrip.dbr` | `targetFxPakName` = `Records\Effects\Spirit\343_NexusImpact_FXPak01.dbr` | **spirit school - the green school in this game.** Also the same "343" donor family b98 flagged elsewhere |
| `records\skills\monster skills\attack_melee\netherstrike.dbr` | `warmupFxPakName` + `targetFxPakName` = `drx_nether_strike_source/target_fx_pak` | nether/spectral FX, DRX-authored, never audited by any of the four waves |
| `records\skills\monster skills\buff_other\unholy_rally.dbr` | no visual field on the record itself | check what it applies to its TARGETS - a buff_other can paint the caster's allies, and one of them standing on him would read as his own glow |

**RULED OUT this pass, with the values:** `svc_enslaver_shroud` (b98's) is clean -
`charBuffFxType = None`, `skillWeaponTintRed/Green/Blue` all `0.0`. It is not the source.
`drxshadowcloakrunning_fx` carries no colour channel fields at all.

**ON BOTH champions, so it cannot explain a difference between them, but still worth checking as an
ADDITIVE source:** `records\skills\spirit\lifedrain.dbr` - lifedrain is classically a green channelled beam
in this engine. If the glow is intermittent rather than constant, this is the likeliest single cause and the
Devourer would glow too.

**METHOD NOTE FOR THE LANE - why four waves missed it.** Every prior wave enumerated FX fields on the
CREATURE record. The creature record is now clean, and the green persists, so by elimination the source is
one layer out: a SKILL's FX pak, a buff applied to something standing next to him, or the mesh asset itself.
Do not re-audit the creature record and declare victory again. Ask Will one question the data cannot answer -
**is the glow constant, or only when he attacks/casts?** - because constant points at mesh or a self-buff,
and intermittent points at soulrip/netherstrike/lifedrain.

### AMENDMENT, same day - WILL'S THREE CLARIFICATIONS MOVE THE TARGET OFF THE MONSTER ENTIRELY

**WILL, VERBATIM, in order:**

> "it is constant, he glows green the whole time"
>
> "immediately when i summon him he glows green its like a green smoke"
>
> "he has black smoke too but the green is more prominent"
>
> "it depends on the lighting"

**"WHEN I SUMMON HIM" IS THE WHOLE BALL GAME.** He is describing the **summoned PET**, not the world monster.
Those are different records. Four fix waves - and my own probe an hour ago - all audited
`um_toxeus_enslaver_99`, the MONSTER. What Will actually looks at when he reports this is
`records\skills\soulskills\pets\toxeus_enslaver_{1,2,3}.dbr`, summoned by the soul's granted skill. **That
alone plausibly explains four "fixed" waves and a still-green summon: right symptom, wrong record.**

**BUT THE PETS ARE ALSO CLEAN AT THE .DBR LEVEL** (measured on `967b1f97`, all three tiers identical):
`baseTexture` = `NewSkeleton_Charcoal.tex`, `mesh` = `RevenantPoison.msh`,
`charFxPakRunningNames` = the demons' `drxshadowcloakrunning_fx_pak`, `dissolveColor` R0/G0/B255. No green
field anywhere. So the green is NOT expressed in any creature-or-pet `.dbr` field, on either surface.

**"BLACK SMOKE TOO, GREEN MORE PROMINENT" MEANS TWO EMITTERS, AND WE ONLY ACCOUNT FOR ONE.** The black is
`drxshadowcloakrunning_fx` - the demons' shroud, which is what he asked for and wants to keep. The green is a
SECOND, unaccounted emitter. Any fix must kill the green WITHOUT killing the black.

**"IT DEPENDS ON THE LIGHTING" IS A STRONG MECHANICAL TELL:** brightness varying with scene light is how an
**additive-blend particle** behaves. That points away from a flat texture or a solid tint field and toward a
particle asset.

**RANKED SUSPECTS after these clarifications:**
1. **The `.pfx` particle asset behind the shroud chain.** `drxshadowcloakrunning_fx.dbr` carries almost no
   fields of its own (a probe over every colour/texture/particle-named field returned only `Anchored = 0`), so
   the actual particle definition lives in the referenced **`.pfx` binary** (b98 resolved it to
   `shadowcloakrunning.pfx` in `DRXeffects.arc`). **No `.dbr` edit can change a colour baked into a `.pfx`** -
   which is exactly why four waves of field edits could sincerely "fix" this and change nothing on screen.
2. **The summon skill's own FX** - `records\skills\soulskills\summon_toxeus_enslaver.dbr` and its pet-bar
   chain. NOT YET PROBED, and it is the best fit for "immediately when i summon him". Do this first: it is
   cheap and it is the newest untested surface.
3. **`RevenantPoison.msh`** - still possible, but note the crimson pets (`bloodtoxeus_1`, `toxeus_eoat_1`)
   wear the SAME mesh and Will has not reported them green. Rank last, and if it IS the mesh, ask Will
   whether the crimson variants glow too before touching it.

**THE PROCESS LESSON, which matters more than this bug.** For four waves nobody asked *"which record are you
actually looking at?"* The green was reported on "the Enslaver"; there are at least five Enslaver-ish records
(the monster, three pet tiers, and the marauder minions). One clarifying question - "summoned or in the
world?" - would have redirected every one of those waves. Ask it before the next lane starts, not after.

### SECOND AMENDMENT - WILL IS RIGHT: THE SHROUD WAS NEVER IMPLEMENTED ON THE THING HE SUMMONS

**WILL, VERBATIM:**

> "no the black is not the demon shroud i asked for, that is still not implemented. the black is something else"

**HE IS CORRECT, AND MY LABEL WAS WRONG.** I told him the black smoke was the demons' shroud he asked for.
It is not. Measured on `967b1f97`:

| surface | skills | `svc_enslaver_shroud` present? | `charFxPakRunningNames` |
|---|---|---|---|
| `um_toxeus_enslaver_99` (MONSTER) | 19 | **YES** - slot 19 | `drxshadowcloakrunning_fx_pak` |
| `soulskills\pets\toxeus_enslaver_1` (PET) | 13 | **NO** | `drxshadowcloakrunning_fx_pak` |
| `soulskills\pets\toxeus_enslaver_3` (PET) | 13 | **NO** | `drxshadowcloakrunning_fx_pak` |

So:
1. **b98 wired the requested shroud to the MONSTER ONLY.** All three PET tiers never received it. Will
   summons the pet, so from where he stands the request was simply not delivered - and he is right to say so.
   `R-95` / the b98 report claim the Enslaver shroud is "DONE in data, colour AND shape". That claim is
   **HALF TRUE and must be corrected**: done on one of the two surfaces the player actually sees.
2. **The black smoke he currently sees is `charFxPakRunningNames` -> `drxshadowcloakrunning_fx_pak`, which was
   ALREADY on the pet records before any of our work.** It is pre-existing DRX pet FX, not ours. That is
   exactly his "the black is something else".
3. Even the monster's copy is **not deployed** - it is on `main`, not on his disk.

**MY ERROR, recorded because it is the same failure mode twice in one day:** I repeated a lane's "DONE" claim
without checking WHICH RECORD it landed on. The lane said "Enslaver shroud done"; there are two Enslaver
surfaces; it did one. Combined with the R-100 finding that the Hunt's soul was also reported-missing purely
because nothing was deployed, the rule is: **a "DONE" in a lane report is a claim about a branch, not about
what Will can see. Check the surface AND the deploy before telling him anything is implemented.**

**ADDED SCOPE for the shroud work (not a new ruling - the original request, finished properly):** wire the
shroud to ALL THREE PET TIERS as well as the monster, and gate it roster-derived over
`{monster} + {every pet tier}` so a future tier cannot be silently skipped. Then deploy, because none of it
counts until it is on his disk.

### THIRD AMENDMENT - WILL SENT A SCREENSHOT. WHAT IS VISIBLE, AND WHY IT INVERTS A b98 ASSUMPTION.

Will: *"can you see the green on the summoned pet?"* - screenshot, Prison of Souls, his spear-and-shield
character next to the summoned Enslaver pet. Also: *"even in bright areas you can see the green but on certain
backgrounds it is extremely striking"*.

**WHAT IS ACTUALLY VISIBLE (stated as observation, separated from inference):**
- A distinct **volumetric green smoke cloud centred on the pet**, hugging the ground around its feet and lower
  body, extending to the pet's LEFT - i.e. AWAY from the soul-cage set piece. It is emitted by the pet.
- Its hue is **mossy / olive green**, clearly DIFFERENT from the Prison of Souls cage's bright **cyan-teal**
  beam a few metres to the right. Two different greens in one frame. **That hue difference is the load-bearing
  observation: it rules out "you are just seeing the cage's light reflected off him".**
- The pet's bones also read green-tinted, but the cage throws green ambient light across that whole area, so
  the SKIN tint is confounded and must not be used as evidence either way.
- **No obvious black smoke in this frame**, consistent with his "the black is something else" and with the
  shroud never having reached the pets.

**NEW LEADING HYPOTHESIS, and it inverts what b98 assumed.** The pet record has **exactly ONE** particle
emitter: `charFxPakRunningNames` -> `drxshadowcloakrunning_fx_pak` -> `drxshadowcloakrunning_fx` ->
(a `.pfx` binary, `shadowcloakrunning.pfx` in `DRXeffects.arc`). Will sees exactly ONE dominant smoke cloud,
and it is green. The parsimonious conclusion is that **that one emitter IS the green smoke** - i.e.
`shadowcloakrunning.pfx` is a green spectral cloak in DRX, not a black one.

b98 assumed that pak was BLACK - it reasoned from Will's description of the demons' smoke and then wired the
SAME pak onto the monster as `svc_enslaver_shroud`, calling it "the demons' black shroud, colour AND shape".
If this hypothesis holds, **b98's shroud does not fix the green - it ADDS a second green emitter to the
monster.** ⚠️ **DO NOT DEPLOY b98's shroud as-is until the `.pfx` colour is confirmed.** Verify before
believing this; but verify it FIRST, because it is cheap and it gates a deploy.

**THE ONE MEASUREMENT THAT SETTLES IT:** extract `shadowcloakrunning.pfx` from `DRXeffects.arc` and read its
texture reference and colour keys. Mechanical byte work - Opus, not Fable (per the byte-reading budget rule).
Then check what the marauder demons actually emit, because Will likes THEIR smoke; if they use this same pak
and read black to him, the difference is elsewhere and this hypothesis dies.

### FOURTH AMENDMENT - **SOLVED BY ELIMINATION. IT IS THE MESH.** `RevenantPoison.msh`.

**WILL, VERBATIM - the observation that closed it:**

> "yes the demons that he summons have the proper black shroud and they dont have any green"

**MY OWN `.pfx`-IS-GREEN HYPOTHESIS IS DEAD, and his observation is what killed it.** The marauder demons
carry the **identical** effect record and show **no green at all**, so that effect is genuinely black. Reported
here rather than quietly dropped, because it was the leading theory one message ago and it lasted exactly as
long as it took to check it against him.

**THE FOUR-WAY COMPARISON, measured on `967b1f97` - one variable is left standing:**

| record | mesh | baseTexture | `charFxPakRunningNames` | green in game? |
|---|---|---|---|---|
| `um_enslaver_marauder_99` (his demons) | **`ShadowStalker.msh`** | *(none)* | `drxshadowcloakrunning_fx_pak` | **NO - correct black shroud** ✅ |
| `pets\toxeus_enslaver_1` (what he summons) | **`RevenantPoison.msh`** | `NewSkeleton_Charcoal.tex` | `drxshadowcloakrunning_fx_pak` | **GREEN** ❌ |
| `um_toxeus_enslaver_99` (the monster) | **`RevenantPoison.msh`** | `NewSkeleton_Charcoal.tex` | `drxshadowcloakrunning_fx_pak` | green (his original report) ❌ |
| `pets\bloodtoxeus_1` (Devourer pet) | `RevenantPoison.msh` | `newskeleton_crimson.tex` | *(none)* | never reported |

**The FX pak is byte-identical between the clean demon and the green pet. The mesh is the only difference that
tracks the symptom.** Therefore the green is baked into **`Creatures\Monster\Skeleton\RevenantPoison.msh`** -
the *poison* variant of the revenant skeleton - as an emissive or a secondary material the `.dbr`'s
`baseTexture` field does not override (`baseTexture` replaces the primary skin only).

**THIS RETROSPECTIVELY EXPLAINS EVERY EARLIER FAILURE, and it is a lesson, not an excuse:**
- **Constant** - a mesh renders every frame; no skill or buff timing involved. Matches "he glows green the
  whole time".
- **Visible even in bright areas, striking on certain backgrounds** - an emissive shell, exactly his words.
- **Four fix waves changed nothing** because all four edited FX FIELDS, and the green was never in a field.
  We were editing the correct-looking layer of the wrong subsystem, and each wave could sincerely verify its
  own change and still not move a pixel.

**THE FIX, and it pays a second debt:** put the Enslaver - **the monster AND all three pet tiers** - on a mesh
that is not the poison revenant. **`ShadowStalker.msh` is the evidenced choice**: it is proven green-free in
this exact scene, and it is literally what his own demons wear, so it is in-family rather than arbitrary. This
simultaneously satisfies **R-93**, which wants the Enslaver and the Devourer to stop sharing
`RevenantPoison.msh`.

⚠️ **THE REAL RISK IS ANIMATION, NOT COLOUR.** A mesh swap re-rigs everything: the Enslaver's inline animation
rows and every skill that names a specific anim must still resolve, or he T-poses or goes uncastable. b98 hit
exactly this class of bug with the spear rig. The lane must prove every referenced `.anm` resolves on the new
mesh BEFORE claiming the fix, and must check the marauder's own rig as the reference implementation.

**LIFT THE DEPLOY BLOCK:** b98's `svc_enslaver_shroud` is **exonerated** as a green source (its pak is the
black one the demons wear). It is still only wired to the MONSTER and still needs extending to the three pet
tiers, but it is safe to deploy.

**ONE CHEAP CONFIRMATION, worth doing before the swap:** ask Will to summon the **Devourer** pet. Same mesh,
crimson texture, and no FX pak at all. If it also glows green, the mesh conclusion is confirmed independently
and the swap must cover him too. If it does NOT, the mechanism is a mesh-plus-charcoal-texture interaction and
the fix may be a texture change instead of a mesh swap - a smaller and safer change.

### FIFTH AMENDMENT - CORROBORATED. THE FIX IS A MESH SWAP, NOT A TEXTURE CHANGE.

**WILL, VERBATIM:**

> "i cant summon the devourer since i havent been able to kill him to get his soul but from what i remember
> he had the green glow too"

**THIS IS THE DISCRIMINATING ANSWER, and it settles the open branch.** The two candidates left were
(a) the mesh alone, or (b) a `RevenantPoison.msh` + `NewSkeleton_Charcoal.tex` interaction. The Devourer wears
the **same mesh with a DIFFERENT texture** (`newskeleton_crimson.tex`) and Will remembers him green as well.

| record | mesh | baseTexture | green? |
|---|---|---|---|
| Enslaver (monster + 3 pet tiers) | `RevenantPoison.msh` | `NewSkeleton_Charcoal.tex` | **green** (confirmed, screenshot) |
| Devourer | `RevenantPoison.msh` | `newskeleton_crimson.tex` | **green** (Will, from memory) |
| Marauder demons | `ShadowStalker.msh` | *(none)* | **clean** (confirmed in game) |

Green survives a texture change and dies with a mesh change. **So the texture is exonerated and a texture-only
fix would NOT have worked. The mesh swap is required, and it must cover the Devourer too, not just the
Enslaver.**

**CONFIDENCE, stated honestly:** the Enslaver half is confirmed by a screenshot; the Devourer half is Will's
recollection, not a fresh observation, because he has not been able to kill the Devourer and so cannot summon
him. It is corroborating rather than conclusive - but it is consistent, it comes from the same person who
correctly retracted his own earlier explanation of this bug, and it points the same way as the marauder
comparison. **Treat the mesh as the cause; re-confirm the Devourer opportunistically rather than blocking the
fix on it.**

**SCOPE UPDATE for the fix:** `ShadowStalker.msh` on the Enslaver monster + all three Enslaver pet tiers +
`um_bloodtoxeus_99` + the Devourer's pet tiers. Since R-93 wants these two champions to STOP sharing a mesh,
the lane should pick a distinct clean mesh per champion rather than moving both onto the marauders' one -
otherwise the green is fixed and R-93 is broken in the same commit. Both must be proven green-free before
either ships.

### ⚠️ A DESIGN FLAG WILL SHOULD HEAR ONCE, ARISING FROM THE SAME MESSAGE

**He has not been able to kill the Devourer at all.** Meanwhile R-100 asks to give that same boss THREE power
additions: **Bloodbath** (#1), **Blood Frenzy** on low health (#12) and **summonable minions** (#13). Blood
Frenzy specifically triggers when he is nearly dead - i.e. precisely at the moment Will currently loses the
fight. Those three stack onto a boss that is already beating him.

This is **not** a refusal and nothing here is being scaled down on my own authority: R-100 stands as written and
will be implemented as specified. It is worth one sentence to him so the decision is informed - he may well
want exactly that (he is the one who put the Devourer on a hidden chest as a hard secret), and if so the answer
is "yes, harder is the point". But he should choose it knowing the three changes compound on an encounter he
has not yet won. `BL-b98-DEBT-2` is the related debt. R-93
remains PARTIALLY IMPLEMENTED (Enslaver and Devourer share `RevenantPoison.msh`), a second reason to revisit
that mesh regardless of the green.

---

## R-103 [2026-07-29] Toxeus champions: KEEP all three power additions. The lever is REFLECT, and it is found.

**WILL, VERBATIM:**

> "yes harder is the point, keep all three. if we need to make him more killable we will reduce his reflect
> damage or his health or something. currently the reflect damage is what makes these variants nearly
> unkillable since i one shot myself when i hit them"
>
> "the answer is not cutting skills but cutting elsewhere"

**RULING: R-100 #1 (Bloodbath), #12 (Blood Frenzy) and #13 (summonable minions) all STAND, in full.** Do not
water any of them down, do not "balance" them by trimming their numbers, and do not propose cutting a skill as
a difficulty fix. Harder is the intent. The difficulty lever is elsewhere, and he named it.

**THE SOURCE IS FOUND - ONE RECORD, ONE FIELD PAIR, SHARED BY ALL THREE VARIANTS.** Measured on `967b1f97`:

`records\skills\monster skills\passive_buffs\toxeus_passiveproperties.dbr`
- **`defensiveReflect` = 100.0**
- **`defensiveReflectChance` = 33.0**

Carried by all three champions and nothing else on them reflects: the Enslaver (skill slot 11), the Devourer
(slot 11) and the Endless Hunt (slot 8). None of the three creature records carries a reflect field of its own.
Leinth carries **no** reflect at all, which is why she does not produce this symptom.

**WHAT THOSE TWO NUMBERS ACTUALLY MEAN, and why Will's experience is the correct read:** one hit in three
returns **100% of the damage dealt** to the attacker. So the reflected damage **scales with the PLAYER's own
damage**, without limit. The better geared Will gets, the more certainly he kills himself - and any build that
can burst a boss down can one-shot itself doing it. That is not a hard fight, it is a stat that inverts
progression: investing in damage strictly increases the chance you die to your own hit. His "nearly
unkillable" is exactly what 100/33 produces.

**RECOMMENDATION (his call - this is a balance number): cut the MAGNITUDE, not the frequency.**
- Lowering `defensiveReflect` from 100 to roughly 25-35 keeps the "do not just facetank-spam him" signal, keeps
  a reflected hit genuinely painful, and stops it being lethal-by-construction to strong characters.
- Lowering `defensiveReflectChance` instead (e.g. 33 -> 5) leaves it a coin-flip instadeath that is simply
  rarer. That is worse design: the same feel-bad, just less often and less learnable.
- Health is the honest alternative lever he also offered, and it is strictly safer than reflect because it
  scales with the fight rather than with the player's build. Reflect first, health only if still needed.

**REQUIRED CHECK BEFORE EDITING - the orb04 lesson applies exactly.** `toxeus_passiveproperties` is a SHARED
record. Enumerate every creature that carries it BEFORE changing it in place; if anything outside the Toxeus
champions uses it, mint a champion-specific passive instead of editing the shared one, exactly as
`genericbossorb_05` was minted rather than editing `genericbossorb_04` and silently buffing 19 bosses.

**GATE:** assert the reflect pair stays within the ruled band on every Toxeus champion, and that no champion
regains a per-record reflect field that bypasses the shared passive. Plant a negative at 100.0 and confirm the
build reds.

### AMENDMENT - WILL'S SOUL-STACKING POINT: RIGHT AS A MECHANIC, BUT IT DOES NOT APPLY TO THESE THREE

**WILL, VERBATIM:**

> "note that his soul is equipped as an item so reflect damage on his soul adds on top of the reflect damage
> he has as a skill"

**THE MECHANIC HE DESCRIBES IS REAL and worth writing down as a standing consideration.** These champions DO
wear their own souls - `chanceToEquipFinger2 = 100.0` on all four records, with `lootFinger2Item1` naming their
own n/e/l soul triple - so any defensive property on the soul ITEM genuinely adds to whatever their skills
grant. That is a correct reading of the equipment model and it is not obvious from the records.

**BUT MEASURED ON `967b1f97`, IT CONTRIBUTES NOTHING HERE. The worn souls carry ZERO reflect and ZERO
retaliation:**

| champion | equips | soul %-reflect | soul flat retaliation |
|---|---|---|---|
| Enslaver | 100% | **none** | **none** |
| Devourer | 100% | **none** | **none** |
| Endless Hunt | 100% | **none** | **none** |
| Endless Hunt (Legendary variant) | 100% | **none** | **none** |

(`enslaver_soul_{n,e,l}`, `blood_toxeus_soul_{n,e,l}`, `toxeus_hunt_soul_{n,e,l}` - all nine records, every
`*reflect*` and `*retaliation*` field either absent or zero.)

**SO THE ENTIRE REFLECT IS THE ONE SKILL: `toxeus_passiveproperties` at 100.0 / 33.0.** Good news for the fix -
there is exactly one field pair to change and no hidden second source stacking behind it. Will's instinct to
check was right; the answer is that it comes back clean.

**A DISTINCTION THAT MATTERS FOR THE FIX, since the two get conflated:**
- **`defensiveReflect` (%)** returns a PROPORTION of the damage taken, so it scales with the player's own hit
  and is unbounded. This is what one-shots him.
- **`retaliation*` (flat)** deals a fixed amount back regardless of the incoming hit, so it cannot one-shot a
  healthy character. Harmless by comparison.
Only the first needs touching. Do not "fix" retaliation and report the reflect solved.

**STANDING CONSIDERATION FOR EVERY OTHER BOSS (not this fix, but bake it into future briefs):** **983** soul
records across this mod carry non-zero `retaliation*` fields, and monsters wear their own souls at 100%. So for
any OTHER champion the soul really can stack defensive properties onto the monster, and a difficulty
investigation that reads only the creature and its skills will under-count. **Always read the worn soul too.**
Worth a gate that sums a champion's skill-granted and soul-granted reflect and fails above a ruled ceiling.

**STATUS:** measured and specified, NOT implemented. Single lever confirmed: `toxeus_passiveproperties`
`defensiveReflect` 100.0 (chance 33.0), no soul contribution. Awaiting Will's number - my recommendation is
30. Everything else in R-100 for these champions proceeds unchanged, all three power additions included.

---

## R-104 [2026-07-29] Soul EQUIP chance: the real distribution, and what it means for the 50 -> 33 ruling

**WILL, VERBATIM, correcting me:**

> "no every monster does not wear it soul at full chance i dont think, you can tell when they have their soul
> equipped since they are stronger when it is on them"

**HE IS RIGHT AND I WAS WRONG.** I wrote "every monster wears its own soul at 100%" in the R-103 amendment. That
was an overgeneralisation from the four Toxeus champions, which are the ONLY creatures in the database at 100%.
Corrected here rather than left standing, because a wrong premise about this field would mis-scope every
soul-rate change.

**MEASURED DISTRIBUTION on `967b1f97` - 1,722 soul-bearing creatures carry a `chanceToEquipFinger2`:**

| chance | creatures | what it is |
|---|---|---|
| **100%** | **4** | exactly `um_toxeus_enslaver_99`, `um_bloodtoxeus_99`, `um_toxeus_hunt_99`, `um_toxeus_hunt_l_99` - R-48's fixed-spawn ubers. **Do not retune.** |
| **66%** | **373** | the largest non-zero cohort |
| **50%** | **361** | the cohort R-DROP-50 set, and the one his 50 -> 33 ruling names |
| 25% | 111 | |
| 10% / 5% / 2% / 0.5% / 0.3% | 77 | long tail |
| **0%** | **796** | carry a soul in the slot but NEVER equip it, so it can never drop - a separate latent problem, and much larger than the 22 detached creatures found by the b97 identity audit |

**HIS MECHANICAL OBSERVATION IS CONFIRMED AND IT MATTERS:** "you can tell when they have their soul equipped
since they are stronger when it is on them". Correct - an equipped soul applies its item properties to the
monster. Which means **`chanceToEquipFinger2` does DOUBLE DUTY: it is simultaneously the soul DROP rate and a
monster POWER switch.** Lowering it does not only make souls rarer, it makes those monsters weaker more often.

**THEREFORE, TWO THINGS TO PUT BACK TO WILL BEFORE IMPLEMENTING R-100 #19 ("decrease the general soul drop rate
for monsters who dont have a fixed spawn from 50% to 33%"):**

1. **WHICH COHORT?** There is no single general rate. He named 50%, which is 361 creatures - but the LARGER
   cohort sits at **66%** (373 creatures) and is untouched by a literal reading. Does #19 mean (a) only the 50%
   cohort -> 33, leaving 373 creatures at a HIGHER rate than the ones he just lowered, or (b) every non-fixed
   cohort down to 33, or (c) 66 and 50 both -> 33? Reading (a) is literal but produces an inverted result, so
   this needs his word rather than my inference.
2. **THE POWER SIDE EFFECT.** Cutting 50 -> 33 also means those monsters spawn WITHOUT their soul's stats 17
   percentage points more often - i.e. they get weaker, not just stingier. If he wants the drop rarer WITHOUT
   the power drop, that is a different and larger change (decouple the drop from the equip), and it should be
   costed separately rather than smuggled in.

**NOT AT ISSUE:** the four 100% champions stay at 100% (R-48), and #19 explicitly scopes itself to monsters
WITHOUT a fixed spawn, which those four are not.

**STATUS:** measured, correction recorded, R-100 #19 held pending his answer on cohort scope. Nothing changed.

---

## R-105 [2026-07-29] SOUL EQUIP/DROP RATE POLICY - 66% and 50% both go to 33%; the sub-25% cohorts need one more call

**WILL, VERBATIM:**

> "no monsters should be at 66%. move all 66% and 50% to 33%. Which ones are 25% or smaller? the ones that are
> smaller should be 33% I think unless they are bosses at fixed locations? i think we said 25% for fixed
> location bosses and 33% for non-fixed location bosses"

**RATIFIED AND UNAMBIGUOUS:** every creature at **66%** (373) and **50%** (361) -> **33%**. That is **734
creatures**. The four Toxeus champions stay at **100%** (R-48). His remembered policy - **25% for
fixed-location bosses, 33% for non-fixed** - is confirmed as the design rule and is now law of record.

**HIS POLICY MEMORY CHECKS OUT AGAINST THE DATA.** The existing 25% bucket is 111 creatures of which **108 are
`boss_*` fixed-location bosses** (Chimaera, Polyphemus, the Telkines, Dragon Liche and so on). So 25% already
means "fixed-location boss" in the shipped data. Nothing to change there.

**THE SUB-25% BUCKETS, MEASURED - 188 creatures, and they are THREE different kinds of thing:**

| rate | count | what they actually are | policy answer |
|---|---|---|---|
| 25% | 111 | **108 `boss_*` fixed bosses** + 3 oddities (`us_meritamen_34`, `spiderblackwidow01`, `bloodcrow_soul`) | **already correct** - leave at 25. The 3 oddities need eyeballing |
| 10% | 12 | all `boss_pharaohshonorguard1..4` - fixed bosses, but at 10 not 25 | **-> 25%** (fixed bosses, wrong rate) |
| 5% | 2 | **ours**: `um_calybe_20`, `um_lyialeafsong_18` | **-> 33%** (non-fixed ubers) |
| 2% | 39 | **all ours** - 13 heroes x n/e/l (`um_alethadarkclaw`, `um_amyntanimblebow`, `um_dimanae_19`, `um_inoniastrongheart_18`, `um_isadorasunspear`, ...) | **-> 33%** (non-fixed ubers; at 2% their souls effectively never drop) |
| 0.3% | 5 | `pharaoh'shonorguard_mummypriest_19..31` - boss-ish | **-> 25%** if fixed |
| **0.5%** | **13** | **ORDINARY TRASH MONSTERS** - `swift_ar_archer_08`, `swift_ar_huntress_10`, `swift_br_archer_14`, `duskyboar_17`, `gorgon_slayer_16`, `maenad_huntress_18`, `maenad_sorceress_20` | ⚠️ **NEEDS HIS CALL** |
| **0.3%** | **6** | **ORDINARY TRASH MONSTERS** - `cragharpy_witch_18`, `dayria_carrioncrow_40`, `carrioncrow_05/1/2/3` | ⚠️ **NEEDS HIS CALL** |

**THE ONE THING HIS POLICY DOES NOT COVER, and it must not be inferred.** His rule is stated in terms of
BOSSES - fixed versus non-fixed. But **19 of the sub-25% carriers are neither: they are ordinary trash
monsters** (archers, huntresses, a boar, crows, a harpy witch) sitting at 0.3-0.5%. A literal application of
"the ones that are smaller should be 33%" would raise **common respawning trash to a one-in-three soul drop**,
which would flood the game with souls and cheapen every soul in it. That is almost certainly not what he
means, but it IS what the words say, so it goes back to him rather than being quietly excluded.

Three options for him: (a) leave ordinary monsters at their current fractional rates - they are trash, the low
rate is the point; (b) give ordinary monsters their own tier, e.g. 5%; (c) genuinely take them to 33%.
**Recommendation: (a).** The 0.3-0.5% rates read as deliberate rarity on infinitely-respawning enemies, and
they are the only thing in this whole table that is NOT a boss or an uber.

**STILL SEPARATE AND STILL OPEN:** the **796 creatures at 0%** carry a soul in `lootFinger2Item1` that can never
be equipped and therefore can never drop. That is a latent content bug of its own, 35x the scale of the 22
detached creatures the b97 identity audit found. Not part of this rate policy; needs its own lane.

**IMPLEMENTATION NOTES:** this is the `DROP-50` constant's territory - the change must go through the same
single shared classifier rather than a second parallel code path (the b97 vet caught drifted duplicate logic
here before). Gate it: assert every cohort lands on its ruled rate, that the four champions stay at 100, and
plant negatives for a champion knocked off 100 and for a cohort left at 66.

**STATUS:** 66%/50% -> 33% is RATIFIED and ready to implement (734 creatures). The 10% and 0.3% boss buckets ->
25% follow from his stated policy. The 19 ordinary-monster carriers are HELD pending his answer.
