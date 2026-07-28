# b91 - DEEP-CHEST DEVOURER GUARD: the 100% spawn, round 2 (REPEAT REPORT)

**Branch** `fix/devourer-chest` (worktree `.claude/worktrees/devourer-chest`, base `main` @ `255b86c` = build50)
**Date** 2026-07-28
**Scope** DB only (arz + Text coupled pair) + a new whole-chain map contract. `Levels.arc` / `Quests.arc` untouched, hash-proven.

---

## 1. WILL'S REPORT (2026-07-27, verbatim)

> "toxeus the murderer devourer of blood is not spawning at the proper location next to his chest in
> the blood cave even though we said he should have a 100% spawn rate there in the existing spawn
> pool that is there"

This is a **REPEAT** of the b79 report (2026-07-16). Ruling **R-3** (Toxeus arc). DONE-MEANS-DONE:
fixed exhaustively, with a permanent gate, not triaged into follow-up.

---

## 2. GROUND TRUTH IN THE DEPLOYED ARTIFACTS

Everything below was decoded from the bytes Will actually plays, not from source:

* DEV arz `SoulvizierClassicDEV.arz` md5 `c1a8fa2aee5e6eb88b641b28d7dc6ae4`
* DEV `Levels.arc` md5 `943d0ab9516d332db79bd7f9fd2d3ffe` (build49 TESTHUB)
* DEV `Text.arc` `fcca4927...`, `Quests.arc` `5e664c7b...`

### (a) The map instance next to the chest - INTACT

Whole-map scan of all 2282 levels with the version-aware 0x05 parser (72-byte records on blob
version 0x11/0x0f, 56 otherwise, plus the 16-byte UniqueId on flagged instances):

| record | placements map-wide | level | local position |
|---|---|---|---|
| `records\drxitem\container\proxy_hidden_bloodcave_chest.dbr` (the renamed hidden chest) | **1** | `Levels/World/xBloodCave/drxBC2.lvl` | `(9.13, 28.00, 137.14)` |
| `records\drxmap\proxy\egg_blooddragon_pack.dbr` (the guard) | **1** | `Levels/World/xBloodCave/drxBC2.lvl` | `(13.17, 28.00, 136.06)` |

**4.20u apart.** Exactly one of each, in the same level, adjacent. The M15 "existing spawn group"
architecture is present and correct on the shipped map.

> Parchment control (R-1/R-2, a DIFFERENT axis - not touched by this lane): the same corrected scan
> finds `records\drxmap\proxy\q_bloodtoxeus_ambush.dbr` placed **once**, in
> `drxFirstxistion_connection.lvl` @ `(36.00, 10.005, 19.50)`, 4u from `finalletter` @
> `(32.46, 10.005, 17.59)`. The b79 relocation IS deployed. No parchment regression; nothing in this
> lane changes `chanceToRun` or any parchment record.

### (b) The proxy -> pool -> monster chain, as it SHIPPED (pre-b91)

```
records\drxmap\proxy\egg_blooddragon_pack.dbr        [Proxy]
    pool1                 = records\drxmap\proxy\pools\egg_blooddragon.dbr   (weight1 = 10, the only pool)
    difficultyEquationFile= records\proxies orient\difficulty_04.dbr
    difficultyLimitsFile  = records\proxies orient\limit_area002.dbr    <-- DEFECT 2
    placementExtents      = 3.5     chanceToRun = (absent)

records\drxmap\proxy\pools\egg_blooddragon.dbr       [ProxyPool.tpl]
    spawnMin = spawnMax   = 4
    name1/2/3             = records\drxcreatures\blooddragons\blooddragon01.dbr   (Champion, charLevel [40,56,71])
    weight1/2/3           = 100
    championChance        = 100.0
    championMin           = 1      (b79's fix landed: it IS 1 in the shipped bytes)
    championMax           = 1
    nameChampion1         = records\xpack\...\um_bloodtoxeus_99.dbr     <-- DEFECT 1 (Boss, charLevel [40,68,100])
    weightChampion1       = 100
    proxyPoolEquation     = ''      (neutralized, correct)
```

Exactly ONE proxy in the whole 51,085-record DB references this pool. So the b79 field fix shipped,
the placement shipped, and the Devourer still did not appear.

### (c) Difficulty / act / quest / one-shot gates

`quest = 0` on the proxy; no quest condition, no act gate, no "already spawned" flag anywhere on the
chain. The only difficulty-sensitive element is the proxy's `difficultyLimitsFile` (defect 2 below).

---

## 3. ROOT CAUSE (the proven chain failure)

**b79 fixed a FIELD inside the wrong SHAPE.** The chain was wired end to end, but the Devourer sat in
the pool's CHAMPION slot, and the shipped data proves that is not how a guaranteed boss is built: of
the 1,845 ProxyPools in the DB, **624 put a `monsterClassification=Boss` monster in a MAIN (`nameN`)
slot** - that is the shape every guaranteed boss uses, including this mod's own `q_leinth_lone`,
`q_vashkarr_lone`, the whole `q_yard_*` set, and `q_bloodtoxeus_lone` (`_BT_POOL`) for this very
monster - while all **90 Boss-in-champion pools are the base game's rare "uber monster" lottery**
(73 of them at `championMin=0`; every one of the 17 with `championMin>=1` lists the boss ALONGSIDE
3-4 non-boss champions, so the floor guarantees *a* champion, never *that* boss). Before b91,
`egg_blooddragon` was the **only pool in 51,085 records making a Boss the SOLE champion entry** - a
shape with zero precedent anywhere in the shipped data.

**The repo's own fail-loud gate already encoded this law and was never pointed at the chest guard.**
`apply_svc_patches._verify_mod_spawn_proxies_eligible` asserts (A) the boss is in a `nameN` slot with
`spawnMax - championMax >= 1`, and (B) the proxy's limit window contains his `charLevel` on N/E/L -
but it only walks `_MOD_AUTHORED_SPAWN_PROXIES`, and the chest guard (a mod-authored construction on
a NATIVE DRX proxy/pool pair) was never registered there. Had it been, the build would have failed
LOUD since M15 (2026-07-09) on BOTH shipped defects: the Devourer is in **no** `nameN` slot, and
`egg_blooddragon_pack` still carried `limit_area002`, the area-TRASH window (`N[23-26] E[38-51]
L[60-65]`) that tops out below his `charLevel [40,68,100]` on **every** difficulty - the exact
condition `docs/BLOOD_TOXEUS_DESIGN.md` section 5 says forces the no-cap boss limits file
(`limit_bloodtoxeus`, `[1..110]`) on every proxy that spawns him. The chest guard was the one
Devourer surface still on the trash limit.

### Candidate causes enumerated and killed with evidence

| candidate | verdict | evidence |
|---|---|---|
| b79's `championMin` fix never shipped | **KILLED** | deployed arz `c1a8fa2a` carries `championMin=1` |
| the map placement was lost / never rebuilt | **KILLED** | whole-map scan: chest x1 + guard x1 in `drxBC2`, 4.20u apart |
| the placed instance points at a DIFFERENT (old) pool record | **KILLED** | instance -> `egg_blooddragon_pack`; its only `pool1` -> `egg_blooddragon`; that record carries the Toxeus wiring |
| the fix lives in a record that is not the one placed | **KILLED** | exactly 1 referencing proxy in 51,085 records, exactly 1 placement map-wide |
| a later pipeline writer stomps the value | **KILLED** | `egg_blooddragon` has exactly ONE writer in the whole pipeline (`_apply_m15_toxeus_group_joins`), and the deployed bytes match its intent |
| TESTHUB-only / canonical-only placement | **KILLED** | the placement is in the canonical `drxBC2`, present in the deployed DEV TESTHUB map |
| `proxyPoolEquation` rescaling the counts | **KILLED** | `proxyPoolEquation = ''` in the shipped bytes |
| act / quest / difficulty / one-shot gate | **KILLED** | `quest=0`, no quest condition or spawned-flag on the chain |
| pool math: the champion slot is not reachable for a Boss at 100% | **SUSPECTED (defect 1) - precedent, NOT proven mechanism** | no shipped pool uses this shape (28 sole-champion-Boss pools, exactly 1 with championMin>=1 = ours); under the repo's own documented semantics the old shape SHOULD have worked, and this report does not explain why it did not |
| the proxy's limit window sits below the boss's level | **THE CAUSE (defect 2)** | `limit_area002` max `26/51/65` vs `charLevel [40,68,100]`; the repo's own eligibility gate treats this as a fail |
| Will's SAVE has the area baked | see section 6 - not the cause, but it does gate what he will see |

---

## 4. THE FIX (pipeline level, BL-103)

`tools/apply_svc_patches.py :: _apply_m15_toxeus_group_joins` - rebuilt to the PROVEN
guaranteed-boss construction, deriving the escorts from the pool's own native mains so the roster is
preserved rather than invented:

| field | before (shipped) | after (b91) |
|---|---|---|
| `name1/2/3` | `blooddragon01` x3 | **`um_bloodtoxeus_99` x3 (the MAIN)** |
| `weight1/2/3` | 100 | 100 |
| `nameChampion1/2/3` | `um_bloodtoxeus_99`, -, - | **`blooddragon01` x3 (the escorts)** |
| `weightChampion1/2/3` | 100, -, - | 100, 100, 100 |
| `championChance` | 100.0 | 100.0 |
| `championMin` / `championMax` | 1 / 1 | **3 / 3** |
| `spawnMin` / `spawnMax` | 4 / 4 | 4 / 4 (untouched) |
| `proxyPoolEquation` | `''` | `''` |
| proxy `difficultyLimitsFile` | `limit_area002` (`N26/E51/L65`) | **`limit_bloodtoxeus` (`[1..110]` N/E/L)** |

Guaranteed mains = `spawnMax - championMax` = `4 - 3` = **exactly 1 Devourer + 3 blood dragons, every
run, at every party size 1..6** (the equation stays neutralized, so the literal counts hold). This is
the same construction as `_BT_POOL` (`spawnMax=3`, `championMin=championMax=2` -> 1 Devourer + 2 blood
demons), scaled to the chest group of 4. **The encounter Will designed is unchanged**: the same single
native proxy, the same spot 4.2u from the chest, the same 1 Devourer + 3 blood dragons. Only which
slot the Devourer occupies changed, from the never-guaranteed champion slot to the guaranteed main
slot.

Scoping proof for the proxy edit: `egg_blooddragon_pack` is placed EXACTLY ONCE map-wide and is the
ONLY proxy referencing this pool, so both edits touch this one encounter and nothing else in the game.

**Registered in `_MOD_AUTHORED_SPAWN_PROXIES`** (44 proxies now, was 43), so the pre-existing
fail-loud invariants (main-in-name-slot, champion-crowd-out, limit-window containment,
equation-neutralized via `_svc_lock_authored_pool_counts`) cover the chest guard permanently.

The Part D champion-count cap (`toxeus_suite._verify_toxeus_champion_cap`) re-derives its roster from
the db and still bounds the chest guard at `<= 1` Devourer: build log
`[D] champion-count-cap invariant OK: 2 Blood-Toxeus pool(s) ... each surface <= 1 Toxeus at any party
size 1-6`.

---

## 5. THE GATE (no-new-surface law)

New contract **`MAP-CHESTGUARD-1`** (P0), `tools/contracts/contracts_map.py::contract_chest_guard`.
It asserts the WHOLE chain over the SHIPPED artifacts (built map + built arz), not one field:

1. the hidden chest is placed **exactly once**;
2. the guard proxy is placed **exactly once**, in the **same level**, within **12u** of the chest;
3. proxy -> `pool1` -> the Devourer record all **resolve** in the arz;
4. the Devourer is a **weighted MAIN (`nameN`) entry**, no foreign monster in the main slots, and
   guaranteed mains = `spawnMax - championMax` == **exactly 1** with `championChance > 0`
   (effective spawn probability **100%**, exactly one Devourer);
5. `proxyPoolEquation` is neutralized, so those literal counts hold at every party size;
6. the proxy's limit window **contains** his `charLevel` on Normal/Epic/Legendary.

**Planted negative tests** (`tools/contracts/_negtest_map.py::test_chest_guard`, 7 checks, all PASS):
compliant b91 shape -> silent; then it fires on (1) the Devourer demoted to champion-only **which is
the exact shape that shipped and did not spawn**, (2) champion crowd-out (0 guaranteed mains),
(3) >1 guaranteed Devourer, (4) `proxyPoolEquation` restored, (5) the guard proxy not placed,
(6) an area-trash limit window below his charLevel. Full suite: **43/43 checks PASS**.

**Real-world negative proof (better than synthetic):** running the map contracts against the
**actually deployed pre-b91 artifacts** exits **1** and reports exactly the two defects this report
diagnoses:

```
P0  MAP-CHESTGUARD-1  the Devourer is not a weighted MAIN (nameN) entry of the guard pool ...
      - records\drxmap\proxy\pools\egg_blooddragon.dbr
P1  MAP-CHESTGUARD-1 x3  Normal/Epic/Legendary: the guard proxy's limit window tops out below
                          the Devourer's authored level ...
      - records\drxmap\proxy\egg_blooddragon_pack.dbr
```

and the same command against the b91 build **PASSES** (0 P0 / 0 P1).

---

## 6. SAVE IMPACT - what Will must do to see it

**TQ persists per-character, per-difficulty map state, and the blood cave's chest room is inside
that state.** Two independent things matter:

1. **The DB change only takes effect on a spawn that has not happened yet.** A monster group already
   instantiated in Will's save keeps whatever it rolled at first entry. The chest room is a
   *dungeon interior* - if his character has already cleared/visited it on that difficulty, the
   already-resolved group can persist.
2. **The chest itself is one-shot.** `proxy_hidden_bloodcave_chest` is a container; once opened it
   stays opened for that character. Opening the chest is not the test - the Devourer standing next
   to it is.

**How Will tells the difference (in order of cost):**

* **Cheapest reliable test:** kill TQ + Steam, restart, load a character, and enter the blood-cave
  chest room **on a difficulty he has NOT yet cleared it on** (e.g. Epic if he has only done Normal).
  The Devourer must be there, next to the chest, with 3 blood dragons - 100%, first entry.
* **On a fresh character** (or `SoulvizierClassicDEV2`, the fresh-char surface): walk the cave to the
  deep chest room. Guaranteed.
* **On his existing character, same difficulty, room already visited:** if the Devourer is absent
  there but present on a fresh visit, that is the SAVE, not the mod. That is the discriminator.
* Either way: **restart Steam + TQ before testing** (standing rule - the running game holds mod files
  in memory) and confirm the mod entry is `SoulvizierClassicDEV`.

Note the diagnosis does not *depend* on the save question: the shipped pool could not guarantee the
Devourer to any character, on any save, on any visit. The save only decides how quickly Will sees the
fix.

---

## 7. BUILD + VERIFY

Build: `PYTHONHASHSEED=0 SVC_RELEASE_DROPS=1 py tools/build_svc_database.py <098i> <0.9> <041>
scratch_b91/SoulvizierClassic.arz <TQAE base>` - **exit 0**, every fail-loud gate green.

Key build-log lines:

```
M15/b91 chest room: egg_blooddragon pool -> GUARANTEED-BOSS shape (name1..3 = um_bloodtoxeus_99 MAIN,
  3 blood-dragon champion escorts, championChance=100 championMin=championMax=3, spawnMax=4 ->
  exactly 1 Devourer + 3 dragons every run, 1..6P); proxy difficultyLimitsFile -> limit_bloodtoxeus
  [1..110] (was the area-trash limit_area002 ...)
Spawn-eligibility invariant OK: 44 mod-authored spawn proxy(ies) spawn their boss on N/E/L with adds.
[D] champion-count-cap invariant OK: 2 Blood-Toxeus pool(s) ... each surface <= 1 Toxeus at any party size 1-6
```

Text: `py tools/build_text_arc.py <098i Text_EN.arc> scratch_b91/Text.arc scratch_b91/uber_soul_tags.txt`
- exit 0, built from the **BUILD-EMITTED** manifest (`49b6d85ba15236aa5df60f610e3a7bf0`, byte-identical
to the shipped one), Text bytes therefore unchanged.

### Record-diff vs the DEPLOYED baseline (`c1a8fa2a`, = `work/.../SoulvizierClassic.arz`)

```
ADDED 0   REMOVED 0   MODIFIED 2
  ~ records\drxmap\proxy\egg_blooddragon_pack.dbr  (1 field)
      difficultyLimitsFile: limit_area002 -> limit_bloodtoxeus
  ~ records\drxmap\proxy\pools\egg_blooddragon.dbr (11 fields)
      FileDescription, championMin 1->3, championMax 1->3,
      name1/2/3 blooddragon01 -> um_bloodtoxeus_99,
      nameChampion1 um_bloodtoxeus_99 -> blooddragon01,
      nameChampion2/3 (new) blooddragon01, weightChampion2/3 (new) 100
```

**Exactly the intended records, nothing else.** Since the baseline was produced by an earlier run of
the same pipeline, this diff doubles as a determinism proof of the whole DB build.

| gate | result |
|---|---|
| DB build (all fail-loud invariants) | **exit 0** |
| `validate_tags.py` | **PASS** (356/356 referenced, 417/417 authoritative; the 2 known base/SV `tagNewMonster*` WARNs unchanged) |
| A7 Occult/Hunting golden (arz + Text) | **PASS** (84 / 90 waived, 0 other) |
| b77 unlock-alignment | **PASS** |
| `_negtest_map.py` | **43/43 PASS** (7 new chest-guard checks) |
| contracts `--only map` on the b91 build + DEV map | **GATE PASS** (0 P0 / 0 P1 / 3 P2, all pre-existing portal P2s) |
| contracts `--only map` on the pre-b91 DEPLOYED artifacts | **exit 1**, `MAP-CHESTGUARD-1` P0 + 3x P1 (the real-world planted negative) |

### Hashes

| artifact | md5 |
|---|---|
| built arz (NEW) | `1c27d5fa650b5c076696db4ad379672f` |
| built `Text.arc` | `fcca49277b9d31ed451e4a6843898843` (**unchanged bytes**) |
| build-emitted `uber_soul_tags.txt` | `49b6d85ba15236aa5df60f610e3a7bf0` |
| baseline arz (pre-change = what was deployed) | `c1a8fa2aee5e6eb88b641b28d7dc6ae4` |

---

## 8. DEPLOY (DEV)

Target `CustomMaps\SoulvizierClassicDEV`. **Coupling used: arz + Text ship as a pair; the map lane was
not touched, so `Levels.arc` (build49 TESTHUB) and `Quests.arc` stay exactly as they were.** Text.arc
rebuilt to byte-identical output, so per the standing "verify unchanged, do not touch" rule it was
verified in place rather than recopied.

Pre-deploy backups: `local/db_backups/SoulvizierClassicDEV_pre-b91_c1a8fa2a.arz` and
`local/b91_work_arz_prev.arz` (both `c1a8fa2a`).

| DEV file | md5 after deploy | proof |
|---|---|---|
| `Database/SoulvizierClassicDEV.arz` | `1c27d5fa650b5c076696db4ad379672f` | **== built arz** |
| `Resources/Text.arc` | `fcca49277b9d31ed451e4a6843898843` | **== built Text.arc** (bytes unchanged) |
| `Resources/Levels.arc` | `943d0ab9516d332db79bd7f9fd2d3ffe` | **UNTOUCHED** (still build49 TESTHUB) |
| `Resources/Quests.arc` | `5e664c7b190965fd69f6ff15d77d85e4` | **UNTOUCHED** |

`work/SoulvizierClassic/` staged to match (`Levels.arc` `fc0adcc0...` canonical + `Quests.arc`
`5e664c7b...` both unchanged).

**In-arz re-probe of the DEPLOYED file:**

```
records\drxmap\proxy\egg_blooddragon_pack.dbr
    pool1                = records\drxmap\proxy\pools\egg_blooddragon.dbr
    difficultyLimitsFile = records\proxies orient\limit_bloodtoxeus.dbr
records\drxmap\proxy\pools\egg_blooddragon.dbr
    name1/2/3        = um_bloodtoxeus_99   weight1/2/3 = 100
    nameChampion1/2/3= blooddragon01       weightChampion1/2/3 = 100
    championChance   = 100.0   championMin = 3   championMax = 3
    spawnMin = spawnMax = 4    proxyPoolEquation = ''
```

TQ was NOT running at deploy time (Steam client only, untouched). **Will must kill TQ + Steam and
restart before testing.**

---

## 9. LEDGER

`docs/WILL_RULINGS.md`:
* **R-3** PENDING -> **IMPLEMENTED b91** with the corrected cause (the ruling's own hypothesis - the
  `q_bloodtoxeus_lone_50` retirement - was already reconciled as wrong in b79; b79's replacement
  hypothesis, `championMin=0`, is now also proven insufficient: the true cause is the boss occupying
  a champion slot at all, plus the area-trash limit window).
* **R-49** appended: Will's verbatim 2026-07-27 repeat report.
* R-1 / R-2 / R-13 (parchment axis) untouched and verified un-regressed in section 2(a).

---

## 10. DEBT REGISTER (standing law 4)

1. **BL-b91-DEBT-1 - in-game confirmation is launch-gated.** Only Will can confirm the Devourer now
   stands by the chest. Section 6 gives the discriminating test (fresh difficulty / fresh character).
2. **BL-b91-DEBT-2 - Steam/canonical not shipped.** This is a DEV-only arz deploy (`build51-dev`).
   The Workshop build still carries the champion-slot chest guard; promote after Will confirms.
3. **BL-b91-DEBT-3 - the chest guard's blood dragons now scale on the `[1..110]` window** instead of
   the `limit_area002` `N26/E51/L65` clamp, because proxy limits are per-proxy, not per-monster. That
   is the intended consequence of un-diluting the superboss and matches every other Devourer surface;
   flag for Will if the 3 escorts feel too strong on Normal.
4. **BL-b91-DEBT-4 - other NATIVE proxies carrying mod-authored spawns are still unregistered.**
   `egg_blooddragon_pack` was found only because Will reported it twice. A sweep should enumerate
   every native proxy/pool the pipeline edits and register each in `_MOD_AUTHORED_SPAWN_PROXIES`.
