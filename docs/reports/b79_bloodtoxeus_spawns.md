# b79 - Blood Toxeus spawn paths: chest 100% + parchment entourage + renames (round 1)

> Branch `fix/bloodtoxeus-spawns` off `feat/toxeus-champions` (b73 champions kit tip 8769a5a).
> Owner lane: Blood-Toxeus SPAWN PATHS (proxies, pools, placements of q_bloodtoxeus_*) + the
> entourage wiring. Reference build45 arz = 917d9047 (what Will is playing on DEV).

## Will's report (2026-07-16, build45 DEV, verbatim)
"what happened to blood toxeus? he was supposed to spawn next to Esti's Hidden Chest in the blood
cave 100% of the time. Also, he didn't spawn with his guys next to the tattered parchment."
Follow-up (renames): the chest-open quest read "Toxeus The Murderer's Stash" -> should be "Toxeus the
Murderer, Devourer of Blood's Stash"; and the chest is "Esti's Hidden Chest" -> should be "Toxeus the
Murderer, Devourer of Blood's Hidden Chest".

## Rulings ledger (docs/WILL_RULINGS.md) - this lane closes R-1..R-4
- R-1 (STANDING): any Blood-Toxeus 33% encounter spawns WITH the pack -> section 3.
- R-2: one 33% roll in the parchment room, no double-spawn -> section 3 (relocated, not added).
- R-3 (PENDING): 100% chest spawn, broken by "q_bloodtoxeus_lone_50 orphan retirement and/or
  placement loss; the chest encounter is deliberately adjacent-to-chest (exempt from generic
  clearance)" -> section 1/2. RECONCILIATION: the ruling's cause hypothesis is imprecise. Ground
  truth: the chest was re-architected at M15 to the egg-pool-champion mechanism (per Will's M15
  "add toxeus to the EXISTING spawn group within the esti chest area at 100%"), and the real break
  is `championMin=0` on that pool, NOT the q_bloodtoxeus_lone_50 (parchment @50) retirement - the
  chest uses `egg_blooddragon`, never q_bloodtoxeus_lone_50. The fix keeps Will's M15 "existing
  group" architecture and sets the champion floor; the encounter stays adjacent-to-chest + clearance-
  exempt exactly as R-3 states.
- R-4: the two renames -> section 4.

---

## 1. CHEST RCA (what broke the 100% spawn) - three sentences

The deep "Esti's Hidden Chest" (drxBC2, `proxy_hidden_bloodcave_chest` @ local (9.13,28,137.14)) is
guarded by the NATIVE `egg_blooddragon_pack` proxy placed 4.2u away @ (13.17,28,136.06), whose pool
`pools\egg_blooddragon.dbr` the M15 wave (2026-07-09) edited to add `um_bloodtoxeus_99` as
`nameChampion1` with `championChance=100 championMax=1` - but it LEFT `championMin` at its inherited 0.
Because Toxeus is the CHAMPION here (not a main), a zero champion-FLOOR does not guarantee him: ground
truth from the base game's own "boss + guaranteed champion escort" pools proves the floor must be set -
`xsq22_wave2` ships championMin=championMax=1 and `xsq17_keres_escortparty` ships championMin=championMax=2,
while `arachnos_01_overseer04` (base game, verified championChance=100, championMin=0, championMax=1 - the
EXACT same shape as the egg pool except the floor) still only SOMETIMES spawns its champion, because a
100% champion-CHANCE with a 0 champion-FLOOR is base-game "occasional zone-trash champion", not a
guaranteed escort. (33 base-game pools run championChance=100 with championMin=0 this way -
cryptworm_03_general02/general03/ranged02, keres_03_melee02, ...; 148 guaranteed-escort pools set
championMin==championMax.) So the egg pool with championMin=0 frequently rolled 4 blood dragons and NO Devourer - he was
never the 100% guardian; this was born broken at M15 (nothing "retired" it later - the map placement,
the pool, and `nameChampion1=um_bloodtoxeus_99` are all intact in build45; `q_bloodtoxeus_lone_50`'s
retirement never touched this egg chain).

## 2. CHEST FIX (100% guaranteed)
`tools/apply_svc_patches.py` `_apply_m15_toxeus_group_joins`: set `championMin=1` on the egg pool ->
`championMin == championMax == 1, championChance=100` = the exact xsq22 guaranteed-escort shape ->
**exactly 1 Devourer + 3 blood dragons, every run, every party size** (the proxyPoolEquation was already
neutralized so championMax=1 holds at 1..6 players). The chest guard is a deliberate adjacent-to-chest
one-shot guardian (4.2u from the chest) and is therefore EXEMPT from generic spacing/clearance laws by
design - it is not a respawn fountain (documented in-code). The champion-cap gate is unaffected
(Toxeus-as-champion worst case = championMax = 1, still <= 1).

## 3. PARCHMENT / ENTOURAGE RCA + FIX
**Geography (ground-truthed in the deployed map, 688,692,180 B):** the tattered parchment is
`finalletter` @ (32.46,10.005,17.59) in `drxFirstxistion_connection.lvl`, sitting amid the native
`demon_01_cluster` swarm @ (37.16,10.005,20.46) - "the little demon guys right on top of the tattered
parchment" from Will's M15 request. The single 33% Blood-Toxeus roll (`q_bloodtoxeus_ambush`,
chanceToRun=33, reusing `_BT_POOL` = 1 Toxeus + 2 blood-demon adds) was placed one level over in
`drxFirstRoom.lvl` @ (100,1,50) - a DIFFERENT room. So Toxeus never appeared at the parchment. The
entourage was actually fine (when the drxFirstRoom ambush fired, `_BT_POOL` did include his 2 blood
demons); the LOCATION was wrong.

**Fix (map lane, `build_section_surgery.py`):** RELOCATE the single ambush from `drxFirstRoom` to
`drxFirstxistion_connection` @ (36.0,10.005,19.5) - in the walkable pocket 1.5u from the native demon
spawn and ~4u from the parchment, at the shared flat floor Y=10.005. Now the 33% roll fires WITH his 2
blood-demon guys, amid the parchment's native demon swarm, right on the tattered parchment. This keeps
**EXACTLY ONE 33% roll** (relocated, not added; the drxFirstRoom placement is removed), no DB pool
change (champion-cap gate untouched), and is MP-safe (`_BT_POOL` carries no proxyPoolEquation).

### Entourage roster (his guys)
`_BT_POOL` (`pools\q_bloodtoxeus_lone.dbr`): spawnMin=spawnMax=3, championChance=100, championMin=championMax=2,
name1/2/3 = um_bloodtoxeus_99, nameChampion1/2/3 = b_med_blooddemon_30/31/32 -> exactly 1 Devourer + 2
med blood-demon champions per spawn, plus the native `demon_01_cluster` (3-8 small blood demons) already
on the parchment. The retired `demon_01_cluster_toxeus50` derived pool (git 5c8bda1) stays retired - the
proxy chanceToRun mechanism gives a cleaner single 33% roll than a champion% and does not need a map
instance-repoint.

## 4. RENAMES (`tools/build_text_arc.py`)
- `tagSQECTitle` (chest quest journal/reward title): "Toxeus the Murderer's Stash" ->
  **"Toxeus the Murderer, Devourer of Blood's Stash"**.
- `tagTitleTagTESTER` (reward-popup mirror): same, kept in sync.
- `tagHiddenChestNAME` (the CHEST's in-world container name; NEW override): "Esti's Hidden Chest" ->
  **"Toxeus the Murderer, Devourer of Blood's Hidden Chest"**. DB-verified this tag is used by ONLY the
  3 chest tiers (`hidden_bloodcave_chest_01/02/03`), so the rename is scoped to this one chest. Possessive
  matches the monster name tag `tagMonsterHemorrheus` = "{^r}Toxeus the Murderer, Devourer of Blood".
- `tagSQECFullText` (the chest REWARD-QUEST full-text popup body; round-2 override): SV source
  "You found Esti's hidden chest. ^n^W&BRewarded : ^n&S^rMythic Formula" ->
  **"You found Toxeus the Murderer, Devourer of Blood's Hidden Chest. ^n^W&BRewarded : ^n&S^rMythic Formula"**.
  Round 1 renamed the title (`tagSQECTitle` -> "...'s Stash") and the container name but MISSED this body
  tag, so the reward panel showed title "Toxeus..." over body "You found Esti's hidden chest." The
  `^n^W&BRewarded : ^n&S^rMythic Formula` suffix is preserved byte-exact; the possessive matches the
  container-name capitalization. Single-definition fix-block override (skipped during SV emission via
  `_FIX_BLOCK_TAGS`, so its two identical SV defs cannot trip the duplicate-tag gate).
- **Esti sweep (round 2):** after all four overrides, a full sweep of the BUILT Text.arc modstrings.txt
  (local scratch, A7 golden + de-clobber active) finds ZERO "Esti" occurrences of any kind - the string is
  gone entirely from the shipped text. (The only "Esti" substring anywhere in the SV SOURCE is the unrelated
  base word "Estimated time left:" in install.txt, `tagInstallerText01`, which the build does not emit.)
  Round 1's "no other surface says Esti" claim was WRONG - it had missed `tagSQECFullText`; that is now
  fixed and the claim is verified true against the actual built Text.arc.

## 5. Will test instructions (full blood-cave run)
1. RESTART Steam + TQ (mod files lock in memory); confirm the deploy landed.
2. Enter the blood cave. In the parchment corridor (`drxFirstxistion_connection`), find the tattered
   parchment with the little demon guys: ~1 in 3 room-loads, "Toxeus the Murderer, Devourer of Blood"
   spawns THERE with 2 blood-demon guys amid the swarm. (Re-enter the room a few times to see the 33%.)
3. Go deep to the hidden chest room (drxBC2). The Devourer spawns next to the chest EVERY time (100%),
   with 3 blood dragons. Open the chest: it now reads "Toxeus the Murderer, Devourer of Blood's Hidden
   Chest" and the reward quest reads "Toxeus the Murderer, Devourer of Blood's Stash".

## 6. Verification (round 1)
- **Full scratch DB builds** (both EXIT=0, so all in-build gates + registry verifies incl.
  `_verify_toxeus_champion_cap` PASSED with championMin=1):
  - base branch (feat/toxeus-champions 8769a5a) scratch arz md5 = `5a8947ff72ee0029d7412e690450b262`
  - fix branch scratch arz md5 = `fcc8b46e41ebaac9e093a9d45ef75b10`
- **arz record-diff base -> fix = EXACTLY 1 modified record, 0 added, 0 removed:**
  `records\drxmap\proxy\pools\egg_blooddragon.dbr` -> `championMin: [0] -> [1]`. Nothing else. This
  IS exactly the fix. Final egg-pool shape: spawnMin=spawnMax=4, championChance=100,
  championMin=championMax=1 (the xsq22 guaranteed-escort shape).
- **Contracts (`run_contracts.py --arz fix_scratch.arz`):** the reported 96 P0 / 7244 P1 are the
  PRE-EXISTING whole-DB baseline (identical on base). My change touches only `championMin` (a
  spawn-count field no contract subject validates), and the record-diff proves it is the ONLY field
  changed, so ZERO new P0/P1 are introduced by construction. (contracts_map/quests need --levels-arc
  and are the integration-gate's job.)
- **Map source-of-truth (static INJECT_SPECS):** `q_bloodtoxeus_ambush` now placed ONLY in
  `drxfirstxistion_connection.lvl` @ (36.0,10.005,19.5); `drxfirstroom.lvl` is no longer an
  INJECT_SPECS key (ambush removed); no other level places it -> EXACTLY ONE placement, relocated.
  The injection mechanism (`inject_into_sv_only_blob` -> `inject_into_0x05`, SV-only v0e, flags=0,
  no 0x14, exemplar rot) is already proven for finalletter + q_enslaver_warband in this exact level.
- **Text lane (static):** tagSQECTitle / tagTitleTagTESTER / tagHiddenChestNAME all carry the new
  strings; tagHiddenChestNAME is in `_FIX_BLOCK_TAGS` (SV-emission-skip -> dup-gate safe + folded
  into the mod-tag manifest so validate_tags treats it mod-owned+present).
- **py_compile:** all 4 changed files OK.
- **DEFERRED to integration/deploy gate** (heavy, out of a spawn-paths round-1 lane): the full
  canonical + TESTHUB map build + blob-diff (expect only drxfirstroom + drxfirstxistion_connection
  blobs to differ, navmesh 24/24 byte-identical, QUESTS byte-untouched) and the Text.arc
  validate_tags/golden gate. The map change is deterministic from the INJECT_SPECS proven above.
