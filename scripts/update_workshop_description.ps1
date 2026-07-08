<#
.SYNOPSIS
    Update ONLY the Steam Workshop item's description (and optional change note).
.DESCRIPTION
    Metadata-only Workshop update: builds a VDF with NO contentfolder and NO
    visibility field, so SteamCMD updates the item's title/description without
    re-uploading the 1.1 GB content and without touching visibility.

    The description text is docs/WORKSHOP_DESCRIPTION.bbcode - the SINGLE source
    of truth, shared with upload_workshop.ps1 (which re-sends it on every content
    upload). Edit that file, then run this script to push the new text live.
.PARAMETER SteamUser
    Your Steam username. Required for SteamCMD login (session is cached).
.PARAMETER ChangeNote
    Optional change note shown on the item's Change Notes tab.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts/update_workshop_description.ps1 -SteamUser trevenaw7
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$SteamUser,
    [string]$ChangeNote = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

. "$PSScriptRoot\_common.ps1"

$steamcmd = Require-Config 'STEAMCMD_EXE'
$idFile = Join-Path $RepoRoot 'local\workshop_item_id.txt'
$descFile = Join-Path $RepoRoot 'docs\WORKSHOP_DESCRIPTION.bbcode'
$distDir = Join-Path $RepoRoot 'dist\workshop'
$vdfPath = Join-Path $distDir 'description_update.vdf'

if (-not (Test-Path $steamcmd)) {
    Write-Host "ERROR: SteamCMD not found at $steamcmd" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $idFile)) {
    Write-Host 'ERROR: local/workshop_item_id.txt not found; there is no published item to update.' -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $descFile)) {
    Write-Host "ERROR: description file not found: $descFile" -ForegroundColor Red
    exit 1
}

$publishedId = (Get-Content $idFile -Raw).Trim()
if ($publishedId -notmatch '^\d{5,}$') {
    Write-Host "ERROR: workshop_item_id.txt content '$publishedId' does not look like a Workshop item id." -ForegroundColor Red
    exit 1
}

$title = 'Soulvizier Classic (AE Port)'
# VDF KeyValues quoted strings accept REAL newlines; never escape them into literal
# '\n' (Steam renders that as text). Double-quote characters are FORBIDDEN in the
# description and change note (SteamCMD's KeyValues parser can terminate the string
# early); fail loud instead of trusting escape handling.
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
if ($ChangeNote.Contains('"')) {
    Write-Host 'ERROR: the change note contains a double-quote character; use single quotes instead (VDF-unsafe).' -ForegroundColor Red
    exit 1
}

# Metadata-only manifest: no contentfolder (content untouched), no visibility
# (stays as-is; passing it here could flip the live public item by accident).
$changeNoteLine = ''
if ($ChangeNote -ne '') {
    $changeNoteLine = "  `"changenote`"      `"$ChangeNote`"`r`n"
}
$vdfContent = @"
"workshopitem"
{
  "appid"           "475150"
  "publishedfileid" "$publishedId"
  "title"           "$title"
  "description"     "$description"
$changeNoteLine}
"@

New-Item -ItemType Directory -Force -Path $distDir | Out-Null
Set-Content -Path $vdfPath -Value $vdfContent -Encoding UTF8

Write-Host '=== Workshop description update (metadata only) ===' -ForegroundColor Cyan
Write-Host "Item: $publishedId"
Write-Host "Description: $($description.Length) chars from docs/WORKSHOP_DESCRIPTION.bbcode"
Write-Host "VDF manifest: $vdfPath"
Write-Host ''

& $steamcmd +login $SteamUser +workshop_build_item (Resolve-Path $vdfPath).Path +quit

if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    Write-Host "SteamCMD exited with code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ''
Write-Host 'Description update pushed.' -ForegroundColor Green
Write-Host 'Verify: https://steamcommunity.com/sharedfiles/filedetails/?id=3759792705' -ForegroundColor Green
