#Requires -Version 5.1
<#
.SYNOPSIS
    Deploy the working mod into the Windows CustomMaps folder for testing.
.DESCRIPTION
    Backs up any existing deployed version, then copies work/SoulvizierClassic/
    into the CustomMaps folder so the user can test via "Play Custom Quest" in TQAE.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$modName = 'SoulvizierClassic'
$workMod = Join-Path $RepoRoot "work\$modName"
$customMaps = Require-Config 'WIN_CUSTOMMAPS'
$deployTarget = Join-Path $customMaps $modName
$backupDir = Join-Path $RepoRoot 'backups\deployed'

Write-Host '=== Deploy to CustomMaps ===' -ForegroundColor Cyan

# Backup ALL character saves before any deployment (Main + Custom Quest)
$tqDocsBase = Require-Config 'TQ_DOCS_BASE'
$charBackupDir = Join-Path $RepoRoot 'backups\characters'
$saveDirs = @(
    @{ Path = (Join-Path $tqDocsBase 'SaveData\Main'); Label = 'Main' },
    @{ Path = (Join-Path $tqDocsBase 'SaveData\User'); Label = 'CustomQuest' }
)

$totalBacked = 0
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$snapDir = Join-Path $charBackupDir $timestamp

foreach ($sd in $saveDirs) {
    if (-not (Test-Path $sd.Path)) { continue }
    $charFolders = @(Get-ChildItem -Path $sd.Path -Directory -ErrorAction SilentlyContinue |
        Where-Object { Test-Path (Join-Path $_.FullName 'Player.chr') })

    if ($charFolders.Count -eq 0) { continue }

    $subDir = Join-Path $snapDir $sd.Label
    New-Item -ItemType Directory -Path $subDir -Force | Out-Null

    if ($totalBacked -eq 0) {
        Write-Host ''
        Write-Host "Backing up character saves..." -ForegroundColor Yellow
    }
    Write-Host "  [$($sd.Label)] $($charFolders.Count) character(s):" -ForegroundColor Yellow
    foreach ($cf in $charFolders) {
        $dest = Join-Path $subDir $cf.Name
        Copy-Item -Path $cf.FullName -Destination $dest -Recurse -Force
        $chrSize = (Get-Item (Join-Path $cf.FullName 'Player.chr')).Length
        Write-Host "    $($cf.Name) ($([math]::Round($chrSize / 1KB, 1)) KB)"
        $totalBacked++
    }
}

if ($totalBacked -gt 0) {
    Write-Host "  $totalBacked total character(s) backed up to: backups\characters\$timestamp\" -ForegroundColor Green

    # Prune old backups (keep last 10)
    $allSnaps = @(Get-ChildItem -Path $charBackupDir -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending)
    if ($allSnaps.Count -gt 10) {
        $toRemove = $allSnaps[10..($allSnaps.Count - 1)]
        foreach ($old in $toRemove) {
            Remove-Item $old.FullName -Recurse -Force
            Write-Host "  Pruned old backup: $($old.Name)" -ForegroundColor DarkGray
        }
    }
    Write-Host ''
} else {
    Write-Host 'No character saves found to back up.' -ForegroundColor DarkGray
}

if (-not (Test-Path $workMod)) {
    Write-Host "work/$modName/ not found. Run bootstrap_working_mod.ps1 first." -ForegroundColor Red
    exit 1
}

# Auto-sync merged Levels.arc if newer than working copy
$mergedLevels = Join-Path $RepoRoot 'local\Levels_merged.arc'
$workLevels = Join-Path $workMod 'Resources\Levels.arc'
if (Test-Path $mergedLevels) {
    $mergedTime = (Get-Item $mergedLevels).LastWriteTime
    $workTime = if (Test-Path $workLevels) { (Get-Item $workLevels).LastWriteTime } else { [datetime]::MinValue }
    if ($mergedTime -gt $workTime) {
        $mergedMB = [math]::Round((Get-Item $mergedLevels).Length / 1MB, 1)
        Write-Host "Syncing newer Levels_merged.arc ($mergedMB MB) to working mod..." -ForegroundColor Yellow
        $resDir = Join-Path $workMod 'Resources'
        if (-not (Test-Path $resDir)) { New-Item -ItemType Directory -Path $resDir -Force | Out-Null }
        Copy-Item $mergedLevels $workLevels -Force
        Write-Host 'Levels.arc synced.' -ForegroundColor Green
    }
}

# Verify essential files exist
$dbFile = Join-Path $workMod "Database\$modName.arz"
if (-not (Test-Path $dbFile)) {
    Write-Host "Database/$modName.arz not found in working mod." -ForegroundColor Red
    exit 1
}

# Create CustomMaps directory if needed
if (-not (Test-Path $customMaps)) {
    Write-Host "Creating CustomMaps directory: $customMaps"
    New-Item -ItemType Directory -Path $customMaps -Force | Out-Null
}

# Backup existing deployment
if (Test-Path $deployTarget) {
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $backupPath = Join-Path $backupDir "$modName\$timestamp"
    Write-Host "Backing up existing deployment to: backups/deployed/$modName/$timestamp/"
    if (-not (Test-Path $backupPath)) { New-Item -ItemType Directory -Path $backupPath -Force | Out-Null }
    Copy-Item -Path "$deployTarget\*" -Destination $backupPath -Recurse -Force
    Remove-Item $deployTarget -Recurse -Force
    Write-Host 'Backup complete.' -ForegroundColor Green
}

# Deploy
Write-Host "Deploying to: $deployTarget"
Copy-Item -Path $workMod -Destination $deployTarget -Recurse -Force

# Verify
$deployedArz = Join-Path $deployTarget "Database\$modName.arz"
if (Test-Path $deployedArz) {
    $deployedFiles = @(Get-ChildItem $deployTarget -Recurse -File)
    $deployedMB = [math]::Round(($deployedFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
    Write-Host ''
    Write-Host "Deployed $($deployedFiles.Count) files ($deployedMB MB)" -ForegroundColor Green
    Write-Host "Database: $deployedArz" -ForegroundColor Green
    Write-Host ''
    Write-Host 'To test: Launch TQAE -> Play Custom Quest -> SoulvizierClassic' -ForegroundColor Cyan
} else {
    Write-Host 'ERROR: Database file not found in deployed folder!' -ForegroundColor Red
    exit 1
}

Write-Host 'Done.' -ForegroundColor Green
