<#
.SYNOPSIS
    Package the SoulvizierClassic mod for Steam Workshop upload.
.DESCRIPTION
    Creates a clean staging folder at dist/workshop/SoulvizierClassic/ with
    only the files needed for the Workshop item: database, resources, maps.
    Must run bootstrap_working_mod.ps1 first to build the mod.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$workDir = Join-Path $RepoRoot 'work\SoulvizierClassic'
$distDir = Join-Path $RepoRoot 'dist\workshop\SoulvizierClassic'

# Verify the mod has been built
$arzFile = Join-Path $workDir 'Database\SoulvizierClassic.arz'
if (-not (Test-Path $arzFile)) {
    Write-Host 'ERROR: Mod not built yet. Run bootstrap_working_mod.ps1 first.' -ForegroundColor Red
    exit 1
}

Write-Host '=== Package for Steam Workshop ===' -ForegroundColor Cyan

# Clean previous staging
if (Test-Path $distDir) {
    Remove-Item $distDir -Recurse -Force
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

# --- Summary ---
$allFiles = @(Get-ChildItem $distDir -Recurse -File)
$totalMB = [math]::Round(($allFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host ''
Write-Host "Workshop package ready: $($allFiles.Count) files, $totalMB MB" -ForegroundColor Green
Write-Host "Location: $distDir"
Write-Host ''
Write-Host 'Next: run upload_workshop.ps1 to upload to Steam Workshop.' -ForegroundColor Green
