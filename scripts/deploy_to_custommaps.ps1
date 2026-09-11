#Requires -Version 5.1
<#
.SYNOPSIS
    Deploy the working mod into the Windows CustomMaps folder for testing.
.DESCRIPTION
    Backs up any existing deployed version, then copies work/SoulvizierClassic/
    into the CustomMaps folder so the user can test via "Play Custom Quest" in TQAE.

    BACKUPS GO TO THE NETWORK DRIVE (R-259, Will 2026-09-10: "if you need to save backups like
    this move them to the network drive"). Both snapshot kinds live under WIN_BACKUP_ROOT from
    local/config.env:
      <WIN_BACKUP_ROOT>\deployed\<mod>\<yyyyMMdd_HHmmss>\   newest BACKUP_KEEP kept (default 5)
      <WIN_BACKUP_ROOT>\characters\<yyyyMMdd_HHmmss>\      newest 10 kept
    The root is REQUIRED and is resolved + write-probed before any save or the deploy target is
    touched; an unmounted drive aborts the deploy loudly and there is NO local fallback. The old
    in-repo backups\deployed\ tree (one full ~1.3 GB copy per deploy, never rotated) had reached
    ~300 GB on C:. Every rotation delete goes through the junction-refusing guard in
    scripts/_backup.ps1 (docs/MISTAKES.md 2026-09-09).
#>
[CmdletBinding()]
param(
    # Opt-in: sync local\Levels_merged.arc into work\ before deploying.
    # Guarded because a stale local rebuild once nearly clobbered the good map
    # (see CLAUDE.md "Deploy hazard"). Pass -SyncLevels only after verifying
    # local\Levels_merged.arc is a correct, current build.
    [switch]$SyncLevels
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"
. "$PSScriptRoot\_backup.ps1"

$modName = 'SoulvizierClassic'
$workMod = Join-Path $RepoRoot "work\$modName"
$customMaps = Require-Config 'WIN_CUSTOMMAPS'
$deployTarget = Join-Path $customMaps $modName

Write-Host '=== Deploy to CustomMaps ===' -ForegroundColor Cyan

# R-259: the backup root comes from config and is checked FIRST. Fail loud here, before any
# character save or the deploy target is touched; never fall back to a path on C:.
if (-not $Config['WIN_BACKUP_ROOT']) {
    Write-Host "ERROR: Required config key 'WIN_BACKUP_ROOT' is missing from local\config.env." -ForegroundColor Red
    Write-Host '       R-259: deploy backups live on the network drive. Add a line such as' -ForegroundColor Red
    Write-Host '         WIN_BACKUP_ROOT=Z:\Computer Backup\tqit_soulvizier_classic' -ForegroundColor Red
    Write-Host '       (doctor.ps1 cannot detect it, but preserves it once set). Nothing was deployed.' -ForegroundColor Red
    exit 1
}
$backupRoot = $null
$backupKeep = 5
try {
    $backupRoot = Resolve-BackupRoot -Root (Require-Config 'WIN_BACKUP_ROOT') -RepoRoot $RepoRoot
    $backupKeep = Get-BackupKeep -Config $Config
} catch {
    Write-Host "ERROR: backup root check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host '       Nothing was deployed. Mount the network drive or fix WIN_BACKUP_ROOT / BACKUP_KEEP in local\config.env (see README).' -ForegroundColor Red
    exit 1
}
$backupDir = Join-Path $backupRoot 'deployed'
$charBackupDir = Join-Path $backupRoot 'characters'
Write-Host "Backup root: $backupRoot  (keep newest $backupKeep deploy snapshot(s) per mod, newest 10 character snapshots)" -ForegroundColor DarkGray

# Backup ALL character saves before any deployment (Main + Custom Quest)
$tqDocsBase = Require-Config 'TQ_DOCS_BASE'
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
    Write-Host "  $totalBacked total character(s) backed up to: $snapDir\" -ForegroundColor Green

    # Prune old character snapshots (keep newest 10). Every delete goes through the R-259 guard:
    # a snapshot outside the root, or one that is or contains a junction, is skipped, never deleted.
    $charRot = Invoke-BackupRotation -Root $backupRoot -Kind 'characters' -Keep 10
    foreach ($n in $charRot.Removed) { Write-Host "  Pruned old character backup: $n" -ForegroundColor DarkGray }
    foreach ($n in $charRot.Skipped) { Write-Host "  NOT pruned (guard refused, see the warning above): $n" -ForegroundColor Yellow }
    Write-Host ''
} else {
    Write-Host 'No character saves found to back up.' -ForegroundColor DarkGray
}

if (-not (Test-Path $workMod)) {
    Write-Host "work/$modName/ not found. Run bootstrap_working_mod.ps1 first." -ForegroundColor Red
    exit 1
}

# Sync merged Levels.arc into the working mod ONLY when explicitly requested.
# (Previously auto-synced whenever local was newer; a stale local rebuild made
# that a foot-gun that would have replaced the good deployed map.)
$mergedLevels = Join-Path $RepoRoot 'local\Levels_merged.arc'
$workLevels = Join-Path $workMod 'Resources\Levels.arc'
if (Test-Path $mergedLevels) {
    $mergedTime = (Get-Item $mergedLevels).LastWriteTime
    $workTime = if (Test-Path $workLevels) { (Get-Item $workLevels).LastWriteTime } else { [datetime]::MinValue }
    if ($mergedTime -gt $workTime) {
        if ($SyncLevels) {
            $mergedMB = [math]::Round((Get-Item $mergedLevels).Length / 1MB, 1)
            Write-Host "Syncing newer Levels_merged.arc ($mergedMB MB) to working mod..." -ForegroundColor Yellow
            $resDir = Join-Path $workMod 'Resources'
            if (-not (Test-Path $resDir)) { New-Item -ItemType Directory -Path $resDir -Force | Out-Null }
            Copy-Item $mergedLevels $workLevels -Force
            Write-Host 'Levels.arc synced.' -ForegroundColor Green
        } else {
            Write-Host 'NOTE: local\Levels_merged.arc is newer than work\ but was NOT synced.' -ForegroundColor Yellow
            Write-Host '      Re-run with -SyncLevels after verifying the local build is correct.' -ForegroundColor Yellow
        }
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

# Backup existing deployment (R-259: onto the network drive, verified by count, then rotated)
if (Test-Path $deployTarget) {
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $backupPath = Join-Path $backupDir "$modName\$timestamp"
    Write-Host "Backing up existing deployment to: $backupPath\"
    if (-not (Test-Path $backupPath)) { New-Item -ItemType Directory -Path $backupPath -Force | Out-Null }
    Copy-Item -Path "$deployTarget\*" -Destination $backupPath -Recurse -Force

    # Verify the copy by COUNT, never by exit status (docs/MISTAKES.md 2026-09-09 guard 4),
    # BEFORE the deploy target is removed. A short copy leaves the target untouched.
    $srcFiles = @(Get-ChildItem -LiteralPath $deployTarget -Recurse -File -Force)
    $dstFiles = @(Get-ChildItem -LiteralPath $backupPath -Recurse -File -Force)
    if ($dstFiles.Count -ne $srcFiles.Count) {
        Write-Host "ERROR: backup incomplete: $($dstFiles.Count) of $($srcFiles.Count) files reached $backupPath. Deploy target left untouched." -ForegroundColor Red
        exit 1
    }
    $srcMB = [math]::Round(($srcFiles | Measure-Object -Property Length -Sum).Sum / 1MB, 1)
    Write-Host "Backup complete: $($dstFiles.Count) files ($srcMB MB)." -ForegroundColor Green

    # Rotate: keep the newest $backupKeep snapshots of this mod. Every delete is guarded
    # (scripts/_backup.ps1); a refused snapshot is reported and left in place.
    $deployRot = Invoke-BackupRotation -Root $backupRoot -Kind 'deployed' -SubPath $modName -Keep $backupKeep
    foreach ($n in $deployRot.Removed) { Write-Host "  Pruned old deploy snapshot: $n" -ForegroundColor DarkGray }
    foreach ($n in $deployRot.Skipped) { Write-Host "  NOT pruned (guard refused, see the warning above): $n" -ForegroundColor Yellow }

    # The deploy target is removed recursively. Refuse if it is or contains a directory
    # junction / symlink: that delete would reach a foreign tree (docs/MISTAKES.md 2026-09-09).
    $targetLinks = @(Get-BackupLinkDirectories -Path $deployTarget)
    if ($targetLinks.Count -gt 0) {
        Write-Host "ERROR: $deployTarget is or contains $($targetLinks.Count) directory junction/symlink(s) (first: $($targetLinks[0].FullName)). Refusing the recursive delete; remove the link(s) by hand and re-run." -ForegroundColor Red
        exit 1
    }
    Remove-Item $deployTarget -Recurse -Force
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
