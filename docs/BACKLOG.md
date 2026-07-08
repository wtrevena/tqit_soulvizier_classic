# BACKLOG - Open issues (as of 2026-07-08, from Will's live TESTHUB play session)

> This is the authoritative running list of everything still broken or unfinished.
> Ordered roughly by priority. Each item: symptom (what Will saw) → likely cause →
> fix approach → which lane/files. Read docs/HANDOFF_LIVE_STATE.md first for deploy state,
> then docs/PLAYBOOK.md for how to do each kind of change.

## 🔴 P0 - visible/blocking, confirmed in-game 2026-07-08

### B-PORTAL-1: Portals are ugly flat blue panels / hard-to-see arrows
- **Symptom (Will, screenshots):** the born-open GridEntrance portals now APPEAR (build27 fix
  worked) but render as a **flat 2D blue rectangle** with a small light-blue triangle/arrow, not
  an attractive portal. In Duister (Secret Place) they're flat teal panels floating in the room.
- **Cause:** when we swapped GridEntranceDynamic → base GridEntrance for the born-open fix
  (commit portals-born-open / build27), we kept `mesh` but the base GridEntrance class renders its
  portal-plane placeholder (the blue panel) rather than a nice swirling FX. The dynamic class had
  the pretty visual tied to its open-animation; the static class shows the raw portal quad.
- **Fix approach:** give the portal records a proper portal MESH + FX. Options: (a) find a
  base-game always-open portal that looks good and copy its mesh/fx fields; (b) attach a portal
  particle effect (the Tower-of-Judgment `TJ_JudgementRoom_PortalObject` swirl, or a rift FX) as a
  separate decoration/effect entity co-located with each portal; (c) check if base GridEntrance has
  a `portalFxName`/`meshFxName` field that we left empty. MUST keep born-open + teleport working
  (don't revert to Dynamic). Files: tools/apply_svc_patches.py (the `_make_portals_born_open_*`
  block) for record fields, or tools/build_section_surgery.py to co-locate an FX entity.
- **Verify:** in-game only (visual). Static gate: portal record has a non-empty mesh/fx that resolves.

### B-PORTAL-2: Portal placed in the middle of the walkway (blocks passage)
- **Symptom:** the blue portal to the RHS of the respawn fountain sits **right in the path** -
  Will can't walk past it without being teleported. (Screenshot 1: the flat blue panel east of the
  fountain, on the only route.)
- **Cause:** hub/door portal placement coords chosen for on-mesh + distance-from-friendlies, but
  NOT for "off the natural walking path." A portal you can't avoid = forced teleport.
- **Fix approach:** relocate that portal (and audit all hub portals) OFF the main traffic lane -
  tuck them against a wall/edge so the player walks TO them deliberately. In the blood-cave first
  room the 5 hub portals should be a neat row along a wall, not blocking the tunnel. Files:
  `_HUB_CAVE_ENTRANCES` / `_HUB_CAVE_RETURNS` coords in tools/build_section_surgery.py; the door
  portal coords in the A1/A2/Sparta specs. Re-run gate_doors_hub after moving.
- **NOTE:** this is the TESTHUB hub portals AND possibly canonical doors - check both.
- **2026-07-08:** G1 (the fountain-camp Garden door, the offender Will hit) relocated ~12.4u off
  the walking lane by the map wave. NEW SAME-CLASS HAZARD found by audit: the Sparta door entrance
  P1 in catacube02_floorlast sits 6.0u from the stairsdown01 traffic funnel; relocate it too
  (in the wave). Vista S1 and maze03 A1 placements are fine.

### B-PORTAL-3: Return/back teleport doesn't work (one-way trip)
- **Symptom:** Will teleported to "Duister" (Secret Place) via the panel, could walk around, but
  **could not teleport back**. Also: "all the portals in Duister are broken."
- **Cause:** the return portal (GridExitOneWay landing → its own back-entrance) either wasn't
  swapped to born-open (only the OUTBOUND portal_olympianarena1 was swapped; the RETURN
  portal_olympianarena2 is GridExitOneWay - is IT visible/functional?), OR the Secret Place cluster's
  INTERNAL portals (SV's own darkforest transition portals) are DynGridEntrance that never open
  (same class bug, different records, explicitly out-of-scope in the born-open fix - see
  DYNGRID_GATE_RCA.md note 2). "All portals in Duister broken" strongly implies the 11-level Secret
  Place cluster's own inter-level portals need the same born-open treatment.
- **Fix approach:** (1) verify the return portal_olympianarena2 renders + teleports (GridExitOneWay
  semantics - does it need born-open too? it's a different class); (2) enumerate ALL DynGridEntrance
  portals in the Secret Place cluster (and every SV area) and apply the born-open swap to them too
  (generalize `_make_portals_born_open` beyond portal_olympianarena1 to ALL our-relevant
  DynGridEntrance records that should be always-open). Files: apply_svc_patches born-open block.
- **LIVE UPDATE 2026-07-08 (Will, public build):** the GARDEN OF MERCHANTS return portal is ALSO
  broken (outbound from the fountain camp teleported fine; the return in the Garden did nothing).
  With Duister's returns already confirmed broken, one-way returns are SYSTEMIC: verify and fix the
  returns of ALL FOUR portal areas (Garden, Secret Place, Uber Dungeon, Sparta Crypt). Outbound
  born-open entrances are CONFIRMED WORKING live (first public-build walk-in teleport verified).
- **ROOT-CAUSE DISCRIMINATOR (2026-07-08 byte-level diagnosis):** every 0x14 binding is CORRECT
  (60B prefixed entrances, 48B landings, pairing intact, dest GUIDs verified, no mis-wire). The
  live pattern: entrances hosted in ORIGINAL-INDEX levels fire (G1 in HV01, hub portals in swapped
  Random09A); entrances hosted in APPENDED SV-only levels never fire (G3 in the Garden, S3 + hub
  returns in darkforestenter). Invented return-entrances have zero native precedent (native
  bidirectional doors = one 0x14 mouth + one reciprocal 0x06 descriptor in the destination).
- **FIX RECIPES (handed to the 2026-07-08 map wave):** SPARTA = convert to a NATIVE two-way door by
  repurposing SC2's dangling 0x06 tail descriptor in place (exit d76121ad..., mouth efbf54c9...,
  src catacube GUID 817574a8..., door cell (6,0,4)); remove injected P2/P3/P4. UBER (A1) = DEFER
  (crypt_floor1 is a 2-layer grid; door-cell Y = layer index; needs layer RE first). GARDEN =
  no native map return possible (terrain level); SV's DESIGNED return is the rift shrine
  teleportshrine_gom, VERIFIED FULLY WIRED in our build (Will: walk-test rift travel from the
  Garden shrine). DUISTER = its teleportshrineorient01 shrine is INERT (flags=0, no uid, no GROUPS
  member); wiring it like the Garden shrine gives Duister the same SV-native rift return.
  Escalation if appended-host entrances must ever fire: Frida runtime session in the Garden.
- **Walk-test predictions:** maze03-hosted hub return WORKS; SC2/murderbossroom-hosted returns
  broken until the SC2 conversion; pillagedvillage -> forestobsidiantransition = control case.

### B-SUMMON-1: Summoned pets spawn NAKED / broken (no equipment, some immobile)
- **Symptom (Will):** "Summon Boneash" summons Boneash but he has **no weapon, no helmet, no
  chestplate, no greaves - nothing**. Earlier: the Blood-High-Priest soul's "Call the Blood
  Blade-Dancer" summon appeared as a **floating scythe, immobile** (bug F).
- **Cause:** the wave-created pets (and possibly the base Boneash) have incomplete equipment/visual
  wiring. Per CLAUDE.md lessons: pet equipment must be set via `_set_pet_equipment()` with hardcoded
  item paths - copying loot/equip fields from Monster.tpl → Pet.tpl CRASHES, so pets are authored
  bare and equipment is added back explicitly. If `_set_pet_equipment` wasn't called (or the item
  paths are wrong), the pet spawns naked. The floating-scythe = mesh/animation-table mismatch
  (the pet's mesh is a weapon-only rig, or charAnimationTable doesn't match the body mesh).
- **Fix approach:** THIS IS THE ENTITY CONTRACT SUITE'S JOB (spec in HANDOFF §4b, workflow
  wf_87586bbf-b63 was STOPPED on hold - RESUME it). It must: (1) for every summonable pet, verify
  mesh + charAnimationTable exist and are rig-compatible; (2) verify equipment is wired
  (`_set_pet_equipment` called with resolving paths) OR the pet is intentionally unarmed; (3) fail
  the build on any naked/floating/immobile pet. First fix Boneash + Blade-Dancer, then all wave pets.
  Files: tools/apply_svc_patches.py pet-creation blocks; reference the WORKING Lyia Leafsong pet.
- **Cross-check:** Will said "if this soul has this issue we probably have many others" - treat as
  systemic across ALL summon souls we created (bwpriest x3, lillued x3, and any other spawnObjects).

### B-TOXEUS-1: Blood Toxeus shroud is still GREEN, not RED
- **Symptom (Will, screenshot 2):** the new Toxeus the Murderer, Devourer of Blood boss fights, but
  the **aura/shroud around him is GREEN** (the Athens-Toxeus poison shroud), not red.
- **Cause:** the rename+reskin (toxeus-devourer-rename) changed the MESH to the Athens rig +
  the crimson skin TEXTURE, but the SHROUD is a separate attached FX/skill (the Athens Toxeus has a
  green poison-cloud aura skill or a bound FX). We changed body color but not the aura FX color.
- **Fix approach:** find the aura/shroud FX on um_bloodtoxeus_99 (a skill in its skill list, or a
  charFX/bound-effect field) - it's inherited from the Athens Toxeus (green poison theme). Swap it
  to a red/blood-themed FX (there are red/blood FX in the DRX effects - trail_wep_spear uses blood;
  look for a red aura/cloud). Files: apply_svc_patches _create_blood_toxeus, the monster's FX/skill
  fields. Keep his Blood Boil kit; just recolor the ambient shroud.

## 🟠 P1 - confirmed broken, non-blocking

### B-SPRITE-1: Exploding sprites do not respawn (STILL - reconfirmed 2026-07-08)
- **Symptom:** the exploding sprites near the occultist pyre spawn once, then never again - Will
  stood on the volcano/pyre spawner for minutes, nothing new. (Was task #37A; STILL broken.)
- **Cause (hypothesis):** our placed t1_pitspawner cluster is missing the continuous-spawn config
  (spawn interval / max-alive / respawn-on-death fields) OR is a one-shot-per-level-load spawner
  vs the Greece exemplar's continuous one. Will's leave-and-return discriminator test was never
  reported back - needs it: leave the area + return; if 3 fresh sprites reappear = per-level-load
  refill (config gap); if none = spawner died with its brood (wrong record).
- **Fix approach:** diff our pit records vs the LIVE Greece occultist pit (which spawns
  continuously) field-by-field - spawn timing/limit/controller. Match Greece. Files:
  tools/build_section_surgery.py sprite/pit specs (the B2 block).

### B-TEMPLE-DOOR-1: "Temple Entrance - Locked ~ Sealed By Guardian" won't open
- **Symptom:** killing the guardian in front of the sealed temple door in the blood cave does NOT
  unseal it. (Was task #37C.)
- **DIAGNOSIS 2026-07-08 (byte-proven; 'never ported' REFUTED):** the full unlock chain is present
  and intact in build27. Doors = babtpl_waterfallroom_secretdoor.dbr + waterblocker.dbr
  (FixedItemDoor, locked=1, tagBloodCaveTempleEntrance; waterblocker carries the Sealed By Guardian
  hint tag) in drxbc2.lvl. Controller = open_bloodcave_portal.qst step 0 trigger 'Unlock Waterfall
  Door': Condition_KillAllCreaturesFromProxy(q_highpriest_lone, isResettable=1) ->
  Action_UnlockFixedItem on BOTH doors; ported byte-intact; quest registered at idx 97/256 (inside
  the load window since build22). Guardian proxy/pool/monsters all present under identical names
  (no soul-wave rename). Nothing to port, no slot to add, no rename.
- **Residual = RUNTIME** (quest adoption / proxy-death arming across region streaming; same
  reliability class as the widow-letter window bug). Will's original failing test predates the
  build22 window fix, so the door may ALREADY WORK. **DISCRIMINATOR (Will, on the fresh public-build
  character): in the blood cave waterfall room (drxBC2), kill the lone guardian miniboss in front of
  the Temple Entrance and see if it unlocks.** Unlocks = close this item (build22 fixed it). Still
  sealed = the proxy is not spawning its guardian (population wiring, sibling of B-SPRITE-1) or
  KillAllCreaturesFromProxy is not arming for an adopted control quest; investigate THAT, not the port.

### B-SMOKE-1: Region smoke density far below SV (STILL - reconfirmed)
- **Symptom:** some smoke present, but SV had FAR more, starting the moment you enter the section.
- **Cause:** the C4 atmosphere restore covered ENTITY emitters only; the REGION-WIDE ENVIRONMENT
  half (SD/0x18 or level 0x09 env params - volumetric fog) was never restored (vet hedge on record).
- **2026-07-08 REFUTATION:** the region-env transplant hypothesis is DEAD: the 0x09 env/fog record
  is byte-identical SV vs shipped for every affected level (the v1-vs-v2 divergence is a re-save
  framing marker, not content); SD/0x10 carry no fog delta. DO NOT transplant 0x09/0x17 (framing
  mismatch corrupts). Remaining levers: (a) map side = restore the still-dropped SV Delphi entities
  via INJECT_SPECS at SV-exact coords (delphilowlands02: t1_pitspawner_01 x2, t1_pitspawner_02,
  t1_lildude x6, soundobject_cageglow; delphilowlands04: cage_binding_fx01 + cage props + lildudes
  + vitstaffs; delphilowlands03: lildudes + vitstaffs) - in the 2026-07-08 map wave; (b) DB side =
  audit fog_occult_fx01/pit_fx01/pit_fx02/bugcloud_smallfx emission values vs SV-era - in the
  2026-07-08 DB wave (item 9). If both come back SV-faithful, the residual gap is engine-era
  rendering, not data.

### B-TEXT-TAGS-1: 8 Blood Toxeus / Crimson Verdict tags render as raw strings in-game
- **Symptom:** on the PUBLIC item, Hemorrheus's name, the Crimson Verdict set name, its 4 set-piece
  item names, the Vein Render sword, and the Hemorrhage soul (name + description) display as raw tag
  strings (e.g. `tagSVCSetCrimsonVerdict`) instead of proper names. Verified: the deployed `Text.arc`
  is missing all 8 tags that shipped `.arz` records reference. Confirmed by `validate_tags` and
  enumerated in `docs/MULTIPLAYER_COMPAT.md` §M3.1 (+ the `docs/STEAM_RELEASE.md` pre-flight).
- **The 8 tags (each referenced by a deployed record, absent from `Text.arc`):**
  `tagMonsterHemorrheus`, `tagSVCSetCrimsonVerdict`, `tagSVCSoulHemorrhage`, `tagSVCSoulHemorrhageDESC`,
  `tagSVCarmCrimsonVerdict`, `tagSVChlmCrimsonVerdict`, `tagSVCtorCrimsonVerdict`, `tagSVCwpnVeinRender`.
- **Cause:** the known `build_text_arc.py` ↔ `build_svc_database.py` coupling gap - these tags postdate
  the `mod_authored_tags.txt` manifest, so the build's referenced-mod tag *gate* does not know it owns
  them and passes, yet they never got written into `Text.arc`. Not an MP/determinism/crash problem
  (name/description tags only), so friends-only co-op is unaffected - but it is visible to every public
  subscriber.
- **Fix approach:** add the 8 tags (and audit for siblings) so `build_text_arc.py` emits them, rebuild
  `Text.arc`. **COUPLED DEPLOY: arz + Text.arc must ship together** (tags changed). Then re-verify
  `validate_tags` has zero referenced-and-missing tags, redeploy locally + push the Workshop update.
  Files: `tools/build_text_arc.py`, the tag manifests (`work/.../Database/uber_soul_tags.txt` is the
  LIVE one), and whatever authored these records in `tools/apply_svc_patches.py`.

### B-SOUL-PROC-1: Soul-granted 'Activated on attack' skill never procs (NEW 2026-07-08, P1)
- **Symptom (Will, public build, co-op session, fresh level-5 Occultist):** the Crommyonian Sow
  Soul tooltip says "Grants Skill: Ground Smash (Activated on attack), Cooldown: 8 Seconds" but the
  skill NEVER activates when attacking.
- **Why the existing validator missed it:** validate_soul_augments only checks that
  itemSkillName / itemSkillAutoController REFERENCES RESOLVE; a proc needs the whole activation
  chain to be semantically right (controller Class + activation event + proc chance + the granted
  skill being an executable active skill with a valid animation on the wielder).
- **ROOT CAUSE FOUND (2026-07-08 recon, byte-verified): PORT REGRESSION, SYSTEMIC = 219 souls.**
  The souls set itemSkillName + itemSkillAutoController but omit itemSkillLevel, so the granted
  skill instantiates at level 0 = inactive (tooltip renders, controller has nothing castable).
  Base game sets itemSkillLevel on 876/876 granted-skill items; SV 0.98i on 941/941. A/B proof in
  our own arz: sstheno_soul (same controller + same skill class, level 4) works; gorgonguard_soul
  (SAME skill + SAME controller, level absent) is dead. 211 broken souls come from ONE function
  (apply_svc_patches _overhaul_generic_souls: OVERHAULS dict never includes itemSkillLevel) + 8
  hand-authored itemSkillLevel==0 (snaptooth/orythroneus/rocksting e/l + crowboar n/e).
- **Fix (spec'd, folded into the 2026-07-08 DB wave as item 7):** inject per-tier default
  itemSkillLevel (n/e/l = 1/2/3) in the overhaul apply loop when absent; bump the 8 zeros; extend
  the validator with semantic activation-chain checks (skill Class = Skill_*, itemSkillLevel >= 1,
  controller template = SkillAutoCastController.tpl with chanceToRun > 0 and triggerType set).
  Gate: broken chains 219 -> 0, previously-OK 1,152 souls byte-unchanged.

## 🟡 P2 - pending answers / smaller

### B-AREA-NAME-1: Garden of Merchants minimap label reads 'Duister' (NEW 2026-07-08)
- **Symptom (Will, public build):** he teleported from the fountain camp into a garden/courtyard
  full of merchants (= the Garden of Merchants, destination wiring CORRECT), but the minimap/region
  name displayed 'Duister' (the Secret Place forest naming; Dutch for dark). The restored Garden
  level apparently carries a wrong display-name reference inherited during restoration.
- **Fix approach:** root-cause the level display-name mechanism (level blob field vs tag ref vs
  Text string); fix the Garden label and AUDIT ALL restored areas' labels (Uber Dungeon, Boss Arena,
  Sparta Crypt, Duister itself) for the same inherited-name defect. The 2026-07-08 map wave was told
  to investigate; if the fix is Text-side it rides the next arz+Text coupled push.

### B-SUPRA-NOTIFY-1 (P3): supra formula grant is SILENT (placeholder tags)
- The Esfri chest quest grant (open_bloodcave_portal.qst, Hidden Chest Control) gives the supra
  formula via Action_GiveItem straight into the bag, but its notification uses SV's placeholder tags
  (tagTitleTagTESTER / tagLOCATIONTAGTESTER) so players get NO visible message and easily miss the
  reward. Inherited SV 0.98i debt, not a port regression. Fix: real notification text (Quests+Text
  coupling). See the 2026-07-08 Esfri recon in the resolved item below.

### B-STARTER-CHEST-1 (Will request 2026-07-08): more bags + potions for co-op
- The starter chest must drop 12 INVENTORY BAG items + 36 HEALTH POTIONS (so a full co-op party
  each get bags). Guaranteed fixed loot; branch the table if shared so only the starter chest
  changes. Ships canonical (co-op = public byte-identical build). Routed to the DB wave (item 10).

### B-TESTHUB-TOXEUS-1 (Will request 2026-07-08): remove cave-mouth Toxeus from TESTHUB
- The Blood Toxeus/Hemorrheus test spawn ~9.9u outside the blood-cave mouth (TESTHUB-only) BLOCKS
  Will from walking into the cave to test the hub portals. Remove it permanently from the TESTHUB
  injection (canonical never had it; the superboss lives in the waterfall chamber). Routed to the
  map wave; ships in a local interim TESTHUB test build for Will now + the vetted wave build.

### B-DB-HYGIENE-1 (P3): dead orphan record potionexp_test.dbr
- records/item/miscellaneous/oneshot/potionexp_test.dbr carries a corrupted NEGATIVE
  bonusExperiencePoints (int32 overflow of ~4e9) and has ZERO inbound references. Harmless dead
  test artifact from upstream; remove or exclude when convenient (the 2026-07-08 DB wave may
  already handle it as its hygiene item).

### B-DUISTER-EXPLORE: Secret Place ("Duister") first-visit findings incomplete
- Will reached Duister but died to Toxeus before touring the other areas. All 5 hub destinations
  (Knossos/Uber, Garden, Sparta, Secret Place, Murder Bunny) still need a full walk-test once the
  portals are pretty + return works. Duister's own portals all reported broken (see B-PORTAL-3).

## 🔵 STANDING PENDING WORK (from the master queue - not new bugs)

- Entity contract suite (HANDOFF §4b, wf_87586bbf-b63) - RESUME; it owns B-SUMMON-1.
- Map contract suite (task #30, wf_8da16855-efe) - RESUME; add B-TEMPLE-DOOR + B-PORTAL contracts.
- Occult/Hunting mastery UI recheck (#35) - PARTIALLY ROOT-CAUSED 2026-07-08 (B-MASTERY-LABEL-1):
  the mastery SELECT screen shows 'Rogue' because modstrings.txt defines tagSkillName050 /
  tagMasteryBrief05 / tagMasteryTitle05 TWICE (SV's Rogue lines first, the Occult fix block appended
  later; the engine keeps the FIRST definition) and tagMasteryDescription05 still carries vanilla
  Rogue flavor text. Fix = suppress OCCULT_FIX_TAGS keys during per-file emission in
  tools/build_text_arc.py + add tagMasteryDescription05 Occult copy (Will signs off wording) + a
  fail-loud duplicate-tag gate. Owned by the 2026-07-08 DB wave. The in-tree name is correct;
  other masteries are unaffected (single definitions).
- Souls quality pass vs SV originals (#31).
- Toxeus encounter suite: 10-25% canonical entrance spawn, rant scroll (MP per-player), Legendary
  stalker feasibility, 6-player checklist (#32).
- Comprehensive dropped-visuals restoration (#28).
- Cold Tombs (#36) - ON HOLD per Will.

## FIX-ROUND BATCHING NOTE
All the P0/P1 map items (B-PORTAL-1/2/3, B-SPRITE-1, B-SMOKE-1, B-TEMPLE-DOOR-1) share the map
lane → batch into one implement→vet wave, rebuild BOTH artifacts (canonical + TESTHUB), coupled
deploy. The DB items (B-SUMMON-1, B-TOXEUS-1) share apply_svc_patches → one DB wave. B-TEXT-TAGS-1
rides that DB wave (arz + Text.arc ship together). Portals touch BOTH lanes (record fields = DB;
placement = map) - coordinate.

## 🌐 WORKSHOP FEEDBACK (triage inbound player reports here)

The Workshop item (3759792705) is PUBLIC, so players will report problems via **Workshop comments**
and ratings on the item page. There is no automated inbox - Will (or an agent, if he pastes them in)
must read the comments periodically and triage each report INTO THIS BOARD:

1. Reproduce or map the report to an existing item (many will be B-PORTAL-* / B-SUMMON-1 / the raw
   tags B-TEXT-TAGS-1, already known). If it matches, note "also reported on Workshop" on that item.
2. If it is new, file it here with a `B-<AREA>-N` id, the player's description (verbatim), a
   reproduction/cause hypothesis, and the fix lane - same shape as the items above.
3. Distinguish **mod bugs** from **install/environment issues** (missing 4GB LAA patch, loaded a
   normal character into the Custom Quest, base-game version mismatch, subscribed-but-not-downloaded).
   Environment issues → answer in a Workshop reply + capture the FAQ in `docs/SHARE_AND_PLAY.md` /
   `docs/STEAM_RELEASE.md`; do not clutter the bug board with them.
4. When a fix ships, note the build/commit and (optionally) reply on the Workshop comment so the
   reporter knows it is addressed.

Standing watch items likely to draw comments until fixed: the 8 raw tags (B-TEXT-TAGS-1) are visible
to every subscriber right now; portals look rough (B-PORTAL-1). Prioritize those before a wider push.

## ✅ RESOLVED / VERIFIED

### B-CHEST-1: Esfri's chest = WORKING AS DESIGNED, one-time per character (RESOLVED 2026-07-08)
- Exhaustive recon (shipped arz + Quests.arc + SV 0.98i upstream, byte-level): the chest
  (proxy_hidden_bloodcave_chest -> hidden_bloodcave_chest_0{1,2,3}, Champion-locked
  FixedItemContainer) drops random gear/gold from its own table; the SUPRA FORMULA comes from the
  QUEST ACTION on Condition_UseFixedItem: Action_BestowTriggerToken('OpenedHiddenChest') +
  Action_GiveItem(supra_special) = exactly ONE random supra formula (1 of 25) placed SILENTLY into
  the bag (placeholder notification tags, see B-SUPRA-NOTIFY-1). The token is permanent per
  character and a Disable Chest trigger kills the proxy on every later level load: NO re-open, ever,
  for that character (not a session-reset chest, by design). The 'entering the area grants a
  formula' memory is REFUTED for BOTH our build and SV upstream (quest logic byte-identical).
  Will action: check bags/caravan for an unnoticed supra recipe scroll; a NEW character can earn
  one again. Quest confirmed inside the load window (idx 97/256) in the shipped map.

### POTIONS VERIFIED DROPPING (2026-07-08, recon + adversarial verify, both PASS)
- Skill point (2), attribute point (2), and experience (48) potions are all present in the shipped
  arz, fully wired, and actively dropping: they ride the SAME live rare-misc loot slot as relics
  across ~1,956 creatures (all acts x N/E/L), deliberately rare (roughly 0.006% common to ~0.5%
  boss per kill for a specific skill/attr potion); exp potions are ALSO sold by Greece market mages
  and all three types are forge-craftable. Progression gating by act is intentional data. No fix
  needed; do not re-investigate. (Reproduce: audit scripts referenced in the 2026-07-08 session.)

## ✅ RESOLVED: deploy / packaging

### B-WORKSHOP-PKG-1: Workshop item shipped as two broken mods "database" + "resources" (FIXED 2026-07-08, commit 1851203, tag workshop-wrapper-fix)
- **Symptom:** subscribers to item 3759792705 saw TWO broken mods "database" and "resources"
  instead of one "SoulvizierClassic". Root cause: package_workshop.ps1 staged database/ and
  resources/ as direct children of the vdf contentfolder, and SteamCMD uploads the contentfolder's
  CONTENTS, so the item root had no SoulvizierClassic wrapper (TQAE treats each top-level folder of a
  workshop item as a mod name).
- **Fix:** package_workshop.ps1 now stages to dist/workshop/content/SoulvizierClassic/{database,
  resources} and upload_workshop.ps1 points the vdf contentfolder at dist/workshop/content (whose
  only child is SoulvizierClassic). The packager wipes the stale wrapperless staging each run,
  asserts the content root has exactly one child, adds a permanent fail-loud TESTHUB guard (aborts if
  the packaged Levels.arc MD5 equals local/Levels_merged_TESTHUB.arc), and prints the packaged
  Levels.arc size + MD5. Verified: canonical map A1BA5DB2F00FFA067A808753A2E1EAC5 (688,691,849 B)
  matches the published copy; 53-file package; item root = a single SoulvizierClassic folder.
  **Re-uploaded and verified LIVE (2026-07-08): a fresh steamcmd download of item 3759792705 shows the
  item root = a single SoulvizierClassic wrapper, so the "two mods" bug is resolved on the live item.**
  Scripts: scripts/package_workshop.ps1, scripts/upload_workshop.ps1.
