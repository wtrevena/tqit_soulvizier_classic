# SoulvizierClassic Crash Analysis Report

Date: 2026-03-02

## Executive Summary

The game crashes are caused by **32-bit virtual address space exhaustion** in the TQ
Anniversary Edition engine. The 32-bit TQ.exe (with LAA, ~4 GB limit) cannot sustain the
combined memory footprint of the base game + SoulvizierClassic mod resources under gameplay
load. When GPU texture/mesh creation fails, the D3D11 rendering code dereferences a null
pointer and crashes.

**This is a game engine bug** (no null-check after D3D resource creation failure) that we
cannot fix directly, but we can reduce the probability of triggering it by optimizing the
mod's resource footprint.

## Crash Statistics

- **43 crash dumps** over 11 days (Feb 20 – Mar 2, 2026)
- All crashes: `0xc0000005` (EXCEPTION_ACCESS_VIOLATION)
- Settings reduced to absolute minimum (TEXTURES: 0, SHADOWS: 0, DETAIL: 0) — still crashes
- Fresh boot with only Cursor + game running — still crashes

### Crash Distribution by Date

| Date   | Crashes | Notes |
|--------|---------|-------|
| Feb 20 | 2       | Database/zone loading crashes |
| Feb 21 | 4       | Mixed crash types |
| Feb 22 | 12      | 1 map loading crash + 11 rendering crashes |
| Feb 28 | 7       | All rendering crashes |
| Mar 1  | 14      | All rendering crashes |
| Mar 2  | 4       | All rendering crashes (even at min settings) |

## Crash Signatures

### Type 1: D3D11 Rendering Crash (~90% of all crashes)

```
CreateDirect3D11DeviceFromDXGIDevice + 769492 bytes
```
- Address: always 0x6be19214 (deterministic)
- Parameters: 0x0 0x69 → null pointer + offset 0x69 = reading member from null D3D object
- ECX = 0x0 (null) in all instances
- Preceded by dozens of "Couldn't initialize resource" / "CreateTexture error" warnings

**Root cause:** D3D11 texture or buffer creation returns null due to resource exhaustion.
Game code does not null-check the result before dereferencing.

### Type 2: GraphicsFont/ResourceLoader Chain (~5%)

```
GAME::GraphicsFont::Initialize → GAME::Resource::GetLoadedState →
GAME::ResourceLoader::LoadResource → GAME::Display::Render
```

Same underlying cause — resource loading fails during rendering, null propagates.

### Type 3: Map Loading Crash (1 occurrence, Feb 22)

```
GAME::World::LoadMap + 743 bytes
```

Occurred during initial map load. Possibly related to our hybrid-merged Levels.arc.

### Type 4: Database/Zone Loading Crash (1 occurrence, Feb 20)

```
GAME::ZoneManager::~ZoneManager → GAME::Engine::LoadDatabase
```

Early crash during database loading. May have been a one-time issue.

## Memory Footprint Analysis

### TQ.exe Process Constraints
- **Architecture:** PE32 (32-bit) with LARGE_ADDRESS_AWARE
- **Max virtual address space:** ~4 GB on 64-bit Windows
- **GPU:** AMD Radeon 780M (integrated, shares system RAM for VRAM)

### Mod Resource Breakdown

| Archive | Compressed | Decompressed | Content |
|---------|-----------|-------------|---------|
| Levels.arc | 640 MB | **2.04 GB** | Merged world map (SVAERA pathfinding + SV custom areas) |
| DRXtextures.arc | 213 MB | — | DRX visual overhaul textures |
| drx.arc | 60 MB | — | DRX game data |
| DRXsounds.arc | 58 MB | — | DRX sounds |
| SVTextures.arc | 44 MB | — | SV creature textures (343 files) |
| **Creatures.arc** | **39 MB** | **~98 MB** | **290 PC skin textures + 2 meshes (cosmetic only)** |
| SVMesh.arc | 27 MB | — | SV creature meshes/animations (234 files) |
| SVSounds.arc | 15 MB | — | SV sounds |
| Items.arc | 8.9 MB | — | 812 SV item textures/icons |
| DRXeffects.arc | 7.8 MB | — | DRX effects |
| Other small .arc | 6.5 MB | — | Various SV content |
| **Total** | **~1.09 GB** | — | |

For comparison, the base game loads ~2.5 GB of its own archives on top of this.

### Key Finding: Levels.arc

The merged world map decompresses to **2.04 GB** — consuming half the 4 GB address space
by itself if fully resident. Comparison:

| Source | Compressed | Decompressed | Parts |
|--------|-----------|-------------|-------|
| Upstream SV 0.98i (TQIT) | 296 MB | 930 MB | 3,548 |
| SVAERA (AE native) | 662 MB | 2.01 GB | 7,665 |
| Our hybrid merge | 670 MB | 2.04 GB | 7,799 |

Our merge adds 35 MB decompressed (46 SV-only custom levels) over SVAERA's base.
The map file passed decompression integrity checks.

### Key Finding: Creatures.arc is Purely Cosmetic

Our Creatures.arc (39 MB, 290 files) contains **exclusively player character skin textures**
and 2 PC mesh files. Zero overlap with actual creature/monster data. SVAERA ships only 2
files (547 KB) in their Creatures.arc, with PC skins in a separate `SV_NewSkins.arc`.

### Key Finding: No Redundancy Between Archives

All files across our archives are unique with only 2 trivial exceptions (azorian bracers
textures duplicated between Items.arc and SVItems.arc). Our archives are already delta-only
in terms of content — every file is SV-specific, not a duplicate of base game data.

### Key Finding: LMesh.arc is Empty

LMesh.arc (217 KB on disk) contains **0 files**. It's an empty archive consuming a file
handle and TOC memory for nothing.

### Key Finding: Proxy RunEquation Failures

Game logs show repeated `RunEquation load failure` for SV spawn formulas:
```
poolValue (((poolValue * 2.3) - (poolValue / (0.0 +(numberOfPlayers * 1.0)))))
```
These are SV's custom multiplayer scaling formulas that the AE engine can't parse.
They're **benign warnings** — the engine falls back to default pool values. These do not
cause crashes but may affect monster spawn density (likely spawning fewer than intended).

## Optimization Plan

### Phase 1: Immediate Archive Cleanup

| Action | Savings | Risk |
|--------|---------|------|
| Remove LMesh.arc (empty, 0 files) | 217 KB | None |
| Remove Creatures.arc (290 cosmetic PC skins) | 39 MB | Players lose SV character skin variety |
| Remove 2 duplicate azorian bracers from Items.arc | Trivial | None |

**Total Phase 1 savings: ~39 MB compressed, ~98 MB decompressed**

Creatures.arc removal rationale: All 290 files are cosmetic PC skin textures from the
TQIT modding community. They're loaded on-demand per character, not all at once. But
removing the archive eliminates the TOC overhead, file handle, and any residual memory
mapping. The game gracefully falls back to base game character skins — no crashes, just
fewer cosmetic options. This matches SVAERA's approach (547 KB vs our 39 MB).

### Phase 2: Optional "Lite Mode" (DRX-free build)

The DRX (Diablo Re-eXtinction) visual overhaul is the largest resource consumer:

| Archive | Size |
|---------|------|
| DRXtextures.arc | 213 MB |
| drx.arc | 60 MB |
| DRXsounds.arc | 58 MB |
| DRXeffects.arc | 8 MB |
| **Total DRX** | **339 MB** |

Removing DRX archives would reduce the mod from 1.09 GB to **750 MB** (31% reduction).
Trade-off: DRX monsters would use fallback/base game visuals. This should be offered as
an optional "lite mode" for players on integrated graphics or limited hardware.

### Phase 3: Script Updates

- Update `bootstrap_working_mod.ps1` to implement Phase 1 cleanup
- Add a `-LiteMode` switch for Phase 2 DRX-free builds
- Update `deploy_to_custommaps.ps1` if needed

## Systemic Limitations

Even with all optimizations, the fundamental constraint is the 32-bit engine's 4 GB address
space limit combined with integrated graphics. The mod's Levels.arc alone decompresses to
2 GB. The base game adds another ~2.5 GB of resources. With DLLs, runtime allocations, and
GPU memory-mapped regions competing for the same 4 GB, crashes under load are likely to
continue at reduced frequency.

**The only complete solutions would be:**
1. A 64-bit game engine (not available)
2. Dedicated GPU with separate VRAM (hardware upgrade)
3. Dramatically reducing mod content (defeats purpose)

Our optimizations reduce crash frequency but cannot eliminate crashes entirely on this
hardware configuration.
