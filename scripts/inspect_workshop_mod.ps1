#Requires -Version 5.1
<#
.SYNOPSIS
    Inspect the SVAERA workshop mod structure in detail.
.DESCRIPTION
    Locates the SVAERA_customquest in the Workshop folder and reports on:
    - .map files, Maps/ directories
    - .arz database files
    - .arc resource files (especially Levels.arc)
    - Levels.arc contents via ArchiveTool listing
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$workshopBase = Require-Config 'STEAM_WORKSHOP_475150'
$archiveTool = $Config['TQ_ARCHIVETOOL']

Write-Host '=== Inspect SVAERA Workshop Mod ===' -ForegroundColor Cyan
Write-Host ''

# ── Locate SVAERA folder ────────────────────────────────────────────
$svaera = $null

$knownId = Join-Path $workshopBase '2076433374\SVAERA_customquest'
if (Test-Path $knownId) {
    $svaera = $knownId
    Write-Host "Found SVAERA via known Workshop ID 2076433374"
} else {
    Get-ChildItem $workshopBase -Directory -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        if (Get-ChildItem $_.FullName -Filter 'SVAERA_customquest.arz' -Recurse -ErrorAction SilentlyContinue) {
            $svaera = $_.FullName
        }
    }
    if ($svaera) {
        Write-Host "Found SVAERA via .arz search: $svaera"
    }
}

if (-not $svaera) {
    Write-Host 'SVAERA_customquest not found in Workshop folder.' -ForegroundColor Red
    exit 1
}

Write-Host "SVAERA root: $svaera"
Write-Host ''

# ── .map files ───────────────────────────────────────────────────────
Write-Host '--- .map files ---' -ForegroundColor Cyan
$mapFiles = @(Get-ChildItem $svaera -Recurse -Filter '*.map' -ErrorAction SilentlyContinue)
if ($mapFiles.Count -eq 0) {
    Write-Host '  (none found)'
} else {
    foreach ($f in $mapFiles) {
        Write-Host "  $($f.FullName) ($([math]::Round($f.Length / 1MB, 2)) MB)"
    }
}
Write-Host ''

# ── Maps/ directories ───────────────────────────────────────────────
Write-Host '--- Maps/ directories ---' -ForegroundColor Cyan
$mapDirs = @(Get-ChildItem $svaera -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq 'Maps' })
if ($mapDirs.Count -eq 0) {
    Write-Host '  (no Maps/ directory found)'
} else {
    foreach ($d in $mapDirs) {
        $contents = @(Get-ChildItem $d.FullName -ErrorAction SilentlyContinue)
        Write-Host "  $($d.FullName) ($($contents.Count) items)"
        foreach ($item in $contents) {
            Write-Host "    $($item.Name)"
        }
    }
}
Write-Host ''

# ── .arz files ───────────────────────────────────────────────────────
Write-Host '--- .arz files ---' -ForegroundColor Cyan
$arzFiles = @(Get-ChildItem $svaera -Recurse -Filter '*.arz' -ErrorAction SilentlyContinue)
if ($arzFiles.Count -eq 0) {
    Write-Host '  (none found)'
} else {
    foreach ($f in $arzFiles) {
        $rel = $f.FullName.Replace($svaera, '.')
        Write-Host "  $rel ($($f.Length) bytes, $([math]::Round($f.Length / 1MB, 2)) MB)"
    }
}
Write-Host ''

# ── .arc files ───────────────────────────────────────────────────────
Write-Host '--- .arc files ---' -ForegroundColor Cyan
$arcFiles = @(Get-ChildItem $svaera -Recurse -Filter '*.arc' -ErrorAction SilentlyContinue)
if ($arcFiles.Count -eq 0) {
    Write-Host '  (none found)'
} else {
    foreach ($f in $arcFiles) {
        $rel = $f.FullName.Replace($svaera, '.')
        $marker = ''
        if ($f.Name -match '(?i)^levels\.arc$') { $marker = ' <-- KEY: Levels data' }
        Write-Host "  $rel ($([math]::Round($f.Length / 1MB, 1)) MB)$marker"
    }
}
Write-Host ''

# ── Levels.arc inspection via ArchiveTool ────────────────────────────
$levelsArc = $arcFiles | Where-Object { $_.Name -match '(?i)^levels\.arc$' } | Select-Object -First 1

if ($levelsArc -and $archiveTool -and (Test-Path $archiveTool)) {
    Write-Host '--- Levels.arc contents (via ArchiveTool -list) ---' -ForegroundColor Cyan

    $listOutput = $null
    try {
        $listOutput = & $archiveTool $levelsArc.FullName -list 2>&1 | Out-String
    } catch {
        $listOutput = $null
    }

    if ($listOutput -and $listOutput.Trim().Length -gt 0 -and $listOutput -notmatch '(?i)error|fail|cannot') {
        $lines = @($listOutput -split "`n" | Where-Object { $_.Trim().Length -gt 0 })
        Write-Host "  Total entries: $($lines.Count)"
        Write-Host '  First 30 entries:'
        $lines | Select-Object -First 30 | ForEach-Object { Write-Host "    $_" }
        if ($lines.Count -gt 30) {
            Write-Host "    ... ($($lines.Count - 30) more entries)"
        }
    } else {
        Write-Host '  -list did not produce usable output. Falling back to extract-and-count...'

        $tmpDir = Join-Path $RepoRoot 'local\tmp_levels_extract'
        if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force }
        New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

        try {
            & $archiveTool $levelsArc.FullName -extract $tmpDir 2>&1 | Out-Null
            $extracted = @(Get-ChildItem $tmpDir -Recurse -File -ErrorAction SilentlyContinue)
            Write-Host "  Extracted file count: $($extracted.Count)"
            if ($extracted.Count -gt 0) {
                Write-Host '  Sample filenames (first 30):'
                $extracted | Select-Object -First 30 | ForEach-Object {
                    $rel = $_.FullName.Replace($tmpDir, '.')
                    Write-Host "    $rel"
                }
                if ($extracted.Count -gt 30) {
                    Write-Host "    ... ($($extracted.Count - 30) more files)"
                }
                $extensions = $extracted | Group-Object Extension | Sort-Object Count -Descending
                Write-Host '  File types:'
                foreach ($ext in $extensions) {
                    Write-Host "    $($ext.Name): $($ext.Count) files"
                }
            }
        } catch {
            Write-Host "  Extract failed: $_" -ForegroundColor Red
        } finally {
            if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force }
            Write-Host '  (temp folder cleaned up)'
        }
    }
} elseif ($levelsArc) {
    Write-Host '--- Levels.arc inspection skipped (ArchiveTool not available) ---' -ForegroundColor Yellow
} else {
    Write-Host '--- No Levels.arc found in SVAERA mod ---' -ForegroundColor Yellow
}

Write-Host ''

# ── Also inspect upstream Soulvizier 0.98i for comparison ───────────
$upstreamDir = Join-Path $RepoRoot 'upstream\soulvizier_098i'
if (Test-Path $upstreamDir) {
    Write-Host '--- Upstream Soulvizier 0.98i comparison ---' -ForegroundColor Cyan
    $upMapFiles = @(Get-ChildItem $upstreamDir -Recurse -Filter '*.map' -ErrorAction SilentlyContinue)
    $upMapDirs = @(Get-ChildItem $upstreamDir -Recurse -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq 'Maps' })
    $upLevels = Get-ChildItem $upstreamDir -Recurse -Filter 'Levels.arc' -ErrorAction SilentlyContinue | Select-Object -First 1

    Write-Host "  .map files: $($upMapFiles.Count)"
    foreach ($f in $upMapFiles) { Write-Host "    $($f.FullName.Replace($upstreamDir, '.')) ($([math]::Round($f.Length / 1MB, 2)) MB)" }
    Write-Host "  Maps/ directories: $($upMapDirs.Count)"
    Write-Host "  Levels.arc: $(if ($upLevels) { "$([math]::Round($upLevels.Length / 1MB, 1)) MB" } else { 'not found' })"

    if ($upLevels -and $archiveTool -and (Test-Path $archiveTool)) {
        Write-Host ''
        Write-Host '  Upstream Levels.arc contents (via ArchiveTool -list):' -ForegroundColor Cyan
        $upListOutput = & $archiveTool $upLevels.FullName -list 2>&1 | Out-String
        if ($upListOutput -and $upListOutput.Trim().Length -gt 0) {
            $upLines = @($upListOutput -split "`n" | Where-Object { $_.Trim().Length -gt 0 })
            Write-Host "    Total entries: $($upLines.Count)"
            Write-Host '    First 20 entries:'
            $upLines | Select-Object -First 20 | ForEach-Object { Write-Host "      $_" }
            if ($upLines.Count -gt 20) {
                Write-Host "      ... ($($upLines.Count - 20) more entries)"
            }
        }
    }
    Write-Host ''
}

# ── Summary ──────────────────────────────────────────────────────────
Write-Host '=== Summary ===' -ForegroundColor Cyan
$hasMap = $mapFiles.Count -gt 0
$hasLevels = @($arcFiles | Where-Object { $_.Name -match '(?i)^levels\.arc$' }).Count -gt 0
$hasMapDir = $mapDirs.Count -gt 0

Write-Host "  SVAERA ships world01.map:     $(if ($hasMap) { 'YES' } else { 'NO' })"
Write-Host "  SVAERA has Maps/ directory:   $(if ($hasMapDir) { 'YES' } else { 'NO' })"
Write-Host "  SVAERA ships Levels.arc:      $(if ($hasLevels) { 'YES' } else { 'NO' })"
Write-Host "  SVAERA .arz count:            $($arzFiles.Count)"
Write-Host "  SVAERA .arc count:            $($arcFiles.Count)"

if (Test-Path $upstreamDir) {
    $upHasMap = (@(Get-ChildItem $upstreamDir -Recurse -Filter '*.map' -ErrorAction SilentlyContinue)).Count -gt 0
    $upHasLevels = @(Get-ChildItem $upstreamDir -Recurse -Filter 'Levels.arc' -ErrorAction SilentlyContinue).Count -gt 0
    Write-Host "  Upstream ships .map files:    $(if ($upHasMap) { 'YES' } else { 'NO' })"
    Write-Host "  Upstream ships Levels.arc:    $(if ($upHasLevels) { 'YES' } else { 'NO' })"
}

Write-Host ''
Write-Host 'Done.' -ForegroundColor Green
