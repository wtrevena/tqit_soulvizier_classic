# b82 - Blood Cave deterministic crash RCA (round 1)

Branch: `fix/bloodcave-crash` (worktree). Reference: build45 (main 33d25d6), arz md5 917d9047
(unchanged - this round authors NO .arz/.arc/map change; it adds one validator + docs).
Will's report (2026-07-16, P0): "there is some item or something in the blood cave that is not
wired correctly since every time i go to that same area the game crashes."

## VERDICT (round 1)
**No single broken-wiring offender found that this lane may fix.** Two independent, exhaustive
checks came back clean, and the forensics point at a MAP-STRUCTURAL navmesh condition (not a
dangling item/record), whose two concrete candidate fix-surfaces are both owned by reserved
parallel lanes. Deliverables this round: (1) forensic reconciliation of the Jul-13 native dump;
(2) a new permanent gate that rules out the "placed record with unresolvable asset" offender
class in the blood cave (PASS); (3) the bisect + Frida probe plan keyed on Will naming the exact
chamber. Confidence that the *subsystem* is the Engine.dll navmesh-load path: HIGH. Confidence
that a fixable single "item wired wrong" exists in this lane: LOW (actively evidenced against).

---

## 1. FORENSICS

### 1a. The Jul-13 TQ-written native dump (read first, per brief)
`My Games/.../TitanQuest_LENOVO_P14S_G_4_2026_7_13x20_27.dmp.txt` (build41 era,
mod `SoulvizierClassicDEV`). Exception 0xc0000005, EIP `0x5fe4e270`, EDX=`0x400` (1024 = a size),
EDI=`0x0`, params `0x0 0x1feffd0c`.

Call stack as the TQ handler labelled it:
```
GAME::RegionId::Write + 48 bytes
GAME::ZoneManager::~ZoneManager + 9160 bytes
0xa0000073  ...
```
**Address math corrects the labels.** Module bases from the dump's own module list:
Engine.dll = `0x5fc40000`, Game.dll = `0x5f6a0000`. The faulting EIP `0x5fe4e270` lies INSIDE
Engine.dll (`0x5fe4e270 - 0x5fc40000` = RVA **`0x1020e270`**), NOT in Game.dll's range at all.
So the `GAME::RegionId::Write` / `GAME::ZoneManager::~ZoneManager` labels are the crash handler's
nearest-preceding Game.dll public-symbol guesses and are wrong; the real fault is Engine.dll code
at RVA `0x1020e270`, which sits ~`0x19000` past `ProcessRLTD` (`0x101f4ba0`) in the same
navmesh/region subsystem. EDX=`0x400` + EDI=`0x0` + near-null param is exactly the per-tile
alloc/memcpy burst profile documented for that path. So the native dump **corroborates** the
prior WER-based RCA (map-side navmesh load), it does not point to a broken item.

Game-log tail (last lines the handler flushed) names nothing that crashed: dozens of benign
`Tried to create duplicate non-modifier skill (armor_passive / drx*)` warnings, one
`AnimationSelected: Invalid reference () ... malepc_dw_skill_jumpslash.anm` (a PLAYER dual-wield
animation, not blood-cave content), and `SkillManager::Unable to create skill (shieldcharge.dbr)
(records\skills\sv\pygmalion\replicant_41.dbr)` (engine skips the skill; benign). These are the
last flushed log lines, not the cause.

### 1b. The recurring WER dumps (prior deep analysis, re-affirmed)
`docs/crash/DEEP_DUMP_ANALYSIS_2026-07-12.md` + `WER_FINDINGS_2026-07-12.md` establish, from all
7 CrashDumps `.dmp` files (incl. both build36 dumps), that the recurring blood-cave crash is
heap corruption detonating inside `ProcessRLTD` (Engine.dll navmesh parser) invoked from the
`0x0b` nav-load section gate - two stable ntdll offsets, an INVARIANT ProcessRLTD ancestor chain
across all 5 Sig-B dumps, structurally-clean injected navmesh data (39/39 donors pass full
FastLZ + REC\x02 invariants), and - the clincher - the build36 .arz mitigation changed the dump
signatures by ZERO. A DB-driven monster/summon/loot corrupter would have shifted something.
Root subsystem = MAP-SIDE navmesh load; leading hypothesis H1 = grid-seam-chain co-residency /
tile-coordinate collision as the player streams successive deep chambers.

### 1c. The "loot equation crash" hypothesis is REFUTED
The brief flagged the TATTERED PARCHMENT `FixedItemLoot` `numberOfPlayers*1` equation as a prime
suspect. The engine's own game logs (`docs/crash_analysis_report.md` sec "Proxy RunEquation
Failures" + CLAUDE.md content-gaps) show SV's `RunEquation` MP-scaling formulas
(`poolValue ((...numberOfPlayers*1.0...))`) **fail to parse but are BENIGN warnings** - the
engine falls back to default pool/values and continues. An unparseable loot/pool equation
reduces spawn density; it does not crash. So the parchment equation is not the crash.

---

## 2. BLOOD-CAVE SURFACE INVENTORY (what our builds TOUCH)

Map-PLACED (canonical `INJECT_SPECS`, `tools/build_section_surgery.py`), per level:
- `xbloodcave/drxfirstxistion_connection.lvl`: FINALLETTER (widow letter static) + EN_WARBAND_SPEC
  (Enslaver warband set-piece proxy). The M15 parchment repoint here is RETIRED (documented, never
  a live spec) - this level's real specs = finalletter + enslaver warband only.
- `bossarena/boss_arena.lvl`: 6x `5mlight_dyn_orange` (Aithon fire-ring dressing, EffectEntity).
- `secret_place/darkforestenter.lvl`: `svc_testhub_return` NPC (Toxeus superboss area return).
- `orient/silkroad/hiddenvalley01.lvl`: respawn fountain + caravan + C4 totem/light/campfire
  atmosphere cluster (all EffectEntity/light/Decoration).
- `orient/silkroad/hiddenvalleyborder04.lvl`: Hades merchant wagon + occult atmosphere cluster +
  B2 pit-spawner sprite pack (t1_pitspawner_01/02, t1_lildude, pit_fx01).

DB-SPAWNED into blood-cave levels (reserved-lane territory - see §4): the q_bloodtoxeus proxies /
pools / chest (egg_blooddragon_pack pool + um_bloodtoxeus_99), the drxFirstRoom ambush
(q_bloodtoxeus_ambush), the parchment demon_01_cluster, the majestic chests (b43), the Toxeus /
Devourer superboss + kit (melinoe_bloodboil, toxeus_bladestorm, etc.), and the various proxy
packs the SV blood-cave blobs reference natively.

Full cluster = 44 level blobs matched by the gate's blood-cave substrings (xbloodcave, bloodcave,
bossarena, secret_place, hiddenvalley01, hiddenvalleyborder04).

---

## 3. CHAIN VALIDATION (new this round)

### 3a. New gate: map-placed-record resolution
`tools/contracts/gate_placed_record_resolution.py`. The existing `validate_render_chain*.py`
gates only cover DB-SPAWNED summon pets; MAP-PLACED records in the Levels.arc level blobs were an
uncovered gap - and the offender class the brief named ("placed record with unresolvable asset")
is exactly a placed entity whose `records\...\.dbr` does not exist in the shipped DB, which the
engine instantiates with a null/dangling pointer that detonates on zone/region teardown.

The gate extracts every embedded `records\...\.dbr` ref from each blood-cave-cluster level blob in
the deployed `Levels.arc` and asserts each resolves in the union of the mod `SoulvizierClassic.arz`
+ base `database.arz` (the engine's real mod-over-base resolution).

**Result: PASS.** 1096 distinct placed-record refs across 44 blood-cave-cluster blobs; every one
resolves. Negative test (planted dangling ref) is correctly flagged. So there is NO dangling
map-placed record reference in the blood cave - the "placed record with unresolvable asset"
offender class is ruled out at the record-resolution level.

(One initial phantom hit - `setdress\ orienttownsetdresstablegroup.dbr` with an embedded space -
was a regex artifact: the non-greedy body class included space 0x20 and bridged a length-prefix
byte between two adjacent strings. Tightened the body to `[!-~]` (no space; TQ record paths never
contain spaces) and re-ran clean. The real space-free record resolves in base.)

Scope note: the gate's authoritative scope is the blood-cave cluster (default), fully covered by
mod+base. `--all` whole-map mode additionally needs the Ragnarok/Atlantis/EE DLC databases unioned
(pass them comma-separated to `--base`); without them `--all` false-positives on xpack2/3/4 records.
Not needed for this crash (the blood cave uses only base + mod records).

### 3b. Named DB suspects
- Parchment `numberOfPlayers*1` loot equation: refuted as a crash cause (§1c; benign parse-fail).
- melinoe_bloodboil "BloodBoil" named anim + the Devourer/Toxeus kit: the kit records are
  documented in `apply_svc_patches.py` (`_BT_SK_*`) as "all EXIST, classes DB-verified"; this is
  the reserved bloodtoxeus/boss territory (§4) - flagged for that lane, not edited here.

---

## 4. RESERVED-LANE HANDOFF (PARALLEL-LANE GUARD)
The only two concrete candidate fix-surfaces both live in reserved sets, so per the guard this
lane produces the spec and does NOT edit them:
- **`fix/bloodtoxeus-spawns`** owns the q_bloodtoxeus proxies/pools/chest + entourage
  (egg_blooddragon_pack pool + um_bloodtoxeus_99, q_bloodtoxeus_ambush, the parchment
  demon_01_cluster, and the Toxeus kit/entourage). HANDOFF: if a future round pins the crash to a
  specific spawned entity in a named chamber, that entity's record/chain fix is theirs.
- **`fix/chumbi-lag`** owns boss placements/spacing. HANDOFF: the Toxeus/Aithon/Devourer boss
  PLACEMENTS (which chamber, spacing, co-residency with the streaming seam) are theirs; note H1
  (navmesh co-residency) is a cluster-packing property that interacts with where heavy boss
  set-pieces sit relative to the grid-seam chain.

Nothing broken was found OUTSIDE the reserved sets to fix, so no record edit is made this round.
(Per WILL_RULINGS RETIREMENT PROTOCOL, no record is deleted; the q_bloodtoxeus_lone_50 lesson.)

---

## 5. BISECT + PROBE PLAN (the decisive next step)
Static analysis has gone as far as it can: the data is clean, the subsystem is pinned, the exact
triggering chamber/tile is not statically determinable. The next round needs ONE of:

1. **Will names the exact area** (the "same area" he crosses). Then bisect the per-level inventory
   (§2) for that chamber: check its co-resident neighbors' navmesh tile-coordinate spans for
   collision (H1), and its placed/spawned set for a heavy set-piece at the streaming seam.
2. **Frida ProcessRLTD ENTER/LEAVE probe** (harness exists: `docs/crash/WILL_CRASH_PROBE_GUIDE.md`,
   `tools/debug/frida_test13.py` / `frida_probe.py`). Hook the caller gate `Engine+0x1b4158`
   (read `edi`=Level*, log its GUID+name), wrap ProcessRLTD (`Engine+0x1f4ba0`) ENTER/LEAVE, and
   snapshot the region-manager live-instance array (`[[Engine+0x3743f0]+0x34]+0x50]`) at entry.
   The chamber that logs ENTER with no LEAVE at the crash = the corrupting load; the co-resident
   array names its neighbors (tests H1 directly).
3. **Full Page-Heap on TQ.exe** (`gflags /p /enable TQ.exe /full`) converts the delayed heap
   detonation into an immediate fault at the corrupting write (size-filtered if the 32-bit LAA
   process OOMs). Single most decisive step for confirming the corrupter.

If H1 is confirmed, the map-side remedy is `CAVE_ENTRY_CHAIN_TRACE.md` Fix B (relocate the
blood-cave cluster into XZ-disjoint empty world space, or connect deep chambers with interior
GridEntrance portals so at most 1-2 navmeshes are co-resident) - a heavy map rebuild that is
itself map-structural (coordinate with the map lane).

---

## 6. GATE (permanent)
`tools/contracts/gate_placed_record_resolution.py` - blood-cave (default) + whole-map (`--all`)
map-placed-record resolution, with a planted-dangling-ref negative test (`--negtest`). Run:
```
py tools/contracts/gate_placed_record_resolution.py \
   work/SoulvizierClassic/Resources/Levels.arc \
   work/SoulvizierClassic/Database/SoulvizierClassic.arz \
   --base "<game>/Database/database.arz"
```
PASS on build45 (917d9047). Recommend wiring into the map-contracts family.
