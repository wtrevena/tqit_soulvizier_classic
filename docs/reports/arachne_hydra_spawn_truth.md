# ARACHNE + HYDRA spawn truth - independent verifier (2026-07-14)

Read-only, clean-room re-derivation from raw bytes. Does NOT trust b51 or the E/L audit; every
claim below was re-computed from the build40 arz (`work/.../SoulvizierClassic.arz` md5
`b33c5a44...`), the base game arz/map, `upstream/soulvizier_098i`, the DEPLOYED DEV/DEV2/canonical
maps, and Will's live `_Toxeus` character save. Worktree `feat/arachne-hydra-truth` @ `e993a33`.

Will's question (paraphrased): "b51 + the E/L audit both say Arachne's spawn is byte-identical to
SV098 and her placement is present, yet she did NOT appear on my Epic playthrough. How can she be
intact yet absent? Did I test a wrong version? And check the HYDRA too (another Legendary-only
monster, Athens swamps)."

---

## TL;DR / VERDICT

- **HYDRA is genuinely, provably Legendary-ONLY, and Will could NOT have seen her on anything he has
  played.** Her gate proxy has NO Normal pool and NO Epic pool; only `poolLegendary1 = BossPool_24_Hydra`.
  On Normal/Epic the Athens arena is filled by separate "normal only fodder" skeleton/harpy proxies
  (which explicitly point their `poolLegendary1` at `EmptyPool` so they vanish on Legendary). Will's
  save has **only Normal + Epic instances (no Legendary folder at all)** and his fog-of-war shows he
  **never even entered Athens on Epic**. So Hydra was doubly unreachable. This is 100% stock base-game
  behavior, unchanged by the mod. **Not a bug, not a version issue.**

- **ARACHNE's Shame is intact AND Epic-guaranteed (NOT Legendary-only), and it is NOT a version
  issue.** Re-derived from the build40 bytes: on **Epic** the proxy uses `poolEpic1 = PoolB =
  spiderblackwidow01` (Boss, guaranteed single spawn); the player-level window is `[1,75]` on all
  difficulties, so Epic is not clamped out. Her proxy is **placed as a real 0x05 entity** in the exact
  DEV map Will played. The DEV arz is **byte-identical (md5 `b33c5a44`) to canonical build40**. So on a
  **fresh** Epic instance she spawns, guaranteed. Every DEV build he ran (38a/39/40) carries this same
  intact chain + placement.

- **Why she was absent on HIS Epic save is a per-character SAVE-STATE artifact, not a current-build
  defect - and I will NOT hand-wave the mechanism.** His fog-of-war proves he DID explore the Fetid
  Lair on Epic (at level 52, ~65h playtime, i.e. very over-leveled for Epic Act 1), and he does NOT
  carry Arachne's Shame's soul. But the exact reason she isn't there **cannot be proven from the save
  files**, because TQ stores **no decodable per-level monster/kill record** anywhere in the save (only
  fog-of-war, quest-trigger state, spawn position, and the character itself). The repeatedly-asserted
  "save-baking bakes the monster spawn" explanation has **never been proven** and I could not prove it
  either; the repo's own leave-and-return respawn model is still an open empirical question
  (`docs/BACKLOG.md` B-SPRITE-1). **We should stop stating "save-baking" as established fact.** The
  only way to get ground truth is a controlled in-game test on a FRESH Epic instance (details in sec 6).

### Gates
| gate | value |
|---|---|
| `arachne_proxy_placed` | **YES** - `jg06_arachnospool - poisonspring c` is a placed 0x05 entity in `ArachnosUnderground01_Floor0.lvl` in DEV (played), DEV2, canonical, and base (68 instances, byte-identical blob) |
| `arachne_gate_resolves` | **YES (Epic + Legendary guaranteed)** - `poolEpic1`/`poolLegendary1..3 = JG06_Arachnos_PoolB = spiderblackwidow01` (Boss, weight10/limit1, spawn 1); limits window `[1,75]` all difficulties; NOT on Normal |
| `hydra_level` | `Levels/World/Greece/Athens/Area02_Athens01.lvl` (gate proxy `records\proxies boss\boss\bossproxy_25_hydra.dbr`, placed as 0x05) |
| `hydra_true_gating` | **Legendary-ONLY** - proxy has no Normal/Epic pool; only `poolLegendary1 = BossPool_24_Hydra` (`boss_hydra_60/63/66`, Boss). Athens Normal/Epic filled by `Normal Only Fodder\hydra_skeleton_*`/`hydra_harpycrow_*` whose `poolLegendary1 = EmptyPool` (so fodder vanishes and only the Hydra remains on Legendary) |
| `hydra_present` | **YES** - proxy placed in Athens Area02 0x05 (DEV/DEV2/canon/base); chain intact via overlay (`boss_hydra_60/63/66` still `Boss` in build40; `BossPool_24_Hydra` unchanged) |
| `any_runtime_gate_failure_found` | **NONE FOUND (statically).** No difficulty/limits/pool gate excludes Arachne from Epic or breaks Hydra's Legendary spawn. Static analysis cannot observe runtime; a fresh-instance test is required to rule out a runtime-only factor |

---

## 1. HYDRA - definitive, and it clears Will completely

The audit's proxy path (`records\proxies boss\bossproxy_25_hydra.dbr`) was **wrong** (missing the
`boss\` subfolder). The real gate is `records\proxies boss\boss\bossproxy_25_hydra.dbr` (base
pass-through; the mod does not ship its own copy, so it resolves from base unchanged). Re-derived:

```
bossproxy_25_hydra.dbr  (Class=Proxy, difficultyLimitsFile=Limit_Area007)
  NORMAL pools     : (none)          -> spawns nothing from this proxy
  EPIC pools       : (none)          -> spawns nothing from this proxy
  poolLegendary1   : BossPool_24_Hydra -> name1/2/3 = BOSS_Hydra_60/63/66 (all monsterClassification=Boss, weight10)
  Limit_Area007    : Normal[13,16]  Epic[41,51]  Legendary[65,73]
```

Semantics (verified against the fodder pattern below, and against the whole base game, where the
vast majority of proxies define only `pool1..N` yet spawn on all three difficulties): an **undefined**
`poolEpic*`/`poolLegendary*` set falls back to `pool1..N`; a **defined** one replaces it. Hydra's proxy
has neither Normal nor Epic pools, so on Normal/Epic it draws from nothing -> **no Hydra**; on
Legendary `poolLegendary1` supplies the guaranteed boss. Hence **Hydra spawns ONLY on Legendary.**

What fills Athens Area02 on Normal/Epic is a separate set of proxies in the same level:
`records\proxies boss\normal only fodder\hydra_skeleton_02n/03n\...` and `hydra_harpycrow_01n\...`.
Each has `pool1..3` = skeletons/harpies (used on Normal + Epic via fallback) and, tellingly,
`poolLegendary1 = Records\Proxies Boss\Normal Only Fodder\EmptyPool.dbr`. The designers explicitly
route the fodder to an EmptyPool on Legendary so it **disappears**, leaving only the real Hydra. This
is the textbook TQ boss-arena gate and it is fully intact in our build. (Side note: our Enslaver
roaming sweep injected `um_toxeus_enslaver_99 @ weight1/limit1` into those Athens skeleton fodder
pools - an ADD, it removes nothing.)

**Will could not have seen the Hydra:**
- His `_Toxeus` save has difficulty folders **`Normal` and `Epic` only - no `Legendary`** (he has never
  played Legendary).
- His **Epic fog-of-war has ZERO Athens entries** - he has not even reached Athens on Epic (he is
  mid-Act-1, all-Greece: 130 Greece levels, 0 Egypt/Orient).
- On **Normal** he did explore Athens (37 Athens levels incl. `area02_athens01`), but Hydra is
  Legendary-only, so she was correctly absent there too.
- His inventory carries **no Hydra soul**.

Conclusion: Hydra is working exactly as base TQ intends. Nothing to fix, no version issue. If Will
wants to fight her, he must reach **Athens on LEGENDARY**.

---

## 2. ARACHNE's Shame - intact, Epic-guaranteed, and NOT a version issue

### 2.1 The spawn chain, re-derived from build40 bytes (overlay = build40-over-base)

```
Level  ArachnosUnderground01_Floor0.lvl ("Fetid Lair")  places 0x05 proxy:
  records\proxies quest\greece\journal\jg06_arachnospool - poisonspring c.dbr
    difficultyEquationFile = Proxies Boss\HeroDifficulty_01  (averagePlayerLevel*1)
    difficultyLimitsFile   = Proxies Boss\HeroLimit_All      (min 1 / max 75 on Normal, Epic AND Legendary)
    pool1          = JG06_Arachnos_Pool  (NORMAL: jg6_orbedweaver_05/07/09 Champions + arachnos overseers - NO boss)
    poolEpic1      = JG06_Arachnos_PoolB (EPIC:      spiderblackwidow01 - Boss)
    poolLegendary1 = JG06_Arachnos_PoolB (LEGENDARY: spiderblackwidow01 - Boss)
    poolLegendary2 = JG06_Arachnos_PoolB
    poolLegendary3 = JG06_Arachnos_PoolB
      JG06_Arachnos_PoolB: name1 = spiderblackwidow01, weight1=10, limit1=1  (single-member => guaranteed 1)
        spiderblackwidow01 (build40): Class=Monster, monsterClassification=Boss, charLevel=[45,60,73], desc=tagBlackWidow
```

So: **Normal -> she cannot appear** (pool1 = orbweavers, no boss). **Epic -> guaranteed exactly one
Arachne's Shame** (poolEpic1 = PoolB). **Legendary -> guaranteed** (poolLegendary1..3 = PoolB). The
`[1,75]` player-level window covers any Epic character, so **Epic is not clamped out**. This matches
Will's memory ("guaranteed on Epic + Legendary, not a chance roll") verbatim.

This guarantee is **entirely a Soulvizier addition** delivered via the mod's arz: the **BASE** proxy
has ONLY `pool1` (orbweavers) - no `poolEpic`, no `poolLegendary`, i.e. base spawns NO Arachne on any
difficulty. SV098 (and build40, byte-identical for spawn purposes) add the Epic/Legendary boss pools.
So her Epic spawn **requires the mod's arz override to be loaded** (relevant to sec 4).

### 2.2 She is NOT Legendary-only (unlike Hydra)

Directly contrasting the two: Arachne has a **defined `poolEpic1`** (= the boss), so Epic uses it;
Hydra has **no `poolEpic`** and no Normal pool, so Hydra is Legendary-only. Arachne is **Epic +
Legendary**. Will played Epic, so she was supposed to be there.

### 2.3 Placement is intact in the exact map he played

Parsing the 0x05 (objects) section of `ArachnosUnderground01_Floor0.lvl` in every map:

| map | proxy placed in 0x05? | 0x05 instance count | blob |
|---|---|---|---|
| **DEV (the one he played)** | **YES** | 68 | 873,443 B |
| DEV2 | YES | 68 | 873,443 B |
| canonical (`work/`) | YES | 68 | 873,443 B |
| base game | YES | 68 | 873,443 B |
| SV098 | YES | 70 | (SV's own copy) |

The Fetid Lair level is base-native (SVAERA preserved it); DEV/DEV2/canonical/base blobs are
byte-identical (68 instances). Her proxy is a genuine placed entity, not merely a DB record. **Not a
merge-drop** (contrast Aniketos, which the E/L audit correctly found dropped).

### 2.4 Version question - REFUTED

- The DEV arz he played (`CustomMaps\SoulvizierClassicDEV\Database\SoulvizierClassicDEV.arz`) is
  **md5 `b33c5a44...` = byte-identical to canonical build40** (`work/.../SoulvizierClassic.arz`). Same
  intact chain.
- His active Epic `map.dat` records `modName = SoulvizierClassicDEV`, `mapPath = Levels/world/world01.map`.
- DEV and DEV2 place the proxy identically (both 68-instance, byte-identical to base).
- b51 established (and this re-derivation agrees) the arachnos chain was never modified by any commit;
  it is inherited verbatim from SV 0.98i. So **every DEV build he has run - build38a-dev / build39-dev /
  build40-dev - carries the same intact chain + placement**. A version switch would not change her
  presence. **It is not a wrong-version problem.**

---

## 3. The save evidence (what his `_Toxeus` actually shows)

Character: `_Toxeus`, level **52**, ~**64.8 h** playtime (`playTimeInSeconds=233264`), money 9.3M,
2 masteries. (An older doc's "level 37" is stale.) A `Player.chr.corrupted_20260310_2050` marks a
March corruption event.

Per-map save contents (decoded): `map.dat` (196 B - just current spawn position + one level GUID),
`fowData.arz` (fog-of-war: an arc of per-level `.fow` bitmaps with **plain level names**), `Quest.myw`
/ `QuestToken.myw` / `*.que` (quest state). **There is no per-level monster or kill file anywhere.**

Fog-of-war (which levels he actually explored):
- **Epic: 134 levels, all Greece** (130 Greece, 5 xpack, 0 Egypt/Orient) - mid-Act-1. **INCLUDES
  `.../ug_arachnosunderground/arachnosunderground01_floor0.fow`** - so **he DID enter the Fetid Lair on
  Epic**. **ZERO Athens** entries on Epic.
- Normal: 928 levels (full campaign incl. 37 Athens levels + the Fetid Lair).

Quest triggers near "arachne" that HAVE baked state on Epic are all **journal / scripted-scene lore
triggers, not boss gates**: `Greece Journal - Poisoned Spring` (JG06, the naiad/spring), `Scripted
Scene - Tegea Scenes` (`SS_PreTegea_ArachnosCave` - a different, pine-forest arachnos spot), and
`Greece Journal - Olive Branch` (JG14, whose step `JG14_Found Arachne` is a lore "found the grove"
beat). **Arachne's Shame the boss is a pure map-proxy spawn and is NOT gated by any of these quests** -
killing her is not a quest objective, so these tell us only that he walked through those areas.

Inventory: **26 boss/hero souls** (Medusa, Ephialtes, Dagon, Enslaver, Voranthys, Podarce, ...), but
**NO Arachne's Shame soul and NO Hydra soul**. (Weak evidence: souls have a drop chance and can be
stashed/sold, so absence is consistent with "never killed her" but does not prove it.)

---

## 4. The "save-baking" claim - honest assessment (this is the part we kept hand-waving)

**We have repeatedly asserted "TQ bakes the monster spawn into the save on first visit, so a
non-resetting cave never re-rolls." I could not prove that, and I will not assert it.** Here is the
honest state of the evidence:

1. **The save stores no per-level monster/kill record that I can decode.** The only per-map files are
   `map.dat` (position), `fowData.arz` (fog bitmaps), and the quest files (`.myw`/`.que`). None of them
   encodes "Arachne is dead in ArachnosUnderground01" or the rolled monster layout. So there is no
   artifact to point at and say "here is the baked empty spawn."
2. **The engine's leave-and-return respawn behavior is itself an OPEN question in this project**
   (`docs/BACKLOG.md` B-SPRITE-1: exploding sprites "do not respawn (STILL)... per-level-load vs dead...
   Will is testing"). If TQ actually re-rolls a non-reset cave's proxies on re-entry, a guaranteed
   proxy like Arachne would re-appear every visit - which would mean her absence is NOT save-baking at
   all.
3. Therefore the true reason she was absent on his specific Epic save is **one of several candidate
   causes, none distinguishable from the static files**:
   - **(a) She spawned and he killed her**, over-leveled (L52 in Epic Act 1 one-shots everything), and
     got no soul drop (or stashed it); the cleared cave does not re-roll her for him. (Working as
     designed.)
   - **(b) His Epic Fetid Lair instance was first rolled in a context where the mod's arz Boss override
     was not active** (an early/broken deploy, or a non-mod session), so the proxy only had `pool1`
     (orbweavers) and never produced a boss - and TQ persisted that roll. (A historical artifact of his
     save, not a current-build defect - the current arz is correct.)
   - **(c) He entered the level but never reached her sub-chamber**, so the proxy never triggered; the
     partial instance persisted. (Less likely for a single-floor cave, but possible.)
   All three are **his-save / his-playthrough** explanations. **None implicates the current build**, whose
   fresh-spawn path is byte-proven intact (sec 2).

**Bottom line on the mechanism:** "save-baking" is a plausible, standard-for-TQ hypothesis, but it is
**unproven** and should be described as such, not as fact. The one thing that is certain: her absence is
tied to **his existing character's world-state**, not to any defect in build40 / the DEV deploy.

---

## 5. Was anything actually broken? No.

- Arachne: chain intact + Epic-guaranteed + proxy placed in the played map + arz version-identical to
  canonical. A fresh Epic instance WILL show her. **No DB fix, no map fix warranted** (and editing the
  intact guarantee would be a forbidden rebalance).
- Hydra: chain intact + proxy placed + Legendary-only exactly as base intends. **No fix warranted.**
- No runtime gate that excludes Epic (Arachne) or breaks Legendary (Hydra) was found in the static
  data. (Caveat: static analysis cannot see runtime; sec 6 is how to close that.)

---

## 6. The ONE decisive next step (stop guessing - measure)

Because the static spawn path is proven intact and version-invariant, the real-world cause can only be
settled in-game:

1. **Fresh-instance test (cheapest decisive):** a Custom-Quest character that reaches **Epic** and
   enters a Fetid Lair it has **never visited on Epic** - i.e. effectively a NEW character, since
   `_Toxeus` has already instanced the only Fetid Lair on Epic. Restart Steam + TQ first; hash-verify
   the DEV deploy landed. **If she appears -> confirms his old instance is the artifact** (whatever the
   persistence mechanism), and the mod is fine. **If she does NOT appear on a fresh Epic entry ->
   there is a runtime-only factor the static data cannot see, and THAT is the real bug** to chase (with
   the existing Frida spawn/`ProcessRLTD` probe hooked on the `poisonspring c` proxy).
2. Do **not** attempt to "un-bake" `_Toxeus`'s existing Epic Fetid Lair from the DB/map - a save's
   instanced level cannot be reset from static data; that is not achievable and not a bug to fix.
3. **Hydra needs no test** - it is base-correct Legendary-only content, and Will simply has not played
   Legendary.

### Exact where-and-when for Will to look
- **Arachne's Shame:** difficulty **EPIC or LEGENDARY** (never Normal). Location: the **Fetid Lair** =
  the underground arachnos cave `ArachnosUnderground01_Floor0`, reached in **Greece Act 1, Area003**
  (the pine-forest / pre-Tegea region). Guaranteed single Boss spider from the `poisonspring c` proxy.
- **Hydra:** difficulty **LEGENDARY ONLY** (never Normal or Epic). Location: **Athens**,
  `Area02_Athens01` (Greece Act 1, the Athens approach). On Normal/Epic that spot has skeletons/harpies
  instead; only on Legendary does the Hydra replace them.

---

## Appendix - evidence artifacts (read-only probes, scratchpad)

- `ah_db.py` - Arachne proxy -> per-difficulty pools -> members + limits, re-derived from build40/base/SV098 bytes.
- `ah_findhydra.py` / `ah_hydra2.py` - located the real Hydra proxy (`proxies boss\boss\...`) + full
  Normal/Epic/Legendary walk + the "normal only fodder" EmptyPool-on-Legendary gate.
- `ah_place.py` - 0x05 placement check for both proxies across DEV/DEV2/canonical/base/SV098.
- `ah_fow.py` - decoded `fowData.arz` explored-level lists (Fetid Lair present on Epic; Athens absent on Epic).
- `ah_visited.py` / `ah_quescan.py` / `ah_quegrep.py` / `ah_quehash.py` - established that `.que` = quest
  state (not monster bake), `map.dat` is 196 B, and that the save has no per-level monster record.
- `ah_char.py` - Player.chr (level 52, ~65 h) + baked JG06/JG14/Tegea quest states (all lore triggers).
- `ah_inv.py` - inventory soul scan (26 souls; no Arachne's Shame soul, no Hydra soul).
