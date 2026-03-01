#Requires -Version 5.1
<#
.SYNOPSIS
    Copy installed Workshop mod folders into reference_mods/ for analysis.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$workshopPath = Require-Config 'STEAM_WORKSHOP_475150'
$refDir = Join-Path $RepoRoot 'reference_mods'

if (-not (Test-Path $refDir)) { New-Item -ItemType Directory -Path $refDir -Force | Out-Null }

Write-Host '=== Sync Reference Mods ===' -ForegroundColor Cyan

# Find SVAERA_customquest
$svaeraSrc = $null
Get-ChildItem $workshopPath -Directory | ForEach-Object {
    $inner = Join-Path $_.FullName 'SVAERA_customquest'
    if (Test-Path $inner) { $svaeraSrc = $inner }
}

if (-not $svaeraSrc) {
    Write-Host 'SVAERA_customquest not found in Workshop folder.' -ForegroundColor Red
    exit 1
}

$svaeraDst = Join-Path $refDir 'SVAERA_customquest'
Write-Host "Source:      $svaeraSrc"
Write-Host "Destination: $svaeraDst"

if (Test-Path $svaeraDst) {
    Write-Host 'Removing old reference copy...'
    Remove-Item $svaeraDst -Recurse -Force
}

Write-Host 'Copying...'
Copy-Item -Path $svaeraSrc -Destination $svaeraDst -Recurse -Force

$fileCount = @(Get-ChildItem $svaeraDst -Recurse -File).Count
$sizeMB = [math]::Round((Get-ChildItem $svaeraDst -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
Write-Host "Copied $fileCount files ($sizeMB MB)" -ForegroundColor Green

# Write reference doc
$docsDir = Join-Path $RepoRoot 'docs'
if (-not (Test-Path $docsDir)) { New-Item -ItemType Directory -Path $docsDir -Force | Out-Null }

$dbSize = if (Test-Path "$svaeraDst\Database\SVAERA_customquest.arz") {
    [math]::Round((Get-Item "$svaeraDst\Database\SVAERA_customquest.arz").Length / 1MB, 1)
} else { 'N/A' }

$arcFiles = @(Get-ChildItem "$svaeraDst\Resources" -Filter '*.arc' -Recurse -ErrorAction SilentlyContinue)

$docContent = @"
# Reference Mods

## SVAERA_customquest

- **Workshop ID**: 2076433374
- **Source**: ``$svaeraSrc``
- **Copied**: $(Get-Date -Format 'yyyy-MM-dd HH:mm')
- **Files**: $fileCount
- **Size**: $sizeMB MB
- **Database**: SVAERA_customquest.arz ($dbSize MB)
- **Resource archives**: $($arcFiles.Count) .arc files

### Resource archive listing

$(($arcFiles | ForEach-Object { "- ``$($_.Name)`` ($([math]::Round($_.Length / 1MB, 1)) MB)" }) -join "`n")

### Key observations

- No .map files: Custom Quest with database + resource overrides only
- Uses XPack2/3/4 resource archives (Ragnarok, Atlantis, Eternal Embers content)
- Includes DRX effects/textures (visual overhaul by Dragonlord)
- Has Text.arc for custom string tags
- This is **Soulvizier AERA** (the Steam fork with nerfs) — used as structure reference only
"@

Set-Content -Path (Join-Path $docsDir 'reference_mods.md') -Value $docContent -Encoding UTF8
Write-Host "Wrote docs/reference_mods.md" -ForegroundColor Green
Write-Host 'Done.' -ForegroundColor Green
