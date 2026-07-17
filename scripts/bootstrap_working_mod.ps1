#Requires -Version 5.1
<#
.SYNOPSIS
    Create the working mod tree for SoulvizierClassic under work/.
.DESCRIPTION
    Builds the mod from known-good sources:
    1. Full SV 0.98i .arz patched by build_svc_database.py:
       - Potion drop rates restored from SV 0.9
       - Souls wired to 1,667+ monster records (66% rare / 25% boss)
       - All equipment made enchantable
    2. Resource .arc files from upstream Soulvizier 0.98i
    3. Merged Levels.arc (SVAERA AE pathfinding + SV custom map areas)
    4. Modified Text_EN.arc with Occult mastery label fix
#>
[CmdletBinding()]
param(
    [switch]$SkipArzBuild,
    [switch]$LiteMode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$upstreamDir = Join-Path $RepoRoot 'upstream\soulvizier_098i'
$referenceDir = Join-Path $RepoRoot 'reference_mods\SVAERA_customquest'
$workDir = Join-Path $RepoRoot 'work\SoulvizierClassic'
$modName = 'SoulvizierClassic'

Write-Host '=== Bootstrap Working Mod ===' -ForegroundColor Cyan

if (-not (Test-Path $upstreamDir)) {
    Write-Host 'upstream/soulvizier_098i/ not found. Run import_upstream_soulvizier.ps1 first.' -ForegroundColor Red
    exit 1
}

# Create mod directory structure
foreach ($sub in @('Database', 'Resources')) {
    $dir = Join-Path $workDir $sub
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "Created: work/SoulvizierClassic/$sub/"
    }
}

# --- Step 1: Build delta .arz ---
$dstArz = Join-Path $workDir "Database\$modName.arz"
$toolsDir = Join-Path $RepoRoot 'tools'
$pythonExe = $Config['PYTHON_EXE']
if (-not $pythonExe) { $pythonExe = 'python' }

$srcArz = @(Get-ChildItem $upstreamDir -Recurse -Filter '*.arz' -ErrorAction SilentlyContinue)
$baseArz = Join-Path $Config['TQAE_ROOT'] 'database\database.arz'

$sv09Dir = Join-Path $RepoRoot 'upstream\soulvizier_0.9'
$sv09Arz = @(Get-ChildItem $sv09Dir -Recurse -Filter '*.arz' -ErrorAction SilentlyContinue)

$sv041Dir = Join-Path $RepoRoot 'upstream\soulvizier_041'
$sv041Arz = @(Get-ChildItem $sv041Dir -Recurse -Filter '*.arz' -ErrorAction SilentlyContinue)

if (-not $SkipArzBuild -and $srcArz.Count -gt 0) {
    Write-Host ''
    Write-Host 'Building patched .arz (SoulvizierClassic)...' -ForegroundColor Yellow
    $buildScript = Join-Path $toolsDir 'build_svc_database.py'

    if ($sv09Arz.Count -gt 0 -and $sv041Arz.Count -gt 0) {
        & $pythonExe $buildScript $srcArz[0].FullName $sv09Arz[0].FullName $sv041Arz[0].FullName $dstArz
    } elseif ($sv09Arz.Count -gt 0) {
        Write-Host 'SV 0.4.1 not found for legacy skills, skipping legacy skill restore' -ForegroundColor Yellow
        & $pythonExe $buildScript $srcArz[0].FullName $sv09Arz[0].FullName '' $dstArz
    } else {
        Write-Host 'SV 0.9 not found for potion rate reference, using simplified build' -ForegroundColor Yellow
        Copy-Item $srcArz[0].FullName $dstArz -Force
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host 'WARNING: Patched build failed, falling back to full upstream .arz' -ForegroundColor Yellow
        Copy-Item $srcArz[0].FullName $dstArz -Force
    }
} elseif ($srcArz.Count -gt 0) {
    Write-Host 'Copying full upstream .arz (no patching)' -ForegroundColor Yellow
    Copy-Item $srcArz[0].FullName $dstArz -Force
} else {
    Write-Host 'WARNING: No .arz file found in upstream.' -ForegroundColor Yellow
}

if (Test-Path $dstArz) {
    $arzSize = [math]::Round((Get-Item $dstArz).Length / 1MB, 1)
    Write-Host "Database: $modName.arz ($arzSize MB)"
}

# --- Step 2: Copy .arc resource files from upstream ---
Write-Host ''
Write-Host 'Copying upstream .arc resources...' -ForegroundColor Yellow
$arcFiles = @(Get-ChildItem $upstreamDir -Recurse -Filter '*.arc' -ErrorAction SilentlyContinue)
if ($arcFiles.Count -gt 0) {
    foreach ($arc in $arcFiles) {
        $relPath = $arc.FullName.Substring($upstreamDir.Length + 1)
        $parentFolder = Split-Path $relPath -Parent

        if ($parentFolder -match '(?i)resource') {
            $subPath = $relPath.Substring($relPath.IndexOf('\') + 1)
            $dst = Join-Path $workDir "Resources\$subPath"
        } else {
            $dst = Join-Path $workDir "Resources\$($arc.Name)"
        }

        $dstDir = Split-Path $dst -Parent
        if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }

        Copy-Item $arc.FullName $dst -Force
    }
    Write-Host "Copied $($arcFiles.Count) .arc files from upstream"
} else {
    Write-Host 'WARNING: No .arc files found in upstream.' -ForegroundColor Yellow
}

# --- Step 2b: Strip archives that are incompatible, empty, or redundant ---
# Categories:
#   TQIT UI    - TQIT engine resources that break AE's modern UI
#   Empty      - Archives with 0 files inside (waste of file handles)
#   Cosmetic   - PC character skin textures (290 skins, 39 MB) -- cosmetic only,
#                game falls back to base game skins. Saves ~39 MB compressed / ~98 MB
#                decompressed address space. Matches SVAERA's approach (547 KB).
$stripList = @(
    # --- TQIT UI/engine (incompatible with AE) ---
    'Caravan.arc',
    'detailedmap.arc',
    'Dialog.arc',
    'Enchanter.arc',
    'Fonts.arc',
    'InGameUI.arc',
    'Maps.arc',
    'Market.arc',
    'menu.arc',
    'MenuButtons.arc',
    'Options.arc',
    'Prompt Window.arc',
    'SkillsPanel.arc',
    'Teleport Map.arc',
    'Text_DE.arc',
    'Text_EN.arc',
    'Text_FR.arc',
    'UI.arc',
    'XPack.arc',
    # --- Empty archives ---
    'LMesh.arc',
    # --- Cosmetic-only (PC skin textures, 39 MB) ---
    'Creatures.arc'
)

Write-Host ''
Write-Host 'Stripping incompatible/empty/cosmetic .arc files...' -ForegroundColor Yellow
$strippedCount = 0
$strippedMB = 0
foreach ($arcName in $stripList) {
    $target = Join-Path $workDir "Resources\$arcName"
    if (Test-Path $target) {
        $sz = [math]::Round((Get-Item $target).Length / 1MB, 1)
        $strippedMB += $sz
        Remove-Item $target -Force
        Write-Host "  Stripped: $arcName ($sz MB)"
        $strippedCount++
    }
}

# Strip the entire XPack subfolder (TQIT expansion pack UI/shaders/menus/quests)
$xpackDir = Join-Path $workDir 'Resources\XPack'
if (Test-Path $xpackDir) {
    $xpackFiles = @(Get-ChildItem $xpackDir -File)
    foreach ($f in $xpackFiles) {
        Remove-Item $f.FullName -Force
        Write-Host "  Stripped: XPack\$($f.Name)"
        $strippedCount++
    }
    Remove-Item $xpackDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Stripped $strippedCount files (~$strippedMB MB)"

# --- Step 2c: Lite Mode -- strip DRX visual overhaul for low-memory systems ---
# DRX (Diablo Re-eXtinction) adds 339 MB of visual assets. On systems with
# integrated graphics and limited address space, removing DRX reduces crash
# frequency. DRX monsters will use fallback/base game visuals.
if ($LiteMode) {
    Write-Host ''
    Write-Host '[LITE MODE] Stripping DRX visual overhaul archives (339 MB)...' -ForegroundColor Yellow
    $drxStripList = @(
        'DRXtextures.arc',   # 213 MB - DRX creature textures
        'drx.arc',           #  60 MB - DRX game data
        'DRXsounds.arc',     #  58 MB - DRX sounds
        'DRXeffects.arc'     #   8 MB - DRX effects
    )
    $drxStripped = 0
    $drxMB = 0
    foreach ($arcName in $drxStripList) {
        $target = Join-Path $workDir "Resources\$arcName"
        if (Test-Path $target) {
            $sz = [math]::Round((Get-Item $target).Length / 1MB, 1)
            $drxMB += $sz
            Remove-Item $target -Force
            Write-Host "  Stripped: $arcName ($sz MB)"
            $drxStripped++
        }
    }
    Write-Host "Lite mode: stripped $drxStripped DRX archives (~$drxMB MB)" -ForegroundColor Green
}

# --- Step 2d: Create selective DLC stub archives ---
# SoulvizierClassic only uses Acts I-IV (through Hades). DLC archives for
# Ragnarok, Atlantis, Eternal Embers load even in Custom Quest mode.
# We selectively block DLC-specific content (dialog, music, sounds, region
# scenery) while KEEPING archives that may update base game resources
# (creatures, items, terrain textures, underground areas, effects, UI).
Write-Host ''
Write-Host 'Creating selective DLC stub archives...' -ForegroundColor Yellow
$baseResources = Join-Path $Config['TQAE_ROOT'] 'Resources'
$dlcPacks = @('XPack2', 'XPack3', 'XPack4')
$dlcStubCount = 0
$dlcBlockedMB = 0

# Archives that may contain base game updates -- DO NOT BLOCK
$dlcKeepList = @(
    'creatures.arc', 'items.arc', 'item.arc',
    'effects.arc', 'terraintextures.arc', 'underground.arc',
    'scenerygreece.arc', 'scenery.arc',
    'ui.arc', 'ingameui.arc', 'menu.arc',
    'shaders.arc', 'lights.arc', 'system.arc', 'quests.arc'
)

foreach ($xpack in $dlcPacks) {
    $baseXpackDir = Join-Path $baseResources $xpack
    if (-not (Test-Path $baseXpackDir)) { continue }

    $stubDir = Join-Path $workDir "Resources\$xpack"
    if (-not (Test-Path $stubDir)) {
        New-Item -ItemType Directory -Path $stubDir -Force | Out-Null
    }

    $baseArcs = @(Get-ChildItem $baseXpackDir -Filter '*.arc' -ErrorAction SilentlyContinue)
    $blocked = 0
    foreach ($baseArc in $baseArcs) {
        if ($dlcKeepList -contains $baseArc.Name.ToLower()) { continue }

        $stubPath = Join-Path $stubDir $baseArc.Name
        # Write a valid empty .arc: 28-byte header + padding to 2048 bytes
        $header = [byte[]]@(
            0x41, 0x52, 0x43, 0x00,   # Magic: ARC\0
            0x01, 0x00, 0x00, 0x00,   # Version: 1
            0x00, 0x00, 0x00, 0x00,   # num_entries: 0
            0x00, 0x00, 0x00, 0x00,   # num_data: 0
            0x00, 0x00, 0x00, 0x00,   # toc_size: 0
            0x00, 0x00, 0x00, 0x00,   # string_size: 0
            0x00, 0x08, 0x00, 0x00    # toc_offset: 2048 (0x0800)
        )
        $padding = [byte[]]::new(2048 - 28)
        $bytes = $header + $padding
        [System.IO.File]::WriteAllBytes($stubPath, $bytes)

        $blockedMB = [math]::Round($baseArc.Length / 1MB, 0)
        $dlcBlockedMB += $blockedMB
        $dlcStubCount++
        $blocked++
    }
    Write-Host "  $xpack/: $blocked DLC-only archives blocked"
}
Write-Host "Created $dlcStubCount DLC stubs (blocks ~$dlcBlockedMB MB of DLC-specific content)" -ForegroundColor Green

# --- Step 2e: Stage grafted render arcs (Rune Golem D5 closure) ---
# assets/runegolem/_DRX_Meshes.arc + _DRX_Textures.arc carry the ONLY SVAERA art the
# Rune Golem graft needs (mesh + 3 skins + glow + spawn anim + 4 skill-bar icons). They
# are committed minimal arcs (extracted once from SVAERA's unshipped _DRX_Meshes/
# _DRX_Textures) so the build is self-contained. The pet record's mesh + the mesh's own
# texture refs hardcode the archive names `_DRX_Meshes` / `_DRX_Textures`, so the arcs
# MUST keep those exact filenames. Everything else in the golem render chain resolves in
# base AE (shader/bump/anims/party icons). Do NOT strip these.
Write-Host ''
Write-Host 'Staging grafted render arcs (Rune Golem)...' -ForegroundColor Yellow
$golemAssets = Join-Path $RepoRoot 'assets\runegolem'
$golemArcs = @('_DRX_Meshes.arc', '_DRX_Textures.arc')
$golemStaged = 0
foreach ($ga in $golemArcs) {
    $src = Join-Path $golemAssets $ga
    if (Test-Path $src) {
        Copy-Item $src (Join-Path $workDir "Resources\$ga") -Force
        $gz = [math]::Round((Get-Item $src).Length / 1KB, 1)
        Write-Host "  Staged: $ga ($gz KB)"
        $golemStaged++
    } else {
        Write-Host "  WARNING: missing $src (Rune Golem will render invisible)" -ForegroundColor Red
    }
}
Write-Host "Staged $golemStaged Rune Golem render arc(s)" -ForegroundColor Green

# --- Step 3: Levels.arc (merged: SVAERA pathfinding + SV custom map objects) ---
$mergedLevels = Join-Path $RepoRoot 'local\Levels_merged.arc'
$svaeraLevels = Join-Path $referenceDir 'Levels.arc'
if (-not (Test-Path $svaeraLevels)) {
    $svaeraLevels = @(Get-ChildItem $referenceDir -Recurse -Filter 'Levels.arc' -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($svaeraLevels) { $svaeraLevels = $svaeraLevels.FullName }
}
$dstLevels = Join-Path $workDir 'Resources\Levels.arc'

if (Test-Path $mergedLevels) {
    $mSize = [math]::Round((Get-Item $mergedLevels).Length / 1MB, 1)
    Write-Host ''
    Write-Host "Using merged Levels.arc (${mSize} MB) - SVAERA pathfinding + SV custom map areas" -ForegroundColor Green
    Copy-Item $mergedLevels $dstLevels -Force
} elseif (Test-Path $dstLevels) {
    # local\Levels_merged.arc is missing but work\ already has a Levels.arc.
    # Do NOT overwrite it with the SVAERA base: that would wipe the merged SV
    # areas (blood cave etc.) from the good deployed map. Keep what is there.
    $keepSize = [math]::Round((Get-Item $dstLevels).Length / 1MB, 1)
    Write-Host ''
    Write-Host "NOTE: local\Levels_merged.arc not found; KEEPING existing work Levels.arc (${keepSize} MB)." -ForegroundColor Yellow
    Write-Host '      Not overwriting with the SVAERA base. Run tools/svaera_plus_portals.py to' -ForegroundColor Yellow
    Write-Host '      regenerate the merged map (with SV areas + navmeshes) before deploying.' -ForegroundColor Yellow
} elseif ($svaeraLevels -and (Test-Path $svaeraLevels)) {
    # Fresh setup only: no merged map AND no existing work Levels.arc. Seed from
    # the SVAERA base so the mod at least loads; SV areas are added by the merge.
    $svaeraSize = [math]::Round((Get-Item $svaeraLevels).Length / 1MB, 1)
    Write-Host ''
    Write-Host "Seeding SVAERA Levels.arc (${svaeraSize} MB) - AE pathfinding, missing custom SV areas" -ForegroundColor Yellow
    Write-Host "  Run tools/svaera_plus_portals.py to build the merged Levels.arc with SV areas restored" -ForegroundColor Yellow
    Copy-Item $svaeraLevels $dstLevels -Force
} else {
    Write-Host 'WARNING: No Levels.arc found.' -ForegroundColor Red
}

# --- Step 4: Build Text.arc (AE Custom Quest uses Resources/Text.arc with modstrings.txt) ---
$svTextEnArc = Join-Path $upstreamDir 'Resources\Text_EN.arc'
$dstTextArc = Join-Path $workDir 'Resources\Text.arc'
$uberTagsFile = Join-Path $workDir 'Database\uber_soul_tags.txt'

# Remove old Text_EN.arc if present (AE doesn't load it for Custom Quest mods)
$oldTextEn = Join-Path $workDir 'Resources\Text_EN.arc'
if (Test-Path $oldTextEn) {
    Remove-Item $oldTextEn -Force
    Write-Host '  Removed obsolete Text_EN.arc (AE uses Text.arc)'
}

if (Test-Path $svTextEnArc) {
    Write-Host ''
    Write-Host 'Building Text.arc (modstrings.txt with all SV text + Occult fix + uber soul tags)...' -ForegroundColor Yellow
    $buildTextScript = Join-Path $toolsDir 'build_text_arc.py'

    # B38 i18n de-clobber: give build_text_arc the player's base-game Text_EN.arc
    # so it drops vanilla tags whose value equals the base game's. Re-emitting
    # those does nothing in English but OVERRIDES the localized value in every
    # non-English base Text_XX.arc (the Steam "cant change the language" bug).
    # Passed via env var (unambiguous vs positional args); build_text_arc also
    # accepts it as the 4th positional. Absent -> build warns + keeps old behavior.
    $baseTextEnArc = Join-Path $Config['TQAE_ROOT'] 'Text\Text_EN.arc'
    if (Test-Path $baseTextEnArc) {
        $env:SVC_BASE_TEXT_EN = $baseTextEnArc
        Write-Host "  i18n de-clobber base text: $baseTextEnArc" -ForegroundColor DarkGray
    } else {
        Write-Host "  WARNING: base-game Text_EN.arc not found at $baseTextEnArc; i18n de-clobber will be skipped." -ForegroundColor Yellow
    }

    $textArgs = @($buildTextScript, $svTextEnArc, $dstTextArc)
    if (Test-Path $uberTagsFile) {
        $textArgs += $uberTagsFile
    }
    & $pythonExe @textArgs

    if ($LASTEXITCODE -ne 0) {
        Write-Host 'WARNING: Text.arc build failed!' -ForegroundColor Red
    } else {
        $arcSize = [math]::Round((Get-Item $dstTextArc).Length / 1KB, 1)
        Write-Host "  Text.arc built ($arcSize KB)" -ForegroundColor Green
    }

    # --- Step 4b: Gate on tag validation (catches stale Text.arc) ---
    # Every mod name/description tag the .arz references must resolve to a
    # Text.arc entry. Guards against build_text_arc.py running against a stale
    # uber_soul_tags.txt (the tagSoulSVC9005/9006 orphan class). Fails the build
    # loudly rather than shipping raw tag strings in-game.
    # The mod-owned tag set is now driven by the mod_authored_tags.txt manifest
    # that build_text_arc.py writes next to Text.arc (written-set membership),
    # which also covers previously-missed mod tags (tagSkillName050,
    # tagNewSkill321DESC, tagbreachDESC). validate_tags.py auto-discovers it, but
    # we pass it explicitly (4th positional arg, after the authoritative uber
    # tags) so the wiring is visible and robust.
    $validateScript = Join-Path $toolsDir 'validate_tags.py'
    $modTagManifest = Join-Path $workDir 'Resources\mod_authored_tags.txt'
    if ((Test-Path $validateScript) -and (Test-Path $dstArz) -and (Test-Path $dstTextArc)) {
        Write-Host ''
        Write-Host 'Validating name/description tags (.arz -> Text.arc)...' -ForegroundColor Yellow
        $validateArgs = @($validateScript, $dstArz, $dstTextArc)
        if (Test-Path $uberTagsFile) {
            $validateArgs += $uberTagsFile
            if (Test-Path $modTagManifest) {
                $validateArgs += $modTagManifest
            }
        }
        & $pythonExe @validateArgs
        if ($LASTEXITCODE -ne 0) {
            Write-Host ''
            Write-Host 'ERROR: Tag validation FAILED. The .arz references tags absent from Text.arc.' -ForegroundColor Red
            Write-Host '       This usually means Text.arc is stale relative to the .arz.' -ForegroundColor Red
            Write-Host '       Rebuild the .arz and Text.arc together (do not -SkipArzBuild), then re-run.' -ForegroundColor Red
            exit 1
        }
        Write-Host '  Tag validation passed.' -ForegroundColor Green
    }

    # --- Step 4b-2: Gate on formula-name text (B80) ---
    # Every obtainable DRX supra craft formula's rendered display name must
    # reference its crafted result's own rendered name (the "Mythic Formula -
    # <Result>" convention). Guards against a formula shell's description tag
    # being left pointed at (or repointed to) a DIFFERENT formula's donor tag -
    # the Galefury/Crystalline-Mask bug (Will 2026-07-16, b80, ledger R-41). See
    # tools/validate_formula_names.py + docs/reports/b80_formula_names.md.
    $validateFormulaNamesScript = Join-Path $toolsDir 'validate_formula_names.py'
    if ((Test-Path $validateFormulaNamesScript) -and (Test-Path $dstArz) -and (Test-Path $dstTextArc)) {
        Write-Host ''
        Write-Host 'Validating supra formula display names (.arz -> Text.arc)...' -ForegroundColor Yellow
        & $pythonExe $validateFormulaNamesScript $dstArz $dstTextArc
        if ($LASTEXITCODE -ne 0) {
            Write-Host ''
            Write-Host 'ERROR: Formula-name validation FAILED. A supra craft formula displays the wrong name.' -ForegroundColor Red
            Write-Host '       See tools/validate_formula_names.py output above and docs/reports/b80_formula_names.md.' -ForegroundColor Red
            exit 1
        }
        Write-Host '  Formula-name validation passed.' -ForegroundColor Green
    }
} else {
    Write-Host 'WARNING: SV Text_EN.arc not found for text build' -ForegroundColor Yellow
}

# --- Step 4c: Gate on soul augment/proc resolution ---
# Every skill a SOUL grants (augmentSkillName1..4 / itemSkillName /
# itemSkillAutoController) is a DBR path written verbatim into the .arz with no
# resolution (apply_svc_patches.py _set_soul_fields). A wrong path (e.g. a
# records\skills\dream\* skill that actually lives under records\xpack\skills\
# dream\*, or a Runemaster skill that does not exist in TQAE) makes the engine
# silently grant nothing. This gate decodes every soul's granted-skill refs and
# fails the build loudly if any does not resolve. .arz-only (no Text.arc dep).
$soulValidateScript = Join-Path $toolsDir 'validate_soul_augments.py'
if ((Test-Path $soulValidateScript) -and (Test-Path $dstArz)) {
    Write-Host ''
    Write-Host 'Validating soul augment/proc skill references (.arz)...' -ForegroundColor Yellow
    & $pythonExe $soulValidateScript $dstArz
    if ($LASTEXITCODE -ne 0) {
        Write-Host ''
        Write-Host 'ERROR: Soul augment validation FAILED. One or more souls grant a' -ForegroundColor Red
        Write-Host '       skill whose DBR path does not resolve in the .arz (silent no-op).' -ForegroundColor Red
        Write-Host '       Fix the offending skill path constant in tools/apply_svc_patches.py.' -ForegroundColor Red
        exit 1
    }
    Write-Host '  Soul augment validation passed.' -ForegroundColor Green
}

# --- Step 4d: Gate on soul-granted summon pets (B-SUMMON-1) ---
# Every soul-granted summon must spawn a complete, renderable, usable pet:
# mesh present, proven mesh+animation rig pairing, resolving equipment with no
# never-auto-equips player Epic/Legendary uniques (the naked-Boneash bug),
# live controller and skill refs. Resolution matches runtime (mod UNION base
# game); SV-upstream pets are warn-only (proven by SV play). Fails the build
# loudly on any broken mod-authored summon chain.
$summonValidateScript = Join-Path $toolsDir 'validate_summon_pets.py'
if ((Test-Path $summonValidateScript) -and (Test-Path $dstArz)) {
    Write-Host ''
    Write-Host 'Validating soul-granted summon pets (.arz)...' -ForegroundColor Yellow
    $summonArgs = @($summonValidateScript, $dstArz)
    if (Test-Path $baseArz) { $summonArgs += $baseArz }
    if ($srcArz.Count -gt 0) {
        if (-not (Test-Path $baseArz)) { $summonArgs += '' }
        $summonArgs += $srcArz[0].FullName
    }
    & $pythonExe @summonArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host ''
        Write-Host 'ERROR: Summon-pet validation FAILED. One or more soul-granted' -ForegroundColor Red
        Write-Host '       summons spawn a broken pet (naked/floating/inert class).' -ForegroundColor Red
        Write-Host '       Fix the pet-creation block in tools/apply_svc_patches.py.' -ForegroundColor Red
        exit 1
    }
    Write-Host '  Summon-pet validation passed.' -ForegroundColor Green
}

# --- Step 5: Quest system ---
# Use SVAERA's Quests.arc (100 AE-compatible quest files + tokens.bin).
# Custom portal quests are added on top.
Write-Host ''
Write-Host 'Setting up quest system...' -ForegroundColor Yellow
$svaeraQuests = Join-Path $referenceDir 'Resources\Quests.arc'
$dstQuests = Join-Path $workDir 'Resources\Quests.arc'
if (Test-Path $svaeraQuests) {
    Copy-Item $svaeraQuests $dstQuests -Force
    $qSize = [math]::Round((Get-Item $dstQuests).Length / 1KB, 1)
    Write-Host "  Copied SVAERA Quests.arc ($qSize KB)" -ForegroundColor Green
} else {
    Write-Host '  WARNING: SVAERA Quests.arc not found' -ForegroundColor Yellow
}
$questScript = Join-Path $toolsDir 'build_quest_files.py'
if (Test-Path $questScript) {
    Write-Host '  Building custom portal quests...' -ForegroundColor Yellow
    & $pythonExe $questScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host '  WARNING: Quest build failed!' -ForegroundColor Red
    }
}

# --- Step 6: Clean up duplicate files in Items.arc ---
# Items.arc and SVItems.arc both contain azorian bracers textures. Remove
# duplicates from Items.arc since SVItems.arc takes priority.
$dstItems = Join-Path $workDir 'Resources\Items.arc'
if (Test-Path $dstItems) {
    $dedupeScript = Join-Path $toolsDir 'dedupe_items_arc.py'
    if (Test-Path $dedupeScript) {
        Write-Host ''
        Write-Host 'Deduplicating Items.arc (removing files already in SVItems.arc)...' -ForegroundColor Yellow
        $svItemsArc = Join-Path $workDir 'Resources\SVItems.arc'
        & $pythonExe $dedupeScript $dstItems $svItemsArc
    }
}

# --- Summary ---
Write-Host ''
Write-Host '--- Working mod contents ---' -ForegroundColor Cyan
$workFiles = @(Get-ChildItem $workDir -Recurse -File)
$totalMB = [math]::Round(($workFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "Total: $($workFiles.Count) files, $totalMB MB"

Write-Host ''
if ($LiteMode) {
    Write-Host 'Working mod bootstrapped at work/SoulvizierClassic/ [LITE MODE]' -ForegroundColor Green
    Write-Host '  DRX visual overhaul stripped for reduced memory footprint.' -ForegroundColor Yellow
} else {
    Write-Host 'Working mod bootstrapped at work/SoulvizierClassic/' -ForegroundColor Green
}
Write-Host 'Next: run deploy_to_custommaps.ps1 to deploy for testing.' -ForegroundColor Green
