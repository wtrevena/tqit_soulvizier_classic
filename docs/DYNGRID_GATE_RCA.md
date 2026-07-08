# What gates GridEntranceDynamic portal VISIBILITY and OPENNESS — full RCA + the fix

> 2026-07-07. Root-cause of Will's report (TESTHUB, standing in the blood-cave first room):
> **NO hub portals visible.** Disassembly of `backups/game_dll/Game.dll.original`
> (5,835,264 B, ImageBase 0x10000000) and `Engine.dll.original` + the record/template bytes.
> All VAs below are in those images. Reproduce with the read-only scripts:
> `tools/debug/recon_dyngrid_gate.py` (records+templates), `tools/debug/disasm_game_dyngrid.py`
> + `disasm_visfield.py` + `disasm_vtable.py` (Game.dll visibility class),
> `tools/debug/disasm_eng.py`-style dumps of Engine.dll (`SetPortalIsOpen`, `GetPortalOnOtherSide`,
> the cross-region linker). `py` launcher, `PYTHONIOENCODING=utf-8`, capstone+pefile.

---

## 0. Executive verdict

**Every invented door + the whole test hub places `records\quests\portal_olympianarena1.dbr`
(Class `GridEntranceDynamic`) as the ENTRANCE, and that record ships with
`visibilityMode = NeverVisible`. That single field is why the portals are invisible.**

Two INDEPENDENT properties of a `GridEntranceDynamic` are controlled by two different things:

| Property | Controlled by | Value now | Effect now |
|----------|---------------|-----------|------------|
| **Mesh renders?** (visible) | DBR `visibilityMode` field → entity `[obj+0x3ec]` | `NeverVisible` (=1) | mesh HIDDEN at spawn |
| **Portal teleports?** (open) | Engine `Portal[+0xfc]` "IsOpen", set by the entity's activate + Open/Close | closed at spawn | inert until quest opens it |

- **Visibility is a pure DBR concern.** `visibilityMode=AlwaysVisible` makes the mesh render
  at spawn, unconditionally, with NO quest — proven below and base-game-precedented.
- **Openness is NOT a DBR concern.** The `GridEntranceDynamic` activate method CLOSES its portal
  at every spawn (`SetPortalIsOpen(0)`), and the ONLY opener is `Action_OpenDynGridEntrance`
  (`bossarena.qst`), which needs the quest ADOPTED on the character. **No DBR field can make a
  `GridEntranceDynamic` born-open.**

**THE FIX (shipped, DB-only, no map rebuild): set `portal_olympianarena1`'s `visibilityMode` to
`AlwaysVisible`** (`tools/apply_svc_patches.py` `_make_portals_unconditionally_visible`, wired into
`apply_all_extended_patches` + a fail-loud invariant `_verify_portals_visible`). Because ALL portal
instances in BOTH the canonical and TESTHUB maps reference this one record, patching it makes every
portal (A1 maze03→Uber, Sparta, Garden, Secret Place, and all 20 hub portals) visible at once, on
FRESH and PRE-EXISTING characters. This removes the dependency on `bossarena.qst`'s
`Action_ShowNpc`. **Teleport openness is analyzed in §5 (options ranked); it is a separate, quest /
class-swap concern that is walk-test-gated, not a DBR field.**

---

## 1. The record + template (byte evidence)

`records\quests\portal_olympianarena1.dbr` (entrance; ships in upstream SV 0.98i AND the built mod DB):
```
templateName, database\Templates\GridEntranceDynamic.tpl
Class,         GridEntranceDynamic
visibilityMode, NeverVisible          <-- THE GATE
mesh,          XPack\SceneryUnderground\TowerJudgement\SetDress\TJ_JudgementRoom_PortalObject_01.msh
quest, 0 ; scale, 1 ; (anim/shadow fields)
```
`records\quests\portal_olympianarena2.dbr` (landing): Class `GridExitOneWay`, `invisibleInWorld,1`,
no `visibilityMode` field. (A one-way exit endpoint; left untouched by the fix.)

**Template `database\Templates\GridEntranceDynamic.tpl`** (from `Toolset/Templates.arc`, read via
`tools/arc_patcher.ArcArchive`): `visibilityMode` is a **picklist** with exactly three values:
```
Variable { name = "visibilityMode" class = "picklist" type = "string"
           defaultValue = "AlwaysVisible;NeverVisible;VisibleWhenOpen;" }
```
For a TQ picklist the FIRST listed value is the default, so an ABSENT `visibilityMode` defaults to
`AlwaysVisible`. There is NO `initiallyOpen`/`startOpen`/state field anywhere in the template chain
(`GridEntranceDynamic.tpl` → includes `GridEntrance.tpl` → `Tile.tpl`). The only Config fields are
`visibilityMode` and `allowUnconnected` (a bool "allow portal to be unconnected", not an open flag).

## 2. Base-game precedent (decisive)

All 10 base-game `GridEntranceDynamic` records + their `visibilityMode`:

| record | visibilityMode | note |
|--------|----------------|------|
| `xpack3\scenery\atlantis\08tartarus\nature\cliffs\entrance01.dbr` | **AlwaysVisible** | the VISIBLE outer Tartarus cave entrance |
| `xpack3\scenery\atlantis\08tartarus\structure\infrastructure\tartarus_entrance01.dbr` | *(absent → AlwaysVisible)* | |
| `xpack\quests\objects\xsq15_mirrorportal.dbr` | *(absent → AlwaysVisible)* | |
| `xpack\sceneryunderground\hadescrypt\setdress\hc_goldmirror01.dbr` | *(absent → AlwaysVisible)* | |
| `xpack3\tartarus\entryportalobject.dbr` | NeverVisible | quest-gated (Tartarus entry) |
| `xpack4\quests\item\teleport\x4_mq_jc002_*_gridentrancedynamic_a.dbr` (x2) | NeverVisible | quest-gated |
| `xpack\sceneryunderground\hadescave\setdress\hc_orpheusquest_portalobject_01.dbr` | NeverVisible | quest-gated (Orpheus) |
| `xpack\sceneryunderground\hadescrypt\setdress\hc_eurydicequest_portalobject_01.dbr` | NeverVisible | quest-gated (Eurydice) |
| `xpack\sceneryunderground\towerjudgement\setdress\tj_judgementroom_portalobject_01.dbr` | NeverVisible | quest-gated (the mesh our portal shares) |

**Pattern:** base game uses `NeverVisible` for portals that must stay hidden until a quest reveals
them (Orpheus/Eurydice/Tartarus-entry), and `AlwaysVisible` for a portal the player should SEE
before it opens (the outer Tartarus entrance). Our hub/door portals want the latter. Note the string
`"AlwaysVisible"` does not even appear in Game.dll — it is the parser's else/default branch (§3),
confirming it is the "just render it" case.

## 3. The visibility mechanism (Game.dll disassembly)

The `visibilityMode` string, its enum, and its consumer all live in **Game.dll** (NOT Engine.dll —
Engine.dll contains none of the strings). Strings: `visibilityMode`@0x1034a5b0,
`NeverVisible`@0x1034a5a0, `VisibleWhenOpen`@0x1034a5c0 (`AlwaysVisible`: absent).

**Parser — `GridEntranceDynamic::Read` @ 0x101ae3eb** (maps the DBR string to the enum
`[obj+0x3ec]`):
```
0x101ae3ea push 0x1034a5b0            ; "visibilityMode"  -> ReadStringField(...)
0x101ae434 mov  edx,0x1034a5a0        ; "NeverVisible"
0x101ae445 call 0x10003e60 ; strcmp
0x101ae44c je   0x101ae45a
0x101ae44e mov  [edi+0x3ec],1         ;  == NeverVisible  -> 1
0x101ae45a mov  edx,0x1034a5c0        ; "VisibleWhenOpen"
0x101ae463 call 0x10003e60 ; strcmp
0x101ae46f and  eax,2
0x101ae472 mov  [edi+0x3ec],eax       ;  == VisibleWhenOpen -> 2, else (AlwaysVisible/absent) -> 0
```
So `[obj+0x3ec]` = {AlwaysVisible=0, NeverVisible=1, VisibleWhenOpen=2}. The ctor
(0x101aed4b) defaults it to 0.

**Consumer — the activate/setup method @ ~0x101ae2xx** (runs on level entry). The relevant tail:
```
0x101ae2d0 cmp [edi+0x2fc],0 / jne .. / call [vtbl+0x120]   ; create the Portal if absent (born open)
0x101ae2f1 call SetPortalIsOpen(0)                          ; *** CLOSE the portal (UNCONDITIONAL) ***
0x101ae2f7 cmp [edi+0x3ec],1                                ; visibilityMode == NeverVisible?
0x101ae2fe jne 0x101ae30c                                   ;   NOT NeverVisible -> skip the hide
0x101ae306 call [vtbl+0xb0](0)                              ;   Show(0) = HIDE the mesh (ONLY if NeverVisible)
```
=> The mesh is hidden at spawn **only** when `visibilityMode == NeverVisible`. `AlwaysVisible`(0)
and `VisibleWhenOpen`(2) skip the hide → the mesh renders. This is INDEPENDENT of the portal open
flag, which is closed a few instructions earlier regardless of `visibilityMode`.

`VisibleWhenOpen` differs from `AlwaysVisible` only in the animated Open/Close transitions
(0x101ad8bc / 0x101ada73 / 0x101ad935: `cmp [+0x3ec],2` → toggle mesh Show(0/1) as the portal
opens/closes). For our "always render it" goal, `AlwaysVisible` is the correct pick (renders even
while the portal is closed).

## 4. The openness mechanism (Game.dll + Engine.dll)

- **Every Engine Portal is BORN OPEN.** Portal ctor (Engine 0x10205dcd) `mov word[esi+0xfc],0x0101`.
- **`GridEntrance::SetPortalIsOpen(bool)`** (Engine 0x10194d60, imported into Game.dll as
  `[0x1031fac8]`): `mov ecx,[this+0x2fc] (the Portal) ; mov al,[esp+4] ; mov [ecx+0xfc],al`. So the
  bool is written DIRECTLY to `Portal[+0xfc]`: `SetPortalIsOpen(1)` → open, `(0)` → closed.
- **The activate method CLOSES the portal at every spawn** (`SetPortalIsOpen(0)` @ 0x101ae2f1),
  and the entity's open-state field `[obj+0x3e4]` (ctor default 1; persisted across saves at Load
  0x101ade8a: `saved==0 → 3 (open), else → 1 (closed)`). So a FRESH `GridEntranceDynamic` spawns
  CLOSED; once opened, the open state persists in the save.
- **The ONLY opener is the quest.** `bossarena.qst` step-1 trigger: `Condition_OnLevelLoad`
  (level-agnostic, fires on every load, `canReFire=1`) → `Action_ShowNpc(portal_olympianarena1)` +
  `Action_OpenDynGridEntrance(portal_olympianarena1)` + `Action_UnlockFixedItem(portal_olympianarena1)`.
  `Action_OpenDynGridEntrance` → the entity's Open() (0x101ad910) → `SetPortalIsOpen(1)`.
  `Action_ShowNpc` is what currently makes the mesh appear (only if the quest fires).
- **The teleport itself** (why the pair works off pure 0x14, no 0x06): the cross-region path linker
  (Engine 0x101f3680) requires, per portal: `Portal[+0xfc]` open (0x101f36f4), dest region resolved
  by GUID (`GetConnectedRegion` 0x102063e0), dest `Level[+0x6a48]` navmesh-loaded (0x101f37ff), AND
  the PAIRED portal open — `GetPortalOnOtherSide(exit_uid)` (0x1020dfd0) searches the DEST region's
  portal list (`region[+0x8c..0x90]`) for a portal whose UniqueId (`portal+4`) == the entrance's
  exit id, then checks `[+0xfc]` (0x101f3854). The paired portal is the `GridExitOneWay` LANDING
  entity's portal (born open, never self-closed — `GridExitOneWay` is a plain `GridEntrance`
  subclass with none of the Dynamic state machine). So the destination needs NO `0x06` GridSystem
  descriptor for this teleport; the landing entity supplies the paired portal. (The Sparta-wave
  "static GridEntrance needs a 0x06 pair" note was a mis-generalization from a base-game correlation
  — base static entrances happen to front `0x06` GridSystem dungeons — not an engine requirement of
  the 0x14 path.)

**Net:** the entrance portal is the ONLY closed link. Make IT open and the whole hop works.

## 5. Openness — the teleport half. ROUND 2: SOLVED UNCONDITIONALLY (class-swap), disasm-proven.

Round 1 shipped VISIBILITY (§0) and left openness "walk-test-gated" with 3 ranked options. Round 2
was tasked to DELIVER an unconditional openness mechanism that does NOT depend on per-character
quest adoption (the `wf_c0012e88-64a` goal + the brief). It is now settled with full disassembly +
byte evidence: **class-swap the ENTRANCE record `portal_olympianarena1` from `GridEntranceDynamic`
to the static `GridEntrance`, and reformat every entrance instance's 0x14 from 48 -> 60 bytes.**
A static `GridEntrance` is BORN OPEN and NEVER self-closes, so the portal teleports for a FRESH
AND a PRE-EXISTING character with NO quest. The five load-bearing facts (all reproduced round 2):

1. **`SetPortalIsOpen` has EXACTLY 3 call sites in ALL of Game.dll, and 0 in Engine.dll**
   (`disasm_setportalisopen_sites.py` on Game IAT slot 0x1031fac8;
   `disasm_gridentrance_engine.py` scans Engine .text E8 calls to the export 0x10194d60):
   - `0x101ad8dd` arg 0 (close) in `GridEntranceDynamic::Close` (fn 0x101ad8b0)
   - `0x101ad92f` arg 1 (open)  in `GridEntranceDynamic::Open`  (fn 0x101ad910; what the quest calls)
   - `0x101ae2f1` arg 0 (close) in `GridEntranceDynamic::activate` (fn 0x101ae140; runs at spawn)
   ALL THREE belong to the `GridEntranceDynamic` state machine. **No static `GridEntrance` code
   path can ever close a portal.** So a static `GridEntrance` portal, once created open, STAYS open.

2. **The Engine Portal is born OPEN** (Portal ctor writes `[+0xfc]=0x0101`, §4). A static
   `GridEntrance` runs `OnAddToLevel` (Engine 0x101950f0) -> base add + `CreatePortal`
   (vtbl[+0x120] -> 0x10194e60), and **`OnAddToLevel` does NOT call SetPortalIsOpen**
   (disassembled: it calls only base OnAddToLevel 0x102415e0 then CreatePortal). Born-open, no close.

3. **`GridEntrance` is a fully instantiable engine class** used by **153 base-game records** (every
   cave mouth: Silk Road / Egypt / Greece / Rhakotis, template `Engine\GridEntrance.tpl`), each
   born-open + always-visible with NO quest. It exports ctor (0x10195340), vtable
   `??_7GridEntrance` (0x102f7620), `Read(BinaryReader)` (0x10195240), `CreatePortal`,
   `GetConnectedPortalId/RegionId`, `RTTI_new`. So `Class,GridEntrance` records instantiate via
   Engine RTTI. **These 153 records are the decisive base-game precedent** for an always-open,
   always-visible cross-level entrance with no quest (exactly what our doors want).

4. **The teleport RESOLUTION is identical for static and dynamic and reads ONLY the 0x14 binding
   (no 0x06 dependency).** `GridEntrance::GetConnectedPortalId` (0x10195070) = `return [this+0x2d8]`
   (the exit_uid); `GridEntrance::GetConnectedRegionId` (0x10195060) = `return [this+0x2e8]`
   (the dest_guid). Both read the `[+0x2c8..+0x2f4]` binding block that `GridEntrance::Read`
   populates from the 0x14 payload. The cross-region linker uses exit_uid -> `Region::GetPortal`
   (0x1020dfd0) to find the PAIRED landing portal (the `GridExitOneWay`, born-open) + dest_guid ->
   dest region. **No 0x06 GridSystem descriptor is consulted for the portal teleport** (0x06 is
   the separate tile-streaming subsystem). This is the SAME pure-0x14 path A1/Sparta already rely
   on; the class-swap keeps it byte-for-byte and only removes the quest-open gate. The Sparta-wave
   "static GridEntrance needs a 0x06" note was a mis-generalization from a base-game correlation
   (base static mouths happen to also front 0x06 dungeons), disproven by facts 1+4.

5. **The 0x14 payload format is CLASS-COUPLED (the one thing that must also change in the MAP).**
   Byte-measured from the merged map (`compare_gridentrance_0x14.py`, keyed by INSTANCE index):
   - native static `GridEntrance` (SilkRdDngEntrance_C01_Ext, HV01 inst[30]) 0x14 = **60 bytes** =
     `[12B (2,0,1) prefix 02000000 00000000 01000000] + [48B mouth+exit+dest]`.
   - our `GridEntranceDynamic` (A1 maze03 inst[447]) 0x14 = **48 bytes** = `[48B binding]`, NO prefix.
   `GridEntrance::Read` consumes 12+48=60 (its base Read eats the 12-byte generic header, then it
   reads 12 dwords = 48-byte binding into [+0x2c8..]). `GridEntranceDynamic` has its own 48-byte
   binary-Read override. So **if we swap the Class to `GridEntrance` we MUST prepend the 12-byte
   `(2,0,1)` prefix to every entrance instance's 0x14** (48 -> 60), or the base Read would eat 12
   bytes of the binding and misalign. This is a map rebuild (both artifacts), keyed to the record
   swap. The reformatted 0x14 then byte-matches the proven-working Silk Road mouth's exact framing.

**No base-game collateral:** `portal_olympianarena1` / `portal_olympianarena2` are placed ZERO
times in the base-game map (`count_portal_instances.py` on the base Levels.arc = 0/0); they are
used only by our mod (SV boss-arena chain + our invented doors). So changing the record's class /
0x14 has no vanilla side-effect.

**Scope of the class-swap fix (round 2):**
- DB: `portal_olympianarena1.dbr` -> Class `GridEntrance`, templateName `Engine\GridEntrance.tpl`,
  drop the Dynamic-only fields (`visibilityMode`, `quest`, `openingAnimationSpeed`,
  `openIdleAnimationSpeed`), keep `mesh`/`scale`/`actorHeight`/`actorRadius` (mirror a native
  GridEntrance record's minimal field set). Landing `portal_olympianarena2` UNTOUCHED (already
  `GridExitOneWay`, born-open, invisibleInWorld=1).
- MAP: prepend the 12-byte `(2,0,1)` prefix to EVERY `portal_olympianarena1` instance's 0x14 in
  BOTH `Levels_merged.arc` (7 entrances) and `Levels_merged_TESTHUB.arc` (17 entrances). Landings
  keep their 48-byte 0x14. This is the `svaera_plus_portals` map build (the entrance 0x14 constants
  in `build_section_surgery.py` become 60-byte; the A1/Sparta already-in-build25 entrances get the
  same treatment because they reference the same record).

Options 1 (rely on quest window) and 3 (fold into `sv_commonmechanics`) are SUPERSEDED: they leave
openness dependent on quest adoption, which the brief + `wf_c0012e88-64a` explicitly forbid. The
class-swap makes openness a pure raw-data property (born-open class + matching 60-byte binding).
The round-1 `visibilityMode=AlwaysVisible` fix becomes REDUNDANT for the entrance (a static
`GridEntrance` renders unconditionally) but is kept harmless/idempotent as belt-and-suspenders
until the swap lands, then removed to avoid setting a field the GridEntrance template lacks.

## 6. IMPLEMENTED (round 2) - what the fix touches + gate results

### Code (2 halves, must ship coupled)
- **DB half** `tools/apply_svc_patches.py`: `_make_portals_born_open_gridentrance(db)` swaps
  `portal_olympianarena1.dbr` Class GridEntranceDynamic -> `GridEntrance`, templateName ->
  `Engine\GridEntrance.tpl`, the arz per-record TYPE string -> `GridEntrance`, and DROPS the
  Dynamic-only fields (visibilityMode/quest/opening*/openIdle*/... ) while KEEPING mesh/scale/
  actor* (mirrors a native GridEntrance record; the mesh renders because GridEntrance.tpl includes
  Tile.tpl which defines mesh). `_verify_portals_born_open(db)` asserts the entrance is a clean
  GridEntrance (Class + record_type + templateName + mesh present + no residual Dynamic fields).
  Both wired into `apply_all_extended_patches` with a fail-loud `SystemExit`. Idempotent (a second
  build no-ops on an already-GridEntrance record). The `_1x` alias (FixedItemTeleport) and the `_2`
  landing (GridExitOneWay) are untouched.
- **MAP half** `tools/build_section_surgery.py`: `GRIDENTRANCE_0x14_PREFIX = (2,0,1)` (12 bytes) +
  a block in `_normalize_spec` that prepends it to EVERY `portal_olympianarena1` entrance's
  `x14_payload` (48 -> 60 bytes; landings keep 48). This flows through BOTH injection paths
  (shared step-6/7 in `svaera_plus_portals.py` and `inject_into_sv_only_blob`), so all entrances in
  BOTH artifacts get the 60-byte GridEntrance 0x14 with NO per-site edits. Idempotent-guarded.
  Rebuild: `py tools/svaera_plus_portals.py` (canonical) + `SVC_TEST_HUB=1 py ...` (TESTHUB).

### DEPLOY COUPLING (critical - the two halves are byte-locked)
A class-swapped entrance is read by `GridEntrance::Read` which consumes a **60-byte** 0x14. The
old maps wrote a **48-byte** 0x14 for the Dynamic class. Deploying the swapped arz against a
48-byte-0x14 map (or vice-versa) MISALIGNS the binary read -> visible-but-inert or worse. So the
new arz and the two new maps MUST ship together. Both fail-loud invariants enforce their own half.
`arz`+`Text` still ship together (this adds no tags -> Text.arc unaffected, validate_tags unaffected).
Quests.arc: NO change needed - `bossarena.qst`'s `Action_OpenDynGridEntrance`/`Action_ShowNpc`
become harmless no-ops (the record is no longer a DynGrid; TQ quest actions are RTTI-filtered by
class, so a non-DynGrid record is skipped, not crashed - and build25 already fires these actions
against these records without crashing).

### GATE RESULTS (all PASS, both artifacts)
- **DB build** (all fail-loud invariants incl. `_verify_portals_born_open` + the 4 Toxeus/soul
  invariants): PASS, exit 0. `tools/debug/gate_portal_visibility.py <arz>`: PASS (entrance = clean
  born-open GridEntrance; landing = untouched GridExitOneWay; alias = FixedItemTeleport).
- **Map openness** `tools/debug/gate_portal_openness.py`: canonical 7/7 entrances 60-byte + prefix
  + non-zero dest, 9 landings 48-byte, pairing intact; TESTHUB 17/17 + 19 landings, pairing intact.
- **Byte-exemplar match** `tools/debug/compare_gridentrance_0x14.py`: our rebuilt entrance 0x14 is
  byte-identical in framing to the WORKING native Silk Road cave mouth (both 60B, prefix
  `020000000000000001000000` + mouth/exit/dest) - the engine reads that mouth correctly on every
  blood-cave entry, so it reads ours identically.
- **Collateral** `tools/debug/gate_openness_collateral.py` (vs build26) + `gate_doors_hub.py`
  collateral (vs build25): PASS - only the portal-entrance blobs changed (+12B/entrance in 0x14
  only), **0 navmeshes (0x0b) changed**, QUESTS/GROUPS/SD/BITMAPS byte-identical.
- **Standing map gates**: `verify_merged_bc_navmeshes` 24/24 (both artifacts);
  `entrance_landing_check --check-merged` PASS (native blood-cave mouth intact, 508 cells dY 0.00);
  full re-parse 2282 levels / 0 bad offsets / 0 bad magic (both). `gate_doors_hub.py` placement +
  crosstalk + hubidentity + c1 + c3 + c4 all PASS. `gate_sparta_placement.py` A-workstream (Sparta
  portals) PASS with the 60-byte entrance format (its 2 B2-caravan FAILs are pre-existing build24
  coord staleness, unrelated to this fix).

### GATE 3 (unconditional-open) - argued from data, not hope
A static `GridEntrance` portal has **no per-character open-state** anywhere. At every level load the
Engine creates its Portal BORN OPEN (`Portal[+0xfc]=0x0101`) and NOTHING closes it (fact 1:
`SetPortalIsOpen(0)` has only GridEntranceDynamic-class callers). There is no quest, no token, no
adoption, no `.que`/Quest.myw entry, and no `[obj+0x3e4]` saved open-state involved (that field is
the Dynamic class's; the static class never touches it). Therefore a FRESH character and a 24h-old
PRE-EXISTING character both get an always-open, always-visible portal, deterministically, from the
raw map+DB bytes alone. This is exactly `wf_c0012e88-64a`'s goal: "portals open from raw data, no
quest dependency."

### New/edited files (round 2)
- `tools/apply_svc_patches.py` (born-open swap + invariant, replaces the round-1 visibility patch),
  `tools/build_section_surgery.py` (60-byte entrance prefix in `_normalize_spec` + mechanism
  comments), `tools/debug/gate_portal_openness.py` (NEW map gate),
  `tools/debug/gate_openness_collateral.py` (NEW collateral gate),
  `tools/debug/gate_portal_visibility.py` (rewritten -> born-open arz gate),
  `tools/debug/gate_doors_hub.py` + `gate_sparta_placement.py` (updated for 60-byte entrances),
  `tools/debug/compare_gridentrance_0x14.py` + `count_portal_instances.py` +
  `disasm_activate_flow.py` + `disasm_class_vtables.py` + `disasm_vtable_slots.py` +
  `disasm_setportalisopen_sites.py` + `disasm_gridentrance_engine.py` (NEW read-only evidence).
- Rebuilt: `local/Levels_merged.arc` + `local/Levels_merged_TESTHUB.arc` (baselines saved as
  `*.build26-baseline.arc`). NOT deployed/committed (main session owns that + the coupled arz build).
