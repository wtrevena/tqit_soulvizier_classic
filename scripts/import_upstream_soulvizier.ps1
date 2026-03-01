#Requires -Version 5.1
<#
.SYNOPSIS
    Import original Soulvizier 0.98i archive from third_party/ into upstream/.
.DESCRIPTION
    Locates the Soulvizier archive in third_party/, extracts it into
    upstream/soulvizier_098i/, and writes an inventory doc.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$thirdParty = Join-Path $RepoRoot 'third_party'
$upstreamDir = Join-Path $RepoRoot 'upstream\soulvizier_098i'
$docsDir = Join-Path $RepoRoot 'docs'

if (-not (Test-Path $thirdParty)) {
    New-Item -ItemType Directory -Path $thirdParty -Force | Out-Null
}

Write-Host '=== Import Upstream Soulvizier ===' -ForegroundColor Cyan

# Find the archive (zip, 7z, or rar)
$archive = $null
foreach ($pattern in @('*oulvizier*0.98*', '*oulvizier*098*', '*SV*098*', '*soulvizier*')) {
    $matches = @(Get-ChildItem $thirdParty -File -Filter $pattern -ErrorAction SilentlyContinue)
    if ($matches.Count -gt 0) {
        $archive = $matches[0]
        break
    }
}

if (-not $archive) {
    Write-Host ''
    Write-Host 'No Soulvizier archive found in third_party/.' -ForegroundColor Red
    Write-Host ''
    Write-Host 'Please download the original Soulvizier 0.98i archive and place it in:'
    Write-Host "  $thirdParty" -ForegroundColor Yellow
    Write-Host ''
    Write-Host 'Expected filename patterns: *soulvizier*0.98*, *SV*098*, etc.'
    Write-Host 'Supported formats: .zip, .7z, .rar'
    exit 1
}

Write-Host "Found archive: $($archive.Name) ($([math]::Round($archive.Length / 1MB, 1)) MB)"

# Clean previous extraction
if (Test-Path $upstreamDir) {
    Write-Host 'Removing previous extraction...'
    Remove-Item $upstreamDir -Recurse -Force
}
New-Item -ItemType Directory -Path $upstreamDir -Force | Out-Null

# Extract based on extension
$ext = $archive.Extension.ToLower()
Write-Host "Extracting ($ext)..."

switch ($ext) {
    '.zip' {
        Expand-Archive -Path $archive.FullName -DestinationPath $upstreamDir -Force
    }
    { $_ -in '.7z', '.rar' } {
        $sevenZip = Get-Command '7z' -ErrorAction SilentlyContinue
        if (-not $sevenZip) {
            $sevenZip = Get-Command 'C:\Program Files\7-Zip\7z.exe' -ErrorAction SilentlyContinue
        }
        if (-not $sevenZip) {
            Write-Host '7-Zip not found. Install with: winget install 7zip.7zip' -ForegroundColor Red
            exit 1
        }
        & $sevenZip.Source x $archive.FullName "-o$upstreamDir" -y
    }
    default {
        Write-Host "Unsupported archive format: $ext" -ForegroundColor Red
        exit 1
    }
}

# If extraction created a single subfolder, flatten it
$topItems = @(Get-ChildItem $upstreamDir)
if ($topItems.Count -eq 1 -and $topItems[0].PSIsContainer) {
    $innerDir = $topItems[0].FullName
    Write-Host "Flattening single subfolder: $($topItems[0].Name)"
    $tempDir = "$upstreamDir-temp"
    Move-Item $innerDir $tempDir
    Remove-Item $upstreamDir -Force
    Rename-Item $tempDir $upstreamDir
}

# Inventory
Write-Host ''
Write-Host '--- Upstream Contents ---' -ForegroundColor Cyan

$arzFiles = @(Get-ChildItem $upstreamDir -Recurse -Filter '*.arz' -ErrorAction SilentlyContinue)
$arcFiles = @(Get-ChildItem $upstreamDir -Recurse -Filter '*.arc' -ErrorAction SilentlyContinue)
$mapFiles = @(Get-ChildItem $upstreamDir -Recurse -Filter '*.map' -ErrorAction SilentlyContinue)
$dbrFiles = @(Get-ChildItem $upstreamDir -Recurse -Filter '*.dbr' -ErrorAction SilentlyContinue)
$allFiles = @(Get-ChildItem $upstreamDir -Recurse -File)
$totalSizeMB = [math]::Round(($allFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)

Write-Host "Total files: $($allFiles.Count) ($totalSizeMB MB)"
Write-Host "ARZ files: $($arzFiles.Count)"
Write-Host "ARC files: $($arcFiles.Count)"
Write-Host "MAP files: $($mapFiles.Count)"
Write-Host "DBR files: $($dbrFiles.Count)"

# Write inventory doc
if (-not (Test-Path $docsDir)) { New-Item -ItemType Directory -Path $docsDir -Force | Out-Null }

$inventoryLines = @(
    '# Upstream Soulvizier 0.98i Inventory',
    '',
    "- **Source archive**: ``$($archive.Name)`` ($([math]::Round($archive.Length / 1MB, 1)) MB)",
    "- **Extracted to**: ``upstream/soulvizier_098i/``",
    "- **Date**: $(Get-Date -Format 'yyyy-MM-dd HH:mm')",
    "- **Total files**: $($allFiles.Count)",
    "- **Total size**: $totalSizeMB MB",
    '',
    '## Key artifacts',
    ''
)

if ($arzFiles.Count -gt 0) {
    $inventoryLines += '### Database (.arz)'
    $inventoryLines += ''
    foreach ($f in $arzFiles) {
        $rel = $f.FullName.Replace($upstreamDir, '.').Replace('\', '/')
        $inventoryLines += "- ``$rel`` ($([math]::Round($f.Length / 1MB, 1)) MB)"
    }
    $inventoryLines += ''
}

if ($arcFiles.Count -gt 0) {
    $inventoryLines += '### Resources (.arc)'
    $inventoryLines += ''
    foreach ($f in $arcFiles) {
        $rel = $f.FullName.Replace($upstreamDir, '.').Replace('\', '/')
        $inventoryLines += "- ``$rel`` ($([math]::Round($f.Length / 1MB, 1)) MB)"
    }
    $inventoryLines += ''
}

if ($mapFiles.Count -gt 0) {
    $inventoryLines += '### Maps (.map)'
    $inventoryLines += ''
    foreach ($f in $mapFiles) {
        $rel = $f.FullName.Replace($upstreamDir, '.').Replace('\', '/')
        $inventoryLines += "- ``$rel`` ($([math]::Round($f.Length / 1MB, 1)) MB)"
    }
    $inventoryLines += ''
}

if ($dbrFiles.Count -gt 0) {
    $inventoryLines += "### Database records (.dbr): $($dbrFiles.Count) files"
    $inventoryLines += ''
}

$inventoryLines += '## Directory tree (top 2 levels)'
$inventoryLines += ''
$inventoryLines += '```'
Get-ChildItem $upstreamDir -Depth 1 | ForEach-Object {
    $rel = $_.FullName.Replace($upstreamDir, '.').Replace('\', '/')
    if ($_.PSIsContainer) {
        $inventoryLines += "$rel/"
    } else {
        $inventoryLines += "$rel ($([math]::Round($_.Length / 1MB, 1)) MB)"
    }
}
$inventoryLines += '```'

Set-Content -Path (Join-Path $docsDir 'upstream_inventory.md') -Value ($inventoryLines -join "`n") -Encoding UTF8
Write-Host "Wrote docs/upstream_inventory.md" -ForegroundColor Green
Write-Host 'Done.' -ForegroundColor Green
