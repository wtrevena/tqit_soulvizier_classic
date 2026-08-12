# HANDOFF LIVE STATE
> ## BUILD84 DEPLOYED TO DEV (2026-08-12) - R-240 loot-volume trim + R-241 uber-orb legendary chance; arz-ONLY; **STEAM UPLOAD PENDING (main session runs it)**
> **DEV `SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = work
> `Database/SoulvizierClassic.arz` = `4bfea2e6fbffa1d80fa55d52807eb5c3`** (55,580,179 B, 51,297 records).
> DEV copied with md5 source==dest verification **while TQ.exe was NOT running** (nothing killed, Steam
> not restarted); **1 of 62 DEV files changed**, 0 added, 0 removed, the folder md5-inventoried before and
> after and the other 61 byte-identical. det-2x **byte-IDENTICAL** across two independent COLD builds
> (both `SVC_NO_CACHE=1`), `4bfea2e6` both times.
> **NOT YET ON STEAM.** The lane is integrated (`main` fast-forwarded `7459e22` -> `1a003a2`), built,
> gated GREEN and deployed to DEV; the Steam upload + GitHub push are the MAIN SESSION's to run.
> Push-gate is pre-proven: dist==work all 5 artifacts PASS, TESTHUB guard PASS (packaged `6784cf0f`, NOT
> the TESTHUB `7a7ca9ac`), single `SoulvizierClassic` wrapper, 56 files / 1188.4 MB.
> - **What it is:** Will's two loot rulings of 2026-08-11. **R-240 (loot-volume trim):** the canonical
>   chests and orbs pay a run's worth of gear, not a vendor's stock; the two-chest Polis cage that was
>   paying ~36 Legendary-grade pieces a run now stays under `{n:4.55, e:3.2, l:4.55}` and still guarantees
>   a target-grade piece at >= 95% of runs (>= 90% under integer truncation). The local-only **TESTHUB**
>   farm keeps its rich volume via a cloned twin set (floors `{n:35, e:23, l:29}`), so one shared arz
>   expresses "canonical trims, TESTHUB stays rich". **R-241 (uber-orb legendary chance):** no orb loot
>   row is a guaranteed-legendary roll any more; the 3 apex tables' 100% row is demoted to the family
>   value 21.2%, dropping worst-orb legendaries-per-open from 8.43 to 0.846 (ceiling 1.00).
> - **arz-ONLY, both couplings SATISFIED not waived.** `Levels.arc 6784cf0f` (canonical) / `Text.arc
>   a9fed7ba` / `Quests.arc 607ec99c` / `Creatures.arc 8c0d8d53` md5-proven byte-unchanged. **0 new tags**
>   authored, so `validate_tags` PASSES against the EXISTING `Text.arc` and no Text rebuild was needed.
> - **Record-diff vs the shipped `44499f56`: ADDED 44 / REMOVED 0 / MODIFIED 69, ZERO unexplained.** The
>   44 ADDED are all TESTHUB-only twin records (20 `svc_polisvault_hub_chest_*`, 6 `svc_polisvault_hub_pool_*`,
>   18 `polisvault_hub_*` loot tables), unreachable on the canonical/Steam map by construction. The 69
>   MODIFIED are canonical loot surfaces (21 polisvault cage, 27 `svc_*hoard_loot_0N`, 3 `bloodcave_0N`
>   donors, 3 `svc_uberorb_apex_*`, 3 `boss_charon_*01b`, 12 `uberorb_default_*`); the ONLY fields that
>   move anywhere are `numSpawnMinEquation` (69), `numSpawnMaxEquation` (69) and `loot4Chance` (3, the
>   apex 100 -> 21.2). Zero members, zero weights, zero pools, zero tags; NO hub twin appears in MODIFIED
>   (clone-then-trim proven).
> - **Contracts: 0 P0 / 0 P1 / 4510 P2** on the built arz, and the baseline `44499f56` under the identical
>   config gives **4492**. The +18 delta is entirely `C-RES-DBR-1`, one per themed twin container, an
>   INERT `lockedSound -> sounds/soundpaks/decorations/lockedobjectpak.dbr` advisory the 21 canonical
>   polisvault chests already carry in the baseline (P2, prov drx). **Zero new P0/P1, zero new violation
>   class.** Every coexisting gate (R-210 DLC cap, R-211 Atlantis voyage cap, unlock-alignment,
>   orb_armor_rows, armor_loot_breadth, loot_distribution, orb/chest breadth, craft/thrown, relic tiers)
>   PASSES in-build under `SVC_REQUIRE_GATES=1`.
> - **Gate records:** `docs/BACKLOG.md` -> BUILD84-DEV GATE RECORD + the lane R-240 / R-241 GATE RECORDs
>   under it. Ruling: `docs/WILL_RULINGS.md` -> R-240 + R-241.
> - **Rollback (one step):** `local/DEV_arz_deployed_prev.arz` = `44499f56` (the build83 arz this
>   replaced); this artifact kept at `local/build84_run1.arz` = `4bfea2e6`.
> - ⚠️ **NOT PROVEN IN-GAME.** Will's DEV check: open the two Polis Vault gaoler cage chests and an uber's
>   Mystical Orb - they should pay a handful of good pieces, not a vendor's stock, and a legendary should
>   be an occasional treat rather than a guarantee. `BL-R241-DEBT-1` is OPEN and honest: the worst orb
>   still pays a legendary 60.9% of opens against a "low chance" bar of 25%; closing that gap is a POOL
>   COMPOSITION call reserved for Will (option B), not a gate action, so the gate ANNOUNCES it and passes.
>   Fully quit TQ and restart Steam first.


> ## BUILD83 SHIPPED TO DEV **AND** STEAM (2026-08-11) - BL-R181-DEBT-7: the fifteen ordinary uber orbs pay armour at parity; arz-ONLY
> **DEV `SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = Steam
> `Database/SoulvizierClassic.arz` = `44499f56ed52bc91219db64eb4de2f11`** (55,562,820 B, 51,253 records).
> DEV copied with md5 source==dest verification **while TQ.exe was NOT running** (nothing killed, Steam
> not restarted); **1 of 62 DEV files changed**, 0 added, 0 removed, the folder md5-inventoried before and
> after and the other 61 byte-identical. det-2x **byte-IDENTICAL** across two independent full builds, the
> second with the prefix cache disabled.
> Steam: **Workshop item 3759792705, `Upload finished ... : OK`, ManifestID `4288024812107747101`**
> (steamcmd workshop log 2026-08-11 08:33:31 -> 08:33:42), `-Update -Visibility 0` with the VDF read back
> to confirm `"visibility" "0"` (stays PUBLIC). 56 files, 1188.3 MB, single wrapper. **STEAM = DEV =
> `main`.** Push-gate: dist==work all 5 artifacts PASS, TESTHUB guard PASS (packaged `6784cf0f`, NOT the
> TESTHUB `7a7ca9ac`), single-wrapper PASS, `run_contracts` on the DIST payload **0 P0 / 0 P1 / 4492 P2**,
> identical to the live baseline. Changenote 2,981 bytes, VDF-safe. Tag `build83-ship` at this doc commit.
> - **What it is:** the last un-owned loot surface in the mod. R-220 (`build79`) wrote fifteen loot
>   tables and widened only their WEAPON row; R-181 (`build80`) decided ownership by asking what FOLDER a
>   table lived in (`\svc\`), and those fifteen live elsewhere. So **nobody owned their armour, no surface
>   audited them, and both fail-loud loot gates were GREEN for three builds while fifteen live surfaces
>   starved**: weapon:armour **3.41:1 to 8.47:1**, thinnest worn slot **0.007 to 0.041** pieces per open.
>   They now run **0.28:1 to 0.49:1** with a thinnest worn slot of **0.29 to 1.16**, which is the ratio
>   the three apex orb tables R-181 already rescued have shipped since `build75`. Total drops per open
>   **RISE on all 15** (7.93 -> 9.24, 9.32 -> 11.77, 13.68 -> 15.83) and are flat on all 42 others.
> - **The class of defect is dead, not just this instance.** Ownership is no longer a folder test: the
>   distribution gate DERIVES the orb tables from R-220's own scope, and `ownership_problems` enforces
>   "every loot table a module WRITES must be inside the gate's surface set" from two witnesses - the
>   shared-builder ledger (OWN1) and the registry touch log (OWN2). **This build is OWN2's first live
>   execution** and it passed with the touch log present; in harnesses with no registry run it ANNOUNCES
>   its own downgrade rather than passing silently.
> - **arz-ONLY, both couplings SATISFIED not waived.** `Levels.arc 6784cf0f` (canonical) / `Text.arc
>   a9fed7ba` / `Quests.arc 607ec99c` / `Creatures.arc 8c0d8d53` md5-proven byte-unchanged. **0 new tags**
>   authored, so `validate_tags` PASSES against the EXISTING `Text.arc` and no Text rebuild was needed.
> - **Record-diff vs the shipped `09a0f51d`: ADDED 0 / REMOVED 0 / MODIFIED 15, ZERO unexplained**, 12
>   fields each. Censused mechanically over all 180 field changes: **165 raised, 15 field-added, 0
>   LOWERED, 0 member-replaced**. The three apex tables are absent from the diff, the predicted no-op.
> - **Contracts: 0 P0 / 0 P1 / 4492 P2, and the baseline arz under the identical config also gives 4492**
>   - zero new violations. Every coexisting gate (b79 orb breadth, b80 loot distribution, b81
>   craft/thrown, chest breadth, relic tiers, unlock alignment, R-210 DLC cap, R-211 voyage cap) PASSES on
>   this artifact, and the two loot gates were re-run against the DEPLOYED DEV bytes as the anti-inert
>   proof. Negatives: **17 RED + 3 positive controls GREEN** (armour) and **11/11** (orb).
> - **Gate records:** `docs/BACKLOG.md` -> BUILD83-DEV GATE RECORD + the lane GATE RECORD under it.
>   Ruling: `docs/WILL_RULINGS.md` -> R-181 SECOND AMENDMENT.
> - **Rollback (one step):** `local/DEV_arz_deployed_prev.arz` = `09a0f51d` (the build82 arz this
>   replaced); the same bytes at `local/build82_run1_09a0f51d.arz`, this artifact at
>   `local/build83_run1_44499f56.arz`.
> - ⚠️ **NOT PROVEN IN-GAME (rides with `BL-R181-DEBT-1`).** **Will's check: kill any Mystical Orb uber
>   and open the orb - helms, torsos, greaves and shields should now fall out of it alongside weapons,
>   across a few kills.** Honest warning in the same note: these fifteen now run armour-HEAVY (2 to 3.5
>   armour per weapon), which is the apex orb's own shipped ratio, but if it reads as an armour vending
>   machine that is a real finding and one constant moves it back. Full note in `docs/WILL_TEST_GUIDE.md`.
>   Fully quit TQ and restart Steam first.


> ## BUILD82 SHIPPED TO DEV **AND** STEAM (2026-08-11) - R-211 Atlantis sea-voyage cap; arz-ONLY
> **DEV `SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = Steam
> `Database/SoulvizierClassic.arz` = `09a0f51dcc5c64b3d84c123a421aeef1`** (55,562,756 B, 51,253 records).
> DEV copied with md5 source==dest verification **while TQ.exe was NOT running** (nothing killed, Steam
> not restarted); **1 of 62 DEV files changed**, the 61 siblings re-hashed after the copy and byte-identical.
> Steam: **Workshop item 3759792705, `Upload finished ... : OK`, ManifestID `7197248715535460168`**
> (steamcmd workshop log 2026-08-11 04:08:40 -> 04:08:59), `-Update -Visibility 0` with the VDF read back
> to confirm `"visibility" "0"` (stays PUBLIC). 56 files, 1188.3 MB, single wrapper.
> - **What it is:** R-211, the travel half of the standing Immortal-Throne cap. R-210 (`build78`) removed
>   the Atlantis PAGE and explicitly left the SHIP as `BL-PORTALCAP-DEBT-1`. **Atlantis is not a post-Hades
>   act: it branches off RHODES, mid-Immortal-Throne**, which is why neither A5 cap ever touched it.
>   `x3mq_Marinos_Rhodes` has ZERO static placements and enters the world only through a `DLCActorSpawner`;
>   talking to him fires `Action_BoatDialog(rhodes_boatmantogadir)`, the only doorway into the XPack3 act.
>   Six base records are now overridden per record path (the A5 pattern): `actorToSpawn` DELETED on both
>   `DLCActorSpawner` records, `startVisible=0` + `IncludeInMap=0` on the two boundary boat captains, and an
>   AND-unsatisfiable `RequireDLC=TQA2` + `RequireNoDLC=TQA2` on both Tartarus act portals. The quest layer
>   was deliberately NOT used: all 20 XPack3 quests are registered under the `XPack3/Quests/...` namespace,
>   so the md5-full-registry-path trap that made the build33 cap ship inert applies verbatim.
> - **arz-ONLY, both couplings SATISFIED not waived.** `Levels.arc 6784cf0f` (canonical) / `Text.arc a9fed7ba` /
>   `Quests.arc 607ec99c` / `Creatures.arc 8c0d8d53` md5-proven byte-unchanged. 0 new tags authored, so
>   `validate_tags` PASSES against the EXISTING `Text.arc` and no Text rebuild was needed.
> - **Record-diff vs the shipped `f1671207`: ADDED 6 / REMOVED 0 / MODIFIED 0, ZERO unexplained** - the six
>   capped records and nothing else. **det-2x byte-identical.** Gate records: `docs/BACKLOG.md` -> R-211 SHIP
>   RECORD + BUILD82-DEV GATE RECORD. Ruling: `docs/WILL_RULINGS.md` -> R-211. RCA + 10-route audit:
>   `docs/ATLANTIS_VOYAGE_CAP.md`.
> - **NEW permanent gate:** `tools/gate_atlantis_voyage_cap.py` (fail-loud, golden allow-list, negative-tested
>   4 ways incl. a COLLATERAL over-reach plant) runs in-memory at cap time, on the WRITTEN `.arz`, on the
>   DEPLOYED DEV artifact and again on the DIST payload at push-gate. Its V5 check proves the DERIVED list of
>   resolvable Atlantis-transit routes is EMPTY; V4 fails if the cap reaches beyond its golden allow-list.
> - **The leak was reproduced as an artifact fact first:** the gate FAILED on the live `build78` arz with
>   `V5 4 resolvable Atlantis-transit route(s) remain`, so the fix is measured in both directions.
> - **Contracts: 0 P0 / 0 P1 / 4492 P2 on the dist payload, and the baseline arz under the identical config
>   also gives 4492** - zero new violations. Every coexisting gate (b79 orb breadth, b80 loot distribution,
>   b81 craft/thrown, chest breadth, relic tiers, unlock alignment, R-210 DLC cap) PASSES on this artifact.
> - **Rollback (one step, either surface):** `local/build81_ship_f1671207.arz` (also
>   `local/DEV_arz_deployed_prev.arz`) = the build81 arz this replaced.
> - **`BL-PORTALCAP-DEBT-1` is CLOSED.** The last Atlantis access path is shut.
> - ⚠️ **STILL OPEN (`BL-VOYAGECAP-DEBT-1`, P1, launch-gated):** NOT PROVEN IN-GAME. **Will's check (needs an
>   Atlantis-DLC owner): after beating Typhon, walk Rhodes - no Marinos, no captain offering Gadir, no
>   Atlantis adventure in the quest log; portal page still 4 tabs.** Full note at the top of
>   `docs/WILL_TEST_GUIDE.md`. Fully quit TQ and restart Steam first.


> ## BUILD81 SHIPPED TO DEV **AND** STEAM (2026-08-11) - R-184/185/186 the craft chain; arz-ONLY
> **DEV `SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = Steam
> `Database/SoulvizierClassic.arz` = `f16712077f315e5d5cf38a32f9c1fec6`** (55,556,551 B, 51,247 records).
> **Workshop item 3759792705 is now build81 CANONICAL** (was build80): `Upload finished ... : OK`,
> ManifestID **`8270033132631496719`** (steamcmd 2026-08-11 03:22:40 -> 03:22:57), `-Update
> -Visibility 0` with the VDF read back to confirm `"visibility" "0"` (stays PUBLIC). 56 files,
> 1188.3 MB, single wrapper. **STEAM = DEV = `main`.** Details in the entry below (the DEV half) and in
> `docs/BACKLOG.md` -> BUILD81-DEV GATE RECORD. Tag `build81-ship` at this doc commit.
> - **Push-gate before upload:** dist==work all 5 artifacts PASS, TESTHUB guard PASS (packaged
>   `6784cf0f`, NOT the TESTHUB `7a7ca9ac`), `run_contracts` on the DIST payload **0 P0 / 0 P1 / 4492
>   P2** - identical to the live baseline, so ZERO new violations. Changenote 3,193 chars, VDF-safe.
> - **TQ.exe never running, never killed; Steam never restarted.** DEV was deployed first
>   (`build81-dev`).
> - **Rollback (Steam):** re-upload the build80 arz, kept at `local/build80_ship_c5851a1a.arz`; the
>   other four artifacts are unchanged. This ship's artifact: `local/build81_run1_f1671207.arz`.

> ## BUILD81-DEV DEPLOYED TO DEV (2026-08-11) - R-184/185/186 the craft chain; arz-ONLY
> **`SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = `f16712077f315e5d5cf38a32f9c1fec6`**
> (55,556,551 B, 51,247 records), copied with md5 source==dest verification **while TQ.exe was NOT
> running** (nothing killed, Steam not restarted). **1 of 62 DEV files changed**, 0 added, 0 removed;
> the 61 siblings were re-hashed after the copy and are byte-identical. det-2x **byte-IDENTICAL**
> across two independent full builds, the second with the prefix cache DISABLED.
> - **What it is:** Will's craft-chain order after reading `docs/CHEST_DROP_MATRIX.md` - *"i meant do
>   the mythic formulas drop. they can drop in normal as well, but the legendary items should not drop
>   in normal. All of the reagents need to be droppable somewhere in the game... Yes we should make the
>   legendary thrown weapons droppable."* Three defects, all measured and all closed:
>   **(1)** the 42 uber "supra" formulas sat only on the Epic/Legendary act tables, so a Normal chest
>   reached **0 of 42**; both supra pools are now members of all four `01_act*_arcaneformulae` at
>   **1.42%-1.60%** - rarer on Normal than the base game already makes them on Epic (2%) and Legendary
>   (5%). Normal coverage **0/42 -> 42/42**, and legendary GEAR on the Normal branch stays **0**.
>   **(2)** 36 of the 78 reagents were unreachable from any Legendary chest, including 3 that **do not
>   exist in this database** (Ragnarok `xpack2` records the four thrown recipes named, so all four were
>   uncompletable for everyone playing the mod). Now **61 of 82 reachable**, every non-MI reagent on
>   **19 of 19** legendary chest surfaces, all **42/42 craftables completable**.
>   **(3)** the thrown class had no unique loot table in this era at all: **0 of 5** legendary thrown
>   were reachable from anything. `svc_unique_thrown_{n,e,l}01` is authored and named as the seventh
>   class of the breadth master.
> - **arz-ONLY, both couplings SATISFIED not waived.** `Text.arc a9fed7ba` / `Levels.arc 6784cf0f` /
>   `Quests.arc 607ec99c` / `Creatures.arc 8c0d8d53` md5-proven byte-unchanged. **0 new tags authored**,
>   so `validate_tags` PASSES against the EXISTING `Text.arc`.
> - **Record-diff vs the shipped `c5851a1a`: ADDED 8 / REMOVED 0 / MODIFIED 16, ZERO unexplained.**
>   Non-reduction proved mechanically over the whole diff: **18 values raised, 0 lowered, 18 members
>   added, 0 removed**. The only replacements are the 12 reagent refs on the four thrown recipes, which
>   is precisely what R-185 rules.
> - **NEW permanent gate:** `tools/gate_craft_thrown_breadth.py` + the in-build
>   `craft_thrown_breadth.verify()` sharing one implementation (F1/G1/G3/G4/C1/C2), negative-tested
>   **12/12**. `svc_armor_breadth.apply_wave` now runs this module first in registry order so the dry
>   run mirrors the real build.
> - **⚠️ THE b80 MERGE WAS THE HARD PART - read the addendum before touching loot weights.** b80 had
>   left a written merge hazard (`BL-R181-DEBT-4`); it is DISCHARGED (thrown is its own gear slot, 12
>   classes not 11; `MAX_WEAPON_CLASS_SHARE` re-derived 0.29 -> 0.28). The non-obvious part: round 1
>   satisfied b80's D3 mass floor by giving thrown full class parity, **all gates went green, and it
>   was still wrong** - it paid 1.30 of each craft-only supra thrown per cage run, 2.9x a plain
>   legendary spear. It was rebuilt. Thrown keeps its vetted quarter-class weight and is exempt from
>   D3's MASS floor on a measured size rule (5 records against 23 for the next-smallest class), held to
>   a REACHABILITY rule instead. Full argument: `docs/WILL_RULINGS.md` -> R-184/185/186 SHIPPED
>   ADDENDUM.
> - **Contracts: 0 P0 / 0 P1 / 4492 P2 == the build79/build80 baseline.** Gate record:
>   `docs/BACKLOG.md` -> BUILD81-DEV GATE RECORD. Registry: 58 modules.
> - **Rollback (one step):** `local/DEV_arz_deployed_prev.arz` = `c5851a1a` (the build80 arz this
>   replaced); the same bytes are kept at `local/build80_ship_c5851a1a.arz`, this artifact at
>   `local/build81_run1_f1671207.arz`.
> - **Will's in-game check:** full note at the top of `docs/WILL_TEST_GUIDE.md`. Fully quit TQ and
>   restart Steam first.

> ## BUILD80 SHIPPED TO DEV **AND** STEAM (2026-08-11) - R-181 armour breadth + loot distribution; arz-ONLY
> **DEV `SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = Steam
> `Database/SoulvizierClassic.arz` = `c5851a1abbebe9eb7744c9311fa14728`** (55,552,948 B, 51,239 records).
> **Workshop item 3759792705 is now build80 CANONICAL** (was build79): `Upload finished ... : OK`, ManifestID
> **`4755232758446325792`** (steamcmd `workshop_log.txt` 2026-08-11 01:02:13 -> 01:02:24), `-Update
> -Visibility 0` with the VDF read back to confirm `"visibility" "0"` (stays PUBLIC). 56 files, 1188.3 MB,
> single wrapper. **STEAM = DEV = `main`.** Details in the entry below (the DEV half) and in
> `docs/BACKLOG.md` -> SHIP RECORD R-181 + BUILD80-DEV GATE RECORD. Tag `build80-ship` at this doc commit.
> - **Push-gate:** dist==work all 5 artifacts PASS, TESTHUB guard PASS (canonical `6784cf0f`, not the DEV
>   `7a7ca9ac`), single-wrapper PASS, `run_contracts` on the DIST payload 0 P0 / 0 P1 / 4492 P2 (identical to
>   the build79 baseline, so ZERO new violations on the uploaded bytes), changenote 2,832 bytes pure ASCII.
> - **TQ.exe never running, never killed; Steam never restarted** - `steam.exe` is still PID 3952 from
>   2026-08-09 13:02:21, the same PID observed at the start of this lane. DEV was deployed first
>   (`build80-dev`), and the three loot gates were re-run against the DEPLOYED DEV arz before packaging.
> - **Rollback (Steam):** re-upload the build79 arz, kept at `local/build79_ship_883a31e2.arz`; the other
>   four artifacts are unchanged. This ship's artifact: `local/build80_ship_c5851a1a.arz`.

> ## BUILD80-DEV DEPLOYED TO DEV (2026-08-11) - R-181 armour breadth + loot distribution; arz-ONLY
> **`SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = `c5851a1abbebe9eb7744c9311fa14728`**
> (55,552,948 B, 51,239 records), copied with md5 source==dest verification **while TQ.exe was NOT running**
> (nothing killed, Steam not restarted). **1 of 62 DEV files changed**, 0 added, 0 removed; the 61 siblings
> were re-hashed after the copy and are byte-identical. det-2x **byte-IDENTICAL** across two independent
> full builds, the second with the prefix cache DISABLED.
> - **What it is:** R-181, Will's TWO reports in one sitting - "also what about the armor? i am not really
>   seeing armor drops like shields, chest plates, helmets, etc." and "you overcorrected, that run 4
>   scorpions tail spears dropped". **Both are RATE reports and R-180 could not see either**: R-180 asked
>   REACHABILITY (can a chest pay a legendary spear at all) and was correctly green, while the cage paid
>   **58.5 legendary weapons to 12.4 armour pieces (4.73:1)** with the helm at 1.6% of the run and SPEAR at
>   24.0% against an even share of 9.1%. Now: **every one of the 11 gear classes sits between 7.8% and
>   10.8%**, weapons:armour **1.22:1**, armour pieces per run **12.4 -> 49.4**, and nothing was reduced
>   (total legendary gear per run RISES 70.8 -> 109.4).
> - **The 4 Scorpion's Tails, arithmetically:** P(some legendary spear lands 4x in one cage run)
>   **27.0% -> 6.3%**; P(four Scorpion's Tails specifically) **2.07% -> 0.45%**. ⚠️ **P(ANY single item
>   lands 4x) only moves 47.3% -> 39.7%**, because volume ROSE. The honest sentence to Will is "much rarer
>   for a spear, still routine for something", not "fixed". `numSpawn` is the volume lever and lowering it
>   is HIS call (`BL-R181-DEBT-5`).
> - **arz-ONLY, both couplings SATISFIED not waived.** `Text.arc a9fed7ba` / `Levels.arc 7a7ca9ac` (TESTHUB,
>   the DEV variant) / `Quests.arc 607ec99c` / `Creatures.arc 8c0d8d53` md5-proven byte-unchanged on the DEV
>   surface. 0 new tags authored, so `validate_tags` PASSES against the EXISTING `Text.arc`.
> - **Record-diff vs the shipped `883a31e2`: ADDED 3 / REMOVED 0 / MODIFIED 57, ZERO unexplained** - the 3
>   armour masters, plus 54 swept surfaces + the 3 aggregate weapon masters. Non-reduction proved
>   mechanically over the whole diff: **603 values raised, 0 lowered, 60 members added, 0 removed.**
> - **NEW permanent gate:** `tools/gate_loot_distribution.py` + the in-build `armor_loot_breadth.verify()`
>   sharing one implementation (D1-D9), negative-tested **7 plants RED / 2 controls GREEN**. It is
>   ORTHOGONAL to R-180's reachability gate by construction: it reds the shipped arz with **328 findings
>   over 42 surfaces** while R-180's gate is green on the same bytes.
> - **Contracts: 0 P0 / 0 P1 / 4492 P2 == the build79 baseline** under the identical config. Gate record:
>   `docs/BACKLOG.md` -> BUILD80-DEV GATE RECORD. Ruling: `docs/WILL_RULINGS.md` -> R-181 + AMENDMENT.
> - **Rollback (one step):** `local/DEV_arz_deployed_prev.arz` = `883a31e2` (the build79 arz this replaced);
>   the same bytes are kept at `local/build79_ship_883a31e2.arz`, this artifact at
>   `local/build80_run1_c5851a1a.arz`.
> - **Will's in-game check:** Prison of Souls / Hades Palace floor 4, kill Alkyoneus the Soul-Gaoler, open
>   all 6 cage chests across 2-3 runs; expect helms/chest plates/bracers/greaves/shields alongside weapons,
>   no class dominating, no 4x-same-spear runs. Also check a red-uber Mystical Orb chest: those were the
>   worst surfaces in the mod (0.07 helms per open) and now pay ~1.2 of every worn slot. Full note at the
>   top of `docs/WILL_TEST_GUIDE.md`. Fully quit TQ and restart Steam first.

> ## BUILD79 SHIPPED TO DEV **AND** STEAM (2026-08-11) - R-220 uber orb loot breadth; arz-ONLY
> **DEV `SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = Steam
> `Database/SoulvizierClassic.arz` = `883a31e2b87f03a54a51c550147c8242`** (55,551,723 B, 51,236 records).
> **Workshop item 3759792705 is now build79 CANONICAL** (was build78): `Upload finished : OK`, ManifestID
> **`867654719607079771`** (steamcmd 2026-08-11 00:02:45 -> 00:03:08), `-Update -Visibility 0` with the VDF
> read back to confirm `"visibility" "0"` (stays PUBLIC). 56 files, 1188.3 MB, single wrapper.
> **STEAM = DEV = `main`.** Details in the entry below (the DEV half) and in `docs/BACKLOG.md` -> SHIP RECORD
> R-220 + BUILD79-DEV GATE RECORD. Tag `build79-ship` at this doc commit.
> - **Rollback (Steam):** re-upload the build78 arz, kept at `local/build78_ship_f6638462.arz`; the other
>   four artifacts are unchanged. This ship's artifact: `local/build79_ship_883a31e2.arz`.

> ## BUILD79-DEV DEPLOYED TO DEV (2026-08-10) - R-220 uber orb loot breadth; arz-ONLY
> **`SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = `883a31e2b87f03a54a51c550147c8242`**
> (55,551,723 B, 51,236 records), copied with md5 source==dest verification **while TQ.exe was NOT running**
> (nothing killed, Steam not restarted). **1 of 62 DEV files changed**, 0 removed; the 61 siblings were
> re-hashed after the copy and are byte-identical. det-2x **byte-IDENTICAL** across two independent full builds.
> - **What it is:** R-220, Will's order "for the mystical orbs that the uber monsters drop, the items should
>   drop with increased breadth as well so all classes of items could be dropped". R-180 fixed the CHESTS;
>   the ORBS carried the identical collapsed weapon row in a second donor family (`1h_all_*01` = axe/club/
>   sword, with bow and staff named directly and SPEAR forgotten), so **0 spears of any quality were
>   reachable from 15 of the 18 uber orb tables, at every tier and every difficulty**. Scope is DERIVED from
>   the consumer (51 uber carriers -> 7 proxies, 6 in reach -> 18 tables), never typed. 15 tables now name
>   the tier-correct `svc_unique_weapons_{n,e,l}01` master at weight 800, with the weapon row at 40% and the
>   shield row at 30% (orb05's shipped values since build75). Spear **0 -> 18 / 9 / 22**.
> - **arz-ONLY, both couplings SATISFIED not waived.** `Text.arc a9fed7ba` / `Levels.arc 7a7ca9ac` (TESTHUB,
>   the DEV variant) / `Quests.arc 607ec99c` / `Creatures.arc 8c0d8d53` md5-proven byte-unchanged on the DEV
>   surface. 0 new tags authored, so `validate_tags` PASSES against the EXISTING `Text.arc`.
> - **Record-diff vs the shipped `f6638462`: ADDED 0 / REMOVED 0 / MODIFIED 15, ZERO unexplained** - every one
>   a loot table with exactly 4 changed fields, and the tier law is readable off the diff (every `[n]` table
>   took `n01`, every `[e]` took `e01`, every `[l]` took `l01`). The 3 apex tables do not appear at all.
> - **NEW permanent gate:** `tools/gate_orb_loot_breadth.py` + the in-build `orb_loot_breadth.verify()`
>   sharing one implementation (O1-O6), negative-tested **11/11**. A second `apply()` on the finished arz is
>   a measured no-op (0 tables widened, 0 chance raises), so the payout can never be double-raised.
> - **Contracts: 0 P0 / 0 P1 / 4492 P2, and the build78 baseline under the identical config also gives 4492** -
>   zero new violations, measured both directions. Gate record: `docs/BACKLOG.md` -> BUILD79-DEV GATE RECORD.
>   Ruling: `docs/WILL_RULINGS.md` -> R-220.
> - **Rollback (one step):** `local/DEV_arz_deployed_prev.arz` = `f6638462` (the build78 arz this replaced);
>   the same bytes are kept at `local/build78_ship_f6638462.arz`, this artifact at `local/build79_run1_883a31e2.arz`.
> - **Will's in-game check:** kill any orb-dropping uber and open the Mystical Orb - spears should now be
>   possible, with visible class variety across kills. Same trip as R-180: the Prison of Souls / Hades Palace
>   floor 4 **Unbound Gaoler** drops a tier-4 orb; the **Boar Snatcher** (Pine Forest / SpartaOptCave03) is the
>   low-level tier-1 control. Full note at the top of `docs/WILL_TEST_GUIDE.md`. Fully quit TQ and restart
>   Steam first.
> - ⚠️ **The higher DROP RATE is a separable, un-asked-for half and is vetoable in one line**
>   (`svc_orb_breadth.RAISE_ROW_CHANCES = False`); the breadth half is untouched either way. See the BACKLOG
>   record's closing section.

> ## BUILD78 SHIPPED TO DEV **AND** STEAM (2026-08-10) - R-210 portal-page DLC cap; arz-ONLY
> **DEV `SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = Steam
> `Database/SoulvizierClassic.arz` = `f663846233295da3e8824bfa4d8925c8`** (55,551,546 B, 51,236 records).
> DEV copied with md5 source==dest verification **while TQ.exe was NOT running** (nothing killed, Steam
> not restarted); **1 of 62 DEV files changed**, the 61 siblings re-hashed after the copy and byte-identical.
> Steam: **Workshop item 3759792705, `Upload finished : OK`, ManifestID `3967507886597870867`**
> (steamcmd 2026-08-10 21:59:12 -> 21:59:32), `-Update -Visibility 0` with the VDF read back to confirm
> `"visibility" "0"` (stays PUBLIC). 56 files, 1188.3 MB, single wrapper.
> - **What it is:** R-210, Will's bug "in the portal page i see atlantis which should be disabled in this
>   mod". The portal window's page list is ONE record, `records\ingameui\teleportmap\teleportmap.dbr`;
>   SV ships a four-page IT-era copy but `strip_ui_overrides()` deletes every `records\ingameui\` record
>   that is not a mastery tree, so the mod shipped NO override and the BASE game's seven-page record won.
>   The base record is now imported byte-faithfully with exactly the 9 DLC page fields deleted, plus the
>   same treatment for the quest log's 6 DLC act-tab fields on `player quests\questwindow.dbr`. The cap
>   runs AFTER the strip and asserts that ordering (the one way it could ship inert).
> - **arz-ONLY, both couplings SATISFIED not waived.** `Levels.arc 6784cf0f` (canonical) / `Text.arc a9fed7ba` /
>   `Quests.arc 607ec99c` / `Creatures.arc 8c0d8d53` md5-proven byte-unchanged. 0 new tags authored, so
>   `validate_tags` PASSES against the EXISTING `Text.arc` and no Text rebuild was needed.
> - **Record-diff vs the shipped `435cc485`: ADDED 2 / REMOVED 0 / MODIFIED 0, ZERO unexplained** - the two
>   capped records and nothing else. Gate records: `docs/BACKLOG.md` -> R-210 SHIP RECORD + BUILD78-DEV GATE
>   RECORD. Ruling: `docs/WILL_RULINGS.md` -> R-210. RCA: `docs/PORTAL_PAGE_DLC_CAP.md`.
> - **NEW permanent gate:** `tools/gate_dlc_act_ui_cap.py` (fail-loud, golden allow-list, negative-tested
>   3 ways) runs in-memory at cap time, on the WRITTEN `.arz`, and again on the DIST payload at push-gate.
>   It fails equally if a DLC act reappears OR if one of the four legitimate acts goes missing.
> - **Contracts: 0 P0 / 0 P1 / 4492 P2 on the dist payload, and the baseline arz under the identical config
>   also gives 4492** - zero new violations, measured both directions.
> - **Rollback (one step, either surface):** `local/build77_ship_435cc485.arz` (also
>   `local/DEV_arz_deployed_prev.arz`) = the build77 arz this replaced.
> - **Will's in-game check:** open a portal and count the act tabs - four (Greece / Egypt / Orient /
>   Immortal Throne), no Atlantis; the Immortal Throne page still lists Olympus and all of Hades. Full note
>   at the top of `docs/WILL_TEST_GUIDE.md`. Fully quit TQ and restart Steam first.
> - ⚠️ **STILL OPEN (`BL-PORTALCAP-DEBT-1`, P1):** this removes the Atlantis PAGE, not the Atlantis VOYAGE.
>   An Atlantis-DLC owner can still sail Rhodes -> Gadir -> Atlantis. Needs its own lane and Will's sign-off
>   on the layer; options ranked in `PORTAL_PAGE_DLC_CAP.md` section 8.

> ## BUILD77 SHIPPED TO STEAM (2026-08-10) - R-201 soul tier naming; arz-only delta on build76-ship
> **Workshop item 3759792705 is now build77 CANONICAL** (was build76). `Committing update...Success.` +
> `Updated Workshop item: 3759792705`; VDF read back `"visibility" "0"` (stays PUBLIC). 56 files, 1188.3 MB,
> single wrapper. **STEAM = DEV = `main`** for the arz: `435cc485ee43e739b85d4221e6c9bb4b` (55,550,972 B).
> - `Database/SoulvizierClassic.arz` = **`435cc485`** (CHANGED from `16994072`). det-2x byte-identical.
> - `Resources/Levels.arc` = `6784cf0f` CANONICAL (NOT the TESTHUB `7a7ca9ac`) / `Quests.arc` = `607ec99c` /
>   `Text.arc` = `a9fed7ba` / `Creatures.arc` = `8c0d8d53` - all byte-unchanged, re-uploaded as-is.
> - **Push-gate:** dist==work all 5 artifacts PASS, TESTHUB guard PASS, single-wrapper PASS,
>   `run_contracts` on the dist payload 0 P0 / 0 P1 / 4492 P2 (identical to the baseline A/B, so ZERO new
>   violations), changenote 1,939 chars VDF-safe.
> - **TQ.exe never running, never killed; Steam never restarted.** DEV was deployed first (`build77-dev`).
> - Tag `build77-ship` at this doc commit. Rollback (Steam): re-upload the build76 set (arz `16994072`,
>   kept at `local/build76_ship_16994072.arz`; the other four artifacts are unchanged).
> - ✅ **POST-SHIP INDEPENDENT VET = GO** (ship operator, read-only, no rebuild/re-upload). Re-proved from
>   bytes, not from this doc: record-diff `16994072` -> `435cc485` = **0 added / 0 removed / 196 modified,
>   changed-field set exactly `['itemQualityTag']`, all under `svc_uber\`, 0 unexplained**; convention +
>   distinctness over ALL THREE tiers (n=716 / e=739 / l=739 records, 740 families) = **0 C1 / 0 C2** on the
>   shipped arz AND on the newer `f6638462` now live (so R-201 survived the R-210 rebuild); `tagSoulEpic`
>   = `{^F}Epic` + `tagSoulLegendary` = `{^F}Legendary` both DEFINED in the shipped `Text.arc a9fed7ba`,
>   which is what makes the byte-identical Text the coupling law SATISFIED (tag-diff = zero changed tags);
>   Steam upload re-confirmed from `C:\steamcmd\logs\content_log.txt` (ManifestID `4847215467152146492`,
>   `Upload finished ... : OK` 21:27:37). One NEW pre-existing debt found and registered:
>   **`BL-R201-DEBT-1`** (5 of our 98 share a display name with an SV soul - Charon, General Yrrt'ik, Ice
>   Mandible, Kallixenia, Plague Feast; the gate only checks within a family). Will's test note was
>   corrected to use only provably-unique names.


> ## BUILD77-DEV DEPLOYED TO DEV (2026-08-10) - R-201 soul tier naming; arz-ONLY
> **`SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = `435cc485ee43e739b85d4221e6c9bb4b`**
> (55,550,972 B, 51,234 records), copied with md5 source==dest verification **while TQ.exe was NOT running**
> (nothing killed, Steam not restarted). 1 of 62 DEV files changed; the 61 siblings were re-hashed after the
> copy and are byte-identical.
> - **What it is:** R-201. The 98 souls this port authored (all under `soul\svc_uber\`) had no
>   `itemQualityTag` on any tier, so their normal / epic / legendary records all rendered the SAME name.
>   Every SV-original family (641 of 739) has always carried n=absent / e=`tagSoulEpic` / l=`tagSoulLegendary`,
>   which the engine renders as a PREFIX. 196 records (98 families x Epic + Legendary) now carry it, so the
>   Gaoler reads "Soul of the Gaoler" / "Epic Soul of the Gaoler" / "Legendary Soul of the Gaoler".
>   No string was renamed and no SV original was touched (the fix is ADD-ONLY).
> - **arz-ONLY.** `Levels.arc 7a7ca9ac` (TESTHUB, the DEV variant) / `Text.arc a9fed7ba` / `Quests.arc 607ec99c` /
>   `Creatures.arc 8c0d8d53` md5-proven byte-unchanged on the DEV surface. `validate_tags` PASS against the
>   EXISTING `Text.arc` - this wave authors NO new tag, so no Text rebuild was needed and the arz+Text
>   coupling law is satisfied rather than waived.
> - **Record-diff vs the shipped `16994072`: ADDED 0 / REMOVED 0 / MODIFIED 196, ZERO unexplained** (each row
>   is one `svc_uber\*_soul_{e,l}.dbr` with exactly one changed field). Gate record: `docs/BACKLOG.md` ->
>   GATE RECORD - R-201 SOUL TIER NAMING. Ruling: `docs/WILL_RULINGS.md` -> R-201.
> - **NEW permanent gate:** `_verify_soul_tier_naming` (fail-loud, no whitelist) runs in `run_registry_gates`
>   after the whole patches registry, so souls added by any FUTURE content module are covered. Negative-tested
>   4 ways.
> - **Rollback (one step):** `local/DEV_arz_deployed_prev.arz` = `16994072` (the build76 arz this replaced) ->
>   copy back over the DEV `Database/SoulvizierClassicDEV.arz`. The same bytes are also kept at
>   `local/build76_ship_16994072.arz`.
> - **Will's in-game check:** pick up the Soul of the Gaoler on Epic and on Legendary and read the item name.
>   Full note at the top of `docs/WILL_TEST_GUIDE.md`. Fully quit TQ and restart Steam first.


> ## BUILD75-DEV DEPLOYED TO DEV (2026-08-10) - R-180 chest-loot breadth; arz-ONLY; Steam rides the b63 package
> **`SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz` = `3fb1f3ce8889e27de2491ab12814547d`**
> (55,539,324 B, 51,231 records), copied with md5 source==dest verification **while TQ.exe was NOT running**
> (nothing killed, Steam not restarted). **DEV2 no longer exists** - `SoulvizierClassicDEV` is the only DEV entry.
> - **What it is:** R-180 chest-loot breadth (every mod chest pays every weapon class, SPEAR included; the cage's
>   six chests get 3 themed variants per difficulty at 50/25/25) **plus** the 08-08/08-09 relic difficulty-tiering
>   that had never shipped. det-2x identical across two independent builds; registry 54 modules, order `0c76e6652069`.
> - **arz-ONLY.** At build time `Levels.arc 78a3e263` / `Text.arc a9fed7ba` / `Quests.arc 6b25f8dd` /
>   `Creatures.arc 8c0d8d53` were md5-proven byte-unchanged. `validate_tags` PASS against the EXISTING `Text.arc`,
>   so no Text rebuild was needed. Gate record: `docs/BACKLOG.md` -> BUILD75-DEV GATE RECORD. Tag `build75-dev`.
> - **Rollback (one step):** `local/DEV_arz_deployed_prev.arz` = `9c190b99` (the arz this replaced) -> copy back over
>   the DEV `Database/SoulvizierClassicDEV.arz`. A clean copy of the NEW artifact is kept at
>   `local/SoulvizierClassic.build75-dev.R180.arz`.
> - ⚠️ **The other DEV artifacts moved under this lane, by the concurrent b63 SILENT-WARDEN lane, not by it.**
>   As of this note the DEV entry carries `Levels.arc 7a7ca9ac` and `Quests.arc 607ec99c` (the b63 Warden
>   relocation + travel rewire), NOT the `3a6f9d74`/`6b25f8dd` pair that was live when this arz was built. The DEV
>   surface therefore carries BOTH fixes; that is intended, and the two changes are disjoint (arz vs Levels+Quests).
> - **Steam: ✅ LIVE.** `main` advanced to `824ed0c` (b63 Warden P0) then `5742775` (R-200) mid-build, and that lane
>   packaged + uploaded a COMBINED payload that **contains this arz `3fb1f3ce`** plus its Warden
>   `Levels.arc 6784cf0f` / `Quests.arc 607ec99c` (`Text.arc a9fed7ba` + `Creatures.arc 8c0d8d53` unchanged), under a
>   combined `docs/WORKSHOP_CHANGENOTE.bbcode`. **Workshop item 3759792705, `Upload finished : OK`, ManifestID
>   `5994342952492618257`** (steamcmd log 2026-08-10 19:22:53 -> 19:23:09). Steam is no longer build74 (`d447f095`).
>   This lane did NOT run the upload - a second package/upload would have raced a concurrent write to the same item.
>   ⚠️ Owed by that lane: **no `buildNN-ship` tag was taken** (the shipped tree is a mix of both lanes, so neither
>   lane's commit is an honest anchor), and **R-200 (`5742775`) is NOT in the shipped arz** - the package reused this
>   lane's already-built arz rather than rebuilding from the newer `main`, so R-200 still awaits a ship.
> - **Will's in-game check (build75-dev):** Prison of Souls / Hades Palace floor 4 - kill **Alkyoneus the
>   Soul-Gaoler**, open **all 6 cage chests across 3 runs**; expect **legendary spears** and visible class variety
>   between chests. Full note in `docs/WILL_TEST_GUIDE.md` (R-180 section). Fully quit TQ and restart Steam first.

> ## BUILD40-DEV DEPLOYED TO DEV + DEV2 (2026-07-14, post-Steam-ship) - both DEV surfaces now build40-dev
> **`SoulvizierClassicDEV` AND `SoulvizierClassicDEV2` both = build40-dev.** Deployed while TQ.exe was NOT
> running (Steam client NOT restarted). Both DEV entries carry the **TESTHUB** Levels (the Helos traveler
> hub) over the build40 DB/Text/Quests - identical artifacts, only the arz filename differs per the
> folder-name convention. All 4 artifacts md5-verified source==dest on BOTH entries:
> - **arz** = `b33c5a447f3a8ca652c14f78d4ad1dd4` (55,351,206 B) - the build40 DB (warden C-RES-DBR-1 P1 FIX
>   `32ea0e8` included). DEV -> `Database/SoulvizierClassicDEV.arz`; DEV2 -> `Database/SoulvizierClassicDEV2.arz`.
> - **Resources/Levels.arc** = `d4965d298ee308a4e31ffd39802ce404` (688,677,830 B) = the build40 **TESTHUB** map
>   (NOT the canonical `9981085b` that shipped to Steam). This is the hub-enabled dev-only variant; it is never
>   uploaded to Steam.
> - **Resources/Quests.arc** = `37cf867f3550f5031dba5cb1cf31f30f` (194,801 B) = build40 canonical Quests.
> - **Resources/Text.arc** = `c910da653f23ff84598b69833854d9db` (87,555 B) = build40 Text.
> - **DEV2 is the fresh-char test surface:** deploy the placement/spawn fixes (b41-b48) and eyeball them on a
>   BRAND-NEW Custom Quest character on DEV2 to dodge save-baking (Will's main DEV char has world state baked
>   in). See the WILL_TEST_GUIDE BUILD40 CHECKS section.
> - **Rollback (one step, build40-dev -> build39-dev):** the pre-deploy DEV/DEV2 artifacts (build39-dev: arz
>   `5bf7dac2` / Levels `4fcc058c` TESTHUB hub v2 / Quests `7655f17e` / Text `e1b73e05`) are saved to
>   `local/DEV_{arz,Levels,Quests,Text}_deployed_prev.*` and `local/DEV2_{arz,Levels,Quests,Text}_deployed_prev.*`
>   (all 8 md5-verified). Copy them back over the DEV/DEV2 entries to revert.
> - **Steam is build40 canonical** (shipped earlier today, ManifestID `6660459504081325574`, canonical Levels
>   `9981085b`); this DEV deploy does NOT touch Steam. Tag `build40-dev` at this doc commit.
> - **To load: fully quit TQ if open, then start TQ fresh** (Steam was already running and was NOT restarted;
>   the deploy landed while TQ was closed, so the files are not locked).

> ## BUILD40 SHIPPED TO STEAM (2026-07-14) - FIRST canonical map+quest advance since build36a; TESTHUB hub NOT shipped
> **Workshop item 3759792705 is now build40 CANONICAL** (was build39). Will's standing directive: ship the FULL build40
> to Steam including the Ephialtes/Mnemophage sizes AND the Aithon arena (sight-unseen, "ship everything, including the
> 3"). ALL 4 canonical artifacts advanced - the FIRST canonical Levels+Quests change since build36a. Shipped md5s (each
> verified at gate-record, stage, package, dist, and the F9 dist==work push-gate):
> - `Database/SoulvizierClassic.arz` = **`b33c5a447f3a8ca652c14f78d4ad1dd4`** (55,351,206 B, 51,029 records) - the
>   build40 DB: record-diff vs build39 `5bf7dac2` = 14 ADDED / 0 REMOVED / 1035 MODIFIED, ZERO unexplained. Content: b42
>   boss chests (Charon/Dorus/Ephialtes/Tantalus) + Ephialtes dread-nova, b43 boss_arena + Aithon Embercrown soul
>   (n/e/l), b49 enslaver + Endless-Hunt undead/Hades pool sweeps (990 records) + shadowstalker rig, b50 pet-white
>   nameplates, b52 Dagon, b53 orb, b47 Kroisos. 13-module registry (order `b82195e9551a`, +bossarena b43). Warden
>   C-RES-DBR-1 P1 FIX (`32ea0e8`): `ember_satyr_warden_55.lootLowerBodyItem1` scrubbed (the 3 dangling
>   {N,E,L}_SatyrBrute leg-loot refs gone; 0 gameplay change - the slot dropped nothing, same as the base donor);
>   contracts_resources 1 P1 -> 0 P1.
> - `Resources/Text.arc` = **`c910da653f23ff84598b69833854d9db`** (87,555 B) - i18n de-clobber (10,600 base-identical SV
>   tags dropped); validate_tags PASS (321 referenced + 367 authoritative tags resolve, incl. b52 Dagon / b47 Kroisos /
>   b43 Aithon); golden A7 PASS (41 waived).
> - `Resources/Levels.arc` = **`9981085b78f1600cc0b31c3bec4cfd92`** (688,691,745 B) = build40 CANONICAL map (NOT the
>   TESTHUB `d4965d298ee308a4e31ffd39802ce404`). FIRST canonical rebuild since build36a `60a62880`. 18 intended blobs
>   (b41 Hades cluster / b42 / b43 boss_arena / b45 ThebesOptTombA / b46 / b47 Medea TempleUG x2 / b48 established
>   returns); navmesh(0x0b) 0 changed (byte-identical); QUESTS(0x1b) byte-identical (256-window parity). The b48
>   established returns (Garden/Secret/Uber/Sparta) are the deliberate CANONICAL warden-mute bugfix that motivated the
>   rebuild (`docs/reports/b48_sparta_mute_fix.md`).
> - `Resources/Quests.arc` = **`37cf867f3550f5031dba5cb1cf31f30f`** (194,801 B) = build40 CANONICAL Quests (SUPERSEDES
>   the old TESTHUB `7655f17e`). The 25 hub boat-dialog triggers are appended to the always-loaded `sv_commonmechanics`
>   refire step (NO new QUESTS-section registration -> map 256-window parity intact); they are INERT on canonical
>   because the canonical map places 0 hub NPCs (T6 proven). 107 entry_type==3 quest records.
> - **Push-gate (all against the exact dist payload): GATE PASS.** F9 dist==work coupling PASS (all 4 artifacts). F7
>   run_contracts on the DIST payload: **0 P0 / 0 P1 / 4909 P2** across 5 modules (map 3 + quests 2 + resources 4792 +
>   summons 112 + souls 0; every P2 is pre-existing SV/DLC/base-inherited debt; warden C-RES-DBR-1 P1 GONE). Contract
>   whitelists UNMODIFIED, so the 0 P1 is genuine (the warden was FIXED, not whitelisted). `gate_travel_npc_invariants`
>   T1-T6 PASS on the canonical `.arc`: **0 authored walk-throughs, 0 hub-record placements** (25 hub records 0x
>   canonical / 1x TESTHUB), 5 per-area returns fire - proving the DEV hub did NOT leak. Package TESTHUB guard PASS
>   (packaged `9981085b` differs from TESTHUB `d4965d29`).
> - **Upload:** steamcmd cached session (no re-auth: "Logging in using cached credentials...OK"), `-Update -Visibility
>   0`; "Committing update...Success" + "Upload complete", **ManifestID `6660459504081325574`** (steamcmd log 2026-07-14
>   12:09:56 -> 12:10:29 OK). Steam client NOT restarted; TQ.exe was not running.
> - **DEV + local UNTOUCHED by this ship:** the canonical build40 map is staged in `work/` + `local/Levels_merged.arc`;
>   the TESTHUB variant (`local/Levels_merged_TESTHUB.arc` `d4965d29`) is local-only and was NOT uploaded. A build40 DEV
>   CustomMaps deploy remains pending a TQ-exit window (separate from this Steam ship).
> - **Rollback (Steam):** re-upload the build39 canonical set (arz `5bf7dac2` / Levels `60a62880` / Text `e1b73e05` /
>   Quests `56acee66`). Tag `build40-ship` at this doc commit; gate record = BACKLOG.md BUILD40 GATE RECORD @ `9d74b1c`.

> ## BUILD39 SHIPPED TO STEAM (2026-07-14) - boss-skill fixes; DEV traveler hub NOT shipped
> **Workshop item 3759792705 is now build39 CANONICAL** (was build38a). Will explicitly ordered
> "ship build 39 to steam." Only the DB (`arz`) and `Text.arc` advanced from published build38a; the
> canonical `Levels.arc` and `Quests.arc` were re-uploaded BYTE-IDENTICAL to build38a/build36a (the
> build39 map/quest change is the TESTHUB Helos hub v2, dev-only, deliberately kept OFF Steam).
> Shipped md5s (each verified at snapshot, stage, package, and in the F9 dist==work push-gate):
> - `Database/SoulvizierClassic.arz` = **`5bf7dac29beb75757178179c363af2cf`** (55,354,147 B) = the
>   build39-dev arz. Fix on top of build38a's b37/b38 fixes: `boss_skill_fix`, so every new boss
>   casts its skills in BOTH fought and soul-summoned forms. 12-module registry (order
>   `4c688f58d1aa`); record-diff vs build38a 8 added / 10 changed, zero unexplained.
> - `Resources/Text.arc` = **`e1b73e050975b63521a30062c21e009b`** (87,360 B) = build39-dev Text.
> - `Resources/Levels.arc` = **`60a628807c1746e7bbde14946de62107`** (688,682,781 B) = CANONICAL
>   build36a map (NOT the TESTHUB `4fcc058c590ab0719e224940ba0b9266`). Byte-identical to build38a.
> - `Resources/Quests.arc` = **`56acee660e0c3dc7408f7d985231338c`** (194,092 B) = CANONICAL build36
>   Quests (NOT the TESTHUB `7655f17e5a5f8bf13956ef456ca10595` with 25 hub triggers). Byte-identical
>   to build38a. Both canonical artifacts staged from `local/` because work/ held the TESTHUB copy.
> - **Push-gate (all against the exact dist payload): GATE PASS.** run_contracts 0 P0 / 0 P1 / 4910
>   P2 across all 5 modules (every P2 pre-existing SV/DLC-inherited debt; anm_dreamcopy whitelist
>   entry present). F9 dist==work coupling PASS. Travel-invariant gate (`gate_travel_npc_invariants`
>   T6) PASS on the canonical `.arc`: 0 hub-record placements, 0 authored walk-throughs (SV-native
>   baseline 3 only), which proves the DEV hub did NOT leak. Package TESTHUB guard PASS (packaged
>   Levels `60a62880` differs from TESTHUB `4fcc058c`).
> - **Upload:** steamcmd cached session (no re-auth), `-Update -Visibility 0`; SteamCMD "Committing
>   update...Success" + "Upload complete", ManifestID `4886001279629433633` (steamcmd log
>   2026-07-14 08:14:48 -> 08:14:57 OK). Delta-only: Levels/Quests unchanged from build38a were
>   skipped. Tagged `build39-ship`. Shipped concurrently with the build40 lane consolidation on main
>   (build40's in-flight merge/index left undisturbed; doc committed path-scoped).

> ## BUILD39-DEV DEPLOYED TO DEV (2026-07-13, post-Steam-ship) - boss skills + hub v2
> **DEV entry `SoulvizierClassicDEV` = build39-dev** (deployed by the TQ-exit watcher ~570s after
> Will's session ended; all 4 artifacts md5-verified source==dest):
> - `Database/SoulvizierClassicDEV.arz` = `5bf7dac29beb75757178179c363af2cf` (55,354,147 B; 12-module
>   registry order `4c688f58d1aa` incl. `boss_skill_fix` - every new boss casts in BOTH fought and
>   soul-summoned forms; record-diff vs build38a: 8 added / 10 changed, zero unexplained, zero
>   design-field drift).
> - `Resources/Levels.arc` = `4fcc058c590ab0719e224940ba0b9266` (688,686,024 B, TESTHUB) - hub v2:
>   travelers land at the in-game travel NPC / area entrance (NOT the boss set-piece; fixes the
>   land-inside-the-chest insta-death), plus boss-entrance portals for every placed boss.
> - `Resources/Text.arc` = `e1b73e050975b63521a30062c21e009b` (87,360 B); `Resources/Quests.arc` =
>   `7655f17e5a5f8bf13956ef456ca10595` (194,754 B, 25 hub travel triggers).
> - Rollback (one step, staged): `local/DEV_{arz,Text,Levels,Quests}_deployed_prev.*` = the
>   build38a-dev set (6631f252 / dff9ad01 / 841c56cd / 838bdc3a).
> - WILL: restart TQ only. KNOWN RESIDUAL: the Sparta traveler mute-click fix (b48) may not be in
>   this hub build - lands in the b40 consolidation with the rest of the in-flight lanes.
> - Steam is UNAFFECTED (still build38a canonical; TESTHUB never ships).

> ## BUILD38A SHIPPED TO STEAM (2026-07-13) - canonical b37/b38 fixes; DEV traveler hub NOT shipped
> **Workshop item 3759792705 is now build38a CANONICAL** (was build36a). Will explicitly
> authorized the ship ("everything that has been fixed ship to steam ... the latest version ...
> without the dev testing things"). Only the DB (`arz`) and `Text.arc` advanced from the published
> build36a; the canonical `Levels.arc` and `Quests.arc` were re-uploaded BYTE-IDENTICAL to build36a
> (no b37/b38 map or quest change is canonical - the Helos traveler hub is a TESTHUB/dev-only thing
> and was deliberately kept OFF Steam). Shipped canonical md5s (each verified at stage, package, and
> in the F9 dist==work push-gate):
> - `Database/SoulvizierClassic.arz` = **`6631f25219be1b8f9874c95af68755c7`** (55,340,923 B) - the
>   fixes: mastery-UI audit (8 icon repoints + Earth Rupture de-dup via Flame Surge/Flame Arch
>   relabel + Earth col reflow + Dream bg) + cross-mastery skill-tree UI, damage-display (7 AE
>   floating combat-text FontStyle binds on `records\xpack\game\gameengine.dbr`), Enslaver v2
>   single-spawn/rate + Endless-Hunt legendary-stalker per-slot `limitN=1`, four generals + the b37
>   registry bosses (diadochi / polis_vault / neferkha / toxeus_suite) + skill_quality + H/O
>   improvements. 11-module registry, order hash `7c74a51f6ed8`, post-finalization
>   `run_registry_verifies` GREEN.
> - `Resources/Text.arc` = **`dff9ad01ec1d81064f426d9456470eaf`** (87,261 B) - language de-clobber
>   (~10,600 base-identical SV tags dropped so the base `Text_EN` strings win).
> - `Resources/Levels.arc` = **`60a628807c1746e7bbde14946de62107`** (688,682,781 B) = CANONICAL
>   build36a map (NOT the TESTHUB `841c56cd`). The 17 Helos-hub traveler NPC records exist INERTLY in
>   the arz but are NOT placed in this map.
> - `Resources/Quests.arc` = **`56acee660e0c3dc7408f7d985231338c`** (194,092 B) = CANONICAL build36
>   Quests (NOT the TESTHUB `838bdc3a`, which carries the 17 hub travel triggers). RESTAGED from
>   `local/Quests_deployed_prev.arc` before packaging because work/ held the TESTHUB copy.
> - **Push-gate (all against the exact dist payload): GATE PASS.** run_contracts 0 P0 / 0 P1 / 4910
>   P2 across all 5 modules (every P2 is pre-existing SV/DLC-inherited debt - matches build36a's
>   clean gate; anm_dreamcopy whitelist entry already present). F9 dist==work coupling PASS. Travel
>   invariant gate (`gate_travel_npc_invariants` T6) PASS on the canonical `.arc`: 0 hub-record
>   placements (each of the 17 travelers = 0x), 0 authored walk-throughs (SV-native baseline 3 only).
>   The 7 damage FontStyle targets and the Enslaver/Diadochi `343_dark_smoke` FX all RESOLVE (no
>   green fallback).
> - **Upload:** steamcmd cached session (no re-auth), `-Update -Visibility 0`; SteamCMD "Committing
>   update...Success" + "Upload complete", ManifestID `2737266903501499696`
>   (steamcmd log 2026-07-13 19:30:44 -> 19:30:57 OK). The workshop description (bbcode) is already
>   live and re-sent on every content upload.
> - **DEV + local UNTOUCHED:** the DEV entry `SoulvizierClassicDEV` still runs build38a-dev with the
>   TESTHUB map (`841c56cd`) + TESTHUB Quests (`838bdc3a`); that dev traveler hub is local-only and
>   was NOT shipped. **Steam client NOT restarted and NOTHING killed** - TQ.exe was running (Will
>   actively playing); the Workshop upload used steamcmd's separate cached session, which does not
>   require the Steam client or TQ to be closed.
> - **Rollback (Steam):** re-upload the build36a canonical set (arz `63ca7cf8` / Levels `60a62880` /
>   Text `2af4ce38` / Quests `56acee66`). Tag `build38a-ship` at this doc commit.

> ## BUILD38A-dev DEPLOYED TO DEV (2026-07-13) - DB-only Endless-Hunt stalker limit=1 fix (arz only; Text/map/Quests stay build38-dev); STEAM UNTOUCHED
> **The DEV entry `SoulvizierClassicDEV` now runs build38a-dev.** ONLY the DB (`arz`) advanced from
> build38-dev; `Text.arc`, the TESTHUB `Levels.arc`, and `Quests.arc` are byte-identical to build38-dev
> (verified on disk, deliberately NOT recopied, per the "verify unchanged, do not touch" deploy rule).
> All four coupled artifacts were md5-verified at source + destination.
> - `Database/SoulvizierClassicDEV.arz` = **`6631f25219be1b8f9874c95af68755c7`** (55,340,923 B):
>   DB-only rebuild (registry 11 modules, order hash `7c74a51f6ed8`, post-finalization
>   `run_registry_verifies` phase GREEN) that adds the missing per-slot `limitN=1` cap to the
>   Endless-Hunt legendary stalker sweep in the Hades trash pools
>   (`tools/patches/toxeus_suite.py` `_sweep_inject_legendary_stalker`). This closes the exact
>   "two-in-one-trigger" defect class just fixed for the Enslaver: pool MAIN draws are with-replacement,
>   so a weight-1 member with no limit could roll twice in one trigger; vanilla always caps rare pack
>   members with `limitN=1`. Apply-time gate LIVE PASS: 345 eligible Hades trash pools carry the Hunt
>   at weight 1 + per-slot limit 1 (p_slot <= 1/2400, <=1 Hunt per trigger); 0 non-Hades/boss/quest/hero
>   leaks; Enslaver sweep unchanged. Record-diff vs build38-dev arz (`fcd5dcab`) = 0 ADDED / 0 REMOVED /
>   345 CHANGED, ZERO unexplained: every delta is exactly one `records\xpack\proxieshades\` pool's Hunt
>   name-slot gaining `limitN=1` (Int), 1 field/record, 0 collateral. +1,360 B vs build38-dev = 345 new
>   int fields. validate_tags PASS (0 new tags authored); contracts(souls/summons/resources) +
>   contracts(map vs TESTHUB Levels `841c56cd`) GATE PASS (0 P0 / 0 P1).
> - `Resources/Text.arc` = **`dff9ad01ec1d81064f426d9456470eaf`** (87,261 B), `Resources/Levels.arc` =
>   **`841c56cd2b6b8a87209327cb02529d23`** (688,688,154 B), and `Resources/Quests.arc` =
>   **`838bdc3a3716b5e9028c076317e99608`** (194,581 B): ALL UNCHANGED from build38-dev (the fix authors
>   no new tags and no map/quest edits, so none were rebuilt). Verified on disk, NOT recopied. Canonical
>   `local/Levels_merged.arc` (`60a62880`) also untouched.
> - **STEAM = build36a canonical, UNTOUCHED** (Workshop item 3759792705: arz `63ca7cf8` / Levels
>   `60a62880` / Text `2af4ce38` / Quests `56acee66`). TESTHUB is LOCAL-ONLY; never uploaded.
> - **To see it, Will only needs to fully quit + restart TQ.** Do NOT restart Steam (it stays
>   build36a); TQ was not running at deploy time.
> - **Will's in-game check wanted (build38a-dev):** the **Endless-Hunt legendary stalker** should now
>   appear **at most once per Hades trash pack** (no more two-in-one-trigger doubles). Everything else
>   is identical to build38-dev, so the build38-dev checks (damage numbers, mastery pages, English
>   sanity) still hold.
> - **Rollback to build38-dev on DEV:** copy `local/DEV_arz_deployed_prev.arz` (`fcd5dcab`) -> DEV
>   `Database/SoulvizierClassicDEV.arz` (Text/Levels/Quests need no change). Build gate record at
>   `261af9e` (`docs/BACKLOG.md`, BUILD38A GATE RECORD); tag `build38a-dev` at this deploy commit.

> ## BUILD38-dev DEPLOYED TO DEV (2026-07-13) - b38 arz + Text only (map/Quests stay build37-dev); STEAM UNTOUCHED
> **The DEV entry `SoulvizierClassicDEV` now runs build38-dev.** Only the DB (`arz`) and `Text.arc`
> advanced from build37-dev; the TESTHUB map and Quests are byte-identical to build37-dev (verified on
> disk, deliberately NOT recopied, per the "verify unchanged, do not touch" deploy rule). All four
> coupled artifacts were md5-verified source + destination:
> - `Database/SoulvizierClassicDEV.arz` = **`fcd5dcab40359aa94b421dd8cef4b81e`** (55,339,563 B):
>   11-module registry build (order hash `7c74a51f6ed8`, post-finalization `run_registry_verifies`
>   phase GREEN), the 5 GO-vetted b38 branches folded in: mastery-UI audit (8 icon repoints + Earth
>   Rupture de-dup via Flame Surge/Flame Arch relabel + Earth col-428 reflow + Dream bg), damage_display
>   (7 missing AE FontStyle pointers bound on xpack gameengine.dbr), enslaver-v2 roam sweep (/10 vs
>   build36a, structural limit=1 per pool slot), earthfury pcsafe cd restored 16.0 -> 5.0 (fixes the
>   build37-dev regression). Record-diff vs build37-dev arz (`56d6db22`) = 1242 changed, 0 added,
>   0 removed, ZERO unexplained.
> - `Resources/Text.arc` = **`dff9ad01ec1d81064f426d9456470eaf`** (87,261 B): language de-clobber
>   (dropped 10,600 SV tags that were byte-identical to base `Text_EN` so the base strings win;
>   sanity-diff 0 not-in-base / 0 value-mismatch). Golden A7 PASS (41 waived / 0 other), validate_tags
>   PASS. Size dropped from build37-dev's 377,150 B precisely because those base-identical tags are no
>   longer duplicated in the mod arc.
> - `Resources/Levels.arc` = **`841c56cd2b6b8a87209327cb02529d23`** (688,688,154 B) and
>   `Resources/Quests.arc` = **`838bdc3a3716b5e9028c076317e99608`** (194,581 B): UNCHANGED from
>   build37-dev (TESTHUB map, `SVC_TEST_HUB=1`, 17 Helos-hub travel triggers). Verified on disk, NOT
>   recopied. Canonical `local/Levels_merged.arc` (`60a62880`) also untouched.
> - **STEAM = build36a canonical, UNTOUCHED** (Workshop item 3759792705: arz `63ca7cf8` / Levels
>   `60a62880` / Text `2af4ce38` / Quests `56acee66`). TESTHUB is LOCAL-ONLY; never uploaded.
> - **To see it, Will only needs to fully quit + restart TQ.** Do NOT restart Steam (it stays
>   build36a); TQ was not running at deploy time.
> - **Will's in-game checks wanted (build38-dev):** (1) **DAMAGE NUMBERS** - floating damage numbers
>   display with correct font styling (the 7 AE FontStyle binds); (2) **MASTERY PAGES** - the mastery
>   selection screens look right (8 icon repoints, Earth Rupture no longer duplicated, Earth column
>   reflow, Dream background); (3) **ENGLISH SANITY CHECK** - a quick read that skill/item/UI text still
>   reads correctly after the language de-clobber (base-game strings now win for the 10,600 de-duped
>   tags). Full step-by-step in `docs/WILL_TEST_GUIDE.md` (BUILD38 CHECKS).
> - **Rollback to build37-dev on DEV:** copy `local/DEV_arz_deployed_prev.arz` (`56d6db22`) -> DEV
>   `Database/SoulvizierClassicDEV.arz` and `local/DEV_Text_deployed_prev.arc` (`8c7229db`) -> DEV
>   `Resources/Text.arc` (Levels/Quests need no change). Build gate record at `19f85da`
>   (`docs/BACKLOG.md`); tag `build38-dev` at this deploy commit.

> ## BUILD37-dev DEPLOYED TO DEV (2026-07-13) - TESTHUB traveler hub + coupled arz/Text/Quests; STEAM UNTOUCHED
> **The DEV entry `SoulvizierClassicDEV` now runs build37-dev** (local TESTHUB build for Will's
> Helos-traveler-hub tour before anything more ships to Steam). All 4 coupled artifacts were copied to
> `CustomMaps/SoulvizierClassicDEV` and md5-verified on disk (source + destination both hashed):
> - `Resources/Levels.arc` = **`841c56cd2b6b8a87209327cb02529d23`** (688,688,154 B): TESTHUB map
>   (`SVC_TEST_HUB=1`), 17 hub-gated traveler/return NPCs. Canonical `local/Levels_merged.arc` UNCHANGED
>   (`60a62880`) - never rebuilt.
> - `Database/SoulvizierClassicDEV.arz` = **`56d6db221466eb991804f001aa1a83a5`** (55,334,381 B): first
>   full-registry DB build (9 modules, order hash `7ed29402a38d`) - registry bosses
>   (neferkha/toxeus_suite/polis_vault/diadochi/four_generals) + skill_quality de-filler + H/O
>   improvements + lane-A (BL-ENSLAVER-SPAWNS / smoke-FX / bloodhound). Record-diff vs build36 arz =
>   124 ADDED / 0 REMOVED / 1394 CHANGED, 0 unexplained, 0 clobbers.
> - `Resources/Text.arc` = **`8c7229db978fd5ecc24a94053c30306e`** (377,150 B): golden A7 guard PASS
>   (41 waived / 0 other); validate_tags PASS.
> - `Resources/Quests.arc` = **`838bdc3a3716b5e9028c076317e99608`** (194,581 B): exactly 17 Helos-hub
>   travel triggers appended to `sv_commonmechanics.qst`; entry-diff vs build36a = ONLY that file.
>   (Levels+Quests couple: the hub NPCs ride the map, their dialog triggers ride Quests; the 256-slot
>   QUESTS window parity is preserved.)
> - **STEAM = build36a canonical, UNTOUCHED** (Workshop item 3759792705: arz `63ca7cf8` /
>   Levels `60a62880` / Text `2af4ce38` / Quests `56acee66`). TESTHUB is LOCAL-ONLY; never uploaded.
> - **To see it, Will only needs to fully quit + restart TQ** (Steam was already restarted today;
>   TQ was closed at deploy time). Tour: `docs/WILL_TEST_GUIDE.md` HELOS TRAVELER HUB section.
> - **Rollback to build36a on DEV:** copy `local/Levels_merged.arc` (`60a62880`) -> DEV
>   `Resources/Levels.arc`; rebuild the arz from git tag `build36` (or restore from `local/db_backups/`);
>   `local/Text_deployed_prev.arc` (`2af4ce38`) + `local/Quests_deployed_prev.arc` (`56acee66`) -> DEV
>   Text/Quests. Tag `build37-dev`; gate record at `efc1933` (`docs/BACKLOG.md`).
> - **Two non-blocking tuning-lane notes** (not gate failures, for a human glance): (1) pcsafe
>   `earthfury_ring` `skillCooldownTime` is 16.0 in this build vs 5.0 in build36a (opposite the A4
>   "16->5" build-log narrative); (2) stale "x60" comment in
>   `toxeus_suite._sweep_inject_legendary_stalker` (the Enslaver monolith sweep is now x300).

> ## BUILD36a P0 HOTFIX (2026-07-12) - walk-through travel portals REMOVED; NPC-dialog travel only
> **LIVE STEAM breakage fixed** (item 3759792705): "cant walk south in Helos - teleported to Garden of Merchants with no way back." Per Will's TRAVEL LAW every walk-through/proximity teleport we authored is stripped from the canonical map; ALL cross-area travel now routes through the NPC boat-dialog (Helos portal-master out; each area's `svc_testhub_return` NPC or an SV rift shrine back). Map tooling only (`tools/build_section_surgery.py`) - **arz/Text/Quests UNCHANGED from build36** (the return-NPC record + its dialog already shipped in the build36 arz/Quests, inert until the canonical map now places the NPC).
> - **Fix commit `0f08297`; tag `build36a`.** Canonical `Levels_merged.arc` md5 **`60a628807c1746e7bbde14946de62107`** (was `b42be44f`; 688,682,781 B). arz **63ca7cf8** / Text **2af4ce38** / Quests **56acee66** = build36, reused byte-identical (no DB/Quests rebuild).
> - **Blob-diff vs build36 canonical = EXACTLY 9 changed level blobs, 0 added/removed:** the 7 portal levels (startingfarmland06d, hiddenvalley01, gardenofmerchants, rhodes_secretvista_01, darkforestenter, maze03, catacube02_floorlast) + crypt_floor1 + spartacryptlevel2. Gates GREEN: navmeshes 24/24, seam-lattice 24 aligned/0 misaligned, entrance-landing PASS, map contracts 0 P0 / 0 P1 (3 pre-existing native/DLC P2).
> - **Removal inventory (20 authored teleports):** 16 walk-through GridEntrance/GridExitOneWay/map_portal_aura REMOVED from INJECT_SPECS (Helos H1/R2 + swirl; HV01 G1/G4 + swirl; Garden G2/G3/H2/R1 + swirl; vista S1/S4; Secret S2/S3; maze03->Uber; catacube->Sparta) + 4 native 0x06/0x05 return doors DISABLED (SC2 REWRITE_0X06, crypt APPEND_0X06, crypt REMOVE_0X05 - SV-original left untouched). KEPT: Helos + Olympus portal-master NPCs (dialog travel); rift shrines teleportshrine_gom + teleportshrineorient01. PROMOTED TESTHUB->canonical: 4 `svc_testhub_return` NPCs (Garden/Secret/Uber/Sparta). TESTHUB variants unchanged, local-only.
> - **STEAM: SHIPPED 2026-07-12** - SteamCMD "Upload complete", item 3759792705, Visibility 0 (public), cached login (no re-auth). Push-gate PASSED (F9 dist==work + F7 contract suite 0 P0/0 P1) after ONE justified whitelist entry (see below). **DEV (SoulvizierClassicDEV): map STAGED to work/ (`60a62880`); the CustomMaps DEV `Resources/Levels.arc` copy is DEFERRED** while TQ.exe is running (Will actively playing / crash-loop recovery) - copy `local/Levels_merged.arc` over the DEV `Resources/Levels.arc` when TQ exits; NEVER kill TQ.exe.
> - **PUSH-GATE WHITELIST (ship operator):** `tools/contracts/whitelist_quests.txt` +1 justified line `QST-DOOR-UNLOCK bossarena.qst :: records/quests/portal_olympianarena1.dbr` - removing the portal left bossarena.qst's unlock action naming an unplaced door (engine name-lookup no-ops; harmless; intended P0 consequence). Follow-up: a future Quests.arc rebuild should drop the dead action, then remove the whitelist line.

> **BUILD36 SHIPPED 2026-07-12** to Steam Workshop (item 3759792705, "Upload complete") AND the DEV entry (SoulvizierClassicDEV, hash-verified). Tag `build36` @ 9f96340. arz md5 63ca7cf8, canonical Levels_merged md5 b42be44f, Text 2af4ce38, Quests 56acee66 (reused, unchanged). CANONICAL map both targets (TESTHUB rebuild skipped - quota; canonical carries all content). What shipped: 5 uber bosses (Dorus/Tantalus/Charon/Mnemophage/Ephialtes) + Ereban relic + Enslaver rework (skeleton + 4 demon-strength marauders + orbs) + pet overhaul (4 summon-bug fixes) + 18 mastery grafts + Rune Golem + 6 soul RCA fixes + Shadow Stalker + Bloodcrow/Makaria/Anapaest CDs + Flash Powder rework + 21 handcrafted souls + Obsidian balance + Act-5->Epic fix + Vort red + crash mitigation. See docs/WILL_TEST_GUIDE.md (test menu + boss locations + SV areas) and docs/NEXT_STEPS_BUILD37.md (everything unfinished). MP TESTED+works.

---

# HANDOFF - LIVE PROJECT STATE (Soulvizier Classic)

> **Trust level: LIVE - keep this current.** This is the single current-state board. A brand-new
> agent reads `CLAUDE.md` → `docs/README.md` → this file, in that order.
> Open bugs/queue live in `docs/BACKLOG.md`; how-to recipes live in `docs/PLAYBOOK.md`.
> Long history was moved to `docs/ARCHIVE_2026-07.md` (do not trust it for current state).
> Last updated: 2026-07-08 (post workshop-wrapper-fix + doc consolidation).

---

## 1. WHAT THE MOD IS (2 lines)

Soulvizier Classic is a total-conversion Custom Quest mod for **Titan Quest Anniversary Edition
(TQAE)** - SV 0.98i back-ported and merged with SVAERA + the DRX visual overhaul, headlined by
hundreds of collectible monster "souls", a restored/walkable Soulvizier blood cave and its SV area
questlines, ~60 boss souls, 10 masteries, and a new blood superboss (Toxeus the Murderer).
It ships as content-only data (`.arz` database + `.arc` resources); no DLL/exe patch - Steam-clean.

---

## 2. ARTIFACT MODEL (where everything lives)

| Location | Role |
|---|---|
| `work/SoulvizierClassic/` | **Shipped staging.** The exact tree that gets packaged: `Database/SoulvizierClassic.arz` + `Resources/*.arc` (Levels/Text/Quests/DRX/SV/XPack). Regenerated by the build; gitignored. |
| `local/` | **Build outputs + backups.** Canonical map build `Levels_merged.arc`, hub variant `Levels_merged_TESTHUB.arc`, per-build baselines (`Levels_merged.buildNN-baseline.arc`), rolling `*_deployed_prev.arc`, `db_backups/`, `save_backups/`, navmesh donors in `editor_normalized/`. gitignored. |
| `dist/workshop/content/SoulvizierClassic/` | **Workshop staging.** What `package_workshop.ps1` writes: a SINGLE `SoulvizierClassic/` wrapper with `database/` + `resources/` inside. SteamCMD uploads the CONTENTS of `dist/workshop/content` (one child). |
| `dist/SoulvizierClassic_CustomMaps.zip` | **Manual/ModDB share artifact** (no-Steam co-op path - see `SHARE_AND_PLAY.md`). |
| `<TQ docs>/CustomMaps/SoulvizierClassic/` | **Local deploy target** (the running game reads here). Full path: `C:/Users/willi/OneDrive/Documents/My Games/Titan Quest - Immortal Throne/CustomMaps/SoulvizierClassic`. |
| Steam Workshop item **3759792705** | **The public listing** (appid 475150). Subscribers download here. `local/workshop_item_id.txt` holds the id. |

`tools/` (Python build pipeline), `scripts/` (PowerShell deploy/package/upload), and `docs/` are the
COMMITTED source of truth. `upstream/` and `reference_mods/` are gitignored source inputs.

---

## 3. CURRENT STATE (build27 + workshop-wrapper-fix, all verified on disk 2026-07-08)

> **DB-lane UPDATE 2026-07-09 (build30.2):** the shipped arz is now the STARTER-CHEST-FIXED
> build30.2 (`work/.../SoulvizierClassic.arz`, 54,658,764 B, md5 `3f60574155d18f24a28658725093d699`;
> record-diff vs build30 `45be22b8` = exactly `tutorialpotionchest.dbr`). Root cause + lesson in
> `BACKLOG.md` -> RESOLVED -> B-STARTER-CHEST. The table below is otherwise build27-era history
> (builds 28/29/30 shipped 07-08/07-09 without this file being refreshed; map lane is at build31b
> in git, not yet uploaded at the time of this note).

**Published Workshop content = build27 canonical.** Verified via fresh steamcmd download; sizes/MD5s
below re-verified against `work/` and the deployed CustomMaps copy on 2026-07-08.

| Artifact | Size (bytes) | MD5 | Notes |
|---|---|---|---|
| `Levels.arc` (canonical) | 688,691,849 | `A1BA5DB2F00FFA067A808753A2E1EAC5` | born-open portals + Toxeus spawn map. `work/.../Levels.arc` == `local/Levels_merged.arc` byte-identical. |
| `SoulvizierClassic.arz` | 54,529,030 | `7C6E209988F0CE815BAF35F058B6A0A8` | sha256 `5014f1903aa4163adaeb8c35fd71ca8fe36db2a7293aa874932660619b600c8f`. Toxeus-spawn fix + born-open invariants + mastery/supra repairs. |
| Workshop package | - | - | exactly **53 files** under one `SoulvizierClassic/` wrapper. |

- **Workshop packaging bug is RESOLVED (2026-07-08, commit `1851203`, tag `workshop-wrapper-fix`).**
  The item root is now a single `SoulvizierClassic/` wrapper (was two broken mods "database" +
  "resources"). `package_workshop.ps1` stages to `dist/workshop/content/SoulvizierClassic/{database,
  resources}`, wipes the stale wrapperless `dist/workshop/SoulvizierClassic` every run, asserts the
  content root has exactly one child, has a **fail-loud TESTHUB MD5 guard** (aborts if the packaged
  `Levels.arc` MD5 == `local/Levels_merged_TESTHUB.arc`), and prints the packaged size + MD5.
  `upload_workshop.ps1` points the vdf `contentfolder` at `dist/workshop/content` and re-asserts the
  single wrapper before uploading. Full recipe: `docs/PLAYBOOK.md` §3.
- **Item is PUBLIC** (`-Visibility 0`). Updates push with:
  `package_workshop.ps1` → `upload_workshop.ps1 -SteamUser trevenaw7 -Update -Visibility 0`
  (steamcmd session cached, no prompts). NEVER upload a TESTHUB artifact.
- **Known content gap (queued, not yet fixed): 8 Text.arc tags render raw** (Blood Toxeus / Crimson
  Verdict names + descriptions). See `BACKLOG.md` → `B-TEXT-TAGS-1`. Fix = coupled arz + Text push.

---

## 4. DEPLOY ASYMMETRY - TESTHUB vs canonical (critical; verified on disk)

Will's LOCAL install runs a **different map** than the Workshop:

- **Workshop / canonical map:** `Levels.arc` `A1BA5DB2…` (688,691,849 B). Co-op-safe (byte-identity).
- **Will's LOCAL CustomMaps map:** the **TESTHUB variant** - `local/Levels_merged_TESTHUB.arc`
  `96A9EB14C88E308E9F850515526C23E4` (688,687,885 B), currently deployed to
  `CustomMaps/SoulvizierClassic/Resources/Levels.arc` (confirmed on disk 2026-07-08). It adds ~20 hub
  portal entities in the Silk Road cave + a Blood Toxeus test spawn at the cave mouth.
- Both run over the **same** build27 arz (`7C6E2099…`, 54,529,030 B) - the arz/Quests/Text are the
  shared coupled build, so only the map differs.
- **TESTHUB is LOCAL-ONLY. No co-op while it is deployed** (MP requires byte-identical maps). It must
  NEVER be uploaded (the packager's TESTHUB guard enforces this).
- **Two entries in Will's in-game map list:** Will is ALSO subscribed to item 3759792705, so his
  "Custom Quest" list shows two `SoulvizierClassic` entries - the subscription copy (canonical,
  under Steam's `steamapps/workshop/content/475150/3759792705/`) and his local TESTHUB (under
  `CustomMaps/`). This is expected; the local CustomMaps copy is the TESTHUB one.

**REVERT the TESTHUB (restore co-op-safe canonical locally):**
```
cp local/Levels_merged.arc "<DEPLOY>/Resources/Levels.arc"   # canonical map
cmp -s local/Levels_merged.arc "<DEPLOY>/Resources/Levels.arc"   # must be byte-identical
```
The arz/Quests/Text need no change (already the shared build). After this, local == Workshop item
and MP is safe. Rolling backups if needed: `local/Levels_deployed_prev.arc`,
`local/Quests_deployed_prev.arc`, `local/db_backups/`, `local/save_backups/`. Recipe also in
`docs/PLAYBOOK.md` §3 (deploy).

---

## 5. OPEN WORK → see docs/BACKLOG.md

`docs/BACKLOG.md` is THE single bug/queue board. Current live-test findings (build27, Will's
2026-07-07/08 sessions), summarized - read BACKLOG for full detail, cause, and fix lane:

- **P0:** `B-PORTAL-1` portals render as flat blue panels (need real mesh/FX); `B-PORTAL-2` a portal
  blocks the walkway (forced teleport); `B-PORTAL-3` return/one-way + all Duister (Secret Place)
  portals broken; `B-SUMMON-1` summons spawn naked / floating-scythe / immobile; `B-TOXEUS-1` Blood
  Toxeus shroud is GREEN, should be RED.
- **P1:** `B-SPRITE-1` pyre sprites do not respawn; `B-TEMPLE-DOOR-1` sealed temple door never unseals
  after the guardian dies; `B-SMOKE-1` region smoke density far below SV.
- **P2 / pending:** `B-CHEST-1` did an Esfri supra formula actually drop? (ask Will); `B-DUISTER-EXPLORE`
  full walk-test of all 5 hub destinations once portals are fixed; `B-TEXT-TAGS-1` the 8 raw tags.
- **Standing queue (not new bugs):** entity contract suite (owns B-SUMMON-1), map contract suite,
  mastery selection-screen recheck, souls quality pass vs SV originals, Toxeus encounter suite,
  dropped-visuals restoration, Cold Tombs (ON HOLD). Cut-by-design areas: `docs/CUT_CONTENT.md`.
- **Workshop feedback:** players report via Workshop comments on item 3759792705 - triage into
  BACKLOG (see its WORKSHOP FEEDBACK section).

---

## 6. STANDING RULES (Will's law - never violate)

- **Implement→vet loop is MANDATORY** for any non-trivial change: independent implementer (Opus max)
  → independent vet (Opus max) that reproduces every claim from raw bytes → re-run until clean.
  Never ship self-vetted work. (Fable is exhausted - all Opus now.) Detail: `docs/PLAYBOOK.md` §0.
- **Commit + tag BEFORE every build Will tests**; roll a backup before every deploy.
- **Deploy couplings (ship together or not at all):** `Levels.arc` + `Quests.arc` when both changed
  (single-letter guarantee + neutralizations); `arz` + `Text.arc` when tags changed; the born-open
  **portal swap couples arz + BOTH maps** (60-byte 0x14 read must stay aligned).
- **TESTHUB artifacts are LOCAL-ONLY**, never Workshop; no co-op while deployed.
- **Occult + Hunting masteries hold Will's HAND-TUNING** - never revert to SV; only fix objectively
  dead refs, reported separately. Content-level changes = proposals to Will only.
- **Souls taste hierarchy:** (a) Will's explicit build-script edit blocks = LAW; (b) SV ORIGINAL
  souls = the design bible for everything generated; (c) more fun/powers welcome if thematically
  coherent. All soul refs must resolve.
- **The campaign ends at Hades (Immortal Throne) for ALL DLC combos** (proven by 256-controller
  sweep). Do not reopen DLC acts. DLC integration = CANCELLED by Will.
- **Never touch `map.dat`. Steam-clean only** (no DLL patches). 6-player MP max (TQAE native).
- **Build gates are fail-loud** - a build that trips any gate does NOT ship: 5 DB invariants
  (soul-leaks, soul-augments, supra-refs, tags, spawn-eligibility) + per-wave map gates
  (verify_merged_bc_navmeshes, entrance_landing_check, engine_corridor_full, cluster_seam_check,
  overcoverage_check, gate_doors_hub, portal-openness). Gate list: `docs/PLAYBOOK.md` §12.

---

## 7. BUILD & DEPLOY - see docs/PLAYBOOK.md

The full, current build/deploy/Workshop command reference is `docs/PLAYBOOK.md` §2–3. Quick pointers:
- Database: `py tools/build_svc_database.py <098i> <0.9> <041> work/.../SoulvizierClassic.arz <TQAE base arz>`
- Text: `py tools/build_text_arc.py <098i Text_EN.arc> work/.../Text.arc work/.../Database/uber_soul_tags.txt`
- Quests: `py tools/build_quest_files.py`
- Map: `py tools/gen_bc_navmeshes.py` then `py tools/svaera_plus_portals.py`
  (`SVC_TEST_HUB=1` env writes the TESTHUB variant to its own file).
- Python: `C:/Users/willi/AppData/Local/Programs/Python/Python312/python.exe`, `PYTHONIOENCODING=utf-8`.
- Deploy local: `scripts/deploy_to_custommaps.ps1`. Package/upload Workshop: `scripts/package_workshop.ps1`
  then `scripts/upload_workshop.ps1 -SteamUser trevenaw7 -Update -Visibility 0`.
- Determinism is your friend: rebuild twice, compare MD5; a vet should reproduce the exact MD5.

---

## 8. WILL'S CHARACTER / SAVE FACTS

Character `_Toxeus` (~lvl 38 Stalker). Save backups: `local/save_backups/*.zip` (+ hash manifests).
The `_ToxeuQ` sandbox copy was DELETED (Steam Cloud quota). Steam Cloud sync errors = quota; never
accept cloud-over-local. Quest adoption on existing characters WORKS (the engine auto-adopts newly
loadable quests; hidden/controller quests never show in the journal - do not misdiagnose from journal
absence). The mod is a total conversion: always use a dedicated Custom-Quest character; never load a
normal character into it or "bounce" a character between mod and base game (corrupts the character).

---

## 9. GOTCHAS / STALE-STATE POINTERS

- The **LIVE** `uber_soul_tags.txt` is `work/SoulvizierClassic/Database/uber_soul_tags.txt`;
  root-level and `local/` copies are STALE DECOYS.
- The game LOCKS `Levels.arc` while running - a `cp` may fail "Device or resource busy"; poll until
  it unlocks to deploy.
- NEVER commit these parked/other-lane strays: `tools/fix_mc_output.py`, `tools/hybrid_merge.py`,
  `tools/create_uber_souls.py`, `tools/populate_svbake_records.py`, `tools/setup_svbake_world.py`,
  `tools/wrl_format.py`, `tools/reconcile_seam_heights.py`, `tools/svaera_plus_portals.py` (has
  uncommitted other-lane changes - coordinate before touching), `tools/debug/gate_doors_hub.py`,
  `docs/blood_cave_walkin_entrance_plan.md`, `docs/BLOOD_TOXEUS_DESIGN.md`, `docs/DOORS_HUB_LOG.md`.
  Stage files explicitly; never `git add -A`.
- The two in-flight contract-suite workflows (entity + map) were STOPPED on hold; their run IDs +
  transcript paths + the full entity-contract-suite spec are preserved in `docs/ARCHIVE_2026-07.md`.
