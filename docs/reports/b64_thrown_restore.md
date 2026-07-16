# b64 - Thrown-Wielder RESTORE (not invented families)

> **Will's design law (verbatim, supersedes b58's "invent + place" approach):**
> *"instead of us wiring them back into spawn pools and us deciding which pools to
> wire them into, cant we just restore them into the existing pools that they
> previously spawned in?"* + *"restore the ones that are in the expansions and
> then scale up them to match SV difficulty."* DLC dependency confirmed
> acceptable (subscribers already need the DLC to load this Custom Quest mod).
>
> **Ground-truth sources (read-only, independently re-derived from scratch -
> the b58 probe scripts were session-ephemeral and not committed):**
> - Effective DB = base TQAE `database.arz` (74,013 recs) overlaid by golden mod
>   `SoulvizierClassic.arz` md5 **`eb8bc37775540f872003f873abf8e8be`** (build41,
>   51,023 recs, `work/SoulvizierClassic/Database/SoulvizierClassic.arz`).
> - No heavy build. Every finding below is a static read of the golden + base
>   `.arz` (record fields, loot-table chase, `ProxyPool.tpl` reverse-index,
>   `Proxy`-class placement reverse-index) plus `docs/BACKLOG.md`'s own
>   committed reachability rulings (Victory Portal/Act-5/Atlantis history) for
>   the act-transition chain. Levels_merged.arc was NOT byte-scanned per
>   record (no heavy build) - reachability for the 10 restored records is
>   proven via their own base-game `Proxy` placement paths (`records\proxies
>   greek\area004\...`, `records\proxies egypt\area002 - abedju\...`, `records
>   \proxies orient\area002 - silkroad\...` / `area004 - greatwall\...` /
>   `area006 - jadepalace\...`, `records\xpack\proxieshades\area005 plains of
>   judgement\...` / `area007 elysian fields\...`), cross-checked against the
>   BACKLOG's documented reachable-act list.

---

## VERDICT (TL;DR)

**10 of the 74 audited wielders are restored, in place, into the SAME base-game
pools that already spawn them - zero map/pool changes.** The other 64 are
genuinely DLC-act content (Ragnarok Scandia/Corinthia/Germany/Asgard or
Atlantis) our campaign does not traverse; per the design law, **nothing
was invented or placed for them** - they are reported below with options.

1. **Independently re-deriving the b58 "74" from scratch** (a monster is an
   IDENTITY thrower if its STATIC weapon slot, or the paired MONSTER-MAGIC/
   UNIQUE slots, resolve via loot-table chase to `Class=WeaponHunting_
   RangedOneHand` - this excludes ~49 "incidental" monsters, mostly base-game
   skeletons and Ragnarok's `dvergr`, whose weapon randomizer merely offers a
   low-weight *alternate* thrown option in slots 2/4 alongside a sword/axe/
   mace, not an identity) yields **75 records**; one
   (`xpack2\creatures\npc\corinth\fighting\ss_porcusroh2_die.dbr`) is a
   scripted kill-cam prop with **zero** pool membership anywhere in base+DLC
   data, not a spawnable wielder - net **74**, exactly reproducing b58's
   figure by an independent method (methodology fully documented in Part 1).
2. **(a) OVERLAY-DISARMED, restored HERE - 10 records / 4 rigs.** The base
   game shipped genuine throwers on FOUR rigs our campaign already places in
   reachable zones - `Maenad02.msh` (Act 1 Greece), `DuneRaider01.msh` (Act 2
   Egypt), `TigerMan01.msh` (Act 3 Orient), and **`Machae{01,02,03}A.msh`**
   (Immortal Throne - Elysian Fields / Plains of Judgement). The SV-classic
   roster predates thrown weapons and overlaid every one of these 10 records
   to a bow (maenad/tigerman/machae) or melee (duneraider) weapon, **clearing
   the right-hand loot arrays outright**. Every one of their base-game
   `ProxyPool`s is verified UNCHANGED (or case-normalized only) in the golden
   overlay - restoring the fields on the SAME record is the entire fix; no
   pool/map edit needed. **Machae is a correction to the b58 audit**: its
   rig sits under the "xpack" (no digit) Immortal Throne namespace and was
   filed there as "DLC/unreachable" without checking WHERE in IT it is
   placed - ground truth: its own `ProxyPool`s place it in Elysian Fields and
   the Plains of Judgement, both core, always-reachable Hades-arc content
   (`records\xpack\proxieshades\area005 plains of judgement\...` /
   `area007 elysian fields\...`), not a DLC bonus act.
3. **(b) POOL-MEMBERSHIP-LOST: NONE found.** Every DLC-only `ProxyPool`
   (Ragnarok `proxiesnorth`, Atlantis `proxiesatlantis`) is untouched by our
   overlay (`in_golden=False`, pure base pass-through) - our own mod never
   dropped a wielder out of a pool it used to be in.
4. **(c) INTACT-BUT-UNREACHABLE - 64 records, not restored/placed.** Every
   remaining wielder resolves correctly and sits in its original, unchanged
   base `ProxyPool` - but that pool's own `Proxy` placement is Ragnarok
   Scandia/Corinthia/Germany/Asgard/Dvergr-Lands (46 records) or Atlantis
   Outer-Atlantis (18 records). Per the standing IT-cap ruling
   (`docs/BACKLOG.md`), the post-Hades Victory Portal goes to **Epic**, not
   Ragnarok/Scandia or Eternal Embers, and Atlantis is reachable only via the
   early-Egypt Rhodes/Marinos boat chain Will has asked to leave **PARKED**.
   No invented pool wiring - see Part 4 for the full area breakdown + options.
5. **SV-difficulty scaling** (Part 3): the 7 restored Common-rank records had
   `characterLife` untouched since raw base AE (ratio 1.0 vs the golden
   overlay) - genuinely under-tuned, confirming the task's premise - scaled
   x1.20 (the empirical Common-rank median our own SV integration already
   applies elsewhere, n=258). The 3 Champion duneraider variants were
   **already** SV-scaled by a prior wave (`characterLife` golden/base ratio
   exactly 1.4, uniformly across all three) - left untouched, not
   double-scaled.
6. **Module**: `tools/patches/thrown_restore.py`, **REGISTERED** in
   `tools/patches/__init__.py` `REGISTRY` (this wave, unlike b58's
   `thrown_wielders.py` which stays unregistered/shelved - see Part 5).

---

## PART 1 - METHODOLOGY (independently re-deriving "74")

The b58 probe scripts (`twa_gt_*.py`) were session-ephemeral, never committed,
so this wave re-derives the population from scratch and cross-checks it lands
on the same number by a documented, reproducible method:

1. **Thrown-item universe.** Scan every record's `Class` field in base +
   golden; `Class = WeaponHunting_RangedOneHand` = **178 base + 13 mod-added
   (191 total)**, all `xpack2/3/4` (the 13 golden-only ones are the mod's own
   `_add_supra_thrown_weapons` legendary supras - `docs/BACKLOG.md`).
2. **Loot-table chase.** A monster's `lootRightHandItemN` / `lootLeftHandItemN`
   (N=1..6) is a `[N,E,L]` triple of `LootItemTable_FixedWeight` dbr paths;
   each table's own `lootNameK`/`lootWeightK` (K=1..30) resolve to items
   (occasionally to a further nested table - handled recursively, depth-capped
   at 4, cycle-guarded). A monster "resolves thrown" for a hand if
   `chanceToEquip{Hand}Hand > 0` AND at least one non-zero-weight item slot's
   table chases to a thrown item.
3. **Identity vs incidental.** Slots 1/3/5 (static/monster-magic/unique) are
   the coherent 3-tier THROWN block (same structure b58's own
   `thrown_wielders.py` documents for the 3 rigs it armed). Slots 2/4 are a
   *different*, unrelated alternate-weapon-type slot pair (e.g. Ragnarok's
   `dvergr` warriors have a ~0.6%-weight thrown option in right-hand item2
   alongside equally-minor sword/axe/club alternates - the same shape base
   skeletons show on left-hand item2/4). Filtering to slot 1/3/5 hits only:
   **75 records** (vs. 124 before the filter, which includes the ~49
   incidental skeleton/dvergr/`x4_dev` false positives).
4. **Not-a-wielder.** `xpack2\creatures\npc\corinth\fighting\
   ss_porcusroh2_die.dbr` (a scripted death/kill-cam NPC prop under
   `creatures\npc`, not `creatures\monster`) has **zero** membership in any of
   the 2,763 base `ProxyPool.tpl` records scanned - it is never placed by any
   pool in vanilla+DLC data. Excluding it: **74**, exactly reproducing b58.

---

## PART 2 - THE FULL 74-WIELDER CLASSIFICATION TABLE

### (a) OVERLAY-DISARMED - restored this wave (10 records)

| Record | Family / rig | Rank | Home (base `Proxy` placement) | Base->Golden equip (pre-restore) | Restored equip |
|---|---|---|---|---|---|
| `creature\monster\maenad\ar_archer_06.dbr` | Maenad02.msh | Common | Act 1 Greece, Area004/005 | RIGHT 100%->0% (loot cleared), LEFT bow 0%->100% | RIGHT 100% thrown (1h_ranged_01b/06a/11a), LEFT 0% |
| `creature\monster\maenad\br_archer_10.dbr` | Maenad02.msh | Common | Act 1 Greece, Area004/005 + `proxies boss\le_new` | same pattern | same family tables |
| `creature\monster\duneraider\am_assassin_15.dbr` | DuneRaider01.msh | Champion | **none - orphan in vanilla itself** (see note) | dual RIGHT+LEFT 100%->100% melee `1h_dyn` | dual RIGHT+LEFT 100% thrown (1h_ranged_02b/07a/12a) |
| `creature\monster\duneraider\am_assassin_21.dbr` | DuneRaider01.msh | Champion | Act 2 Egypt, Area002 - Abedju | dual RIGHT+LEFT 100%->100% melee | dual RIGHT+LEFT 100% thrown, same family |
| `creature\monster\duneraider\am_assassin_27.dbr` | DuneRaider01.msh | Champion | Act 2 Egypt, Area002 - Abedju + scripted `encact2`/scene13 | dual RIGHT+LEFT 100%->100% melee | dual RIGHT+LEFT 100% thrown, same family |
| `creature\monster\tigerman\ar_archer_27.dbr` | TigerMan01.msh | Common | Act 3 Orient, Silk Road/Great Wall/Jade Palace | RIGHT 100%->0% (loot cleared), LEFT bow 0%->100% | RIGHT 100% thrown (1h_ranged_03a/08a/13a), LEFT 0% |
| `creature\monster\tigerman\ar_archer_33.dbr` | TigerMan01.msh | Common | Act 3 Orient, Silk Road/Great Wall/Jade Palace | same pattern | same family tables |
| `xpack\creatures\monster\machae\ar_archer_37.dbr` | Machae01A.msh | Common | **Immortal Throne** - Elysian Fields / Plains of Judgement | RIGHT 100%->0% (loot cleared), LEFT bow 0%->100% | RIGHT 100% thrown (1h_ranged_04b/09b/14b), LEFT 0% |
| `xpack\creatures\monster\machae\br_archer_37.dbr` | Machae02A.msh | Common | Immortal Throne - Elysian Fields / Plains of Judgement | same pattern | same family tables |
| `xpack\creatures\monster\machae\cr_archer_37.dbr` | Machae03A.msh | Common | Immortal Throne - Elysian Fields / Plains of Judgement | same pattern | same family tables |

**Orphan note (`am_assassin_15`):** this record IS overlay-disarmed exactly
like its 21/27 siblings (base right+left = thrown melee->overlay = melee), and
is restored here for identity consistency with the rest of the Dune Raider
family - but it has **zero** `ProxyPool` membership anywhere in base+DLC data
(checked exhaustively across all 2,763 pools). It is dead/unplaced content in
**vanilla TQ itself**, not an SV regression, and per Will's design law ("restore
into pools they previously spawned in") there is no pool to restore it into.
Restoring its equipment is harmless but has **zero player-visible spawn
effect alone** - flagged, not hidden.

**Machae's third variant (`cr_archer_37`)** is a genuine find beyond b58's
2-variant machae mention (which only tracked `ar_`/`br_archer_37`) - the base
game ships a third sub-rig (`Machae03A.msh`) at the identical charLevel
`[37,54,69]`, also disarmed identically, also placed in the same two Elysium/
Judgement pools (`_c` suffix variant tables). All three are in the restore.

### (b) POOL-MEMBERSHIP-LOST

**None.** Every DLC-area `ProxyPool` referencing any of the 64 unreachable
wielders below is `in_golden=False` (pure base pass-through, never touched by
our overlay). Our own mod's various pool edits (roaming-rare sweeps, drop-rate
work, hero insertions) only ever touched pools our overlay ALSO explicitly
overrides for other reasons (e.g. the 8 pools in bucket (a) above, which
picked up unrelated champion/density tuning from other waves but kept every
name-slot's own monster membership intact - verified diff, case-only or
proportional-reweight only, zero name-slot removed).

### (c) INTACT-BUT-UNREACHABLE - 64 records, NOT restored/placed

Every one below resolves correctly (right-hand loot chases to a thrown
weapon) and sits in its own unchanged base `ProxyPool` - the placement is the
problem, not the equipment or the pool membership. Grouped by area (each
row's `Proxy` placement folder is ground-truth, not inferred from naming):

| Area (base `Proxy` placement) | Reachable in our world? | Count | Families |
|---|---|---|---|
| Ragnarok - Corinthia (`proxiesnorth\area001 corinthia`) | **No** - this is Ragnarok's OWN zone of that name (a b58 residual now resolved: nothing to do with reachable Greece, despite the "greekbandit" naming) | 3 | Greek Bandit Slinger |
| Ragnarok - Southern/Northern Germany (`proxiesnorth\area002/003`) | **No** - post-Hades Victory Portal goes to Epic, not Scandia (A5 fix, `docs/BACKLOG.md`) | 24 | Troll Skulk, Celtic Bandit Slinger |
| Ragnarok - Scandia/Asgard (`proxiesnorth\area004/006`) | **No** - same A5 cap | 7 | Aesir Jarl/Fodder-Thrower |
| Ragnarok - Dvergr Lands/Scandia (`proxiesnorth\area004/005`) | **No** - same A5 cap | 3 | Yerren Thrower |
| Ragnarok - Germany/Scandia "fake einherjar" (`proxiesnorth\area002/003/004`) | **No** - same A5 cap | 3 | Mercenary Skirmisher |
| Ragnarok quest bosses (`xpack2\quests\proxies\pools\x2q03_nerthusancient{1,2}_pool`) | **No** - Ragnarok Act-5 quest content, same A5 cap | 6 | "Ancient Earth"/"Ancient Forest" (Nerthus Ancients) |
| Atlantis - Outer Atlantis (`proxiesatlantis\area003`) | **Parked** - technically walkable pre-Hades via the Rhodes/Marinos boat chain for an Atlantis-DLC owner, but Will's standing ruling keeps this PARKED/non-functional for now | 12 | Potamoi Thrower |
| Atlantis (`proxiesatlantis`, beastman pools) | **Parked** - same Atlantis caveat; one `monkeyman_01_ranged01` pool has ZERO base `Proxy` reference at all (unused in vanilla too) | 6 | Monkeyman Flinger |

**Options for Will** (no action taken; pick one per area, or leave capped):
1. **Leave capped** (current default; matches the standing IT-cap + A5 rulings) -
   these 64 simply never spawn, same as today.
2. **Lift the Atlantis park** for the 18 Potamoi/Monkeyman records specifically
   (they are pre-Hades reachable via the existing Rhodes boat chain that
   already exists in our data, per the prior Atlantis recon in
   `docs/BACKLOG.md`) - this would need the same Quests.arc-level un-cap work
   already scoped for "Rhodes->Atlantis" in that recon, not a pool/equip change.
3. **Reconsider the A5 cap** for the 43 Ragnarok-area records - this would
   mean genuinely opening Ragnarok/Scandia post-Hades, a MUCH bigger map/quest
   change than this DB-only wave and outside the design law's "restore into
   EXISTING reachable pools" instruction; not recommended for this wave.

---

## PART 3 - SV-DIFFICULTY SCALING (ground truth)

Sampling every `Class=Monster` record present in BOTH base and golden with an
UNCHANGED `monsterClassification` (2,992 candidates; 925 had >=1 stat field
actually rescaled by our own SV integration), the golden/base `characterLife`
ratio distribution:

| Rank | n | median | min | max |
|---|---|---|---|---|
| Common | 258 | **1.20** | 0.18 | 3.33 |
| Champion | 423 | 1.26-1.30 | 0.60 | 2.80 |
| Boss | 66 | 1.28 | 1.00 | 1.85 |

This is a wide, per-monster/per-family hand-tuned spread, **not** a flat
constant - the task's own premise ("their base-AE stats are under-tuned")
holds for exactly the 7 Common restored records here (their `characterLife`
was **verified byte-identical to raw base AE**, ratio 1.0, i.e. genuinely
never touched by any prior SV pass), so this module applies the empirical
Common-rank **median (x1.20)** to `characterLife` only - the sole per-record
stat field these specific variants define (OA/DA/STR/DEX/INT are absent on
both the base and golden records - template-inherited, nothing to scale).

| Record | Base `characterLife` | Scaled (x1.20) |
|---|---|---|
| `maenad\ar_archer_06` | 45.0 | 54.0 |
| `maenad\br_archer_10` | 71.0 | 85.2 |
| `tigerman\ar_archer_27` | 324.0 | 388.8 |
| `tigerman\ar_archer_33` | 409.0 | 490.8 |
| `machae\ar_archer_37` | 718.0 | 861.6 |
| `machae\br_archer_37` | 718.0 | 861.6 |
| `machae\cr_archer_37` | 718.0 | 861.6 |

The 3 Champion Dune Raider variants are **already** SV-scaled by a prior wave
(golden/base `characterLife` ratio is exactly **1.4** for all three - 194.0
->271.6, 288.0->403.2, 404.0->565.6) - this module does **not** touch their
stats (verified by `verify()`: it asserts their current life is >= base, never
reverts or re-scales).

---

## PART 4 - DROP SAFETY

Every restored record's right(+left, dual families)-hand loot arrays are the
family's own **exact vanilla** `[N,E,L]` static/monster-magic/unique tables
(captured verbatim from the base donor, not reconstructed) - drop weights
match the original vanilla band exactly (monster-magic slot 20-25, unique
slot 4-5, out of ~5025 total slot weight, ~0.08-0.1%): identical to how that
same monster's bow/melee drop slot was already weighted before the disarm.
Soul gate: all 10 records are Common/Champion rank; `chanceToEquipFinger2`
is **0.0 in both base and golden for every one** (verified) - restoring
equipment does not touch the soul slot, and `verify()` re-asserts it stays 0.

---

## PART 5 - THE MODULE

`tools/patches/thrown_restore.py` (registered in `tools/patches/__init__.py`
`REGISTRY`, inserted between `damage_display` and `boss_skill_fix` - disjoint
namespace, order-independent, confirmed zero record-path overlap with any
other registered module via a full-tree grep). Unlike b58's
`tools/patches/thrown_wielders.py` (kept, UNREGISTERED, docstring updated to
point here - see its own file for the design-history record of the
invented-family approach), this module:

- **Edits the 10 roster records IN PLACE** - no `clone_record`, no new
  namespace, no new `ProxyPool`. `apply()` restores each record's base
  right(+left)-hand equip/loot fields verbatim and applies `COMMON_SCALE`
  (x1.20) to `characterLife` for the 7 Common records only.
- **`verify(db, tags)`**: every restored record's mesh is unchanged and on
  the throw-PROVEN `RIG_WHITELIST`; RIGHT hand equips a thrown weapon at
  100%; LEFT hand is either ALSO thrown (dual duneraider family) or fully
  disabled (single-hand families - no residual bow can beat the throw); drop
  weights are in the vanilla band; no soul leak; Common life is scaled
  exactly, Champion life is left alone (asserted >= base, never reverted).
- **`_negtest(db, tags)`**: 8 broken shapes each rejected (non-thrown weapon,
  off-whitelist rig, right hand unequipped, left hand wrongly re-enabled on a
  single-hand family, drop weight out of band, soul-leak, scaling reverted to
  raw base, and a dual-thrower's left hand wrongly disabled).
- **Dry-run harness** (`py tools/patches/thrown_restore.py <mod.arz>`): loads
  the golden build41 arz directly, proves the premise (roster record starts
  disarmed), applies, and asserts **`db._modified` == exactly the 10 roster
  paths** (0 new records, 0 stray modifications outside the roster).

### Verification run (against `work/SoulvizierClassic/Database/SoulvizierClassic.arz`, md5 `eb8bc37775540f872003f873abf8e8be`)

```
premise: ar_archer_06.dbr chanceToEquipRightHand in overlay = 0.0 (0 => disarmed, restore required)
intended-only record delta: +0 added (must be 0 - in-place restore only)
modified records: 10 (roster size 10); stray modifications: 0
post: ar_archer_06.dbr RIGHT=100.0 LEFT=0.0 loot1[0]=records\xpack2\item\loottables\weapons\static\1h_ranged_01b.dbr life=54.0
  thrown_restore.verify: OK (10 records restored in place, 9 with confirmed reachable base pool membership, 1 orphan-in-vanilla flagged, 0 new records, 0 new pools)
  thrown_restore._negtest: OK (8 broken shapes each rejected)

thrown_restore DRY-RUN: PASS (0 new records; 10 records restored in place; verify OK; negtest OK)
```

### Gates

- `py -m py_compile tools/patches/thrown_restore.py tools/patches/__init__.py` - **PASS**.
- `py tools/patches/_check_registry.py` - **PASS** (14 modules, order hash
  `55c412e9b265...`).
- Full-tree grep for every roster record's basename across `tools/*.py` +
  `tools/patches/*.py` - only `thrown_wielders.py` (unregistered) also
  references them, and only as `clone_record` DONORS (read-only; it never
  mutates the donor record itself) - **0 collision risk**.
- `py tools/contracts/run_contracts.py --only souls,summons --arz
  work/.../SoulvizierClassic.arz` (fastest 2 domains; no map/resources
  needed) against the CURRENT (unmodified by this wave - no heavy build was
  run) build41 arz: **souls 0/0/0 clean**. `summons` shows 96 P0 / 556 P2
  pre-existing `MONSTER-MESH` / `SUMMON-PET-MESH` violations (bloodcave
  bodies, pitsprites, soul-pet meshes, arachnos/bat/boarmonstrous/etc.) -
  **confirmed via full-text search of the violations JSON that ZERO of the
  652 reference any of the 10 roster records**; this worktree lacks the full
  `Resources/` art tree (mesh files) needed for mesh-resolution checks, a
  pre-existing environment gap wholly unrelated to this module (the same
  caveat b58's own report flagged: "the in-run FAIL was the missing-art
  environment artifact"). The `map`/`resources`/`quests` contract domains
  need the 688 MB `Levels_merged.arc` + full `Resources/` tree and were not
  run, per the "no heavy build" constraint - this module makes zero map/
  Quests/resource changes, so they are not expected to be affected.

---

## PART 6 - OPEN ITEMS FOR WILL

1. **Naming** (amgoz1 creative bar). Tigerman `ar_archer_27/33` and all 3
   Machae variants currently carry a mod-authored "~ Archer" name tag from the
   disarm-era bow rework (base tags were "Elite Prowler"/"Sentinel" - also not
   a great fit for a thrower). Left untouched (a design-voice call, not a
   mechanical restore) - want an amgoz-pass once you see them throw in-game
   (e.g. "~ Skirmisher"/"~ Javelineer")?
2. **The 64 unreachable wielders** (Part 2c) - leave capped (default), lift
   the Atlantis park for Potamoi/Monkeyman specifically, or (not recommended
   this wave) reconsider the Ragnarok A5 cap.
3. **`am_assassin_15` orphan** - restored for consistency but has zero
   spawn effect alone (dead in vanilla TQ itself, not our regression). No
   action needed; flagged for awareness only.

---

## Appendix - reproduction

All probes read-only vs `work/SoulvizierClassic/Database/SoulvizierClassic.arz`
(md5 `eb8bc37775540f872003f873abf8e8be`) and the base game's
`Database/database.arz` (74,013 recs). Module self-test:
`py tools/patches/thrown_restore.py <golden.arz>`. Registry check:
`py tools/patches/_check_registry.py`.
