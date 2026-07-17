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
- R-3 [pre-b41, STANDING] PENDING (fix/bloodtoxeus-spawns) Blood Toxeus spawns next to the blood-cave hidden chest 100% of the time - broken by the q_bloodtoxeus_lone_50 "orphan" retirement and/or placement loss; the chest encounter is deliberately adjacent-to-chest (exempt from generic clearance).
- R-4 [2026-07-16] PENDING (fix/bloodtoxeus-spawns) quest rename "Toxeus the Murderer, Devourer of Blood's Stash"; chest rename "Toxeus the Murderer, Devourer of Blood's Hidden Chest" (was Esti's Hidden Chest).
- R-5 [2026-07-16] IMPLEMENTED feat/toxeus-champions (b73) "the blood toxeus should have the Tears of Blood ability granted by the Arcane Formula - Blood of Ares" + "The toxeus devourer of blood should have maybe a 10 second cool down on a weaker version" - NOTE ground truth: corridor + deep boss share ONE record; both currently weak-10s; full-strength corridor variant = OPEN Will decision.
- R-6 [2026-07-16] IMPLEMENTED feat/toxeus-champions (b73) Enslaver + Devourer get unique identity kits ("his abilities are pretty generic") - Soul-Rip / Chains of Servitude / Unholy Dominion; Blood Frenzy. Per-ability veto open on DEV.
- R-7 [2026-07-16] PENDING (feat/black-poison) "we have wanted the devourer to have a literal black poison asset from the beginning and use that all along" - CREATE svc_black_poison; it is the Devourer's poison AND End of All Things' strike buff. Colors may only be claimed from in-game-confirmed assets.
- R-8 [2026-07-16] IMPLEMENTED feat/toxeus-undivided (b72) End of All Things: name "Toxeus the Murderer, End of All Things"; ring "Soul of Toxeus, End of All Things"; formula demands LEGENDARY tier of the 3 Toxeus souls; 11-item kit per verbatim rulings (unlimited energy; NetherStrike max 0.5s; max SmokeScreen; max Galefury-granted skill; Tears of Blood 3s; Murderer's Edge + black poison (R-7); Entropy aura; Blood Feast; thralls = blood-cave tall casters w/ bloodhounds; The Ending w/ Light-of-Helios flash visual; Arrat the Corruptor AOE); ash-pale body + per-skill fragment colors; stronger than every Toxeus champion.
- R-9 [2026-07-16] PENDING (feat/black-poison) "let the Rite of the Undivided drop wherever else any supra / uber weapons formulas have a chance to drop".
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
- R-31 [2026-07-16] PENDING (fix/chumbi-lag) boss pileup unstacked to intended locations; the summon issue is CO-PRIMARY ("both are making the game freeze"): tomb-guardian dogs hard-capped + TTL, sepulcher fight playable standing alone.
- R-32 [2026-07-16] PENDING (fix/chumbi-lag) boss reward containers are NEVER quest-gated chests (the widow-quest Dead Adventurer's Chest reuse).

## Souls & items
- R-40 [2026-07-16] PENDING (fix/soul-tiers) souls scale across normal/epic/legendary (Blood Cult High Priest epic == normal = the defect class); strict-progress gate.
- R-41 [2026-07-16] PENDING (fix/formula-names) formula display names match what they craft ("Mythic Formula - Crystalline Mask" crafts Galefury).
- R-42 [earlier, STANDING] Munderizer over-band damage BLESSED; Shadow Link large radius KEPT; legion terminal drop 66 fine for now (revisit next souls pass); soul drop rates: random 50 / placed 66 / boss 25.

## Process (meta-rulings)
- R-50 [2026-07-16] "what do you need to do to manage your tasks better so we dont end up with stuff like this happening over and over" -> THIS LEDGER + retirement protocol + player-surface checklist + no-new-surface-without-a-gate + debt register. See CLAUDE.md standing rules.
