# b71 - ENSLAVER CHAIN RCA + upstream fix (round 1): skeleton identity + anti-oscillation chain gate

Branch `fix/enslaver-chain` (worktree). DB lane (`apply_svc_patches.py` + registry
module `enslaver_pet_fx.py`). Ground truth: build44 LIVE arz `439a9279` (== worktree
`work/SoulvizierClassic/Database/SoulvizierClassic.arz`), build41 `eb8bc377`
(`local/baseline_build41.arz`, the b55 GO state), build43 `e6ec1459`.

## Will's report (build44 in-game, P1 REPEAT-FILED - "we are just oscillating here")
Three symptoms:
1. "toxeus the murderer enslaver of souls summon is now green" (screenshot: the
   summoned skeleton pack wrapped in a GREEN cloud in Fayum Oasis).
2. "the icon for the skill to summon him is now the icon that the shadow stalker
   summon has."
3. "the icon in the pet display bar (top-left) shows the image for lyia the summoned
   pet we built the others based on. Find a skeleton example for toxeus and make it
   consistent across the summon skill icon and the top-left pet-bar icon."

## THE OSCILLATION TIMELINE (and why every gate missed it)
- **b38** (build ~) gave the ENCOUNTER monster `um_toxeus_enslaver_99` an all-black
  rig (charcoal skin + darksmoke shroud, green weapon glow deleted). Will confirmed
  the fought Enslaver is black.
- **b40** (build41) gave every `_build_boss_summon` boss summon a fitting granted-SKILL
  button icon (was the Lyia nymph). The Enslaver was assigned `stealth\stalkerup`
  ("he is a ShadowStalker demon"). b40's report **explicitly deferred** the pet-bar
  `StatusIcon` (Lyia residue) as "a separate surface ... left for a future pass".
- **b55** (build41, GO) black-rigged the soul-summon PET records (strip green Lyia FX,
  inherit the source's dark shroud) for the Enslaver / marauder / Hades-Marshal families.
  It was a **data-only dry-run vet, never confirmed in-game.**
- **b44** Will tests in-game and reports the three symptoms above.

**Ground-truth reconciliation (the decisive finding): the ENTIRE Enslaver chain is
BYTE-IDENTICAL between build41 (b55 GO) and build44** - soul items, granted skill,
all 3 main pets, all 3 marauder sub-pets, the Hades-Marshal family: every record
`IDENTICAL` (`scratchpad/diff_chain.py`). A roster-wide chain diff of all 51 boss-summon
soul families confirms **0 icon changes and 0 spawnObjects changes** build41->build44
(`scratchpad/roster_sweep.py`). **The working theory that a build42 module regenerated
or re-pointed the chain is REFUTED.** Nothing regressed in build42. The symptoms are
LONGSTANDING state that Will only now scrutinized:
- Symptom #2 = b40's deliberate `stalkerup` icon (present since build41).
- Symptom #3 = the Lyia `StatusIcon` residue b40 deferred (present since forever).
- Symptom #1 (green) = NOT reproducible from any current DB field (see below).

**Why every gate missed it:** b55's `verify()` asserted its OWN pet FX FIELDS in
isolation (record-level), so it stayed green while the LIVE CHAIN (soul->skill->icon,
pet->portrait) diverged. There was no CHAIN-level gate. That is the record-level-vs-
chain-level gap this round closes.

## The green (symptom #1) - RCA verdict: not a current DB defect
Exhaustive ground-truth analysis of the build44 arz:
- The 3 Enslaver pets (`toxeus_enslaver_1..3`) are field-for-field identical to the
  CONFIRMED-BLACK encounter monster on every persistent visual field (mesh
  `RevenantPoison.msh`, `baseTexture=NewSkeleton_Charcoal.tex`, shroud
  `svc_enslaver_darksmoke`); `NewSkeleton_Charcoal.tex` RESOLVES in the shipped arcs
  (so no fallback to a green default skin).
- The proven green mechanism is the `envenomweapon` buff (`skillWeaponTintGreen=1.0`
  + green poison FX) - demonstrated by the Devourer of Blood pet `bloodtoxeus_1`
  (INTENTIONAL green, SAME RevenantPoison mesh) which carries `buffSelfSkillName=
  envenomweapon`. The b55-fixed Enslaver/marauder pets carry **zero** green markers
  (envenom / heartofoak / regrowth / natureswrath / sylvannymph / maenad all stripped),
  and the marauder's default attack is a plain `arrowdefault01` projectile (not green).
- The marauder pet is field-identical to the marauder MONSTER (both `ShadowStalker.msh`,
  no baseTexture, `drxshadowcloak` shroud whose pfx uses dark-smoke textures).

**Conclusion:** the DB cannot reproduce the green Will sees; the pets are byte-identical
to the b55 GO state and carry no green source. The most likely cause is **save-state
persistence** - b55's "no fresh drop needed" claim was wrong for an ALREADY-SUMMONED
permanent pet (spawnObjectsTimeToLive removed): an Enslaver pack summoned before the
arz updated keeps its old (pre-b55) green appearance until RE-SUMMONED. A residual
faint pfx tint on the dark shroud is a secondary possibility (asset-level, not DB).
Either way, no speculative FX change is made this round (that would risk regressing the
confirmed-black state); the chain gate LOCKS the zero-green-marker invariant. **WILL-CONFIRM:**
after a full Steam restart, DISMISS the current pack and RE-SUMMON from the soul - if it
is still green, the residue is asset-level and we chase the pfx next round.

## The fix (upstream, BL-103 - the offender preserves the correct end-state)
The offender is `_build_boss_summon` (apply_svc_patches.py): it clones the Lyia pet
(bringing Lyia's `StatusIcon`) and never overrode it, and b40 pointed the Enslaver at
the stalker icon. Both are fixed AT THE HELPER (not patched-over downstream):

1. **Skill icon** (`_SUMMON_SKILL_ICON['summon_toxeus_enslaver']`): `stealth\stalkerup`
   -> `soul\deathwalkersummonup` (+down). Deathwalker = an undead soul-walker glyph,
   distinct from the sibling Devourer's `licheking` and kravmoloch's `bonefiend`, and
   fitting "Enslaver of Souls".
2. **Pet-bar portrait** (NEW `_SUMMON_PET_PORTRAIT` map + `_set_summon_pet_portrait`,
   called in `_build_boss_summon` for player-facing summons only): overwrite the Lyia
   `StatusIcon`/`StatusIconRed` with a portrait matching each boss's icon identity;
   the Enslaver gets `deathwalker_party_up/red` - ONE skeleton story across the summon
   button and the pet bar. Bosses without a matching `*_party_` portrait get the
   neutral `proxy_party` (never the nymph). The **pet-of-pet marauders + wyrmlings are
   NOT touched** (`player_facing=False` at those two `_build_boss_summon` call sites) -
   they never display in the pet bar (Will 2026-07-16).
3. **Hades Marshal**: keeps its `wrathofthestyx` icon; pet-bar portrait Lyia ->
   `proxy_party` (neutral, non-Lyia). No bespoke hades party portrait ships - a custom
   one is a future art call (WILL-CONFIRM).

Every icon/portrait path is arc-verified to resolve in the shipped Resources.

## The chain gate (anti-oscillation deliverable)
`enslaver_pet_fx.verify()` is extended with `_verify_chain()` (`_CHAIN` spec for the
Enslaver + Hades Marshal families). Run post-finalization on the FINAL arz, it walks
the LIVE chain and fails loud on ANY drift: soul item grants the expected summon skill
-> skill icon == expected -> spawnObjects == expected pets -> each pet's pet-bar portrait
== expected AND not Lyia -> zero green markers on the pets -> marauder sub-summon
spawnObjects + zero-green on the sub-pets. (The "resolves in shipped arcs" leg is owned
by contracts_resources, which has the arc index.)

**Negative test (`scratchpad/replay_b71.py`), each MUST fail the gate:**
- unfixed build44 (stalker icon + Lyia portrait) -> FAILS (proves it catches the report)
- replant Lyia portrait on an Enslaver pet -> FAILS
- revert the stalker icon -> FAILS
- re-point the soul's granted skill (simulate the feared build42 regression) -> FAILS
- plant `envenomweapon` on a marauder sub-pet -> FAILS
After the fix, the gate PASSES (verified on the real scratch build).

## Roster sweep (fix the CLASS, not the screenshot)
`scratchpad/roster_sweep.py` decoded every boss-summon soul chain in build41 AND build44:
- **icon changed build41->build44: 0; spawnObjects changed: 0** (no chain regressed - the
  whole class is stable since b40/b55; the oscillation theory is refuted roster-wide).
- **18 families show the Lyia pet-bar portrait** = exactly the 17 `_build_boss_summon`
  bosses + Lyia herself (correct). This round fixes all 17: 7 get an on-identity portrait
  matching their b40 skill icon (enslaver->deathwalker, bloodtoxeus->licheking,
  meritamen->phagia, sarpedon->satyr, longnu->hydra, broodmother->slimebrood,
  kravmoloch->bonefiend); the other 10 (pygmalion, eaterofdays, xeiwang, charon,
  hadesmarshal, mnemophage, mountainblade, neferkha, tantalus, voranthys) get the
  neutral `proxy_party` (WILL-CONFIRM: bespoke portraits are a future art pass).
- **24 families carry systemic green markers** on their spawned pets (the ~77-pet Lyia
  residue b55 flagged as a Will design call - some greens are intended, e.g. the
  Devourer). The Enslaver / marauder / Hades-Marshal are NOT among them (b55 fixed them).
  These are NOT regressions of Will's mechanism and are out of scope this round (flagged
  for the same future systemic pet-identity pass b55 named).

## Verification (all green)
- Full scratch DB build EXIT 0; all in-build gates + 25 registry verifies green
  (enslaver_pet_fx chain gate included). A7 Occult/Hunting golden freeze PASS (66 waived,
  0 other).
- Chain gate PASS on the real build + all 5 negatives proven to fail.
- Record-diff vs build44: **intended-only, 52 records** = 51 pet `StatusIcon`/`StatusIconRed`
  (17 player-facing families x 3 tiers, Lyia -> identity/proxy) + 1 skill
  `summon_toxeus_enslaver` icon (stalker -> deathwalker). **0 marauder/wyrmling records,
  0 collateral.**
- Contracts (souls/summons/resources): GATE PASS, **0 P0 / 0 P1** (4903 P2, pre-existing
  systemic count, no new). validate_tags PASS.
- Idempotency: two independent full builds are BYTE-IDENTICAL (arz md5 `f0a58c1c` twice).

## Files changed
- `tools/apply_svc_patches.py` - enslaver skill icon stalker->deathwalker; new
  `_SUMMON_PET_PORTRAIT` map + `_DEFAULT_SUMMON_PORTRAIT` + `_set_summon_pet_portrait`;
  `_build_boss_summon` gains `player_facing` (portrait applied only when True); the two
  pet-of-pet call sites pass `player_facing=False`.
- `tools/patches/enslaver_pet_fx.py` - `_CHAIN` spec + `_verify_chain()` + helpers,
  wired into `verify()` (the anti-oscillation chain gate).
- `docs/BACKLOG.md` - B71 entry.
- `docs/reports/b71_enslaver_chain_rca.md` - this report.

## What Will will see (after a full Steam restart)
- The **Summon Toxeus the Enslaver** ability button shows the deathwalker (skeleton)
  glyph, NOT the shadow-stalker icon.
- The summoned Enslaver's **top-left pet-bar portrait** shows the deathwalker (skeleton)
  face, NOT Lyia's - matching the summon button (one skeleton identity).
- Every OTHER boss summon's pet bar also stops showing Lyia (7 on-identity, 10 neutral).
- The **green**: the Enslaver/marauder pet DATA is provably green-free. Please DISMISS
  the current pack and RE-SUMMON from the soul after the restart. If it is still green,
  that confirms an asset-level (pfx/save) residue we chase next round.
