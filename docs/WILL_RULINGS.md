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

**ROUND 2 (2026-07-29, after an independent vet returned NO-GO). No shipped byte changed** - the vet
reproduced every byte-level and gate-level claim above exactly, and its single blocking item was a
DOCUMENTATION defect: this lane had written a **false** incident narrative (a merge accused of deleting
101 lines of this file) into this ledger, the BACKLOG gate record and the wave report. That is retracted
in all four places with every disproving command reproduced - see the RETRACTION block in the R-100
section below. Three substantive corrections also landed, each re-measured rather than restated:

1. **The name-tag cross-check's claim is now scoped to what it measurably catches.** It catches an
   out-of-namespace Toxeus that REUSES one of the four roster display tags; one that also invents a NEW
   tag is invisible to both derivations. Planted both cases against the built arz: roster tag ->
   `gate=FAIL` (caught), fresh tag -> `gate=PASS` (blind). The blind spot is EMPTY today (0 records
   outside the namespace carry a `*toxeus*` controller, wear a `*toxeus*` soul, or point at
   `genericbossorb_05`, over all 51,124 records), so this bounds the GATE, not the bytes.
   `BL-b101-DEBT-8`.
2. **The `dropItems = 0` claim is now evidenced, not asserted.** Exactly FIVE `Monster.tpl` records in
   all 51,124 combine `dropItems == 0` with a `treasureProxyName`: `q_leinth_47/49/50` ->
   `bosschestproxy_leinth` (a shipped, gate-proven, PLAYER-FACING drop) plus the two zzdev records this
   lane wired. So the two mechanisms are independent by this mod's own live precedent. This sets the
   severity of `BL-b101-DEBT-2`: `z_toxeus`'s apex orb is NOT rendered inert by `dropItems = 0`, so the
   Will-decision item is real. Still not in-game confirmed.
3. **The nearest adjacent exclusion is documented.** `um_enslaver_marauder_99` (same folder as three
   roster champions, `Monster.tpl`, no orb) is the Enslaver's summoned minion -
   `tagSVCMonsterEnslaverMarauder` -> `'{^r}Enslaved Shadow Marauder'`, its own constant commented
   `# hostile Champion` - correctly excluded, and now said so.

Round 2 also merged `main` @ `b376b61` (R-106 / R-106 amendment / R-107; docs + `tools/debug/probe_*.py`
only, verified to touch zero build inputs), cleaned four stale build logs off the repo root, re-cited the
tip baseline in place of the stale round-1 md5, and re-ran the full gated build to re-print the same
arz md5. Tag `build71-dev` marks the round-2 commit; `build69-dev` marks round 1 and the two are
BYTE-IDENTICAL by construction.

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

### R-100 #7 + #18 IMPLEMENTED (2026-07-30, `feat/uber-visibility`, the R-108 wave)

> Scoped strictly to items **#7** and **#18**. This block adds to the section, it does not rewrite any of
> Will's words or any other lane's item rows above.

**#7 - exclamation mark on every uber we made EXCEPT the Devourer: IMPLEMENTED**
(`tools/patches/uber_quest_markers.py`).

MEASURED FIRST (`py tools/patches/uber_quest_markers.py --analyze` on this branch's own build of `main`
@ `7efd107`, md5 `6a3a491db546b603c52132237c40aa63`): the placed-uber roster was **26 records and ALL 26
already carried `DisplayAsQuestItem = 1`** - including the Enslaver, both Endless Hunt forms, both Polis
Gaoler forms, Tantalus + Tantalus Unbound, the Mnemophage chain, Menoetes, and `um_bloodtoxeus_99`. So the
"give it to all of them" half of #7 was **already shipped by b91 and simply never deployed** - R-100's own
"TWO OF HIS REPORTS ARE EXPLAINED BY A DEPLOY THAT NEVER RAN" note applies verbatim to "the other major
bosses you have made ... do not have one". **No new code was needed for that half, and none was written.**

The only CODE change #7 needs is the EXCEPTION: the Devourer is MARKED in the shipped arz, and Will ruled he
must not be. `MARKER_EXEMPT` now names him with his ruling. Roster **26 -> 25 targets + 1 exempt**.

⚠️ **PRECISION, because the two states are easy to conflate.** `apply()` ENFORCES
`DisplayAsQuestItem = 0` on the exempt set rather than merely omitting it from the write loop, and the two
paths differ, both measured:
* against the shipped/BASELINE arz (a finished product this module had already marked), `apply()` genuinely
  **writes** the 0 - negtest plant 6 reports `before=1.0 after=0.0`;
* on a FRESH build the record reaches this module at 0 already, so the green build honestly prints
  `R-100 #7 EXEMPT 1 record(s) forced to DisplayAsQuestItem=0 (0 newly unmarked)`.

The 1 -> 0 delta in the record diff is therefore against the BASELINE ARZ, which is the correct
before/after for "what changes for the player". Enforcing rather than skipping is what lets the GATE assert
the 0, so a later writer cannot put the marker back and have nothing notice.

The exemption is a NAMED set because "hidden" is a placement property with no DB expression - but it cannot
rot: `_exempt_closure()` asserts every entry exists AND is a member of the derived roster (a stale entry reds
the build), and closes it over `actorToSpawnOnDeath` so a future Devourer transform form inherits the
exemption the same way rule B would have marked it. Measured: the Devourer has NO chain and no record spawns
him, so today's closure is exactly one record. Everything else stays roster-derived - a future uber that
lands in the placement proxies and pays a soul is marked with no edit here.

`--negtest` -> **PASS (8/8)**, including three new plants: re-marking the exempt boss is flagged (the
exemption is an invariant, not an omission), the exempt boss is out of the write roster and measured
`before=1.0 after=0.0`, and a stale exemption reds the build.

**#18 - the Guardians of the General must READ as uber: IMPLEMENTED**
(`tools/patches/general_guardians.py`, a NEW registry module that retunes the six
`svc_general_{a,b,c}_guard{1,2}` records `four_generals` builds).

**HE IS RIGHT ON ALL SIX COUNTS, AND TWO OF THEM ARE OUTRIGHT BUGS** (measured on the same arz):

| his words | measured |
|---|---|
| "they are small" | `scale = 1.45` - **SMALLER than the `am_warden_43` Champion they were cloned from (1.5)** and than their general (1.65). `_build_guards`' docstring calls 1.45 "a modest scale bump"; against its own donor it is a shrink. **BUG.** |
| "they look just like the other guys" | `mesh = XPack\Creatures\Monster\Machae\machae01b.msh`, **byte-identical to that warden's**. Both guards of a pair clone ONE donor, so they also match each other. |
| "super weak ... i killed them so fast" | `characterLife [3200, 4200, 5400]` vs their general's `[20244, 25305, 30366]` (the PAIR is 32% of one general); zero defensive resists; `characterLifeRegen 0`. Below every named elite escort this mod ships (`um_enslaver_marauder_99` 2.0/`[10000,14000,18000]`, `svc_diadochi_striderguard_97` 2.4/`[10000,14000,19000]`, `svc_tantalus_famishedshade_90` 2.0/`[4500,6500,9000]`). |
| "no special skills or anything" | kit = `armor_passive`, `bonusdamage_physical`, `shieldcharge`, `specialAttackSkillName = shieldcharge` - **all four inherited VERBATIM from the donor. `four_generals` added zero skills**, so a "named elite honor guard" fights exactly like the trash beside it, and all six fight identically. **BUG.** |
| "they dont have any chests" | the three `q_general_*_guardpair` proxies carry no `accessory1/Epic1/Legendary1`. |
| "dont drop any orbs" | no `treasureProxyName` on any of the six. |
| "besides their red names" | correct, and already true: the `{^r}` is in the tags `four_generals` minted. Those names were the only part of these six ever held to the amgoz1 bar. |

**THE FIX, held to the amgoz1 bar - identity, not a stat multiplier.** `four_generals` had already written
each guard's identity into its NAME and then never implemented it, so each guard now gets the SIGNATURE PAIR
of skills its own epithet demands, and no two of the six share one:

| guard | name `four_generals` gave it | signature (`†` = rides a blank-anim CLONE, see the round-2 correction below) |
|---|---|---|
| a1 | `{^r}Ravok the Lawless ~ Machae Reaver` | `minotaur_onslaught` + `gigantes_groundbreaker` |
| a2 | `{^r}Sethuun ~ Machae Soul-Warden` | `empusa_spirit_lifedrainnova` + `hero_slowspiritbolt_ring` |
| b1 | `{^r}Bhikru the Bilespitter ~ Machae Venomancer` | `hero_vomitbile`† + `empusavenomancer_venombolt`† |
| b2 | `{^r}Nakoth ~ Machae Plague-Ward` | `empusa_venom_venomcloud` + `hero_poisonwave` |
| c1 | `{^r}Kharzun the Ember ~ Machae Pyre-Ward` | `empusa_pyro_pillarofflame` + `hero_flamewave`† |
| c2 | `{^r}Voreth ~ Machae Cinder-Reaver` | `gigantes_shieldcharge`† + `hero_bouncingfire_ring` |

*(All six ALSO keep a slot-1 special, `shieldcharge`, which round 1 left on the shipped record and round 2
repointed to a fifth blank-anim clone. Round 1 shipped all five of those as silent no-ops.)*

Plus, every number derived from something already in the db rather than invented:
* `scale` **1.45 -> 2.0** - `um_enslaver_marauder_99`'s own scale, i.e. the encounter **Will himself points
  at as the model in this same message** (#13: "give ... some guys they can summon like toxeus the murderer
  enslaver of souls has"). 33% over every machae in the room, 21% over their general.
* `characterLife` -> **45% of the general each pair guards, per difficulty** = `[9110, 11387, 13665]`. The
  pair is ~91% of one general combined: a real fight that never eclipses the boss. Inside the measured house
  band on all three difficulties. `characterLifeRegen 0 -> 5.0` (the general's own value).
* themed resists per general element (`defensiveLife` / `defensivePoison` / `defensiveFire` at 35, shared
  `defensivePhysical` 20 - the marshal's 30 one tier down), never a flat wall.
* **orb** -> `genericbossorb_03`. The ladder, measured: `01` = ten L16-20 bosses; `02` = five, INCLUDING our
  own Champion escort `svc_obs_escort_permean` (so a Champion on a boss orb is shipped precedent); `03` = six
  L45-48 bosses, the guards' own `charLevel [42,58,72]` band; `04` = nineteen incl. their marshal; `05` = the
  eight-record Toxeus apex roster **reserved by R-99** and gate-locked by `uber_apex_orb.verify()`. `03` is
  the honest rung and it touches neither audited tier. Nothing about the orb records is edited - a pointer,
  not a shared-record write.
* **chest** -> ONE dedicated hoard per PAIR (monolith `_svc_build_dedicated_hoard` recipe, 9 new records per
  general), wired to the pair proxy's `accessory1/Epic1/Legendary1`. `LockedClassification` is overridden
  from the recipe's `Boss` to **`Champion`** - the guards ARE Champions, so a Boss lock would seal the chest
  **forever**; `Champion` is a shipped valid value whose three carriers include `hidden_bloodcave_chest_01`,
  the very donor this chain clones. The accessory mechanism hard-caps at ONE chest per difficulty
  (`Proxy.tpl` exposes no `accessory2..N`), so **this cannot reproduce #9's three-Tantalus-Hoards problem**.
* **b76 / R-31 DENSITY LAW HELD BY CONSTRUCTION:** not one of the twelve signature skills is a pet-spawner,
  and `verify()` re-asserts that mechanically (no `Skill_*SpawnPet*`, no `spawnObjects`). This lane adds
  **zero** permanent entities to the Hades war-council rooms.
* `monsterClassification` stays **Champion** and the soul loot stays cleared, deliberately: promoting to Hero
  would make them soul-eligible under `wire_souls_to_monsters` and collide head-on with **R-106**. Will asked
  for chests and orbs, not souls.

`--negtest` -> round 1 reported **PASS (14/14)**, including "reverted to the shipped 1.45", "scale merely
equal to the plain warden donor", "reverted to the shipped `[3200,4200,5400]`", "guard HP raised above its
general", "orb moved onto R-99's reserved apex tier", "chest left on the recipe's Boss lock (never opens)",
"guard promoted to Hero", "general de-quested", and a pet-spawner smuggled into a guard kit.

> ### 🛑 ROUND-2 CORRECTION (2026-08-05): FOUR OF THE TWELVE COULD NOT FIRE, AND THE 14/14 GATE COULD NOT SEE IT
>
> **The round-1 statement "12 distinct signature skills" was TRUE about the WIRING and FALSE about the
> PLAY.** Measured on round 1's own build (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`,
> 51,151 records), not inferred:
>
> * every guard binds `charAnimationTableName = records\xpack\creatures\monster\machae\anm\anm_machae.dbr`;
> * that table declares exactly FOUR `<row>SpecialAnimRef<N<=15>` clip names - `bow1='HeavyShot'`,
>   `sHanded1='ThunderClap'`, `spear1='Slam'`, `spear2='Strike'`;
> * Game.dll's `SkillManager::StartSkill` aborts a special SILENTLY when the caster's table has no clip for
>   the skill's `skillSpecialAnimationName` (this repo's own crash-law RE, already applied once as the b42
>   Ephialtes Dread Nova fix in `tools/apply_svc_patches.py`);
> * so these **NEVER FIRED**: `hero_vomitbile` ('Belch', guard b1), `empusavenomancer_venombolt` ('Belch',
>   guard b1 - BOTH of its two), `hero_flamewave` ('ShadowScythe', guard c1), `gigantes_shieldcharge`
>   ('Charge', guard c2);
> * and the slot-1 special all six INHERITED, `records\skills\defensive\shieldcharge.dbr`, names
>   'ShieldCharge', also absent - on `skillName3` AND `specialAttackSkillName`, on all six.
> * **20 dead cast slots in total. Bhikru the Bilespitter (b1) therefore had ZERO castable specials of any
>   kind**, so Will's complaint ("no special skills or anything to make them even noticeable") was left
>   literally true for one of the six.
>
> **TRUE STATEMENT AFTER THE ROUND-2 FIX:** twelve distinct signature skills over six monsters, **EIGHT
> pointed at the shipped record verbatim and FOUR riding a mod-authored blank-anim CLONE** of it, plus the
> inherited slot-1 special repointed to a fifth clone on all six. Fix = the b42 recipe: clone into
> `records\skills\svc\` and blank the clone's `skillSpecialAnimationName` so the cast rides the default
> attack clip every rig has. **CLONE, NEVER EDIT** - the five donors carry other monsters (venombolt alone
> has 25, `shieldcharge` 85 other carrier slots); `verify()` proves on the built db that every donor still
> holds its shipped clip name and every clone holds none.
>
> Repick-a-clip-the-rig-HAS was considered and rejected per skill: the four clips are per weapon ROW
> (bow/sHanded/spear) and the guards' weapon comes from a 100%-chance loot pool, so a repick would be
> castable only on some rolls; blanking is row-independent.
>
> **THE GATE IS THE REAL FIX.** `general_guardians.verify()` now asserts, for every guard and every
> `skillNameN` / `specialAttack*SkillName` slot, that the named `skillSpecialAnimationName` is empty or
> present in that creature's OWN resolved animation table - and reds otherwise. Planted negatives prove it
> catches exactly the round-1 defect ('Belch'), a clip that exists nowhere, the raw-donor wiring, the
> inherited dead slot-1, a donor edited in place, and an unresolvable anim table; a matching positive
> proves a clip the rig DOES declare is still accepted, so the rule is membership, not "must be empty".
> Standalone re-measurement: `py tools/patches/general_guardians.py --castability <arz>`.
>
> **LESSON, and it is the point of this correction:** the round-1 gate checked that the twelve skills were
> WIRED, RESOLVED and pet-free. It never checked they could be PLAYED. A gate that passes 14/14 on the
> defect it exists to catch is worse than no gate, because it is cited as proof.

**⚠️ ONE #18-ADJACENT CALL IS DELIBERATELY NOT GUESSED AND GOES BACK TO WILL: do the Guardians get
exclamation marks too?** #18 calls these six "the uber bosses we added" while #7 asks for a marker on "all
the uber bosses we made" - but `uber_quest_markers` rule A marks placed encounters that pay a SOUL, and the
guards pay none, so they are mechanically outside the roster; and three markers per war-council room (general
+ two guards) is precisely the map spam rule A exists to prevent. They ship UNMARKED. If Will wants them
marked it is one line (a pinned extra set in `uber_quest_markers`). Registered as debt.

> **MEASURED 2026-07-30 (independent re-verification pass, same lane), and it settles HOW - not WHETHER:**
> the obvious "just derive it, don't hand-list it" idea - mark any placed monster carrying a dedicated
> `genericbossorb_*` - **OVER-CAPTURES BY EXACTLY ONE RECORD** and therefore cannot be used as-is.
> Measured over the built arz (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`,
> md5 `b55515970be41c2542208e84a8705640`): of the 27 placed records rule A excludes as retinue/adds,
> **7 carry a boss orb - the 6 Guardians (`genericbossorb_03`) plus `svc_obs_escort_permean.dbr`
> (`genericbossorb_02`), which is an ESCORT ADD and must not get a marker.** All 27 adds are rank
> `champion`, so rank cannot separate them either. So if Will says yes, the honest shape is the pinned
> extra set the paragraph above names (symmetric with `MARKER_EXEMPT`, cross-checked against the derived
> roster so it cannot rot), NOT a widened derivation. This measurement is recorded so the next lane does
> not spend the effort re-deriving a rule that does not close.

**ALSO NOT DONE HERE (visual):** the two guards of a pair still share one `mesh`. Differentiating them means
a mesh swap, which is the exact class of change the `fix/green-mesh-swap` lane is in flight on and which
needs an in-game check. The "stop being a lookalike" win here comes from `scale 2.0` (33% over every machae
in the room) plus twelve loud, distinct attack FX. Per-guard ambient aura FX (`charFxPakRunningNames`) was
considered and rejected: the shipped candidates are `svc_black_poison_charfxpak` and `svc_ashsmoke_charfxpak`,
which the `black_poison` lane's own gate audits. Registered as debt.

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

### SIXTH AMENDMENT - **BUILT (b102, `fix/green-mesh-swap`).** What shipped, and the two places this ruling was wrong.

**STATUS: R-102 IMPLEMENTED in data on `fix/green-mesh-swap`. NOT DEPLOYED, NOT SEEN BY WILL.**
Nothing below claims a colour or a silhouette in game - the player-surface checklist forbids that, and
this whole bug exists because four waves claimed exactly that. What is claimed is measured.

**NO NEW RULING NUMBER WAS MINTED, deliberately.** The decade census
(`git grep -ohE "R-[0-9]+" <branch> -- docs/WILL_RULINGS.md` over every local branch) returns **R-124** on
`feat/devourer-kit` and R-119 on four others, so 103+ is an active race between in-flight lanes. This lane
amends the ruling it was given instead of claiming a number it would have to defend.

**THE ROOT CAUSE, RE-MEASURED FIRST-HAND rather than cited.** `tools/mesh_assets.embedded_fx_of()` reads
the `.msh` binary out of `Creatures.arc`:

| mesh | embedded effect entity | bones |
|---|---|---|
| `Creatures\Monster\Skeleton\RevenantPoison.msh` | **`Records\Effects\MonsterFX\Buffs\RevenantPoison_FX.dbr`** | 20 |
| `Creatures\Monster\Skeleton\SkeletonGrayBlack01New.msh` | **none** | 20 |
| `Creatures\Monster\Skeleton\GoldenSkeleton01.msh` | **none** | 20 |
| `Creatures\Monster\ShadowStalker\ShadowStalker.msh` | `Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr` | 30 |

and that effect entity, read out of the base-game `.arz`, is `boneList = Bone_R_Weapon; Bone_L_Weapon` ->
`Effects\MonsterFX\Buffs\RevenantPoison.pfx`, whose own bytes name **`Shaders\Particle\ParticleAdditive.ssh`**.
An additive-blend particle is precisely Will's *"it depends on the lighting"* - so that tell is now
mechanism, not inference. (The b92 colour decode R 0.534 / G 1.000 / B 0.591 is CITED, not re-derived: a
naive float scan of the `.pfx` found no normalized triple, so this lane does not claim a colour number of
its own.)

**WHERE THIS RULING WAS WRONG, ONE.** It named `ShadowStalker.msh` as "the evidenced choice". It is not,
for two independently sufficient reasons: **(a)** it is not effect-free - it carries
`ShadowStalker_Smoke.dbr` - so it is evidence about one particular effect being black, not about the mesh
class being clean; and **(b)** `um_toxeus_hunt_99` ALREADY WEARS IT, so putting the Enslaver on it would have
fixed the Enslaver-vs-Devourer collision by creating an Enslaver-vs-Hunt one. The ruling's own warning
against "fix the green and break R-93 in the same commit" applied to its own recommendation.

**WHERE THIS RULING WAS WRONG, TWO - and this one is the good news.** It called the mesh swap the
*dangerous* half ("A mesh swap re-rigs everything... he T-poses or goes uncastable"). Measured, it is the
opposite for this swap. Both champions bind `anm_skeleton01`, and that table plus all **40** inline
overrides on each champion record are built from **`SkeletonGrayBlackNEW_*.anm`** - the animation set of
`SkeletonGrayBlack01New.msh`. The Enslaver has been playing SkeletonGrayBlack clips on a RevenantPoison
body all along. Moving him onto `SkeletonGrayBlack01New.msh` puts him on the NATIVE mesh of his own clips:
this swap **removes** a cross-rig mismatch. Bone sets are identical (20/20, same names) across
RevenantPoison, SkeletonGrayBlack01New and GoldenSkeleton01, so nothing an existing clip drives goes
missing, and every `*SpecialAnimRef*` that serves LethalStrike / AoE360 / BloodBoil / Summon lives on the
animation TABLE, which the mesh is not part of.

**WHAT SHIPPED**

| champion | mesh | why this one, measured |
|---|---|---|
| Enslaver of Souls (monster + every pet tier + 2 preview proxies) | `SkeletonGrayBlack01New.msh` | FX-free; identical rig; **native mesh of the clips he already plays**; `newskeleton_charcoal.tex` on this mesh is a shipped pairing |
| Devourer of Blood (monster + every pet tier + the End-of-All-Things pets + 2 preview proxies) | `GoldenSkeleton01.msh` | FX-free; identical rig; only **4.6%** of its bytes differ from RevenantPoison, so his silhouette survives the fix; 464 shipped users, 59 of them on a `NewSkeleton_*` override + `ANM_Skeleton01` |
| The Endless Hunt | `ShadowStalker.msh` (unchanged) | already distinct; its embedded smoke is the one Will looked at and called "the proper black shroud", so it is grandfathered BY NAME rather than ignored |

**R-93's mesh half is therefore also delivered**: three champions, three distinct meshes, none of them the
green one. `Skeleton01.msh` was the other FX-free candidate and was **rejected**: it differs from
`SkeletonGrayBlack01New.msh` by 784 bytes out of 348,798 (**0.2%**) - it is the same model, so using both
would have satisfied R-93 on paper while leaving two champions that still read as one creature.

**THE SECOND AMENDMENT'S SHROUD GAP IS CLOSED.** `svc_enslaver_shroud` now covers `{monster}` +
`{every pet tier}`, and the tiers are **derived** from `summon_toxeus_enslaver.spawnObjects` rather than
listed, so a future 4th tier is in scope for the fix and the gate with no code change. The gate also
asserts the pets' controller actually fires self-buffs (`BuffSelfBehavior = WhenEnemyIsSeen`) - a
`Skill_BuffSelfToggled` that the AI never toggles is an empty slot, and nothing would have caught that.

**SHARED-RECORD LAW, both directions.** `RevenantPoison.msh` has **30** carriers in the built arz and only
**13** are ours. The other 17 - four base/SV green revenants (whose green is INTENDED: they wear
`newskeleton_grean.tex`, and `um_toxeus_21` is one of them), ten `pharaohshonorguard_mummyguardian_*`
summons and the `old_z_toxeus` dev dummy - are untouched, and the gate FAILS if the mesh ever reaches zero
carriers (RETIREMENT PROTOCOL: this lane repoints, it never retires).

**THREE THINGS THIS LANE DID NOT DECIDE, listed so they are not mistaken for done:**
1. **Does the End of All Things want a FOURTH distinct silhouette?** It is a crafted supra pet cloned from
   the Devourer's pets and it follows his mesh today, which kills its green for free. Whether the
   apotheosis of the line should look like its own creature is a design call, Will's, not this lane's.
2. **How any of it READS in game.** Unseen. Colour and silhouette claims need Will's eye
   (`BL-R102-DEBT-1`).
3. **The `Build\Resources\` animation defect.** `spearSpellAttackAnim` on **306** records - Charon, the
   liches, the base skeleton pets, Iron Lore test monsters, and two of ours by inheritance - names an
   ArtManager BUILD PATH that resolves nowhere at runtime. It ships that way in the base game, it is
   unrelated to the mesh, and repointing 306 mostly-not-ours records is a different lane. The animation
   gate EXCLUDES that one prefix by name, loudly, rather than passing silently or failing on a base-game
   defect (`BL-R102-DEBT-3`).

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
> ⚠️ **RATES SUPERSEDED BY R-243 (2026-08-12):** the two NUMBERS below (33% non-fixed / 25% fixed-location boss) are lowered to **20% non-fixed / 10% fixed-location boss** by R-243 (at the end of this file). Everything else about R-105 - the classifier, the count-over-class tension, the 0%/100% pins, the HELD cohorts - is UNCHANGED. Read R-243 for the current rates.

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

---

## R-106 [2026-07-29] "Only hero monsters should drop their soul" - RATIFIED as the rule, but the data inverts his premise

**WILL, VERBATIM:**

> "most of the monsters that have a soul are probably trash monsters, only hero monsters should drop their soul"

**THE RULE IS RATIFIED:** soul drops belong to Hero / Champion / Quest / Boss class creatures. Common (trash)
monsters should not drop souls.

**BUT HIS FACTUAL PREMISE IS THE WRONG WAY ROUND, and this is good news for the rate change.** The engine's own
`monsterClassification` field is authoritative here (Common / Champion / Hero / Quest / Boss), and it beats the
name-based guessing I used in R-105. Cross-tabulated over all **1,722** soul-bearing creatures:

| rate | Boss | Hero | Quest | Champion | Common | unset | total |
|---|---|---|---|---|---|---|---|
| **100%** | 4 | . | . | . | . | . | 4 |
| **66%** | 34 | **222** | **117** | . | **0** | . | 373 |
| **50%** | 14 | **347** | . | . | **0** | . | 361 |
| **25%** | 106 | . | 3 | . | **0** | 2 | 111 |
| 10% | 12 | . | . | . | 0 | . | 12 |
| 5% | 1 | 1 | . | . | 0 | . | 2 |
| 2% | . | 39 | . | . | 0 | . | 39 |
| 0.5% | . | . | . | 6 | **6** | 1 | 13 |
| 0.3% | . | . | . | 1 | **9** | 1 | 11 |
| **0%** | 9 | **28** | 1 | 172 | 324 | 262 | 796 |
| TOTAL | 180 | 637 | 121 | 179 | 339 | 266 | 1722 |

**THREE CONSEQUENCES, all measured:**

1. **THE R-105 RATE CHANGE IS SAFE AND NEEDS NO NARROWING.** Every one of the 734 creatures going 66%/50% ->
   33% is already **Hero, Quest or Boss**. There are **ZERO Common monsters** in either cohort. His worry about
   blanket-raising trash does not apply - the rule was already being followed at those rates.

2. **ONLY 15 COMMON MONSTERS HAVE ANY SOUL CHANCE AT ALL**, and they are exactly the ones flagged in R-105:
   6 swift archers at 0.5%, plus 4 carrion crows and 5 `pharaoh'shonorguard_mummypriest_*` at 0.3%.
   **Per this ruling those 15 go to 0%.** (Note the mummy priests classify as **Common** despite a boss-ish
   name - which is precisely why the classification field, not the filename, is the authority. My R-105
   suggestion to raise them to 25% was wrong and is withdrawn.)

3. **THE REAL DEFECT IS THE MIRROR IMAGE, AND IT IS 14x BIGGER: 210 HERO/CHAMPION/QUEST/BOSS CREATURES SIT AT
   0%** and therefore can never drop the soul they carry - 28 Hero, 172 Champion, 9 Boss, 1 Quest. Examples:
   `hero_adarathelovely_43`, `um_legion_28/28a/28b`, `am_carrionlord_12/15`, `bm_plaguelord_10/12`,
   `em_sirenofthedeep_37`, `ember_satyr_warden_55`, `us_mormo_16`, `ar_slayer_11/14`, `am_giganticbat_12/14/16`.
   **"Only heroes should drop souls" is nearly true already; "heroes SHOULD drop souls" is broken 210 times.**
   That is where the real content is missing, and it is the same defect class as the 22 detached creatures the
   b97 audit found - at 10x the scale.

**THE 324 COMMON AT 0% ARE CORRECT** under this ruling and must be left alone. Do not "fix" them upward.

**IMPLEMENTATION for this ruling:** derive the target rate from `monsterClassification`, never from the record
name or folder. One shared classifier (the b97 vet already caught drifted duplicate logic in this exact area).
Gate it: no Common carrier above 0%, every Hero/Quest non-fixed carrier at 33%, fixed bosses at 25%, the four
Toxeus champions at 100%, and plant a negative for a Common monster nudged to 33%.

**OPEN FOR WILL:** the 210 hero-class zeroes are a content decision, not just a rate flip - each needs a soul
that suits the creature (the amgoz1 bar), and some may be deliberately soul-less. Recommend a dedicated lane
that reports the roster with a proposed soul per creature before changing anything.

### AMENDMENT - HIS CRITERION IS A DISPLAY ONE. MAPPED. AND THREE OF OUR OWN UBERS CANNOT DROP THEIR SOULS.

**WILL, VERBATIM:**

> "gigantic bats are probably not heroes with stars above their heads. only guys with stars above their heads or
> better should drop souls, or guys with purple names"

**HIS DOUBT ABOUT THE BATS WAS HALF RIGHT, AND THE HALF THAT WAS WRONG MATTERS.** They are not Hero - measured,
`am_giganticbat_12/14/16` are **`Champion`**. But **Champion IS the star tier**: a Champion is precisely the
beefed-up monster that displays a star above its head. So by his own criterion - "stars above their heads **or
better**" - the gigantic bats **do** qualify. The question he actually needs to answer is therefore narrower
than it looks:

**DOES "STARS OR BETTER" INCLUDE THE WHOLE CHAMPION TIER? That is the 172-creature decision.** The engine's
classes map onto his display language like this:
- **`Champion`** -> star above the head. 172 of the zeroes. Beefed-up ordinary monsters, spawned in numbers:
  gigantic bats, carrion lords, plague lords, `ar_slayer`, `ember_satyr_warden`, the `mutated_*` variants.
- **`Hero`** -> the purple/named uniques he described. **28** of the zeroes: `hero_adarathelovely_43`,
  `um_legion_28/28a/28b`, `us_frostscarab_35`, `um_morbi_17`, `hero_grom_31`, `hero_wheedletongue_41`,
  `ur_masai_43`, `us_poisonsiren_14`.
- **`Boss`** -> **9**. See below, because this is the real find.
- **`Quest`** -> 1 (`01_akara`, already a known WILL DECISION as `BL-b97-DEBT-7`).

**MY RECOMMENDATION: Hero + Boss + Quest yes, Champion NO.** Champions are ordinary monsters wearing a star and
they spawn in quantity - 172 records, many in n/e/l triples of the same creature. Souls from them would be
common by volume even at a modest rate, which is the flooding problem in a different costume. His instinct to
squint at the bats is the right instinct even though their class technically qualifies. **This is his call, not
mine** - it is the difference between roughly 38 creatures and roughly 210.

### 🔴 THE ACTUAL BUG, FOUND IN PASSING: THREE OF OUR OWN UBER BOSSES CAN NEVER DROP THEIR SOULS

Of the 9 `Boss`-class carriers stuck at 0%, three are **ours**, and they are fixed-location ubers we built:
- `um_charon_ferryman_99.dbr`
- `um_polisgaoler_99.dbr`  *(the Soul Gaoler - also R-100 #17 and R-101's key leak)*
- `um_tantalus_99.dbr`  *(also R-100 #8, outside his den, and #9, three chests)*

Plus base/SV bosses `us_mormo_16`, `ur_uber_45`, `um_inkeyes_45`, `um_inkeyes2_45`, `um_bloodcrow_50`,
`um_bloodcrow_50_l`.

**These need no policy decision at all.** They are fixed-location bosses, so R-105 already rules them at **25%**,
and they are currently at **0** - carrying a soul that can never drop. That is a plain defect in our own content
and it should be fixed in the same lane as the rate sweep, not held behind the Champion question.

**STATUS:** rule ratified. R-105's 734-creature change confirmed safe. 15 Common carriers -> 0%. My R-105
mummy-priest suggestion withdrawn (they are Common). **Three of our own uber bosses at 0% -> 25%, no decision
needed.** The Champion tier (172 creatures) is HELD pending Will's yes/no; Hero + Boss + Quest zeroes proceed to
a content lane that proposes a soul per creature.

---

## R-107 [2026-07-29] Gaoler soul scoping (already correct - I was wrong), and WHY the Devourer is unkillable

**WILL, VERBATIM:**

> "yeah so the soul gaoler should not drop the soul just the unbound final version. also i just tried to kill the
> blood cave toxeus the devourer and I one hit myself when i hit him, he is basically unkillable with the current
> reflect damage unless you use pets to kill him but i am playing on epic and i have two toxeus the murderer,
> enslaver of souls pets summoned and they cant kill him so i guess i cant kill him"

### PART 1 - THE GAOLER RULING IS ALREADY IMPLEMENTED, AND MY EARLIER CLAIM WAS WRONG

**CORRECTION.** In the R-106 amendment I listed `um_polisgaoler_99` among "three of our own ubers that can never
drop their souls - a plain defect". That was wrong. Measured:

| record | class | soul chance | soul carried |
|---|---|---|---|
| `um_polisgaoler_99` (base) | Boss | **0.0** | `wardenofsouls_soul_{n,e,l}` (the base game's) |
| `um_polisgaoler_unbound_99` (final) | Boss | **66.0** | `polisgaoler_soul_{n,e,l}` (**ours**) |

The base Gaoler already does not drop, the unbound final form already does, and they carry **different** souls.
**His ruling was already satisfied before he gave it** - so the correct action here is NOT to raise the base
Gaoler. It is: leave the base at 0, and take the unbound form **66% -> 25%** under R-105's fixed-boss rate.
The two remaining genuine 0% defects from that list stand: `um_charon_ferryman_99` and `um_tantalus_99`.
(Both Gaolers still leak the Warden key - R-101 is unaffected.)

### PART 2 - ⚠️ THE REFLECT CUT CANNOT BE MADE IN PLACE. IT WOULD NERF WILL'S OWN PETS.

`toxeus_passiveproperties` has **18 carriers**, and they are not all things Will fights:

- **Monsters he fights (7):** `um_toxeus_enslaver_99`, `um_toxeus_hunt_99`, `um_toxeus_hunt_l_99`,
  `um_bloodtoxeus_99`, `um_toxeus_21`, `um_toxeus_99`, plus `drxcreatures\crowheroes\less.dbr` -
  **a DRX crow hero that is not a Toxeus creature at all** (pure collateral).
- **PETS HE SUMMONS (9):** `pets\toxeus_enslaver_{1,2,3}`, `pets\bloodtoxeus_{1,2,3}`, `pets\toxeus_eoat_{1,2,3}`.
- 2 zzdev dummies.

**So a one-line edit of `defensiveReflect` 100 -> 30 would also strip 70 points of reflect off the very pets
Will is using to try to kill this boss.** That is the exact failure mode the `genericbossorb_04` lesson exists to
prevent, and it would have silently made his situation worse while the commit message said "made the boss more
killable".

**REQUIRED IMPLEMENTATION:** mint a **monster-only** passive (clone of the current record) carrying the reduced
reflect, point the 6 Toxeus MONSTERS at it, and leave the 9 PET records on the original 100/33 so his summons
keep their defence. `less.dbr` also stays on the original - it is not ours to retune. Gate it: assert no pet
record ever lands on the monster passive and vice versa, and plant a negative both ways.

### PART 3 - WHY HE CANNOT KILL HIM, MEASURED. REFLECT IS NOT THE ONLY WALL.

Devourer, on **Epic** (the difficulty he is playing), from the built record plus the shared passive:

| | value |
|---|---|
| `characterLife` | 13,000 / **18,000** / 24,000 (n/e/l) |
| `defensivePierce` | **70%** |
| `defensiveBleeding` | 80% |
| `defensivePoison` | 80% |
| `defensiveLife` (vitality) | 100% |
| `characterDodgePercent` | 15% |
| `characterDeflectProjectile` | 33% |
| `defensiveBlockModifierChance` | 25% |
| `defensiveConfusion` / `defensiveConvert` | 150% each |
| **reflect** | **100% at 33% chance** |

**THE THING WORTH SEEING: his own character is a SPEAR user - pierce damage - and this boss has 70% pierce
resistance.** So Will is simultaneously (a) dealing roughly a third of his damage, and (b) taking his own full
hit back one time in three. That is not a hard boss, it is a hard counter to his specific build wearing a
one-shot mechanic. And his pets fail for the same reason: the Enslaver pet kit is physical/pierce-flavoured
into 70% pierce plus 15% dodge plus 33% deflect on 18,000 life.

**THREE LEVERS, in the order I would pull them (all his call, all numbers his to set):**
1. **Reflect 100 -> ~30** on the monster-only passive. Fixes the one-shot, which is the actual blocker, and
   costs nothing elsewhere.
2. **`defensivePierce` 70 -> ~40.** This is the quiet one that makes the fight feel possible rather than merely
   survivable, and it is the reason pets are not working either. 70% resistance against a spear build is a
   near-immunity.
3. **`characterLife`** last. It is the honest lever he offered, but cutting life shortens a fight that is
   currently unwinnable rather than long - fix the first two and this may not be needed.

**DO NOT** touch Bloodbath, Blood Frenzy or the summons (R-103: "harder is the point, keep all three", "the
answer is not cutting skills but cutting elsewhere").

**STATUS:** measured and specified, NOT implemented. **Will is currently HARD-BLOCKED from finishing this
encounter**, so this outranks the rest of the R-100 batch. Awaiting his numbers; my recommendations are reflect
30 and pierce 40.

---

## R-109 [2026-07-30] Tombstone XP recovery must EQUAL the XP lost on death

**WILL, VERBATIM, in two steps - the second SUPERSEDES the first and is the ruling:**

> "one thing we need to check is when you go find your tombstone after you die, you should only get 10% of the
> original xp that is awarded since we cut the death penalty"

> "lets make the tombstone xp recovery match the xp lost upon dying"

**THE RULING IS THE INVARIANT, NOT THE NUMBER: `XP recovered from the death marker == XP lost to the death
penalty`, exactly, on every difficulty.** Implement the equality; do not hardcode 10%.

**WHY THE SECOND FORM IS THE BETTER RULE, and why it must be built as stated.** "10% of the original" is only
correct while b93's cut happens to be 90%. If the death penalty is ever retuned again - and R-103 shows Will
does retune numbers once he has played with them - a hardcoded 10% silently desynchronises and re-opens the
exploit. Deriving the recovery FROM the penalty makes the pair self-correcting: change the penalty, the marker
follows automatically.

**THE BUG THIS CLOSES, which we introduced.** b93 cut `deathPenaltyEquation` to
`(currentPlayerLevel^3) * ((1 + (3 * gameDifficultyDV)) / 90)` and `deathPenaltyMax` 500000 -> 50000. If the
death-marker recovery still pays the pre-cut amount, then **dying and walking back to the marker is a NET XP
GAIN** - the player loses 10% and recovers 100%. That is a free-XP loop created by our own change, and it is
exactly the kind of coupled field a single-value edit misses.

**IMPLEMENTATION:**
- Find the field/equation governing what the death marker returns. Do not assume it is a mirror of
  `deathPenaltyEquation`; measure what it actually pays today.
- Express the recovery in terms of the penalty so the two cannot drift. If the engine will not accept a derived
  expression, then mirror the penalty's own equation verbatim and add a gate that fails when they differ.
- **Report the measured before/after BOTH WAYS** - XP lost on death, and XP recoverable from the marker - at
  several levels across all three difficulties, so the equality is provable rather than asserted.

**GATE (tighten what the R-108 wave was briefed with):** the wave's brief said `recovered <= lost`. That was
the weaker safety form and it is now SUPERSEDED - assert **equality**. `recovered < lost` is no longer a pass:
it would quietly punish the player twice. Plant negatives on both sides: recovery above the penalty must red
the build, and recovery below it must red the build.

### AMENDMENT - **MY PREMISE WAS WRONG. THERE WAS NEVER A FREE-XP EXPLOIT.** Disproven from the engine.

I wrote above that "dying and recovering the marker is a NET XP GAIN - a free-XP loop we introduced". That is
**FALSE**, and the lane disproved it from `Game.dll` rather than accepting it. Recorded prominently because the
wrong version was stated confidently, in the ledger, twice.

**WHAT THE ENGINE ACTUALLY DOES** (disassembled, capstone, VAs given so anyone can re-check):
- There is exactly ONE `"RedemptionMultiplier"` literal (VA `0x10346548`).
- It has exactly ONE writer - the push at `0x1019b8ba` supplying the **0.5f** default - and exactly ONE reader,
  `mulss xmm0,[edi+0x2a04]` at `0x10194fca`, inside `GetPlayerExperienceRedemptionAmount`.
- **The load-bearing find:** `RegisterExperienceLoss` stores its arg2 into `GraveInfo+0x0C`, and at its single
  call site (`0x10208012`) that arg2 is the return of the helper at `0x1017d620`, which computes
  `old - max(old - penalty, floor)` - i.e. **the REALISED loss**, already clamped.

So the marker never paid "the original pre-cut amount". It pays **`realised_loss * RedemptionMultiplier`**, and
the multiplier shipped at **0.5**. b93's death-penalty cut therefore scaled the recovery automatically and
could not have opened an exploit. What actually existed was the OPPOSITE defect: **the player recovered only
half of what they lost**, on every death, in stock and in this mod.

**WILL'S RULING IS UNCHANGED AND NOW EVEN SIMPLER TO SATISFY:** `recovered == lost` is achieved by setting
`RedemptionMultiplier` **0.5 -> 1.0**. It is derived from the realised loss by the engine itself, so it cannot
drift when the penalty is retuned - which is exactly the property Will asked for and the reason his second
formulation ("match the xp lost") was the better rule.

**PROOF THAT IT IS DERIVED, NOT HARDCODED:** the lane's gate plants a retuned penalty (divisor 90 -> 45, cap ->
123456) and the equality still ACCEPTS - so the invariant survives a future rebalance. 7/7 tombstone negatives
fire, both directions, re-run independently by the vet.

**THE LESSON, and it is the same one as the b91 `difficultyLimitsFile` claim:** I asserted a mechanism from the
shape of a field name and a plausible story, then wrote it into the design law of record as fact. Both times an
agent that went to the actual engine found the opposite. **A mechanism claim belongs in this ledger only with
the bytes that prove it.**

**STATUS:** R-109 IMPLEMENTED in the `feat/uber-visibility` branch (`RedemptionMultiplier` 0.5 -> 1.0), vet-
reproduced independently, awaiting only that branch's round-2 merge. The exploit framing above is retracted.

---

## R-140 [2026-07-30] IMPLEMENTED - R-100 #15 ROOT CAUSE: the thrown-wielders are frozen because SV strips the thrown ANIMATION STANCE, not because of anything to do with their weapons

> **NUMBER CHOICE.** The R-100 decade and everything up to **R-124** is claimed somewhere across the 120
> branch heads, and **R-130** is claimed (uncommitted) by the `map-placement` worktree. `R-140..R-149` was
> proven free before use, against `main`, all 120 heads' WHOLE TREES, and every worktree WORKING DIR
> (uncommitted included):
> * `git grep -l -E "R-14[0-9]" $(git for-each-ref --format='%(refname:short)' refs/heads)` -> **empty**
> * `for d in $(git worktree list --porcelain | grep '^worktree ' | sed 's/^worktree //'); do grep -rl -E "R-14[0-9]" "$d/docs" "$d/tools"; done` -> **empty**
>
> This ruling AMENDS R-100 #15 with its root cause and implementation. It does not renumber, move or alter
> R-100.

**WILL, VERBATIM (R-100 #15, recorded 2026-07-29, the item R-100 itself calls "the most serious item in the
batch"):**

> "also all of the guys that we brought back into the game which utilize thrown objects are all frozen in the
> game, they spawn and they cant move or attack or anything they are broken"

**FIRST, A CORRECTION TO THE BRIEF FOR THIS LANE.** The owner named for this defect was
`tools/patches/thrown_wielders.py`. That file is **SUPERSEDED and UNREGISTERED** - its own header says so, and
`grep -n thrown tools/patches/__init__.py` confirms it is not in `REGISTRY`. It cannot be the cause of anything
in Will's game. The **LIVE** module is `tools/patches/thrown_restore.py` (b64), registered at `[16/47]`, which
restores the base equip/loot fields on 10 records in place. Everything below is about that module's roster.

**ROOT CAUSE (measured against base TQAE `database.arz`, SV 0.98i `database.arz`, and the SHIPPED build
`md5 6a3a491db546b603c52132237c40aa63`, 51,124 records - not inferred):**

A TQ creature plays one animation block per WEAPON CLASS. Equipping a `WeaponHunting_RangedOneHand` (a thrown
weapon) puts the creature in the `rangedOneHand` stance, or `dualRanged` when BOTH hands are thrown. The `.anm`
clips for a stance come from the creature's ANIMATION TABLE (`charAnimationTableName`).

`py tools/debug/probe_anim_tables.py <base.arz> <sv098i.arz>` and
`py tools/debug/probe_anim_tables.py local/baseline_main.arz`:

| animation table | stance | base TQAE | SV 0.98i **and our shipped build** |
|---|---|---|---|
| `ANM_Maenad.dbr` | `rangedOneHand` | **9 clips** | **0 clips** |
| `ANM_Tiger.dbr` | `rangedOneHand` | **10 clips** | **0 clips** |
| `ANM_Machae.dbr` | `rangedOneHand` | **11 clips** | **0 clips** |
| `ANM_DuneRaider.dbr` | `dualRanged` | **9 clips** | **0 clips** |

SV 0.98i's roster predates thrown weapons, and a record overlay is WHOLESALE - so SV's copies of those four
tables replace the base ones and bind **no run anim, no walk anim, no attack anim** for the thrown stance.
`thrown_restore` then hands the creature a javelin. It enters that stance and becomes a statue. That is
precisely, and only, what Will reported.

**WHY EVERY PRIOR "PROVEN ON 3 FAMILIES AND RE-VERIFIED" CLAIM WAS WORTHLESS.** They tested the wrong thing.
The 92 numeric `rangedOneHand*AnimSpeed` / `*AnimWeight` fields DO survive SV's overlay (template defaults), so
`thrown_wielders.verify`'s check - `rangedOneHandAttackAnimWeight1 is not None` - is TRUE on a table that binds
no clip at all. A weight with nothing to weight is not a rig. The mesh RIG_WHITELIST was also true and also
irrelevant: the mesh has the clips; nothing was pointing at them.

**MEASURED SCOPE, stated as an invariant and not as N names.** `py tools/debug/probe_frozen_throwers.py
local/baseline_main.arz` on the shipped build: **10 thrown wielders in the entire database, and all 10 FROZEN** -
maenad `ar_archer_06`/`br_archer_10`, tigerman `ar_archer_27`/`_33`, machae `ar`/`br`/`cr_archer_37`, duneraider
`am_assassin_15`/`_21`/`_27`. "All of the guys" was exactly right.

**WHERE THE FIX BELONGS - decided from shipping data, not from belief.**
`py tools/debug/probe_anim_authority.py <base.arz>` over all **5,561** base-game `Class=Monster` records:
* 2,596 records bind a Run/Walk/Attack slot on the RECORD that their table does not -> the record IS read.
* 8,884 bind one on the TABLE that their record does not -> the table IS read (per-field fallback).
* **For `rangedOneHand` and `dualRanged` specifically: ZERO records bind them at record level; 1,085 + 259 get
  them from the TABLE only.** Not one shipping thrower in the game carries its thrown anims on its own record.

So the table is the load-bearing surface and the only shape with shipping precedent. Writing the clips onto the
creature records instead would have been an invented shape - and if the engine reads this stance from the table
alone, it would have shipped a third statue.

**SHARED-RECORD LAW APPLIES, HARD.** Carrier census on the shipped build
(`probe_thrown_stance_gap.py ... --carriers`): `ANM_Maenad` **168 carriers, 166 NON-TARGET** (every maenad in
the game, including `um_lyialeafsong_18` - one of Will's own pets); `ANM_Tiger` 68/66; `ANM_Machae` 64/61;
`ANM_DuneRaider` 30/27. So the four tables are **cloned**, never edited: `tools/patches/thrown_anim_rig.py`
clones each into `records\creature\monster\svc\thrown_anm\*`, restores the base stance clips VERBATIM on the
clone (39 clips over 4 families, every value captured from base TQAE), and repoints `charAnimationTableName` on
exactly the 10 roster records - which it IMPORTS from `thrown_restore.ROSTER` so the two can never drift.

**THE GATE (process law #4), stated over the roster:** *no `Class=Monster` record may equip a thrown weapon
while naming an animation table that leaves that weapon's stance without `RunAnim` + `WalkAnim` +
`AttackAnim1`.* One implementation (`scan_frozen_throwers`) serves the gate, the negatives and the probe.
Planted negatives, all firing: lose the run clip / lose the walk clip / lose the attack clip / repoint a roster
record back at SV's stripped table (the exact shipped bug) / bind a `.msh` where an `.anm` belongs / edit a
shared original in place / arm ANY non-roster monster with a thrown weapon on a stripped table. Two
must-stay-GREEN controls: a non-thrown equip change on a sibling monster, and a non-critical clip slot.

**ASSETS PROVEN, not assumed:** all **31/31** distinct `.anm` clips this restores resolve in the shipped arcs,
0 missing (`py tools/debug/probe_anm_asset_resolve.py <game> work/SoulvizierClassic/Resources`, exact inner
archive paths printed so an archive-name-stripping artifact cannot masquerade as a resolution).

**STATUS: IMPLEMENTED** on `fix/quest-item-leaks`. **10 frozen -> 0.** No family had to be disabled: all four
rigs are restorable, because the clips were never missing - only the pointers were.

**NOT PROVEN AND CANNOT BE PROVEN HERE (Will's, launch-gated):** that the restored wielders *visibly throw* and
move in-game. Every claim above is a database/asset proof. The mod is not deployed by this lane, and only a
play test can confirm the animation reads correctly. The 3 duneraider variants are also **dual**-throwers whose
stance is `dualRanged`; `am_assassin_15` additionally has ZERO ProxyPool membership anywhere in vanilla (a b64
finding, unchanged here), so it cannot be the one he sees - the Egypt sighting must be `_21` or `_27`.

---

## R-141 [2026-07-30] IMPLEMENTED - R-101 quest-item leaks closed; plus ONE measured correction and ONE genuinely open Will decision

**WILL, VERBATIM (both reports, which is what made this a class rather than a bug):**

> "when you cloned the monster to create the Soul of the Unferried, you literally clone another monster in the
> game who is a quest monster who drops Charon's Oar, and now this monster is also dropping Charon's Oar."

> "Same thing with the Key of the Warden of Souls, that is now a farmable item from the uber boss you made that
> you cloned from the warden of souls, they now drop the key of the warden of souls which they should not"

**R-101's SWEEP REPRODUCES EXACTLY** on this lane's own baseline
(`py tools/debug/probe_quest_coupled_fields.py local/baseline_main.arz`, build md5
`6a3a491db546b603c52132237c40aa63`): 62 `itemClassification==Quest` records; **611** `um_*` records; exactly
**3** carry `perPartyMemberDropItemName` and **all 3 point at a Quest item**. Inbound census agrees:
`xsq12_charonsoar` <- 4 legitimate Charon forms + our uber; `z_wardenofsoulskey` <- `xsecrethero_wardenofsouls_48`
+ BOTH our Gaolers. Nothing about R-101 needed re-deriving; it needed building.

**MEASURED CORRECTION TO R-101.** R-101 instructs "clear `perPartyMemberDropItemName` (and any matching chance
field)". **There is no matching chance field.** `perPartyMemberDropChance` is ABSENT (dtype `None`) on all three
records. Nothing to clear. The gate therefore PINS it absent-or-zero instead, so a future percentage-gated
re-add cannot slip past a check that only looked at the name field.

**THE DONORS - the whole risk - are proven untouched three independent ways:** `apply()` records exactly which
records it wrote and `verify()` asserts no donor is in that set; `verify()` asserts every donor STILL hands out
its exact quest item (so the real quests provably still work); and the wave's arz record-diff shows the 5 donor
records unchanged.

**GATE:** *no `um_*` record may carry a `perPartyMemberDropItemName` resolving to `itemClassification == Quest`* -
a roster invariant, DB-wide. `apply()` deliberately fixes the three MEASURED records BY NAME rather than
clearing whatever it finds: a 4th inherited leak must turn the build RED for a human, not be silently laundered.
Negatives both ways, as R-101 demanded: re-adding each of the three reds; the same class planted on a DIFFERENT
uber reds; a donor stripped of its quest drop reds; and **a NON-quest per-party drop on an uber stays GREEN**
(the field itself is legitimate - the gate reported "1 carrier, 0 pointing at a Quest item").

**THE WIDER SWEEP R-101 ASKED FOR ("report what it finds, even where it changes nothing"), over all 611 ubers:**
* `DisplayAsQuestItem = 1` on **24** ubers. **NOT a leak** - on a creature record this is the minimap
  exclamation-marker rig (`uber_quest_markers`), which is exactly what Will ASKED for in R-100 #7. Left alone.
* `quest = 1` on **exactly 2** records - `um_polisgaoler_99` and `um_polisgaoler_unbound_99` - inherited from
  the quest boss `xsecrethero_wardenofsouls_48`. **No other uber in the database carries it.** This is a real
  second inheritance from the same clone, and it is the one thing the sweep found that R-101 did not name.
* No `questItem*`-style reference, journal hook or one-shot flag was found on any uber.

### R-141a - OPEN WILL DECISION (not taken by this lane): the Gaolers' inherited `quest = 1` flag

Both Gaolers are flagged to the engine as QUEST monsters because they were cloned from one. That flag changes
how the engine treats a live encounter (spawn/limit/respawn/tracking behaviour), and the Gaoler encounter is
Will's own content, so **clearing it is a design change, not a mechanical fix** - exactly the line R-101 itself
draws around the donors. Nothing was changed. The current value is PINNED by the gate so it cannot drift
silently while the question is open, and it is registered as `BL-R101-QUESTFLAG-1`.

**THE QUESTION FOR WILL:** the Soul Gaoler and his unbound form are repeatable uber encounters that the engine
still believes are one-off quest monsters. Do you want that flag cleared? **RECOMMENDATION: yes, clear it** -
a repeatable farm target should not be wearing a quest monster's engine flag, and it is the same reasoning that
made the quest-item drop wrong. But it is deliberately NOT done on my own authority, because it touches how a
live encounter of yours spawns, and R-100 #17 already has you re-scoping this same creature's chests and loot
tiers. One lane should own the Gaoler end to end and take this with it.

**STATUS: IMPLEMENTED** (the 3 leaks) on `fix/quest-item-leaks`. **3 leaks -> 0**, 0 donors written.
**NOT DONE / OPEN:** R-141a above, and the in-game confirmation that the Oar and the Key no longer drop - which
only Will can give, since this lane does not deploy.

---

## R-140 AMENDMENT [2026-07-30] Three measured corrections to R-140, from an INDEPENDENT re-derivation. The fix is unchanged and is now BETTER evidenced than R-140 claimed.

> **This amends R-140 in place. It does not renumber, move or alter R-140 or R-141, and takes no new
> number** - it corrects facts inside an existing ruling, which is what the ledger law requires when a
> ruling's evidence turns out to be wrong. The FIX that shipped is unchanged: nothing below alters a
> record, a clip or the roster. Two of the three corrections make the shipped fix *more* defensible
> than R-140 argued; the third widens a number R-140 understated.
>
> Method: none of R-140's own probes were used. Every fact below was re-derived with independent code
> against base TQAE `database.arz` (74,013 records), SV 0.98i `database.arz`, this lane's baseline
> (`local/baseline_main.arz`, md5 `6a3a491db546b603c52132237c40aa63`) and the wave build
> (md5 `78e5957f9a09e3bfed44599ac6a36854`). R-140's ROOT CAUSE and its 10-record roster both
> REPRODUCED exactly, so the diagnosis stands - only these three claims were wrong.

### CORRECTION 1 (the important one) - "ZERO records bind the thrown stance at record level" is FALSE, and the second surface therefore has real shipping precedent

R-140 says, and uses as its reason for treating the animation TABLE as the only precedented surface:

> "For `rangedOneHand` and `dualRanged` specifically: ZERO records bind them at record level ... Not one
> shipping thrower in the game carries its thrown anims on its own record."

**Measured over all base-game `Class=Monster` records: 7 bind `rangedOneHandRunAnim` / `AttackAnim1` and 5
bind the `dualRanged` equivalents, at RECORD level.** Nine of those twelve are themselves thrown wielders,
and **every one of them carries `charAnimationTableName = None`** - no animation table at all, the whole
thrown rig on the creature record:

| record | stance | its animation table |
|---|---|---|
| `xpack2\creatures\monster\bosses\ancient_earth_42 / _45 / _48` | `rangedOneHand` | **None** |
| `xpack2\quests\npc\non speaking\scripted\x2q06_thor` | `rangedOneHand` | **None** |
| `xpack2\creatures\monster\bosses\ancient_forest_42 / _45 / _48` | `dualRanged` | **None** |
| `xpack4\creatures\monster\zz_dev\ancient_forest_48`, `x4_dev_junga_skeleton` | `dualRanged` | **None** |

(The other three - `x2q06_lokieagle`, `x2q07_lokieagle`, `x3mq_telhinelyktos_fleeing` - bind the stance at
record level without equipping a thrown weapon.)

R-140's probe missed these because it asked "which records bind a slot their TABLE does not", and a record
with no table at all falls out of that comparison entirely.

**WHY THIS MATTERS.** R-140 shipped the record-level clips as a hedge - "belt AND braces, deliberately" -
justified by an *unprovable* worry about SV's `Monster.tpl` corruption of `ANM_Maenad`. That hedge is no
longer needed as a hedge: the Nerthus Ancients are the shipping game's own thrown BOSSES and they carry
exactly this shape. The shape our 10 records now have (record-level clips **and** a valid table) is a
strict superset of a shape TQ itself ships and animates. **Keep it.** The correction removes the only real
objection to the second surface - that it was invented - so belt-and-braces is ratified on evidence
rather than on caution.

### CORRECTION 2 - "10 thrown wielders in the entire database" is MOD-ONLY; the engine-visible number is 78

The mod `.arz` is an **OVERLAY**, not a full merge: **41,226 base records are not in it**, and the engine
reads those from base. Every census in R-140 walked the mod's record names only, so "10 thrown wielders in
the entire database" really means *10 in the mod's own records*.

Resolved the way the engine resolves (mod overlay first, base as pass-through), the union holds
**78 thrown wielders: our 10 (all 10 were frozen, all 10 now fixed) + 68 base-only**.

**The roster is nevertheless COMPLETE, and this is the check that proves it:** the danger was a base-only
thrower naming one of the four SV-stripped tables, since it would inherit our broken table while being
invisible to a mod-only scan. **Measured: 0 base-only monsters both name a stripped table AND equip a
thrown weapon.** No monster outside the 10 is frozen by this defect. R-140's conclusion survives; its
framing did not.

One further outlier, recorded so a later gate widening does not mistake it for a regression:
`xpack2\creatures\npc\corinth\fighting\ss_porcusroh2_die` (a base-only scripted Corinth NPC) resolves
`rangedOneHandWalkAnim` nowhere. **This is PRE-EXISTING in the stock game** - base's own `ANM_MalePC01`
binds no `rangedOneHandWalkAnim` at all - and is not introduced, worsened or touched by this mod.

### CORRECTION 3 - the shared-carrier census is mod-only and understates the blast radius

R-140's carrier counts are mod-record counts. Adding the base-only carriers the overlay leaves in place:

All counts below are PRE-FIX (measured on `local/baseline_main.arz`), which is the state the
clone-or-edit decision was actually taken against:

| table | R-140 (mod-only, pre-fix) | base-only | TRUE total (pre-fix) |
|---|---|---|---|
| `ANM_Maenad` | 168 | 8 | **176** |
| `ANM_Tiger` | 68 | 19 | **87** |
| `ANM_Machae` | 64 | 4 | **68** |
| `ANM_DuneRaider` | 30 | 0 | **30** |

> **A correction inside the correction, kept visible on purpose.** The first draft of this table
> printed 174 / 85 / 65 / 30 - I had put R-140's PRE-fix mod counts in column 1 and my own POST-fix
> totals in column 3, so the rows did not even add up. It was caught by running
> `probe_thrown_union_scope.py` against the post-fix build and the pre-fix baseline separately and
> noticing 166+8=174 vs 168+8=176. Recorded rather than quietly fixed, because "the census was run
> against the wrong artifact" is the exact failure mode this whole amendment exists to correct, and it
> is worth knowing it is easy enough to make twice in one day. Post-fix the mod-side counts are
> 166 / 66 / 61 / 27 (the 2/2/3/3 roster records having moved to the clones), i.e. post-fix totals
> 174 / 85 / 65 / 27.

**The CLONE-not-edit decision is correct at both counts and nothing changes** - the numbers only get worse
for editing in place, never better. Recorded because SHARED-RECORD LAW is decided on exactly these
numbers, and a future lane reading R-140 would under-count its own blast radius by up to 31 carriers.

### WHAT THIS AMENDMENT ADDED TO THE BUILD (not just prose)

`tools/gate_thrown_anim_assets.py`. R-140 proved the database BINDS the stance; nothing proved the `.anm`
clips it binds actually SHIP. That is the identical failure shape one layer down (green database, frozen
monster), and R-100 #15's brief asked for it explicitly: *"prove for each that its attack/move animations
resolve"*, *"GATE: every thrown wielder's referenced anms resolve; planted negative on a broken binding."*

**Invariant:** *for every `Class=Monster` that equips a thrown weapon, every `.anm` this database binds for
that weapon's stance - on the creature record OR on its animation table - must resolve in the shipped arc
set under the engine's own archive scoping.* Resolution delegates to
`validate_render_chain.EngineArcResolver` (the repo's canonical engine-faithful resolver); the thrower
enumeration is imported from `patches.thrown_anim_rig.scan_frozen_throwers`. Neither can drift from the
module it gates.

Result on the wave build: **PASS - 10 wielders, 31 distinct clips, 31/31 resolve, 0 frozen.**
`--selftest`: **6 planted cases, 5 must-RED all RED, 1 must-stay-GREEN GREEN**, gate GREEN again after full
restore. One must-RED is a real clip named under the WRONG XPack scope - that case exists because a naive
strip-the-first-component matcher reported all 9 machae clips as MISSING during this verification when
they are in fact present in `Resources\xpack\Creatures.arc`. The canonical resolver is what makes this
gate trustworthy rather than merely green.

**STATUS: R-140 stands as amended.** Diagnosis reproduced, fix unchanged and better evidenced, one gate
added. Still NOT proven and still Will's: that the restored wielders visibly throw and move in-game
(BL-R140-LAUNCH-1). Everything here remains a database/asset proof.

## R-120..R-123 + R-125 [2026-07-30] - b102 `feat/devourer-kit`: the Devourer + Endless Hunt implementation wave

> **NUMBER HYGIENE - AND ONE LIVE COLLISION, RESOLVED BY MOVING OUR OWN.** R-100..R-107 were taken
> by the 07-29 lanes and R-108..R-119 are taken elsewhere. When this lane started, `R-12[0-9]` was
> provably free: `git grep -l -E "R-12[0-9]\b" $(git rev-list --all)` -> **empty**, and a
> working-copy grep over `docs/WILL_RULINGS.md` + `docs/BACKLOG.md` in `main` AND all 100+ in-flight
> worktrees -> **empty**.
>
> **THAT STOPPED BEING TRUE WHILE THIS LANE WAS BUILDING.** Re-checked at the end of the session,
> three commits from two OTHER live lanes had landed a ruling numbered **R-124** minutes later
> (`fix/uber-placement` @ `b1774d5` and `7940e78`, `fix/green-mesh-swap` @ `b302abd`), and
> `fix/uber-placement` / `feat/soul-economy` had also taken R-130, R-140 and R-149. Per the ledger
> law this lane **renumbered ITS OWN ruling** (the old R-124 is now **R-125**, re-verified free
> against every worktree working copy at the time of writing) and **did not touch either other
> lane's number** - reassigning another lane's ruling from a third lane is exactly the silent
> cross-lane edit the ledger exists to prevent, and picking an incumbent between same-day lanes is
> the orchestrator's call, not this lane's. **R-120..R-123 and R-125 are this lane's;
> R-124 belongs to the other two lanes and they still collide with each other.** Registered as
> `BL-b102-DEBT-3`.
>
> **NONE OF R-120..R-123 / R-125 IS A NEW WILL DECISION.** R-100 #1/#12/#13, R-103 and R-107 are the
> decisions; this decade records what was MEASURED while implementing them, where the measurement
> contradicts what those rulings assumed, and the two design choices that are this lane's own and are
> therefore vetoable. Will's words are quoted, never paraphrased into a ruling.

---

## R-120 [2026-07-30] IMPLEMENTED b102 - AMENDMENT to R-100 #1: "grant Bloodbath to the Devourer" was never a wiring gap. The skill was already wired at 90% and had never once fired.

**R-100 #1, Will verbatim:** *"We should grant the skill Bloodbath from the Erebenea the Bloodletter
Soul to toxeus the devourer of blood but lets reduce the cooldown on the skill from 45s to like 15s."*

Measured on the built arz `6a3a491db546b603c52132237c40aa63` (51,124 records), which is byte-identical
to the artefact the b101 gate record names:

| | measured |
|---|---|
| the skill behind "Bloodbath" | `records\skills\soulskills\melinoe_bloodboil.dbr` - `skillCooldownTime` **45.0** (exactly Will's "45s"), icon `DRXtextures\skill icons\soul\bloodbathup.tex` |
| how the Erebenea soul grants it | `erebenea_soul_{n,e,l}.itemSkillName` -> the `pcsafe\` twin (the B-SOUL-PROC-2 player-safe clone) |
| already on the Devourer? | **YES** - `um_bloodtoxeus_99.skillName1` @ level `[8,12,16]` AND `specialAttackSkillName` @ `specialAttackChance` **90.0**, shipped since build32 |
| `melinoe_bloodboil.skillSpecialAnimationName` | **`'BloodBoil'`** |
| the Devourer's caster table | `records\creature\monster\skeleton\anm\anm_skeleton01.dbr` |
| every `SpecialAnimRef` that table binds | dHanded: DwAttAlpha, JumpSlash, Crosscut, AoE360, BladeSweep, Charge - sHanded: AoE360, LethalStrike, Absorb, Charge, Bolts, Strike, ShieldSkill01, Staff - staff: Spellshock - unarmed: Halfring, Fullring |
| `'BloodBoil'` among them | **ABSENT** |
| records in the whole DB binding a `'BloodBoil'` ref | **exactly 2**, neither a skeleton: `creature\monster\maenad\anm\anm_maenad.dbr` [bowSpecialAnimRef7] and `drxcreatures\bloodwitch\anm_acolyte.dbr` [unarmedSpecialAnimRef1] |

**Under this repo's own disasm-proven hard law B-SOUL-PROC-2** (BACKLOG "RCA v2":
`Game.dll SkillManager::StartSkill`, log string *"Animation failed to start in
SkillManager::StartSkill"* va `0x1035c3b0`, gate vcall va `0x102561d4`) a cast whose
`skillSpecialAnimationName` cannot start on the CASTER's animation table is **aborted**. That same
BACKLOG entry already names this exact token in its census of never-playable monster anims:
*"BloodBoil x29"*.

**So the Devourer's signature nova, wired at a 90% cast chance, has never fired in any build.** That is
why Will experienced Bloodbath as absent, and why "grant it to him" was the right request from a
player's chair even though the record already named it.

**IMPLEMENTED as:** a CLONE, `records\skills\boss skills\svc_devourer_bloodbath.dbr`, at
`skillCooldownTime` **15.0** (Will's number, behind the named constant `BLOODBATH_COOLDOWN`) with
`skillSpecialAnimationName` **DELETED entirely** - the exact remedy this repo already shipped for the
same law (the `pcsafe\` clones; the BACKLOG records 172/204 base proc grants as anim-less, and records
that an EMPTY string has zero precedent - B-TOXEUS-2). Only `um_bloodtoxeus_99` is repointed.

**WHY A CLONE AND NOT THE RECORD ITSELF - the SHARED-RECORD LAW.** `melinoe_bloodboil` has **7
carriers** and **6 are Will's own summoned PETS** (`pets\bloodtoxeus_{1,2,3}`,
`pets\toxeus_eoat_{1,2,3}`); its `pcsafe\` twin has 26 more on player soul items. Cutting the cooldown
in place would have silently tripled the cast rate of six pets nobody asked about. `melinoe_bloodboil`
ships byte-unchanged.

---

## R-121 [2026-07-30] IMPLEMENTED b102, **FLAGGED FOR WILL VETO** - the SAME law kills the Enslaver's marauder summon, which is the exemplar R-100 #13 is patterned on.

**R-100 #13, Will verbatim:** *"also we need to give toxeus the murderer devourer of blood and toxeus
the murderer endless hunt some guys they can summon like toxeus the murderer enslaver of souls has."*

Measured: `records\skills\boss skills\svc_enslaver_summonmarauders.dbr` carries
`skillSpecialAnimationName = 'Summon'`; its sole carrier `um_toxeus_enslaver_99` rides the same
`anm_skeleton01` table and binds no `'Summon'` ref anywhere. **The Enslaver's marauder summon has never
fired either.** What Will has been seeing is his warband: `q_enslaver_warband` spawns
`championMin=championMax=4` Enslaved Shadow Marauders *present at spawn*, so the boss appears escorted
without ever casting.

Shipping two working summons while the one he named as the reference stays dead is exactly the
"triaged-into-follow-up = NOT done" failure, so the anim was deleted here too (single carrier, so the
shared-record law does not force a clone; one field, no numbers touched).

**THIS IS THE ONE CHANGE IN THE WAVE WILL DID NOT ASK FOR BY NAME.** It makes the Enslaver meaningfully
harder - up to 4 more summoned marauders on top of his 4 warband escorts. R-103 sanctions the direction
(*"yes harder is the point"*, *"the answer is not cutting skills but cutting elsewhere"*), and the
Enslaver is also one of the six monsters whose reflect drops 100 -> 30 in the same wave, so he nets
easier on the mechanic that was actually killing Will. Vetoable by deleting `_fix_enslaver_summon` -
nothing else depends on it.

---

## R-122 [2026-07-30] AMENDMENT to R-103/R-107: reflect and pierce were NOT the only walls, and the audit that finds the rest.

R-107 Part 3 measured the Devourer's defensive wall and concluded *"That is not a hard boss, it is a
hard counter to his specific build wearing a one-shot mechanic."* Both levers it named are implemented
in b102 (reflect 100 -> 30 on a monster-only clone, pierce 70 -> 40, `characterLife` untouched as the
reserved third lever). **What it could not see is that the fight was also being fought by a boss whose
two most conspicuous abilities never fired** (R-120, R-121). The honest statement of the encounter
after b102 is therefore NOT "the same fight minus reflect": it is a *different* fight - less lethal on
the one-shot axis, more active on every other. Will should be told that before he re-fights it.

**THE STANDING LESSON, and why this is a ruling and not a footnote:** a difficulty investigation that
reads a monster's stats and its skill LIST is not enough. A skill can be present, levelled, and wired
to a 90%-chance cast slot and still be mechanically absent. **Every future boss tuning or difficulty
RCA must first run the castability walk** - for each active cast slot, does the skill resolve, and if
it declares a `skillSpecialAnimationName`, does the caster bind that ref (via its own inline
`<family>SpecialAnimRef<i>` block **or** its `charAnimationTableName` table)?

The b91 `coldworm_buffs` gate had the right idea but read only the monster's own
`unarmedSpecialAnimRef*`. The Devourer and the Enslaver carry **none** of their own - every binding
they have comes from `anm_skeleton01` - so that walk would have reported both champions as having no
animations at all. `devourer_kit._bound_anim_refs` follows the table and every weapon family, and
`gate_violations` runs it over all six casters in this wave.

**CREDIT WHERE IT IS DUE, so this ruling is not read as "nobody did this":** b98's
`toxeus_hunt_encounter._castability_violations()` already walks every populated active slot on the
Endless Hunt and derives the WIELDED anim row from the Class of the weapon he is guaranteed in
RightHand, which is stricter still - for that one record. The gap is that neither walk was ever run
over the Devourer or the Enslaver. **Registered as debt `BL-b102-DEBT-2`: promoting the walk to a
DB-wide invariant over every boss is NOT done here.**

**ONE MORE THING THE FIRST BUILD TAUGHT, worth keeping.** `boss_skill_fix.verify` re-asserts its own
b39 fixes by looking for the SUBSTRING `'toxeus_passiveproperties'` in a skillName slot on
`um_toxeus_hunt_99`, so an earlier draft that named the monster-only clone
`svc_toxeus_monster_passive` **failed the build** with *"skill toxeus_passiveproperties vanished from
kit (regression)"*. That gate was right and the clone was renamed
`svc_toxeus_passiveproperties_monster` rather than the gate weakened. **STANDING: when the
shared-record law makes you clone a record that an existing gate matches by substring, keep the
donor's basename inside the clone's basename.** It costs nothing and it keeps the older gate's
protection intact.

---

## R-123 [2026-07-30] R-100 #12 (Blood Frenzy) is SATISFIED, but its payload is thin. **OPEN WILL DECISION - deliberately not taken here.**

**R-100 #12, Will verbatim:** *"We should also give the skill Blood Frenzy to the devourer of blood
(activated on low health), see Chief Bullfrog Quak soul for this skill."*

Measured: the Devourer **already carries**
`records\skills\monster skills\passive_buffs\quak_bloodfrenzy.dbr` on `skillName17` at level
`[4,8,12]`, placed by b73. It is `Skill_PassiveOnLifeBuffSelf`, `lifeMonitorPercent 25.0`,
`skillActiveDuration 6.0`, `skillCooldownTime 18.0`, and it declares **no** special animation, so
unlike Bloodbath it genuinely triggers. b102 asserts it and does **not** duplicate it.

**HONEST RESIDUAL:** measured field by field, the record's ONLY non-zero offensive payload is
`offensiveSlowLifeLeachModifier [50..240]` - a life-leech-over-time modifier - plus the `quak_bufffx`
visual. b73's report describes it as an "attack-speed + bleed/leech surge"; the attack-speed half is
not in the record (`characterAttackSpeed` and `characterAttackSpeedModifier` are both 0.0). So at his
levels it is a real trigger with a small effect.

**NOT CHANGED HERE, on purpose.** Will asked for the skill, and the skill is there. Retuning its
numbers is a balance change he did not ask for, and `quak_bloodfrenzy` is SHARED with the Chief
Bullfrog Quak soul the player can equip, so any buff would need the clone-and-repoint treatment rather
than an in-place edit. **If Will wants Blood Frenzy to bite**, the answer is a
`svc_devourer_bloodfrenzy` clone carrying real numbers - one more record, the same pattern as Bloodbath.

---

## R-125 [2026-07-30] IMPLEMENTED b102, **NAMES + DONORS FLAGGED FOR WILL VETO** - the two new minion families, and the doc that is cited as the bar but does not exist.

**`docs/amgoz1_design_voice.md` IS NOT IN THIS TREE.** It is cited as law in `docs/BACKLOG.md` (3x),
`docs/HUNTING_IMPROVEMENT_SUGGESTIONS.md`, four wave reports, `tools/patches/bossarena.py` and a wip
workflow, but `git log --all --diff-filter=A -- '*amgoz1_design_voice*'` returns **nothing** - it was
never committed. b65 already noticed ("re-distilled from first principles since
`amgoz1_design_voice.md` is gone from the tree") and the citations kept accumulating anyway. Every
brief that says "held to the amgoz1 bar (amgoz1_design_voice.md)" points at a file no agent can read.
**Registered as debt `BL-b102-DEBT-1`: either author it or strike the citations.**

The bar used for this wave was RECONSTRUCTED from shipped SV/DRX content measured in the arz: a
creature's kit and retinue come from ITS OWN family (SV's Erebenea the Bloodletter grants a bleed nova
because she is a lamia bloodletter; DRX's blood-cult disciple summons bloodhounds); names are concrete
and physical, never category labels ("Enslaved Shadow Marauder", "Neferkha, the Rimebound Pharaoh");
and a champion's adds carry a different SILHOUETTE from him so the fight reads at a glance. Will's own
R-100 #18 is the negative form of the same bar - adds that *"look just like the other guys ... not big
with no special skills or anything to make them even noticeable besides their red names"*.

| | Devourer of Blood | Endless Hunt |
|---|---|---|
| name | **"Gorged Bloodspawn"** | **"Courser of the Endless Hunt"** |
| record | `drxcreatures\blooddemon\um_devourer_bloodspawn_99.dbr` | `drxcreatures\bloodhound\um_hunt_courser_99.dbr` |
| donor | `c_large_blooddemon_40` (Champion, Demon, `DRX\meshes\blooddemon01.msh`) | `c_bloodhound_44` (Champion, Demon, `DRX\meshes\bloodhound.msh`) |
| why HIM | the blood demons are ALREADY his declared retinue - `_BT_BLOODDEMON` names `b_med_blooddemon_30/31/32` as his phase adds and `q_bloodtoxeus_lone` spawns exactly those three as his escort. He is the Devourer *of blood*; what he summons is the blood he has drunk | he is the hunter - Quarry's Mark, Long Reach, Run Down, the Runbreaker spear, endless pursuit. What a hunter fields is a pack that runs the quarry to ground |
| stats | Champion, band [40,68,100], HP [4500,6200,8400], scale 2.4, 200/260 hand, runSpeed 1.3 | Champion, band [40,68,100], HP [3500,4800,6500], scale 1.7, 180/240 hand, runSpeed 1.6 |
| cast slot | REPLACES `specialAttack5` | lands on a FREE `specialAttack5` - nothing displaced |

Both minions ship `dropItems 0`, `chanceToEquipFinger2 0`, `DisplayAsQuestItem 0` and no
`treasureProxyName`, so a re-summonable add can never become a loot faucet, can never pay out a soul
(R-42/R-106) and can never enter the `uber_quest_markers` roster. The courser also gets an anim-less
clone of the donor hound's spit (`svc_courser_bloodspew`), because the donor's own
`bloodhound\skills\puke.dbr` demands `'BloodPuke'` while the donor binds only `'Roar'` - the same
B-SOUL-PROC-2 defect one rig over.

**THE ONE DISPLACEMENT, and why.** The Devourer's `specialAttack5` held
`t1_skill_pitspawner_summonlildude_02`, a shared DRX map-dressing spawner whose payload
`t1_lildude_02` is a **charLevel 9, 1.0-HP, scale 0.5** pit sprite - on a boss whose own band is
[40,68,100]. That is exactly the "not real minions" the request is about, and the engine caps every
monster at `specialAttack5`, so a new cast ability has to claim a slot. **RETIREMENT PROTOCOL
OBSERVED:** the pit-spawner record is NOT deleted, blanked or renamed, keeps its two other carriers
(`t1_pitspawner_01/02`) and keeps its place in the Devourer's `skillName9` slot - only the AI cast
slot moved.

**DENSITY (the b76 chumbi-freeze precedent), stated as worst-case simultaneous entity counts** - both
summons are `petLimit 3` / `petBurstSpawn 3` / cd 8s, against the Enslaver's shipped 4 / 6 / 2s:

* Devourer, `q_bloodtoxeus_lone` (spawnMin=Max 3, championMin=Max 2): **1 boss + 2 blood demons + 3 summoned = 6**
* Devourer, `egg_blooddragon` (spawnMin=Max 4, championMin=Max 3): **1 boss + 3 blood dragons + 3 summoned = 7**
* Hunt, `q_toxeus_hunt_lone` (spawnMin=Max 1, championChance 0): **1 boss + 3 summoned = 4**
* Hunt, roaming sweep: the host pool's own members + 1 Hunt (his per-pool cap is 1) + 3 coursers

For comparison the shipped Enslaver reaches 1 + 4 warband + 4 summoned = **9**, and the b76 offenders
were **uncapped**. Neither new summon is unbounded.

**Both names are this lane's invention and are flagged for Will veto**, per the standing creative-bar
rule; they ship as defaults.

---

## R-126 [2026-07-30] IMPLEMENTED b102 - DERIVED FROM MEASUREMENT (not a Will decision; vetoable). `actorHeight` is a per-RIG constant, NOT a size knob, and the b102 minions had invented values.

**This ruling exists because the record-diff cannot catch this class of defect, and it did not.**
`ADDED 7 / REMOVED 0 / CHANGED 7` was green while both new minions shipped with a wrong field, because
an invented value on a record that is itself NEW is not a "change" against any baseline. It took a
DB-wide measurement of the animation rig to see it.

**WHAT WAS WRONG.** The first draft of `tools/patches/devourer_kit.py` wrote `actorHeight` on both new
minions as if it were part of making them bigger:

| record | donor | donor scale -> ours | donor actorHeight -> ours |
|---|---|---|---|
| `um_devourer_bloodspawn_99` | `c_large_blooddemon_40` | 1.75 -> **2.4** | 1.0 -> **1.6** |
| `um_hunt_courser_99` | `c_bloodhound_44` | 1.25 -> **1.7** | 1.7 -> **1.4** |

The courser is the tell: its `scale` went **UP** 1.36x while its `actorHeight` went **DOWN** 18%.
Whatever `actorHeight` is, it cannot be both.

**THE MEASUREMENT (`py tools/debug/probe_actorheight.py <arz>`, 51,131 records).** Group every record
by its `mesh` - i.e. by the rig it animates on - and ask whether `actorHeight` ever moves with `scale`:

* **2,122** rigs carry an `actorHeight` on more than one record.
* **184** of those have BOTH `scale` and `actorHeight` varying inside the rig.
* **60** still vary once the `actorHeight = 0.0` class is dropped (0.0 is a distinct "no height"
  state used by ambient/non-combat variants - e.g. `ag_insect_antlion_0Nn` sit at 0.0 while every
  real antlion on the same mesh sits at 1.7 across scale 0.7..1.39).
* **ZERO** rigs - 0 of 2,122 - make `actorHeight` proportional to `scale`.

> **Which artefact each number came from, because it matters.** The counts above are the
> **DEFECTIVE** build `974d77d2ffc3fa5cbefca15816183276` - the one that still carried the two
> invented values. Re-run on the **corrected** build `8a81a53f2b0f40004e4b3b17b81e0480`, the same
> survey reports **58**, not 60, for the third bullet: the two rigs this wave touched stopped being
> counted as "varying" the moment the minions went back to inheriting. 2,122 / 184 / **0** are
> unchanged. That 60 -> 58 delta is itself the cleanest confirmation that our two records were the
> anomaly, so both numbers are recorded rather than quietly replaced.

And on the two rigs this wave actually touched:

* `DRX\meshes\blooddemon01.msh` - **24** other records spanning `scale` **0.7 -> 1.75**. Every one of
  them `actorHeight` **1.0** (or 0.0). Ours was the only 1.6 on the rig.
* `DRX\meshes\bloodhound.msh` - **9** other records spanning `scale` **1.0 -> 2.25**. Every one of them
  `actorHeight` **1.7** (or 0.0). Ours was the only 1.4 on the rig.

`xbloodhound_36` is the control that settles it: that rig **already has** a record scaled to 2.25,
*larger than our courser's 1.7*, and it did **not** touch `actorHeight`. If the field were a size knob,
that record is where the base content would have proved it.

**THE RULE (standing, applies to every future clone, not just these two).** `actorHeight` is where the
engine hangs a creature's name plate and hit FX on its rig. It belongs to the MESH, not to the
instance. **A cloned creature inherits its donor's `actorHeight`. Make a creature bigger with `scale`.**
If a lane ever has a real reason to move it, the reason has to be a measured property of the rig, and
the measurement goes in this ledger.

**WHAT SHIPPED.** `_build_minion` no longer takes or writes a height argument at all - the field is
simply left inherited. **`scale` is untouched**: the Gorged Bloodspawn still ships at 2.4 and the
Courser at 1.7, so neither minion got smaller; only the rig constant was put back.

**THE GATE (CLAUDE.md law #4).** `devourer_kit.gate_violations()` now asserts each minion's
`actorHeight` equals **its donor's, read live out of the same db** - not a number copied into the
module, which could drift away from the rig the way the original values did. The donors are separately
proven byte-unchanged by the b102 record-diff, so the gate is anchored to ground truth. Planted
negative **N10** re-creates the exact shipped defect (courser `actorHeight` 1.4) and is asserted to
fire; the suite is now **10/10 with a clean control**.

**RESIDUAL, HONESTLY STATED.** What `actorHeight` does at runtime is inferred from the data (its
distribution over rigs, and the 0.0 "no height" class), not from disassembly. That does not weaken the
ruling - being the only record on a 25-record rig with a bespoke value is a defect whatever the field
drives - but a lane that wants to move it deliberately should pin the mechanic first.

**DEBT:** this is the same shape as `BL-b102-DEBT-2` (the castability walk): a rig-constant check
should eventually run over every cloned creature in the DB, not just the two this wave authored.
Registered as `BL-b102-DEBT-9`. NOT done here.

## R-130 [2026-07-30] The Den of Tantalus is a CAVE, chest counts drop to one, and "off the main walking path" gets a measurable definition

> **DECADE CLAIM.** 130-139 was proven free before minting. `git grep -h -oE "R-1(2[5-9]|3[0-9])"
> $(git branch --format='%(refname:short)')` over the WHOLE TREE of ALL 120 local branches returns
> **empty**; the maximum ruling number claimed anywhere is R-124 (`feat/devourer-kit`), with
> R-119 live on three further in-flight branches (`feat/sanctuary-populate`, `feat/soul-economy`,
> `feat/toxeus-apex-roster`). 125-129 are free but are left as slack so the next lane also gets a
> whole decade. This lane owns 130 only.

Source: R-100 items #8, #9, #10, #14, #16 and the #16b standing rule. Will's words are already recorded
verbatim in R-100; this entry is the DESIGN LAW derived from them plus the three measurements that
change how the rule must be implemented.

### PART 1 - #8. THE DEN OF TANTALUS IS A CAVE INTERIOR, AND b45 DID NOT "FAIL TO HOLD"

**Will, R-100 #8:** *"tantalus the hunger unbound is not inside the den of tantalus like he is supposed to
be, he is sitting right in front of the den of tantalus outside of it."*

The b45 task that claimed this fix is marked COMPLETED, and the brief asked why it did not hold.
**It held. It shipped. It implemented the wrong target.** Measured on the deployed DEV map
(`Levels.arc` md5 `943d0ab9516d332db79bd7f9fd2d3ffe`):

| fact | evidence |
|---|---|
| The b45 coordinate IS deployed | 0x05 read of blob [755]: `q_tantalus_lone.dbr` @ local (34.00,-13.40,106.00) - exactly b45's number, not the pre-b45 (54,-15.2,114.3) |
| The Den of Tantalus is **not** that level | blob [755] `Styx_SwampBorder_01`'s 0x17 REGION guid resolves to SD region **"Stygian Marsh"** (`xtagRegionName33`) |
| The Den of Tantalus **is** the cave | `Styx_CaveUG_FrogCamp01/02/03` [878/879/880] all resolve to **"Den of Tantalus"** (`xtagRegionName80`) |
| The way in | SwampBorder_01 instance #24 `ext_hc_cliffwall01.dbr` @ (27,-13,115) is a GridEntrance; its 0x14 binding names dest GUID `620fd291..` = `Styx_CaveUG_FrogCamp01.lvl` |
| Why the b45 metric was incapable | `pj_denoftantalus.dbr` is `Class=AreaOfInterest`, `AreaDescription=xtagPOI12` ("Den of Tantalus") - a **signpost** standing 2.8u in FRONT of that cave mouth, outdoors |

So b45 moved the boss from 28.1u to 10.2u from an outdoor signpost and called 10.2u "unambiguously in
the den". Minimising distance to that marker **cannot** put the boss inside the den, because the marker
is not inside the den either. Ten units from it is, precisely, *right in front of the den, outside of it*
- Will's exact sentence. The lesson is not "b45 was careless"; b45 surveyed diligently against a metric
that could not answer the question.

**RULING: containment is proven by the AREA BANNER, never by proximity to a POI, a landmark or a
doorway.** The oracle is the level's own 0x17 REGION guid resolved against the world SD (0x18) and Text -
the same binding that paints the top-right area name in game (RE'd and proven across all 2282 levels in
`docs/reports/b46_minimap_result.md`). If the host level's banner does not read the intended area, the
encounter is not in that area, and no clearance arithmetic may argue with it. Gated by
`tools/debug/gate_uber_placement.py` (ORACLE 1).

**IMPLEMENTED:** Tantalus moves to `Styx_CaveUG_FrogCamp02` local (30.0,1.0,40.0) - the den's treasure
chamber, ~100u of walking deep, 9.3u from the den's own golden hoard, clr@6.0 100%/100%/100%, comp#1,
nearest functional native 9.33u. The Helos area-return NPC deliberately stays OUTSIDE in the marsh
(it is the travel landing), which is why `TANTALUS_OUTDOOR_HOST_KEY` remains a separate constant.

### PART 2 - #9/#10. ONE CHEST PER FIXED UBER, SCOPED AS A CLASS

**Will, R-100 #9:** *"he has three chests, all of them tantalus hoard where he should only have one."*
**#10:** *"the uber monster soul of the unferried also had three chests."*

These are **one mechanism, not two coincidences**: the Unferried IS the Charon / Golden Bough encounter,
and both chest sets are b42 round-2's `_chest_triangle`. **RULING: `UBER_CHEST_COUNT = 1`, applied to the
whole b42 class** (Ephialtes, Tantalus, Charon/Unferried, Kroisos/Dorus) - not special-cased to the two
Will happened to walk into. Ephialtes and Kroisos carry the identical three-identical-chests arrangement
and would have drawn the same report the moment he reached them; fixing only the reported two guarantees
a repeat report, which is what DONE-MEANS-DONE exists to prevent.

This **AMENDS b42 round-2** (*"replace the current chest with three large majestic chests"*), itself a
Will decision - recorded as a supersession, not a silent override. **Nothing is retired:** the DB side is
untouched (the bosses still carry no accessory chest; the world-chest proxy records and their
region-tuned hoard chains are unchanged), the surviving chest keeps the b42 triangle's own already
surveyed "A" offset, and one constant reverses the whole thing.

WARNING - FOR WILL: he named two bosses; this applies the rule to four. If he wants Ephialtes or Kroisos
to keep three, that is a one-line change.

### PART 3 - #16b. WHAT "THE MAIN WALKING PATH" MEANS, MEASURABLY

**Will, R-100 #16b:** *"the main walking path is not the appropriate place for uber monsters we are
placing in the game."*

A standing rule needs a definition a build can check. **RULING: the main walking path is derived from the
level's own navmesh, not drawn by hand.** Gateways = tile-edge crossings + 0x06/0x14 door mouths;
multi-source BFS gives the exact on-shortest-route set `{c : dA[c] + dB[c] <= dist(A,B) + slack}` for
every gateway pair. An encounter **BLOCKS** if deleting its 6u footprint disconnects a gateway pair, and
is **ON-PATH** if its 12u engagement disc intersects a shortest route.

**The calibration matters as much as the metric.** The raw ON-PATH test failed 15 of 20 shipped
placements, which cannot be right - Will named exactly ONE (the Helepolis) and has fought Menoetes,
Ephialtes and the Gaoler horde happily where they stand. The difference is the LEVEL, not the boss: in a
tight dungeon corridor the level *is* the path and "move him off it" is not a thing that can be done; in
an open field there is somewhere else to stand. So the rule only bites where an alternative exists:
**ON-PATH is a failure only where >= 25% of the level's walkable area is off-path**; below that it is
reported as ON-PATH(UNAVOIDABLE) and never gates. This is a policy constant, tunable by a future ruling.

**IMPLEMENTED (#16):** the Helepolis was measured at **0.0u** from a shortest route - literally on the
line, on two gateway pairs' routes, in a level that is 29% off-path (an alternative plainly existed).
Moved to Elysian_Fields_03 local (70.0,8.8,80.0): **18.9u** off-route, **zero** on-path pairs, clr@6.0
100%/100%/100%, comp#1, nearest native 10.0u.

WARNING - FOR WILL, the one taste trade-off: the whole WESTERN half of that meadow is the corridor (the
best western candidate still read 6.7u), so the fix costs him adjacency to the two native `xsq25` siege
striders - the Helepolis now stands ~45u east of them in the walled court. If he would rather keep him
among his kin and accept being near the path, say so and it is a coordinate change.

### PART 4 - #14. THE "LOWER CITY OF LOST SOULS" UBER IS THE MNEMOPHAGE

**Will, R-100 #14:** *"the uber boss in the lower city of lost souls has no chest that he is guarding and
the orb he drops is trash."*

R-100 left the boss unidentified. **Measured: it is the Mnemophage.** His host
`Judgment_TempleUG_Mnemosyne01` binds SD region `xtagRegionName36` = **"Lower City of Lost Souls"**. Both
halves of his report are confirmed against the build: `_SVC_FIXED_UBER_CHESTS` deliberately excludes him
(*"Mnemophage carries no chest by design"*), so there is no `svc_mnemophage_chest` record to place, and
`um_mnemophage_core_99` sits on `genericbossorb_04` (~5.70 expected items) while R-99's apex tier
`genericbossorb_05` is ~21.16 - which is exactly what "trash" describes.

**STATUS of #14: NOT IMPLEMENTED, and deliberately so.** Both halves need DB records this map lane does
not own: a chest needs `_svc_build_world_chest_proxy(db,'mnemophage',...)` + a dedicated hoard + a Text
tag + a `_SVC_CHEST_STD` bracket, and the orb needs `um_mnemophage_core_99` moved to `genericbossorb_05`
- which R-99 records as REQUIRING `uber_apex_orb.verify()` to be rewritten roster-derived first, because
its planted NEGATIVE 2 asserts that a third record on orb05 must FAIL. Doing that from a map branch would
red the build and collide with the `feat/toxeus-apex-roster` lane. Specified here, handed off, not faked.

**STATUS:** Parts 1, 2 and 3 IMPLEMENTED on `fix/uber-placement` and gated. Part 4 SPECIFIED, owner
needed. The full #16b audit of every existing placement - including the ones deliberately left alone -
is in the wave report.

---

## R-131 [2026-07-30] The two chest-less ubers get a hoard; the "trash orb" is a TIER complaint, not a Mnemophage defect

> **DECADE CLAIM.** R-131 was proven free before minting.
> `git grep -h -oE "R-1(2[5-9]|3[0-9])" $(git branch --format='%(refname:short)')` over the WHOLE TREE of
> all **120** local branches returns exactly `R-125`, `R-130`, `R-131` - and
> `git grep -l "R-131" ...` shows the only carriers are this lane's own four source files, i.e. this
> ruling's own implementation. R-125 belongs to `feat/devourer-kit`; R-130 is this lane's prior pass.
> **126-129 and 132-139 remain free.**

Source: R-100 **#14** and **#16**, the two halves R-130 Part 4 SPECIFIED and handed off. This entry
implements the CHEST half of both and rules on the ORB half with a measurement that changes the answer.

**SUPERSEDES R-130 Part 4's "NOT IMPLEMENTED, and deliberately so."** That status was written on the
belief that the chest halves belonged to a different lane. They did not: `_svc_build_dedicated_hoard`
and `_svc_build_world_chest_proxy` are the exact helpers the other four fixed ubers already call, in the
same two files this lane already edits. Handing them off was a triage, and a triaged item is not a done
item.

### PART 1 - #14 + #16, THE CHEST HALVES: IMPLEMENTED

**Will, R-100 #14, verbatim:** *"the uber boss in the lower city of lost souls has no chest that he is
guarding and the orb he drops is trash."*
**Will, R-100 #16, verbatim:** Machine uber boss (**Destroyer of Cities**) drops **no chest**, and
stands **in the main walking path**.

Both now carry a hoard, built on the SAME chain as the other four rather than by a new mechanism:

| | the Mnemophage (#14) | the Helepolis (#16) |
|---|---|---|
| host / area banner | `Judgment_TempleUG_Mnemosyne01` -> **Lower City of Lost Souls** | `Elysian_Fields_03` -> **Delian Meadows** |
| boss band (N/E/L) | [46, 68, 100] | [58, 80, 97] |
| `_SVC_CHEST_STD` bracket | `svc_mnemophagehoard` = 45-47 / 63-65 / 63-65 | `svc_diadochihoard` = 57-59 / 63-65 / 63-65 |
| chest name | **"Mnemophage's Lethe-Hoard"** | **"Helepolis's Spoil-Hoard"** |
| world-chest proxy | `records\drxmap\proxy\svc_mnemophage_chest.dbr` | `records\drxmap\proxy\svc_diadochi_chest.dbr` |
| placed at (level-local) | (45.6, 3.0, 71.0) | (72.6, 8.8, 80.0) |

**WHY THE HELEPOLIS CHEST RIDES HIS RELOCATION.** His chest is centred on the R-100 #16 OFF-PATH spot
(70, 8.8, 80), not on his retired b41 spot. Putting a new chest on the old coordinate would have
re-created the very defect #16 exists to fix - a reward the player has to stand in the corridor to open.
Because it rides the boss, it is off the walking path by construction, and the placement gate audits it
as an independent record anyway (it discovers chests from the map by marker, so both new chests are
containment- and path-checked without the gate being told about them).

**WHAT WAS NOT RETIRED.** The Mnemophage's no-chest was a DELIBERATE build36 design choice - the shipped
comment read *"the Mnemophage's marquee is the custom amulet, not a hoard (differentiator)"*. Will has
now played the encounter and overruled it. That intent is QUOTED IN PLACE in the source rather than
deleted, and his Lethe's Draught amulet is untouched: he gains a chest and loses nothing. The Helepolis
never had a chest at all, so his half is a gap being closed, not a design being reversed.

**THE NEW SURFACE SHIPS WITH ITS GATE.** Both prefixes are added to `_SVC_FIXED_UBER_CHESTS`, so
`_svc_verify_world_chests` now asserts for six ubers, not four, that the boss proxy's accessory tiers
are EMPTY **and** the world-chest record exists. If a later lane deletes either hoard, the build reds
instead of the chest quietly vanishing. (Measured before wiring: all four accessory slots on
`q_mnemophage_lone` and `q_diadochi_lone` are already `None`, so the assertion is satisfiable.)

### PART 2 - #14's ORB: THE MEASUREMENT INVERTS THE PREMISE. **PENDING - OPEN WILL DECISION.**

R-130 Part 4 said the orb half was blocked by the `uber_apex_orb.verify()` roster gate. **That is true
but it is not the real reason, and the real reason matters more.** Measured on the shipped arz
`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, `treasureProxyName` on every placed fixed uber:

```
Tantalus (terminal)  um_tantalus_unbound_99      genericbossorb_04
Mnemophage (core)    um_mnemophage_core_99       genericbossorb_04   <- the "trash" orb
Ephialtes            um_ephialtes_99             genericbossorb_04
Kroisos / Dorus      um_dorus_99                 genericbossorb_04
Helepolis            um_helepolis_99             genericbossorb_04
Charon (ferryman)    um_charonform2_ferryman_99  bosschest02_charon  (own named essence)
Devourer (Toxeus)    um_bloodtoxeus_99           genericbossorb_05   (R-99 roster)
```

**The Mnemophage's orb is not worse than his peers' - it is IDENTICAL to all four of them.** So "his orb
is trash" is a complaint about the **orb04 tier as a whole**, not a Mnemophage-specific defect. That
reframes the fix completely:

* Moving **only** the Mnemophage to orb05 would make him a strict outlier above Tantalus, Ephialtes,
  Kroisos and the Helepolis for no stated reason, and would red the build (`uber_apex_orb.verify()`
  asserts the orb05 carrier set is EXACTLY the derived Toxeus roster - that assertion is R-47/R-99's
  "not all champions" guarantee and is working as intended here, not obstructing).
* Moving **all five** onto orb05 is precisely the change Will refused ONE DAY EARLIER, in R-99, verbatim:
  *"i didnt tell you to increase the drop of all the champions, just the toxeus variants (all variants we
  made and didnt make) and leinth."*

**Doing either on my own authority would be overriding a ruling Will made yesterday.** So the orb half is
recorded as an open decision with the numbers rather than guessed at. **RECOMMENDATION:** the chest
shipped in Part 1 is the substantive answer to #14 - a Boss-locked, region-tuned dedicated hoard is a far
larger reward swing than the orb tier - so try it in play before re-tiering anything. If it still reads
thin, the clean options are (a) leave orb04 alone and raise the hoard's brackets, (b) mint ONE new mid
tier for the five placed non-Toxeus fixed ubers as a class, keeping orb05 exclusively Toxeus+Leinth and
R-99 intact, or (c) explicitly widen R-99 to admit them. **(b) is the option that fits every existing
ruling.** Not (a)-through-(c) chosen here; Will's call.

**STATUS:** Part 1 **IMPLEMENTED** on `fix/uber-placement`, gated and record-diffed. Part 2 **PENDING -
OPEN WILL DECISION**, measured, nothing changed.

## R-150 [2026-07-30] IMPLEMENTATION RECORD + factual amendments: R-105 / R-106 / R-107 rates, R-100 #11 forge acts, R-100 #17 Gaoler

> ### ⚠️ RENUMBERED R-140 -> R-150. THIS LANE MOVED ITS OWN, AND TOUCHED NOBODY ELSE'S.
>
> The original claim below was made in good faith and was true when written:
> `git grep -oE "\bR-1[0-9][0-9]\b" $(git branch -a --format='%(refname)')` returned R-100..R-124 +
> R-130 taken and the whole R-140..R-149 decade free. **It stopped being true while this lane was
> building.** Re-run at the end of the session:
>
> ```
> git grep -ohE "\bR-[0-9]{3}\b" $(git branch -a --format='%(refname)') -- docs/WILL_RULINGS.md | sort -u
>   -> R-100..R-125, R-130, R-140, R-141, R-149
> git grep -hnE "^## R-14[01]" refs/heads/fix/quest-item-leaks -- docs/WILL_RULINGS.md
>   -> 2389: ## R-140 ... R-100 #15 ROOT CAUSE: the thrown-wielders are frozen ...
>   -> 2488: ## R-141 ... R-101 quest-item leaks closed ...
>   -> 2551: ## R-140 AMENDMENT ... Three measured corrections to R-140 ...
> ```
>
> `fix/quest-item-leaks` had taken **R-140 for a completely different subject**, plus R-141 and an
> R-140 AMENDMENT that cross-reference each other. Per the ledger law a lane renumbers **its own**
> ruling and never reassigns another lane's, so **this** block moved: R-140 -> **R-150**. The
> R-150..R-159 decade was re-verified free against main and every in-flight branch with the command
> above at the moment of writing. Nothing on `fix/quest-item-leaks` was edited, and its R-140 stands.
> (`feat/devourer-kit`'s own collision note names `feat/soul-economy` as an R-140 incumbent - that
> note is now stale by exactly this renumber, and is left alone for the same reason.)
>
> **THIS IS NOT A NEW WILL DECISION.** No new words of his exist. It records (a) that R-105, R-106,
> R-107 Part 1, R-100 #11 and R-100 #17 are now IMPLEMENTED in code, and (b) the places where the
> MEASUREMENT inside those rulings - or inside this block's own first draft - was wrong or
> incomplete, corrected here rather than left standing, because a wrong premise about these fields
> mis-scopes every future soul change. Every correction is a command anyone can re-run.
>
> ⚠️ **AMENDMENTS 7-9 CORRECT AMENDMENT 5 AND THE FIRST DRAFT OF THIS BLOCK.** Amendments 1-6 were
> written from a build whose gate had never been run to green. It was then run, and it FAILED with 76
> violations. Read amendments 7-9 before trusting any count in 1-6.

### WHAT SHIPPED (branch `feat/soul-economy`)

| ruling | verbatim ask | shipped |
|---|---|---|
| R-105 | "no monsters should be at 66%. move all 66% and 50% to 33%" | **368** of the 373 at 66% and **all 361** at 50% -> 33 (**729** total, the build's own histogram). Of the remaining 5: **1** -> 25 (`um_polisgaoler_unbound_99`, R-107) and **4** HELD at 66 by the older UNTOUCHED ruling. The 50% cohort is EMPTY; the 66% cohort is exactly those 4 |
| R-105 | "25% for fixed location bosses and 33% for non-fixed location bosses" | the 12 `boss_pharaohshonorguard*` 10% -> 25%; the 5% pair and the 39 2%-tier heroes -> 33% |
| R-106 | "only hero monsters should drop their soul" | the 11 Common **droppers** -> 0% (the other 4 are PETS, see amendment 2) |
| R-106 | the four R-48 Toxeus champions stay 100 | asserted by gate invariant G3, unchanged |
| R-106 amdt | `um_charon_ferryman_99` + `um_tantalus_99` 0% -> 25% | **NOT shipped - the amendment is wrong, see AMENDMENT 6** |
| R-107 | "the soul gaoler should not drop the soul just the unbound final version" | base `um_polisgaoler_99` pinned at 0; `um_polisgaoler_unbound_99` 66% -> 25% |
| R-100 #11 | XP-potion forge formulas cannot use our souls | **580** soul->formula memberships added over 3 rounds to a fixed point (577 + 3 + 0); the 12 formulas now list **2,161** souls, **204** of them our own minted `svc_uber` souls |
| R-100 #17 | halve the Gaoler's chests; his epic chests drop "essence" not "embodiment" | 5 placements -> 2; the normal-tier guaranteed donors replaced with the chest's own legendary tier |

**HELD, untouched, and named so it cannot be lost:** the **172 Champion-tier carriers at 0%** plus **7
Champion carriers with a live fractional rate**. R-106's amendment put the star tier squarely to Will
("DOES 'STARS OR BETTER' INCLUDE THE WHOLE CHAMPION TIER? That is the 172-creature decision") and he has
not answered. The classifier returns HELD for them and gate invariant G7 fails if the HELD set drifts.

### AMENDMENT 1 - R-100 #11's premise is wrong: there is NO act classification FIELD

His words were *"the souls that we added ... do not have the proper classification on them"*. There is no
field to set. SV 0.98i ships 12 `ItemArtifactFormula` records
`records\item\formulas\{n,e,l}_{01..04}_lesserpotionofexperience_formula.dbr` whose three reagent slots
each hold an **enumerated list**: `[0X_actY_anysoul.dbr, <every soul of that act at that difficulty>]`
(measured: the `e_01` formula holds 152 entries, 151 of them `*_soul_e.dbr`). A soul is "act N" **iff it
is named in act N's list**, so a soul we mint is unusable until its path is appended there. `{n,e,l}` is
the difficulty tier and `01..04` is the act (1 Greece, 2 Egypt, 3 Orient, 4 Hades).
Reproduce: `py tools/debug/probe_xp_formula_reagents.py <arz>`.

**There is no act-5 formula anywhere** (SV 0.98i is Immortal-Throne-era; the base game ships none), so a
soul dropped by an `xpack2`/`xpack3` monster has no list to join. Those are reported, never forced into
act 4. **OPEN FOR WILL:** mint a 5th/6th formula set, or leave Ragnarok/Atlantis souls out of the forge.

### AMENDMENT 2 - four of R-106's fifteen "Common carriers" are WILL'S OWN PETS

R-106 ruled "those 15 go to 0%". Measured with `py tools/debug/probe_common_carriers.py <arz>`:

| carriers | what they are | action |
|---|---|---|
| 6 `soul\test\swift_ar_archer_08` / `swift_br_archer_14` (n/e/l) | Class=**Monster** | -> 0 |
| 5 `skills\boss skills\summoned minions\pharaoh'shonorguard_mummypriest_*` | Class=**Monster** | -> 0 |
| 4 `skills\soulskills\pets\carrioncrow_05/1/2/3` | **Class=Pet, Pet.tpl** | **HELD** |

The last four are the crows **a soul summons for him**. R-104 established that `chanceToEquipFinger2` does
double duty - drop rate AND a power switch - and on a Pet only the second meaning exists, because a pet
drops nothing. Zeroing them would have nerfed his summons and changed no drop anywhere: the
`toxeus_passiveproperties` trap (18 carriers, 9 of them his pets) in a new costume. Pet/Proxy/ProxyPool
templates are therefore excluded from the rate roster. **OPEN FOR WILL:** should a summoned crow keep
wearing its soul? (Recommendation: yes - leave them.)

### AMENDMENT 3 - the 1,722-carrier roster is NOT the `\creature(s)\` roster

R-104/R-106 cross-tabulated 1,722 soul-bearing creatures. The shipped `verify_soul_drop_rates` gate's own
`_is_creature()` path filter sees only **1,279** of them. The missing 443 include **every record R-105
named in the sub-25% buckets**: the 6 swift archers and all 39 of the 2%-tier heroes live under
`records\item\equipmentring\soul\test\`, the 5 mummy priests under `records\skills\boss skills\summoned
minions\`, and a Quest carrier at 66% under `records\drxcreatures\`. Applying the ruling on the old
roster would have shipped it half-done AND the gate would not have seen the half that was missed.
Selection is now by TEMPLATE, because the base game gives special bosses bespoke Monster-derived
Classes - `SpiritHost` (all 12 pharaoh honour guards), `Hades`, `Cerberus`, `Typhon`, `Ormenos`,
`Megalesios` - and a `Class == 'Monster'` filter silently drops 35 live carriers including the entire
10% cohort.

### AMENDMENT 4 - R-105's "0.3%" bucket is 0.35%, and the Common split is 6/9 with 4 of the 9 being pets

Measured on the built arz: the low buckets are **0.5% (13 records)** and **0.35% (11 records)**, not 0.3%.
Of the 15 Common carriers, 6 sit at 0.5 and 9 at 0.35 - and 4 of those 9 are the pet crows, so **11**
records were zeroed, not 15.

### AMENDMENT 5 - A TENSION INSIDE R-105, AND A RULING COLLISION THE BUILD CAUGHT

R-105 says both of these:
1. "move all 66% and 50% to 33%. **That is 734 creatures**" (a COUNT), and
2. "**25% for fixed location bosses** and 33% for non-fixed".

Five of the 734 are fixed-location act bosses: `boss_charon_39/41/43`, `boss_satyrshaman_55` and
`records\drxcreatures\bloodwitch\boss_hades_54.dbr`. Sentence 1 puts them at 33; sentence 2 at 25.

**AND FOUR OF THEM WERE ALREADY UNDER AN OLDER, EXPLICIT RULING OF HIS.**
`tools/patches/double_soul_rulings.py` ruling (c): *"CHARON 39/41/43 + HADES 54 - UNTOUCHED (Will's
explicit ruling)"*, enforced by a field-level zero-diff `verify()`. That gate **FAILED this wave's
first fully-gated build** and named exactly `boss_charon_39/41/43` + `boss_hades_54`. A newer COUNT
does not silently overrule an older explicit "untouched", so those four are **HELD at 66** (listed in
`build_svc_database.SOUL_RATE_UNTOUCHABLE`, cross-checked against that module's own roster by gate
G2b) and the collision goes back to Will. The sweep therefore moves **794** carriers (796 after this carve-out, then 2 more removed by AMENDMENT 6), not 800.

That leaves ONE record still sitting on the original tension: **`boss_satyrshaman_55`** ships at 33
under the count. Registered as `BL-b102-DEBT-2`; one line from him settles both halves.


### AMENDMENT 6 - THE R-106 AMENDMENT'S OTHER TWO "PLAIN DEFECTS" ARE NOT DEFECTS EITHER

The R-106 amendment listed three of our ubers as "fixed-location bosses ... currently at 0 - carrying a
soul that can never drop. That is a plain defect ... They need no policy decision at all." **R-107
already retracted that claim for the third one** (the Gaoler): *"the soul gaoler should not drop the
soul just the unbound final version"*.

**The other two are the same shape.** Measured (`py tools/debug/probe_uber_transform_chains.py <arz>`):

| head | chance | death-transforms into | terminal chance |
|---|---|---|---|
| `um_charon_ferryman_99` (carries `boss_charon_soul`) | **0** | `um_charonform2_ferryman_99` (carries `ferryman_soul`) | 66 |
| `um_tantalus_99` (carries `aberkios_soul`) | **0** | `um_tantalus_unbound_99` (carries `tantalus_soul`) | 66 |
| `um_polisgaoler_99` (carries `wardenofsouls_soul`) | **0** | `um_polisgaoler_unbound_99` (carries `polisgaoler_soul`) | 66 |

Every head carries its DONOR's soul and every terminal carries OURS. The 0 is the
one-soul-per-encounter law, not a defect - and raising it makes a single encounter pay two different
souls, which is precisely the Legion defect class. **The build proved it, loudly**: with the two heads
raised to 25, `double_soul_rulings.verify` failed with *"legion_soul_stages distinct-soul roster after
this module's fixes = [... um_charon_ferryman_99, um_tantalus_99], expected exactly Charon 39/41/43 +
Hades 54"*.

All three heads are pinned at 0 (`build_svc_database.SOUL_RATE_ZERO_PINS`). Only
`um_polisgaoler_unbound_99` remains a fixed-boss pin at 25. **Nothing here needs a Will decision** - it
is recorded so a later lane does not re-implement the amendment's wrong sentence.

### THE ONE CLASSIFIER, AND THE GATE

`build_svc_database.ruled_soul_equip_rate()` is the single decision point; it derives fixed-vs-non-fixed
from `soul_drop_rate()`, which keys on `monsterClassification` and never on the record name or folder -
the reason that matters is in R-106 itself (the mummy priests classify **Common** behind a boss-ish
filename). `apply_svc_patches._apply_soul_rate_policy()` applies it as the **last writer** of the release
build, so a hand-set rate anywhere upstream cannot survive. `tools/verify_soul_drop_rates.py` checks the
FINAL arz per-record against that same function and adds 7 whole-cohort invariants (G1..G7) with 7
planted negatives plus a positive control.

### R-100 #17: WHY THE GAOLER'S CHESTS COULD NOT SIMPLY BE MADE DIFFICULTY-AWARE

Measured on the base game (74,013 records): a **Monster.tpl** loot slot IS difficulty-indexed - 2,703
records carry `lootMisc2Item1 = [01_actN, 02_actN, 03_actN]`, including this Gaoler's own donor
`xsecrethero_wardenofsouls_48`. A **container's** loot table is NOT: **zero** `lootNNameM` fields
anywhere carry more than one value, and the base game instead ships one chest record per tier
(`goldenchest_normal_/epic_/legendary_01`). So the shipped defect - the one slot that fires at 100%
handing out normal-tier "Essence of ..." relics inside an otherwise legendary-tier chest - was fixed by
matching that slot to the chest's own tier. A vault that pays a different tier per DIFFICULTY needs 3
chest records per spot plus map-side placement: `BL-b102-DEBT-3`, Will's call.

### R-107 PART 2 IS NOT IMPLEMENTED

The Devourer reflect/pierce cut (Will HARD-BLOCKED from finishing that encounter) is untouched by this
lane - it needs his numbers, and its required implementation is a monster-only clone of
`toxeus_passiveproperties` so his 9 pets keep their defence. Still PENDING, still outranking the rest of
the R-100 batch.

### AMENDMENT 7 [2026-07-30] AMENDMENT 5 UNDERCOUNTED THE R-105 TENSION BY 7, AND THE CLASSIFIER WAS NOT IDEMPOTENT

AMENDMENT 5 said "**Five** of the 734 are fixed-location act bosses" and `BL-b102-DEBT-2` said the
carve-out left "**ONE** record on the original tension" (`boss_satyrshaman_55`). Both numbers are
wrong. Measured on the baseline arz, not inferred:

```
py -c "... roster = apply_svc_patches._soul_carrier_roster(baseline_main.arz);
       {r for r,cls,cur in roster
          if cur in (66.0, 50.0) and build_svc_database._soul_is_farmable_boss(r, cls)}"
  -> 12 records, all at 66.0, all cls=Boss
```

| record | in R-105's ratified 734 | classifier says | outcome |
|---|---|---|---|
| `boss_charon_39` / `_41` / `_43` | yes | fixed boss / 25 | **HELD at 66** (older UNTOUCHED ruling) |
| `boss_hades_54` | yes | fixed boss / 25 | **HELD at 66** (older UNTOUCHED ruling) |
| `boss_satyrshaman_55` | yes | fixed boss / 25 | ships **33** (COUNT) |
| `boss_coldworm50`, `boss_dagon_66` | yes | fixed boss / 25 | ships **33** (COUNT) |
| `q_leinth_47` / `_49` / `_50` | yes | fixed boss / 25 | ships **33** (COUNT) |
| `murderbunny` | yes | fixed boss / 25 | ships **33** (COUNT) |
| `svc_um_hadesmarshal_80` | yes | fixed boss / 25 | ships **33** (COUNT) |

So the open question for Will is **EIGHT records, not one**. The eight are not act bosses in the
Greece/Egypt/Orient/Hades sense - seven are OUR OWN placed ubers plus one base-game arena boss - and
`_soul_is_farmable_boss` reaches them through a naive `boss_`/`q_` path heuristic, which is exactly
why five of them used to carry `_KNOWN_EXCEPTIONS` waivers reading "the shipped value IS intended".

**AND THIS WAS NOT MERELY A COUNTING ERROR - IT WAS A LIVE DEFECT.** `ruled_soul_equip_rate()` keyed
the ratified-cohort rule on the record's CURRENT value, so it returned 33 while the record still sat
at 66 and **25 for the same record once 33 had been written**. The applier and the gate therefore
disagreed by construction, and the first fully-gated build of this wave failed on exactly these 8
records, twice each (LAST-WRITER mismatch + UNINTENDED golden-diff). The fix is
`build_svc_database.SOUL_RATE_COUNT_OVER_CLASS`, checked before both value-keyed rules, plus a
build-time re-derivation of the set from the pre-policy arz that HALTS the build if a new
fixed-location boss ever appears in the 66/50 cohort. Gate invariant **G8** + 2 planted negatives.

### AMENDMENT 8 [2026-07-30] THE UNTOUCHED-RULING ROSTER WAS THE ONLY ROSTER THE GATE COULD NOT DEFEND

Cohort invariant **G7b** ("every HELD record is Champion-classified, unset, or gated at 0") predates
the ruling-collision carve-out recorded in AMENDMENT 5. That carve-out holds 8 Boss-classified
Charon/Hades carriers at a **live** 66/25, so G7b red on all 8 - a gate failing on the carve-out its
own wave introduced. G7b now admits a fourth legal reason to be HELD, scoped to exactly
`SOUL_RATE_UNTOUCHABLE` (which G2b already cross-checks against `double_soul_rulings`' own roster).

Closing that exposed a worse hole and it is closed too. Because those records are HELD,
`expected == cur` by construction, so the intended-diff-vs-golden check called **any** move of them
"intended": the one roster protected by an explicit Will ruling was the only roster with no
standalone guard. A golden delta on an `SOUL_RATE_UNTOUCHABLE` record is now an unconditional
failure with its own planted negative.

### AMENDMENT 9 [2026-07-30] THE TESTING BUILD SILENTLY DID NOT FORCE 52 CARRIERS TO 100%

AMENDMENT 3 caught the `\creature(s)\` path filter in the gate's `_is_creature`.
**`apply_svc_patches._force_100_pct_soul_drops` had the identical filter and therefore the identical
hole.** Measured on the b102 build: 52 live soul carriers sit outside any `\creature(s)\` path and
were never boosted, so a build made with `SVC_TESTING_DROPS=1` left them at their RELEASE rate:

| n | path | what lives there |
|---|---|---|
| 42 | `records\item\equipmentring\soul\test\` | SV files real `Monster.tpl` records under an ITEM path - R-105's whole 2%-tier hero cohort |
| 5 | `records\item\miscellaneous\monsterscrolls\pets\` | monster-scroll summons |
| 4 | `records\test\` | **our own placed ubers** - `boss_dagon_66`, `boss_coldworm50` |
| 1 | `records\skills\monster skills\summoning_pets\pets\` | `dayria_carrioncrow_40` |

"I killed it twenty times on a 100% test build and got no soul" was therefore a **true report about
the test harness**, not about the drop rate. The forcer now uses the ONE shared
`_soul_carrier_roster`. Release builds never call it, and the record-diff proves the shipped release
arz is unchanged by this. The `chance > 0` gate is untouched, so Common (0 after R-106) still cannot
be re-enabled - the normal-yeti bug stays fixed - and the roster excludes Pet/Proxy/ProxyPool, so no
summon is affected.

### AMENDMENT 10 [2026-07-30] TWO MORE LIVE CARRIERS ARE HELD BY UNSET CLASSIFICATION, AND SHOULD BE NAMED

AMENDMENT 2 named the 4 pet crows. Measured, there are **two more** carriers with a live sub-1% rate
that the policy holds and that nothing in R-105/R-106 addresses, because their `monsterClassification`
is **empty** and the classifier refuses to rule on an unset class:

| record | rate | what it is |
|---|---|---|
| `records\item\miscellaneous\monsterscrolls\pets\duskyboar_17.dbr` | 0.5 | monster-scroll summon |
| `records\skills\monster skills\summoning_pets\pets\dayria_carrioncrow_40.dbr` | 0.35 | a monster's summoned pet |

Both are `Monster.tpl` (so the Pet/Proxy template exclusion does not catch them) but both are
**summons, not farmable monsters**, so the same reasoning as the crows applies: their
`chanceToEquipFinger2` is a power switch far more than a drop rate. They are HELD, untouched, and
recorded here so "the sub-25 buckets are all resolved" is never claimed. Registered under
`BL-b102-DEBT-1`. **OPEN FOR WILL** together with the crows, one answer covers all six.
**STATUS:** ~~ruled, in flight~~ **IMPLEMENTED** on `feat/uber-visibility` (the R-108 wave lane, task
`wx0ky10vv`) as `tools/patches/tombstone_xp_recovery.py`. Held to the EQUALITY, not to 10%. Detail below.

### R-109 IMPLEMENTATION (2026-07-30, `feat/uber-visibility`)

**THE MECHANISM WAS FOUND IN THE SHIPPED BYTES, NOT ASSUMED.** R-109 says "Do not assume it is a mirror of
`deathPenaltyEquation`; measure what it actually pays today." Measured, via the PE export table and a
disassembly of the stock 32-bit `Game.dll` (image base `0x10000000`); reproduce with
`py tools/debug/probe_tombstone_xp.py --disasm`:

| symbol | VA | what it does |
|---|---|---|
| `?CharacterIsDying@Player@GAME@@UAEXXZ` | `0x10207fc0` | the on-death handler |
| `?GetPlayerDeathExperiencePenalty@GameEngine@GAME@@QBEI...` | `0x101945a0` | evaluates the equation object at `GE+0x103C`, floors at 0, rounds (`+0.5` from `0x103a3348`, then `fistp` with RC=11), clamps between `GE+0x1064` (`deathPenaltyMin`) and `GE+0x1068` (`deathPenaltyMax`) |
| (XP helper on `Player+0xC2C`, not exported) | `0x1017d620` | MEASURED: `new = max(total - penalty, FLOOR)`, writes `new` back, **returns `old - new` = the amount ACTUALLY removed** (clamped at 0). `FLOOR` comes from `0x1017d540`, an equation evaluated for index `min(max(level-1,0), cap)`. INTERPRETATION (no field names in the binary): that is the current level's XP threshold, i.e. a death cannot de-level you. **R-109 does not rest on that reading** - only on the measured part, that the grave is handed the REALISED loss |
| `?RegisterExperienceLoss@GameEngine@GAME@@QAEXIH@Z` | `0x10194540` | `mov [eax+0xc], ecx` - stores that actual loss at **`GraveInfo+0x0C`** |
| `?GetPlayerExperienceRedemptionAmount@GameEngine@GAME@@IAEII@Z` | `0x10194f60` | reads `GraveInfo+0x0C`, `mulss xmm0, [edi+0x2a04]`, truncates |
| the GameEngine field loader | `0x1019b8c3` | `mov [esp],0x3f000000` (0.5f default) / `push "RedemptionMultiplier"` / `fstp [edi+0x2a04]` - the ONLY writer of `GE+0x2A04`, and the `mulss` above is its only reader |

So, exactly: **`recovered = trunc( (float)(XP ACTUALLY LOST) * RedemptionMultiplier )`**, on the same
`records\xpack\game\gameengine.dbr` that `death_xp_penalty` (R-80) owns. `Game.dll` also hard-codes the ONE
gravestone record at `0x00344554` (`Records/XPack/Item/Gravestones/GravestoneGreece.dbr`, Class
`FixedItemGravestone`).

**🛑 R-109's PREMISE WAS WRONG IN THE PLAYER'S FAVOUR, AND THAT CORRECTION IS THE HONEST REPORT.** R-109
feared "the player loses 10% and recovers 100%" - a free-XP loop we introduced with b93. **That loop never
existed.** The grave stores the amount actually removed, not a precomputed absolute, so b93's cut scaled the
recovery in lockstep: before b93 you lost `P` and got back `0.5P`; after b93 you lost `0.1P` and got back
`0.05P`. Recovery was ALWAYS half the loss and never above it. The real pre-R-109 defect is the opposite one,
and it is exactly the one R-109's own gate clause names: **the player was being punished twice.**

**THE CHANGE (one field, and it is DERIVED, not hardcoded):**

    records\xpack\game\gameengine.dbr
      RedemptionMultiplier    0.5  ->  1.0        (dtype FLOAT, preserved)

At 1.0 the engine's own formula collapses to `recovered = lost`. R-109 asks for the recovery to be
"expressed in terms of the penalty so the two cannot drift" - **the engine already does that**, because
`RegisterExperienceLoss` records the realised loss and the redemption path never reads `deathPenalty*` at
all. Retune the penalty however you like and the marker follows with no edit here. That is proved, not
argued: negtest plant 6 retunes the penalty to divisor 45 / cap 123456 and the gate still **passes untouched**.
1.0f is also the value `GameEngine`'s own constructor puts in that member before the DBR load
(`0x101a378d`, `mov dword ptr [ebx+0x2a04], 0x3f800000`), so it is the engine's own number, not an
out-of-band one.

**MEASURED BEFORE/AFTER, BOTH WAYS** (`py tools/patches/tombstone_xp_recovery.py --table <arz>`; every LOST /
BACK value is an integer because the engine rounds before the clamp):

| level | difficulty | LOST pre-b93 | LOST now | BACK @0.5 pre-b93 | BACK @0.5 now (shipped) | **BACK @1.0 now (R-109)** |
|---|---|---|---|---|---|---|
| 10 | Normal | 111 | 11 | 55 | 5 | **11** |
| 10 | Epic | 444 | 44 | 222 | 22 | **44** |
| 10 | Legendary | 778 | 78 | 389 | 39 | **78** |
| 40 | Normal | 7111 | 711 | 3555 | 355 | **711** |
| 40 | Epic | 28444 | 2844 | 14222 | 1422 | **2844** |
| 40 | Legendary | 49778 | 4978 | 24889 | 2489 | **4978** |
| 70 | Normal | 38111 | 3811 | 19055 | 1905 | **3811** |
| 70 | Epic | 152444 | 15244 | 76222 | 7622 | **15244** |
| 70 | Legendary | 266778 | 26678 | 133389 | 13339 | **26678** |
| 85 | Legendary | 477653 | 47765 | 238826 | 23882 | **47765** |
| 100 | Normal | 111111 | 11111 | 55555 | 5555 | **11111** |
| 100 | Epic | 444444 | 44444 | 222222 | 22222 | **44444** |
| 100 | Legendary | 500000 | 50000 | 250000 | 25000 | **50000** |

Ratio recovered/lost: **0.5000 before, 1.0000 after**, on all three difficulties.

**EXACTNESS.** The round-trip is int32 -> double -> float32 -> `mulss 1.0f` -> truncate. float32 represents
every integer below 2^24 exactly, `x * 1.0f` is exact, and truncating an exactly-represented integer returns
it. The shipped `deathPenaltyMax` is 50,000, i.e. **336x inside** that bound, and `verify()` re-proves the
headroom against the LIVE cap rather than a constant (and reds the build if a future lane raises the cap
past 2^24).

**THE GATE**, in R-109's superseding form (equality, both sides): `verify()` runs on the FINAL merged arz and
re-derives the equality numerically over L1-1000 x Normal/Epic/Legendary **against the LIVE penalty knobs read
out of the arz** plus the realised-loss domain up to the float32 bound (3,012 checked points), re-asserts the
FLOAT dtype, re-asserts all five dead `gameengine` lookalikes still at 0.5 (anti-shotgun), and re-asserts the
gravestone record still exists and is still `FixedItemGravestone` (retirement protocol - `Game.dll` hard-codes
that path, so retiring it would delete the surface this ruling is about).

`py tools/patches/tombstone_xp_recovery.py --negtest` -> **PASS (7/7)**:

| plant | expected | got |
|---|---|---|
| control - the ruled state | ACCEPT | ACCEPT |
| recovery ABOVE the loss (multiplier 2.0) | REJECT | REJECT |
| recovery BELOW the loss (the pre-R-109 0.5) | REJECT | REJECT |
| the hardcoded-10% form R-109 rejects (multiplier 0.1) | REJECT | REJECT |
| a dead lookalike shotgunned with the edit | REJECT | REJECT |
| the ONE gravestone record de-classed | REJECT | REJECT |
| **penalty retuned (divisor 90 -> 45, cap -> 123456), no edit here** | **ACCEPT** | **ACCEPT** |

**SCOPE:** one field on one record. `deathPenaltyEquation` / `Min` / `Max` are re-asserted byte-equal by this
module's own scope proof, so R-80 is provably untouched. No new records, no tags, no map bytes, no
`Text.arc` surface. MULTIPLAYER: a DB field, so every player must ship the identical arz (the standing
determinism statement); it carries no party-size or spawn-equation term.

**NOT PROVEN IN-GAME.** The arithmetic is engine-side and is proved from the disassembly and from the
gate, but no character has died and walked back to a marker on a build carrying this change. Will's
in-game check is the launch gate (registered as debt).

---

## Player-facing names / vanilla-name fidelity (new section; decade 160-169, opened 2026-08-06, branch `fix/pr4-gorgon-vanilla`)

> Decade proven free by git grep at open time: `for n in 160..169; do git grep -h "R-$n\b" -- docs/WILL_RULINGS.md; done` = 0 hits each.

## R-160 [2026-08-06] IMPLEMENTED (branch `fix/pr4-gorgon-vanilla`) "restore the FULL VANILLA names" - PR-4, Steam player Flozer44 (2026-07-28): the two Gorgon spellcasters show their vanilla names SWAPPED ("Impious"/"Geomancy Adept" on the wrong monsters, in his words). Un-swap them to the stock-Titan-Quest assignment.

**GROUND TRUTH (measured from the bytes; Will's paraphrase reconciled to the actual strings).** The two
gorgon-caster archetypes, identified by each creature's OWN skill kit (never guessed):

| record | kit signature (skillName1/2) | element |
|---|---|---|
| `records\creature\monster\gorgon\ar_pyromancer_13.dbr` + `_16` | BlazingWeapons + PillarofFlame | FIRE |
| `records\creature\monster\gorgon\ar_venomancer_13.dbr` + `_16` | Arachnos_VenomBolt + Arachne PoisonCloud | POISON |

BASE TQAE `database.arz` assigns `description`: FIRE pyromancer -> `tagMonsterName1263`, POISON venomancer ->
`tagMonsterName1256`. BASE TQAE `Text_EN.arc` (and SV 0.98i's, byte-for-byte the same strings):
`tagMonsterName1263` = "Gorgon ~ Geomancer", `tagMonsterName1256` = "Gorgon ~ Profaner". So the literals Will
and the player named ("Impious"/"Geomancy Adept") appear in NO text source - they are a paraphrase of the
actual vanilla strings "Profaner"/"Geomancer". Soulvizier 0.98i (which our merge carries VERBATIM) FLIPPED
the two record->tag pointers relative to base (the STRINGS were never changed): our shipped build had FIRE ->
1256 ("Profaner") and POISON -> 1263 ("Geomancer") - exactly the swap the player saw.

**THE FIX (smallest correct change).** Repoint `description` on the 4 records back to the base-game
assignment (FIRE -> 1263 "Gorgon ~ Geomancer", POISON -> 1256 "Gorgon ~ Profaner"). No tag STRING is edited
and no NEW tag is minted (both are base-game tags, present in base `Text_EN.arc` and resolving from it
underneath our `Text.arc` after the i18n de-clobber). Implemented as the registry module
`tools/patches/gorgon_vanilla_names.py` (before the no-op `visuals`). SHARED-RECORD LAW: `verify()` asserts
the two tags are carried by EXACTLY these 4 records in the merged DB (the XPack4 chaos gorgons use the
DISTINCT `x4tagMonsterName*Chaos` tags), and the name is bound to identity via the kit-signature check.

**PROOF.** Record-diff vs a same-environment main-HEAD baseline (`3a3a0b41...`): 0 ADDED, 0 REMOVED, exactly
4 MODIFIED, `description` field only. Fixed arz `ab02f16e11d2cfa2dd05c0ce479fb917`; Text.arc
`39c505485aa4abb6c5bf8d1bf5e62f4b`. Full gated build green (SVC_REQUIRE_GATES=1); `validate_tags` PASS;
Text.arc read-back confirms fire caster -> "Gorgon ~ Geomancer", poison caster -> "Gorgon ~ Profaner".

**NOTE (honest, not a blocker).** In stock Titan Quest neither name is element-perfect: the FIRE caster wears
"Geomancer" (an earth name) and the POISON caster wears "Profaner". This fix restores the exact stock-TQ
display names on the correct creatures, per Will's "restore the FULL VANILLA names" - it does not invent new
element-matched names. NOT PROVEN IN-GAME: a display-name change is proven from the rebuilt Text.arc, but a
player eyeballing the two monsters near Knossos is the launch gate (orchestrator owns deploys).
## Items / costume dyes
- R-160 [2026-08-06] IMPLEMENTED `fix/pr2-dye-skins` (Resources-only; no arz change) - **Will verbatim
  (PR-2 decision):** *"try to FIND the missing costume-dye skin assets; wire in the ones found; for the
  ones that cannot be found, REMOVE them."* Context: the Garden-of-Merchants "special / costume dyes"
  (OneShot_Dye records) reskin the PC to `Creatures\PC\{Male,Female}\...tex` from amgoz1's AllSkins
  pack; the shipped mod painted the PC flat GREY (Flozer44 report, PR-2). ROOT CAUSE (byte-proven):
  `scripts/bootstrap_working_mod.ps1` Step 2b STRIPPED `Creatures.arc` as "cosmetic - falls back to
  base skins", but the AllSkins skin paths do NOT exist in base -> unresolved material -> grey. The
  skins DO exist, in SV 0.98i's OWN `Creatures.arc` (md5 5ef9d00a, in `third_party/soulvizier098i.zip`
  - the source the prior `fix/pr2-dyes-grey` lane never checked, which is why it concluded "drop"). FOUND:
  a purely-additive mod `Creatures.arc` (288 net-new SV skin entries; overrides 0 base asset) makes ALL
  288 OBTAINABLE dyes resolve. Gate `tools/gate_dye_skins.py` proves it (PASS iff zero obtainable dye
  references a missing skin; --negtest). NOT-FOUND -> "REMOVE": 34 dyes reference a male skin that
  exists in NO shippable source (14 `Nyours_Placeholder*`, 15 `NtheRavens_MaleHairy*`, 5 one-offs) - ALL
  34 are ORPHAN records already in NO loot table and NOT placed in the world map, i.e. already
  unobtainable, so "removed" is already true; per the RETIREMENT PROTOCOL the dead records are left
  intact (not deleted) and documented. **OPEN FOR WILL (flagged, not vetoed here):** the restored skins
  are amgoz1's AllSkins community pack (some nude/topless/lingerie variants - original SV content), and
  keeping `Creatures.arc` costs ~+98 MB decompressed address space on the 32-bit engine (mitigated by
  the 4GB LAA patch). In-game confirmation that a dyed PC now renders is LAUNCH-GATED. See
  docs/BACKLOG.md PR-2 and the dye-skins lane report.
## Side-area access / discoverability (decade 160-169, opened 2026-08-06, branch `fix/pr5-catacomb-traveler`)

## R-170 [2026-08-06] IMPLEMENTED (fix/pr5-catacomb-traveler) - the Sparta Crypt is entered from the Athens catacombs, not from Helos

VERBATIM (Will's decision, PR-5): "the Sparta Crypt should be entered from the Athens CATACOMBS, not
from Helos."

CONTEXT: on the shipped/canonical map the Sparta Crypt (spartacryptlevel2) was reachable ONLY via
"Almyros the Wayfarer" (portal_master_helos) in the Helos start plaza, whose boat menu carried a "The
Sparta Crypt" destination. Nobody could discover it - the Steam player Flozer44 AND Will (2026-07-14,
R-triage in BACKLOG PR-5) both hunted the Athens catacombs for a portal that was not there. The
catacomb traveler records (svc_area_return_sparta / svc_helos_trav_sparta) existed in the arz but
shipped placed 0x (TESTHUB-only).

IMPLEMENTED as a coupled MAP + QUESTS change (arz + Text untouched; the enter-offer menu tags already
shipped):
- MAP: svc_area_return_sparta (the Athens-catacomb "tomb guy" + the b62 enter-offer OWNER) is PROMOTED
  from the TESTHUB-only return set to a single CANONICAL placement in the deepest Athens catacomb
  (catacube02_floorlast, by stairsdown01) at local (25,1,38) = world (-6587,1,-3180) - on-mesh
  d=0.14u, clr 100% all 3 tilesets, comp#1. Its 0x0b navmesh is byte-identical (only 0x05 grows by
  the one NPC). The interior return NPC svc_testhub_return_sparta already stands in the crypt and was
  NOT duplicated.
- QUESTS: the "The Sparta Crypt" destination (tagSVCHelosToSparta) is REMOVED from Almyros's Helos boat
  menu; his Garden / Secret Place / Uber Dungeon destinations are KEPT. The catacomb NPC's existing
  boat-dialog ("Descend into the Sparta Crypt", tagSVCEnterSpartaCrypt) lands the player on-mesh inside
  spartacryptlevel2 at (-5596,-2,-1410). NOTE the landing is NOT Almyros's raw (-5602,-2,-1409): that
  spot FAILS gate_landing_clearance (greece_sarcophagia02_02 is a CONTAINER at 2.38u < the 4.0u min -
  the chest-pin bug class); the b62-nudged (-5596,-2,-1410) passes at 100%.

PROOFS (built this lane): canonical map wave 2677f7ac (baseline f30303ed = ship) - ONLY
catacube02_floorlast.lvl 0x05 changed, navmesh identical. Quests wave 85f73859 (baseline bd0fb5f9 =
ship) - ONLY sv_commonmechanics.qst, portal_master_helos 4->3, tagSVCHelosToSparta 2->1,
Garden/Secret/Uber 2->2. Gates green: gate_traveler_responds (canonical + TESTHUB, built + spec),
gate_landing_clearance v1 (PASS=27, both maps).

NOT PROVEN IN-GAME. Deploys are the orchestrator's. Will's walk (into the deepest Athens catacomb, talk
to the traveler by the stairs-down, descend, kill through, return) is the remaining launch gate -
registered as debt. See docs/WILL_TEST_GUIDE.md (PR-5 catacomb-entrance step) and BACKLOG PR-5.

### R-170 AMENDMENT [2026-08-06] IMPLEMENTED (fix/pr5-sparta-polish) - name the catacomb NPC "Warden of the Spartan Crypt" + descend-only menu

VERBATIM (Will's decision, PR-5 polish): Will decided TWO things about the catacomb entrance NPC that
R-170 placed: (1) NAME it "Warden of the Spartan Crypt" (it had displayed the generic shared name
"Return Traveler"); (2) its menu is DESCEND ONLY - remove the "Helos (Return)" travel option it
inherited from the shared area-return record.

SHARED-RECORD LAW (the crux): the record R-170 placed at the catacomb was svc_area_return_sparta,
whose descriptionTag tagSVCNpcAreaReturn ("Return Traveler") is SHARED by all 11 area-return travelers
(Dorus, Tantalus, Charon, ... Obsidian). Renaming that tag OR mutating that record would rename/alter
every sibling. So instead this lane CLONES svc_area_return_sparta into a DEDICATED record
svc_warden_sparta_crypt with its OWN descriptionTag (tagSVCNpcWardenSpartaCrypt = "Warden of the
Spartan Crypt") + a fitting greeting (tagSVCWardenSpartaCryptChat), and PLACES THE CLONE at the exact
proven on-mesh catacomb spot (local (25,1,38) = world (-6587,1,-3180)) instead of svc_area_return_sparta.

IMPLEMENTED (coupled arz + Text + MAP + QUESTS; the shared record left BYTE-UNCHANGED):
- arz (apply_svc_patches _create_sparta_crypt_warden): svc_warden_sparta_crypt = a byte-identical clone
  of svc_area_return_sparta except description + messageDialogTag + FileDescription. The shared
  svc_area_return_sparta is untouched (Class=Npc, description=tagSVCNpcAreaReturn) and kept as the clone
  donor per the RETIREMENT PROTOCOL - it is now placed NOWHERE.
- Text: 2 new tags minted (name + greeting); tagSVCNpcAreaReturn = "Return Traveler" untouched.
- MAP (build_section_surgery): INJECT_SPECS[catacube02_floorlast] places WARDEN_SPARTA_DBR (the clone),
  same coord, same NPC byte-shape -> the level's 0x0b navmesh is byte-identical; only the 0x05 record-
  path string differs (+1 byte).
- QUESTS (build_quest_files): the "Descend into the Sparta Crypt" enter-offer (tagSVCEnterSpartaCrypt)
  is keyed on the CLONE; svc_area_return_sparta's "Helos (Return)" entry (tagSVCAreaReturnToHelos) is
  REMOVED from HELOS_HUB_TRAVEL -> the Warden offers EXACTLY ONE option; the shared record now carries
  no route and no placement. The interior return NPC svc_testhub_return_sparta (in spartacryptlevel2)
  is UNCHANGED - it still sends the player back to this catacomb door / Helos.
- GATES: gate_travel_npc_invariants T2/T5/T5c brought green for the 24-record hub + the new canonical
  Warden + the retired donor (the R-170 lane had left this battery red); gate_traveler_responds HUB_KW
  += svc_warden_sparta (Warden now tracked, proven to own only its descend route); gate_landing_clearance
  classifies svc_warden as a soft-collision NPC (like svc_area_return_*).

PROOFS (built this lane, this env; baseline = main-HEAD 48f47f4). arz record-diff base ab02f16e ->
wave d447f095: ADDED=1 (svc_warden_sparta_crypt), REMOVED=0, MODIFIED=0 (svc_area_return_sparta
byte-unchanged). Text.arc modstrings diff: +2 lines only (Warden name + greeting), 0 removed;
tagSVCNpcAreaReturn="Return Traveler" unchanged. sv_commonmechanics boat-route diff: the Warden owns
EXACTLY ONE route (tagSVCEnterSpartaCrypt -> on-mesh (-5596,-2,-1410)); svc_area_return_sparta lost
BOTH routes (retired). Canonical map baseline 2677f7ac (== R-170 ship wave) -> wave 78a3e263, and
TESTHUB baseline e708389f -> d5ce1835: ONLY CataCube02_FloorLast changed (0x05 +1 B), 0x0b navmesh
BYTE-IDENTICAL (124427, parse_rec02 OK), 0 levels added/removed, QUESTS/GROUPS/SD/BITMAPS/DATA2 byte-
identical. Placement counts on the built canonical map: svc_warden_sparta_crypt x1 (CataCube02_FloorLast),
svc_area_return_sparta x0, svc_testhub_return_sparta x1 (SpartaCryptLevel2), Almyros (portal_master_helos)
x1 offering Garden/Secret/Uber only. Gates GREEN: gate_travel_npc_invariants (build-free + built-arc T6),
gate_traveler_responds (canonical + TESTHUB), gate_landing_clearance --wiring v1 (built map PASS).

NOT PROVEN IN-GAME. Deploys are the orchestrator's. Will's walk (into the deepest Athens catacomb, talk
to the WARDEN by the stairs-down, confirm the name reads "Warden of the Spartan Crypt" and the menu has
ONLY "Descend into the Sparta Crypt", descend, return) is the remaining launch gate - registered as debt.

### R-170 FOLLOW-UP [2026-08-10] IMPLEMENTED (fix/warden-sparta-dialog) - b63 THE WARDEN WAS MUTE: the descend route moves onto the proven trigger class + he moves off the teleport landing

VERBATIM (Will's bug report, 2026-08-10): "when I click on the guy who travels you to the spartan
crypt (warden of the spartan crypt) nothing happens, no dialog box comes up, nothing."

THIS IS THE R-170 AMENDMENT'S OWN LAUNCH GATE FAILING. That entry closed with "NOT PROVEN IN-GAME
... Will's walk ... is the remaining launch gate - registered as debt". The walk happened; it failed.
SEVERITY P0 AND LIVE ON STEAM since 2026-08-06 (ship record commit 045efb6, Workshop 3759792705):
PR-5 deleted tagSVCHelosToSparta from Almyros's Helos menu and the canonical map does not place
svc_helos_trav_sparta at all, so the catacomb Warden is the SOLE entrance to spartacryptlevel2 for
every subscriber. If he is mute there, that whole area has been unreachable for four days.

WHAT WAS WRONG (two stacked defects; deploy staleness was RULED OUT - the DEV set Will played is
coherent, arz + Text + Levels + Quests all carry PR-5, and his live _Toxeus .que files match the
DEV quest definition exactly at 402 triggers / 39 boat actions).

PRIMARY - MENU SOURCE. The POLISH left the Warden with EXACTLY ONE menu entry, and that entry was
emitted by build_quest_files._add_traveler_enter_offers. The Warden was the ONLY placed NPC in the
mod whose entire menu came from an enter-offer, and that trigger class has ZERO in-game
confirmations anywhere in this project, whereas all 30 earlier triggers in the host step are classes
Will has demonstrably used. Before the POLISH the catacomb NPC carried tagSVCAreaReturnToHelos from
HELOS_HUB_TRAVEL, a proven class; commit 1f66404 removed that line to honour DESCEND ONLY and in
doing so left the never-verified class as his sole menu source. Zero menu entries = no dialog box at
all, which is exactly the symptom.
HONEST CAVEAT, stated so nobody over-claims: the two generators emit a STRUCTURALLY IDENTICAL
trigger (verified against the deployed DEV quest - same Condition_OnLevelLoad, same single
Action_BoatDialog, same field order). The only real differences are the displayTag string and the
trigger's POSITION in step 1, because enter-offers are appended LAST (the Warden was trigger 31 of
33). So the operative change is REGISTRATION ORDER plus generator provenance, not a different
mechanism. This is the strongest quest-side lever available; if the Warden is still mute after this
wave, the next suspect is Action_BoatDialog binding only for levels loaded at trigger time (test by
teleporting in versus walking in), and the cure is a GridEntrance door (the proven build24/25
Knossos-to-Uber mechanism) instead of a boat NPC.

CONTRIBUTING - CLICK TARGETING. He stood at world (-6587,1,-3180), byte-for-byte the destination of
BOTH routes that teleport the player to that door (tagSVCHelosToSparta, tagSVCReturnToAthensCatacomb).
0.00u. That only ever shipped because commit f83162f made gate_landing_clearance TOLERATE it (it
classified svc_warden into the soft-collision NPC class, which raises a NOTE and never a FAIL)
instead of moving him.

IMPLEMENTED (Quests + MAP + gates; arz and Text UNTOUCHED, no new records, no new tags):
- QUESTS (build_quest_files): the Warden's single route moves from TRAVELER_ENTER_OFFERS into
  HELOS_HUB_TRAVEL, as its FIRST row (earliest hub slot). Count conservation is now a build-time
  law (_HUB_PLUS_ENTER_TRIGGERS = 26), so step 1 stays at 33 triggers / 39 boat actions - exactly
  what the deployed and Steam builds carry.
- MAP (build_section_surgery): the Warden moves local (25,1,38) -> (25,1,32) = world
  (-6587,1,-3186). Surveyed on the canonical ship map 78a3e263: d=0.14u on-mesh, clr 100/100/99%,
  comp#1/123720; 6.00u from both landings (was 0.00u); stairsdown01 6.51u (was 6.07u) so he still
  stands right by the stairs-down as this ledger and WILL_TEST_GUIDE describe; nearest hard collider
  4.58u (was 3.69u). Talk NPC, flags=0, no 0x14 -> the level's 0x0b navmesh stays byte-identical.
- GATES (no-new-surface-without-a-gate): G-SOLE-SOURCE (no placed boat NPC may draw its entire menu
  from TRAVELER_ENTER_OFFERS); G-DIALOG-CHAIN (every placed traveler's record -> quest -> QUESTS
  load-window chain must resolve); G-NPC-LANDING-SEP (exemption-free minimum separation between any
  placed boat NPC and any boat route destination); the same sole-source law asserted at import time
  in build_quest_files and again in gate_travel_npc_invariants T5c.

R-170 AND ITS AMENDMENT ARE UNCHANGED AS DESIGN LAW. Will's ruling is about the MENU, not about
which generator emits it: the Warden still offers EXACTLY ONE option, "Descend into the Sparta
Crypt" (tagSVCEnterSpartaCrypt), still lands at (-5596,-2,-1410), and still has NO "Helos (Return)"
port. gate_travel_npc_invariants T5c now asserts that menu shape DIRECTLY (exactly one route, that
tag, never tagSVCAreaReturnToHelos), so it can no longer be satisfied by accident.
DO NOT "fix" a future Warden problem by re-adding tagSVCAreaReturnToHelos to him - that would give
him two options and violate Will's DESCEND-ONLY decision.

PROOFS (build-free, this env; baseline main-HEAD 63238f3): gate_travel_npc_invariants GATE PASS;
gate_traveler_responds --specs and --specs --canonical PASS (31 route owners / 39 routes UNCHANGED;
sources hub 24->25, enter_offer 2->1); gate_traveler_responds --negtest PASS (7 planted violations
caught, baseline green); negtest_warden_dialog PASS (10/10, including a false-positive guard);
the NEW gate run against PRISTINE main goes RED naming svc_warden_sparta_crypt, i.e. it would have
caught the 2026-08-06 regression; gate_landing_clearance vs the DEPLOYED DEV map (still carrying the
old placement) reports exactly 1 G-NPC-LANDING-SEP violation of 156 pairs, the Warden at 0.00u.

NOT PROVEN IN-GAME, AND THE PREVIOUS "shipped on evidence" IS EXACTLY WHY THIS BUG EXISTS. Deploys
and the Steam update are the orchestrator's/Will's. The remaining gate is Will's walk. Test on
LEGENDARY or EPIC: his Normal-difficulty .que is still the stale pre-PR-5 shape (403 triggers / 41
boat actions) and will only re-sync on next load. Steam must be updated in the same wave, keeping
arz+Text and Levels+Quests coupled, with a changenote saying the Sparta Crypt entrance was broken
from 2026-08-06 to the fix date.

## Chest loot breadth (new section; decade 180-189, opened 2026-08-10, lane `chest-loot-breadth`)

## R-180 [2026-08-10] IMPLEMENTED (chest-loot-breadth) - the chests must drop DIFFERENT items, and legendary SPEARS must be possible

VERBATIM (Will, 2026-08-10): "we need to update the chests in the test hub in the place where the
Polybotes Soul drops in the prison of souls so that they drop different items since right now I am
seeing every chest drop the same items pretty much ever playthrough, there are never any legendary
spears dropped it is basically the same items dropped over and over by all chests. we need to expand
the bredth of the legendary items dropped in the testhub chests and also in the steam version."

WHICH CHESTS: "the place where the Polybotes Soul drops in the prison of souls" = the Polis Daemonai
Warden's Vault-Cage in `hadespalace_floor04_01`, guarded by Alkyoneus the Soul-Gaoler (Polybotes =
`xhero_polybotes_47`, the cage's H6 lieutenant). The TESTHUB cage holds SIX physical chests (the 2
canonical placements + the 4 farm duplicates of 2026-08-08, commit `7d6e276`) but only TWO records.

ROOT CAUSE, measured on the live DEV arz `9c190b99` (both halves are real defects, not perception):
1. NO LEGENDARY SPEARS WAS STRUCTURAL. Every mod chest's weapon row is a clone of the DRX donor
   `loottable_hidden_bloodcave_0N`, whose loot1 names `static_all_l01a` (w1000), `static_staff_l01a`
   (w500), `unique_1h_l01` (w200), `bow_l01` (w200), `staff_l01` (w200). `unique_1h_l01` is a
   LootMasterTable with EXACTLY THREE children - axe, club, sword. Spear, thrown and every 2H class
   are not members. The donor compensates for bow and staff by naming them DIRECTLY and simply forgot
   the third excluded class, SPEAR. The only spear path left was `static_all_l01a ->
   static_spear_l01a`, a static randomizer with 50 Rare / 24 Magical / 5 Common / 1 Broken and ZERO
   Legendary leaves. So a legendary spear was IMPOSSIBLE from all 40 mod chest tables while 24
   legendary spears sat in the DB unreachable. `xpack\...\weapons\unique\spear_l01.dbr` (17 items,
   all Legendary, same shape as the already-named `bow_l01`) was named by zero chests in the mod.
2. THE SAMENESS. `loot3Chance=100` with a single member (`unique_1h_l01`) made one axe/mace/sword
   unique the only slot that reliably fired; loot1 (weapons) and loot6 (shields) fired at 14% each
   (1.13 expected non-guaranteed hits per open), and the two placed chest records were near-clones
   (field diff: 70 identical, 4 different), so six chests drew from one collapsed pool.

IMPLEMENTED (arz-only - the chest records and loot tables live entirely in the .arz and the TESTHUB
duplicates reference the SAME records, so the fix reaches the TESTHUB cage AND canonical/Steam
together, with no Levels/Text/Quests rebuild):
- `tools/svc_loot_breadth.py` (NEW) is the ONE implementation. FixedItemLoot caps at 6 groups x 6
  members (measured across base + mod) and loot1 already used 5, so breadth is added the base game's
  own way: one aggregate LootMasterTable per tier, `svc_unique_weapons_{n,e,l}01` = unique_1h + spear
  + bow + staff (xpack band) + the base `all_{tier}0{1,2,3}` mastertables, dropped into the single
  free member slot at w800. Weapon-row chance 14 -> 40, shield row 14 -> 30. The GUARANTEED loot3
  weapon member is re-aimed from `unique_1h_*01` onto that master AT THE SAME WEIGHT, so every
  chest's guaranteed weapon:relic split is exactly what shipped - only the classes it can pay widen.
- `tools/patches/chest_loot_breadth.py` (NEW, registered last before `visuals`) sweeps all 51
  mod-owned gear chests + the 3 DRX donors, so the Steam half of the ask ("and also in the steam
  version") and every boss hoard get the identical treatment from one edit. Closes BL-b102-DEBT-4.
- `tools/patches/polis_vault.py`: the cage stops mirroring itself with NO map edit. Each placed
  chest's per-difficulty ProxyAccessoryPool now names THREE THEMED containers at 50/25/25 instead of
  one - chest_01 = martial (spear + 1H bias) / hunter (bow + spear) / warden (shield + armour),
  chest_03 = apex (any class + relic) / adept (staff) / sovereign (jewellery). That is the base
  game's cave-boss-chest construction (952 shipped ProxyAccessoryPools name more than one container;
  `legendary_01_cavebosschest_01` picks among 3 at 75/50/25), so each of the six physical chests
  resolves its own theme at spawn and re-rolls on a later playthrough.

NON-REDUCTION (Will farms this cage on Legendary; R-100 #17 + Will 2026-08-08 both preserved it):
numSpawn equations untouched and asserted per variant, no member removed, no chance lowered, the
guaranteed slot still 100%, the Legendary chain still lands on `polisvault_0N`. Every edit is
additive or a strict raise. The per-difficulty relic law (Essence / Embodiment / Incarnation) is
preserved by construction and re-proven by `gate_relic_difficulty_tiers` (21 branches, 0 leaks).

MEASURED (dry-run of the real code against the live arz, before -> after):
Legendary 258 -> 308 distinct legendary items, legendary spears 0 -> 22 (every ungated one);
Epic 90 -> 111 (9 spears); Normal 99 -> 181 own-tier items (18 spears) with ZERO legendary gear
leaked down. The 2 spears still out of reach are deliberate: `svc_l_runbreaker` (the Endless Hunt's
guaranteed drop) and the DRX supra craft-only spear.

GATE (law 4, no new surface without a gate): `tools/gate_chest_loot_breadth.py` + the in-build
`chest_loot_breadth.verify()` + `polis_vault.verify()` T7, all sharing one implementation - B1 every
mod chest reaches every weapon class at its own tier (SPEAR named explicitly), B2 per-tier pool
floor, B3 no legendary gear on Normal, plus the differentiation assertion that the cage's tables are
never field-identical again. Negatives: `tools/debug/negtest_chest_breadth.py` (5 plants RED, 2
positive controls GREEN).

NOT PROVEN IN-GAME. The build, DEV deploy and Steam ship are the orchestrator's; Will's check (kill
Alkyoneus, open all 6 cage chests across 3 runs, expect legendary spears and visible class variety)
is the remaining launch gate. See docs/WILL_TEST_GUIDE.md and the BACKLOG gate record.

**STATUS 2026-08-10 (ship lane, tag `build75-dev`): BUILT + FULLY GATED + LIVE ON DEV.** arz
`3fb1f3ce8889e27de2491ab12814547d` (55,539,324 B, 51,231 records), det-2x identical across two
independent builds, 54-module registry order `0c76e6652069`. Record-diff vs the live baseline
`9c190b99` = ADDED 27 / REMOVED 0 / MODIFIED 48 with ZERO unexplained rows. All gates green:
`chest_loot_breadth` + `polis_vault` T1-T7 + `gate_chest_loot_breadth` + `gate_relic_difficulty_tiers`
(33 branches, 0 leaks) + 3 negtests + `validate_tags` PASS + `run_contracts` 0 P0 / 0 P1 / 4492 P2.
Coupling proof holds: `Levels.arc 78a3e263` / `Text.arc a9fed7ba` / `Quests.arc 6b25f8dd` byte-unchanged,
so the change is arz-only and reaches the TESTHUB cage and canonical/Steam together, exactly as this
ruling requires. Deployed to `SoulvizierClassicDEV` md5-verified with TQ closed (nothing killed).
The Steam half rides the concurrent b63 SILENT-WARDEN package, which already stages this arz.
Still NOT PROVEN IN-GAME - Will's cage check remains the launch gate.
## R-200 [2026-08-10] IMPLEMENTED (branch `fix/boar-snatcher-orb`, module `tools/patches/red_uber_orbs.py`) - every RED UBER drops the mystical orb

**Will, VERBATIM (2026-08-10):**

> "boar snatcher legendary spider should drop a mystical orb like the other red uber monsters"

(Number chosen as R-200 rather than R-180/R-190 because two other lanes started the SAME day - the
chest-loot-breadth wave and the Sparta-warden-dialog wave - and would naturally take the next tens.
Renumber at integration if it collides; the ruling text is what binds.)

**"MYSTICAL ORB" IS LITERAL, NOT A PARAPHRASE.** Every `genericbossorb_0N` chest in this mod carries
`description = tagEndChest02`, and the base game's `Text_EN.arc` defines `tagEndChest02 = Mystical Orb`
(siblings: `xtagChest17 = Hades' Essence`, `xtagChest18 = Charon's Essence`, `tagEndChest01 = Typhon's
Essence`). b53 settled that the generic orb, NOT a bespoke "X's Essence", is the mod convention (R-47),
and `docs/reports/b53_orb_essence.md` predicted this exact sentence.

**THE BOAR SNATCHER, IDENTIFIED FROM THE BYTES.** Display tag `tagAEMonsterName06` = "Boar Snatcher";
records `records\creature\monster\spider\um_boareater_{40,42,44}.dbr` (charLevel 15/17/19),
`Monster.tpl`, `monsterClassification = Boss` (RED), placed in `Greece/Area003/PineForest04` +
`Greece/MiniDungeons/SpartaOptCave03` in BASE and in our deployed map. The RECORD is named "boareater"
while the DISPLAY name is "Boar Snatcher", which is why a filename search finds nothing - resolve
through the tag, never the filename. All three carried NO `treasureProxyName` field at all.

**WHY NO GATE CAUGHT IT - TWO HOLES, BOTH CLOSED.**
1. There was NO orb-breadth gate at all. Every orb wiring in the repo is a hand-typed target list
   (`_BOSS_ORB_TARGETS`, `general_guardians`, `polis_vault`, `diadochi`, `four_generals`,
   `devourer_kit`, `leinth_wave`), and the only orb GATES were `uber_apex_orb.verify()` (the 8-record
   Toxeus roster + Leinth) and `general_guardians`' own. R-99 already learned in this exact domain
   that a typed list is how the Endless Hunt shipped orb-less for two waves.
2. **THE HOLE THAT ACTUALLY HID IT:** every roster derivation in this repo runs over the MOD db only,
   but the runtime resolution universe is mod UNION BASE. The Boar Snatcher is a base-only record, so
   it was invisible to every derivation and would have survived a naively written class gate too.
   `red_uber_orbs` derives its roster over the UNION, which is what actually closes this.

**THE CLASS (derived, never typed):** `Monster.tpl` + `monsterClassification == 'Boss'` (the repo's own
word for RED - see `_amend_boss_loot_orbs`, "Give red (Boss) custom bosses the base-game on-death
chest-orb the red act bosses drop") AND either (a) basename starts `um_` (the uber namespace
`uber_quest_drops` swept for R-101) or (b) it wears a `tagSVCMonster*` tag (our own ubers under a donor
filename). MEASURED: 55 red ubers, 41 already orbed, 14 missing.

**WIRED (8), tier = the minimum-distance measured consumer band:** Boar Snatcher x3 (15/17/19) ->
orb01; Neferkha (32) -> orb02, and the orb rides the UBER because his terminal `as_ghosthero_32` is
SHARED with five roaming mummy heroes; `um_frost_36` (36) -> orb02; `um_phagia_44` (44) -> orb03, whose
lower twin `um_phagia_34` had been on orb02 all along; Aithon the Ember-Crowned (55) -> orb04, the
rule-(b) catch; Kravmoloch (74) -> orb04 and deliberately NOT orb05, which R-99 reserves for the Toxeus
roster.

**EXEMPT (6), each condition re-proven mechanically so it cannot rot:** the 4 transform SHELLS whose
TERMINAL form carries the orb (Charon, Mnemophage - the `_MN_ORB_SHELL` "shell: stay orb-less"
precedent - Polis Gaoler, Tantalus), and the 2 `dropItems = 0` soul-summon copies of the Bloodcrow
under `records\item\equipmentring\soul\test\`.

**SCOPE BOUNDARY, STATED SO NOBODY WIDENS IT BY ACCIDENT.** 458 Boss-class records exist in the runtime
universe and 346 carry no orb; this ruling does NOT touch the other 333 (base act/quest bosses that pay
out through level-placed quest chests). Registered as `BL-R200-DEBT-1`.

**GATE:** *every RED UBER carries a `treasureProxyName` that RESOLVES in mod UNION base, or is in a
pinned EXEMPT set whose stated condition still holds.* Plus: the 8 pins land exactly, the Boar Snatcher
override is present in the MOD db and still reads Boss/"Boar Snatcher", every pinned tier's
3-difficulty chain resolves, each pin is still the minimum-distance tier, and nothing this module wires
touches orb05. Negative test `py tools/patches/red_uber_orbs.py --negtest <arz>`: 9/9 as designed,
including N3 (a NEW red uber with no orb = this very regression) and N8 (a Hero-rank `um_` record with
no orb stays GREEN - the gate is red-only and does not invent policy for the 412 Hero ubers).

**NOT PROVEN IN-GAME.** Will's kill of the Boar Snatcher (Silk Road / PineForest04 or SpartaOptCave03)
and seeing the orb drop is the remaining launch gate - registered as `BL-R200-DEBT-2`.

---

## R-170 FOLLOW-UP - SHIP RECORD [2026-08-10] b63 SHIPPED: DEV + **STEAM** (tag `build75-ship`)

STATUS: IMPLEMENTED -> **SHIPPED**. Merged to `main` at `824ed0c`. DEV carries the coupled pair
(`Levels.arc` TESTHUB `7a7ca9ac`, `Quests.arc` `607ec99c`) with arz/Text/Creatures proven
byte-unchanged. Workshop item 3759792705 updated and confirmed (`Committing update...Success.`),
shipping canonical `Levels.arc` `6784cf0f` + `Quests.arc` `607ec99c` alongside the chest-loot wave's
arz `3fb1f3ce`. **The entrance was unreachable for subscribers from 2026-08-06 to 2026-08-10.**

R-170 AND ITS AMENDMENT REMAIN THE DESIGN LAW, UNCHANGED AND NOW MACHINE-ENFORCED. The Warden still
offers EXACTLY ONE option, `tagSVCEnterSpartaCrypt`, landing `(-5596,-2,-1410)`, and NO Helos return.
Nothing about Will's descend-only decision was traded away to fix the muteness: only the generator
that emits the route changed, plus 6 units of position. `gate_travel_npc_invariants` T5c now asserts
that menu shape directly, and `_assert_enter_offers_are_second_entries()` fails the BUILD if an
enter-offer is ever again an NPC's sole menu source. Never re-add `tagSVCAreaReturnToHelos` to him.

ONE CORRECTION TO THE b63 RCA, recorded so the next agent does not inherit a wrong number. The RCA
prescribed a 4.0u minimum for the new `G-NPC-LANDING-SEP` check ("matching the existing collider
threshold"). Measurement rejected that: 4.0u is the CONTAINER minimum, and applying it here would
have failed roughly 20 boat-NPC/landing pairs that Will demonstrably travels through every session
(the tightest proven-working pair is 1.12u at the Helos plaza). The shipped threshold is **1.0u**,
which separates the actual defect (0.00u, coincident placement) from every confirmed-working case,
and the gate PRINTS the tightest margin on each run (currently +0.12u) so drift is visible instead of
silent. A gate calibrated to a round number that reds working content is a gate that gets switched
off.

WHAT IS STILL OWED, AND IT IS THE SAME DEBT THAT CAUSED THIS RULING. NOT PROVEN IN-GAME. The
2026-08-06 amendment closed with "Will's walk is the remaining launch gate" and the walk failed; this
ship closes on exactly the same standing, from bytes and gates alone. Will tests on **Legendary or
Epic** (his Normal `.que` is the stale pre-PR-5 shape). If the Warden is still silent, the single
diagnostic question is **did he walk in or teleport in** - that answer selects the already-identified
fallback, a `GridEntrance` door (the proven build24/25 Knossos->Uber / Sparta L2 mechanism) instead of
a boat NPC.

---

## Soul tier naming (decade 200-209 continued; opened 2026-08-10, branch `fix/soul-tier-naming`)

## R-201 [2026-08-10] IMPLEMENTED (branch `fix/soul-tier-naming`) - the Epic and Legendary tiers of OUR souls must be NAMED Epic and Legendary

**Will, VERBATIM (2026-08-10):**

> "the new souls we made dont have named variants, i.e., the epic, legendary and normal versions of
> the soul of the gaolor are all named the same where as the rest of the souls are named things like
> Soul of the Gaolor, Epic Soul of the gaolor, legendary soul of the gaolor"

(R-201 follows R-200, which was minted the same day by the `fix/boar-snatcher-orb` lane. The ruling
text is what binds; renumber at integration if it ever collides.)

**HE DESCRIBED THE MECHANISM EXACTLY, AND IT WAS ALREADY IN THE DATA.** A soul does NOT carry three
name strings. Its three tier records SHARE ONE `itemNameTag` - the evocative base name - and
differentiate through **`itemQualityTag`**, which the engine renders as a PREFIX in front of the item
name. Measured on the shipped `build76` arz (`16994072`), **641 of the 739 multi-tier soul families -
every single SV-original family, zero exceptions** - carry:

| tier record | `itemQualityTag` | what the player reads |
|---|---|---|
| `<base>_soul_n.dbr` | ABSENT | Soul of the Gaoler |
| `<base>_soul_e.dbr` | `tagSoulEpic` (`{^F}Epic`) | **Epic** Soul of the Gaoler |
| `<base>_soul_l.dbr` | `tagSoulLegendary` (`{^F}Legendary`) | **Legendary** Soul of the Gaoler |

**THE DEFECT, EXHAUSTIVELY SCOPED.** The 98 non-compliant families are ALL of, and ONLY, the OURS-path
roster under `records\item\equipmentring\soul\svc_uber\` - the Gaoler is one of them. Every one carried
`itemQualityTag` on NO tier, so all three rendered the identical string. The cause is structural, not a
per-soul slip: every generator (`create_uber_souls.design_soul`, `_apply_dewired_hero_handcraft`, and
the hand-authored boss souls) writes ONE field set to all three tiers and none of them ever emitted the
field. It would have recurred on the next soul we added.

**NO EXEMPTION LIST, BY CONSTRUCTION - AND THAT IS THE POINT.** The tier word is a PREFIX in FRONT of
the shared name tag, so law #2 (SV originals untouchable) and the evocative hand-designed names
(`_HAND_DESIGNED_SOUL_TAGS`) are satisfied WITHOUT touching a single string: "Soul of the Gaoler" stays
verbatim on normal and simply gains "Epic "/"Legendary " above it, which is precisely what Will
described. The fix is ADD-ONLY - it never rewrites an authored `itemQualityTag` - so an SV original
cannot be mutated by it even in principle. No new Text tag is authored: `tagSoulEpic` and
`tagSoulLegendary` are already in the shipped `Text.arc` from the SV text pass.

**FIX.** `apply_svc_patches._apply_soul_tier_naming(db)`, run inside `run_registry_gates` immediately
after the F6 naming standard - i.e. AFTER the whole patches registry - so it also covers souls a future
content module adds. 196 records changed (98 families x Epic + Legendary), 1 field each.

**GATE (fail-loud, no whitelist): `_verify_soul_tier_naming(db, tags)`.**
- **C1 CONVENTION** - every canonical soul tier record's `itemQualityTag` matches its tier.
- **C2 DISTINCTNESS** - Will's bug stated as an invariant: within one soul family, no two tiers may
  render the same `(quality, name)` pair.
Scope is the canonical `<base>_soul_{n,e,l}` family plus SV's `<base>_soul` normal spelling. amgoz's
`(... conflicted copy ...)` junk, the `soultemplate*` authoring stubs, SV's `_soul_n_` double-authored
typo copies and the loot-table records that share the soul folders are out of scope by construction
(no `itemNameTag`, or no tier family) - deliberately, so the gate reports defects and not noise.
`validate_tags` gained `itemQualityTag` in `TAG_FIELDS` plus a `REQUIRED_TAGS` backstop, so the two
prefix tags can never silently vanish from `Text.arc` and leave "tagSoulEpic" rendering in-game.

**NEGATIVE-TESTED 4 ways** (`scratchpad/negtest_r201.py`): gate RED on the pre-fix build76 arz (196
records / 98 families, ZERO false positives on SV originals); gate RED when ONE shipped record's tag is
stripped; normalizer idempotently restores it and the gate goes GREEN; gate RED when the Legendary tier
is given the Epic tag. The gate is not vacuous.

**NOT PROVEN IN-GAME.** The one-line check is Will's: pick up the Gaoler soul on Epic and on Legendary
and read the item name.

---

## Act cap / DLC surfaces (new section; decade 210-219, opened 2026-08-10, branch `fix/portal-atlantis-cap`)

## R-210 [2026-08-10] IMPLEMENTED (branch `fix/portal-atlantis-cap`) - no DLC act may appear on the portal page

**VERBATIM (Will, 2026-08-10):** "in the portal page i see atlantis which should be disabled in this
mod"

This is the act-selection-UI half of the standing IMMORTAL-THRONE CAP ruling (Will, 2026-07-10:
"lets not make atlantis or anything past immortal throne reachable for now and we will fine tune
immortal throne then if we want to add in the other areas later then we can"). It is read as the
general rule, not one tab: **no DLC act (Ragnarok / Atlantis / Eternal Embers) may be offered on any
act-selection surface.**

**LIST SOURCE.** The portal window's page list is ONE record,
`records\ingameui\teleportmap\teleportmap.dbr` (`WorldlMapWindow.tpl`); each act page is a
`<Page>Button` / `<Page>MapImage` / `<Page>ZoneList` triple. Base TQAE carries seven pages. SV 0.98i
ships an IT-era copy with only the four base pages, but `strip_ui_overrides()` deletes every
`records\ingameui\` record that is not a mastery tree, so the mod shipped NO override and the record
resolved from the BASE `.arz`. The quest log's act tabs
(`records\ingameui\player quests\questwindow.dbr` buttons/maps 5/6/7) fell through the same hole.

**LAYER.** Mod `.arz` record override, the A5 pattern (a `.dbr`'s identity IS its record path, so
the mod arz wins per path; the A5 inert-fix trap is specific to archive-hosted quest files keyed by
md5 of the registry path). The base records are imported byte-faithfully and exactly the DLC fields
deleted, so the four Immortal-Throne-era pages and AE's layout are preserved. The cap runs AFTER
`strip_ui_overrides()` and asserts that ordering; a fail-loud golden gate
(`tools/gate_dlc_act_ui_cap.py`, negative-tested) proves on the WRITTEN `.arz` that the rendered
portal page list is exactly Greece / Egypt / Orient / Immortal Throne.

**SEVERITY CORRECTION, recorded so nobody reads this as cosmetic.** Atlantis is not merely a dead
list entry: `XPack3/Quests/x3mq_AtlantisAdventure.qst` is registered at index 211 of the map's
255-entry QUESTS window, and BOTH `x3mq_marinos_rhodes_spawner.dbr` and `rhodes_boatmantogadir.dbr`
are placed in `Rhodes_CityFinal_01` on the mandatory spine. An Atlantis-DLC owner can still SAIL to
Atlantis. That leak stays OPEN as `BL-PORTALCAP-DEBT-1`; it needs its own lane and Will's sign-off on
the layer. See `docs/PORTAL_PAGE_DLC_CAP.md`.

**AMENDMENT 2026-08-10:** the sail leak is now CLOSED by **R-211** (branch `fix/atlantis-voyage-cap`).
`BL-PORTALCAP-DEBT-1` is RESOLVED.

---

## R-211 [2026-08-10] IMPLEMENTED (branch `fix/atlantis-voyage-cap`) - no DLC act may be REACHABLE, not merely un-listed

**VERBATIM (Will, 2026-08-10, on the R-210 report):** Atlantis is disabled in this mod. R-210 removed
the Atlantis PAGE and left the SHIP; this lane closes the last access path.

R-211 is the travel half of the same standing IMMORTAL-THRONE CAP ruling (Will, 2026-07-10: "lets not
make atlantis or anything past immortal throne reachable for now and we will fine tune immortal
throne then if we want to add in the other areas later then we can"). Read as the general rule:
**a DLC act must be UNREACHABLE, and an act-selection surface being clean is not the same thing as
the act being unreachable.** Every future cap lane enumerates transit routes, not list entries.

**WHY IT SURVIVED THE OTHER THREE CAPS.** Both A5 caps are POST-HADES transitions and R-210 was UI
only. **Atlantis branches from RHODES, mid-Immortal-Throne**, on the mandatory Olympus -> Rhodes ->
Hades spine, so no prior cap ever touched it.

**THE ROUTE.** `x3mq_Marinos_Rhodes` has ZERO static placements in our `world01.map` and enters the
world ONLY through the `DLCActorSpawner` `x3mq_marinos_rhodes_spawner.dbr` (placed once, in
`Rhodes_CityFinal_01`). Talking to him fires `x3mq_AtlantisAdventure.qst` (map QUESTS idx 211, inside
the 255-entry load window) -> `Action_BoatDialog(rhodes_boatmantogadir)`, the only transition from the
reachable Immortal-Throne world into the XPack3 act; the chain ends at
`Action_BoatDialog(gadir_boatmantoatlantis)`. `XPack3TartarusPortal.qst` (idx 205) unlocks the
Tartarus act portal from Gadir or Corinth.

**LAYER (and why the quest layer is unavailable).** All 20 XPack3 quests are registered under the
`XPack3/Quests/...` namespace, so the A5 md5-full-registry-path trap applies verbatim and a mod quest
at the plain `Quests.arc` root would ship inert. So: DB-record cap, the A5 pattern (a `.dbr`'s
identity IS its record path; the mod `.arz` overrides the base `.arz` per path, runtime-confirmed).
**arz-only: no map rebuild, no `Quests.arc` change, so neither deploy coupling is engaged.**

**SIX OVERRIDES, each on a shape the base game itself ships.** Delete `actorToSpawn` on both
`DLCActorSpawner` records (the template declares it `file_dbr` / `defaultValue ""`, so absence IS the
declared default); hide the two boundary boat captains with `startVisible=0` + `IncludeInMap=0`
(`startVisible=0` ships on 604 retail records; `IncludeInMap=0` is the A5 minimap-ghost lesson; and
NO quest in ANY of the five base quest archives fires `Action_ShowNpc` at either captain, so nothing
can undo it); and give both Tartarus act portals the A5 AND-unsatisfiable DLC gate. `dlcRequirement`
is deliberately left alone (a picklist; deleting it could read as "no DLC required"). The Malta /
Hesperides captains and every RETURN boatman are deliberately untouched - interior to an act that is
now unreachable, and the return boats are the anti-strand path.

**GATE.** `tools/gate_atlantis_voyage_cap.py`, fail-loud, negative-tested (4 planted defects, one of
them a COLLATERAL xpack3 override, so the gate fails on over-reach as well as under-reach), wired
in-memory and on the WRITTEN `.arz`. Its V5 check proves the DERIVED list of resolvable
Atlantis-transit routes is EMPTY. **NOT PROVEN IN-GAME** (`BL-VOYAGECAP-DEBT-1`): the one-line check
needs an Atlantis-DLC owner - after Typhon, walk Rhodes and find no Marinos and no captain offering
Gadir. See `docs/ATLANTIS_VOYAGE_CAP.md`.
---

## R-181 [2026-08-10] IMPLEMENTED (branch `fix/armor-loot-breadth`, module `tools/patches/armor_loot_breadth.py`) - armour must drop like armour, and no class may run away with the run

**WILL, VERBATIM (2026-08-10), TWO reports in one sitting:**

> "also what about the armor? i am not really seeing armor drops like shields, chest plates,
> helmets, etc."

> "you overcorrected, that run 4 scorpions tail spears dropped"

**BOTH REPORTS ARE RATE REPORTS, AND R-180 COULD NOT SEE EITHER.** R-180 asked and answered a
REACHABILITY question - can a chest pay a legendary spear at all. Measured on the SHIPPED build76
arz `16994072`: every one of the 51 mod chest tables already reaches all five worn slots, ZERO have
an empty slot, and R-180's own gate was GREEN. Nothing was unreachable. What was wrong was HOW OFTEN.
Per open of the cage's chest_01 the shipped build pays **11.56 legendary weapons against 0.17 helms /
0.26 arms / 0.68 torso / 0.29 legs / 1.25 shields**. Over the six-chest cage run: **58.5 weapons to
12.4 armour pieces, a 4.73:1 ratio, with the helm at 1.6% of the run's legendary mass.** Will is not
misreading a wide pool; he is correctly reading a starving one. A gate that counts distinct reachable
items is blind to this by construction, which is why R-181 adds a second, orthogonal gate rather than
tightening the first.

**THE FOUR SCORPION'S TAILS, ARITHMETICALLY.** Not a within-class weighting bug - the cage's spear
weights were already near-uniform (the top spear carried 1.33x its class's uniform share). It was
VOLUME x CLASS SHARE:

1. `loot3Chance = 100` fires EVERY spawn iteration (S = 12.48 on chest_01, S = 14.40 on chest_03) and
   every member of it is a weapon or relic table, so a cage run pays roughly 75 guaranteed weapons.
2. SPEAR took **24.0%** of the run's legendary gear (even across the 11 gear slots is 9.1%) through
   three stacked paths: the martial theme's direct spear member at 30% of the guaranteed slot, the
   aggregate weapon master naming `spear_l01` again, and `all_l0N` naming it a third time. Meanwhile
   `unique_1h_*01` pays THREE classes (axe/mace/sword) from ONE member slot and carried a single
   spear's weight, so each 1H class got a THIRD of a spear's mass.
3. 16.99 spear drops per run over 22 distinct spears gives **P(some spear lands 4x in one run) =
   27.0%**, and P(that spear is specifically Scorpion's Tail) = 2.07%. Will's run was the ordinary
   case, not bad luck. (`u_e_scorpion'stail` is item 11 of `spear_l01`, Legendary-classified, level
   50.) Modelled under the assumption most FAVOURABLE to the shipped build - `LootItemTable_DynWeight`
   treated as uniform over its `itemNames` - so 27.0% is a LOWER bound on the real skew.

**IMPLEMENTED (arz-only; no Levels / Text / Quests change, 0 new tags, so it reaches the TESTHUB cage
and canonical/Steam together exactly as R-180 does):**

- `tools/svc_loot_distribution.py` (NEW) is the MODEL: E[drops of item x per open] = S x SUM_G
  (chance_G/100 x P(x | group G)). The engine reading is MEASURED, not assumed - 167 of the 296
  base-game FixedItemLoot tables have group chances summing past 100 (up to 226.2 on
  `hermit mage chest_*`), which is impossible if the six groups were mutually exclusive.
- `tools/svc_armor_breadth.py` (NEW) is the WRITE contract: the 3 aggregate armour masters
  `svc_unique_armor_{n,e,l}01` (all five worn slots at equal weight, R-180's own machinery reused),
  every armour row lifted to the weapon row's 40% (shipped 33 / 31 / 30), unique-armour members
  raised to 850 against roughly 1700 of static junk, the armour master into the first free
  armour-row member slot at 1700, and `unique_1h_*01` re-weighted to 3x its single-class siblings.
- `tools/svc_loot_breadth.py` (EDIT): the aggregate weapon master now weights per CLASS, not per
  member. Theme class-biases softened - each theme keeps its shipped weapon:relic:armour split TO THE
  PERCENT (ENFORCED, not merely intended: the armour sweep skips any group at 100% chance, because
  that row belongs to the theme - see amendment finding 2), and `warden` now pays all five worn slots
  instead of only shield + torso.
- `tools/patches/armor_loot_breadth.py` (NEW, registered immediately after `chest_loot_breadth`)
  sweeps all 51 mod chests + the 3 DRX donors, so the cage, every boss hoard, the guard-pair hoards
  and the blood-cave mega chest get the identical treatment from one edit.

**A SHIELD'S `Class` IS `WeaponArmor_Shield`, NOT `ArmorProtective_*`.** Any audit written as
`startswith('Armor')` reports zero shields; any weapon audit written as `startswith('Weapon')` counts
every shield as a weapon. Both errors erase the slot Will named FIRST.
`svc_loot_distribution.GEAR_SLOTS` is the single authority and nothing re-derives it. (The arm slot is
likewise two classes - `ArmorProtective_Forearm` and `ArmorJewelry_Bracelet`.)

**NON-REDUCTION (R-100 #17 / Will 2026-08-08 / R-180), re-proven per edit:** numSpawn equations
untouched, no member removed, no group chance lowered, no member weight lowered, guaranteed slot still
100%, the Legendary chain still lands on `polisvault_0N`. Expected drops per cage run RISE from 70.8
to 109.5. What changes inside an armour row is its COMPOSITION - legendary up, static junk down as a
fraction - which is the ask, because "i am not really seeing armor drops" is a report about
legendaries on a Legendary farm, not about item count.

**MEASURED (dry run of the real modules against the shipped arz), cage run before -> after:**

Expected legendary drops per six-chest run (3x chest_01 + 3x chest_03, each drawing a themed variant
at the pool's 50/25/25):

| slot | shipped | R-181 | | slot | shipped | R-181 |
|---|---|---|---|---|---|---|
| axe | 5.28 (7.5%) | 9.61 (8.8%) | | helm | 1.11 (1.6%) | 9.51 (8.7%) |
| mace/club | 6.27 (8.9%) | 11.22 (10.2%) | | arms | 1.70 (2.4%) | 8.56 (7.8%) |
| sword | 5.43 (7.7%) | 9.73 (8.9%) | | torso | 2.63 (3.7%) | 10.00 (9.1%) |
| **SPEAR** | **16.99 (24.0%)** | **10.70 (9.8%)** | | legs | 1.89 (2.7%) | 9.54 (8.7%) |
| bow | 12.12 (17.1%) | 9.25 (8.5%) | | shield | 5.03 (7.1%) | 11.79 (10.8%) |
| staff | 12.37 (17.5%) | 9.55 (8.7%) | | **weapon:armour** | **4.73:1** | **1.22:1** |

Even across the 11 gear classes is 9.1%. **After the wave every one of the eleven sits between 7.8%
and 10.8%**; before, the spread ran from 1.6% to 24.0%. Armour pieces per run 12.4 -> 49.4. Thinnest
worn slot on ANY of the 42 surfaces, per open: 0.04 -> 0.62.

**THE 4x PROBABILITIES, AND AN HONEST READING OF THEM.** Computed two independent ways that agree -
analytically (Poisson over per-item lambdas) and by Monte Carlo over the real sampling process (4000
simulated runs; per-chest variant draw, integer spawn-iteration count, each loot group rolled
independently):

| event, per six-chest cage run | shipped | R-181 | |
|---|---|---|---|
| P(SOME legendary spear lands 4x) | 27.0% | **6.3%** | 4.3x rarer |
| P(four Scorpion's Tails specifically) | 2.07% | **0.45%** | 4.6x rarer |
| P(ANY single legendary gear item lands 4x) | 47.3% | **39.7%** | barely moves |

**The third row is why this ruling does NOT say "negligible".** Will's report was "four copies of the
SAME legendary spear", and that specific event is now roughly 1 run in 16 instead of 1 in 4. But
seeing four copies of SOMETHING is still better than a coin flip, because total legendary gear per run
RISES 70.8 -> 109.5 while `numSpawn` is deliberately untouched under the non-reduction law. The honest
sentence to Will is "much rarer for a spear, still routine for something", not "fixed". **numSpawn is
the volume lever, and lowering it is a WILL DECISION, logged as `BL-R181-DEBT-5` rather than taken
quietly here** - it would reduce drops per open, which is exactly what non-reduction forbids without
his say-so.

Item pools are UNCHANGED (270 distinct gear items reachable from the cage) - this ruling moves RATES,
R-180 moved REACH.

**GATE (law 4, no new surface without a gate):** `tools/gate_loot_distribution.py` + the in-build
`armor_loot_breadth.verify()`, one shared implementation. **42 surfaces over 54 tables** - the cage's
three themed variants at their 50/25/25 pool weights on each difficulty, every boss and guard-pair
hoard, the three `svc_uberorb_apex_*` orb tables, and the blood-cave mega chest's three DRX donors.
Checks: D1/D2 class share caps, D3 no starving class, D4 no item over 5.8x its class's uniform share,
D5 no item over 3.0% of the surface, D6 weapon:armour at most 1.85:1 and D6b at least 0.24:1 (fixing
armour must not quietly bury weapons), D7 every worn slot at least 0.52 pieces per open, D8/D9 the
same evenness measured INSIDE the weapon side and INSIDE the armour side. Every threshold is derived
from a `--calibrate` run against BOTH the shipped arz and the fix (`--apply`), and each REDS the
shipped state - D1 by 23%, D2 37%, D3 27%, D5 94%, D6 289%, D7 13x, D8 43%, D9 22% - while clearing
the fix by 13-40%. The one that does not red the shipped state (D4) is labelled a regression guard in
the source rather than dressed up as a fix.

**`apply()` ALSO ASSERTS WRITE SET == AUDIT SET** and fails the build if any table this wave writes is
absent from the gate's surface set. That assertion exists because both halves of it failed once: see
the amendment below.

**D8/D9 EXIST BECAUSE A PLANTED NEGATIVE CAME BACK GREEN.** Once armour parity lands, armour carries
half the gear mass, so re-planting the SHIPPED spear over-weighting reads as only about 21% of total
gear and slides under D1/D2. The skew Will reported lives inside the weapon side and has to be
measured in the weapon side's own denominator. Negatives:
`py tools/debug/negtest_armor_breadth.py <arz>` - **7** planted defects all RED, plus two positive
controls, one of which proves the DELIBERATE warden armour bias stays GREEN (a gate that cannot tell
a designed theme from a defect is a gate that gets switched off - the b63 1.0u lesson).

**SCOPE BOUNDARIES, STATED SO NOBODY WIDENS THEM BY ACCIDENT.**

1. **There is NO owner-based exclusion.** Every mod-owned gear chest is in scope, including the three
   `svc_uberorb_apex_{n,e,l}01c` tables. An earlier draft of this ruling deferred them to the
   concurrent b79 `fix/orb-loot-breadth` lane; that was wrong and is corrected in the amendment below.
2. General MONSTER armour drops are MEASURED AND REPORTED, NOT CHANGED. Re-measured over all 51,236
   records of the build78 arz: `chanceToEquipHead` / `Forearm` / `Torso` / `LowerBody` exists as a
   field on ~6,530 records and is NONZERO on **1503 / 1733 / 1846 / 1423** of them, of which only
   **12 / 12 / 14 / 12 are mod-owned** - 0.69% to 0.84% of the population. Monster armour dropping is
   BASE-GAME-GOVERNED in this mod, inherited wholesale by the merge. `chanceToEquipShield` does not
   exist as a field on ANY of the 51,236 records, so no monster in this DB can drop a shield off its
   body at all: shields come only from chests and merchants. Whether to touch base monster loot is a
   Will decision, not a silent scope widening (`BL-R181-DEBT-2`).
3. Two residual POOL gaps, reported not fixed: the cage reaches 19 of 41 legendary axes (46%) and 33
   of 71 legendary torsos (46%), against 75-92% for every other slot (`BL-R181-DEBT-3`).
4. `WeaponHunting_RangedOneHand` is bucketed with `bow`, which the concurrent
   `fix/craft-thrown-breadth` lane will silently invalidate at merge (`BL-R181-DEBT-4`).
5. `numSpawn` - the drop-VOLUME lever - is untouched, and lowering it is a Will decision
   (`BL-R181-DEBT-5`).
6. **The 15 loot tables R-220/b79 writes (`uberorb_default_*`, `boss_charon_*01b`) are outside this
   module's `\svc\` ownership rule and R-220 widens only their weapon row, so armour on them is
   owned by NOBODY - and measured with both waves applied, all fifteen starve it: weapon:armour
   2.0:1 to 4.1:1, thinnest worn slot 0.01-0.04 per open against the D7 floor of 0.52.** Reported,
   not fixed: one lane per problem, and b79 has already merged (`BL-R181-DEBT-7`). The fix is
   mechanical - identical donor shape, one `widen_armor_rows` call per table plus `all_surfaces()`.
   **-> CLOSED 2026-08-11 by the R-181 SECOND AMENDMENT below** (branch `fix/orb-armor-rows`, module
   `tools/patches/orb_armor_rows.py`). Note for the record: "2.0:1 to 4.1:1" understated it. Measured
   on the shipped build80 arz `c5851a1a` the fifteen ran **3.45:1 to 8.38:1** with a thinnest worn
   slot of **0.007**, because the reading above was taken before b79's own weapon-row raise landed.

**NOT PROVEN IN-GAME.** The build, DEV deploy and Steam ship are the orchestrator's. Will's check -
kill Alkyoneus, open all six cage chests across a couple of runs, expect visible helms, chest plates,
greaves and shields alongside weapons and no run dominated by one spear - is the remaining launch
gate.

---

### R-181 AMENDMENT [2026-08-10] - what the independent vet found, and the three laws it produced

The first round of R-181 was vetted independently before build and **six findings came back, one of
them a live-surface hole of exactly the kind this ruling exists to close.** Recorded here verbatim in
substance, because the pattern matters more than the patch.

**1. THREE LIVE SURFACES WERE STARVING EVERY WORN SLOT, AND THE GATE COULD NOT SEE THEM (high).**
`svc_armor_breadth.in_scope()` excluded `svc_uberorb_apex_{n,e,l}01c` on the stated grounds that the
concurrent b79 lane "owns armour slots for orb tables". **That claim was false**, proven two ways:
applying b79's wave to the same arz changes 15 records (`uberorb_default_*`, `boss_charon_*01b`, xpack
`uberorb_default_*01c`) and touches none of the three apex tables; and b79's own module docstring says
so in writing - the apex tables "are already widened by the time this module runs and are therefore a
no-op here", and what it widens is "only the CLASSES the weapon row can pay". Nobody was widening
armour on them. Worse, the exclusion also removed them from `all_surfaces()`, so the fail-loud gate
never audited them either - **the exact R-180 failure mode this wave exists to end.** These are LIVE:
they back `genericboss05_chest_{normal,epic,legendary}` (R-200's red-uber Mystical Orb chests, shipped
to Steam the same day) and `bosschest_leinth_{01,02,03}`. Measured on the shipped build78 arz,
`svc_uberorb_apex_l01c` paid **0.07 helms / 0.07 arms / 0.08 torso / 0.07 legs / 0.17 shields against
0.98 weapons per open**. After: **1.17 / 1.05 / 1.19 / 1.17 / 1.39**.

> **LAW: a lane boundary is only real if the other lane's CODE says so.** Owner-based exclusions are
> gone from this module entirely, and `apply()` now asserts WRITE SET == AUDIT SET and fails the build
> on any divergence. "Another lane owns it" is not a fact; it is a claim to verify.

**2. THE SWEEP WAS REWRITING THE GUARANTEED THEME SLOT (medium).** `armor_groups()` detected armour
rows from member paths alone and scanned groups 1-6, so it also matched the 100%-chance slot that
`THEMES` owns. On `polisvault_01_{n,e,l}c` - the WARDEN theme - it raised a documented 50% weapon /
50% armour split to **12.8 / 87.2**, which made this ruling's own words ("each theme keeps its shipped
weapon:relic:armour split TO THE PERCENT") false in four separate documents. Fixed: `armor_groups()`
now skips any group at chance >= 100. **Read off the chance, not hardcoded to group 3** - measured,
the guaranteed slot is g3 on all 48 chest and hoard tables but **g4** on the apex tables, so the
obvious shortcut would have swept the theme slot and skipped a real 10% row. Warden ships its
documented 500/400/60/40 again. Separately, `martial` genuinely ships **700/200/600 of 1500**, not
700/200/100 of 1000 - `unique_1h` pays three classes from one member slot so it carries 3x its spear
sibling - and the source table now says so instead of claiming the weights are per-mille.

**3. THREE TABLES WERE WRITTEN BUT NEVER AUDITED (medium).** `apply()` sweeps `targets +
DRX_DONORS.values()`, but the donor names match neither half of the `\svc\` ownership rule, so
`loottable_hidden_bloodcave_{01,02,03}` sat in the write set and outside the audit set - while being
the most weapon-inverted surfaces in the mod (0.31 / 0.37 / 0.33 : 1) and the stated derivation of the
D6b floor. Added to `all_surfaces()`. Audit coverage 36 surfaces/48 tables -> **42/54**.

**4. THE FIX WAS OVER-CORRECTING IN THE MIRROR DIRECTION, AND ONLY THE NEWLY-VISIBLE SURFACES SHOWED
IT.** With the apex tables finally audited, D6b red them at **0.17:1 - an 85%-armour surface**. Root
cause is a real modelling error worth remembering: `ARMOR_UNIQUE_WEIGHT = 850` is an ABSOLUTE weight
derived from ONE donor family. The armour statics happen to be identical across families, so every
armour row lands at ~50% legendary everywhere - but the WEAPON row was left at whatever its donor
shipped, and the families differ hard (**DRX 1500 static / 54.5% legendary vs uberorb apex 2500 static
/ 29.6%**, because the apex donor carries `static_all` at 2000 and its unique members at 50 instead of
1000 and 200). Lifting armour to parity therefore lifted apex armour ~17x while its weapon side stayed
diluted. Fixed by expressing the weapon-row target as a **SHARE** (`WEAPON_ROW_LEGENDARY_SHARE = 0.50`)
and raising the aggregate master to reach it - **not** the named members, which was tried and rejected
because the apex weapon row names bow and staff directly but has no spear member and no free slot, so
raising named members would have paid bow/staff ~473 against SPEAR's 133 and rebuilt R-180's defect
while fixing another. The cage and blood-cave rows are already above the share and do not move.

> **LAW: a constant derived from one donor family is a bug waiting for the second family.** Express
> balance targets as SHARES of the row they govern, not as absolute weights.

**5. THRESHOLDS RE-DERIVED.** The original numbers were calibrated against the 36-surface set - which
excluded the six structurally hardest surfaces in the mod. Re-derived over all 42: D1 0.42 -> **0.35**
(tightened), D2 0.21 -> **0.25**, D3 0.016 -> **0.0145**, D6 1.65 -> **1.85**, D6b 0.25 -> **0.24**,
D7 0.60 -> **0.52**. Every one still reds the shipped defect by the margins listed above. This is
recorded as a movement, not quietly restated, because loosening a threshold to clear a red is exactly
how a gate dies.

**6. NEGATIVES 6 -> 7, AND ONE RETARGETED.** N5 ("every armour row switched off") went GREEN after fix
2 - correctly, because the warden theme's guaranteed slot legitimately pays armour, so killing its
chance rows starves nothing. It now plants on the martial variant, whose armour is entirely in chance
rows. **N7 is new**: it re-plants the over-correction from finding 4 on a live apex table, so
`MIN_WEAPON_ARMOUR_RATIO` is proven load-bearing rather than asserted.

**7. TWO RECORD CORRECTIONS.** The branch was based on `d77c3b9` (BUILD76-SHIP) and every number was
quoted against arz `16994072`; main had moved to `178ff4a` (build78). Everything was re-measured
against the current arz `f663846233295da3e8824bfa4d8925c8` and main is merged in. And the monster
census in the original ruling (1084 / 1497 / 1594 / 1234) reproduced from no population at all; the
correct figures are in scope boundary 2 above. The conclusion it supported was unaffected.

---

## Chest loot breadth (decade 180-189 CONTINUED; 2026-08-10, branch `fix/craft-thrown-breadth`)

> R-180 (above) was the WEAPON-CLASS half of the chest-breadth wave. R-184 to R-186 are the
> CRAFT-CHAIN half, from Will's follow-up the same day after reading `docs/CHEST_DROP_MATRIX.md`.
>
> ⚠️ **NUMBERING NOTE (collision avoided, not merely renamed).** This lane first minted these three
> as R-181/182/183. The concurrent `fix/armor-loot-breadth` lane (b80, the loot-balance/armour wave
> queued to ship AHEAD of this one) had already claimed **R-181** on its own branch for the armour
> parity + weapon-class weight rebalance, both in `docs/WILL_RULINGS.md` and in code comments in
> `tools/svc_loot_breadth.py`. On the `fix/debt-docs` LEDGER-HYGIENE precedent the INCUMBENT keeps
> the number, so this lane moved wholesale to **R-184 / R-185 / R-186**, leaving 182-183 free in case
> b80 mints more in the same decade. Nothing about any ruling's CONTENT changed. R-190..R-199 also
> remain free.

**VERBATIM (Will, 2026-08-10), the whole message, split into the three rulings below:**

> "i meant do the mythic formulas drop. they can drop in normal as well, but the legendary items
> should not drop in normal. All of the reagents need to be droppable somewhere in the game, ideally
> from chests since that is where people will look. if players farm legendary long enough, they
> should be able to find all the reagents without having to farm a specific area or a specific
> character (except for the monster unique droppable items like the green items that are needed to
> build some of the formulas...). Yes we should make the legendary thrown weapons droppable."

## R-184 [2026-08-10] IMPLEMENTED (`fix/craft-thrown-breadth`) - MYTHIC FORMULAS DROP ON EVERY DIFFICULTY, LEGENDARY ITEMS STILL DO NOT DROP ON NORMAL

**VERBATIM:** *"i meant do the mythic formulas drop. they can drop in normal as well, but the
legendary items should not drop in normal."*

This is an explicit, narrow EXEMPTION carved out of the R-100 #17 tier law: **formulas** are exempt,
**items** are not. It costs nothing to grant, because every supra formula record is
`itemClassification = Common` - no legendary GEAR moves at all.

**MEASURED CAUSE.** The 42 uber ("supra") craftables are built by 59 formula records, 42 of which sit
on `records\xpack\item\loottables\arcaneformulae\supra.dbr` and 41 on the rarer `supra_special.dbr`.
The base game wires those two pools into the EPIC and LEGENDARY act tables only:
`02_act{1..4}_arcaneformulae` = `LootMasterTable [ ..._table 98, supra 2 ]`, `03_act{1..4}` =
`[ ..._table 95, supra 5 ]`, and `03_act4_arcaneformulae_sp` for supra_special.
`01_act{1..4}_arcaneformulae` is a bare `LootItemTable_FixedWeight` of 25 base formulas with no supra
member at all - so a Normal-tier mod chest reached **0 of 42** uber formulas.

**FIX.** Both pools are added as ONE new member each of all four `01_act{1..4}_arcaneformulae`
tables, at weights computed against each table's own pre-existing total: `supra` at 1%,
`supra_special` at 0.5%, so mythic formulas are **rarer on Normal (1.5% combined) than the base game
already makes them on Epic (2%) and Legendary (5%)**. Base-game precedent for a
`LootItemTable_FixedWeight` naming a loot TABLE in a `lootNameN` slot: 56 shipped records do it
(e.g. `raremisc\01_rareunique_all.dbr` names `weapons\unique\sword_n01.dbr`). Nothing removed, no
weight lowered. Blast radius is deliberate and matches the ruling: those four tables are the Normal
formula source for 935 / 389 / 379 / 665 monster records as well as the chests, so mythic formulas
now drop on Normal **everywhere**, not only from mod chests.

**BOTH pools were required, and the gate is what proved it:** `artifact_mortoksskull_formula`
(Mortok's Skull) exists ONLY on `supra_special`, so wiring `supra` alone left exactly one of the 42
craftables formula-less on Normal and the F1 gate red. The same pair is what R-9 already treats as
"wherever any supra / uber weapons formulas have a chance to drop".

**MEASURED RESULT:** Normal craftable coverage **0/42 -> 42/42**; Epic and Legendary unchanged at
42/42. Legendary GEAR reachable from the Normal branch: **0 before, 0 after** (re-proven by
`svc_loot_breadth` B3 and by the new C2 rule).

## R-185 [2026-08-10] IMPLEMENTED (`fix/craft-thrown-breadth`) - EVERY REAGENT IS FINDABLE BY FARMING LEGENDARY; ONLY THE GREEN/MI ITEMS STAY MONSTER-SPECIFIC

**VERBATIM:** *"All of the reagents need to be droppable somewhere in the game, ideally from chests
since that is where people will look. if players farm legendary long enough, they should be able to
find all the reagents without having to farm a specific area or a specific character (except for the
monster unique droppable items like the green items that are needed to build some of the
formulas...)."*

**MEASURED CAUSE.** 78 distinct reagents feed the 42 craftables; **36 were unreachable from every
Legendary-tier chest pool**, in four very different groups:

| group | count | what it is |
|---|---:|---|
| MI / "green" (`itemClassification = Rare`) | 19 | Will's own exemption. Kept where they are. |
| ordinary base uniques | 8 | 3 torso, 3 amulet, 2 ring - they live only on the act-2/act-3 banded tables (`caster_l02`, `finger_e02`, the DRX `randomized\*` tables) that no chest pool names. |
| IT "divine artifacts" (`ItemArtifact`) | 6 | 0 of 292 artifacts were reachable from any mod chest at any difficulty. |
| **records the MOD does not carry** | 3 | `records\xpack2\item\equipmentweapons\1hranged\{u_l_08, u_e_06, mi_l_machae}.dbr` are **RAGNAROK (xpack2)** records absent from the mod's own arz. *(Precision, round 2: they DO exist in an installed base game if the player owns Ragnarok - 12,483 `xpack2` records in Will's 74,013-record install - but xpack2 ships only with that DLC and R-210 caps the playable arc at Immortal Throne with the Ragnarok act pages suppressed.)* **All four thrown craftables (Charon's Toll, Hati, The Last Word, Sanguine Orbit) named exactly those three and nothing else, so all four were uncompletable in practice for everyone playing this mod.** |

**FIX.** The 8 + 6 = 14 obtainable-but-unreachable reagents go into new mod-owned tables
(`svc_craft_reagents_{torso,amulet,ring,artifact}_l01`), each hung off the LEGENDARY-tier host
master(s) the chest pools already reach, at ~5% of each host's own total. **All 14 are
`itemClassification = Legendary`, so they can only ever enter a legendary branch - the tier law holds
by construction, not by promise.** No chest or hoard record is touched (that surface belongs to the
concurrent loot-balance lane); this is pool membership only. The three Ragnarok ghosts cannot be "put
into a pool" - a record that is not in the database has nothing to drop - so the four thrown formulas
are repointed onto thrown records that DO exist in this era (the DRX vit wands), in the shape the
database's own recipes use: **2 ordinary + 1 green, all three of the result's own item Class**, which
43 of the 59 uber formulas already follow.

**"NOT A SPECIFIC CHARACTER" IS A SURFACE COUNT, NOT A REACHABILITY QUESTION - rule G4.** The first
cut of this lane hung the artifact reagents off `04_l_misc` alone. That satisfied "reachable from the
legendary chest pool" and was still wrong: measured over the 19 legendary mod chest tables,
`unique_torso_l01`, `amulet_l01`, `finger_l01` and `unique_1h_l01` are reached by **19/19** but
`04_l_misc` by **1/19** - and that one surface is `svc_uberorb_apex_l01c`, the apex uber-boss loot
orb. Six reagents behind one boss family is exactly what Will ruled out, and a union-reachability
test cannot see the difference. The artifact family therefore also hangs off `amulet_l01` and
`finger_l01` (a divine artifact is a trinket; jewellery is its closest kin), and the gate grew a
SPREAD rule: **every non-MI reagent must be payable by at least half of the legendary chest surfaces,
never fewer than 3.** Measured after: **60/60 non-MI reagents (54 ordinary + 6 artifact) at 19/19, floor 10.**

**THE MI EXEMPTION IS EARNED BY A *LIVE* MONSTER, NOT ASSUMED.** The gate derives the MI roster by
rule (`itemClassification == 'Rare'`), fails loud if it drifts from the committed list, and then
proves every entry monster-farmable by walking the reference graph upward from the item to
Monster-class records - **discounting dev duplicates** (`copy of ...`, `xxx...`). Will exempts the
greens *because a monster drops them*; a green that no live monster drops is therefore **not** inside
the exemption, and rule G3 FAILS the build unless it is chest-placed like an ordinary reagent.
Roster and sources: `py tools/gate_craft_thrown_breadth.py <arz> --mi-sources`, and
`docs/CHEST_DROP_MATRIX.md` section 2 carries the committed table.

**THE ONE ORPHANED GREEN, RESOLVED (was `BL-CRAFT-DEBT-1`).** `mi_l_gigantes2` gates Doomherald,
Swordfish and Omega, and MEASURED it has **zero live carriers**: its only carrier is the DRX dev
duplicate `copy of anapaest_45`, because the live `anapaest_45` names placeholder
`drxdishonorguard\equip\bogus\*` ITEM records in the same six slots and the
`drxdishonorguard\equip\loottables\03_master_legendary` that would have re-hung the gigantes tables
has **0 holders**. Rather than rewire a live boss's equip loadout (a loot-balance change, and it
would visibly change what Anapaest wields), the green is chest-placed like an ordinary reagent:
`svc_craft_reagents_orphanmi_l01` on `unique_1h_l01`, its own weapon class, reached **19/19**. The
committed roster `MI_NO_LIVE_CARRIER` records it so a future lane that wires a real carrier - or that
kills another green's last live carrier - has to come back to this ruling. **Those three craftables
are completable; the ledger no longer disagrees with the data.**

**MEASURED RESULT:** reagents reachable from a Legendary chest **42/78 -> 61/82** (the universe moves
to 82 because the repoint replaces 3 dead records with 4 live ones and adds the 3 Common vit wands),
which is **every single non-MI reagent plus the orphaned green**. Craftables whose reagents are all
obtainable: **42/42, with no asterisk.** The seven Will named - Ananke's Canvas, Mortok's Skull, The
All-Seeing Eye, Charon's Toll, Hati, The Last Word, Sanguine Orbit - go from **0/3 reagents to
COMPLETABLE**, all seven.

## R-186 [2026-08-10] IMPLEMENTED (`fix/craft-thrown-breadth`) - THE LEGENDARY THROWN WEAPONS DROP

**VERBATIM:** *"Yes we should make the legendary thrown weapons droppable."*

Answering `docs/CHEST_DROP_MATRIX.md` known-gap #1, which reported the thrown / one-hand-ranged class
as the one class **nothing in the mod could pay at all**: 5 legendary records existed, 0 were
reachable, and there was no "unique one-hand-ranged" loot table in this TQIT-era database for the
R-180 aggregate master to name. This ruling makes the four craft-only supra thrown weapons the ONLY
supra items in the mod that also drop; the other 38 stay craft-only, unchanged.

**FIX.** `records\item\loottables\svc\svc_unique_thrown_{n,e,l}01.dbr`, named by
`svc_loot_breadth._master_members` as the **seventh class** of the `svc_unique_weapons_{tier}01`
masters - so thrown is payable everywhere those masters are named, which is every mod chest's weapon
row AND its guaranteed slot, testhub and Steam alike.

* **`LootItemTable_FixedWeight`, not `DynWeight`, on purpose:** every legendary thrown record is
  `itemLevel 65`, which sits outside the 46-56 band the `_e01` class tables use, so a level-banded
  table could never pay one on the Epic tier.
* **Tier law by membership:** `n` names ONLY the two `itemLevel`-30 wands (Rare + Common) - zero
  Legendary; `e` and `l` name the 5 Legendary thrown, plus the 3 Common vit wands that the repointed
  recipes need as reagents (rule G1 requires a legendary farmer to be able to find every reagent in a
  chest).
* **Weights are derived, not chosen, and they are PER TIER.** A full class weight is 1000 and buys
  ~20 records, so a class takes `records/20` of one. Legendary/Epic thrown is 5 legendary records ->
  **250**; NORMAL thrown is a 2-record band -> **100**. MEASURED against the masters as they shipped
  (7 members, total **6100** at every tier): e/l **250 / 6350 = 3.94%** of a weapon roll, n
  **100 / 6200 = 1.61%**. *(Correction of record: the first cut of this ruling said "250 against
  6700 ... ~0.26%"; 6700 matches no measured state of the record, before or after, and the same wrong
  pair was in the code comment. The derivation "5-record class vs 17-24, so a quarter of a class
  weight" is unaffected and still holds.)* Inside the table the ordinary DRX wand carries 100, each
  craft-tier supra 10 and each Common wand 5, so a specific supra thrown is ~6.5% of a thrown roll
  and ~0.26% of a weapon roll: reachable, and still a prize.
* **A DELIBERATE OMISSION, so it is a choice and not an oversight.** This era's only
  Epic-classification thrown records - `f_n_kaskeron`, `f_l_qilinseternalpyre`, `f_l_godshatter` -
  are BASE-GAME craft results, and they were **NOT** made droppable: making a base craft result fall
  out of a chest devalues base crafting, and Will asked for the LEGENDARY thrown to drop. The
  consequence is that Normal's thrown band cannot pay at that tier's target classification (Epic),
  which is why the Normal master weight is derived from the 2-record band rather than the 5-record
  one - the class no longer consumes an end-game-sized share of a Normal weapon roll for level-30
  filler.
* **PLAYER SURFACE CHECKED (process law #3), and it is the R-140 question:** R-140 proved that
  equipping a `WeaponHunting_RangedOneHand` puts a creature into the `rangedOneHand` stance and that
  SV's roster tables bind no clips for it, which is why the restored thrown MONSTERS froze. Measured
  for the PLAYER: `records\creature\pc\anm\anm_malepc01.dbr` and `anm_femalepc.dbr` each carry **153
  rangedOneHand fields, all 153 bound**, and the DRX vit wands already drop today (`03_m_wands` plus
  the bloodwitch reavers), so the class is live player content in this build. No freeze risk.

**MEASURED RESULT:** legendary thrown reachable from a Legendary chest **0 -> 5**, from an Epic chest
**0 -> 5**, from Normal **0 -> 0** (2 non-legendary thrown instead). The class-breadth gate family
grows the C1/C2 rules so a regression reds; 9/9 negative tests behave as specified.

## R-184/185/186 SHIPPED ADDENDUM (2026-08-11, `build81-dev` + `build81-ship`, arz `f1671207`)

Shipped after the b80 merge. Everything below is MEASURED on the built arz; the rulings above are
unchanged in substance, and the two numbers that moved are corrected here rather than edited silently.

**THE MERGE FOUND SOMETHING NEITHER LANE COULD SEE ALONE, AND IT WAS WORTH THE ROUND TRIP.** b80
(R-181) left a written merge hazard in `tools/svc_loot_distribution.py` (`BL-R181-DEBT-4`): it had
bucketed `WeaponHunting_RangedOneHand` into the `bow` slot because nothing paid that class yet, and it
listed the two things the merging lane owed. Both are now done - thrown has its own slot (12 gear
classes, not 11) and `MAX_WEAPON_CLASS_SHARE` was re-derived for seven weapon classes, **0.29 ->
0.28** (measured worst 0.2363 SPEAR, b80's own 16.8% margin; still reds the shipped 0.4145 by 48%).
The debt is DISCHARGED.

**THE FIRST ATTEMPT AT THE THIRD CONSEQUENCE WAS WRONG, AND THE RECORD SAYS SO.** Giving thrown its
own slot put it inside D3, b80's 1.45% starvation floor. It failed on 9 of 42 surfaces, so round 1 of
the merge raised the class to full parity mass (1350) and flattened the four supra to uniform weights
to satisfy D5. Every gate went green. It was still wrong, and only turning the numbers back into what
a player sees showed it:

| six-chest Gaoler cage run, Legendary | at parity (1350) | AS SHIPPED (250) |
|---|---:|---:|
| thrown items per run | 6.48 | **1.26** |
| a SPECIFIC craft-only supra thrown | 1.30 | **0.081** |
| a SPECIFIC plain legendary SPEAR | 0.44 | 0.44 |
| supra thrown vs plain spear | **2.9x MORE common** | **5.4x rarer** |

A cage run handing Will 1.3 Charon's Tolls is the same shape as the report he already filed against
this wave family (*"you overcorrected, that run 4 scorpions tail spears dropped"*), and it would gut
the craft chain R-184 and R-185 exist to repair. **No gate would ever have complained.**

**ROOT CAUSE, AND THE RULE THAT REPLACED IT.** D3's floor was calibrated on this mod's ordinary gear
classes. MEASURED whole-database universe per class at its own target classification:

> **Legendary:** thrown **5** | bow 23 | mace 24 | SPEAR 24 | staff 25 | sword 28 | legs 33 | shield 33 | arms 37 | helm 39 | axe 41 | torso 71
> **Epic:** thrown **3** | SPEAR 32 | bow 33 | mace 37 | staff 38 | sword 44 | legs 53 | shield 59 | axe 66 | arms 68 | helm 80 | torso 123

Thrown is **4.6x smaller than the smallest ordinary class**. A mass floor written for 23 records does
not transfer to 5. So thrown is exempt from D3's MASS floor (`SLD.D3_ERA_EXEMPT`, threshold
`D3_MIN_CLASS_UNIVERSE = 12`, half the smallest ordinary class) - **and not from scrutiny**: "the
class is payable" is still enforced, by REACHABILITY instead of mass (C1/C2 over all 51 mod chest
tables and all 18 uber orb tables). The class may be thin; it cannot vanish. Three negatives prove the
exemption reds when it stops being earned, reds on a typo'd slot name, and is load-bearing at all
(removing it produces 22 D3 thrown findings, so it is protecting something real).

**TWO CORRECTIONS OF RECORD to R-186 above:**
1. The thrown master weight is unchanged at **250**, but it is no longer a literal - it is
   `SLB._CLASS_WEIGHT // 4`, so a future balance lane re-scales thrown with everything else instead of
   silently shrinking it, which is exactly what b80 did to the hard-coded number. R-186 derived the
   quarter from an ESTIMATE ("a class weight buys ~20 records"); the measured smallest ordinary class
   is 23, so 5/23 is a quarter and **the original ratio was right for a better reason than it gave**.
2. R-186's quoted shares were against the pre-b80 master (7 members, total 6100). Against b80's master
   (total 8100) they are **e/l 250/8350 = 2.99%** and **n 100/8200 = 1.22%** of a weapon-master roll.

**R-184 AS SHIPPED, measured on the built arz:** mythic formulas now reach every Normal act table at
**1.478% / 1.554% / 1.596% / 1.423%** (acts 1-4) - below the base game's own Epic 2% and Legendary 5%,
as ruled. Normal craftable coverage **42/42**; legendary GEAR reachable from the Normal weapon branch
**0 of 116 leaves**, and from the Normal thrown table **0 of 2**.

**R-185 AS SHIPPED:** 82 distinct reagents = **22 MI/green** (exempt, each proven monster-farmable) +
54 ordinary + 6 artifact + **0 missing**; **61 reachable from a Legendary chest**; thinnest non-MI
spread **19 of 19** legendary chest surfaces (floor 10). All 42 craftables completable. *(The "19
MI/green" in R-185 above counted the ORIGINAL 78-reagent universe; the repoint retires the
`mi_l_machae` ghost and introduces the three green vit wands, so 19 - 0 + 3 = 22 in the 82-reagent
universe. Same roster, different denominator.)*
---

## Uber orb loot breadth (new section; decade 220-229, opened 2026-08-10, lane `fix/orb-loot-breadth`)

## R-220 [2026-08-10] IMPLEMENTED (branch `fix/orb-loot-breadth`, module `tools/patches/orb_loot_breadth.py`) - the uber's MYSTICAL ORB must pay every class too

**Will, VERBATIM (2026-08-10):**

> "for the mystical orbs that the uber monsters drop, the items should drop with increased breadth
> as well so all classes of items could be dropped"

(NUMBERING, and the correction that produced it. This lane was first written as R-210 against a
ledger snapshot taken at `build76-ship`, where 210 was free. It was not free by the time the work
landed: `fix/portal-atlantis-cap` minted **R-210 for the portal-page DLC cap** the same day and it
is already PUBLIC on Steam as `build78-ship`. Two entries under one number in the file CLAUDE.md
calls "THE DESIGN LAW OF RECORD" is exactly the failure the ledger exists to prevent, so this lane
renumbered wholesale to **R-220**, opening the 220-229 decade for the orb-container class - the
outcome this note originally argued for anyway. R-180 owns 180-189 (chests), R-200/R-201 the 200s,
R-210 the act-cap surfaces. The ruling TEXT is what binds; the number must still be unique.
This entry also sits at the ledger TAIL, after R-201 and R-210, because the ledger is append-only
newest-LAST and those two were appended while this branch was in flight.)

**"AS WELL" POINTS AT R-180, AND THAT IS EXACTLY WHAT THIS IS.** R-180 fixed the CHESTS that
morning: every mod chest now names the aggregate weapon master `svc_unique_weapons_{n,e,l}01` and
legendary spears went 0 -> 22. Will's "as well" is the OTHER half of the mod's loot economy - the
on-death orb. The literal "mystical orb" is settled by R-200: every `genericbossorb_0N` chest carries
`description = tagEndChest02` and base `Text_EN` defines `tagEndChest02 = Mystical Orb`.

**THE DEFECT, MEASURED ON THE build76 SHIP ARZ (51,234 records) - IT IS R-180's DEFECT, IN A SECOND
DONOR FAMILY, AND IT IS TOTAL.** Each orb tier is really THREE loot tables (the proxy's
`accessory1` / `accessoryEpic1` / `accessoryLegendary1` slots -> pool -> chest -> `tables`). Every
one of them carries the same collapsed weapon row, using 5 of its 6 member slots:

    all_13-15 (w2000) . staff_all_13-15 (w500) . unique\1h_all_n01 (w27)
    . unique\bow_n01 (w27) . unique\staff_n01 (w27)

`1h_all_*01` is a LootMasterTable with exactly THREE children - axe, club, sword. The donor
compensates for bow and staff by naming them DIRECTLY and forgot the third excluded class, SPEAR;
the level-banded statics beside it carry no unique spears at all. Result: **0 spears of ANY quality
were reachable from 15 of the 18 uber orb tables, at every tier and every difficulty.**

**THE TELL, AND WHY THIS WAS INVISIBLE.** The three tables that were already fine are orb05's
`records\item\loottables\svc\svc_uberorb_apex_{n,e,l}01c` - and only because they live in an `\svc\`
folder, so R-180's `chest_loot_breadth` sweep (scoped to mod-OWNED FixedItemLoot) reached them. The
other four tiers sit under `records\item\containers\defaultloot\` and `records\xpack\item\containers\
loot tables\`, which that ownership rule cannot see. R-180's own gate was therefore GREEN on a build
where four of five orb tiers could not drop a spear. This is the same lesson as R-200 hole 1, one
layer down: a scope rule chosen for one container class silently excludes another.

**IMPLEMENTED (arz-only - proxies, pools, chests and loot tables all live in the `.arz`, so the fix
reaches the TESTHUB, DEV and canonical/Steam together with no Levels/Text/Quests rebuild):**
- `tools/svc_orb_breadth.py` (NEW) is the ONE implementation of the orb contract, and it is a THIN
  driver over R-180's `tools/svc_loot_breadth.py` - the same masters, the same `widen_weapon_row`,
  the same `audit_table`. Not a second opinion.
- `tools/patches/orb_loot_breadth.py` (NEW, registered after `chest_loot_breadth` and
  `red_uber_orbs`, before the no-op `visuals`) applies it and carries the gate.
- PER TABLE, and nothing else: the tier-correct master into the ONE free loot1 member slot at
  weight 800, `loot1Chance` (weapons) 13/14 -> 40 and `loot6Chance` (shields) 13/14 -> 30. Those two
  numbers are NOT invented here - they are the values orb05 has SHIPPED since build75, so the ladder
  becomes self-consistent: after this wave every loot container in the mod, chest or orb, has the
  same weapon-row shape.

**TWO SEPARABLE DECISIONS, AND ONLY THE FIRST IS WHAT WILL ASKED FOR - SO THE SECOND GETS AN
EXPLICIT VETO POINT.** The wave moves 60 fields on 15 base-game orb tables, and they are two halves:
1. **BREADTH (30 field moves) - Will's actual order.** The added `loot1Name<free>` /
   `loot1Weight<free>` member per table. This is the whole of "all classes of items could be
   dropped": spear 0 -> 18 / 9 / 22, and it is what the O1/O2b gate defends.
2. **PAYOUT (30 field moves) - NOT asked for, defensible, and droppable on its own.**
   `loot1Chance` 13/14 -> 40 and `loot6Chance` 13/14 -> 30. Justification: those are the values
   orb05's apex tables have shipped since build75, and R-180 made the identical raise on the chests
   without objection, so raising them makes the ladder consistent rather than inventing a number.
   But it roughly TRIPLES how often an orb's weapon row fires and doubles the shield row, which is a
   payout change, not a breadth change.
   **Vetoing half 2 costs ONE edit, and the switch ships with the wave:** set
   `svc_orb_breadth.RAISE_ROW_CHANCES = False` and the orbs gain every weapon class at exactly the
   drop rate they have today. It lives in the ORB module, not in the shared
   `svc_loot_breadth.widen_weapon_row`, precisely so vetoing the orb payout cannot silently revert
   R-180's chest raises. Half 1 is untouched either way.

**SCOPE IS DERIVED, NEVER TYPED, AND DERIVED OVER MOD UNION BASE** (R-200 hole 2: a roster derived
over the mod db alone is blind to a base-only uber). An UBER is R-200's own predicate - `um_*`
basename or a `tagSVCMonster*` display tag. SCOPE = every proxy an uber names + every table its
three difficulty slots resolve to. MEASURED: **51 uber carriers -> 7 proxies, 6 of them IN REACH
-> 18 tables** =
`genericbossorb_01..05` (the mystical-orb ladder) plus `bosschest02_charon`, whose terminal Ferryman
`um_charonform2_ferryman_99` IS a red uber and whose three tables carry the identical collapse.

**THE SCOPE BOUNDARY, STATED SO NOBODY WIDENS IT BY ACCIDENT** (the R-200 precedent, in spirit):
the six proxies whose consumers are BASE act/quest bosses rather than ubers are OUT -
`bosschestproxy11_aktaios` (3 Telkines), `bosschestproxy21_typhon` (2), `bosschestproxy_blackwidow`
(1), `coldworm_orb` (1), `1_default_33-35` (1) - and `bosschestproxy_leinth`, whose three Boss-rank
carriers are neither `um_` nor tagSVCMonster. Leinth needs nothing anyway: `uber_apex_orb` repointed
her chests onto the `svc_uberorb_apex_*` tables, so R-180 already widened them and R-180's gate
already covers them. Registered as `BL-R220-DEBT-1`. A negative test proves the boundary is real AND
live: plant a new uber on the Aktaios orb and the derived scope GROWS to cover it and reds.

**WHAT THE GATE FOUND ON ITS OWN FIRST UNION RUN, AND WHY IT IS NOT WIDENED.** Deriving over mod UNION
base immediately paid for itself: exactly ONE uber names a proxy the mod overlay does not contain -
the base-only Hero-rank DEVICE `records\creature\devices\darkobelisk\um_darkobelisk_55.dbr`
(`tagAEMonsterName07`, the Dark Obelisk) -> `records\proxies boss\le_new\25_towerofjudgement_treasure.dbr`.
MEASURED: it resolves fine in the base game, and its chain lands on `g_default_{n,e,l}01c` - the GOLDEN
CHEST tables (`tagChest006`), each shared with FIVE base containers (the act-4 golden chests, two
side-quest golden chests, the Cerberus and Skeletal Typhon repeat boss chests). Widening it would
rewrite the base game's act-4 golden-chest economy from a lane asked about mystical orbs. It is PINNED
in `svc_orb_breadth.OUT_OF_REACH` with that reason (`BL-R220-DEBT-1`), and a NEW base-only chain fails
the gate (O5) so it becomes a human decision rather than a silent omission. TWO GUARDS came out of that
finding and both ship: O5 (base-only chains must be pinned, and a pin that names nothing is stale
config) and O6 (an in-scope table that ANY container outside the uber chains also names is excluded
from the sweep and stops the build until a human decides - so this lane can never quietly rewrite
shared base loot). Both are exercised by planted negatives; O6 is currently a pure guard, since all 15
non-mod-owned in-scope tables were measured to have exactly ONE referrer, their own orb chest.

**NON-REDUCTION / IDENTITY LAW (Will farms these ubers; R-100 #17 + Will 2026-08-08 preserved).**
`apply()` snapshots all 60 in-scope records - every table AND every proxy, accessory pool and chest
in every chain - and FAILS THE BUILD if any field outside `loot1Name<free>` / `loot1Weight<free>` /
`loot1Chance` / `loot6Chance` moves, or if any chance drops. So numSpawn equations come through
byte-unchanged (the apex tier keeps its `*2.2/*2.4` edge over the generic `*1.2/*1.6` and
`*0.9/*1.3`), as do the relic row, the potion row, both armour rows, the mesh, the gold generator,
the level equation and `description tagEndChest02`. No member is ever removed and no chance lowered.
There is deliberately NO guaranteed-weapon retarget: an orb's loot3 is potions + rare misc at 10%,
not the chests' 100% weapon slot, and adding one would change HOW MUCH an orb pays. Will asked for
breadth.

**TIER LAW preserved by construction:** the master is resolved through the DIFFICULTY SLOT the chain
arrived on, so the normal branch can only gain `*_n01` tables (measured 100% Epic-classification).
MEASURED BASELINE, stated rather than implied: the normal branch of every orb tier ALREADY reaches
41-56 `ItemArtifact` + 3 `ItemArtifactFormula` Legendary-classified records (base-game mercenary
scrolls and arcane formulae - exactly what R-180's own B3 exempts) and ZERO legendary GEAR, before
and after.

**ONE CONSEQUENCE OF THAT RULE IS A BASE-GAME RETIERING, AND IT IS DELIBERATE - RECORDED SO NOBODY
LATER READS IT AS AN ACCIDENT.** "Tier comes from the difficulty slot, never the file name" is the
right rule (`uberorb_default_53-55` is a LEVEL band, not a tier), but applied to orb02 it does more
than widen. MEASURED: `genericbossorb_02.accessoryLegendary1` resolves to
`records\item\containers\defaultloot\uberorb_default_53-55.dbr`, whose shipped weapon row names
`1h_all_e03` / `bow_e03` / `staff_e03` - the base game gave that orb EPIC-band uniques on LEGENDARY
difficulty. This lane wires it the LEGENDARY master, so it is the largest single jump in the wave:
**138 -> 241** distinct legendary items, the only table whose delta exceeds +100. Legendary
difficulty arguably should pay legendary uniques, so this is not being reverted - but the per-tier
table below presents it alongside pure-breadth deltas and it is not purely breadth.
**AND THE EXISTING TIER GATE CANNOT CORROBORATE IT.** `tools/gate_relic_difficulty_tiers.py`'s
`audit_proxy_chain` skips any table failing `is_mod_loot`. MEASURED on the build78 arz
(`f6638462`): of the 18 in-scope orb tables only the 3 mod-owned apex ones are visible to it, and
**of the 15 tables this lane actually WRITES, ZERO are visible** - so that gate's "33 mod-owned
branches audited, PASS" is necessarily unchanged by this wave and proves nothing about it either
way. The tier claim therefore rests solely on this lane's own B1/B3 + O2b, and B3 only forbids
legendary GEAR on the NORMAL branch - an epic/legendary mixup that ADDED the wrong master ALONGSIDE
the right one on an epic branch would pass O2b unseen. Registered as `BL-R220-DEBT-6`.

**MEASURED (dry-run of the real code against the LIVE build78 arz `f6638462`, 51,236 records - first
measured on build76 and RE-measured on build78 after this branch merged `main`, because build77 (soul
names) and build78 (portal page) are arz deltas and "they don't touch loot tables" had to be proved
rather than assumed. Every number below is bit-identical across the two bases.) Target-classification
pool and reachable spears, before -> after:**

    orb01    n 117 -> 195   e  72 -> 99    l 194 -> 260     spear 0 -> 18 / 9 / 22
    orb02    n 101 -> 182   e  75 -> 102   l 138 -> 241     spear 0 -> 18 / 9 / 22
    orb03    n  96 -> 180   e  71 -> 96    l 196 -> 262     spear 0 -> 18 / 9 / 22
    orb04    n  99 -> 181   e  95 -> 116   l 258 -> 308     spear 0 -> 18 / 9 / 22
    orb05    n 181          e 116          l 308            unchanged - R-180 got there
    charon   n  99 -> 181   e  95 -> 116   l 258 -> 308     spear 0 -> 18 / 9 / 22

**GATE (law 4, no new surface without a gate):** `tools/gate_orb_loot_breadth.py` + the in-build
`orb_loot_breadth.verify()`, sharing ONE implementation - O1 every in-scope table reaches every
weapon class at its own difficulty (SPEAR named explicitly), O2 the per-branch pool floor
(n 150 / e 80 / l 200, each ~15% under the post-wave thinnest table), O2b the breadth master is
still NAMED in the weapon row (structural, so a re-collapse reds by name), O3 no legendary GEAR on
the normal branch, O4 every chain resolves end to end at all three difficulties and the derived
scope never shrinks below its measured 6-IN-REACH-proxy / 18-table floor, **O4b no table is reached
at two different difficulties** (the one narrowing a table COUNT cannot see: `scope_tables`
de-duplicates first-wins, so such a table would be widened with ONE tier's master and audited against
ONE tier's floor while the count stayed at 18), O5 every base-only uber chain is
PINNED with its reason and no pin is stale, O6 no in-scope table is shared with a container outside
the uber chains. HONEST LIMIT recorded in the code: only the NORMAL floor also sits above the pre-wave
value, so on the epic and legendary branches the revert catch is O1 + O2b, not the count. Negatives:
`py tools/debug/negtest_orb_breadth.py <arz>` - **11/11 on the live build78 arz**, run over mod UNION
base like the build gate, each case asserting its own check code (a re-collapse; a floor-only collapse
with B1 proven NOT to fire; a tier leak; a broken chain link; the derivation killed; a NEW uber
dragging an unseen chain into scope; a base chest starting to share an orb table, with B1/B2 proven
NOT to fire; an unpinned base-only chain; one table reached at two difficulties; plus two positive
controls). The apply-side collapse guard counts the IN-REACH proxies exactly as the gate does, so it
cannot be one proxy weaker than the floor it quotes.

**INTEGRATION, stated because two SIBLING lanes edit the same shared builder.** This lane's only edit
to `tools/svc_loot_breadth.py` is the cosmetic `noun=` kwarg. `fix/armor-loot-breadth` and
`fix/craft-thrown-breadth` also rewrite that file, and craft-thrown rewrites `audit_table` itself
while keeping the old signature - so a wholesale take of its hunk would delete the kwarg. Mitigated
in-lane (the orb side probes for it and degrades loudly rather than raising `TypeError` inside a
fail-loud gate), but the hand-resolution and the RE-MEASURE of `POOL_FLOOR` after either sibling
changes the shared master's membership are the integrator's, registered as `BL-R220-DEBT-5`.

**NOT PROVEN IN-GAME.** The build, DEV deploy and Steam ship are the orchestrator's; Will's kill of
any orb-dropping uber and seeing spears / class variety out of the orb is the remaining launch gate.
Registered as `BL-R220-DEBT-2`. See `docs/WILL_TEST_GUIDE.md` and the BACKLOG gate record.

**SHIPPED (2026-08-11, tags `build79-dev` + `build79-ship`).** Everything above was built and re-measured
on the real artifact rather than the dry-run, and every predicted number came out identical: arz
`883a31e2b87f03a54a51c550147c8242` (55,551,723 B, 51,236 records), det-2x byte-identical, record-diff vs
the shipped `f6638462` = **15 MODIFIED / 0 added / 0 removed, 4 fields each, ZERO unexplained**, with the
tier law readable straight off the diff (`[n]`->`n01`, `[e]`->`e01`, `[l]`->`l01`). Spear **0 -> 18 / 9 /
22** on every tier that was broken; pools n 180..195 / e 96..116 / l 241..308. Live on DEV and on Steam
(item 3759792705, ManifestID `867654719607079771`, still PUBLIC). arz-ONLY: Text/Levels/Quests/Creatures
md5-proven byte-unchanged, so the arz+Text coupling was SATISFIED, not waived. Contracts 0 P0 / 0 P1 /
4492 P2, identical to the baseline A/B. The PAYOUT half shipped ON, as argued above, and stays vetoable in
one line (`RAISE_ROW_CHANCES = False`). One new debt filed by the ship lane: `BL-R220-DEBT-7` (the R-200
negtest harness cannot run against a post-R-200 arz - pre-existing, measured on the untouched shipped
baseline too). Full records: `docs/BACKLOG.md` -> SHIP RECORD + BUILD79-DEV GATE RECORD.

---

## R-181 SECOND AMENDMENT [2026-08-11] IMPLEMENTED (branch `fix/orb-armor-rows`, module `tools/patches/orb_armor_rows.py`) - the orb tables' armour has an OWNER, and "owned by nobody" is now structurally impossible

**WILL'S ORDER, the one this closes:** orbs roll ALL item classes - **armour parity included**. R-220
delivered the weapon half of that on the mystical orbs. This is the armour half.

**WHAT WAS ACTUALLY WRONG, and it is not "someone forgot a table".** R-181 decided what it owned by
asking what FOLDER a loot table lived in (`\svc\`). R-220 then wrote fifteen tables in other folders -
`uberorb_default_*` x12 and `boss_charon_{n,e,l}01b` - and widened only their WEAPON row. Armour on
them belonged to no module, so no surface audited them, so **both fail-loud loot gates were GREEN for
an entire build while fifteen live player surfaces starved.** MEASURED on the shipped build80 arz
`c5851a1a`:

| | shipped build80 | after this wave |
|---|---|---|
| weapon:armour, the 15 tables | **3.45:1 .. 8.38:1** (cap 1.85) | **0.28:1 .. 0.49:1** |
| thinnest worn slot, per open | **0.007 .. 0.044** | **0.285 .. 1.164** |
| thinnest worn slot, per spawn iteration | **0.0011 .. 0.0050** | **0.0443 .. 0.1406** |

After the wave every uber orb in the mod sits in the SAME weapon:armour band as the three apex orbs
Will already farms (0.28-0.33), which is the parity test that matters: consistency with the surface he
has actually played, not a number chosen here.

**THE FIX IS R-181'S OWN TREATMENT, NOT A SECOND OPINION.** One `svc_armor_breadth.widen_armor_rows`
call per table: every armour row to the weapon row's 40%, every unique-armour member to 850, the
aggregate armour master (all five worn slots at equal weight) into the shield row's free member slot,
plus the weapon row's own two R-181 corrections so lifting armour cannot INVERT the surface. Additive
or a strict raise throughout - nothing removed, nothing lowered, `numSpawn` untouched.

**TWO THINGS HAD TO BE WIDENED BEFORE THE TREATMENT COULD EVEN SEE THESE TABLES, and both were silent
misses rather than design decisions:**

1. **The two donor families spell "unique" differently.** The xpack/DRX family names
   `\torso\mastertables\unique_torso_l01.dbr`; the base-game LEVEL-BANDED family the nine
   `uberorb_default_<band>` tables clone names `\torso\mastertables\unique\torsoall_n01.dbr` and
   `\head\mastertables\uniques\headall_n01.dbr`. `_UNIQUE_ARMOR_RE` matched only the first spelling,
   so on those nine tables it saw the SHIELD member and none of the four body slots - which is why
   helm/arms/torso/legs sat at the donor's weight of 27 against ~1700 of static junk. Same split on
   the weapon side (`unique_1h_l01` vs `unique\1h_all_l01`), which hid the fact that one member was
   paying axe+mace+sword at a single class's weight. The expressions are now strictly WIDER - every
   path the old ones matched still matches - and the proof is byte-level, below.
2. **Ownership was a folder name.** It is now a rule about WRITES.

**THE LAW THIS ADDS (`tools/svc_loot_ownership.py`):**

> Every loot table a module WRITES must be inside the distribution gate's surface set.

Not "every mod-owned table" - every WRITTEN table, whoever wrote it and wherever it lives. Two
independent witnesses, because neither alone is enough: the LEDGER (the four shared loot builders
register every table they touch, so any caller anywhere is covered, including dry runs and the
negative battery) and the REGISTRY TOUCH LOG (`run_registry` already recorded every `_modified.add()`
against the module that made it; it is now persisted as `db._registry_touch_log` for the
post-finalization gates, which catches a module that writes loot fields RAW). A missing touch log is
ANNOUNCED, never a silent pass. Coverage of the orb tables is likewise DERIVED - `all_surfaces` reads
R-220's own `scope_tables` - so a sixteenth orb table is swept AND audited the day it exists. A typed
list of fifteen names is exactly how this debt existed.

**ONE THRESHOLD GAINED A SECOND FORM, AND IT WAS DERIVED, NOT LOOSENED.** D7 ("every worn slot pays
0.52 pieces per open") is a statement about a container that spawns ~10.6 items, because that is the
container it was calibrated on - every one of R-181's 42 surfaces spawns 10.58 to 18.96, so the number
was never volume-sensitive and nothing said so. The orb tables spawn **5.06 to 8.28**. On them the
same absolute number is not a parity demand, it is a demand for more DROPS - `numSpawn`, which
`BL-R181-DEBT-5` reserves to Will - and it is unreachable from the other side too: after the treatment
they sit at weapon:armour 0.28-0.49 against D6b's 0.24 floor, so armour on them CANNOT be lifted
further without burying weapons. So **D7 keeps its exact number and its exact behaviour on every
surface at or above the volume it was derived at (all 42 - byte-identical), and D7b asserts the same
invariant with the container's own volume divided out, on all 57.** That quantity turns out to be
nearly a constant of the contract: after the wave EVERY chest, hoard, cage variant, DRX donor and orb
lands on 0.1406 / 0.0589 / 0.0996 per iteration by tier. **D7b at 0.0375 reds all 57 surfaces of the
defect state** (its best reading is 0.0175), making it a strictly stronger revert-detector than the
absolute floor it complements. Nothing was weakened: the defect state goes from 27 findings to **622**.

> ⚠️ **SUPERSEDED BY ROUND 3 (see the ROUND 3 amendment at the end of this file). The paragraph below
> is kept VERBATIM because the mistake is the lesson.** Its build79 readings reproduce exactly, but
> b79 was three ships stale: against the LIVE b82 artifact three of the four surfaces were made WORSE
> by this lane and `uberorb_default_29-31` was pushed from compliant (0.0251) to over-cap (0.0323) by
> it. The stated cause was wrong too. Round 3 removed the cause and **three of the four pins are
> deleted**; the one that remains sits BELOW its surface's own pre-lane value.

**FOUR SURFACES CARRY A MEASURED, REASONED D5 PIN INSTEAD OF A LOOSENED CAP.** Four level-banded orb
tiers hold a single item at 3.2-4.5% of the surface's gear mass against the 3.0% cap. MEASURED on
build79, BEFORE any of this: 3.2%, 4.58%, 4.61%, 4.47% - **pre-existing concentrations that were
invisible only because nobody audited the table**, and this wave IMPROVES two of them. The obvious
alternative - let D5's cap scale with pool size, the argument D4 already makes for classes - was
measured and REJECTED: the smallest x-uniform among the 24 pre-existing surfaces D5 reds in the defect
state is 3.53 and the largest among the new orb surfaces is 6.35, so any clause loose enough to pass
the orbs would let **23 of those 24 shipped defects through**. The global cap therefore stays 0.030 for
every surface in the mod and these four are held to their own measured ceiling, each with a written
reason; a pin that falls back under the global cap reds as dead config. Cause registered as
`BL-R181-DEBT-9`: base-game level-banded static randomisers paying a narrow set of high-band
legendaries, the same class of finding D4 already records and the same content this mod does not own.

**NON-REGRESSION IS PROVEN AT THE BYTE LEVEL, NOT ASSERTED.** The R-181 wave running on this branch
against the build79 arz reproduces the **SHIPPED build80 bytes exactly on all 360 FixedItemLoot
records in the db** - so the widened expressions and the new surface set change nothing outside R-220
scope. Every other calibration number is unmoved: D1 0.2084, D2 0.2084, D4 5.0383, D6 1.5857, D8
0.2413, D9 0.2918, D3 0.0175, D6b 0.2845.

**GATES.** All three loot gates PASS on the build80 arz with the wave applied: distribution (57
surfaces, up from 42), orb breadth (18 tables, pools GREW - epic 101-121 against the 95-116 R-220
shipped, legendary 246-327 against 246-308), chest breadth (35 tables). Registry selfcheck OK, 58
modules, order `4a8297a0e59d`. Negative battery: **13 planted defects all red, 3 positive controls
green**, including the b79 armour rows replanted on one table from EACH donor family and the SYNTHETIC
ORPHAN planted against both ownership witnesses.

**NOT PROVEN IN-GAME, and it is the same gate as R-181's.** Everything above is a database and gate
proof. Will's check: kill any uber that drops a Mystical Orb (a red-uber orb, Charon's Essence, or any
generic-orb uber) and expect helms / chest plates / bracers / greaves / shields out of the ORB at
roughly the rate the cage chests now pay them.

**`BL-R181-DEBT-4` WAS OBSERVED LIVE HERE, THEN CLOSED BY b81'S OWN MERGE.** That debt predicted that
bucketing `WeaponHunting_RangedOneHand` with `bow` would be invalidated the moment
`fix/craft-thrown-breadth` landed. Measured here by accident, mid-flight, against an arz that lane had
just built: **D8 bow read 29.2-29.8% against its then-29.0% cap on six of the new orb surfaces** - they
are the thinnest weapon pools in the mod, so a mis-bucketed weapon class shows THERE first. b81 then
merged and did both halves itself (thrown has its own slot in `WEAPON_SLOTS`/`SLOT_ORDER`;
`MAX_WEAPON_CLASS_SHARE` re-derived 0.29 -> 0.28 for seven weapon classes). Re-verified after merging
main into this lane: **D8's worst reading over all 57 surfaces is 0.2363.** The observation is kept
because it is the evidence the debt was real.

**RE-MEASURED AFTER `main` ADVANCED (b81, thrown as a real twelfth gear class; and again after b82).**
`main` moved twice while this lane was in flight, so every number above was re-taken with the merges in
place - round 2's readings are against the SHIPPED `local/build81_ship_f1671207.arz`
(`f16712077f315e5d5cf38a32f9c1fec6`), not the pre-ship run `c502f173` round 1 quoted: distribution PASS on 57 surfaces across all 12 classes, orb / chest /
craft-thrown gates PASS, **16 negatives red and 3 positive controls green**, registry 59 modules order
`ba6fde285aad`, and the D5 pins all still earned (49-51 moved 0.0453 -> 0.0451, still above the 0.030
global cap, so none went stale) - **that last clause is SUPERSEDED BY ROUND 3: "still above the global
cap" was true and "still earned" was not, because the lane itself had put three of them there. Three
of the four pins are now deleted.** The merge had exactly two conflicts, both ADDITIVE - each side had
added an independent block - and this lane's negtest cases were renumbered N10/N11 to stop colliding
with b81's N7-N9. **Blast radius, proven exactly:** every loot module EXCEPT `orb_armor_rows`
reproduces the shipped b81 bytes identically on all 360 FixedItemLoot records; adding it changes
exactly **15 records, 12 fields each, and nothing else**.

**MEASURE FROM `local/`, NOT FROM `work/`.** Mid-lane, `work/SoulvizierClassic/Database/
SoulvizierClassic.arz` was rewritten by a concurrent build (md5 `c502f173` at 01:53, against build80's
`c5851a1a`). Two readings taken against it before that was noticed were discarded and re-taken. This is
`BL-R181-DEBT-8` biting a second time; while a fleet is running, the committed artifacts in `local/`
are the only safe baselines.

### R-181 SECOND AMENDMENT, ROUND 2 [2026-08-11] - the independent vet found this lane committing its own defect class, and the law it produced

The round-2 vet returned **1 HIGH, 2 MEDIUM, 2 LOW**. All five are closed on this branch. One of them
matters far past its patch, because it is this ruling's own subject caught happening again.

**THE HIGH: A FAIL-LOUD GATE WENT QUIET ON A LIVE SURFACE WHILE ITS PASS LINE SAID OTHERWISE.** D7 -
the absolute "every worn slot pays at least 0.52 legendary pieces per open" floor - is asserted only
on containers at or above the volume it was derived at, via `spawn >= ARMOR_SLOT_FLOOR_REF_SPAWN`.
`S_eff` is a WEIGHTED SUM over a surface's variants, not a literal, so the three
`svc_uberorb_apex_{n,e,l}01c` surfaces compute **10.579999999999998** - `1.78e-15` under the constant.
The comparison was therefore False and **D7 was never evaluated on them at all**, leaving an unguarded
band of **0.3968 .. 0.52 pieces per open** on each, roughly a quarter of the floor. It was guarded
before this lane. Worse, `svc_uberorb_apex_e01c` at 0.6229 is **the exact surface the 0.52 number was
calibrated on**, and two documents said in writing that D7 kept its exact behaviour on "all 42,
byte-identical". Both were false for 3 of the 42. The vet demonstrated it rather than arguing it:
cutting that surface's armour rows 25% reds on `main` and passed GREEN on this branch.

> **LAW: A THRESHOLD MUST BE ASSERTED, DEMONSTRABLY, AT THE PLACE ITS NUMBER WAS DERIVED.** A
> calibration anchor is the one surface where a threshold provably means what it says. If the check is
> not switched ON there, the number is folklore. `svc_loot_distribution.reference_surface_problems`
> (**D7X**) now asserts exactly that, from the opposite direction to the comparison it protects: not
> "is the `>=` written correctly" but "is D7 demonstrably ON at the reference surface, and is that
> surface still in the audit set at all". A future edit to the threshold, the equations, the variant
> weights or the comparison cannot switch D7 off there without reding. It caught its own constant
> being written with a wrong label prefix on the first run.

> **LAW: A GATE STATES THE COUNT, NEVER THE UNIVERSAL.** "every surface at or above the reference
> volume" is unfalsifiable in a log; **"the 42 of 57 surfaces at or above the reference volume"** is a
> number a reader can watch move. Both the standalone gate and the in-build gate now print it. This is
> the same discipline `armor_loot_breadth` already applied to D7b ("saying every worn slot clears
> 0.52/open while a low-volume orb sits at 0.28 would be a gate lying in its own PASS line") - the
> round-1 lane wrote that sentence and then broke it two constants over.

**THE FIX IS A TOLERANCE PLUS A STRUCTURE, NOT A TOLERANCE.** `d7_applies()` is now the single
implementation of the boundary (`ARMOR_SLOT_FLOOR_REF_TOL = 1e-9` relative - seven orders of magnitude
under the coarsest real gap between two surfaces' volumes, so it can only ever absorb float noise),
used by the audit, both PASS lines and the negatives alike. Two permanent negatives pin it: **N12**
plants the vet's own regression on the reference surface inside the band D7b alone cannot see, **N13**
nudges the reference volume past that surface's own S_eff so D7X itself must red. Measured after:
**D7 asserted on 42 of 57 surfaces**, every calibration number unchanged, 16 negatives red.

**THE TWO MEDIUMS: A GATE MUST NOT CLAIM MORE REACH THAN IT HAS.** The ownership gate printed "every
loot table written in this build is audited by a surface or EXEMPT", which neither witness could
enforce: `tools/apply_svc_patches.py` runs OUTSIDE `run_registry` (no touch log -> OWN2 blind) and
writes some loot rows without a shared builder (-> OWN1 blind). Both halves done. Its **27
`svc_*hoard_loot_{01,02,03}` gear containers now call `note_write`**, so the ledger genuinely covers
them - measured, all 27 are inside the audited surface set and ownership stays at 0 problems. Its
base-game `defaultloot` restore is deliberately OUTSIDE the contract and is now **named in the PASS
line itself** and registered as `BL-R181-DEBT-10`: those writes copy a value straight out of the base
arz, restoring a base-game row to its base-game shape rather than widening a mod surface, and
base-game monster loot is `BL-R181-DEBT-2`, a Will decision. The second medium was record hygiene -
three gate numbers in the BACKLOG record did not reproduce (35 vs **51** tables, 13 vs **16**
negatives, 58/`4a8297a0` vs **59**/`ba6fde28`); they were pre-merge readings left standing beside
post-merge ones and are **corrected in place**, because this repo's records are the audit trail a cold
successor trusts. `main` was re-merged at **`0019861`** (b81 shipped, b82 atlantis-voyage landed);
sole conflict was the additive BACKLOG header, `tools/` auto-merged clean, all gates re-green.

**THE TWO LOWS, both "the proof did not prove what it printed".** The scope proof's name-field branch
was a bare `pass` whose comment claimed the value was checked above - it was not, so a donor shape
carrying an existing member could have been clobbered while the proof reported PASS and the failure
text promised "no member removed". It now asserts the slot was empty. And `orb_scope`'s cache was keyed
on record count alone, so a rewire that moved a chain between EXISTING tables would serve a stale
scope; the key now carries the write count, the gate derives with `fresh=True` from the db's final
state, and `verify()` compares that against what `apply()` actually swept and fails loud on any
difference - the only way to catch a table reached after the sweep, since nothing wrote it and no
ownership witness would fire.

### R-181 SECOND AMENDMENT, ROUND 3 [2026-08-11] - the lane was making three live surfaces worse, and its own record said the opposite

The round-2 vet returned **1 HIGH and 3 LOW**. All four are closed on this branch. The HIGH is the one
that matters past its patch, and it is the same failure shape as round 2's - a proof measured against
something other than what it claimed - but this time it had a **gameplay consequence**, not only a
documentation one.

**THE HIGH: FOUR PER-SURFACE CEILINGS RAISED WILL'S CAP ON NUMBERS FROM A THREE-SHIPS-STALE ARTIFACT.**
`MAX_ITEM_SHARE_TOTAL = 0.030` is the guard born from Will's own report - *"you overcorrected, that run
4 scorpions tail spears dropped"*. Round 2 raised it to 0.037/0.044/0.039/0.052 on four orb surfaces
and justified all four with the sentence *"MEASURED on build79, the state BEFORE any of this"*, adding
that the treatment IMPROVED two of them. Those b79 readings were honestly sourced and reproduce
exactly - but **b79 was three ships stale**, and the b81 craft/thrown wave had since diluted the weapon
side of those very surfaces. Measured against `local/build82_run1_09a0f51d.arz`, the LIVE Steam/DEV
bytes the build replaces, round 2's true before -> after was:

| surface | b82 before | round 2 after | round 2's claim |
|---|---|---|---|
| `uberorb_default_29-31` | **0.0251** (UNDER the cap) | **0.0323** | "unchanged, pre-existing" |
| `uberorb_default_39-41` | 0.0338 | **0.0383** | "IMPROVED from 0.0458" |
| `uberorb_default_43-45` | 0.0339 | 0.0337 | "IMPROVED from 0.0461" |
| `uberorb_default_49-51` | 0.0330 | **0.0451** | "0.0447 before it" |

Three worse, one flat, and **29-31 pushed from compliant to over-cap by the lane itself** - it needed a
pin ONLY because the lane put it there. The stated cause was inverted too: on b82 the top item on all
four is a WEAPON; after round 2 it is an ARMOUR piece round 2's own rows introduced.

> **LAW: A BASELINE IS AN ARTIFACT, AND THE ONLY HONEST ONE IS THE ARTIFACT YOU ARE REPLACING.**
> "Before" does not mean "before this branch existed"; it means **the bytes that are live right now**.
> A lane that has been rebased across three ships has three candidate baselines and only one of them
> tells a player what changed. Every before/after in a ship record is now measured against the LIVE
> artifact by md5, and the md5 is quoted beside the number.

> **LAW: WHEN A GUARD OF WILL'S REDS ON YOUR OWN WORK, MOVE THE WORK.** Raising a threshold because the
> lane trips it is the failure mode the threshold exists to prevent. The order of resort is: fix the
> cause, then take it to Will as a balance call, and only then pin - and a pin is only honest if it
> sits **below** what the surface measured before the lane touched it, so it cannot admit anything the
> lane created.

**THE CAUSE, MEASURED, AND FIXED AT SOURCE.** `ARMOR_UNIQUE_WEIGHT = 850` is an ABSOLUTE weight, and it
silently assumed the pool behind a member SPREADS what it is given. Over all 55 distinct unique-armour
members any in-scope armour row names, the share of a member's own mass carried by its top item runs:
aggregate master **1.2-3.5%** (N=47-149), xpack family **3.7-20.0%**, and the base-game LEVEL-BANDED
family the nine `uberorb_default_<band>` tables are cloned from **4.9-46.4%** - `legsall_e03` has six
items and puts 46.4% of its mass on one pair of greaves. Raising that member 27 -> 850 multiplies that
one item **~31x**. That, not any base-game randomiser, is what round 2 shipped.

> **LAW: AN EVEN-SPREAD INSTRUMENT IS ONLY AS EVEN AS ITS POOL.** This module already held that "the
> master is the even-spread instrument, so any per-slot bias must be expressed by a THEME, never
> smuggled in here" - and then handed the same absolute weight to pools with six items in them.
> `ARMOR_UNIQUE_REF_TOP_SHARE` bounds each member by its own pool's measured evenness and hands the
> surplus to the aggregate master, conserving total unique-armour weight per table and moving only its
> distribution. The reference (0.21) is set from the SHIPPED fleet - above the highest top-share any
> pre-existing surface can reach (`unique_torso_e01` 0.1967) and above the perfectly-uniform five-item
> banded shields (0.2000) - so it fires on SKEW and never on pool size, and **0 of the 42 pre-existing
> surfaces change a single field.**

**RESULT: THREE OF THE FOUR PINS ARE GONE, DELETED BY THE GATE'S OWN STALE-PIN CHECK.** 29-31 **0.0292**,
43-45 **0.0272**, 49-51 **0.0286** - all under the 0.030 global cap unpinned, and the run that proved it
failed with three `D5 STALE PIN` findings naming them, which is the stale-pin discipline doing exactly
its job. One pin remains: `uberorb_default_39-41` at **0.033**, holding a surface that measures 0.0308
after this lane against **0.0338 before it**. The last 3% needs `unique_torso_e01` capped, which 19
pre-existing cage/hoard/apex surfaces also draw from and whose torso mass would fall ~12% against D7's
0.52/open floor - measured, and rejected as the worse trade. The residue is registered as a rewritten
`BL-R181-DEBT-9`: these orb surfaces pay only 2.7-5.8 legendary pieces per open, and a 3% single-item
cap on a surface that thin needs 33+ effective items in every class it pays, against base-game pools
holding 5-9. **N14** plants the bound's defeat and reds.

**THE THREE LOWS, all "a check claimed more reach than it has".** `orb_armor_rows.verify`'s `missing`
check is a cache/rewire detector, not independent coverage evidence - `all_surfaces` derives its orb
surfaces from the same `orb_scope`, so coverage there is by construction, which IS the intent; the
docstring now says which of its three checks proves what, and warns that a PASS is not coverage
evidence. `orb_scope`'s cache key cannot see a write to an ALREADY-modified record, so calling it
closed "by construction" was too strong: it is a narrowing, and the real guarantee is `fresh=True` plus
the `_svc_orb_swept` comparison. And **OWN2 has never executed inside a real build** - it needs
`db._registry_touch_log`, which only exists under `run_registry` - so the ship build is its first live
execution; that is stated in the ship record rather than carried quietly.

> **LAW: A NEGATIVE THAT DOES NOT FIRE MUST NOT SHIP AS THOUGH IT DOES.** The evenness bound's second
> half - handing the surplus to the master - was planted as a negative and came back GREEN: forcing the
> master back to `ARMOR_MASTER_WEIGHT` moves the worst worn-slot yield 0.04517 -> 0.04249 against
> D7b's 0.0375 floor, spending ~6% of the headroom and reding nothing. So no negative ships for it and
> it is labelled what it is - a balance choice inside a margin, `BL-R181-DEBT-11`.

---

## R-230 (Will 2026-08-11, verbatim): "every time we make a new build we should be pushing the code to remote on github"
Standing law: EVERY build ship ends with `git push origin main --tags`. The ship step is not
complete until the push succeeds. Applies to every lane from build84 onward (already baked
into the in-flight b84/b86/b87 ship briefs); doc-only commits push at the next convenient
point, ship commits push immediately.

---

## R-231 [2026-08-11] IMPLEMENTED (branch `feat/charon-rework`, module `tools/patches/charon_rework.py`) - the Golden Bough uber is replaced, not patched. **NAMES FLAGGED FOR WILL VETO.**

### R-231-A - WILL'S ORDER, VERBATIM, AND THE ARTIFACT PROOF THAT HE IS RIGHT

> "the charon uber boss we created needs to be re-worked, he is pretty much identical to the base
> game charon boss we cloned him off. maybe we can replace him with a different uber monster that
> is more unique"

**Do not restate this as "the same guy, bigger" - that diagnosis is wrong and the fix would have
been wrong with it.** `um_charon_ferryman_99` (Charon01.msh, sc 1.7) ALREADY rig-swapped to
`um_charonform2_ferryman_99` (Charon02.msh, sc 1.2). The defect was the KIT, byte-for-byte,
measured on the live build83 arz (51,253 records):

| slot | ours F1 | `boss_charon_43` | ours F2 | `boss_charonform2_43` |
|---|---|---|---|---|
| skillName1 | charon_projectiletrigger | charon_projectiletrigger | charon_projectiletrigger | charon_projectiletrigger |
| skillName4 | charon_selfbuff | charon_selfbuff | charon_selfbuff | charon_selfbuff |
| skillName6 | charon_geyserform1 | charon_geyserform1 | charon_geyserform2 | charon_geyserform2 |
| skillName7 | charon_summon | charon_summon | charon_swoopstomp | charon_swoopstomp |
| skillName8 | - | - | charon_tidalwave | charon_tidalwave |
| specialAttack 1..4 | identical | identical | identical | identical |

The ONLY authored deltas were `characterLife`, four resist floats, `scale`, `actorHeight`, one
aura and a `deathEffect`. `apply_svc_patches._create_goldenbough_boss` said it out loud in its own
comment: *"Keep Charon02's own kit verbatim"*. **R-100 #3 filed this on 2026-07-29** ("needs its own
kit, held to the amgoz1 bar") **and it was never built.** This ruling closes it.

Two further defects the same encounter carried, both now fixed and both gated:

* **BOTH forms shared ONE display tag** (`tagSVCMonsterCharonFerryman`), so the phase turn had no
  name change on screen at all. They are now distinct strings and `verify()` fails if they collide.
* The Champion escort `svc_charon_wraith_99` shipped `characterLife = [878.0, 300.0, 400.0]` -
  **life FALLING from Normal to Epic.** That is R-100 #18 (*"super weak ... they appear just like
  normal guys"*) as a measurable field. Nobody had filed it.

### R-231-B - THE IDENTITY RULING. Charon leaves the Golden Bough forecourt.

> ⚠️ **THE NAMES AND THE PHASE-2 BODY IN THIS SECTION ARE SUPERSEDED BY R-231-E.**
> "Ormenos" turned out to be a live boss already in this database (the China Telkine, 59 records,
> its own soul) and the phase-2 donor turned out to be immobile. Read R-231-E for what ships.
> Everything else in R-231-B stands.

~~**ORMENOS, THE GILDED ROOT** (phase 1) to **ORMENOS, THE BOUGH IN BLOOM** (phase 2, terminal)~~,
now **AKREMON, THE GRASPING ROOT** to **AKREMON, THE HEARTWOOD ABLAZE**,
escorted by two **HANDBRIARS**. **This wave owns the final boss + soul naming under Will's order.**

* **PLANT.** Race census of all 53 Boss-class mod ubers: Undead 18, Demon 14, Beastman 8,
  Insectoid 4, Magical 3, Animal 3, Beast 2, Device 1, **Plant ZERO**. Both forms are Plant.
* **THE ONLY UBER IN THE MOD THAT BUILDS TERRAIN.** `Skill_DefensiveWall` has **zero** carriers
  across the whole uber roster; phase 1 casts `quillwards` (cd 20, spawns `pets\quillvine_12` on a
  10-to-30s TTL ladder) and grows cover between itself and you, while `drx_earthbind` (radius 22,
  cd 20) stops you leaving.
* **THE WOOD DOES NOT BLEED, THE FLOWER DOES.** Phase 1 keeps the donor's native
  `ascacophus_bleeddamageimmunity` (`defensiveBleeding 100.0`), which tells the mod's marquee bleed
  spears to sit down for half the fight; phase 2 does NOT carry it, so that build comes back for
  the kill. *Honest framing: bleed immunity is NOT a roster first - `um_helepolis_99` already
  carries the identical record. It is a first for a LIVING boss.*
* **BEAT 2 IS A REAL PHASE BEAT WITH NO NEW SPAWN TECH.** `svc_bough_splitting`
  (`Skill_PassiveOnLifeBuffSelf`, `lifeMonitorPercent 33.0`, 12s, cd 5) fires ITSELF at 33% life -
  ~~the `um_vashkarr_99` pattern~~ **CORRECTED IN ROUND 3: that citation is REFUTED.**
  `um_vashkarr_99` carries `lowhealth_berserkerrage01` at `skillLevel 0`, i.e. INACTIVE by the mod's
  own B-SOUL-PROC-1 lesson, so it proves nothing. The mechanic is fine and the real live precedents
  are `elder_um_boarmonstrous_16` (`skillLevel 5`) and `elder_am_boar_09` (`skillLevel 3`) on
  `lowhealth_boarberserkerrage01`; this lane wires `svc_bough_splitting` at level 10, inside its
  `skillMaxLevel 15`. (R-231-E measured this and the module's CORRECTION 7 records it, but the
  refuted citation was left standing here, outside R-231-E's supersede banner - which covered only
  "the names and the phase-2 body". A stale claim in the design law of record is a decoy for the
  next agent, so it is corrected in place.) This lane folds the thorn retaliation into that record,
  so the thorns come out WITH the splitting instead of on a random cast roll.
* **NAMES ARE THIS LANE'S INVENTION AND SHIP AS DEFAULTS FLAGGED FOR WILL VETO**, per the standing
  creative-bar rule (the R-125 precedent). Six Will-decisions are listed in the lane report; every
  one is implemented at its recommended value behind a named constant, so none of them blocks.

**ARZ-ONLY. NO MAP REBUILD.** The Golden Bough forecourt placement, `q_goldenbough_lone`, its pool,
`limit_goldenbough`, the one hoard chest, `svc_charon_chest` and the TESTHUB yard twins are all
REUSED. All three guaranteed rewards survive on the terminal: the Golden Bough amulet at
`lootMisc4` / 100%, the hoard, and a soul.

### R-231-C - THE b86 COORDINATION NOTE: **ROW 7 STANDS. NO SUPERSEDE WAS NEEDED.**

The brief for this lane anticipated that row 7 of `docs/SOUL_RENAME_PROPOSAL.md` would have to be
superseded. **It does not, and the next agent must not re-litigate this.** The two records are
different, quoted here so the question is closed:

| | row 7's soul | OUR uber's soul |
|---|---|---|
| record | `records\item\equipmentring\soul\svc_uber\boss_charon_soul_{n,e,l}.dbr` | `records\item\equipmentring\soul\svc_uber\ferryman_soul_{n,e,l}.dbr` |
| tag | `tagSoulSVC9005` (GENERATED by `create_uber_souls`) | `tagSVCSoulFerryman` (hand-designed; in `_HAND_DESIGNED_SOUL_TAGS`) |
| dropper | the BASE-GAME `boss_charon_{39,41,43}` | our uber's terminal form |

They never collided. Our uber vacating the ferryman display namespace entirely **strengthens** row
7's primary (`DISPLAY_NAME_OVERRIDES['boss_charon']`) rather than conflicting with it. **b86 ships
row 7 unchanged.**

### R-231-D - RETIREMENT PROTOCOL: nothing is deleted, and here is why that is the SAFE choice

No record is retired. The three monster records are **rewritten IN PLACE at their existing paths**,
because TQ bakes ITEM paths into saves but not MONSTER paths, and because three separate gates key
on those exact basenames - authoring new paths reds all three:

1. `tools/verify_soul_drop_rates.py` pins `um_charonform2_ferryman_99` to `('PLACED', 33.0)`; a new
   terminal at a new path leaves the old record un-PLACED and its klass flips.
2. `tools/build_svc_database.py:SOUL_RATE_ZERO_PINS` pins the chain HEAD `um_charon_ferryman_99` at 0.
3. `tools/patches/uber_quest_drops.LEAKS[0]` and `tools/patches/red_uber_orbs.EXEMPT` key on the pair.

The record NAMES now lie about their contents. That is registered as `BL-BOUGH-DEBT-1` for a future
breaking build, exactly as the frozen ITEM paths are.

One sanctioned workaround IS retired: `_SUMMON_IDENTITY_ALLOW['ferryman']` is deleted, because the
soul's summon is now the SAME species as its dropper (both **`DRX\meshes\emberoakmesh.msh`**) and
the F2 identity gate - which compares the summon SOURCE's mesh to the DROPPER's mesh - is green with
no exemption. `'voranthys'` stays. If this wave is ever reverted, that gate reds loudly and names
the record, which is the correct alarm.
> **ROUND-3 CORRECTION, in place.** This bullet read `SVMesh/meshes/hellflower.msh` - round-1 text
> left un-updated after R-231-E swapped the phase-2 donor to `um_emberoak_42` for D19 mobility. The
> CONCLUSION was and is correct (the identity gate is green with no exemption, re-proved by running
> `_verify_soul_summon_identity` standalone over the post-rework db), but the ledger is design law
> and a wrong record path in it is a decoy for the next agent.

### THE FIVE SPEC CORRECTIONS THIS LANE MEASURED (the ratified spec was wrong on each)

1. **Cast slots: the spec allocated FOUR new casts on phase 1 and only THREE are free.** The donor
   occupies `specialAttackSkillName` (stumpstomp) and `specialAttack3` (hero_quillvines) - both its
   own-family signature, which R-125 forbids displacing - and the engine caps at five. The thorn
   coat moved onto the beat-2 self-trigger instead; nothing was displaced.
2. **Skill slots:** the donor also occupies `skillName15` and `skillName17`, not just 1-6/10/11/12,
   and it DOES carry `racial_plant` as a skill (the spec said it did not).
3. **`boss_conversionimmunity` IS resolvable** and both shipped forms carry it; the spec told the
   implementer to probe-and-skip. It ships.
4. **THE TERMINAL KEEPS `bosschest02_charon`, AND THIS IS A HARD GATE, NOT TASTE.** The spec's lore
   reading wanted the Charon-named orb gone (b53 did exactly that for Dagon). MEASURED:
   `tools/svc_orb_breadth.py` sets `MIN_PROXIES = 6` / `MIN_TABLES = 18`, `orb_loot_breadth.apply`
   RAISES below either floor, and that scope is derived as "every proxy an UBER names" - and this
   terminal is the ONLY uber naming that proxy. Retargeting it drops the scope to 5/15, reds the
   build, and orphans three tables that `orb_loot_breadth` + `orb_armor_rows` already widened. The
   hellflower donor inherits no chest, so the module SETS it explicitly. `BL-BOUGH-DEBT-4`.
5. **`offensiveTrapMin/Max`** (the spec's soul proc) is carried by **ZERO** of the DB's 2,095 soul
   records and only 32 records DB-wide. The field that means the same thing and that souls actually
   carry is `offensiveSlowPhysicalMin` + `...DurationMin`. That ships instead.

### THE GATE THAT SHIPS WITH THE NEW SURFACE (process law #4)

`charon_rework.verify()`, fail-loud, negative-tested (**28** planted defects plus one apply-time
assert as of round 3 - `py tools/debug/negtest_charon_rework.py` reports 29 RED, 0 gate holes, every
one
RED, restoration proved GREEN after each): the proxy chain resolves to the new boss on BOTH the
forecourt and the TESTHUB yard; all three guaranteed rewards stay wired; A9 (own-rig clones only,
the donor's own skin, no invented `actorHeight` per R-126); the crash laws (no `charFxPak`, no
dangling skill ref, permanent pets TTL-free); **a NEW strictly-ascending-`characterLife` invariant
over EVERY `svc_*` Champion escort in the DB, not just ours** - that is the R-231-A escort defect
made structurally impossible; and an identity gate that reds if any `charon_*` signature skill or
any shared cast rotation ever comes back.

Round 2 added five more, each one the anti-regression for a finding below (R-231-E):
**exactly-one summon-pet registration** naming the terminal's own donor; **D19 mobility** on all six
placed and summoned bodies (nonzero `characterRunSpeed` AND an anim table that actually binds
`unarmedRunAnim` - the second half is the one that matters); **no end-to-end vitality wall**;
**no display-name collision** with a live record family; and **Epic durability inside a band
anchored on the LIVE Gaoler records** rather than a constant, so the band tracks the roster.

---

### R-231-E - ROUND-2 AMENDMENT [2026-08-11]. The vet found eight; the fix found a ninth.

An independent vet of the round-1 module proved a P0 that reds the whole DB build, two P1s, three
P2s and two P3s. Every one is fixed. Fixing them surfaced one more defect nobody had looked for,
and it is the most serious of the set because it would have shipped a duplicate identity.

#### 1. THE NAME WAS ALREADY TAKEN. "Ormenos" is the China Telkine. (found this round)

The ratified spec named this boss **Ormenos**. Measured on the live artifact: `Ormenos` is already a
boss in this database - `boss_chinatelkine_ormenos_{38,41,44}.dbr` - and **59 records** carry the
name, including `controller_ormenos`, six `ormenos_*` boss skills, three `ormenos_magmasprite_*`
summoned minions, `Ormenos_FireSpawn_FX`, and **its own soul** at
`records\item\equipmentring\soul\telkine\ormenos_soul_{n,e,l}.dbr`. `apply_svc_patches.py:1371`
literally maps `('boss_chinatelkine_ormenos', 'Ormenos', 25.0)`.

Shipping a second, unrelated Ormenos - with a second soul - is the duplicate-identity class Will
keeps filing (R-100 #2, the Meritamen/Phagia class, the soul-rename wave). **RULING: the boss is
AKREMON** (the Greek word for a *bough*): zero record hits and zero text-resource hits across the
whole mod, and a tighter lore fit than Ormenos ever had, because the shrine's entire subject is a
bough. `verify()` now carries a collision gate that checks every minted name token against the live
record namespace, so the mistake cannot recur on any future rename.

| surface | ships |
|---|---|
| phase 1 | `{^r}Akremon, the Grasping Root` |
| phase 2, terminal | `{^r}Akremon, the Heartwood Ablaze` |
| Champion escort x2 | `{^G}Handbriar` |
| soul | `{^F}Soul of the Grasping Root` |
| summon skill | `Graft the Burning Heartwood` |
| pet | `Burning Heartwood` |
| hoard chest | `The Orchard of Hands` |

**Still flagged for Will's veto**, same as R-231-B.

#### 2. P0 - the branch did not build. Stale summon-pet registration.

`_build_boss_summon` appended to `_SUMMON_PET_BUILDS`, which is cleared once per run. The monolith's
`_create_goldenbough_boss` builds the three `charon_oarsman_*` pets from `charon_minion_30`; this
module then rebuilds **the same pet records** from its own donor. Both pairs stayed registered, and
`run_registry_gates` runs afterwards and judges the whole list - so PET-STAT-MIRROR compared the
newly-built pets against a source that no longer wrote them and failed the build, and the F2
soul-summon-identity gate failed next for the same reason (which is precisely what the deleted
`_SUMMON_IDENTITY_ALLOW['ferryman']` entry used to paper over).

**Fixed upstream**, because replace-by-pet-path-set is the only semantically correct answer: pet
records on disk can only have been built by their **last** writer. With no duplicate pet set the
behaviour is byte-identical, so this is a pure improvement to the monolith. The module keeps an
idempotent prune, and `verify()` asserts the END STATE - exactly one registration names these pets
and its source is the terminal's own donor - rather than trusting either half. The standalone
negtest now **seeds the monolith's stale pair before `apply()`**, so the trap is exercised for real.

#### 3. P1 - the terminal, both escorts and the soul's permanent pet were all IMMOBILE.

Round 1 built phase 2 from `us_hellflower_37` and the escort from `am_quillvine_35`. Both ship
`characterRunSpeed = 0.0`, and it is **not tunable**: their anim table
`records\creature\monster\quilvine\anm\anm_quilvine.dbr` declares the `*RunAnimSpeed` scalars but
binds **no `unarmedRunAnim` and no `unarmedWalkAnim` clip at all**. Raising the speed would ask the
rig for an animation it does not have - the B-SOUL-PROC-2 / D19 class the crash laws forbid.

So the **terminal form - the body carrying all three guaranteed rewards** - could not chase a player
who simply stood off; the two "escorts" could not escort; and the soul's marquee permanent summon
could never follow its owner. The encounter as built was very likely *easier* than the Charon it
replaces, which is the opposite of Will's order.

**RULING: a placed or summoned body must sit on a rig that BINDS locomotion. A nonzero runSpeed is
not evidence.** Donors swapped to bodies that own a mobile rig while keeping Plant:

| body | round 1 | ships | rig / table |
|---|---|---|---|
| phase 2, terminal | `us_hellflower_37` | **`um_emberoak_42`** | `emberoakmesh.msh` / `anm_bogdweller` |
| Champion escort | `am_quillvine_35` | **`am_junglecreep_41`** | `JungleCreep01.msh` / `anm_junglecreep` |
| phase 1 | `xhero_strongbark_44` | unchanged | `Ascacophus02.msh` / `anm_ascacophus02` |

The ember oak is strictly better on every axis the design cared about: it is mobile; its fire kit is
richer and native (`ringofflame` is a **toggled burning ring it simply wears**, so the fire reads on
screen with zero FX authoring, plus `volcanicorb` with two modifiers, `drxheatshield` and
`emberoak_stoneform`); it keeps Plant so the Plant-is-zero headline stands; its live scale 1.90
makes the 2.0 ask a 1.05x stretch instead of the hellflower's 1.33x; and its rotation puts only ONE
chance-100 cast ahead of our additions instead of three, which is also the structural fix for the
round-1 P2 that the added casts would rarely fire. **Honest cost: the terminal is no longer amgoz1's
own SV hellflower.** The immobile quilvine rig still appears in the fight, in the one role where
being rooted is correct - the `quillwards` wall pets.

Speeds are now written explicitly, two of the three exactly rig-proven, all inside the measured
Boss-uber band (min 0.35 / median 1.00 / max 4.00): **1.35** phase 1 (`credits_ringlesstree` ships
1.35 on that mesh), **1.45** terminal (above this rig's only live carrier at 1.0 - disclosed,
`BL-BOUGH-DEBT-6`), **1.30** escort (`um_speckledjim_45` ships 1.30 on that mesh). The shipped
Charon forms ran 2.8 and 4.0, the two fastest bodies in the entire 53-boss roster; this encounter
deliberately does not chase that outlier.

#### 4. P1 - the D19 assert had its guard inverted on the one case it exists for.

The `apply_svc_patches.py` D19 pet-mobility block read
`if _run_fields and f'{_row}RunAnim' not in _run_fields:`. An anim table with **zero** locomotion
clips yields an empty `_run_fields`, so the condition short-circuited to `False` and **the assert
passed** - it only ever fired on a table that had *some* rows with locomotion but not the pet's row.
That is why three permanently immobile permanent pets were built with no warning. **RULING: the
truthiness test is dropped; a locomotion-less anim table now fails LOUD**, which is what the assert
was written to do.

#### 5. P2 - the vitality wall. `defensiveLife 100` on both forms.

`defensiveLife` is VITALITY resistance. Round 1 shipped 100 on **both** phases, i.e. total vitality
immunity for the entire fight, while the design's headline claim was that the bleed/vitality build
benched by phase 1 gets its kill in phase 2. The claim was false against the artifact.
**RULING: 60 on phase 1, 40 on the terminal**, and `verify()` reds if the terminal is ever walled
again. Bleed immunity stays on phase 1 only: it is the deliberate half-fight lever and Will's
decision 6 - a lever the fight hands back is not a wall.

#### 6. P2 - tempo. The anti-kite lever was one 18% roll on a 20-second cooldown.

Snare `drx_earthbind` 18 -> **40**, wall `quillwards` 15 -> **30**, fan `razorquill_megaburst`
22 -> **35**, on top of the explicit 1.35 runSpeed. The skills' own cooldowns still do the real
spacing; the chances only govern how reliably the boss reaches for them. On the terminal,
`razorquill_nova` 25 -> **50** and `typhon_thornyaura` 15 -> **40**, so the two casts that actually
differentiate phase 2 stop being the least likely things in the fight.

#### 7. DURABILITY, calibrated to the reference frame instead of to nothing.

Round 1 justified its life values as "exact parity with the shipped Charon forms" - 58,000 on Epic -
which was never itself calibrated against anything. `docs/reports/gaoler_variance_rca.md` is the
named frame: the Soul-Gaoler is two forms totalling **35,000 on Epic** *plus a six-strong guard
horde*, and that RCA's verdict is hard-but-fair and killable, "no action warranted".

| | Normal | Epic | Legendary |
|---|---|---|---|
| Akremon (2 forms + 2 Champions) | 27,000 | **35,000** | 46,000 |
| the Gaoler (2 forms + 6 guards) | 26,000 | **35,000** | 47,000 |

Epic matched exactly. The escort goes to `[5000, 7000, 9500]` (ascending, sized off the live
Champion-escort roster). **RULING: uber durability is justified against a named, measured peer, not
against whatever the record happened to say before.** The gate anchors on the LIVE Gaoler records
so the band tracks the roster instead of going stale.

#### 8. P3 - the tallies are re-measured, and one citation was wrong.

Race census re-run on the live artifact: 53 Boss-class `um_*`/`svc_um_*`, Undead 18, Demon 14,
Beastman 8, Insectoid 4, Magical 3, Animal 3, Beast 2, Device 1, **Plant 0** - reproducing the
ratified spec exactly. (A vet pass reported 50 / Demon 12 / Beastman 7 off a different artifact; the
number the design rests on, Plant = 0, holds in both readings.) And the beat-2 precedent was wrong:
`um_vashkarr_99` carries `lowhealth_berserkerrage01` at **`skillLevel 0`**, i.e. inactive by the
mod's own B-SOUL-PROC-1 lesson, so it proved nothing. The live precedent is
`elder_um_boarmonstrous_16` (Champion, level 5) and `elder_am_boar_09` (level 3). The mechanic is
sound; only the citation was bad. **RULING: a number does not enter the design law of record until
it has been measured on the artifact in the wave that writes it down.**

---

### R-231-F - ROUND-3 AMENDMENT [2026-08-11]. The two surfaces the PLAYER KEEPS were still Charon.

An independent vet of the round-2 module proved two P1s, two P2s and three P3s. Every one is fixed.
**Both P1s are the SAME defect class as round 2's P0** - *a superseded writer's output surviving
under the new writer's at a FROZEN path* - and both of them landed on the surfaces a player actually
keeps: the soul in his stash, and the skill on his skill bar.

**RULING, generalised because this is now three occurrences in three rounds:**
> **When a wave rewrites content at a path FROZEN for save-compat, it owns clearing what the earlier
> writer left there. A creator helper that "ensures" a record (`_ensure_record` no-ops when the
> record exists) and a setter that layers keys (`_set_soul_fields`) CANNOT re-theme anything - they
> can only add to it. The gate for such a wave must prove the OLD identity is ABSENT, not merely
> that the new one is PRESENT.**

#### 1. P1 - the soul was RE-LABELLED, not RE-THEMED.

Measured after `apply()` over the live build83 arz: `ferryman_soul_e.dbr` still carried the whole
shipped "Soul of the Unferried" stat block underneath the new one -

`offensiveCold{Min,Max,Modifier}` · `offensiveSlowCold{Min,DurationMin}` · `defensiveCold` ·
`offensiveLife{Min,Max}` (vitality) · `offensiveLifeLeechMin` · `defensiveLifeLeech` ·
`offensiveFear{Min,Max}` · **`offensivePercentCurrentLifeMin`**

- the last being **base Charon's own signature lever** (`charon_geyserform1`, 24 roster carriers),
which the ratified spec forbade on this soul BY NAME. The new fire/pierce block layered on top, so
the tooltip read Cold + Slow + Cold Resist + Vitality + Life Leech + Fear + %Current Life on an item
called *"Soul of the Grasping Root"* dropped by a burning tree, at roughly double the offensive load
anyone had balanced.

**FIX:** `_strip_superseded_soul_stats` clears the superseded bonus-STAT block before `_create_soul`
rebuilds - deliberately SURGICAL (the six stat prefixes `offensive`/`defensive`/`retaliation`/
`character`/`augmentSkill`/`itemSkill`, minus exactly the keys the rebuild is about to write), so
nothing structural is ever in reach and `itemQualityTag` / `itemText` are re-applied afterwards by
`run_registry_gates` finalization, which runs after every registry module. MEASURED: 13 ferryman
fields removed per tier, 13 new ones added, **0 structural losses**. `itemSkill*` is in the prefix
set on purpose - it makes a stale `itemSkillAutoController` (the D19/D21 manual-cast law)
structurally impossible to inherit.

#### 2. P1 - the granted summon still wore Charon's face.

`records\skills\soulskills\summon_charon_oarsman.dbr` shipped
`SVTextures\skills\drownedspirit{up,down}.tex` - a **drowned-ghost** glyph, and a Charon-specific one
(only 3 records in the 51,253-record DB reference `drownedspirit*`) - plus Lyia's
`maenadalertpak` cast sound, under the name *"Graft the Burning Heartwood"*. **R-125's
player-surface law names the icon explicitly**, and this is the icon the player looks at every cast.

**FIX, at the SOURCE OF TRUTH:** `_SUMMON_SKILL_ICON['summon_charon_oarsman']` in
`tools/apply_svc_patches.py` now maps `DRXtextures\skill icons\soul\flamewave{up,down}.tex` - a fire
glyph for a burning ember oak. **This row beats the table's own convention rather than merely meeting
it: it is the first entry with ZERO collisions of any kind.** `flamewave{up,down}` is referenced by
**0 records across EVERY string field of all 51,253** - no other summon, and no other granted skill
either - and both halves are **PRESENT** in the shipped `DRXtextures.arc` (1,463 entries) under
`skill icons/soul/`. Every established row in that table shares its glyph with a live non-summon
skill (`bloodbathup` 3, `thunderorbup` 4, `voidsnapup` 1); this one shares with nothing.

Two alternatives were measured and rejected. `flamering{up,down}` is a tighter 1:1 with the pet's own
`ringofflame` and is PROVEN to render (live carriers `yaoguai_flamering.dbr` + its pcsafe clone) -
but that is a **soul-granted** skill, so a player holding the Yaoguai soul and this one would see one
glyph on two skill-bar buttons, which is the duplicate-identity class Will keeps filing. It stays
documented in the table as the proven-render fallback. `summonquilvine{up,down}` is already claimed
by the live `summon_hellflower.dbr` and is the wrong species since the phase-2 donor became the ember
oak. **Honest residual:** a glyph with zero live carriers has never been seen on screen in this mod
either; a UI icon carries none of the cross-mesh UV risk the 343_dark_smoke lesson is about, no
colour is claimed for it, and one look at the skill bar closes it (`BL-BOUGH-DEBT-10`).
The hit sound goes to the terminal donor's OWN `bogdwelleralertpak` - the `<family>alertpak`
convention every already-fixed summon uses.
**HONEST:** `maenadalertpak` is a **class-wide** residue - `_build_boss_summon` never writes
`skillHitSound`, so **31 of the 52** soul summons in the DB carry it. This lane did not create it and
fixes only its own record; the class is registered as `BL-BOUGH-DEBT-9`.

#### 3. P2 - the scaler swap was blind, and the constant that would have caught it was unused.

`skillName12` was overwritten unconditionally on both boss forms while `_SK_HERO_SCALING` was
declared and referenced nowhere - the intent to verify the swap existed and was never implemented.
Both boss donors do carry `hero_scaling` there, but the ESCORT donor `am_junglecreep_41` carries
`globalproperties_legendary01` in the same slot, so **one future donor swap would have destroyed a
difficulty row with a GREEN gate**. `_swap_scaler` now asserts the incumbent and SystemExits
otherwise. **Honest scope:** `globalproperties_*` rows carry only `characterBaseAttackSpeedTag` plus
UI bitmaps - no stat or resistance scaling - and 8 of the 53 Boss-class ubers declare none at all, so
the shipped shape sits inside the roster norm. Latent-trap fix, not a balance change.

#### 4. P2 - the law-4 build obligations are a SHIP-PHASE constraint, not a code defect.

This lane ran static gates only, per its brief. The b44 landing/clearance gate on
`q_goldenbough_lone`, the full DB build + **COUPLED** Text.arc build, `validate_tags`,
`run_contracts` against the 0/0/4492 baseline, det-2x byte-identity, record-diff and the b86
duplicate-display-name gate are all recorded as `BL-BOUGH-DEBT-8` so the ship phase cannot skip them.

#### 5. P3 x3 - stale claims in this ledger and in the module, corrected in place.

* **R-231-D** said the soul's summon body is `SVMesh/meshes/hellflower.msh`. The shipped body is
  `DRX\meshes\emberoakmesh.msh` (round-1 text left behind by R-231-E's donor swap). The conclusion
  was correct; the path was not.
* **R-231-B** still cited `um_vashkarr_99` as the beat-2 precedent, which R-231-E itself refuted
  (`skillLevel 0` = inactive). R-231-E's supersede banner covered only "the names and the phase-2
  body", so the refuted citation was left standing as if true. Corrected in place.
* The `hero_quillvines` retinue adds are **also** stationary (`quillvine_01..06`, all on
  `anm_quilvine.dbr` at runSpeed 0.0), not just the `quillwards` wall pets. Donor-native,
  unmutated, no crash law touched - but the disclosure named only the wall pets, and "the retinue
  keeps firing" must not be read as "it sends things after you". Both pet families count toward the
  add-density reading owed under `BL-BOUGH-DEBT-2`.

**RULING (process): a stale claim in the design law of record is a decoy for the next agent.** A
supersede banner must either enumerate everything it supersedes or be widened; leaving a refuted
sentence standing under a narrow banner is how a wave re-litigates a question that was already
settled.

#### 6. WHAT WAS ACTUALLY RUN THIS ROUND (static only, per the lane's brief)

All against the live build83 arz (`work/SoulvizierClassic/Database/SoulvizierClassic.arz`, 51,253
records), with the monolith's stale `charon_minion_30` pet registration SEEDED so the harness sees
the real build state:

| reading | result |
|---|---|
| `charon_rework.apply()` + `verify()` | GREEN |
| soul re-theme, PRE/POST field diff, all 3 tiers | **13 ferryman fields removed per tier, 13 new added, 0 structural losses** (`itemText` / `itemQualityTag` / `bitmap` / `mesh` / `Class` all intact) |
| granted summon | icon `drownedspirit*` -> `flamewave*`; `skillHitSound` `maenadalertpak` -> `bogdwelleralertpak` |
| `_verify_soul_summon_identity` (F2) | GREEN **with no `ferryman` exemption**, stale pair seeded |
| `_verify_soul_augments_resolve` | GREEN |
| `_verify_no_unclassified_soul_leaks` | GREEN |
| `_verify_soul_itemskill_activation` | GREEN |
| `_verify_granted_skill_diversity` | GREEN |
| `_verify_no_supra_dead_refs` | GREEN |
| `_verify_boss_orbs` | GREEN |
| `patches.selfcheck()` | OK, 60 modules, order `96d61e6f2b0ce307` |
| `negtest_charon_rework.py` | **29 RED, 0 gate holes**, every restoration proved GREEN |

**NOT RUN, and blocking the ship phase, not this lane:** the b44 landing/clearance gate, the full DB
build, the COUPLED Text.arc build, `validate_tags`, `run_contracts`, det-2x and record-diff. All six
are enumerated in `BL-BOUGH-DEBT-8` so they cannot be skipped.

---

### R-231-G - ROUND-4 AMENDMENT [2026-08-11]. **THE NUMBERS NOBODY AUTHORED.**

Round 3 fixed superseded WRITERS surviving at frozen paths. Round 4 fixes the mirror defect:
**a donor's own payload riding along under a claim that did not mention it.** Five findings, one
class, and the biggest one was still unmeasured after the vet's report.

> **RULING (process, and the reason this section exists):** *when a lane clones a record and then
> states a number about the result, it owns EVERY non-zero field in that record, not just the ones
> it wrote.* A verbatim clone is not a neutral starting point - it is a set of authored decisions
> made by somebody else for a different creature. Three of this lane's five round-4 findings were
> invisible precisely because nobody diffed the donor's own values against the claim being made.
> The standing fix is the one applied below: **author the value, or state the inherited one.**

#### 1. P1 - BEAT 2 WAS SILENTLY A 36% DAMAGE SHIELD. THE VET CAUGHT TWO OF THREE.

`svc_bough_splitting` was a verbatim clone of `lowhealth_berserkerrage01`, whose `ActorName` is
`DefensiveMastery_Adrenaline`, wired on phase 1 at `skillLevel 10`. MEASURED on the live build83
arz, the donor carries **three** non-zero 20-row level arrays and the clone inherited all three:

| field | donor array | row 9 (= the wired level 10) | disclosed anywhere? |
|---|---|---|---|
| `damageAbsorptionPercent` | `[10,12,15,18,22,24,26,29,32,36,...,65]` | **36.0% flat absorption** | no |
| `characterLifeRegen` | `[5,5,6,6,6,7,7,7,8,8,...,11]` | **8.0/s regen** | no |
| `offensivePhysicalModifier` | `[15,20,25,30,35,40,45,50,55,60,...,110]` | **+60% physical damage** | **no - and the vet did not catch this one either** |

With `lifeMonitorPercent 33.0`, `skillActiveDuration 12.0` and `skillCooldownTime 5.0` (cooldown
SHORTER than duration) it is **permanently up for the whole last third of phase 1**. Meanwhile the
claim repeated verbatim in the module header, in R-231-E #7 and in the BACKLOG player-surface
checklist is *"Epic total 35,000, matching the Gaoler's 35,000 exactly"* - a figure computed from
`characterLife` alone. Phase 1's last 5,610 Epic HP actually cost about **56% more damage** than
that number stated.

**RULED - author all three, as FLAT 20-ROW ARRAYS so no future retune of `_SPLIT_LEVEL` can
mis-index back into a donor value:**

* `damageAbsorptionPercent` -> **0.0**. The durability claim is now true as written. A boss that
  ALSO shrugs off a third of incoming damage is a wall, and the order asked for a hard fight.
* `characterLifeRegen` -> **0.0**. A boss healing during its own last third is the
  "unkillable, then killable" shape `gaoler_variance_rca.md` exists to prevent.
* `offensivePhysicalModifier` -> **35.0, KEPT AND STATED**. Beat 2 must DO something or it is a
  cosmetic bark-crack, and an enrage that hits HARDER is the correct half of an Adrenaline donor to
  keep: it costs the player time, not immunity. 35 is this lane's number, not the donor's
  accidental 60, and `verify()` asserts it on every one of the 20 rows.

Context, measured: only 3 of the 53 Boss-class mod ubers carry ANY `Skill_PassiveOnLifeBuffSelf` -
`um_bloodcrow_50` (lvl 3), `um_bloodtoxeus_99` (lvl 4) and `um_vashkarr_99` (lvl **0** = inactive,
exactly as R-231-E CORRECTION 7 states). At level 10 the verbatim clone would have been the
strongest low-health self-buff on the roster by a wide margin.

#### 2. P2 - THE TERMINAL'S ORDINARY LOOT BAND REGRESSED A FULL ACT.

The re-clone from `um_emberoak_42` (a DRX **act-2/3** creature) replaced this encounter's
Hades-tier tables with the donor's own: `n_03_unique_all` + `item\materials\jungleroot`;
`03_*_misc`; `relic_15-21 / 41-45 / 57-61`; `01/02/03_act2_arcaneformulae`.

**PHASE 1 of this same encounter was already correct** (`n_04_unique_all`, `04_*_misc`,
`01/02/03_act4_relics`, act-4 formulae - the strongbark donor's own), so the two halves of one boss
were banded a full act apart, and **the LOW one was the form carrying the Golden Bough, the soul
and the orb**. The peer band is not a guess: `um_polisgaoler_unbound_99` - the very boss this lane
anchors durability to - runs `01/02/03_act4_relics` + `01/02/03_act4_arcaneformulae`.

**RULED:** the terminal's `Misc1/2/3` are retargeted onto the act-4 band by named constant
(`_ACT4_UNIQUE` / `_ACT4_MISC` / `_ACT4_RELICS` / `_ACT4_FORMULAE`), and the two act-3 `jungleroot`
crafting rows are muted by weight - a jungle root does not fall off a burning tree at the Styx.
The three GUARANTEED rewards were never affected and are unchanged.

#### 3. P2 - PHASE 1 WENT FROM DROPPING NOTHING TO A 75/13/1.6 ROLL. NOW IT IS A DECISION.

MEASURED: the shipped `um_charon_ferryman_99` had **no Misc loot at all**. The strongbark re-clone
inherited its full table (`Misc3 @75`, `Misc2 @13`, `Misc1 @1.6`). Defensible in isolation - every
other transform shell drops, and this roll is byte-for-byte the Mnemophage shell's shape - but it
is an **encounter-level loot INCREASE**, on the exact encounter behind Will's own R-100 #10
complaint (*"the uber monster soul of the unferried also had three chests"*, which R-108 answered
by cutting three chests to one), shipping in the same window as b84 `fix/loot-volume-trim`.

**RULED: MUTED**, back to the shipped shell's own shape, behind `_ORM_MUTE_MISC` so it reverses in
one line. ~~This wave therefore does **not** raise the encounter's ordinary loot volume in any
direction a trim lane would have to re-trim~~, and the terminal - now correctly banded per #2 - is
where the payout lives. Verified: no breadth module derives scope from a monster's `lootMisc*`
pointers (`orb_loot_breadth` keys on `treasureProxyName`; b84's `svc_loot_volume` is
container-scoped), so muting the CHANCE orphans nothing.

> 🔴 **THE STRUCK SENTENCE WAS FALSE WHEN WRITTEN. CORRECTED BY R-231-H #2 (round 5).** This round
> measured the SHELL and never measured the TERMINAL. #2 above re-banded the terminal's *tables*
> and never looked at its *chances*, which are the volume: it shipped
> `chanceToEquipMisc1/2/3 = 1.6 / 100.0 / 75.0` inherited verbatim from the `um_emberoak_42`
> re-clone, i.e. **the encounter went 0 -> 176.6**, a guaranteed potion every kill plus a 75%
> relic/formula roll, in the same window as - and against a written statement issued to - the b84
> trim lane. Round 5 muted the terminal too, so the sentence is now true of the shipped artifact;
> it was not true of round 4's. Table banding and slot chance are two different measurements and
> this lane needed both.

#### 4. P2 - `docs/WILL_TEST_GUIDE.md` WAS NOT UPDATED, UNDER A CHECKLIST CLAIMING "NONE SILENTLY DEFERRED".

The document Will actually reads to test the thing this wave built still described *"Charon, the
Unferried ... TWO PHASES, ~60k total; drowned-oarsman escorts; ... the Ferryman's Toll hoard"*.
Every clause was false: Akremon the Grasping Root / the Heartwood Ablaze, **35,000** on Epic,
Handbriar champions, Soul of the Grasping Root, and a hoard now labelled **"The Orchard of Hands"** -
so Will would have hunted for a chest label that no longer exists. Both sibling lanes (b84, b86)
update this file; this one did not.

**RULED, and fixed beyond the finding:** the entry is rewritten to describe the actual fight and to
name the one number most worth checking in play (the Gaoler-matched 35,000). Also found and fixed
while sweeping the same file - **a live player surface nobody had flagged**: the Helos/TESTHUB
traveler NPC is named through the tags pipeline as `'Traveler: Golden Bough (Charon)'`
(`HELOS_HUB_OUTBOUND`, `tagSVCNpcTravCharon`). Retargeted to `(Akremon)` at the source of truth -
STRING only, record path and tag KEY frozen, so no map rebuild is implied.

#### 5. P3 - THREE STALE OPERATOR/FLAVOUR SURFACES.

* `tools/debug/gate_uber_placement.py:117,169` still labelled the encounter *"M6 Charon / Soul of
  the Unferried"*. The asserted half of the tuple is the AREA name, so the gate still passed - but
  it is the gate a future agent reads to find this encounter. Relabelled.
* **The Handbriar's entire rotation was beetle bile.** `am_junglecreep_41` was chosen for its rig
  and its D19 mobility (R-231-E #3), never for its kit, and it ships exactly one cast:
  `beetlebile_vomitbile`, a five-projectile POISON burst at MediumRange - under docs calling the
  escort *"a ground-hugging whipping vine ... maximum silhouette contrast"*. **RULED:** the declared
  slot and the cast both move to `quillvine_barb` (physical + `offensivePierceRatioMin 50`), whose
  seven live carriers are `quillvine_01..06` - **the very bodies the boss's own `quillwards` wall
  and `hero_quillvines` retinue put on the field**. The escorts now fire the same barb as the briar
  the boss grows: the R-125 own-family bar satisfied at the ENCOUNTER level rather than the donor
  level. HONEST: this is also a NERF in raw output (5 x 159/183/207 poison -> one barb at
  245/263/300 physical), which is the right direction for an add beside a Gaoler-calibrated boss.
* **The soul pets lost their difficulty rows, and `_swap_scaler`'s own discipline had never been
  applied to the pets it was written for.** `_build_boss_summon` -> `_update_existing_fields`
  overwrote the Lyia baseline's slots from the emberoak SOURCE, so the three pets took a MONSTER's
  `hero_scaling` and lost `globalproperties_normal01` / `_epic01` / `_legendary01`. Gameplay impact
  is nil by R-231-F CORRECTION 13's own measurement, but it is residue on a permanent player pet.
  **RULED:** `_restore_pet_difficulty_rows` asserts `hero_scaling` IS the incumbent, swaps
  `globalproperties_normal01` into that slot with the shipped `[1,0,0]` vector, and re-adds the
  other two. End state = the SHIPPED pet shape, i.e. a strict non-regression.
* Also corrected, monolith-wide: `_build_boss_summon`'s log line claimed the anim strip left *"the
  source anm table now drives the body"*. It does not - the strip is SOURCE-FAITHFUL by design, so
  the source's OWN weapon-row overrides survive, and on this donor some point at a foreign rig
  (`staffWalkAnim = ...\Neanderthal_Run.anm`; unreachable at `loadout=None`, and class-wide - 16 of
  the 237 soulskill pets carry the same clip). The line now states what the function actually did.

#### 6. WHAT WAS RUN THIS ROUND (static only, per the lane's brief)

All against the live build83 arz (51,253 records), monolith stale-pet registration SEEDED:

| reading | result |
|---|---|
| `charon_rework.apply()` + `verify()` | GREEN |
| `negtest_charon_rework.py` | ~~41 RED~~ **44 RED, 0 gate holes** (42 planted + 2 apply-time asserts), every restoration proved GREEN. *The "41" recorded here was stale - corrected by R-231-H #7, which re-ran the harness and counted `^neg(` in the round-4 commit (`bdcc411`) to confirm 42. On a lane whose whole discipline is that every recorded number is measured, an unmeasured one in the evidence table is the worst place for it.* |
| post-apply field dump of all 5 fixes | absorption `[20 rows, all 0.0]`, regen `[20 rows, all 0.0]`, phys-mod `[20 rows, all 35.0]`; terminal Misc1/2/3 on the act-4 band with both jungleroot weights 0; shell `chanceToEquipMisc1/2/3 = [0,0,0]`; escort casts `quillvine_barb` with 0 beetle-bile; pets carry `[1,0,0]/[0,1,0]/[0,0,1]` and 0 `hero_scaling` |
| durability, unchanged | `[13000,17000,22000]` + `[14000,18000,24000]` = **35,000 Epic**, and now that number is the whole story |

**STILL NOT RUN, and still blocking the ship phase, not this lane:** the b44 landing/clearance
gate, the full DB build, the COUPLED Text.arc build, `validate_tags`, `run_contracts`, det-2x and
record-diff. All enumerated in `BL-BOUGH-DEBT-8`.

**Names remain this lane's invention and ship as defaults flagged for Will veto** (R-231-B).

---

### R-231-H - ROUND-5 AMENDMENT [2026-08-11]. **THE FIELDS AND THE PROFILE NOBODY MEASURED.**

Eight vet findings, all eight fixed. Every one was reproduced independently against the live
build83 arz (51,253 records) **before** anything was edited, and measuring the first P1 the way its
own fix demanded turned up **two more defects of the identical class that nobody had reported**.
That is the round's lesson: the reported bug was "one field has the wrong name", and the honest fix
for it was "prove every authored number against its own peers", which is a different and much
larger job.

#### 1. P1 - THE SOUL'S DOWNSIDE WAS ON THE WRONG FIELD, AND TWO MORE WERE OFF THE MAP

`characterRunSpeed` is the **creature locomotion scalar**. Measured over the 2,453 peer souls under
`records\item\equipmentring\soul`: 2,158 carriers, band **[0.00, 1.28]**, **zero negatives**. The
**item** movement-percent field is `characterRunSpeedModifier`: 2,224 carriers, **155 negative**,
band [-28.00, 45.00] - and `mnemophage_soul_{n,e,l}`, the mod's own hand-designed uber soul and
this one's direct roster neighbour, ships **exactly -8.0 / -6.0 / -5.0** there. So round 3 wrote
the right three numbers into the wrong field: the movement penalty asserted in the module header,
in R-231-F and in `WILL_TEST_GUIDE.md` **did not exist**, and a negative absolute run speed shipped
on a permanently-equipped item instead. Also refuted: the "Tantalus/Ephialtes tradition" cited as
precedent - `tantalus_soul_*` carries **neither** field.

Then, banding the whole authored block rather than the one reported field:

| authored | value | live peer band | verdict |
|---|---|---|---|
| `characterRunSpeed` | -8 / -6 / -5 | [0.00, 1.28], 2,158 carriers, 0 negative | **wrong field** |
| `offensiveSlowPhysicalMin` | 22 / 31.2 / 40 | [0.00, **8.00**], only **3 of 2,095** carriers non-zero | **5x the live ceiling** |
| `offensiveSlowPhysicalDurationMin` | 3.0 | [0.00, **0.00**] - *every* one of 2,095 carriers ships 0.0 | **inert family** |

Round 3 chose `offensiveSlowPhysical*` because 2,095 souls *carry* the field. **Carrying a field is
not using it.** The family the mod actually snares with is `offensiveSlowRunSpeed*`: 46 non-zero
carriers, band [0.00, 79.00] with durations [0.00, 4.00], and the top of that list is precisely the
hand-designed souls this one belongs beside (`thebloatedone` 79.0/4.0s, `meglograi` 75.0/3.0s,
`camelbane` 71.0/4.0s). **RULED:** the snare moves onto `offensiveSlowRunSpeedMin` +
`offensiveSlowRunSpeedDurationMin` (58.0 legendary, 2.0/2.5/3.0s), the penalty moves onto
`characterRunSpeedModifier`, and a new gate proves **every** authored soul stat is a field peers
carry, at a value inside their measured band, with a name ban on both refuted families.

#### 2. P1 - THE ENCOUNTER'S ORDINARY LOOT WENT 0 -> 176.6 WHILE R-231-G #3 SAID IT DID NOT

See the correction box on R-231-G #3. **RULED: MUTED**, not kept, behind `_BLOOM_MUTE_MISC`.

This is a **decision, not a correctness fix**, and it is recorded as one. 176.6 is defensible on
peer parity - it is exactly `um_ephialtes_99` / `um_mnemophage_99` / `um_helepolis_99`, against a
53-boss roster whose median is 4.5 - so keeping it would have been arguable. It is muted because
(a) the shipped encounter paid exactly **zero** on both forms and this lane's stated discipline is
zero balance drift, so the vet's job stays identity rather than numbers; (b) it keeps the written
coordination statement issued to the in-flight b84 trim lane **true as issued**, which is worth
more than 176.6 of Misc roll; and (c) the encounter's payout is *designed* as the guaranteed Golden
Bough (Misc4 100%) + the dedicated hoard chest + the soul + the boss orb, and ordinary Misc rolls
were never part of it. `Misc4` is deliberately **not** in `_MUTED_MISC_SLOTS`, and a gate asserts
that the mute never eats the Bough. **Will can flip `_BLOOM_MUTE_MISC` to `False` in one line** if
he wants roster parity instead.

#### 3. P2 - BOTH FORMS' SIGNATURE LEVERS WERE MANA-GATED ON BODIES THAT DO NOT REGENERATE

MEASURED post-apply: phase 1 carried `characterMana 3000` / `characterManaRegen 0.0`, both
inherited from `xhero_strongbark_44` and never written, against a rotation costing **312.0** at the
wired levels (`drx_earthbind` 172.0 + `quillwards` 140.0; stumpstomp, `hero_quillvines` and
`razorquill_megaburst` are free). **3000 / 312 = ~9.6 cycles**, after which the snare and the wall
- the two things the whole design rests on - are dead for the rest of the fight, and "ZERO other
uber fields a `Skill_DefensiveWall`" plus "you cannot kite this fight" quietly become "for the
first ten casts". **The vet flagged phase 1; the terminal was worse and nobody had reached it:**
mana 1177 / regen 5.0 against a 417.0 rotation = ~2.8 cycles.

Roster context: 46 of 53 Boss ubers carry mana-costing casts and only 2 run regen <= 0. The
calibration reference `um_polisgaoler_99` is 3000 + 2.0 against a 326 rotation; the Charon this
replaces ran 8000 + 50.0. **RULED:** pool = the Gaoler's 3000 on both forms; regen sized by a
stated rule - `regen >= rotation_cost / 20s`, the cooldown that spaces the rotation - giving 16.0
and 21.0. **This is not a durability wall:** mana regen adds zero effective HP and only keeps the
boss casting the things that make it this boss, and both numbers sit far under the shipped Charon's.
The gate **recomputes the rotation cost off the final record at final wired levels**, so a future
skill or level retune that outruns the pool reds instead of shipping a boss that goes quiet.

#### 4. P2 - THE WHOLE CC / ELEMENTAL PROFILE CHANGED SILENTLY, INCLUDING AN INHERITED 300% STUN WALL

MEASURED, record block plus every skill grant at its wired level:

| | Stun | Freeze | Petrify | Trap | Cold | Fire |
|---|---|---|---|---|---|---|
| SHIPPED, both forms | 100 | 100 | 100 | 80 | 60 | 30 |
| ROUND 4, phase 1 | 50 | **0** | 150 | **0** | -30 | -30 |
| ROUND 4, terminal | **300** | **0** | 100 | **0** | -30 | 70 |

Two defects in one measurement: **freeze-lock became available on both forms** where the shipped
encounter was immune, and the terminal simultaneously inherited a hard **300% stun wall** from
`hero_fire` - on a wave whose CORRECTION 10 headline is *NO WALLS* and whose round-4 thesis is
*"a donor's own payload riding along under a claim that did not mention it"*. Nothing in the
module, in R-231 or in the BACKLOG mentioned any of it.

**RULED.** `hero_fire` is a **shared base record**, so it is never mutated - it is swapped out of
its own declared slot for the strongbark's `elementalresistance_10xlevel` (the same passive this
encounter already fields on phase 1; +10 elemental, zero CC grant), and the +40 fire it used to
hand over is authored on the record instead. An explicit CC floor is authored on both forms at
**Stun 75 / Freeze 60 / Trap 60 effective** - deliberately **resistant, not immune**, because an
uber a Warfare player can perma-stun is not a fight and a 100 wall is the shipped Charon's answer
this lane rejected. The gate asserts the **effective** value (record + every grant at its wired
level), so the axis is pinned against any future donor, skill or level change.

**DISCLOSED rather than fixed, and gated to the disclosed number:** *Petrify* lands at 150 on phase
1 and 100 on the terminal, entirely from roster-standard uber skills (`boss_conversionimmunity`
+100, which is what stops a player converting the boss, and the donor's bleed immunity +50). That
axis genuinely **is** a wall; it is inherited roster-wide rather than authored here, and it is
written down instead of left for the next vet.

**PROMOTED FROM ACCIDENT TO DESIGN:** `racial_plant` hands both forms **-30 fire and -30 cold**. On
phase 1 that is now *the point* - the tree burns - so the fire build that trivialises beat 1 has to
be put down for beat 3, which is the same inversion the bleed immunity runs in the other direction.
The terminal buys fire back to +70 on the record. Both numbers are asserted, not merely tolerated.

#### 5. P3 - BEAT 2 STILL WORE ITS DONOR'S FACE

`svc_bough_splitting` still shipped `skillActivatedAuraName = Skill_Adrenaline_FX01` +
`targetFxPakName = Buff07` + `ActorName = DefensiveMastery_Adrenaline`. Round 4 authored all three
of the donor's stat arrays and left its **visuals**, so the one beat this round is *named* after
("the bark comes apart and the thorns come out") rendered the player Defence-mastery Adrenaline
buff aura. Repointed onto `Typhon_Thorn_CharFXPak` - the FX of the mechanic the beat actually
grants (retaliation pierce = thorns), and the exact value `typhon_thornyaura` already ships in all
three of its own FX fields, a skill this module wires onto the terminal. Base-resolved exactly like
the value it replaces (**both** measured absent from the mod arz), so no new resolution class and
no new art asset. **Not a crash-law surface:** the record is `Skill_PassiveOnLifeBuffSelf`, never a
`Skill_SpawnPet`, and no monster record gains a `charFxPak` field.

#### 6. P3 - R-126 HAD A BLIND SPOT ON THIS MODULE'S OWN OUTPUT

The three permanent soul pets are rebuilt by this wave onto `DRX\meshes\emberoakmesh.msh`, whose
only live carrier ships `actorHeight 1.0`, and kept the Lyia baseline's **2.0** - because
`_build_boss_summon` writes mesh and baseTexture but never `actorHeight`. Not a regression (the
shipped oarsmen were 2.0 too, on CharonGhost.msh) and the impact is targeting / health-bar
anchoring rather than render, but **the invariant this module is proudest of did not cover the
bodies it builds**. Value read off the donor, never invented; the gate now covers all six bodies.

#### 7. P3 - TWO DISCLOSURES CORRECTED

* **The retinue's faucet.** Phase 1 keeps `hero_quillvines` as its R-125 own-family retinue. Its
  six spawns (`...\summoning\pets\quillvine_01..06.dbr`) each ship `dropItems 1` +
  `chanceToEquipMisc1 3.0` on the act-3 table `01_act3_vinygrowth.dbr`. These are **shared
  base-game records** used by the stock ascacophus heroes, so this lane does not mutate them - but
  "this wave does not raise the encounter's ordinary loot volume" is only true of the records it
  **owns**, and that is now how it is written. A gate reads all six and pins the disclosed number.
* **The negtest count.** See the correction on the R-231-G evidence table: 44, not 41.

#### 8. THE ONE THIS ROUND CAUSED ITSELF, CAUGHT BY ITS OWN HARNESS

Muting the terminal's slot chances (#2) **silently switched the existing under-band TABLE gate
off**, because that gate required `chanceToEquipMisc{i} > 0` before it would consider a row
reachable. The standing negative *"the act-3 jungleroot row un-muted at the Styx"* went **GREEN**.
Measured, not reasoned about. The mute is a reversible decision behind a named constant, and the
stated reason the act-4 retarget lives underneath it is that an un-mute has to land on the right
band - so for the records this module mutes, the tables are now judged on their own merit and only
the per-ITEM weight gates. **A fix that blinds a gate is not a fix**, and it took a planted
negative to say so.

#### 9. WHAT WAS RUN THIS ROUND (static only, per the lane's brief)

All against the live build83 arz (51,253 records), monolith stale-pet registration SEEDED:

| reading | result |
|---|---|
| `charon_rework.apply()` + `verify()` | **GREEN** (~40s wall including the full arz decode) |
| `negtest_charon_rework.py` | **66 RED, 0 gate holes** (64 planted + 2 apply-time asserts), every restoration proved GREEN, harness complete |
| post-apply field dump, all 8 fixes | soul `characterRunSpeedModifier = -8/-6/-5` with `characterRunSpeed` **absent**; snare on `offensiveSlowRunSpeedMin`; terminal `chanceToEquipMisc1/2/3 = [0,0,0]` with `Misc4 = 100.0`; mana `3000/16.0` and `3000/21.0`; effective Stun/Freeze/Trap = 75/60/60 both forms with `hero_fire` gone; split FX on the thorn pak; pets `actorHeight 1.0` |
| durability, **unchanged** | `[13000,17000,22000]` + `[14000,18000,24000]` = **35,000 Epic** vs the Gaoler's 35,000 |

**STILL NOT RUN, and still blocking the ship phase, not this lane:** the b44 landing/clearance
gate, the full DB build, the COUPLED Text.arc build, `validate_tags`, `run_contracts`, det-2x and
record-diff. All enumerated in `BL-BOUGH-DEBT-8`.

**Names remain this lane's invention and ship as defaults flagged for Will veto** (R-231-B).

---

### R-231-I - ROUND-6 AMENDMENT [2026-08-12]. THE SHIP GATES WERE RUN - and the lane was NOT arz-only. Ships as BUILD85.

Rounds 1-5 ran static gates only (apply()+verify() on a finished arz). Round 6 ran the REAL
ones on `main` fast-forwarded to build84 (`f989a3b`) with this lane merged: the full DB build
from upstream, the COUPLED `Text.arc` build, `validate_tags`, `run_contracts`, det-2x and
record-diff. Three things the static path had HIDDEN surfaced; all three are fixed at source.

1. **THE FULL DB BUILD DID NOT COMPLETE (P0, FIXED).** `verify()`'s SOUL BAND GATE walks
   ~2,450 peer souls through `_one()`, and in a real full IN-MEMORY build some peers carry an
   empty-list stat field; `_one()` did `v[0]` on `[]` -> uncaught IndexError -> `run_registry_
   verifies` aborted and NO arz was written. The arz write+reload drops empty-list fields, so the
   round-5 apply-onto-a-finished-arz harness never saw it. REPRODUCED (an unfixed full build
   crashed at `charon_rework.py:1063`, no arz landed). FIX: `_one()` treats `[]` as absent.

2. **verify() RED WITH 9 PROBLEMS - and it was verify(), NOT the content (P0, FIXED).** With the
   crash guarded, the CC/elemental/petrify/mobility gate failed: phase-1 effective stun 25 (vs 75),
   fire/cold 0 (vs -30), terminal fire 100 (vs 70), petrify 100 (vs 150), and three D19 reds
   claiming Ascacophus02/BogDweller/JungleCreep bind NO unarmedRunAnim. ALL nine are ONE bug and it
   is not the authoring: `ArzDatabase` keys records case-SENSITIVELY, but a donor's inherited
   `skillName*` / `charAnimationTableName` VALUE is stored in the upstream's own case (e.g.
   `Records\XPack\...\ANM_Ascacophus02.dbr`) while the referenced record's key is lowercase.
   `resolves()` matched case-INSENSITIVELY and said "present", but the follow-on `get_fields()/
   get_field_value()` did a raw case-SENSITIVE lookup and MISSED - so every donor-inherited grant
   read as zero and every anim table read as binding no locomotion clip. The engine resolves paths
   case-INSENSITIVELY and `write_arz` lowercases keys, so the SHIPPED bytes and the game are
   correct: MEASURED on the built arz, effective **Stun 75 / Freeze 60 / Trap 60**, phase-1
   **fire/cold -30**, terminal **fire +70**, **petrify 150/100** - exactly WILL-DECISION 13 - and
   all three placed bodies D19-mobile. FIX: `verify()` reads referenced records through a
   `_canon()` resolver (lowercased name -> actual stored key). Zero shipped bytes change - a
   read-only gate. Proven on the live arz: a mixed-case ref makes get_fields RunAnim `[]` and
   defensiveStun `None`; through `_canon` they are `['unarmedRunAnim']` and `50.0`.

3. **THE LANE IS NOT "arz-only" - it is arz + a COUPLED Text.arc, no map rebuild (FIXED).** The
   module mints one tag key (`tagSVCMonsterAkremonBlaze`) and rewrites seven `tagSVC*` strings.
   Shipped against the frozen `Text.arc` (a9fed7ba) the terminal renders a RAW TAG and phase-1/
   escort/soul/summon keep the OLD Charon strings - **PROVEN**: `C-RES-TAG-1` reds **1 P1
   (mod-owned tag absent)** against the frozen text, and `validate_tags` FALSE-PASSES because the
   stale build84 manifest omits the minted key (finding 6). The names REQUIRE the coupled
   `Text.arc` build the standing "arz+Text ship together" rule already mandates; "arz-only" only
   ever meant "no Levels/Quests rebuild" (frozen proxy chain reused, canonical `Levels.arc`
   6784cf0f byte-unchanged). The rewritten `tagSVC*` keys are absent from SV 0.98i's own Text_EN.arc,
   so the uber-tag section is their sole definition and the rename lands cleanly (0 duplicate-tag
   conflicts). With the coupled `Text.arc` built: all 7 rewritten/minted tags carry the new Akremon
   strings, `validate_tags` PASSES honestly on the FRESH manifest, and `C-RES-TAG-1` is clean.

**RESULT (build84 @ f989a3b + this lane):** full DB build COMPLETES; all registry verifies GREEN
incl. `charon_rework.verify: OK`; coupled `Text.arc` built; `validate_tags` PASS (rebuilt) / demo-
FAIL signal (frozen); `run_contracts` **0 P0 / 0 P1 / 4510 P2 = the build84 baseline exactly, ZERO
new violations**; record-diff = **ADDED 1 (`svc_bough_splitting`) + MODIFIED 14 = the 15-record lane
footprint, zero unexplained**, build84's loot records untouched. `BL-BOUGH-DEBT-8` items 2-5 are now
RUN. Ships as **BUILD85** (next sequential after build84; the "b87" codename in old notes is a dev
name). Two fixes committed on `feat/charon-rework`; the Steam upload + push are the MAIN SESSION's.

> **NUMBERING NOTE (2026-08-11): these two rulings were R-230 and R-231 for most of their lane, and
> moved here under this ledger's own precedent - the LIVE ruling keeps its number, the newcomer moves
> to the next free slot.** Three branches had minted into the same range on the same day: `main` took
> **R-230** for Will's push-per-build law, `feat/charon-rework` took **R-231** for the Golden Bough
> rework, and this lane held both. This lane was the only one colliding with two others and the only
> one that could be renumbered without editing somebody else's in-flight branch, so it took the free
> decade wholesale and in order. 190 references moved, zero old ids left, and the counts before and
> after match exactly (107 and 37).
>
> **R-240 and R-241 are now CLAIMED. The next free ruling number is R-242** - and the lesson for the
> next lane is the cheap one: **check every branch, not just `main`, before minting an id**, because
> `git grep '^## R-' main` would have said R-231 was free and it was not.

## R-240 [2026-08-11] IMPLEMENTED (branch `fix/loot-volume-trim`, module `tools/patches/loot_volume_trim.py`) - the chests pay a RUN's worth, not a vendor's stock; the TESTHUB farm keeps its own

> **AMENDED BY R-247.7a (2026-08-13, scope carve-out - NOT a repeal):** the three Devourer-stash
> tables `loottable_hidden_bloodcave_{01,02,03}` (the blood-cave "Toxeus the Murderer, Devourer of
> Blood's Stash" Majestic chest) LEAVE this ruling's trim scope and its V1 canonical ceiling
> (`svc_loot_volume.R247_STASH_EXEMPT`); Will 2026-08-13, verbatim: "wtf did you do to all the chests
> like toxeus the murderer devourer of blood's stash? Revert it back to what it was dropping in the
> original sv you nerfed the fuck out of it." Their numSpawn equations are restored to the SV 0.98i
> originals (`*3.8/*4.1`) by `tools/patches/r247_bloodcave_rulings.py`, which becomes the single
> volume authority for exactly those three records. EVERY other surface (cage, hoards, orbs, world
> loot) stays under this ruling unchanged. Full measurement + supersession text: R-247 part 7.

> "we probably need to trip the loot-volume trim, especially on the steam version where maybe from
> the two chests, you get guaranteed 1 legendary item. on the testhub version we can spawn more that
> is fine."

**THIS IS THE SAY-SO `BL-R181-DEBT-5` WAS WAITING FOR, AND THE DEBT SAID SO IN ADVANCE.** R-181,
verbatim: *"numSpawn is the volume lever, and lowering it is a WILL DECISION, logged as
BL-R181-DEBT-5 rather than taken quietly here - it would reduce drops per open, which is exactly what
non-reduction forbids without his say-so."* Three waves then raised COMPOSITION while volume stood
still. MEASURED on the shipped `build83` arz `44499f56`, which is live on Steam and DEV right now, the
two canonical cage chests opened once pay:

| difficulty | grade it pays | shipped b83 | R-240 | cut |
|---|---|---:|---:|---:|
| Normal | Epic | **43.71** | **3.84** | 11.4x |
| Epic | Legendary | **28.17** | **2.68** | 10.5x |
| Legendary | Legendary | **36.41** | **3.82** | 9.5x |

**NON-REDUCTION IS SUSPENDED FOR VOLUME AND VOLUME ONLY.** The module writes exactly two fields per
record - `numSpawnMinEquation` and `numSpawnMaxEquation` - and its own scope proof FAILS THE BUILD if
any member, weight or group chance moves. No pool loses an item, no chance is lowered, the guaranteed
100% row stays 100%. Every breadth and distribution property b75-b83 shipped therefore survives at
lower volume, and that is re-proven rather than asserted: `chest_loot_breadth.verify` and
`armor_loot_breadth.verify` both run AFTER this module on the same db and both stay green.

**WHY THE OTHER GATES SURVIVE A VOLUME CUT BY CONSTRUCTION.** Breadth counts DISTINCT REACHABLE items,
a property of the loot graph, and `numSpawn` only multiplies how often that graph is sampled.
Distribution D1-D6, D8, D9 and D7b are all RATIOS and divide the volume out. D7 - an ABSOLUTE floor of
armour pieces per open - is the single exception in the whole contract, and R-181's own block comment
had already written the answer: *"below that the number is a numSpawn demand rather than a parity
one"*. So D7's floor is now DERIVED in code (a per-iteration strength times an anchor volume) and
**D7X2** re-proves the committed anchor against the anchor surface's own bytes every run. The anchor
also MOVES, off `svc_uberorb_apex_e01c` and onto `gaoler cage chest_01 [l]`: the never-empty floor
lifts every thin container to the same 1.125 iterations, so the old volume proxy stopped separating
anything and D7 would newly have red the fifteen R-220 orb tables b80 deliberately excluded.

**THE COST, MEASURED and not estimated (an earlier draft of this line said "42-of-57 to 21-of-75" and
both halves were wrong):** the audit set is **63** surfaces after this wave (57 canonical + the 6 new
TESTHUB twins), and **D7 is asserted on 24 of them - only 18 of the 57 CANONICAL surfaces.** That is a
bigger canonical cost than the wrong number admitted. The 18: cage chest_01 [l], chest_03 [e],
chest_03 [l]; the 3 blood-cave donors; `polisvault_02/_04/_05`; and the 9 `svc_*hoard_loot_03` tables.
D7 now asserts on **no orb at all** (apex or level-banded), on **none of the 18 `_01`/`_02` hoard
tables**, and on exactly **one Normal-difficulty canonical surface** (`loottable_hidden_bloodcave_01`).
**D7b - 0.0375 worn-slot pieces per SPAWN ITERATION, unchanged, asserted on all 63 - is what carries
the invariant now**, exactly as R-181's own comment predicted it would have to, and the R-181 gate
re-run on the trimmed db returns 0 findings.

**THE LADDER, and it is per DIFFICULTY as asked.** Every equation keeps its exact
`(<bracket>)*<M>` shape and only `<M>` moves, so `numberOfPlayers` co-op scaling is preserved
byte-for-byte in form.

| tier | trim | e.g. cage chest_01 | S before -> after |
|---|---:|---|---|
| Normal | x0.085 | `*2.4/*2.8` -> `*0.2188/*0.25` | 12.48 -> 1.125 |
| Epic | x0.095 | `*2.4/*2.8` -> `*0.228/*0.266` | 12.48 -> 1.186 |
| Legendary | x0.105 | `*2.4/*2.8` -> `*0.252/*0.294` | 12.48 -> 1.310 |

**RANK IS PRESERVED IN SPAWN VOLUME (S), AND THAT IS THE ONLY UNIT THE CLAIM HOLDS IN.** The trim is
multiplicative on each table's shipped multiplier, so S keeps its order: the blood-cave mega chest
stays the highest-S surface (1.991 against the cage's 1.310/1.512) and cage chest_03 stays above
chest_01 on every difficulty. Two corrections to what that does NOT mean, both measured, because an
earlier draft of this ruling claimed the order survived generally:
- **In gear per open the order is different, and it was different BEFORE this wave** - the trim
  neither caused it nor can fix it. On the shipped `build83` arz cage chest_01 [n] already paid 23.88
  against the blood cave's 17.45 and the hoards' 19.19, and chest_03 already paid less than chest_01 on
  all three difficulties. After: cage 2.153, hoards 1.730, blood cave 1.483-1.497. Gear-per-open is S
  times COMPOSITION, and composition is R-180/R-181/R-220's, not this lever's.
- **The orb rank does not survive even in S.** The never-empty floor lifts every thin container to the
  same floor volume, so `svc_uberorb_apex_n01c` and `orb uberorb_default_n01c` both land on S 1.125 /
  1.014 gear per open - EQUAL, where shipped they were 10.58/9.53 against 5.06/4.56. The b79 precedent
  Will asked to keep ("orbs stay generous relative to chests") survives in the sense he asked for - an
  orb at 1.014 against a cage chest at 2.153 is generous - but "apex beats level-banded" is a casualty
  of the discrete floor, recorded as one rather than repeated. `--calibrate` prints S and gear/open
  side by side for all 63 surfaces so neither claim need be made from memory.

**"GUARANTEED" IS TREATED AS A GUARANTEE, NOT AN AVERAGE - UNDER BOTH READINGS OF THE SPAWN COUNT.** A
never-empty floor (`MIN_SPAWN_MIN_SOLO = 1.05` iterations at one player) keeps at least one loot
iteration on every container, so the 100% guaranteed row still fires. That floor is not taste:
build28/29/30 replaced a numSpawn equation with the bare literal `48`, the engine's evaluator returned
0, and the chest opened and dropped NOTHING - a P0 that took three builds to find. V3 and V4 plant that
P0 rather than trusting a comment.

**The model is a MODEL, and this ruling says so rather than letting one number stand as measured engine
behaviour.** `spawn_iterations` returns the CONTINUOUS mean of the min and max equations. Before the
trim S ran 5.06-18.96 and the fractional part was noise; after it, every canonical cage table
evaluates to between **1.0502 and 1.6128** iterations solo, so under INTEGER TRUNCATION every one of
them is exactly ONE iteration and the rounding mode is the whole question. **We do not know which the
engine does** (`BL-R240-DEBT-5`), so both are gated:

| difficulty | continuous gear | P(>=1), V7 floor 95% | int-truncated gear | P(>=1), V7b floor 90% |
|---|---:|---:|---:|---:|
| Normal | 3.84 | 99.99% | 3.29 | 99.96% |
| Epic | 2.68 | 96.86% | 2.12 | **93.78%** |
| Legendary | 3.82 | 99.63% | 2.74 | 98.30% |

The Epic truncated figure is **below the 95% V7 enforces**, and V7 reported green because its model
never discretises - which is precisely why V7b exists and why the two floors are separate numbers. The
direction of the error is benign for the ask: 2.1-2.7 legendaries a run is CLOSER to "guaranteed 1
legendary item" than 2.7-3.8. Two consequences worth carrying forward: **the ceilings (V1/V6) stay on
the continuous reading**, which is the higher one, so every check is evaluated under the model hardest
on it; and **solo, the per-difficulty ladder is a continuous-model artefact** - all three difficulties
truncate to the same single iteration, and what separates them is composition. The ladder still does
real work in co-op, where every bracket exceeds 13.8 iterations.

**THE MECHANICAL FLOOR IS 2.74, NOT 1.0, AND THAT IS STATED PLAINLY.** ONE spawn iteration of the
canonical cage already pays 1.60 + 1.14 = 2.74 Legendary-grade pieces, because six loot groups roll
independently per iteration and their chances sum past 280%. The `numSpawn` lever cannot reach a
literal "1 legendary item" per run; it bottoms out at 2.74 and this wave lands at 3.82 continuous
(2.74 truncated - i.e. the truncated Legendary reading is ALREADY sitting on the mechanical floor).
Going lower means lowering group chances or the guaranteed row - COMPOSITION, which this lane is
forbidden to touch. Registered as `BL-R240-DEBT-1`. **If Will means literally one, that is the one-line
follow-up and it needs his word, because it takes the guaranteed row below 100%.**

> **ONE CONSTANT OF HEADROOM WAS LEFT ON THE TABLE, DELIBERATELY, AND IT SHOULD NOT BE DISCOVERED
> LATER.** The Legendary cage lands at S = 1.310 / 1.512, comfortably ABOVE the 1.05 / 1.20 never-empty
> floor, so `CANON_TRIM['l']` still has room the Normal and Epic tiers do not. Dropping Legendary to
> the floor takes its run from **3.82 to about 3.08** continuous (2.74 truncated, the mechanical floor
> itself). So the honest sentence is: **it is the per-difficulty LADDER, not the mechanics, holding
> Legendary at 3.82** - "within 40% of the floor" is true and it is a choice, not a limit. One constant
> if Will wants it tighter, and the ladder's own rationale (a Legendary container keeps more of its
> shipped volume than a Normal one) is the only thing arguing against. `BL-R240-DEBT-6`.

**THE TESTHUB HALF IS A RECORD SPLIT, BECAUSE THE ARZ IS SHARED.** The four TESTHUB farm-duplicate
cage chests (Will 2026-08-08) named the SAME two container records as the two canonical placements, so
a trim written into those records would have reached Will's DEV farm too. There is ONE database and
both map variants read it, so the split can only live in the RECORDS: `loot_volume_trim` clones the
whole cage chain to a `_hub` twin BEFORE trimming - so the twin carries the shipped volume and every
b75-b83 breadth/armour edit verbatim, with no second copy of the tuning to keep in step - and
`build_section_surgery.build_hub_extra_specs` points the four TESTHUB-only placements at the twin.
PROVEN both ways: the hub specs name `svc_polisvault_hub_chest_01/03`, `B41_SPECS` still names
`svc_polisvault_chest_01/03`. TESTHUB run stays **43.71 / 28.17 / 36.41**, canonical **3.84 / 2.68 /
3.82** - a 9.5x split on Legendary.

> WARNING - **COUPLING:** the map half needs the TESTHUB Levels variant REBUILT (`SVC_TEST_HUB=1`).
> Until then the four duplicates keep naming the canonical records and DEV's cage is trimmed like
> canonical. That is the SAFE direction (DEV under-pays, Steam never over-pays). Canonical `B41_SPECS`
> is untouched, so `local/Levels_merged.arc` stays byte-identical and the Steam delta stays arz-only.

**GATE (law 4, no new surface without a gate):** `tools/svc_loot_volume.py` is the one implementation,
shared by `tools/gate_loot_volume.py`, `loot_volume_trim.verify()` and the negatives. V1 canonical
ceiling per open, V2 TESTHUB FLOOR (so a later lane cannot quietly kill the DEV farm while every
ceiling stays green), V3 never-empty, V4 equation form, V5 the twin is strictly richer, V6 the cage RUN
ceiling per difficulty, V7 the guarantee, V7b the guarantee under integer truncation. Negatives:
`py tools/debug/negtest_loot_volume.py <arz>` - **11 planted defects RED, 3 controls GREEN**, and they
plant in BOTH directions: too much (N1, the defect Will reported) and too little (N5, the MIRROR - this
lane's own over-correction, trimmed until the guarantee dies). Two more were added by the round-2 vet:
**N10** plants the defect V7b exists for - a guarantee "repaired" by raising `numSpawnMax` inside the
truncation band `[1,2)`, which moves the continuous model and literally nothing a player sees - and
**N11** plants a SECOND `apply_wave` on the same database.

> **THE WAVE IS APPLY-ONCE, NOT IDEMPOTENT, and four places in the round-1 lane claimed otherwise.**
> `clone_hub_cage` would re-clone the TESTHUB twin off the already-TRIMMED canonical records (the
> canonical-vs-TESTHUB split then simply ceases to exist), and the trim is multiplicative with no
> marker in the bytes saying it has already run. **Measured: a second apply drifts 58 tables and lands
> the DEV farm at ~1.04x canonical instead of ~9.5x.** No shipped artifact was ever at risk -
> `patches.run_registry` asserts each module runs exactly once, which is why det-2x is byte-identical -
> but the workflow the docs advertised did not exist. The twin's own existence is now the guard, a
> second call fails LOUD, and `gate_loot_volume --apply` detects the applied state and says so.

> **THE R-181 DISTRIBUTION GATE NOW REDS ON ANY PRE-R-240 ARZ, AND THAT IS THE ANCHOR WORKING.**
> `gate_loot_distribution.py` on this branch cannot be used as a "the baseline passes too" control
> against the rollback artifact, the previous build, or any lane branched before this one: it emits
> `D7X2 the committed ARMOR_SLOT_FLOOR_REF_SPAWN=1.3100 no longer matches the reference surface gaoler
> cage chest_01 [l], which MEASURES 12.4800 spawn iterations`. On an untrimmed arz the anchor surface
> really does measure 12.48. **Every other coexisting gate still passes on the untrimmed arz** (chest
> breadth 51 tables, orb breadth 18, craft/thrown, artifacts - all 0 findings), so a lone D7X2 red on a
> pre-R-240 artifact is not a defect and the Ship lane should not chase it.

**NOT PROVEN IN-GAME.** Everything above is a database and gate proof. **Will's check: Prison of Souls
/ Hades Palace floor 4, kill Alkyoneus the Soul-Gaoler, open BOTH canonical cage chests on Legendary -
expect a handful of items with roughly one to four legendaries, not a floor covered in them; and on the
DEV TESTHUB cage the four duplicates should still pour.** Registered as `BL-R240-DEBT-3`.

### R-240 COMPANION RULING [2026-08-11] PENDING - "artifacts should never drop from chests"

**WILL, VERBATIM (2026-08-11):** *"artifacts should never drop from chests"*.

> 🚨 **WILL DECISION REQUIRED BEFORE THIS COUNTS AS SATISFIED - do not read the green gate as
> compliance.** The ruling as stated is NOT what ships. What ships asserts *"zero equippable artifacts
> reachable from any mod chest, hoard or orb EXCEPT six pinned by name"*, and those six are reachable
> because of **R-185, one of Will's own rulings, shipped the day before**. A literal zero-artifact gate
> would RED the live `build83` build and require reverting R-185. The six-artifact exemption is
> therefore a **decision for Will, not a detail** - either he ratifies the exemption (and this entry
> becomes IMPLEMENTED-WITH-EXEMPTION), or he takes the one-lane follow-up priced in `BL-R240-DEBT-2`
> and the roster deletes itself. **The independent round-2 vet re-derived this from the bytes with its
> own loot-graph walker and confirmed both halves: the relayed "current state already complies
> (0/292)" is false, and the six reachable records are exactly
> `e_da_crescentmoonofartemis`, `e_da_demetersbounty`, `l_da_goldeneyeofsunwukong`, `l_da_ikonofzeus`,
> `l_da_mardukstabletofdestiny`, `l_da_thothsglory`**, reached via
> `records\item\loottables\svc\svc_craft_reagents_artifact_l01.dbr`, which is named by
> `04_l_misc.lootName7`, `amulet_l01.lootName4` and `finger_l01.lootName3`.

**THE PREMISE THIS ARRIVED WITH WAS WRONG, AND SAYING SO IS THE POINT.** It was relayed as a no-op -
"current state already complies (0/292), assert it so it can never regress". It does not comply.
MEASURED on the shipped b83 arz `44499f56`: **30 of the 57 mod loot surfaces reach an `ItemArtifact`
record**; 16 distinct artifacts are reachable, **6 equippable + 10 mercenary scrolls**. The six are the
IT divine artifacts (Ikon of Zeus, Thoth's Glory, Marduk's Tablet of Destiny, Golden Eye of Sun Wukong,
Crescent Moon of Artemis, Demeter's Bounty) and they drop **BY DESIGN, from R-185** - a Will ruling of
2026-08-10 whose rule G1 requires every non-green reagent of every uber craftable to be findable in a
Legendary chest, and two craftables (Mortok's Skull, The All-Seeing Eye) name nothing but divine
artifacts.

So the newer ruling and a shipped one COLLIDE, and a volume lane does not get to resolve that quietly.
**Ledger state: PENDING, deliberately.** What ships is everything enforceable without reverting R-185:
`tools/svc_chest_artifacts.py` + `tools/gate_chest_artifacts.py` assert **A1** no equippable artifact
is reachable from any mod chest, hoard or orb beyond a roster pinned BY NAME; **A2/A3** every pin is
re-derived from the bytes every run (still reachable AND still named as a reagent by a real formula) so
a pin cannot outlive its reason; **A4** the scroll discriminator still discriminates. **135 of the 141
equippable artifacts are proven unreachable; nothing new can leak.**

**A SCROLL IS NOT AN ARTIFACT, AND THE DIFFERENCE IS MEASURED.** All 299 `ItemArtifact` records sit on
`ItemArtifact.tpl`, so the engine `Class` cannot separate a Divine artifact from a mercenary-hire
scroll. What does: **158 of the 299 point `itemSkillName` at `records\skills\scroll skills\...` and 141
do not.** The 141 are what a player wears. A literal all-299 reading would demand stripping merc
scrolls out of the base game's own `04_*_misc` tables - changing every chest in the campaign - which is
neither the ask nor something a loot lane may do.

**WHAT FULL COMPLIANCE COSTS (`BL-R240-DEBT-2`), priced so Will can decide in one step:** delete the
`svc_craft_reagents_artifact_l01` member from its three hosts (`04_l_misc`, `amulet_l01`, `finger_l01`);
`svc_craft_thrown`'s rules G1 and G4 then RED on those six, so they need a new exemption class in the
same shape as the existing MI/green one - *"a reagent that is itself a craftable"*.
`docs/CHEST_DROP_MATRIX.md` 6.5 already reaches that verdict independently ("No fix needed ... this
recipe is a craft-a-craft by base-game design"), so 42-of-42 completability survives. **It is one lane,
and one lane per problem means it is not this one.** The day it runs, A3 reds the now-dead pins and the
roster deletes itself.

### R-200 CLARIFICATION [2026-08-11] - ordinary bosses do NOT get orbs, BY DESIGN

**WILL, VERBATIM (2026-08-11):** *"no ordinary bosses dont get orbs"*.

`BL-R200-DEBT-1` (333 non-uber Boss-class records carrying no orb) and `BL-R200-DEBT-3` (the 4
non-uber, non-`tagSVC` Boss-class oddities the R-200 audit surfaced and declined to wire) are both
**CLOSED AS BY-DESIGN**. No code change: R-200 already drew exactly this boundary and its red-uber gate
already asserts the positive side (every RED uber HAS an orb, negtest N3 reds a new red uber with no
orb, N8 proves the scope stays red-only). The ordinary bosses keep paying through their level-placed
quest chests, which is what they have always done.

---

## R-241 [2026-08-11] IMPLEMENTED, then SUPERSEDED-BY-R-242 (2026-08-12) for the general orbs - an uber orb has a CHANCE at a legendary, not a guarantee. [branch `fix/loot-volume-trim`, module `tools/patches/orb_legendary_chance.py`] **NOTE: R-242 replaces the flat 21.2% apex demotion with a per-difficulty 0/50/75 treatment on the 15 GENERAL orbs and EXCLUDES the Toxeus/Leinth apex; the apex 100 -> 21.2 demotion below is RETAINED by R-242 as the apex's frozen build85 state. `BL-R241-DEBT-1` is CLOSED-BY-R-242. Read R-242 at the end of this file.**

**WILL, VERBATIM (2026-08-11):**

> "you made the orbs way too good... those dont need to have guaranteed legendary drops, they should
> just have a chance to drop legendary items, but a low chance."

**THIS RULING SUPERSEDES THE b79 "ORBS STAY GENEROUS" PRECEDENT WHEREVER THE TWO COLLIDE**, and that
is recorded here rather than resolved quietly inside a module. R-220's b79 record carries Will's
earlier instruction that orbs remain generous *relative to chests*; that half survives (a trimmed orb
still pays about 2.06 items against a cage chest's 2.15, and the apex orb is still the richest orb in
the mod). What does NOT survive is "an orb reliably pays legendaries".

### THE NUMBER HE ASKED FOR, MEASURED FIRST

On the shipped `build83` arz `44499f56` - live on Steam and DEV at the time of the ruling - the orb
surface is **18 loot tables, 6 per difficulty** (15 ordinary + 3 apex). Guaranteed-legendary rows,
i.e. a loot group at chance 100 that can pay a legendary:

| difficulty | orb tables | guaranteed-legendary rows | which |
|---|---:|---:|---|
| Normal | 6 | **1** | `svc_uberorb_apex_n01c` g4 @100% (0.44% legendary by weight) |
| Epic | 6 | **1** | `svc_uberorb_apex_e01c` g4 @100% (5.25% legendary) |
| Legendary | 6 | **1** | `svc_uberorb_apex_l01c` g4 @100% (6.28% legendary) |
| **total** | **18** | **3** | all three the SAME row on the SAME family; **none is a PURE legendary row** |

All fifteen ordinary orb tables run that identical amulet/relic/ring/formula row at **12.7%** or
**21.2%**. The apex 100% was the outlier.

### THE ROW COUNT IS NOT WHERE THE GUARANTEE LIVED, AND THAT IS THE FINDING

Answering *"three rows, and all of them are 94%+ non-legendary"* would have answered the question and
missed the report. What Will hit is a guarantee made of **VOLUME**. Per ONE orb open on b83:

| difficulty | E[legendary items per open] | P(at least one legendary) |
|---|---:|---:|
| Normal | 0.003 .. 0.047 | 0.3% .. 4.6% |
| Epic | **2.579 .. 6.291** | **93.6% .. 99.9%** |
| Legendary | **3.738 .. 8.432** | **98.4% .. 99.99%** |

An apex Legendary orb paid **eight and a half legendary-grade items per open**. Six loot groups
rolling independently over 5.06-10.58 spawn iterations manufacture that with no 100% row involved -
which is exactly why R-220's breadth gate, R-181's distribution gate and R-240's volume gate were
**all green** while Will was looking at a vending machine. A guarantee is not always a field.

### WHAT SHIPPED

Two levers, in registry order:

1. **R-240's volume trim** (previous slot) takes every orb to the never-empty floor:
   S 5.06 / 6.44 / 8.28 / 10.58 -> **1.125**.
2. **R-241's demotion** discharges the literal half: the three guaranteed rows drop to the **richest
   NON-guaranteed chance that same row already carries in the orb family (21.2%)**. The target is
   **DERIVED from the shipped bytes**, never typed, and cross-checked against the value the contract
   was measured on, so a retune of `boss_charon_*01b` cannot silently relocate the demotion (negtest
   M7). Will's ruling offers *"chance-based OR non-legendary"*; chance-based is the smaller change,
   because making the row non-legendary means deleting `amulet_{tier}01` and `finger_{tier}01` from
   it - the ONLY legendary amulet and ring an orb can pay, i.e. breadth Will asked for in b75-b83,
   destroyed to satisfy a rate ruling.

**3 records, 3 fields. 0 members, 0 weights, 0 spawn equations, 0 pools.** The module's scope proof
fails the build if anything else moves, so breadth and distribution survive verbatim and the variety
still lands **WHEN** a legendary rolls. RESULT, per ONE orb open:

| difficulty | E[legendary] shipped b83 | E[legendary] R-240+R-241 | cut | guaranteed rows |
|---|---:|---:|---:|---:|
| Normal | 0.003 .. 0.047 | **0.001 .. 0.004** | ~12x | 1 -> **0** |
| Epic | 2.579 .. 6.291 | **0.451 .. 0.622** | ~10x | 1 -> **0** |
| Legendary | 3.738 .. 8.432 | **0.699 .. 0.846** | **~10x** | 1 -> **0** |

**THE HEADLINE, in the unit the report was made in: at most ONE legendary item per orb open on
Legendary difficulty, against 8.43 shipped - a 90% cut, with zero guaranteed-legendary rows anywhere
in the surface.**

### THE GATE, AND ITS MIRROR

`tools/gate_orb_legendary.py` / `tools/patches/orb_legendary_chance.verify()`, one shared
implementation in `tools/svc_orb_legendary.py`:

- **O1** ZERO guaranteed-legendary rows (the ruling, literally).
- **O2** no orb pays more than `ORB_MAX_LEG_PER_OPEN` = {n 0.05, e 0.75, **l 1.00**} legendary items
  per open.
- **O3** ... and pays at least one no more often than `ORB_MAX_P_LEGENDARY` = {n 2%, e 55%, l 68%}.
- **O4** THE MIRROR: a legendary must still be POSSIBLE at a real rate, floor {e 15%, l 25%} - because
  *"just a CHANCE"* is an instruction that the chance still exists. Measured on the INTEGER-TRUNCATED
  spawn count, which is the pessimistic side of a floor.
- **O5** THE SECOND MIRROR: an orb must still pay at least 1.50 items of any kind per open, so no
  ceiling can be satisfied by turning the orb into an empty box.

There is deliberately **no truncated CEILING twin**. Truncated S is always <= continuous S and both
readings rise with S, so a truncated ceiling could never fire while its continuous parent was green:
a check that cannot fail, printed in a PASS line, is worse than no check. The first draft had one; it
was removed once the monotonicity was written down instead of assumed.

**REPRODUCED AS AN ARTIFACT FACT BEFORE IT WAS FIXED:** the gate emits **29 findings** on the live b83
arz - 3 O1, 12 O2, 14 O3. (It read 43 while the inert `O3b` twin above still existed; deleting a check
that could never fail removed its 14 duplicate lines and nothing else. Re-measured after the deletion,
not adjusted to match.) Negatives: `py tools/debug/negtest_orb_legendary.py <arz>` - 8 planted defects RED (including M5,
which is green on the continuous reading and RED under truncation, the exact case O4's model choice
exists for, and round-3's M8, which drives the legendary rate under the low-chance bar and proves the
undischarged-notice CLEARS at 3.7% rather than being a permanent banner) and 4 positive controls GREEN
(round-3 added Q4: the notice FIRES on the shipping build, 60.9% against the 25% bar, naming the debt).

### THE HALF THIS LANE COULD NOT REACH - `BL-R241-DEBT-1`, WILL DECISION [CLOSED-BY-R-242, 2026-08-12: Will ruled the general orbs to explicit per-difficulty numbers (0/50/75) and the Toxeus/Leinth apex to keep its current loot - option (B) taken for the general orbs, exclusion for the apex]

**P(at least one legendary) lands at 54-61% on Legendary difficulty, and 60% is not "a low chance".**
Stated here rather than buried, because the ruling is not fully discharged and a green gate must not
imply that it is.

**WHY.** After the trim an orb pays ~2.06 items per open, and **~40% of a Legendary-tier orb's entire
drop mass IS legendary-classified** - because R-180/R-220 deliberately weighted
`svc_unique_weapons_l01` and `svc_unique_armor_l01` at ~47-50% of the weapon and shield rows to buy
the CLASS BREADTH Will asked for in the same fortnight. If the orb pays anything, there is a good
chance the thing it pays is legendary. That is composition, not volume.

**WHY THIS LANE DID NOT SIMPLY DO IT.** The only remaining lever is scaling those rows'
`loot{g}Chance`, and that is NOT the volume lever `numSpawn` is: `svc_loot_distribution` **D7b asserts
worn-slot armour pieces PER SPAWN ITERATION (>= 0.0375) on all 63 surfaces**, and a uniform
group-chance scale divides that reading by the same factor - reding armour parity on every orb.
Scaling only the legendary-heavy rows moves D3/D4 (weapon:armour) and D6 (armour-slot share) instead.
Either way it re-litigates the armour parity b75-b83 shipped, which this lane was told is untouchable.

**THE TWO OPTIONS, PRICED:**

- **(A) Accept 54-61%** as "a chance, not a guarantee", on the strength of the 90% cut in legendary
  ITEMS and the zero guaranteed rows. Cost: nothing. The ceilings above become permanent.
- **(B) Push the chance below the 25% LOW-CHANCE BAR.** 25% is `LOW_CHANCE_RULING_BAR` - one open in
  four - and it is the single number this lane proposes for what "a low chance" means, since Will's
  sentence fixes none. It is deliberately generous, so clearing it is a real bar and not a technicality.
  Needs a composition lane inside R-180/R-181/R-220's scope: give
  the Legendary-tier orb rows an epic-grade sibling pool to split their weight with, so the orb still
  pays two items but they are usually Epic. Cost: one lane, a re-derivation of D7b's floor for the orb
  family, and a re-run of the orb-breadth gate. **It is one lane, and one lane per problem means it is
  not this one.**

**ROUND-3 AMENDMENT (2026-08-11): THE COMMITTED CEILING IS NOT A CHOSEN RATE, AND THE GATE SAYS SO.**
The round-3 vet's objection was not that the lane stopped in the wrong place - it independently
confirmed the lever is spent - but that `ORB_MAX_P_LEGENDARY` = {n 2%, e 55%, l 68%} silently writes
"not low" into the design law as the permanent band, so a later reader lands on 68% and concludes 68%
is the intent. It is not. It is a ratchet holding the 90% cut in legendary ITEMS that this wave DID
deliver. Three corrections carry that:

1. **If Will rules (B), those two numbers come down IN THE SAME COMMIT as the fix.** Recorded in the
   constant's own comment, in `BL-R241-DEBT-1`, and in Will's test note.
2. **`svc_orb_legendary.undischarged_notice()`** measures the worst surface against
   `LOW_CHANCE_RULING_BAR` (**25%** - one open in four, deliberately generous so the notice only fires
   when the gap is beyond argument, and explicitly NOT asserted as a number Will gave) and prints a
   banner naming this debt on **every** run of the standalone audit and the in-build `verify`, on the
   PASS path as well as the FAIL path. The PASS line now ends *"PASS MEANS THE COMMITTED BAND IS HELD,
   NOT THAT R-241 IS FINISHED"*. It does **not** red the gate: closing the gap is a composition ruling,
   and **a gate may not take a ruling on Will's behalf** - the same principle that made this lane log
   `BL-R181-DEBT-5` instead of cutting volume quietly three waves ago.
3. **The notice is tested from both sides**, because a notice nobody tests is a comment with extra
   steps: negtest **Q4** proves it fires on the shipping build, and negtest **M8** drives the measured
   rate under the bar and proves it **CLEARS** - so it is a live measurement that will disappear by
   itself when a later lane actually delivers "a low chance", not a permanent banner readers learn to
   skip.

**AND THE TEST NOTE WAS WRONG BEFORE IT WAS RIGHT.** Both this ledger's companion test note and
`BL-R241-DEBT-2` told Will to expect a legendary to "be an event, not the default" - twenty lines above
the admission that it happens on 54-61% of opens, which is more likely than not. Corrected in both
places to the unit that actually moved: **at most one legendary per open**, count the pile, and judge
the rate against the number in the debt rather than against a sentence that flattered the result.
---

### R-240/R-241 GATE COLLISIONS [2026-08-11] IMPLEMENTED - two pre-existing gates asserted the law these rulings REPLACE, and both would have aborted the build

**THIS IS A LEDGER ACT, NOT A THRESHOLD EDIT.** A lane may not quietly delete another ruling's
proof. Both collisions below were found by the round-3 independent vet, both were proven with a
CONTROL (the same harness, the same code, two arz files: the shipped b83 `44499f56` untouched vs
the same arz plus this lane's two waves), and both are recorded here BEFORE the gates were touched.

Neither gate was relaxed. Both were re-expressed so that the thing they actually protect is still
protected, against the number Will has now ordered instead of the number he has now overruled.

---

#### COLLISION 1 - `polis_vault.verify` T5: *"payout must never shrink"*

**WHAT IT ASSERTED.** For all 18 Gaoler cage loot tables, that `numSpawnMin/MaxEquation` ends with
the placed chest's shipped multiplier from `_PLACED_TIERED` (`01` -> `*2.4`/`*2.8`, `03` ->
`*2.8`/`*3.2`), with the literal failure message **"payout must never shrink"**.

**THE COLLISION.** R-240 rewrites exactly those two fields on exactly those tables. **36 T5
problems -> `SystemExit("polis_vault gate FAILED")`.** Verify order does not save it: every
`verify()` runs after every `apply()`, so `polis_vault` always sees the trimmed db.

**WHY THE GATE IS NOT SIMPLY WRONG.** It was a correct reading of the law it was written under.
Non-reduction was in force and nobody had authorised a volume cut. Will has now authorised exactly
that cut, in these words:

> "we probably need to trip the loot-volume trim, especially on the steam version where maybe from
> the two chests, you get guaranteed 1 legendary item. on the testhub version we can spawn more that
> is fine."

So a gate whose failure message is "payout must never shrink" cannot also be the law that forbids
shipping his ruling. **Deleting it would be worse than the collision** - T5 is the only thing
standing between the cage and a silent starve.

**THE AMENDMENT.** T5 now computes the expected multiplier through **R-240's own transform**
(`svc_loot_volume.trimmed_multipliers`, the single implementation the trim itself writes with)
instead of reading a b83 literal. **Two discrete values are accepted per field and no others** - the
pre-R-240 shipped multiplier and the post-R-240 committed one - so it is still an exact-match
ratchet, not a band. A new **T5b** reds a HALF-TRIMMED cage (some variants trimmed, some not), which
neither the original check nor a single-era rewrite could catch.

**WHY TWO ERAS AND NOT ONE.** Not convenience - two reasons, both load-bearing:
1. The ship lane runs every coexisting gate against the **rollback artifact** as an anti-inert
   control. A gate that only knows the post-R-240 value reds on the previous ship arz and the
   control becomes noise (the same hazard the vet raised against `gate_loot_distribution`'s D7X2,
   `BL-R240-DEBT-8`).
2. A **partial** trim is a real defect that a single-era gate cannot see at all.

---

#### COLLISION 2 - `uber_apex_orb.verify`: R-72/R-99's no-nerf proof

**WHAT IT ASSERTED.** R-72/R-99 (Will 2026-07-27) put the whole Toxeus roster **and Leinth** on ONE
apex drop calibre, and the gate proves it by comparing the apex tables against Leinth's own frozen
reference tables (`loottable_leinth_{29-31,49-51,63-65}`, deliberately never written per the
retirement protocol): `*2.2`/`*2.4` and `loot4Chance` 100.0, reding on any reduction.

**THE COLLISION.** R-240 trims the apex tables ~10x; R-241 demotes their `loot4Chance` 100.0 ->
21.2. Both directions are exactly what the no-nerf proof exists to catch. **18 problems ->
`SystemExit`.** The vet found this in check **(h)**; a **second, independent copy of the same law in
check (c)** was behind it and would have aborted the build three lines later on the same three
records. Amending only (h) would have been cosmetic.

**THE SUPERSESSION, STATED PLAINLY.** R-241 supersedes **the absolute-floor half of R-72/R-99, and
only that half.** The proof has two halves braided together:

| half | what it says | status |
|---|---|---|
| **UNITY** | Leinth sits on the SAME tables as the roster; never singled out, never left behind | **SURVIVES WHOLE.** Will lowered the shared calibre for everyone *including her*, which is the opposite of singling her out. Now proved TWICE: her chest->table identity, plus one era across all three difficulties. |
| **ABSOLUTE** | the calibre is never numerically below her frozen b96 numbers | **SUPERSEDED by R-241**, in Will's own words. |

> "you made the orbs way too good... those dont need to have guaranteed legendary drops, they should
> just have a chance to drop legendary items, but a low chance."

An absolute floor pinned to `*2.2`/`*2.4` and `loot4Chance` 100.0 **is** the vending machine he is
describing. It cannot also be the law that forbids fixing it.

**WHAT WAS NOT SUPERSEDED, and is still proved against her originals:** gold
(`goldGeneratorLevel`), the unique-share weights (`LEINTH_UNIQUE_WEIGHT`), the no-`/`-in-an-MP-equation
law, and **every loot group chance except the ones R-241's census named for demotion**. A trim lane
gets to lower the two things Will pointed at and nothing else.

**THE OLD PROOF IS NOT DELETED.** `_no_nerf_problems` still runs **verbatim** at `apply()` time -
R-240/R-241 are registered LAST, so at that moment the apex tables still carry the b96 calibre and
her frozen tables are the correct comparand, and the migration the proof was written for is proved
exactly as it always was. It also still runs verbatim in `verify()` on any pre-R-240 arz.

**THE ORDERING THAT MAKES THAT TRUE, MEASURED** (`patches.REGISTRY`, 61 slots): `polis_vault` **10**,
`uber_apex_orb` **39**, `armor_loot_breadth` **55**, `loot_volume_trim` **59**,
`orb_legendary_chance` **60**, `visuals` **61**. So both colliding modules `apply()` *before* the two
trim modules - their apply-time guards are untouched - while **every `verify()` runs after every
`apply()`**, which is precisely why the collision existed at verify time and only at verify time.

**THE PASS LINE NAMES THE ERA.** Printing "all four calibre knobs >= her original chest" on a
trimmed db would be the gate telling the ship lane the opposite of what it just proved.

---

---

#### COLLISION 3 - R-181's OWN NEGATIVE BATTERY, which this lane had made blind

**FOUND IN ROUND 4, BY THIS LANE, NOT BY THE VET** - and worth stating plainly, because it is the one
the process nearly missed. The round-3 sweep ran all 53 registry `verify()` hooks. That found
collisions 1 and 2. It could not have found this one, because **a battery is not a verify() hook**.

`tools/debug/negtest_armor_breadth.py` on the shipped b83 arz: **NEGTEST FAILED: 2**.

Its **N12** case planted a 25% armour cut on `svc_uberorb_apex_e01c` - the surface `ARMOR_SLOT_FLOOR`
was anchored on when the case was written - and expected D7 to red. **It measured GREEN (BLIND).**
R-240 re-anchored the floor onto `gaoler cage chest_01 [l]` and re-derived it as per-iteration strength
x the trimmed anchor volume, taking it from **0.52 to 0.0644 per open, about 8x lower**. A 25% cut on a
surface calibrated at ~0.62/open lands near 0.47, an order of magnitude clear of the new floor.

**The check that the round-2 vet built specifically to make that regression permanently catchable had
been made uncatchable by this lane, and the battery went on describing the superseded contract.** Its
whole-build positive control failed too, on the single expected D7X2 problem (`BL-R240-DEBT-8`).

**FIXED, AND MADE ROT-PROOF.** N12 no longer hardcodes the surface or the percentage: it reads
`SLD.ARMOR_SLOT_FLOOR_REF_SURFACE` and **sizes the cut from the live floor**, so whoever moves the
anchor next still gets a plant that lands just under it. The positive control sets aside exactly the
D7X2 problem, names it, prints it, and reds on anything else. A new **N12b measures and prints, every
run, how deep a cut the old anchor can now absorb** - reported rather than asserted, because a test
that asserts a hole stays open is not a test.

**WHAT IS LEFT IS A DESIGN QUESTION, NOT A BUG (`BL-R240-DEBT-9`), AND CHASING THE REWRITE TO GROUND
MADE IT SHARPER THAN "THE FLOOR HAS SLACK".** Measured on `gaoler cage chest_01 [l]` (S=12.48): D7
binds at 0.0644/open, D7b binds at 0.0375/iteration = **0.468/open equivalent**. **D7b is 7.3x tighter,
so D7 can no longer fire first on the very surface it is anchored to.** Proven by planting: a 60%
armour cut there reds D6 and D7b on four slots and yields **zero** D7 findings; a D7-specific red would
need roughly a 96% cut. On the old anchor (`svc_uberorb_apex_e01c`, thinnest armour slot 0.6229/open
over S=10.58, matching b80's own calibration to the digit) a cut must now exceed **89.7% to red D7 and
36.3% to red D7b**, against **16.5%** before. Coverage separately fell from **42 of 57** canonical
surfaces to **18 of 57**.

**NONE OF THIS MAKES THE RE-ANCHOR WRONG.** Holding 0.52/open against a container that now spawns ~1.1
iterations would turn D7 into a numSpawn demand and red the whole mod for the ruling itself, and D7b is
unchanged and asserted on all 63 surfaces, so armour parity IS still enforced. The open question is
what to do with an absolute floor that has become decorative on its own anchor: keep it as a dominated
no-op, retire it and say so, or re-derive it per volume band. That is an R-181 composition decision and
therefore a different lane. `N12c` prints the dominance ratio on every run so the answer cannot be lost.

**THE RULE THIS ONE PRODUCES.** *A lane that changes a contract must re-run that contract's NEGATIVE
BATTERY, not merely its gate. A gate answers "is the current build clean"; only the battery answers
"can this gate still SEE a regression". Amending the first while leaving the second encoding the old
law produces a green build guarded by a blind gate.*

---

#### THE PROOF, MEASURED

|  | `polis_vault` | `uber_apex_orb` |
|---|---|---|
| shipped b83 `44499f56`, untouched | PASS | PASS |
| same arz + this lane's two waves, BEFORE this amendment | **36 problems -> abort** | **18 problems -> abort** |
| same arz + this lane's two waves, AFTER | PASS (era: R-240) | PASS (era: R-240) |

**NEGATIVE BATTERY:** `py tools/debug/negtest_gate_amendments.py <arz>` - **12 plants, all RED**,
covering every clause of both amended checks in both directions (a third multiplier; a silent
starve; a re-inflation; a half-trimmed cage; an unparseable equation; a third calibre; the demoted
row drifting back up; the demoted row cut further; a gold nerf; a non-demoted group chance below her
floor; unity broken; an era mix). The battery also proves its own restore is clean, so a planted
defect cannot leak into the next case and make the battery lie.

**THE RULE THIS PRODUCES.** *When a lane's authorised change contradicts a standing gate, the gate is
amended in the ledger with the superseding quote, the surviving half is re-proved rather than
assumed, and the negative battery is re-earned clause by clause. A green build that was made green by
deleting a proof is not a green build.*

---

## R-242 [2026-08-12] IMPLEMENTED (branch `fix/orb-rates-by-difficulty`, module `tools/patches/orb_legendary_chance.py`) - uber-orb legendary/blue chance BY DIFFICULTY; Toxeus + Leinth excluded. SUPERSEDES R-241's flat 21.2% demotion and CLOSES `BL-R241-DEBT-1`.

> **R-247.7a AUDIT NOTE (2026-08-13, measured NOT-INVOLVED - no amendment needed):** Will's stash-chest
> nerf report named this wave as a prime suspect; measurement clears it. The Devourer-stash tables
> `loottable_hidden_bloodcave_{01,02,03}` were NEVER in this ruling's 15-general-table calibration
> (their loot1/2/5/6 chances sit at the pre-R-242 40.0, not the 46.5-67.2 calibrated band) and their
> relic row (21.2) is byte-equal to the SV 0.98i original. The stash nerf was R-240's volume trim
> alone - see the R-240 amendment + R-247 part 7. This ruling's orb treatment is untouched.

> "yeah actually all the orbs that uber monsters drop should have a 50% chance of dropping a legendary item on epic, a 75% of dropping a legendary item on legendary, a 0% chance of dropping a legendary item on normal, but a 75% chance of dropping a blue item on normal (this is a sub legendary item, idk what the name of this class of item is but they show up blue)"

**WILL, VERBATIM (2026-08-12), part 2 (the exclusion):**

> "Note that Leinth and the toxeus variants keep their current higher / better orbs / better drop rates / more loot"

This is the "genuinely rare, deliberate decision" R-241 deferred as `BL-R241-DEBT-1`. R-241 flatly demoted the apex relic row to 21.2% as the whole answer and left the Legendary chance at 54-61% ("not a low chance"). Will's new ruling replaces that: the GENERAL orbs get an explicit per-difficulty legendary/blue treatment, and the Toxeus + Leinth apex is EXCLUDED and kept at its build85 state. **`BL-R241-DEBT-1` is CLOSED-BY-R-242.**

### "BLUE" = EPIC, PROVEN FROM THE BYTES

"blue" is itemClassification **Epic**, one tier below Legendary (the standard TQ ladder Broken < Common < Magical < Rare < Epic < Legendary; Epic renders blue, engine-baked, no classification->color record exists in either arz). MEASURED on the build85 arz `5a6d63a9`: on every NORMAL orb the four unique-gear rows resolve to **Epic-classification** records with **0.00% legendary GEAR**; on the EPIC/LEGENDARY orbs those same rows resolve to **Legendary**. So "the blue item a Normal orb drops" IS the Epic gear it pays, and "75% blue on normal" means raising the chance the Normal orb's Epic gear rows fire.

### THE PARTITION - DERIVED, NOT TYPED

The 18 in-scope uber-orb loot tables (svc_orb_breadth's own derived scope) split into:

| set | count | tables | treatment |
|---|---:|---|---|
| **GENERAL** | 15 | `uberorb_default_{13-15,19-21,29-31,39-41,43-45,49-51,53-55,55-57,63-65}` + `uberorb_default_{n,e,l}01c` + `boss_charon_{n,e,l}01b` | 0/50/75 legendary + 75 blue-on-normal |
| **EXCLUDED** | 3 | `svc_uberorb_apex_{n,e,l}01c` | kept byte-identical to build85 (Will part 2) |

A table is **EXCLUDED iff every uber chain that reaches it has carriers that are ALL Toxeus (or Leinth)**. The derived excluded set is **cross-checked against the pinned apex roster** (`X0`) so a general orb rewired onto Toxeus/Leinth loot, or a fourth apex table, reds instead of silently changing scope. MEASURED: the 3 apex tables' only carriers are the R-99 Toxeus roster (`um_toxeus_21/99`, `um_bloodtoxeus_99`, `um_toxeus_enslaver_99`, `um_toxeus_hunt_99/_l_99`) plus Leinth's chests; none of the 15 general tables is reached by any Toxeus/Leinth carrier. The partition is exact and derivable.

### THE LOAD-BEARING CORRECTION - THERE IS NO SINGLE "LEGENDARY ROW"

The ruling's phrasing assumes a legendary row whose chance is the legendary chance. The bytes say otherwise: legendary/blue output is **EMERGENT** across the four unique-GEAR rows loot1 (weapons), loot2 (torso/head), loot5 (legs/arms), loot6 (shield), each firing at its own `loot{g}Chance` over S spawn iterations. loot4 (amulet/relic/ring/formula) carries almost no legendary mass - setting it to 50% would yield ~2.5% legendary, not 50%. So Will's "50% chance of dropping a legendary item" is read faithfully as observable orb behaviour:

> **P(at least one legendary item per orb open) = the target.**

and the lever is a **UNIFORM per-(table, difficulty) chance on loot1/2/5/6**, CALIBRATED per table against the emergent model to hit the number. Uniform because it preserves the weapon:armour:shield mass ratio (R-181 D3/D4/D6 parity) and RAISING chances only strengthens the D7b armour-per-iteration floor - so the change is armour-parity-safe by construction and touches only `loot{g}Chance`, the exact field domain R-241's scope proof already permitted.

### THE DIFFICULTY MECHANISM

Each difficulty of each general orb is a physically SEPARATE FixedItemLoot record; the difficulty is selected UPSTREAM by the proxy's `accessory1`/`accessoryEpic1`/`accessoryLegendary1` slot. So the chances are set DIRECTLY on each of the 15 distinct records (the relic-tiering-approved pattern, NOT the rejected container game-mode array).

### WHAT SHIPPED (arz-only, build86)

On the 15 general tables, loot1/2/5/6 calibrated from 40.0 to the per-table value that lands the target (all within +/-5pp band): **Normal ~46.5-46.8%** (blue/Epic 75%, legendary GEAR held at 0), **Epic ~41.4-56.1%** (legendary 50%), **Legendary ~56.9-67.2%** (legendary 75%). On the 3 excluded apex tables, the guaranteed relic row is still demoted 100 -> 21.2 (the DERIVED family value, R-241's), which IS their build85 state - letting it revert to 100 would both change the bytes and re-arm a guaranteed legendary row.

**MODIFIED 15 records / 60 field moves, all `loot{g}Chance`, all RAISES; the 3 apex tables 0 fields changed (byte-identical to build85).** 0 members, 0 weights, 0 spawn equations, so breadth, distribution and the relic law survive verbatim and the variety still lands WHEN one rolls.

| tier | target | general P(target) after | excluded apex (frozen b85) |
|---|---|---|---|
| Normal | blue(Epic) 75%, leg-GEAR 0% | 75.0%, leg-GEAR **0.00%** | Epic 69.0%, leg 0.1% |
| Epic | legendary 50% | ~50.0% | legendary 48.9% |
| Legendary | legendary 75% | ~75.0% | legendary **60.9%** |

### THE GATE, AND ITS MIRRORS

`tools/gate_orb_legendary.py` / `tools/patches/orb_legendary_chance.verify()`, one shared implementation in `tools/svc_orb_legendary.py`:

- **X0** the DERIVED Toxeus/Leinth exclusion set equals the pinned apex roster (a rewired consumer reds, not silently changes scope).
- **G1** each general orb pays its per-difficulty target within +/-5pp.
- **G2** a Normal general orb pays 0% legendary GEAR (the tier law; the base-game scroll/formula leak on loot4 is exempt and measured apart - the ~0.1-0.35% "legendary on normal" is Legendary-classified mercenary scrolls / arcane formulae, never gear).
- **G3** each excluded apex table is byte-identical to build85 (loot profile + numSpawn), and **G3b** its OUTPUT is frozen too, so a shared unique master the apex READS (e.g. `svc_unique_weapons_l01`, shared with the general orbs) cannot be retuned to leak into the frozen apex while its own bytes stay put.
- **G5** every orb still pays at least 1.50 items of any kind (the empty-box mirror, so a rate band cannot be met by deleting the reward).

Negatives: `py tools/debug/negtest_orb_legendary.py <arz>` - 6 planted defects + the partition-drift guard RED, 3 positive controls GREEN (the wave green, the inversion notice fires, the coexisting breadth/distribution/volume gates stay green on the same db).

### THE HONEST RESIDUE - `BL-R242-DEBT-1`, WILL DECISION

Freezing the excluded apex at its build85 numbers makes it **WEAKER than the general orbs on Legendary legendary-chance: apex 60.9% vs general 75%.** That is an inversion of Will's "keep their better orbs / more loot" - after this lane the general orbs drop legendaries MORE OFTEN than the "better" Toxeus/Leinth apex on Legendary. The apex keeps a **volume edge** (S 1.131 vs 1.125) and a **richer loot4** (21.2 vs 12.7 relics/jewelry/formulae) only. This is the LITERAL byte-unchanged exclusion Will ruled (part 2), and it is the instruction of THIS lane. The gate PRINTS this on every run (`inversion_notice`) and does NOT red on it - lifting the apex above the general target is a composition decision, Will's A/B call:

- **(A) Accept the inversion**: the apex's superiority is volume + loot4 + identical breadth. Cost: nothing.
- **(B) Bump the apex** Legendary/Epic legendary chance to strictly exceed the general target (e.g. apex leg >= 80% / >= 55%). Cost: one follow-up lane; the inversion notice clears in the same commit.

Also disclosed (intrinsic, not a defect): raising the gear rows raises total gear VOLUME per open (~+45% gear on Legendary), partially re-inflating R-240's trim - the smallest-blast-radius lever; the alternative (nudging numSpawn) re-opens R-240 and is not recommended.

### OPEN FLAGS FOR WILL (surfaced, defaults taken per the recon)

1. **Charon/Akremon is treated as GENERAL** (`boss_charon_{n,e,l}01b`, terminal `um_charonform2_ferryman_99` = Akremon after build85). It is neither Leinth nor a Toxeus variant, so by the literal ruling it is general and gets 0/50/75. Its orb currently shares the apex-richer loot4=21.2 (untouched by this wave). Flagged because Akremon is a marquee uber Will may want kept apex-tier.
2. **No blue floor added on Epic/Legendary orbs** - Will only specified Normal's 75% blue. Incidental Epic drops left as-is.

## R-243 [2026-08-12] IMPLEMENTED (branch `fix/soul-rate-10-20`) - lower the soul drop rates further. SUPERSEDES the RATES half of R-105.

**WILL, VERBATIM:**

> "Lets lower the drop rate further, so for non-fixed location bosses the drop rate should be 20%, and for fixed location bosses the drop rate should be 10%."

**THE CHANGE (arz-only, ships as BUILD87):** in `tools/build_svc_database.py`, `SOUL_RATE_FIXED_BOSS` **25.0 -> 10.0** and `SOUL_RATE_NONFIXED` **33.0 -> 20.0**. This supersedes ONLY the two rate NUMBERS of R-105; the classifier `ruled_soul_equip_rate()`, the count-over-class tension set, and every pin are otherwise untouched.

**PRESERVED BYTE-IDENTICAL (not a rate this ruling touches):**
- `SOUL_RATE_COMMON = 0` - Common/trash never drops (R-106). Unchanged.
- `SOUL_RATE_R48_CHAMPION = 100` - the four fought Toxeus champions (`um_toxeus_enslaver_99`, `um_bloodtoxeus_99`, `um_toxeus_hunt_99`, `um_toxeus_hunt_l_99`). Unchanged (R-48/R-90/R-91).
- `SOUL_RATE_ZERO_PINS = 0` heads (`um_polisgaoler_99`, `um_charon_ferryman_99`, `um_tantalus_99`). Unchanged (R-107). Their UNBOUND terminals follow the new **fixed-boss 10%** (`um_polisgaoler_unbound_99` = 25 -> 10; the Charon/Tantalus terminals are non-fixed, 33 -> 20).
- **HELD Charon 39/41/43 + Hades 54** (`SOUL_RATE_UNTOUCHABLE`, `BL-b102-DEBT-2`): Will's older explicit "untouched" outranks the sweep; `double_soul_rulings.verify` enforces byte-identity on all 8 monster records. NOT re-rated.

**THE IMPLEMENTATION NUANCE, RESOLVED.** The ruling's note said "the sweep must recognize 25 and 33 as source cohorts (extend `SOUL_RATE_RATIFIED_COHORTS` to 25/33 OR the equivalent)." The equivalent is already in place and is the CORRECT mechanism here: the release build regenerates every rate FROM UPSTREAM each run (det-2x/3x from the SV source arz), so at policy time a carrier's pre-policy value is its wire/module value (25 boss / 50 random / 66 placed / the SV 10/5/2 sub-tiers), not the 25/33 that R-105 shipped. `ruled_soul_equip_rate` rule 8 (`soul_drop_rate()` fallthrough) re-rates by CLASSIFICATION regardless of the incoming value - non-fixed -> 20, fixed boss -> 10 - so 25 and 33 (and 10/5/2) are all recognized as source values by class, not by a cohort literal. Adding 25/33 to `SOUL_RATE_RATIFIED_COHORTS` would be WRONG: `_apply_soul_rate_policy` derives the count-over-class pin as {carrier in a ratified cohort AND `_soul_is_farmable_boss`} and fails loud on drift, and wire sets EVERY farmable act boss to 25 pre-policy - a 25 cohort would explode that derived set far past the 8-member pin and abort the build. The 25/33-shipped records ARE proven re-rated: `dryrun_soul_rate_policy` over the build86 arz shows the move table **33 -> 20 x770, 25 -> 10 x118** with every pin held, and record_diff vs build86 shows the same footprint.

**CENSUS (dryrun over build86 `ffea3261`, gate-view / idempotent re-derivation):** 770 non-fixed carriers 33 -> 20, 118 fixed-location bosses 25 -> 10 (888 changed). HELD: 4 R-48 champions at 100, the 3 chain heads + 262 unset + 172 Champion + 28 hero-0 + Common at 0, and the 8 Charon/Hades UNTOUCHABLE at 66/25 (byte-identical). Named: `um_polisgaoler_unbound_99` 25 -> 10; `um_charonform2_ferryman_99` / `um_tantalus_unbound_99` 33 -> 20; `boss_satyrshaman_55` (count-over-class) 33 -> 20; `boss_charon_39/41/43` HELD.

**GATE:** `tools/verify_soul_drop_rates.py` reads the two rates from the constants (no literals), so it asserts every fixed boss = `SOUL_RATE_FIXED_BOSS` (10) and every non-fixed = `SOUL_RATE_NONFIXED` (20), all pins intact, with planted negatives that RED if a fixed boss is off 10, a non-fixed off 20, or any pin moves (the honour-guard negative was corrected: it now plants the non-fixed rate, because planting a bare 10 would - correctly - no longer red under R-243).

---

## R-244 [2026-08-11] IMPLEMENTED (branch `fix/supra-legendary-gate`, module `tools/patches/supra_recipe_laws.py`) - the three supra-craft laws

> **NUMBERING NOTE (2026-08-12): this ruling was authored as R-231 on the `fix/supra-legendary-gate`
> lane (cut from build84-dev `7459e22`). In parallel `feat/charon-rework` independently minted **R-231**
> for the Golden Bough rework, which SHIPPED as build85 and owns R-231 (with its R-231-A..I amendments).
> Reconciling this lane onto build87 (`main` tops out at R-243) collided the two, so the supra ruling was
> renumbered to the next free number **R-244** and its four debts moved **BL-R231-DEBT-1..4 ->
> BL-R244-DEBT-1..4**. Ruling numbers are docs-only: the CONTENT below is unchanged and the .arz is
> unaffected. Process law #1: rulings are never silently collided.**

**WILL, VERBATIM, LAW A:**
> "ok for the four epic craftable reagent's, we need to change it so that one of the items needed to
> craft the formula needs to be found in legendary like the rest of the craftable supra recipes."

**WILL, VERBATIM, LAW B:**
> "each craftable supra should have different requirements (we should not have two formulas that both
> require stymphalian, plisskey, and deathweavers legtip)"

**WILL, VERBATIM, LAW C:**
> "the last word should not be dropped in epic, only legendary"

**THE LAWS, stated so a later lane cannot re-break them:** every one of the supra recipes names at
least one reagent whose only obtain paths are Legendary-tier; no two supra craftables name the same
reagent set; and no supra ITEM is reachable from a Normal- or Epic-tier loot surface.

**WHAT WAS WRONG, measured on the build83 ship arz `44499f56` (51,253 records).** LAW A: 4 offenders,
exactly the four thrown Will named; the other 38 were already gated. LAW B: **5 duplicate groups over
15 of the 42 craftables** - a SIX-way axe group Will did not know about, a three-way mace group, and
three pairs including his own example. LAW C: 4 offenders; the supra thrown sat on
`svc_unique_thrown_e01` as well as `_l01`, and through `svc_unique_weapons_e01` that Epic membership
reached **all 16 Epic chest surfaces, via 24 loot tables** (every Epic mod chest, general's hoard,
polis vault, the blood-cave mega chest, the Epic uber orb tables). *(Round-2 correction: round 1 wrote
"51 surfaces" here and in three other places. 51 was the item's TOTAL pre-fix loot-table closure
across BOTH the Epic and the Legendary path; post-fix the closure is 27, all Legendary, so the
Epic-specific part was 24 tables. 51 is separately the mod's whole chest-surface count - 16 N + 16 E +
19 L - which is how the two got conflated. Measured post-fix: `svc_wep_lastword` surf n=0 e=0 l=19.)*
**There is no name collision**: exactly one record in the
database is named The Last Word, `records\drxitem\supra\svc_wep_lastword.dbr`. **No monster pays any
supra**, and Normal was already clean.

**THE FIX: 14 formula fields and 4 loot memberships. No new record, no formula/result change.**

**LAW C IS A RELOCATION, NOT A RETIREMENT.** "only legendary" leaves `svc_unique_thrown_l01`
untouched, so R-186's own ask ("make the legendary thrown weapons droppable") still holds at the tier
Will kept it for. Rule S4c fails the build if a later lane finishes the job Will did not ask for.
R-180/R-186 non-reduction is SUPERSEDED for these four memberships and nothing else; every surviving
member of the Epic thrown table GAINS share (total 155 -> 115).

> **LAW A IS PER-RECIPE BECAUSE THE ONE-MOVE FIX COLLIDES WITH LAW C, and this is the reusable
> lesson.** Promoting the shared `u_vit_wand` off the Epic thrown table would have fixed all four
> recipes with one membership and no formula edit - and it reds C1 on every Epic mod chest in the
> game. The ENTIRE `WeaponHunting_RangedOneHand` universe at `itemClassification = Legendary` is
> **five records**: `u_vit_wand` plus the four supra thrown. `TARGET_IC['e']` is Legendary, so C1
> ("the thrown class is payable at its own tier") can only ever be satisfied by one of those five.
> LAW C removes four; promoting `u_vit_wand` removes the fifth. **Before promoting a shared reagent
> out of a tier, count how many records of its CLASS remain at that tier's target classification.**

**GATES (fail-loud, in the craft gate family; `tools/svc_supra_recipes.py` is the one implementation
shared by the in-build gate, the standalone gate and the negatives):** S1 Legendary-only reagent per
recipe; S2 reagent-set uniqueness (+S2b two formulas of one craftable must agree); S3 every
replacement resolves, is not one of the 13 dead `records\equipmentweapon\axe\` twins, and is
Legendary-reachable; S4 no supra item below Legendary (+S4b the 38 craft-only supras named by no loot
table at all, +S4c the four stay droppable on Legendary). **13/13 negatives behave** (corrected in
place: this line read 10/10 from round 1 and the round-2 delta table read 12/12; the current suite is
13/13), N1 being the shipped defect replanted byte-for-byte.

**S3 EARNED ITS KEEP DURING THE LANE:** the in-flight LAW B table pointed Ten Suns' Wrath at
Zhurong's Firebow, which an EPIC chest pool reaches - it would have de-duplicated the recipe while
adding no gate. The pick is now Qin Warbow (Legendary-only, and Hou Yi's myth is Chinese anyway).

**SPEAR ORPHAN CENSUS (Will, same session: "are there any other orphaned spears that we can make
craftable supra formulas for?") - ANSWER: THERE ARE NONE, and the number is zero rather than small.**
Measured: **0** Legendary-classification spears that nothing in the database names; **0** spear
records in a dead twin folder (`records\equipmentweapon\` contains ONE subfolder, `axe`, with 151
records - the axe case that produced 14 dead axes has no spear equivalent); 22 of the 24 Legendary
spears are chest-reachable and the other 2 are already purposed (`drxitem\supra\wep_spear` = Blood
Whisper, the craft-only supra; `svc_l_runbreaker` = the mod's own guaranteed drop). Of 32
Epic-classification spears exactly 2 sit outside the chest pools and both are purposed. The
`\spear\default\` (**102** records, corrected from 101) and `\spear\old\` (39) records are base
random-generation art and dev-era duplicates: **0 of the 141 carry an `itemLevel`**, which is what
settles that they are not orphaned uniques. *(Round-2 correction, re-measured independently on the
same arz: `\spear\default\` = **102** records with `itemLevel` 0 and `itemNameTag` **0**;
`\spear\old\` = 39 records with `itemLevel` 0 and `itemNameTag` **39**. Round 1 wrote "101" and "no
unique name tag"; the count was off by one and the name-tag half is **false for `old\`**. The
conclusion stands on the `itemLevel` evidence alone. Full class split for the record:
`WeaponHunting_Spear` = 301 records, Common 129 / Epic 32 / Legendary 24 / Rare 14 / unclassified
102, which matches the round-1 Legendary and Epic counts exactly.)*

**ROUND-2 CORRECTION TO THE SPEAR COST ESTIMATE - Will was quoted a price our own shipped code
disproves.** Round 1 concluded new spear supras "would have to be authored from scratch (new item
records + new Text tags + **art**)". The art claim is wrong: `tools/patches/uber_orphan_weapons.py`
(b66) already promoted 14 weapons to the supra tier and its docstring states every result "KEEPS its
orphan's mesh/skin/icon (**no new art** - Will's efficiency law)". Stronger still, **3 of those 14 -
Hati, Sword Fish, Di Jun's Pride - were BASE-GAME-ONLY records absent from this mod's database
entirely**, reconstructed verbatim from the bundled dump `tools/patches/data/b66_orphan_donor_fields.json`
(verified: exactly the 3 keys `hati`, `swordfish`, `dijunspride`). So the donor pool is **not** limited
to orphans already in this arz, and no art work is implied. The honest per-spear cost is **a result
record cloned from a donor + one Text tag + a formula shell + the loot wiring the other 42 already
have**. What remains true is that **no spear orphan exists inside this database**.

**AND THE BASE GAME WAS THEN CENSUSED TOO, WHICH ROUND 1 NEVER DID - THE ANSWER IS STILL NO.** The
corrected cost only matters if a donor exists, and the b66 precedent said donors may live outside this
arz, so the base game's own `database.arz` was measured directly: **440 `WeaponHunting_Spear` records,
of which exactly ONE named Epic/Legendary record is referenced by nothing at all** -
`testpoisonspear`, itemLevel 52, `itemNameTag` = **"BEST SPEAR EVER"**. That is a developer test
asset, not shippable content, and it is the entire pool.

**So round 1's ANSWER was right and only its REASONING was too narrow.** There are no orphaned spears
to promote, in this database or in the base game, and the reason is structural rather than accidental:
the axe case produced 14 orphans because `records\equipmentweapon\axe\` is a dead twin folder, and
**spears have no such folder**. Any new craftable spear supra would therefore be genuinely new content
(a donor-cloned result record + Text tag + formula shell + loot wiring, no art) built on a *live*
base-game spear rather than a revived dead one, which is a different design act from what Will asked
about and needs his explicit go-ahead. `BL-R244-DEBT-1` stays open on that narrowed question only.

### R-244 ROUND 2 [2026-08-11] - the vet caught LAW A failing on one of the four recipes Will named

**HATI WAS NOT ACTUALLY GATED, and the gate said it was.** Round 1 pointed Hati's slot 2 at
`e_da_crescentmoonofartemis` (Crescent Moon of Artemis). It is `itemClassification = Legendary`, no
Normal or Epic chest pool reaches it, a Legendary pool does, and no sub-Legendary loot table names it -
so it passed every arm rule S1 had. **And it gates nothing**, because a divine artifact is never
*found*: it is **made**, and `e_da_crescentmoonofartemis_formula` is paid by the four **EPIC**
`02_act1..4_arcaneformulae_table` records. A player could craft it on Epic and finish Hati without ever
farming Legendary - the exact defect Will filed, surviving inside its own fix, on one of the four
recipes he named by hand.

**ROOT CAUSE: S1 only ever looked at DROP paths.** All four of its arms asked "who pays this item";
none asked "who can BUILD this item". That is a whole class of hole, not one bad pick - the repo
already knew the class existed (`svc_craft_thrown`'s own docstring notes the six IT divine artifacts
are "craftable from base arcane formulae the chests DO drop, but not droppable themselves").

**FIX, two parts, and the second is the one that matters.**
1. **Hati's reagent is now `u_l_artemis'silverbow` (Artemis' Silver Bow).** Same goddess, opposite
   provenance: **nothing in the database builds it**, it is `u_l_` drop-only, and **19 of 19 Legendary
   chest surfaces pay it**. The wolf that hunts the moon is handed the moon-huntress's own bow. The
   four thrown gates remain four different item classes - amulet / **bow** / spear / mace.
2. **`legendary_only` gained arm 5, the craft-path check:** if any formula in the database builds the
   reagent, every one of those formulas must itself be Legendary-tier-only by the same closure test.
   ~~No recursion into the formula's own reagents is needed or wanted~~ **- CORRECTED IN ROUND 3, see
   below: the recursion IS needed, because "the formula is the gate" is false in this database.** The
   round-2 caution behind that sentence was real and survives inside the recursion: formula reagent
   slots are per-difficulty ARRAYS, measured -
   `e_da_crescentmoonofartemis_formula.reagent3BaseName = [02x_vengeance, 03x_vengeance]` - so the
   walk reads them per SLOT (any one variant satisfies a slot; every slot must be satisfied), and
   `03x_vengeance` is a base-game record this mod's arz does not contain, which is why an absent
   record counts as obtainable rather than as a gate.
   `table_tier` was widened at the same time to read the base game's spelled-out convention
   (`xq04 - arcaneformulae_legendary`), so every table paying a formula can be classified instead of
   returning `None` and being silently forgiven.

**ARM 5 IS NOT "CRAFTED REAGENTS NEVER GATE", AND THAT DISTINCTION IS LOAD-BEARING.** Every divine
artifact in the game is a craft result (**77 of 77** have a formula; TQ drops formulas, never
artifacts), so a blanket rule would have redded the two DRX artifact craftables
(`artifact_mortoksskull`, `artifact_plus2`) with no legal fix available and forced a cosmetic reagent
swap into recipes Will never complained about. Measured instead: their gates - Thoth's Glory, Ikon of
Zeus, Marduk's Tablet of Destiny, Golden Eye of Sun Wukong - are genuinely Legendary-gated and **need
no edit**. ~~because they are paid only by the LEGENDARY `03_act1..4_arcaneformulae_table` records~~
**- ROUND-3 CORRECTION: that stated reason was false. Their formulas ARE reachable from an EPIC mod
chest, on 15 of 16 Epic surfaces (`BL-R244-DEBT-4`). What gates them is one level deeper: those
formulas consume `l_ga_doxakalo` (+ the Legendary relic `03_act4_cunningofoddyseus`),
`l_ga_elementalrage` and `l_ga_totemofthepolymath`, and nothing below Legendary pays those.** The
verdict is unchanged and now measured rather than assumed. Negative test N2d is the false-red guard
that keeps it that way; N2c replants the Hati defect and proves the craft arm fires; N2e (round 3)
makes Thoth's Glory's own chain Epic-satisfiable without touching a loot table and proves the
recursion fires. Final: **42 of 42 craftables carry a Legendary-gated reagent under the sound rule.**

**ROUND-2 GATE READINGS, measured on the build83 ship arz `44499f56` with the lane's own two
idempotent writes applied (static gates only; Ship does the build):**

| reading | round 1 | round 2 |
|---|---|---|
| negative tests | 10/10, no craft-path negative existed | **12/12**, incl. N2c (arm 5 fires) + N2d (no false red) |
| craftables carrying a Legendary gate | 42/42 *claimed*, 39/42 in truth | **42/42, proved** |
| thinnest craftable's gate count | 1 (Hati's was bogus) | **1, and every one of them sound** |
| reagents provably Legendary-only | 41 of 92 | **45 of 92** (the widened `table_tier` promotes 4 that the `?`-tier quest tables had been hiding) |
| distinct reagent sets / duplicate groups | 42 / 0 | **42 / 0** (unchanged) |
| supra items droppable | N 0 / E 0 / L 4 | **N 0 / E 0 / L 4** (unchanged) |
| Hati's gate | `e_da_crescentmoonofartemis` (Epic-craftable) | **`u_l_artemis'silverbow`** (drop-only, 19/19 L) |

`svc_craft_thrown.audit_db` (the b81 C+G rules: thrown tier coverage, reagent completability, MI
provenance) reports **0 problems** on the same database, so the b81-adjacent gates did not regress.
`tools/patches/_check_registry.py` selfcheck OK, 60 modules, order hash
`97684dfedee8e62e010d0b42db4ff3adb801e51c4094b30973f92d251802a829`.

**KNOWN RESIDUAL, stated rather than laundered (new debt `BL-R244-DEBT-4`, P2):** an **EPIC** mod chest
reaches the **LEGENDARY** arcane-formula tables on **15 of 16 Epic surfaces** - traced concretely as
`svc_charonhoard_loot_02 -> 03_act4_arcaneformulae_sp -> 03_act4_arcaneformulae_table ->
l_da_thothsglory_formula`. That is a chest-WIRING tier defect that predates this lane and belongs to
the chest-table owner, not to a recipe module. ~~Arm 5 asks whether the FORMULA's own tables are
Legendary, which is the question this module can answer honestly.~~ **ROUND-3 CORRECTION: that
sidestep is what made the gate's stated reason false. The walk now takes this measurement at face
value - an Epic chest DOES pay those formulas - and proves the gate one level below them instead. The
debt stays open and is still the chest owner's to fix; the gate's verdicts no longer depend on it
either way.**

### ROUND 3 (2026-08-11, third vet): THE OUTCOME WAS RIGHT, THE REASON WAS FALSIFIED

**WHAT THE VET MEASURED.** Round 2's craft check read only the tier of the tables that NAME a
formula, on the stated theory that "the formula is the gate". On the lane-applied db, all four
formulas round 2 quoted as its PASS evidence are reachable from **15 of 16 EPIC chest surfaces**
(BFS-derived: `svc_charonhoard_loot_02 -> 03_act4_arcaneformulae_sp -> 03_act4_arcaneformulae_table ->
l_da_thothsglory_formula`). So the theory is false exactly where the ledger asserted it, the module
docstring taught it, and `docs/SUPRA_CRAFTING_GUIDE.md` told players it as fact under a header
promising "no source is guessed". **42/42 still held** - the vet re-derived that independently - but a
future divine-artifact reagent with no Legendary member deeper in its chain would have PASSED while
being fully Epic-craftable. That is round 1's hole class, not a wording nit.

**THE FIX.** `legendary_only` now delegates to **`obtainable_below_legendary`**, which asks ONE
question at every depth: *can a player who never sets foot in Legendary end up HOLDING this record,
by drop or by craft?* Order is the point - measured evidence decides, convention is consulted only
where this database physically cannot measure:
1. record does not resolve -> obtainable (a base-game record the overlay never copied; an unprovable
   claim must never become a PASS);
2. a Normal/Epic chest pool reaches it -> obtainable;
3. a Normal/Epic-tier table in its upward closure names it -> obtainable (the MONSTER path);
4. **the craft path**: for each formula that builds it, if that formula is itself obtainable below
   Legendary AND every one of its reagent SLOTS has one variant obtainable below Legendary, the record
   can be MADE below Legendary. Slots, not a flat list, because a slot is a per-difficulty array;
5. nothing fired. If the record is VISIBLE to the measurement, the silence is the answer -
   Legendary-only. If it is invisible (no pool at any tier, no table anywhere), fall back to the base
   game's own record-name convention: `n_`/`e_`/`0N_` -> obtainable, `l_`/`03_` -> Legendary, no tier
   in the name -> obtainable.

**WHY STEP 5 NEEDS THAT FALLBACK, AND IT IS NOT A LOOPHOLE.** This arz is a ~51k-record OVERLAY, not
the whole game. `n_la_amberflask` resolves, sits in no chest pool at any tier and is named by no loot
table in it. Reading that silence as "Legendary-only" gates the entire base-game artifact chain behind
Legendary and turns `e_da_crescentmoonofartemis` into a PASS - i.e. it re-blesses round 1's defect.
Measured both ways before choosing.

**READINGS (same arz, same two idempotent writes; static gates only, Ship builds):**

| reading | round 2 | round 3 |
|---|---|---|
| negative tests | 12/12 | **13/13**, +N2e (the recursion fires) |
| reagents provably Legendary-only | 45 of 92 | **45 of 92 - identical, and now proved** |
| craftables carrying a Legendary gate | 42/42, right answer / false reason | **42/42, measured** |
| Thoth's Glory's gate | `l_da_thothsglory_formula`'s own table tier (FALSE - an Epic chest pays it) | **`l_ga_doxakalo` + the Legendary relic `03_act4_cunningofoddyseus`** |
| Ikon of Zeus / Marduk's Tablet / Golden Eye | same false reason | **`l_ga_elementalrage` / `l_ga_totemofthepolymath` x2** |
| Crescent Moon of Artemis | RED (asserted from the formula's tier) | **RED, and shown: all three slots of its Epic formula are Epic-payable** |
| S1-S4 / `SCT.audit_db` / `SLB.audit_db` | 0 problems | **0 problems** (51 chest tables) |

**N2e, the negative round 2 could not have written:** make Thoth's Glory's own craft chain
Epic-satisfiable (swap `l_ga_doxakalo` -> `n_ga_furyoftheages`, `03_act4_cunningofoddyseus` ->
`01_act4_shadeofhektor`) **without touching a single loot table**. Round 2's rule cannot see that
plant; round 3's reds on it.

**DOC CORRECTIONS THE SAME PASS (the round-2 correction pass had updated this ledger and left the
board and the player guide behind):** `docs/BACKLOG.md` said "46 of 91 reagents" in two places and the
guide said "91 distinct reagents" / "69 come from chests". Measured: **92 reagents, 45 Legendary-only,
72 chest-payable, 20 that no chest pays** - exactly 20 of the 22 Monster Infrequents, the other two
greens (**Animus**, **Perversion of the Bloodborn** `mi_vit_wand_01`) being chest-payable - **71**
Legendary-chest reachable, `SCT` split **22 MI + 64 ordinary + 6 artifact**. The guide's two artifact
passages no longer tell players the arcane formula is the gate.

### TWO THINGS THAT NEED ONE WORD FROM WILL

1. **The four supra thrown still drop on LEGENDARY (N 0 / E 0 / L 4).** Will's verbatim was "the last
   word should not be dropped in epic, **only legendary**", and R-186 was his earlier ask to make the
   legendary thrown droppable, so stripping the Legendary side too would silently revert a standing
   ruling. Rule S4c fails the build if a later lane finishes that job. **Ratify or correct.**
2. **LAW B is satisfied at the minimum: one changed slot per duplicate.** 42/42 reagent sets are now
   distinct and 0 duplicate groups remain, but the de-duplicated recipes still share two of three
   reagents - the six-way axe group all still carry Shai'tan + Dragonian and differ only in slot 1,
   and Will's own example (Aquimae / Crystal Tear of Nyx) still shares Plissken + Deathweaver's
   Legtip. This is the minimal non-reduction change and it keeps each DRX-authored original intact,
   but **if Will meant "different" more strongly than "not identical", say so and the spread widens.**

---

## R-170 SECOND FOLLOW-UP [2026-08-12] IMPLEMENTED (branch `fix/warden-awakening`, b88) - THE WARDEN WAS STILL MUTE: b63 changed the SLOT, the defect was the ACTION SET. A remote boat NPC must be AWAKENED (`ShowNpc` + `UpdateNPCDialog("Dialog Needed")`) before it is offered.

VERBATIM (Will's bug report, re-confirmed BROKEN ON STEAM after b63 shipped): "when I click on the
guy who travels you to the spartan crypt (warden of the spartan crypt) nothing happens, no dialog
box comes up, nothing."

THIS IS THE R-170 FOLLOW-UP'S OWN LAUNCH GATE FAILING, A SECOND TIME. That entry closed "NOT PROVEN
IN-GAME ... The remaining gate is Will's walk." The walk happened; it failed again. SEVERITY P0 AND
LIVE ON STEAM since 2026-08-06: the catacomb Warden is the SOLE canonical entrance to
`spartacryptlevel2`, so that whole area has been unreachable for every subscriber.

WHAT b63 GOT RIGHT AND WHAT IT GOT WRONG. Its RCA correctly identified the Warden as the only placed
NPC whose entire menu came from an unverified trigger class, and its own HONEST CAVEAT said the two
generators emit a STRUCTURALLY IDENTICAL trigger and that "the operative change is REGISTRATION
ORDER plus generator provenance, not a different mechanism". That caveat was the truth: a decode of
the DEPLOYED `Quests.arc 607ec99c` proves the Warden's trigger is STILL
`Condition_OnLevelLoad -> [Action_BoatDialog]` alone. Moving a slot could not, and did not, change
in-game behaviour. b63's own "next suspect" line named the real shape of the problem - "Action_
BoatDialog binding only for levels loaded at trigger time (test by teleporting in versus walking
in)" - and proposed a GridEntrance DOOR as the cure. Will steered to the NON-DOOR fix. This is it.

THE ACTUAL ROOT CAUSE. A boat NPC that is CO-RESIDENT with the level whose load fires the trigger
(the 14 Helos plaza travelers) is awakened by its own level's load, so `Action_BoatDialog` alone
suffices - which is why those work and masked the defect. An NPC the player TELEPORTS INTO (the
Warden in `CataCube02_FloorLast`, every `svc_area_return_*`, every `svc_testhub_return_*`) is not,
so it needs to be awakened explicitly. `build_svc_database._import_dialog_needed` spells out the
engine rationale: the "Dialog Needed" DialogPak "makes NPCs clickable when assigned via
Action_UpdateNPCDialog. Without it, NPCs render but have no yellow icon and can't be clicked." That
is Will's symptom word for word - the NPC is visible, the click does nothing.

THE MECHANISM IS DRX/SV-UPSTREAM-AUTHENTIC, NOT INVENTED HERE. The one remote-level, teleport-out
NPC in the whole mod that BINDS is the Leinth exit vortex "Ioannes"
(`records/drxmap/bloodcave/portals/vortexportal_exit.dbr`, Class=Npc, `bossfight.lvl`). Its
triggers carry `[OpenDoor,] ShowNpc + UpdateNPCDialog + BoatDialog` in the UPSTREAM SV XPack bytes
this repo ports byte-for-byte - DRX shipped a working remote teleport NPC using this triple before
this project touched anything - and the project already adopted it twice (`cb372fe`
`_promote_leinth_exit_fallbacks`, `d9f6647` `_add_leinth_exit_nokill_fallback`).

IMPLEMENTED (QUESTS.ARC ONLY; arz, Levels, Text and Creatures all UNTOUCHED; no new record, no new
tag, no new QUESTS registration - every trigger still rides the already-registered
`sv_commonmechanics` host step):
- `build_quest_files._npc_awaken_actions(npc)` emits `Action_ShowNpc` + `Action_UpdateNPCDialog(npc,
  "Records\Dialog\Story\Dialog Needed.dbr")` as raw parse-tree tuples decoded VERBATIM out of the
  deployed vortex primary - including its odd `UpdateNPCDialog.delayTime` = uint32 `0x40000000`
  (IEEE float 2.0). Preserved, not "normalized": this is the ONLY awakening shape with upstream
  provenance, and shipping an untested variant of the one thing known to work would repeat b63's
  mistake in a new form.
- The pair is PREPENDED, ahead of the unchanged `Action_BoatDialog`(s), in all three SVC boat
  generators: `_add_helos_traveler_hub_travel` (the Warden at row 0 + every `svc_area_return_*`),
  `_add_testhub_portal_travel` (the 5 `svc_testhub_return_*`), `_add_traveler_enter_offers` (the
  uber enter-offer). 31 triggers upgraded.
- SCOPE IS UNIFORM. The 14 co-resident plaza travelers are UPGRADED too rather than left a second
  class - safe and idempotent by the same reasoning b48/b94 already ship on (ShowNpc on an
  already-shown NPC and re-assigning the standard pak are both no-ops), and one uniform shape is
  what keeps the fail-loud deltas simple enough to actually catch a regression. The SVAERA-authored
  co-resident `portal_master_helos` is the one boat trigger left on the old shape (deliberate, and
  registered as debt).
- FAIL-LOUD DELTAS UPDATED in all three generators (they previously asserted one reference per
  npc/tag): each NPC now gains `2 + n_dests` references per trigger, plus a new
  `_delta("Dialog Needed")` assertion requiring exactly one `Action_UpdateNPCDialog` per emitted
  trigger.
- GATE (no-new-surface-without-a-gate): `tools/debug/gate_boat_npc_awakening.py` (A0-A6), also run
  in-build against the WRITTEN arc. Its NPC roster is DERIVED from the three build tables, so a
  future traveler added without the awakening pair reds the build.

R-170 AND ITS AMENDMENT ARE UNCHANGED AS DESIGN LAW. The Warden still owns EXACTLY ONE route,
`tagSVCEnterSpartaCrypt` ("Descend into the Sparta Crypt"), still lands at `(-5596,-2,-1410)`, and
still carries NO "Helos (Return)" port. DESCEND ONLY, per Will. Every `Action_BoatDialog` payload in
the whole quest is byte-identical to the shipped build; only actions were ADDED in front. Step 1
stays 33 triggers / 39 boat actions / max=33, so `_HUB_PLUS_ENTER_TRIGGERS` conservation holds.
DO NOT "fix" a future Warden problem by re-adding `tagSVCAreaReturnToHelos` to him.

PROOFS (this env; base `8035da0` = the build87 ship):
- HARNESS FIDELITY FIRST - the UNPATCHED code rebuilds the shipped `Quests.arc` EXACTLY
  (`607ec99cbf5fd97135204ad465130722`, 194,963 B), so the diff is attributable to this change alone.
- PATCHED `Quests.arc` = `736cd50a3540a010e2678520922e03ce`, 195,476 B (+513 B), det-2x/3x
  byte-identical (`PYTHONHASHSEED=0`).
- ARC DIFF: 107 -> 107 entries, `CHANGED = ['sv_commonmechanics.qst']` and NOTHING else;
  `open_bloodcave_portal.qst` (the reference vortex) byte-identical.
- PER-TRIGGER DECODE: all 31 upgrades are a PURE PREPEND onto the unchanged BEFORE action list;
  trigger headers, conditions and all BoatDialog payloads byte-identical; both awakening blocks
  field-for-field equal to the vortex.
- Contracts `--only quests`: 0 P0 / 0 P1 / 2 P2 on the new arc AND on the baseline arc under the
  identical config = ZERO new violations. `tests_quests_negative` 31/31 PASS.
- `gate_traveler_responds` PASS three ways (`--specs`, `--specs --canonical`, and against the built
  `Quests.arc` + canonical `Levels.arc`: 31 route owners / 39 routes UNCHANGED, host quest at QUESTS
  index 96 of 255, in-window). `gate_travel_npc_invariants` PASS. `negtest_warden_dialog` 10/10 PASS.
  `validate_tags` PASS (383 mod tags, 0 new).
- ANTI-INERT: the NEW gate run against the DEPLOYED/STEAM `607ec99c` EXITS 1, naming
  `svc_warden_sparta_crypt` among 31 `A1` violations - it reproduces Will's bug as an artifact fact
  and would have caught BOTH the 2026-08-06 and 2026-08-10 regressions. Planted-defect suite 5/5.
- `records\dialog\story\dialog needed.dbr` CONFIRMED present in the shipped arz `3c88e537`, along
  with all 30 SVC boat NPC records, so `Action_UpdateNPCDialog` resolves without an arz rebuild.

NOT PROVEN IN-GAME (`BL-b88-DEBT-1`), AND THE HONEST CAVEAT IS STATED RATHER THAN BURIED
(`BL-b88-DEBT-2`): NO remote boat NPC in this mod has a recorded in-game confirmation yet - the
vortex exit that supplies the reference shape is itself playtest-pending (`BL-b94-DEBT-10`). This is
evidence-backed, not Will-confirmed. The evidence is nonetheless non-circular: the triple is
upstream-authentic, is the project's own adopted mechanism, and directly explains Will's exact
symptom via the engine rationale in `_import_dialog_needed`. Will's check: fully quit TQ + restart
Steam, then click the Warden by the stairs-down in `CataCube02_FloorLast`. If he is STILL mute, the
remaining lever is the GridEntrance door (build24/25 Knossos-to-Uber mechanism).

---

## R-247 [2026-08-13] IN PROGRESS (branch `feat/akremon-enhancement`) - Akremon enhanced significantly + orb rename; second forms are ESCALATIONS (Lethaeus); class-wide multi-form/uber audit; Endless Hunt is a SKELETON with fitting summons; EoAT formula chain + tiered Toxeus souls + soul +all-skills law

Appended VERBATIM from Will's 2026-08-13 rulings (the orchestrator brief packaged them as six numbered parts; the verbatim quotes inside are Will's own words):

1. "akremon the heartwood ablaze got way smaller and turned into a different character completely who was much much
   weaker, he should be enhanced significantly. also he still drops an orb named Charon's Essence"
2. STANDING DIRECTION from 2026-08-12 (the backlogged kit pass, NOW ACTIVATED by ruling 1): make the kit MORE innovative
   by MERGING distinctive skills from multiple sources (some of Telkine Ormenos's moves + Charon + other monsters),
   amgoz1-style, for a truly signature kit. Cite amgoz1_design_voice.md in the content brief (standing creative bar).
3. LETHAEUS (Will 2026-08-13, verbatim): "lethaeus the unremembered has the same problem, the second form of the boss is
   much smaller and much weaker than the original form." In this mod the design law is: the second/final form is the
   ESCALATION (cf. the Soul Gaoler -> unbound final version pattern). A form-2 smaller AND weaker than form-1 = defect.
4. THE CLASS-WIDE AUDIT (implied by two hits; curious-QA law - find them ALL offline, do not let Will discover them one
   fight at a time): enumerate EVERY multi-form boss (actorToSpawnOnDeath chains + any other form mechanism) and every
   uber-tier boss in the shipped arz; measure form-vs-form (scale/HP/damage/defense) and boss-vs-uber-band. Produce the
   full audit table. FIX in this lane: Akremon + Lethaeus (fully, per rulings) + any BLATANT same-class offender (form 2
   strictly smaller AND weaker than form 1 - the D5 blatant-error-sweep precedent; each fix individually justified and
   listed). Borderline/judgment cases: FLAG in the table for Will, do not retune.
5. ENDLESS HUNT IDENTITY (Will 2026-08-13, verbatim): "also toxeus the murderer the endless hunt is still a demon not a
   skeleton and he summons blood hounds which makes no sense." TWO FIXES on um_toxeus_hunt_99 (+ his _l/zzdev siblings if
   they share the defect - enumerate): (a) MESH/RACE: he must be a SKELETON like every Toxeus variant - follow the
   green-mesh lane precedent (Enslaver=SkeletonGrayBlack01New.msh, Devourer=GoldenSkeleton01.msh; pick a distinct clean
   skeleton mesh for the Hunt, in-game-confirmed asset only, no green-glow-class mesh); fix race fields to match the
   family. Note Will said "STILL a demon" - git-archaeology what b98 intended vs shipped. (b) SUMMONS: replace the blood
   hounds (blood = the DEVOURER's theme, not the Hunt's) with summons fitting the Endless Hunt's identity (skeletal
   spear-hunter, endless pursuit) in amgoz1 voice - design your best recommendation (e.g. skeletal huntsmen/spectral
   pursuers in the family's black-shroud style), castability+summon-chain gated (A9 render-chain law), flag the choice
   in not_done for Will's veto. Keep his 4 b98 skills + endless-pursuit mechanics + spear intact.
6. ENDLESS HUNT KILL-CHAIN + TIERED SOULS (Will 2026-08-13 after killing the LEGENDARY Hunt, verbatim): "So I was able to
   kill the demon version of legendary toxeus the murderer, the endless hunt and i got his soul and the mystical orb but
   it didnt drop the forge formula that should allow you make craft the uber toxeus the murderer soul which should allow
   you to summon the toxeus the murderer guy who you cant even fight in the game, toxeus the murderer end of all things.
   the formula to craft his soul should have dropped when i killed the endless hunt. also the endless hunt wasnt using a
   spear, and his soul should let you summon him and it doesnt. also when you pick up toxeus the murder enslaver of souls
   soul, you can summon toxeus the murderer enslaver of souls. the legendary and epic versions of the soul should allow
   you to summon much stronger versions of him instead of all the normal epic and legendary versions letting you summon
   the same version." FOUR items:
   (a) EOAT FORMULA DROP: trace the full chain in the shipped arz - Hunt death -> End-of-All-Things forge-formula drop ->
       forge recipe -> EoAT soul -> EoAT summon. Find WHY a Legendary Hunt kill dropped soul+orb but NO formula (wrong
       record/chance/difficulty row/missing wiring - b98 claimed "EoAT formula" shipped; archaeology what broke). FIX so
       the formula reliably drops from the Hunt (state the chosen chance + justify; Will expected it from HIS kill, so
       default 100% like the soul unless a ruling says otherwise) and the ENTIRE craft->summon chain resolves (every link
       gated: formula item exists, recipe consumes real ingredients, produces the EoAT soul, soul summon castable + A9).
   (b) SPEAR - VERIFY FIRST, FIX ONLY IF BROKEN: Will initially reported "the endless hunt wasnt using a spear" but then
       SOFTENED it (verbatim): "maybe he was using a spear and i couldnt see it, there was a lot going on." So this is an
       UNCERTAIN observation, not a confirmed bug. Byte-verify the whole spear chain: weapon record resolves, equip
       chance/slot correct, anim table carries the spear stances (the thrown-wielder lesson class). If the bytes prove it
       correct: change NOTHING, report it PROVEN with the evidence. Only fix if a real defect shows in the bytes.
   (c) HUNT SOUL SUMMONS HIM: his soul item must grant a working summon of the Endless Hunt (like the other Toxeus souls).
       Trace why it currently does not (missing skill grant, dead pet record, dtype trap) + fix; pet lessons apply
       (Pet.tpl restrictions, permanent-pet spawnObjectsTimeToLive=[], NEVER clone_record for souls - use _ensure_record;
       CLAUDE.md key lessons section).
   (d) TIERED SOUL SUMMONS: measure how the n/e/l tiers of the TOXEUS-FAMILY souls are configured today (one record or
       three, per-difficulty pet rows, identical-or-not - full table in the report; a parallel recon answers Will quickly
       but YOUR measurement is the implementation truth). IMPLEMENT for the Toxeus-family souls (Enslaver + Devourer +
       Hunt + EoAT as applicable): Normal < Epic < Legendary summon strength, Epic/Legendary "much stronger" (justify the
       scaling from the uber band; per-difficulty rows or tier records - pick the mechanism the pet system supports safely
       per the Pet.tpl lessons). The MOD-WIDE extension (every soul in the game tiered) = FLAG as a Will decision with a
       measured landscape table, do NOT implement mod-wide in this lane.
   (e) SOUL +ALL-SKILLS BONUS (Will 2026-08-13 follow-up, verbatim): "also the epic and legendary versions of these
       toxeus the murderer souls should give you +2 and +3 to all skills respectively and +1 to all skills for the normal
       difficulty soul." EXACT LAW for the Toxeus-family soul ITEMS (the wearer bonus, on the soul-as-equipment):
       Normal tier = +1 to all skills, Epic = +2, Legendary = +3. Use the base-game +all-skills item mechanism
       (augmentAllLevel or whichever field base items provably use - verify from a base +all-skills item), correct dtype
       (the INT/FLOAT corruption trap), stacking sanely with whatever the souls already grant. Applies to "these toxeus
       the murderer souls" = the family rosters in (d).

STATUS: implementation in this lane (feat/akremon-enhancement). Note on R-231-E: ruling 1's "enhanced
significantly" (with the "ultimate boss tier" context) re-anchors the Akremon durability calibration
off the R-231-E Gaoler frame onto the measured Toxeus band; R-231-E correction 10 is SUPERSEDED on
that one axis (durability reference frame), and charon_rework.verify()'s band gate moves with it.

### R-247 PARTS 7 + 8 (2026-08-13, second orchestrator packet, appended VERBATIM same-turn)

7. CHESTS + DEVOURER SPAWNS (Will 2026-08-13, ANGRY, verbatim): "wtf did you do to all the chests like toxeus the
   murderer devourer of blood's stash? Revert it back to what it was dropping in the original sv you nerfed the fuck
   out of it. also on normal difficulty toxeus the murderer devourer of blood wasnt even there guarding his stash, he
   should spawn there 100% of the time on every difficulty. also something else got messed up where toxeus the
   murderer, enslaver of souls is spawning in the entrance to the blood cave next to the tattered parchment where
   toxeus the murderer, devourer of blood should be spawning at a 33% rate." THREE items:
   (a) CHEST REVERT: measure the Devourer's stash chest (the blood-cave chest-room Majestic chest guarded by
       um_bloodtoxeus_99) + the family of uber stash chests: CURRENT loot vs ORIGINAL SV 0.98i (the upstream arz =
       the design bible; decode the SV originals). Identify WHICH wave nerfed them (prime suspects: R-240 loot-volume
       trim [build84] and R-242 orb-chance rework [build86]) and REVERT these stash chests to the original-SV drop
       richness. LEDGER DISCIPLINE: R-240/R-242 were Will-ratified - this ruling SUPERSEDES them FOR THESE CHESTS;
       amend the ledger entries with the scope carve-out, do not silently contradict them. Enumerate exactly which
       chests you revert (the "chests like ... stash" class = the uber/boss stash chests; general world loot stays
       under R-240) and show before/current/after tables.
   (b) DEVOURER STASH SPAWN 100% ALL DIFFICULTIES: on Normal he was ABSENT from his stash. The M15 mechanism put
       um_bloodtoxeus_99 at 100% into the chest-area pack proxy (egg_blooddragon_pack). Decode the pool per-difficulty:
       find why Normal has no Devourer (difficulty-gated row / champion-cap equation / pool weights) and fix to 100%
       spawn on Normal+Epic+Legendary.
   (c) PARCHMENT SPOT = DEVOURER at 33%, NOT ENSLAVER: at the blood-cave entrance beside the tattered parchment, the
       ENSLAVER is spawning where the DEVOURER should spawn at 33%. Decode the parchment-area pool (the old BACKLOG
       queued items "PARCHMENT REPOINT" + "33% CHANCE retune championChance 50->33 via toxeus_suite" - check whether a
       half-landed change caused the wrong variant); fix: Devourer at 33% there, Enslaver removed from that spot
       (verify where the Enslaver SHOULD spawn per the ledger and that his correct spawns remain intact).
8. ENSLAVER EPIC DIFFICULTY - NOTE ONLY, DO NOT TUNE (Will 2026-08-13, verbatim, append to ledger as an OPEN TUNING
   QUESTION): "I am level 70 running through legendary difficulty easily and I still cant kill toxeus the murderer,
   enslaver of souls on epic difficulty since I just kill myself when i hit him. I have like all the best legendary
   gear, all of it enchanged, and two normal difficulty toxeus the murderer, enslaver of souls pets both of whom i
   have summoned and I still cant kill him... I hit him like 4 or 5 times and then i have to hit one of his demon guys
   to restore health since I have like 50% attack damage converted to health which doesn't work on skeletons but which
   works on his demons... maybe i need to get to like level 90 and come back idk. i can now kill the normal difficulty
   variant with both my pets but he is like level 41 or something. Maybe this difficulty setting is right, idk but
   make note of it." Record with the mechanics observation: melee-leech builds are DOUBLE-countered (reflect self-
   damage + undead leech-immunity blocks sustain on the boss), pets cannot outpace his heal. Measure + report his Epic
   reflect%/heal-rate/HP as data for the future tuning decision. NO stat changes to the Enslaver in this lane.

#### R-247.8 OPEN TUNING QUESTION - the Enslaver on Epic (MEASURED, no change made)

Measured from the shipped arz `a86afc15` (`um_toxeus_enslaver_99`, Epic values): **charLevel 68,
characterLife 45,000, characterLifeRegen 12.0/s (flat, all difficulties), hand 350-500**, reflect via
`svc_toxeus_passiveproperties_monster` = **defensiveReflect 30% at defensiveReflectChance 33%** (ALREADY
reduced from 100/33 by R-103/R-107 - the shipped state IS the post-nerf reflect), plus
defensivePercentCurrentLife 20, defensivePhysical 40, dodge 15, deflect 33. Race Undead = the engine's
leech-immunity class, so Will's 50% ADCTH sustains on the DEMON adds but never on the boss - exactly his
observation; his two NORMAL-tier pets (18k life post-R-247.6d) cannot outpace 12/s regen + reflect
chip on himself. NO change in this lane per Will's own "Maybe this difficulty setting is right, idk but
make note of it". Future levers if he rules: reflect chance/magnitude (one clone field each),
characterLifeRegen, or an undead-leech partial-bypass on his record. OPEN - Will's call.

#### R-247.7 measured verdicts + supersessions (this lane, `tools/patches/r247_bloodcave_rulings.py`)

* **7(a) THE NERF WAVE IS R-240 ALONE, and only its VOLUME lever.** SV 0.98i originals
  (`upstream/soulvizier_098i` arz) for `loottable_hidden_bloodcave_{01,02,03}` run
  `numSpawnMin/MaxEquation = (3+(1.8*numberOfPlayers))*3.8 / *4.1` = **~18.2-19.7 loot iterations
  solo**; the shipped build90 tables run `*0.323/*0.3485`, `*0.361/*0.3895`, `*0.399/*0.4305` =
  **~1.6-2.1 iterations** (the R-240 per-tier calibration; an ~11-12x volume cut - Will's "nerfed the
  fuck out of it"). R-242 is MEASURED NOT INVOLVED: its 15-general-table chance calibration never
  touched these tables (their loot1/2/5/6 chances sit at the pre-R-242 40.0, not the 46.5-67.2 R-242
  band), and their relic row loot4Chance 21.2 is byte-equal to the SV ORIGINAL 21.2 (R-241's "derived
  family value" IS the SV value here - nothing to revert on that axis).
  **SUPERSESSION (scope carve-out): R-247.7a removes exactly these THREE tables from R-240's trim
  scope and V1 canonical ceiling** (`svc_loot_volume.R247_STASH_EXEMPT`); the revert restores the SV
  numSpawn equations verbatim. Chances/weights/members are NOT reverted: the shipped 40.0 chances +
  widened weights + svc-unique rows carry R-181's parity contract and the mod's own unique items, and
  they are all >= the SV values - so the reverted chest pays >= original-SV richness on every axis
  (~19 iterations x higher-than-SV chances). Every OTHER R-240 surface (cage, hoards, orbs, world
  loot) stays under R-240 unchanged. The revert class was ENUMERATED by a full both-arz sweep: the 3
  bloodcave tables are the ONLY SV-original stash-chest tables the trim reached (the other 15 trimmed
  SV records are all uber-ORB tables = the R-242 orb class, untouched here; the cage/hoard/vault
  stash chests are mod-authored with no SV original = flagged for Will below, not reverted).
* **7(b) NO difficulty-gated row EXISTS in the shipped bytes.** The egg_blooddragon pool is
  difficulty-invariant: spawnMin=spawnMax=4, championChance=100, championMin=championMax=3 (3 blood
  dragons), name1..3 = um_bloodtoxeus_99, proxyPoolEquation NEUTRALIZED, proxy difficulty file =
  difficulty_04 (the same file EVERY proven boss proxy uses), limits = limit_bloodtoxeus [1..110] on
  N/E/L. Under the mod's own RE'd + negative-tested spawn model (champions REPLACE mains; guaranteed
  mains = spawnMax - championMax = 1) the Devourer is ALREADY guaranteed on every difficulty from
  these bytes - the Normal absence Will saw is NOT derivable from any decoded DB field. Fix shipped:
  the pool is HARDENED to the in-game-proven `_BT_POOL` byte-shape class (per-slot `limit1..3=1` +
  weight 150, the shape Will has repeatedly seen deliver the Devourer at the entrance ambush), and
  the residual channels (engine champion-budget runtime behaviour; a per-difficulty flag on the map
  INSTANCE) are registered as `BL-R247-DEBT-6` with the escalation path (dedicated solo guard proxy,
  the q_yard shape) pre-designed. The closing proof is Will's Normal-difficulty look.
* **7(c) ROOT CAUSE: TWO set-pieces share the parchment chamber.** The 33% Devourer ambush
  (`q_bloodtoxeus_ambush`, pool = 1 Devourer + 2 blood demons, chanceToRun 33 - wired CORRECTLY) was
  RELOCATED into `drxFirstxistion_connection` by b79; the A1/build36 **Enslaver warband set-piece**
  (`q_enslaver_warband`, chanceToRun **100**, Enslaver + 4 marauders) was ALREADY placed in that same
  chamber ~26.6u away. Will therefore meets the 100% Enslaver warband "next to the tattered
  parchment" and reads it as the Devourer spawn gone wrong. The old BACKLOG "PARCHMENT REPOINT /
  championChance 50->33" items are NOT the cause (the 50% parchment pool was retired 2026-07-14,
  never wired; the ambush IS at 33). Fix shipped: `q_enslaver_warband.chanceToRun 100 -> 0` (the
  placed instance goes dormant; the chamber then holds exactly the ruled state - Devourer @33%,
  Enslaver gone). **SUPERSESSION: R-247.7c supersedes the A1/build36 warband PLACEMENT at this spot.
  KNOWN COLLISION with R-18** ("the dependable per-encounter beat is the PLACED warband set-piece"):
  the Enslaver's dependable placed beat is now VACANT - his remaining spawns are the rare roam
  (weight-1/K=600, R-18-frozen), the egypt/orient undead-pool rares, and the TESTHUB yard
  (`q_yard_enslaver`, untouched). Relocating the warband to a DEEPER blood-cave pocket is a one-spec
  map-lane change registered as `BL-R247-DEBT-7` (WILL DECISION on the destination; this arz lane
  does not move map placements).
