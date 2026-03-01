#Requires -Version 5.1
<#
.SYNOPSIS
    Detect all key paths, validate prerequisites, and write local/config.env.
.DESCRIPTION
    Windows-native equivalent of doctor.sh. Finds TQAE install, Workshop mods,
    Documents paths, and modding tools. Writes local/config.env for use by all
    other project scripts.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ConfigDir = Join-Path $RepoRoot 'local'
$ConfigFile = Join-Path $ConfigDir 'config.env'

if (-not (Test-Path $ConfigDir)) { New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null }

$ok = 0; $warn = 0; $fail = 0

function Pass($msg)  { Write-Host "  [OK]   $msg" -ForegroundColor Green;   $script:ok++ }
function Skip($msg)  { Write-Host "  [WARN] $msg" -ForegroundColor Yellow;  $script:warn++ }
function Fail($msg)  { Write-Host "  [FAIL] $msg" -ForegroundColor Red;     $script:fail++ }

Write-Host '=== SoulvizierClassic Doctor (Windows) ===' -ForegroundColor Cyan
Write-Host ''

# ── Windows username ─────────────────────────────────────────────────
$WinUser = $env:USERNAME
if ($WinUser) { Pass "Windows user: $WinUser" } else { Fail 'Could not determine Windows username' }

# ── Documents path (handle OneDrive redirect) ────────────────────────
$WinDocs = [Environment]::GetFolderPath('MyDocuments')
if (-not $WinDocs -or -not (Test-Path $WinDocs)) {
    foreach ($candidate in @(
        "$env:USERPROFILE\OneDrive\Documents",
        "$env:USERPROFILE\Documents"
    )) {
        if (Test-Path $candidate) { $WinDocs = $candidate; break }
    }
}
if ($WinDocs -and (Test-Path $WinDocs)) { Pass "Documents: $WinDocs" } else { Fail 'Could not find Documents folder' }

# ── TQ IT documents base ────────────────────────────────────────────
$TqDocsBase = $null
foreach ($candidate in @(
    (Join-Path $WinDocs 'My Games\Titan Quest - Immortal Throne'),
    (Join-Path $WinDocs 'My Games\Titan Quest')
)) {
    if (Test-Path $candidate) { $TqDocsBase = $candidate; break }
}
if ($TqDocsBase) { Pass "TQ docs base: $TqDocsBase" } else { Fail 'Could not find Titan Quest documents folder' }

# ── CustomMaps path ──────────────────────────────────────────────────
$WinCustomMaps = if ($TqDocsBase) { Join-Path $TqDocsBase 'CustomMaps' } else { '' }
if ($WinCustomMaps -and (Test-Path $WinCustomMaps)) {
    Pass "CustomMaps folder exists: $WinCustomMaps"
} else {
    Skip "CustomMaps folder not found, will create on deploy: $WinCustomMaps"
}

# ── Working path ─────────────────────────────────────────────────────
$WinWorking = if ($TqDocsBase) { Join-Path $TqDocsBase 'Working' } else { '' }
if ($WinWorking -and (Test-Path $WinWorking)) {
    Pass "Working folder exists: $WinWorking"
} else {
    Skip "Working folder not found: $WinWorking (may be needed for ArtManager)"
}

# ── TQAE install path ───────────────────────────────────────────────
$TqaeRoot = $null

function Find-TqaeInLibrary($libPath) {
    $p = Join-Path $libPath 'steamapps\common\Titan Quest Anniversary Edition'
    if ((Test-Path $p) -and (Test-Path (Join-Path $p 'TQ.exe'))) { return $p }
    return $null
}

$defaultSteam = 'C:\Program Files (x86)\Steam'
$TqaeRoot = Find-TqaeInLibrary $defaultSteam

if (-not $TqaeRoot) {
    $vdf = Join-Path $defaultSteam 'steamapps\libraryfolders.vdf'
    if (Test-Path $vdf) {
        $vdfContent = Get-Content $vdf -Raw
        $matches = [regex]::Matches($vdfContent, '"path"\s+"([^"]+)"')
        foreach ($m in $matches) {
            $libPath = $m.Groups[1].Value -replace '\\\\', '\'
            $result = Find-TqaeInLibrary $libPath
            if ($result) { $TqaeRoot = $result; break }
        }
    }
}

if ($TqaeRoot) { Pass "TQAE install: $TqaeRoot" } else { Fail 'Could not find Titan Quest Anniversary Edition install' }

# ── ArchiveTool ──────────────────────────────────────────────────────
$TqArchiveTool = $null
if ($TqaeRoot) {
    $at = Join-Path $TqaeRoot 'ArchiveTool.exe'
    if (Test-Path $at) { $TqArchiveTool = $at; Pass "ArchiveTool: $TqArchiveTool" }
    else { Skip 'ArchiveTool.exe not found' }
} else { Skip 'ArchiveTool.exe not found (no TQAE root)' }

# ── ArtManager ───────────────────────────────────────────────────────
$TqArtManager = $null
if ($TqaeRoot) {
    $am = Join-Path $TqaeRoot 'ArtManager.exe'
    if (Test-Path $am) { $TqArtManager = $am; Pass "ArtManager: $TqArtManager" }
    else { Skip 'ArtManager.exe not found' }
} else { Skip 'ArtManager.exe not found (no TQAE root)' }

# ── Steam Workshop for TQAE (app 475150) ────────────────────────────
$SteamWorkshop475150 = $null
foreach ($steamRoot in @($defaultSteam, 'C:\Program Files\Steam')) {
    $candidate = Join-Path $steamRoot 'steamapps\workshop\content\475150'
    if (Test-Path $candidate) { $SteamWorkshop475150 = $candidate; break }
}
if ($SteamWorkshop475150) {
    $modCount = @(Get-ChildItem $SteamWorkshop475150 -Directory -ErrorAction SilentlyContinue).Count
    Pass "Workshop (475150): $SteamWorkshop475150 ($modCount mod(s))"
} else { Skip 'Workshop folder for TQAE not found' }

# ── SteamCMD ─────────────────────────────────────────────────────────
$SteamCmdExe = $null
foreach ($candidate in @('C:\steamcmd\steamcmd.exe', 'C:\SteamCMD\steamcmd.exe')) {
    if (Test-Path $candidate) { $SteamCmdExe = $candidate; break }
}
if ($SteamCmdExe) { Pass "SteamCMD: $SteamCmdExe" } else { Skip 'SteamCMD not found (needed later for Workshop upload)' }

# ── Python ───────────────────────────────────────────────────────────
Write-Host ''
Write-Host '--- Windows tool check ---' -ForegroundColor Cyan
$pythonExe = $null
try {
    $pyVer = & python --version 2>&1
    if ($pyVer -match 'Python (\d+\.\d+)') {
        $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
        Pass "Python: $pyVer ($pythonExe)"
    } else { Skip 'Python not found' }
} catch { Skip 'Python not found' }

foreach ($tool in @('git', '7z')) {
    try {
        $cmd = Get-Command $tool -ErrorAction SilentlyContinue
        if ($cmd) { Pass "$tool`: $($cmd.Source)" }
        else { Skip "$tool not found" }
    } catch { Skip "$tool not found" }
}

# ── Write config.env ─────────────────────────────────────────────────
Write-Host ''
Write-Host '--- Writing config ---' -ForegroundColor Cyan

$configContent = @"
# Auto-generated by doctor.ps1 — $(Get-Date -Format 'o')
WIN_USER=$WinUser
WIN_DOCS=$WinDocs
TQ_DOCS_BASE=$TqDocsBase
WIN_CUSTOMMAPS=$WinCustomMaps
WIN_WORKING=$WinWorking
TQAE_ROOT=$TqaeRoot
TQ_ARCHIVETOOL=$TqArchiveTool
TQ_ARTMANAGER=$TqArtManager
STEAM_WORKSHOP_475150=$SteamWorkshop475150
STEAMCMD_EXE=$SteamCmdExe
REPO_ROOT=$RepoRoot
"@

Set-Content -Path $ConfigFile -Value $configContent -Encoding UTF8
Pass "Config written to $ConfigFile"

# ── Summary ──────────────────────────────────────────────────────────
Write-Host ''
Write-Host "=== Summary: $ok OK, $warn WARN, $fail FAIL ===" -ForegroundColor Cyan

if ($fail -gt 0) {
    Write-Host "FATAL: $fail critical check(s) failed. Fix the above and re-run." -ForegroundColor Red
    exit 1
}
if ($warn -gt 0) {
    Write-Host 'Some optional items missing — see warnings above.' -ForegroundColor Yellow
}

Write-Host 'Doctor complete.' -ForegroundColor Green
exit 0
