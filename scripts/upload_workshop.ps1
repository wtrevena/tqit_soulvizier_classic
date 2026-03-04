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
    [switch]$Update
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$steamcmd = Require-Config 'STEAMCMD_EXE'
$distDir = Join-Path $RepoRoot 'dist\workshop'
$contentDir = Join-Path $distDir 'SoulvizierClassic'
$vdfPath = Join-Path $distDir 'workshop.vdf'
$idFile = Join-Path $RepoRoot 'local\workshop_item_id.txt'

# Verify SteamCMD exists
if (-not (Test-Path $steamcmd)) {
    Write-Host "ERROR: SteamCMD not found at $steamcmd" -ForegroundColor Red
    Write-Host 'Install SteamCMD to C:\steamcmd\ and re-run doctor.ps1' -ForegroundColor Yellow
    exit 1
}

# Verify package exists
if (-not (Test-Path (Join-Path $contentDir 'database\SoulvizierClassic.arz'))) {
    Write-Host 'ERROR: Workshop package not found. Run package_workshop.ps1 first.' -ForegroundColor Red
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
$description = @"
Soulvizier 0.98i ported to Titan Quest Anniversary Edition.

A massive overhaul mod featuring:
- 800+ new monster souls to collect and equip
- 10 masteries (including Occult and Neidan from DLC)
- New uber boss dungeon with custom portals
- Enhanced mercenary scroll system
- Improved pet summon skills (Hydra, Rakanizeus, Boneash, and more)
- Legacy skills restored from Soulvizier 0.4.1
- Balanced for AE engine with DLC compatibility

Requires: Titan Quest Anniversary Edition (base game only - DLCs optional)
Play via: Custom Quest > SoulvizierClassic
"@

$contentFullPath = (Resolve-Path $contentDir).Path

$vdfContent = @"
"workshopitem"
{
  "appid"           "475150"
  "publishedfileid" "$publishedId"
  "contentfolder"   "$($contentFullPath -replace '\\', '\\')"
  "title"           "$title"
  "description"     "$($description -replace '"', '\"' -replace "`n", '\n')"
  "visibility"      "0"
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
