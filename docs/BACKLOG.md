# BACKLOG - Open issues (as of 2026-07-08, from Will's live TESTHUB play session)

> This is the authoritative running list of everything still broken or unfinished.
> Ordered roughly by priority. Each item: symptom (what Will saw) → likely cause →
> fix approach → which lane/files. Read docs/HANDOFF_LIVE_STATE.md first for deploy state,
> then docs/PLAYBOOK.md for how to do each kind of change.

> 🚨 **STANDING RULE (Will, 2026-07-09): NEVER REMOVE SKILLS FROM MASTERIES.** Edit fields =
> preferred; add new skills/slots = allowed; REMOVE a skill/tree slot = forbidden without Will's
> explicit per-item approval (removal candidates go on a proposal list back to Will, never into
> a build); re-enabling disabled original content = encouraged; in-record dangling-ref cleanup =
> allowed field-editing, but when in doubt treat it as a removal and ask. Full operational text
> + the Wave 1/2 compliance sweep in the header of docs/MASTERY_AUDIT_2026-07-09.md.

## 🔴 P0 - visible/blocking, confirmed in-game 2026-07-08

### B-OLYMPUS-RHODES-1 (P0 CAMPAIGN BLOCKER): no working portal after Typhon (Olympus -> Rhodes/Hades)
- **Symptom (Will, fresh session):** killed Typhon at the Olympus summit, no working continuation
  portal to Rhodes; the campaign cannot progress past Olympus. Q1 lane added an
  Action_UnlockFixedItem on the "Olympus - Typhon Defeated" token (in "quest that controls bosses
  and their doors.qst" idx 68, loads fine) - STILL no portal on a genuinely fresh kill.
- **RCA (M7 + M12, byte-definitive):** the base post-Typhon portal `xq00_olympus_portaltorhodes`
  (FixedItemTeleport, `locked=1`, "Opened by Zeus after Typhon Killed") is present at OlympusFinal02
  instance [41]. Its destination is ENGINE-INTERNAL (not in the record, the 0x14 [generic 12B], the
  GROUPS, or the SD - verified in ours AND SVAERA). No quest in ANY arc (base + 5 XPack + SVAERA +
  ours) references it. **"Copy SVAERA" has NOTHING to copy:** instance [41] is BYTE-IDENTICAL across
  SVAERA / ours / base (rec_md5 `0975f9aa…`, flags=1, uid `24018446…`, 0x14 `2900…01000000`, pos
  (305.79,90.11,486.84)); SVAERA's DB is an empty 2KB stub so it uses base's `locked=1` record;
  SVAERA's quest 15 / boss-doors controller / init quest are all byte-identical to base; SVAERA's
  QUESTS registry is a subset of ours (DB-lane Q3: no IT main quest missing). So SVAERA is NOT
  born-open and has NO special portal wiring. (scratchpad inst41_diff.py / svaera_cmp.py / svaera_q.py)
- **FIX (chosen): the boat-dialog NPC (Model C).** A summit "portal master / Hermes" NPC ->
  Action_BoatDialog to the Rhodes arrival - a DATA-DRIVEN teleport that does not depend on the
  engine-internal FixedItemTeleport. Map-side spec READY (build_section_surgery.py
  OLYMPUS_RHODES_NPC_SPEC_PENDING): NPC at OlympusFinal02 local (305.80,90.20,490.80) = world
  (1155.80,90.20,-3190.20), 4u from the portal on the Typhon plateau, navmesh-verified on-mesh +
  100% clear + connected. Rhodes arrival = the base's OWN paired target
  `xq00_rhodes_olympusportaltarget` @ Rhodes_CityFinal_01 = WORLD **(700, 41, -6466)** (on-mesh).
  GATED on the DB lane (a8f5446a) authoring `records\quests\portal_master_olympus.dbr` + the
  boat-dialog quest (MAP-REF-1). Then wire the spec, rebuild both maps, gates, coupled map+Quests
  DEV deploy. Mesh `Credits_Portal.msh` + the portal anms DO resolve (base XPack Items.arc) - render
  is not the blocker; the dead engine destination is.

### B-MERGE-SD-GROUPS-1 (P1, map lane): GROUPS half FIXED (build31e M13a); SD half OPEN (M13b, needs sd_format RE)
- **M13a SHIPPED (build31e, 2026-07-10): the GROUPS restoration.** New merge in
  `svaera_plus_portals.py merge_groups_svaera_base`: SVAERA/base records (SVAERA order, verbatim)
  + SV-extra members appended per-record (4: the HV01 fountain, the SV maze respawn, JadeFigurine,
  1 SV Hades member; levelGUID-validated, 0 stale skips) + the 4 SV-only groups (New Group x2,
  DRXShrineTeleport_Duister, zRespawnSanctuary). RESTORED: Tower-of-Judgement floor-4 respawn
  (32703cac.., the Lane B mandatory-path dead shrine), teleportshrineolympus01 (3c007d48.., the
  Olympus rift stop - B-OLYMPUS-TELESHRINE-1 is thereby RESOLVED BETTER THAN FILED: restored, not
  removed), Shrine_Teleport_Orient 12th member, + base-correct member positions/GUIDs in 42 more
  same-name records (golden chests, unified proxies, the Q15/xQ00 portal-pairing [Any Entity]
  records). NEW fail-loud GATE `tools/verify_groups_bindings.py` (forward per-instance check:
  every placed StrategicMovement*Shrine uid must be GROUPS-bound; the gap contracts_map
  MAP-GROUPS-1 could not catch): **374/374 devices bound, 0 dead** on both variants + the 5
  Lane-B must-bind uids asserted in-build (M13A_MUST_BIND). Walk-test: ToJ floor-4 respawn +
  the Olympus rift shrine + HV01 fountain still binding.
- **M13b OPEN: the SD(0x18) half.** Ours is still SV's v6 section (116,299B) vs SVAERA/base v7
  (227,893B). Analysis so far (2026-07-10 session, scratchpad m13_sd_parse/m13_sd_deep): SD =
  [u32=2][version 6|7][u32][count] + named zone/env records; REGION records = type+unk+name +
  GUID(16) + 8 floats + embedded display tag + trailer (SV carries the FULL base tagRegionName01-185
  set + its 9 SV zone tags: tagBCX x4, tagMZoneGoM, tagNewMZone1, tagJoLandia, tagSPDarkForest,
  tagSPRogueEncampment); env/fog records ('Rhodes Fog', 'X2_*') have larger bodies and **v7 records
  carry an extra field at body offset ~112 vs v6** - so porting requires a real sd_format.py
  (round-trip-proven, qst_format-standard) and v6->v7 record conversion, NOT a heuristic splice.
  What the SD swap would gain: TQAE base-act env re-authoring + all DLC-act zone/env records
  (mostly capped acts). What a naive swap would LOSE: the 9 SV zone-label records (blood cave,
  GoM, Secret Place) - hence record-level merge only. No PROVEN defect is SD-attributed today.

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
- **build28 (2026-07-08):** 12 broken pets repointed at their source monsters' loot-table
  loadouts (player uniques never auto-equip -> naked) + NEW validate_summon_pets gate. Verified
  present in the deployed arz (c4aa4d75); validator PASSes with upstream-only WARNs.
- **REPEAT-FILED (Will, live on build28): "summons are broken".** build29 findings, all fixed:
  (1) SOUL-GRANTED summon skills are gated by the SAME StartSkill anim abort as B-SOUL-PROC-2
  (see its RCA v2): a summon skill with a non-playable special anim NEVER SPAWNS its pet
  (strongbark_quillvines anim Roar x8 souls, barmanu_blizzard + gargantuanyeti_iceblast +
  nehebkau-class anim Summon x21 souls) - pcsafe clone + repoint like every other grant;
  (2) 25 soulskills pets (carrioncrow, peng, quillvine_03, skeleton_archer/soldier ladders)
  shipped with EMPTY monsterClassification while every working exemplar (Lyia, Boneash, base
  WraithLord) is Common - set to Common;
  (3) validate_summon_pets extended to cover the FULL chain from GRANTING ITEM to living pet:
  summon-skill castability (anim), itemSkillLevel vs spawnObjects ladder (warn), pet
  monsterClassification, plus the existing mesh/rig/equipment/controller/skill checks.
  Equipment-side (naked/floating) remains as build28 authored it; needs Will's walk verdict on
  freshly summoned pets (saved-item baking does not affect pets, they spawn from the DB).

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
- **REPEAT-FILED (Will, live on build28, 2026-07-08): "the ground attack in the soul is still not
  working" / "souls skills are broken".** The build28 itemSkillLevel fix IS in the deployed arz
  (c4aa4d75: 1371/1371 granted-skill souls carry level >= 1, sow souls at 1/2/3) so the level fix
  was NECESSARY but NOT SUFFICIENT.
- **RCA v2 (B-SOUL-PROC-2, build29, disasm-proven):** Game.dll SkillManager::StartSkill (log
  string "Animation failed to start in SkillManager::StartSkill" va 0x1035c3b0, gate vcall at va
  0x102561d4) ABORTS the whole cast and returns false when the skill's skillSpecialAnimationName
  cannot start on the CASTER's animation table. Our shipped PC tables (SV's own, byte-identical
  port; anm_malepc01/anm_femalepc) define 32 special-anim names of which only TWO (AoE360,
  Colossus) exist in EVERY weapon row of both sexes. cyclops_groundsmash ("Ground Smash") carries
  anim ClubSlam, a Cyclops-rig animation in NO PC row: the proc can never fire for a player at any
  itemSkillLevel. 39 distinct soul-granted skills carry never-playable monster anims (ClubSlam
  x105 souls, Spit x55, Punch x36, BloodBoil x29, Summon x21, GroundPound, Bite, ...); dozens more
  (ThunderClap/Ensnare/CallOfTheHunt/...) play only with SOME weapon types. Working A/B from
  Will's own sessions: summon_boneash (NO special anim) fired; cyclops_groundsmash (ClubSlam)
  never did. Secondary defect, same chain: the basetemplates autocast controllers the souls
  inherit carry NO autoTargetRadius while every WORKING base-game Enemy/AttackEnemy controller
  carries 10-15 (the only base item using base_atenemy_onattack is the known-broken EE
  sihailongwang spear).
- **FIX (build29, SHIPPED in the wave):** apply_svc_patches _fix_granted_skill_castability:
  every soul-granted skill whose special anim is not universally playable is CLONED to
  records\skills\soulskills\pcsafe\ with the skillSpecialAnimationName field REMOVED entirely
  (exact base-parity: sampled base controller-cast grants carry the field ABSENT, never
  empty-string; wraithlordsummons + 172/204 base proc grants are anim-less) and the souls
  repointed; originals untouched so monsters/pets sharing them (melinoe_bloodboil = Blood
  Toxeus kit, spellbreaker, wraithlord deathnova) keep their animations. Enemy-targeted soul
  controllers lacking autoTargetRadius get 15.0 (base concrete-controller parity); Self/Ally
  controllers are deliberately untouched (base Self controllers use a wide 10-15 radius;
  forcing a small value could suppress self-buff auto-casts). Build29 counts: 60 skills cloned,
  442 soul grants repointed, 6 Enemy controllers given a radius. Invariant + the standalone
  validate_soul_augments now FAIL the build on any non-universal granted anim and any Enemy
  controller without a radius (negative-tested against the build28 arz, which they fail).
  NOTE for testing: TQ saves bake item properties at pickup, so souls already in a bag may keep
  dead grants; verify on FRESHLY DROPPED souls (the build29 starter chest's sow souls were the
  test vehicle; that slot is gone since build30 - use any boss/hero soul drop instead).
- **Same-gate siblings found (NOT fixed in build29, report-only):** player mastery skills with
  monster-only anims are equally uncastable and were already dead in SV (Earth drxmeteor anim
  MeteorShower; Medicine tree TelkineSummonSkeleton/TelekinesisStart; Storm spellbreaker anim
  Drain as a TREE skill). Fixing those changes mastery behavior; needs Will's call.

## 🟡 P2 - pending answers / smaller

### B-FX-DANGLING-1: ~353 pre-existing dangling Chris\UnarmedProjectile_FX01 particle refs (build30 delta vet)
- **Symptom:** arz-wide, ~353 records (incl. player Earth skills drxflamesurge/drxvolcanicorb)
  reference the nonexistent `Records\SandBox\Chris\UnarmedProjectile_FX01.dbr` in
  particleEffectNameN slots. Cosmetic only (the engine skips the missing layer; no crash).
  The 3 pcsafe soul-skill copies were fixed in the build30 F-wave (F7a); the rest are upstream
  SV debt. Fix approach: an F7b-style sweep (strip or repoint) if Will wants the fx layers
  back; else leave. Also inert leftovers to strip in the same pass: orphaned
  particleEffectAttachPoint2/3 on the 3 pcsafe skills; supra wep_spear.dbr's bumpTexture
  (harmless on the base RSpear14B mesh).

### B-GATE-HARDEN-1: build gates SKIP (not FAIL) outside the work/ layout (build30 delta vet)
- The A9 render-chain + F2 summons-contract gates skip loudly when the game dir / staged
  Resources are absent (scratch determinism builds). Optional hardening: an env flag
  (SVC_REQUIRE_GATES=1 -> FAIL instead of SKIP) so a mis-pathed work build can never
  silently skip its gates. Also: persist stage-baseline arz copies (e.g. the D10 0e70ffe6
  baseline) under local/db_backups/ so intermediate record-diffs stay reproducible after
  session scratchpads are cleaned.

### B-AREA-NAME-1: Garden of Merchants minimap label reads 'Duister' (NEW 2026-07-08)
- **Symptom (Will, public build):** he teleported from the fountain camp into a garden/courtyard
  full of merchants (= the Garden of Merchants, destination wiring CORRECT), but the minimap/region
  name displayed 'Duister' (the Secret Place forest naming; Dutch for dark). The restored Garden
  level apparently carries a wrong display-name reference inherited during restoration.
- **Fix approach:** root-cause the level display-name mechanism (level blob field vs tag ref vs
  Text string); fix the Garden label and AUDIT ALL restored areas' labels (Uber Dungeon, Boss Arena,
  Sparta Crypt, Duister itself) for the same inherited-name defect. The 2026-07-08 map wave was told
  to investigate; if the fix is Text-side it rides the next arz+Text coupled push.

### B-TOXEUS-2 (P0, build29 RCA + FIX): Blood Toxeus stopped spawning on build28
- **Symptom (Will, TESTHUB, 2026-07-08):** the cave-mouth Blood Toxeus no longer spawns. Proxy
  q_bloodtoxeus_lone byte-verified present in the TESTHUB map; the SAME proxy+pool spawned him
  2026-07-07 on the build27 arz. Delta = the arz only.
- **RCA (byte-proven, build27-vs-build28 boss closure diff):** proxy + pool + monster stats are
  IDENTICAL; the ONLY closure delta is the B-TOXEUS-1 recolor: (1) new clone
  bloodtoxeus_envenomweapon set weaponEnchantment='' - an empty-string .dbr ref with ZERO
  precedent (base game 0 of 56 weaponEnchantment carriers; build27 0 of 56; enchantment-less
  base Skill_BuffSelfToggled records OMIT the field, 31 of 50); (2) new clone
  bloodtoxeus_summonlildude ADDED charFxPakSelfNames to a Skill_SpawnPetMonster - a field NO
  record of any Skill_SpawnPet* class carries in base or build27 (and the donor never had the
  green pak, so the recolor premise was wrong for this skill). Both zero-precedent field shapes
  are loader-abort suspects (unloadable monster = silent no-spawn). **The arz is shared, so the
  canonical secret-area Hemorrheus is equally dead on the PUBLIC build28 item = live P0.**
- **FIX (build29, Lane A):** the envenom clone DELETES the weaponEnchantment field (base-absence
  parity) and keeps the red leinth-aura pak (proven loadable in that exact field shape via
  leinth_aura_buff on a live-spawning boss); the lildude summon reverts to the shared donor
  record (boss skillName9/specialAttack5SkillName = exact build27 bytes; the clone is no longer
  created). Red-shroud intent KEPT (initialSkillName/skillName3 -> the envenom clone). NEW
  fail-loud invariant _verify_boss_kit_clone_shape (apply_svc_patches): a registered boss-kit
  clone must not add fields its donor lacks, must not blank a donor .dbr ref, and its refs must
  resolve. Negative-tested. Gate: boss + closure field-parity with build27 except the intended
  recolor deltas (verified in the build29 record diff). Will's walk test still decides.

### B-SUPRA-NOTIFY-1 (P3): supra formula grant is SILENT (placeholder tags)
- The Esfri chest quest grant (open_bloodcave_portal.qst, Hidden Chest Control) gives the supra
  formula via Action_GiveItem straight into the bag, but its notification uses SV's placeholder tags
  (tagTitleTagTESTER / tagLOCATIONTAGTESTER) so players get NO visible message and easily miss the
  reward. Inherited SV 0.98i debt, not a port regression. Fix: real notification text (Quests+Text
  coupling). See the 2026-07-08 Esfri recon in the resolved item below.
- **BUILD29 DISASM REFUTATION of the "chest tier-1" plan (LANE B COORDINATION, P0):** the closed
  RCA's mechanism claim ("set loot3Chance=100 on loottable_hidden_bloodcave_0{1,2,3} -> the chest
  always drops exactly 1 supra formula") is FALSE. Game.dll FixedItemContainerController disasm
  (0x10182120 / 0x10181530 / 0x10181da0): a chest spawns numSpawn items and picks ONE loot slot
  PER ITEM by roulette over the slots' chance values (chances are RELATIVE WEIGHTS, not
  independent gates). With the Esti tables' chances summing 113.2 and numSpawn ~18-20, a
  loot3Chance=100 slot would put a supra formula on ~47% of every draw = ~8-9 formulas per open,
  and can never guarantee exactly 1. The ONLY exactly-once mechanism is the EXISTING quest
  Action_GiveItem (Condition_UseFixedItem -> token + GiveItem) - i.e. SV's original design.
  **Lane A therefore left the Esti loot tables byte-identical to build28, and Lane B's
  _neutralize_esti_chest_supra (already written into tools/build_quest_files.py expecting the
  chest-side grant) MUST NOT SHIP - with it the player would get ZERO formulas ever. Keep the
  quest grant; the whole item then needs no change at all (notification tags already resolve).**
- **ALREADY RESOLVED Text-side (verified during build29):** build_text_arc
  QUEST_INTEGRATION_TAGS defines tagLOCATIONTAGTESTER = "The Blood Cave" and tagTitleTagTESTER =
  "Esti's Hidden Chest", so the popup renders real strings, not raw tags (the build29 attempt to
  redefine them tripped the duplicate-tag gate, proving the definitions live). Residual polish
  only: the quest still references the TESTER tag KEYS and "Esti's" is a probable "Esfri's" typo;
  wording pass for Will.

### B-TESTHUB-TOXEUS-1 (Will request 2026-07-08): remove cave-mouth Toxeus from TESTHUB
- The Blood Toxeus/Hemorrheus test spawn ~9.9u outside the blood-cave mouth (TESTHUB-only) BLOCKS
  Will from walking into the cave to test the hub portals. Remove it permanently from the TESTHUB
  injection (canonical never had it; the superboss lives in the waterfall chamber). Routed to the
  map wave; ships in a local interim TESTHUB test build for Will now + the vetted wave build.

### B-OLYMPUS-TELESHRINE-1 - RESOLVED BETTER THAN FILED (build31e M13a, 2026-07-10): shrine RESTORED
- The M13a GROUPS restoration re-bound teleportshrineolympus01 (uid 3c007d48...) into
  Shrine_Teleport_Hades as part of base parity - the Olympus rift shrine now WORKS instead of
  dangling (strictly better than the leave-as-is ruling; nothing removed, base-game behavior
  restored). Walk-verify with the M13 wave: activate the shrine at the Olympus summit approach
  and check it joins the rift/teleport network. History: it was dangling since the original
  merge (SV's TQIT-era Shrine_Teleport_Hades clobbered base's; the M6 recon, check_respawn.py).

### B-DB-HYGIENE-1 (P3): dead orphan record potionexp_test.dbr
- records/item/miscellaneous/oneshot/potionexp_test.dbr carries a corrupted NEGATIVE
  bonusExperiencePoints (int32 overflow of ~4e9) and has ZERO inbound references. Harmless dead
  test artifact from upstream; remove or exclude when convenient (the 2026-07-08 DB wave may
  already handle it as its hygiene item).

### B-DUISTER-EXPLORE: Secret Place ("Duister") first-visit findings incomplete
- Will reached Duister but died to Toxeus before touring the other areas. All 5 hub destinations
  (Knossos/Uber, Garden, Sparta, Secret Place, Murder Bunny) still need a full walk-test once the
  portals are pretty + return works. Duister's own portals all reported broken (see B-PORTAL-3).

### BUILD29 CONTRACT-SUITE DB FIXES (2026-07-08, shipped with the B-SOUL-PROC-2 wave)
Violations found by the finished entity contract suite (feat/contract-suite), fixed in
apply_svc_patches _fix_wave29_contract_items:
- SOUL-NAME-RESOLVES (8): satyrmagi_soul + satyrspiritcaller_soul {n,e,l} carried undefined
  placeholder tagSoul1 -> new tags tagSVCSoulSatyrMagi / tagSVCSoulSatyrSpiritcaller with real
  names; test\kyrashadowdancer_soul {e,l} carried bare tagSoulName -> repointed at the live
  tagSoulName323. (SV 0.98i upstream carries the SAME dangling tags - inherited debt, no
  original names existed to prefer. The test\kyra pair is dropped by ZERO monsters =
  unreachable dev items; tags fixed anyway per the brief. The live maenad kyra souls already
  used tagSoulName323 and are untouched.)
- SOUL-AUGMENT-LEVEL (4): crowboar_soul_n/e augmentSkillLevel1/2 == 0 -> n=1, e=2 (l untouched).
- MONSTER-SKILLS-LOOT (5, was reported as 10 refs): blood-cave bodies ancestralwarrior a-e
  skillName1 pointed at nonexistent Melee_Poison09-12_10.dbr -> repointed at the real
  attackmelee_poison09-12_10.dbr (same dir, SV renamed it).
- MONSTER-SPAWN-ELIGIBILITY (1): bw_priest_houndmaster pool spawnMax=2 with
  championMin=championMax=2 left 0 guaranteed main slots (champion crowd-out, Blood-Toxeus
  class) -> spawnMax=3.
- SUMMON-PET-CLASSIFICATION (25, was reported as 17): soulskills pets missing
  monsterClassification -> Common (see B-SUMMON-1 build29 note).
- B-SUPRA-NOTIFY-1 (2 tags): already resolved by build_text_arc QUEST_INTEGRATION_TAGS
  (see its entry); no change needed.
(68x MAP-REF-1 dropped dyer/Great-Wall NPCs = map lane, not this wave.)

## 🔵 STANDING PENDING WORK (from the master queue - not new bugs)

### BUILD31 DB WAVE QUEUE (Will via coordinator, 2026-07-09; batch as one wave)
Train contents (commit-group order per coordinator 2026-07-09): (0) Q1 Typhon->Rhodes portal
unlock (URGENT, Quests.arc lane - SHIPPED as build30.3, live on Steam 2026-07-09; the unlock
event now lives in the shipped Quests.arc 631a2b4d - build ON it, keep it byte-intact in any
Quests rebuild + gate-assert its survival), (1) MASTERY WAVE 1 broken fixes B1-B6 + the new
player-skill-anim gate (**GATED + GREEN 2026-07-09**, arz 06a9a24a, commit afb30a0 - see the
gate log below), (D19) IMMOBILE HUO-REN SUMMON P1 (insert NEXT, before feature groups - on
Steam now; see item below), (2) Mastery Wave 1 Defense/Earth/Storm boosts + D16 Shadow Stalker
+ D17 Core Dweller, (3) D11 + D12 + D15 + **D18a Emberscale icon + D18b Emberscale effect
redesign**, (4) D13 + D14 + **D20 War King Sarpedon summon soul**, (5) Enslaver (approved),
(6) N4-DB Vashkarr, (7) Q2 portal-master NPC (arz + Quests + Text coupled). N2 Typhon-gate mesh
swap = CANCELLED (Will chose the portal-master model C; existing walk-through portals stay
transitionally, retire in phase 2).

> **GROUP 1 GATE LOG (2026-07-09, DB lane):** arz 06a9a24a (54,660,353 B) vs build30.2 baseline
> 3f605741. Record-diff = EXACTLY 28 records, all bucketed to B1-B6 (0 unbucketed): drxmeteor/
> drxthunderball/drxenslavespirit anim -> '' (B1/2/3); drxweaponpool_shieldsmash min 0->[12..61] +
> modifier 0->[20..50] (B4); nightmare_01..20 skillName1 repoint (lowercase resolving MasterMind
> path) + skillLevel1 min(tier,12) ramp (B5); anm_malepc01 + anm_femalepc gained row-matched
> SpecialAnim/Ref pairs for Taunt/Ensnare/Flamesurge/ThunderClap/Barrage/Crosscut/Hew into free
> idx<=14 (B6, pure additions); two Dream passives '0'->'' (hygiene). Gates ALL PASS: new
> player-skill-anim gate PASS on arz + NEGATIVE test FAILS correctly on the b30.2 baseline
> (Meteor/Thunderball/Bonespire + mp_taunt/hailofaxes/shenpao/breathattack/smokecloud);
> validate_soul_augments 0/0; validate_mastery_golden (Occult/Hunting) intact; validate_summon_pets
> PASS; validate_tags PASS; contracts souls+summons 0 P0/0 P1 (112 pre-existing upstream P2, not
> Group-1 records); det-2x rebuild both == committed 06a9a24a. No gate-code fixes needed.

### D19 (P1 BUG, INSERT NEXT - on Steam build30.3): Huo-ren the Mountainblade summon is IMMOBILE
- **Symptom (Will, live):** "I can summon Huo-ren the mountainblade when I pick up his soul but he
  is broken he doesnt move." The D9 summon pet (mountainblade_1/2/3, built by _build_boss_summon
  from um_mountainblade_43) spawns but does not move.
- **Diagnose the pet-mobility axes:** (a) charAnimationTableName - does the pet's anim table carry
  MOVEMENT clips for the flameguard mesh rig (the B-SUMMON-1 'immobile floating scythe' class was
  exactly this); (b) characterRunSpeed/characterWalkSpeed silently ZEROED (dtype law - decode the
  numeric fields); (c) the pet 'controller' field (working pets carry e.g. controller_skelly_aggressive
  - does mountainblade_N have one?); (d) compare against working exemplars (lyialeafsong; also check
  ALL THREE new summon families Narok/Vort/Mountainblade - if _build_boss_summon has a systemic gap
  it hits all; fix at the BUILDER level).
- **Fix + GATE:** extend the summon validators with a PET-MOBILITY check (movement anims present in
  the anim table for the rig + runSpeed>0 + controller present); negative-test on the current broken
  record. Also apply the resulting fix from birth to D13/D14/D20 pets. Files: tools/apply_svc_patches.py
  (_build_boss_summon), tools/validate_summon_pets.py.
Mastery specs = docs/MASTERY_AUDIT_2026-07-09.md (§2 broken fixes, §3 Wave 1; the no-removal
standing rule in its header is BINDING). Broken player skills outrank feature items.
Each group: gates + bucketed record-diff + commit; whole set -> independent delta-vet before
ship (coordinator dispatches); DEV-deploy for Will after major groups is fine (local only).
Will's standing ruling: only convert summon-souls he EXPLICITLY names.

- **Q1 IMPLEMENTED (2026-07-09): Olympus -> Rhodes portal unlock.** M7 RCA: the portal record
  (xq00_olympus_portaltorhodes, FixedItemTeleport locked=1 'Opened by Zeus after Typhon
  Killed') is unlocked by an engine-internal campaign hook that never fires in Custom Quest;
  no quest references it. FIX (tools/build_quest_files.py _add_typhon_rhodes_unlock): ONE
  trigger appended to the vanilla controller 'quest that controls bosses and their doors.qst'
  (already in-arc + registered + never completes + already evaluates this exact token):
  OnLevelLoad + OwnsTriggerToken('Olympus - Typhon Defeated') -> Action_UnlockFixedItem
  (canReFire=1; field shapes mirror the HOST file's own byte-verified idioms - no
  isQuestCritical2, no delayTime). Repeat-on-load = idempotent + retroactive for existing
  token-holders (Will's main). Rebuilt Quests.arc 631a2b4d; entry-diff vs shipped 846c43f3 =
  EXACTLY the host quest; quest-record contract PASS (107 records). SHIPPED as build30.3.
  **Q1 FAILED IN-GAME (Will, fresh session, 2026-07-09): Typhon killed, unlock event present,
  still NO portal.** Confirms M7's FixedItemTeleport-destination-is-engine-internal risk.

- **Q3 (2026-07-09): Olympus->Rhodes = COPY SVAERA, not a quest. QUESTS-LANE VERDICT: NO
  restore needed - the fix is MAP-SIDE.** Coordinator hypothesis (build22 dropped IT-act main
  quest registrations -> Rhodes campaign won't activate) is REFUTED by byte analysis
  (scratchpad q3_registry_diff.py / q3_content_diff.py / q3_portal_refs.py):
  - SVAERA registers 254 QUESTS entries; ours 256. **SVAERA-registered identities absent from
    our registry: 0.** Every SVAERA main quest (scripted scene_rhodes, xq03_theroadtohades,
    xq06_thethroneofhades, quest 10-15, all XPack2/3/4) is registered, cleanly shifted +4 by the
    build22 SV-quest insertion, all inside the 256 window (Rhodes/Hades at idx 108-138, far in).
  - Quest FILE presence: **0 SVAERA .qst files missing** from our Quests.arc (we ship all 100 +
    our 6). Only ONE file byte-differs from SVAERA: 'quest that controls bosses and their
    doors.qst' (+804B = our Q1 trigger APPENDED = byte-superset, all SVAERA behavior preserved).
    The 2 added endpoint-cap controllers (x4_other_001_control_expansionportals,
    xquest_controlsbossdoors) surgically remove ONLY the POST-Hades IT->EE / IT->Ragnarok
    EXPANSION portals - they do NOT touch Rhodes/Hades progression.
  - **NO quest in SVAERA OR the base game references xq00_olympus_portaltorhodes** (corroborates
    M7). SVAERA (a working Custom Quest that runs the full Rhodes/Hades campaign) drives the
    Olympus->Rhodes transition MAP-SIDE, not via a quest -> the fix belongs to the MAP LANE
    (a4207d65): make our OlympusFinal02 portal instance [41] born-open (locked=0) like SVAERA's,
    OR replicate SVAERA's placed transition. There is nothing for the Quests lane to author.
  - **Q1 unlock trigger recommendation:** it is the ONLY non-SVAERA-faithful edit in our
    Quests.arc and it is INERT (failed in-game). Once the map lane makes the portal born-open it
    is fully redundant. RECOMMEND reverting 'quest that controls bosses and their doors.qst' to
    byte-identical SVAERA (drop _add_typhon_rhodes_unlock) for fidelity; harmless if kept.
    DECISION DEFERRED to coordinator + map-lane mechanism report. If kept, it must remain a
    byte-superset (the survival gate-assert still holds).
  - COUPLED SHIP: map(born-open portal) is the load-bearing change; arz/Quests/Text unchanged on
    the DB lane for Q3.
- **Q2 QUEUED: PORTAL-MASTER NPC for SV-area travel (Will chose model C; map lane M8b has the
  mechanism analysis).** DB+Quests+Text triple: (a) friendly quest-NPC record (base boatman
  class pattern, render-safe mesh per D5 law, amgoz1-voice name e.g. 'Almyros the Wayfarer' +
  'Portal Master' title tag); (b) boat-dialog quest offering the 4 SV destinations (Garden of
  Merchants / Secret Place / Uber Dungeon / Sparta Crypt), each -> Action_BoatDialog teleport
  to landing coords from the map lane (coordinate); QUESTS REGISTRY LAW: events append to an
  already-registered loaded quest (sv_commonmechanics = natural host), NO new registrations;
  verify action shapes against base boatman quests (quest 8 to-egypt, quest 7 knossos) via
  qst_format; (c) confirmation-dialog text tags (validate_tags). All three artifacts couple;
  map lane places the NPC after the record lands. Old boat-dialog failure predated B2 (quests
  now load); pilot walk-test proves it.
- **D16 QUEUED (Will, verbatim: the swap skill 'is basically suicide... make him stronger,
  much stronger'): SHADOW STALKER OVERHAUL - EXPLICIT OCCULT-FREEZE EXCEPTION.** (1) find the
  Stalker's position-swap first ability (teleport-exchange into packs) in the Occult pet kit
  and REMOVE it from the PET kit (Will explicitly sanctioned; pet skill slot, not a player
  tree slot - the no-remove mastery law does not bind; substitute a better skill if one fits,
  report the choice); (2) substantially buff the pet ladder (life/damage/resists/speed, all
  tiers; benchmark = mastery-audit Part II, Stalker ~1440 HP reference; aggressive per Will);
  (3) validate_mastery_golden WILL fire: regenerate the golden baseline for EXACTLY the
  changed records/fields, commit documents the Will-ordered exception verbatim; gate keeps
  guarding all other Occult records. Pets spawn fresh per cast = retroactive for existing
  characters.
- **D17 QUEUED (Will: 'make the volcano guy much stronger in earth mastery'): CORE DWELLER.**
  The Earth magma golem (audit: 781/1940/2250 HP, STR 425, taunt+boulder+stonehand+wildfire).
  Buff substantially ON TOP of the Wave 1 Earth boosts: ~1.5-2x life, meaningful damage
  scaling, armor up, keep the taunt identity (Earth's ONLY pet vs Occult's 5-body package).
  Report before/after ladders. (Reading note: 'volcano guy' = the golem; if Will meant
  Volcanic Orb, the Wave 1 cd 4->1.5 boost already covers it - flagged in the report.)

### BUILD32 TRAIN (queued 2026-07-09; implement AFTER build31 ships)
- **N6-DB: Obsidian Halls treasure roulette - WILL SIGNED OFF (2026-07-09).** Full approved
  design + locked decisions: docs/OBSIDIAN_ROULETTE_DESIGN.md (chanceToRun 25.0/corner;
  Voranthys = the one summon-soul via _build_boss_summon on the SepulchralWyrm01 rig; all
  designer defaults incl. locked Boss-classification mega-chest, 5-elite warbands, no charm,
  Sarkoth soul = pcsafe typhon_meteorstorm 2/3/4). Scope per design section 6:
  _create_obsidian_roulette(db) = 4 guardians (derived natives, wild kits + ondeath skills all
  existence-verified), shared warband pool (spawnMin=Max=6, championChance=100, championMax=5),
  4 corner proxies w/ accessory tiers + no-cap limit clone [1..110], 3 svc_obsidianhoard chests
  (hpalace_chestlg01 mesh scale 1.4, goldGeneratorChance=100, guaranteed epic N /
  legendary-or-epic E/L) + 3 accessory pools + loot tables, 4 amgoz1-voice souls (66% Finger2;
  Ilsevar dream augments MUST use the xpack paths - the base-dream twins DANGLE), tags.
  NEW gates: accessory-chain-resolves + chest-lock-classification==Boss + ondeath resolution.
  In-game confirm item for Will's DEV pass: DropProjectileTelekinesis anim on the liche rig.
  MAP-REF-1 ordering: DB records land in the build32 arz BEFORE map lane M10 injects
  (4 INJECT_SPECS + shared v0e branch).
- **MASTERY WAVE 2** per docs/MASTERY_AUDIT_2026-07-09.md §3 Wave 2: Warfare (horn/standard
  uptime, armband path fix, optional warwind), Nature (force-of-nature 360->180, petBonus ML1-40
  ramp w/ overshoot check, defensiveConvert artifact zeroing, wolf FX hygiene), remaining Spirit
  (outsider 360->120 + TTL 60, deathward 300->180, bonepet xxx-spiritbreath re-enable +
  placeholder cleanup - skillName6 no-op = KEEP or EDIT, never remove, per the standing rule),
  remaining Dream (timefield dead-ref clear, phantasm uptime, psionic beam, mana-ladder
  extensions, phantomstrike self-slow = EDIT to zero/flip not remove, phantasm loot dangler),
  RuneMaster tunes (castability breakage may already be covered in build31 group 1 via the
  anim-table restoration - verify before re-implementing), Neidan tunes (mastery-bar stat-stick
  question = Will decision, splash modifier attachment = verify EE semantics first).
  ⚠️ Dream truncation note: §3 Wave 2 Dream items 2-6 numbers are reconstructed - pull the FULL
  Dream boosts block from Part III (the Dream lane's boosts array) for exact targets before
  writing. ⚠️ Golden-freeze expansion decision (doc §5): freeze the tuned trees AFTER each
  wave's QA, regenerating the snapshot in the same step.
- **N4-DB: Forest of the Ancients cave boss - WILL SIGNED OFF w/ amendments (2026-07-09).**
  Full design = the FotA design agent's final report (coordinator-held). Placement: Random05A.lvl
  cave via ToTomb02 east of Chang'an; Majestic Chest at local (24.01,1.00,28.70) stays UNTOUCHED.
  Band/HP APPROVED: charLevel [38,56,71], HP [12000,16500,21000].
  WILL'S DECISIONS: identity = (B) `{^r}Vashkarr, Eldest of the Ancients`, ANCIENT DRAGONIAN
  warlord, mesh `Creatures\Monster\Dragonian\AncientDragonian01.msh`; derive the kit from the
  DRAGONIAN family for anim-safety (NOT the option-A djinn donor). Escort = FULL-STRENGTH
  dragonian lieutenants (pool spawnMax=3, championChance=100, championMax=2 - satisfies
  spawnMax-championMax>=1): Vashkarr + 2 serious dragonians ALWAYS. Minions ("he should also be
  able to spawn many minions very often") = frequent minion-summon on his kit: clone the
  yaoguai_summonshadowstalkers Skill_SpawnPetMonster pattern -> DRAGONIAN fodder, short cooldown,
  multiple per cast; exact numbers in the implementation sign-off. SOUL = NO SUMMON ("it can just
  be really good"): vashkarr_soul_{n,e,l} = dense aggressive STAT suite at the band, richer than
  the Narok/Vort suites, {^F} tag ('Soul of the Eldest' or similar), 66% drop via
  SVC_RELEASE_DROPS, validate_soul_augments green.
  RECON (build30.2 arz, verified on-disk): `AncientDragonian01.msh` SHIPS on 7 records
  (bm_deathlance_32/34/36 + bm_ravager_31/33/35/37, Common L31-37) = the anim-safety derivation
  base; variants AncientDragonianB01.msh (bs_warlock Champions L34/37/40), AncientDragonianC01.msh
  (br_frostscourge). ESCORT CANDIDATES at band: Champions bs_warlock_40 (ancient-B caster,
  visually kin), em_ravager_41 (flameguardmesh), savage_deathlance_39; dragonian Heroes
  um_mukashi_38 / um_bloodskinner_40 / um_wisang_43 / um_mountainblade_43 (CAVEAT: hero escorts
  each 66%-drop their own souls per kill and Mountainblade is already a summon-boss soul - decide
  if that double reward is intended; the visually-kin pick = bs_warlock + a deathlance/ravager-
  derived full-strength champion clone). CEILING NOTE: shipped dragonians top out at L43, so
  escorts + minions need charLevel [38,56,71] laddered clones for epic/legendary (the
  replicant_41 [41,58,71] pattern). MINION FODDER pick: bm_ravager / bm_deathlance derived (SAME
  ancient mesh = literally 'the Ancients'); proposed cadence for sign-off: burst 3 per cast,
  ~6 s cooldown, minion charLevel [38,56,71] (tune off the decoded donor - VERIFIED at
  records\skills\boss skills\yaoguai_summonshadowstalkers.dbr, plus a skills\skills\ alias).
  PROXY: q_vashkarr_lone (chanceToRun=100) staged in BOTH drxmap\proxy\ and drxmap\proxy\pools\
  per the verified q_bloodtoxeus_lone precedent; limit/difficulty donors ON DISK:
  records\proxies boss\herolimit_all.dbr (verified present); NOTE 'HeroDifficulty_01' does NOT
  exist as a record-name substring - on-disk difficulty donors are the difficulty_01..04
  families (records\proxies orient\, xpack\proxieshades\) + xpack bossdifficulty_01; pull the
  EXACT donor path from the design doc (donor-verbatim rule). Boss passives suite per design
  section 4 (boss_conversionimmunity, all_hpscaling, boss_scaling, globalproperties
  epic/legendary boss, monsterClassification=Boss). RENDER LAW on AncientDragonian01.msh + skin
  (EngineArcResolver). Records: um_vashkarr_99 (named path preferred) + proxy + pool + minion
  skill + soul + tags (validate_tags). MAP-SIDE DEPENDENCY: these records MUST land in the
  build31 arz BEFORE the map lane injects the placement (MAP-REF-1); the map lane adds the v0e
  routing case + INJECT_SPECS in its next wave. All gates + bucketed record-diff.
- **D11: Rally** (coordinator holds the brief).
- **D12: Coastal Ichthian Myrmidon soul boost** (coordinator brief 2026-07-09).
- **D15: reward-potion name colors** (Will: Fortitude + skill-point potions should be the same
  dark red as the experience potions). RECON COMPLETE - ready to implement, pure Text-side:
  the dark red is the leading **`^M` color code** in the tag VALUE (shipped Text.arc:
  `tagNewItem6=^MPotion of Experience`, shared by ALL 48 potionexp_NN records). The four
  uncolored tags, each used by EXACTLY ONE record (arz-wide reverse-scan done, zero sharing,
  so no recolor side effects): `tagNewItem3` = 'Lesser Potion of Fortitude' (potionattri_01),
  `tagNewItem70` = 'Potion of Fortitude' (potionattri_02), `tagNewItem4` = 'Lesser Potion of
  Learning' (potionskill_01), `tagNewItem69` = 'Potion of Learning' (potionskill_02).
  FIX: these are SV-upstream tags (SV Text_EN.arc via build_modstrings), so override through
  the sanctioned single-definition dict `TEXT_FIX_TAGS` in tools/build_text_arc.py (skipped
  during SV emission, duplicate-tag gate stays green): add the four keys with the same values
  prefixed `^M`. No arz change; itemText desc tags untouched; check_duplicate_tags +
  validate_tags must PASS; Text.arc ships coupled with the build31 arz push as always.
- **D14: Phygmalian Replicator summon soul** (Will: "Phygmalian replicator soul should summon the
  soul" = the soul summons the Replicator). Records identified on the build30.2 arz (spelled
  PYGMALION in-data): monster `records\creature\monster\automatoi\um_pygmalion_41.dbr` (Hero,
  single tier, charLevel 41, tag tagNewHero262, mesh `Creatures\Monster\Automatoi\Automatoi01.msh`
  = base-game + texture `SVTextures/creatures/automatoi/pygmalion_body.tex` = SV arc; wears
  `defaultHeadPiece = ...\automatoi\pygmalion_headb.dbr` -> pet NEEDS _set_pet_equipment with
  that head piece per the F2 naked-pet law). Souls `...\soul\automatoi\pygmalion_soul_{n,e,l}.dbr`
  (tag tagSoulName583): augment swordtraining 3/4/5 + petBonusName petbonus_pygmalion_{n,e,l},
  NO itemSkillName proc -> the summon displaces nothing; KEEP augment + petBonus (petBonus buffs
  pets = direct synergy with the new summon).
  **SELF-REPLICATION - WILL'S RULING (2026-07-09, verbatim): "dont have the safe limits on the
  pygmalion replicator replicates make it crazy."** Faithful transplant of the monster's replicate
  kit; ADD NOTHING (no new petLimit, TTL, cooldown, or any artificial constraint). Both
  engineering checks RESOLVED from the decoded records (build30.2 arz):
  (1) NO RECURSION IN-DATA: `replicant_41.dbr`'s full kit is decoded (batter, shieldcharge +
  disruption, shieldsmash, lightning melee w/ slow, armor_passive, construct_resists,
  globalproperties) and it does NOT carry replicate (no skillName8, no buffSelfSkillName). The
  monster's faithful shape = ONE-GENERATION replication: copies do not copy. Ship exactly that.
  (2) ENGINE TOLERANCE MOOT: `replicate.dbr`'s OWN native fields already bound the population -
  petLimit = 3/4/5 (per skill level 1/2/3), skillCooldownTime = 9/8/7 s, petBurstSpawn = 1,
  skillManaCost = 75, skillMaxLevel = 3 (ladder 1/2/3 fits the F1 gate), NO
  spawnObjectsTimeToLive (replicants persist until killed). These are limits the MONSTER lives
  with = faithful = KEEP; nothing new is added per the ruling. No unbounded growth exists, no
  crash mechanism; nothing was silently limited.
  EXPECTED IN-GAME (sign-off numbers): the pet auto-casts Replicate every 9/8/7 s (same buffSelf
  wiring as the monster), building to the native cap of 3/4/5 PERMANENT replicants whose
  charLevel scales 41/58/71 with the skill level; each replicant is a full fighting construct.
  Legendary-tier screen state: the Pygmalion pet + 5 permanent L71 copies, all friendly
  (pet-side Skill_SpawnPet chain, Boneash precedent). `spawnObjects = replicant_41` with
  charLevel [41,58,71] = the ladder's power curve comes free from the skill itself.
  (`copy of replicate.dbr` = Skill_AktaiosMirage upstream junk; ignore.) Full D13 recipe +
  gates; the summon-skill ladder tiers map 1:1 onto replicate's existing 3 levels.
- **D13: Eater of Days summon soul** (Will: "The Eater of Days soul should let you summon him").
  Records identified on the build30.2 arz: monster
  `records\creature\monster\sepulchralwyrm\um_eaterofdays_45.dbr` (Hero-classified, single tier
  L45, tag tagNewHero91, mesh `DRX\meshes\eaterofdaysmesh.msh`, texture
  `DRXTextures\creatures\sepulchralwyrm\sepulchralwyrm_eaterofdays.tex` - DRX arcs ship with the
  mod; render-chain gate must still verify mesh-internal shaders). Souls
  `...\soul\sepulchralwyrm\eaterofdays_soul_{n,e,l}.dbr` carry ONLY an augment
  (drxdeathchillaura 3/4/5), NO itemSkillName proc - the summon grant displaces nothing (keep
  the aura augment). Kit donor skill available: `eaterofdays_necrobolt` (attack_projectile).
  Standard D7/D8/D9 conversion: manual-cast Skill_SpawnPet ladder tiers 1/2/3, itemSkillLevel
  1/2/3 (F1 gate enforces <= skillMaxLevel), permanent pet via _build_boss_summon from the
  boss's OWN mesh/anim/skills, NO monster equipment/loot field copies (_set_pet_equipment
  hardcoded if armor is needed), 'Summon <full name>' tag + {^F} law + uber_soul_tags, gates:
  validate_summon_pets + render_chain + soul_augments + summons contract 0 P1 + bucketed
  record-diff.
- **Boss-summon-soul candidates remaining (for Will's batch approval):** regenerated ranked on
  the build30.2 arz via the real wiring join (lootFinger2Item1): 643 souls wired to monsters,
  61 already summon, 578 do not. Top Boss-class by level: dragonliche L63, manticore L56,
  darksatyrshaman L55, hades L54, bloodcrow + talos L50, antaeus L49, typhon + undeadtyphon +
  meglograi L48, palai + deeptresher L47, syrinx + polyphemus + wheedletongue + uber L45,
  ormenos + cerberus + maenadsorceress(no proc) L44, charon both forms L43, yaoguai L41,
  pemphredo + bandari L40, deino + enyo L39, gargantuanyeti L38, barmanu L37, scarabaeus +
  permean L35, sandwraithlord L34, aktaios L33, grimshell L33, nehebkau L30, sandwraith L29,
  megalesios L27, minotaurlord L26, medusa L24, alastor L24, euryale L23, sstheno + arachne L22,
  toxeus (Athens) L21, calybe L20, nessus L15; notable Hero-class: sp_toxeus L99 (the SP
  superboss), wardenofsouls L48, insenzia/torak/koios L47-48 (procless souls - clean adds).
  Regeneration script (re-runnable on any arz): session scratchpad `rank_summon_candidates.py`;
  full dump `summon_candidates_ranked.txt`.

- **FEATURE (Will 2026-07-09): throwing weapons in the campaign.** The mod already requires
  Ragnarok (Runemaster mastery, XPack2 world levels), so throwing weapons are available engine-side;
  they never drop in Acts 1-4 because vanilla loot tables only place them in Act 5. Wire thrown
  weapons into the campaign loot tables (and consider a thrown-weapon soul or two). Will: "we dont
  even have the throwing objects in the game (although I wish we did)".
- **DESCRIPTION CORRECTIONS for next metadata push (2026-07-09):** (1) known-issues still says the
  Uber Dungeon return is not wired - build30's M1 wired the crypt_floor1 native return door, remove
  that line; (2) requirements: state that MULTIPLAYER (joining a session) requires ALL expansions
  (Ragnarok + Atlantis + Eternal Embers) because the merged world declares all-DLC content
  (server-join "get DLC" bounce, confirmed by a real player 2026-07-09); single-player hard
  requirement stays Eternal Embers. Also warn the Steam "get DLC" redirect lands in an empty cart
  (Steam deep-link bug) - buy from the store pages directly.

- Contract suite - **BUILT + committed** (`tools/contracts/`, branch `feat/contract-suite`). One
  unified 51-contract, 5-lane suite (souls/summons/resources/map/quests) that subsumes BOTH the
  planned entity + map contract suites; every contract has a negative test proving it fires. Run:
  `py tools/contracts/run_contracts.py --arz … --levels-arc local/Levels_merged.arc …` (full
  command in PLAYBOOK §12). Run it before every deploy; fail-loud (exit 1 on any non-whitelisted
  P0/P1). **Against the build29-in-flight artifacts it (correctly) FAILS with 108 P1** on real,
  unfixed defects - do NOT weaken the contracts; fix the records:
  - `SUMMON-PET-CLASSIFICATION` x17 (soulskills pets carrioncrow/peng/… have no
    monsterClassification) -> **B-SUMMON-1** (the DB wave owns this).
  - `MAP-REF-1` x68 (SV `all_sv\creature\npc\dyer\*` NPCs + a few `proxies greek\*` pools are placed
    in Greek/Egypt town levels but never compiled into the arz -> silently fail to spawn) ->
    dropped-SV content (#28 / `DROPPED_CONTENT_AUDIT.md`); restore the records OR, if the dyer
    feature is cut-by-design, list them in `whitelist_map.txt` + `CUT_CONTENT.md`.
  - `MONSTER-SKILLS-LOOT` x10 (drxmap blood-cave `bodies\ancestralwarrior*`/`body01` reference a
    missing `Melee_Poison09-12_10.dbr` skill) -> **NEW**; add the skill or clear the ref.
  - `SOUL-NAME-RESOLVES` x8 (satyrmagi/satyrspiritcaller/kyrashadowdancer souls carry placeholder
    name tags `tagSoul1`/`tagSoulName` that resolve nowhere) -> **B-TEXT-TAGS-1 class**, new souls.
  - `SOUL-AUGMENT-LEVEL` x4 (crowboar_soul_n/e `augmentSkillLevel1/2 == 0` = dead +0 augments) ->
    **B-SOUL-PROC-1 residual** (build29 fixed itemSkillLevel but not these augment levels).
  - `MONSTER-SPAWN-ELIGIBILITY` x1 (`bw_priest_houndmaster` pool: championChance=100/championMin=2/
    spawnMax=2 crowds out its named `c_disciple_39`) -> the Blood-Toxeus no-spawn class, **NEW**.
  Build29 progress the suite confirms vs the frozen build27 baseline: 338 -> 108 P1 (SOUL-PROC-
  ACTIVATION 219->0 = B-SOUL-PROC-1; SUMMON-PET-NAKED 6->0; C-RES-TAGDUP-1 5->0 = B-MASTERY-LABEL-1;
  B-TEXT-TAGS-1 Crimson-Verdict tags now resolve). B-TEMPLE-DOOR/B-PORTAL coverage is already in
  (MAP-DOOR-1, MAP-PORTAL-1/2/3).
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

### M14 (build31e, 2026-07-10): dead-content-audit small items - dev quest de-registered + stray tombstone de-placed
- `testquesttoopendoors.qst` DE-REGISTERED from the QUESTS(0x1b) load window (was idx 101 - a
  leftover dev quest duplicating door unlocks on unverified conditions and burning a slot of the
  256 window). Registry is now 255 entries; boundary pair (hcdungeon_control + x2_StartQuest)
  intact; quest identity is name-keyed so the post-101 index shift is neutral; one slot FREED for
  future registrations (e.g. z_primrosecontroller if the Primrose secret is ever un-mooted). The
  .qst stays in the arcs harmlessly (never loads). `DEREGISTERED_NATIVE_BASENAMES` +
  fail-loud asserts in svaera_plus_portals.build_ordered_quest_list.
- The stray Atlantis `tombstone.dbr` (locked FixedItemQuestObject, dev placeholder description
  'Hogge', zero quest refs) DE-PLACED from Greek MonsterCave01B (was inst [58]).
  `REMOVE_STRAY_PROP_SPECS` in build_section_surgery.py; the only level blob the build31e wave
  changed (per-level byte-diff proof; M13a lives in the world GROUPS/QUESTS sections).

### B-STARTER-CHEST-1 + B-STARTER-CHEST-2: starter chest RESOLVED (build30.2, in-game verified 2026-07-09)
- **Symptoms:** (1) Will 2026-07-08: the chest should drop 12 inventory bags + 36 potions for co-op;
  (2) Will, live build30: opening the starter chest drops NOTHING (not even potions).
- **ROOT CAUSE (validated end-to-end via DEV A/B tests):** build28 (5af85d3) replaced the record's
  native RunEquation numSpawnMin/MaxEquation '3+(2*numberOfPlayers)' with the bare integer literal
  '48'. The engine evaluates the bare-literal form to 0 on this container -> numSpawn 0 -> the
  WHOLE chest dead (including the untouched potion slot) through b28/b29/b30. The chest had dropped
  bags since v1.0 (17257c8: loot2+loot3 = startingloot_sack at chance 100, native equation); every
  build27-era deployed arz (e.g. c4aa4d75) drops. The build30.1 "byte exoneration" compared
  build30-vs-build29 = broken-vs-broken, and its bare-literal precedent (boss_tartarus min/max='1',
  a different container) did not transfer. Decisive in-game datapoints: SV-original byte-restore
  (arz 39174e9c) = potions drop; equation-form fix (arz c959a372) = potions + bags drop ("that
  worked perfect" - Will 2026-07-09); the literal builds = nothing.
- **FIX (build30.2, grant_all_inventory_bags in tools/build_svc_database.py):** numSpawnMin==Max =
  '46+(2*numberOfPlayers)' (equation FORM, 48 solo, scales co-op like the original); ONE active
  slot loot1Chance=100 with dual tables Health_01-05All w108 : startingloot_sack w36 (3:1 ->
  E[36 potions + 12 bags]; multi-table slots = ubiquitous base FixedItemLoot precedent, e.g.
  defaultloot\hiddenchest_greece_00-15); loot2..6 restored to the record's NATIVE inert shape
  (chance 0, weights 0, NameN fields DELETED not blanked - an empty-string .dbr ref is the
  B-TOXEUS-2 zero-precedent loader-abort shape); NO soul (build29's sow slot stays removed).
- **LESSON (standing):** RunEquation-typed fields require equation-form values - bare integer
  literals can silently evaluate to 0. Byte precedent does not transfer between containers, and
  a byte-diff against another broken build proves nothing: in-game verification is MANDATORY for
  engine-facing constructs.

### A10 SUMMON-THE-BOSS SOULS: Narok the Rockskin + Vort the Red (build29, owner request)
- Both souls now GRANT A MANUAL-CAST SUMMON OF THEIR OWN BOSS (the Boneash-proven pattern:
  pets cloned from Lyia Leafsong's Pet.tpl baseline, rig/skills replaced with the SOURCE
  monster's own, loot-table equipment via _set_pet_equipment, permanent companion, no autocast
  controller). Narok = um_rockskin_42 (storm/spirit staff caster, Ternion + storm orbs); Vort =
  hero_tarthon_na'arak_40 (the record that DISPLAYS "Vort the Red" via tagMonsterName1139 - the
  SV filename mismatch is upstream). Summon skills records\skills\soulskills\summon_{narok,vort}
  .dbr: 250/300/350 energy, 180s recharge, 3-tier pet ladder, boss-name pet nameplates.
- NEEDS WILL SIGN-OFF (aggressive-but-sane per "way more powerful"): Narok pet life
  9500/14000/20000 (source floor 9.3-13.9k), INT 450 STR 250 DEX 200, dmg 60-90/90-140/130-200,
  scale 1.3; Vort pet life 18000/26000/36000 (source floor 17.8-26.8k), STR 450 DEX 350 INT 400,
  dmg 70-100/105-160/150-230, scale 1.55 (source). Soul lines: rockskin ternion augment 3/4/5 ->
  6 uniform, +250 life, mana penalty -80 -> +150, +25% cast, +25 fire res; vort concussive blast
  2/3/4 -> 5 uniform + NEW thunderball augment 4, +200 life/mana, +30% cast, +25 lightning res.
- Gated by: summon-pet chain validator, castability (no special anim), clone-shape rules,
  record-diff enumeration. Fail-loud: a missing source record now ABORTS the build (was a
  print-and-continue WARNING for all pet summons).

### A6 HUNTING BOLT TRAP = FOUND, ALREADY LIVE (build29 decode, REPORT-ONLY - no change made)
- Will's memory of "a custom-modded bolt trap in Hunting" is CORRECT and matches the SHIPPED
  build28 artifact: Hunting (mastery UI slot 6) slot 19 = records\skills\hunting\drxmonsterlure.dbr,
  display name "Lay Trap" (tagSkillName083), Class Skill_AttackProjectileSpawnPet, spawnObjects =
  the full 20-level bolt-trap pet ladder (records\skills\hunting\drxpet\bolttrap_01..20, mesh
  Effects\Hunting\TrapTikiCrossbow.msh, attack = bolttrap_defaultattackskill
  Skill_AttackProjectileBurst, petLimit 3-5, TTL 30s, monsterClassification Common, NO special
  anim = castable). SV 0.98i upstream had the same design but wired only levels 1-2 in
  spawnObjects; the shipped 20-level ladder is richer (hand-tuning). Modifier slots: 20 =
  drxmonsterlure_petmodifier_detonate, 21 = drxmonsterlure_rapidconstruction. Separately, the
  OCCULT tree (slot 5) carries drxlaytrap ("Breach") + drxlaytrap_petmodifier_multishotbolttrap.
  NOTHING to fix; tree untouched per the hand-tuning law.

### A9 SUMMON-PET RENDER-CHAIN VALIDATOR = LIVE (build29)
- tools/validate_render_chain.py, wired into build_svc_database post-write: every soul-granted
  summon pet's mesh + baseTexture + status icons and the summon skill's bar icons must resolve
  in the shipped arcs (mod Resources + game Resources[/XPack*]; TQ archive-name resolution incl.
  the XPack second-component convention). Mod-authored pet mesh/texture = FAIL (invisible-pet
  class of bug); icons + upstream records = WARN. build29: 203 pets / 2852 art refs checked,
  PASS with ~22 upstream WARNs (known cosmetic debt now visible: thunderballnova + some soul
  party icons, albinospider/formicid upstream meshes). Negative-tested (bogus mesh on a mod pet
  correctly fails the build). NOTE: the gate needs the standard work/ layout (a Resources dir
  beside the arz output + the game dir from the base-arz argument); an isolated rebuild to a
  scratch dir SKIPS it loudly instead of false-failing every mod art ref.

### A7 GOLDEN FREEZE GUARD = LIVE (build29)
- tools/occult_hunting_golden.json (generated from the build28 SHIPPED pair arz c4aa4d75 + Text
  38d6582a) freezes the owner's hand-tuned Occult (slot 5) + Hunting (slot 6) state: 125 records
  (UI slots/panectrl x3 priorities/positions + every tree skill + 1 hop of buff/pet delegation
  payloads) + 110 name/desc tag definition lists (per-file, in order - first-definition wins).
  Fail-loud gates: build_svc_database post-write (DB half) + build_text_arc post-write (full
  pair). ANY drift fails the build unless its printed key is added to owner_approved_overrides
  with Will's sign-off. Negative-tested (record-field, tag-value, and tree-membership mutations
  all caught). Validator: tools/validate_mastery_golden.py (also runs standalone).

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
