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
    [switch]$SkipArzBuild
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

# --- Step 2b: Strip TQIT-era UI/engine .arc files that conflict with AE ---
# SV 0.98i shipped with TQIT engine resources (menus, panels, fonts, etc.)
# that override AE's modern UI system and cause rendering issues (broken
# skill icons, missing mastery backgrounds, incompatible UI layouts).
# SVAERA (working AE port) strips all these and only keeps SV-content archives.
$tqitStripList = @(
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
    'XPack.arc'
)

Write-Host ''
Write-Host 'Stripping TQIT-era UI/engine .arc files (incompatible with AE)...' -ForegroundColor Yellow
$strippedCount = 0
foreach ($arcName in $tqitStripList) {
    $target = Join-Path $workDir "Resources\$arcName"
    if (Test-Path $target) {
        $sz = [math]::Round((Get-Item $target).Length / 1MB, 1)
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

Write-Host "Stripped $strippedCount TQIT .arc files"

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
} elseif ($svaeraLevels -and (Test-Path $svaeraLevels)) {
    $svaeraSize = [math]::Round((Get-Item $svaeraLevels).Length / 1MB, 1)
    Write-Host ''
    Write-Host "Using SVAERA Levels.arc (${svaeraSize} MB) - AE pathfinding, missing custom areas" -ForegroundColor Yellow
    Write-Host "  Run tools/merge_levels.py to build merged Levels.arc with custom SV areas restored" -ForegroundColor Yellow
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
} else {
    Write-Host 'WARNING: SV Text_EN.arc not found for text build' -ForegroundColor Yellow
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

# --- Summary ---
Write-Host ''
Write-Host '--- Working mod contents ---' -ForegroundColor Cyan
$workFiles = @(Get-ChildItem $workDir -Recurse -File)
$totalMB = [math]::Round(($workFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "Total: $($workFiles.Count) files, $totalMB MB"

Write-Host ''
Write-Host 'Working mod bootstrapped at work/SoulvizierClassic/' -ForegroundColor Green
Write-Host 'Next: run deploy_to_custommaps.ps1 to deploy for testing.' -ForegroundColor Green
