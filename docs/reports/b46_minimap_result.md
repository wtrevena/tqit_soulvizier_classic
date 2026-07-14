# b46 - Uber Dungeon minimap + area-label fix (ROUND 3, authoritative result)

> Fix for Will's 2026-07-13 report: in the Uber Dungeon (1) the drawn minimap does not line up
> with the level ("black void" under the player), and (2) the top-right area label reads
> "Village of Helos". Branch `feat/b46-minimap`. **This round-3 doc supersedes round 1 and round 2.**
> No heavy build; all proofs are dry-runs on COPIES of the canonical ground-truth map
> (`local/Levels_merged.arc`, .arc MD5 `60a62880`) + the SV 0.98i upstream. Regenerable probes +
> the verification harness are in the session scratchpad (`b46r3/probe_0x17*.py`, `verify_fix.py`,
> `verify_gates2.py`, `probe_index.py`, `probe_dungeon_parity.py`, `mint_guid.py`).

---

## 0. TL;DR - one reported bug, two mechanisms; round 3 CORRECTS the round-2 label no-op

| symptom | mechanism (ground-truth, b46r3) | fix | status |
|---|---|---|---|
| **1. minimap "black void"** | crypt_floor1's LEVELS-entry teleport-zone `dbr` was EMPTY -> its minimap TGA never composites onto a world-map page | assign `greece/delphi.dbr` (mapIndex 0) so the TGA composites on the Greece page at the level's own grid corner | **retained from r1/r2** (vet said keep); mechanism inferred, needs Will's in-game check |
| **2. "Village of Helos" label** | crypt_floor1's **0x17 REGION list is EMPTY** -> no region name resolves -> the banner retains the last region (Helos, the teleport origin) | inject a minted region GUID into crypt's 0x17 **REGION list** + add the matching SD (0x18) region record + Text tag | **CORRECTED in round 3** (r2 was a no-op) |

**What round 2 got wrong (vet HIGH, confirmed):** the 0x17 section's three leading GUID lists are
`[ENV][REGION][AUDIO]`, not `[layer][region]`. Round 2 read crypt's GUID `59c096c3...` as its
"region" GUID and appended an SD *region* record for it - but `59c096c3` is crypt's **AUDIO**-list
GUID (the "UberDungeon - Floor1" audio zone), and crypt's **REGION list is genuinely EMPTY** (count
0). The banner reads the REGION list, so appending an SD region for the audio GUID changed nothing
on screen. Round 3 targets the correct slot: it **adds a region entry to crypt's 0x17 REGION list**
(a map-side level-blob edit round 2 avoided) plus the matching SD record.

**All 29 verification gates PASS** (24 in `verify_fix.py` + 5 in `verify_gates2.py`; Section 5).
**Residual: neither symptom is in-game-confirmed** - static analysis cannot render, and no agent here
may launch TQ. The label fix now makes crypt structurally IDENTICAL to a shipped working single-
region dungeon (Section 2), so the static case is strong; both halves still want Will's eyes.

---

## 1. Ground-truth re-derivation of the 0x17 section (the round-3 correction)

Every level blob's `0x17` section (the baked detail/lighting layer) begins with three GUID lists,
then an opaque per-cell raster:

```
u32 magic = 1
u32 version
ENV list   : u32 count; count x { u8 index(1-based, per-level); u8 guid[16] }
REGION list: u32 count; count x { u8 index(1-based, per-level); u8 guid[16] }
AUDIO list : u32 count; count x { u8 index(1-based, per-level); u8 guid[16] }
raster ... (opaque; preserved verbatim)
```

**The on-screen top-right area-name banner is the level's REGION-list GUID resolved against the
world SD (0x18) REGION records.** Proof (all on the canonical map):

- **Byte-exact round-trip of this 3-list parse/serialize across ALL 2282 levels** (0 failures;
  `probe_0x17_parser.py`). The parse boundary (where the raster begins) is validated for every level.
- **Every level that shows a name carries exactly its SD-region GUID in this REGION list**
  (`probe_0x17b.py`): boss_arena -> 'Olympian Arena', startingcave01 -> 'Natural Cave',
  spartacryptlevel2 -> 'Ancient Tomb', gardenofmerchants -> 'Duister', darkforestenter -> 'Dark
  Forest', tfinale -> 'JoLandia'.
- **crypt_floor1's REGION list is EMPTY** (env=1 [UberDungeonLevel1], region=**0**, audio=1
  [`59c096c3` = "UberDungeon - Floor1" audio zone]). Byte proof: at offset 29 in crypt's 0x17 the
  region count is `00 00 00 00`; the `59c096c3` GUID sits in the AUDIO list at offset 38.

The index byte is a **per-level 1-based ordinal** (the SAME region GUID gets different indices in
different levels - 'Laconia Hills' is 1/1/2/3 across levels; `probe_index.py`), so it is a local
slot, not a global reference. A single region in an interior dungeon uses index 1: **1194 of 1195
single-region levels use index 1** (the sole exception is a giant OUTDOOR terrain level,
`3_1TheDunes09`, 0x06 = 1.09 MB). crypt is an interior dungeon, so index 1 is correct.

## 2. Symptom 2 - the area-label fix (round 3)

Give crypt_floor1 a real REGION identity, mirroring every shipped named dungeon:

1. **`inject_0x17_region()`** (in `tools/build_section_surgery.py`) appends a minted region GUID to
   crypt_floor1's 0x17 REGION list via the proven `parse_0x17_header`/`build_0x17_header` round-trip.
   ENV + AUDIO lists, the 0x17 raster, and every other section (incl. navmesh 0x0b) stay
   byte-identical; only the REGION list grows by one 17-byte entry (index 1). Wired into the SV-only
   structural-patch step in `svaera_plus_portals.main()` (`apply_0x17_region_labels`), which runs
   before the 0x0b navmesh injection (that injection preserves 0x17 verbatim - proven in Section 5).
2. **`add_sv_region_labels()`** appends the matching SD (0x18) REGION record for the SAME minted GUID
   (additive, GUID-keyed -> existing regions + the audio/miniboss tail byte-identical). Its display
   name is a Text.arc tag.

**The airtight static argument:** crypt's post-fix 0x17 = env 1 / region 1 / audio 1, and its blob
section set `[0x05, 0x14, 0x06, 0x0b, 0x17]` is **byte-for-byte the same shape as the WORKING
startingcave01 and spartacryptlevel2** (single-region interior dungeons that display 'Natural Cave'
/ 'Ancient Tomb' throughout, with no dedicated region-volume section). The fix makes crypt
structurally identical to shipped, working dungeons - not a novel structure.

**Minted region GUID** `67a0a0fa76ed27fc22ed82d2636b3b81`, collision-checked against every GUID in
the map (SD env/region/tail + every level's 0x17 GUIDs + level GUIDs = 32,110 GUIDs, 0 collisions;
`mint_guid.py`). A FRESH GUID (not the audio `59c096c3`) is used so nothing is dual-defined across
the audio + region lists - this also clears the round-2 vet's LOW note.

**Name = "The Obsidian Halls"** (tag `tagSVCRegionObsidianHalls`): matches the hub NPC the player
clicks ("Traveler: The Obsidian Halls"), the room content (Kravmoloch, Keeper of the Wheel of the
Obsidian Halls), and the amgoz1 flavor bar. The travel-arrival tag `tagSVCHelosToUber` still reads
"The Uber Dungeon"; to make the banner match that instead, change the label + the
`tagSVCRegionObsidianHalls` Text value. (Flagged for Will - one-line either way.)

## 3. Symptom 1 - the minimap fix (retained from r1/r2)

Unchanged and vet-RETAINED: `apply_zone_dbr_overrides()` assigns each relocated zoneless SV interior
a mapIndex-correct existing zone so its minimap TGA composites onto the continent page at the level's
own grid corner. crypt_floor1: empty `dbr` -> `greece/delphi.dbr` (mapIndex 0; Delphi is the nearest
already-composited content). 14 levels total; only the `dbr` field changes (LEVELS is self-
delimiting). Georeference (numeric): crypt grid corner `(-2578,0,-2682)`, footprint X[-2578,-2258]
Z[-2682,-2362] CONTAINS the boat-dialog teleport target `(-2438,-2450)`. Mechanism is inferred (the
Helos-hub natural experiment: every zoneless destination is reported-broken, every zoned one is not);
still wants Will's in-game composite check.

## 4. Scope - why crypt_floor1 is the ONLY level needing the label fix

The Helos hub's direct teleport destinations (`build_quest_files.py`) all land in a level that
already resolves a region name - EXCEPT the Uber Dungeon:

| hub destination | lands in | 0x17 region | banner |
|---|---|---|---|
| Uber `(-2438,10,-2450)` | crypt_floor1 | **EMPTY** | **"Village of Helos" (THE bug)** |
| Garden | gardenofmerchants | 'Duister' | OK |
| Secret `(-2396,2,-5790)` | darkforestenter | 'Dark Forest' | OK (landing resolves) |
| Sparta | spartacryptlevel2 | 'Ancient Tomb' | OK |
| BossArena | boss_arena | 'Olympian Arena' | OK |
| Warband / Dorus / Tantalus / Charon / Mnemophage / Ephialtes | silkroad / medea / styx / judgment | (base regions) | OK |

crypt_floor1 is the UNIQUE level entered directly from the Helos plaza whose region list is empty, so
it is the only one that retains the Helos label. The secret_place SUB-rooms (behindthesp,
forestobsidiantransition, murderbossroom, woodscorner, secretforest2, pillagedvillage) also have
empty/unresolved region lists, but they are reached by WALKING from the "Dark Forest" landing, so
they retain "Dark Forest" (thematically correct for a forest cluster), never "Village of Helos".
coldtombs is vestigial (no navmesh, unreachable). None of these is the reported bug; minting per-room
labels would be worse, and touching the shared forest region GUID risks regressing darkforest's
working "Dark Forest" label. Documented as accepted residual (Section 6).

## 5. Verification - 29/29 gates PASS (dry-run on copies)

`verify_fix.py` (24 gates):
- **Label:** crypt 0x17 REGION list EMPTY before -> 1 entry (minted GUID) after; ENV+AUDIO lists
  byte-identical; raster (30740 B) byte-identical; +17 bytes exactly; every non-0x17 section
  byte-identical INCLUDING **navmesh 0x0b (320324 B) BYTE-IDENTICAL**; section set/order unchanged.
- **Pipeline-order replay** on the SV-source crypt blob (0x0a): +region -> +0x0b -> 0x0a stripped,
  0x0b present, **minted region SURVIVES the 0x0b injection** (label edit persists to final blob).
- **SD:** round-trips byte-identical; +1 region (293->294); appended region = minted GUID, name
  "The Obsidian Halls", tag `tagSVCRegionObsidianHalls`; ENV list + opaque tail (52762 B) + all prior
  regions byte-identical; minted GUID not previously an SD region.
- **Cross-resolve:** crypt's new 0x17 region GUID -> new SD region -> tag/name. PASS.
- **Minimap:** crypt dbr EMPTY -> `greece/delphi.dbr`; 14 levels, only `dbr` field changes, 0
  non-target changes; georeference footprint contains the teleport target.
- **Untouched:** QUESTS(0x1b) not referenced by any edit (sha `226461e7`, 11460 B, byte-identical by
  construction); 0x17 injection targets ONLY crypt_floor1.

`verify_gates2.py` (5 gates): MAP-SD-1 (the new SD tag is extracted by the contract scanner and
resolves in `build_text_arc` TEXT_FIX_TAGS = "The Obsidian Halls"); canonical SD has NO region for
`59c096c3` (round-2 never leaked to main; final state collision-clean); single-region-index-1 is the
convention (1194 at idx 1, non-1 = the one outdoor terrain level); **crypt POST-FIX section set ==
working startingcave01 dungeon** `[0x05,0x14,0x06,0x0b,0x17]`.

py_compile: PASS on all three changed files.

**Blob-diff summary:** the only changed map sections are crypt_floor1's **0x17** (+17 B, one REGION
entry) and the world **SD** (+1 region, +111 B) and the 14 LEVELS `dbr` fields. QUESTS, GROUPS,
BITMAPS, DATA2, and every `0x0b`/`0x05`/`0x06`/`0x14` section (crypt's and every other level's) are
byte-identical. The 256-window QUESTS parity is untouched; every navmesh is byte-identical.

## 6. Confidence + residuals (honest)

- **Label (symptom 2): HIGH static confidence.** The region -> SD -> tag mechanism is proven on 2282
  levels; the fix makes crypt's 0x17 IDENTICAL in shape to two shipped, working single-region
  dungeons (startingcave01, spartacryptlevel2). The only thing static analysis cannot do is render.
- **Minimap (symptom 1): MEDIUM-HIGH.** Compositing mechanism inferred (well-supported); wants a
  visual check.
- **In-game gate (Will's, not doable by any agent here):** DEV launch after a Steam restart, click
  "Traveler: The Obsidian Halls", enter the Uber Dungeon, confirm (a) the drawn map appears under the
  player (no black void) and (b) the banner reads "The Obsidian Halls", not "Village of Helos".
- **Accepted residual:** the secret_place sub-rooms retain "Dark Forest" (correct theme, not the
  reported bug); coldtombs is vestigial. The banner-name choice ("The Obsidian Halls" vs "The Uber
  Dungeon") is flagged for Will (one-line change).

Deploy: rebuild the map (`py tools/svaera_plus_portals.py`, canonical + TESTHUB) AND Text.arc
together (DEPLOY COUPLING: the SD region references `tagSVCRegionObsidianHalls`; `contract_sd_tags`
fails loud if the map ships without the Text tag), then deploy both to `SoulvizierClassicDEV`.
