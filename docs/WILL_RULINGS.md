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

## Process (meta-rulings)
- R-50 [2026-07-16] "what do you need to do to manage your tasks better so we dont end up with stuff like this happening over and over" -> THIS LEDGER + retirement protocol + player-surface checklist + no-new-surface-without-a-gate + debt register. See CLAUDE.md standing rules.

---

## HISTORICAL BACKFILL (b84 sweep, round 1, 2026-07-16) - see docs/BACKLOG.md DEBT REGISTER for the
## open-item counterpart of this sweep. Numbering continues each section's existing range; sections
## reserve a decade (Toxeus 1-19, Masteries 20-29, World 30-39, Souls 40-49, Process 50-59); new
## topics get a fresh decade (Legal 60-69). **2026-07-28: Souls & items 40-49 is FULL (R-49 was
## claimed 2026-07-27 by the fix/devourer-chest lane) - its OVERFLOW decade is 70-79.**

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
- R-16 [2026-07-14] PENDING (BACKLOG entry "approved-by-Will-2026-07-14", NOT scheduled) Legendary-only
  Toxeus stalker via the proven Hydra fixed-placement pattern (`pool1` empty + `poolLegendary1` = boss
  pool) - APPROVED, QUEUED, not built; the already-shipped roaming Endless Hunt (Hades-confined) stays
  as-is alongside it, Will's call whether it is additive or a replacement. Source: docs/
  MULTIPLAYER_COMPAT.md M4.6-M4.7; docs/reports/toxeus_suite_recon.md sec 5.3.
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
- R-47 [pre-build41, STANDING] "the generic orb target Will wants" [paraphrased] - custom Boss-class
  encounters (Blood Toxeus, Enslaver, Vashkarr, Broodmother, Dorus, Sarkoth, Gorrahk, Ilsevar,
  Voranthys, Tantalus, Mnemophage-core, Ephialtes, ...) drop the un-named generic apex orb
  (`genericbossorb_04`, no bespoke "X's Essence" name) as the established convention - NOT a bespoke
  named essence per boss. Source: docs/reports/b53_orb_essence.md sec 4.

### Legal / permissions (new section)
- R-60 [2026-07-04] STANDING "Will's decision, 2026-07-04 - no Lite build" - KEEP DRX (Dragonlord's
  visual overhaul) in the shipped mod; `-LiteMode` is off the table (it strips assets the blood cave
  itself needs). Keeping DRX keeps Dragonlord's permission on the Workshop-publish critical path.
  Source: docs/STEAM_RELEASE.md:33 (the verbatim string); docs/SHARE_AND_PLAY.md; docs/PERMISSIONS.md; CLAUDE.md content-gaps section (same ruling,
  multiply cited).
- R-61 [2026-07-10] STANDING "he said it was cool" (Will relaying soa's verbal permission) - soa
  (SVAERA author) granted verbal permission for the additive mastery-graft reuse (R-28); a written
  confirmation is still an open standing obligation, as is amgoz1's and Dragonlord's written
  permission (neither captured in writing as of 2026-07-10). Source: docs/PERMISSIONS.md.

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
