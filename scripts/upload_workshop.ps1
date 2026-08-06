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
    [string]$Visibility = '1',
    # Steam Change Notes entry for THIS update. Defaults to docs/WORKSHOP_CHANGENOTE.bbcode.
    # Upload FAILS if neither is supplied - a silent empty change log is not acceptable.
    [string]$ChangeNote,
    # Workshop COVER IMAGE (the thumbnail shown in browse/subscribed lists). Defaults to
    # assets/workshop_preview.jpg if present. Will 2026-07-27: "right now our mod shows up on
    # steam without any cover image" - the VDF never carried a previewfile key, so the item has
    # had no thumbnail since launch. Steam: JPG/PNG, under 1 MB, square-ish (600x600+ ideal).
    [string]$PreviewFile
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

# ── Push-gate (build30 F7 + F9, Will's standing "protection from push") ──────
# TWO fail-loud stages, both against what will ACTUALLY be uploaded:
#   (1) F9 dist==work coupling (the stale-dist ship-through hole the delta vet
#       found): SteamCMD uploads dist/workshop/content, populated only by a
#       prior package_workshop.ps1 run - nothing else keeps it in sync with
#       work/. Hash-compare the 4 coupled artifacts (arz, Text, Levels, Quests)
#       dist vs work; ANY mismatch aborts with "run package_workshop first".
#   (2) F7 contract suite against the DIST payload itself (per-artifact
#       overrides), not the work/ copy. run_contracts exits 0 = clean;
#       1 = non-whitelisted P0/P1 or module crash; 2 = setup/artifact error.
Write-Host '=== Push-gate 1/2: dist == work artifact coupling (F9) ===' -ForegroundColor Cyan
$workMod = Join-Path $RepoRoot 'work\SoulvizierClassic'
$coupled = @(
    @{ Name = 'SoulvizierClassic.arz'; Work = (Join-Path $workMod 'Database\SoulvizierClassic.arz'); Dist = (Join-Path $wrapperDir 'database\SoulvizierClassic.arz') },
    @{ Name = 'Text.arc';   Work = (Join-Path $workMod 'Resources\Text.arc');   Dist = (Join-Path $wrapperDir 'resources\Text.arc') },
    @{ Name = 'Levels.arc'; Work = (Join-Path $workMod 'Resources\Levels.arc'); Dist = (Join-Path $wrapperDir 'resources\Levels.arc') },
    @{ Name = 'Quests.arc'; Work = (Join-Path $workMod 'Resources\Quests.arc'); Dist = (Join-Path $wrapperDir 'resources\Quests.arc') }
)
$mismatch = $false
foreach ($a in $coupled) {
    if (-not (Test-Path $a.Work)) {
        Write-Host ("ERROR: staged work artifact missing: {0}" -f $a.Work) -ForegroundColor Red
        $mismatch = $true; continue
    }
    if (-not (Test-Path $a.Dist)) {
        Write-Host ("ERROR: dist artifact missing: {0}" -f $a.Dist) -ForegroundColor Red
        $mismatch = $true; continue
    }
    $hw = (Get-FileHash -Algorithm MD5 -Path $a.Work).Hash.ToLower()
    $hd = (Get-FileHash -Algorithm MD5 -Path $a.Dist).Hash.ToLower()
    if ($hw -ne $hd) {
        Write-Host ("MISMATCH: {0}  work={1}  dist={2}" -f $a.Name, $hw.Substring(0, 8), $hd.Substring(0, 8)) -ForegroundColor Red
        $mismatch = $true
    } else {
        Write-Host ("  OK {0} ({1})" -f $a.Name, $hw.Substring(0, 8)) -ForegroundColor Green
    }
}
if ($mismatch) {
    Write-Host 'ABORT: dist/workshop is STALE (dist != work). Run package_workshop.ps1 first, then re-run this upload.' -ForegroundColor Red
    exit 1
}

Write-Host '=== Push-gate 2/2: contract suite against the DIST payload (F7) ===' -ForegroundColor Cyan
$pyExe = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
if (-not (Test-Path $pyExe)) { $pyExe = 'py' }
$env:PYTHONIOENCODING = 'utf-8'
& $pyExe (Join-Path $RepoRoot 'tools\contracts\run_contracts.py') `
    --arz (Join-Path $wrapperDir 'database\SoulvizierClassic.arz') `
    --text-arc (Join-Path $wrapperDir 'resources\Text.arc') `
    --levels-arc (Join-Path $wrapperDir 'resources\Levels.arc') `
    --quests-arc (Join-Path $wrapperDir 'resources\Quests.arc') `
    --resource-arc-dir (Join-Path $wrapperDir 'resources')
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: contract suite FAILED against dist (exit $LASTEXITCODE) - upload ABORTED." -ForegroundColor Red
    Write-Host 'Fix the payload (or add a JUSTIFIED whitelist entry) and re-run. NEVER bypass this gate.' -ForegroundColor Yellow
    exit 1
}
Write-Host 'Push-gates PASS (dist == work, contracts clean on dist) - proceeding to upload.' -ForegroundColor Green

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

# CHANGE NOTE (Will 2026-07-27: "are we updating the change notes on steam as we go?" - we were
# NOT; every update before build51 posted with an empty change log). Source of truth is
# docs/WORKSHOP_CHANGENOTE.bbcode: write the note for THIS update there before uploading, or pass
# -ChangeNote to override. Same VDF-safety rules as the description (no double-quotes, no
# backslashes - KeyValues treats them as escapes).
if (-not $ChangeNote) {
    $noteFile = Join-Path $RepoRoot 'docs\WORKSHOP_CHANGENOTE.bbcode'
    if (Test-Path $noteFile) { $ChangeNote = (Get-Content $noteFile -Raw).TrimEnd() }
}
if (-not $ChangeNote) {
    Write-Host 'ERROR: no change note. Write docs/WORKSHOP_CHANGENOTE.bbcode or pass -ChangeNote "..."' -ForegroundColor Red
    Write-Host '       (subscribers see this in the Change Notes tab; shipping blind is how we lost the log for builds 27-50.)' -ForegroundColor Red
    exit 1
}
if ($ChangeNote.Contains('"') -or $ChangeNote.Contains('\')) {
    Write-Host 'ERROR: change note contains a double-quote or backslash (VDF-unsafe). Use single quotes and forward slashes.' -ForegroundColor Red
    exit 1
}
if ($ChangeNote.Length -gt 8000) {
    Write-Host "ERROR: change note length $($ChangeNote.Length) exceeds the 8000-char Steam cap." -ForegroundColor Red
    exit 1
}
Write-Host "Change note ($($ChangeNote.Length) chars):" -ForegroundColor Cyan
Write-Host $ChangeNote

# PREVIEW / COVER IMAGE.
# ⛔ NOT attempted by default. PROVEN 2026-08-06: this Workshop item (3759792705) lives on Steam's
#    LEGACY UGC cloud storage (`k_EPublishedFileStorageSystemLegacyCloud`), and the preview upload
#    ALWAYS fails there with `UGC Upload Limit exceeded` (steamcmd cloud_log.txt). Worse, bundling the
#    failing preview into the same run made two earlier sessions misread the whole upload as failed
#    ("Reverting to previous content ... Limit exceeded") when the CONTENT depot actually committed
#    fine. So the previewfile key is OMITTED unless you explicitly pass -PreviewFile, isolating the
#    content upload from the broken cover path. The cover must be set another way (in-game/website).
$previewLine = ''
if ($PreviewFile) {
    if (-not (Test-Path $PreviewFile)) {
        Write-Host "ERROR: preview file not found: $PreviewFile" -ForegroundColor Red
        exit 1
    }
    $previewFull = (Resolve-Path $PreviewFile).Path
    $previewSize = (Get-Item $previewFull).Length
    if ($previewSize -gt 1MB) {
        Write-Host "ERROR: preview image is $([math]::Round($previewSize/1MB,2)) MB; Steam caps the preview at 1 MB. Recompress it." -ForegroundColor Red
        exit 1
    }
    if ($previewFull -notmatch '\.(jpg|jpeg|png)$') {
        Write-Host "ERROR: preview must be .jpg/.jpeg/.png (got $previewFull)" -ForegroundColor Red
        exit 1
    }
    $previewLine = "`n  `"previewfile`"     `"$($previewFull -replace '\\', '\\')`""
    Write-Host "Preview image: $previewFull ($([math]::Round($previewSize/1KB)) KB)" -ForegroundColor Cyan
} else {
    Write-Host 'WARNING: no preview image - the Workshop item will show a BLANK tile.' -ForegroundColor Yellow
    Write-Host '         Put one at assets/workshop_preview.jpg or pass -PreviewFile.' -ForegroundColor Yellow
}

$vdfContent = @"
"workshopitem"
{
  "appid"           "475150"
  "publishedfileid" "$publishedId"
  "contentfolder"   "$($contentFullPath -replace '\\', '\\')"
  "title"           "$title"
  "description"     "$description"
  "changenote"      "$ChangeNote"$previewLine
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
