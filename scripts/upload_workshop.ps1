<#
.SYNOPSIS
    Upload SoulvizierClassic to Steam Workshop using SteamCMD.
.DESCRIPTION
    Creates a workshop VDF manifest and calls SteamCMD to upload.
    On first upload, creates a new Workshop item.
    On subsequent uploads, updates the existing item using the saved ID.

    Requires: SteamCMD installed, Steam account credentials, and
    package_workshop.ps1 to have been run first.
.PARAMETER SteamUser
    Your Steam username. Required for SteamCMD login.
.PARAMETER Update
    If set, updates an existing Workshop item (reads ID from local/workshop_item_id.txt).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$SteamUser,
    [switch]$Update,
    # Steam Workshop visibility: 0=public, 1=friends-only, 2=hidden, 3=unlisted.
    # First upload defaults to friends-only so the item can be verified (and
    # coop-tested by a friend) before flipping public with -Update -Visibility 0.
    [ValidateSet('0','1','2','3')]
    [string]$Visibility = '1'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$steamcmd = Require-Config 'STEAMCMD_EXE'
$distDir = Join-Path $RepoRoot 'dist\workshop'
# contentDir = the vdf contentfolder SteamCMD uploads. It must contain EXACTLY one child,
# the SoulvizierClassic wrapper folder, so the Workshop item root = a single
# SoulvizierClassic folder (database\ + resources\ inside it). Pointing contentfolder at
# the wrapper folder itself would upload database\/resources\ to the item root, which TQAE
# reads as two broken mods "database" and "resources" (the 2026-07-08 "two mods" bug).
$contentDir = Join-Path $distDir 'content'
$wrapperDir = Join-Path $contentDir 'SoulvizierClassic'
$vdfPath = Join-Path $distDir 'workshop.vdf'
$idFile = Join-Path $RepoRoot 'local\workshop_item_id.txt'

# Verify SteamCMD exists
if (-not (Test-Path $steamcmd)) {
    Write-Host "ERROR: SteamCMD not found at $steamcmd" -ForegroundColor Red
    Write-Host 'Install SteamCMD to C:\steamcmd\ and re-run doctor.ps1' -ForegroundColor Yellow
    exit 1
}

# Verify package exists (inside the SoulvizierClassic wrapper) and has the required
# single-wrapper layout, so we never upload the "two mods" layout.
if (-not (Test-Path (Join-Path $wrapperDir 'database\SoulvizierClassic.arz'))) {
    Write-Host 'ERROR: Workshop package not found. Run package_workshop.ps1 first.' -ForegroundColor Red
    exit 1
}
$rootChildren = @(Get-ChildItem $contentDir -Force)
if ($rootChildren.Count -ne 1 -or $rootChildren[0].Name -ne 'SoulvizierClassic' -or -not ($rootChildren[0] -is [System.IO.DirectoryInfo])) {
    $names = ($rootChildren | ForEach-Object { $_.Name }) -join ', '
    Write-Host "ERROR: contentfolder $contentDir must contain exactly one folder 'SoulvizierClassic'." -ForegroundColor Red
    Write-Host "Found: $names" -ForegroundColor Red
    Write-Host 'Re-run package_workshop.ps1 (it rebuilds the correct single-wrapper layout).' -ForegroundColor Red
    exit 1
}

Write-Host '=== Upload to Steam Workshop ===' -ForegroundColor Cyan

# Determine published file ID
$publishedId = '0'
if ($Update) {
    if (Test-Path $idFile) {
        $publishedId = (Get-Content $idFile -Raw).Trim()
        Write-Host "Updating existing Workshop item: $publishedId"
    } else {
        Write-Host 'ERROR: No workshop_item_id.txt found. Run without -Update for first upload.' -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host 'Creating NEW Workshop item'
    if (Test-Path $idFile) {
        $existingId = (Get-Content $idFile -Raw).Trim()
        Write-Host "WARNING: workshop_item_id.txt already exists (ID: $existingId)" -ForegroundColor Yellow
        Write-Host 'Use -Update to update the existing item, or delete local/workshop_item_id.txt to create a new one.' -ForegroundColor Yellow
        $confirm = Read-Host 'Continue creating a NEW item? (y/N)'
        if ($confirm -ne 'y') {
            Write-Host 'Aborted.' -ForegroundColor Yellow
            exit 0
        }
    }
}

# Build the VDF manifest
$title = 'Soulvizier Classic (AE Port)'
# NOTE: the VDF description must contain REAL newlines (KeyValues quoted strings
# accept them); never escape them into literal '\n' - Steam renders that as text.
$description = @"
Soulvizier 0.98i ported to Titan Quest Anniversary Edition - the classic souls overhaul, playable again, plus new content.

Features:
- 800+ monster souls to collect and equip, including 60+ newly completed boss souls (summon-the-boss and boss-skill souls)
- The Soulvizier blood cave restored and fully walkable, with its questlines (Grieving Widow, secret waterfall chamber, and more)
- New superboss: a blood-soaked incarnation of Toxeus the Murderer guarding the secret area, with the Crimson Verdict legendary set
- 10 masteries (including Occult and Neidan), legacy skills restored
- Epic and legendary enchanting, improved pet summons

Requires: Titan Quest Anniversary Edition. Play via Custom Quest > SoulvizierClassic with a dedicated Custom Quest character.
Strongly recommended: the community 4GB LAA patch for TQ.exe (large mod).
"@

$contentFullPath = (Resolve-Path $contentDir).Path

$vdfContent = @"
"workshopitem"
{
  "appid"           "475150"
  "publishedfileid" "$publishedId"
  "contentfolder"   "$($contentFullPath -replace '\\', '\\')"
  "title"           "$title"
  "description"     "$($description -replace '"', '\"')"
  "visibility"      "$Visibility"
}
"@

Set-Content -Path $vdfPath -Value $vdfContent -Encoding UTF8
Write-Host "VDF manifest: $vdfPath"
Write-Host "Content folder: $contentFullPath"
Write-Host ''

# Call SteamCMD
Write-Host 'Launching SteamCMD...' -ForegroundColor Yellow
Write-Host '  You will be prompted for your Steam password and possibly Steam Guard code.' -ForegroundColor Yellow
Write-Host ''

$vdfFullPath = (Resolve-Path $vdfPath).Path
& $steamcmd +login $SteamUser +workshop_build_item $vdfFullPath +quit

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host "SteamCMD exited with code $LASTEXITCODE" -ForegroundColor Red
    Write-Host 'Check the output above for errors.' -ForegroundColor Yellow
    exit $LASTEXITCODE
}

# Try to extract the Workshop item ID from SteamCMD output
# SteamCMD prints: "Successfully created/updated Workshop item <ID>"
# We parse the log to find it
$logDir = Join-Path (Split-Path $steamcmd) 'logs'
$workshopLog = Join-Path $logDir 'workshop_log.txt'

if (Test-Path $workshopLog) {
    $logContent = Get-Content $workshopLog -Raw
    if ($logContent -match 'PublishedFileId\s*[=:]\s*(\d+)' -or
        $logContent -match 'item\s+(\d{5,})') {
        $newId = $Matches[1]
        if ($newId -ne '0') {
            Set-Content -Path $idFile -Value $newId
            Write-Host ''
            Write-Host "Workshop item ID: $newId" -ForegroundColor Green
            Write-Host "Saved to: $idFile"
        }
    }
}

Write-Host ''
Write-Host 'Upload complete!' -ForegroundColor Green
if ($publishedId -eq '0') {
    Write-Host 'Check your Steam Workshop items to find the new item and set visibility.' -ForegroundColor Yellow
    Write-Host 'IMPORTANT: Save the Workshop item ID to local/workshop_item_id.txt for future updates.' -ForegroundColor Yellow
} else {
    Write-Host "Updated Workshop item: $publishedId"
}
Write-Host ''
Write-Host 'Your friends can subscribe to the mod on Steam Workshop to download it.' -ForegroundColor Green
