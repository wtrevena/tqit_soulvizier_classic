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
- R-7 [2026-07-16] PENDING (feat/black-poison) "we have wanted the devourer to have a literal black poison asset from the beginning and use that all along" - CREATE svc_black_poison; it is the Devourer's poison AND End of All Things' strike buff. Colors may only be claimed from in-game-confirmed assets.
- R-8 [2026-07-16] IMPLEMENTED feat/toxeus-undivided (b72) End of All Things: name "Toxeus the Murderer, End of All Things"; ring "Soul of Toxeus, End of All Things"; formula demands LEGENDARY tier of the 3 Toxeus souls; 11-item kit per verbatim rulings (unlimited energy; NetherStrike max 0.5s; max SmokeScreen; max Galefury-granted skill; Tears of Blood 3s; Murderer's Edge + black poison (R-7); Entropy aura; Blood Feast; thralls = blood-cave tall casters w/ bloodhounds; The Ending w/ Light-of-Helios flash visual; Arrat the Corruptor AOE); ash-pale body + per-skill fragment colors; stronger than every Toxeus champion.
- R-9 [2026-07-16] PENDING (feat/black-poison) "let the Rite of the Undivided drop wherever else any supra / uber weapons formulas have a chance to drop".
- R-13 [2026-07-16] PENDING (feat/black-poison) "also make it so if you kill either toxeus the devourer of blood of toxeus the enslaver of souls you also get the formula" - Rite of the Undivided ALSO drops on killing the Devourer OR the Enslaver (read as guaranteed on-kill; implementer flags if convention argues for a chance instead). Extends R-9 (both sources coexist).
- R-10 [2026-07-16] IMPLEMENTED fix/runtime-green (b75) + PENDING follow-up: Enslaver summon = BLACK (steal the marauders' shadowcloak smoke). Diadochi generals + Helepolis share the green-rendering 343_dark_smoke - swap after Will confirms the Enslaver reads black.
- R-11 [2026-07-16] PENDING (fix/runtime-green pet-identity commit) "Toxeus the murderer, enslaver of souls is a beastman not a skeleton" - Enslaver family race = skeleton/Undead; all boss-summon pets inherit race/sounds/distress from their SOURCE monster.
- R-12 [2026-07-16] IMPLEMENTED b71 skeleton identity: Enslaver summon-skill icon + pet-bar portrait = one consistent skeleton (deathwalker) identity; marauders do NOT show in the pet bar (no portrait requirement).

## Masteries
- R-20 [2026-07-16] IMPLEMENTED b44/b45 revert + SV alignment: trees match SV ground truth; Will's hand-tuned overlays preserved; shapes = isCircular per SV (PoisonousGas circle; BladeFury, SmokeScreen squares).
- R-21 [2026-07-16] IMPLEMENTED b70 "Hunting eviscerate should be a square".
- R-22 [2026-07-16] IMPLEMENTED b70 (C2) col6 restack verbatim: "lets have darklings be in the same lane as throwing knife, but we will have darklings unlock at 10, dark aperture unlock at 16, and then above it we will have throwing knife at 24 and the augment to throwing knife at 32 so we wont have lines behind one another".
- R-23 [2026-07-16] IMPLEMENTED feat/mastery-sv-fix "so how does dark invigoration work? I think it should augment shadow link" - genuinely augments via SkillTree slot order (proven mechanism); NEVER reorder skillName{N} slots (binding surface).
- R-24 [2026-07-16] PENDING (fix/mastery-unlock) "Proceed with fixing the masteries as appropriate" - b74 audit implementation: every button's real unlock == its drawn row (Warfare col3 + Earth col4 ladders as WILL-VETO).
- R-25 [2026-07-16] STANDING Darklings/DarkAperture/ToxicConcoction/ShadowStalker are PRE-0.98i SV content ("I did not create these by hand") - their canonical layout authority = SV 0.9/0.41 extractions.

## World / placement
- R-30 [2026-07-16] PENDING (fix/chumbi-lag) verbatim: "you need to space these monsters out instead of putting them all on top of one another" + fountain death-loop = never again: SPACING LAW (fountain/NPC clearance + min inter-encounter distance, permanent placement gate).
- R-31 [2026-07-16] PARTIALLY IMPLEMENTED b46, REMAINDER PENDING (fix/chumbi-lag) boss pileup unstacked to intended locations; the summon issue is CO-PRIMARY ("both are making the game freeze"): tomb-guardian dogs hard-capped + TTL, sepulcher fight playable standing alone.
  - **STATUS 2026-07-28 (branch `fix/debt-gate`, B76-R2-SUMMON-GATE):** the *summon-cap* half is IMPLEMENTED and now **GATED**. b46 restored the finite `spawnObjectsTimeToLive` on the sepulcher/tomb-guardian chain (`tools/patches/summon_caps.py` `_TTL_TARGETS`: tomb guardians 5.0s per SV's own shodema value, alastor skeleton warrior/archer + the recursive `summonpet_undeadmelee01` 20.0s per the four_generals precedent). As of today `summon_caps.verify()` additionally enforces the whole CLASS - no unbounded fast summoner (`Skill_*SpawnPet*` with no petLimit, no TTL, cooldown < 10s) may enter the arz outside an evidenced waiver of 8 base/dead/test records - so a NEW freeze-class summoner can no longer ship unnoticed. Deliberately NOT a blanket petLimit-no-TTL rule (~140 healthy skills have that shape). Planted negative test: `py tools/patches/summon_caps.py --negtest`.
  - **STILL PENDING (do not read the above as R-31 closed):** (a) the *boss pileup* half - unstacking the piled bosses to their intended locations (the b46 Monster Test Yard removal addressed the TESTHUB QA cluster, not the general SPACING LAW of R-30); (b) "sepulcher fight playable standing alone" is a RUNTIME judgement only Will's in-game pass can settle. The ⚠️ WILL-VETO on the exact TTL seconds also stands - the fix is the PRESENCE of a finite TTL, not the value.
- R-32 [2026-07-16] PENDING (fix/chumbi-lag) boss reward containers are NEVER quest-gated chests (the widow-quest Dead Adventurer's Chest reuse).

## Souls & items
- R-40 [2026-07-16] PENDING (fix/soul-tiers) souls scale across normal/epic/legendary (Blood Cult High Priest epic == normal = the defect class); strict-progress gate.
- R-41 [2026-07-16] IMPLEMENTED fix/formula-names (b80) formula display names match what they craft ("Mythic Formula - Crystalline Mask" crafts Galefury) - fixed by repointing `ar_hunter_helm_formula.dbr`'s description onto SV098i's own already-correct, previously-orphaned `tagRecipe_ar_helm_fix`; full 245-formula sweep found no other instance; permanent gate added (`tools/patches/formula_names.py` verify() + `tools/validate_formula_names.py`). See `docs/reports/b80_formula_names.md`.
- R-42 [earlier, STANDING - PARTIALLY SUPERSEDED by R-48 (2026-07-27) for the two fought Toxeus champions ONLY; every other record's rate stands unchanged] Munderizer over-band damage BLESSED; Shadow Link large radius KEPT; legion terminal drop 66 fine for now (revisit next souls pass); soul drop rates: random 50 / placed 66 / boss 25.
- R-43 [2026-07-16] IMPLEMENTED fix/soul-tiers @ d9353e4 (b85, pending merge) "the high priest soul should allow you to summon the high priest" - the Blood Cult High Priest soul's summon = the HIGH PRIEST himself (his identity/mesh/kit as the pet, all 3 tiers scaled), per boss-summon conventions + the b71/b81 identity laws (icon/portrait/race/sounds = High Priest). Companion check: epic soul must spawn the epic-tier pet (verified true roster-wide in b78, re-proven for this family).

## Process (meta-rulings)
- R-50 [2026-07-16] "what do you need to do to manage your tasks better so we dont end up with stuff like this happening over and over" -> THIS LEDGER + retirement protocol + player-surface checklist + no-new-surface-without-a-gate + debt register. See CLAUDE.md standing rules.

---

## HISTORICAL BACKFILL (b84 sweep, round 1, 2026-07-16) - see docs/BACKLOG.md DEBT REGISTER for the
## open-item counterpart of this sweep. Numbering continues each section's existing range; sections
## reserve a decade (Toxeus 1-19, Masteries 20-29, World 30-39, Souls 40-49, Process 50-59); new
## topics get a fresh decade (Legal 60-69).

### Toxeus arc (continued)
- R-13 [2026-07-14] IMPLEMENTED (M4 MP-compat sweep, feat/toxeus-encounter-suite) Will's call verbatim:
  "we need to retire the one we are adding and just update the 15% one to 33%." Retires the never-wired
  ~50% parchment-room Toxeus feature (`demon_01_cluster_toxeus50` pool+proxy, `q_bloodtoxeus_lone_50`)
  entirely; the sole corridor Blood-Toxeus roll stays the `drxFirstRoom` ambush, `chanceToRun` retuned
  15->33. SUPERSEDES R-14. Source: docs/MULTIPLAYER_COMPAT.md M4.7 item 5; docs/reports/
  toxeus_suite_recon.md sec 0.
- R-14 [2026-07-09] SUPERSEDED by R-13 (2026-07-14) "put toxeus devourer of blood there too with 50%
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
- R-43 [2026-07-14] IMPLEMENTED (D2/FIX 5) Will's directive, verbatim: "Do not promote tomb guardian
  and do not have him drop a soul." `um_tombguardian_26` kept Common / `chanceToEquipFinger2=0.0`; the
  attached-but-undroppable `um_tombguardian_soul_{n,e,l}` rings were detached then retired (removed
  from the arz) along with their orphaned name tag. Source: docs/reports/souls_quality_fix.md sec 3
  (P2-a).
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
