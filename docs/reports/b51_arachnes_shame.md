# b51 RCA - "Arachne's Shame" (Fetid Lair guaranteed hero spider) absent on Epic

Read-only RCA. No fixes applied. Ground truth: base TQAE `database.arz` + `Levels.arc`,
`upstream/soulvizier_098i` (classic SV = the design bible / "guaranteed" behaviour Will
remembers), our `reference_mods/SVAERA_customquest` map base, and the exact arz + map Will
plays now: `baseline_build38.arz` (== DEV/Steam arz 6631f252) + deployed
`work/SoulvizierClassic/Resources/Levels.arc`.

## TL;DR / VERDICT

**The guaranteed-spawn chain for Arachne's Shame is FULLY INTACT in the shipped build - byte-for-byte
functionally identical (modulo path-casing + one soul-drop LOOT field) to classic SV 0.98i, in both
the arz AND the deployed map.** No DB edit and no map edit of ours broke her guaranteed Epic/Legendary
spawn. Every one of the brief's five hypotheses is refuted with direct evidence.

Because the mechanism is provably a guarantee AND provably intact, her absence in Will's **already-visited**
Epic Fetid Lair is a **persisted-save / baked-instance artifact**, not a systemic break: the Fetid Lair
is a non-resetting Act-1 cave; it was instanced on his Epic character at first visit, when she *did*
spawn (she is guaranteed) - she is almost certainly **already killed** (bosses do not respawn in a baked
instance). A **fresh Epic instance** (new Custom Quest character, or a Fetid Lair that character has not
yet entered on Epic) will show her per the current arz. Recommended action = a **test**, not a code fix
(there is nothing broken to fix; altering the intact guarantee would be a forbidden rebalance).

---

## 1. Her record + the guaranteed spawn chain (per difficulty)

**Identity.** "Arachne's Shame" is SV's rename of the base-game "Black Widow" hero spider:
- Name tag: `tagBlackWidow = Arachne's Shame` (our `modstrings.txt`; base `Text_EN` has no such value).
- Monster record: **`records\creature\monster\typhon\spiderblackwidow01.dbr`**
  - `description = tagBlackWidow`, `monsterClassification = Boss`, `charLevel = 45`, `Class = Monster`.
  - In BASE TQAE this record is an unused stub (`description = "Eight Legged Fiend"`, `charLevel = 1`); SV
    turned it into the L45 Boss.
- Her soul: `tagSoulName491 = {^F}Arachne's Shame Soul`; loot `lootFinger2Item1 = arachnesshame_soul_{n,e,l}`.

**The Fetid Lair.** `tagRegionName178 = "Fetid Lair"`. It is the base-game Greece Act-1 arachnos cave
**`Levels/World/Greece/Area003/UG_ArachnosUnderground/ArachnosUnderground01_Floor0.lvl`** (the ONLY level
in every map that places her proxy; single floor, no Floor1+).

**The guaranteed E/L mechanism (exactly the pattern the brief described).** The Fetid Lair level places a
dedicated proxy that per-difficulty selects a boss pool where she is `spawnMin = spawnMax = 1`:

```
Level ArachnosUnderground01_Floor0.lvl
  places proxy  records\proxies quest\greece\journal\jg06_arachnospool - poisonspring c.dbr  (Class=Proxy)
    difficultyEquationFile = Records\Proxies Boss\HeroDifficulty_01.dbr
    difficultyLimitsFile   = Records\Proxies Boss\HeroLimit_All.dbr    <- E/L gate (allows all)
    pool1          = ...\Greece\JG06_Arachnos_Pool.dbr    (NORMAL: regular arachnos, NO boss)
    poolEpic1      = ...\Greece\JG06_Arachnos_PoolB.dbr   (EPIC:      Arachne's Shame)
    poolLegendary1 = ...\Greece\JG06_Arachnos_PoolB.dbr   (LEGENDARY: Arachne's Shame)
    poolLegendary2 = ...\Greece\JG06_Arachnos_PoolB.dbr
    poolLegendary3 = ...\Greece\JG06_Arachnos_PoolB.dbr
      JG06_Arachnos_PoolB.dbr:
        name1 = ...\typhon\spiderblackwidow01.dbr   weight1 = 10   limit1 = 1
        spawnMin = 1   spawnMax = 1   championChance = 0
        => draws EXACTLY ONE Arachne's Shame, guaranteed, whenever PoolB is used
```

So on **Normal** she cannot appear (pool1 has no boss); on **Epic** the proxy uses `poolEpic1 = PoolB`
and on **Legendary** `poolLegendary1..3 = PoolB` -> **guaranteed Arachne's Shame on E/L, absent on Normal.**
This matches Will's report verbatim ("guaranteed spawn ... on Epic + Legendary, not a chance/hero-roll").

This guarantee is **SV-authored**: base `poisonspring c` had ONLY `pool1` (regular arachnos, all
difficulties). SV added `poolEpic1`/`poolLegendary1..3 = PoolB` + `HeroDifficulty_01`/`HeroLimit_All` onto
the existing base level placement - no map change was needed by SV, just the DB record the base placement
already points at.

---

## 2. DIFF of every chain link: (classic SV098 = correct) vs (BUILD38 = Will's build)

| Chain link | record | SV098 -> BUILD38 real (non-casing) diffs | Intact? |
|---|---|---|---|
| Monster | `typhon\spiderblackwidow01.dbr` | ONLY `chanceToEquipFinger2` 3.0 -> 25.0 (soul-drop **loot** rate). `monsterClassification=Boss`, `charLevel=45`, `skillName2..5`, `specialAttackSkillName`, `lootFinger2Item1` all identical. | YES (spawn-wise) |
| Boss pool | `JG06_Arachnos_PoolB.dbr` | **0** (`name1=spiderblackwidow01`, `weight1=10`, `limit1=1`, `spawnMin=spawnMax=1`, `championChance=0` identical) | YES |
| Normal pool | `JG06_Arachnos_Pool.dbr` | **0** | YES |
| Proxy (E/L gate) | `jg06_arachnospool - poisonspring c.dbr` | **0** (`pool1`/`poolEpic1`/`poolLegendary1..3`, `difficultyEquationFile=HeroDifficulty_01`, `difficultyLimitsFile=HeroLimit_All` identical) | YES |
| E/L limits file | `Proxies Boss\HeroLimit_All.dbr` | **0** (present in mod arz, identical to SV098) | YES |
| Difficulty file | `Proxies Boss\HeroDifficulty_01.dbr` | not in mod arz = unmodified base record, resolves from base game at runtime (mod arz overlays base: 51,007 mod records vs base's 74,013) | YES |
| **Map placement** | `ArachnosUnderground01_Floor0.lvl` | **byte-size identical** (873,443 B, 69 dbr refs) across BASE / SVAERA / our DEPLOYED; DBR-set diff DEPLOYED vs SVAERA = **0 dropped / 0 added**; all three `poisonspring a/b/c` proxies present | YES |

The single functional DB change anywhere in her record is the soul-drop **loot** rate (3% -> 25%), which
has zero bearing on spawning. Everything spawn-relevant is identical to classic SV.

---

## 3. Hypotheses - all REFUTED with evidence

1. **Pool spawnMin/Max/championChance altered / diversity-zeroed (houndmaster crowd-out class).**
   REFUTED. `JG06_Arachnos_PoolB` is 0-diff: `spawnMin=spawnMax=1`, `championChance=0`, single member
   `spiderblackwidow01 @ weight10/limit1`. She is the whole pool; she cannot be crowded out.

2. **Limits-file / charLevel window now excludes Epic (the Hemorrheus limit_area002 clamp).**
   REFUTED. The proxy's `difficultyLimitsFile = HeroLimit_All.dbr` is present in build38 with **0** real
   diffs vs SV098; `poolEpic1`/`poolLegendary1..3` are wired to PoolB; `charLevel=45` unchanged. Nothing
   clamps Epic out.

3. **Enslaver x600 roaming sweep displaced/broke her guaranteed slot.**
   REFUTED. `_sweep_inject_roaming_rare` (apply_svc_patches.py:10504) only touches pools whose path
   starts with `proxies orient\pools`, `proxies egypt\pools`, `proxies greek\`, or `xpack\proxieshades`.
   Her pool is `proxies quest\pools\greece\` - **not** in the allow-list - and her proxy is
   `proxies quest\greece\journal\`. PoolB is 0-diff, confirming the sweep never touched it. (The sweep's
   own comment cites `spiderblackwidow01 @ limit 1` only as a *vanilla precedent* for the `limit=1` idiom.)

4. **Spider soul/loot edit (build36 white-spider / chanceToEquipFinger2 gating) corrupted/declassed her.**
   REFUTED. Full-record diff shows her record differs from SV098 ONLY in `chanceToEquipFinger2` (a LOOT
   field) + path casing. `monsterClassification=Boss` (not declassed), `charLevel=45`, and the entire
   skill kit are identical. The yeti-style non-Hero/Boss zeroing does not touch her (she is Boss). No
   dtype-zero corruption.

5. **skill_quality / boss-kit edit corrupted her.**
   REFUTED. `tools/patches/boss_skill_fix.py` references `spiderblackwidow01` **only in a comment** (as a
   vanilla example of a legitimate chance>0 level-0 special, "venomnova@50%"); its apply/verify roster is
   scoped to the `um_*_99` mod-apex naming convention. She is not in any apply set. Her skills are
   identical to SV098.

**No tool in `tools/` touches her spawn chain.** Grep for `spiderblackwidow` / `jg06_arachnos` /
`poisonspring` / `arachnos_poolb` finds her only in (a) comments, (b) her soul design
(`create_uber_souls.py`, loot), and (c) the global soul-drop-rate wiring (loot). The pool, proxy,
limits file, and map placement all pass through from SV098 unchanged.

---

## 4. Curious-QA - other guaranteed E/L cave/hero bosses (same edit-class sweep)

Swept **all 811** proxies in build38 that use the guaranteed-E/L pattern (`poolEpic*`/`poolLegendary*`)
and diffed each proxy + its referenced pools vs SV098.

- `poisonspring c` (Arachne's Shame): **[OK] / intact** - not among the flagged records.
- 261 proxies show real SV->build38 diffs, but **every one is a TRASH-pack pool** (skeleton, sprite,
  liche, jackalman, antlion, djinnsprite, empusa, cryptwormscarab, iceraptor, gigantes, ...) altered by
  two **intentional global operations**, neither of which removes an existing guaranteed member:
  1. **Enslaver roaming sweep** - appends `name3 = um_toxeus_enslaver_99 @ weight1 / limit1` and scales
     existing member weights x600 (e.g. `weight1/2: 100 -> 60000`).
  2. **Champion-coldworm injection** - `nameChampion1 = records\test\boss_coldworm50.dbr @ weightChampion1=2`
     on cryptworm/bonescarab pools (an intentional mod champion; see note below).
- **No guaranteed single-boss hero pool lost its boss.** No sibling of Arachne's Shame is broken by our
  spawn edits. This corroborates that our global spawn work only *adds* roamers/champions to trash packs.

Low-priority curiosity (out of scope, not a break): `boss_coldworm50` lives in the `records\test\`
namespace yet is shipped as a live champion in Greece/underworld cryptworm+bonescarab pools
(apply_svc_patches.py:1523+). It is intentional mod content that ADDS a champion; worth a glance for
naming hygiene, unrelated to Arachne's Shame.

---

## 5. git-blame / broken_since

**broken_since = N/A - never broken.** The arachnos spawn chain (monster/pool/proxy/limits/placement) was
never modified by any commit; it is inherited verbatim from SV 0.98i (DB) and the base/SVAERA map
(placement). The only her-adjacent edits in our history are her **soul** (design + drop-rate, loot only)
and a `boss_skill_fix` comment. There is therefore no edit to blame for a spawn break, because the spawn
chain in the exact build Will plays equals classic SV.

---

## 6. Persisted-save assessment (brief's explicit caveat - both stated)

- **Systemic-break theory (brief's a-priori primary):** REFUTED by direct, multi-layer evidence above -
  the guarantee is present and intact in `baseline_build38.arz` + the deployed map. On a **fresh** Epic
  Fetid Lair the current build spawns her, guaranteed.
- **Persisted-save theory (now the primary, evidence-led explanation):** TQ bakes a level instance into
  the character save at first visit; Act-1 caves like the Fetid Lair do not reset. Will's Epic character
  visited the Fetid Lair earlier; at that first visit she spawned (guaranteed) and was almost certainly
  **killed** (bosses stay dead in a baked instance) - or the instance is otherwise baked. Re-entering the
  baked instance shows no spider. This fully reconciles "guaranteed" + "absent now" without any systemic
  break.

Note: because the chain was never broken in any of our builds, the alternative
"instance baked while she was bugged-out" sub-case has no supporting evidence.

---

## 7. Fix plan (minimal, evidence-driven; restore = guarantee only, no rebalance)

There is **nothing broken in the arz or map to fix** - the E/L guarantee is correct and already matches
classic SV. The registry/crash/no-rebalance laws all point to **no code change**. The decisive next step
is a **test on a FRESH instance**, sequenced as:

1. **Will test (decider):** on Epic, enter a Fetid Lair his current Epic character has **not yet visited**
   (or roll a new Custom Quest character to Epic and reach the Fetid Lair). Restart Steam + TQ first
   (standing rule) so the current arz/map are loaded.
   - **She appears** -> confirmed persisted-save / working-as-designed. Close. (Optional docs-only: add a
     WILL_TEST_GUIDE line that already-visited caves are save-baked and do not re-roll bosses.)
   - **She does NOT appear on a fresh Epic entry** -> escalate to runtime diagnosis (the static chain says
     she must spawn, so a runtime-only factor would be implicated): live spawn/`ProcessRLTD` probe via the
     existing Frida crash-probe harness, and re-examine the `HeroLimit_All`/difficulty engine behaviour at
     runtime.
2. **Do NOT** "restore" the pool/proxy - they are already correct; editing them is a no-op at best and a
   rebalance (banned) at worst. Making her spawn in an *already-baked* save is not achievable via arz/map
   (a save cannot be un-baked from the DB); it would require a new placement or a quest-spawn = a design
   change, out of RCA scope.

---

## Appendix - evidence artifacts (scratchpad, read-only probes)

- `b51_find.py` / `b51_find2.py` - tag `tagBlackWidow="Arachne's Shame"`, region 178 = Fetid Lair.
- `b51_chain.py` -> `b51_chain.out` - full reference scan; her record + PoolB dumped/diffed (PoolB 0-diff).
- `b51_proxy.py` / `b51_proxyc.py` - proxy `poisonspring c` full field diff (0 real diffs; poolEpic/poolLegendary=PoolB).
- `b51_limits.py` - `HeroLimit_All` 0-diff; `HeroDifficulty_01` base-resolved.
- `b51_map.py` - the proxy is placed only in `ArachnosUnderground01_Floor0.lvl`, present in all 5 maps incl. OUR_DEPLOYED.
- `b51_level.py` -> `b51_level.out` - that level byte-identical base/SVAERA/deployed; 0 placed-object drift vs SVAERA.
- `b51_curious.py` -> `b51_curious.out` - 811 E/L proxies swept; poisonspring c OK; 261 diffs all trash-pack Enslaver/coldworm adds.

---

# ROUND 1 IMPLEMENTER - independent re-verification + fix decision (2026-07-13)

Per the mandatory implement->vet discipline, the implementer did NOT take the RCA on trust. The
guaranteed-spawn chain was re-derived clean-room from the raw arz bytes (fresh scripts, independent
of the RCA out-files) and the "restore the broken link" instruction was tested against the evidence.

## Independent clean-room dry-run replay (`b51_replay.py`)

Loaded BASE / SV098 / BUILD38 arz and resolved the proxy -> pool(s) -> limits -> monster chain
exactly as the engine does, per difficulty. Results (nothing taken on trust):

- **PART A - full field dumps.**
  - `JG06_Arachnos_PoolB` SV098 == BUILD38: `spawnMin=1 spawnMax=1 championChance=0.0`, members =
    exactly one `spiderblackwidow01` (weight 10, limit 1), **zero champions, no Enslaver appended**.
  - `spiderblackwidow01` SV098 == BUILD38: `Class=Monster`, `monsterClassification=Boss`,
    `charLevel=(45,60,73)`, `description=tagBlackWidow`. NOT declassed, NOT dtype-zeroed. (BASE is the
    unused stub: classification=None, charLevel 1, "Eight Legged Fiend".)
- **PART B - path-casing-insensitive functional diff SV098 -> BUILD38, all 5 chain links:**
  proxy = 0, normal pool = 0, boss pool = 0, limits = 0, monster = 1 diff and that one diff is
  `chanceToEquipFinger2` 3.0 -> 25.0 (soul-drop LOOT rate, non-spawn). **Spawn-relevant diffs across
  the entire chain = 0.**
- **PART C - per-difficulty replay yields IDENTICAL verdicts on SV098 and BUILD38:**
  - Normal: **ABSENT** (proxy uses `pool1` = regular orbweaver pool, no boss).
  - Epic: **GUARANTEED (exactly 1 Arachne's Shame)** (proxy uses `poolEpic1` = PoolB; limits window
    [1,75] always covers an Epic player).
  - Legendary: **GUARANTEED (exactly 1 Arachne's Shame)** (`poolLegendary1..3` = PoolB).
  - `OVERALL: chain SV098->BUILD38 spawn-functionally INTACT = True`. This matches Will's report
    verbatim: guaranteed on Epic + Legendary, none on Normal, not a chance/hero-roll.

## Code-ownership grep (who could have broken it)

`grep -niE "spiderblackwidow|jg06_arachnos|poisonspring|arachnos_poolb"` over `tools/` finds her spawn
identifiers ONLY in (a) a comment in the Enslaver sweep citing `spiderblackwidow01 @ limit 1` as a
*vanilla precedent* for the limit=1 idiom, (b) her SOUL design in `create_uber_souls.py` (loot), and
(c) a `boss_skill_fix.py` comment (not in its apply roster). `herolimit_all` appears many times but
only as a **donor path** that other mod bosses (Blood Toxeus, Wyrmhorde, obsidian, neferkha,
polis_vault, toxeus_suite) CLONE to a new record; none mutate the base `herolimit_all.dbr` (PART B: it
is 0-diff). **No code owns or edits her spawn chain**, so there is no "owning code" break to repair.

## Curious-QA sibling sweep (same edit class)

- `b51_siblings.py`: of all 809 SV098 E/L proxies, exactly **1** points at a strict single-member
  guaranteed Boss/Hero/Quest pool (Arachne's `poisonspring c` -> PoolB). It is GUARANTEED-INTACT in
  BUILD38.
- `b51_siblings2.py` (broader): across all 809 E/L proxies, collect every Boss/Hero/Quest-classified
  member in their Epic+Legendary pools, then confirm BUILD38 still contains each. **0 proxies lost a
  boss/hero/quest member.** No sibling guaranteed boss was crowded-out, removed, declassed, or
  unwired by our global spawn edits (the Enslaver x600 sweep / coldworm-champion injection only ADD to
  trash packs). Arachne's Shame is essentially the unique boss of this exact class, and it is intact.

## FIX DECISION - no arz/map/code change (evidence-driven)

The brief's round-1 premise ("restore the broken link the RCA found") does **not** hold: the RCA
found no broken link, and the implementer's independent replay confirms the E/L guarantee is already
present, correct, and byte-functionally identical to classic SV 0.98i. Therefore:

- **No fix is applied.** "Restoring" an already-correct guarantee is a no-op; altering the intact
  pool/proxy/limits/monster would be a forbidden **rebalance / SV-design mutation beyond restoration**
  and would violate the no-rebalance law. The minimal, evidence-driven action is **zero change**.
- **guarantee_restored = already-intact** (verified, not modified): Epic and Legendary each yield
  exactly one guaranteed Arachne's Shame; Normal yields none - as base/SV intended.
- **siblings_fixed = 0**: none broken, none needed fixing.

## The real decider = a FRESH-INSTANCE test (persisted save)

Her absence in Will's **already-visited** Epic Fetid Lair is a persisted-save / baked-instance
artifact (non-resetting Act-1 cave; she spawned guaranteed at first Epic entry and is almost certainly
already killed). No DB/map edit can un-bake a save. **Decider:** on Epic, restart Steam + TQ, then
enter a Fetid Lair the character has NOT yet visited (or a new Custom Quest character on Epic).
- She appears -> confirmed working-as-designed; close.
- She does NOT appear on a fresh Epic entry -> escalate to runtime diagnosis (Frida spawn probe;
  `HeroLimit_All` engine behaviour), since the static chain proves she must spawn.

## Gates (round 1)

`tools/patches/_check_registry.py` -> selfcheck OK (12 modules, order 4c688f58...). `py_compile` of
`apply_svc_patches.py` / `boss_skill_fix.py` / `create_uber_souls.py` -> OK. Working tree carries only
this report edit (no arz/map/tool change). No heavy build (arz probes + replay on read-only copies).

## Round-1 evidence artifacts (scratchpad)

- `b51_replay.py` - clean-room per-difficulty replay; PART A/B/C above.
- `b51_siblings.py` / `b51_siblings2.py` - E/L guaranteed-boss sibling sweeps (0 broken).
