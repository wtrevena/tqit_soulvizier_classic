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
# The description lives in docs/WORKSHOP_DESCRIPTION.bbcode - the single source of truth,
# shared with scripts/update_workshop_description.ps1 (metadata-only pushes). Every content
# upload re-sends it, so edits to the live description MUST go into that file.
# NOTE: the VDF description must contain REAL newlines (KeyValues quoted strings accept
# them); never escape them into literal '\n' - Steam renders that as text. Double-quote
# characters are FORBIDDEN in the description (SteamCMD's KeyValues parser can terminate
# the string early); we fail loud instead of trusting escape handling.
$descFile = Join-Path $RepoRoot 'docs\WORKSHOP_DESCRIPTION.bbcode'
if (-not (Test-Path $descFile)) {
    Write-Host "ERROR: description file not found: $descFile" -ForegroundColor Red
    exit 1
}
$description = (Get-Content $descFile -Raw).TrimEnd()
if ($description.Contains('"')) {
    Write-Host "ERROR: docs/WORKSHOP_DESCRIPTION.bbcode contains a double-quote character; use single quotes instead (VDF-unsafe)." -ForegroundColor Red
    exit 1
}
if ($description.Contains('\')) {
    Write-Host 'ERROR: docs/WORKSHOP_DESCRIPTION.bbcode contains a backslash; VDF treats it as an escape character (VDF-unsafe). Use forward slashes.' -ForegroundColor Red
    exit 1
}
if ($description.Length -lt 100 -or $description.Length -gt 8000) {
    Write-Host "ERROR: description length $($description.Length) chars is outside the sane range (100..8000; Steam caps at 8000)." -ForegroundColor Red
    exit 1
}

$contentFullPath = (Resolve-Path $contentDir).Path

$vdfContent = @"
"workshopitem"
{
  "appid"           "475150"
  "publishedfileid" "$publishedId"
  "contentfolder"   "$($contentFullPath -replace '\\', '\\')"
  "title"           "$title"
  "description"     "$description"
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
