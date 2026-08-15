<#
.SYNOPSIS
    Package the SoulvizierClassic mod for Steam Workshop upload.
.DESCRIPTION
    Stages the Workshop item under dist/workshop/content/SoulvizierClassic/ so the
    uploaded item root contains a SINGLE wrapper folder named SoulvizierClassic (with
    database/ and resources/ inside it). SteamCMD uploads the CONTENTS of the vdf
    contentfolder (dist/workshop/content), so that folder must hold exactly one child:
    SoulvizierClassic. Shipping database/ and resources/ at the item root makes TQAE
    read them as two broken mods "database" and "resources" (the 2026-07-08 "two mods"
    bug). Must run bootstrap_working_mod.ps1 first to build the mod.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$workDir = Join-Path $RepoRoot 'work\SoulvizierClassic'
# contentRoot = the vdf contentfolder; its ONLY child must be the SoulvizierClassic
# wrapper folder. staleWrapperDir = the OLD wrapperless layout (database/ + resources/
# at the top), deleted every run so it can never be picked up and uploaded.
$contentRoot = Join-Path $RepoRoot 'dist\workshop\content'
$distDir = Join-Path $contentRoot 'SoulvizierClassic'
$staleWrapperDir = Join-Path $RepoRoot 'dist\workshop\SoulvizierClassic'

# Verify the mod has been built
$arzFile = Join-Path $workDir 'Database\SoulvizierClassic.arz'
if (-not (Test-Path $arzFile)) {
    Write-Host 'ERROR: Mod not built yet. Run bootstrap_working_mod.ps1 first.' -ForegroundColor Red
    exit 1
}

Write-Host '=== Package for Steam Workshop ===' -ForegroundColor Cyan

# --- Fail-loud STEP-0 RECEIPT guard (BL-b98-DEBT-3; runs BEFORE everything) ---
# FOUR consecutive ship dispatches (2026-08-15) were spent on work that was already live,
# and one of them proposed a deploy that would have REVERTED Will's play surface. Each was
# caught by hand. tools/gate_already_shipped.py made the check mechanical; this makes it a
# PRECONDITION - packaging refuses to stage a byte unless step 0 ran green for THIS ship.
# Escape for a note-only re-upload of an already-shipped payload:
#   py tools/gate_already_shipped.py --repackage "why"
$step0 = Join-Path $RepoRoot 'tools\gate_already_shipped.py'
if (-not (Test-Path $step0)) {
    Write-Host 'ERROR: tools/gate_already_shipped.py is missing - ship-procedure step 0 cannot be verified.' -ForegroundColor Red
    exit 1
}
$env:PYTHONIOENCODING = 'utf-8'
& py $step0 --verify-receipt
if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host '=== FATAL: SHIP-PROCEDURE STEP 0 DID NOT RUN GREEN - ABORTING ===' -ForegroundColor Red
    Write-Host 'Nothing was staged. Run step 0 first:' -ForegroundColor Red
    Write-Host '  py tools/gate_already_shipped.py --lane <branch-or-sha> --tag build<N>-ship' -ForegroundColor Red
    exit 1
}

# --- Fail-loud TESTHUB guard (runs BEFORE staging) ---
# The local-only TESTHUB map variant (local/Levels_merged_TESTHUB.arc) is for local
# play-testing and must NEVER be uploaded to Steam Workshop. If the map about to be
# packaged is byte-identical to it, abort loudly. Always print the packaged Levels.arc
# size + MD5 so every package run is auditable against the published item.
$workLevels = Join-Path $workDir 'Resources\Levels.arc'
if (-not (Test-Path $workLevels)) {
    Write-Host "ERROR: Resources\Levels.arc not found at $workLevels" -ForegroundColor Red
    exit 1
}
$workLevelsInfo = Get-Item $workLevels
$workLevelsMd5 = (Get-FileHash $workLevels -Algorithm MD5).Hash
$testhubArc = Join-Path $RepoRoot 'local\Levels_merged_TESTHUB.arc'
if (Test-Path $testhubArc) {
    $testhubMd5 = (Get-FileHash $testhubArc -Algorithm MD5).Hash
    if ($testhubMd5 -eq $workLevelsMd5) {
        Write-Host ''
        Write-Host '=== FATAL: TESTHUB MAP DETECTED - ABORTING ===' -ForegroundColor Red
        Write-Host 'work Resources\Levels.arc is byte-identical to the LOCAL-ONLY TESTHUB map.' -ForegroundColor Red
        Write-Host "  packaged map : $workLevels" -ForegroundColor Red
        Write-Host "  TESTHUB map  : $testhubArc" -ForegroundColor Red
        Write-Host "  shared MD5   : $workLevelsMd5" -ForegroundColor Red
        Write-Host 'The TESTHUB variant is for local testing only and must never ship. Aborting.' -ForegroundColor Red
        exit 1
    }
    Write-Host "TESTHUB guard OK: packaged MD5 $workLevelsMd5 differs from TESTHUB MD5 $testhubMd5" -ForegroundColor DarkGray
} else {
    Write-Host 'TESTHUB guard: no local\Levels_merged_TESTHUB.arc present to compare against.' -ForegroundColor DarkGray
}
Write-Host "Packaged Levels.arc: $($workLevelsInfo.Length) bytes  MD5 $workLevelsMd5" -ForegroundColor Cyan

# Clean previous staging - remove BOTH the content root AND the stale wrapperless layout
# (dist\workshop\SoulvizierClassic) so an old build can never linger and get uploaded.
if (Test-Path $staleWrapperDir) {
    Remove-Item $staleWrapperDir -Recurse -Force
}
if (Test-Path $contentRoot) {
    Remove-Item $contentRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $distDir -Force | Out-Null

# --- Database ---
$dbDest = Join-Path $distDir 'database'
New-Item -ItemType Directory -Path $dbDest -Force | Out-Null
Copy-Item $arzFile -Destination $dbDest
Write-Host "  database/SoulvizierClassic.arz"

# --- Resources ---
$resSrc = Join-Path $workDir 'Resources'
$resDest = Join-Path $distDir 'resources'
New-Item -ItemType Directory -Path $resDest -Force | Out-Null

# Copy all .arc files (top level)
$arcFiles = @(Get-ChildItem $resSrc -Filter '*.arc' -ErrorAction SilentlyContinue)
foreach ($arc in $arcFiles) {
    Copy-Item $arc.FullName -Destination $resDest
}
Write-Host "  resources/: $($arcFiles.Count) .arc files"

# Copy subdirectories (XPack2, XPack3, XPack4 stubs)
$subDirs = @(Get-ChildItem $resSrc -Directory -ErrorAction SilentlyContinue)
foreach ($sub in $subDirs) {
    $subDest = Join-Path $resDest $sub.Name
    Copy-Item $sub.FullName -Destination $subDest -Recurse
    $subArcs = @(Get-ChildItem $sub.FullName -Filter '*.arc' -Recurse -ErrorAction SilentlyContinue)
    Write-Host "  resources/$($sub.Name)/: $($subArcs.Count) files"
}

# --- Maps ---
$mapsSrc = Join-Path $workDir 'Maps'
if (Test-Path $mapsSrc) {
    $mapFiles = @(Get-ChildItem $mapsSrc -Recurse -File -ErrorAction SilentlyContinue)
    if ($mapFiles.Count -gt 0) {
        $mapsDest = Join-Path $distDir 'maps'
        Copy-Item $mapsSrc -Destination $mapsDest -Recurse
        Write-Host "  maps/: $($mapFiles.Count) files"
    }
}

# --- Summary + single-wrapper invariant check ---
$allFiles = @(Get-ChildItem $distDir -Recurse -File)
$totalMB = [math]::Round(($allFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)

# The vdf contentfolder ($contentRoot) must contain EXACTLY one folder: SoulvizierClassic.
# This is the guard against the "two mods" bug regressing.
$rootChildren = @(Get-ChildItem $contentRoot -Force)
if ($rootChildren.Count -ne 1 -or $rootChildren[0].Name -ne 'SoulvizierClassic' -or -not ($rootChildren[0] -is [System.IO.DirectoryInfo])) {
    $rootChildNames = ($rootChildren | ForEach-Object { $_.Name }) -join ', '
    Write-Host ''
    Write-Host '=== FATAL: content root layout is wrong ===' -ForegroundColor Red
    Write-Host "Expected exactly one folder 'SoulvizierClassic' under $contentRoot" -ForegroundColor Red
    Write-Host "Found: $rootChildNames" -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host "Workshop package ready: $($allFiles.Count) files, $totalMB MB" -ForegroundColor Green
Write-Host "Wrapper folder : $distDir"
Write-Host "Content folder : $contentRoot"
Write-Host '  (upload_workshop.ps1 sets the vdf contentfolder to the Content folder above;'
Write-Host '   the item root will then contain a single SoulvizierClassic folder.)'
Write-Host ''
Write-Host 'Next: run upload_workshop.ps1 to upload to Steam Workshop.' -ForegroundColor Green
